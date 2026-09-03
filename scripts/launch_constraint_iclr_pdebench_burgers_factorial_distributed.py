"""Launch one outcome-blind half of the frozen Burgers factorial confirmation."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from launch_constraint_iclr_pdebench import hydra_list

CONFIG_NAME = "pdebench_burgers_nu0p01_factorial_confirmation"
WORKER_SEEDS = {
    "v100a": tuple(range(4000, 4015)),
    "v100b": tuple(range(4015, 4030)),
}


def build_distributed_burgers_command(root: Path, worker: str) -> list[str]:
    if worker not in WORKER_SEEDS:
        raise ValueError(f"unsupported worker: {worker}")
    return [
        sys.executable,
        str(root / "scripts/run_constraint_iclr_pdebench_fno.py"),
        "--config-name",
        CONFIG_NAME,
        f"seeds={hydra_list(WORKER_SEEDS[worker])}",
        (
            "output=experiments/constraint_attribution_iclr/pdebench/"
            f"burgers_factorial_confirmation_{worker}_20260901.jsonl"
        ),
        (
            "checkpoint_dir=experiments/constraint_attribution_iclr/pdebench/"
            f"burgers_factorial_checkpoints_{worker}_20260901"
        ),
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", choices=tuple(WORKER_SEEDS), required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    command = build_distributed_burgers_command(root, args.worker)
    print(" ".join(command), flush=True)
    if not args.dry_run:
        subprocess.run(command, cwd=root, check=True)


if __name__ == "__main__":
    main()
