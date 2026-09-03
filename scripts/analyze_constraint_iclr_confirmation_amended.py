"""Run the eight-system confirmation after the two frozen Burgers failures."""

from __future__ import annotations

import argparse
import json
import math
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from analyze_constraint_iclr import (
    CONFIRMATION_SEEDS,
    analyze_confirmation,
    system_key,
    validate_confirmation_lock,
    validate_provenance,
)
from constraint_iclr_common import sha256_file

EXPECTED_GIT_HEAD = "86dd76ee0127c5eb7945a5806bdad74548c62459"
EXPECTED_LOCK_SHA256 = "5100ae5ca6f757a5166fba3692fd912e19e7a0c7a4da65980488e92a402c604e"
EXPECTED_FAILURE_DECISION_SHA256 = (
    "8c20198a85fb5425faf05f0f54364d579806e318646a0a4b35901e32380f797c"
)
COMPLETE_SYSTEMS = (
    "A:advection",
    "A:diffusion",
    "B:advection",
    "B:diffusion",
    "C:ad2d",
    "H:contraction_near",
    "H:contraction_strong",
    "M2:fifo_cda",
)
FAILED_SYSTEMS = {
    "A:burgers": {
        "incident_path": (
            "experiments/constraint_attribution_iclr/deployment/"
            "v100a_aburgers_nonfinite_incident_20260831.yaml"
        ),
        "incident_sha256": (
            "44f3241022e241b9af2d4fac4f554bc98d34f672c5370dbb9835272347a33d13"
        ),
        "status": "failed_incomplete",
        "attempts": 2,
    },
    "B:burgers": {
        "incident_path": (
            "experiments/constraint_attribution_iclr/deployment/"
            "v100b_bburgers_nonfinite_incident_20260901.yaml"
        ),
        "incident_sha256": (
            "89a3fe99f57b56e58c9de248496f76a03c548a85bbcc75f2e3455d0460f7e40b"
        ),
        "status": "failed_incomplete",
        "attempts": 1,
    },
}


