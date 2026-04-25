"""Tests for v3 architecture features (regime, twopop, multi-scale Hawkes, entropy)."""

from __future__ import annotations

import torch

from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator
from ecomd.models.price_formation import ExcessDemandParams, ExcessDemandPrice
from ecomd.models.regime_latent import RegimeGRU, RegimeGRUConfig, RegimeReadHead
from ecomd.eval.entropy_production import (
    compute_entropy_production_stats,
    entropy_production_per_step,
    per_channel_force_decomposition,
)


# ─────────────────────────────────────────────────────────────────────────────
# Multi-scale Hawkes
# ─────────────────────────────────────────────────────────────────────────────


def test_multi_scale_hawkes_two_memories():
    p = ExcessDemandParams(
        hawkes_alpha=0.1, hawkes_kappa=0.3,
        hawkes_alpha_long=0.01, hawkes_kappa_long=0.2,
    )
    pf = ExcessDemandPrice(p)
    state = pf.init_state(torch.device("cpu"), torch.float32)
    assert state.hawkes_memory is not None
    assert state.hawkes_memory_long is not None
    assert float(state.hawkes_memory) == 0.0
    assert float(state.hawkes_memory_long) == 0.0


def test_multi_scale_hawkes_long_memory_decays_slower():
    """Long-memory channel should decay slower than short."""
    p = ExcessDemandParams(
        hawkes_alpha=0.5, hawkes_kappa=0.0,        # short: fast EMA, no excitation
        hawkes_alpha_long=0.05, hawkes_kappa_long=0.0,  # long: slow EMA
    )
    pf = ExcessDemandPrice(p)
    state = pf.init_state(torch.device("cpu"), torch.float32)
    s = torch.randn(5, 3) * 0.1
    sn = s + torch.randn_like(s) * 0.5  # injection
    g = torch.Generator().manual_seed(0)
    out = pf.step(state, s, sn, generator=g)
    # After one step, long memory should be smaller (slower α)
    assert float(out.state.hawkes_memory_long) < float(out.state.hawkes_memory)


def test_multi_scale_hawkes_disabled_when_alphas_zero():
    """No long-memory when both kappa_long and alpha_long are 0."""
    p = ExcessDemandParams(hawkes_alpha=0.0, hawkes_kappa=0.0,
                           hawkes_alpha_long=0.0, hawkes_kappa_long=0.0)
    pf = ExcessDemandPrice(p)
    state = pf.init_state(torch.device("cpu"), torch.float32)
    assert state.hawkes_memory is None
    assert state.hawkes_memory_long is None


# ─────────────────────────────────────────────────────────────────────────────
# Regime GRU
# ─────────────────────────────────────────────────────────────────────────────


def test_regime_gru_only_steps_every_k():
    """Cell should not update on non-multiple-of-k steps."""
    g = RegimeGRU(RegimeGRUConfig(d_regime=4, d_input=3, update_every=4))
    h0 = g.init_h(torch.device("cpu"), torch.float32)
    stats = torch.tensor([1.0, 0.5, 0.1])
    h1 = g.maybe_step(h0, step_idx=1, market_stats=stats)
    h2 = g.maybe_step(h0, step_idx=4, market_stats=stats)
    # step 1 should be no-op (returns h0 unchanged); step 4 should update
    assert torch.allclose(h0, h1)
    assert not torch.allclose(h0, h2)


def test_regime_read_head_returns_positive_multiplier():
    head = RegimeReadHead(d_regime=4)
    h = torch.randn(4) * 0.1
    mul = head(h)
    assert mul.dim() == 0
    assert float(mul) > 0


# ─────────────────────────────────────────────────────────────────────────────
# Two-population per-type γ, T
# ─────────────────────────────────────────────────────────────────────────────


def test_twopop_assigns_persistent_types():
    cfg = EcoMDConfig(n_agents=20, d_state=8, hidden=16, twopop_enabled=True,
                      twopop_gamma_scale=(0.5, 1.0, 1.5, 2.0),
                      twopop_temp_scale=(2.0, 1.0, 0.5, 0.5))
    sim = EcoMDSimulator(cfg)
    assert sim.twopop_type_idx is not None
    assert sim.twopop_type_idx.shape == (20,)
    # All values in [0, K)
    assert int(sim.twopop_type_idx.max()) < 4
    assert int(sim.twopop_type_idx.min()) >= 0


def test_twopop_run_completes():
    cfg = EcoMDConfig(n_agents=10, d_state=4, hidden=8, twopop_enabled=True,
                      twopop_gamma_scale=(0.5, 1.5, 1.0, 2.0),
                      twopop_temp_scale=(2.0, 0.5, 1.0, 0.5))
    sim = EcoMDSimulator(cfg)
    traj = sim.run(n_steps=10, seed=0)
    assert traj.log_returns.shape == (10,)


