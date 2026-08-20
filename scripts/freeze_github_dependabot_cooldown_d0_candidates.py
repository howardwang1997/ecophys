"""Freeze outcome-blind D0 candidate cohorts from the immutable D-1 artifact."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import yaml

from ecomd.data.github_verification_liquidity import (
    assert_outcome_blind_payload,
    canonical_json_sha256,
    count_arrival_clusters,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ALLOWED_PATH = (
    REPO_ROOT / "data/raw/github_dependabot_cooldown_dminus1_v1/allowed_records.jsonl.gz"
)
DEFAULT_RESULT_PATH = (
    REPO_ROOT / "results/agent_markets/github_dependabot_cooldown_dminus1_v1.json"
)
DEFAULT_MANIFEST_PATH = (
    REPO_ROOT / "data/manifests/github_dependabot_cooldown_dminus1_v1.json"
)
DEFAULT_CONFIG_PATH = (
    REPO_ROOT / "configs/agent_markets/github_dependabot_cooldown_dminus1_v1.yaml"
)
DEFAULT_OUTPUT_PATH = (
    REPO_ROOT / "data/manifests/github_dependabot_cooldown_d0_candidate_ids_v1.json"
)


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _mapping(value: Any, *, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object")
    return value


def _sequence(value: Any, *, label: str) -> Sequence[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError(f"{label} must be an array")
    return value


def _canonical_without_digest(payload: Mapping[str, Any]) -> str:
    return canonical_json_sha256(
        {key: value for key, value in payload.items() if key != "canonical_payload_sha256"}
    )


def _candidate_row(row: Mapping[str, Any], *, gap_hours: float) -> dict[str, Any]:
    repository = _mapping(row.get("repository"), label="repository")
    config = _mapping(row.get("configuration"), label="configuration")
    bot_events = _sequence(row.get("bot_pull_requests"), label="bot pull requests")
    workflow_paths = sorted(str(value) for value in _sequence(row.get("workflow_paths"), label="paths"))
    timestamps = [str(_mapping(event, label="bot PR").get("created_at", "")) for event in bot_events]
    human_count = row.get("human_pull_request_count")
    if isinstance(human_count, bool) or not isinstance(human_count, int) or human_count < 0:
        raise ValueError("human PR support count must be a nonnegative integer")
    payload = {
        "repository_id": int(repository["id"]),
        "node_id": str(repository["node_id"]),
        "full_name": str(repository["full_name"]),
        "frame_rank": int(repository["frame_rank"]),
        "created_at": str(repository["created_at"]),
        "stargazers_count": int(repository["stargazers_count"]),
        "default_branch": str(repository["default_branch"]),
        "treatment_class": str(config["treatment_class"]),
        "config_commit_sha": config.get("commit_sha"),
        "config_content_sha256": config.get("content_sha256"),
        "schedule_schema": list(_sequence(config.get("schedule_schema"), label="schedule schema")),
        "grouping_present": config.get("grouping_present"),
        "workflow_paths": workflow_paths,
        "workflow_path_count": len(workflow_paths),
        "pre_bot_pr_count": len(bot_events),
        "pre_bot_24h_cluster_count": count_arrival_clusters(timestamps, gap_hours=gap_hours),
        "pre_human_pr_lower_bound_capped_100": human_count,
    }
    assert_outcome_blind_payload(payload)
    return payload


def build_ledger(
    *,
    allowed_path: Path,
    result_path: Path,
    manifest_path: Path,
    config_path: Path,
) -> dict[str, Any]:
    """Build the deterministic candidate ledger from the sealed formal records."""
    result = _mapping(json.loads(result_path.read_text(encoding="utf-8")), label="result")
    manifest = _mapping(json.loads(manifest_path.read_text(encoding="utf-8")), label="manifest")
    config = _mapping(yaml.safe_load(config_path.read_text(encoding="utf-8")), label="config")
    if result.get("mode") != "formal":
        raise ValueError("candidate freeze requires the formal D-1 result")
    support = _mapping(result.get("support"), label="result support")
    if support.get("scientific_decision") != "green_freeze_d0_before_opening_queue_outcomes":
        raise ValueError("candidate freeze requires a GREEN D-1 result")
    if result.get("canonical_payload_sha256") != _canonical_without_digest(result):
        raise ValueError("formal D-1 result canonical hash mismatch")
    if manifest.get("canonical_payload_sha256") != _canonical_without_digest(manifest):
        raise ValueError("formal D-1 manifest canonical hash mismatch")
    file_sha = _file_sha256(allowed_path)
    if file_sha != manifest.get("allowed_records_file_sha256"):
        raise ValueError("allowed-record file hash does not match the formal manifest")

    with gzip.open(allowed_path, "rt", encoding="utf-8") as handle:
        rows = [_mapping(json.loads(line), label="allowed record") for line in handle if line.strip()]
    assert_outcome_blind_payload(rows)
    if canonical_json_sha256(rows) != manifest.get("allowed_records_canonical_sha256"):
        raise ValueError("allowed-record canonical hash does not match the formal manifest")

    calibration = _mapping(config.get("calibration_window"), label="calibration window")
    minimum_bot = int(calibration["minimum_bot_prs_for_high_support_repository"])
    gap_hours = float(calibration["cluster_gap_hours"])
    candidates = [_candidate_row(row, gap_hours=gap_hours) for row in rows]
    treated = [
        row
        for row in candidates
        if row["treatment_class"] == "default_treated"
        and row["workflow_path_count"] > 0
        and row["pre_bot_pr_count"] >= minimum_bot
        and row["pre_human_pr_lower_bound_capped_100"] > 0
    ]
    controls = [
        row
        for row in candidates
        if row["treatment_class"] == "no_dependabot_control"
        and row["workflow_path_count"] > 0
        and row["pre_bot_pr_count"] == 0
        and row["pre_human_pr_lower_bound_capped_100"] > 0
    ]
    negative_controls = [
        row
        for row in candidates
        if row["treatment_class"] == "already_cooled"
        and row["workflow_path_count"] > 0
        and row["pre_bot_pr_count"] >= minimum_bot
        and row["pre_human_pr_lower_bound_capped_100"] > 0
    ]
    cohorts = {
        "default_treated_high_support": sorted(treated, key=lambda row: row["frame_rank"]),
        "no_dependabot_candidate_controls": sorted(controls, key=lambda row: row["frame_rank"]),
        "already_cooled_high_support_negative_controls": sorted(
            negative_controls, key=lambda row: row["frame_rank"]
        ),
    }
    if {key: len(value) for key, value in cohorts.items()} != {
        "default_treated_high_support": 72,
        "no_dependabot_candidate_controls": 447,
        "already_cooled_high_support_negative_controls": 33,
    }:
        raise RuntimeError("candidate counts no longer match the immutable formal D-1 decision")

    payload: dict[str, Any] = {
        "schema_version": 1,
        "audit": "github_dependabot_cooldown_d0_candidates",
        "freeze_git_sha": subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip(),
        "source": {
            "dminus1_result_path": result_path.relative_to(REPO_ROOT).as_posix(),
            "dminus1_result_canonical_sha256": result["canonical_payload_sha256"],
            "dminus1_manifest_path": manifest_path.relative_to(REPO_ROOT).as_posix(),
            "dminus1_manifest_canonical_sha256": manifest["canonical_payload_sha256"],
            "allowed_records_path": allowed_path.relative_to(REPO_ROOT).as_posix(),
            "allowed_records_file_sha256": file_sha,
            "allowed_records_canonical_sha256": manifest["allowed_records_canonical_sha256"],
        },
        "selection": {
            "pre_window_from_utc": calibration["from_utc"],
            "pre_window_to_utc": calibration["to_utc"],
            "minimum_bot_prs": minimum_bot,
            "cluster_gap_hours": gap_hours,
            "require_actions_workflow_path": True,
            "require_positive_human_pr_lower_bound": True,
            "human_pr_count_is_lower_bound_capped_at": 100,
        },
        "cohort_counts": {key: len(value) for key, value in cohorts.items()},
        "cohort_canonical_sha256": {
            key: canonical_json_sha256(value) for key, value in cohorts.items()
        },
        "cohorts": cohorts,
        "outcomes_opened": False,
    }
    assert_outcome_blind_payload(payload)
    payload["canonical_payload_sha256"] = canonical_json_sha256(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allowed", type=Path, default=DEFAULT_ALLOWED_PATH)
    parser.add_argument("--result", type=Path, default=DEFAULT_RESULT_PATH)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or output.with_name(output.name + ".partial").exists():
        raise FileExistsError(f"refusing to overwrite frozen candidate ledger: {output}")
    payload = build_ledger(
        allowed_path=args.allowed.resolve(),
        result_path=args.result.resolve(),
        manifest_path=args.manifest.resolve(),
        config_path=args.config.resolve(),
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    partial = output.with_name(output.name + ".partial")
    partial.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    partial.replace(output)
    print(json.dumps({"output": str(output), **payload["cohort_counts"]}, sort_keys=True))


if __name__ == "__main__":
    main()
