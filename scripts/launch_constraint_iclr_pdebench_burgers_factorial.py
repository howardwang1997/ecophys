"""Launch the frozen PDEBench Burgers factorial preflight or formal worker."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from launch_constraint_iclr_pdebench import hydra_list

CONFIG_NAME = "pdebench_burgers_nu0p01_factorial_confirmation"


def build_burgers_factorial_command(root: Path, mode: str) -> list[str]:
    command = [
        sys.executable,
        str(root / "scripts/run_constraint_iclr_pdebench_fno.py"),
        "--config-name",
        CONFIG_NAME,
    ]
    if mode == "formal":
        return command
    if mode != "preflight":
        raise ValueError(f"unsupported launch mode: {mode}")
    overrides = {
        "stage": "factorial_preflight",
        "seeds": hydra_list([3999]),
        "split.confirmation_start": "9000",
        "split.confirmation_count": "8",
        "split.train_trajectories_per_seed": "64",
        "training.epochs": "1",
        "training.checkpoint_every_epochs": "1",
        "evaluation.horizons": hydra_list([1]),
        "output": (
            "experiments/constraint_attribution_iclr/pdebench/"
            "burgers_factorial_preflight_20260901.jsonl"
        ),
        "checkpoint_dir": (
            "experiments/constraint_attribution_iclr/pdebench/"
            "burgers_factorial_preflight_checkpoints_20260901"
        ),
    }
    command.extend(f"{key}={value}" for key, value in overrides.items())
    return command


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("preflight", "formal"), required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    command = build_burgers_factorial_command(root, args.mode)
    print(" ".join(command), flush=True)
    if not args.dry_run:
        subprocess.run(command, cwd=root, check=True)


if __name__ == "__main__":
    main()
