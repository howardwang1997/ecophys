"""Unit tests for M1.1 — AR(1) drift whitening.

The mechanism subtracts a fraction of EMA(past drift) from the current
per-agent drift, acting as a high-pass filter. Targets the v3 architectural
floor on `autocorr_returns` (every cell μ ≈ 0.4 vs band [-0.1, 0.2];
returns are AR(1) ρ̂≈0.9). See plan at ~/.claude/plans/curried-cuddling-cloud.md.
"""

from __future__ import annotations

import numpy as np
import pytest
import torch

from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator
from ecomd.physics.integrator import OverdampedLangevin


def _baseline_config(**overrides) -> EcoMDConfig:
    base = dict(
        n_agents=64, d_state=8, hidden=16, dt=0.01,
        gamma_init=10.0, temperature_init=0.05, init_state_scale=0.1,
        pairwise_kind="stochastic_mlp", sps_k_random=8,
        learn_gamma=False, learn_temperature=False,
    )
    base.update(overrides)
    return EcoMDConfig(**base)


def test_ar1_default_off_is_bit_identical() -> None:
    """Both knobs zero must produce exactly the same trajectory as baseline."""
    g_a = torch.Generator().manual_seed(11)
    g_b = torch.Generator().manual_seed(11)
    itg_a = OverdampedLangevin()
    itg_b = OverdampedLangevin(ar1_whiten_lambda=0.0, ar1_whiten_strength=0.0)
    s, f = torch.zeros(8, 4), torch.zeros(8, 4)
    out_a = itg_a.step(s, f, torch.zeros_like(s), T=0.05, gamma=10.0, dt=0.01, generator=g_a)
    out_b = itg_b.step(s, f, torch.zeros_like(s), T=0.05, gamma=10.0, dt=0.01, generator=g_b)
    assert torch.allclose(out_a.s_next, out_b.s_next)


def test_ar1_only_one_knob_set_is_off() -> None:
    """Either lambda=0 alone OR strength=0 alone disables the mechanism."""
    g_a = torch.Generator().manual_seed(3)
    g_b = torch.Generator().manual_seed(3)
    g_c = torch.Generator().manual_seed(3)
    itg_a = OverdampedLangevin()
    itg_b = OverdampedLangevin(ar1_whiten_lambda=0.9, ar1_whiten_strength=0.0)
    itg_c = OverdampedLangevin(ar1_whiten_lambda=0.0, ar1_whiten_strength=0.5)
    s = torch.zeros(8, 4)
    f = torch.ones(8, 4) * 0.1
    out_a = itg_a.step(s, f, torch.zeros_like(s), T=0.05, gamma=10.0, dt=0.01, generator=g_a)
    out_b = itg_b.step(s, f, torch.zeros_like(s), T=0.05, gamma=10.0, dt=0.01, generator=g_b)
    out_c = itg_c.step(s, f, torch.zeros_like(s), T=0.05, gamma=10.0, dt=0.01, generator=g_c)
    assert torch.allclose(out_a.s_next, out_b.s_next)
    assert torch.allclose(out_a.s_next, out_c.s_next)


def test_ar1_whitening_reduces_drift_autocorr() -> None:
    """With a constant force (pure drift), whitening should drive cumulative
    drift toward zero compared to no whitening, because the high-pass filter
    removes the DC component.
    """
    n_steps, n_agents, d = 200, 32, 4
    f_const = torch.ones(n_agents, d) * 0.5  # constant external drift
    g_base = torch.Generator().manual_seed(42)
    g_whit = torch.Generator().manual_seed(42)
    itg_base = OverdampedLangevin()
    itg_whit = OverdampedLangevin(ar1_whiten_lambda=0.9, ar1_whiten_strength=0.9)
    s_base = torch.zeros(n_agents, d)
    s_whit = torch.zeros(n_agents, d)
    cum_drift_base = torch.zeros(n_agents, d)
    cum_drift_whit = torch.zeros(n_agents, d)
    for _ in range(n_steps):
        out_base = itg_base.step(s_base, f_const, torch.zeros_like(s_base),
                                 T=0.0, gamma=10.0, dt=0.01, generator=g_base)
        out_whit = itg_whit.step(s_whit, f_const, torch.zeros_like(s_whit),
                                 T=0.0, gamma=10.0, dt=0.01, generator=g_whit)
        cum_drift_base = cum_drift_base + (out_base.s_next - s_base)
        cum_drift_whit = cum_drift_whit + (out_whit.s_next - s_whit)
        s_base = out_base.s_next
        s_whit = out_whit.s_next
    cum_base = float(cum_drift_base.abs().mean())
    cum_whit = float(cum_drift_whit.abs().mean())
    # Whitening should suppress accumulated drift by at least 50%.
    assert cum_whit < 0.5 * cum_base, (
        f"whitening did not reduce drift accumulation: "
        f"baseline cum |drift|={cum_base:.4f}, whitened={cum_whit:.4f}"
    )


def test_ar1_reset_state_clears_buffer() -> None:
    itg = OverdampedLangevin(ar1_whiten_lambda=0.9, ar1_whiten_strength=0.5)
    g = torch.Generator().manual_seed(0)
    s = torch.zeros(8, 4)
    f = torch.ones(8, 4)
    itg.step(s, f, torch.zeros_like(s), T=0.05, gamma=10.0, dt=0.01, generator=g)
    assert itg._drift_ema is not None
    itg.reset_state()
    assert itg._drift_ema is None


def test_ar1_validation_errors() -> None:
    with pytest.raises(ValueError):
        OverdampedLangevin(ar1_whiten_lambda=1.0)
    with pytest.raises(ValueError):
        OverdampedLangevin(ar1_whiten_lambda=-0.1)
    with pytest.raises(ValueError):
        OverdampedLangevin(ar1_whiten_strength=-0.1)
    with pytest.raises(ValueError):
        OverdampedLangevin(ar1_whiten_strength=1.5)


def test_ar1_simulator_finite() -> None:
    """End-to-end smoke through full simulator: must not produce NaN."""
    cfg = _baseline_config(ar1_whiten_lambda=0.9, ar1_whiten_strength=0.3)
    sim = EcoMDSimulator(cfg).eval()
    with torch.no_grad():
        traj = sim.run(n_steps=200, seed=42)
    r = traj.log_returns_np()[1:]
    assert r.size > 0 and np.isfinite(r).all()


def test_ar1_combo_with_other_mechanisms_finite() -> None:
    """Stack AR(1) whitening with Lévy + asym + memk + microstructure."""
    cfg = _baseline_config(
        noise_dist="levy", noise_levy_alpha=1.9,
        asym_drag_alpha=0.4,
        memory_kernel_lambda=0.95, memory_kernel_strength=0.5,
        microstructure_rho=0.2,
        ar1_whiten_lambda=0.9, ar1_whiten_strength=0.3,
    )
    sim = EcoMDSimulator(cfg).eval()
    with torch.no_grad():
        traj = sim.run(n_steps=200, seed=42)
    r = traj.log_returns_np()[1:]
    assert r.size > 0 and np.isfinite(r).all()
