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
