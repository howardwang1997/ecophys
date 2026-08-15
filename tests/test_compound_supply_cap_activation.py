import hashlib
import json
from collections import Counter
from copy import deepcopy
from pathlib import Path

import pytest

from ecomd.research.compound_supply_cap_activation import (
    FROZEN_CANDIDATE_IDS,
    FROZEN_IMPLEMENTATIONS,
    LOOKBACK_BLOCK_OFFSETS,
    _failure_artifact,
    _utilization_record,
    build_http_transport,
    decode_totals_collateral,
    derive_parent_candidates,
    expected_operation_plan,
    load_supply_cap_activation,
    normalize_verified_source,
    validate_parent_evidence,
    validate_supply_cap_activation,
)

MANIFEST_PATH = Path("data/manifests/compound_v3_supply_cap_activation_preflight_v1.yaml")
MECHANICS_SUMMARY_PATH = Path(
    "experiments/v14_compound_v3_candidate_mechanics_preflight/artifacts_v2/summary.json"
)
MECHANICS_CANDIDATES_PATH = Path(
    "experiments/v14_compound_v3_candidate_mechanics_preflight/artifacts_v2/candidates.json"
)
ADDRESS = "0x528c57a87706c31765001779168b42f24c694e1b"


def _word(value: int) -> str:
    return value.to_bytes(32, "big").hex()


def _abi() -> list[dict[str, object]]:
    return [
        {
            "type": "function",
            "name": "totalsCollateral",
            "stateMutability": "view",
            "inputs": [{"name": "", "type": "address"}],
            "outputs": [
                {"name": "totalSupplyAsset", "type": "uint128"},
                {"name": "_reserved", "type": "uint128"},
            ],
        },
        {
            "type": "function",
            "name": "getAssetInfoByAddress",
            "stateMutability": "view",
            "inputs": [{"name": "asset", "type": "address"}],
            "outputs": [
                {
                    "name": "",
                    "type": "tuple",
                    "components": [
                        {"name": "offset", "type": "uint8"},
                        {"name": "asset", "type": "address"},
                        {"name": "priceFeed", "type": "address"},
                        {"name": "scale", "type": "uint64"},
                        {"name": "borrowCollateralFactor", "type": "uint64"},
                        {"name": "liquidateCollateralFactor", "type": "uint64"},
                        {"name": "liquidationFactor", "type": "uint64"},
                        {"name": "supplyCap", "type": "uint128"},
                    ],
                }
            ],
        },
    ]


def _source_metadata(bytecode: bytes = b"\x60\x00") -> dict[str, object]:
    source = """
    struct TotalsCollateral { uint128 totalSupplyAsset; uint128 _reserved; }
    mapping(address => TotalsCollateral) public totalsCollateral;
    function supplyCollateral(address asset, uint128 amount) internal {
        TotalsCollateral memory totals = totalsCollateral[asset];
        totals.totalSupplyAsset += amount;
        AssetInfo memory assetInfo = getAssetInfoByAddress(asset);
        if (totals.totalSupplyAsset > assetInfo.supplyCap) revert SupplyCapExceeded();
        totalsCollateral[asset] = totals;
    }
    """
    return {
        "is_verified": True,
        "is_fully_verified": True,
        "is_changed_bytecode": False,
        "name": "Comet",
        "language": "solidity",
        "compiler_version": "v0.8.15+commit.e14f2714",
        "compiler_settings": {"optimizer": {"enabled": True, "runs": 1}},
        "verified_at": "2023-01-01T00:00:00Z",
        "abi": json.dumps(_abi()),
        "file_path": "contracts/Comet.sol",
        "source_code": source,
        "additional_sources": [],
        "deployed_bytecode": "0x" + bytecode.hex(),
    }


def _derived() -> list[dict[str, object]]:
    summary = json.loads(MECHANICS_SUMMARY_PATH.read_text(encoding="utf-8"))
    candidates = json.loads(MECHANICS_CANDIDATES_PATH.read_text(encoding="utf-8"))
    return derive_parent_candidates(summary, candidates)


def test_manifest_parents_survivors_and_exact_request_plan() -> None:
    manifest = load_supply_cap_activation(MANIFEST_PATH)

    assert validate_supply_cap_activation(manifest) == []
    assert validate_parent_evidence(manifest, Path.cwd()) == []
    derived = _derived()
    assert [item["candidate"]["candidate_id"] for item in derived] == list(FROZEN_CANDIDATE_IDS)
    plan = expected_operation_plan(manifest, derived)
    assert len(plan) == 141
    assert Counter(item["provider"] for item in plan) == {
        "blockscout": 49,
        "blockscout_smart_contract": 7,
        "publicnode_execution": 85,
    }
    assert Counter(item["method"] for item in plan if item["operation_type"] == "json_rpc") == {
        "eth_call": 100,
        "eth_chainId": 2,
        "eth_getBlockByNumber": 24,
        "eth_getCode": 8,
    }
    assert [item["label"] for item in plan[:2]] == ["blockscout_chain_id", "publicnode_chain_id"]
    assert plan[2]["path"] == f"/api/v2/smart-contracts/{FROZEN_IMPLEMENTATIONS[0]['address']}"
    assert plan[9]["label"] == f"{FROZEN_CANDIDATE_IDS[0]}:old_implementation_code"
    assert plan[-1]["label"] == (
        f"{FROZEN_CANDIDATE_IDS[-1]}:lookback_{LOOKBACK_BLOCK_OFFSETS[-1]:06d}:totals_publicnode"
    )


