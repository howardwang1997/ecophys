"""Tests for Track B-α Hopfield regime module + EcoMD integration."""

from __future__ import annotations

import math

import pytest
import torch

from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator
from ecomd.models.hopfield_regime import HopfieldRegime, HopfieldRegimeConfig


# ── Unit: HopfieldRegime module ─────────────────────────────────────────────


def test_construction_validates_n_prototypes():
    with pytest.raises(ValueError):
        HopfieldRegime(HopfieldRegimeConfig(n_prototypes=1))


def test_construction_validates_beta():
    with pytest.raises(ValueError):
        HopfieldRegime(HopfieldRegimeConfig(beta=0.0))


def test_init_h_shape():
    cfg = HopfieldRegimeConfig(d_regime=12)
    mod = HopfieldRegime(cfg)
    h = mod.init_h(torch.device("cpu"), torch.float32)
    assert h.shape == (12,)
    assert torch.equal(h, torch.zeros_like(h))


def test_maybe_step_no_update_outside_cadence():
    """When step_idx % update_every != 0, h must be returned unchanged."""
    cfg = HopfieldRegimeConfig(d_regime=8, n_prototypes=4, update_every=4)
    mod = HopfieldRegime(cfg)
    h = torch.randn(8)
    market_stats = torch.randn(cfg.d_input)
    out = mod.maybe_step(h, step_idx=3, market_stats=market_stats)
    assert torch.equal(out, h)


def test_maybe_step_updates_on_cadence_step():
    """At step_idx multiple of update_every, h must be replaced by an
    attention-weighted prototype sum."""
    cfg = HopfieldRegimeConfig(d_regime=8, n_prototypes=4, update_every=4)
    mod = HopfieldRegime(cfg)
    h0 = mod.init_h(torch.device("cpu"), torch.float32)
    market_stats = torch.tensor([0.5, 0.3, -0.1, 0.2])
    h1 = mod.maybe_step(h0, step_idx=4, market_stats=market_stats)
    assert h1.shape == (8,)
    # untrained init is small; h1 will be very close to zero but not all-zero
    assert torch.isfinite(h1).all()


def test_attention_sums_to_one():
    cfg = HopfieldRegimeConfig(d_regime=16, n_prototypes=5)
    mod = HopfieldRegime(cfg)
    market_stats = torch.randn(cfg.d_input)
    alpha = mod.attention(market_stats)
    assert alpha.shape == (5,)
    assert math.isclose(float(alpha.sum()), 1.0, abs_tol=1e-5)
    assert (alpha >= 0).all() and (alpha <= 1).all()


def test_read_is_identity():
    cfg = HopfieldRegimeConfig(d_regime=8)
    mod = HopfieldRegime(cfg)
    h = torch.randn(8)
    assert torch.equal(mod.read(h), h)


def test_prototype_collapse_loss_bounded():
    """Cosine-similarity-based collapse loss must lie in [-1, 1] regardless
    of prototype scale."""
    cfg = HopfieldRegimeConfig(d_regime=16, n_prototypes=4, init_gain=10.0)
    mod = HopfieldRegime(cfg)
    val = float(mod.prototype_collapse_loss())
    assert -1.0 <= val <= 1.0


def test_gradient_flows_to_prototypes():
    cfg = HopfieldRegimeConfig(d_regime=8, n_prototypes=4, update_every=1)
    mod = HopfieldRegime(cfg)
    market_stats = torch.randn(cfg.d_input)
    h = mod.maybe_step(torch.zeros(8), step_idx=0, market_stats=market_stats)
    loss = h.pow(2).sum()
    loss.backward()
    assert mod.prototypes.grad is not None
    assert torch.isfinite(mod.prototypes.grad).all()
    # query MLP also receives gradient
    for p in mod.query_mlp.parameters():
        assert p.grad is not None


def test_sharp_beta_concentrates_attention():
    """With a large β, attention should concentrate on a single prototype
    (one entry close to 1, others close to 0)."""
    torch.manual_seed(0)
    cfg = HopfieldRegimeConfig(d_regime=16, n_prototypes=4, beta=50.0, init_gain=1.0)
    mod = HopfieldRegime(cfg)
    market_stats = torch.tensor([1.0, 0.5, -0.3, 0.2])
    alpha = mod.attention(market_stats).detach()
    # max entry should dominate
    assert float(alpha.max()) > 0.7


# ── Integration: EcoMDSimulator with regime_kind="hopfield" ─────────────────


