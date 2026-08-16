"""Zero-account Aave V3 cross-deployment Configurator-program directory."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from itertools import groupby, pairwise
from pathlib import Path
from typing import cast

import requests
import yaml

from ecomd.research.aave_lt_event_directory import (
    CONFIGURATOR_ID,
    EVENT_CONTRACT,
    decode_quantity,
    normalize_address,
    normalize_data,
    normalize_directory_log,
    normalize_hash,
    root_intervals,
    split_inclusive_interval,
)
from ecomd.research.compound_v3_chain_metadata import canonical_json_sha256

SCHEMA_VERSION = "ecophys-aave-v3-cross-deployment-program-directory/v1"
ARTIFACT_SCHEMA_VERSION = "ecophys-aave-v3-cross-deployment-program-directory-audit/v1"
AUDIT_ID = "aave_v3_cross_deployment_program_directory_v1"
STAGE = "zero_account_cross_deployment_configurator_program_directory"
AS_OF = "2026-08-16"
ZERO_ADDRESS = "0x" + "0" * 40
UPGRADED_TOPIC = EVENT_CONTRACT["upgraded"]["topic0"]

EXPECTED_PARENTS: dict[str, object] = {
    "bundle_summary_path": "experiments/v14_aave_v3_bundle_structure_feasibility/artifacts/summary.json",
    "bundle_summary_sha256": "922312a9c75a64cfe66a1ef828140df938929e4bc6fbac9200a3a1f6fa9d9db9",
    "bundle_manifest_path": "data/manifests/aave_v3_bundle_structure_feasibility_v1.yaml",
    "bundle_manifest_sha256": "e8cf60b2577bdf9e46f68f15c0c7e21931a3d705357420a907b75d74838a65e0",
    "a1a_summary_path": "experiments/v14_aave_v3_lt_event_directory/artifacts/summary.json",
    "a1a_summary_sha256": "ff3e120920b766957353c59c02341c42990a18818a751d62da6e1a6798a3c1bb",
    "a1a_directory_path": "experiments/v14_aave_v3_lt_event_directory/artifacts/event_directory.json",
    "a1a_directory_sha256": "1d1d73b5f5ba51c60841a411edf563317f143e9599e3eac958643895c90648ec",
    "expected_bundle_decision": "COMPLETE_DEVELOPMENT_BUNDLE_STRUCTURE_AUTHORIZE_VECTOR_COMPILER_PROTOCOL_DESIGN_ONLY",
    "expected_a1a_decision": "FAIL_AAVE_LT_EVENT_DIRECTORY_KEEP_ACCOUNTS_RESPONSES_AND_G1_LOCKED",
}

EXPECTED_SOURCE_FILES = {
    "arbitrum": (
        "src/AaveV3Arbitrum.sol",
        "6ced3e9db2b3af5808cc4ec7d4d08ae74ba93598",
        "67353fe8ff68bf166c24d0ef3a110713bbb2128d122d60a045e5ad61d72b6cff",
    ),
    "avalanche": (
        "src/AaveV3Avalanche.sol",
        "649607f0b9140df203b7745ae46c6df3fd18935c",
        "04eb0307e435920d05e1a20ad74bbcf765dc6a8febc80e4f2d9d309b3b84d1fd",
    ),
    "bnb": (
        "src/AaveV3BNB.sol",
        "3c515e02e613c5891be9da280e7942534d384054",
        "cffe4c9b69b70d13e5fad83007c04e170e6ebc1a7ef806b53d20507a9c506494",
    ),
    "base": (
        "src/AaveV3Base.sol",
        "1a43dc376203b92bad17172988c951c3f951a556",
        "1965f69c52ac312c0af43a349ac55f41abded3250cad475ea445abc8c58fce48",
    ),
    "ethereum": (
        "src/AaveV3Ethereum.sol",
        "9fc2e4533f0bd4d8e47a05f41ee539a688efe2d7",
        "1a862b7389de3d59ee77680a8edb451a29e630a07813a0c5becdce65d730a22a",
    ),
    "gnosis": (
        "src/AaveV3Gnosis.sol",
        "c341afa33b2d671c10bd6129ecbfe811cc7ea37d",
        "b43452360f76eb1ceb9ca0cf11602836b9b2f000e06c07228a61534f3655cdba",
    ),
    "linea": (
        "src/AaveV3Linea.sol",
        "2b9edb8f7bf6d301718e165c1a8510c321075933",
        "d1b5bfaf93e780c49d7475d0f2cc5ab33778717a93975992e23861677488262c",
    ),
    "optimism": (
        "src/AaveV3Optimism.sol",
        "f8cc265ece5505f65ef6cc2f91ff456937b34fde",
        "7a352505339412e53d71330354bc8e67a9ee960d0ae958609a61fbc653944995",
    ),
    "polygon": (
        "src/AaveV3Polygon.sol",
        "82d9e0bcd2cab0348078cd1580a6f36629e0fc27",
        "94879a4ed820c09ca8d76b81782fa245d7866705301e4676c73b5d178b95ae49",
    ),
    "scroll": (
        "src/AaveV3Scroll.sol",
        "51ebc143922143aeb1a54e188f64881808523094",
        "af0154c572df10fe973834c182f9d607430649e05f6879cb95703f98779b98cb",
    ),
}

EXPECTED_DEPLOYMENTS: dict[str, dict[str, object]] = {
    "ethereum": {
        "chain_id": 1,
        "chain_id_hex": "0x1",
        "split": "development",
        "network_access_in_b0": False,
        "pool_addresses_provider": "0x2f39d218133afab8f2b819b1066c7e434ad94e9e",
        "pool": "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2",
        "pool_configurator": "0x64b761d848206f447fe2dd461b0c635ec39ebb27",
        "price_oracle": "0x54586be62e3c3580375ae3723c145253060ca0c2",
    },
    "arbitrum": {
        "chain_id": 42161,
        "chain_id_hex": "0xa4b1",
        "split": "train",
        "network_access_in_b0": True,
        "pool_addresses_provider": "0xa97684ead0e402dc232d5a977953df7ecbab3cdb",
        "pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
        "pool_configurator": "0x8145edddf43f50276641b55bd3ad95944510021e",
        "price_oracle": "0xb56c2f0b653b2e0b10c9b928c8580ac5df02c7c7",
        "primary_rpc_url": "https://arbitrum-one-rpc.publicnode.com",
        "replica_rpc_url": "https://arb1.arbitrum.io/rpc",
    },
    "avalanche": {
        "chain_id": 43114,
        "chain_id_hex": "0xa86a",
        "split": "train",
        "network_access_in_b0": True,
        "pool_addresses_provider": "0xa97684ead0e402dc232d5a977953df7ecbab3cdb",
        "pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
        "pool_configurator": "0x8145edddf43f50276641b55bd3ad95944510021e",
        "price_oracle": "0xebd36016b3ed09d4693ed4251c67bd858c3c7c9c",
        "primary_rpc_url": "https://avalanche-c-chain-rpc.publicnode.com",
        "replica_rpc_url": "https://api.avax.network/ext/bc/C/rpc",
    },
    "optimism": {
        "chain_id": 10,
        "chain_id_hex": "0xa",
        "split": "train",
        "network_access_in_b0": True,
        "pool_addresses_provider": "0xa97684ead0e402dc232d5a977953df7ecbab3cdb",
        "pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
        "pool_configurator": "0x8145edddf43f50276641b55bd3ad95944510021e",
        "price_oracle": "0xd81eb3728a631871a7ebbad631b5f424909f0c77",
        "primary_rpc_url": "https://optimism-rpc.publicnode.com",
        "replica_rpc_url": "https://mainnet.optimism.io",
    },
    "polygon": {
        "chain_id": 137,
        "chain_id_hex": "0x89",
        "split": "train",
        "network_access_in_b0": True,
        "pool_addresses_provider": "0xa97684ead0e402dc232d5a977953df7ecbab3cdb",
        "pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
        "pool_configurator": "0x8145edddf43f50276641b55bd3ad95944510021e",
        "price_oracle": "0xb023e699f5a33916ea823a16485e259257ca8bd1",
        "primary_rpc_url": "https://polygon-bor-rpc.publicnode.com",
        "replica_rpc_url": "https://polygon.drpc.org",
    },
    "base": {
        "chain_id": 8453,
        "chain_id_hex": "0x2105",
        "split": "validation",
        "network_access_in_b0": True,
        "pool_addresses_provider": "0xe20fcbdbffc4dd138ce8b2e6fbb6cb49777ad64d",
        "pool": "0xa238dd80c259a72e81d7e4664a9801593f98d1c5",
        "pool_configurator": "0x5731a04b1e775f0fdd454bf70f3335886e9a96be",
        "price_oracle": "0x2cc0fc26ed4563a5ce5e8bdcfe1a2878676ae156",
        "primary_rpc_url": "https://base-rpc.publicnode.com",
        "replica_rpc_url": "https://mainnet.base.org",
    },
    "gnosis": {
        "chain_id": 100,
        "chain_id_hex": "0x64",
        "split": "validation",
        "network_access_in_b0": True,
        "pool_addresses_provider": "0x36616cf17557639614c1cddb356b1b83fc0b2132",
        "pool": "0xb50201558b00496a145fe76f7424749556e326d8",
        "pool_configurator": "0x7304979ec9e4eaa0273b6a037a31c4e9e5a75d16",
        "price_oracle": "0xeb0a051be10228213baeb449db63719d6742f7c4",
        "primary_rpc_url": "https://gnosis-rpc.publicnode.com",
        "replica_rpc_url": "https://rpc.gnosischain.com",
    },
    "bnb": {
        "chain_id": 56,
        "chain_id_hex": "0x38",
        "split": "test",
        "network_access_in_b0": True,
        "pool_addresses_provider": "0xff75b6da14ffbbfd355daf7a2731456b3562ba6d",
        "pool": "0x6807dc923806fe8fd134338eabca509979a7e0cb",
        "pool_configurator": "0x67bdf23c7fce7c65ff7415ba3f2520b45d6f9584",
        "price_oracle": "0x39bc1bfda2130d6bb6dbefd366939b4c7aa7c697",
        "primary_rpc_url": "https://bsc-rpc.publicnode.com",
        "replica_rpc_url": "https://bsc-dataseed.bnbchain.org",
    },
    "linea": {
        "chain_id": 59144,
        "chain_id_hex": "0xe708",
        "split": "test",
        "network_access_in_b0": True,
        "pool_addresses_provider": "0x89502c3731f69ddc95b65753708a07f8cd0373f4",
        "pool": "0xc47b8c00b0f69a36fa203ffeac0334874574a8ac",
        "pool_configurator": "0x812e7c19421d9f41a6ddcf047d5cc2de2ca5bfa2",
        "price_oracle": "0xcfdada7dcd2e785cf706badbc2b8af5084d595e9",
        "primary_rpc_url": "https://linea-rpc.publicnode.com",
        "replica_rpc_url": "https://rpc.linea.build",
    },
    "scroll": {
        "chain_id": 534352,
        "chain_id_hex": "0x82750",
        "split": "test",
        "network_access_in_b0": True,
        "pool_addresses_provider": "0x69850d0b276776781c063771b161bd8894bcdd04",
        "pool": "0x11fcfe756c05ad438e312a7fd934381537d3cffe",
        "pool_configurator": "0x32bcab42a2bb5ac577d24b425d46d8b8e0df9b7f",
        "price_oracle": "0x04421d8c506e2fa2371a08efaabf791f624054f3",
        "primary_rpc_url": "https://scroll-rpc.publicnode.com",
        "replica_rpc_url": "https://rpc.scroll.io",
    },
}

EXPECTED_SUPPORT_THRESHOLDS: dict[str, object] = {
    "per_named_non_development_deployment_minimum_programs": 10,
    "train": {
        "deployments": ["arbitrum", "avalanche", "optimism", "polygon"],
        "minimum_programs": 120,
        "minimum_unique_topic0": 12,
        "minimum_multi_log_programs": 30,
        "minimum_deployments_with_upgrade_program": 2,
        "minimum_span_days": 730,
        "minimum_distinct_calendar_quarters": 8,
    },
    "validation": {
        "deployments": ["base", "gnosis"],
        "minimum_programs": 40,
        "minimum_unique_topic0": 8,
        "minimum_multi_log_programs": 10,
        "minimum_deployments_with_upgrade_program": 1,
        "minimum_span_days": 365,
        "minimum_distinct_calendar_quarters": 4,
    },
    "test": {
        "deployments": ["bnb", "linea", "scroll"],
        "minimum_programs": 60,
        "minimum_unique_topic0": 8,
        "minimum_multi_log_programs": 15,
        "minimum_deployments_with_upgrade_program": 1,
        "minimum_span_days": 365,
        "minimum_distinct_calendar_quarters": 4,
    },
    "minimum_total_non_development_programs": 220,
}

EXPECTED_PROGRAM_INCLUSION_RULE: dict[str, object] = {
    "provider_history_scanned_from_genesis_to_cutoff": True,
    "derive_every_configurator_surface_from_provider_events": True,
    "official_current_configurator_must_be_in_derived_surface": True,
    "scan_all_topics_at_every_derived_configurator_surface": True,
    "program_key": ["chain_id", "transaction_hash"],
    "include_if_at_least_one_configurator_surface_log": True,
    "include_upgrade_only_initialization_emergency_steward_and_governance_transactions": True,
    "no_parameter_type_direction_or_scalar_purity_filter": True,
    "retain_full_normalized_topics_and_data": True,
    "provider_logs_are_context_not_programs_unless_transaction_also_has_configurator_log": True,
    "first_proxy_initialization_does_not_require_upgraded_event": True,
    "every_later_provider_implementation_transition_requires_matching_upgraded_event": True,
}

ALLOWED_METHODS = frozenset({"eth_chainId", "eth_blockNumber", "eth_getBlockByNumber", "eth_getLogs"})
REQUIRED_GATES = frozenset(
    {
        "parent_hashes_and_decisions",
        "frozen_official_address_sources",
        "exact_deployment_universe_and_split",
        "replicated_chain_identities",
        "deterministic_replicated_cutoff_headers",
        "complete_provider_log_directories",
        "complete_configurator_surface_derivation",
        "complete_bounded_configurator_log_directories",
        "strict_log_normalization",
        "no_duplicate_or_conflicting_logs",
        "source_corrected_configurator_upgrade_histories",
        "exact_program_grouping_and_block_headers",
        "minimum_train_support",
        "minimum_validation_support",
        "minimum_test_support",
        "minimum_total_support",
        "request_byte_log_and_program_caps",
        "zero_account_and_response_access_boundary",
    }
)
TRUE_ACCESS_KEYS = frozenset(
    {
        "official_deployment_source_opened",
        "chain_rpc_used",
        "cutoff_and_program_block_headers_opened",
        "provider_log_rows_opened",
        "configurator_log_rows_opened",
        "configuration_program_transaction_hashes_opened",
        "normalized_event_topics_and_data_opened",
        "development_ethereum_parent_reused",
    }
)
FALSE_ACCESS_KEYS = frozenset(
    {
        "transaction_rows_opened",
        "receipt_rows_opened",
        "calldata_rows_opened",
        "call_trace_rows_opened",
        "historical_contract_state_opened",
        "contract_code_opened",
        "governance_proposal_or_payload_rows_opened",
        "account_state_rows_opened",
        "participant_action_rows_opened",
        "liquidation_rows_opened",
        "price_or_oracle_value_rows_opened",
        "realized_response_rows_opened",
        "raw_rpc_payloads_retained",
        "paid_data_used",
        "external_workers_used",
        "gpu_used",
    }
)
EXPECTED_DECISION_POLICY: dict[str, object] = {
    "all_gates_required": True,
    "pass": "PASS_CROSS_DEPLOYMENT_PROGRAM_DIRECTORY_AUTHORIZE_B1_COMPILER_PROTOCOL_DESIGN_ONLY",
    "fail": "FAIL_CROSS_DEPLOYMENT_PROGRAM_DIRECTORY_KEEP_B1_ACCOUNTS_RESPONSES_G1_GPU_LOCKED",
    "authorized_next_stage": "separately_frozen_historical_abi_source_receipt_state_compiler_protocol_design_only",
}


class UniqueKeyLoader(yaml.SafeLoader):
    """YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[object, object]:
    loader.flatten_mapping(node)
    result: dict[object, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValueError(f"duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping)


def _mapping(value: object) -> Mapping[str, object] | None:
    if not isinstance(value, Mapping):
        return None
    return cast(Mapping[str, object], value)


def _sequence(value: object) -> Sequence[object] | None:
    if isinstance(value, str) or not isinstance(value, Sequence):
        return None
    return cast(Sequence[object], value)


def load_program_manifest(path: str | Path) -> dict[str, object]:
    """Load a duplicate-safe B0 manifest."""

    value = yaml.load(Path(path).read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
    if not isinstance(value, dict):
        raise ValueError("program manifest root must be a mapping")
    return cast(dict[str, object], value)


def sha256_file(path: Path) -> str:
    """Hash one file without loading it all into memory."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _deployment_map(manifest: Mapping[str, object]) -> dict[str, Mapping[str, object]]:
    values = _sequence(manifest.get("deployments"))
    if values is None:
        return {}
    result: dict[str, Mapping[str, object]] = {}
    for value in values:
        deployment = _mapping(value)
        if deployment is None or not isinstance(deployment.get("name"), str):
            return {}
        name = cast(str, deployment["name"])
        if name in result:
            return {}
        result[name] = deployment
    return result


def validate_program_manifest(manifest: Mapping[str, object]) -> list[str]:
    """Validate the frozen B0 identifiers, scope, thresholds, and access locks."""

    errors: list[str] = []
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version differs from the frozen contract")
    if manifest.get("audit_id") != AUDIT_ID:
        errors.append("audit_id differs from the frozen contract")
    if manifest.get("as_of") != AS_OF or manifest.get("stage") != STAGE:
        errors.append("date or stage differs from the frozen contract")
    if manifest.get("parents") != EXPECTED_PARENTS:
        errors.append("parents differ from the frozen artifact contract")

    source = _mapping(manifest.get("source_identity"))
    if source is None:
        errors.append("source_identity must be a mapping")
    else:
        if source.get("repository") != "https://github.com/aave-dao/aave-address-book.git":
            errors.append("source repository differs from the official frozen repository")
        if source.get("commit") != "70e2f303fe93616784148d6827df6644e5dda4db":
            errors.append("source commit differs from the frozen commit")
        if source.get("license") != "MIT":
            errors.append("source license differs from the frozen license")
        files = _sequence(source.get("files"))
        observed_files: dict[str, tuple[object, object, object]] = {}
        if files is not None:
            for value in files:
                item = _mapping(value)
                if item is None or not isinstance(item.get("deployment"), str):
                    observed_files = {}
                    break
                observed_files[cast(str, item["deployment"])] = (
                    item.get("path"),
                    item.get("git_blob"),
                    item.get("sha256"),
                )
        if observed_files != EXPECTED_SOURCE_FILES:
            errors.append("source file identities differ from the frozen address book")

    expected_order = [
        "ethereum",
        "arbitrum",
        "avalanche",
        "optimism",
        "polygon",
        "base",
        "gnosis",
        "bnb",
        "linea",
        "scroll",
    ]
    deployment_values = _sequence(manifest.get("deployments"))
    deployments = _deployment_map(manifest)
    observed_order = (
        [cast(str, cast(Mapping[str, object], item).get("name")) for item in deployment_values]
        if deployment_values is not None and all(isinstance(item, Mapping) for item in deployment_values)
        else []
    )
    if observed_order != expected_order or set(deployments) != set(EXPECTED_DEPLOYMENTS):
        errors.append("deployment universe or ordering differs from the frozen contract")
    for name, expected in EXPECTED_DEPLOYMENTS.items():
        observed = deployments.get(name)
        if observed is None:
            continue
        for key, expected_value in expected.items():
            if observed.get(key) != expected_value:
                errors.append(f"deployments.{name}.{key} differs from the frozen value")
        for address_key in ("pool_addresses_provider", "pool", "pool_configurator", "price_oracle"):
            try:
                normalize_address(observed.get(address_key), path=f"deployments.{name}.{address_key}")
            except ValueError as exc:
                errors.append(str(exc))

    selection = _mapping(manifest.get("selection_contract"))
    if selection is None:
        errors.append("selection_contract must be a mapping")
    else:
        expected_selection: dict[str, object] = {
            "development_deployment": "ethereum",
            "development_parent_reused_without_new_rpc": True,
            "primary_universe_selected_before_new_event_counts": True,
            "excluded_deployments_cannot_be_added_after_support_is_seen": True,
            "split_is_by_deployment_and_frozen_before_new_logs": True,
        }
        for key, expected_value in expected_selection.items():
            if selection.get(key) != expected_value:
                errors.append(f"selection_contract.{key} differs from the frozen value")

    cutoff = _mapping(manifest.get("cutoff"))
    expected_cutoff: dict[str, object] = {
        "timestamp_utc": "2026-08-15T00:00:00Z",
        "timestamp_unix": 1_786_752_000,
        "from_block": 0,
        "end_block_rule": "largest_block_with_timestamp_less_than_or_equal_to_cutoff",
        "require_next_block_timestamp_strictly_after_cutoff": True,
        "require_primary_replica_exact_number_hash_and_timestamp_agreement": True,
    }
    if cutoff != expected_cutoff:
        errors.append("cutoff rule differs from the frozen timestamp contract")

    if manifest.get("program_inclusion_rule") != EXPECTED_PROGRAM_INCLUSION_RULE:
        errors.append("program inclusion rule differs from the frozen contract")

    if manifest.get("support_thresholds") != EXPECTED_SUPPORT_THRESHOLDS:
        errors.append("support thresholds differ from the frozen OOD contract")

    rpc = _mapping(manifest.get("rpc"))
    expected_rpc: dict[str, object] = {
        "maximum_requests_per_second_across_sources": 2,
        "maximum_transport_retries": 2,
        "maximum_http_attempts": 50_000,
        "maximum_response_bytes": 536_870_912,
        "maximum_normalized_logs": 250_000,
        "maximum_programs": 50_000,
        "log_response_limit": 10_000,
        "root_partition_block_count": 250_000,
        "raw_response_payloads_retained": False,
        "endpoint_substitution_after_freeze": False,
        "rpc_error_on_multiblock_log_interval_action": "recursively_bisect_inclusive_interval",
        "rpc_error_on_single_block_log_interval_action": "fail",
        "exactly_limit_response_action": "recursively_bisect_inclusive_interval",
        "learned_range_limit_reused_within_deployment": True,
        "failed_logical_requests_retained": True,
        "user_agent": "EcoPhys-V14-Aave-cross-deployment-program-directory/1.0",
    }
    if rpc is None:
        errors.append("rpc must be a mapping")
    else:
        for key, expected_value in expected_rpc.items():
            if rpc.get(key) != expected_value:
                errors.append(f"rpc.{key} differs from the frozen value")
        methods = _sequence(rpc.get("allowed_methods"))
        if methods is None or set(methods) != ALLOWED_METHODS or len(methods) != len(ALLOWED_METHODS):
            errors.append("allowed_methods differ from the frozen set")

    access = _mapping(manifest.get("access_boundary"))
    if access is None or set(access) != TRUE_ACCESS_KEYS | FALSE_ACCESS_KEYS:
        errors.append("access boundary keys differ from the frozen contract")
    else:
        for key in sorted(TRUE_ACCESS_KEYS):
            if access.get(key) is not True:
                errors.append(f"access_boundary.{key} must be true")
        for key in sorted(FALSE_ACCESS_KEYS):
            if access.get(key) is not False:
                errors.append(f"access_boundary.{key} must be false")

    gates = _sequence(manifest.get("gates"))
    if gates is None or set(gates) != REQUIRED_GATES or len(gates) != len(REQUIRED_GATES):
        errors.append("gates differ from the frozen set")
    if manifest.get("decision_policy") != EXPECTED_DECISION_POLICY:
        errors.append("decision policy differs from the frozen contract")
    return errors


def validate_parent_artifacts(manifest: Mapping[str, object], root: str | Path) -> list[str]:
    """Verify the immutable A1a and development-replay parents."""

    errors: list[str] = []
    parents = _mapping(manifest.get("parents"))
    if parents is None:
        return ["parents must be a mapping"]
    root_path = Path(root)
    pairs = (
        ("bundle_summary_path", "bundle_summary_sha256"),
        ("bundle_manifest_path", "bundle_manifest_sha256"),
        ("a1a_summary_path", "a1a_summary_sha256"),
        ("a1a_directory_path", "a1a_directory_sha256"),
    )
    for path_key, hash_key in pairs:
        relative = parents.get(path_key)
        expected_hash = parents.get(hash_key)
        if not isinstance(relative, str) or not isinstance(expected_hash, str):
            errors.append(f"invalid parent fields {path_key}/{hash_key}")
            continue
        path = root_path / relative
        if not path.is_file():
            errors.append(f"missing parent artifact: {relative}")
        elif sha256_file(path) != expected_hash:
            errors.append(f"parent hash mismatch: {relative}")
    for path_key, decision_key in (
        ("bundle_summary_path", "expected_bundle_decision"),
        ("a1a_summary_path", "expected_a1a_decision"),
    ):
        relative = parents.get(path_key)
        if not isinstance(relative, str) or not (root_path / relative).is_file():
            continue
        try:
            value: object = json.loads((root_path / relative).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"cannot parse parent {relative}: {exc}")
            continue
        parent = _mapping(value)
        if parent is None or parent.get("decision") != parents.get(decision_key):
            errors.append(f"parent decision mismatch: {relative}")
    return errors


class RpcCallError(RuntimeError):
    """Bounded JSON-RPC request failure eligible for interval bisection."""


class RpcCollector:
    """Rate-limited JSON-RPC client retaining only response hashes and normalized rows."""

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
        self._next_id = 1
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": user_agent})
        self.http_attempts = 0
        self.response_bytes = 0
        self.records: list[dict[str, object]] = []
        self.failed_calls: list[dict[str, object]] = []

    def call(
        self,
        *,
        url: str,
        deployment: str,
        provider: str,
        label: str,
        method: str,
        params: Sequence[object],
    ) -> object:
        """Issue one bounded call and discard its raw body after hashing."""

        if method not in ALLOWED_METHODS:
            raise ValueError(f"forbidden JSON-RPC method: {method}")
        request_id = self._next_id
        self._next_id += 1
        request = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": list(params)}
        prior_errors: list[str] = []
        for attempt in range(self._maximum_transport_retries + 1):
            if self.http_attempts >= self._maximum_http_attempts:
                raise RuntimeError("maximum HTTP-attempt cap reached")
            if self._last_start is not None:
                time.sleep(max(0.0, self._minimum_interval - (time.monotonic() - self._last_start)))
            self._last_start = time.monotonic()
            self.http_attempts += 1
            try:
                response = self._session.post(url, json=request, timeout=60.0)
                body = response.content
                self.response_bytes += len(body)
                if self.response_bytes > self._maximum_response_bytes:
                    raise RuntimeError("maximum response-byte cap exceeded")
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
                            "request_index": len(self.records),
                            "deployment": deployment,
                            "provider": provider,
                            "label": label,
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
        self.failed_calls.append(
            {
                "failed_call_index": len(self.failed_calls),
                "deployment": deployment,
                "provider": provider,
                "label": label,
                "method": method,
                "params": list(params),
                "request_sha256": canonical_json_sha256(request),
                "attempt_count": self._maximum_transport_retries + 1,
                "errors": prior_errors,
                "failed_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            }
        )
        raise RpcCallError(f"{deployment}:{provider}:{label} failed: {prior_errors}")


def _rpc_from_manifest(manifest: Mapping[str, object]) -> RpcCollector:
    rpc = cast(Mapping[str, object], manifest["rpc"])
    return RpcCollector(
        user_agent=cast(str, rpc["user_agent"]),
        maximum_requests_per_second=float(cast(int, rpc["maximum_requests_per_second_across_sources"])),
        maximum_transport_retries=cast(int, rpc["maximum_transport_retries"]),
        maximum_http_attempts=cast(int, rpc["maximum_http_attempts"]),
        maximum_response_bytes=cast(int, rpc["maximum_response_bytes"]),
    )


def normalize_block_header(value: object, *, expected_number: int | None, path: str) -> dict[str, object]:
    """Retain only the canonical block identity and timestamp."""

    block = _mapping(value)
    if block is None:
        raise ValueError(f"{path} must be a block mapping")
    number = decode_quantity(block.get("number"), path=f"{path}.number")
    if expected_number is not None and number != expected_number:
        raise ValueError(f"{path}.number differs from the requested block")
    timestamp = decode_quantity(block.get("timestamp"), path=f"{path}.timestamp")
    return {
        "number": number,
        "hash": normalize_hash(block.get("hash"), path=f"{path}.hash"),
        "parent_hash": normalize_hash(block.get("parentHash"), path=f"{path}.parentHash"),
        "timestamp_unix": timestamp,
        "timestamp_utc": datetime.fromtimestamp(timestamp, UTC).isoformat().replace("+00:00", "Z"),
    }


def resolve_endpoint_cutoff(
    rpc: RpcCollector,
    *,
    deployment: str,
    provider: str,
    url: str,
    expected_chain_id: str,
    cutoff_timestamp: int,
) -> dict[str, object]:
    """Find the largest block at or before a frozen timestamp by deterministic binary search."""

    chain_id_value = rpc.call(
        url=url,
        deployment=deployment,
        provider=provider,
        label="chain_id",
        method="eth_chainId",
        params=[],
    )
    if chain_id_value != expected_chain_id:
        raise ValueError(f"{deployment}:{provider} chain ID mismatch")
    latest_value = rpc.call(
        url=url,
        deployment=deployment,
        provider=provider,
        label="latest_block_number",
        method="eth_blockNumber",
        params=[],
    )
    latest_number = decode_quantity(latest_value, path=f"{deployment}.{provider}.latest")
    header_cache: dict[int, dict[str, object]] = {}

    def header(number: int) -> dict[str, object]:
        cached = header_cache.get(number)
        if cached is not None:
            return cached
        normalized = normalize_block_header(
            rpc.call(
                url=url,
                deployment=deployment,
                provider=provider,
                label=f"cutoff_search_header:{number}",
                method="eth_getBlockByNumber",
                params=[hex(number), False],
            ),
            expected_number=number,
            path=f"{deployment}.{provider}.header[{number}]",
        )
        header_cache[number] = normalized
        return normalized

    latest_header = header(latest_number)
    if cast(int, latest_header["timestamp_unix"]) <= cutoff_timestamp:
        raise ValueError(f"{deployment}:{provider} latest block does not pass the frozen cutoff")
    genesis_header = header(0)
    if cast(int, genesis_header["timestamp_unix"]) > cutoff_timestamp:
        raise ValueError(f"{deployment}:{provider} genesis is later than the frozen cutoff")
    low = 0
    high = latest_number
    while low < high:
        midpoint = (low + high + 1) // 2
        if cast(int, header(midpoint)["timestamp_unix"]) <= cutoff_timestamp:
            low = midpoint
        else:
            high = midpoint - 1
    cutoff_header = header(low)
    next_header = header(low + 1)
    if not (
        cast(int, cutoff_header["timestamp_unix"])
        <= cutoff_timestamp
        < cast(int, next_header["timestamp_unix"])
    ):
        raise ValueError(f"{deployment}:{provider} adjacent cutoff headers do not bracket cutoff")
    return {
        "provider": provider,
        "chain_id": chain_id_value,
        "latest_header_at_collection": latest_header,
        "cutoff_header": cutoff_header,
        "next_header": next_header,
        "binary_search_unique_header_count": len(header_cache),
    }


def resolve_replicated_cutoff(
    rpc: RpcCollector, deployment: Mapping[str, object], *, cutoff_timestamp: int
) -> dict[str, object]:
    """Resolve and cross-provider replicate one deployment cutoff."""

    name = cast(str, deployment["name"])
    expected_chain_id = cast(str, deployment["chain_id_hex"])
    primary = resolve_endpoint_cutoff(
        rpc,
        deployment=name,
        provider="primary",
        url=cast(str, deployment["primary_rpc_url"]),
        expected_chain_id=expected_chain_id,
        cutoff_timestamp=cutoff_timestamp,
    )
    replica = resolve_endpoint_cutoff(
        rpc,
        deployment=name,
        provider="replica",
        url=cast(str, deployment["replica_rpc_url"]),
        expected_chain_id=expected_chain_id,
        cutoff_timestamp=cutoff_timestamp,
    )
    replicated = (
        primary["cutoff_header"] == replica["cutoff_header"]
        and primary["next_header"] == replica["next_header"]
    )
    return {"primary": primary, "replica": replica, "replicated": replicated}


def normalize_program_log(
    raw: Mapping[str, object],
    *,
    deployment: str,
    chain_id: int,
    expected_address: str,
    role: str,
    from_block: int,
    to_block: int,
) -> dict[str, object]:
    """Normalize a provider or Configurator-surface log without inventing ABI semantics."""

    address = normalize_address(raw.get("address"), path="log.address")
    if address != expected_address:
        raise ValueError("log address differs from the requested stream")
    block_number = decode_quantity(raw.get("blockNumber"), path="log.blockNumber")
    if not from_block <= block_number <= to_block:
        raise ValueError("log block lies outside the requested interval")
    topics_value = raw.get("topics")
    if not isinstance(topics_value, list) or not topics_value:
        raise ValueError("log topics must be a nonempty list")
    topics = [normalize_hash(value, path=f"log.topics[{index}]") for index, value in enumerate(topics_value)]
    data = normalize_data(raw.get("data"), path="log.data")
    if raw.get("removed", False) is not False:
        raise ValueError("removed logs are forbidden")
    base: dict[str, object] = {
        "deployment": deployment,
        "chain_id": chain_id,
        "role": role,
        "address": address,
        "block_number": block_number,
        "block_hash": normalize_hash(raw.get("blockHash"), path="log.blockHash"),
        "transaction_hash": normalize_hash(raw.get("transactionHash"), path="log.transactionHash"),
        "transaction_index": decode_quantity(raw.get("transactionIndex"), path="log.transactionIndex"),
        "log_index": decode_quantity(raw.get("logIndex"), path="log.logIndex"),
        "topic0": topics[0],
        "topics": topics,
        "data": data,
        "topic_count": len(topics),
        "data_byte_count": (len(data) - 2) // 2,
    }
    if role == "provider":
        semantic = normalize_directory_log(
            raw,
            expected_address=expected_address,
            role="provider",
            from_block=from_block,
            to_block=to_block,
        )
        for key, value in semantic.items():
            if key not in base:
                base[key] = value
        return base
    if role != "configurator":
        raise ValueError(f"unsupported log role: {role}")
    if topics[0] == UPGRADED_TOPIC:
        if len(topics) != 2 or data != "0x" or topics[1][2:26] != "0" * 24:
            raise ValueError("malformed Configurator Upgraded log")
        base.update({"event_type": "upgraded", "implementation": "0x" + topics[1][-40:]})
    else:
        base["event_type"] = "opaque_configurator_event"
    return base


def deduplicate_program_logs(
    records: Sequence[Mapping[str, object]],
) -> tuple[list[dict[str, object]], int, int]:
    """Deduplicate exact chain/log identities and count conflicting observations."""

    by_identity: dict[tuple[object, ...], dict[str, object]] = {}
    duplicate_count = 0
    conflict_count = 0
    for value in records:
        record = dict(value)
        identity = (
            record["chain_id"],
            record["block_hash"],
            record["transaction_hash"],
            record["log_index"],
            record["address"],
        )
        existing = by_identity.get(identity)
        if existing is None:
            by_identity[identity] = record
        elif existing == record:
            duplicate_count += 1
        else:
            conflict_count += 1
    ordered = sorted(
        by_identity.values(),
        key=lambda item: (
            cast(int, item["chain_id"]),
            cast(int, item["block_number"]),
            cast(int, item["transaction_index"]),
            cast(int, item["log_index"]),
            cast(str, item["address"]),
        ),
    )
    return ordered, duplicate_count, conflict_count


def collect_log_stream(
    rpc: RpcCollector,
    *,
    deployment: str,
    chain_id: int,
    url: str,
    address: str,
    role: str,
    intervals: Sequence[tuple[int, int]],
    response_limit: int,
    maximum_normalized_logs: int,
    initial_maximum_interval_span: int | None = None,
) -> tuple[list[dict[str, object]], dict[str, int]]:
    """Collect a complete inclusive stream with fail-closed saturation/error bisection."""

    accepted: list[dict[str, object]] = []
    query_count = 0
    saturated_split_count = 0
    rpc_error_split_count = 0
    preemptive_split_count = 0
    maximum_depth = 0
    learned_maximum_interval_span = initial_maximum_interval_span or 0

    def visit(interval_from: int, interval_to: int, *, root_index: int, depth: int) -> None:
        nonlocal query_count, saturated_split_count, rpc_error_split_count
        nonlocal preemptive_split_count, maximum_depth, learned_maximum_interval_span
        interval_span = interval_to - interval_from + 1
        if learned_maximum_interval_span > 0 and interval_span > learned_maximum_interval_span:
            preemptive_split_count += 1
            left, right = split_inclusive_interval(interval_from, interval_to)
            visit(*left, root_index=root_index, depth=depth + 1)
            visit(*right, root_index=root_index, depth=depth + 1)
            return
        query_count += 1
        maximum_depth = max(maximum_depth, depth)
        try:
            result = rpc.call(
                url=url,
                deployment=deployment,
                provider="primary",
                label=(f"{role}:{address}:root={root_index}:depth={depth}:{interval_from}-{interval_to}"),
                method="eth_getLogs",
                params=[
                    {
                        "address": address,
                        "fromBlock": hex(interval_from),
                        "toBlock": hex(interval_to),
                    }
                ],
            )
        except RpcCallError:
            if interval_from == interval_to:
                raise
            rpc_error_split_count += 1
            candidate_span = max(1, interval_span // 2)
            if learned_maximum_interval_span == 0 or candidate_span < learned_maximum_interval_span:
                learned_maximum_interval_span = candidate_span
            left, right = split_inclusive_interval(interval_from, interval_to)
            visit(*left, root_index=root_index, depth=depth + 1)
            visit(*right, root_index=root_index, depth=depth + 1)
            return
        if not isinstance(result, list):
            raise ValueError(f"{deployment}:{role} eth_getLogs result must be a list")
        if len(result) >= response_limit:
            if interval_from == interval_to:
                raise RuntimeError(f"{deployment}:{role} saturated a single block")
            saturated_split_count += 1
            left, right = split_inclusive_interval(interval_from, interval_to)
            visit(*left, root_index=root_index, depth=depth + 1)
            visit(*right, root_index=root_index, depth=depth + 1)
            return
        for index, raw in enumerate(result):
            raw_mapping = _mapping(raw)
            if raw_mapping is None:
                raise ValueError(f"{deployment}:{role} log[{index}] must be a mapping")
            accepted.append(
                normalize_program_log(
                    raw_mapping,
                    deployment=deployment,
                    chain_id=chain_id,
                    expected_address=address,
                    role=role,
                    from_block=interval_from,
                    to_block=interval_to,
                )
            )
            if len(accepted) > maximum_normalized_logs:
                raise RuntimeError("maximum normalized-log cap exceeded")

    for root_index, interval in enumerate(intervals):
        visit(*interval, root_index=root_index, depth=0)
    return accepted, {
        "root_interval_count": len(intervals),
        "query_count": query_count,
        "saturated_split_count": saturated_split_count,
        "rpc_error_split_count": rpc_error_split_count,
        "preemptive_split_count": preemptive_split_count,
        "maximum_split_depth": maximum_depth,
        "learned_maximum_interval_span": learned_maximum_interval_span,
    }


def derive_configurator_surfaces(
    provider_records: Sequence[Mapping[str, object]], *, official_current: str
) -> dict[str, object]:
    """Derive every Configurator address route visible in the complete provider history."""

    surfaces: set[str] = set()
    creation_rows: list[dict[str, object]] = []
    proxy_set_rows: list[dict[str, object]] = []
    direct_set_rows: list[dict[str, object]] = []
    unknown_rows: list[dict[str, object]] = []
    for item in provider_records:
        event_type = item.get("event_type")
        if event_type == "unknown_provider":
            unknown_rows.append(dict(item))
        if item.get("id") != CONFIGURATOR_ID:
            continue
        if event_type == "proxy_created":
            address = cast(str, item["proxy"])
            surfaces.add(address)
            creation_rows.append(dict(item))
        elif event_type == "address_set_as_proxy":
            address = cast(str, item["proxy"])
            surfaces.add(address)
            proxy_set_rows.append(dict(item))
        elif event_type == "address_set":
            address = cast(str, item["new_address"])
            if address != ZERO_ADDRESS:
                surfaces.add(address)
            direct_set_rows.append(dict(item))
    ordered_surfaces = sorted(surfaces)
    return {
        "addresses": ordered_surfaces,
        "address_count": len(ordered_surfaces),
        "official_current": official_current,
        "official_current_observed": official_current in surfaces,
        "proxy_created_rows": creation_rows,
        "address_set_as_proxy_rows": proxy_set_rows,
        "direct_address_set_rows": direct_set_rows,
        "unknown_provider_rows": unknown_rows,
    }


def source_corrected_configurator_history(
    provider_records: Sequence[Mapping[str, object]],
    configurator_records: Sequence[Mapping[str, object]],
    *,
    surfaces: Sequence[str],
) -> dict[str, object]:
    """Match all post-initial provider transitions to proxy upgrades."""

    creations = [
        dict(item)
        for item in provider_records
        if item.get("event_type") == "proxy_created" and item.get("id") == CONFIGURATOR_ID
    ]
    direct_sets = [
        dict(item)
        for item in provider_records
        if item.get("event_type") == "address_set" and item.get("id") == CONFIGURATOR_ID
    ]
    transitions: list[dict[str, object]] = []
    for item in provider_records:
        if item.get("event_type") == "pool_configurator_updated":
            transitions.append(
                {
                    "block_number": item["block_number"],
                    "transaction_hash": item["transaction_hash"],
                    "log_index": item["log_index"],
                    "route": "pool_configurator_updated",
                    "old_implementation": item["old_address"],
                    "new_implementation": item["new_address"],
                }
            )
        elif item.get("event_type") == "address_set_as_proxy" and item.get("id") == CONFIGURATOR_ID:
            transitions.append(
                {
                    "block_number": item["block_number"],
                    "transaction_hash": item["transaction_hash"],
                    "log_index": item["log_index"],
                    "route": "address_set_as_proxy",
                    "old_implementation": item["old_implementation"],
                    "new_implementation": item["new_implementation"],
                    "declared_proxy": item["proxy"],
                }
            )
    transitions.sort(key=lambda item: (cast(int, item["block_number"]), cast(int, item["log_index"])))
    upgrades = [
        {
            "address": item["address"],
            "block_number": item["block_number"],
            "transaction_hash": item["transaction_hash"],
            "log_index": item["log_index"],
            "implementation": item["implementation"],
        }
        for item in configurator_records
        if item.get("event_type") == "upgraded"
    ]
    upgrades.sort(key=lambda item: (cast(int, item["block_number"]), cast(int, item["log_index"])))
    continuity = bool(transitions) and transitions[0]["old_implementation"] == ZERO_ADDRESS
    for prior, current in pairwise(transitions):
        continuity = continuity and prior["new_implementation"] == current["old_implementation"]
    initial_creation_matches = (
        len(creations) == 1
        and bool(transitions)
        and creations[0].get("transaction_hash") == transitions[0]["transaction_hash"]
        and creations[0].get("implementation") == transitions[0]["new_implementation"]
        and creations[0].get("proxy") in surfaces
    )
    later_transition_keys = Counter(
        (item["transaction_hash"], item["new_implementation"]) for item in transitions[1:]
    )
    upgrade_keys = Counter((item["transaction_hash"], item["implementation"]) for item in upgrades)
    initial_key = (
        (transitions[0]["transaction_hash"], transitions[0]["new_implementation"]) if transitions else None
    )
    initial_upgrade_count = upgrade_keys[initial_key] if initial_key is not None else 0
    later_upgrade_keys = upgrade_keys.copy()
    if initial_key is not None:
        del later_upgrade_keys[initial_key]
    checks = {
        "one_initial_proxy_creation": len(creations) == 1,
        "initial_creation_matches_first_transition": initial_creation_matches,
        "initial_transition_allows_zero_or_one_matching_upgrade": bool(transitions)
        and initial_upgrade_count <= 1,
        "continuous_old_to_new_implementation_chain": continuity,
        "every_later_transition_has_one_matching_upgrade": later_transition_keys == later_upgrade_keys,
        "all_upgrades_emitted_by_derived_surfaces": all(item["address"] in surfaces for item in upgrades),
        "no_direct_configurator_address_set": not direct_sets,
        "all_proxy_routes_name_derived_surface": all(
            item.get("route") != "address_set_as_proxy" or item.get("declared_proxy") in surfaces
            for item in transitions
        ),
    }
    return {
        "proxy_creation_count": len(creations),
        "transition_count": len(transitions),
        "upgrade_count": len(upgrades),
        "initial_upgrade_count": initial_upgrade_count,
        "direct_address_set_count": len(direct_sets),
        "transitions": transitions,
        "upgrades": upgrades,
        "checks": checks,
        "passed": all(checks.values()),
    }


def fetch_program_block_headers(
    rpc: RpcCollector,
    *,
    deployment: str,
    url: str,
    records: Sequence[Mapping[str, object]],
) -> dict[int, dict[str, object]]:
    """Fetch and validate the timestamp header for every program block."""

    hashes_by_number: dict[int, set[str]] = defaultdict(set)
    for item in records:
        hashes_by_number[cast(int, item["block_number"])].add(cast(str, item["block_hash"]))
    headers: dict[int, dict[str, object]] = {}
    for block_number in sorted(hashes_by_number):
        if len(hashes_by_number[block_number]) != 1:
            raise ValueError(f"{deployment}: conflicting log block hashes at {block_number}")
        header = normalize_block_header(
            rpc.call(
                url=url,
                deployment=deployment,
                provider="primary",
                label=f"program_block_header:{block_number}",
                method="eth_getBlockByNumber",
                params=[hex(block_number), False],
            ),
            expected_number=block_number,
            path=f"{deployment}.program_header[{block_number}]",
        )
        if header["hash"] not in hashes_by_number[block_number]:
            raise ValueError(f"{deployment}: program header/log hash mismatch at {block_number}")
        headers[block_number] = header
    return headers


def _calendar_quarter(timestamp: int) -> str:
    moment = datetime.fromtimestamp(timestamp, UTC)
    return f"{moment.year}-Q{(moment.month - 1) // 3 + 1}"


def build_program_records(
    configurator_records: Sequence[Mapping[str, object]],
    provider_records: Sequence[Mapping[str, object]],
    *,
    deployment: str,
    chain_id: int,
    split: str,
    headers: Mapping[int, Mapping[str, object]],
) -> list[dict[str, object]]:
    """Group every Configurator-surface log by the frozen chain/transaction key."""

    ordered = sorted(
        configurator_records,
        key=lambda item: (
            cast(int, item["block_number"]),
            cast(int, item["transaction_index"]),
            cast(int, item["log_index"]),
            cast(str, item["address"]),
        ),
    )
    provider_count_by_tx = Counter(cast(str, item["transaction_hash"]) for item in provider_records)
    programs: list[dict[str, object]] = []
    for transaction_hash, grouped in groupby(ordered, key=lambda item: cast(str, item["transaction_hash"])):
        logs = [dict(item) for item in grouped]
        block_numbers = {cast(int, item["block_number"]) for item in logs}
        block_hashes = {cast(str, item["block_hash"]) for item in logs}
        transaction_indices = {cast(int, item["transaction_index"]) for item in logs}
        if len(block_numbers) != 1 or len(block_hashes) != 1 or len(transaction_indices) != 1:
            raise ValueError(f"{deployment}:{transaction_hash} has inconsistent log identity")
        block_number = next(iter(block_numbers))
        header = headers.get(block_number)
        if header is None or header.get("hash") not in block_hashes:
            raise ValueError(f"{deployment}:{transaction_hash} lacks a matching program header")
        timestamp = cast(int, header["timestamp_unix"])
        topic_counts = dict(sorted(Counter(cast(str, item["topic0"]) for item in logs).items()))
        programs.append(
            {
                "program_id": f"{chain_id}:{transaction_hash}",
                "deployment": deployment,
                "chain_id": chain_id,
                "split": split,
                "block_number": block_number,
                "block_hash": next(iter(block_hashes)),
                "block_timestamp_unix": timestamp,
                "block_timestamp_utc": header["timestamp_utc"],
                "calendar_quarter": _calendar_quarter(timestamp),
                "transaction_hash": transaction_hash,
                "transaction_index": next(iter(transaction_indices)),
                "configurator_addresses": sorted({cast(str, item["address"]) for item in logs}),
                "configurator_log_count": len(logs),
                "unique_topic0_count": len(topic_counts),
                "topic0_counts": topic_counts,
                "contains_upgrade": any(item.get("event_type") == "upgraded" for item in logs),
                "multi_log": len(logs) >= 2,
                "same_transaction_provider_log_count": provider_count_by_tx[transaction_hash],
                "configurator_logs": logs,
            }
        )
    if len(programs) != len({cast(str, item["program_id"]) for item in programs}):
        raise ValueError(f"{deployment}: duplicate program identity")
    return programs


def collect_deployment_directory(
    rpc: RpcCollector,
    deployment: Mapping[str, object],
    *,
    cutoff_timestamp: int,
    rpc_config: Mapping[str, object],
    remaining_log_budget: int,
) -> tuple[dict[str, object], dict[str, object]]:
    """Collect one deployment's provider surface and complete Configurator program directory."""

    name = cast(str, deployment["name"])
    chain_id = cast(int, deployment["chain_id"])
    split = cast(str, deployment["split"])
    primary_url = cast(str, deployment["primary_rpc_url"])
    cutoff = resolve_replicated_cutoff(rpc, deployment, cutoff_timestamp=cutoff_timestamp)
    primary_cutoff = cast(Mapping[str, object], cutoff["primary"])
    cutoff_header = cast(Mapping[str, object], primary_cutoff["cutoff_header"])
    to_block = cast(int, cutoff_header["number"])
    intervals = root_intervals(0, to_block, cast(int, rpc_config["root_partition_block_count"]))
    provider_address = cast(str, deployment["pool_addresses_provider"])
    provider_raw, provider_queries = collect_log_stream(
        rpc,
        deployment=name,
        chain_id=chain_id,
        url=primary_url,
        address=provider_address,
        role="provider",
        intervals=intervals,
        response_limit=cast(int, rpc_config["log_response_limit"]),
        maximum_normalized_logs=remaining_log_budget,
    )
    provider_records, provider_duplicates, provider_conflicts = deduplicate_program_logs(provider_raw)
    learned_span = provider_queries["learned_maximum_interval_span"] or None
    official_configurator = cast(str, deployment["pool_configurator"])
    surface = derive_configurator_surfaces(provider_records, official_current=official_configurator)
    derived_addresses = cast(list[str], surface["addresses"])
    addresses_to_scan = sorted(set(derived_addresses) | {official_configurator})
    configurator_raw: list[dict[str, object]] = []
    configurator_queries: dict[str, dict[str, int]] = {}
    for address in addresses_to_scan:
        available = remaining_log_budget - len(provider_records) - len(configurator_raw)
        if available < 0:
            raise RuntimeError("maximum normalized-log cap exceeded")
        address_records, address_queries = collect_log_stream(
            rpc,
            deployment=name,
            chain_id=chain_id,
            url=primary_url,
            address=address,
            role="configurator",
            intervals=intervals,
            response_limit=cast(int, rpc_config["log_response_limit"]),
            maximum_normalized_logs=available,
            initial_maximum_interval_span=learned_span,
        )
        configurator_raw.extend(address_records)
        configurator_queries[address] = address_queries
        observed_span = address_queries["learned_maximum_interval_span"]
        if observed_span > 0 and (learned_span is None or observed_span < learned_span):
            learned_span = observed_span
    configurator_records, configurator_duplicates, configurator_conflicts = deduplicate_program_logs(
        configurator_raw
    )
    history = source_corrected_configurator_history(
        provider_records,
        configurator_records,
        surfaces=addresses_to_scan,
    )
    headers = fetch_program_block_headers(
        rpc,
        deployment=name,
        url=primary_url,
        records=configurator_records,
    )
    programs = build_program_records(
        configurator_records,
        provider_records,
        deployment=name,
        chain_id=chain_id,
        split=split,
        headers=headers,
    )
    topic_counts = dict(sorted(Counter(cast(str, item["topic0"]) for item in configurator_records).items()))
    program_timestamps = [cast(int, item["block_timestamp_unix"]) for item in programs]
    deployment_checks = {
        "chain_identity_replicated": (
            cast(Mapping[str, object], cutoff["primary"])["chain_id"] == deployment["chain_id_hex"]
            and cast(Mapping[str, object], cutoff["replica"])["chain_id"] == deployment["chain_id_hex"]
        ),
        "cutoff_headers_replicated": cutoff["replicated"] is True,
        "provider_directory_complete": provider_queries["query_count"] >= len(intervals),
        "configurator_surface_complete": surface["official_current_observed"] is True
        and not cast(list[object], surface["unknown_provider_rows"]),
        "configurator_directories_complete": set(configurator_queries) == set(addresses_to_scan)
        and all(value["query_count"] >= len(intervals) for value in configurator_queries.values()),
        "no_duplicate_or_conflicting_logs": provider_duplicates == 0
        and provider_conflicts == 0
        and configurator_duplicates == 0
        and configurator_conflicts == 0,
        "source_corrected_upgrade_history": history["passed"] is True,
        "program_headers_complete": len(headers)
        == len({cast(int, item["block_number"]) for item in programs}),
    }
    summary = {
        "deployment": name,
        "chain_id": chain_id,
        "split": split,
        "official_addresses": {
            "pool_addresses_provider": provider_address,
            "pool": deployment["pool"],
            "pool_configurator": official_configurator,
            "price_oracle": deployment["price_oracle"],
        },
        "cutoff": cutoff,
        "root_interval_count_per_stream": len(intervals),
        "provider_directory": {
            "normalized_log_count": len(provider_records),
            "duplicate_count": provider_duplicates,
            "conflict_count": provider_conflicts,
            "unknown_event_count": len(cast(list[object], surface["unknown_provider_rows"])),
            "queries": provider_queries,
        },
        "configurator_surface": surface,
        "configurator_directory": {
            "normalized_log_count": len(configurator_records),
            "duplicate_count": configurator_duplicates,
            "conflict_count": configurator_conflicts,
            "topic0_counts": topic_counts,
            "queries_by_address": configurator_queries,
        },
        "configurator_history": history,
        "program_directory": {
            "program_count": len(programs),
            "program_block_count": len(headers),
            "unique_topic0_count": len(topic_counts),
            "multi_log_program_count": sum(cast(bool, item["multi_log"]) for item in programs),
            "upgrade_program_count": sum(cast(bool, item["contains_upgrade"]) for item in programs),
            "first_timestamp_unix": min(program_timestamps) if program_timestamps else None,
            "last_timestamp_unix": max(program_timestamps) if program_timestamps else None,
            "distinct_calendar_quarters": sorted({cast(str, item["calendar_quarter"]) for item in programs}),
        },
        "checks": deployment_checks,
        "passed": all(deployment_checks.values()),
    }
    directory = {
        "deployment": name,
        "chain_id": chain_id,
        "split": split,
        "cutoff_header": cutoff_header,
        "provider_records": provider_records,
        "program_block_headers": [headers[number] for number in sorted(headers)],
        "programs": programs,
    }
    return summary, directory


def summarize_support(
    programs: Sequence[Mapping[str, object]],
    thresholds: Mapping[str, object],
) -> tuple[dict[str, object], dict[str, bool]]:
    """Evaluate the precommitted train/validation/test breadth thresholds."""

    per_deployment = Counter(cast(str, item["deployment"]) for item in programs)
    minimum_per_deployment = cast(int, thresholds["per_named_non_development_deployment_minimum_programs"])
    split_summaries: dict[str, object] = {}
    split_passes: dict[str, bool] = {}
    for split in ("train", "validation", "test"):
        contract = cast(Mapping[str, object], thresholds[split])
        named = cast(Sequence[str], contract["deployments"])
        rows = [item for item in programs if item.get("split") == split]
        topics = {topic for item in rows for topic in cast(Mapping[str, object], item["topic0_counts"])}
        timestamps = [cast(int, item["block_timestamp_unix"]) for item in rows]
        quarters = {cast(str, item["calendar_quarter"]) for item in rows}
        deployments_with_upgrade = {
            cast(str, item["deployment"]) for item in rows if cast(bool, item["contains_upgrade"])
        }
        span_days = (max(timestamps) - min(timestamps)) / 86_400.0 if len(timestamps) >= 2 else 0.0
        checks = {
            "exact_named_deployments": {cast(str, item["deployment"]) for item in rows}.issubset(set(named)),
            "minimum_each_named_deployment": all(
                per_deployment[name] >= minimum_per_deployment for name in named
            ),
            "minimum_programs": len(rows) >= cast(int, contract["minimum_programs"]),
            "minimum_unique_topic0": len(topics) >= cast(int, contract["minimum_unique_topic0"]),
            "minimum_multi_log_programs": sum(cast(bool, item["multi_log"]) for item in rows)
            >= cast(int, contract["minimum_multi_log_programs"]),
            "minimum_deployments_with_upgrade_program": len(deployments_with_upgrade)
            >= cast(int, contract["minimum_deployments_with_upgrade_program"]),
            "minimum_span_days": span_days >= cast(int, contract["minimum_span_days"]),
            "minimum_distinct_calendar_quarters": len(quarters)
            >= cast(int, contract["minimum_distinct_calendar_quarters"]),
        }
        split_summaries[split] = {
            "named_deployments": list(named),
            "program_count": len(rows),
            "program_count_by_deployment": {name: per_deployment[name] for name in named},
            "unique_topic0_count": len(topics),
            "multi_log_program_count": sum(cast(bool, item["multi_log"]) for item in rows),
            "deployments_with_upgrade_program": sorted(deployments_with_upgrade),
            "first_timestamp_unix": min(timestamps) if timestamps else None,
            "last_timestamp_unix": max(timestamps) if timestamps else None,
            "span_days": span_days,
            "distinct_calendar_quarters": sorted(quarters),
            "checks": checks,
            "passed": all(checks.values()),
        }
        split_passes[split] = all(checks.values())
    total_minimum = cast(int, thresholds["minimum_total_non_development_programs"])
    summary = {
        "per_deployment_program_count": dict(sorted(per_deployment.items())),
        "minimum_each_named_deployment": minimum_per_deployment,
        "splits": split_summaries,
        "total_non_development_program_count": len(programs),
        "minimum_total_non_development_programs": total_minimum,
        "total_support_passed": len(programs) >= total_minimum,
    }
    return summary, {
        "train": split_passes["train"],
        "validation": split_passes["validation"],
        "test": split_passes["test"],
        "total": len(programs) >= total_minimum,
    }


def _git_output(root: Path, args: Sequence[str], *, text: bool) -> str | bytes:
    result = subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=text)
    return cast(str | bytes, result.stdout)


def inspect_address_book_source(
    manifest: Mapping[str, object], source_root: str | Path
) -> list[dict[str, object]]:
    """Re-read every frozen address file from the exact official git object tree."""

    root = Path(source_root)
    source = cast(Mapping[str, object], manifest["source_identity"])
    commit = cast(str, source["commit"])
    observed_commit = cast(str, _git_output(root, ["rev-parse", "HEAD"], text=True)).strip()
    if observed_commit != commit:
        raise ValueError("address-book source HEAD differs from the frozen commit")
    files = cast(Sequence[Mapping[str, object]], source["files"])
    inventory: list[dict[str, object]] = []
    for item in files:
        path = cast(str, item["path"])
        object_spec = f"{commit}:{path}"
        blob = cast(str, _git_output(root, ["rev-parse", object_spec], text=True)).strip()
        data = cast(bytes, _git_output(root, ["cat-file", "blob", object_spec], text=False))
        observed_sha256 = hashlib.sha256(data).hexdigest()
        if blob != item["git_blob"] or observed_sha256 != item["sha256"]:
            raise ValueError(f"address-book source identity mismatch: {path}")
        inventory.append(
            {
                "deployment": item["deployment"],
                "path": path,
                "git_blob": blob,
                "sha256": observed_sha256,
                "byte_count": len(data),
            }
        )
    return inventory


def collect_program_directory(
    manifest: Mapping[str, object],
    *,
    root: str | Path,
    address_book_source: str | Path,
    rpc: RpcCollector | None = None,
) -> tuple[dict[str, object], dict[str, object], list[dict[str, object]]]:
    """Collect the complete frozen B0 directory without opening transactions or outcomes."""

    errors = validate_program_manifest(manifest)
    errors.extend(validate_parent_artifacts(manifest, root))
    if errors:
        raise ValueError("invalid B0 manifest: " + "; ".join(sorted(set(errors))))
    source_inventory = inspect_address_book_source(manifest, address_book_source)
    if rpc is None:
        rpc = _rpc_from_manifest(manifest)
    rpc_config = cast(Mapping[str, object], manifest["rpc"])
    cutoff_config = cast(Mapping[str, object], manifest["cutoff"])
    cutoff_timestamp = cast(int, cutoff_config["timestamp_unix"])
    deployment_values = cast(Sequence[Mapping[str, object]], manifest["deployments"])
    network_deployments = [item for item in deployment_values if item["network_access_in_b0"] is True]
    deployment_summaries: list[dict[str, object]] = []
    deployment_directories: list[dict[str, object]] = []
    normalized_log_count = 0
    program_count = 0
    for deployment in network_deployments:
        remaining = cast(int, rpc_config["maximum_normalized_logs"]) - normalized_log_count
        deployment_summary, deployment_directory = collect_deployment_directory(
            rpc,
            deployment,
            cutoff_timestamp=cutoff_timestamp,
            rpc_config=rpc_config,
            remaining_log_budget=remaining,
        )
        deployment_summaries.append(deployment_summary)
        deployment_directories.append(deployment_directory)
        provider_count = cast(
            int,
            cast(Mapping[str, object], deployment_summary["provider_directory"])["normalized_log_count"],
        )
        configurator_count = cast(
            int,
            cast(Mapping[str, object], deployment_summary["configurator_directory"])["normalized_log_count"],
        )
        deployment_program_count = cast(
            int,
            cast(Mapping[str, object], deployment_summary["program_directory"])["program_count"],
        )
        normalized_log_count += provider_count + configurator_count
        program_count += deployment_program_count
        if normalized_log_count > cast(int, rpc_config["maximum_normalized_logs"]):
            raise RuntimeError("maximum normalized-log cap exceeded")
        if program_count > cast(int, rpc_config["maximum_programs"]):
            raise RuntimeError("maximum program cap exceeded")
    programs = [
        program
        for directory in deployment_directories
        for program in cast(Sequence[Mapping[str, object]], directory["programs"])
    ]
    support, support_passes = summarize_support(
        programs, cast(Mapping[str, object], manifest["support_thresholds"])
    )
    access = cast(Mapping[str, object], manifest["access_boundary"])
    access_ok = all(access[key] is True for key in TRUE_ACCESS_KEYS) and all(
        access[key] is False for key in FALSE_ACCESS_KEYS
    )
    checks = [cast(Mapping[str, object], item["checks"]) for item in deployment_summaries]
    gates = {
        "parent_hashes_and_decisions": True,
        "frozen_official_address_sources": len(source_inventory) == len(EXPECTED_SOURCE_FILES),
        "exact_deployment_universe_and_split": len(network_deployments) == 9,
        "replicated_chain_identities": all(item["chain_identity_replicated"] is True for item in checks),
        "deterministic_replicated_cutoff_headers": all(
            item["cutoff_headers_replicated"] is True for item in checks
        ),
        "complete_provider_log_directories": all(
            item["provider_directory_complete"] is True for item in checks
        ),
        "complete_configurator_surface_derivation": all(
            item["configurator_surface_complete"] is True for item in checks
        ),
        "complete_bounded_configurator_log_directories": all(
            item["configurator_directories_complete"] is True for item in checks
        ),
        "strict_log_normalization": True,
        "no_duplicate_or_conflicting_logs": all(
            item["no_duplicate_or_conflicting_logs"] is True for item in checks
        ),
        "source_corrected_configurator_upgrade_histories": all(
            item["source_corrected_upgrade_history"] is True for item in checks
        ),
        "exact_program_grouping_and_block_headers": all(
            item["program_headers_complete"] is True for item in checks
        )
        and len(programs) == len({cast(str, item["program_id"]) for item in programs}),
        "minimum_train_support": support_passes["train"],
        "minimum_validation_support": support_passes["validation"],
        "minimum_test_support": support_passes["test"],
        "minimum_total_support": support_passes["total"],
        "request_byte_log_and_program_caps": rpc.http_attempts
        <= cast(int, rpc_config["maximum_http_attempts"])
        and rpc.response_bytes <= cast(int, rpc_config["maximum_response_bytes"])
        and normalized_log_count <= cast(int, rpc_config["maximum_normalized_logs"])
        and len(programs) <= cast(int, rpc_config["maximum_programs"]),
        "zero_account_and_response_access_boundary": access_ok,
    }
    policy = cast(Mapping[str, object], manifest["decision_policy"])
    passed = set(gates) == REQUIRED_GATES and all(gates.values())
    method_counts = dict(sorted(Counter(cast(str, item["method"]) for item in rpc.records).items()))
    summary = {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "audit_id": manifest["audit_id"],
        "as_of": manifest["as_of"],
        "parents": manifest["parents"],
        "source_identity": {
            "repository": cast(Mapping[str, object], manifest["source_identity"])["repository"],
            "commit": cast(Mapping[str, object], manifest["source_identity"])["commit"],
            "file_inventory": source_inventory,
        },
        "selection_contract": manifest["selection_contract"],
        "cutoff_contract": manifest["cutoff"],
        "development_context": {
            "deployment": "ethereum",
            "network_access_in_b0": False,
            "development_bundle_count": 77,
            "included_in_support_thresholds": False,
        },
        "deployment_summaries": deployment_summaries,
        "support": support,
        "request_summary": {
            "successful_request_count": len(rpc.records),
            "failed_logical_request_count": len(rpc.failed_calls),
            "http_attempt_count": rpc.http_attempts,
            "response_byte_count": rpc.response_bytes,
            "method_counts": method_counts,
            "all_one_attempt": all(item["attempt_count"] == 1 for item in rpc.records),
        },
        "inventory": {
            "network_deployment_count": len(network_deployments),
            "normalized_log_count": normalized_log_count,
            "program_count": len(programs),
            "unique_program_identity_count": len({cast(str, item["program_id"]) for item in programs}),
        },
        "access_boundary": manifest["access_boundary"],
        "gates": gates,
        "gate_counts": {"pass": sum(gates.values()), "fail": sum(not value for value in gates.values())},
        "decision": policy["pass"] if passed else policy["fail"],
        "authorized_next_stage": policy["authorized_next_stage"] if passed else None,
        "limitations": manifest["limitations"],
    }
    directory = {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "audit_id": manifest["audit_id"],
        "cutoff_contract": manifest["cutoff"],
        "program_inclusion_rule": manifest["program_inclusion_rule"],
        "deployment_directories": deployment_directories,
    }
    return summary, directory, rpc.records


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--address-book-source", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--response-hashes", type=Path, required=True)
    parser.add_argument("--failure", type=Path, required=True)
    parser.add_argument("--collection-commit")
    return parser


def main() -> None:
    """Run B0 once from an exact clean protocol worktree."""

    args = _build_parser().parse_args()
    outputs = (args.summary, args.directory, args.response_hashes, args.failure)
    for output in outputs:
        if output.exists():
            raise FileExistsError(f"refusing to overwrite {output}")
    root = Path.cwd()
    current_commit = cast(str, _git_output(root, ["rev-parse", "HEAD"], text=True)).strip()
    status = cast(str, _git_output(root, ["status", "--porcelain"], text=True)).strip()
    if status:
        raise RuntimeError("collection worktree must be clean")
    if args.collection_commit is not None and args.collection_commit != current_commit:
        raise ValueError("collection commit must equal the clean worktree HEAD")
    manifest = load_program_manifest(args.manifest)
    manifest_sha256 = sha256_file(args.manifest)
    rpc: RpcCollector | None = None
    try:
        errors = validate_program_manifest(manifest)
        errors.extend(validate_parent_artifacts(manifest, root))
        if errors:
            raise ValueError("invalid B0 manifest: " + "; ".join(sorted(set(errors))))
        rpc = _rpc_from_manifest(manifest)
        summary, directory, requests_ledger = collect_program_directory(
            manifest,
            root=root,
            address_book_source=args.address_book_source,
            rpc=rpc,
        )
    except Exception as exc:
        completed_requests = [] if rpc is None else rpc.records
        failed_calls = [] if rpc is None else rpc.failed_calls
        failure = {
            "schema_version": ARTIFACT_SCHEMA_VERSION,
            "audit_id": manifest.get("audit_id"),
            "collection_commit": current_commit,
            "manifest_sha256": manifest_sha256,
            "failure_type": type(exc).__name__,
            "failure_message": str(exc),
            "completed_successful_request_count": len(completed_requests),
            "failed_logical_request_count": len(failed_calls),
            "http_attempt_count": 0 if rpc is None else rpc.http_attempts,
            "response_byte_count": 0 if rpc is None else rpc.response_bytes,
            "failed_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        }
        _write_json(args.failure, failure)
        _write_json(
            args.response_hashes,
            {
                "schema_version": ARTIFACT_SCHEMA_VERSION,
                "audit_id": manifest.get("audit_id"),
                "collection_commit": current_commit,
                "manifest_sha256": manifest_sha256,
                "requests": completed_requests,
                "failed_calls": failed_calls,
            },
        )
        raise
    summary["collection_commit"] = current_commit
    summary["manifest_sha256"] = manifest_sha256
    directory["collection_commit"] = current_commit
    directory["manifest_sha256"] = manifest_sha256
    response_artifact = {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "audit_id": manifest["audit_id"],
        "collection_commit": current_commit,
        "manifest_sha256": manifest_sha256,
        "requests": requests_ledger,
        "failed_calls": rpc.failed_calls,
    }
    _write_json(args.summary, summary)
    _write_json(args.directory, directory)
    _write_json(args.response_hashes, response_artifact)
    print(
        json.dumps(
            {
                "decision": summary["decision"],
                "gate_counts": summary["gate_counts"],
                "program_count": cast(Mapping[str, object], summary["inventory"])["program_count"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
