#!/usr/bin/env python3
"""Analyze two retained AEMO NEMDE members under frozen XML gates."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import cast

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ecomd.research.aemo_nemde_xml_conformance import (
    SOURCE_MANIFEST_PATH,
    load_json,
    load_manifest,
    manifest_sha256,
    parse_member_range,
    summarize_conformance,
    utc_now,
    validate_download_receipt,
    validate_manifest,
    validate_retention_receipt,
    verify_local_ranges,
)


def _tracked_clean_commit() -> str:
    for arguments in (["git", "diff", "--quiet"], ["git", "diff", "--cached", "--quiet"]):
        if subprocess.run(arguments, cwd=ROOT, check=False).returncode != 0:
            raise RuntimeError("tracked files changed after the frozen protocol commit")
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=ROOT / SOURCE_MANIFEST_PATH)
    arguments = parser.parse_args()
    commit = _tracked_clean_commit()
    manifest = load_manifest(arguments.manifest)
    errors = validate_manifest(manifest)
    if errors:
        raise RuntimeError("invalid NEMDE-XML manifest: " + "; ".join(errors))
    outputs = cast(dict[str, object], manifest["outputs"])
    raw_root = ROOT / cast(str, outputs["raw_root"])
    summary_path = ROOT / cast(str, outputs["summary"])
    if summary_path.exists():
        raise FileExistsError(summary_path)
    download = load_json(ROOT / cast(str, outputs["download_receipt"]))
    retention = load_json(ROOT / cast(str, outputs["retention_receipt"]))
    receipt_errors = [
        *validate_download_receipt(download, manifest),
        *validate_retention_receipt(retention, download, manifest),
        *verify_local_ranges(raw_root, download, manifest),
    ]
    if receipt_errors:
        raise RuntimeError("invalid retained NEMDE ranges: " + "; ".join(receipt_errors))
    if download["protocol_git_commit"] != commit or retention["protocol_git_commit"] != commit:
        raise RuntimeError("retained ranges were not produced by the current frozen commit")
    source_sha = manifest_sha256(arguments.manifest)
    if download["source_manifest_sha256"] != source_sha:
        raise RuntimeError("frozen manifest bytes changed")

    parsed: list[dict[str, object]] = []
    for spec in cast(list[dict[str, object]], manifest["objects"]):
        result = parse_member_range(raw_root / cast(str, spec["expected_filename"]), spec)
        parsed.append(result)
        print(
            json.dumps(
                {
                    "object_id": spec["object_id"],
                    "local_header_pass": result["local_header_pass"],
                    "crc_pass": result["crc_pass"],
                    "xml_parse_pass": result["xml_parse_pass"],
                    "section_contract_pass": result["section_contract_pass"],
                },
                sort_keys=True,
            ),
            flush=True,
        )
    summary = summarize_conformance(
        parsed,
        retention,
        manifest,
        source_manifest_sha256=source_sha,
        analyzer_git_commit=commit,
        generated_at=utc_now(),
    )
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
