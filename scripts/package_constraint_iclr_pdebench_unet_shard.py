"""Package one completed U-Net shard and its exact final checkpoints."""

from __future__ import annotations

import argparse
import json
import os
import tarfile
from pathlib import Path
from typing import Any

import torch
from constraint_iclr_common import sha256_file

EXPECTED_SEEDS = {
    "v100a": list(range(7000, 7015)),
    "v100b": list(range(7015, 7030)),
}
EXPECTED_MECHANISMS = {"free", "free_res", "hard_abs", "hard", "projection"}
TRAINED_MECHANISMS = {"free", "free_res", "hard_abs", "hard"}
EXPECTED_BENCHMARK = "pdebench_advection_beta0.4_unet_factorial_v1"
EXPECTED_STAGE = "factorial_confirmation"
EXPECTED_CHECKPOINT_SCHEMA = "constraint-iclr-pdebench-v1"
EXPECTED_EPOCHS = 200


def _read_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        try:
            value = json.loads(line)
        except json.JSONDecodeError as error:
            raise RuntimeError(
                f"invalid shard JSONL line {line_number}: {error}"
            ) from error
        if not isinstance(value, dict):
            raise RuntimeError(f"shard JSONL line {line_number} is not an object")
        records.append(value)
    return records


def _checkpoint_prefix(worker_id: str) -> Path:
    return Path(
        "experiments/constraint_attribution_iclr/pdebench/"
        f"unet_factorial_checkpoints_{worker_id}_20260902"
    )


