"""Unit tests for M1.2 — Zumbach causal-asymmetry feedback.

The mechanism boosts the integrator's noise scale on each step by an EMA of
past price-level r² (or downside r² in mode='downside'). Past-only by
construction (causal EMA), this is the time-asymmetric coupling that
produces D(τ) > 0 in the zumbach_asymmetry stylized fact. Targets the v3
architectural floor where every cell shows zumbach_asymmetry μ < 0
(wrong sign vs band [+0.001, +0.5]).
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


def test_zumbach_default_off_is_bit_identical() -> None:
    """Both knobs zero must produce exactly the same trajectory as baseline."""
    g_a = torch.Generator().manual_seed(11)
    g_b = torch.Generator().manual_seed(11)
    itg_a = OverdampedLangevin()
    itg_b = OverdampedLangevin(zumbach_feedback_lambda=0.0, zumbach_feedback_strength=0.0)
    s, f = torch.zeros(8, 4), torch.zeros(8, 4)
    out_a = itg_a.step(s, f, torch.zeros_like(s), T=0.05, gamma=10.0, dt=0.01, generator=g_a)
    out_b = itg_b.step(s, f, torch.zeros_like(s), T=0.05, gamma=10.0, dt=0.01, generator=g_b)
    assert torch.allclose(out_a.s_next, out_b.s_next)


def test_zumbach_only_one_knob_set_is_off() -> None:
    """Either lambda=0 alone OR strength=0 alone disables the mechanism."""
    g_a = torch.Generator().manual_seed(3)
    g_b = torch.Generator().manual_seed(3)
    itg_a = OverdampedLangevin()
    itg_b = OverdampedLangevin(zumbach_feedback_lambda=0.9, zumbach_feedback_strength=0.0)
    s, f = torch.zeros(8, 4), torch.zeros(8, 4)
    out_a = itg_a.step(s, f, torch.zeros_like(s), T=0.05, gamma=10.0, dt=0.01, generator=g_a)
    out_b = itg_b.step(s, f, torch.zeros_like(s), T=0.05, gamma=10.0, dt=0.01, generator=g_b)
    assert torch.allclose(out_a.s_next, out_b.s_next)


def test_zumbach_ema_updates_via_price_signal_abs() -> None:
    """EMA must track past r² when mode='abs' (any sign contributes)."""
    itg = OverdampedLangevin(
        zumbach_feedback_lambda=0.5, zumbach_feedback_strength=1.0,
        zumbach_feedback_mode="abs",
    )
    assert itg._zumbach_ema == 0.0
    itg.update_price_signal(0.1)
    # ema = 0.5 * 0 + 0.5 * 0.01 = 0.005
    assert abs(itg._zumbach_ema - 0.005) < 1e-9
    itg.update_price_signal(-0.2)
    # ema = 0.5 * 0.005 + 0.5 * 0.04 = 0.0225
    assert abs(itg._zumbach_ema - 0.0225) < 1e-9


def test_zumbach_ema_updates_via_price_signal_downside() -> None:
    """In mode='downside', only negative returns contribute."""
    itg = OverdampedLangevin(
        zumbach_feedback_lambda=0.5, zumbach_feedback_strength=1.0,
        zumbach_feedback_mode="downside",
    )
    itg.update_price_signal(0.1)  # positive: contrib=0
    assert itg._zumbach_ema == 0.0
    itg.update_price_signal(-0.2)  # negative: contrib=0.04
    # ema = 0.5 * 0 + 0.5 * 0.04 = 0.02
    assert abs(itg._zumbach_ema - 0.02) < 1e-9
    itg.update_price_signal(0.3)  # positive: contrib=0
    # ema = 0.5 * 0.02 + 0.5 * 0 = 0.01
    assert abs(itg._zumbach_ema - 0.01) < 1e-9


def test_zumbach_boost_increases_noise_scale() -> None:
    """When _zumbach_ema is non-zero, noise displacement magnitude must scale up.

    Set up identical seeds, identical force, identical noise. Run one step
    with EMA=0 (no boost), one step with EMA pre-loaded (boost active).
    The post-boost displacement magnitude should exceed the no-boost one.
    """
    itg_off = OverdampedLangevin()
    itg_on = OverdampedLangevin(zumbach_feedback_lambda=0.5, zumbach_feedback_strength=50.0)
    # Pre-load the on-EMA via price signal updates so the boost is non-trivial.
    # |r|=0.3, r²=0.09. EMA saturates ~0.09 within ~5 updates.
    # Boost = strength × ema = 50 × 0.09 = 4.5 → noise_scale ×= 5.5.
    for _ in range(10):
        itg_on.update_price_signal(-0.3)
    assert itg_on._zumbach_ema > 0.05

    g_off = torch.Generator().manual_seed(5)
    g_on = torch.Generator().manual_seed(5)
    s = torch.zeros(64, 4)
    f = torch.zeros_like(s)
    out_off = itg_off.step(s, f, torch.zeros_like(s),
                           T=0.05, gamma=10.0, dt=0.01, generator=g_off)
    out_on = itg_on.step(s, f, torch.zeros_like(s),
                         T=0.05, gamma=10.0, dt=0.01, generator=g_on)
    mag_off = float((out_off.s_next - s).abs().mean())
    mag_on = float((out_on.s_next - s).abs().mean())
    assert mag_on > 1.5 * mag_off, (
        f"zumbach boost should enlarge noise displacement: off={mag_off:.6f}, on={mag_on:.6f}"
    )


def test_zumbach_reset_state_clears_ema() -> None:
    itg = OverdampedLangevin(zumbach_feedback_lambda=0.5, zumbach_feedback_strength=1.0)
    itg.update_price_signal(0.5)
    assert itg._zumbach_ema > 0.0
    itg.reset_state()
    assert itg._zumbach_ema == 0.0


def test_zumbach_validation_errors() -> None:
    with pytest.raises(ValueError):
        OverdampedLangevin(zumbach_feedback_lambda=1.0)
    with pytest.raises(ValueError):
        OverdampedLangevin(zumbach_feedback_lambda=-0.1)
    with pytest.raises(ValueError):
        OverdampedLangevin(zumbach_feedback_strength=-0.1)
    with pytest.raises(ValueError):
        OverdampedLangevin(zumbach_feedback_mode="invalid")


def test_zumbach_simulator_finite() -> None:
    """End-to-end smoke through full simulator: must not produce NaN."""
    cfg = _baseline_config(
        zumbach_feedback_lambda=0.9, zumbach_feedback_strength=0.5,
        zumbach_feedback_mode="abs",
    )
    sim = EcoMDSimulator(cfg).eval()
    with torch.no_grad():
        traj = sim.run(n_steps=200, seed=42)
    r = traj.log_returns_np()[1:]
    assert r.size > 0 and np.isfinite(r).all()


def test_zumbach_downside_simulator_finite() -> None:
    """Downside-only mode must also produce finite trajectory."""
    cfg = _baseline_config(
        zumbach_feedback_lambda=0.95, zumbach_feedback_strength=1.0,
        zumbach_feedback_mode="downside",
    )
    sim = EcoMDSimulator(cfg).eval()
    with torch.no_grad():
        traj = sim.run(n_steps=200, seed=42)
    r = traj.log_returns_np()[1:]
    assert r.size > 0 and np.isfinite(r).all()


def test_zumbach_combo_with_other_mechanisms_finite() -> None:
    """Stack Zumbach + AR(1) whitening + asym + B3 (the 089 attribution combo)."""
    cfg = _baseline_config(
        asym_drag_alpha=0.6,
        ar1_whiten_lambda=0.9, ar1_whiten_strength=0.3,
        zumbach_feedback_lambda=0.95, zumbach_feedback_strength=0.5,
        regime_enabled=True, regime_discrete_enabled=True, regime_n_states=3,
    )
    sim = EcoMDSimulator(cfg).eval()
    with torch.no_grad():
        traj = sim.run(n_steps=200, seed=42)
    r = traj.log_returns_np()[1:]
    assert r.size > 0 and np.isfinite(r).all()
