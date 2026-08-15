import json
from collections import Counter
from copy import deepcopy
from pathlib import Path

import pytest

import ecomd.research.compound_supply_cap_activation_v2 as activation_v2
from ecomd.research.compound_supply_cap_activation import (
    FROZEN_CANDIDATE_IDS,
    FROZEN_IMPLEMENTATIONS,
    load_supply_cap_activation,
)
from ecomd.research.compound_supply_cap_activation_v2 import (
    _failure_artifact,
    build_http_transport,
    derive_parent_candidates,
    expected_operation_plan,
    load_supply_cap_activation_v2,
    validate_parent_evidence_v2,
    validate_supply_cap_activation_v2,
)

MANIFEST_PATH = Path("data/manifests/compound_v3_supply_cap_activation_preflight_v2.yaml")
V1_MANIFEST_PATH = Path("data/manifests/compound_v3_supply_cap_activation_preflight_v1.yaml")


def _derived(manifest: dict[str, object]) -> list[dict[str, object]]:
    parents = manifest["parents"]
    assert isinstance(parents, dict)
    summary = json.loads(Path(parents["mechanics_summary_path"]).read_text(encoding="utf-8"))
    candidates = json.loads(Path(parents["mechanics_candidates_path"]).read_text(encoding="utf-8"))
    return derive_parent_candidates(summary, candidates)


def test_v2_overlay_parents_inheritance_and_exact_operation_plan() -> None:
    manifest = load_supply_cap_activation_v2(MANIFEST_PATH)
    v1 = load_supply_cap_activation(V1_MANIFEST_PATH)

    assert validate_supply_cap_activation_v2(manifest) == []
    assert validate_parent_evidence_v2(manifest, Path.cwd()) == []
    for key in ("parents", "selection_contract", "official_source_contract", "activation_contract"):
        assert manifest[key] == v1[key]
    derived = _derived(manifest)
    assert [item["candidate"]["candidate_id"] for item in derived] == list(FROZEN_CANDIDATE_IDS)
    assert manifest["official_source_contract"]["implementations"] == list(FROZEN_IMPLEMENTATIONS)
    plan = expected_operation_plan(manifest, derived)
    assert len(plan) == 105
    assert Counter(item["provider"] for item in plan) == {
        "blockscout": 73,
        "blockscout_smart_contract": 7,
        "publicnode_execution": 25,
    }
    assert Counter(item["method"] for item in plan if item["operation_type"] == "json_rpc") == {
        "eth_call": 48,
        "eth_chainId": 2,
        "eth_getBlockByNumber": 48,
    }
    assert plan[-1]["label"] == f"{FROZEN_CANDIDATE_IDS[-1]}:lookback_050400:totals_blockscout"


def test_publicnode_is_header_only_and_blockscout_is_only_state_provider() -> None:
    manifest = load_supply_cap_activation_v2(MANIFEST_PATH)
    plan = expected_operation_plan(manifest, _derived(manifest))

    publicnode_methods = [
        item["method"]
        for item in plan
        if item["operation_type"] == "json_rpc" and item["provider"] == "publicnode_execution"
    ]
    state_operations = [
        item for item in plan if item["operation_type"] == "json_rpc" and item["method"] == "eth_call"
    ]
    assert Counter(publicnode_methods) == {"eth_getBlockByNumber": 24, "eth_chainId": 1}
    assert {item["provider"] for item in state_operations} == {"blockscout"}
    assert all(item.get("method") != "eth_getCode" for item in plan)
    assert all("asset_info_post" not in item["label"] for item in plan)


def test_validator_rejects_archive_state_access_rule_and_plan_drift() -> None:
    manifest = load_supply_cap_activation_v2(MANIFEST_PATH)
    broken = deepcopy(manifest)
    broken["repair_contract"][
        "replace_publicnode_historical_state_with_blockscout_documented_historical_eth_call"
    ] = False
    broken["sources"]["publicnode_archive_state_used"] = True
    broken["access_boundary"]["cross_provider_historical_state_replication_performed"] = True
    broken["expected_request_contract"]["network_operation_count_without_retry"] = 106

    errors = validate_supply_cap_activation_v2(broken)

    assert "repair_contract differs from the frozen narrow repair" in errors
    assert "PublicNode archive state must remain disabled" in errors
    assert "access_boundary.cross_provider_historical_state_replication_performed must be false" in errors
    assert "expected_request_contract differs from the frozen v2 plan" in errors


def test_v2_failure_artifact_retains_completed_normalized_evidence_only() -> None:
    manifest = load_supply_cap_activation_v2(MANIFEST_PATH)
    transport = build_http_transport(manifest)
    transport.http_attempts = 1
    transport.response_bytes = 23
    transport.records.append({"label": "blockscout_chain_id", "response_body_sha256": "a" * 64})
    transport.attempt_records.append(
        {"label": "blockscout_chain_id", "outcome": "success", "response_body_sha256": "a" * 64}
    )
    source = {
        "address": FROZEN_IMPLEMENTATIONS[0]["address"],
        "fully_conforming_source": True,
        "raw_source_retained": False,
    }
    candidate = {
        "candidate": {"candidate_id": FROZEN_CANDIDATE_IDS[0]},
        "data_and_source_conforming": True,
    }

    artifact = _failure_artifact(
        manifest=manifest,
        manifest_sha256="b" * 64,
        collection_commit="c" * 40,
        transport=transport,
        completed_sources=[source],
        completed_candidates=[candidate],
        error=RuntimeError("later transport failure"),
    )

    partial = artifact["partial_normalized_evidence"]
    assert partial["completed_implementation_sources"] == [source]
    assert partial["completed_candidates"] == [candidate]
    assert partial["is_complete_scientific_result"] is False
    assert artifact["scientific_gate_decision_reached"] is False
    assert artifact["decision"] == "INFRASTRUCTURE_FAILURE_NO_SUPPLY_CAP_ACTIVATION_RESULT_V2"
    assert artifact["authorized_next_stage"] is None
    assert artifact["raw_response_payloads_retained"] is False
    assert "raw_response" not in artifact


