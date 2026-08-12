#!/usr/bin/env python3
"""Run the frozen Experiment 142 admission-contract fixtures."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
from typing import cast

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ecomd.invariant_calibration.g0_contract import (
    AdmissionStatus,
    assess_candidate,
    candidate_from_dict,
)

SUITE_SCHEMA = "exp142-g0-contract-fixtures/v1"
RESULT_SCHEMA = "exp142-g0-contract-result/v1"


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _require_clean_repository() -> None:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    if result.stdout.strip():
        raise RuntimeError("Experiment 142 requires a clean committed checkout")


def _reverse_collections(value: object) -> object:
    if isinstance(value, dict):
        mapping = cast(dict[object, object], value)
        return {
            key: _reverse_collections(item)
            for key, item in reversed(tuple(mapping.items()))
        }
    if isinstance(value, list):
        return [_reverse_collections(item) for item in reversed(value)]
    return value


def _apply_mutations(base: object, mutations: object) -> object:
    if not isinstance(base, dict) or not isinstance(mutations, dict):
        raise ValueError("base_candidate and mutations must be mappings")
    payload = deepcopy(cast(dict[str, object], base))
    for dotted_path, value in cast(dict[object, object], mutations).items():
        if not isinstance(dotted_path, str) or not dotted_path:
            raise ValueError("mutation paths must be non-empty strings")
        parts = dotted_path.split(".")
        cursor = payload
        for part in parts[:-1]:
            child = cursor.get(part)
            if not isinstance(child, dict):
                raise ValueError(f"mutation parent {part!r} is not a mapping")
            cursor = cast(dict[str, object], child)
        cursor[parts[-1]] = deepcopy(value)
    return payload


def run_suite(path: Path) -> dict[str, object]:
    """Evaluate every frozen case and return a deterministic result bundle."""
    suite_object = yaml.safe_load(path.read_text())
    if not isinstance(suite_object, dict):
        raise ValueError("fixture suite must be a mapping")
    suite = cast(dict[str, object], suite_object)
    if suite.get("schema") != SUITE_SCHEMA or suite.get("experiment") != 142:
        raise ValueError("fixture suite schema or experiment number changed")
    if suite.get("contains_real_candidate") is not False:
        raise ValueError("Experiment 142 must not contain a real candidate")
    base = suite.get("base_candidate")
    cases_object = suite.get("cases")
    if not isinstance(base, dict) or not isinstance(cases_object, list):
        raise ValueError("fixture suite base_candidate/cases are invalid")

    rows: list[dict[str, object]] = []
    group_hashes: dict[str, set[str]] = {}
    for index, case_object in enumerate(cases_object):
        if not isinstance(case_object, dict):
            raise ValueError(f"cases[{index}] must be a mapping")
        case = cast(dict[str, object], case_object)
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not case_id:
            raise ValueError(f"cases[{index}].case_id must be a non-empty string")
        payload = _apply_mutations(base, case.get("mutations"))
        if case.get("reverse_collections") is True:
            payload = _reverse_collections(payload)
        elif case.get("reverse_collections") is not False:
            raise ValueError(f"cases[{index}].reverse_collections must be boolean")

        expected_status = case.get("expected_status")
        expected_reasons = case.get("expected_reason_codes")
        expected_error = case.get("expected_schema_error_contains")
        if expected_status is not None and not isinstance(expected_status, str):
            raise ValueError(f"cases[{index}].expected_status must be string or null")
        if not isinstance(expected_reasons, list) or not all(
            isinstance(item, str) for item in expected_reasons
        ):
            raise ValueError(f"cases[{index}].expected_reason_codes must be strings")
        if expected_error is not None and not isinstance(expected_error, str):
            raise ValueError(
                f"cases[{index}].expected_schema_error_contains must be string or null"
            )

        try:
            candidate = candidate_from_dict(payload)
            report = assess_candidate(candidate)
            actual_status: str | None = report.status.value
            actual_reasons = list(report.reason_codes)
            schema_error: str | None = None
            semantic_hash: str | None = report.candidate_sha256
            automated_pass = report.automated_novelty_pass
        except ValueError as error:
            actual_status = None
            actual_reasons = []
            schema_error = str(error)
            semantic_hash = None
            automated_pass = False

        expected_reasons_strings = cast(list[str], expected_reasons)
        outcome_matches = (
            actual_status == expected_status
            and actual_reasons == expected_reasons_strings
            and (
                (expected_error is None and schema_error is None)
                or (
                    isinstance(expected_error, str)
                    and isinstance(schema_error, str)
                    and expected_error in schema_error
                )
            )
        )
        group = case.get("semantic_equivalence_group")
        if group is not None:
            if not isinstance(group, str) or semantic_hash is None:
                raise ValueError(f"cases[{index}] has invalid semantic equivalence group")
            group_hashes.setdefault(group, set()).add(semantic_hash)
        rows.append(
            {
                "case_id": case_id,
                "expected_status": expected_status,
                "actual_status": actual_status,
                "expected_reason_codes": expected_reasons_strings,
                "actual_reason_codes": actual_reasons,
                "schema_error": schema_error,
                "candidate_sha256": semantic_hash,
                "automated_novelty_pass": automated_pass,
                "outcome_matches": outcome_matches,
            }
        )

    gates = {
        "exact_expected_outcomes": all(bool(row["outcome_matches"]) for row in rows),
        "semantic_hash_invariance": bool(group_hashes)
        and all(len(hashes) == 1 for hashes in group_hashes.values()),
        "no_automated_novelty_pass": not any(
            bool(row["automated_novelty_pass"]) for row in rows
        ),
        "no_pass_state": "PASS" not in {status.value for status in AdmissionStatus},
        "no_real_candidate": suite["contains_real_candidate"] is False,
        "actual_market_data_read": False,
        "actual_gpu_hours_zero": True,
    }
    passed = all(gates.values())
    return {
        "schema": RESULT_SCHEMA,
        "experiment": 142,
        "suite_id": suite.get("suite_id"),
        "git_commit": _git_commit(),
        "fixture_file_sha256": _file_sha256(path),
        "contract_implementation_sha256": _file_sha256(
            ROOT / "ecomd/invariant_calibration/g0_contract.py"
        ),
        "cases": rows,
        "semantic_equivalence_groups": {
            key: sorted(values) for key, values in sorted(group_hashes.items())
        },
        "gates": gates,
        "decision": "PASS_PROCESS_VALIDATION" if passed else "FAIL_PROCESS_VALIDATION",
        "scientific_status": "NO_ADMISSIBLE_REAL_CANDIDATE",
        "resource_audit": {
            "market_data_files_read": 0,
            "sealed_periods_opened": 0,
            "gpu_hours": 0.0,
            "fixture_contains_policy_violation_control": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--fixtures",
        type=Path,
        default=ROOT / "experiments/142_ncs_g0_reentry_contract/fixtures.yaml",
    )
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    if arguments.output.exists():
        raise FileExistsError(f"refusing to overwrite {arguments.output}")
    _require_clean_repository()
    result = run_suite(arguments.fixtures)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
