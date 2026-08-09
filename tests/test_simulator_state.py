from __future__ import annotations

import io

import pytest
import torch

from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator, SimulatorState


def _stateful_config(*, jumps: bool = True) -> EcoMDConfig:
    return EcoMDConfig(
        n_agents=10,
        d_state=4,
        hidden=8,
        dt=0.05,
        pairwise_kind="stochastic_mlp",
        sps_k_random=3,
        sps_resample_per_step=False,
        regime_enabled=True,
        regime_d=4,
        regime_update_every=2,
        agent_memory_enabled=True,
        agent_memory_d=4,
        agent_memory_update_every=2,
        global_state_enabled=True,
        global_state_d=4,
        global_state_update_every=3,
        global_state_into_pair=True,
        memory_kernel_lambda=0.8,
        memory_kernel_strength=0.2,
        microstructure_rho=0.1,
        ar1_whiten_lambda=0.8,
        ar1_whiten_strength=0.1,
        zumbach_feedback_lambda=0.8,
        zumbach_feedback_strength=0.1,
        multi_timescale_enabled=True,
        timescale_fast_frac=0.6,
        timescale_slow_freq=3,
        jump_lambda=6.0 if jumps else 0.0,
        jump_scale=0.03 if jumps else 0.0,
    )


def _assert_state_equal(left: SimulatorState, right: SimulatorState) -> None:
    torch.testing.assert_close(left.s, right.s, rtol=0.0, atol=0.0)
    torch.testing.assert_close(left.s_prev, right.s_prev, rtol=0.0, atol=0.0)
    torch.testing.assert_close(
        left.price_state.log_price, right.price_state.log_price, rtol=0.0, atol=0.0
    )
    torch.testing.assert_close(
        left.price_state.last_log_return,
        right.price_state.last_log_return,
        rtol=0.0,
        atol=0.0,
    )
    torch.testing.assert_close(
        left.price_state.volatility, right.price_state.volatility, rtol=0.0, atol=0.0
    )
    assert left.step_idx == right.step_idx
    assert left.price_state.step == right.price_state.step
    assert left.fundamental == right.fundamental
    for lhs, rhs in (
        (left.h_regime, right.h_regime),
        (left.h_agent, right.h_agent),
        (left.h_global, right.h_global),
        (left.integrator.mem_ema, right.integrator.mem_ema),
        (left.integrator.prev_eps, right.integrator.prev_eps),
        (left.integrator.drift_ema, right.integrator.drift_ema),
        (left.pairwise_cache.edges, right.pairwise_cache.edges),
        (left.rng_state, right.rng_state),
    ):
        assert (lhs is None) == (rhs is None)
        if lhs is not None and rhs is not None:
            torch.testing.assert_close(lhs, rhs, rtol=0.0, atol=0.0)
    assert left.integrator.last_price_delta == right.integrator.last_price_delta
    assert left.integrator.zumbach_ema == right.integrator.zumbach_ema
    assert left.pairwise_cache.kind == right.pairwise_cache.kind
    assert left.pairwise_cache.steps_since_refresh == right.pairwise_cache.steps_since_refresh
    assert left.shock_schedule == right.shock_schedule
    assert left.shock_dyn == right.shock_dyn


def test_monolithic_equals_arbitrary_state_complete_chunks() -> None:
    torch.manual_seed(17)
    sim = EcoMDSimulator(_stateful_config())
    sim._shock_schedule = {
        3: {"type": "temperature_spike", "mult": 1.7, "dur": 4},
        9: {"type": "state_kick", "frac": 0.2, "mag": 1.5},
    }
    initial = sim.init_simulator_state(seed=31415)

    full_state, full_traj = sim.rollout_state(
        initial.clone(), 13, create_graph=False
    )

    chunk_state = initial.clone()
    returns = []
    for length in (2, 5, 1, 5):
        chunk_state, traj = sim.rollout_state(
            chunk_state, length, create_graph=False
        )
        returns.append(traj.log_returns)

    torch.testing.assert_close(
        full_traj.log_returns, torch.cat(returns), rtol=0.0, atol=0.0
    )
    _assert_state_equal(full_state, chunk_state)


