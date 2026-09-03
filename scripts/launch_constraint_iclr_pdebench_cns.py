"""Launch the frozen CNS CUDA preflight or a registered formal seed worker."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from launch_constraint_iclr_pdebench import hydra_list

CONFIG_NAME = "pdebench_cns_eta0p01_factorial_distributed_20260902"
WORKER_SEEDS = {
    "v100a": list(range(5000, 5015)),
    "v100b": list(range(5015, 5030)),
}


def build_cns_command(root: Path, mode: str, worker: str | None) -> list[str]:
    command = [
        sys.executable,
        str(root / "scripts/run_constraint_iclr_pdebench_cns.py"),
        "--config-name",
        CONFIG_NAME,
    ]
    if mode == "formal":
        if worker not in WORKER_SEEDS:
            raise ValueError("formal CNS launch requires v100a or v100b")
        overrides = {
            "worker_id": str(worker),
            "seeds": hydra_list(WORKER_SEEDS[str(worker)]),
            "output": (
                "experiments/constraint_attribution_iclr/pdebench/"
                f"cns_factorial_confirmation_{worker}_20260902.jsonl"
            ),
            "checkpoint_dir": (
                "experiments/constraint_attribution_iclr/pdebench/"
                f"cns_factorial_checkpoints_{worker}_20260902"
            ),
        }
    elif mode == "preflight":
        if worker is not None:
            raise ValueError("CNS preflight does not accept a formal worker ID")
        overrides = {
            "stage": "cns_factorial_preflight",
            "seeds": hydra_list([4999]),
            "split.confirmation_count": "8",
            "split.train_trajectories_per_seed": "64",
            "training.epochs": "1",
            "training.checkpoint_every_epochs": "1",
            "evaluation.horizons": hydra_list([1]),
            "output": (
                "experiments/constraint_attribution_iclr/pdebench/"
                "cns_factorial_preflight_20260902.jsonl"
            ),
            "checkpoint_dir": (
                "experiments/constraint_attribution_iclr/pdebench/"
                "cns_factorial_preflight_checkpoints_20260902"
            ),
        }
    else:
        raise ValueError(f"unsupported CNS launch mode: {mode}")
    command.extend(f"{key}={value}" for key, value in overrides.items())
    return command


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("preflight", "formal"), required=True)
    parser.add_argument("--worker", choices=tuple(WORKER_SEEDS))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    command = build_cns_command(root, args.mode, args.worker)
    print(" ".join(command), flush=True)
    if not args.dry_run:
        subprocess.run(command, cwd=root, check=True)


if __name__ == "__main__":
    main()
