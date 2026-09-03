"""Launch the frozen PDEBench v2 CUDA preflight or formal worker."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def hydra_list(values: list[int] | list[str]) -> str:
    return "[" + ",".join(str(value) for value in values) + "]"


def build_command(root: Path, config_name: str, mode: str) -> list[str]:
    command = [
        sys.executable,
        str(root / "scripts/run_constraint_iclr_pdebench_fno.py"),
        "--config-name",
        config_name,
    ]
    if mode == "formal":
        return command
    if mode != "preflight":
        raise ValueError(f"unsupported launch mode: {mode}")
    overrides = {
        "stage": "external_preflight",
        "seeds": hydra_list([1999]),
        "split.confirmation_start": "9000",
        "split.confirmation_count": "8",
        "split.train_trajectories_per_seed": "64",
        "training.epochs": "1",
        "training.checkpoint_every_epochs": "1",
        "evaluation.horizons": hydra_list([1]),
        "output": "experiments/constraint_attribution_iclr/pdebench/preflight_v2.jsonl",
        "checkpoint_dir": "experiments/constraint_attribution_iclr/pdebench/preflight_checkpoints_v2",
    }
    command.extend(f"{key}={value}" for key, value in overrides.items())
    return command


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("preflight", "formal"), required=True)
    parser.add_argument(
        "--config-name", default="pdebench_advection_fno_v2_confirmation"
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    command = build_command(root, args.config_name, args.mode)
    print(" ".join(command), flush=True)
    if not args.dry_run:
        subprocess.run(command, cwd=root, check=True)


if __name__ == "__main__":
    main()
