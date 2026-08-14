#!/usr/bin/env python3
"""Collect frozen AEMO ZIP prefixes under the channel-scoped source contract."""

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
from ecomd.research.aemo_source_contract import (
    RANGE_BYTES,
    audit_source_contract_response,
    load_source_contract_manifest,
    manifest_sha256,
    summarize_source_contract_audit,
    utc_now,
    validate_source_contract_manifest,
)

USER_AGENT = "EcoPhys-AEMO-source-contract-audit/1.0"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "data/manifests/aemo_source_contract_v1.yaml",
    )
    arguments = parser.parse_args()
    commit = require_clean_repository(ROOT)
    manifest = load_source_contract_manifest(arguments.manifest)
    errors = validate_source_contract_manifest(manifest)
    if errors:
        raise RuntimeError("invalid AEMO source contract: " + "; ".join(errors))
    outputs = cast(dict[str, object], manifest["outputs"])
    output_path = ROOT / cast(str, outputs["summary"])
    if output_path.exists():
        raise FileExistsError(output_path)

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    audits: list[dict[str, object]] = []
    range_value = f"bytes=0-{RANGE_BYTES - 1}"
    for spec in cast(list[dict[str, object]], manifest["objects"]):
        status: int | None = None
        content = b""
        transport_error: str | None = None
        response_headers: dict[str, str] = {}
        try:
            response = session.get(
                cast(str, spec["url"]),
                headers={"Range": range_value},
                stream=True,
                timeout=(30.0, 120.0),
                allow_redirects=False,
            )
            status = response.status_code
            response_headers = {
                key: value
                for key, value in response.headers.items()
                if key.lower()
                in {
                    "content-length",
                    "content-range",
                    "etag",
                    "last-modified",
                    "content-type",
                }
            }
            if status == 206:
                response.raw.decode_content = False
                content = response.raw.read(RANGE_BYTES + 1)
                if len(content) > RANGE_BYTES:
                    transport_error = f"response exceeded frozen {RANGE_BYTES}-byte cap"
            response.close()
        except requests.RequestException as error:
            transport_error = f"{type(error).__name__}: {error}"
        audit = audit_source_contract_response(
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
                    "zip_prefix_parse": audit["zip_prefix_parse"],
                    "source_contract_pass": audit["source_contract_pass"],
                },
                sort_keys=True,
            ),
            flush=True,
        )

    summary = summarize_source_contract_audit(
        audits,
        source_manifest=arguments.manifest.relative_to(ROOT).as_posix(),
        source_manifest_sha256=manifest_sha256(arguments.manifest),
        collector_git_commit=commit,
        generated_at=utc_now(),
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
