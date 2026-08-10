from __future__ import annotations

import json
from pathlib import Path

import yaml

from ecomd.data.yfinance_provenance import canonical_payload_sha256, sha256_file

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_taker_flow_response_contract_is_frozen_and_source_bound() -> None:
    path = REPO_ROOT / "configs/empirical_physics/taker_flow_response_feasibility_v1.yaml"
    protocol = yaml.safe_load(path.read_text())
    contract = protocol["contract"]
    assert contract["status"] == (
        "frozen_after_daily_regime_failure_before_binance_acquisition_or_response_outputs"
    )
    source_path = REPO_ROOT / "results/empirical_physics/regime_memory_exploratory_v1.json"
    source = json.loads(source_path.read_text())
    assert sha256_file(source_path) == contract["source_regime_result_file_sha256"]
    assert canonical_payload_sha256(source) == contract[
        "source_regime_result_canonical_sha256"
    ]
    assert protocol["data"]["symbols"] == ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    assert protocol["data"]["months"] == ["2024-01", "2024-02", "2024-03"]
    assert protocol["data"]["signed_flow_name"] == "taker_flow_imbalance_not_cks_ofi"
    assert protocol["data"]["cks_ofi_language"] == "forbidden"
    assert len(
        protocol["archive_validation"]["daily_monthly_exact_crosscheck_dates"]
    ) == 9
    assert protocol["event_selection"]["selection_uses_current_or_future_returns"] is False
    assert protocol["dependence_aware_inference"]["inference_unit"] == (
        "common_utc_calendar_day_not_event_or_asset_day"
    )
    assert protocol["primary_gate"]["every_clause_required"] is True
    assert protocol["decision"]["pass"] == (
        "permit_fresh_quarter_aggtrades_event_time_confirmation_protocol_only"
    )
    assert protocol["compute"]["gpu_forbidden"] is True


def test_taker_flow_manifest_is_either_pending_or_immutably_bound() -> None:
    protocol_path = (
        REPO_ROOT / "configs/empirical_physics/taker_flow_response_feasibility_v1.yaml"
    )
    protocol = yaml.safe_load(protocol_path.read_text())
    data = protocol["data"]
    status = data["manifest_binding_status"]
    if status == "pending_result_blind_acquisition":
        assert data["manifest_canonical_payload_sha256"] is None
        assert data["manifest_file_sha256"] is None
        assert data["acquisition_protocol_git_sha"] is None
        assert data["acquisition_protocol_sha256"] is None
        return
    assert status == "bound_after_result_blind_acquisition_before_response_outputs"
    manifest_path = REPO_ROOT / data["manifest_path"]
    manifest = json.loads(manifest_path.read_text())
    assert sha256_file(manifest_path) == data["manifest_file_sha256"]
    assert canonical_payload_sha256(manifest) == data[
        "manifest_canonical_payload_sha256"
    ]
    assert manifest["repository"]["git_sha"] == data["acquisition_protocol_git_sha"]
    assert manifest["code"]["protocol_sha256"] == data["acquisition_protocol_sha256"]
