#!/usr/bin/env python3
"""Run the explicitly post-hoc AEMO direction-bundle diagnostic."""

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

from ecomd.research.aemo_direction_bundles import (
    FROZEN_ROW_SUMMARY_SHA256,
    summarize_direction_bundles,
)
from ecomd.research.aemo_row_conformance import (
    SOURCE_MANIFEST_PATH,
    file_sha256,
    load_download_receipt,
    load_retention_receipt,
    load_row_conformance_manifest,
    parse_conformance_archives,
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
            raise RuntimeError("tracked files changed after the diagnostic code commit")
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "experiments/v14_aemo_direction_bundle_diagnostic/artifacts/summary.json",
    )
    arguments = parser.parse_args()
    if arguments.output.exists():
        raise FileExistsError(arguments.output)
    commit = _tracked_clean_commit()

    manifest_path = ROOT / SOURCE_MANIFEST_PATH
    manifest = load_row_conformance_manifest(manifest_path)
    manifest_errors = validate_row_conformance_manifest(manifest)
    if manifest_errors:
        raise RuntimeError("invalid row manifest: " + "; ".join(manifest_errors))
    prior_root = ROOT / "experiments/v14_aemo_row_conformance/artifacts"
    download = load_download_receipt(prior_root / "download_receipt.json")
    retention = load_retention_receipt(prior_root / "retention_receipt.json")
    download_errors = validate_download_receipt(download, manifest)
    retention_errors = validate_retention_receipt(retention, download, manifest)
    local_errors = verify_local_downloads(arguments.raw_root, download, manifest)
    errors = (*download_errors, *retention_errors, *local_errors)
    if errors:
        raise RuntimeError("invalid retained inputs: " + "; ".join(errors))

    frozen_summary_path = prior_root / "summary.json"
    frozen_summary_sha256 = file_sha256(frozen_summary_path)
    if frozen_summary_sha256 != FROZEN_ROW_SUMMARY_SHA256:
        raise RuntimeError("frozen E1a summary hash changed")
    frozen_payload: object = json.loads(frozen_summary_path.read_text(encoding="utf-8"))
    if not isinstance(frozen_payload, dict):
        raise ValueError("frozen E1a summary root must be a mapping")
    frozen_summary = cast(dict[str, object], frozen_payload)

    tables, observations = parse_conformance_archives(arguments.raw_root, manifest)
    if not observations or any(item.get("pass") is not True for item in observations):
        raise RuntimeError("retained archives no longer pass their frozen parse contracts")
    summary = summarize_direction_bundles(
        tables,
        frozen_summary,
        analyzer_git_commit=commit,
        generated_at=utc_now(),
        frozen_summary_sha256=frozen_summary_sha256,
    )
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
