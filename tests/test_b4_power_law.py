"""Unit tests for B4 — power-law external potential.

The B4 mechanism replaces the standard MLP-only external potential with

    V_ext(s) = w_mlp · MLP(s, ctx) + w_pow · Σ_i |s_i|^α / α

For α<2, the gradient ∇V_pow ∝ sign(s) · |s|^(α-1) is sub-linear at large
|s|, allowing more excursion before the restoring force dominates. Combined
with finite noise temperature, this produces intrinsically fat-tailed
return distributions, targeting hill_tail_index (band [2, 4], where v3
+ Lévy noise both fail at <10% pass rate).
"""

from __future__ import annotations

import numpy as np
import pytest
import torch

from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator
from ecomd.models.potentials import ExternalPotential, PowerLawExternalPotential


def _baseline_config(**overrides) -> EcoMDConfig:
    base = dict(
        n_agents=64, d_state=8, hidden=16, dt=0.01,
        gamma_init=10.0, temperature_init=0.05, init_state_scale=0.1,
        pairwise_kind="stochastic_mlp", sps_k_random=8,
        learn_gamma=False, learn_temperature=False,
    )
    base.update(overrides)
    return EcoMDConfig(**base)


def test_power_law_validation_errors() -> None:
    with pytest.raises(ValueError):
        PowerLawExternalPotential(d=4, alpha=0.0)  # too small
    with pytest.raises(ValueError):
        PowerLawExternalPotential(d=4, alpha=3.0)  # too large
    with pytest.raises(ValueError):
        PowerLawExternalPotential(d=4, w_pow=-0.1)


def test_power_law_default_off_matches_external_shape() -> None:
    """w_pow=0 reduces to MLP-only; output is finite and same shape as
    ExternalPotential.
    """
    torch.manual_seed(0)
    d, c = 4, 3
    ext = ExternalPotential(d=d, context_dim=c, hidden=8)
    pwl = PowerLawExternalPotential(d=d, context_dim=c, hidden=8,
                                    alpha=2.0, w_pow=0.0, w_mlp=1.0)
    s = torch.randn(16, d)
    ctx = torch.zeros(c)
    v_ext = ext(s, ctx)
    v_pwl = pwl(s, ctx)
    assert v_ext.shape == v_pwl.shape  # both scalars
    assert torch.isfinite(v_ext) and torch.isfinite(v_pwl)


def test_power_law_force_is_sublinear_for_alpha_below_2() -> None:
    """At α=1.4, |∇V_pow| at |s|=10 should be MUCH smaller than at α=2
    (quadratic). This is the defining property: sub-linear restoring force.

    We test via autograd on the power-law term only (w_mlp=0, w_pow=1).
    """
    torch.manual_seed(0)
    pwl_subq = PowerLawExternalPotential(d=4, hidden=8, alpha=1.4, w_pow=1.0, w_mlp=0.0)
    pwl_quad = PowerLawExternalPotential(d=4, hidden=8, alpha=2.0, w_pow=1.0, w_mlp=0.0)
    s = torch.full((4, 4), 10.0, requires_grad=True)
    ctx = torch.zeros(3)
    v_subq = pwl_subq(s, ctx)
    g_subq = torch.autograd.grad(v_subq, s)[0]
    s2 = torch.full((4, 4), 10.0, requires_grad=True)
    v_quad = pwl_quad(s2, ctx)
    g_quad = torch.autograd.grad(v_quad, s2)[0]
    # |grad| at |s|=10: α=1.4 → 10^0.4 ≈ 2.51; α=2 → 10
    assert g_subq.abs().mean() < g_quad.abs().mean()
    # And sub-quadratic should be near 10^0.4 ≈ 2.51
    assert 1.5 < g_subq.abs().mean().item() < 4.0


def test_power_law_simulator_finite_run() -> None:
    """End-to-end simulator run with α=1.5 must produce finite returns."""
    cfg = _baseline_config(power_law_external=True, power_law_alpha=1.5,
                           power_law_w_pow=0.5, power_law_w_mlp=1.0)
    sim = EcoMDSimulator(cfg).eval()
    with torch.no_grad():
        traj = sim.run(n_steps=200, seed=42)
    r = traj.log_returns_np()[1:]
    assert r.size > 0 and np.isfinite(r).all()


def test_power_law_combo_with_other_v4_finite() -> None:
    """Stack B4 with Lévy + asym + memk + microstructure + adiabatic.

    This is exactly what 087's b4_alpha15_combo cell does. Verify no NaN.
    """
    cfg = _baseline_config(
        noise_dist="levy", noise_levy_alpha=1.9,
        asym_drag_alpha=0.4,
        memory_kernel_lambda=0.95, memory_kernel_strength=1.0,
        microstructure_rho=0.3,
        inner_steps_per_price=3,
        power_law_external=True, power_law_alpha=1.5,
        power_law_w_pow=0.5, power_law_w_mlp=1.0,
    )
    sim = EcoMDSimulator(cfg).eval()
    with torch.no_grad():
        traj = sim.run(n_steps=200, seed=42)
    r = traj.log_returns_np()[1:]
    assert r.size > 0 and np.isfinite(r).all()


def test_power_law_default_off_simulator_matches_baseline() -> None:
    """When power_law_external=False (default), simulator constructs the
    same MLP-only ExternalPotential it would without the flag. We check
    structural equivalence rather than bit-identical trajectories
    (different module construction order draws different random init).
    """
    cfg = _baseline_config(power_law_external=False, power_law_alpha=1.5)
    sim = EcoMDSimulator(cfg).eval()
    # Confirm the external potential is plain ExternalPotential, not power-law
    pot = sim.potential
    assert pot.external.__class__.__name__ == "ExternalPotential"


def test_power_law_on_simulator_uses_powerlaw_class() -> None:
    """When power_law_external=True, the simulator's external potential is
    a PowerLawExternalPotential instance.
    """
    cfg = _baseline_config(power_law_external=True, power_law_alpha=1.5)
    sim = EcoMDSimulator(cfg).eval()
    pot = sim.potential
    assert pot.external.__class__.__name__ == "PowerLawExternalPotential"
    assert abs(pot.external.alpha - 1.5) < 1e-6
