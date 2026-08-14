#!/usr/bin/env python3
"""Collect the six frozen AEMO SQLLoader control files and audit metadata only."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import cast

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import requests

from ecomd.market_world.provenance import require_clean_repository
from ecomd.research.aemo_loader_controls import (
    audit_loader_control,
    load_loader_manifest,
    manifest_sha256,
    summarize_loader_audit,
    utc_now,
    validate_loader_manifest,
)

USER_AGENT = "EcoPhys-AEMO-loader-control-audit/1.0"
MAX_CONTROL_BYTES = 65_536


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "data/manifests/aemo_loader_control_audit_v3.yaml",
    )
    arguments = parser.parse_args()
    commit = require_clean_repository(ROOT)
    manifest = load_loader_manifest(arguments.manifest)
    errors = validate_loader_manifest(manifest)
    if errors:
        raise RuntimeError("invalid loader-control manifest: " + "; ".join(errors))
    outputs = cast(dict[str, object], manifest["outputs"])
    output_path = ROOT / cast(str, outputs["summary"])
    if output_path.exists():
        raise FileExistsError(output_path)

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    audits: list[dict[str, object]] = []
    for spec in cast(list[dict[str, object]], manifest["objects"]):
        content = b""
        status: int | None = None
        transport_error: str | None = None
        response_headers: dict[str, str] = {}
        try:
            response = session.get(
                cast(str, spec["url"]),
                stream=True,
                timeout=(30.0, 120.0),
                allow_redirects=False,
            )
            status = response.status_code
            response_headers = {
                key: value
                for key, value in response.headers.items()
                if key.lower() in {"content-length", "etag", "last-modified", "content-type"}
            }
            chunks: list[bytes] = []
            observed = 0
            for chunk in response.iter_content(chunk_size=8192):
                if not chunk:
                    continue
                observed += len(chunk)
                if observed > MAX_CONTROL_BYTES:
                    transport_error = "response exceeded 65536-byte metadata cap"
                    break
                chunks.append(chunk)
            content = b"".join(chunks)
            response.close()
        except requests.RequestException as error:
            transport_error = f"{type(error).__name__}: {error}"
        audit = audit_loader_control(
            spec,
            http_status=status,
            content=content,
            response_headers=response_headers,
            retrieved_at=utc_now(),
            transport_error=transport_error,
        )
        audits.append(audit)
        print(
            json.dumps(
                {
                    "object_id": audit["object_id"],
                    "http_status": audit["http_status"],
                    "parse_pass": audit["parse_pass"],
                    "contract_pass": audit["contract_pass"],
                },
                sort_keys=True,
            ),
            flush=True,
        )

    generated_at = utc_now()
    summary = summarize_loader_audit(
        audits,
        source_manifest=arguments.manifest.relative_to(ROOT).as_posix(),
        source_manifest_sha256=manifest_sha256(arguments.manifest),
        collector_git_commit=commit,
        generated_at=generated_at,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
