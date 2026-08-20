from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "results/agent_markets/github_dependabot_cooldown_dminus1_v1.json"
MANIFEST_PATH = ROOT / "data/manifests/github_dependabot_cooldown_dminus1_v1.json"
CONFIG_PATH = ROOT / "configs/agent_markets/github_dependabot_cooldown_dminus1_v1.yaml"
RUNTIME_PATH = ROOT / "configs/agent_markets/github_dependabot_cooldown_dminus1_runtime_v1.yaml"


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_without_digest(payload: dict[str, Any]) -> str:
    body = {key: value for key, value in payload.items() if key != "canonical_payload_sha256"}
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(encoded).hexdigest()


def test_formal_dminus1_result_is_bound_green_and_outcomes_remain_sealed() -> None:
    result = _load(RESULT_PATH)
    manifest = _load(MANIFEST_PATH)

    assert result["git_sha"] == "bf23db8d3e5d5d7ea067fa301d34b099aac3fa45"
    assert result["config_sha256"] == _file_sha256(CONFIG_PATH)
    assert result["runtime_sha256"] == _file_sha256(RUNTIME_PATH)
    assert result["canonical_payload_sha256"] == _canonical_without_digest(result)
    assert manifest["canonical_payload_sha256"] == _canonical_without_digest(manifest)
    assert result["support"]["scientific_decision"] == (
        "green_freeze_d0_before_opening_queue_outcomes"
    )
    assert all(result["support"]["gates"].values())
    assert result["outcome_seal"]["queue_review_merge_security_values_opened"] is False
    assert manifest["forbidden_raw_outcome_payload_persisted"] is False


def test_formal_support_and_treatment_counts_cannot_be_silently_rewritten() -> None:
    result = _load(RESULT_PATH)
    assert result["frame"]["repository_count"] == 1_000
    assert result["treatment_class_counts"] == {
        "already_cooled": 63,
        "ambiguous": 9,
        "default_treated": 226,
        "no_dependabot_control": 702,
    }
    assert result["support"]["metrics"] == {
        "default_treated_with_actions": 226,
        "deterministic_derived_summary_hash": True,
        "eligible_no_dependabot_controls": 447,
        "high_support_default_treated": 72,
        "historical_config_recovery_rate": 0.9744318181818182,
        "no_forbidden_persisted_field": True,
        "pre_event_clusters": 2_499,
        "pre_event_dependabot_pull_requests": 9_280,
        "required_queue_field_presence_rate": 1.0,
        "unique_frame_repositories": 1_000,
        "workflow_run_access_rate": 1.0,
    }
    assert result["transport"]["request_count"] == 4_573
    assert result["transport"]["http_code_counts"] == {"200": 4_519, "404": 54}


def test_formal_manifest_binds_the_outcome_blind_allowed_record_artifact() -> None:
    result = _load(RESULT_PATH)
    manifest = _load(MANIFEST_PATH)
    expected_file = "74dc95a2d9e20d0bfb86feb48bed4d1b741877f4d528880981e1427cb5212448"
    expected_canonical = "ae7c9f3686f9da2f16dd2c3d32680bf8679de72c8d4c8a6316006cc97690b423"

    assert result["outcome_seal"]["allowed_records_file_sha256"] == expected_file
    assert result["outcome_seal"]["allowed_records_canonical_sha256"] == expected_canonical
    assert manifest["allowed_records_file_sha256"] == expected_file
    assert manifest["allowed_records_canonical_sha256"] == expected_canonical
    assert manifest["transport"] == result["transport"]
