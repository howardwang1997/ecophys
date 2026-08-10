from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pytest
import torch

from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator, SimulatorState
from ecomd.training.losses import MomentTargets
from ecomd.training.train_distributed import (
    CHECKPOINT_FORMAT_VERSION,
    capture_rank_runtime,
    restore_rank_runtime,
    save_checkpoint,
    try_load_checkpoint,
)


def _config() -> EcoMDConfig:
    return EcoMDConfig(
        n_agents=8,
        d_state=4,
        hidden=8,
        dt=0.01,
        pairwise_kind="stochastic_mlp",
        sps_k_random=3,
        sps_resample_per_step=False,
        regime_enabled=True,
        regime_d=4,
        agent_memory_enabled=True,
        agent_memory_d=4,
        global_state_enabled=True,
        global_state_d=4,
        jump_lambda=1.0,
        jump_scale=0.01,
        memory_kernel_lambda=0.8,
        memory_kernel_strength=0.1,
    )


def _assert_tree_equal(left: Any, right: Any) -> None:
    assert type(left) is type(right)
    if isinstance(left, torch.Tensor):
        torch.testing.assert_close(left, right, rtol=0.0, atol=0.0)
    elif isinstance(left, dict):
        assert left.keys() == right.keys()
        for key in left:
            _assert_tree_equal(left[key], right[key])
    elif isinstance(left, (list, tuple)):
        assert len(left) == len(right)
        for lhs, rhs in zip(left, right, strict=True):
            _assert_tree_equal(lhs, rhs)
    elif isinstance(left, np.ndarray):
        np.testing.assert_array_equal(left, right)
    else:
        assert left == right


def _make_runtime() -> tuple[
    EcoMDSimulator,
    torch.optim.Optimizer,
    SimulatorState,
    torch.Generator,
    torch.Generator,
]:
    torch.manual_seed(133)
    sim = EcoMDSimulator(_config())
    optim = torch.optim.Adam(sim.parameters(), lr=1e-3)
    generator = torch.Generator(device="cpu").manual_seed(9_001)
    auxiliary = torch.Generator(device="cpu").manual_seed(9_002)
    state = sim.init_simulator_state(generator=generator)
    state, trajectory = sim.rollout_state(state, 4, generator=generator)
    trajectory.log_returns.square().mean().backward()
    optim.step()
    return sim, optim, state, generator, auxiliary


def test_atomic_state_complete_checkpoint_round_trip(tmp_path: Path) -> None:
    sim, optim, state, generator, auxiliary = _make_runtime()
    history = [{"iter": 0, "total_rank0": 1.25}]
    runtime = capture_rank_runtime(
        rank=0,
        simulator_state=state,
        generator=generator,
        auxiliary_generator=auxiliary,
        history=history,
        device=torch.device("cpu"),
    )
    checkpoint = tmp_path / "checkpoint.pt"
    targets = MomentTargets(acf_sq_mean=0.1, leverage_sum=-0.1, hill_alpha=3.0)
    save_checkpoint(
        checkpoint,
        sim=sim,
        optim=optim,
        iter_idx=1,
        targets=targets,
        sim_config={"n_agents": 8},
        train_config={"state_complete": True},
        world_size=1,
        state_complete=True,
        rank_runtimes=[runtime],
    )
    assert checkpoint.exists()
    assert not list(tmp_path.glob(".checkpoint.pt.tmp-*"))
    raw = torch.load(checkpoint, map_location="cpu", weights_only=False)
    assert raw["format_version"] == CHECKPOINT_FORMAT_VERSION

    torch.manual_seed(999)
    restored_sim = EcoMDSimulator(_config())
    restored_optim = torch.optim.Adam(restored_sim.parameters(), lr=1e-3)
    iteration, restored_runtime, exact = try_load_checkpoint(
        checkpoint,
        sim=restored_sim,
        optim=restored_optim,
        rank=0,
        world_size=1,
        state_complete=True,
        device=torch.device("cpu"),
    )
    assert iteration == 1
    assert exact
    assert restored_runtime is not None
    restored_generator = torch.Generator(device="cpu")
    restored_auxiliary = torch.Generator(device="cpu")
    restored_state, restored_history = restore_rank_runtime(
        restored_runtime,
        rank=0,
        generator=restored_generator,
        auxiliary_generator=restored_auxiliary,
        device=torch.device("cpu"),
    )

    _assert_tree_equal(state.detached().to("cpu").to_checkpoint(), restored_state.to_checkpoint())
    _assert_tree_equal(sim.state_dict(), restored_sim.state_dict())
    _assert_tree_equal(optim.state_dict(), restored_optim.state_dict())
    assert torch.equal(generator.get_state(), restored_generator.get_state())
    assert torch.equal(auxiliary.get_state(), restored_auxiliary.get_state())
    assert restored_history == history


