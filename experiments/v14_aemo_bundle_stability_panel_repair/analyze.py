#!/usr/bin/env python3
"""Run the unchanged panel science contract after the frozen plumbing repair."""

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
    build_day_manifest,
    build_day_receipts,
    load_download_receipt,
    load_panel_manifest,
    load_retention_receipt,
    summarize_panel,
    validate_download_receipt,
    validate_panel_manifest,
    validate_retention_receipt,
)
from ecomd.research.aemo_bundle_stability_panel import (
    SOURCE_MANIFEST_PATH as ORIGINAL_MANIFEST_PATH,
)
from ecomd.research.aemo_bundle_stability_panel import (
    manifest_sha256 as original_manifest_sha256,
)
from ecomd.research.aemo_bundle_stability_repair import (
    ORIGINAL_DOWNLOAD_PATH,
    ORIGINAL_RETENTION_PATH,
    SOURCE_MANIFEST_PATH,
    load_materialization_receipt,
    load_repair_manifest,
    manifest_sha256,
    utc_now,
    validate_materialization_receipt,
    validate_original_provenance,
    validate_repair_manifest,
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
            raise RuntimeError("tracked files changed after the frozen repair commit")
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
    repair_manifest = load_repair_manifest(arguments.manifest)
    repair_manifest_sha = manifest_sha256(arguments.manifest)
    repair_errors = validate_repair_manifest(repair_manifest, source_sha256=repair_manifest_sha)
    provenance_errors = validate_original_provenance(ROOT)
    if repair_errors or provenance_errors:
        raise RuntimeError("invalid frozen repair: " + "; ".join([*repair_errors, *provenance_errors]))
    repair_outputs = cast(dict[str, object], repair_manifest["outputs"])
    raw_root = ROOT / cast(str, repair_outputs["raw_root"])
    receipt_path = ROOT / cast(str, repair_outputs["materialization_receipt"])
    summary_path = ROOT / cast(str, repair_outputs["summary"])
    if summary_path.exists():
        raise FileExistsError(summary_path)
    materialization = load_materialization_receipt(receipt_path)
    receipt_errors = validate_materialization_receipt(materialization, repair_manifest)
    if receipt_errors:
        raise RuntimeError("invalid repair materialization: " + "; ".join(receipt_errors))
    if materialization["protocol_git_commit"] != commit:
        raise RuntimeError("materialization was not produced by current repair commit")
    local_errors = verify_local_materializations(raw_root, materialization, repair_manifest)
    if local_errors:
        raise RuntimeError("local repair inputs changed: " + "; ".join(local_errors))

    original_manifest_path = ROOT / ORIGINAL_MANIFEST_PATH
    panel_manifest = load_panel_manifest(original_manifest_path)
    panel_manifest_sha = original_manifest_sha256(original_manifest_path)
    panel_errors = validate_panel_manifest(panel_manifest, source_sha256=panel_manifest_sha)
    if panel_errors:
        raise RuntimeError("original panel manifest changed: " + "; ".join(panel_errors))
    original_download = load_download_receipt(ROOT / ORIGINAL_DOWNLOAD_PATH)
    original_retention = load_retention_receipt(ROOT / ORIGINAL_RETENTION_PATH)
    original_download_errors = validate_download_receipt(original_download, panel_manifest)
    original_retention_errors = validate_retention_receipt(
        original_retention, original_download, panel_manifest
    )
    if original_download_errors or original_retention_errors:
        raise RuntimeError(
            "original receipt chain changed: "
            + "; ".join([*original_download_errors, *original_retention_errors])
        )

    day_summaries: list[dict[str, object]] = []
    for raw_day in cast(list[dict[str, object]], panel_manifest["days"]):
        day_manifest = build_day_manifest(panel_manifest, raw_day)
        day_resources = cast(dict[str, object], day_manifest["resource_contract"])
        if day_resources != {"maximum_total_data_rows": 4_000_000}:
            raise RuntimeError("repaired day resource contract differs from frozen cap")
        tables, observations = parse_conformance_archives(raw_root, day_manifest)
        day_download, day_retention = build_day_receipts(
            panel_manifest,
            raw_day,
            original_download,
            original_retention,
        )
        day_summary = summarize_bundle_confirmation(
            tables,
            observations,
            day_manifest,
            day_download,
            day_retention,
            source_manifest_sha256=repair_manifest_sha,
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
        panel_manifest,
        original_download,
        original_retention,
        source_manifest_sha256=repair_manifest_sha,
        analyzer_git_commit=commit,
        generated_at=utc_now(),
        source_manifest_path=SOURCE_MANIFEST_PATH,
    )
    summary["repair_provenance"] = {
        "failed_protocol_decision": "FAIL_PANEL_IMPLEMENTATION_PRE_PARSE",
        "failed_protocol_commit": "1f44811e75a455f161532fbfdd3bde2092508bf5",
        "repair_scope": "add_missing_day_resource_contract_only",
        "aemo_source_request_count": 0,
        "dates_or_scientific_gates_changed": False,
    }
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