def test_totals_collateral_decoder_enforces_shape_width_and_reserved_zero() -> None:
    value = "0x" + _word(123_456) + _word(0)

    assert decode_totals_collateral(value) == {"total_supply_asset": 123_456, "reserved": 0}
    with pytest.raises(ValueError, match="exactly two ABI words"):
        decode_totals_collateral("0x" + _word(123_456))
    with pytest.raises(ValueError, match="exceed uint128"):
        decode_totals_collateral("0x" + _word(2**128) + _word(0))
    with pytest.raises(ValueError, match="reserved field"):
        decode_totals_collateral("0x" + _word(123_456) + _word(1))


def test_verified_source_requires_bytecode_abi_and_enforcement_semantics() -> None:
    bytecode = b"\x60\x00"
    expected_hash = hashlib.sha256(bytecode).hexdigest()

    clean = normalize_verified_source(
        _source_metadata(bytecode),
        expected_address=ADDRESS,
        expected_code_sha256=expected_hash,
        maximum_files=10,
        maximum_bytes=100_000,
    )

    assert clean["fully_conforming_source"] is True
    assert clean["deployed_bytecode_sha256"] == expected_hash
    assert clean["source_file_count"] == 1
    assert all(clean["semantic_marker_checks"].values())
    assert clean["raw_source_retained"] is False

    changed = _source_metadata(bytecode)
    changed["is_changed_bytecode"] = True
    changed["source_code"] = "contract Comet {}"
    rejected = normalize_verified_source(
        changed,
        expected_address=ADDRESS,
        expected_code_sha256=expected_hash,
        maximum_files=10,
        maximum_bytes=100_000,
    )
    assert rejected["fully_conforming_source"] is False
    assert rejected["checks"]["bytecode_not_changed"] is False
    assert rejected["checks"]["all_enforcement_markers_present"] is False


def test_verified_source_rejects_duplicate_abi_keys_and_source_paths() -> None:
    metadata = _source_metadata()
    metadata["abi"] = '[{"type":"function","type":"event"}]'
    metadata["additional_sources"] = [
        {"file_path": metadata["file_path"], "source_code": "contract Duplicate {}"}
    ]

    result = normalize_verified_source(
        metadata,
        expected_address=ADDRESS,
        expected_code_sha256=hashlib.sha256(b"\x60\x00").hexdigest(),
        maximum_files=10,
        maximum_bytes=100_000,
    )

    assert result["fully_conforming_source"] is False
    assert any("duplicate file paths" in error for error in result["normalization_errors"])
    assert any("duplicate JSON key" in error for error in result["normalization_errors"])


def test_exact_saturation_is_confirmatory_and_near_cap_is_diagnostic_only() -> None:
    exact = _utilization_record(1_000, 1_000)
    near = _utilization_record(999, 1_000)
    slack = _utilization_record(899, 1_000)

    assert exact["exactly_saturated"] is True
    assert exact["headroom_raw_units"] == 0
    assert near["at_least_990000_ppm"] is True
    assert near["exactly_saturated"] is False
    assert slack["at_least_900000_ppm"] is False


def test_validator_rejects_account_access_candidate_replacement_and_threshold_drift() -> None:
    manifest = load_supply_cap_activation(MANIFEST_PATH)
    broken = deepcopy(manifest)
    broken["access_boundary"]["account_state_rows_opened"] = True
    broken["selection_contract"]["candidate_replacement_after_freeze"] = True
    broken["activation_contract"]["utilization_diagnostics_ppm"] = [800_000]
    broken["expected_request_contract"]["network_operation_count_without_retry"] = 140

    errors = validate_supply_cap_activation(broken)

    assert "access_boundary.account_state_rows_opened must be false" in errors
    assert "selection_contract differs from the frozen contract" in errors
    assert "activation_contract differs from the frozen contract" in errors
    assert "expected_request_contract differs from the frozen plan" in errors


def test_failure_artifact_is_bounded_and_never_a_scientific_decision() -> None:
    manifest = load_supply_cap_activation(MANIFEST_PATH)
    transport = build_http_transport(manifest)
    transport.http_attempts = 1
    transport.response_bytes = 19
    transport.records.append({"label": "blockscout_chain_id", "response_body_sha256": "a" * 64})
    transport.attempt_records.append(
        {"label": "blockscout_chain_id", "outcome": "success", "response_body_sha256": "a" * 64}
    )

    artifact = _failure_artifact(
        manifest=manifest,
        manifest_sha256="b" * 64,
        collection_commit="c" * 40,
        transport=transport,
        error=RuntimeError("x" * 2_100),
    )

    assert artifact["decision"] == "INFRASTRUCTURE_FAILURE_NO_SUPPLY_CAP_ACTIVATION_RESULT"
    assert artifact["scientific_gate_decision_reached"] is False
    assert artifact["authorized_next_stage"] is None
    assert artifact["successful_operation_count"] == 1
    assert artifact["http_attempt_count"] == artifact["http_attempt_record_count"] == 1
    assert len(artifact["exception"]["message"]) == 2_000
    assert artifact["exception"]["message_truncated"] is True
    assert "raw_response" not in artifact
