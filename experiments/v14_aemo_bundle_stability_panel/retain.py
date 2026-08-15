#!/usr/bin/env python3
"""Retain new panel inputs and materialize prior identities from verified R2."""

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

from ecomd.research.aemo_bundle_stability_panel import (
    RETENTION_SCHEMA_VERSION,
    SOURCE_MANIFEST_PATH,
    load_download_receipt,
    load_panel_manifest,
    manifest_sha256,
    utc_now,
    validate_download_receipt,
    validate_panel_manifest,
)
from ecomd.research.aemo_row_conformance import file_sha256


def _tracked_clean_commit() -> str:
    for arguments in (
        ["git", "diff", "--quiet"],
        ["git", "diff", "--cached", "--quiet"],
    ):
        clean_result = subprocess.run(arguments, cwd=ROOT, check=False)
        if clean_result.returncode != 0:
            raise RuntimeError("tracked files changed after the frozen protocol commit")
    commit_result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return commit_result.stdout.strip()


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


def _head_or_none(client: Any, bucket: str, key: str) -> dict[str, Any] | None:
    from botocore.exceptions import ClientError

    try:
        return cast(dict[str, Any], client.head_object(Bucket=bucket, Key=key))
    except ClientError as error:
        code = str(error.response.get("Error", {}).get("Code", ""))
        if code in {"404", "NoSuchKey", "NotFound"}:
            return None
        raise