def test_world_size_mismatch_hard_fails(tmp_path: Path) -> None:
    sim, optim, state, generator, auxiliary = _make_runtime()
    runtime = capture_rank_runtime(
        rank=0,
        simulator_state=state,
        generator=generator,
        auxiliary_generator=auxiliary,
        history=[],
        device=torch.device("cpu"),
    )
    checkpoint = tmp_path / "checkpoint.pt"
    save_checkpoint(
        checkpoint,
        sim=sim,
        optim=optim,
        iter_idx=1,
        targets=MomentTargets(0.1, -0.1, 3.0),
        sim_config={},
        train_config={},
        world_size=1,
        state_complete=True,
        rank_runtimes=[runtime],
    )
    with pytest.raises(ValueError, match="world_size"):
        try_load_checkpoint(
            checkpoint,
            sim=sim,
            optim=optim,
            rank=0,
            world_size=2,
            state_complete=True,
        )


def test_checkpoint_requires_every_rank_runtime(tmp_path: Path) -> None:
    sim, optim, _, _, _ = _make_runtime()
    with pytest.raises(ValueError, match="one runtime per rank"):
        save_checkpoint(
            tmp_path / "checkpoint.pt",
            sim=sim,
            optim=optim,
            iter_idx=1,
            targets=MomentTargets(0.1, -0.1, 3.0),
            sim_config={},
            train_config={},
            world_size=2,
            state_complete=True,
            rank_runtimes=[],
        )


def test_checkpoint_execution_metadata_must_match_on_resume(tmp_path: Path) -> None:
    sim, optim, state, generator, auxiliary = _make_runtime()
    runtime = capture_rank_runtime(
        rank=0,
        simulator_state=state,
        generator=generator,
        auxiliary_generator=auxiliary,
        history=[],
        device=torch.device("cpu"),
    )
    checkpoint = tmp_path / "checkpoint.pt"
    binding = {"git_sha": "abc", "data_manifest_sha256": "def"}
    save_checkpoint(
        checkpoint,
        sim=sim,
        optim=optim,
        iter_idx=1,
        targets=MomentTargets(0.1, -0.1, 3.0),
        sim_config={},
        train_config={},
        world_size=1,
        state_complete=True,
        rank_runtimes=[runtime],
        execution_metadata=binding,
    )
    restored_sim = EcoMDSimulator(_config())
    restored_optim = torch.optim.Adam(restored_sim.parameters(), lr=1e-3)
    iteration, _, exact = try_load_checkpoint(
        checkpoint,
        sim=restored_sim,
        optim=restored_optim,
        state_complete=True,
        expected_execution_metadata=binding,
    )
    assert iteration == 1
    assert exact
    with pytest.raises(ValueError, match="execution metadata"):
        try_load_checkpoint(
            checkpoint,
            sim=restored_sim,
            optim=restored_optim,
            state_complete=True,
            expected_execution_metadata={**binding, "git_sha": "wrong"},
        )
