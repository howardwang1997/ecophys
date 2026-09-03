"""Download, verify, and lock the frozen PDEBench external dataset."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from constraint_iclr_common import sha256_file
from omegaconf import OmegaConf
from run_constraint_iclr_pdebench_fno import inspect_public_dataset, resolve_path


def download_with_curl(url: str, destination: Path, expected_bytes: int) -> None:
    if destination.is_file():
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + ".part")
    if partial.exists() and partial.stat().st_size > expected_bytes:
        raise RuntimeError(f"partial download exceeds frozen byte count: {partial}")
    subprocess.run(
        [
            "curl",
            "--fail",
            "--location",
            "--silent",
            "--show-error",
            "--retry",
            "5",
            "--retry-all-errors",
            "--continue-at",
            "-",
            "--output",
            str(partial),
            url,
        ],
        check=True,
    )
    if partial.stat().st_size != expected_bytes:
        raise RuntimeError(
            f"downloaded byte count mismatch: expected {expected_bytes}, got {partial.stat().st_size}"
        )
    os.replace(partial, destination)


def build_data_lock(
    *,
    root: Path,
    config_path: Path,
    resolved: dict[str, Any],
    inspection: dict[str, Any],
) -> dict[str, Any]:
    protocol_path = resolve_path(root, str(resolved["protocol_path"]))
    expected_protocol_sha256 = resolved.get("protocol_sha256")
    if not expected_protocol_sha256:
        raise RuntimeError("set protocol_sha256 in the Hydra config before locking data")
    actual_protocol_sha256 = sha256_file(protocol_path)
    if actual_protocol_sha256 != str(expected_protocol_sha256):
        raise RuntimeError(
            "protocol SHA-256 mismatch: "
            f"expected {expected_protocol_sha256}, got {actual_protocol_sha256}"
        )
    schema_amendment_path = resolve_path(root, str(resolved["schema_amendment_path"]))
    expected_schema_amendment_sha256 = resolved.get("schema_amendment_sha256")
    if not expected_schema_amendment_sha256:
        raise RuntimeError("set schema_amendment_sha256 before locking data")
    actual_schema_amendment_sha256 = sha256_file(schema_amendment_path)
    if actual_schema_amendment_sha256 != str(expected_schema_amendment_sha256):
        raise RuntimeError(
            "schema-amendment SHA-256 mismatch: "
            f"expected {expected_schema_amendment_sha256}, got {actual_schema_amendment_sha256}"
        )
    dataset_cfg = resolved["dataset"]
    return {
        "schema_version": "constraint-iclr-pdebench-data-lock-v1",
        "created_at": datetime.now(UTC).isoformat(),
        "benchmark_id": resolved["benchmark_id"],
        "protocol_path": str(protocol_path.relative_to(root)),
        "protocol_sha256": actual_protocol_sha256,
        "schema_amendment_path": str(schema_amendment_path.relative_to(root)),
        "schema_amendment_sha256": actual_schema_amendment_sha256,
        "config_path": str(config_path.relative_to(root)),
        "config_sha256": sha256_file(config_path),
        "source": {
            "doi": dataset_cfg["doi"],
            "version": int(dataset_cfg["version"]),
            "file_id": int(dataset_cfg["file_id"]),
            "url": dataset_cfg["url"],
            "filename": dataset_cfg["filename"],
            "license": "CC BY 4.0",
        },
        "inspection": inspection,
    }


def write_new_lock(path: Path, lock: dict[str, Any]) -> None:
    if path.exists():
        existing = json.loads(path.read_text(encoding="utf-8"))
        if existing.get("inspection") == lock.get("inspection") and existing.get(
            "protocol_sha256"
        ) == lock.get("protocol_sha256") and existing.get(
            "schema_amendment_sha256"
        ) == lock.get("schema_amendment_sha256"):
            return
        raise RuntimeError(f"refusing to overwrite a non-identical data lock: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(lock, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/constraint_iclr/pdebench_advection_fno.yaml"),
    )
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    config_path = resolve_path(root, args.config)
    resolved = OmegaConf.to_container(OmegaConf.load(config_path), resolve=True)
    if not isinstance(resolved, dict):
        raise TypeError("PDEBench config must resolve to a mapping")
    dataset_cfg = resolved["dataset"]
    if not isinstance(dataset_cfg, dict):
        raise TypeError("dataset config must resolve to a mapping")
    dataset_path = resolve_path(root, str(dataset_cfg["path"]))
    if args.download:
        download_with_curl(
            str(dataset_cfg["url"]), dataset_path, int(dataset_cfg["expected_bytes"])
        )
    inspection = inspect_public_dataset(dataset_path, dataset_cfg)
    lock = build_data_lock(
        root=root,
        config_path=config_path,
        resolved=resolved,
        inspection=inspection,
    )
    lock_path = resolve_path(root, str(dataset_cfg["lock_path"]))
    write_new_lock(lock_path, lock)
    print(f"data_lock={lock_path}")
    print(f"data_lock_sha256={sha256_file(lock_path)}")
    print(f"dataset_sha256={inspection['sha256']}")
    print("dataset_invariant_gate=passed")


if __name__ == "__main__":
    main()
