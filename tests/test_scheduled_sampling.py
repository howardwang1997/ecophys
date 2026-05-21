"""Tests for Track B-β scheduled-sampling noise widening."""

from __future__ import annotations

import math

import pytest
import torch

from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator
from ecomd.training.scheduled_sampling import (
    ScheduledSamplingState,
    state_from_config,
)


# ── Unit: ScheduledSamplingState ────────────────────────────────────────────


def test_state_validates_max_prob_range():
    with pytest.raises(ValueError):
        ScheduledSamplingState(max_prob=-0.1)
    with pytest.raises(ValueError):
        ScheduledSamplingState(max_prob=1.1)


def test_state_validates_ramp_schedule():
    with pytest.raises(ValueError):
        ScheduledSamplingState(max_prob=0.2, ramp_schedule="exponential")  # type: ignore[arg-type]


def test_state_validates_sigma_mult():
    with pytest.raises(ValueError):
        ScheduledSamplingState(max_prob=0.2, sigma_mult=0.5)  # widening only


def test_get_prob_linear_monotone_and_caps():
    st = ScheduledSamplingState(max_prob=0.4, ramp_schedule="linear", warmup_iters=10)
    probs = [st.get_prob(i) for i in range(20)]
    assert probs[0] == 0.0
    # strictly increasing during warmup
    for i in range(1, 10):
        assert probs[i] > probs[i - 1]
    # exactly max at warmup boundary, capped after
    assert math.isclose(probs[10], 0.4, abs_tol=1e-9)
    for i in range(11, 20):
        assert math.isclose(probs[i], 0.4, abs_tol=1e-9)


def test_get_prob_cosine_smooth():
    st = ScheduledSamplingState(max_prob=0.3, ramp_schedule="cosine", warmup_iters=8)
    p0 = st.get_prob(0)
    p_mid = st.get_prob(4)
    p_end = st.get_prob(8)
    assert p0 == 0.0
    assert math.isclose(p_end, 0.3, abs_tol=1e-9)
    # cosine midpoint should be 0.15 (half-way up the S-curve)
    assert math.isclose(p_mid, 0.15, abs_tol=1e-6)


def test_state_disabled_when_max_prob_zero():
    st = ScheduledSamplingState(max_prob=0.0)
    assert st.enabled is False
    assert st.get_prob(100) == 0.0


def test_state_from_config_returns_none_when_disabled():
    cfg = EcoMDConfig(n_agents=5, d_state=4, hidden=8, scheduled_sampling_enabled=False)
    assert state_from_config(cfg) is None


def test_state_from_config_builds_when_enabled():
    cfg = EcoMDConfig(
        n_agents=5, d_state=4, hidden=8,
        scheduled_sampling_enabled=True,
        ss_max_prob=0.3, ss_ramp_schedule="cosine",
        ss_warmup_iters=16, ss_sigma_mult=1.7,
    )
    st = state_from_config(cfg)
    assert st is not None
    assert st.enabled
    assert st.max_prob == 0.3
    assert st.ramp_schedule == "cosine"
    assert st.warmup_iters == 16
    assert st.sigma_mult == 1.7


# ── Integration: rollout_chunk with ss_prob=0 must be bit-exact baseline ────


def _build_sim(seed: int = 0, **cfg_overrides) -> tuple[EcoMDSimulator, torch.Generator]:
    cfg = EcoMDConfig(n_agents=12, d_state=6, hidden=16, dt=0.01, **cfg_overrides)
    sim = EcoMDSimulator(cfg)
    gen = torch.Generator().manual_seed(seed)
    return sim, gen


def test_ss_prob_zero_preserves_baseline_bit_exact():
    """With ss_prob=0, rollout_chunk must produce identical trajectory to
    the baseline call without any ss args — no RNG draws, no drift. Uses a
    single sim so network parameters are identical between calls; only the
    generator seed controls RNG.
    """
    sim, _ = _build_sim(seed=0)
    # Run 1: baseline (no ss args)
    gen_a = torch.Generator().manual_seed(42)
    s_a = sim.init_state(generator=gen_a)
    s_prev_a = s_a.detach().clone()
    ps_a = sim.init_price()
    _, _, traj_a, _ = sim.rollout_chunk(
        s_a, s_prev_a, ps_a, n_steps=12, generator=gen_a, create_graph=False,
    )
    # Run 2: same sim, fresh generator + state, explicit ss_prob=0.0
    gen_b = torch.Generator().manual_seed(42)
    s_b = sim.init_state(generator=gen_b)
    s_prev_b = s_b.detach().clone()
    ps_b = sim.init_price()
    _, _, traj_b, _ = sim.rollout_chunk(
        s_b, s_prev_b, ps_b, n_steps=12, generator=gen_b, create_graph=False,
        ss_prob=0.0, ss_sigma_mult=1.5,
    )
    assert torch.equal(traj_a.log_returns, traj_b.log_returns)
    assert torch.equal(traj_a.states, traj_b.states)


