"""Run the pre-registered, data-free EcoMD v1 M0 CPU feasibility gate."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import platform
import resource
import subprocess
import sys
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import torch
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator, SimulatorState  # noqa: E402
from ecomd.training.losses import (  # noqa: E402
    LossWeights,
    MomentTargets,
    build_targets_from_returns,
)
from ecomd.training.m0_contract import validate_m0_config  # noqa: E402
from ecomd.training.train_distributed import train_distributed  # noqa: E402

DEFAULT_CONFIG = REPO_ROOT / "configs" / "ecomd_v1" / "m0_reference.yaml"


def _load_config(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("M0 config must be a mapping")
    validate_m0_config(payload)
    return payload


def _synthetic_returns(seed: int = 20_260_811, length: int = 4096) -> np.ndarray:
    generator = np.random.default_rng(seed)
    innovations = generator.standard_normal(length)
    returns = np.empty(length, dtype=np.float64)
    variance = 1.0e-4
    for index, innovation in enumerate(innovations):
        returns[index] = math.sqrt(variance) * innovation
        variance = 5.0e-6 + 0.08 * returns[index] ** 2 + 0.87 * variance
    return returns


def _new_simulator(simulator_config: dict[str, Any], seed: int) -> EcoMDSimulator:
    torch.manual_seed(seed)
    return EcoMDSimulator(EcoMDConfig(**simulator_config))


def _train(
    simulator: EcoMDSimulator,
    targets: MomentTargets,
    weights: LossWeights,
    simulator_config: dict[str, Any],
    training_config: dict[str, Any],
    checkpoint_path: Path,
    *,
    stop_after_iter: int | None = None,
) -> list[dict[str, Any]]:
    return train_distributed(
        simulator,
        targets,
        weights,
        n_iters=int(training_config["n_iters"]),
        chunk_steps=int(training_config["chunk_steps"]),
        lr=float(training_config["lr"]),
        grad_clip=float(training_config["grad_clip_max_norm"]),
        seed=int(training_config["seed"]),
        persistent_state=bool(training_config["persistent_state"]),
        warmup_steps=int(training_config["warmup_steps"]),
        lr_warmup_iters=int(training_config["lr_warmup_iters"]),
        rank=0,
        world_size=1,
        checkpoint_path=checkpoint_path,
        checkpoint_every_s=float(training_config["checkpoint_every_s"]),
        mixed_precision=str(training_config["mixed_precision"]),
        rollout_reg_cfg={"enabled": False},
        state_complete=bool(training_config["state_complete"]),
        sim_config=simulator_config,
        train_config=training_config,
        stop_after_iter=stop_after_iter,
    )


def _assert_tree_equal(left: Any, right: Any, path: str = "root") -> None:
    if type(left) is not type(right):
        raise AssertionError(
            f"{path}: type mismatch {type(left).__name__} != {type(right).__name__}"
        )
    if isinstance(left, torch.Tensor):
        if not torch.equal(left, right):
            raise AssertionError(f"{path}: tensor mismatch")
        return
    if isinstance(left, np.ndarray):
        if not np.array_equal(left, right):
            raise AssertionError(f"{path}: ndarray mismatch")
        return
    if isinstance(left, dict):
        if left.keys() != right.keys():
            raise AssertionError(f"{path}: dictionary keys mismatch")
        for key in left:
            _assert_tree_equal(left[key], right[key], f"{path}.{key}")
        return
    if isinstance(left, (list, tuple)):
        if len(left) != len(right):
            raise AssertionError(f"{path}: sequence length mismatch")
        for index, (lhs, rhs) in enumerate(zip(left, right, strict=True)):
            _assert_tree_equal(lhs, rhs, f"{path}[{index}]")
        return
    if left != right:
        raise AssertionError(f"{path}: {left!r} != {right!r}")


def _load_checkpoint(path: Path) -> dict[str, Any]:
    payload = torch.load(path, map_location="cpu", weights_only=False)
    if not isinstance(payload, dict):
        raise ValueError(f"invalid checkpoint payload: {path}")
    return payload


def _continuation_returns(
    checkpoint: dict[str, Any],
    simulator_config: dict[str, Any],
    seed: int,
    steps: int = 8,
) -> torch.Tensor:
    simulator = _new_simulator(simulator_config, seed)
    simulator.load_state_dict(checkpoint["sim_state_dict"])
    runtimes = checkpoint["rank_runtimes"]
    if not isinstance(runtimes, list) or len(runtimes) != 1:
        raise ValueError("checkpoint must contain exactly one rank runtime")
    state = SimulatorState.from_checkpoint(runtimes[0]["simulator_state"])
    _, trajectory = simulator.rollout_state(state, steps, create_graph=False)
    return trajectory.log_returns.detach().cpu()


def _git_metadata(repo_root: Path) -> tuple[str, bool]:
    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=normal"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return sha, not bool(dirty.strip())


def _peak_rss_mib() -> float:
    raw = float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return raw / (1024.0 * 1024.0) if sys.platform == "darwin" else raw / 1024.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-clean", action="store_true")
    args = parser.parse_args()

    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)

    reference_config = _load_config(args.config.resolve())
    git_sha, worktree_clean = _git_metadata(REPO_ROOT)
    if args.require_clean and not worktree_clean:
        raise RuntimeError("formal M0 CPU gate requires a clean worktree")

    cpu_config = copy.deepcopy(reference_config)
    cpu_config["simulator"]["n_agents"] = 64
    cpu_config["training"]["n_iters"] = 2
    allowed = reference_config["contract"]["allowed_cpu_overrides"]
    if allowed != {"simulator.n_agents": [64], "training.n_iters": [2]}:
        raise RuntimeError("unexpected CPU override contract")

    simulator_config = dict(cpu_config["simulator"])
    training_config = dict(cpu_config["training"])
    weights = LossWeights(**training_config["loss_weights"])
    target_returns = _synthetic_returns()
    targets = build_targets_from_returns(
        target_returns,
        max_lag=weights.max_lag,
        k_frac=weights.hill_k_frac,
        include_multi_fact=False,
    )
    seed = int(training_config["seed"])

    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="ecomd-m0-cpu-") as temporary:
        temporary_path = Path(temporary)
        reference_path = temporary_path / "reference.pt"
        resumed_path = temporary_path / "resumed.pt"

        reference_simulator = _new_simulator(simulator_config, seed)
        reference_started = time.perf_counter()
        reference_history = _train(
            reference_simulator,
            targets,
            weights,
            simulator_config,
            training_config,
            reference_path,
        )
        reference_seconds = time.perf_counter() - reference_started

        interrupted_simulator = _new_simulator(simulator_config, seed)
        resumed_started = time.perf_counter()
        _train(
            interrupted_simulator,
            targets,
            weights,
            simulator_config,
            training_config,
            resumed_path,
            stop_after_iter=1,
        )
        resumed_simulator = _new_simulator(simulator_config, seed)
        resumed_history = _train(
            resumed_simulator,
            targets,
            weights,
            simulator_config,
            training_config,
            resumed_path,
        )
        resumed_seconds = time.perf_counter() - resumed_started

        reference_checkpoint = _load_checkpoint(reference_path)
        resumed_checkpoint = _load_checkpoint(resumed_path)
        _assert_tree_equal(
            reference_checkpoint["sim_state_dict"],
            resumed_checkpoint["sim_state_dict"],
            "sim_state_dict",
        )
        _assert_tree_equal(
            reference_checkpoint["optim_state_dict"],
            resumed_checkpoint["optim_state_dict"],
            "optim_state_dict",
        )
        _assert_tree_equal(
            reference_checkpoint["rank_runtimes"],
            resumed_checkpoint["rank_runtimes"],
            "rank_runtimes",
        )
        _assert_tree_equal(reference_history, resumed_history, "history")

        reference_continuation = _continuation_returns(
            reference_checkpoint, simulator_config, seed
        )
        resumed_continuation = _continuation_returns(
            resumed_checkpoint, simulator_config, seed
        )
        if not torch.equal(reference_continuation, resumed_continuation):
            raise AssertionError("post-resume continuation trajectory mismatch")

    gradient_tensors = [
        parameter.grad
        for parameter in reference_simulator.parameters()
        if parameter.grad is not None
    ]
    gradients_finite = bool(gradient_tensors) and all(
        bool(torch.isfinite(gradient).all()) for gradient in gradient_tensors
    )
    nonzero_gradient_tensors = sum(
        bool(gradient.abs().sum() > 0) for gradient in gradient_tensors
    )
    history_finite = all(
        math.isfinite(float(record[key]))
        for record in reference_history
        for key in (
            "total_rank0",
            "total_world_mean",
            "acf_sim",
            "leverage_sim",
            "hill_sim",
            "grad_norm",
        )
    )
    continuation_finite = bool(torch.isfinite(reference_continuation).all())
    if not (
        gradients_finite
        and nonzero_gradient_tensors > 0
        and history_finite
        and continuation_finite
    ):
        raise RuntimeError("M0 CPU numerical gate failed")

    canonical_cpu = json.dumps(
        cpu_config, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    result = {
        "schema_version": 1,
        "status": "PASS",
        "result_scope": "mechanical_feasibility_only_not_market_fidelity",
        "scientific_claim_authorized": False,
        "v100_pilot_authorized_next": True,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "git_sha": git_sha,
        "worktree_clean_at_start": worktree_clean,
        "reference_config": str(args.config.resolve().relative_to(REPO_ROOT)),
        "reference_config_sha256": hashlib.sha256(
            args.config.resolve().read_bytes()
        ).hexdigest(),
        "cpu_effective_config_sha256": hashlib.sha256(canonical_cpu).hexdigest(),
        "overrides": {
            "simulator.n_agents": 64,
            "training.n_iters": 2,
        },
        "reference_n_agents": int(reference_config["simulator"]["n_agents"]),
        "parameter_count": sum(
            parameter.numel() for parameter in reference_simulator.parameters()
        ),
        "synthetic_target": {
            "seed": 20_260_811,
            "n_returns": int(target_returns.size),
            "returns_sha256": hashlib.sha256(target_returns.tobytes()).hexdigest(),
            "acf_sq_mean": targets.acf_sq_mean,
            "leverage_sum": targets.leverage_sum,
            "hill_alpha": targets.hill_alpha,
        },
        "gates": {
            "loss_history_finite": history_finite,
            "all_existing_gradients_finite": gradients_finite,
            "finite_nonzero_gradient_parameter_tensors": nonzero_gradient_tensors,
            "model_state_exact": True,
            "optimizer_state_exact": True,
            "dynamic_state_and_rng_exact": True,
            "history_exact": True,
            "post_resume_8_step_trajectory_exact": True,
            "post_resume_trajectory_finite": continuation_finite,
        },
        "continuation_returns_sha256": hashlib.sha256(
            reference_continuation.numpy().tobytes()
        ).hexdigest(),
        "history": reference_history,
        "timing_seconds": {
            "uninterrupted_two_iterations": reference_seconds,
            "interrupted_then_resumed": resumed_seconds,
            "total": time.perf_counter() - started,
        },
        "peak_rss_mib": _peak_rss_mib(),
        "environment": {
            "python": platform.python_version(),
            "torch": torch.__version__,
            "numpy": np.__version__,
            "platform": platform.platform(),
            "torch_num_threads": torch.get_num_threads(),
            "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        },
    }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
