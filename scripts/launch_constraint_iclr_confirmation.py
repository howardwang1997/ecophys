"""Launch locked confirmation jobs without reading pilot OOD outcomes."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from constraint_iclr_common import sha256_file
from launch_constraint_iclr_pilot import RUNNERS, hydra_value
from omegaconf import OmegaConf


def build_commands(
    root: Path,
    manifest: dict[str, Any],
    lock: dict[str, Any],
    worker: str,
    *,
    lock_path: Path,
    lock_sha256: str,
) -> list[tuple[str, list[str]]]:
    systems = [str(value) for value in manifest["workers"][worker]]
    commands: list[tuple[str, list[str]]] = []
    for system_key in systems:
        if system_key not in lock["systems"]:
            raise KeyError(f"lock is missing required system {system_key}")
        specification = manifest["systems"][system_key]
        output = f"experiments/constraint_attribution_iclr/confirmation/{system_key.replace(':', '_')}.jsonl"
        for job in lock["systems"][system_key]["confirmation_jobs"]:
            overrides = {
                **specification["overrides"],
                "capacity_grid": [int(job["capacity"])],
                "epochs_grid": [int(job["epochs"])],
                "lr_grid": [float(job["learning_rate"])],
                "mechanisms": [str(job["mechanism"])],
                "selection_lock_path": str(lock_path),
                "selection_lock_sha256": lock_sha256,
                "output": output,
            }
            command = [
                sys.executable,
                str(root / RUNNERS[str(specification["runner"])]),
                "--config-name",
                str(specification["config"]),
            ]
            command.extend(f"{key}={hydra_value(value)}" for key, value in overrides.items())
            name = f"{system_key}:{job['mechanism']}:{job['config_id']}"
            commands.append((name, command))
    return commands


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", required=True)
    parser.add_argument("--lock", type=Path, required=True)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("configs/constraint_iclr/confirmation_manifest.yaml"),
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    manifest_path = args.manifest if args.manifest.is_absolute() else root / args.manifest
    lock_path = args.lock if args.lock.is_absolute() else root / args.lock
    manifest = OmegaConf.to_container(OmegaConf.load(manifest_path), resolve=True)
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise TypeError("confirmation manifest must resolve to a mapping")
    try:
        lock_reference = lock_path.relative_to(root)
    except ValueError:
        lock_reference = lock_path
    lock_sha256 = sha256_file(lock_path)
    for name, command in build_commands(
        root,
        manifest,
        lock,
        args.worker,
        lock_path=lock_reference,
        lock_sha256=lock_sha256,
    ):
        print(f"[{name}] {' '.join(command)}", flush=True)
        if not args.dry_run:
            subprocess.run(command, cwd=root, check=True)


if __name__ == "__main__":
    main()
