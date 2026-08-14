#!/usr/bin/env python3
"""Download and audit the ten held-out AEMO archives without opening data rows."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import cast

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import requests
import yaml

from ecomd.market_world.provenance import require_clean_repository
from ecomd.research.aemo_development_audit import file_sha256
from ecomd.research.aemo_semantic_crosswalk import (
    RESOLVED_STAGE,
    build_heldout_header_contract,
    inspect_crosswalk_archive,
    load_crosswalk,
    manifest_sha256,
    summarize_heldout_header_audit,
    utc_now,
    validate_crosswalk,
)

USER_AGENT = "EcoPhys-AEMO-semantic-validation/1.0"
TRANSPORT_RETRIES = 2
CHUNK_BYTES = 8 * 1024 * 1024


def _append_json_line(path: Path, payload: dict[str, object]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def _read_ledger(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    result: list[dict[str, object]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        payload: object = json.loads(line)
        if not isinstance(payload, dict):
            raise RuntimeError(f"download ledger line {line_number} is not an object")
        result.append(cast(dict[str, object], payload))
    return result


def _stream_download(
    session: requests.Session,
    *,
    url: str,
    partial_path: Path,
    resume: bool,
) -> tuple[int | None, str | None, int, dict[str, str]]:
    existing_bytes = partial_path.stat().st_size if partial_path.exists() else 0
    if existing_bytes and not resume:
        raise FileExistsError(f"partial archive exists; use --resume: {partial_path}")
    headers = {"Range": f"bytes={existing_bytes}-"} if existing_bytes else {}
    for attempt in range(1, TRANSPORT_RETRIES + 2):
        try:
            response = session.get(
                url,
                headers=headers,
                stream=True,
                timeout=(30.0, 180.0),
                allow_redirects=False,
            )
        except requests.RequestException as error:
            if attempt <= TRANSPORT_RETRIES:
                time.sleep(1.0)
                continue
            return None, f"{type(error).__name__}: {error}", attempt, {}
        response_headers = {
            key: value
            for key, value in response.headers.items()
            if key.lower() in {"content-length", "content-range", "etag", "last-modified"}
        }
        expected_status = 206 if existing_bytes else 200
        if response.status_code != expected_status:
            response.close()
            return response.status_code, None, attempt, response_headers
        mode = "ab" if existing_bytes else "xb"
        try:
            with partial_path.open(mode) as handle:
                for chunk in response.iter_content(chunk_size=CHUNK_BYTES):
                    if chunk:
                        handle.write(chunk)
                handle.flush()
                os.fsync(handle.fileno())
        except requests.RequestException as error:
            response.close()
            return None, f"{type(error).__name__}: {error}", attempt, response_headers
        response.close()
        return response.status_code, None, attempt, response_headers
    raise AssertionError("unreachable transport retry loop")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "data/manifests/aemo_semantic_crosswalk_v2_resolved.yaml",
    )
    parser.add_argument("--resume", action="store_true")
    arguments = parser.parse_args()
    commit = require_clean_repository(ROOT)
    manifest = load_crosswalk(arguments.manifest)
    errors = validate_crosswalk(manifest)
    if errors or manifest.get("stage") != RESOLVED_STAGE:
        raise RuntimeError("invalid resolved crosswalk: " + "; ".join(errors))
    resolution = cast(dict[str, object], manifest["resolution"])
    if resolution.get("all_head_requests_pass") is not True:
        raise RuntimeError("HEAD metadata gate did not pass")

    outputs = cast(dict[str, object], manifest["outputs"])
    raw_root = ROOT / cast(str, outputs["raw_root"])
    ledger_path = ROOT / cast(str, outputs["request_ledger"])
    header_path = ROOT / cast(str, outputs["header_contract"])
    summary_path = ROOT / cast(str, outputs["summary"])
    if header_path.exists() or summary_path.exists():
        raise FileExistsError("held-out header contract or summary already exists")
    archive_root = raw_root / "archives"
    archive_root.mkdir(parents=True, exist_ok=True)
    if ledger_path.exists() and not arguments.resume:
        raise FileExistsError(f"download ledger exists; use --resume: {ledger_path}")
    downloads = _read_ledger(ledger_path)
    objects = cast(list[dict[str, object]], manifest["objects"])
    completed_ids = [entry.get("object_id") for entry in downloads]
    expected_prefix = [item["object_id"] for item in objects[: len(downloads)]]
    if completed_ids != expected_prefix:
        raise RuntimeError("download ledger is not an exact prefix of the frozen object list")

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    for index, spec in enumerate(objects[len(downloads) :], start=len(downloads)):
        object_id = cast(str, spec["object_id"])
        expected_bytes = cast(int, spec["expected_bytes"])
        final_path = archive_root / f"{object_id}.zip"
        partial_path = archive_root / f"{object_id}.zip.part"
        if final_path.exists():
            if not arguments.resume:
                raise FileExistsError(f"archive exists without ledger entry: {final_path}")
            status: int | None = 200
            transport_error: str | None = None
            attempts = 0
            response_headers: dict[str, str] = {}
            recovered = True
        else:
            status, transport_error, attempts, response_headers = _stream_download(
                session,
                url=cast(str, spec["url"]),
                partial_path=partial_path,
                resume=arguments.resume,
            )
            recovered = False
            if status == 200 or (status == 206 and partial_path.exists()):
                partial_path.replace(final_path)
        observed_bytes = final_path.stat().st_size if final_path.exists() else 0
        sha256 = file_sha256(final_path) if final_path.exists() else None
        logical_http_status = 200 if final_path.exists() else status
        entry: dict[str, object] = {
            "request_index": index,
            "object_id": object_id,
            "sample_label": spec["sample_label"],
            "logical_role": spec["logical_role"],
            "url": spec["url"],
            "retrieved_at": utc_now(),
            "http_status": logical_http_status,
            "terminal_http_status": status,
            "transport_error": transport_error,
            "attempts": attempts,
            "response_headers": response_headers,
            "expected_bytes": expected_bytes,
            "observed_bytes": observed_bytes,
            "byte_match": observed_bytes == expected_bytes,
            "sha256": sha256,
            "recovered_after_interruption": recovered,
        }
        _append_json_line(ledger_path, entry)
        downloads.append(entry)
        print(
            json.dumps(
                {
                    "completed": len(downloads),
                    "total": len(objects),
                    "object_id": object_id,
                    "http_status": logical_http_status,
                    "observed_bytes": observed_bytes,
                    "expected_bytes": expected_bytes,
                    "byte_match": entry["byte_match"],
                },
                sort_keys=True,
            ),
            flush=True,
        )

    audits: list[dict[str, object]] = []
    for spec in objects:
        path = archive_root / f"{spec['object_id']}.zip"
        if path.exists():
            audit = inspect_crosswalk_archive(path, spec, manifest)
            audits.append(audit)
            print(
                json.dumps(
                    {
                        "header_audited": spec["object_id"],
                        "header_package": audit["header_package"],
                        "header_table": audit["header_table"],
                        "header_version": audit["header_version"],
                        "header_pass": audit["header_pass"],
                    },
                    sort_keys=True,
                ),
                flush=True,
            )

    source_hash = manifest_sha256(arguments.manifest)
    generated_at = utc_now()
    header_contract = build_heldout_header_contract(
        audits,
        source_manifest=arguments.manifest.relative_to(ROOT).as_posix(),
        source_manifest_sha256=source_hash,
        generated_at=generated_at,
        generator_git_commit=commit,
    )
    header_path.parent.mkdir(parents=True, exist_ok=True)
    header_path.write_text(
        yaml.safe_dump(header_contract, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    ledger_sha256 = file_sha256(ledger_path)
    summary = summarize_heldout_header_audit(
        downloads,
        audits,
        expected_count=len(objects),
        download_ledger_sha256=ledger_sha256,
    )
    summary["ownership"] = {
        "git_commit": commit,
        "resolved_manifest_sha256": source_hash,
        "generated_at": generated_at,
        "raw_root": raw_root.relative_to(ROOT).as_posix(),
        "raw_archive_bytes": sum(cast(int, item["observed_bytes"]) for item in downloads),
        "uncompressed_csv_bytes": sum(cast(int, audit["member_uncompressed_bytes"]) for audit in audits),
        "row_counts_opened": False,
        "row_filter_performed": False,
        "row_join_performed": False,
        "gpu_used": False,
    }
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
