#!/usr/bin/env python3
"""Compare the frozen structural RPN repair on consumed development cases."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import copy
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
    evaluate_rhs_document,
    extract_member_xml,
    file_sha256,
    load_json,
    load_manifest,
    score_case,
    seal_reference_and_make_sentinels,
    utc_now,
    validate_manifest,
)
from ecomd.research.aemo_nemde_rpn_group_repair import (
    compare_repair_arms,
    install_rpn_group_repair,
)

EXPECTED_PARENT_SUMMARY_SHA = "704b20a54e8232eda57ebdc4525182c8586b104f400dbdddb0a9aa29c6e57119"
EXPECTED_DIAGNOSTIC_SHA = "5c51257ed48c54b4b2164c83729332dd1288438444c1e35fd14dc7022fe80348"
OUTPUT_PATH = "experiments/v14_aemo_nemde_rpn_repair_development/artifacts/development_comparison.json"


def _tracked_clean_commit() -> str:
    for arguments in (["git", "diff", "--quiet"], ["git", "diff", "--cached", "--quiet"]):
        if subprocess.run(arguments, cwd=ROOT, check=False).returncode != 0:
            raise RuntimeError("tracked files changed after the development-plan commit")
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


def _baseline_matches_parent(case: dict[str, object], parent: dict[str, object]) -> bool:
    keys = (
        "dynamic_equation_count",
        "production_reference_count",
        "scored_count",
        "reference_coverage",
        "evaluation_coverage",
        "sentinel_outcome_match_rate",
        "sentinel_success_value_match_rate",
        "failed_constraint_ids",
        "errors",
    )
    return all(case.get(key) == parent.get(key) for key in keys)


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
        raise RuntimeError("invalid parent manifest: " + "; ".join(errors))
    outputs = cast(dict[str, object], manifest["outputs"])
    parent_path = ROOT / cast(str, outputs["summary"])
    diagnostic_path = ROOT / "experiments/v14_aemo_nemde_rhs_reconstruction/artifacts/tail_diagnostic.json"
    if hashlib.sha256(parent_path.read_bytes()).hexdigest() != EXPECTED_PARENT_SUMMARY_SHA:
        raise RuntimeError("parent RHS summary changed")
    if hashlib.sha256(diagnostic_path.read_bytes()).hexdigest() != EXPECTED_DIAGNOSTIC_SHA:
        raise RuntimeError("parent tail diagnostic changed")
    parent_summary = load_json(parent_path)
    if parent_summary.get("decision") != "PARTIAL_INPUT_SIDE_DYNAMIC_RHS_RECONSTRUCTION":
        raise RuntimeError("parent RHS decision changed")
    parent_cases = {
        str(item["object_id"]): item for item in cast(list[dict[str, object]], parent_summary["cases"])
    }
    engine_audit = audit_engine_checkout(arguments.nempy_root)
    if engine_audit["pass"] is not True:
        raise RuntimeError("pinned Nempy checkout failed provenance audit")

    sys.path.insert(0, str(arguments.nempy_root / "src"))
    import nempy.historical_inputs.rhs_calculator as rhs_module
    from nempy.historical_inputs.xml_cache import XMLCacheManager

    documents: list[tuple[dict[str, object], dict[str, float], dict[str, Any], dict[str, Any], int]] = []
    baseline_results: dict[str, tuple[list[dict[str, object]], list[dict[str, object]]]] = {}
    for spec in cast(list[dict[str, object]], manifest["objects"]):
        raw_path = arguments.raw_root / cast(str, spec["expected_filename"])
        if file_sha256(raw_path) != spec["range_sha256"]:
            raise RuntimeError(f"raw range hash changed for {spec['object_id']}")
        xml = extract_member_xml(raw_path, spec)
        document = _parse_xml(xml)
        references, sentinel_a, sentinel_b, replacement_count = seal_reference_and_make_sentinels(document)
        documents.append((spec, references, sentinel_a, sentinel_b, replacement_count))
        baseline_results[cast(str, spec["object_id"])] = (
            evaluate_rhs_document(copy.deepcopy(sentinel_a), XMLCacheManager, rhs_module.RHSCalc),
            evaluate_rhs_document(copy.deepcopy(sentinel_b), XMLCacheManager, rhs_module.RHSCalc),
        )

    repair = install_rpn_group_repair(rhs_module)
    cases: list[dict[str, object]] = []
    for spec, references, sentinel_a, sentinel_b, replacement_count in documents:
        object_id = cast(str, spec["object_id"])
        baseline_a, baseline_b = baseline_results[object_id]
        repaired_a = evaluate_rhs_document(copy.deepcopy(sentinel_a), XMLCacheManager, rhs_module.RHSCalc)
        repaired_b = evaluate_rhs_document(copy.deepcopy(sentinel_b), XMLCacheManager, rhs_module.RHSCalc)
        baseline_case = score_case(spec, references, baseline_a, baseline_b, replacement_count)
        repaired_case = score_case(spec, references, repaired_a, repaired_b, replacement_count)
        baseline_reproduced = _baseline_matches_parent(baseline_case, parent_cases[object_id])
        if not baseline_reproduced:
            raise RuntimeError(f"baseline did not reproduce parent summary for {object_id}")
        cases.append(
            {
                "object_id": object_id,
                "market_date": spec["market_date"],
                "mechanism_phase": spec["mechanism_phase"],
                "baseline_reproduced_parent": baseline_reproduced,
                "baseline": baseline_case,
                "rpn_tree": repaired_case,
                "paired_change": compare_repair_arms(references, baseline_a, repaired_a),
            }
        )
        print(
            json.dumps(
                {
                    "object_id": object_id,
                    "baseline_scored": baseline_case["scored_count"],
                    "rpn_tree_scored": repaired_case["scored_count"],
                    "baseline_p95": cast(dict[str, object], baseline_case["errors"])["normalized_p95"],
                    "rpn_tree_p95": cast(dict[str, object], repaired_case["errors"])["normalized_p95"],
                },
                sort_keys=True,
            ),
            flush=True,
        )

    payload: dict[str, object] = {
        "schema_version": "ecophys-aemo-nemde-rpn-repair-development/v1",
        "generated_at": utc_now(),
        "development_git_commit": commit,
        "development_only": True,
        "claim_or_pass_fail_decision": None,
        "parent_decision_changed": False,
        "parent_summary_sha256": EXPECTED_PARENT_SUMMARY_SHA,
        "parent_diagnostic_sha256": EXPECTED_DIAGNOSTIC_SHA,
        "engine": engine_audit,
        "repair": {
            "name": "term_id_group_term_tree_adapter",
            "input_scada_or_default_logic_changed": False,
            "nempy_checkout_modified": False,
            "stats": repair.stats.as_dict(),
        },
        "cases": cases,
        "claim_boundary": {
            "repair_validated": False,
            "fresh_interval_used": False,
            "full_input_only_replay_validated": False,
            "full_day_or_solver_unlocked": False,
            "causal_or_model_claim_allowed": False,
            "gpu_or_experiment_156_unlocked": False,
        },
        "resources": {
            "new_aemo_requests": 0,
            "new_r2_reads": 0,
            "reused_local_raw_bytes": 2_097_152,
            "gpu_hours": 0,
            "paid_data_spend": 0,
            "mathematical_solver_used": False,
        },
    }
    output = ROOT / OUTPUT_PATH
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
