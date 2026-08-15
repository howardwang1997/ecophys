"""Transport-repaired zero-account activation audit for Compound III supply-cap events."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter
from collections.abc import Mapping, Sequence
from copy import deepcopy
from pathlib import Path
from typing import cast

import yaml

from ecomd.research.compound_candidate_mechanics import decode_asset_info
from ecomd.research.compound_supply_cap_activation import (
    GET_ASSET_INFO_SELECTOR,
    LOOKBACK_BLOCK_OFFSETS,
    SMART_CONTRACT_PATH_TEMPLATE,
    TOTALS_COLLATERAL_SELECTOR,
    SupplyCapTransport,
    _address_call,
    _block_header,
    _mapping,
    _read_json_mapping,
    _read_json_mapping_list,
    _safe_relative_path,
    _strings,
    _utilization_record,
    decode_totals_collateral,
    derive_parent_candidates,
    load_supply_cap_activation,
    normalize_verified_source,
)
from ecomd.research.compound_supply_cap_activation import (
    validate_parent_evidence as validate_v1_scientific_parents,
)
from ecomd.research.compound_supply_cap_activation import (
    validate_supply_cap_activation as validate_v1_manifest,
)

SCHEMA_VERSION = "ecophys-compound-v3-supply-cap-activation-preflight/v2"
ARTIFACT_SCHEMA_VERSION = "ecophys-compound-v3-supply-cap-activation-audit/v2"
FAILURE_SCHEMA_VERSION = "ecophys-compound-v3-supply-cap-activation-failure/v2"
AUDIT_ID = "compound_v3_mainnet_supply_cap_activation_preflight_v2"
AS_OF = "2026-08-16"
STAGE = "verified_source_blockscout_historical_state_cross_provider_headers_only"
BASE_PROTOCOL = {
    "manifest_path": "data/manifests/compound_v3_supply_cap_activation_preflight_v1.yaml",
    "manifest_sha256": "aac34fd0b8bb1d3e1f63b12fb0230f10039a0d2d7019bf8ea461d433cb5b3037",
    "protocol_commit": "1dfdecf47d60b3f78a1076d2a09ed60f7ad5fc7f",
    "result_path": "experiments/v14_compound_v3_supply_cap_activation_preflight/RESULTS_V1.md",
    "result_sha256": "baf1d606ac535388e6ff53dd3f3f8c54fe3abce0b21400465a937792c513c119",
    "result_commit": "74b8a3767748ffd508c9d1be5255aa26145b71da",
    "failure_path": ("experiments/v14_compound_v3_supply_cap_activation_preflight/artifacts/failure.json"),
    "failure_sha256": "225266d3fb1e394f0714ceed60000ca42c84476ac8bd1641b4eacb8da30c40c8",
    "failure_decision": "INFRASTRUCTURE_FAILURE_NO_SUPPLY_CAP_ACTIVATION_RESULT",
}
REPAIR_CONTRACT = {
    "replace_publicnode_historical_state_with_blockscout_documented_historical_eth_call": True,
    "retain_publicnode_for_cross_provider_historical_block_headers": True,
    "remove_redundant_publicnode_implementation_code_reads": True,
    "remove_redundant_post_event_configuration_read": True,
    "persist_completed_normalized_source_and_candidate_evidence_on_failure": True,
    "four_candidates_source_semantics_lookbacks_activation_rules_unchanged": True,
    "account_participant_price_and_response_access_unchanged_locked": True,
    "no_candidate_capability_probe_before_protocol_commit": True,
    "endpoint_substitution_after_v2_freeze": False,
}
ACCESS_TRUE = frozenset(
    {
        "mechanics_parent_opened",
        "v1_failure_parent_opened",
        "chain_rpc_used",
        "verified_contract_source_metadata_opened",
        "cross_provider_historical_block_headers_opened",
        "parent_implementation_code_hashes_opened",
        "blockscout_historical_configuration_getter_rows_opened",
        "blockscout_historical_aggregate_market_collateral_state_rows_opened",
    }
)
ACCESS_FALSE = frozenset(
    {
        "new_implementation_code_rows_opened",
        "cross_provider_historical_state_replication_performed",
        "new_governance_transaction_or_receipt_rows_opened",
        "new_log_or_call_trace_rows_opened",
        "account_state_rows_opened",
        "participant_action_rows_opened",
        "participant_call_trace_rows_opened",
        "liquidation_rows_opened",
        "price_or_oracle_rows_opened",
        "post_event_aggregate_state_rows_opened",
        "realized_response_rows_opened",
        "raw_source_or_rpc_payloads_retained",
        "paid_data_used",
        "external_workers_used",
        "gpu_used",
    }
)
REQUIRED_INTEGRITY_GATES = frozenset(
    {
        "v1_failure_and_scientific_parents_reproduced",
        "ethereum_mainnet_provider_identity",
        "all_historical_implementations_source_conform",
        "cross_provider_lookback_block_headers_agree",
        "blockscout_historical_configuration_conforms",
        "blockscout_aggregate_totals_within_contemporaneous_cap",
        "all_candidates_evaluated",
        "exact_complete_request_plan",
        "request_and_source_resource_caps",
        "zero_account_and_response_access_boundary",
    }
)
OVERLAY_TOP_LEVEL_KEYS = frozenset(
    {
        "schema_version",
        "audit_id",
        "as_of",
        "stage",
        "base_protocol",
        "repair_contract",
        "access_boundary",
        "sources",
        "expected_request_contract",
        "failure_artifact_contract",
        "integrity_gates",
        "decision_policy",
        "limitations",
    }
)
MATERIALIZED_TOP_LEVEL_KEYS = frozenset(
    {
        "schema_version",
        "audit_id",
        "as_of",
        "stage",
        "base_protocol",
        "repair_contract",
        "parents",
        "access_boundary",
        "sources",
        "selection_contract",
        "official_source_contract",
        "activation_contract",
        "expected_request_contract",
        "failure_artifact_contract",
        "integrity_gates",
        "decision_policy",
        "limitations",
    }
)


def load_supply_cap_activation_v2(path: str | Path) -> dict[str, object]:
    """Materialize the v2 transport overlay over the hash-pinned v1 scientific base."""

    overlay_path = Path(path)
    value: object = yaml.safe_load(overlay_path.read_text(encoding="utf-8"))
    overlay = _mapping(value)
    if overlay is None or set(overlay) != OVERLAY_TOP_LEVEL_KEYS:
        raise ValueError("v2 overlay has invalid top-level structure")
    base_protocol = _mapping(overlay.get("base_protocol"))
    if base_protocol is None or dict(base_protocol) != BASE_PROTOCOL:
        raise ValueError("v2 base protocol differs from the frozen failure parent")
    base_path_value = base_protocol["manifest_path"]
    if not _safe_relative_path(base_path_value):
        raise ValueError("v1 manifest path is unsafe")
    base_path = Path(cast(str, base_path_value))
    if not base_path.is_file():
        raise ValueError("v1 manifest is missing")
    if hashlib.sha256(base_path.read_bytes()).hexdigest() != base_protocol["manifest_sha256"]:
        raise ValueError("v1 manifest hash differs from the frozen value")
    base = load_supply_cap_activation(base_path)
    base_errors = validate_v1_manifest(base)
    if base_errors:
        raise ValueError("v1 scientific base is invalid: " + "; ".join(base_errors))
    materialized = deepcopy(base)
    for key in (
        "schema_version",
        "audit_id",
        "as_of",
        "stage",
        "access_boundary",
        "sources",
        "expected_request_contract",
        "failure_artifact_contract",
        "integrity_gates",
        "decision_policy",
        "limitations",
    ):
        materialized[key] = deepcopy(overlay[key])
    materialized["base_protocol"] = deepcopy(overlay["base_protocol"])
    materialized["repair_contract"] = deepcopy(overlay["repair_contract"])
    return materialized


def validate_supply_cap_activation_v2(manifest: Mapping[str, object]) -> list[str]:
    """Validate v2 while proving all outcome-relevant v1 fields are inherited unchanged."""

    errors: list[str] = []
    if set(manifest) != MATERIALIZED_TOP_LEVEL_KEYS:
        errors.append("materialized v2 top-level keys differ from the frozen contract")
    for key, expected in (
        ("schema_version", SCHEMA_VERSION),
        ("audit_id", AUDIT_ID),
        ("as_of", AS_OF),
        ("stage", STAGE),
    ):
        if manifest.get(key) != expected:
            errors.append(f"{key} differs from the frozen v2 value")
    base_protocol = _mapping(manifest.get("base_protocol"))
    if base_protocol is None or dict(base_protocol) != BASE_PROTOCOL:
        errors.append("base_protocol differs from the frozen v1 parent")
    repair = _mapping(manifest.get("repair_contract"))
    if repair is None or dict(repair) != REPAIR_CONTRACT:
        errors.append("repair_contract differs from the frozen narrow repair")
    access = _mapping(manifest.get("access_boundary"))
    if access is None:
        errors.append("access_boundary must be a mapping")
    else:
        if set(access) != ACCESS_TRUE | ACCESS_FALSE:
            errors.append("v2 access_boundary keys differ from the frozen contract")
        for key in ACCESS_TRUE:
            if access.get(key) is not True:
                errors.append(f"access_boundary.{key} must be true")
        for key in ACCESS_FALSE:
            if access.get(key) is not False:
                errors.append(f"access_boundary.{key} must be false")
    sources = _mapping(manifest.get("sources"))
    if sources is None:
        errors.append("sources must be a mapping")
    else:
        if sources.get("maximum_requests_per_second_across_sources") != 1:
            errors.append("global request rate must equal one per second")
        if sources.get("maximum_transport_retries") != 2:
            errors.append("transport retry count must equal two")
        for key in (
            "maximum_http_attempts",
            "maximum_response_bytes",
            "maximum_verified_source_files",
            "maximum_verified_source_text_bytes",
        ):
            item = sources.get(key)
            if not isinstance(item, int) or isinstance(item, bool) or item <= 0:
                errors.append(f"sources.{key} must be a positive integer")
        if sources.get("publicnode_archive_state_used") is not False:
            errors.append("PublicNode archive state must remain disabled")
        if sources.get("blockscout_is_only_historical_state_provider") is not True:
            errors.append("Blockscout must be declared the only historical state provider")
        if sources.get("raw_response_payloads_retained") is not False:
            errors.append("raw response retention must be false")
        if sources.get("endpoint_substitution_after_freeze") is not False:
            errors.append("endpoint substitution after freeze must be false")
        if sources.get("allowed_rpc_methods") != [
            "eth_chainId",
            "eth_getBlockByNumber",
            "eth_call",
        ]:
            errors.append("allowed RPC methods differ from the v2 transport boundary")
    expected_requests = {
        "candidate_count": 4,
        "unique_implementation_count": 7,
        "lookback_snapshot_count_per_candidate": 6,
        "json_rpc_success_count_without_retry": 98,
        "blockscout_smart_contract_success_count_without_retry": 7,
        "network_operation_count_without_retry": 105,
        "method_counts": {
            "eth_call": 48,
            "eth_chainId": 2,
            "eth_getBlockByNumber": 48,
        },
        "rest_path_template_counts": {SMART_CONTRACT_PATH_TEMPLATE: 7},
        "provider_counts": {
            "blockscout": 73,
            "blockscout_smart_contract": 7,
            "publicnode_execution": 25,
        },
    }
    requests = _mapping(manifest.get("expected_request_contract"))
    if requests is None or dict(requests) != expected_requests:
        errors.append("expected_request_contract differs from the frozen v2 plan")
    failure = _mapping(manifest.get("failure_artifact_contract"))
    if failure is None or failure.get("schema_version") != FAILURE_SCHEMA_VERSION:
        errors.append("failure artifact schema differs from v2")
    elif failure.get("persist_completed_normalized_evidence") is not True:
        errors.append("v2 failure artifact must persist completed normalized evidence")
    gates = _strings(manifest.get("integrity_gates"))
    if (
        gates is None
        or frozenset(gates) != REQUIRED_INTEGRITY_GATES
        or len(gates) != len(REQUIRED_INTEGRITY_GATES)
    ):
        errors.append("integrity_gates differ from the frozen v2 contract")
    expected_policy = {
        "integrity_gates_all_required": True,
        "pass": "PASS_EXACT_CAP_ACTIVATION_AUTHORIZE_MARKET_LEVEL_D1B_DESIGN_ONLY",
        "fail_no_activation": ("FAIL_NO_EXACT_T_MINUS_ONE_SATURATION_RETIRE_COMPOUND_M3_CAUSAL_ROUTE"),
        "fail_conformance": "FAIL_SOURCE_OR_STATE_CONFORMANCE_KEEP_ALL_D1_ROWS_LOCKED",
        "infrastructure_failure": "INFRASTRUCTURE_FAILURE_NO_SUPPLY_CAP_ACTIVATION_RESULT_V2",
        "authorized_next_stage": ("separately_frozen_market_level_collateral_flow_d1b_protocol_design_only"),
    }
    policy = _mapping(manifest.get("decision_policy"))
    if policy is None or dict(policy) != expected_policy:
        errors.append("decision_policy differs from the frozen v2 contract")
    limitations = _strings(manifest.get("limitations"))
    if limitations is None or not limitations:
        errors.append("limitations must be a nonempty string list")
    return sorted(errors)


def validate_parent_evidence_v2(manifest: Mapping[str, object], root: str | Path) -> list[str]:
    """Verify v1 failure/result hashes plus the unchanged D0b/source scientific ancestry."""

    errors: list[str] = []
    root_path = Path(root)
    base_protocol = cast(Mapping[str, object], manifest["base_protocol"])
    for path_key, hash_key in (
        ("manifest_path", "manifest_sha256"),
        ("result_path", "result_sha256"),
        ("failure_path", "failure_sha256"),
    ):
        relative = base_protocol.get(path_key)
        if not _safe_relative_path(relative):
            errors.append(f"base protocol {path_key} is unsafe")
            continue
        path = root_path / cast(str, relative)
        if not path.is_file():
            errors.append(f"base protocol {path_key} is missing")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != base_protocol.get(hash_key):
            errors.append(f"base protocol {path_key} hash differs")
    if errors:
        return sorted(errors)
    base_manifest = load_supply_cap_activation(root_path / cast(str, base_protocol["manifest_path"]))
    for key in ("parents", "selection_contract", "official_source_contract", "activation_contract"):
        if manifest.get(key) != base_manifest.get(key):
            errors.append(f"v2 changed inherited scientific field: {key}")
    errors.extend(validate_v1_scientific_parents(base_manifest, root_path))
    result_text = (root_path / cast(str, base_protocol["result_path"])).read_text(encoding="utf-8")
    failure = _read_json_mapping(root_path / cast(str, base_protocol["failure_path"]))
    if (
        cast(str, base_protocol["protocol_commit"]) not in result_text
        or cast(str, base_protocol["failure_decision"]) not in result_text
    ):
        errors.append("v1 result does not identify the frozen protocol failure")
    if failure.get("decision") != base_protocol["failure_decision"]:
        errors.append("v1 failure artifact decision differs")
    if failure.get("collection_commit") != base_protocol["protocol_commit"]:
        errors.append("v1 failure artifact collection commit differs")
    if failure.get("scientific_gate_decision_reached") is not False:
        errors.append("v1 failure incorrectly records a scientific decision")
    if failure.get("successful_operation_count") != 9 or failure.get("http_attempt_count") != 12:
        errors.append("v1 failure operation/attempt counts differ")
    return sorted(set(errors))


def build_http_transport(manifest: Mapping[str, object]) -> SupplyCapTransport:
    """Construct the one globally rate-limited v2 transport."""

    sources = cast(Mapping[str, object], manifest["sources"])
    return SupplyCapTransport(
        user_agent=cast(str, sources["user_agent"]),
        maximum_requests_per_second=float(cast(int, sources["maximum_requests_per_second_across_sources"])),
        maximum_transport_retries=cast(int, sources["maximum_transport_retries"]),
        maximum_http_attempts=cast(int, sources["maximum_http_attempts"]),
        maximum_response_bytes=cast(int, sources["maximum_response_bytes"]),
    )


def expected_operation_plan(
    manifest: Mapping[str, object], candidates: Sequence[Mapping[str, object]]
) -> list[dict[str, object]]:
    """Build the exact v2 vector with Blockscout state and two-provider headers."""

    plan: list[dict[str, object]] = []

    def rpc(provider: str, label: str, method: str, params: Sequence[object]) -> None:
        plan.append(
            {
                "operation_type": "json_rpc",
                "provider": provider,
                "label": label,
                "method": method,
                "params": list(params),
            }
        )

    rpc("blockscout", "blockscout_chain_id", "eth_chainId", [])
    rpc("publicnode_execution", "publicnode_chain_id", "eth_chainId", [])
    official = cast(Mapping[str, object], manifest["official_source_contract"])
    for item in cast(Sequence[Mapping[str, object]], official["implementations"]):
        address = cast(str, item["address"])
        plan.append(
            {
                "operation_type": "blockscout_smart_contract_rest",
                "provider": "blockscout_smart_contract",
                "label": f"source:{address}",
                "path": SMART_CONTRACT_PATH_TEMPLATE.format(address_hash=address),
            }
        )
    for record in candidates:
        candidate = cast(Mapping[str, object], record["candidate"])
        candidate_id = cast(str, candidate["candidate_id"])
        event_block = cast(int, candidate["block_number"])
        proxy = cast(str, candidate["comet_proxy"])
        asset = cast(str, candidate["asset"])
        asset_call = {"to": proxy, "data": _address_call(GET_ASSET_INFO_SELECTOR, asset)}
        totals_call = {"to": proxy, "data": _address_call(TOTALS_COLLATERAL_SELECTOR, asset)}
        for offset in LOOKBACK_BLOCK_OFFSETS:
            block = event_block - offset
            label = f"{candidate_id}:lookback_{offset:06d}"
            rpc(
                "blockscout",
                f"{label}:header_blockscout",
                "eth_getBlockByNumber",
                [hex(block), False],
            )
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
                [asset_call, hex(block)],
            )
            rpc(
                "blockscout",
                f"{label}:totals_blockscout",
                "eth_call",
                [totals_call, hex(block)],
            )
    return plan


def _observed_operation_plan(records: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    plan: list[dict[str, object]] = []
    for record in records:
        projected = {
            "operation_type": record["operation_type"],
            "provider": record["provider"],
            "label": record["label"],
        }
        if record["operation_type"] == "json_rpc":
            projected.update({"method": record["method"], "params": record["params"]})
        else:
            projected["path"] = record["path"]
        plan.append(projected)
    return plan


def collect_supply_cap_activation_v2(
    manifest: Mapping[str, object],
    *,
    root: str | Path = ".",
    transport: SupplyCapTransport | None = None,
    completed_sources: list[dict[str, object]] | None = None,
    completed_candidates: list[dict[str, object]] | None = None,
) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    """Execute the narrow v2 repair while retaining zero participant rows."""

    errors = validate_supply_cap_activation_v2(manifest)
    errors.extend(validate_parent_evidence_v2(manifest, root))
    if errors:
        raise ValueError("invalid v2 supply-cap activation manifest: " + "; ".join(sorted(set(errors))))
    root_path = Path(root)
    parents = cast(Mapping[str, object], manifest["parents"])
    parent_summary = _read_json_mapping(root_path / cast(str, parents["mechanics_summary_path"]))
    parent_rows = _read_json_mapping_list(root_path / cast(str, parents["mechanics_candidates_path"]))
    candidates = derive_parent_candidates(parent_summary, parent_rows)
    if transport is None:
        transport = build_http_transport(manifest)
    if completed_sources is None:
        completed_sources = []
    if completed_candidates is None:
        completed_candidates = []
    sources = cast(Mapping[str, object], manifest["sources"])
    official = cast(Mapping[str, object], manifest["official_source_contract"])
    blockscout_url = cast(str, sources["blockscout_rpc_url"])
    publicnode_url = cast(str, sources["publicnode_rpc_url"])
    blockscout_rest_url = cast(str, sources["blockscout_smart_contract_base_url"])
    blockscout_chain_id = transport.rpc_call(
        url=blockscout_url,
        provider="blockscout",
        label="blockscout_chain_id",
        method="eth_chainId",
        params=[],
    )
    publicnode_chain_id = transport.rpc_call(
        url=publicnode_url,
        provider="publicnode_execution",
        label="publicnode_chain_id",
        method="eth_chainId",
        params=[],
    )
    source_by_address: dict[str, Mapping[str, object]] = {}
    maximum_source_files = cast(int, sources["maximum_verified_source_files"])
    maximum_source_bytes = cast(int, sources["maximum_verified_source_text_bytes"])
    for item in cast(Sequence[Mapping[str, object]], official["implementations"]):
        address = cast(str, item["address"])
        normalized = normalize_verified_source(
            transport.smart_contract_get(
                base_url=blockscout_rest_url,
                address=address,
                label=f"source:{address}",
            ),
            expected_address=address,
            expected_code_sha256=cast(str, item["code_sha256"]),
            maximum_files=maximum_source_files,
            maximum_bytes=maximum_source_bytes,
        )
        completed_sources.append(normalized)
        source_by_address[address] = normalized

    for record in candidates:
        candidate = cast(Mapping[str, object], record["candidate"])
        proxy_state = cast(Mapping[str, object], record["proxy_state"])
        parent_pre = cast(Mapping[str, object], record["asset_info_pre"])
        parent_post = cast(Mapping[str, object], record["asset_info_post"])
        event_header = cast(Mapping[str, object], record["event_header"])
        candidate_id = cast(str, candidate["candidate_id"])
        event_block = cast(int, candidate["block_number"])
        proxy = cast(str, candidate["comet_proxy"])
        asset = cast(str, candidate["asset"])
        old_address = cast(str, proxy_state["old_implementation"])
        new_address = cast(str, proxy_state["new_implementation"])
        asset_call = {"to": proxy, "data": _address_call(GET_ASSET_INFO_SELECTOR, asset)}
        totals_call = {"to": proxy, "data": _address_call(TOTALS_COLLATERAL_SELECTOR, asset)}
        snapshots: list[dict[str, object]] = []
        for offset in LOOKBACK_BLOCK_OFFSETS:
            block = event_block - offset
            label = f"{candidate_id}:lookback_{offset:06d}"
            blockscout_header = _block_header(
                transport.rpc_call(
                    url=blockscout_url,
                    provider="blockscout",
                    label=f"{label}:header_blockscout",
                    method="eth_getBlockByNumber",
                    params=[hex(block), False],
                ),
                expected_number=block,
                path=f"{label}:header_blockscout",
            )
            publicnode_header = _block_header(
                transport.rpc_call(
                    url=publicnode_url,
                    provider="publicnode_execution",
                    label=f"{label}:header_publicnode",
                    method="eth_getBlockByNumber",
                    params=[hex(block), False],
                ),
                expected_number=block,
                path=f"{label}:header_publicnode",
            )
            asset_info = decode_asset_info(
                transport.rpc_call(
                    url=blockscout_url,
                    provider="blockscout",
                    label=f"{label}:asset_info_blockscout",
                    method="eth_call",
                    params=[asset_call, hex(block)],
                ),
                expected_asset=asset,
            )
            totals = decode_totals_collateral(
                transport.rpc_call(
                    url=blockscout_url,
                    provider="blockscout",
                    label=f"{label}:totals_blockscout",
                    method="eth_call",
                    params=[totals_call, hex(block)],
                )
            )
            utilization = _utilization_record(
                totals["total_supply_asset"], cast(int, asset_info["supply_cap"])
            )
            snapshots.append(
                {
                    "block_offset": offset,
                    "block_number": block,
                    "blockscout_header": blockscout_header,
                    "publicnode_header": publicnode_header,
                    "cross_provider_header_agreement": blockscout_header == publicnode_header,
                    "elapsed_to_event_seconds": cast(int, event_header["timestamp_unix"])
                    - cast(int, blockscout_header["timestamp_unix"]),
                    "asset_info_blockscout": asset_info,
                    "totals_collateral_blockscout": totals,
                    "utilization": utilization,
                }
            )
        immediate = snapshots[0]
        immediate_utilization = cast(Mapping[str, object], immediate["utilization"])
        checks = {
            "old_and_new_verified_source_conform": source_by_address[old_address]["fully_conforming_source"]
            is True
            and source_by_address[new_address]["fully_conforming_source"] is True,
            "all_cross_provider_headers_agree": all(
                item["cross_provider_header_agreement"] is True for item in snapshots
            ),
            "all_snapshot_headers_precede_event": all(
                cast(int, item["elapsed_to_event_seconds"]) > 0 for item in snapshots
            ),
            "all_snapshot_totals_within_contemporaneous_cap": all(
                cast(Mapping[str, object], item["utilization"])["within_cap"] is True for item in snapshots
            ),
            "t_minus_one_asset_info_matches_mechanics_parent": immediate["asset_info_blockscout"]
            == parent_pre,
            "parent_post_asset_info_matches_declared_new_cap": parent_post["supply_cap"]
            == candidate["new_value"],
            "strict_cap_increase": cast(int, candidate["new_value"]) > cast(int, candidate["old_value"]),
        }
        completed_candidates.append(
            {
                "candidate": dict(candidate),
                "event_header": dict(event_header),
                "parent_asset_info_pre": dict(parent_pre),
                "parent_asset_info_post": dict(parent_post),
                "parent_proxy_state": dict(proxy_state),
                "source_implementation_addresses": {"old": old_address, "new": new_address},
                "lookback_snapshots": snapshots,
                "checks": checks,
                "data_and_source_conforming": all(checks.values()),
                "exact_t_minus_one_saturation": immediate_utilization["exactly_saturated"] is True,
                "exactly_saturated_snapshot_offsets": [
                    item["block_offset"]
                    for item in snapshots
                    if cast(Mapping[str, object], item["utilization"])["exactly_saturated"] is True
                ],
                "account_level_estimand_disposition": (
                    "RETIRE_ACCOUNT_LEVEL_M3_FOR_SUPPLY_CAP_EVENTS_UNOBSERVABLE_TREATED_COHORT"
                ),
            }
        )

    rpc_records = [item for item in transport.records if item["operation_type"] == "json_rpc"]
    source_http_records = [
        item for item in transport.records if item["operation_type"] == "blockscout_smart_contract_rest"
    ]
    method_counts = dict(sorted(Counter(cast(str, item["method"]) for item in rpc_records).items()))
    provider_counts = dict(sorted(Counter(cast(str, item["provider"]) for item in transport.records).items()))
    expected = cast(Mapping[str, object], manifest["expected_request_contract"])
    expected_plan = expected_operation_plan(manifest, candidates)
    operation_order_matches = _observed_operation_plan(transport.records) == expected_plan
    exact_requests = (
        len(rpc_records) == expected["json_rpc_success_count_without_retry"]
        and len(source_http_records) == expected["blockscout_smart_contract_success_count_without_retry"]
        and len(transport.records) == expected["network_operation_count_without_retry"]
        and method_counts == expected["method_counts"]
        and {SMART_CONTRACT_PATH_TEMPLATE: len(source_http_records)} == expected["rest_path_template_counts"]
        and provider_counts == expected["provider_counts"]
        and operation_order_matches
        and len(transport.attempt_records) == transport.http_attempts
    )
    access = cast(Mapping[str, object], manifest["access_boundary"])
    access_ok = all(access.get(key) is True for key in ACCESS_TRUE) and all(
        access.get(key) is False for key in ACCESS_FALSE
    )
    total_source_files = sum(cast(int, item["source_file_count"]) for item in completed_sources)
    total_source_text_bytes = sum(cast(int, item["source_text_byte_count"]) for item in completed_sources)
    integrity_gates = {
        "v1_failure_and_scientific_parents_reproduced": True,
        "ethereum_mainnet_provider_identity": blockscout_chain_id == publicnode_chain_id == "0x1",
        "all_historical_implementations_source_conform": all(
            item["fully_conforming_source"] is True for item in completed_sources
        ),
        "cross_provider_lookback_block_headers_agree": all(
            cast(Mapping[str, object], item["checks"])["all_cross_provider_headers_agree"] is True
            for item in completed_candidates
        ),
        "blockscout_historical_configuration_conforms": all(
            cast(Mapping[str, object], item["checks"])["t_minus_one_asset_info_matches_mechanics_parent"]
            is True
            and cast(Mapping[str, object], item["checks"])["parent_post_asset_info_matches_declared_new_cap"]
            is True
            for item in completed_candidates
        ),
        "blockscout_aggregate_totals_within_contemporaneous_cap": all(
            cast(Mapping[str, object], item["checks"])["all_snapshot_totals_within_contemporaneous_cap"]
            is True
            for item in completed_candidates
        ),
        "all_candidates_evaluated": len(completed_candidates) == 4
        and all(item["data_and_source_conforming"] is True for item in completed_candidates),
        "exact_complete_request_plan": exact_requests,
        "request_and_source_resource_caps": transport.http_attempts
        <= cast(int, sources["maximum_http_attempts"])
        and transport.response_bytes <= cast(int, sources["maximum_response_bytes"])
        and total_source_files <= cast(int, sources["maximum_verified_source_files"])
        and total_source_text_bytes <= cast(int, sources["maximum_verified_source_text_bytes"]),
        "zero_account_and_response_access_boundary": access_ok,
    }
    integrity_pass = set(integrity_gates) == set(cast(Sequence[str], manifest["integrity_gates"])) and all(
        integrity_gates.values()
    )
    activated_ids = [
        cast(str, cast(Mapping[str, object], item["candidate"])["candidate_id"])
        for item in completed_candidates
        if item["data_and_source_conforming"] is True and item["exact_t_minus_one_saturation"] is True
    ]
    policy = cast(Mapping[str, object], manifest["decision_policy"])
    if not integrity_pass:
        decision = policy["fail_conformance"]
        authorized_next_stage = None
    elif activated_ids:
        decision = policy["pass"]
        authorized_next_stage = policy["authorized_next_stage"]
    else:
        decision = policy["fail_no_activation"]
        authorized_next_stage = None
    summary = {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "audit_id": manifest["audit_id"],
        "as_of": manifest["as_of"],
        "base_protocol": manifest["base_protocol"],
        "parents": manifest["parents"],
        "provider_chain_ids": {
            "blockscout": blockscout_chain_id,
            "publicnode_execution": publicnode_chain_id,
        },
        "historical_state_provider_count": 1,
        "historical_state_provider": "blockscout",
        "cross_provider_historical_state_replication_performed": False,
        "implementation_source_summary": {
            "audited_count": len(completed_sources),
            "fully_conforming_count": sum(
                item["fully_conforming_source"] is True for item in completed_sources
            ),
            "source_file_count": total_source_files,
            "source_text_byte_count": total_source_text_bytes,
            "records": [
                {
                    "address": item["address"],
                    "name": item["name"],
                    "compiler_version": item["compiler_version"],
                    "deployed_bytecode_sha256": item["deployed_bytecode_sha256"],
                    "checks": item["checks"],
                    "fully_conforming_source": item["fully_conforming_source"],
                }
                for item in completed_sources
            ],
        },
        "candidate_summary": {
            "audited_count": len(completed_candidates),
            "data_and_source_conforming_count": sum(
                item["data_and_source_conforming"] is True for item in completed_candidates
            ),
            "exact_t_minus_one_saturation_count": len(activated_ids),
            "exact_t_minus_one_saturation_candidate_ids": activated_ids,
            "records": [
                {
                    "candidate_id": cast(Mapping[str, object], item["candidate"])["candidate_id"],
                    "block_number": cast(Mapping[str, object], item["candidate"])["block_number"],
                    "market_id": cast(Mapping[str, object], item["candidate"])["market_id"],
                    "asset": cast(Mapping[str, object], item["candidate"])["asset"],
                    "data_and_source_conforming": item["data_and_source_conforming"],
                    "exact_t_minus_one_saturation": item["exact_t_minus_one_saturation"],
                    "exactly_saturated_snapshot_offsets": item["exactly_saturated_snapshot_offsets"],
                }
                for item in completed_candidates
            ],
        },
        "request_summary": {
            "successful_json_rpc_count": len(rpc_records),
            "successful_blockscout_smart_contract_count": len(source_http_records),
            "http_attempt_count": transport.http_attempts,
            "http_attempt_record_count": len(transport.attempt_records),
            "response_byte_count": transport.response_bytes,
            "method_counts": method_counts,
            "rest_path_template_counts": {SMART_CONTRACT_PATH_TEMPLATE: len(source_http_records)},
            "provider_counts": provider_counts,
            "operation_order_matches_frozen_plan": operation_order_matches,
            "all_one_attempt": all(item["attempt_count"] == 1 for item in transport.records),
        },
        "activation_contract": manifest["activation_contract"],
        "account_level_estimand_disposition": (
            "RETIRE_ACCOUNT_LEVEL_M3_FOR_SUPPLY_CAP_EVENTS_UNOBSERVABLE_TREATED_COHORT"
        ),
        "access_boundary": manifest["access_boundary"],
        "integrity_gates": integrity_gates,
        "integrity_gate_counts": {
            "pass": sum(integrity_gates.values()),
            "fail": sum(not value for value in integrity_gates.values()),
        },
        "decision": decision,
        "authorized_next_stage": authorized_next_stage,
        "limitations": manifest["limitations"],
    }
    evidence: dict[str, object] = {
        "implementation_sources": completed_sources,
        "candidates": completed_candidates,
    }
    http_evidence: dict[str, object] = {
        "successful_operations": transport.records,
        "http_attempts": transport.attempt_records,
    }
    return summary, evidence, http_evidence


def _git_value(root: Path, args: Sequence[str]) -> str:
    result = subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _failure_artifact(
    *,
    manifest: Mapping[str, object],
    manifest_sha256: str,
    collection_commit: str,
    transport: SupplyCapTransport | None,
    completed_sources: Sequence[Mapping[str, object]],
    completed_candidates: Sequence[Mapping[str, object]],
    error: Exception,
) -> dict[str, object]:
    contract = cast(Mapping[str, object], manifest["failure_artifact_contract"])
    maximum_characters = cast(int, contract["maximum_exception_message_characters"])
    message = str(error)
    successful_operations = [] if transport is None else transport.records
    http_attempts = [] if transport is None else transport.attempt_records
    return {
        "schema_version": FAILURE_SCHEMA_VERSION,
        "audit_id": manifest["audit_id"],
        "as_of": manifest["as_of"],
        "collection_commit": collection_commit,
        "manifest_sha256": manifest_sha256,
        "base_protocol": manifest["base_protocol"],
        "parents": manifest["parents"],
        "access_boundary": manifest["access_boundary"],
        "exception": {
            "class": type(error).__name__,
            "message": message[:maximum_characters],
            "message_truncated": len(message) > maximum_characters,
        },
        "successful_operation_count": len(successful_operations),
        "http_attempt_count": 0 if transport is None else transport.http_attempts,
        "http_attempt_record_count": len(http_attempts),
        "response_byte_count": 0 if transport is None else transport.response_bytes,
        "successful_operations": successful_operations,
        "http_attempts": http_attempts,
        "partial_normalized_evidence": {
            "completed_implementation_sources": [dict(item) for item in completed_sources],
            "completed_candidates": [dict(item) for item in completed_candidates],
            "is_complete_scientific_result": False,
        },
        "raw_response_payloads_retained": False,
        "scientific_gate_decision_reached": False,
        "decision": cast(Mapping[str, object], manifest["decision_policy"])["infrastructure_failure"],
        "authorized_next_stage": None,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--response-hashes", type=Path, required=True)
    parser.add_argument("--failure", type=Path, required=True)
    parser.add_argument("--collection-commit")
    return parser


def main() -> None:
    """Run one sealed v2 activation audit from an exact clean commit."""

    args = _build_parser().parse_args()
    success_outputs = (args.summary, args.candidates, args.response_hashes)
    for output in (*success_outputs, args.failure):
        if output.exists():
            raise FileExistsError(f"refusing to overwrite {output}")
    root = Path.cwd()
    current_commit = _git_value(root, ["rev-parse", "HEAD"])
    if _git_value(root, ["status", "--porcelain"]):
        raise RuntimeError("collection worktree must be clean")
    if args.collection_commit is not None and args.collection_commit != current_commit:
        raise ValueError("collection commit must equal the clean worktree HEAD")
    manifest = load_supply_cap_activation_v2(args.manifest)
    manifest_sha256 = hashlib.sha256(args.manifest.read_bytes()).hexdigest()
    transport: SupplyCapTransport | None = None
    completed_sources: list[dict[str, object]] = []
    completed_candidates: list[dict[str, object]] = []
    try:
        transport = build_http_transport(manifest)
        summary, candidates, responses = collect_supply_cap_activation_v2(
            manifest,
            root=root,
            transport=transport,
            completed_sources=completed_sources,
            completed_candidates=completed_candidates,
        )
    except Exception as error:
        args.failure.parent.mkdir(parents=True, exist_ok=True)
        _write_json(
            args.failure,
            _failure_artifact(
                manifest=manifest,
                manifest_sha256=manifest_sha256,
                collection_commit=current_commit,
                transport=transport,
                completed_sources=completed_sources,
                completed_candidates=completed_candidates,
                error=error,
            ),
        )
        raise
    summary["collection_commit"] = current_commit
    summary["manifest_sha256"] = manifest_sha256
    for output in success_outputs:
        output.parent.mkdir(parents=True, exist_ok=True)
    _write_json(args.candidates, candidates)
    _write_json(args.response_hashes, responses)
    _write_json(args.summary, summary)
    print(
        json.dumps(
            {
                "decision": summary["decision"],
                "exact_t_minus_one_saturation_count": cast(
                    Mapping[str, object], summary["candidate_summary"]
                )["exact_t_minus_one_saturation_count"],
                "network_operations": len(cast(Sequence[object], responses["successful_operations"])),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
