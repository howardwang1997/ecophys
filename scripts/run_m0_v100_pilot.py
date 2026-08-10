"""Run the frozen EcoMD v1 M0 V100 capacity and exact-resume pilot."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import platform
import socket
import subprocess
import sys
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

import numpy as np
import torch

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator, SimulatorState  # noqa: E402
from ecomd.training.losses import (  # noqa: E402
    LossWeights,
    MomentTargets,
    build_targets_from_returns,
)
from ecomd.training.train_distributed import train_distributed  # noqa: E402
from scripts.run_m0_cpu_feasibility import (  # noqa: E402
    DEFAULT_CONFIG,
    _assert_tree_equal,
    _git_metadata,
    _load_checkpoint,
    _load_config,
    _synthetic_returns,
)


def _pilot_config(reference_config: dict[str, Any]) -> dict[str, Any]:
    pilot = copy.deepcopy(reference_config)
    expected_iterations = int(pilot["compute_protocol"]["v100_pilot_n_iters"])
    if expected_iterations != 10:
        raise ValueError("M0 V100 pilot must use exactly 10 iterations")
    pilot["training"]["n_iters"] = expected_iterations
    if pilot["training"]["mixed_precision"] != "fp32":
        raise ValueError("M0 V100 pilot must use FP32")
    if int(pilot["simulator"]["n_agents"]) != 256:
        raise ValueError("M0 V100 pilot must use the reference N=256 scale")
    return pilot


def _new_simulator(
    simulator_config: dict[str, Any],
    seed: int,
    device: torch.device,
) -> EcoMDSimulator:
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    return EcoMDSimulator(EcoMDConfig(**simulator_config)).to(device)


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


def _continuation_returns(
    checkpoint: dict[str, Any],
    simulator_config: dict[str, Any],
    seed: int,
    device: torch.device,
    steps: int = 8,
) -> torch.Tensor:
    simulator = _new_simulator(simulator_config, seed, device)
    simulator.load_state_dict(checkpoint["sim_state_dict"])
    runtimes = checkpoint["rank_runtimes"]
    if not isinstance(runtimes, list) or len(runtimes) != 1:
        raise ValueError("checkpoint must contain exactly one rank runtime")
    state = SimulatorState.from_checkpoint(runtimes[0]["simulator_state"]).to(device)
    _, trajectory = simulator.rollout_state(state, steps, create_graph=False)
    return trajectory.log_returns.detach().cpu()


def _gpu_metadata(device: torch.device) -> dict[str, Any]:
    properties = torch.cuda.get_device_properties(device)
    query = subprocess.run(
        [
            "nvidia-smi",
            f"--id={device.index or 0}",
            "--query-gpu=uuid,driver_version,vbios_version",
            "--format=csv,noheader,nounits",
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    uuid, driver, vbios = [part.strip() for part in query.split(",", maxsplit=2)]
    return {
        "name": properties.name,
        "uuid": uuid,
        "driver": driver,
        "vbios": vbios,
        "total_memory_gib": properties.total_memory / (1024**3),
        "compute_capability": f"{properties.major}.{properties.minor}",
    }


def _host_id() -> str:
    machine_id_path = Path("/etc/machine-id")
    machine_id = (
        machine_id_path.read_text(encoding="utf-8").strip()
        if machine_id_path.is_file()
        else "unavailable"
    )
    material = f"{socket.gethostname()}:{machine_id}".encode()
    return hashlib.sha256(material).hexdigest()[:16]


def _is_v100_32gb(gpu: dict[str, Any]) -> bool:
    name = str(gpu["name"]).upper()
    supported_name = "V100" in name or "PG503-216" in name
    return supported_name and float(gpu["total_memory_gib"]) >= 30.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--device-index", type=int, default=0)
    parser.add_argument("--require-clean", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    reference_config = _load_config(args.config.resolve())
    pilot_config = _pilot_config(reference_config)
    git_sha, worktree_clean = _git_metadata(REPO_ROOT)
    if args.require_clean and not worktree_clean:
        raise RuntimeError("formal M0 V100 pilot requires a clean worktree")

    canonical_pilot = json.dumps(
        pilot_config, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    config_summary = {
        "git_sha": git_sha,
        "worktree_clean": worktree_clean,
        "reference_config_sha256": hashlib.sha256(
            args.config.resolve().read_bytes()
        ).hexdigest(),
        "pilot_effective_config_sha256": hashlib.sha256(canonical_pilot).hexdigest(),
        "n_agents": int(pilot_config["simulator"]["n_agents"]),
        "n_iters": int(pilot_config["training"]["n_iters"]),
        "chunk_steps": int(pilot_config["training"]["chunk_steps"]),
        "mixed_precision": pilot_config["training"]["mixed_precision"],
    }
    if args.validate_only:
        print(json.dumps(config_summary, indent=2, sort_keys=True))
        return

    if not torch.cuda.is_available():
        raise RuntimeError("M0 V100 pilot requires CUDA")
    device = torch.device("cuda", args.device_index)
    torch.cuda.set_device(device)
    gpu = _gpu_metadata(device)
    if not _is_v100_32gb(gpu):
        raise RuntimeError(
            "M0 pilot requires a 32 GB V100; got "
            f"{gpu['name']!r} with {gpu['total_memory_gib']:.2f} GiB"
        )

    torch.use_deterministic_algorithms(True)
    simulator_config = dict(pilot_config["simulator"])
    training_config = dict(pilot_config["training"])
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
    with tempfile.TemporaryDirectory(prefix="ecomd-m0-v100-") as temporary:
        temporary_path = Path(temporary)
        reference_path = temporary_path / "reference.pt"
        resumed_path = temporary_path / "resumed.pt"

        reference_simulator = _new_simulator(simulator_config, seed, device)
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats(device)
        torch.cuda.synchronize(device)
        reference_started = time.perf_counter()
        reference_history = _train(
            reference_simulator,
            targets,
            weights,
            simulator_config,
            training_config,
            reference_path,
        )
        torch.cuda.synchronize(device)
        reference_seconds = time.perf_counter() - reference_started
        reference_peak_allocated = torch.cuda.max_memory_allocated(device) / (1024**3)
        reference_peak_reserved = torch.cuda.max_memory_reserved(device) / (1024**3)

        del reference_simulator
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats(device)
        interrupted_simulator = _new_simulator(simulator_config, seed, device)
        torch.cuda.synchronize(device)
        resumed_started = time.perf_counter()
        _train(
            interrupted_simulator,
            targets,
            weights,
            simulator_config,
            training_config,
            resumed_path,
            stop_after_iter=5,
        )
        del interrupted_simulator
        resumed_simulator = _new_simulator(simulator_config, seed, device)
        resumed_history = _train(
            resumed_simulator,
            targets,
            weights,
            simulator_config,
            training_config,
            resumed_path,
        )
        torch.cuda.synchronize(device)
        resumed_seconds = time.perf_counter() - resumed_started
        resumed_peak_allocated = torch.cuda.max_memory_allocated(device) / (1024**3)
        resumed_peak_reserved = torch.cuda.max_memory_reserved(device) / (1024**3)

        gradient_tensors = [
            parameter.grad
            for parameter in resumed_simulator.parameters()
            if parameter.grad is not None
        ]
        gradients_finite = bool(gradient_tensors) and all(
            bool(torch.isfinite(gradient).all()) for gradient in gradient_tensors
        )
        nonzero_gradient_tensors = sum(
            bool(gradient.abs().sum() > 0) for gradient in gradient_tensors
        )

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
            reference_checkpoint, simulator_config, seed, device
        )
        resumed_continuation = _continuation_returns(
            resumed_checkpoint, simulator_config, seed, device
        )
        if not torch.equal(reference_continuation, resumed_continuation):
            raise AssertionError("post-resume continuation trajectory mismatch")

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
    peak_allocated = max(reference_peak_allocated, resumed_peak_allocated)
    peak_reserved = max(reference_peak_reserved, resumed_peak_reserved)
    projected_hours = (
        reference_seconds / int(training_config["n_iters"]) * 600.0 / 3600.0
    )
    peak_limit = float(reference_config["compute_protocol"]["peak_reserved_gib_max"])
    time_limit = float(
        reference_config["compute_protocol"]["projected_reference_hours_max"]
    )
    gates = {
        "loss_history_finite": history_finite,
        "all_existing_gradients_finite": gradients_finite,
        "finite_nonzero_gradient_parameter_tensors": nonzero_gradient_tensors,
        "model_state_exact": True,
        "optimizer_state_exact": True,
        "dynamic_state_and_rng_exact": True,
        "history_exact": True,
        "post_resume_8_step_trajectory_exact": True,
        "post_resume_trajectory_finite": continuation_finite,
        "peak_reserved_gib_within_limit": peak_reserved <= peak_limit,
        "projected_reference_hours_within_limit": projected_hours <= time_limit,
    }
    passed = (
        history_finite
        and gradients_finite
        and nonzero_gradient_tensors > 0
        and continuation_finite
        and peak_reserved <= peak_limit
        and projected_hours <= time_limit
    )

    result = {
        "schema_version": 1,
        "status": "PASS" if passed else "FAIL",
        "result_scope": "v100_mechanical_capacity_only_not_market_fidelity",
        "scientific_claim_authorized": False,
        "second_host_repeat_authorized_next": passed,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "git_sha": git_sha,
        "worktree_clean_at_start": worktree_clean,
        "host_id_sha256_prefix": _host_id(),
        **config_summary,
        "gpu": gpu,
        "parameter_count": sum(
            parameter.numel() for parameter in resumed_simulator.parameters()
        ),
        "synthetic_target": {
            "seed": 20_260_811,
            "n_returns": int(target_returns.size),
            "returns_sha256": hashlib.sha256(target_returns.tobytes()).hexdigest(),
            "acf_sq_mean": targets.acf_sq_mean,
            "leverage_sum": targets.leverage_sum,
            "hill_alpha": targets.hill_alpha,
        },
        "gates": gates,
        "continuation_returns_sha256": hashlib.sha256(
            reference_continuation.numpy().tobytes()
        ).hexdigest(),
        "history": reference_history,
        "memory_gib": {
            "peak_allocated": peak_allocated,
            "peak_reserved": peak_reserved,
            "peak_reserved_limit": peak_limit,
        },
        "timing_seconds": {
            "uninterrupted_10_iterations": reference_seconds,
            "interrupted_5_plus_resumed_5": resumed_seconds,
            "total": time.perf_counter() - started,
        },
        "projected_600_iteration_hours": projected_hours,
        "projected_600_iteration_hours_limit": time_limit,
        "environment": {
            "python": platform.python_version(),
            "torch": torch.__version__,
            "numpy": np.__version__,
            "cuda_runtime": torch.version.cuda,
            "platform": platform.platform(),
            "cublas_workspace_config": os.environ["CUBLAS_WORKSPACE_CONFIG"],
            "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        },
    }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
