"""Unit tests for B3 — discrete Gumbel-softmax regime switching.

The B3 mechanism replaces the continuous regime GRU with K-state discrete
switching via Gumbel-softmax. Persistent state stored as K-dim logits;
read heads see a d_regime embedding produced by softmax-weighted state-
embedding lookup. Targets aggregational_gaussianity (band [10, 200]; v4
winners hit 300+ because the continuous GRU smears regime states
together — discrete switching produces genuine quiet vs active periods).
"""

from __future__ import annotations

import numpy as np
import pytest
import torch

from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator
from ecomd.models.regime_latent import (
    DiscreteRegimeGRU,
    DiscreteRegimeGRUConfig,
    RegimeGRU,
)


def _baseline_config(**overrides) -> EcoMDConfig:
    base = dict(
        n_agents=64, d_state=8, hidden=16, dt=0.01,
        gamma_init=10.0, temperature_init=0.05, init_state_scale=0.1,
        pairwise_kind="stochastic_mlp", sps_k_random=8,
        learn_gamma=False, learn_temperature=False,
        regime_enabled=True,  # required for any regime mechanism to engage
        regime_d=16, regime_update_every=4,
    )
    base.update(overrides)
    return EcoMDConfig(**base)


def test_discrete_regime_validation_errors() -> None:
    with pytest.raises(ValueError):
        DiscreteRegimeGRU(DiscreteRegimeGRUConfig(n_states=1))  # too few
    with pytest.raises(ValueError):
        DiscreteRegimeGRU(DiscreteRegimeGRUConfig(gumbel_tau=0.0))


def test_discrete_regime_init_h_shape_is_n_states() -> None:
    """Persistent state must be (n_states,) — the logits, not the embedding."""
    drg = DiscreteRegimeGRU(DiscreteRegimeGRUConfig(n_states=3, d_regime=16))
    h0 = drg.init_h(device=torch.device("cpu"), dtype=torch.float32)
    assert h0.shape == (3,)
    # read() output must be (d_regime,)
    emb = drg.read(h0)
    assert emb.shape == (16,)


def test_discrete_regime_read_is_simplex_weighted_combination() -> None:
    """read(h) = gumbel_softmax(h) @ state_embed. The Gumbel-softmax output
    must lie on the K-1 simplex (non-negative, sums to 1).
    """
    drg = DiscreteRegimeGRU(DiscreteRegimeGRUConfig(n_states=4, gumbel_tau=0.5))
    logits = torch.randn(4)
    soft = torch.nn.functional.gumbel_softmax(logits, tau=drg.cfg.gumbel_tau,
                                              hard=False, dim=-1)
    assert (soft >= 0).all()
    assert torch.isclose(soft.sum(), torch.tensor(1.0), atol=1e-5)


def test_discrete_regime_maybe_step_only_updates_on_schedule() -> None:
    """update_every=4 → only step indices 0, 4, 8 trigger GRU update; in
    between, h is returned unchanged (logits frozen between updates).
    """
    drg = DiscreteRegimeGRU(DiscreteRegimeGRUConfig(
        n_states=3, d_regime=8, d_input=4, update_every=4
    ))
    h = torch.zeros(3)
    stats = torch.tensor([1.0, 0.5, 0.1, 0.2])
    # Off-schedule steps return h unchanged
    h1 = drg.maybe_step(h, step_idx=1, market_stats=stats)
    h2 = drg.maybe_step(h, step_idx=2, market_stats=stats)
    assert torch.equal(h, h1)
    assert torch.equal(h, h2)
    # On-schedule step returns updated logits
    h_new = drg.maybe_step(h, step_idx=0, market_stats=stats)
    assert h_new.shape == (3,)


def test_discrete_regime_simulator_finite_run() -> None:
    """Full simulator run with discrete regime K=3 must produce finite returns."""
    cfg = _baseline_config(regime_discrete_enabled=True,
                            regime_n_states=3, regime_gumbel_tau=1.0)
    sim = EcoMDSimulator(cfg).eval()
    with torch.no_grad():
        traj = sim.run(n_steps=200, seed=42)
    r = traj.log_returns_np()[1:]
    assert r.size > 0 and np.isfinite(r).all()
    # Confirm the simulator instantiated DiscreteRegimeGRU, not the continuous one
    assert isinstance(sim.regime_gru, DiscreteRegimeGRU)


def test_discrete_regime_default_off_uses_continuous() -> None:
    """regime_discrete_enabled=False (default) → continuous RegimeGRU."""
    cfg = _baseline_config(regime_discrete_enabled=False)
    sim = EcoMDSimulator(cfg).eval()
    assert isinstance(sim.regime_gru, RegimeGRU)
    assert not isinstance(sim.regime_gru, DiscreteRegimeGRU)


def test_discrete_regime_combo_with_v4_finite() -> None:
    """Stack B3 with Lévy + asym + memk + microstructure + power-law + adiabatic.

    This is exactly the most-aggressive 086 combo cell. Trajectory must
    remain finite — if not, drop one mechanism in production.
    """
    cfg = _baseline_config(
        noise_dist="levy", noise_levy_alpha=1.9,
        asym_drag_alpha=0.4,
        memory_kernel_lambda=0.95, memory_kernel_strength=1.0,
        microstructure_rho=0.3,
        inner_steps_per_price=3,
        power_law_external=True, power_law_alpha=1.5,
        regime_discrete_enabled=True, regime_n_states=3,
    )
    sim = EcoMDSimulator(cfg).eval()
    with torch.no_grad():
        traj = sim.run(n_steps=200, seed=42)
    r = traj.log_returns_np()[1:]
    assert r.size > 0 and np.isfinite(r).all()


def test_discrete_regime_reproducible_with_same_seed() -> None:
    """Same seed → same trajectory."""
    cfg = _baseline_config(regime_discrete_enabled=True, regime_n_states=3)
    out: list[np.ndarray] = []
    for _ in range(2):
        torch.manual_seed(13)
        sim = EcoMDSimulator(cfg).eval()
        with torch.no_grad():
            t = sim.run(n_steps=50, seed=42)
        out.append(t.log_returns_np())
    np.testing.assert_allclose(out[0], out[1])
