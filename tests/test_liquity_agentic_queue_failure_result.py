from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ecomd.data.aave_qualification import canonical_sha256

REPO_ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = REPO_ROOT / "results/empirical_physics/liquity_agentic_queue_d0_v5_failure.json"


def _load_result() -> dict[str, Any]:
    payload = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_liquity_d0_failure_manifest_is_immutable_and_bound_to_freeze() -> None:
    result = _load_result()
    digest = result.pop("canonical_payload_sha256")

    assert canonical_sha256(result) == digest
    assert digest == "2767a17f204694959d254e1f7a17755a2609bf7507cae3eb6b85d794a9eecf73"
    assert result["decision"] == "stop_liquity_nmi_route_before_support_gate_transport_failure"
    assert result["repository"] == {
        "clean_worktree_at_formal_start": True,
        "config_path": "configs/empirical_physics/liquity_agentic_queue_d0_v5.yaml",
        "config_sha256": "22046333a9d1f16a75eaf2acb91c0f25272c2e344a5b7d7b1229ea31dba30edb",
        "git_sha": "971b985d738da78735d3addffe93a30bbdb7c7d7",
    }


def test_liquity_d0_failure_is_one_blockscout_omission() -> None:
    result = _load_result()
    replication = result["transport"]["full_replication"]
    assert replication["passed"] is False
    assert replication["formal_event_count"] == 24_291
    assert replication["replica_event_count"] == 24_292
    assert replication["formal_only_count"] == 0
    assert replication["replica_only_count"] == 1

    mismatch = result["single_mismatch"]
    assert mismatch["block_number"] == 25_401_761
    assert mismatch["log_index"] == 1_756
    assert mismatch["event_name_from_frozen_topic"] == "BatchUpdated"
    assert mismatch["diagnosis"] == "real_canonical_log_omitted_by_blockscout_index_and_receipt_transport"
    assert mismatch["blockscout_exact_block_eth_getLogs_present"] is False
    assert mismatch["blockscout_transaction_receipt_present"] is False
    for provider_field in {
        "sqd_finalized_portal_present",
        "drpc_exact_block_eth_getLogs_present",
        "drpc_transaction_receipt_present",
        "onfinality_exact_block_eth_getLogs_present",
        "onfinality_transaction_receipt_present",
    }:
        assert mismatch[provider_field] is True


def test_liquity_d0_failure_precedes_support_and_outcomes() -> None:
    result = _load_result()
    assert result["support_gate"] == {
        "evaluated": False,
        "metrics": None,
        "reason": "frozen_full_identity_replication_failed_before_timestamp_attachment_and_support_summary",
    }
    assert result["stop_rule"] == {
        "invoked": True,
        "no_d1_queue_or_market_outcomes": True,
        "no_ecomd_or_gpu": True,
        "no_threshold_relaxation": True,
        "no_transport_reselection_or_rerun_to_seek_pass": True,
    }
    assert result["compute"] == {
        "cpu_only": True,
        "ecomd_used": False,
        "gpu_used": False,
        "paid_data_used": False,
    }
    assert all(value is False for value in result["blinding"].values())
