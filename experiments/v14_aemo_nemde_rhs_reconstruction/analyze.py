#!/usr/bin/env python3
"""Analyze input-side NEMDE dynamic-RHS reconstruction under frozen gates."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
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
    load_json,
    load_manifest,
    manifest_sha256,
    score_case,
    seal_reference_and_make_sentinels,
    summarize_reconstruction,
    utc_now,
    validate_manifest,
    validate_materialization_receipt,
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


def _parse_xml(xml_bytes: bytes) -> dict[str, Any]:
    import xmltodict

    parsed: object = xmltodict.parse(xml_bytes, disable_entities=True)
    if not isinstance(parsed, dict):
        raise TypeError("parsed NEMDE XML root is not a mapping")
    return cast(dict[str, Any], parsed)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=ROOT / SOURCE_MANIFEST_PATH)
    parser.add_argument("--nempy-root", type=Path, required=True)
    arguments = parser.parse_args()
    commit = _tracked_clean_commit()
    manifest = load_manifest(arguments.manifest)
    manifest_errors = validate_manifest(manifest)
    if manifest_errors:
        raise RuntimeError("invalid NEMDE-RHS manifest: " + "; ".join(manifest_errors))
    outputs = cast(dict[str, object], manifest["outputs"])
    raw_root = ROOT / cast(str, outputs["raw_root"])
    receipt_path = ROOT / cast(str, outputs["materialization_receipt"])
    summary_path = ROOT / cast(str, outputs["summary"])
    if summary_path.exists():
        raise FileExistsError(summary_path)
    receipt = load_json(receipt_path)
    receipt_errors = [
        *validate_materialization_receipt(receipt, manifest),
        *verify_local_ranges(raw_root, receipt, manifest),
    ]
    if receipt_errors:
        raise RuntimeError("invalid R2 materialization: " + "; ".join(receipt_errors))
    source_sha = manifest_sha256(arguments.manifest)
    if receipt["protocol_git_commit"] != commit or receipt["source_manifest_sha256"] != source_sha:
        raise RuntimeError("materialization was not produced by this frozen commit and manifest")

    engine_audit = audit_engine_checkout(arguments.nempy_root)
    if engine_audit["pass"] is not True:
        raise RuntimeError("pinned Nempy checkout failed provenance audit")
    sys.path.insert(0, str(arguments.nempy_root / "src"))
    from nempy.historical_inputs.rhs_calculator import RHSCalc
    from nempy.historical_inputs.xml_cache import XMLCacheManager

    cases: list[dict[str, object]] = []
    for spec in cast(list[dict[str, object]], manifest["objects"]):
        xml_bytes = extract_member_xml(raw_root / cast(str, spec["expected_filename"]), spec)
        document = _parse_xml(xml_bytes)
        references, sentinel_a, sentinel_b, replacement_count = seal_reference_and_make_sentinels(document)
        results_a = evaluate_rhs_document(sentinel_a, XMLCacheManager, RHSCalc)
        results_b = evaluate_rhs_document(sentinel_b, XMLCacheManager, RHSCalc)
        case = score_case(spec, references, results_a, results_b, replacement_count)
        cases.append(case)
        print(
            json.dumps(
                {
                    "object_id": spec["object_id"],
                    "dynamic_equation_count": case["dynamic_equation_count"],
                    "evaluation_coverage": case["evaluation_coverage"],
                    "sentinel_outcome_match_rate": case["sentinel_outcome_match_rate"],
                    "pass": case["pass"],
                },
                sort_keys=True,
            ),
            flush=True,
        )
    summary = summarize_reconstruction(
        cases,
        receipt,
        engine_audit,
        source_manifest_sha256=source_sha,
        analyzer_git_commit=commit,
        generated_at=utc_now(),
    )
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
