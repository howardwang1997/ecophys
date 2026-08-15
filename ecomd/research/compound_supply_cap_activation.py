"""Zero-account activation audit for mechanics-conforming Compound III supply-cap events."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import yaml

from ecomd.research.compound_candidate_mechanics import HttpTransport, decode_asset_info
from ecomd.research.compound_governance_inventory import (
    decode_quantity,
    normalize_address,
    normalize_hash,
)
from ecomd.research.compound_v3_chain_metadata import canonical_json_sha256

SCHEMA_VERSION = "ecophys-compound-v3-supply-cap-activation-preflight/v1"
ARTIFACT_SCHEMA_VERSION = "ecophys-compound-v3-supply-cap-activation-audit/v1"
FAILURE_SCHEMA_VERSION = "ecophys-compound-v3-supply-cap-activation-failure/v1"
AUDIT_ID = "compound_v3_mainnet_supply_cap_activation_preflight_v1"
AS_OF = "2026-08-16"
STAGE = "verified_source_historical_aggregate_cap_activation_only"
SMART_CONTRACT_PATH_TEMPLATE = "/api/v2/smart-contracts/{address_hash}"
GET_ASSET_INFO_SELECTOR = "0x3b3bec2e"
TOTALS_COLLATERAL_SELECTOR = "0x59e017bd"
LOOKBACK_BLOCK_OFFSETS = (1, 300, 1_800, 7_200, 21_600, 50_400)
UTILIZATION_THRESHOLDS_PPM = (900_000, 950_000, 990_000)

FROZEN_CANDIDATE_IDS = (
    "supply_cap_16133171_5c9dacfa",
    "supply_cap_16520572_f626c068",
    "supply_cap_16549206_b96f2c61",
    "supply_cap_16668519_f803c13b",
)
FROZEN_IMPLEMENTATIONS = (
    {
        "address": "0x528c57a87706c31765001779168b42f24c694e1b",
        "code_sha256": "71886156895b77afe186394a0b08f281dadb34f670485150ee5d1b736f52334c",
    },
    {
        "address": "0x9a759bc2d5248b1da689c642ad2ca3383657361c",
        "code_sha256": "1944a836893fb7569d7687d7d6de4b6dcfd55160130a7b3d1e4e9d4930a98a15",
    },
    {
        "address": "0xc82f17fe345047739ee5a77687ff8700a0ecb37d",
        "code_sha256": "2ef1e6f03d4d4d5ffc29ff5297cfb4e640196f9bb74b62f342ecc073b732deb6",
    },
    {
        "address": "0x77708e0fee45cb9d177174b260a04beda47d0495",
        "code_sha256": "a47a38f6bf0b8c8e8c323045d6c94c7434da14096b0be920bc9b394fd419d59c",
    },
    {
        "address": "0x1a7e64b593a9b8796e88a7489a2ceb6d079c850d",
        "code_sha256": "d816e8fd0047318be367b1854d19f521e05defd2c1a1f2aba5bd72b3378bf3c2",
    },
    {
        "address": "0x9c1213b63a587658aa46647226068e68dfae5e1e",
        "code_sha256": "03917214699b9781068691fc5ad366c54fabe1a8ebc0bccff340b33db479a4ab",
    },
    {
        "address": "0xbf1f8be5405b184b0cc5ec0fb74839442c6fa1a1",
        "code_sha256": "c892c63fb5eb1d44af58fdeecb1ffdcfadddecebe8cce3f52ca779c023cde411",
    },
)
FROZEN_PARENTS = {
    "mechanics_manifest_path": "data/manifests/compound_v3_candidate_mechanics_preflight_v2.yaml",
    "mechanics_manifest_sha256": "47ef0fab151a532e0fdc4fce2689d67179ccf8b5d1ba22276f7c3d5e8ffe3738",
    "mechanics_protocol_commit": "c7f770a938abe9f0e8452c9bda84bb8ed69f2e5e",
    "mechanics_result_path": "experiments/v14_compound_v3_candidate_mechanics_preflight/RESULTS_V2.md",
    "mechanics_result_sha256": "6bcd3a64b9dc6537f78f05a04c7818f697133f9a06f5e9ea87237cb7fbe2cc31",
    "mechanics_result_commit": "4c8b5e2888fd8fd13774c3d2368f9b96fa78624b",
    "mechanics_summary_path": (
        "experiments/v14_compound_v3_candidate_mechanics_preflight/artifacts_v2/summary.json"
    ),
    "mechanics_summary_sha256": "83e32d0e07ac395d02a9d8a8e385633545a605f62d778f60071e424e32923474",
    "mechanics_candidates_path": (
        "experiments/v14_compound_v3_candidate_mechanics_preflight/artifacts_v2/candidates.json"
    ),
    "mechanics_candidates_sha256": ("553055dae591daab0ef662b02d7e32a98d726fd154a5f43d34575ca3f31160d5"),
    "mechanics_http_evidence_path": (
        "experiments/v14_compound_v3_candidate_mechanics_preflight/artifacts_v2/http_evidence.json"
    ),
    "mechanics_http_evidence_sha256": ("814e66afe43f06cc19b99426f9b7408ccbc423f65e051fcd63de7cbaf5844b87"),
    "metadata_summary_path": "experiments/v14_compound_v3_metadata_preflight/artifacts/summary.json",
    "metadata_summary_sha256": "643edb6750ab5567528a9754bdf92b84143deaa82a9225a9c8ea9730e0d81e11",
    "official_source_commit": "f766f51583c23acc33b2a7824654ef2029a96804",
}
SOURCE_MARKERS = (
    "structTotalsCollateral{uint128totalSupplyAsset;uint128_reserved;}",
    "mapping(address=>TotalsCollateral)publictotalsCollateral;",
    "TotalsCollateralmemorytotals=totalsCollateral[asset];",
    "totals.totalSupplyAsset+=amount;",
    "if(totals.totalSupplyAsset>assetInfo.supplyCap)revertSupplyCapExceeded();",
    "totalsCollateral[asset]=totals;",
)
REQUIRED_INTEGRITY_GATES = frozenset(
    {
        "parent_hashes_and_exact_survivor_derivation",
        "ethereum_mainnet_provider_identity",
        "all_historical_implementations_source_conform",
        "publicnode_runtime_code_reproduces_parent",
        "historical_configuration_getters_replicate",
        "aggregate_totals_cross_provider_and_within_cap",
        "all_candidates_evaluated",
        "exact_complete_request_plan",
        "request_and_source_resource_caps",
        "zero_account_and_response_access_boundary",
    }
)
ACCESS_TRUE = frozenset(
    {
        "mechanics_parent_opened",
        "chain_rpc_used",
        "verified_contract_source_metadata_opened",
        "historical_block_headers_opened",
        "implementation_code_opened_for_hashing",
        "configuration_getter_rows_opened",
        "aggregate_market_collateral_state_rows_opened",
    }
)
ACCESS_FALSE = frozenset(
    {
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
        "official_source_contract",
        "activation_contract",
        "expected_request_contract",
        "failure_artifact_contract",
        "integrity_gates",
        "decision_policy",
        "limitations",
    }
)
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


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


def _reject_duplicate_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _read_json(path: Path) -> object:
    value: object = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_reject_duplicate_pairs)
    return value


def _read_json_mapping(path: Path) -> Mapping[str, object]:
    mapped = _mapping(_read_json(path))
    if mapped is None:
        raise ValueError(f"{path} must contain a JSON mapping")
    return mapped


def _read_json_mapping_list(path: Path) -> list[Mapping[str, object]]:
    mapped = _mapping_list(_read_json(path))
    if mapped is None:
        raise ValueError(f"{path} must contain a JSON list of mappings")
    return mapped


def _safe_relative_path(value: object) -> bool:
    return (
        isinstance(value, str)
        and bool(value)
        and not Path(value).is_absolute()
        and ".." not in Path(value).parts
    )


def _hex_bytes(value: object, *, path: str, allow_empty: bool = False) -> bytes:
    if not isinstance(value, str) or not value.startswith("0x"):
        raise ValueError(f"{path} must be 0x-prefixed hexadecimal bytes")
    body = value[2:]
    if len(body) % 2 != 0 or (not body and not allow_empty):
        raise ValueError(f"{path} has invalid hexadecimal length")
    try:
        return bytes.fromhex(body)
    except ValueError as error:
        raise ValueError(f"{path} contains invalid hexadecimal bytes") from error


def _address_call(selector: str, address: str) -> str:
    normalized = normalize_address(address, path="call.address")
    return selector + ("00" * 12) + normalized[2:]


def decode_totals_collateral(value: object) -> dict[str, int]:
    """Decode the exact public-mapping ABI return for TotalsCollateral."""

    payload = _hex_bytes(value, path="totals_collateral")
    if len(payload) != 64:
        raise ValueError("totals_collateral must contain exactly two ABI words")
    total_supply_asset = int.from_bytes(payload[:32], "big")
    reserved = int.from_bytes(payload[32:], "big")
    if total_supply_asset >= 2**128 or reserved >= 2**128:
        raise ValueError("totals_collateral words exceed uint128")
    if reserved != 0:
        raise ValueError("totals_collateral reserved field must be zero")
    return {"total_supply_asset": total_supply_asset, "reserved": reserved}


def _block_header(value: object, *, expected_number: int, path: str) -> dict[str, object]:
    block = _mapping(value)
    if block is None:
        raise ValueError(f"{path} must be a block mapping")
    number = decode_quantity(block.get("number"), path=f"{path}.number")
    if number != expected_number:
        raise ValueError(f"{path} number differs from requested block")
    timestamp = decode_quantity(block.get("timestamp"), path=f"{path}.timestamp")
    return {
        "number": number,
        "hash": normalize_hash(block.get("hash"), path=f"{path}.hash"),
        "timestamp_unix": timestamp,
        "timestamp_utc": datetime.fromtimestamp(timestamp, tz=UTC).isoformat().replace("+00:00", "Z"),
    }


def _strip_comments_and_whitespace(source: str) -> str:
    without_block = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    without_line = re.sub(r"//[^\r\n]*", "", without_block)
    return re.sub(r"\s+", "", without_line)


def _source_file_inventory(
    metadata: Mapping[str, object], *, maximum_files: int, maximum_bytes: int
) -> tuple[list[dict[str, object]], str]:
    primary_path = metadata.get("file_path")
    primary_source = metadata.get("source_code")
    if not isinstance(primary_path, str) or not primary_path or not isinstance(primary_source, str):
        raise ValueError("verified source primary file is missing")
    raw_files: list[tuple[str, str]] = [(primary_path, primary_source)]
    additional = metadata.get("additional_sources")
    if not isinstance(additional, list):
        raise ValueError("verified source additional_sources must be a list")
    for index, item in enumerate(additional):
        mapped = _mapping(item)
        if mapped is None:
            raise ValueError(f"additional_sources[{index}] must be a mapping")
        file_path = mapped.get("file_path")
        source_code = mapped.get("source_code")
        if not isinstance(file_path, str) or not file_path or not isinstance(source_code, str):
            raise ValueError(f"additional_sources[{index}] has invalid fields")
        raw_files.append((file_path, source_code))
    if len(raw_files) > maximum_files:
        raise ValueError("verified source file cap exceeded")
    if len({path for path, _ in raw_files}) != len(raw_files):
        raise ValueError("verified source contains duplicate file paths")
    total_bytes = sum(len(source.encode("utf-8")) for _, source in raw_files)
    if total_bytes > maximum_bytes:
        raise ValueError("verified source text-byte cap exceeded")
    ordered = sorted(raw_files)
    inventory = [
        {
            "path": path,
            "byte_count": len(source.encode("utf-8")),
            "sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        }
        for path, source in ordered
    ]
    normalized = "".join(_strip_comments_and_whitespace(source) for _, source in ordered)
    return inventory, normalized


def _parse_abi(value: object) -> list[Mapping[str, object]]:
    decoded: object
    if isinstance(value, str):
        decoded = json.loads(value, object_pairs_hook=_reject_duplicate_pairs)
    else:
        decoded = value
    entries = _mapping_list(decoded)
    if entries is None:
        raise ValueError("verified ABI must be a JSON list of mappings")
    return entries


def _abi_function(
    abi: Sequence[Mapping[str, object]], *, name: str, input_types: Sequence[str]
) -> Mapping[str, object] | None:
    matches: list[Mapping[str, object]] = []
    for entry in abi:
        if entry.get("type") != "function" or entry.get("name") != name:
            continue
        inputs = _mapping_list(entry.get("inputs"))
        if inputs is None:
            continue
        if [item.get("type") for item in inputs] == list(input_types):
            matches.append(entry)
    return matches[0] if len(matches) == 1 else None


def _abi_conformance(abi: Sequence[Mapping[str, object]]) -> dict[str, bool]:
    totals = _abi_function(abi, name="totalsCollateral", input_types=("address",))
    totals_outputs = None if totals is None else _mapping_list(totals.get("outputs"))
    totals_exact = (
        totals is not None
        and totals.get("stateMutability") == "view"
        and totals_outputs is not None
        and [item.get("type") for item in totals_outputs] == ["uint128", "uint128"]
    )
    asset = _abi_function(abi, name="getAssetInfoByAddress", input_types=("address",))
    asset_outputs = None if asset is None else _mapping_list(asset.get("outputs"))
    components = (
        None
        if asset_outputs is None or len(asset_outputs) != 1
        else _mapping_list(asset_outputs[0].get("components"))
    )
    asset_exact = (
        asset is not None
        and asset.get("stateMutability") == "view"
        and asset_outputs is not None
        and len(asset_outputs) == 1
        and asset_outputs[0].get("type") == "tuple"
        and components is not None
        and [item.get("type") for item in components]
        == ["uint8", "address", "address", "uint64", "uint64", "uint64", "uint64", "uint128"]
    )
    return {
        "totals_collateral_exact_abi": totals_exact,
        "asset_info_exact_abi": asset_exact,
    }


def normalize_verified_source(
    value: object,
    *,
    expected_address: str,
    expected_code_sha256: str,
    maximum_files: int,
    maximum_bytes: int,
) -> dict[str, object]:
    """Reduce a Blockscout verified-source response to bounded, claim-relevant evidence."""

    metadata = _mapping(value)
    if metadata is None:
        raise ValueError("smart-contract response must be a mapping")
    errors: list[str] = []
    inventory: list[dict[str, object]] = []
    normalized_source = ""
    try:
        inventory, normalized_source = _source_file_inventory(
            metadata, maximum_files=maximum_files, maximum_bytes=maximum_bytes
        )
    except ValueError as error:
        errors.append(str(error))
    abi: list[Mapping[str, object]] = []
    try:
        abi = _parse_abi(metadata.get("abi"))
    except (TypeError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"ABI: {error}")
    try:
        deployed = _hex_bytes(metadata.get("deployed_bytecode"), path="deployed_bytecode")
        deployed_sha256: str | None = hashlib.sha256(deployed).hexdigest()
        deployed_byte_count: int | None = len(deployed)
    except ValueError as error:
        errors.append(str(error))
        deployed_sha256 = None
        deployed_byte_count = None
    abi_checks = _abi_conformance(abi)
    semantic_checks = {marker: marker in normalized_source for marker in SOURCE_MARKERS}
    compiler_settings = metadata.get("compiler_settings")
    compiler_settings_sha256 = (
        canonical_json_sha256(compiler_settings) if _mapping(compiler_settings) is not None else None
    )
    name = metadata.get("name")
    language = metadata.get("language")
    checks = {
        "address_is_expected": normalize_address(expected_address, path="source.address") == expected_address,
        "verified": metadata.get("is_verified") is True,
        "fully_verified": metadata.get("is_fully_verified") is True,
        "bytecode_not_changed": metadata.get("is_changed_bytecode") is False,
        "solidity_language": isinstance(language, str) and language.lower() == "solidity",
        "accepted_comet_contract_name": name in {"Comet", "CometWithExtendedAssetList"},
        "compiler_version_present": isinstance(metadata.get("compiler_version"), str)
        and bool(metadata.get("compiler_version")),
        "compiler_settings_present": compiler_settings_sha256 is not None,
        "deployed_bytecode_matches_parent": deployed_sha256 == expected_code_sha256,
        "source_file_inventory_valid": not errors and bool(inventory),
        **abi_checks,
        "all_enforcement_markers_present": all(semantic_checks.values()),
    }
    return {
        "address": expected_address,
        "expected_deployed_bytecode_sha256": expected_code_sha256,
        "name": name if isinstance(name, str) else None,
        "language": language if isinstance(language, str) else None,
        "compiler_version": (
            metadata.get("compiler_version") if isinstance(metadata.get("compiler_version"), str) else None
        ),
        "compiler_settings_sha256": compiler_settings_sha256,
        "verified_at": metadata.get("verified_at") if isinstance(metadata.get("verified_at"), str) else None,
        "abi_canonical_sha256": canonical_json_sha256(abi),
        "deployed_bytecode_sha256": deployed_sha256,
        "deployed_bytecode_byte_count": deployed_byte_count,
        "source_file_count": len(inventory),
        "source_text_byte_count": sum(cast(int, item["byte_count"]) for item in inventory),
        "source_file_inventory": inventory,
        "source_file_inventory_sha256": canonical_json_sha256(inventory),
        "semantic_marker_checks": semantic_checks,
        "normalization_errors": errors,
        "checks": checks,
        "fully_conforming_source": all(checks.values()),
        "raw_source_retained": False,
    }


def load_supply_cap_activation(path: str | Path) -> dict[str, object]:
    """Load the frozen supply-cap activation manifest."""

    value: object = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    mapped = _mapping(value)
    if mapped is None:
        raise ValueError("supply-cap activation manifest must be a mapping")
    return dict(mapped)


def validate_supply_cap_activation(manifest: Mapping[str, object]) -> list[str]:
    """Validate the complete scientific, access and resource contract."""

    errors: list[str] = []
    if set(manifest) != TOP_LEVEL_KEYS:
        errors.append("manifest top-level keys differ from the frozen contract")
    for key, expected in (
        ("schema_version", SCHEMA_VERSION),
        ("audit_id", AUDIT_ID),
        ("as_of", AS_OF),
        ("stage", STAGE),
    ):
        if manifest.get(key) != expected:
            errors.append(f"{key} differs from the frozen value")
    parents = _mapping(manifest.get("parents"))
    if parents is None or dict(parents) != FROZEN_PARENTS:
        errors.append("parents differ from the frozen contract")
    access = _mapping(manifest.get("access_boundary"))
    if access is None:
        errors.append("access_boundary must be a mapping")
    else:
        if set(access) != ACCESS_TRUE | ACCESS_FALSE:
            errors.append("access_boundary keys differ from the frozen contract")
        for key in ACCESS_TRUE:
            if access.get(key) is not True:
                errors.append(f"access_boundary.{key} must be true")
        for key in ACCESS_FALSE:
            if access.get(key) is not False:
                errors.append(f"access_boundary.{key} must be false")
    selection = _mapping(manifest.get("selection_contract"))
    if selection is None:
        errors.append("selection_contract must be a mapping")
    else:
        expected_selection = {
            "mechanics_parent_decision": (
                "PASS_CANDIDATE_MECHANICS_AUTHORIZE_D1_EXPOSURE_PROTOCOL_DESIGN_ONLY"
            ),
            "fully_conforming_candidate_count": 4,
            "exact_candidate_ids_in_parent_order": list(FROZEN_CANDIDATE_IDS),
            "required_event_type": "update_asset_supply_cap",
            "required_direction": "strict_increase",
            "all_parent_survivors_included": True,
            "candidate_replacement_after_freeze": False,
            "selection_uses_activation_or_response_outcomes": False,
        }
        if dict(selection) != expected_selection:
            errors.append("selection_contract differs from the frozen contract")
    official = _mapping(manifest.get("official_source_contract"))
    if official is None:
        errors.append("official_source_contract must be a mapping")
    else:
        implementations = _mapping_list(official.get("implementations"))
        if implementations is None or [dict(item) for item in implementations] != list(
            FROZEN_IMPLEMENTATIONS
        ):
            errors.append("implementation source order or hashes differ from the frozen parent")
        if official.get("source_commit") != FROZEN_PARENTS["official_source_commit"]:
            errors.append("official source commit differs from the frozen parent")
        if _strings(official.get("required_normalized_source_markers")) != SOURCE_MARKERS:
            errors.append("source semantic markers differ from the frozen contract")
        if official.get("totals_collateral_selector") != TOTALS_COLLATERAL_SELECTOR:
            errors.append("totalsCollateral selector differs from the frozen contract")
        if official.get("get_asset_info_selector") != GET_ASSET_INFO_SELECTOR:
            errors.append("getAssetInfoByAddress selector differs from the frozen contract")
    activation = _mapping(manifest.get("activation_contract"))
    expected_activation = {
        "lookback_block_offsets": list(LOOKBACK_BLOCK_OFFSETS),
        "utilization_diagnostics_ppm": list(UTILIZATION_THRESHOLDS_PPM),
        "confirmatory_strong_activation": "total_supply_asset_equals_supply_cap_at_t_minus_one",
        "near_cap_diagnostics_never_authorize_next_stage": True,
        "lookback_snapshots_do_not_prove_continuous_saturation": True,
        "query_post_event_total_supply_asset": False,
        "account_level_estimand_disposition": (
            "RETIRE_ACCOUNT_LEVEL_M3_FOR_SUPPLY_CAP_EVENTS_UNOBSERVABLE_TREATED_COHORT"
        ),
        "pass_authorizes_account_rows": False,
    }
    if activation is None or dict(activation) != expected_activation:
        errors.append("activation_contract differs from the frozen contract")
    requests = _mapping(manifest.get("expected_request_contract"))
    expected_requests = {
        "candidate_count": 4,
        "unique_implementation_count": 7,
        "lookback_snapshot_count_per_candidate": 6,
        "json_rpc_success_count_without_retry": 134,
        "blockscout_smart_contract_success_count_without_retry": 7,
        "network_operation_count_without_retry": 141,
        "method_counts": {
            "eth_call": 100,
            "eth_chainId": 2,
            "eth_getBlockByNumber": 24,
            "eth_getCode": 8,
        },
        "rest_path_template_counts": {SMART_CONTRACT_PATH_TEMPLATE: 7},
        "provider_counts": {
            "blockscout": 49,
            "blockscout_smart_contract": 7,
            "publicnode_execution": 85,
        },
    }
    if requests is None or dict(requests) != expected_requests:
        errors.append("expected_request_contract differs from the frozen plan")
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
            value = sources.get(key)
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                errors.append(f"sources.{key} must be a positive integer")
        if sources.get("raw_response_payloads_retained") is not False:
            errors.append("raw response retention must be false")
        if sources.get("endpoint_substitution_after_freeze") is not False:
            errors.append("endpoint substitution after freeze must be false")
    gates = _strings(manifest.get("integrity_gates"))
    if (
        gates is None
        or frozenset(gates) != REQUIRED_INTEGRITY_GATES
        or len(gates) != len(REQUIRED_INTEGRITY_GATES)
    ):
        errors.append("integrity_gates differ from the frozen contract")
    policy = _mapping(manifest.get("decision_policy"))
    expected_policy = {
        "integrity_gates_all_required": True,
        "pass": "PASS_EXACT_CAP_ACTIVATION_AUTHORIZE_MARKET_LEVEL_D1B_DESIGN_ONLY",
        "fail_no_activation": "FAIL_NO_EXACT_T_MINUS_ONE_SATURATION_RETIRE_COMPOUND_M3_CAUSAL_ROUTE",
        "fail_conformance": "FAIL_SOURCE_OR_STATE_CONFORMANCE_KEEP_ALL_D1_ROWS_LOCKED",
        "infrastructure_failure": "INFRASTRUCTURE_FAILURE_NO_SUPPLY_CAP_ACTIVATION_RESULT",
        "authorized_next_stage": "separately_frozen_market_level_collateral_flow_d1b_protocol_design_only",
    }
    if policy is None or dict(policy) != expected_policy:
        errors.append("decision_policy differs from the frozen contract")
    failure = _mapping(manifest.get("failure_artifact_contract"))
    if failure is None or failure.get("schema_version") != FAILURE_SCHEMA_VERSION:
        errors.append("failure artifact schema differs from the frozen contract")
    limitations = _strings(manifest.get("limitations"))
    if limitations is None or not limitations:
        errors.append("limitations must be a nonempty string list")
    return sorted(errors)


def derive_parent_candidates(
    summary: Mapping[str, object], candidates: Sequence[Mapping[str, object]]
) -> list[dict[str, object]]:
    """Derive every mechanics survivor and the exact source/code state needed by D1a."""

    candidate_summary = _mapping(summary.get("candidate_summary"))
    if candidate_summary is None:
        raise ValueError("mechanics summary candidate_summary is missing")
    expected_ids = candidate_summary.get("fully_conforming_candidate_ids")
    if expected_ids != list(FROZEN_CANDIDATE_IDS):
        raise ValueError("mechanics summary survivor IDs differ from the frozen order")
    by_id: dict[str, Mapping[str, object]] = {}
    for result in candidates:
        candidate = _mapping(result.get("candidate"))
        if candidate is None or not isinstance(candidate.get("candidate_id"), str):
            raise ValueError("mechanics candidate record is malformed")
        by_id[cast(str, candidate["candidate_id"])] = result
    derived: list[dict[str, object]] = []
    for candidate_id in FROZEN_CANDIDATE_IDS:
        parent_result = by_id.get(candidate_id)
        if parent_result is None or parent_result.get("fully_conforming_candidate") is not True:
            raise ValueError(f"frozen mechanics survivor is missing: {candidate_id}")
        candidate = _mapping(parent_result.get("candidate"))
        proxy_state = _mapping(parent_result.get("proxy_state"))
        pre = _mapping(parent_result.get("asset_info_pre"))
        post = _mapping(parent_result.get("asset_info_post"))
        headers = _mapping(parent_result.get("block_headers"))
        event_header = None if headers is None else _mapping(headers.get("blockscout"))
        if any(item is None for item in (candidate, proxy_state, pre, post, event_header)):
            raise ValueError(f"mechanics survivor evidence is incomplete: {candidate_id}")
        assert candidate is not None
        assert proxy_state is not None
        assert pre is not None
        assert post is not None
        assert event_header is not None
        if candidate.get("event_type") != "update_asset_supply_cap":
            raise ValueError(f"mechanics survivor is not a supply-cap event: {candidate_id}")
        old_value = candidate.get("old_value")
        new_value = candidate.get("new_value")
        if (
            not isinstance(old_value, int)
            or isinstance(old_value, bool)
            or not isinstance(new_value, int)
            or isinstance(new_value, bool)
            or old_value <= 0
            or new_value <= old_value
            or pre.get("supply_cap") != old_value
            or post.get("supply_cap") != new_value
        ):
            raise ValueError(f"mechanics survivor cap transition is invalid: {candidate_id}")
        derived.append(
            {
                "candidate": dict(candidate),
                "proxy_state": dict(proxy_state),
                "asset_info_pre": dict(pre),
                "asset_info_post": dict(post),
                "event_header": dict(event_header),
            }
        )
    return derived


def _derived_implementations(candidates: Sequence[Mapping[str, object]]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    seen: set[str] = set()
    for record in candidates:
        proxy_state = cast(Mapping[str, object], record["proxy_state"])
        for address_key, hash_key in (
            ("old_implementation", "old_code_sha256"),
            ("new_implementation", "new_code_sha256"),
        ):
            address = cast(str, proxy_state[address_key])
            if address in seen:
                continue
            seen.add(address)
            result.append({"address": address, "code_sha256": cast(str, proxy_state[hash_key])})
    return result


def validate_parent_evidence(manifest: Mapping[str, object], root: str | Path) -> list[str]:
    """Reproduce every parent hash, survivor and source reference before network access."""

    errors: list[str] = []
    root_path = Path(root)
    parents = cast(Mapping[str, object], manifest["parents"])
    for path_key, hash_key in (
        ("mechanics_manifest_path", "mechanics_manifest_sha256"),
        ("mechanics_result_path", "mechanics_result_sha256"),
        ("mechanics_summary_path", "mechanics_summary_sha256"),
        ("mechanics_candidates_path", "mechanics_candidates_sha256"),
        ("mechanics_http_evidence_path", "mechanics_http_evidence_sha256"),
        ("metadata_summary_path", "metadata_summary_sha256"),
    ):
        relative = parents.get(path_key)
        if not _safe_relative_path(relative):
            errors.append(f"parent {path_key} is not a safe relative path")
            continue
        path = root_path / cast(str, relative)
        if not path.is_file():
            errors.append(f"parent {path_key} is missing")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != parents.get(hash_key):
            errors.append(f"parent {path_key} hash differs from the frozen value")
    if errors:
        return sorted(errors)
    summary = _read_json_mapping(root_path / cast(str, parents["mechanics_summary_path"]))
    candidate_rows = _read_json_mapping_list(root_path / cast(str, parents["mechanics_candidates_path"]))
    result_text = (root_path / cast(str, parents["mechanics_result_path"])).read_text(encoding="utf-8")
    metadata = _read_json_mapping(root_path / cast(str, parents["metadata_summary_path"]))
    if summary.get("decision") != ("PASS_CANDIDATE_MECHANICS_AUTHORIZE_D1_EXPOSURE_PROTOCOL_DESIGN_ONLY"):
        errors.append("mechanics parent decision is not the frozen pass")
    if summary.get("collection_commit") != parents["mechanics_protocol_commit"]:
        errors.append("mechanics parent collection commit differs")
    if cast(str, parents["mechanics_protocol_commit"]) not in result_text or (
        "PASS_CANDIDATE_MECHANICS_AUTHORIZE_D1_EXPOSURE_PROTOCOL_DESIGN_ONLY" not in result_text
    ):
        errors.append("mechanics result does not identify the frozen protocol and decision")
    try:
        derived = derive_parent_candidates(summary, candidate_rows)
    except ValueError as error:
        errors.append(str(error))
        derived = []
    if derived and _derived_implementations(derived) != list(FROZEN_IMPLEMENTATIONS):
        errors.append("implementation order or code hashes do not reproduce the mechanics parent")
    if metadata.get("decision") != "PASS_SOURCE_METADATA_AUTHORIZE_CHAIN_METADATA_ONLY":
        errors.append("metadata parent decision is not the frozen pass")
    source = _mapping(metadata.get("source"))
    if source is None or source.get("commit") != parents["official_source_commit"]:
        errors.append("metadata parent does not reproduce the official source commit")
    else:
        files = _mapping_list(source.get("files"))
        file_hashes = {} if files is None else {item.get("path"): item.get("sha256") for item in files}
        for source_path, expected_hash in (
            (
                "contracts/CometStorage.sol",
                "7475e03d2945a35e9bbd93fa96ba8bc18d50f60cdb9ea992e6742efbc199850c",
            ),
            (
                "contracts/CometMainInterface.sol",
                "8dab837c9ef1d3805413b2d5c948d8c1f5b009da4e4f9505795b2a1535ec0d1b",
            ),
        ):
            if file_hashes.get(source_path) != expected_hash:
                errors.append(f"metadata parent source hash differs for {source_path}")
    return sorted(errors)


class SupplyCapTransport(HttpTransport):
    """The shared bounded transport plus the one frozen source-metadata endpoint."""

    def smart_contract_get(self, *, base_url: str, address: str, label: str) -> object:
        normalized = normalize_address(address, path="smart_contract.address")
        path = SMART_CONTRACT_PATH_TEMPLATE.format(address_hash=normalized)
        return self._rest_get(
            base_url=base_url,
            path=path,
            label=label,
            provider="blockscout_smart_contract",
            operation_type="blockscout_smart_contract_rest",
            require_mapping=True,
        )


def build_http_transport(manifest: Mapping[str, object]) -> SupplyCapTransport:
    """Construct the single globally rate-limited transport."""

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
    """Build the exact ordered, no-outcome-dependent request vector."""

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
        proxy_state = cast(Mapping[str, object], record["proxy_state"])
        candidate_id = cast(str, candidate["candidate_id"])
        event_block = cast(int, candidate["block_number"])
        proxy = cast(str, candidate["comet_proxy"])
        asset = cast(str, candidate["asset"])
        old_implementation = cast(str, proxy_state["old_implementation"])
        new_implementation = cast(str, proxy_state["new_implementation"])
        rpc(
            "publicnode_execution",
            f"{candidate_id}:old_implementation_code",
            "eth_getCode",
            [old_implementation, hex(event_block - 1)],
        )
        rpc(
            "publicnode_execution",
            f"{candidate_id}:new_implementation_code",
            "eth_getCode",
            [new_implementation, hex(event_block)],
        )
        asset_call = {"to": proxy, "data": _address_call(GET_ASSET_INFO_SELECTOR, asset)}
        rpc(
            "publicnode_execution",
            f"{candidate_id}:asset_info_post",
            "eth_call",
            [asset_call, hex(event_block)],
        )
        totals_call = {"to": proxy, "data": _address_call(TOTALS_COLLATERAL_SELECTOR, asset)}
        for offset in LOOKBACK_BLOCK_OFFSETS:
            block = event_block - offset
            label = f"{candidate_id}:lookback_{offset:06d}"
            rpc(
                "publicnode_execution",
                f"{label}:header",
                "eth_getBlockByNumber",
                [hex(block), False],
            )
            rpc("blockscout", f"{label}:asset_info_blockscout", "eth_call", [asset_call, hex(block)])
            rpc(
                "publicnode_execution",
                f"{label}:asset_info_publicnode",
                "eth_call",
                [asset_call, hex(block)],
            )
            rpc("blockscout", f"{label}:totals_blockscout", "eth_call", [totals_call, hex(block)])
            rpc(
                "publicnode_execution",
                f"{label}:totals_publicnode",
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


def _code_record(value: object, *, expected_sha256: str) -> dict[str, object]:
    payload = _hex_bytes(value, path="implementation_code")
    observed = hashlib.sha256(payload).hexdigest()
    return {
        "byte_count": len(payload),
        "sha256": observed,
        "expected_parent_sha256": expected_sha256,
        "matches_parent": observed == expected_sha256,
    }


def _utilization_record(total: int, cap: int) -> dict[str, object]:
    if cap <= 0:
        raise ValueError("supply cap must be positive")
    return {
        "numerator_total_supply_asset": total,
        "denominator_supply_cap": cap,
        "utilization_ppm_floor": total * 1_000_000 // cap,
        "at_least_900000_ppm": total * 1_000_000 >= cap * 900_000,
        "at_least_950000_ppm": total * 1_000_000 >= cap * 950_000,
        "at_least_990000_ppm": total * 1_000_000 >= cap * 990_000,
        "exactly_saturated": total == cap,
        "within_cap": total <= cap,
        "headroom_raw_units": cap - total,
    }


def collect_supply_cap_activation(
    manifest: Mapping[str, object],
    *,
    root: str | Path = ".",
    transport: SupplyCapTransport | None = None,
) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    """Execute the frozen source/state audit without opening any account or response row."""

    errors = validate_supply_cap_activation(manifest)
    errors.extend(validate_parent_evidence(manifest, root))
    if errors:
        raise ValueError("invalid supply-cap activation manifest: " + "; ".join(sorted(set(errors))))
    root_path = Path(root)
    parents = cast(Mapping[str, object], manifest["parents"])
    parent_summary = _read_json_mapping(root_path / cast(str, parents["mechanics_summary_path"]))
    parent_rows = _read_json_mapping_list(root_path / cast(str, parents["mechanics_candidates_path"]))
    candidates = derive_parent_candidates(parent_summary, parent_rows)
    sources = cast(Mapping[str, object], manifest["sources"])
    official = cast(Mapping[str, object], manifest["official_source_contract"])
    if transport is None:
        transport = build_http_transport(manifest)
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
    source_results: list[dict[str, object]] = []
    source_by_address: dict[str, Mapping[str, object]] = {}
    maximum_source_files = cast(int, sources["maximum_verified_source_files"])
    maximum_source_bytes = cast(int, sources["maximum_verified_source_text_bytes"])
    for item in cast(Sequence[Mapping[str, object]], official["implementations"]):
        address = cast(str, item["address"])
        result = normalize_verified_source(
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
        source_results.append(result)
        source_by_address[address] = result

    candidate_results: list[dict[str, object]] = []
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
        old_code = _code_record(
            transport.rpc_call(
                url=publicnode_url,
                provider="publicnode_execution",
                label=f"{candidate_id}:old_implementation_code",
                method="eth_getCode",
                params=[old_address, hex(event_block - 1)],
            ),
            expected_sha256=cast(str, proxy_state["old_code_sha256"]),
        )
        new_code = _code_record(
            transport.rpc_call(
                url=publicnode_url,
                provider="publicnode_execution",
                label=f"{candidate_id}:new_implementation_code",
                method="eth_getCode",
                params=[new_address, hex(event_block)],
            ),
            expected_sha256=cast(str, proxy_state["new_code_sha256"]),
        )
        asset_call = {"to": proxy, "data": _address_call(GET_ASSET_INFO_SELECTOR, asset)}
        post_replica = decode_asset_info(
            transport.rpc_call(
                url=publicnode_url,
                provider="publicnode_execution",
                label=f"{candidate_id}:asset_info_post",
                method="eth_call",
                params=[asset_call, hex(event_block)],
            ),
            expected_asset=asset,
        )
        totals_call = {"to": proxy, "data": _address_call(TOTALS_COLLATERAL_SELECTOR, asset)}
        snapshots: list[dict[str, object]] = []
        for offset in LOOKBACK_BLOCK_OFFSETS:
            block = event_block - offset
            label = f"{candidate_id}:lookback_{offset:06d}"
            header = _block_header(
                transport.rpc_call(
                    url=publicnode_url,
                    provider="publicnode_execution",
                    label=f"{label}:header",
                    method="eth_getBlockByNumber",
                    params=[hex(block), False],
                ),
                expected_number=block,
                path=f"{label}:header",
            )
            asset_blockscout = decode_asset_info(
                transport.rpc_call(
                    url=blockscout_url,
                    provider="blockscout",
                    label=f"{label}:asset_info_blockscout",
                    method="eth_call",
                    params=[asset_call, hex(block)],
                ),
                expected_asset=asset,
            )
            asset_publicnode = decode_asset_info(
                transport.rpc_call(
                    url=publicnode_url,
                    provider="publicnode_execution",
                    label=f"{label}:asset_info_publicnode",
                    method="eth_call",
                    params=[asset_call, hex(block)],
                ),
                expected_asset=asset,
            )
            totals_blockscout = decode_totals_collateral(
                transport.rpc_call(
                    url=blockscout_url,
                    provider="blockscout",
                    label=f"{label}:totals_blockscout",
                    method="eth_call",
                    params=[totals_call, hex(block)],
                )
            )
            totals_publicnode = decode_totals_collateral(
                transport.rpc_call(
                    url=publicnode_url,
                    provider="publicnode_execution",
                    label=f"{label}:totals_publicnode",
                    method="eth_call",
                    params=[totals_call, hex(block)],
                )
            )
            total = totals_blockscout["total_supply_asset"]
            cap = cast(int, asset_blockscout["supply_cap"])
            utilization = _utilization_record(total, cap)
            snapshots.append(
                {
                    "block_offset": offset,
                    "block_number": block,
                    "header": header,
                    "elapsed_to_event_seconds": cast(int, event_header["timestamp_unix"])
                    - cast(int, header["timestamp_unix"]),
                    "asset_info_blockscout": asset_blockscout,
                    "asset_info_publicnode": asset_publicnode,
                    "totals_collateral_blockscout": totals_blockscout,
                    "totals_collateral_publicnode": totals_publicnode,
                    "configuration_provider_agreement": asset_blockscout == asset_publicnode,
                    "aggregate_provider_agreement": totals_blockscout == totals_publicnode,
                    "utilization": utilization,
                }
            )
        immediate = snapshots[0]
        immediate_utilization = cast(Mapping[str, object], immediate["utilization"])
        checks = {
            "old_and_new_verified_source_conform": source_by_address[old_address]["fully_conforming_source"]
            is True
            and source_by_address[new_address]["fully_conforming_source"] is True,
            "publicnode_old_and_new_code_match_parent": old_code["matches_parent"] is True
            and new_code["matches_parent"] is True,
            "post_asset_info_matches_parent": post_replica == parent_post,
            "all_snapshot_headers_precede_event": all(
                cast(int, item["elapsed_to_event_seconds"]) > 0 for item in snapshots
            ),
            "all_snapshot_configuration_providers_agree": all(
                item["configuration_provider_agreement"] is True for item in snapshots
            ),
            "all_snapshot_aggregate_providers_agree": all(
                item["aggregate_provider_agreement"] is True for item in snapshots
            ),
            "all_snapshot_totals_within_contemporaneous_cap": all(
                cast(Mapping[str, object], item["utilization"])["within_cap"] is True for item in snapshots
            ),
            "t_minus_one_asset_info_matches_parent": immediate["asset_info_blockscout"] == parent_pre,
            "strict_cap_increase": cast(int, candidate["new_value"]) > cast(int, candidate["old_value"]),
        }
        candidate_results.append(
            {
                "candidate": dict(candidate),
                "event_header": dict(event_header),
                "parent_asset_info_pre": dict(parent_pre),
                "parent_asset_info_post": dict(parent_post),
                "source_implementation_addresses": {"old": old_address, "new": new_address},
                "publicnode_code_replica": {"old": old_code, "new": new_code},
                "publicnode_asset_info_post_replica": post_replica,
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
    total_source_files = sum(cast(int, item["source_file_count"]) for item in source_results)
    total_source_text_bytes = sum(cast(int, item["source_text_byte_count"]) for item in source_results)
    all_candidates_conform = all(item["data_and_source_conforming"] is True for item in candidate_results)
    integrity_gates = {
        "parent_hashes_and_exact_survivor_derivation": True,
        "ethereum_mainnet_provider_identity": blockscout_chain_id == publicnode_chain_id == "0x1",
        "all_historical_implementations_source_conform": all(
            item["fully_conforming_source"] is True for item in source_results
        ),
        "publicnode_runtime_code_reproduces_parent": all(
            cast(Mapping[str, object], item["checks"])["publicnode_old_and_new_code_match_parent"] is True
            for item in candidate_results
        ),
        "historical_configuration_getters_replicate": all(
            cast(Mapping[str, object], item["checks"])["post_asset_info_matches_parent"] is True
            and cast(Mapping[str, object], item["checks"])["t_minus_one_asset_info_matches_parent"] is True
            and cast(Mapping[str, object], item["checks"])["all_snapshot_configuration_providers_agree"]
            is True
            for item in candidate_results
        ),
        "aggregate_totals_cross_provider_and_within_cap": all(
            cast(Mapping[str, object], item["checks"])["all_snapshot_aggregate_providers_agree"] is True
            and cast(Mapping[str, object], item["checks"])["all_snapshot_totals_within_contemporaneous_cap"]
            is True
            for item in candidate_results
        ),
        "all_candidates_evaluated": len(candidate_results) == 4 and all_candidates_conform,
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
        for item in candidate_results
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
        "parents": manifest["parents"],
        "provider_chain_ids": {
            "blockscout": blockscout_chain_id,
            "publicnode_execution": publicnode_chain_id,
        },
        "implementation_source_summary": {
            "audited_count": len(source_results),
            "fully_conforming_count": sum(item["fully_conforming_source"] is True for item in source_results),
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
                for item in source_results
            ],
        },
        "candidate_summary": {
            "audited_count": len(candidate_results),
            "data_and_source_conforming_count": sum(
                item["data_and_source_conforming"] is True for item in candidate_results
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
                for item in candidate_results
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
        "implementation_sources": source_results,
        "candidates": candidate_results,
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
    """Run one sealed supply-cap activation audit from an exact clean commit."""

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
    manifest = load_supply_cap_activation(args.manifest)
    manifest_sha256 = hashlib.sha256(args.manifest.read_bytes()).hexdigest()
    transport: SupplyCapTransport | None = None
    try:
        transport = build_http_transport(manifest)
        summary, candidates, responses = collect_supply_cap_activation(
            manifest,
            root=root,
            transport=transport,
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
