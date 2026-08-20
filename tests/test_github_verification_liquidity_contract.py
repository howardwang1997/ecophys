from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs/agent_markets/github_dependabot_cooldown_dminus1_v1.yaml"
RUNTIME_PATH = REPO_ROOT / "configs/agent_markets/github_dependabot_cooldown_dminus1_runtime_v1.yaml"


def _yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_scientific_and_runtime_contracts_are_bound_to_preregistration() -> None:
    config = _yaml(CONFIG_PATH)
    runtime = _yaml(RUNTIME_PATH)
    assert config["contract"]["status"] == "frozen_before_formal_frame_acquisition"
    assert runtime["contract"]["status"] == "frozen_before_formal_frame_acquisition"
    observed_hash = hashlib.sha256(CONFIG_PATH.read_bytes()).hexdigest()
    assert runtime["contract"]["parent_config_sha256"] == observed_hash
    preregistration_sha = runtime["contract"]["preregistration_git_sha"]
    relative_path = CONFIG_PATH.relative_to(REPO_ROOT)
    committed = subprocess.run(
        ["git", "show", f"{preregistration_sha}:{relative_path}"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    ).stdout
    assert hashlib.sha256(committed).hexdigest() == observed_hash


def test_contract_seals_queue_review_merge_and_security_outcomes() -> None:
    config = _yaml(CONFIG_PATH)
    forbidden = set(config["forbidden_persisted_fields"])
    required = {
        "workflow_run_started_at_value",
        "job_started_at_value",
        "job_completed_at_value",
        "workflow_or_job_conclusion",
        "pull_request_closed_or_merged_state",
        "pull_request_review_or_comment_response",
        "duration_or_queue_wait",
        "package_release_timestamp_or_release_age",
        "vulnerability_or_security_outcome",
        "raw_api_payload_containing_any_forbidden_field",
    }
    assert required <= forbidden
    assert config["compute"] == {
        "maximum_mac_core_hours": 20,
        "maximum_local_storage_gb": 5,
        "gpu_allowed": False,
        "paid_data_allowed": False,
        "h20_allowed": False,
    }


def test_formal_frame_and_stop_gates_are_explicit() -> None:
    config = _yaml(CONFIG_PATH)
    assert config["frame"]["pages"] == 10
    assert config["frame"]["per_page"] == 100
    assert config["calibration_window"]["to_utc"] <= config["intervention"]["config_cutoff_utc"]
    assert config["gates"]["minimum_unique_frame_repositories"] == 800
    assert config["gates"]["minimum_default_treated_with_actions"] == 100
    assert config["gates"]["minimum_high_support_default_treated"] == 50
    assert config["decision"]["red"].startswith("stop_before_queue_outcomes")
