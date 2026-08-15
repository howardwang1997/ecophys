from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

PROTOCOL_COMMIT = "a9af33e9c1e519a1b670f5700bf627655ff053fa"
MANIFEST_SHA256 = "aca9d2af723a9644066a85f8ce0c98893a97463402574cdb04feb771944163f9"
EXPECTED_DECISION = "FAIL_NO_EXACT_T_MINUS_ONE_SATURATION_RETIRE_COMPOUND_M3_CAUSAL_ROUTE"
EXPECTED_ARTIFACT_SHA256 = {
    "summary": "e5f4ef20a3561d75cd8b13007fcd2b0e23e518c13aa20f7d0cd1fd4b1f5caa66",
    "candidates": "e452a2fcd00a238f5d44fb9b9c04eab294979fd93b3f6be2490f5845f26e5707",
    "http_evidence": "cf62cf400b243e9883e4d97d69d47b12339f2da2ee312a1437351a6cb03069ad",
}
OFFSETS = [1, 300, 1_800, 7_200, 21_600, 50_400]
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise AssertionError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def construct_mapping(loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    result: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise AssertionError(f"duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    construct_mapping,
)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_pairs)


def read_yaml(path: Path) -> dict[str, Any]:
    value = yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
    assert isinstance(value, dict), path
    return value


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def safe_path(root: Path, value: Any) -> Path:
    assert isinstance(value, str) and value
    relative = Path(value)
    assert not relative.is_absolute() and ".." not in relative.parts
    return root / relative


def project_operation(record: dict[str, Any]) -> dict[str, Any]:
    projected = {
        "operation_type": record["operation_type"],
        "provider": record["provider"],
        "label": record["label"],
    }
    if record["operation_type"] == "json_rpc":
        projected.update({"method": record["method"], "params": record["params"]})
    else:
        projected["path"] = record["path"]
    return projected


