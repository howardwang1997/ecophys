"""Orchestrate uninterrupted versus process-boundary resumed training."""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch
from run_stage import experiment_config

from ecomd.models.ecomd import EcoMDSimulator
from ecomd.training.train_distributed import (
    CHECKPOINT_FORMAT_VERSION,
    try_load_checkpoint,
)

ROOT = Path(__file__).resolve().parents[2]
STAGE = Path(__file__).with_name("run_stage.py")
SPAWN = Path(__file__).with_name("run_spawn.py")


def _compare_exact(left: Any, right: Any, path: str = "root") -> list[str]:
    differences: list[str] = []
    if type(left) is not type(right):
        return [f"{path}: type {type(left).__name__} != {type(right).__name__}"]
    if isinstance(left, torch.Tensor):
        if not torch.equal(left, right):
            differences.append(f"{path}: tensor mismatch")
    elif isinstance(left, np.ndarray):
        if not np.array_equal(left, right):
            differences.append(f"{path}: ndarray mismatch")
    elif isinstance(left, dict):
        if left.keys() != right.keys():
            differences.append(f"{path}: dict keys mismatch")
        else:
            for key in left:
                differences.extend(_compare_exact(left[key], right[key], f"{path}.{key}"))
    elif isinstance(left, (list, tuple)):
        if len(left) != len(right):
            differences.append(f"{path}: length {len(left)} != {len(right)}")
        else:
            for index, (lhs, rhs) in enumerate(zip(left, right, strict=True)):
                differences.extend(_compare_exact(lhs, rhs, f"{path}[{index}]"))
    elif left != right:
        differences.append(f"{path}: {left!r} != {right!r}")
    return differences


