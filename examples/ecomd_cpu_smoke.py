"""Deterministic, data-free EcoMD research-preview smoke check."""

from __future__ import annotations

import hashlib
import io
import json

import torch

from ecomd import __version__
from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator, SimulatorState


def _config() -> EcoMDConfig:
    return EcoMDConfig(
        n_agents=16,
        d_state=4,
        hidden=8,
        dt=0.02,
        pairwise_kind="stochastic_mlp",
        sps_k_random=4,
        sps_resample_per_step=False,
        regime_enabled=True,
        regime_d=4,
        agent_memory_enabled=True,
        agent_memory_d=4,
        global_state_enabled=True,
        global_state_d=4,
        global_state_into_pair=True,
        jump_lambda=1.0,
        jump_scale=0.01,
        jump_legacy_train_proxy=False,
        bptt_checkpoint_every=0,
        bptt_custom_function=False,
    )


def main() -> None:
    torch.set_num_threads(1)
    torch.manual_seed(20260810)
    simulator = EcoMDSimulator(_config())
    initial = simulator.init_simulator_state(seed=1729)

    expected_state, expected = simulator.rollout_state(
        initial.clone(), 12, create_graph=False
    )
    chunk_state = initial.clone()
    parts: list[torch.Tensor] = []
    for length in (3, 1, 5, 3):
        chunk_state, trajectory = simulator.rollout_state(
            chunk_state, length, create_graph=False
        )
        parts.append(trajectory.log_returns)
    actual_returns = torch.cat(parts)
    torch.testing.assert_close(
        expected.log_returns, actual_returns, rtol=0.0, atol=0.0
    )
    torch.testing.assert_close(
        expected_state.s, chunk_state.s, rtol=0.0, atol=0.0
    )

    buffer = io.BytesIO()
    torch.save(chunk_state.to_checkpoint(), buffer)
    buffer.seek(0)
    restored = SimulatorState.from_checkpoint(
        torch.load(buffer, map_location="cpu", weights_only=False)
    )
    resumed_state, resumed = simulator.rollout_state(
        restored, 4, create_graph=False
    )
    direct_state, direct = simulator.rollout_state(
        chunk_state.clone(), 4, create_graph=False
    )
    torch.testing.assert_close(
        direct.log_returns, resumed.log_returns, rtol=0.0, atol=0.0
    )
    torch.testing.assert_close(
        direct_state.s, resumed_state.s, rtol=0.0, atol=0.0
    )

    torch.manual_seed(20260810)
    gradient_simulator = EcoMDSimulator(_config())
    gradient_state = gradient_simulator.init_simulator_state(seed=2718)
    _, gradient_trajectory = gradient_simulator.rollout_state(
        gradient_state, 6, create_graph=True
    )
    loss = gradient_trajectory.log_returns.square().mean()
    loss.backward()
    gradient_parameters = sum(
        parameter.grad is not None
        and bool(torch.isfinite(parameter.grad).all())
        and bool(parameter.grad.abs().sum() > 0)
        for parameter in gradient_simulator.parameters()
    )
    if gradient_parameters == 0:
        raise RuntimeError("no finite non-zero parameter gradient was observed")

    digest = hashlib.sha256(
        expected.log_returns.detach().cpu().numpy().tobytes()
    ).hexdigest()
    print(json.dumps({
        "ecomd_version": __version__,
        "torch_version": torch.__version__,
        "device": "cpu",
        "n_agents": simulator.cfg.n_agents,
        "steps_checked": 16,
        "chunk_exact": True,
        "checkpoint_resume_exact": True,
        "finite_nonzero_gradient_parameters": gradient_parameters,
        "returns_sha256": digest,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
