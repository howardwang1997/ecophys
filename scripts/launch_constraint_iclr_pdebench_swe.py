"""Launch the frozen PDEBench shallow-water preflight or formal worker."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from launch_constraint_iclr_pdebench import hydra_list

PREFLIGHT_CONFIG = "pdebench_swe_rdb_factorial_20260902"
FORMAL_CONFIG = "pdebench_swe_rdb_factorial_distributed_20260902"
WORKER_SEEDS = {
    "v100a": list(range(6000, 6015)),
    "v100b": list(range(6015, 6030)),
}


def build_swe_command(root: Path, mode: str, worker: str | None = None) -> list[str]:
    config_name = FORMAL_CONFIG if mode == "formal" else PREFLIGHT_CONFIG
    command = [
        sys.executable,
        str(root / "scripts/run_constraint_iclr_pdebench_swe.py"),
        "--config-name",
        config_name,
    ]
    if mode == "preflight":
        overrides = {
            "stage": "swe_factorial_preflight",
            "seeds": hydra_list([5999]),
            "split.confirmation_start": "128",
            "split.confirmation_count": "8",
            "split.train_pool_start": "200",
            "split.train_pool_stop": "264",
            "split.train_trajectories_per_seed": "64",
            "training.epochs": "1",
            "training.checkpoint_every_epochs": "1",
            "evaluation.horizons": hydra_list([1]),
            "evaluation.primary_horizon": "1",
            "output": (
                "experiments/constraint_attribution_iclr/pdebench/"
                "swe_factorial_preflight_20260902.jsonl"
            ),
            "checkpoint_dir": (
                "experiments/constraint_attribution_iclr/pdebench/"
                "swe_factorial_preflight_checkpoints_20260902"
            ),
        }
    elif mode == "formal":
        if worker not in WORKER_SEEDS:
            raise ValueError("formal SWE launch requires worker v100a or v100b")
        overrides = {
            "worker_id": str(worker),
            "seeds": hydra_list(WORKER_SEEDS[str(worker)]),
            "output": (
                "experiments/constraint_attribution_iclr/pdebench/"
                f"swe_factorial_{worker}_20260902.jsonl"
            ),
        }
    else:
        raise ValueError(f"unsupported SWE launch mode: {mode}")
    command.extend(f"{key}={value}" for key, value in overrides.items())
    return command


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("preflight", "formal"), required=True)
    parser.add_argument("--worker", choices=tuple(WORKER_SEEDS))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    command = build_swe_command(root, args.mode, args.worker)
    print(" ".join(command), flush=True)
    if not args.dry_run:
        subprocess.run(command, cwd=root, check=True)


if __name__ == "__main__":
    main()