def _run_stage(
    *,
    checkpoint: Path,
    record: Path,
    n_iters: int,
    nproc: int,
    device: str,
    seed: int,
    stop_after: int | None = None,
) -> dict[str, Any]:
    common_arguments = [
        "--checkpoint",
        str(checkpoint),
        "--stage-record",
        str(record),
        "--n-iters",
        str(n_iters),
        "--seed",
        str(seed),
    ]
    stage_arguments = [*common_arguments, "--device", device]
    if stop_after is not None:
        stage_arguments.extend(("--stop-after", str(stop_after)))
    if nproc == 1:
        command = [sys.executable, str(STAGE), *stage_arguments]
    else:
        command = [
            sys.executable,
            str(SPAWN),
            "--nproc",
            str(nproc),
            *common_arguments,
        ]
        if stop_after is not None:
            command.extend(("--stop-after", str(stop_after)))
    environment = os.environ.copy()
    environment["OMP_NUM_THREADS"] = "1"
    if device == "cpu":
        environment["DIST_BACKEND"] = "gloo"
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"stage failed ({completed.returncode})\nstdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )
    return {
        "command": command,
        "stdout_tail": completed.stdout[-2_000:],
        "stderr_tail": completed.stderr[-2_000:],
        "record": json.loads(record.read_text()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--nproc", type=int, default=2)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument("--seed", type=int, default=133_010)
    parser.add_argument("--git-sha")
    args = parser.parse_args()
    if args.device == "cuda" and args.nproc != 1:
        raise ValueError("the available V100 nodes support one local CUDA rank")
    args.work_root.mkdir(parents=True, exist_ok=True)
    run_dir = args.work_root / f"run_{time.time_ns()}_{os.getpid()}"
    run_dir.mkdir()
    baseline_checkpoint = run_dir / "baseline.pt"
    resumed_checkpoint = run_dir / "resumed.pt"
    started = time.perf_counter()

    baseline_stage = _run_stage(
        checkpoint=baseline_checkpoint,
        record=run_dir / "baseline_stage.json",
        n_iters=6,
        nproc=args.nproc,
        device=args.device,
        seed=args.seed,
        stop_after=None,
    )
    split_stage = _run_stage(
        checkpoint=resumed_checkpoint,
        record=run_dir / "split_stage.json",
        n_iters=6,
        nproc=args.nproc,
        device=args.device,
        seed=args.seed,
        stop_after=3,
    )
    resume_stage = _run_stage(
        checkpoint=resumed_checkpoint,
        record=run_dir / "resume_stage.json",
        n_iters=6,
        nproc=args.nproc,
        device=args.device,
        seed=args.seed,
        stop_after=None,
    )

    baseline = torch.load(baseline_checkpoint, map_location="cpu", weights_only=False)
    resumed = torch.load(resumed_checkpoint, map_location="cpu", weights_only=False)
    model_differences = _compare_exact(
        baseline["sim_state_dict"], resumed["sim_state_dict"], "model"
    )
    optimizer_differences = _compare_exact(
        baseline["optim_state_dict"], resumed["optim_state_dict"], "optimizer"
    )
    runtime_differences = _compare_exact(
        baseline["rank_runtimes"], resumed["rank_runtimes"], "runtimes"
    )
    rank_records = resumed["rank_runtimes"]
    all_history_values = [
        value
        for runtime in rank_records
        for record in runtime["history"]
        for value in record.values()
        if isinstance(value, (int, float))
    ]
    temporary_files = sorted(str(path) for path in run_dir.glob(".*.tmp-*"))

    world_mismatch_failed = False
    if int(resumed["world_size"]) != args.nproc:
        raise RuntimeError("checkpoint did not preserve requested world size")
    mismatch_sim = EcoMDSimulator(experiment_config())
    mismatch_optim = torch.optim.Adam(mismatch_sim.parameters(), lr=5e-4)
    try:
        try_load_checkpoint(
            resumed_checkpoint,
            sim=mismatch_sim,
            optim=mismatch_optim,
            rank=0,
            world_size=args.nproc + 1,
            state_complete=True,
            device=torch.device("cpu"),
        )
    except ValueError as error:
        world_mismatch_failed = "world_size" in str(error)

    checks = {
        "format_version_2": baseline["format_version"] == CHECKPOINT_FORMAT_VERSION,
        "iteration_6": baseline["iter_idx"] == resumed["iter_idx"] == 6,
        "final_model_bit_exact": not model_differences,
        "final_optimizer_bit_exact": not optimizer_differences,
        "all_rank_runtime_and_rng_bit_exact": not runtime_differences,
        "rank_record_count_exact": len(rank_records) == args.nproc,
        "rank_ids_exact": {int(item["rank"]) for item in rank_records}
        == set(range(args.nproc)),
        "all_final_rank_models_synchronized": (
            baseline_stage["record"]["ranks_synchronized"]
            and resume_stage["record"]["ranks_synchronized"]
        ),
        "losses_and_gradients_finite": bool(np.isfinite(all_history_values).all()),
        "world_size_mismatch_hard_fails": world_mismatch_failed,
        "no_temporary_checkpoint_remains": not temporary_files,
        "resume_history_contains_iterations_3_to_5": [
            int(item["iter"]) for item in rank_records[0]["history"][-3:]
        ]
        == [3, 4, 5],
    }
    git_sha = args.git_sha or subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    payload = {
        "experiment": "133_distributed_exact_resume",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_sha": git_sha,
        "platform": platform.platform(),
        "torch_version": torch.__version__,
        "device": args.device,
        "nproc": args.nproc,
        "arguments": vars(args) | {"out": str(args.out), "work_root": str(args.work_root)},
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "difference_counts": {
            "model": len(model_differences),
            "optimizer": len(optimizer_differences),
            "rank_runtime": len(runtime_differences),
        },
        "difference_examples": {
            "model": model_differences[:10],
            "optimizer": optimizer_differences[:10],
            "rank_runtime": runtime_differences[:10],
        },
        "temporary_files": temporary_files,
        "stage_records": {
            "baseline": baseline_stage["record"],
            "split": split_stage["record"],
            "resume": resume_stage["record"],
        },
        "wall_seconds": time.perf_counter() - started,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
