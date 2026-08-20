from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
V1_CONFIG_PATH = ROOT / "configs/agent_markets/github_dependabot_cooldown_d0_v1.yaml"
V2_CONFIG_PATH = ROOT / "configs/agent_markets/github_dependabot_cooldown_d0_v2.yaml"
CONFIG_PATH = ROOT / "configs/agent_markets/github_dependabot_cooldown_d0_v3.yaml"
LEDGER_PATH = ROOT / "data/manifests/github_dependabot_cooldown_d0_candidate_ids_v1.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(encoded).hexdigest()


def _parse(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def test_d0_candidate_ledger_is_bound_to_the_formal_outcome_blind_source() -> None:
    config = _load_yaml(CONFIG_PATH)
    ledger = _load_json(LEDGER_PATH)
    body = {key: value for key, value in ledger.items() if key != "canonical_payload_sha256"}

    assert _file_sha256(LEDGER_PATH) == config["source"]["candidate_ledger_file_sha256"]
    assert ledger["canonical_payload_sha256"] == _canonical(body)
    assert ledger["canonical_payload_sha256"] == config["source"]["candidate_ledger_canonical_sha256"]
    assert ledger["source"]["dminus1_result_canonical_sha256"] == (
        config["source"]["dminus1_result_canonical_sha256"]
    )
    assert ledger["outcomes_opened"] is False
    assert ledger["cohort_counts"] == {
        "already_cooled_high_support_negative_controls": 33,
        "default_treated_high_support": 72,
        "no_dependabot_candidate_controls": 447,
    }


def test_d0_v2_supersedes_v1_before_acquisition_without_changing_science() -> None:
    config = _load_yaml(V2_CONFIG_PATH)
    v1 = _load_yaml(V1_CONFIG_PATH)
    assert config["contract"]["supersedes"] == str(V1_CONFIG_PATH.relative_to(ROOT))
    assert config["contract"]["superseded_config_sha256"] == _file_sha256(V1_CONFIG_PATH)
    for key in ("source", "intervention", "windows", "cohorts", "run_identity", "decision", "compute"):
        assert config[key] == v1[key]
    v2_gates = {key: value for key, value in config["gates"].items() if key != "denominator_definitions"}
    assert v2_gates == v1["gates"]
    assert config["prequalification"]["never_uses_postperiod_counts_or_field_presence"] is True


def test_d0_v3_only_resolves_the_external_incident_key_collision() -> None:
    config = _load_yaml(CONFIG_PATH)
    v2 = _load_yaml(V2_CONFIG_PATH)
    assert config["contract"]["supersedes"] == str(V2_CONFIG_PATH.relative_to(ROOT))
    assert config["contract"]["superseded_config_sha256"] == _file_sha256(V2_CONFIG_PATH)
    unchanged = set(v2) - {"contract", "allowed_persisted_fields"}
    for key in unchanged:
        assert config[key] == v2[key]
    v3_allowed = dict(config["allowed_persisted_fields"])
    v2_allowed = dict(v2["allowed_persisted_fields"])
    assert {key: value for key, value in v3_allowed.items() if key != "external_incident"} == {
        key: value for key, value in v2_allowed.items() if key != "external_incident"
    }
    assert v3_allowed["external_incident"] == [
        "incident_id",
        "title",
        "reported_start_utc",
        "reported_resolution_utc",
        "affected_component_names",
        "source_response_sha256",
    ]


def test_d0_candidate_ids_and_cohort_hashes_are_exact_and_disjoint() -> None:
    config = _load_yaml(CONFIG_PATH)
    ledger = _load_json(LEDGER_PATH)
    all_ids: set[int] = set()
    for cohort, rows in ledger["cohorts"].items():
        assert ledger["cohort_canonical_sha256"][cohort] == _canonical(rows)
        assert config["source"]["candidate_cohort_hashes"][cohort] == _canonical(rows)
        ids = {int(row["repository_id"]) for row in rows}
        assert len(ids) == len(rows)
        assert not all_ids.intersection(ids)
        all_ids.update(ids)
    assert len(all_ids) == 552


def test_d0_windows_are_symmetric_and_the_prospective_holdout_is_embargoed() -> None:
    config = _load_yaml(CONFIG_PATH)
    windows = config["windows"]
    one_second = 1.0
    pre_seconds = (
        _parse(windows["primary_pre_to_utc"]) - _parse(windows["primary_pre_from_utc"])
    ).total_seconds() + one_second
    blackout_seconds = (
        _parse(windows["rollout_blackout_to_utc"])
        - _parse(windows["rollout_blackout_from_utc"])
    ).total_seconds() + one_second
    post_seconds = (
        _parse(windows["primary_post_to_utc"]) - _parse(windows["primary_post_from_utc"])
    ).total_seconds() + one_second
    prospective_seconds = (
        _parse(windows["prospective_holdout_to_utc"])
        - _parse(windows["prospective_holdout_from_utc"])
    ).total_seconds() + one_second

    assert pre_seconds == post_seconds == 28 * 24 * 3600
    assert blackout_seconds == 3 * 24 * 3600
    assert prospective_seconds == 56 * 24 * 3600
    assert _parse(windows["prospective_outcomes_may_not_be_accessed_before_utc"]) > _parse(
        windows["prospective_holdout_to_utc"]
    )


def test_d0_matching_sampling_and_outcome_seal_are_explicit() -> None:
    config = _load_yaml(CONFIG_PATH)
    assert config["contract"]["status"] == "frozen_before_formal_outcome_blind_d0_acquisition"
    assert config["run_identity"]["primary_human"] == {
        "actor_type": "User",
        "event_types": ["push"],
        "run_attempt": 1,
        "exclude_dependabot_login": "dependabot[bot]",
    }
    assert config["matching"]["uses_preperiod_fields_only"] is True
    assert config["matching"]["ratio"] == 3
    assert config["matching"]["replacement"] is False
    assert config["gates"]["minimum_matched_treated_repositories"] == 60
    assert config["gates"]["minimum_matched_control_repositories"] == 180
    assert config["gates"]["minimum_treated_repositories_with_shared_bot_human_pool"] == 30

    forbidden = set(config["forbidden_persisted_fields"])
    assert {
        "job_started_at_value",
        "duration_or_queue_wait",
        "pre_post_queue_summary_or_test",
        "pre_post_dependabot_first_stage_contrast",
        "outcome_based_matching_or_sample_selection",
        "raw_api_payload_containing_any_forbidden_field",
    } <= forbidden
    assert config["compute"]["gpu_allowed"] is False
    assert config["compute"]["rtx2060_gpu_allowed"] is False
    assert config["compute"]["h20_allowed"] is False
    assert config["compute"]["paid_data_allowed"] is False
