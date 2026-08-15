#!/usr/bin/env python3
"""Download the three frozen E1b AEMO objects as opaque bytes."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import cast

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import requests

from ecomd.market_world.provenance import require_clean_repository
from ecomd.research.aemo_bundle_confirmation import (
    DOWNLOAD_SCHEMA_VERSION,
    SOURCE_MANIFEST_PATH,
    load_bundle_manifest,
    manifest_sha256,
    utc_now,
    validate_bundle_manifest,
)

USER_AGENT = "EcoPhys-AEMO-bundle-confirmation/1.0"
CHUNK_BYTES = 1 << 20


def _download_once(
    session: requests.Session,
    *,
    url: str,
    partial_path: Path,
    expected_bytes: int,
) -> tuple[int | None, int, str | None, dict[str, str], str | None]:
    status: int | None = None
    observed_bytes = 0
    transport_error: str | None = None
    response_headers: dict[str, str] = {}
    digest = hashlib.sha256()
    try:
        response = session.get(
            url,
            stream=True,
            timeout=(30.0, 180.0),
            allow_redirects=False,
        )
        status = response.status_code
        response_headers = {
            key: value
            for key, value in response.headers.items()
            if key.lower() in {"content-length", "content-type", "etag", "last-modified"}
        }
        if status == 200:
            response.raw.decode_content = False
            with partial_path.open("xb") as handle:
                while chunk := response.raw.read(CHUNK_BYTES):
                    handle.write(chunk)
                    digest.update(chunk)
                    observed_bytes += len(chunk)
                    if observed_bytes > expected_bytes:
                        transport_error = "response exceeded frozen exact-byte cap"
                        break
                handle.flush()
                os.fsync(handle.fileno())
        response.close()
    except (OSError, requests.RequestException) as error:
        transport_error = f"{type(error).__name__}: {error}"
    sha256 = digest.hexdigest() if observed_bytes else None
    return status, observed_bytes, transport_error, response_headers, sha256


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / SOURCE_MANIFEST_PATH,
    )
    arguments = parser.parse_args()
    commit = require_clean_repository(ROOT)
    manifest = load_bundle_manifest(arguments.manifest)
    errors = validate_bundle_manifest(manifest)
    if errors:
        raise RuntimeError("invalid AEMO E1b manifest: " + "; ".join(errors))
    outputs = cast(dict[str, object], manifest["outputs"])
    raw_root = ROOT / cast(str, outputs["raw_root"])
    receipt_path = ROOT / cast(str, outputs["download_receipt"])
    if receipt_path.exists():
        raise FileExistsError(receipt_path)
    raw_root.mkdir(parents=True, exist_ok=True)

    objects = cast(list[dict[str, object]], manifest["objects"])
    for spec in objects:
        final_path = raw_root / cast(str, spec["expected_filename"])
        partial_path = final_path.with_suffix(final_path.suffix + ".part")
        if final_path.exists() or partial_path.exists():
            raise FileExistsError(f"pre-existing E1b payload: {final_path}")

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept-Encoding": "identity"})
    receipts: list[dict[str, object]] = []
    for index, spec in enumerate(objects):
        filename = cast(str, spec["expected_filename"])
        expected_bytes = cast(int, spec["expected_bytes"])
        final_path = raw_root / filename
        partial_path = final_path.with_suffix(final_path.suffix + ".part")
        status, observed_bytes, transport_error, headers, sha256 = _download_once(
            session,
            url=cast(str, spec["url"]),
            partial_path=partial_path,
            expected_bytes=expected_bytes,
        )
        download_pass = (
            status == 200
            and transport_error is None
            and observed_bytes == expected_bytes
            and sha256 is not None
        )
        if download_pass:
            partial_path.replace(final_path)
        receipt: dict[str, object] = {
            "request_index": index,
            "request_count": 1,
            "object_id": spec["object_id"],
            "url": spec["url"],
            "retrieved_at": utc_now(),
            "http_status": status,
            "response_headers": headers,
            "transport_error": transport_error,
            "expected_bytes": expected_bytes,
            "observed_bytes": observed_bytes,
            "sha256": sha256,
            "local_filename": filename,
            "download_pass": download_pass,
            "zip_opened": False,
            "csv_rows_opened": False,
        }
        receipts.append(receipt)
        print(
            json.dumps(
                {
                    "object_id": spec["object_id"],
                    "http_status": status,
                    "observed_bytes": observed_bytes,
                    "expected_bytes": expected_bytes,
                    "download_pass": download_pass,
                },
                sort_keys=True,
            ),
            flush=True,
        )

    overall_pass = len(receipts) == len(objects) and all(item["download_pass"] is True for item in receipts)
    payload: dict[str, object] = {
        "schema_version": DOWNLOAD_SCHEMA_VERSION,
        "generated_at": utc_now(),
        "protocol_git_commit": commit,
        "source_manifest": arguments.manifest.relative_to(ROOT).as_posix(),
        "source_manifest_sha256": manifest_sha256(arguments.manifest),
        "request_policy": "exactly_one_get_per_frozen_object_no_retry_no_replacement",
        "objects": receipts,
        "pass": overall_pass,
        "zip_opened": False,
        "csv_rows_opened": False,
        "gpu_used": False,
        "paid_data_used": False,
        "target_outcome_used": False,
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