def _remote_integrity(
    head: dict[str, Any], *, expected_bytes: int, expected_sha: str
) -> tuple[int, str | None, bool]:
    remote_bytes = int(head.get("ContentLength", -1))
    metadata = cast(dict[str, str], head.get("Metadata", {}))
    remote_sha = metadata.get("sha256")
    return remote_bytes, remote_sha, (remote_bytes == expected_bytes and remote_sha == expected_sha)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / SOURCE_MANIFEST_PATH,
    )
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env.r2")
    arguments = parser.parse_args()
    commit = _tracked_clean_commit()
    manifest = load_panel_manifest(arguments.manifest)
    current_manifest_sha = manifest_sha256(arguments.manifest)
    manifest_errors = validate_panel_manifest(manifest, source_sha256=current_manifest_sha)
    if manifest_errors:
        raise RuntimeError("invalid AEMO panel manifest: " + "; ".join(manifest_errors))
    outputs = cast(dict[str, object], manifest["outputs"])
    raw_root = ROOT / cast(str, outputs["raw_root"])
    download_path = ROOT / cast(str, outputs["download_receipt"])
    retention_path = ROOT / cast(str, outputs["retention_receipt"])
    if retention_path.exists():
        raise FileExistsError(retention_path)
    download = load_download_receipt(download_path)
    download_errors = validate_download_receipt(download, manifest)
    if download_errors:
        raise RuntimeError("invalid panel download receipt: " + "; ".join(download_errors))
    if download["protocol_git_commit"] != commit:
        raise RuntimeError("download was not produced by the current frozen commit")

    downloaded = cast(list[dict[str, object]], download["objects"])
    new_specs = cast(list[dict[str, object]], manifest["new_objects"])
    for index, (item, spec) in enumerate(zip(downloaded, new_specs, strict=True)):
        path = raw_root / cast(str, spec["expected_filename"])
        if not path.is_file():
            raise FileNotFoundError(path)
        if path.stat().st_size != item["observed_bytes"] or file_sha256(path) != item["sha256"]:
            raise RuntimeError(f"new panel object {index} changed after download")

    _load_env(arguments.env_file)
    missing = [
        key
        for key in ("R2_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY")
        if not os.environ.get(key)
    ]
    if missing:
        raise RuntimeError(f"missing R2 environment keys: {missing}")
    contract = cast(dict[str, object], manifest["retention_contract"])
    bucket = cast(str, contract["bucket"])
    configured_bucket = os.environ.get("R2_BUCKET", bucket)
    if configured_bucket != bucket:
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
        config=Config(
            signature_version="s3v4",
            retries={"max_attempts": 5, "mode": "standard"},
        ),
    )

    retained: list[dict[str, object]] = []
    for item, spec in zip(downloaded, new_specs, strict=True):
        path = raw_root / cast(str, spec["expected_filename"])
        key = cast(str, spec["r2_key"])
        expected_sha = cast(str, item["sha256"])
        expected_bytes = cast(int, item["observed_bytes"])
        head = _head_or_none(client, bucket, key)
        uploaded = False
        if head is not None:
            _, _, remote_matches = _remote_integrity(
                head,
                expected_bytes=expected_bytes,
                expected_sha=expected_sha,
            )
            if not remote_matches:
                raise RuntimeError(f"refusing to overwrite mismatched r2://{bucket}/{key}")
        else:
            client.upload_file(
                str(path),
                bucket,
                key,
                ExtraArgs={
                    "ContentType": "application/zip",
                    "Metadata": {"sha256": expected_sha},
                },
            )
            uploaded = True
        verified_head = _head_or_none(client, bucket, key)
        if verified_head is None:
            raise RuntimeError(f"R2 object absent after upload: {key}")
        remote_bytes, remote_sha, verified = _remote_integrity(
            verified_head,
            expected_bytes=expected_bytes,
            expected_sha=expected_sha,
        )
        retained.append(
            {
                "object_id": spec["object_id"],
                "r2_bucket": bucket,
                "r2_key": key,
                "observed_bytes": expected_bytes,
                "sha256": expected_sha,
                "remote_content_length": remote_bytes,
                "remote_metadata_sha256": remote_sha,
                "remote_etag": str(verified_head.get("ETag", "")).strip('"'),
                "uploaded_in_this_run": uploaded,
                "materialization": "source_download_uploaded_to_frozen_r2",
                "verified": verified,
            }
        )
        print(
            json.dumps(
                {
                    "object_id": spec["object_id"],
                    "uploaded": uploaded,
                    "verified": verified,
                },
                sort_keys=True,
            ),
            flush=True,
        )

    reused_specs = cast(list[dict[str, object]], manifest["reused_objects"])
    for spec in reused_specs:
        filename = cast(str, spec["expected_filename"])
        path = raw_root / filename
        partial_path = path.with_suffix(path.suffix + ".part")
        if path.exists() or partial_path.exists():
            raise FileExistsError(f"pre-existing reused identity payload: {path}")
        reuse_bucket = cast(str, spec["r2_bucket"])
        key = cast(str, spec["r2_key"])
        expected_sha = cast(str, spec["sha256"])
        expected_bytes = cast(int, spec["expected_bytes"])
        head = _head_or_none(client, reuse_bucket, key)
        if head is None:
            raise RuntimeError(f"frozen reused R2 object is absent: {key}")
        remote_bytes, remote_sha, remote_verified = _remote_integrity(
            head,
            expected_bytes=expected_bytes,
            expected_sha=expected_sha,
        )
        if not remote_verified:
            raise RuntimeError(f"frozen reused R2 object changed: {key}")
        client.download_file(reuse_bucket, key, str(partial_path))
        local_verified = (
            partial_path.stat().st_size == expected_bytes and file_sha256(partial_path) == expected_sha
        )
        if local_verified:
            partial_path.replace(path)
        retained.append(
            {
                "object_id": spec["object_id"],
                "r2_bucket": reuse_bucket,
                "r2_key": key,
                "observed_bytes": expected_bytes,
                "sha256": expected_sha,
                "remote_content_length": remote_bytes,
                "remote_metadata_sha256": remote_sha,
                "remote_etag": str(head.get("ETag", "")).strip('"'),
                "uploaded_in_this_run": False,
                "source_get_performed": False,
                "materialization": "verified_prior_r2_download_no_source_get",
                "verified": remote_verified and local_verified,
            }
        )
        print(
            json.dumps(
                {
                    "object_id": spec["object_id"],
                    "source_get_performed": False,
                    "verified": remote_verified and local_verified,
                },
                sort_keys=True,
            ),
            flush=True,
        )

    all_verified = len(retained) == len(new_specs) + len(reused_specs) and all(
        item["verified"] is True for item in retained
    )
    payload: dict[str, object] = {
        "schema_version": RETENTION_SCHEMA_VERSION,
        "generated_at": utc_now(),
        "protocol_git_commit": commit,
        "source_manifest": arguments.manifest.relative_to(ROOT).as_posix(),
        "source_manifest_sha256": current_manifest_sha,
        "bucket": bucket,
        "new_object_prefix": contract["new_object_prefix"],
        "objects": retained,
        "all_verified": all_verified,
        "zip_opened": False,
        "csv_rows_opened": False,
    }
    retention_path.parent.mkdir(parents=True, exist_ok=True)
    retention_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