def _build_v3_cfg(**overrides) -> EcoMDConfig:
    """Minimal v3-style config with regime enabled."""
    base = dict(
        n_agents=10, d_state=6, hidden=8, dt=0.01,
        learn_gamma=False, learn_temperature=False,
        regime_enabled=True,
        regime_d=8,
        regime_update_every=2,
        regime_modulate_gamma=True,
        regime_modulate_temp=True,
        regime_modulate_kappa=False,  # not all read heads required
    )
    base.update(overrides)
    return EcoMDConfig(**base)


def test_regime_kind_auto_preserves_legacy_gru():
    """The default regime_kind='auto' (no explicit setting) must produce a
    RegimeGRU when regime_discrete_enabled=False — backward-compatibility
    contract for all 089-099 v3 configs."""
    from ecomd.models.regime_latent import RegimeGRU
    cfg = _build_v3_cfg()  # regime_kind unset → default "auto"
    sim = EcoMDSimulator(cfg)
    assert isinstance(sim.regime_gru, RegimeGRU)


def test_regime_kind_explicit_gru_same_as_auto():
    """Explicit regime_kind='gru' produces identical class to auto-default."""
    from ecomd.models.regime_latent import RegimeGRU
    cfg = _build_v3_cfg(regime_kind="gru")
    sim = EcoMDSimulator(cfg)
    assert isinstance(sim.regime_gru, RegimeGRU)


def test_regime_kind_hopfield_builds():
    cfg = _build_v3_cfg(regime_kind="hopfield", hopfield_n_prototypes=4)
    sim = EcoMDSimulator(cfg)
    assert isinstance(sim.regime_gru, HopfieldRegime)
    # prototypes Z has shape (K, d_regime)
    assert sim.regime_gru.prototypes.shape == (4, 8)


def test_regime_kind_invalid_raises():
    with pytest.raises(ValueError, match="regime_kind must be"):
        EcoMDSimulator(_build_v3_cfg(regime_kind="rnn_lstm"))


def test_gru_regression_bit_exact_to_legacy():
    """**CRITICAL GATE**: regime_kind='auto' (legacy) and regime_kind='gru'
    (explicit) must produce BIT-EXACT trajectories from identical inputs.
    If this test fails, my refactor broke v3 baseline behavior — STOP and
    diagnose before pushing.
    """
    cfg_a = _build_v3_cfg()                       # auto → gru
    cfg_b = _build_v3_cfg(regime_kind="gru")      # explicit gru

    # Same torch.manual_seed before each sim so nn.Module param init matches
    torch.manual_seed(123)
    sim_a = EcoMDSimulator(cfg_a)
    torch.manual_seed(123)
    sim_b = EcoMDSimulator(cfg_b)

    gen_a = torch.Generator().manual_seed(7)
    gen_b = torch.Generator().manual_seed(7)
    s_a = sim_a.init_state(generator=gen_a)
    s_prev_a = s_a.detach().clone()
    s_b = sim_b.init_state(generator=gen_b)
    s_prev_b = s_b.detach().clone()
    ps_a = sim_a.init_price()
    ps_b = sim_b.init_price()
    h_reg_a = sim_a.init_regime()
    h_reg_b = sim_b.init_regime()

    _, _, traj_a, _ = sim_a.rollout_chunk(
        s_a, s_prev_a, ps_a, n_steps=8, generator=gen_a, create_graph=False,
        h_regime=h_reg_a,
    )
    _, _, traj_b, _ = sim_b.rollout_chunk(
        s_b, s_prev_b, ps_b, n_steps=8, generator=gen_b, create_graph=False,
        h_regime=h_reg_b,
    )
    assert torch.equal(traj_a.log_returns, traj_b.log_returns), \
        "regime_kind='gru' broke bit-exactness vs 'auto'"
    assert torch.equal(traj_a.states, traj_b.states)


def test_hopfield_rollout_runs_without_nan():
    cfg = _build_v3_cfg(regime_kind="hopfield", hopfield_n_prototypes=4)
    torch.manual_seed(7)
    sim = EcoMDSimulator(cfg)
    gen = torch.Generator().manual_seed(1)
    s = sim.init_state(generator=gen)
    s_prev = s.detach().clone()
    ps = sim.init_price()
    h_reg = sim.init_regime()
    _, _, traj, _ = sim.rollout_chunk(
        s, s_prev, ps, n_steps=8, generator=gen, create_graph=True,
        h_regime=h_reg,
    )
    assert torch.isfinite(traj.log_returns).all()
    assert torch.isfinite(traj.states).all()
    # Gradient flow through Hopfield + force pipeline
    loss = traj.log_returns.pow(2).mean()
    loss.backward()
    # Prototypes should receive gradient (they're the heart of the Hopfield).
    proto_grad = sim.regime_gru.prototypes.grad
    assert proto_grad is not None and torch.isfinite(proto_grad).all()