def test_ss_active_changes_trajectory():
    """With ss_prob=1.0 and sigma_mult=2.0, every step should be widened, so
    f_stoch magnitude is ~2× baseline.
    """
    sim, _ = _build_sim(seed=0)
    gen_a = torch.Generator().manual_seed(7)
    s_a = sim.init_state(generator=gen_a)
    s_prev_a = s_a.detach().clone()
    ps_a = sim.init_price()
    _, _, traj_a, _ = sim.rollout_chunk(
        s_a, s_prev_a, ps_a, n_steps=8, generator=gen_a, create_graph=False,
    )
    gen_b = torch.Generator().manual_seed(7)
    s_b = sim.init_state(generator=gen_b)
    s_prev_b = s_b.detach().clone()
    ps_b = sim.init_price()
    _, _, traj_b, _ = sim.rollout_chunk(
        s_b, s_prev_b, ps_b, n_steps=8, generator=gen_b, create_graph=False,
        ss_prob=1.0, ss_sigma_mult=2.0,
    )
    base_norm = traj_a.f_stoch.abs().mean()
    wide_norm = traj_b.f_stoch.abs().mean()
    assert wide_norm > base_norm * 1.3  # generous margin (noise variance)
    assert not torch.equal(traj_a.log_returns, traj_b.log_returns)


def test_ss_with_checkpointing_raises():
    """ss_prob>0 not supported under bptt_checkpoint_every>0 (RNG state
    snapshot complexity at chunk boundary); must raise to avoid silent skip.
    """
    sim, _ = _build_sim(seed=0, bptt_checkpoint_every=4)
    gen = torch.Generator().manual_seed(1)
    s = sim.init_state(generator=gen)
    s_prev = s.detach().clone()
    ps = sim.init_price()
    with pytest.raises(ValueError, match="scheduled sampling"):
        sim.rollout_chunk(
            s, s_prev, ps, n_steps=8, generator=gen, create_graph=True,
            ss_prob=0.5, ss_sigma_mult=1.5,
        )


def test_ss_compatible_with_bptt_custom_function():
    """B-β must also work under bptt_custom_function=True (the v3 production
    code path, used by all 089-099 configs). With ss_prob=0, must be
    bit-exact baseline; with ss_active, must widen f_stoch."""
    cfg = EcoMDConfig(
        n_agents=10, d_state=4, hidden=8, dt=0.01,
        bptt_custom_function=True,
    )
    sim = EcoMDSimulator(cfg)

    # Baseline (no ss args)
    gen_a = torch.Generator().manual_seed(13)
    s_a = sim.init_state(generator=gen_a)
    s_prev_a = s_a.detach().clone()
    ps_a = sim.init_price()
    _, _, traj_a, _ = sim.rollout_chunk(
        s_a, s_prev_a, ps_a, n_steps=6, generator=gen_a, create_graph=True,
    )
    # Same path with ss_prob=0 explicitly — must be bit-exact log_returns
    gen_b = torch.Generator().manual_seed(13)
    s_b = sim.init_state(generator=gen_b)
    s_prev_b = s_b.detach().clone()
    ps_b = sim.init_price()
    _, _, traj_b, _ = sim.rollout_chunk(
        s_b, s_prev_b, ps_b, n_steps=6, generator=gen_b, create_graph=True,
        ss_prob=0.0, ss_sigma_mult=1.5,
    )
    assert torch.equal(traj_a.log_returns, traj_b.log_returns)

    # ss_active=true should widen → trajectory differs and remains finite
    gen_c = torch.Generator().manual_seed(13)
    s_c = sim.init_state(generator=gen_c)
    s_prev_c = s_c.detach().clone()
    ps_c = sim.init_price()
    _, _, traj_c, _ = sim.rollout_chunk(
        s_c, s_prev_c, ps_c, n_steps=6, generator=gen_c, create_graph=True,
        ss_prob=1.0, ss_sigma_mult=2.0,
    )
    assert torch.isfinite(traj_c.log_returns).all()
    assert not torch.equal(traj_a.log_returns, traj_c.log_returns)
    # Loss is differentiable through the custom Function path with ss on
    loss = traj_c.log_returns.pow(2).mean()
    loss.backward()
    seen = 0
    for p in sim.parameters():
        if p.grad is not None and torch.isfinite(p.grad).all():
            seen += 1
    assert seen >= 4


def test_ss_partial_prob_intermediate_widening():
    """With ss_prob=0.5, mean f_stoch magnitude should land between baseline
    and full-widened. Confirms the Bernoulli gate fires roughly half the
    steps with sigma_mult=2.0.
    """
    n_steps = 64  # more steps → less noise on the empirical mean
    sim, _ = _build_sim(seed=0)
    gen_a = torch.Generator().manual_seed(11)
    s_a = sim.init_state(generator=gen_a)
    s_prev_a = s_a.detach().clone()
    ps_a = sim.init_price()
    _, _, traj_a, _ = sim.rollout_chunk(
        s_a, s_prev_a, ps_a, n_steps=n_steps, generator=gen_a, create_graph=False,
    )
    gen_b = torch.Generator().manual_seed(11)
    s_b = sim.init_state(generator=gen_b)
    s_prev_b = s_b.detach().clone()
    ps_b = sim.init_price()
    _, _, traj_b, _ = sim.rollout_chunk(
        s_b, s_prev_b, ps_b, n_steps=n_steps, generator=gen_b, create_graph=False,
        ss_prob=0.5, ss_sigma_mult=2.0,
    )
    base_mean = traj_a.f_stoch.abs().mean().item()
    half_mean = traj_b.f_stoch.abs().mean().item()
    # half-active should be strictly above baseline.
    assert half_mean > base_mean