def load_jsonl_exact(paths: Iterable[Path]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in paths:
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise RuntimeError(f"invalid JSONL {path}:{line_number}: {error}") from error
            if not isinstance(record, dict):
                raise RuntimeError(f"non-object JSONL record at {path}:{line_number}")
            records.append(record)
    return records


def _all_finite(value: Any) -> bool:
    if isinstance(value, dict):
        return all(_all_finite(item) for item in value.values())
    if isinstance(value, list):
        return all(_all_finite(item) for item in value)
    if isinstance(value, float):
        return math.isfinite(value)
    return True


def expected_record_keys(
    lock: dict[str, Any], systems: Iterable[str], seeds: Iterable[int]
) -> set[tuple[str, str, str, int]]:
    expected: set[tuple[str, str, str, int]] = set()
    for key in systems:
        for job in lock["systems"][key]["confirmation_jobs"]:
            mechanisms = [str(job["mechanism"])]
            if job["mechanism"] == "free":
                mechanisms.append("projection")
            for mechanism in mechanisms:
                for seed in seeds:
                    expected.add((key, mechanism, str(job["config_id"]), int(seed)))
    return expected


def validate_amended_confirmation(
    records: list[dict[str, Any]],
    lock: dict[str, Any],
    *,
    complete_systems: Iterable[str] = COMPLETE_SYSTEMS,
    failed_systems: Iterable[str] = FAILED_SYSTEMS,
    seeds: Iterable[int] = CONFIRMATION_SEEDS,
    expected_lock_sha256: str = EXPECTED_LOCK_SHA256,
    expected_git_head: str = EXPECTED_GIT_HEAD,
) -> dict[str, Any]:
    complete = tuple(complete_systems)
    failed = set(failed_systems)
    seed_set = {int(value) for value in seeds}
    if set(complete) & failed:
        raise RuntimeError("complete and failed system declarations overlap")
    if set(complete) | failed != set(lock["systems"]):
        raise RuntimeError("complete/failed declarations do not partition the frozen lock")

    expected = expected_record_keys(lock, complete, seed_set)
    observed: set[tuple[str, str, str, int]] = set()
    run_ids: set[str] = set()
    failures: list[str] = []
    for record in records:
        key = system_key(record)
        record_key = (
            key,
            str(record.get("mechanism")),
            str(record.get("config_id")),
            int(record.get("seed", -1)),
        )
        run_id = str(record.get("run_id"))
        if record_key in observed:
            failures.append(f"duplicate system/mechanism/cell/seed {record_key}")
        if run_id in run_ids:
            failures.append(f"duplicate run_id {run_id}")
        observed.add(record_key)
        run_ids.add(run_id)
        if record.get("schema_version") != "constraint-iclr-v1":
            failures.append(f"wrong schema for {run_id}")
        if record.get("stage") != "confirmation":
            failures.append(f"wrong stage for {run_id}")
        if key in failed:
            failures.append(f"failed system unexpectedly has a record: {record_key}")
        if not _all_finite(record):
            failures.append(f"non-finite numeric field for {run_id}")
        provenance = record.get("provenance", {})
        if provenance.get("git_head") != expected_git_head:
            failures.append(f"wrong Git head for {run_id}")
        if provenance.get("git_dirty") is not True:
            failures.append(f"wrong dirty-worktree flag for {run_id}")

    missing = expected.difference(observed)
    extra = observed.difference(expected)
    if missing:
        failures.append(f"missing exact locked records: {len(missing)}")
    if extra:
        failures.append(f"unexpected exact locked records: {len(extra)}")
    failures.extend(validate_provenance(records))
    failures.extend(validate_confirmation_lock(records, expected_lock_sha256))
    if failures:
        raise RuntimeError("; ".join(failures))
    return {
        "record_count": len(records),
        "expected_record_count": len(expected),
        "complete_systems": list(complete),
        "failed_systems": sorted(failed),
        "unique_run_ids": len(run_ids),
        "all_numeric_fields_finite": True,
        "provenance_passed": True,
        "lock_binding_passed": True,
    }


def _verified_release_sha256(
    *,
    root: Path,
    path: Path,
    expected: str,
    artifact_manifest: Path | None,
) -> str:
    observed = sha256_file(path)
    if observed == expected:
        return expected
    if artifact_manifest is not None and artifact_manifest.is_file():
        manifest = json.loads(artifact_manifest.read_text(encoding="utf-8"))
        try:
            relative = path.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            relative = path.as_posix()
        for entry in manifest.get("double_blind_redactions", []):
            if (
                isinstance(entry, dict)
                and entry.get("archive_path") is None
                and entry.get("path") == relative
                and entry.get("source_sha256") == expected
                and entry.get("released_sha256") == observed
            ):
                return expected
    raise RuntimeError(
        f"artifact SHA-256 mismatch for {path}: expected {expected}, got {observed}"
    )


def verify_failure_artifacts(
    root: Path,
    failure_decision: Path,
    artifact_manifest: Path | None = None,
) -> dict[str, Any]:
    verified_decision_sha256 = _verified_release_sha256(
        root=root,
        path=failure_decision,
        expected=EXPECTED_FAILURE_DECISION_SHA256,
        artifact_manifest=artifact_manifest,
    )
    verified: dict[str, Any] = {}
    for key, declaration in FAILED_SYSTEMS.items():
        path = root / str(declaration["incident_path"])
        expected = str(declaration["incident_sha256"])
        _verified_release_sha256(
            root=root,
            path=path,
            expected=expected,
            artifact_manifest=artifact_manifest,
        )
        verified[key] = dict(declaration)
    return {
        "failure_decision_path": str(failure_decision),
        "failure_decision_sha256": verified_decision_sha256,
        "declared_failures": verified,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", type=Path, nargs="+", required=True)
    parser.add_argument(
        "--lock",
        type=Path,
        default=Path(
            "experiments/constraint_attribution_iclr/pilot/"
            "pilot_lock_final_idonly_20260831.json"
        ),
    )
    parser.add_argument(
        "--failure-decision",
        type=Path,
        default=Path(
            "research/discovery/decisions/"
            "constraint_attribution_iclr_v100b_failure_continuation_20260901.yaml"
        ),
    )
    parser.add_argument("--artifact-manifest", type=Path)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(
            "experiments/constraint_attribution_iclr/confirmation/"
            "analysis_amended_20260901.json"
        ),
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    records = load_jsonl_exact(args.records)
    lock = json.loads(args.lock.read_text(encoding="utf-8"))
    observed_lock_sha256 = sha256_file(args.lock)
    if observed_lock_sha256 != EXPECTED_LOCK_SHA256:
        raise RuntimeError(
            f"selection-lock SHA-256 mismatch: {observed_lock_sha256}"
        )
    integrity = validate_amended_confirmation(records, lock)
    failure_artifacts = verify_failure_artifacts(
        root, args.failure_decision, args.artifact_manifest
    )
    amended_lock = {**lock, "systems": {key: lock["systems"][key] for key in COMPLETE_SYSTEMS}}
    result = analyze_confirmation(records, amended_lock)
    result["schema_version"] = "constraint-iclr-analysis-amended-v1"
    result["integrity"] = integrity
    result["failure_artifacts"] = failure_artifacts
    result["selection_lock_sha256"] = observed_lock_sha256
    result["input_sha256_by_path"] = {
        str(path): sha256_file(path) for path in args.records
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
