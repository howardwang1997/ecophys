from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "results/agent_markets/cow_computational_liquidity_t0_v1.json"
MANIFEST_PATH = ROOT / "data/manifests/cow_computational_liquidity_t0_v1.json"
R2_RECEIPT_PATH = ROOT / "data/manifests/cow_computational_liquidity_t0_v1_r2_receipt.json"
CONFIG_PATH = ROOT / "configs/agent_markets/cow_computational_liquidity_t0_v1.yaml"
RUNTIME_PATH = ROOT / "configs/agent_markets/cow_computational_liquidity_t0_runtime_v1.yaml"


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


def test_formal_result_is_bound_red_and_outcome_analysis_stayed_closed() -> None:
    result = _load(RESULT_PATH)
    assert result["repository"]["git_sha"] == "3b1ce6f3f286bc2ddc9aa1dca9f75438cc0b8253"
    assert result["contract"]["preregistration_git_sha"] == (
        "b2153f39621be2de2c30cd0e4851e75de011ce1b"
    )
    assert result["contract"]["scientific_config_sha256"] == _file_sha256(CONFIG_PATH)
    assert result["contract"]["runtime_config_sha256"] == _file_sha256(RUNTIME_PATH)
    assert result["canonical_payload_sha256"] == _canonical_without_digest(result)
    assert result["scientific_decision"] == "red_stop_route_no_window_chain_or_definition_rescue"
    assert result["base_support_gates_pass"] is False
    assert result["data_contract"] == {
        "EcoMD_used": False,
        "association_test_run": False,
        "gpu_used": False,
        "paid_data_used": False,
        "window_or_chain_expansion_used": False,
    }


def test_formal_counts_and_failures_cannot_be_silently_rewritten() -> None:
    result = _load(RESULT_PATH)
    metrics = result["metrics"]
    assert result["formal_window"]["from_block"] == 25_780_000
    assert result["formal_window"]["to_block"] == 25_780_499
    assert result["formal_window"]["settlement_event_count"] == 132
    assert metrics["attempted_settlement_transaction_count"] == 132
    assert metrics["mapped_settlement_transaction_count"] == 131
    assert metrics["distinct_competition_count"] == 119
    assert metrics["valid_winner_removal_count"] == 132
    assert metrics["low_criticality_removal_count"] == 12
    assert metrics["high_criticality_removal_count"] == 97
    assert metrics["submitted_coupled_competition_count"] == 12
    assert metrics["eligible_coupled_competition_count"] == 2
    assert metrics["conflicting_duplicate_auction_count"] == 5
    failed = {name for name, passed in result["gates"].items() if not passed}
    assert failed == {
        "distinct_competition_support",
        "eligible_coupling_green",
        "low_criticality_support",
        "no_conflicting_duplicate_auction_payloads",
        "settlement_transaction_support",
        "submitted_coupling_support",
    }


def test_provenance_manifest_binds_local_raw_shards_without_redistributing_them() -> None:
    result = _load(RESULT_PATH)
    manifest = _load(MANIFEST_PATH)
    assert manifest["canonical_payload_sha256"] == _canonical_without_digest(manifest)
    assert result["data_manifest"]["sha256"] == _file_sha256(MANIFEST_PATH)
    assert result["data_manifest"]["canonical_payload_sha256"] == manifest["canonical_payload_sha256"]
    assert manifest["raw_artifacts"]["blockscout_sha256"] == (
        "475fbe93cf0ba7b7a8821b8a2c963669ea40a815079342828504e060856aae14"
    )
    assert manifest["raw_artifacts"]["cow_sha256"] == (
        "4c6ac93b51efbef109e9bbec46d4a4534fa780e2b92ef8add3d9e247d0a267dd"
    )
    assert manifest["counts"]["parse_failure_counts"] == {"http_404": 1}
    assert manifest["data_contract"]["formal_window_only"] is True


def test_r2_receipt_binds_canonical_bulk_keys_to_local_hashes_and_sizes() -> None:
    manifest = _load(MANIFEST_PATH)
    receipt = _load(R2_RECEIPT_PATH)
    assert receipt["bucket"] == "ecophys"
    objects = {row["key"]: row for row in receipt["objects"]}
    blockscout = objects["raw/cow_computational_liquidity_t0_v1/blockscout_settlement_events.json.gz"]
    cow = objects["raw/cow_computational_liquidity_t0_v1/cow_competitions.jsonl.gz"]
    assert blockscout["content_length"] == manifest["raw_artifacts"]["blockscout_compressed_bytes"]
    assert blockscout["local_sha256"] == manifest["raw_artifacts"]["blockscout_sha256"]
    assert cow["content_length"] == manifest["raw_artifacts"]["cow_compressed_bytes"]
    assert cow["local_sha256"] == manifest["raw_artifacts"]["cow_sha256"]
    assert "not treated as a content hash" in receipt["verification"]
