"""Tests for V_pairwise, V_external, V_dissipation and force extraction."""

from __future__ import annotations

import pytest
import torch

from ecomd.models.potentials import (
    ConservativePotential,
    DissipationParams,
    DissipationPotential,
    ExternalPotential,
    PairwisePotential,
    conservative_forces,
    dissipative_forces,
)


def _seeded_state(n: int, d: int, scale: float = 0.1) -> torch.Tensor:
    g = torch.Generator().manual_seed(7)
    return torch.randn((n, d), generator=g) * scale


# ── Shape / forward ─────────────────────────────────────────────────────────


def test_pairwise_scalar_output():
    pw = PairwisePotential(d=8, hidden=16)
    s = _seeded_state(5, 8)
    u = pw(s)
    assert u.dim() == 0
    assert torch.isfinite(u)


def test_external_scalar_output():
    ext = ExternalPotential(d=8, context_dim=3, hidden=16)
    s = _seeded_state(5, 8)
    ctx = torch.tensor([0.0, 0.1, 0.0])
    u = ext(s, ctx)
    assert u.dim() == 0
    assert torch.isfinite(u)


def test_dissipation_scalar_output():
    diss = DissipationPotential(DissipationParams(lam=0.1))
    s = _seeded_state(5, 8)
    s_prev = _seeded_state(5, 8) + 0.01
    u = diss(s, s_prev)
    assert u.dim() == 0
    assert u.item() > 0


def test_external_context_dim_check():
    ext = ExternalPotential(d=4, context_dim=3)
    s = _seeded_state(3, 4)
    with pytest.raises(ValueError):
        ext(s, torch.tensor([0.0, 0.0]))


# ── Permutation invariance ──────────────────────────────────────────────────


def test_pairwise_permutation_invariant():
    """Reordering agents must not change the total energy."""
    torch.manual_seed(42)
    pw = PairwisePotential(d=8, hidden=16)
    s = _seeded_state(6, 8)
    perm = torch.tensor([3, 0, 5, 2, 4, 1])
    u1 = pw(s)
    u2 = pw(s[perm])
    assert torch.allclose(u1, u2, atol=1e-6)


def test_pairwise_force_permutation_equivariant():
    """Permuting agents permutes forces correspondingly."""
    torch.manual_seed(42)
    pw = PairwisePotential(d=8, hidden=16)
    ext = ExternalPotential(d=8, context_dim=3, hidden=16)
    pot = ConservativePotential(pw, ext)
    s = _seeded_state(6, 8)
    ctx = torch.zeros(3)
    perm = torch.tensor([3, 0, 5, 2, 4, 1])

    f_orig = conservative_forces(pot, s, ctx, create_graph=False)
    f_perm = conservative_forces(pot, s[perm], ctx, create_graph=False)
    assert torch.allclose(f_orig[perm], f_perm, atol=1e-5)


# ── Gradient flow ───────────────────────────────────────────────────────────


def test_conservative_force_shape():
    pw = PairwisePotential(d=8, hidden=16)
    ext = ExternalPotential(d=8, context_dim=3, hidden=16)
    pot = ConservativePotential(pw, ext)
    s = _seeded_state(5, 8)
    f = conservative_forces(pot, s, torch.zeros(3), create_graph=False)
    assert f.shape == s.shape
    assert torch.isfinite(f).all()


def test_dissipative_force_direction():
    """F_diss = -∇_s (λ |s - s_prev|²) = -2λ (s - s_prev). Sign-check."""
    diss = DissipationPotential(DissipationParams(lam=0.5))
    s = torch.tensor([[1.0, 2.0]])
    s_prev = torch.tensor([[0.0, 0.0]])
    f = dissipative_forces(diss, s, s_prev, create_graph=False)
    expected = -2 * 0.5 * (s - s_prev)
    assert torch.allclose(f, expected, atol=1e-5)


def test_force_has_gradient_wrt_params():
    """Forces must backprop into potential parameters (needed for training)."""
    pw = PairwisePotential(d=4, hidden=8)
    ext = ExternalPotential(d=4, context_dim=3, hidden=8)
    pot = ConservativePotential(pw, ext)
    s = _seeded_state(4, 4)
    f = conservative_forces(pot, s, torch.zeros(3), create_graph=True)
    loss = (f ** 2).sum()
    loss.backward()
    # every Linear layer should have a gradient
    seen = 0
    for p in pot.parameters():
        if p.grad is not None and torch.isfinite(p.grad).all():
            seen += 1
    assert seen >= 4  # at least 4 Linear layer weight/bias gradients
