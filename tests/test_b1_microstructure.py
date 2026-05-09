"""Unit tests for B1 — microstructure noise (bid-ask bounce).

The B1 mechanism applies an MA(1) filter to integrator noise:

    ε_t_eff = ε_t - ρ · ε_{t-1}

This produces a known lag-1 negative autocorrelation in s_next - s ≈ in
returns, mirroring real-world bid-ask bounce. Targets autocorr_returns
band [-0.1, 0.20] (v3 baseline mean is +0.38, dominated by AR(1) drift).
"""

from __future__ import annotations

import numpy as np
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


def test_microstructure_default_off_is_bit_identical() -> None:
    """rho=0 must produce exactly the same trajectory as no microstructure."""
    g_a = torch.Generator().manual_seed(11)
    g_b = torch.Generator().manual_seed(11)
    itg_a = OverdampedLangevin()  # baseline
    itg_b = OverdampedLangevin(microstructure_rho=0.0)
    s, f = torch.zeros(8, 4), torch.zeros(8, 4)
    out_a = itg_a.step(s, f, torch.zeros_like(s), T=0.05, gamma=10.0, dt=0.01, generator=g_a)
    out_b = itg_b.step(s, f, torch.zeros_like(s), T=0.05, gamma=10.0, dt=0.01, generator=g_b)
    assert torch.allclose(out_a.s_next, out_b.s_next)


def test_microstructure_induces_negative_lag1_autocorr() -> None:
    """Apply rho=0.5 over many steps; lag-1 autocorrelation of (s_next - s)
    must be clearly negative.

    Theoretical lag-1 ac of MA(1) ε_t - ρ·ε_{t-1} is -ρ/(1+ρ²) ≈ -0.4 at ρ=0.5.
    We use a long flat trajectory (no force) so the ac is dominated by noise.
    """
    itg = OverdampedLangevin(microstructure_rho=0.5)
    g = torch.Generator().manual_seed(7)
    n_steps = 500
    s = torch.zeros(64, 4)
    f = torch.zeros_like(s)
    deltas: list[torch.Tensor] = []
    for _ in range(n_steps):
        out = itg.step(s, f, torch.zeros_like(s), T=0.05, gamma=10.0, dt=0.01, generator=g)
        deltas.append((out.s_next - s).flatten())
        s = out.s_next
    arr = torch.stack(deltas).cpu().numpy()  # (n_steps, n_agents*d)
    # Per-component lag-1 ac, then average
    n_comp = arr.shape[1]
    acs = []
    for j in range(n_comp):
        x = arr[:, j]
        x = x - x.mean()
        denom = (x ** 2).sum()
        if denom == 0:
            continue
        ac = (x[1:] * x[:-1]).sum() / denom
        acs.append(ac)
    mean_ac = float(np.mean(acs))
    assert mean_ac < -0.1, f"expected lag-1 ac < -0.1 under rho=0.5, got {mean_ac:.3f}"


def test_microstructure_reset_state_clears_buffer() -> None:
    """After reset_state, the next step starts from no prev_eps memory, so
    the very first eps after reset is unfiltered.
    """
    itg = OverdampedLangevin(microstructure_rho=0.5)
    g = torch.Generator().manual_seed(0)
    s = torch.zeros(8, 4)
    f = torch.zeros_like(s)
    # Step once to populate _prev_eps
    itg.step(s, f, torch.zeros_like(s), T=0.05, gamma=10.0, dt=0.01, generator=g)
    assert itg._prev_eps is not None
    itg.reset_state()
    assert itg._prev_eps is None


def test_microstructure_simulator_finite() -> None:
    """End-to-end through the full simulator: rho=0.3 must not produce NaN."""
    cfg = _baseline_config(microstructure_rho=0.3)
    sim = EcoMDSimulator(cfg).eval()
    with torch.no_grad():
        traj = sim.run(n_steps=200, seed=42)
    r = traj.log_returns_np()[1:]
    assert r.size > 0 and np.isfinite(r).all()


def test_microstructure_combo_with_levy_finite() -> None:
    """Stack microstructure with Lévy + asym + memk: trajectory must remain finite.

    This composition is exactly what 084 / 086 / 087 combo cells will run.
    """
    cfg = _baseline_config(
        noise_dist="levy", noise_levy_alpha=1.9,
        asym_drag_alpha=0.4,
        memory_kernel_lambda=0.95, memory_kernel_strength=1.0,
        microstructure_rho=0.3,
        inner_steps_per_price=3,
    )
    sim = EcoMDSimulator(cfg).eval()
    with torch.no_grad():
        traj = sim.run(n_steps=200, seed=42)
    r = traj.log_returns_np()[1:]
    assert r.size > 0 and np.isfinite(r).all()


def test_microstructure_validation_errors() -> None:
    """rho out of [0, 1) must raise."""
    import pytest
    with pytest.raises(ValueError):
        OverdampedLangevin(microstructure_rho=1.0)
    with pytest.raises(ValueError):
        OverdampedLangevin(microstructure_rho=-0.1)