# ─────────────────────────────────────────────────────────────────────────────
# Regime + simulator integration
# ─────────────────────────────────────────────────────────────────────────────


def test_regime_simulator_run_completes():
    cfg = EcoMDConfig(n_agents=15, d_state=8, hidden=16,
                      regime_enabled=True, regime_d=8, regime_update_every=2)
    sim = EcoMDSimulator(cfg)
    # Verify the heads exist
    assert sim.regime_gru is not None
    assert sim.regime_head_gamma is not None
    assert sim.regime_head_T is not None
    assert sim.regime_head_kappa is not None
    traj = sim.run(n_steps=20, seed=0)
    assert traj.log_returns.shape == (20,)


def test_regime_disabled_default():
    cfg = EcoMDConfig(n_agents=15, d_state=8, hidden=16)
    sim = EcoMDSimulator(cfg)
    assert sim.regime_gru is None
    assert sim.init_regime() is None


def test_regime_grad_flows_through_heads():
    cfg = EcoMDConfig(n_agents=10, d_state=4, hidden=8, learn_gamma=False, learn_temperature=False,
                      regime_enabled=True, regime_d=4, regime_update_every=2)
    sim = EcoMDSimulator(cfg)
    g = torch.Generator().manual_seed(0)
    s = sim.init_state(generator=g)
    s_prev = s.clone()
    p = sim.init_price()
    h = sim.init_regime()
    _, _, traj, _ = sim.rollout_chunk(s, s_prev, p, n_steps=8, generator=g, h_regime=h)
    loss = traj.log_returns.pow(2).mean()
    loss.backward()
    grad_seen = any(
        ("regime" in name) and (p.grad is not None) and (p.grad.abs().sum() > 0)
        for name, p in sim.named_parameters()
    )
    assert grad_seen, "no grad reached regime parameters"


# ─────────────────────────────────────────────────────────────────────────────
# Entropy production
# ─────────────────────────────────────────────────────────────────────────────


def test_entropy_production_stats_basic():
    cfg = EcoMDConfig(n_agents=15, d_state=4, hidden=8)
    sim = EcoMDSimulator(cfg)
    traj = sim.run(n_steps=50, seed=0)
    stats = compute_entropy_production_stats(traj, T_eff=float(sim.temperature.item()))
    assert stats.sigma_dot_per_step.shape == (50,)
    assert stats.sigma_dot_per_particle.shape == (15,)


def test_entropy_production_with_types():
    cfg = EcoMDConfig(n_agents=20, d_state=4, hidden=8, twopop_enabled=True,
                      twopop_gamma_scale=(0.5, 1.5, 1.0, 2.0),
                      twopop_temp_scale=(2.0, 0.5, 1.0, 0.5))
    sim = EcoMDSimulator(cfg)
    traj = sim.run(n_steps=30, seed=0)
    stats = compute_entropy_production_stats(
        traj,
        T_eff=float(sim.temperature.item()),
        type_idx=sim.twopop_type_idx.cpu().numpy(),
    )
    # Should have entries for at least one type
    assert len(stats.sigma_dot_by_type) >= 1
    assert all(isinstance(k, int) for k in stats.sigma_dot_by_type)


def test_force_decomposition():
    cfg = EcoMDConfig(n_agents=10, d_state=4, hidden=8)
    sim = EcoMDSimulator(cfg)
    traj = sim.run(n_steps=20, seed=0)
    fcd = per_channel_force_decomposition(traj)
    for key in ("f_cons_mean_abs", "f_diss_mean_abs", "f_stoch_mean_abs", "velocity_mean_abs"):
        assert key in fcd
        assert fcd[key] >= 0


# ─────────────────────────────────────────────────────────────────────────────
# Combined: regime + twopop + multi-scale Hawkes all on
# ─────────────────────────────────────────────────────────────────────────────


def test_all_features_combined():
    """The mother-of-all configurations: regime + twopop + multi-scale Hawkes."""
    cfg = EcoMDConfig(
        n_agents=20, d_state=8, hidden=16,
        price_formation_kwargs={
            "hawkes_alpha": 0.1, "hawkes_kappa": 0.3,
            "hawkes_alpha_long": 0.01, "hawkes_kappa_long": 0.1,
        },
        regime_enabled=True, regime_d=8, regime_update_every=4,
        twopop_enabled=True,
        twopop_gamma_scale=(0.5, 1.5, 1.0, 2.0),
        twopop_temp_scale=(2.0, 0.5, 1.0, 0.5),
    )
    sim = EcoMDSimulator(cfg)
    traj = sim.run(n_steps=40, seed=0)
    assert traj.log_returns.shape == (40,)
