#!/usr/bin/env python3
"""Materialize two frozen NEMDE ranges from R2 with zero source requests."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ecomd.research.aemo_nemde_rhs_reconstruction import (
    MATERIALIZATION_SCHEMA_VERSION,
    SOURCE_MANIFEST_PATH,
    file_sha256,
    load_manifest,
    manifest_sha256,
    utc_now,
    validate_manifest,
)


def _tracked_clean_commit() -> str:
    for arguments in (["git", "diff", "--quiet"], ["git", "diff", "--cached", "--quiet"]):
        if subprocess.run(arguments, cwd=ROOT, check=False).returncode != 0:
            raise RuntimeError("tracked files changed after the frozen protocol commit")
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=ROOT / SOURCE_MANIFEST_PATH)
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env.r2")
    arguments = parser.parse_args()
    commit = _tracked_clean_commit()
    manifest = load_manifest(arguments.manifest)
    errors = validate_manifest(manifest)
    if errors:
        raise RuntimeError("invalid NEMDE-RHS manifest: " + "; ".join(errors))
    outputs = cast(dict[str, object], manifest["outputs"])
    raw_root = ROOT / cast(str, outputs["raw_root"])
    receipt_path = ROOT / cast(str, outputs["materialization_receipt"])
    if receipt_path.exists():
        raise FileExistsError(receipt_path)
    raw_root.mkdir(parents=True, exist_ok=True)
    specs = cast(list[dict[str, object]], manifest["objects"])
    for spec in specs:
        path = raw_root / cast(str, spec["expected_filename"])
        if path.exists():
            raise FileExistsError(path)

    _load_env(arguments.env_file)
    missing = [
        key
        for key in ("R2_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY")
        if not os.environ.get(key)
    ]
    if missing:
        raise RuntimeError(f"missing R2 environment keys: {missing}")
    bucket = "ecophys"
    if os.environ.get("R2_BUCKET", bucket) != bucket:
        raise RuntimeError("configured R2 bucket differs from frozen bucket")
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
        config=Config(signature_version="s3v4", retries={"max_attempts": 5, "mode": "standard"}),
    )
    materialized: list[dict[str, object]] = []
    for spec in specs:
        key = cast(str, spec["r2_key"])
        expected_sha = cast(str, spec["range_sha256"])
        expected_bytes = cast(int, spec["range_bytes"])
        head = cast(dict[str, Any], client.head_object(Bucket=bucket, Key=key))
        remote_sha = cast(dict[str, str], head.get("Metadata", {})).get("sha256")
        remote_bytes = int(head.get("ContentLength", -1))
        if remote_sha != expected_sha or remote_bytes != expected_bytes:
            raise RuntimeError(f"frozen R2 object differs: r2://{bucket}/{key}")
        path = raw_root / cast(str, spec["expected_filename"])
        client.download_file(bucket, key, str(path))
        local_bytes = path.stat().st_size
        local_sha = file_sha256(path)
        verified = local_bytes == expected_bytes and local_sha == expected_sha
        materialized.append(
            {
                "object_id": spec["object_id"],
                "r2_key": key,
                "local_filename": spec["expected_filename"],
                "remote_content_length": remote_bytes,
                "remote_metadata_sha256": remote_sha,
                "remote_etag": str(head.get("ETag", "")).strip('"'),
                "local_bytes": local_bytes,
                "local_sha256": local_sha,
                "verified": verified,
                "local_header_opened": False,
                "xml_opened": False,
            }
        )
        print(
            json.dumps({"object_id": spec["object_id"], "verified": verified}, sort_keys=True),
            flush=True,
        )
    payload: dict[str, object] = {
        "schema_version": MATERIALIZATION_SCHEMA_VERSION,
        "generated_at": utc_now(),
        "protocol_git_commit": commit,
        "source_manifest": arguments.manifest.relative_to(ROOT).as_posix(),
        "source_manifest_sha256": manifest_sha256(arguments.manifest),
        "bucket": bucket,
        "new_aemo_request_count": 0,
        "objects": materialized,
        "all_verified": len(materialized) == 2 and all(item["verified"] is True for item in materialized),
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
