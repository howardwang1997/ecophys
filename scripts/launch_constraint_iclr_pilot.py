"""Execute one worker partition from the frozen ICLR pilot manifest."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any

from omegaconf import OmegaConf

RUNNERS = {
    "pde": "scripts/run_constraint_iclr_pde.py",
    "market": "scripts/run_constraint_iclr_market.py",
}


def hydra_value(value: Any) -> str:
    if isinstance(value, list):
        return "[" + ",".join(hydra_value(item) for item in value) + "]"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def build_commands(root: Path, manifest: dict[str, Any], worker: str) -> list[tuple[str, list[str]]]:
    if worker not in manifest["workers"]:
        raise KeyError(f"unknown worker {worker}; expected one of {sorted(manifest['workers'])}")
    commands: list[tuple[str, list[str]]] = []
    for job in manifest["workers"][worker]:
        runner = RUNNERS[str(job["runner"])]
        command = [
            sys.executable,
            str(root / runner),
            "--config-name",
            str(job["config"]),
        ]
        command.extend(f"{key}={hydra_value(value)}" for key, value in job["overrides"].items())
        commands.append((str(job["name"]), command))
    return commands


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", required=True)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("configs/constraint_iclr/pilot_manifest.yaml"),
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--job",
        action="append",
        default=[],
        help="Run only the named manifest job; repeat for multiple jobs.",
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    manifest_path = args.manifest if args.manifest.is_absolute() else root / args.manifest
    loaded = OmegaConf.to_container(OmegaConf.load(manifest_path), resolve=True)
    if not isinstance(loaded, dict):
        raise TypeError("pilot manifest must resolve to a mapping")
    requested = set(args.job)
    for name, command in build_commands(root, loaded, args.worker):
        if requested and name not in requested:
            continue
        print(f"[{name}] {' '.join(command)}", flush=True)
        if not args.dry_run:
            subprocess.run(command, cwd=root, check=True)


if __name__ == "__main__":
    main()
