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
        type_aware_heads: bool = False,
        type_idx: Tensor | None = None,
        n_types: int = 4,
        pair_features_extra: str = "none",
        d_global_in: int = 0,
        edge_gating: bool = False,
        gate_init_p: float = 0.7,
        gate_input_u: bool = True,
    ) -> None:
        super().__init__()
        self.d = d
        self.k_random = k_random
        self.resample_per_step = resample_per_step
        self.d_global_in = int(d_global_in)
        # Tier 4.2: dynamic graph via learned soft gate on each random edge.
        self.edge_gating = bool(edge_gating)
        self.gate_init_p = float(gate_init_p)
        self.gate_input_u = bool(gate_input_u)
        # Tier 1.3: pair features extra
        if pair_features_extra not in ("none", "distance", "inner_prod", "signed_diff", "all"):
            raise ValueError(
                f"pair_features_extra must be one of "
                f"'none'|'distance'|'inner_prod'|'signed_diff'|'all', "
                f"got {pair_features_extra!r}"
            )
        self.pair_features_extra = pair_features_extra
        # base input is concat(s_i, s_j, |Δs|) → 3d. Adjust per extra-feature mode.
        # Note: "signed_diff" REPLACES |Δs| with Δs, so dim stays 3d.
        # "distance" adds 1 scalar; "inner_prod" adds 1 scalar; "all" adds 2 + signed_diff (no extra dim).
        # Tier 4.1: optionally append a broadcast global-state vector u (d_global_in).
        in_dim = 3 * d
        if pair_features_extra in ("distance", "all"):
            in_dim += 1
        if pair_features_extra in ("inner_prod", "all"):
            in_dim += 1
        in_dim += self.d_global_in

        # Tier 1.2: type-aware heads. Shared backbone (all but last layer);
        # per-(src-type, dst-type) last linear → K² heads.
        self.type_aware_heads = type_aware_heads
        if type_aware_heads:
            assert type_idx is not None, "type_aware_heads=True requires type_idx"
            self.n_types = int(n_types)
            self.register_buffer("type_idx", type_idx.to(torch.long), persistent=False)
            self.backbone = nn.Sequential(
                nn.Linear(in_dim, hidden),
                nn.SiLU(),
                nn.Linear(hidden, hidden),
                nn.SiLU(),
            )
            # K² parallel last-layer heads, parameterised as (K², hidden) + (K²,)
            K2 = self.n_types * self.n_types
            self.head_w = nn.Parameter(torch.empty(K2, hidden))
            self.head_b = nn.Parameter(torch.zeros(K2))
            nn.init.xavier_uniform_(self.head_w, gain=0.5)
            for m in self.backbone.modules():
                if isinstance(m, nn.Linear):
                    nn.init.xavier_uniform_(m.weight, gain=0.5)
                    nn.init.zeros_(m.bias)
        else:
            self.n_types = 0
            self.type_idx = None
            self.net = nn.Sequential(
                nn.Linear(in_dim, hidden),
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

        # Tier 4.2: gate MLP. Input is (s_i, s_j, |Δs|) plus optional u.
        # Output is a per-edge logit; we sigmoid + rescale by 1/gate_init_p
        # so E[w·phi] ≈ E[phi] at init (initial bias makes sigmoid ≈ p).
        if self.edge_gating:
            gate_in_dim = 3 * d
            if self.gate_input_u and self.d_global_in > 0:
                gate_in_dim += self.d_global_in
            self.gate_mlp = nn.Sequential(
                nn.Linear(gate_in_dim, hidden),
                nn.SiLU(),
                nn.Linear(hidden, 1),
            )
            for m in self.gate_mlp.modules():
                if isinstance(m, nn.Linear):
                    nn.init.xavier_uniform_(m.weight, gain=0.1)
                    nn.init.zeros_(m.bias)
            # Set output bias so sigmoid(b0) = gate_init_p initially.
            import math as _math
            p = max(min(self.gate_init_p, 0.99), 0.01)
            b0 = _math.log(p / (1.0 - p))
            self.gate_mlp[-1].bias.data.fill_(b0)

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

    def _build_pair_inputs(
        self,
        s_i: Tensor,
        s_j: Tensor,
        u: Tensor | None = None,
    ) -> tuple[Tensor, Tensor]:
        """Return (inp_ij, inp_ji) per pair-feature mode.

        ``u``: optional broadcast global-state vector of shape (d_global_in,).
        When provided AND ``self.d_global_in > 0``, broadcast and concat.
        """
        if self.pair_features_extra in ("none", "distance", "inner_prod"):
            base_diff = (s_i - s_j).abs()
        else:  # "signed_diff" or "all"
            base_diff = (s_i - s_j)

        parts_ij = [s_i, s_j, base_diff]
        parts_ji = [s_j, s_i, base_diff if self.pair_features_extra == "none" else
                    -base_diff if self.pair_features_extra in ("signed_diff", "all")
                    else base_diff]

        if self.pair_features_extra in ("distance", "all"):
            dist = (s_i - s_j).norm(dim=-1, keepdim=True)            # (E, 1)
            parts_ij.append(dist)
            parts_ji.append(dist)
        if self.pair_features_extra in ("inner_prod", "all"):
            inner = (s_i * s_j).sum(dim=-1, keepdim=True)            # (E, 1)
            parts_ij.append(inner)
            parts_ji.append(inner)

        if self.d_global_in > 0:
            E = s_i.shape[0]
            if u is None:
                u_b = torch.zeros((E, self.d_global_in), device=s_i.device, dtype=s_i.dtype)
            else:
                u_b = u.unsqueeze(0).expand(E, self.d_global_in)
            parts_ij.append(u_b)
            parts_ji.append(u_b)

        return torch.cat(parts_ij, dim=-1), torch.cat(parts_ji, dim=-1)

    def _eval_kernel(self, inp_ij: Tensor, inp_ji: Tensor, src: Tensor, dst: Tensor) -> Tensor:
        """φ(s_i, s_j) (symmetrized). Type-aware when enabled."""
        if not self.type_aware_heads:
            phi_ij = self.net(inp_ij).squeeze(-1)
            phi_ji = self.net(inp_ji).squeeze(-1)
            return 0.5 * (phi_ij + phi_ji)
        # Type-aware: route each edge to its (type_src, type_dst) head.
        h_ij = self.backbone(inp_ij)                             # (E, hidden)
        h_ji = self.backbone(inp_ji)
        t_src = self.type_idx[src]                               # (E,)
        t_dst = self.type_idx[dst]
        head_idx_ij = (t_src * self.n_types + t_dst).clamp_(0, self.n_types ** 2 - 1)
        head_idx_ji = (t_dst * self.n_types + t_src).clamp_(0, self.n_types ** 2 - 1)
        w_ij = self.head_w[head_idx_ij]                          # (E, hidden)
        w_ji = self.head_w[head_idx_ji]
        b_ij = self.head_b[head_idx_ij]                          # (E,)
        b_ji = self.head_b[head_idx_ji]
        phi_ij = (h_ij * w_ij).sum(dim=-1) + b_ij                # (E,)
        phi_ji = (h_ji * w_ji).sum(dim=-1) + b_ji
        return 0.5 * (phi_ij + phi_ji)

    def forward(self, s: Tensor, context: Tensor | None = None) -> Tensor:
        # Tier 4.1: when d_global_in>0, the simulator passes the global state
        # vector u via the ``context`` channel (1-D, length d_global_in). When
        # d_global_in==0 we ignore context as before.
        u = context if (self.d_global_in > 0 and context is not None) else None
        n, d = s.shape
        assert d == self.d, f"expected last dim {self.d}, got {d}"

        if self.resample_per_step or self._cached_edges is None:
            edges = self._sample_edges(n, s.device).detach()
            if not self.resample_per_step:
                self._cached_edges = edges
        else:
            edges = self._cached_edges
        src, dst = edges[0], edges[1]                           # (E,)
        E = src.shape[0]

        s_i = s[src]                                            # (E, d)
        s_j = s[dst]                                            # (E, d)

        inp_ij, inp_ji = self._build_pair_inputs(s_i, s_j, u=u)
        phi = self._eval_kernel(inp_ij, inp_ji, src, dst)       # (E,)

        # Tier 4.2: per-edge soft gate, optionally regime-conditioned via u.
        # The gate uses raw (s_i, s_j, |Δs|) features (independent of the
        # pair_features_extra mode) so it's interpretable as "should this
        # edge contribute to V at all?" rather than "with what kernel?".
        if self.edge_gating:
            gate_inp = torch.cat([s_i, s_j, (s_i - s_j).abs()], dim=-1)
            if self.gate_input_u and self.d_global_in > 0 and u is not None:
                gate_inp = torch.cat(
                    [gate_inp, u.unsqueeze(0).expand(E, self.d_global_in)],
                    dim=-1,
                )
            w = torch.sigmoid(self.gate_mlp(gate_inp)).squeeze(-1)   # (E,)
            # Rescale by 1/gate_init_p so E[w·phi] ≈ E[phi] at init.
            phi = phi * w / self.gate_init_p

        # Rescale to estimate the full sum over N·(N-1)/2 unique pairs.
        # Each agent contributes k random partners → N·k ordered edges, but
        # the original V_full sum is over unordered pairs. The factor
        # (N-1)/(2k) makes E[V_stoch] = V_full.
        scale = (n - 1) / (2.0 * self.k_random)
        return scale * phi.sum()


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

    def forward(
        self,
        s: Tensor,
        context: Tensor | None = None,
        u_global: Tensor | None = None,
    ) -> Tensor:
        # External potential gets the price (+ optional agent-pool) context.
        # Pairwise potential gets the global state u (Tier 4.1) when set —
        # we pass u via the pairwise's own context channel since pairwise
        # has its own d_global_in flag controlling whether it's consumed.
        v_pair = self.pairwise(s, context=u_global)
        v_ext = self.external(s, context)
        return v_pair + v_ext


# ─────────────────────────────────────────────────────────────────────────────
# Force extraction helpers
# ─────────────────────────────────────────────────────────────────────────────


def conservative_forces(
    potential: ConservativePotential,
    s: Tensor,
    context: Tensor | None = None,
    *,
    create_graph: bool = True,
    u_global: Tensor | None = None,
) -> Tensor:
    """F_cons = -∇_s V_cons(s, context, u_global). Shape (N, d).

    ``u_global`` is the Tier 4.1 MEGNet-style global state. When None,
    the pairwise potential receives no global vector (back-compat).
    """
    with torch.enable_grad():
        if not s.requires_grad:
            s = s.detach().requires_grad_(True)
        u = potential(s, context, u_global=u_global)
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