def validate_completed_shard(
    *, root: Path, input_path: Path, worker_id: str
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if worker_id not in EXPECTED_SEEDS:
        raise ValueError(f"unknown U-Net worker: {worker_id}")
    records = _read_records(input_path)
    expected_seeds = EXPECTED_SEEDS[worker_id]
    if len(records) != 5 * len(expected_seeds):
        raise RuntimeError(
            f"{worker_id} has {len(records)} records, expected {5 * len(expected_seeds)}"
        )
    run_ids = [str(record.get("run_id")) for record in records]
    if len(set(run_ids)) != len(run_ids):
        raise RuntimeError(f"{worker_id} has duplicate run IDs")
    coverage = {
        (int(record.get("seed", -1)), str(record.get("mechanism")))
        for record in records
    }
    expected_coverage = {
        (seed, mechanism)
        for seed in expected_seeds
        for mechanism in EXPECTED_MECHANISMS
    }
    if coverage != expected_coverage:
        raise RuntimeError(
            f"{worker_id} coverage mismatch: "
            f"missing={sorted(expected_coverage.difference(coverage))}, "
            f"extra={sorted(coverage.difference(expected_coverage))}"
        )
    for record in records:
        if record.get("stage") != EXPECTED_STAGE:
            raise RuntimeError(f"wrong stage for run {record.get('run_id')}")
        if record.get("benchmark_id") != EXPECTED_BENCHMARK:
            raise RuntimeError(f"wrong benchmark for run {record.get('run_id')}")

    trained = {
        (int(record["seed"]), str(record["mechanism"])): record
        for record in records
        if record["mechanism"] in TRAINED_MECHANISMS
    }
    prefix = _checkpoint_prefix(worker_id)
    checkpoints: list[dict[str, Any]] = []
    for key in sorted(trained):
        record = trained[key]
        checkpoint = record.get("checkpoint")
        if not isinstance(checkpoint, dict):
            raise RuntimeError(f"record {record.get('run_id')} has no checkpoint binding")
        raw_path = str(checkpoint.get("path"))
        relative_path = Path(raw_path)
        try:
            relative_path.relative_to(prefix)
        except ValueError as error:
            raise RuntimeError(
                f"checkpoint path is outside the registered worker directory: {relative_path}"
            ) from error
        resolved_root = root.resolve()
        path = (root / relative_path).resolve()
        if not path.is_relative_to(resolved_root):
            raise RuntimeError(f"checkpoint escapes the project root: {path}")
        if not path.is_file():
            raise RuntimeError(f"checkpoint is missing: {path}")
        payload = torch.load(path, map_location="cpu", weights_only=False)
        if not isinstance(payload, dict):
            raise RuntimeError(f"checkpoint payload is not a mapping: {path}")
        if payload.get("schema_version") != EXPECTED_CHECKPOINT_SCHEMA:
            raise RuntimeError(f"checkpoint schema mismatch: {path}")
        if payload.get("run_id") != record.get("run_id"):
            raise RuntimeError(f"checkpoint run ID mismatch: {path}")
        if int(payload.get("completed_epochs", -1)) != EXPECTED_EPOCHS:
            raise RuntimeError(f"checkpoint epoch count mismatch: {path}")
        if not isinstance(payload.get("model_state_dict"), dict):
            raise RuntimeError(f"checkpoint has no model state: {path}")
        checkpoints.append(
            {
                "seed": key[0],
                "mechanism": key[1],
                "run_id": record["run_id"],
                "path": raw_path,
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
                "payload_schema_version": payload["schema_version"],
                "completed_epochs": int(payload["completed_epochs"]),
            }
        )
    if len(checkpoints) != 4 * len(expected_seeds):
        raise RuntimeError(
            f"{worker_id} has {len(checkpoints)} final checkpoints, "
            f"expected {4 * len(expected_seeds)}"
        )
    return records, checkpoints


def package_completed_shard(
    *,
    root: Path,
    input_path: Path,
    worker_id: str,
    archive_path: Path,
    manifest_path: Path,
    sidecar_path: Path,
) -> dict[str, Any]:
    records, checkpoints = validate_completed_shard(
        root=root, input_path=input_path, worker_id=worker_id
    )
    relative_input = input_path.resolve().relative_to(root.resolve())
    relative_manifest = manifest_path.resolve().relative_to(root.resolve())
    manifest = {
        "schema_version": "constraint-iclr-pdebench-unet-shard-transfer-v1",
        "worker_id": worker_id,
        "seeds": EXPECTED_SEEDS[worker_id],
        "record_count": len(records),
        "records": {
            "path": str(relative_input),
            "sha256": sha256_file(input_path),
            "bytes": input_path.stat().st_size,
        },
        "checkpoint_count": len(checkpoints),
        "checkpoints": checkpoints,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_manifest = manifest_path.with_suffix(manifest_path.suffix + ".tmp")
    temporary_manifest.write_text(
        json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary_manifest, manifest_path)

    archive_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_archive = archive_path.with_suffix(archive_path.suffix + ".tmp")
    with tarfile.open(temporary_archive, "w:gz", format=tarfile.USTAR_FORMAT) as archive:
        archive.add(input_path, arcname=str(relative_input), recursive=False)
        for checkpoint in checkpoints:
            archive.add(
                root / str(checkpoint["path"]),
                arcname=str(checkpoint["path"]),
                recursive=False,
            )
        archive.add(manifest_path, arcname=str(relative_manifest), recursive=False)
    os.replace(temporary_archive, archive_path)
    archive_sha256 = sha256_file(archive_path)
    sidecar_path.write_text(
        f"{archive_sha256}  {archive_path.name}\n", encoding="utf-8"
    )
    return {
        **manifest,
        "archive": {
            "path": str(archive_path),
            "sha256": archive_sha256,
            "bytes": archive_path.stat().st_size,
            "members": 2 + len(checkpoints),
        },
        "manifest_sha256": sha256_file(manifest_path),
        "sidecar_sha256": sha256_file(sidecar_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--worker-id", choices=sorted(EXPECTED_SEEDS), required=True)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--sidecar", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    if args.validate_only:
        records, checkpoints = validate_completed_shard(
            root=args.root.resolve(),
            input_path=args.input.resolve(),
            worker_id=args.worker_id,
        )
        print(f"worker_id={args.worker_id}")
        print(f"record_count={len(records)}")
        print(f"checkpoint_count={len(checkpoints)}")
        return
    if args.archive is None or args.manifest is None or args.sidecar is None:
        parser.error("packaging requires --archive, --manifest, and --sidecar")
    result = package_completed_shard(
        root=args.root.resolve(),
        input_path=args.input.resolve(),
        worker_id=args.worker_id,
        archive_path=args.archive.resolve(),
        manifest_path=args.manifest.resolve(),
        sidecar_path=args.sidecar.resolve(),
    )
    print(f"worker_id={result['worker_id']}")
    print(f"record_count={result['record_count']}")
    print(f"checkpoint_count={result['checkpoint_count']}")
    print(f"archive_sha256={result['archive']['sha256']}")


if __name__ == "__main__":
    main()
