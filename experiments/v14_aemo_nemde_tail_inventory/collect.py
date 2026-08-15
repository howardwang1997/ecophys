#!/usr/bin/env python3
"""Download two frozen AEMO NEMDE ZIP suffixes as opaque bytes."""

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
from ecomd.research.aemo_nemde_tail_inventory import (
    DOWNLOAD_SCHEMA_VERSION,
    SOURCE_MANIFEST_PATH,
    TAIL_BYTES,
    load_manifest,
    manifest_sha256,
    utc_now,
    validate_manifest,
)

USER_AGENT = "EcoPhys-AEMO-NEMDE-tail-inventory/1.0"
CHUNK_BYTES = 1 << 20


def _download_tail_once(
    session: requests.Session,
    *,
    url: str,
    partial_path: Path,
) -> tuple[int | None, int, str | None, dict[str, str], str | None]:
    status: int | None = None
    observed_bytes = 0
    transport_error: str | None = None
    response_headers: dict[str, str] = {}
    digest = hashlib.sha256()
    try:
        response = session.get(
            url,
            headers={"Range": f"bytes=-{TAIL_BYTES}"},
            stream=True,
            timeout=(30.0, 240.0),
            allow_redirects=False,
        )
        status = response.status_code
        response_headers = {
            key: value
            for key, value in response.headers.items()
            if key.lower()
            in {"content-length", "content-range", "content-type", "etag", "last-modified"}
        }
        if status == 206:
            response.raw.decode_content = False
            with partial_path.open("xb") as handle:
                while chunk := response.raw.read(CHUNK_BYTES):
                    handle.write(chunk)
                    digest.update(chunk)
                    observed_bytes += len(chunk)
                    if observed_bytes > TAIL_BYTES:
                        transport_error = "response exceeded frozen suffix cap"
                        break
                handle.flush()
                os.fsync(handle.fileno())
        response.close()
    except (OSError, requests.RequestException) as error:
        transport_error = f"{type(error).__name__}: {error}"
    return (
        status,
        observed_bytes,
        transport_error,
        response_headers,
        digest.hexdigest() if observed_bytes else None,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=ROOT / SOURCE_MANIFEST_PATH)
    arguments = parser.parse_args()
    commit = require_clean_repository(ROOT)
    manifest = load_manifest(arguments.manifest)
    errors = validate_manifest(manifest)
    if errors:
        raise RuntimeError("invalid NEMDE-tail manifest: " + "; ".join(errors))
    outputs = cast(dict[str, object], manifest["outputs"])
    raw_root = ROOT / cast(str, outputs["raw_root"])
    receipt_path = ROOT / cast(str, outputs["download_receipt"])
    if receipt_path.exists():
        raise FileExistsError(receipt_path)
    raw_root.mkdir(parents=True, exist_ok=True)
    specs = cast(list[dict[str, object]], manifest["objects"])
    for spec in specs:
        final_path = raw_root / cast(str, spec["expected_filename"])
        partial_path = final_path.with_suffix(final_path.suffix + ".part")
        if final_path.exists() or partial_path.exists():
            raise FileExistsError(final_path)

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept-Encoding": "identity"})
    receipts: list[dict[str, object]] = []
    for index, spec in enumerate(specs):
        filename = cast(str, spec["expected_filename"])
        final_path = raw_root / filename
        partial_path = final_path.with_suffix(final_path.suffix + ".part")
        status, observed, transport_error, headers, sha256 = _download_tail_once(
            session,
            url=cast(str, spec["url"]),
            partial_path=partial_path,
        )
        total = cast(int, spec["expected_archive_bytes"])
        content_range = headers.get("Content-Range") or headers.get("content-range")
        expected_range = f"bytes {total - TAIL_BYTES}-{total - 1}/{total}"
        passed = (
            status == 206
            and transport_error is None
            and observed == TAIL_BYTES
            and content_range == expected_range
            and sha256 is not None
        )
        if passed:
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
            "observed_bytes": observed,
            "sha256": sha256,
            "local_filename": filename,
            "download_pass": passed,
            "zip_metadata_opened": False,
            "xml_member_opened": False,
        }
        receipts.append(receipt)
        print(
            json.dumps(
                {
                    "object_id": spec["object_id"],
                    "http_status": status,
                    "observed_bytes": observed,
                    "download_pass": passed,
                },
                sort_keys=True,
            ),
            flush=True,
        )
    overall_pass = len(receipts) == 2 and all(item["download_pass"] is True for item in receipts)
    payload: dict[str, object] = {
        "schema_version": DOWNLOAD_SCHEMA_VERSION,
        "generated_at": utc_now(),
        "protocol_git_commit": commit,
        "source_manifest": arguments.manifest.relative_to(ROOT).as_posix(),
        "source_manifest_sha256": manifest_sha256(arguments.manifest),
        "request_policy": "one_fixed_suffix_range_per_object_no_retry_no_extension",
        "objects": receipts,
        "pass": overall_pass,
        "zip_metadata_opened": False,
        "xml_member_opened": False,
        "gpu_used": False,
        "paid_data_used": False,
        "target_outcome_used": False,
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