def build_plan(
    v2: dict[str, Any], scientific: dict[str, Any], candidates: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    plan: list[dict[str, Any]] = []

    def rpc(provider: str, label: str, method: str, params: list[Any]) -> None:
        plan.append(
            {
                "operation_type": "json_rpc",
                "provider": provider,
                "label": label,
                "method": method,
                "params": params,
            }
        )

    rpc("blockscout", "blockscout_chain_id", "eth_chainId", [])
    rpc("publicnode_execution", "publicnode_chain_id", "eth_chainId", [])
    template = v2["sources"]["allowed_rest_path_templates"][0]
    for implementation in scientific["official_source_contract"]["implementations"]:
        address = implementation["address"]
        path = template.format(address_hash=address)
        plan.append(
            {
                "operation_type": "blockscout_smart_contract_rest",
                "provider": "blockscout_smart_contract",
                "label": f"source:{address}",
                "path": path,
            }
        )
    asset_selector = scientific["official_source_contract"]["get_asset_info_selector"]
    totals_selector = scientific["official_source_contract"]["totals_collateral_selector"]
    for row in candidates:
        candidate = row["candidate"]
        candidate_id = candidate["candidate_id"]
        proxy = candidate["comet_proxy"]
        asset = candidate["asset"]
        suffix = ("00" * 12) + asset[2:]
        for offset in OFFSETS:
            block = candidate["block_number"] - offset
            label = f"{candidate_id}:lookback_{offset:06d}"
            rpc("blockscout", f"{label}:header_blockscout", "eth_getBlockByNumber", [hex(block), False])
            rpc(
                "publicnode_execution",
                f"{label}:header_publicnode",
                "eth_getBlockByNumber",
                [hex(block), False],
            )
            rpc(
                "blockscout",
                f"{label}:asset_info_blockscout",
                "eth_call",
                [{"to": proxy, "data": asset_selector + suffix}, hex(block)],
            )
            rpc(
                "blockscout",
                f"{label}:totals_blockscout",
                "eth_call",
                [{"to": proxy, "data": totals_selector + suffix}, hex(block)],
            )
    return plan


def verify(root: Path) -> dict[str, Any]:
    manifest_path = root / "data/manifests/compound_v3_supply_cap_activation_preflight_v2.yaml"
    assert sha256_file(manifest_path) == MANIFEST_SHA256
    v2 = read_yaml(manifest_path)
    base = v2["base_protocol"]
    v1_manifest_path = safe_path(root, base["manifest_path"])
    assert sha256_file(v1_manifest_path) == base["manifest_sha256"]
    scientific = read_yaml(v1_manifest_path)

    for path_key, hash_key in (
        ("result_path", "result_sha256"),
        ("failure_path", "failure_sha256"),
    ):
        path = safe_path(root, base[path_key])
        assert sha256_file(path) == base[hash_key]
    assert base["protocol_commit"] == "1dfdecf47d60b3f78a1076d2a09ed60f7ad5fc7f"
    v1_result = safe_path(root, base["result_path"]).read_text(encoding="utf-8")
    v1_failure = read_json(safe_path(root, base["failure_path"]))
    assert base["protocol_commit"] in v1_result and base["failure_decision"] in v1_result
    assert v1_failure["collection_commit"] == base["protocol_commit"]
    assert v1_failure["decision"] == base["failure_decision"]
    assert v1_failure["scientific_gate_decision_reached"] is False
    assert v1_failure["successful_operation_count"] == 9
    assert v1_failure["http_attempt_count"] == 12

    parents = scientific["parents"]
    for path_key, hash_key in (
        ("mechanics_manifest_path", "mechanics_manifest_sha256"),
        ("mechanics_result_path", "mechanics_result_sha256"),
        ("mechanics_summary_path", "mechanics_summary_sha256"),
        ("mechanics_candidates_path", "mechanics_candidates_sha256"),
        ("mechanics_http_evidence_path", "mechanics_http_evidence_sha256"),
        ("metadata_summary_path", "metadata_summary_sha256"),
    ):
        assert sha256_file(safe_path(root, parents[path_key])) == parents[hash_key]

    mechanics_summary = read_json(safe_path(root, parents["mechanics_summary_path"]))
    mechanics_rows = read_json(safe_path(root, parents["mechanics_candidates_path"]))
    survivor_ids = mechanics_summary["candidate_summary"]["fully_conforming_candidate_ids"]
    parent_by_id = {row["candidate"]["candidate_id"]: row for row in mechanics_rows}
    assert survivor_ids == [
        "supply_cap_16133171_5c9dacfa",
        "supply_cap_16520572_f626c068",
        "supply_cap_16549206_b96f2c61",
        "supply_cap_16668519_f803c13b",
    ]
    assert all(parent_by_id[candidate_id]["fully_conforming_candidate"] for candidate_id in survivor_ids)

    artifact_dir = root / "experiments/v14_compound_v3_supply_cap_activation_preflight/artifacts_v2"
    summary_path = artifact_dir / "summary.json"
    candidates_path = artifact_dir / "candidates.json"
    http_path = artifact_dir / "http_evidence.json"
    assert not (artifact_dir / "failure.json").exists()
    artifact_sha256 = {
        "summary": sha256_file(summary_path),
        "candidates": sha256_file(candidates_path),
        "http_evidence": sha256_file(http_path),
    }
    assert artifact_sha256 == EXPECTED_ARTIFACT_SHA256
    summary = read_json(summary_path)
    evidence = read_json(candidates_path)
    http = read_json(http_path)
    assert set(evidence) == {"implementation_sources", "candidates"}
    assert set(http) == {"successful_operations", "http_attempts"}
    candidates = evidence["candidates"]
    sources = evidence["implementation_sources"]

    assert summary["collection_commit"] == PROTOCOL_COMMIT
    assert summary["manifest_sha256"] == MANIFEST_SHA256
    assert summary["base_protocol"] == base
    assert summary["parents"] == parents
    assert summary["provider_chain_ids"] == {"blockscout": "0x1", "publicnode_execution": "0x1"}
    assert summary["historical_state_provider"] == "blockscout"
    assert summary["historical_state_provider_count"] == 1
    assert summary["cross_provider_historical_state_replication_performed"] is False
    assert summary["access_boundary"] == v2["access_boundary"]

    expected_implementations = scientific["official_source_contract"]["implementations"]
    assert [item["address"] for item in sources] == [item["address"] for item in expected_implementations]
    expected_code = {item["address"]: item["code_sha256"] for item in expected_implementations}
    required_markers = set(scientific["official_source_contract"]["required_normalized_source_markers"])
    total_files = 0
    total_text_bytes = 0
    for source in sources:
        assert source["deployed_bytecode_sha256"] == expected_code[source["address"]]
        assert source["expected_deployed_bytecode_sha256"] == expected_code[source["address"]]
        assert source["deployed_bytecode_byte_count"] > 0
        assert source["fully_conforming_source"] is True
        assert source["normalization_errors"] == [] and source["raw_source_retained"] is False
        assert all(source["checks"].values())
        assert set(source["semantic_marker_checks"]) == required_markers
        assert all(source["semantic_marker_checks"].values())
        inventory = source["source_file_inventory"]
        assert len(inventory) == source["source_file_count"]
        assert canonical_sha256(inventory) == source["source_file_inventory_sha256"]
        assert all(SHA256_RE.fullmatch(item["sha256"]) for item in inventory)
        assert sum(item["byte_count"] for item in inventory) == source["source_text_byte_count"]
        assert SHA256_RE.fullmatch(source["abi_canonical_sha256"])
        assert SHA256_RE.fullmatch(source["compiler_settings_sha256"])
        total_files += source["source_file_count"]
        total_text_bytes += source["source_text_byte_count"]
    source_summary = summary["implementation_source_summary"]
    assert source_summary["audited_count"] == len(sources) == 7
    assert source_summary["fully_conforming_count"] == 7
    assert source_summary["source_file_count"] == total_files
    assert source_summary["source_text_byte_count"] == total_text_bytes

    assert [row["candidate"]["candidate_id"] for row in candidates] == survivor_ids
    exact_t_minus_one: list[str] = []
    near_cap_diagnostics: list[dict[str, Any]] = []
    for row in candidates:
        candidate = row["candidate"]
        parent = parent_by_id[candidate["candidate_id"]]
        assert candidate == parent["candidate"]
        assert row["parent_asset_info_pre"] == parent["asset_info_pre"]
        assert row["parent_asset_info_post"] == parent["asset_info_post"]
        assert row["parent_proxy_state"] == parent["proxy_state"]
        assert row["source_implementation_addresses"] == {
            "old": parent["proxy_state"]["old_implementation"],
            "new": parent["proxy_state"]["new_implementation"],
        }
        assert candidate["old_value"] == row["parent_asset_info_pre"]["supply_cap"]
        assert candidate["new_value"] == row["parent_asset_info_post"]["supply_cap"]
        assert candidate["new_value"] > candidate["old_value"]
        snapshots = row["lookback_snapshots"]
        assert [snapshot["block_offset"] for snapshot in snapshots] == OFFSETS
        saturated_offsets: list[int] = []
        for snapshot in snapshots:
            offset = snapshot["block_offset"]
            assert snapshot["block_number"] == candidate["block_number"] - offset
            blockscout_header = snapshot["blockscout_header"]
            publicnode_header = snapshot["publicnode_header"]
            assert blockscout_header == publicnode_header
            assert blockscout_header["number"] == snapshot["block_number"]
            assert blockscout_header["timestamp_unix"] < row["event_header"]["timestamp_unix"]
            assert snapshot["elapsed_to_event_seconds"] == (
                row["event_header"]["timestamp_unix"] - blockscout_header["timestamp_unix"]
            )
            assert snapshot["cross_provider_header_agreement"] is True
            if offset == 1:
                assert blockscout_header["hash"] == row["event_header"]["parent_hash"]
                assert snapshot["asset_info_blockscout"] == row["parent_asset_info_pre"]
            asset_info = snapshot["asset_info_blockscout"]
            totals = snapshot["totals_collateral_blockscout"]
            utilization = snapshot["utilization"]
            assert asset_info["asset"] == candidate["asset"]
            assert totals["reserved"] == 0
            total = totals["total_supply_asset"]
            cap = asset_info["supply_cap"]
            assert 0 <= total <= cap and cap > 0
            assert utilization["numerator_total_supply_asset"] == total
            assert utilization["denominator_supply_cap"] == cap
            assert utilization["headroom_raw_units"] == cap - total
            assert utilization["utilization_ppm_floor"] == total * 1_000_000 // cap
            assert utilization["within_cap"] is True
            assert utilization["exactly_saturated"] is (total == cap)
            for threshold in scientific["activation_contract"]["utilization_diagnostics_ppm"]:
                assert utilization[f"at_least_{threshold}_ppm"] is (
                    utilization["utilization_ppm_floor"] >= threshold
                )
            if total == cap:
                saturated_offsets.append(offset)
        assert row["exactly_saturated_snapshot_offsets"] == saturated_offsets
        t_minus_one_exact = snapshots[0]["utilization"]["exactly_saturated"]
        assert row["exact_t_minus_one_saturation"] is t_minus_one_exact
        assert row["data_and_source_conforming"] is all(row["checks"].values())
        assert row["data_and_source_conforming"] is True
        if t_minus_one_exact:
            exact_t_minus_one.append(candidate["candidate_id"])
        t_minus_one = snapshots[0]
        near_cap_diagnostics.append(
            {
                "candidate_id": candidate["candidate_id"],
                "t_minus_one_utilization_ppm_floor": t_minus_one["utilization"]["utilization_ppm_floor"],
                "t_minus_one_headroom_raw_units": t_minus_one["utilization"]["headroom_raw_units"],
                "maximum_lookback_utilization_ppm_floor": max(
                    snapshot["utilization"]["utilization_ppm_floor"] for snapshot in snapshots
                ),
            }
        )

    candidate_summary = summary["candidate_summary"]
    assert candidate_summary["audited_count"] == 4
    assert candidate_summary["data_and_source_conforming_count"] == 4
    assert candidate_summary["exact_t_minus_one_saturation_candidate_ids"] == exact_t_minus_one == []
    assert candidate_summary["exact_t_minus_one_saturation_count"] == 0
    for record, row in zip(candidate_summary["records"], candidates, strict=True):
        candidate = row["candidate"]
        assert record == {
            "candidate_id": candidate["candidate_id"],
            "block_number": candidate["block_number"],
            "market_id": candidate["market_id"],
            "asset": candidate["asset"],
            "data_and_source_conforming": row["data_and_source_conforming"],
            "exact_t_minus_one_saturation": row["exact_t_minus_one_saturation"],
            "exactly_saturated_snapshot_offsets": row["exactly_saturated_snapshot_offsets"],
        }

    plan = build_plan(v2, scientific, candidates)
    operations = http["successful_operations"]
    attempts = http["http_attempts"]
    assert len(plan) == len(operations) == len(attempts) == 105
    assert [project_operation(record) for record in operations] == plan
    rpc_id = 0
    for index, (operation, attempt) in enumerate(zip(operations, attempts, strict=True)):
        assert operation["operation_index"] == index
        assert operation["attempt_count"] == 1 and operation["prior_errors"] == []
        assert attempt["http_attempt_index"] == index and attempt["logical_attempt"] == 1
        assert attempt["outcome"] == "success" and attempt["error"] is None
        assert attempt["http_status"] == 200
        for key in ("operation_type", "provider", "label", "request_sha256"):
            assert attempt[key] == operation[key]
        for key in ("response_body_sha256", "response_canonical_json_sha256", "response_byte_count"):
            assert attempt[key] == operation[key]
        assert operation["response_byte_count"] > 0
        assert SHA256_RE.fullmatch(operation["response_body_sha256"])
        assert SHA256_RE.fullmatch(operation["response_canonical_json_sha256"])
        if operation["operation_type"] == "json_rpc":
            rpc_id += 1
            request = {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "method": operation["method"],
                "params": operation["params"],
            }
        else:
            request = {
                "method": "GET",
                "url": v2["sources"]["blockscout_smart_contract_base_url"].rstrip("/") + operation["path"],
                "accept": "application/json",
            }
        assert canonical_sha256(request) == operation["request_sha256"]

    methods = Counter(
        operation["method"] for operation in operations if operation["operation_type"] == "json_rpc"
    )
    providers = Counter(operation["provider"] for operation in operations)
    assert dict(methods) == v2["expected_request_contract"]["method_counts"]
    assert dict(providers) == v2["expected_request_contract"]["provider_counts"]
    assert not any(
        operation["provider"] == "publicnode_execution"
        and operation.get("method") in {"eth_call", "eth_getCode"}
        for operation in operations
    )
    request_summary = summary["request_summary"]
    assert request_summary["successful_json_rpc_count"] == 98
    assert request_summary["successful_blockscout_smart_contract_count"] == 7
    assert request_summary["http_attempt_count"] == len(attempts)
    assert request_summary["http_attempt_record_count"] == len(attempts)
    assert request_summary["response_byte_count"] == sum(item["response_byte_count"] for item in attempts)
    assert request_summary["operation_order_matches_frozen_plan"] is True
    assert request_summary["all_one_attempt"] is True

    locks = v2["access_boundary"]
    assert locks["gpu_used"] is False and locks["paid_data_used"] is False
    assert locks["account_state_rows_opened"] is False
    assert locks["participant_action_rows_opened"] is False
    assert locks["post_event_aggregate_state_rows_opened"] is False
    gates = {
        "v1_failure_and_scientific_parents_reproduced": True,
        "ethereum_mainnet_provider_identity": summary["provider_chain_ids"]
        == {"blockscout": "0x1", "publicnode_execution": "0x1"},
        "all_historical_implementations_source_conform": all(
            source["fully_conforming_source"] for source in sources
        ),
        "cross_provider_lookback_block_headers_agree": all(
            snapshot["cross_provider_header_agreement"]
            for row in candidates
            for snapshot in row["lookback_snapshots"]
        ),
        "blockscout_historical_configuration_conforms": all(
            row["checks"]["t_minus_one_asset_info_matches_mechanics_parent"] for row in candidates
        ),
        "blockscout_aggregate_totals_within_contemporaneous_cap": all(
            snapshot["utilization"]["within_cap"]
            for row in candidates
            for snapshot in row["lookback_snapshots"]
        ),
        "all_candidates_evaluated": len(candidates) == 4,
        "exact_complete_request_plan": [project_operation(record) for record in operations] == plan,
        "request_and_source_resource_caps": len(attempts) <= v2["sources"]["maximum_http_attempts"]
        and request_summary["response_byte_count"] <= v2["sources"]["maximum_response_bytes"]
        and total_files <= v2["sources"]["maximum_verified_source_files"]
        and total_text_bytes <= v2["sources"]["maximum_verified_source_text_bytes"],
        "zero_account_and_response_access_boundary": all(
            locks[key] is False
            for key in (
                "account_state_rows_opened",
                "participant_action_rows_opened",
                "participant_call_trace_rows_opened",
                "liquidation_rows_opened",
                "price_or_oracle_rows_opened",
                "post_event_aggregate_state_rows_opened",
                "realized_response_rows_opened",
                "paid_data_used",
                "external_workers_used",
                "gpu_used",
            )
        ),
    }
    assert gates == summary["integrity_gates"] and all(gates.values())
    assert summary["integrity_gate_counts"] == {"pass": 10, "fail": 0}
    assert summary["decision"] == EXPECTED_DECISION
    assert summary["authorized_next_stage"] is None
    assert summary["account_level_estimand_disposition"] == (
        "RETIRE_ACCOUNT_LEVEL_M3_FOR_SUPPLY_CAP_EVENTS_UNOBSERVABLE_TREATED_COHORT"
    )

    return {
        "decision": summary["decision"],
        "artifact_sha256": artifact_sha256,
        "candidate_count": len(candidates),
        "exact_t_minus_one_saturation_count": len(exact_t_minus_one),
        "integrity_gates_passed": sum(gates.values()),
        "network_operations": len(operations),
        "http_attempts": len(attempts),
        "response_byte_count": request_summary["response_byte_count"],
        "near_cap_diagnostics": near_cap_diagnostics,
        "offline_replay_boundary": (
            "request, parent, normalized-evidence, header, state-arithmetic and decision consistency verified; "
            "raw HTTP bodies were intentionally not retained, so raw-response-to-normalized-source/state parsing "
            "cannot be replayed offline"
        ),
    }


if __name__ == "__main__":
    repository = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    print(json.dumps(verify(repository), indent=2, sort_keys=True))
