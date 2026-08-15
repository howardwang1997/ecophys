"""Receipt, payload, trace, getter and finality audit for frozen Compound III candidates."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import time
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import requests
import yaml

from ecomd.research.compound_governance_inventory import (
    CONFIGURATOR,
    ELIGIBLE_EVENT_TYPES,
    decode_quantity,
    normalize_address,
    normalize_governance_log,
    normalize_hash,
)
from ecomd.research.compound_v3_chain_metadata import (
    ADMIN_SLOT,
    IMPLEMENTATION_SLOT,
    canonical_json_sha256,
)

SCHEMA_VERSION = "ecophys-compound-v3-candidate-mechanics-preflight/v1"
ARTIFACT_SCHEMA_VERSION = "ecophys-compound-v3-candidate-mechanics-audit/v1"
AUDIT_ID = "compound_v3_mainnet_candidate_mechanics_preflight_v1"
AS_OF = "2026-08-16"
STAGE = "receipt_payload_trace_getter_finality_only"
BEACON_PATH = "/eth/v1/beacon/light_client/finality_update"
GET_ASSET_INFO_SELECTOR = "0x3b3bec2e"
DEPLOY_SELECTOR = "0x4c96a389"
SETTER_SELECTORS = {
    "update_asset_borrow_collateral_factor": "0xb73585f1",
    "update_asset_liquidate_collateral_factor": "0x77a7dafd",
    "update_asset_supply_cap": "0xa2ced7fd",
}
ADMIN_DEPLOY_SELECTORS = ("0x9627816f", "0xc7d20733")
PROXY_UPGRADE_SELECTORS = ("0x3659cfe6", "0x4f1ef286")
TRACE_CONFIG: dict[str, object] = {
    "tracer": "callTracer",
    "timeout": "60s",
    "tracerConfig": {"onlyTopCall": False, "withLog": False},
}
EVENT_PRIORITY = (
    "update_asset_borrow_collateral_factor",
    "update_asset_liquidate_collateral_factor",
    "update_asset_supply_cap",
)
MARKET_BY_PROXY = {
    "0xc3d688b66703497daa19211eedff47f25384cdc3": "mainnet_usdc",
    "0x5d409e56d886231adaf00c8775665ad0f9897b56": "mainnet_usds",
    "0x3afdc9bca9213a35503b077a6072f3d0d5ab0840": "mainnet_usdt",
    "0xe85dc543813b8c2cfeaac371517b925a166a9293": "mainnet_wbtc",
    "0xa17581a9e3356d9a858b789d68b4d866e593ae94": "mainnet_weth",
    "0x3d0bb1ccab520a66e607822fc55bc921738fafe3": "mainnet_wsteth",
}
FROZEN_PARENTS = {
    "d0_summary_path": "experiments/v14_compound_v3_governance_log_inventory/artifacts/summary.json",
    "d0_summary_sha256": "e03161118ac4cd7aea56f92f40aabdd49348d3170ce256ff42896291c1470b7f",
    "d0_inventory_path": "experiments/v14_compound_v3_governance_log_inventory/artifacts/governance_logs.json",
    "d0_inventory_sha256": "0435a55b652f5b6a6419f22b296b72184aed25c0073a132c232de55f741fd9e2",
    "exposure_design_path": "data/manifests/compound_v3_exposure_control_design_v1.yaml",
    "exposure_design_sha256": "ec329243f9fd071405112f4598b3f7e982d56683beec742e15b920c667e4b85e",
    "chain_summary_path": "experiments/v14_compound_v3_chain_metadata_preflight/artifacts_v2/summary.json",
    "chain_summary_sha256": "14f5b044d8c51e4323419b901a7f037c84c4af45083464e0daaefc561256c944",
    "result_commit": "b07935a5e182cdc4682a1392879291ee8d59136e",
    "source_commit": "f766f51583c23acc33b2a7824654ef2029a96804",
}
ALLOWED_RPC_METHODS = frozenset(
    {
        "eth_chainId",
        "eth_getBlockByNumber",
        "eth_getTransactionByHash",
        "eth_getTransactionReceipt",
        "debug_traceTransaction",
        "eth_getStorageAt",
        "eth_getCode",
        "eth_call",
    }
)
REQUIRED_GATES = frozenset(
    {
        "parent_hashes_and_exact_candidate_derivation",
        "ethereum_chain_and_finality_sources",
        "exact_complete_request_plan",
        "all_receipts_and_d0_logs_conform",
        "cross_provider_candidate_headers",
        "complete_call_traces",
        "candidate_mechanism_call_cones_evaluated",
        "pre_post_getter_and_proxy_state_evaluated",
        "contamination_windows_evaluated",
        "at_least_one_fully_conforming_candidate",
        "request_trace_and_byte_caps",
        "participant_data_access_boundary",
    }
)
TOP_LEVEL_KEYS = frozenset(
    {
        "schema_version",
        "audit_id",
        "as_of",
        "stage",
        "parents",
        "access_boundary",
        "sources",
        "selection_contract",
        "contracts",
        "trace_contract",
        "finality_contract",
        "contamination_contract",
        "expected_request_contract",
        "candidates",
        "gates",
        "decision_policy",
        "limitations",
    }
)
CANDIDATE_KEYS = frozenset(
    {
        "candidate_id",
        "priority_rank",
        "block_number",
        "transaction_hash",
        "market_id",
        "comet_proxy",
        "asset",
        "event_type",
        "old_value",
        "new_value",
        "implementation",
        "nearby_other_governance_blocks",
    }
)
ACCESS_TRUE = frozenset(
    {
        "chain_rpc_used",
        "beacon_api_used",
        "governance_log_parent_opened",
        "governance_transaction_rows_opened",
        "governance_receipt_rows_opened",
        "governance_payload_rows_opened",
        "governance_call_trace_rows_opened",
        "configuration_getter_rows_opened",
        "proxy_slot_rows_opened",
        "implementation_code_opened_for_hashing",
    }
)
ACCESS_FALSE = frozenset(
    {
        "account_state_rows_opened",
        "participant_action_rows_opened",
        "participant_call_trace_rows_opened",
        "liquidation_rows_opened",
        "price_or_oracle_rows_opened",
        "realized_response_rows_opened",
        "raw_rpc_payloads_retained",
        "paid_data_used",
        "external_workers_used",
        "gpu_used",
    }
)
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def _mapping(value: object) -> Mapping[str, object] | None:
    if not isinstance(value, Mapping):
        return None
    return cast(Mapping[str, object], value)


def _mapping_list(value: object) -> list[Mapping[str, object]] | None:
    if not isinstance(value, list):
        return None
    result: list[Mapping[str, object]] = []
    for item in value:
        mapped = _mapping(item)
        if mapped is None:
            return None
        result.append(mapped)
    return result


def _strings(value: object) -> tuple[str, ...] | None:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        return None
    return tuple(cast(list[str], value))


def _safe_relative_path(value: object) -> bool:
    return (
        isinstance(value, str)
        and bool(value)
        and not Path(value).is_absolute()
        and ".." not in Path(value).parts
    )


def load_candidate_mechanics(path: str | Path) -> dict[str, object]:
    """Load one frozen candidate-mechanics manifest."""

    value: object = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("candidate mechanics root must be a mapping")
    return cast(dict[str, object], value)


def validate_candidate_mechanics(manifest: Mapping[str, object]) -> list[str]:
    """Return structural and access-boundary violations."""

    errors: list[str] = []
    if set(manifest) != TOP_LEVEL_KEYS:
        errors.append(f"top level must contain exactly {sorted(TOP_LEVEL_KEYS)}")
    expected_scalars = {
        "schema_version": SCHEMA_VERSION,
        "audit_id": AUDIT_ID,
        "as_of": AS_OF,
        "stage": STAGE,
    }
    for key, expected in expected_scalars.items():
        if manifest.get(key) != expected:
            errors.append(f"{key} must equal {expected}")

    parents = _mapping(manifest.get("parents"))
    if parents is None or dict(parents) != FROZEN_PARENTS:
        errors.append("parents differ from the frozen artifact contract")
        parents = {}
    for key, value in parents.items():
        if key.endswith("_path") and not _safe_relative_path(value):
            errors.append(f"parents.{key} must be a safe relative path")
        if key.endswith("_sha256") and (
            not isinstance(value, str) or SHA256_PATTERN.fullmatch(value) is None
        ):
            errors.append(f"parents.{key} must be a lowercase SHA-256")

    access = _mapping(manifest.get("access_boundary"))
    if access is None or set(access) != ACCESS_TRUE | ACCESS_FALSE:
        errors.append("access_boundary keys differ from the frozen contract")
        access = {}
    for key in ACCESS_TRUE:
        if access.get(key) is not True:
            errors.append(f"access_boundary.{key} must be true")
    for key in ACCESS_FALSE:
        if access.get(key) is not False:
            errors.append(f"access_boundary.{key} must be false")

    sources = _mapping(manifest.get("sources"))
    required_source_values: dict[str, object] = {
        "blockscout_rpc_url": "https://eth.blockscout.com/api/eth-rpc",
        "blockscout_documentation_url": "https://docs.blockscout.com/devs/apis/rpc/eth-rpc",
        "blockscout_terms_url": "https://eaas.blockscout.com/terms-and-conditions",
        "publicnode_rpc_url": "https://ethereum-rpc.publicnode.com",
        "publicnode_beacon_url": "https://ethereum-beacon-api.publicnode.com",
        "publicnode_documentation_url": "https://ethereum.publicnode.dev/",
        "beacon_api_specification_url": "https://github.com/ethereum/beacon-APIs",
        "maximum_requests_per_second_across_sources": 1,
        "maximum_transport_retries": 2,
        "maximum_http_attempts": 600,
        "maximum_response_bytes": 268_435_456,
        "maximum_trace_nodes": 200_000,
        "maximum_trace_input_bytes": 67_108_864,
        "maximum_receipt_logs": 100_000,
        "raw_response_payloads_retained": False,
        "endpoint_substitution_after_freeze": False,
        "user_agent": "EcoPhys-V14-Compound-candidate-mechanics-preflight/1.0",
    }
    expected_source_keys = set(required_source_values) | {"allowed_rpc_methods", "allowed_beacon_paths"}
    if sources is None or set(sources) != expected_source_keys:
        errors.append(f"sources must contain exactly {sorted(expected_source_keys)}")
        sources = {}
    for key, source_expected in required_source_values.items():
        if sources.get(key) != source_expected:
            errors.append(f"sources.{key} must equal the frozen value")
    if _strings(sources.get("allowed_rpc_methods")) != (
        "eth_chainId",
        "eth_getBlockByNumber",
        "eth_getTransactionByHash",
        "eth_getTransactionReceipt",
        "debug_traceTransaction",
        "eth_getStorageAt",
        "eth_getCode",
        "eth_call",
    ):
        errors.append("sources.allowed_rpc_methods differs from the frozen order")
    if _strings(sources.get("allowed_beacon_paths")) != (BEACON_PATH,):
        errors.append("sources.allowed_beacon_paths differs from the frozen path")

    expected_selection = {
        "audit_every_d0_provisional_candidate": True,
        "event_priority": list(EVENT_PRIORITY),
        "within_class_tie_break": "ascending_block_then_transaction_hash",
        "candidate_replacement_after_freeze": False,
        "selection_uses_participant_or_response_data": False,
        "minimum_fully_conforming_candidates": 1,
    }
    selection = _mapping(manifest.get("selection_contract"))
    if selection is None or dict(selection) != expected_selection:
        errors.append("selection_contract differs from the frozen contract")

    expected_contracts = {
        "configurator_proxy": CONFIGURATOR,
        "implementation_slot": IMPLEMENTATION_SLOT,
        "admin_slot": ADMIN_SLOT,
        "get_asset_info_selector": GET_ASSET_INFO_SELECTOR,
        "setter_selectors": SETTER_SELECTORS,
        "deploy_selector": DEPLOY_SELECTOR,
        "proxy_admin_deploy_selectors": list(ADMIN_DEPLOY_SELECTORS),
        "proxy_upgrade_selectors": list(PROXY_UPGRADE_SELECTORS),
        "asset_info_fields": [
            "offset_uint8",
            "asset_address",
            "price_feed_address",
            "scale_uint64",
            "borrow_collateral_factor_uint64",
            "liquidate_collateral_factor_uint64",
            "liquidation_factor_uint64",
            "supply_cap_uint128",
        ],
        "only_declared_asset_field_may_change": True,
    }
    contracts = _mapping(manifest.get("contracts"))
    if contracts is None or dict(contracts) != expected_contracts:
        errors.append("contracts differ from the frozen ABI/slot contract")

    expected_trace = {
        "tracer": "callTracer",
        "timeout": "60s",
        "only_top_call": False,
        "with_log": False,
        "root_must_match_transaction_envelope": True,
        "required_successful_calls": [
            "exact_configurator_setter",
            "exact_configurator_deploy",
            "exact_proxy_admin_deploy_and_upgrade",
            "exact_target_proxy_upgrade",
        ],
        "required_call_type": "CALL",
        "deploy_and_upgrade_strictly_descend_from_proxy_admin_call": True,
        "deploy_and_upgrade_callers_equal_proxy_admin": True,
        "allow_static_calls_outside_mechanism_cone": True,
        "reject_stateful_calls_outside_required_ancestor_descendant_cone": True,
        "failed_internal_calls_do_not_count_as_state_changes": True,
    }
    trace_contract = _mapping(manifest.get("trace_contract"))
    if trace_contract is None or dict(trace_contract) != expected_trace:
        errors.append("trace_contract differs from the frozen call-cone contract")

    expected_finality = {
        "require_publicnode_finalized_tag": True,
        "require_beacon_light_client_finality_update": True,
        "require_beacon_execution_header_match_explicit_rpc_header": True,
        "require_both_finalized_numbers_after_every_candidate": True,
        "require_candidate_header_match_publicnode_and_blockscout": True,
        "local_bls_signature_verification_performed": False,
    }
    finality = _mapping(manifest.get("finality_contract"))
    if finality is None or dict(finality) != expected_finality:
        errors.append("finality_contract differs from the frozen contract")

    expected_contamination = {
        "window_seconds": 86_400,
        "post_merge_block_radius": 7_200,
        "derive_neighbors_from_complete_d0_inventory": True,
        "same_transaction_is_candidate_mechanics_not_neighbor": True,
        "any_other_configurator_or_frozen_proxy_log_inside_window_fails_candidate": True,
        "unique_neighbor_blocks_requiring_headers": [20_721_442, 21_237_796],
    }
    contamination = _mapping(manifest.get("contamination_contract"))
    if contamination is None or dict(contamination) != expected_contamination:
        errors.append("contamination_contract differs from the frozen contract")

    expected_requests = {
        "candidate_count": 14,
        "json_rpc_success_count_without_retry": 187,
        "beacon_success_count_without_retry": 1,
        "network_operation_count_without_retry": 188,
        "method_counts": {
            "eth_chainId": 1,
            "eth_getBlockByNumber": 32,
            "eth_getTransactionByHash": 14,
            "eth_getTransactionReceipt": 14,
            "debug_traceTransaction": 14,
            "eth_getStorageAt": 56,
            "eth_getCode": 28,
            "eth_call": 28,
        },
        "provider_counts": {
            "blockscout": 156,
            "publicnode_execution": 31,
            "publicnode_beacon": 1,
        },
    }
    requests = _mapping(manifest.get("expected_request_contract"))
    if requests is None or dict(requests) != expected_requests:
        errors.append("expected_request_contract differs from the frozen plan")

    candidates = _mapping_list(manifest.get("candidates"))
    if candidates is None or len(candidates) != 14:
        errors.append("candidates must contain exactly fourteen mappings")
        candidates = []
    ids: set[str] = set()
    for index, candidate in enumerate(candidates):
        if set(candidate) != CANDIDATE_KEYS:
            errors.append(f"candidates[{index}] keys differ from the frozen schema")
        candidate_id = candidate.get("candidate_id")
        if (
            not isinstance(candidate_id, str)
            or ID_PATTERN.fullmatch(candidate_id) is None
            or candidate_id in ids
        ):
            errors.append(f"candidates[{index}].candidate_id must be unique and stable")
        else:
            ids.add(candidate_id)
        if candidate.get("priority_rank") != index + 1:
            errors.append(f"candidates[{index}].priority_rank must equal {index + 1}")
        for key in ("block_number", "old_value", "new_value"):
            value = candidate.get(key)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                errors.append(f"candidates[{index}].{key} must be a nonnegative integer")
        try:
            proxy = normalize_address(candidate.get("comet_proxy"), path=f"candidates[{index}].comet_proxy")
            normalize_address(candidate.get("asset"), path=f"candidates[{index}].asset")
            normalize_address(candidate.get("implementation"), path=f"candidates[{index}].implementation")
            if MARKET_BY_PROXY.get(proxy) != candidate.get("market_id"):
                errors.append(f"candidates[{index}].market_id does not match its proxy")
        except ValueError as exc:
            errors.append(str(exc))
        try:
            normalize_hash(candidate.get("transaction_hash"), path=f"candidates[{index}].transaction_hash")
        except ValueError as exc:
            errors.append(str(exc))
        if candidate.get("event_type") not in ELIGIBLE_EVENT_TYPES:
            errors.append(f"candidates[{index}].event_type is not eligible")
        neighbors = candidate.get("nearby_other_governance_blocks")
        if not isinstance(neighbors, list) or any(
            not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in neighbors
        ):
            errors.append(f"candidates[{index}].nearby_other_governance_blocks must be integer blocks")

    gates = _strings(manifest.get("gates"))
    if gates is None or frozenset(gates) != REQUIRED_GATES or len(gates) != len(REQUIRED_GATES):
        errors.append(f"gates must contain exactly {sorted(REQUIRED_GATES)}")
    expected_policy = {
        "all_gates_required": True,
        "pass": "PASS_CANDIDATE_MECHANICS_AUTHORIZE_D1_EXPOSURE_PROTOCOL_DESIGN_ONLY",
        "fail": "FAIL_CANDIDATE_MECHANICS_KEEP_ACCOUNT_AND_RESPONSE_ROWS_LOCKED",
        "authorized_next_stage": "separately_frozen_d1_exposure_count_and_cost_protocol_design",
    }
    policy = _mapping(manifest.get("decision_policy"))
    if policy is None or dict(policy) != expected_policy:
        errors.append("decision_policy differs from the frozen contract")
    limitations = _strings(manifest.get("limitations"))
    if limitations is None or len(limitations) < 6:
        errors.append("limitations must contain at least six strings")
    return sorted(errors)


def _read_json_mapping(path: Path) -> Mapping[str, object]:
    value: object = json.loads(path.read_text(encoding="utf-8"))
    mapped = _mapping(value)
    if mapped is None:
        raise ValueError(f"{path} must contain a JSON mapping")
    return mapped


def _read_json_mapping_list(path: Path) -> list[Mapping[str, object]]:
    value: object = json.loads(path.read_text(encoding="utf-8"))
    mapped = _mapping_list(value)
    if mapped is None:
        raise ValueError(f"{path} must contain a JSON list of mappings")
    return mapped


def derive_d0_candidates(
    summary: Mapping[str, object], inventory: Sequence[Mapping[str, object]]
) -> list[dict[str, object]]:
    """Derive the exact outcome-blind candidate order and neighbor blocks from D0."""

    inventory_summary = _mapping(summary.get("inventory"))
    if inventory_summary is None:
        raise ValueError("D0 summary inventory is missing")
    records = _mapping_list(inventory_summary.get("candidate_records"))
    if records is None:
        raise ValueError("D0 candidate records are missing")
    provisional = [record for record in records if record.get("provisional_atomic_candidate") is True]
    priority = {event_type: index for index, event_type in enumerate(EVENT_PRIORITY)}
    provisional.sort(
        key=lambda item: (
            priority[cast(str, item["event_type"])],
            cast(int, item["block_number"]),
            cast(str, item["transaction_hash"]),
        )
    )
    result: list[dict[str, object]] = []
    for rank, record in enumerate(provisional, start=1):
        block_number = cast(int, record["block_number"])
        transaction_hash = cast(str, record["transaction_hash"])
        event_type = cast(str, record["event_type"])
        prefix = {
            "update_asset_borrow_collateral_factor": "borrow_cf",
            "update_asset_liquidate_collateral_factor": "liquidate_cf",
            "update_asset_supply_cap": "supply_cap",
        }[event_type]
        proxy = cast(str, record["comet_proxy"])
        neighbor_blocks = sorted(
            {
                cast(int, item["block_number"])
                for item in inventory
                if item.get("transaction_hash") != transaction_hash
                and abs(cast(int, item["block_number"]) - block_number) <= 7_200
            }
        )
        result.append(
            {
                "candidate_id": f"{prefix}_{block_number}_{transaction_hash[2:10]}",
                "priority_rank": rank,
                "block_number": block_number,
                "transaction_hash": transaction_hash,
                "market_id": MARKET_BY_PROXY[proxy],
                "comet_proxy": proxy,
                "asset": record["asset"],
                "event_type": event_type,
                "old_value": record["old_value"],
                "new_value": record["new_value"],
                "implementation": record["implementation"],
                "nearby_other_governance_blocks": neighbor_blocks,
            }
        )
    return result


def validate_parent_evidence(manifest: Mapping[str, object], root: str | Path) -> list[str]:
    """Verify parent hashes and exact D0 candidate/neighbor derivation."""

    errors: list[str] = []
    root_path = Path(root)
    parents = cast(Mapping[str, object], manifest["parents"])
    for path_key, hash_key in (
        ("d0_summary_path", "d0_summary_sha256"),
        ("d0_inventory_path", "d0_inventory_sha256"),
        ("exposure_design_path", "exposure_design_sha256"),
        ("chain_summary_path", "chain_summary_sha256"),
    ):
        path = root_path / cast(str, parents[path_key])
        if not path.is_file():
            errors.append(f"parent {path_key} is missing")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != parents[hash_key]:
            errors.append(f"parent {path_key} hash differs from the frozen value")
    if errors:
        return sorted(errors)
    summary = _read_json_mapping(root_path / cast(str, parents["d0_summary_path"]))
    inventory = _read_json_mapping_list(root_path / cast(str, parents["d0_inventory_path"]))
    if summary.get("decision") != "PASS_GOVERNANCE_LOG_INVENTORY_AUTHORIZE_RECEIPT_PAYLOAD_PREFLIGHT_ONLY":
        errors.append("D0 parent decision is not the frozen pass")
    derived = derive_d0_candidates(summary, inventory)
    candidates = _mapping_list(manifest.get("candidates"))
    if candidates is None or [dict(item) for item in candidates] != derived:
        errors.append("manifest candidates differ from exact D0 derivation")
    neighbor_blocks = sorted(
        {
            block
            for candidate in derived
            for block in cast(list[int], candidate["nearby_other_governance_blocks"])
            if block != candidate["block_number"]
        }
    )
    contamination = cast(Mapping[str, object], manifest["contamination_contract"])
    if neighbor_blocks != contamination["unique_neighbor_blocks_requiring_headers"]:
        errors.append("unique contamination-neighbor block plan differs from D0 derivation")
    return sorted(errors)


def _hex_bytes(value: object, *, path: str) -> bytes:
    if not isinstance(value, str) or not value.startswith("0x"):
        raise ValueError(f"{path} must be 0x-prefixed hexadecimal bytes")
    body = value[2:]
    if len(body) % 2 or re.fullmatch(r"[0-9a-fA-F]*", body) is None:
        raise ValueError(f"{path} must contain complete hexadecimal bytes")
    return bytes.fromhex(body)


def _word_address(word: bytes, *, path: str) -> str:
    if len(word) != 32 or any(word[:12]):
        raise ValueError(f"{path} must be one canonical ABI address word")
    return "0x" + word[12:].hex()


def _storage_address(value: object, *, path: str) -> str:
    word = _hex_bytes(value, path=path)
    if len(word) != 32:
        raise ValueError(f"{path} must be one storage word")
    return _word_address(word, path=path)


def _call_data(selector: str, address: str) -> str:
    normalized = normalize_address(address, path="call address")
    return selector + "0" * 24 + normalized[2:]


def decode_asset_info(value: object, *, expected_asset: str) -> dict[str, object]:
    """Decode the static eight-word Comet AssetInfo return value."""

    data = _hex_bytes(value, path="asset_info")
    if len(data) != 8 * 32:
        raise ValueError("asset_info must contain exactly eight ABI words")
    words = [data[index * 32 : (index + 1) * 32] for index in range(8)]
    integers = [int.from_bytes(word, "big") for word in words]
    if integers[0] >= 2**8:
        raise ValueError("asset_info offset exceeds uint8")
    for index in (3, 4, 5, 6):
        if integers[index] >= 2**64:
            raise ValueError("asset_info uint64 field exceeds width")
    if integers[7] >= 2**128:
        raise ValueError("asset_info supply cap exceeds uint128")
    asset = _word_address(words[1], path="asset_info.asset")
    if asset != normalize_address(expected_asset, path="expected_asset"):
        raise ValueError("asset_info asset differs from the requested asset")
    return {
        "offset": integers[0],
        "asset": asset,
        "price_feed": _word_address(words[2], path="asset_info.price_feed"),
        "scale": integers[3],
        "borrow_collateral_factor": integers[4],
        "liquidate_collateral_factor": integers[5],
        "liquidation_factor": integers[6],
        "supply_cap": integers[7],
    }


class HttpTransport:
    """Globally rate-limited RPC/Beacon transport retaining hashes and normalized requests."""

    def __init__(
        self,
        *,
        user_agent: str,
        maximum_requests_per_second: float,
        maximum_transport_retries: int,
        maximum_http_attempts: int,
        maximum_response_bytes: int,
    ) -> None:
        self._minimum_interval = 1.0 / maximum_requests_per_second
        self._maximum_transport_retries = maximum_transport_retries
        self._maximum_http_attempts = maximum_http_attempts
        self._maximum_response_bytes = maximum_response_bytes
        self._last_start: float | None = None
        self._next_rpc_id = 1
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": user_agent})
        self.http_attempts = 0
        self.response_bytes = 0
        self.records: list[dict[str, object]] = []

    def _wait(self) -> None:
        if self._last_start is not None:
            time.sleep(max(0.0, self._minimum_interval - (time.monotonic() - self._last_start)))
        self._last_start = time.monotonic()

    def _consume(self, body: bytes) -> None:
        self.response_bytes += len(body)
        if self.response_bytes > self._maximum_response_bytes:
            raise RuntimeError("maximum response-byte cap exceeded")

    def rpc_call(
        self,
        *,
        url: str,
        provider: str,
        label: str,
        method: str,
        params: Sequence[object],
    ) -> object:
        """Issue one permitted JSON-RPC call."""

        if method not in ALLOWED_RPC_METHODS:
            raise ValueError(f"forbidden JSON-RPC method: {method}")
        request_id = self._next_rpc_id
        self._next_rpc_id += 1
        request = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": list(params)}
        prior_errors: list[str] = []
        for attempt in range(self._maximum_transport_retries + 1):
            if self.http_attempts >= self._maximum_http_attempts:
                raise RuntimeError("maximum HTTP-attempt cap reached")
            self._wait()
            self.http_attempts += 1
            try:
                response = self._session.post(url, json=request, timeout=120.0)
                body = response.content
                self._consume(body)
                response.raise_for_status()
                envelope_value: object = response.json()
            except RuntimeError:
                raise
            except (requests.RequestException, ValueError) as exc:
                prior_errors.append(f"{type(exc).__name__}: {exc}")
            else:
                envelope = _mapping(envelope_value)
                if envelope is None:
                    prior_errors.append("RPC response is not a mapping")
                elif envelope.get("error") is not None:
                    prior_errors.append(f"RPC error: {envelope['error']}")
                elif "result" not in envelope or envelope.get("result") is None:
                    prior_errors.append("RPC result is missing or null")
                else:
                    result = envelope["result"]
                    self.records.append(
                        {
                            "operation_index": len(self.records),
                            "operation_type": "json_rpc",
                            "label": label,
                            "provider": provider,
                            "method": method,
                            "params": list(params),
                            "request_sha256": canonical_json_sha256(request),
                            "response_body_sha256": hashlib.sha256(body).hexdigest(),
                            "response_canonical_json_sha256": canonical_json_sha256(envelope_value),
                            "response_byte_count": len(body),
                            "attempt_count": attempt + 1,
                            "prior_errors": list(prior_errors),
                            "retrieved_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                        }
                    )
                    return result
            if attempt < self._maximum_transport_retries:
                time.sleep(float(attempt + 1))
        raise RuntimeError(f"{label} failed after all attempts: {prior_errors}")

    def beacon_get(self, *, base_url: str, path: str, label: str) -> object:
        """Issue the single frozen Beacon API request."""

        if path != BEACON_PATH:
            raise ValueError(f"forbidden Beacon API path: {path}")
        url = base_url.rstrip("/") + path
        prior_errors: list[str] = []
        for attempt in range(self._maximum_transport_retries + 1):
            if self.http_attempts >= self._maximum_http_attempts:
                raise RuntimeError("maximum HTTP-attempt cap reached")
            self._wait()
            self.http_attempts += 1
            try:
                response = self._session.get(url, headers={"Accept": "application/json"}, timeout=120.0)
                body = response.content
                self._consume(body)
                response.raise_for_status()
                value: object = response.json()
            except RuntimeError:
                raise
            except (requests.RequestException, ValueError) as exc:
                prior_errors.append(f"{type(exc).__name__}: {exc}")
            else:
                if _mapping(value) is None:
                    prior_errors.append("Beacon response is not a mapping")
                else:
                    request_record = {"method": "GET", "url": url, "accept": "application/json"}
                    self.records.append(
                        {
                            "operation_index": len(self.records),
                            "operation_type": "beacon_rest",
                            "label": label,
                            "provider": "publicnode_beacon",
                            "path": path,
                            "request_sha256": canonical_json_sha256(request_record),
                            "response_body_sha256": hashlib.sha256(body).hexdigest(),
                            "response_canonical_json_sha256": canonical_json_sha256(value),
                            "response_byte_count": len(body),
                            "attempt_count": attempt + 1,
                            "prior_errors": list(prior_errors),
                            "retrieved_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                        }
                    )
                    return value
            if attempt < self._maximum_transport_retries:
                time.sleep(float(attempt + 1))
        raise RuntimeError(f"{label} failed after all attempts: {prior_errors}")


def _block_record(value: object, *, expected_number: int | None, path: str) -> dict[str, object]:
    block = _mapping(value)
    if block is None:
        raise ValueError(f"{path} must be a block mapping")
    number = decode_quantity(block.get("number"), path=f"{path}.number")
    if expected_number is not None and number != expected_number:
        raise ValueError(f"{path} number differs from the requested block")
    timestamp = decode_quantity(block.get("timestamp"), path=f"{path}.timestamp")
    transactions = block.get("transactions")
    if not isinstance(transactions, list):
        raise ValueError(f"{path}.transactions must be a list")
    return {
        "number": number,
        "hash": normalize_hash(block.get("hash"), path=f"{path}.hash"),
        "parent_hash": normalize_hash(block.get("parentHash"), path=f"{path}.parentHash"),
        "timestamp_unix": timestamp,
        "timestamp_utc": datetime.fromtimestamp(timestamp, UTC).isoformat().replace("+00:00", "Z"),
        "transaction_count": len(transactions),
    }


def _transaction_record(value: object, *, candidate: Mapping[str, object]) -> dict[str, object]:
    transaction = _mapping(value)
    if transaction is None:
        raise ValueError("transaction must be a mapping")
    input_bytes = _hex_bytes(transaction.get("input"), path="transaction.input")
    record = {
        "hash": normalize_hash(transaction.get("hash"), path="transaction.hash"),
        "block_hash": normalize_hash(transaction.get("blockHash"), path="transaction.blockHash"),
        "block_number": decode_quantity(transaction.get("blockNumber"), path="transaction.blockNumber"),
        "transaction_index": decode_quantity(
            transaction.get("transactionIndex"), path="transaction.transactionIndex"
        ),
        "from": normalize_address(transaction.get("from"), path="transaction.from"),
        "to": normalize_address(transaction.get("to"), path="transaction.to"),
        "value": decode_quantity(transaction.get("value"), path="transaction.value"),
        "input": "0x" + input_bytes.hex(),
        "input_byte_count": len(input_bytes),
        "input_sha256": hashlib.sha256(input_bytes).hexdigest(),
    }
    if record["hash"] != candidate["transaction_hash"]:
        raise ValueError("transaction hash differs from the candidate")
    if record["block_number"] != candidate["block_number"]:
        raise ValueError("transaction block differs from the candidate")
    return record


def _receipt_log(raw: Mapping[str, object]) -> dict[str, object]:
    topics_value = raw.get("topics")
    if not isinstance(topics_value, list) or not topics_value:
        raise ValueError("receipt log topics must be a nonempty list")
    topics = [normalize_hash(item, path="receipt.log.topic") for item in topics_value]
    data = _hex_bytes(raw.get("data"), path="receipt.log.data")
    if raw.get("removed") not in (None, False):
        raise ValueError("removed receipt log is forbidden")
    address = normalize_address(raw.get("address"), path="receipt.log.address")
    block_number = decode_quantity(raw.get("blockNumber"), path="receipt.log.blockNumber")
    record: dict[str, object] = {
        "address": address,
        "block_hash": normalize_hash(raw.get("blockHash"), path="receipt.log.blockHash"),
        "block_number": block_number,
        "transaction_hash": normalize_hash(raw.get("transactionHash"), path="receipt.log.transactionHash"),
        "transaction_index": decode_quantity(
            raw.get("transactionIndex"), path="receipt.log.transactionIndex"
        ),
        "log_index": decode_quantity(raw.get("logIndex"), path="receipt.log.logIndex"),
        "topics": topics,
        "topic_count": len(topics),
        "data_byte_count": len(data),
        "data_sha256": hashlib.sha256(data).hexdigest(),
    }
    if address == CONFIGURATOR or address in MARKET_BY_PROXY:
        record["governance_record"] = normalize_governance_log(
            raw,
            expected_address=address,
            market_id=MARKET_BY_PROXY.get(address),
            from_block=block_number,
            to_block=block_number,
        )
    else:
        record["governance_record"] = None
    return record


def _receipt_record(
    value: object, *, candidate: Mapping[str, object], maximum_logs: int
) -> dict[str, object]:
    receipt = _mapping(value)
    if receipt is None:
        raise ValueError("receipt must be a mapping")
    logs_value = _mapping_list(receipt.get("logs"))
    if logs_value is None or len(logs_value) > maximum_logs:
        raise ValueError("receipt logs are missing or exceed the frozen cap")
    logs = [_receipt_log(item) for item in logs_value]
    record = {
        "transaction_hash": normalize_hash(receipt.get("transactionHash"), path="receipt.transactionHash"),
        "block_hash": normalize_hash(receipt.get("blockHash"), path="receipt.blockHash"),
        "block_number": decode_quantity(receipt.get("blockNumber"), path="receipt.blockNumber"),
        "transaction_index": decode_quantity(
            receipt.get("transactionIndex"), path="receipt.transactionIndex"
        ),
        "from": normalize_address(receipt.get("from"), path="receipt.from"),
        "to": normalize_address(receipt.get("to"), path="receipt.to"),
        "status": decode_quantity(receipt.get("status"), path="receipt.status"),
        "gas_used": decode_quantity(receipt.get("gasUsed"), path="receipt.gasUsed"),
        "logs": logs,
        "log_count": len(logs),
    }
    if record["transaction_hash"] != candidate["transaction_hash"]:
        raise ValueError("receipt transaction differs from the candidate")
    if record["block_number"] != candidate["block_number"]:
        raise ValueError("receipt block differs from the candidate")
    if len({item["log_index"] for item in logs}) != len(logs):
        raise ValueError("receipt contains duplicate log indexes")
    if any(
        item["transaction_hash"] != record["transaction_hash"]
        or item["block_hash"] != record["block_hash"]
        or item["block_number"] != record["block_number"]
        or item["transaction_index"] != record["transaction_index"]
        for item in logs
    ):
        raise ValueError("receipt log identity differs from its receipt")
    return record


def normalize_call_trace(
    value: object, *, maximum_nodes: int, maximum_input_bytes: int
) -> list[dict[str, object]]:
    """Flatten and strictly normalize a callTracer tree."""

    root = _mapping(value)
    if root is None:
        raise ValueError("call trace root must be a mapping")
    records: list[dict[str, object]] = []
    input_bytes_total = 0

    def visit(raw: Mapping[str, object], path: tuple[int, ...], parent_success: bool) -> None:
        nonlocal input_bytes_total
        if len(records) >= maximum_nodes:
            raise RuntimeError("maximum trace-node cap exceeded")
        call_type = raw.get("type")
        if not isinstance(call_type, str) or not call_type:
            raise ValueError("trace call type is missing")
        input_bytes = _hex_bytes(raw.get("input", "0x"), path="trace.input")
        output_bytes = _hex_bytes(raw.get("output", "0x"), path="trace.output")
        input_bytes_total += len(input_bytes)
        if input_bytes_total > maximum_input_bytes:
            raise RuntimeError("maximum trace-input byte cap exceeded")
        error = raw.get("error")
        if error is not None and not isinstance(error, str):
            raise ValueError("trace.error must be a string when present")
        revert_reason = raw.get("revertReason")
        if revert_reason is not None and not isinstance(revert_reason, str):
            raise ValueError("trace.revertReason must be a string when present")
        to_value = raw.get("to")
        to_address = None if to_value is None else normalize_address(to_value, path="trace.to")
        success = parent_success and error is None
        record: dict[str, object] = {
            "path": list(path),
            "type": call_type.upper(),
            "from": normalize_address(raw.get("from"), path="trace.from"),
            "to": to_address,
            "value": decode_quantity(raw.get("value", "0x0"), path="trace.value"),
            "gas": decode_quantity(raw.get("gas", "0x0"), path="trace.gas"),
            "gas_used": decode_quantity(raw.get("gasUsed", "0x0"), path="trace.gasUsed"),
            "input": "0x" + input_bytes.hex(),
            "input_byte_count": len(input_bytes),
            "input_sha256": hashlib.sha256(input_bytes).hexdigest(),
            "selector": "0x" + input_bytes[:4].hex() if len(input_bytes) >= 4 else None,
            "output_byte_count": len(output_bytes),
            "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
            "success": success,
            "error": error,
            "revert_reason": revert_reason,
        }
        records.append(record)
        children = raw.get("calls", [])
        child_list = _mapping_list(children)
        if child_list is None:
            raise ValueError("trace.calls must be a list of mappings")
        for index, child in enumerate(child_list):
            visit(child, (*path, index), success)

    visit(root, (), True)
    return records


def _input_bytes(node: Mapping[str, object]) -> bytes:
    return _hex_bytes(node["input"], path="normalized_trace.input")


def _static_address_argument(data: bytes, index: int) -> str:
    start = 4 + index * 32
    return _word_address(data[start : start + 32], path="call.argument")


def _static_integer_argument(data: bytes, index: int, bits: int) -> int:
    start = 4 + index * 32
    word = data[start : start + 32]
    if len(word) != 32:
        raise ValueError("call integer argument is truncated")
    value = int.from_bytes(word, "big")
    if value >= 2**bits:
        raise ValueError("call integer argument exceeds its ABI width")
    return value


def _path_prefix(prefix: tuple[int, ...], path: tuple[int, ...]) -> bool:
    return len(prefix) <= len(path) and path[: len(prefix)] == prefix


def analyze_mechanism_trace(
    nodes: Sequence[Mapping[str, object]],
    *,
    transaction: Mapping[str, object],
    candidate: Mapping[str, object],
    admin_address: str,
) -> dict[str, object]:
    """Find exact mechanism calls and stateful calls outside their call cone."""

    if not nodes:
        raise ValueError("normalized trace is empty")
    root = nodes[0]
    root_matches = (
        root["path"] == []
        and root["from"] == transaction["from"]
        and root["to"] == transaction["to"]
        and root["value"] == transaction["value"]
        and root["input"] == transaction["input"]
        and root["success"] is True
    )
    setter_matches: list[Mapping[str, object]] = []
    deploy_matches: list[Mapping[str, object]] = []
    admin_matches: list[Mapping[str, object]] = []
    upgrade_matches: list[Mapping[str, object]] = []
    expected_setter = SETTER_SELECTORS[cast(str, candidate["event_type"])]
    proxy = cast(str, candidate["comet_proxy"])
    asset = cast(str, candidate["asset"])
    new_value = cast(int, candidate["new_value"])
    implementation = cast(str, candidate["implementation"])
    for node in nodes:
        if node.get("success") is not True:
            continue
        data = _input_bytes(node)
        selector = cast(str | None, node.get("selector"))
        to_address = node.get("to")
        if (
            node.get("type") == "CALL"
            and to_address == CONFIGURATOR
            and selector == expected_setter
            and len(data) == 100
        ):
            bits = 128 if candidate["event_type"] == "update_asset_supply_cap" else 64
            if (
                _static_address_argument(data, 0) == proxy
                and _static_address_argument(data, 1) == asset
                and _static_integer_argument(data, 2, bits) == new_value
            ):
                setter_matches.append(node)
        if (
            node.get("type") == "CALL"
            and to_address == CONFIGURATOR
            and selector == DEPLOY_SELECTOR
            and len(data) == 36
            and _static_address_argument(data, 0) == proxy
        ):
            deploy_matches.append(node)
        if (
            node.get("type") == "CALL"
            and to_address == admin_address
            and selector in ADMIN_DEPLOY_SELECTORS
            and len(data) >= 68
            and _static_address_argument(data, 0) == CONFIGURATOR
            and _static_address_argument(data, 1) == proxy
        ):
            admin_matches.append(node)
        if (
            node.get("type") == "CALL"
            and to_address == proxy
            and selector in PROXY_UPGRADE_SELECTORS
            and len(data) >= 36
            and _static_address_argument(data, 0) == implementation
        ):
            upgrade_matches.append(node)
    groups = {
        "exact_configurator_setter": setter_matches,
        "exact_configurator_deploy": deploy_matches,
        "exact_proxy_admin_deploy_and_upgrade": admin_matches,
        "exact_target_proxy_upgrade": upgrade_matches,
    }
    required_paths = [tuple(cast(list[int], node["path"])) for matches in groups.values() for node in matches]
    stateful_types = {"CALL", "CALLCODE", "DELEGATECALL", "CREATE", "CREATE2"}
    unclassified: list[dict[str, object]] = []
    for node in nodes:
        if node.get("success") is not True or node.get("type") not in stateful_types:
            continue
        path = tuple(cast(list[int], node["path"]))
        in_cone = any(
            _path_prefix(path, required_path) or _path_prefix(required_path, path)
            for required_path in required_paths
        )
        if not in_cone:
            unclassified.append(
                {
                    "path": node["path"],
                    "type": node["type"],
                    "to": node["to"],
                    "selector": node["selector"],
                    "input_sha256": node["input_sha256"],
                }
            )
    counts = {key: len(value) for key, value in groups.items()}
    exact_required_call_counts = all(value == 1 for value in counts.values())
    topology_conforms = False
    if exact_required_call_counts:
        admin_path = tuple(cast(list[int], admin_matches[0]["path"]))
        deploy_path = tuple(cast(list[int], deploy_matches[0]["path"]))
        upgrade_path = tuple(cast(list[int], upgrade_matches[0]["path"]))
        topology_conforms = (
            len(admin_path) < len(deploy_path)
            and len(admin_path) < len(upgrade_path)
            and _path_prefix(admin_path, deploy_path)
            and _path_prefix(admin_path, upgrade_path)
            and deploy_matches[0]["from"] == admin_address
            and upgrade_matches[0]["from"] == admin_address
        )
    exact_required_calls = exact_required_call_counts and topology_conforms
    return {
        "root_matches_transaction": root_matches,
        "trace_node_count": len(nodes),
        "trace_input_byte_count": sum(cast(int, node["input_byte_count"]) for node in nodes),
        "required_call_counts": counts,
        "required_call_paths": {key: [node["path"] for node in value] for key, value in groups.items()},
        "exact_required_call_counts": exact_required_call_counts,
        "required_call_topology_conforms": topology_conforms,
        "exact_required_calls": exact_required_calls,
        "unclassified_successful_stateful_calls": unclassified,
        "payload_call_cone_isolated": exact_required_calls and not unclassified,
    }


def _receipt_matches_d0(
    receipt: Mapping[str, object],
    parent_rows: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    receipt_logs = cast(Sequence[Mapping[str, object]], receipt["logs"])
    by_key = {
        (item["block_hash"], item["transaction_hash"], item["log_index"]): item for item in receipt_logs
    }
    missing: list[tuple[object, object, object]] = []
    mismatched: list[tuple[object, object, object]] = []
    expected_keys: set[tuple[object, object, object]] = set()
    for parent in parent_rows:
        key = (parent["block_hash"], parent["transaction_hash"], parent["log_index"])
        expected_keys.add(key)
        observed = by_key.get(key)
        if observed is None:
            missing.append(key)
        elif observed.get("governance_record") != dict(parent):
            mismatched.append(key)
    relevant_addresses = {CONFIGURATOR, *MARKET_BY_PROXY}
    extra_relevant = [
        (item["block_hash"], item["transaction_hash"], item["log_index"])
        for item in receipt_logs
        if item["address"] in relevant_addresses
        and (item["block_hash"], item["transaction_hash"], item["log_index"]) not in expected_keys
    ]
    return {
        "expected_d0_log_count": len(parent_rows),
        "missing_d0_log_keys": missing,
        "mismatched_d0_log_keys": mismatched,
        "extra_relevant_log_keys": extra_relevant,
        "d0_logs_conform": not missing and not mismatched and not extra_relevant,
    }


def _beacon_finalized_execution(value: object) -> dict[str, object]:
    response = _mapping(value)
    if response is None:
        raise ValueError("Beacon finality response must be a mapping")
    if response.get("execution_optimistic") is True:
        raise ValueError("Beacon finality response is execution optimistic")
    data = _mapping(response.get("data"))
    finalized_header = _mapping(data.get("finalized_header") if data is not None else None)
    if finalized_header is None:
        raise ValueError("Beacon finality response lacks a finalized header")
    execution = _mapping(finalized_header.get("execution"))
    if execution is None:
        raise ValueError("Beacon finality response lacks a finalized execution header")
    number_value = execution.get("block_number")
    if not isinstance(number_value, str) or re.fullmatch(r"0|[1-9][0-9]*", number_value) is None:
        raise ValueError("Beacon finalized execution block number is not canonical decimal")
    beacon = _mapping(finalized_header.get("beacon"))
    slot_value = beacon.get("slot") if beacon is not None else None
    if not isinstance(slot_value, str) or re.fullmatch(r"0|[1-9][0-9]*", slot_value) is None:
        raise ValueError("Beacon finalized slot is not canonical decimal")
    return {
        "block_number": int(number_value),
        "block_hash": normalize_hash(execution.get("block_hash"), path="beacon.execution.block_hash"),
        "beacon_slot": int(slot_value),
        "version": response.get("version"),
        "execution_optimistic": response.get("execution_optimistic"),
    }


def _changed_field(event_type: str) -> str:
    return {
        "update_asset_borrow_collateral_factor": "borrow_collateral_factor",
        "update_asset_liquidate_collateral_factor": "liquidate_collateral_factor",
        "update_asset_supply_cap": "supply_cap",
    }[event_type]


def _getter_conformance(
    pre: Mapping[str, object], post: Mapping[str, object], candidate: Mapping[str, object]
) -> dict[str, object]:
    changed = _changed_field(cast(str, candidate["event_type"]))
    fields = set(pre)
    unchanged = sorted(field for field in fields if field != changed and pre[field] == post[field])
    changed_fields = sorted(field for field in fields if pre[field] != post[field])
    return {
        "declared_changed_field": changed,
        "observed_changed_fields": changed_fields,
        "unchanged_field_count": len(unchanged),
        "pre_value_matches_event": pre[changed] == candidate["old_value"],
        "post_value_matches_event": post[changed] == candidate["new_value"],
        "only_declared_field_changed": changed_fields == [changed],
        "exact_getter_conformance": pre[changed] == candidate["old_value"]
        and post[changed] == candidate["new_value"]
        and changed_fields == [changed],
    }


def expected_operation_plan(
    manifest: Mapping[str, object],
    *,
    beacon_finalized_block_number: int,
    implementation_addresses: Mapping[str, tuple[str, str]] | None = None,
) -> list[dict[str, object]]:
    """Build the exact ordered plan, with optional response-derived code addresses."""

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

    rpc("publicnode_execution", "chain_id", "eth_chainId", [])
    rpc(
        "publicnode_execution",
        "execution_finalized_header",
        "eth_getBlockByNumber",
        ["finalized", False],
    )
    plan.append(
        {
            "operation_type": "beacon_rest",
            "provider": "publicnode_beacon",
            "label": "beacon_finality_update",
            "path": BEACON_PATH,
        }
    )
    rpc(
        "publicnode_execution",
        "beacon_execution_header_replica",
        "eth_getBlockByNumber",
        [hex(beacon_finalized_block_number), False],
    )
    contamination = cast(Mapping[str, object], manifest["contamination_contract"])
    for block_number in cast(Sequence[int], contamination["unique_neighbor_blocks_requiring_headers"]):
        rpc(
            "blockscout",
            f"contamination_neighbor_header:{block_number}",
            "eth_getBlockByNumber",
            [hex(block_number), False],
        )
    for candidate in cast(Sequence[Mapping[str, object]], manifest["candidates"]):
        candidate_id = cast(str, candidate["candidate_id"])
        transaction_hash = cast(str, candidate["transaction_hash"])
        block_number = cast(int, candidate["block_number"])
        pre_block = block_number - 1
        proxy = cast(str, candidate["comet_proxy"])
        asset = cast(str, candidate["asset"])
        code_addresses = (
            ("__OLD_IMPLEMENTATION_FROM_PRE_SLOT__", "__NEW_IMPLEMENTATION_FROM_POST_SLOT__")
            if implementation_addresses is None
            else implementation_addresses[candidate_id]
        )
        rpc(
            "blockscout",
            f"{candidate_id}:transaction",
            "eth_getTransactionByHash",
            [transaction_hash],
        )
        rpc(
            "blockscout",
            f"{candidate_id}:receipt",
            "eth_getTransactionReceipt",
            [transaction_hash],
        )
        rpc(
            "blockscout",
            f"{candidate_id}:blockscout_header",
            "eth_getBlockByNumber",
            [hex(block_number), False],
        )
        rpc(
            "publicnode_execution",
            f"{candidate_id}:publicnode_header",
            "eth_getBlockByNumber",
            [hex(block_number), False],
        )
        rpc(
            "publicnode_execution",
            f"{candidate_id}:call_trace",
            "debug_traceTransaction",
            [transaction_hash, TRACE_CONFIG],
        )
        for suffix, slot, height in (
            ("implementation_pre", IMPLEMENTATION_SLOT, pre_block),
            ("implementation_post", IMPLEMENTATION_SLOT, block_number),
            ("admin_pre", ADMIN_SLOT, pre_block),
            ("admin_post", ADMIN_SLOT, block_number),
        ):
            rpc(
                "blockscout",
                f"{candidate_id}:{suffix}",
                "eth_getStorageAt",
                [proxy, slot, hex(height)],
            )
        for suffix, implementation, height in (
            ("old_implementation_code", code_addresses[0], pre_block),
            ("new_implementation_code", code_addresses[1], block_number),
        ):
            rpc(
                "blockscout",
                f"{candidate_id}:{suffix}",
                "eth_getCode",
                [implementation, hex(height)],
            )
        asset_call = {"to": proxy, "data": _call_data(GET_ASSET_INFO_SELECTOR, asset)}
        rpc(
            "blockscout",
            f"{candidate_id}:asset_info_pre",
            "eth_call",
            [asset_call, hex(pre_block)],
        )
        rpc(
            "blockscout",
            f"{candidate_id}:asset_info_post",
            "eth_call",
            [asset_call, hex(block_number)],
        )
    return plan


def _observed_operation_plan(records: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    plan: list[dict[str, object]] = []
    for record in records:
        operation_type = cast(str, record["operation_type"])
        projected = {
            "operation_type": operation_type,
            "provider": record["provider"],
            "label": record["label"],
        }
        if operation_type == "json_rpc":
            projected.update({"method": record["method"], "params": record["params"]})
        else:
            projected["path"] = record["path"]
        plan.append(projected)
    return plan


def collect_candidate_mechanics(
    manifest: Mapping[str, object], *, root: str | Path = "."
) -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, object]]]:
    """Execute the frozen all-candidate mechanics audit."""

    errors = validate_candidate_mechanics(manifest)
    errors.extend(validate_parent_evidence(manifest, root))
    if errors:
        raise ValueError("invalid candidate mechanics manifest: " + "; ".join(sorted(set(errors))))
    root_path = Path(root)
    parents = cast(Mapping[str, object], manifest["parents"])
    d0_inventory = _read_json_mapping_list(root_path / cast(str, parents["d0_inventory_path"]))
    d0_by_tx: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in d0_inventory:
        d0_by_tx[cast(str, row["transaction_hash"])].append(row)

    sources = cast(Mapping[str, object], manifest["sources"])
    transport = HttpTransport(
        user_agent=cast(str, sources["user_agent"]),
        maximum_requests_per_second=float(cast(int, sources["maximum_requests_per_second_across_sources"])),
        maximum_transport_retries=cast(int, sources["maximum_transport_retries"]),
        maximum_http_attempts=cast(int, sources["maximum_http_attempts"]),
        maximum_response_bytes=cast(int, sources["maximum_response_bytes"]),
    )
    public_url = cast(str, sources["publicnode_rpc_url"])
    blockscout_url = cast(str, sources["blockscout_rpc_url"])
    beacon_url = cast(str, sources["publicnode_beacon_url"])
    chain_id = transport.rpc_call(
        url=public_url,
        provider="publicnode_execution",
        label="chain_id",
        method="eth_chainId",
        params=[],
    )
    finalized_tag = _block_record(
        transport.rpc_call(
            url=public_url,
            provider="publicnode_execution",
            label="execution_finalized_header",
            method="eth_getBlockByNumber",
            params=["finalized", False],
        ),
        expected_number=None,
        path="execution_finalized_header",
    )
    beacon_finality = _beacon_finalized_execution(
        transport.beacon_get(base_url=beacon_url, path=BEACON_PATH, label="beacon_finality_update")
    )
    beacon_explicit = _block_record(
        transport.rpc_call(
            url=public_url,
            provider="publicnode_execution",
            label="beacon_execution_header_replica",
            method="eth_getBlockByNumber",
            params=[hex(cast(int, beacon_finality["block_number"])), False],
        ),
        expected_number=cast(int, beacon_finality["block_number"]),
        path="beacon_execution_header_replica",
    )
    contamination = cast(Mapping[str, object], manifest["contamination_contract"])
    neighbor_headers: dict[int, dict[str, object]] = {}
    for block_number in cast(Sequence[int], contamination["unique_neighbor_blocks_requiring_headers"]):
        neighbor_headers[block_number] = _block_record(
            transport.rpc_call(
                url=blockscout_url,
                provider="blockscout",
                label=f"contamination_neighbor_header:{block_number}",
                method="eth_getBlockByNumber",
                params=[hex(block_number), False],
            ),
            expected_number=block_number,
            path=f"contamination_neighbor_header:{block_number}",
        )

    candidate_results: list[dict[str, object]] = []
    candidates = cast(Sequence[Mapping[str, object]], manifest["candidates"])
    maximum_logs = cast(int, sources["maximum_receipt_logs"])
    maximum_nodes = cast(int, sources["maximum_trace_nodes"])
    maximum_input_bytes = cast(int, sources["maximum_trace_input_bytes"])
    consumed_receipt_logs = 0
    consumed_trace_nodes = 0
    consumed_trace_input_bytes = 0
    for candidate in candidates:
        candidate_id = cast(str, candidate["candidate_id"])
        transaction_hash = cast(str, candidate["transaction_hash"])
        block_number = cast(int, candidate["block_number"])
        proxy = cast(str, candidate["comet_proxy"])
        asset = cast(str, candidate["asset"])
        transaction = _transaction_record(
            transport.rpc_call(
                url=blockscout_url,
                provider="blockscout",
                label=f"{candidate_id}:transaction",
                method="eth_getTransactionByHash",
                params=[transaction_hash],
            ),
            candidate=candidate,
        )
        receipt = _receipt_record(
            transport.rpc_call(
                url=blockscout_url,
                provider="blockscout",
                label=f"{candidate_id}:receipt",
                method="eth_getTransactionReceipt",
                params=[transaction_hash],
            ),
            candidate=candidate,
            maximum_logs=maximum_logs - consumed_receipt_logs,
        )
        consumed_receipt_logs += cast(int, receipt["log_count"])
        blockscout_header = _block_record(
            transport.rpc_call(
                url=blockscout_url,
                provider="blockscout",
                label=f"{candidate_id}:blockscout_header",
                method="eth_getBlockByNumber",
                params=[hex(block_number), False],
            ),
            expected_number=block_number,
            path=f"{candidate_id}:blockscout_header",
        )
        public_header = _block_record(
            transport.rpc_call(
                url=public_url,
                provider="publicnode_execution",
                label=f"{candidate_id}:publicnode_header",
                method="eth_getBlockByNumber",
                params=[hex(block_number), False],
            ),
            expected_number=block_number,
            path=f"{candidate_id}:publicnode_header",
        )
        trace_nodes = normalize_call_trace(
            transport.rpc_call(
                url=public_url,
                provider="publicnode_execution",
                label=f"{candidate_id}:call_trace",
                method="debug_traceTransaction",
                params=[transaction_hash, TRACE_CONFIG],
            ),
            maximum_nodes=maximum_nodes - consumed_trace_nodes,
            maximum_input_bytes=maximum_input_bytes - consumed_trace_input_bytes,
        )
        consumed_trace_nodes += len(trace_nodes)
        consumed_trace_input_bytes += sum(cast(int, node["input_byte_count"]) for node in trace_nodes)
        pre_block = block_number - 1
        old_implementation = _storage_address(
            transport.rpc_call(
                url=blockscout_url,
                provider="blockscout",
                label=f"{candidate_id}:implementation_pre",
                method="eth_getStorageAt",
                params=[proxy, IMPLEMENTATION_SLOT, hex(pre_block)],
            ),
            path=f"{candidate_id}:implementation_pre",
        )
        new_implementation = _storage_address(
            transport.rpc_call(
                url=blockscout_url,
                provider="blockscout",
                label=f"{candidate_id}:implementation_post",
                method="eth_getStorageAt",
                params=[proxy, IMPLEMENTATION_SLOT, hex(block_number)],
            ),
            path=f"{candidate_id}:implementation_post",
        )
        old_admin = _storage_address(
            transport.rpc_call(
                url=blockscout_url,
                provider="blockscout",
                label=f"{candidate_id}:admin_pre",
                method="eth_getStorageAt",
                params=[proxy, ADMIN_SLOT, hex(pre_block)],
            ),
            path=f"{candidate_id}:admin_pre",
        )
        new_admin = _storage_address(
            transport.rpc_call(
                url=blockscout_url,
                provider="blockscout",
                label=f"{candidate_id}:admin_post",
                method="eth_getStorageAt",
                params=[proxy, ADMIN_SLOT, hex(block_number)],
            ),
            path=f"{candidate_id}:admin_post",
        )
        old_code = _hex_bytes(
            transport.rpc_call(
                url=blockscout_url,
                provider="blockscout",
                label=f"{candidate_id}:old_implementation_code",
                method="eth_getCode",
                params=[old_implementation, hex(pre_block)],
            ),
            path=f"{candidate_id}:old_implementation_code",
        )
        new_code = _hex_bytes(
            transport.rpc_call(
                url=blockscout_url,
                provider="blockscout",
                label=f"{candidate_id}:new_implementation_code",
                method="eth_getCode",
                params=[new_implementation, hex(block_number)],
            ),
            path=f"{candidate_id}:new_implementation_code",
        )
        asset_call = {"to": proxy, "data": _call_data(GET_ASSET_INFO_SELECTOR, asset)}
        pre_asset = decode_asset_info(
            transport.rpc_call(
                url=blockscout_url,
                provider="blockscout",
                label=f"{candidate_id}:asset_info_pre",
                method="eth_call",
                params=[asset_call, hex(pre_block)],
            ),
            expected_asset=asset,
        )
        post_asset = decode_asset_info(
            transport.rpc_call(
                url=blockscout_url,
                provider="blockscout",
                label=f"{candidate_id}:asset_info_post",
                method="eth_call",
                params=[asset_call, hex(block_number)],
            ),
            expected_asset=asset,
        )
        trace_analysis = analyze_mechanism_trace(
            trace_nodes,
            transaction=transaction,
            candidate=candidate,
            admin_address=old_admin,
        )
        receipt_match = _receipt_matches_d0(receipt, d0_by_tx[transaction_hash])
        getter_match = _getter_conformance(pre_asset, post_asset, candidate)
        cross_provider = (
            blockscout_header["hash"]
            == public_header["hash"]
            == transaction["block_hash"]
            == receipt["block_hash"]
            and blockscout_header["timestamp_unix"] == public_header["timestamp_unix"]
        )
        proxy_state = {
            "old_implementation": old_implementation,
            "new_implementation": new_implementation,
            "expected_new_implementation": candidate["implementation"],
            "old_admin": old_admin,
            "new_admin": new_admin,
            "old_code_byte_count": len(old_code),
            "new_code_byte_count": len(new_code),
            "old_code_sha256": hashlib.sha256(old_code).hexdigest(),
            "new_code_sha256": hashlib.sha256(new_code).hexdigest(),
            "conforms": old_implementation != new_implementation
            and new_implementation == candidate["implementation"]
            and old_admin == new_admin
            and old_admin != "0x" + "0" * 40
            and bool(old_code)
            and bool(new_code),
        }
        neighbor_evidence: list[dict[str, object]] = []
        contaminated = False
        for neighbor_block in cast(Sequence[int], candidate["nearby_other_governance_blocks"]):
            if neighbor_block == block_number:
                difference = 0
            else:
                difference = abs(
                    cast(int, neighbor_headers[neighbor_block]["timestamp_unix"])
                    - cast(int, public_header["timestamp_unix"])
                )
            inside = difference <= cast(int, contamination["window_seconds"])
            contaminated = contaminated or inside
            neighbor_evidence.append(
                {
                    "block_number": neighbor_block,
                    "absolute_time_difference_seconds": difference,
                    "inside_window": inside,
                }
            )
        finality_ok = block_number < cast(int, finalized_tag["number"]) and block_number < cast(
            int, beacon_finality["block_number"]
        )
        checks = {
            "transaction_receipt_success_and_identity": receipt["status"] == 1
            and transaction["block_hash"] == receipt["block_hash"]
            and transaction["transaction_index"] == receipt["transaction_index"]
            and transaction["from"] == receipt["from"]
            and transaction["to"] == receipt["to"],
            "receipt_matches_complete_d0_relevant_logs": receipt_match["d0_logs_conform"],
            "cross_provider_header_identity": cross_provider,
            "trace_root_matches_transaction": trace_analysis["root_matches_transaction"],
            "exact_required_mechanism_calls": trace_analysis["exact_required_calls"],
            "payload_call_cone_isolated": trace_analysis["payload_call_cone_isolated"],
            "proxy_implementation_admin_and_code_conform": proxy_state["conforms"],
            "pre_post_asset_getter_conforms": getter_match["exact_getter_conformance"],
            "clean_twenty_four_hour_governance_neighborhood": not contaminated,
            "candidate_precedes_both_finalized_headers": finality_ok,
        }
        candidate_results.append(
            {
                "candidate": dict(candidate),
                "transaction": transaction,
                "receipt": receipt,
                "block_headers": {
                    "blockscout": blockscout_header,
                    "publicnode": public_header,
                },
                "trace_nodes": trace_nodes,
                "trace_analysis": trace_analysis,
                "receipt_d0_conformance": receipt_match,
                "proxy_state": proxy_state,
                "asset_info_pre": pre_asset,
                "asset_info_post": post_asset,
                "getter_conformance": getter_match,
                "contamination_evidence": neighbor_evidence,
                "checks": checks,
                "fully_conforming_candidate": all(checks.values()),
            }
        )

    beacon_matches_explicit = (
        beacon_explicit["number"] == beacon_finality["block_number"]
        and beacon_explicit["hash"] == beacon_finality["block_hash"]
    )
    max_candidate_block = max(cast(int, item["block_number"]) for item in candidates)
    finality_sources = (
        chain_id == "0x1"
        and cast(int, finalized_tag["number"]) > max_candidate_block
        and cast(int, beacon_finality["block_number"]) > max_candidate_block
        and beacon_matches_explicit
    )
    rpc_records = [record for record in transport.records if record["operation_type"] == "json_rpc"]
    beacon_records = [record for record in transport.records if record["operation_type"] == "beacon_rest"]
    method_counts = dict(sorted(Counter(cast(str, item["method"]) for item in rpc_records).items()))
    provider_counts = dict(sorted(Counter(cast(str, item["provider"]) for item in transport.records).items()))
    expected = cast(Mapping[str, object], manifest["expected_request_contract"])
    implementation_addresses = {
        cast(str, candidate["candidate_id"]): (
            cast(str, cast(Mapping[str, object], result["proxy_state"])["old_implementation"]),
            cast(str, cast(Mapping[str, object], result["proxy_state"])["new_implementation"]),
        )
        for result, candidate in zip(candidate_results, candidates, strict=True)
    }
    expected_plan = expected_operation_plan(
        manifest,
        beacon_finalized_block_number=cast(int, beacon_finality["block_number"]),
        implementation_addresses=implementation_addresses,
    )
    operation_order_matches = _observed_operation_plan(transport.records) == expected_plan
    exact_requests = (
        len(rpc_records) == expected["json_rpc_success_count_without_retry"]
        and len(beacon_records) == expected["beacon_success_count_without_retry"]
        and len(transport.records) == expected["network_operation_count_without_retry"]
        and method_counts == expected["method_counts"]
        and provider_counts == expected["provider_counts"]
        and operation_order_matches
    )
    total_trace_nodes = sum(len(cast(Sequence[object], item["trace_nodes"])) for item in candidate_results)
    total_trace_input_bytes = sum(
        cast(int, cast(Mapping[str, object], item["trace_analysis"])["trace_input_byte_count"])
        for item in candidate_results
    )
    total_receipt_logs = sum(
        cast(int, cast(Mapping[str, object], item["receipt"])["log_count"]) for item in candidate_results
    )
    fully_conforming = [
        cast(Mapping[str, object], item["candidate"])
        for item in candidate_results
        if item["fully_conforming_candidate"] is True
    ]
    access = cast(Mapping[str, object], manifest["access_boundary"])
    access_ok = all(access.get(key) is True for key in ACCESS_TRUE) and all(
        access.get(key) is False for key in ACCESS_FALSE
    )
    gates = {
        "parent_hashes_and_exact_candidate_derivation": True,
        "ethereum_chain_and_finality_sources": finality_sources,
        "exact_complete_request_plan": exact_requests,
        "all_receipts_and_d0_logs_conform": all(
            cast(Mapping[str, object], item["checks"])["transaction_receipt_success_and_identity"] is True
            and cast(Mapping[str, object], item["checks"])["receipt_matches_complete_d0_relevant_logs"]
            is True
            for item in candidate_results
        ),
        "cross_provider_candidate_headers": all(
            cast(Mapping[str, object], item["checks"])["cross_provider_header_identity"] is True
            for item in candidate_results
        ),
        "complete_call_traces": all(
            cast(Mapping[str, object], item["checks"])["trace_root_matches_transaction"] is True
            for item in candidate_results
        ),
        "candidate_mechanism_call_cones_evaluated": len(candidate_results) == 14,
        "pre_post_getter_and_proxy_state_evaluated": len(candidate_results) == 14,
        "contamination_windows_evaluated": len(candidate_results) == 14,
        "at_least_one_fully_conforming_candidate": len(fully_conforming) >= 1,
        "request_trace_and_byte_caps": transport.http_attempts <= cast(int, sources["maximum_http_attempts"])
        and transport.response_bytes <= cast(int, sources["maximum_response_bytes"])
        and total_trace_nodes <= cast(int, sources["maximum_trace_nodes"])
        and total_trace_input_bytes <= cast(int, sources["maximum_trace_input_bytes"])
        and total_receipt_logs <= cast(int, sources["maximum_receipt_logs"]),
        "participant_data_access_boundary": access_ok,
    }
    policy = cast(Mapping[str, object], manifest["decision_policy"])
    passed = set(gates) == set(cast(Sequence[str], manifest["gates"])) and all(gates.values())
    slim_candidates = [
        {
            "candidate_id": cast(Mapping[str, object], item["candidate"])["candidate_id"],
            "priority_rank": cast(Mapping[str, object], item["candidate"])["priority_rank"],
            "block_number": cast(Mapping[str, object], item["candidate"])["block_number"],
            "event_type": cast(Mapping[str, object], item["candidate"])["event_type"],
            "market_id": cast(Mapping[str, object], item["candidate"])["market_id"],
            "asset": cast(Mapping[str, object], item["candidate"])["asset"],
            "checks": item["checks"],
            "fully_conforming_candidate": item["fully_conforming_candidate"],
            "trace_node_count": cast(Mapping[str, object], item["trace_analysis"])["trace_node_count"],
            "unclassified_stateful_call_count": len(
                cast(
                    Sequence[object],
                    cast(Mapping[str, object], item["trace_analysis"])[
                        "unclassified_successful_stateful_calls"
                    ],
                )
            ),
        }
        for item in candidate_results
    ]
    summary = {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "audit_id": manifest["audit_id"],
        "as_of": manifest["as_of"],
        "parents": manifest["parents"],
        "finality": {
            "execution_finalized_tag": finalized_tag,
            "beacon_finalized_execution": beacon_finality,
            "beacon_explicit_execution_replica": beacon_explicit,
            "beacon_matches_explicit_execution": beacon_matches_explicit,
            "local_bls_signature_verification_performed": False,
        },
        "contamination_neighbor_headers": {
            str(key): value for key, value in sorted(neighbor_headers.items())
        },
        "candidate_summary": {
            "audited_count": len(candidate_results),
            "fully_conforming_count": len(fully_conforming),
            "fully_conforming_candidate_ids": [item["candidate_id"] for item in fully_conforming],
            "records": slim_candidates,
        },
        "request_summary": {
            "successful_json_rpc_count": len(rpc_records),
            "successful_beacon_count": len(beacon_records),
            "http_attempt_count": transport.http_attempts,
            "response_byte_count": transport.response_bytes,
            "method_counts": method_counts,
            "provider_counts": provider_counts,
            "operation_order_matches_frozen_plan": operation_order_matches,
            "all_one_attempt": all(item["attempt_count"] == 1 for item in transport.records),
            "trace_node_count": total_trace_nodes,
            "trace_input_byte_count": total_trace_input_bytes,
            "receipt_log_count": total_receipt_logs,
        },
        "access_boundary": manifest["access_boundary"],
        "gates": gates,
        "gate_counts": {"pass": sum(gates.values()), "fail": sum(not value for value in gates.values())},
        "decision": policy["pass"] if passed else policy["fail"],
        "authorized_next_stage": policy["authorized_next_stage"] if passed else None,
        "limitations": manifest["limitations"],
    }
    return summary, candidate_results, transport.records


def _git_value(root: Path, args: Sequence[str]) -> str:
    result = subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--response-hashes", type=Path, required=True)
    parser.add_argument("--collection-commit")
    return parser


def main() -> None:
    """Run the frozen candidate-mechanics audit from a clean exact worktree."""

    args = _build_parser().parse_args()
    for output in (args.summary, args.candidates, args.response_hashes):
        if output.exists():
            raise FileExistsError(f"refusing to overwrite {output}")
    root = Path.cwd()
    current_commit = _git_value(root, ["rev-parse", "HEAD"])
    if _git_value(root, ["status", "--porcelain"]):
        raise RuntimeError("collection worktree must be clean")
    if args.collection_commit is not None and args.collection_commit != current_commit:
        raise ValueError("collection commit must equal the clean worktree HEAD")
    manifest = load_candidate_mechanics(args.manifest)
    summary, candidates, responses = collect_candidate_mechanics(manifest, root=root)
    summary["collection_commit"] = current_commit
    summary["manifest_sha256"] = hashlib.sha256(args.manifest.read_bytes()).hexdigest()
    for output in (args.summary, args.candidates, args.response_hashes):
        output.parent.mkdir(parents=True, exist_ok=True)
    _write_json(args.candidates, candidates)
    _write_json(args.response_hashes, responses)
    _write_json(args.summary, summary)
    print(
        json.dumps(
            {
                "decision": summary["decision"],
                "fully_conforming_candidates": cast(Mapping[str, object], summary["candidate_summary"])[
                    "fully_conforming_count"
                ],
                "network_operations": len(responses),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