def _word(value: int) -> str:
    return value.to_bytes(32, "big").hex()


def _address_word(address: str) -> str:
    return "00" * 12 + address[2:]


def _asset_info_result(info: dict[str, object]) -> str:
    return "0x" + "".join(
        [
            _word(info["offset"]),
            _address_word(info["asset"]),
            _address_word(info["price_feed"]),
            _word(info["scale"]),
            _word(info["borrow_collateral_factor"]),
            _word(info["liquidate_collateral_factor"]),
            _word(info["liquidation_factor"]),
            _word(info["supply_cap"]),
        ]
    )


class _FakeTransport:
    def __init__(self, derived: list[dict[str, object]]) -> None:
        self.records: list[dict[str, object]] = []
        self.attempt_records: list[dict[str, object]] = []
        self.http_attempts = 0
        self.response_bytes = 0
        self.by_id = {item["candidate"]["candidate_id"]: item for item in derived}

    def _record(
        self,
        *,
        operation_type: str,
        provider: str,
        label: str,
        method: str | None = None,
        params: list[object] | None = None,
        path: str | None = None,
    ) -> None:
        record: dict[str, object] = {
            "operation_index": len(self.records),
            "operation_type": operation_type,
            "provider": provider,
            "label": label,
            "attempt_count": 1,
        }
        if method is not None:
            record.update({"method": method, "params": params})
        else:
            record["path"] = path
        self.records.append(record)
        self.attempt_records.append(
            {
                "http_attempt_index": self.http_attempts,
                "operation_type": operation_type,
                "provider": provider,
                "label": label,
                "outcome": "success",
            }
        )
        self.http_attempts += 1

    def rpc_call(
        self,
        *,
        url: str,
        provider: str,
        label: str,
        method: str,
        params: list[object],
    ) -> object:
        del url
        self._record(
            operation_type="json_rpc",
            provider=provider,
            label=label,
            method=method,
            params=params,
        )
        if method == "eth_chainId":
            return "0x1"
        candidate_id = label.split(":", 1)[0]
        record = self.by_id[candidate_id]
        candidate = record["candidate"]
        event_header = record["event_header"]
        assert isinstance(candidate, dict)
        assert isinstance(event_header, dict)
        block = int(params[0], 16) if method == "eth_getBlockByNumber" else int(params[-1], 16)
        offset = candidate["block_number"] - block
        if method == "eth_getBlockByNumber":
            return {
                "number": hex(block),
                "hash": "0x" + f"{block:064x}",
                "timestamp": hex(event_header["timestamp_unix"] - offset * 12),
            }
        parent_pre = record["asset_info_pre"]
        assert isinstance(parent_pre, dict)
        if "asset_info" in label:
            return _asset_info_result(parent_pre)
        return "0x" + _word(parent_pre["supply_cap"]) + _word(0)

    def smart_contract_get(self, *, base_url: str, address: str, label: str) -> object:
        del base_url
        self._record(
            operation_type="blockscout_smart_contract_rest",
            provider="blockscout_smart_contract",
            label=label,
            path=f"/api/v2/smart-contracts/{address}",
        )
        return {}


def test_synthetic_complete_collection_reaches_exact_activation_pass(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest = load_supply_cap_activation_v2(MANIFEST_PATH)
    derived = _derived(manifest)
    fake = _FakeTransport(derived)

    def normalized_source(
        value: object,
        *,
        expected_address: str,
        expected_code_sha256: str,
        maximum_files: int,
        maximum_bytes: int,
    ) -> dict[str, object]:
        del value, maximum_files, maximum_bytes
        return {
            "address": expected_address,
            "name": "Comet",
            "compiler_version": "v0.8.15",
            "deployed_bytecode_sha256": expected_code_sha256,
            "source_file_count": 1,
            "source_text_byte_count": 1,
            "checks": {"synthetic": True},
            "fully_conforming_source": True,
        }

    monkeypatch.setattr(activation_v2, "normalize_verified_source", normalized_source)
    summary, evidence, http = activation_v2.collect_supply_cap_activation_v2(
        manifest,
        root=Path.cwd(),
        transport=fake,
    )

    assert summary["decision"] == "PASS_EXACT_CAP_ACTIVATION_AUTHORIZE_MARKET_LEVEL_D1B_DESIGN_ONLY"
    assert summary["candidate_summary"]["exact_t_minus_one_saturation_count"] == 4
    assert summary["integrity_gate_counts"] == {"pass": 10, "fail": 0}
    assert len(evidence["implementation_sources"]) == 7
    assert len(evidence["candidates"]) == 4
    assert len(http["successful_operations"]) == 105
