#!/usr/bin/env python3
"""Evaluate the four frozen panel days sequentially after R2 verification."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import gc
import json
import subprocess
import sys
from pathlib import Path
from typing import cast

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ecomd.research.aemo_bundle_confirmation import summarize_bundle_confirmation
from ecomd.research.aemo_bundle_stability_panel import (
    DAY_SUMMARY_SCHEMA_VERSION,
    SOURCE_MANIFEST_PATH,
    build_day_manifest,
    build_day_receipts,
    load_download_receipt,
    load_panel_manifest,
    load_retention_receipt,
    manifest_sha256,
    summarize_panel,
    utc_now,
    validate_download_receipt,
    validate_panel_manifest,
    validate_retention_receipt,
    verify_local_materializations,
)
from ecomd.research.aemo_row_conformance import parse_conformance_archives


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / SOURCE_MANIFEST_PATH,
    )
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
    summary_path = ROOT / cast(str, outputs["summary"])
    if summary_path.exists():
        raise FileExistsError(summary_path)

    download = load_download_receipt(download_path)
    download_errors = validate_download_receipt(download, manifest)
    if download_errors:
        raise RuntimeError("invalid panel download receipt: " + "; ".join(download_errors))
    retention = load_retention_receipt(retention_path)
    retention_errors = validate_retention_receipt(retention, download, manifest)
    if retention_errors:
        raise RuntimeError("invalid panel retention receipt: " + "; ".join(retention_errors))
    if download["protocol_git_commit"] != commit:
        raise RuntimeError("download was not produced by the current frozen commit")
    local_errors = verify_local_materializations(raw_root, retention, manifest)
    if local_errors:
        raise RuntimeError("local panel inputs changed: " + "; ".join(local_errors))

    day_summaries: list[dict[str, object]] = []
    for raw_day in cast(list[dict[str, object]], manifest["days"]):
        day_manifest = build_day_manifest(manifest, raw_day)
        tables, observations = parse_conformance_archives(raw_root, day_manifest)
        day_download, day_retention = build_day_receipts(
            manifest,
            raw_day,
            download,
            retention,
        )
        day_summary = summarize_bundle_confirmation(
            tables,
            observations,
            day_manifest,
            day_download,
            day_retention,
            source_manifest_sha256=current_manifest_sha,
            analyzer_git_commit=commit,
            generated_at=utc_now(),
            summary_schema_version=DAY_SUMMARY_SCHEMA_VERSION,
            source_manifest_path=SOURCE_MANIFEST_PATH,
        )
        day_summary["decision"] = (
            "PASS_PANEL_DAY_BUNDLE_RELATION"
            if day_summary["pass"] is True
            else "FAIL_PANEL_DAY_BUNDLE_RELATION"
        )
        day_summaries.append(day_summary)
        relation = cast(dict[str, object], day_summary["relation"])
        print(
            json.dumps(
                {
                    "market_date": day_summary["sample_date"],
                    "pass": day_summary["pass"],
                    "tracker_count": relation["tracker_count"],
                    "pair_count": relation["pair_count"],
                },
                sort_keys=True,
            ),
            flush=True,
        )
        del tables
        gc.collect()

    summary = summarize_panel(
        day_summaries,
        manifest,
        download,
        retention,
        source_manifest_sha256=current_manifest_sha,
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
