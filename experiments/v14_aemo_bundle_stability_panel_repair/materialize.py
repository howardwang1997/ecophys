#!/usr/bin/env python3
"""Materialize all repair inputs from verified R2 with zero AEMO requests."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ecomd.market_world.provenance import require_clean_repository
from ecomd.research.aemo_bundle_stability_repair import (
    MATERIALIZATION_SCHEMA_VERSION,
    SOURCE_MANIFEST_PATH,
    load_repair_manifest,
    manifest_sha256,
    utc_now,
    validate_original_provenance,
    validate_repair_manifest,
)
from ecomd.research.aemo_row_conformance import file_sha256


def _load_env(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(path)
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, raw_value = line.partition("=")
        value = raw_value.strip().strip('"').strip("'")
        if value:
            os.environ.setdefault(key.strip(), value)


def _head(client: Any, bucket: str, key: str) -> dict[str, Any]:
    return cast(dict[str, Any], client.head_object(Bucket=bucket, Key=key))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / SOURCE_MANIFEST_PATH,
    )
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env.r2")
    arguments = parser.parse_args()
    commit = require_clean_repository(ROOT)
    manifest = load_repair_manifest(arguments.manifest)
    current_manifest_sha = manifest_sha256(arguments.manifest)
    manifest_errors = validate_repair_manifest(manifest, source_sha256=current_manifest_sha)
    provenance_errors = validate_original_provenance(ROOT)
    if manifest_errors or provenance_errors:
        raise RuntimeError("invalid repair protocol: " + "; ".join([*manifest_errors, *provenance_errors]))
    outputs = cast(dict[str, object], manifest["outputs"])
    raw_root = ROOT / cast(str, outputs["raw_root"])
    receipt_path = ROOT / cast(str, outputs["materialization_receipt"])
    if receipt_path.exists():
        raise FileExistsError(receipt_path)
    raw_root.mkdir(parents=True, exist_ok=True)
    specs = cast(list[dict[str, object]], manifest["objects"])
    for spec in specs:
        path = raw_root / cast(str, spec["expected_filename"])
        partial_path = path.with_suffix(path.suffix + ".part")
        if path.exists() or partial_path.exists():
            raise FileExistsError(f"pre-existing repair payload: {path}")

    _load_env(arguments.env_file)
    missing = [
        key
        for key in ("R2_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY")
        if not os.environ.get(key)
    ]
    if missing:
        raise RuntimeError(f"missing R2 environment keys: {missing}")
    account_id = os.environ["R2_ACCOUNT_ID"]
    endpoint_url = os.environ.get("R2_ENDPOINT_URL", f"https://{account_id}.r2.cloudflarestorage.com")

    import boto3
    from botocore.config import Config

    client = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        region_name="auto",
        config=Config(
            signature_version="s3v4",
            retries={"max_attempts": 5, "mode": "standard"},
        ),
    )
    materialized: list[dict[str, object]] = []
    for spec in specs:
        bucket = cast(str, spec["r2_bucket"])
        key = cast(str, spec["r2_key"])
        expected_bytes = cast(int, spec["expected_bytes"])
        expected_sha = cast(str, spec["sha256"])
        head = _head(client, bucket, key)
        metadata = cast(dict[str, str], head.get("Metadata", {}))
        remote_bytes = int(head.get("ContentLength", -1))
        remote_sha = metadata.get("sha256")
        if remote_bytes != expected_bytes or remote_sha != expected_sha:
            raise RuntimeError(f"frozen repair R2 object changed: {key}")
        path = raw_root / cast(str, spec["expected_filename"])
        partial_path = path.with_suffix(path.suffix + ".part")
        client.download_file(bucket, key, str(partial_path))
        local_verified = (
            partial_path.stat().st_size == expected_bytes and file_sha256(partial_path) == expected_sha
        )
        if local_verified:
            partial_path.replace(path)
        item: dict[str, object] = {
            "object_id": spec["object_id"],
            "r2_bucket": bucket,
            "r2_key": key,
            "observed_bytes": expected_bytes,
            "sha256": expected_sha,
            "remote_content_length": remote_bytes,
            "remote_metadata_sha256": remote_sha,
            "remote_etag": str(head.get("ETag", "")).strip('"'),
            "source_get_performed": False,
            "verified": local_verified,
        }
        materialized.append(item)
        print(
            json.dumps(
                {
                    "object_id": spec["object_id"],
                    "source_get_performed": False,
                    "verified": local_verified,
                },
                sort_keys=True,
            ),
            flush=True,
        )
    all_verified = len(materialized) == len(specs) and all(item["verified"] is True for item in materialized)
    payload: dict[str, object] = {
        "schema_version": MATERIALIZATION_SCHEMA_VERSION,
        "generated_at": utc_now(),
        "protocol_git_commit": commit,
        "source_manifest": arguments.manifest.relative_to(ROOT).as_posix(),
        "source_manifest_sha256": current_manifest_sha,
        "aemo_source_request_count": 0,
        "objects": materialized,
        "all_verified": all_verified,
        "zip_opened": False,
        "csv_rows_opened": False,
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
