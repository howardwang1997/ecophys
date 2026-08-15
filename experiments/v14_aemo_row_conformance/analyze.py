#!/usr/bin/env python3
"""Analyze retained AEMO inputs only after all provenance gates pass."""

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

from ecomd.research.aemo_row_conformance import (
    SOURCE_MANIFEST_PATH,
    load_download_receipt,
    load_retention_receipt,
    load_row_conformance_manifest,
    manifest_sha256,
    parse_conformance_archives,
    summarize_row_conformance,
    utc_now,
    validate_download_receipt,
    validate_retention_receipt,
    validate_row_conformance_manifest,
    verify_local_downloads,
)


def _tracked_clean_commit() -> str:
    for arguments in (["git", "diff", "--quiet"], ["git", "diff", "--cached", "--quiet"]):
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / SOURCE_MANIFEST_PATH,
    )
    arguments = parser.parse_args()
    commit = _tracked_clean_commit()
    manifest = load_row_conformance_manifest(arguments.manifest)
    manifest_errors = validate_row_conformance_manifest(manifest)
    if manifest_errors:
        raise RuntimeError("invalid AEMO row-conformance manifest: " + "; ".join(manifest_errors))
    outputs = cast(dict[str, object], manifest["outputs"])
    raw_root = ROOT / cast(str, outputs["raw_root"])
    download_path = ROOT / cast(str, outputs["download_receipt"])
    retention_path = ROOT / cast(str, outputs["retention_receipt"])
    summary_path = ROOT / cast(str, outputs["summary"])
    if summary_path.exists():
        raise FileExistsError(summary_path)

    download = load_download_receipt(download_path)
    download_errors = validate_download_receipt(download, manifest)
    if download_errors:
        raise RuntimeError("invalid AEMO download receipt: " + "; ".join(download_errors))
    retention = load_retention_receipt(retention_path)
    retention_errors = validate_retention_receipt(retention, download, manifest)
    if retention_errors:
        raise RuntimeError("invalid AEMO retention receipt: " + "; ".join(retention_errors))
    current_manifest_sha256 = manifest_sha256(arguments.manifest)
    if download["protocol_git_commit"] != commit:
        raise RuntimeError("download was not produced by the current frozen commit")
    if download["source_manifest_sha256"] != current_manifest_sha256:
        raise RuntimeError("download manifest hash differs from current exact bytes")
    local_errors = verify_local_downloads(raw_root, download, manifest)
    if local_errors:
        raise RuntimeError("local AEMO inputs changed: " + "; ".join(local_errors))

    tables, observations = parse_conformance_archives(raw_root, manifest)
    summary = summarize_row_conformance(
        tables,
        observations,
        manifest,
        download,
        retention,
        source_manifest_sha256=current_manifest_sha256,
        analyzer_git_commit=commit,
        generated_at=utc_now(),
    )
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