def test_checkpoint_resume_equals_uninterrupted() -> None:
    torch.manual_seed(23)
    sim = EcoMDSimulator(_stateful_config())
    initial = sim.init_simulator_state(seed=2718)
    expected, expected_traj = sim.rollout_state(
        initial.clone(), 12, create_graph=False
    )

    midpoint, first = sim.rollout_state(initial.clone(), 5, create_graph=False)
    buffer = io.BytesIO()
    torch.save(midpoint.to_checkpoint(), buffer)
    buffer.seek(0)
    restored = SimulatorState.from_checkpoint(torch.load(buffer, weights_only=False))
    actual, second = sim.rollout_state(restored, 7, create_graph=False)

    torch.testing.assert_close(
        expected_traj.log_returns,
        torch.cat([first.log_returns, second.log_returns]),
        rtol=0.0,
        atol=0.0,
    )
    _assert_state_equal(expected, actual)


def test_detach_boundary_does_not_change_forward_dynamics() -> None:
    torch.manual_seed(24)
    sim = EcoMDSimulator(_stateful_config())
    initial = sim.init_simulator_state(seed=1414)
    midpoint, _ = sim.rollout_state(initial, 5, create_graph=True)

    attached, attached_traj = sim.rollout_state(
        midpoint.clone(), 3, create_graph=False
    )
    detached, detached_traj = sim.rollout_state(
        midpoint.detached(), 3, create_graph=False
    )

    torch.testing.assert_close(
        attached_traj.log_returns, detached_traj.log_returns, rtol=0.0, atol=0.0
    )
    _assert_state_equal(attached, detached)


def test_attached_chunks_match_monolithic_parameter_gradients() -> None:
    torch.manual_seed(25)
    sim = EcoMDSimulator(_stateful_config(jumps=False))
    initial = sim.init_simulator_state(seed=1515)
    parameters = tuple(parameter for parameter in sim.parameters() if parameter.requires_grad)

    _, full_traj = sim.rollout_state(initial.clone(), 6, create_graph=True)
    full_loss = full_traj.log_returns.square().sum()
    full_grads = torch.autograd.grad(full_loss, parameters, allow_unused=True)

    chunk_state = initial.clone()
    chunk_returns = []
    for length in (2, 1, 3):
        chunk_state, trajectory = sim.rollout_state(
            chunk_state, length, create_graph=True
        )
        chunk_returns.append(trajectory.log_returns)
    chunk_loss = torch.cat(chunk_returns).square().sum()
    chunk_grads = torch.autograd.grad(chunk_loss, parameters, allow_unused=True)

    for full_grad, chunk_grad in zip(full_grads, chunk_grads, strict=True):
        assert (full_grad is None) == (chunk_grad is None)
        if full_grad is not None and chunk_grad is not None:
            torch.testing.assert_close(full_grad, chunk_grad, rtol=1e-6, atol=1e-8)


def test_jump_forward_law_does_not_depend_on_create_graph() -> None:
    torch.manual_seed(29)
    sim = EcoMDSimulator(_stateful_config(jumps=True))
    initial = sim.init_simulator_state(seed=1618)

    inference_state, inference_traj = sim.rollout_state(
        initial.clone(), 8, create_graph=False
    )
    training_state, training_traj = sim.rollout_state(
        initial.clone(), 8, create_graph=True
    )

    torch.testing.assert_close(
        inference_traj.log_returns, training_traj.log_returns, rtol=0.0, atol=0.0
    )
    torch.testing.assert_close(
        inference_state.s, training_state.s, rtol=0.0, atol=0.0
    )
    training_traj.log_returns.square().mean().backward()
    assert any(parameter.grad is not None for parameter in sim.parameters())


def test_clock_mismatch_hard_fails() -> None:
    sim = EcoMDSimulator(_stateful_config(jumps=False))
    state = sim.init_simulator_state(seed=7)
    state.step_idx = 1
    with pytest.raises(ValueError, match="absolute clock mismatch"):
        sim.rollout_state(state, 1, create_graph=False)
