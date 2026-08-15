#!/usr/bin/env python3
"""Run the fixed post-hoc NEMDE RHS tail diagnostic on consumed cases."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ecomd.research.aemo_nemde_rhs_reconstruction import (
    SOURCE_MANIFEST_PATH,
    audit_engine_checkout,
    extract_member_xml,
    load_json,
    load_manifest,
    manifest_sha256,
    seal_reference_and_make_sentinels,
    utc_now,
    validate_manifest,
    validate_materialization_receipt,
    verify_local_ranges,
)
from ecomd.research.aemo_nemde_rhs_tail_diagnostic import diagnose_case

EXPECTED_RESULT_SUMMARY_SHA = "704b20a54e8232eda57ebdc4525182c8586b104f400dbdddb0a9aa29c6e57119"
OUTPUT_PATH = "experiments/v14_aemo_nemde_rhs_reconstruction/artifacts/tail_diagnostic.json"


def _tracked_clean_commit() -> str:
    for arguments in (["git", "diff", "--quiet"], ["git", "diff", "--cached", "--quiet"]):
        if subprocess.run(arguments, cwd=ROOT, check=False).returncode != 0:
            raise RuntimeError("tracked files changed after the diagnostic-plan commit")
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def _parse_xml(xml_bytes: bytes) -> dict[str, Any]:
    import xmltodict

    parsed: object = xmltodict.parse(xml_bytes, disable_entities=True)
    if not isinstance(parsed, dict):
        raise TypeError("parsed NEMDE XML root is not a mapping")
    return cast(dict[str, Any], parsed)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=ROOT / SOURCE_MANIFEST_PATH)
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--nempy-root", type=Path, required=True)
    arguments = parser.parse_args()
    commit = _tracked_clean_commit()
    manifest = load_manifest(arguments.manifest)
    errors = validate_manifest(manifest)
    if errors:
        raise RuntimeError("invalid NEMDE-RHS manifest: " + "; ".join(errors))
    outputs = cast(dict[str, object], manifest["outputs"])
    receipt = load_json(ROOT / cast(str, outputs["materialization_receipt"]))
    receipt_errors = [
        *validate_materialization_receipt(receipt, manifest),
        *verify_local_ranges(arguments.raw_root, receipt, manifest),
    ]
    if receipt_errors:
        raise RuntimeError("invalid diagnostic raw inputs: " + "; ".join(receipt_errors))
    result_summary_path = ROOT / cast(str, outputs["summary"])
    if hashlib.sha256(result_summary_path.read_bytes()).hexdigest() != EXPECTED_RESULT_SUMMARY_SHA:
        raise RuntimeError("committed RHS result summary changed")
    result_summary = load_json(result_summary_path)
    if result_summary.get("decision") != "PARTIAL_INPUT_SIDE_DYNAMIC_RHS_RECONSTRUCTION":
        raise RuntimeError("diagnostic parent decision changed")
    engine_audit = audit_engine_checkout(arguments.nempy_root)
    if engine_audit["pass"] is not True:
        raise RuntimeError("pinned Nempy checkout failed provenance audit")

    sys.path.insert(0, str(arguments.nempy_root / "src"))
    from nempy.historical_inputs.rhs_calculator import RHSCalc
    from nempy.historical_inputs.xml_cache import XMLCacheManager

    cases: list[dict[str, object]] = []
    for spec in cast(list[dict[str, object]], manifest["objects"]):
        xml_bytes = extract_member_xml(arguments.raw_root / cast(str, spec["expected_filename"]), spec)
        document = _parse_xml(xml_bytes)
        references, sentinel_document, _unused, _count = seal_reference_and_make_sentinels(document)
        diagnostic = diagnose_case(sentinel_document, references, XMLCacheManager, RHSCalc)
        cases.append(
            {
                "object_id": spec["object_id"],
                "market_date": spec["market_date"],
                "mechanism_phase": spec["mechanism_phase"],
                **diagnostic,
            }
        )
        print(
            json.dumps(
                {
                    "object_id": spec["object_id"],
                    "successful": diagnostic["successful_scored_equation_count"],
                    "failed": diagnostic["failed_equation_count"],
                },
                sort_keys=True,
            ),
            flush=True,
        )
    payload: dict[str, object] = {
        "schema_version": "ecophys-aemo-nemde-rhs-tail-diagnostic/v1",
        "generated_at": utc_now(),
        "diagnostic_git_commit": commit,
        "source_manifest": SOURCE_MANIFEST_PATH,
        "source_manifest_sha256": manifest_sha256(arguments.manifest),
        "parent_result_decision": "PARTIAL_INPUT_SIDE_DYNAMIC_RHS_RECONSTRUCTION",
        "parent_result_summary_sha256": EXPECTED_RESULT_SUMMARY_SHA,
        "post_hoc_descriptive_only": True,
        "original_decision_changed": False,
        "engine": engine_audit,
        "cases": cases,
        "claim_boundary": {
            "repair_validated": False,
            "threshold_changed": False,
            "equations_excluded": False,
            "one_day_or_full_solver_unlocked": False,
            "gpu_or_model_work_unlocked": False,
        },
        "resources": {
            "new_aemo_requests": 0,
            "new_r2_reads": 0,
            "reused_local_raw_bytes": 2_097_152,
            "gpu_hours": 0,
            "paid_data_spend": 0,
        },
    }
    output_path = ROOT / OUTPUT_PATH
    if output_path.exists():
        raise FileExistsError(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
