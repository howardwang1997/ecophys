"""Potential energy modules for EcoMD v0.

The total potential decomposes as

    U_θ(s, context) = V_pairwise(s) + V_external(s, context) + V_dissipation(s, s_prev)

with separate conservative and dissipative contributions so Phase 4 fluctuation-
theorem analysis can book-keep each force channel independently.

Design notes
------------
- All potentials are :class:`torch.nn.Module` with a `forward(...) -> scalar`.
- :func:`conservative_forces` and :func:`dissipative_forces` use
  :func:`torch.autograd.grad` with ``create_graph=True`` so forces are themselves
  differentiable — required for BPTT through the integrator.
- The pairwise potential is implemented naively as O(N^2) (fine for N ≤ 10^3 on
  Mac). Phase 3 swaps this module for a MACE-lite k-NN equivariant GNN; the
  :class:`Potential` protocol is what the integrator depends on.
- Permutation invariance is built-in: ``V_pairwise`` sums a symmetric kernel
  over pairs; ``V_external`` sums a per-agent term.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import torch
import torch.nn as nn
from torch import Tensor

# ─────────────────────────────────────────────────────────────────────────────
# Protocols
# ─────────────────────────────────────────────────────────────────────────────


class Potential(Protocol):
    """Anything the integrator can call to get scalar energy."""

    def __call__(self, s: Tensor, context: Tensor | None = None) -> Tensor: ...


# ─────────────────────────────────────────────────────────────────────────────
# Pairwise potential: V_pairwise(s) = Σ_{i<j} φ_θ(s_i, s_j)
# ─────────────────────────────────────────────────────────────────────────────


class PairwisePotential(nn.Module):
    """Symmetric pairwise MLP on concat([s_i, s_j, |s_i - s_j|]).

    To make the per-pair kernel φ_θ symmetric in (i, j) we evaluate it on both
    orderings and average. This keeps the gradient well-defined and exactly
    permutation-invariant.
    """

    def __init__(self, d: int, hidden: int = 64) -> None:
        super().__init__()
        self.d = d
        self.net = nn.Sequential(
            nn.Linear(3 * d, hidden),
            nn.SiLU(),
            nn.Linear(hidden, hidden),
            nn.SiLU(),
            nn.Linear(hidden, 1),
        )
        for m in self.net.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight, gain=0.5)
                nn.init.zeros_(m.bias)

    def forward(self, s: Tensor, context: Tensor | None = None) -> Tensor:
        del context  # pairwise potential is context-free in v0
        n, d = s.shape
        assert d == self.d, f"expected last dim {self.d}, got {d}"

        s_i = s.unsqueeze(1).expand(n, n, d)
        s_j = s.unsqueeze(0).expand(n, n, d)
        diff = (s_i - s_j).abs()

        inp_ij = torch.cat([s_i, s_j, diff], dim=-1)
        inp_ji = torch.cat([s_j, s_i, diff], dim=-1)
        phi_ij = self.net(inp_ij).squeeze(-1)
        phi_ji = self.net(inp_ji).squeeze(-1)
        phi = 0.5 * (phi_ij + phi_ji)

        mask = torch.triu(torch.ones(n, n, device=s.device, dtype=torch.bool), diagonal=1)
        return phi[mask].sum()


# ─────────────────────────────────────────────────────────────────────────────
# Stochastic pair sampling (v0.9): V ≈ unbiased Monte Carlo over random pairs
# ─────────────────────────────────────────────────────────────────────────────


class StochasticPairwisePotential(nn.Module):
    """Same symmetric pair kernel as ``PairwisePotential`` but evaluated on a
    random subset of pairs per forward pass.

    Each agent i samples ``k_random`` other agents uniformly (with replacement
    excluded from self). The full V = Σ_{i<j} φ(s_i, s_j) is estimated by

        V_stoch(s) = (N-1)/(2k) · Σ_{(i,j) ∈ E_random} φ(s_i, s_j)

    with E[V_stoch] = V_full (unbiased). Variance scales as O((P-E)/E) where
    P = N(N-1)/2 and E = N·k. At N=10^4, k=50 → std-to-signal ~10%,
    comparable to minibatch SGD noise.

    Memory cost: O(N·k·d) forward per step (vs O(N²·d) for the dense
    version), enabling N ≥ 10^4 on a single H20 card.

    Key design choice vs MACE-lite's k-NN: **pairs are sampled uniformly at
    random**, not by feature-space proximity. Random sampling gives an
    unbiased estimator of the full-pair potential; k-NN gives a biased
    estimator favouring local interactions, which we showed today (2026-04-24
    Session 17) produces flat-ACF dynamics instead of real vol clustering.

    Parameters
    ----------
    d : state dimension
    hidden : MLP hidden dim
    k_random : number of random pair partners per agent per forward (50 default)
    resample_per_step : if True, sample fresh edges each forward; if False,
        keep the same edges within a training chunk (faster but higher variance).
    """

    def __init__(
        self,
        d: int,
        hidden: int = 64,
        k_random: int = 50,
        resample_per_step: bool = True,
        spatial_batch_size: int = 0,
    ) -> None:
        super().__init__()
        self.d = d
        self.k_random = k_random
        self.resample_per_step = resample_per_step
        # spatial_batch_size: 0 = off (process all edges at once);
        # B > 0 = process edges in chunks of B, wrap each chunk in
        # torch.utils.checkpoint so MLP intermediate activations are
        # released between chunks (recomputed on backward). Reduces
        # per-step pairwise memory from O(N×k) to O(B). Compute overhead
        # ~1.3-1.5×. Recommended: B = 50_000 to 200_000 edges.
        self.spatial_batch_size = spatial_batch_size
        self.net = nn.Sequential(
            nn.Linear(3 * d, hidden),
            nn.SiLU(),
            nn.Linear(hidden, hidden),
            nn.SiLU(),
            nn.Linear(hidden, 1),
        )
        for m in self.net.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight, gain=0.5)
                nn.init.zeros_(m.bias)
        # Cache for non-resampling mode
        self._cached_edges: Tensor | None = None

    def reset_edge_cache(self) -> None:
        self._cached_edges = None

    def _sample_edges(self, n: int, device: torch.device) -> Tensor:
        """Return (2, N·k) long tensor of (src, dst) pairs."""
        k = min(self.k_random, n - 1)
        # For each i ∈ [n], pick k distinct j ≠ i. Use torch.randperm per-row,
        # then drop self-match. Vectorized with rand + topk.
        rand = torch.rand(n, n, device=device)
        rand.fill_diagonal_(-1.0)  # push self to bottom after largest-k selection
        _, idx = torch.topk(rand, k=k + 1, dim=1, largest=True)
        # idx[:,0] might still be the diagonal if it was +1 (unlikely but
        # possible after fill_diagonal_=-1). Actually -1 is below any rand in [0,1],
        # so diagonal will never win topk(largest). Safe to use all k columns.
        idx = idx[:, :k]  # (n, k)
        src = torch.arange(n, device=device).unsqueeze(1).expand(n, k).reshape(-1)
        dst = idx.reshape(-1)
        return torch.stack([src, dst], dim=0)

    def _phi_batch(self, s: Tensor, edges_b: Tensor) -> Tensor:
        """Compute (1/2)(phi_ij + phi_ji).sum() for a batch of edges.

        Returns a scalar — the contribution to V from this edge batch.
        """
        src, dst = edges_b[0], edges_b[1]
        s_i = s[src]
        s_j = s[dst]
        diff = (s_i - s_j).abs()
        inp_ij = torch.cat([s_i, s_j, diff], dim=-1)
        inp_ji = torch.cat([s_j, s_i, diff], dim=-1)
        phi_ij = self.net(inp_ij).squeeze(-1)
        phi_ji = self.net(inp_ji).squeeze(-1)
        return 0.5 * (phi_ij + phi_ji).sum()

    def forward(self, s: Tensor, context: Tensor | None = None) -> Tensor:
        del context
        n, d = s.shape
        assert d == self.d, f"expected last dim {self.d}, got {d}"

        if self.resample_per_step or self._cached_edges is None:
            edges = self._sample_edges(n, s.device).detach()
            if not self.resample_per_step:
                self._cached_edges = edges
        else:
            edges = self._cached_edges
        E = edges.shape[1]

        # Rescale to estimate the full sum over N·(N-1)/2 unique pairs.
        scale = (n - 1) / (2.0 * self.k_random)

        B = int(self.spatial_batch_size)
        if B <= 0 or B >= E or not s.requires_grad:
            # Original path — all edges at once. Fast for small E or no-grad
            # forward (inference). Avoids the checkpoint overhead.
            phi_total = self._phi_batch(s, edges)
            return scale * phi_total

        # Spatial-checkpoint path: process edges in chunks of B, wrap each
        # in torch.utils.checkpoint so the MLP intermediate activations get
        # discarded after summing each batch's contribution. The per-batch
        # contribution is recomputed during backward.
        # NOTE: this reduces pairwise *forward* peak memory by ~E/B factor.
        # When the outer caller uses ``create_graph=True`` (e.g. via
        # conservative_forces for BPTT), the inner V_b's higher-order
        # gradient graph may still be retained for second-order autograd —
        # so this primarily helps when N (and therefore E) is very large
        # and the per-batch MLP size dominates a single step's memory.
        V_total = torch.zeros((), device=s.device, dtype=s.dtype)
        for start in range(0, E, B):
            end = min(start + B, E)
            edges_b = edges[:, start:end].contiguous()
            V_b = torch.utils.checkpoint.checkpoint(
                self._phi_batch, s, edges_b,
                use_reentrant=False,
                preserve_rng_state=False,  # pairwise MLP has no RNG inside
            )
            V_total = V_total + V_b
        return scale * V_total


# ─────────────────────────────────────────────────────────────────────────────
# External potential: V_external(s, context) = Σ_i ψ_θ(s_i, context)
# ─────────────────────────────────────────────────────────────────────────────


class ExternalPotential(nn.Module):
    """Per-agent potential coupled to market context.

    ``context`` is expected to be a 1-D tensor of shape (c,) describing the
    current market state (e.g. [log_price, vol, r_prev]). In v0 c=3.
    """

    def __init__(self, d: int, context_dim: int = 3, hidden: int = 64) -> None:
        super().__init__()
        self.d = d
        self.context_dim = context_dim
        self.net = nn.Sequential(
            nn.Linear(d + context_dim, hidden),
            nn.SiLU(),
            nn.Linear(hidden, hidden),
            nn.SiLU(),
            nn.Linear(hidden, 1),
        )
        for m in self.net.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight, gain=0.5)
                nn.init.zeros_(m.bias)

    def forward(self, s: Tensor, context: Tensor | None = None) -> Tensor:
        if context is None:
            context = torch.zeros(self.context_dim, device=s.device, dtype=s.dtype)
        if context.dim() != 1 or context.shape[0] != self.context_dim:
            raise ValueError(
                f"context must be 1-D with {self.context_dim} entries, got shape {tuple(context.shape)}"
            )
        n = s.shape[0]
        ctx = context.unsqueeze(0).expand(n, self.context_dim)
        inp = torch.cat([s, ctx], dim=-1)
        psi = self.net(inp).squeeze(-1)
        return psi.sum()


# ─────────────────────────────────────────────────────────────────────────────
# Dissipative potential: V_dissipation(s, s_prev) = λ · Σ_i |s_i - s_i_prev|²
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class DissipationParams:
    lam: float = 0.01


class DissipationPotential(nn.Module):
    """Explicit quadratic friction term, not learned.

    The gradient of this potential is the dissipative force used in the
    Jarzynski / Crooks book-keeping of Phase 4. It is explicit (not part of the
    learned θ) so the conservative/dissipative split is identifiable.
    """

    def __init__(self, params: DissipationParams | None = None) -> None:
        super().__init__()
        self.params = params or DissipationParams()

    def forward(self, s: Tensor, s_prev: Tensor) -> Tensor:
        if s.shape != s_prev.shape:
            raise ValueError(f"shape mismatch: {s.shape} vs {s_prev.shape}")
        return self.params.lam * ((s - s_prev) ** 2).sum()


# ─────────────────────────────────────────────────────────────────────────────
# Composite: joint conservative potential Ũ_cons = V_pairwise + V_external
# ─────────────────────────────────────────────────────────────────────────────


class ConservativePotential(nn.Module):
    """V_cons = V_pairwise + V_external. Learned; no dissipation."""

    def __init__(self, pairwise: PairwisePotential, external: ExternalPotential) -> None:
        super().__init__()
        self.pairwise = pairwise
        self.external = external

    def forward(self, s: Tensor, context: Tensor | None = None) -> Tensor:
        return self.pairwise(s) + self.external(s, context)


# ─────────────────────────────────────────────────────────────────────────────
# Force extraction helpers
# ─────────────────────────────────────────────────────────────────────────────


def conservative_forces(
    potential: ConservativePotential,
    s: Tensor,
    context: Tensor | None = None,
    *,
    create_graph: bool = True,
) -> Tensor:
    """F_cons = -∇_s V_cons(s, context). Shape (N, d)."""
    # Force extraction needs autograd even during inference — temporarily enable.
    with torch.enable_grad():
        if not s.requires_grad:
            s = s.detach().requires_grad_(True)
        u = potential(s, context)
        (grad_s,) = torch.autograd.grad(u, s, create_graph=create_graph)
    return -grad_s


def dissipative_forces(
    dissipation: DissipationPotential,
    s: Tensor,
    s_prev: Tensor,
    *,
    create_graph: bool = True,
) -> Tensor:
    """F_diss = -∇_s V_diss(s, s_prev). Shape (N, d)."""
    with torch.enable_grad():
        if not s.requires_grad:
            s = s.detach().requires_grad_(True)
        u = dissipation(s, s_prev)
        (grad_s,) = torch.autograd.grad(u, s, create_graph=create_graph)
    return -grad_s
