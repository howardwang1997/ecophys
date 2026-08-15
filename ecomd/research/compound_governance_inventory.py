"""Governance-log-only inventory for Compound III mainnet Comet markets."""

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

from ecomd.research.compound_v3_chain_metadata import canonical_json_sha256

SCHEMA_VERSION = "ecophys-compound-v3-governance-log-inventory/v1"
ARTIFACT_SCHEMA_VERSION = "ecophys-compound-v3-governance-log-audit/v1"
STAGE = "governance_configuration_logs_only"
AUDIT_ID = "compound_v3_mainnet_governance_log_inventory_v1"
AS_OF = "2026-08-16"
CONFIGURATOR = "0x316f9708bb98af7da9c68c1c3b5e79039cd336e3"
FROZEN_PARENTS = {
    "exposure_design_path": "data/manifests/compound_v3_exposure_control_design_v1.yaml",
    "exposure_design_sha256": "ec329243f9fd071405112f4598b3f7e982d56683beec742e15b920c667e4b85e",
    "chain_summary_path": "experiments/v14_compound_v3_chain_metadata_preflight/artifacts_v2/summary.json",
    "chain_summary_sha256": "14f5b044d8c51e4323419b901a7f037c84c4af45083464e0daaefc561256c944",
    "source_commit": "f766f51583c23acc33b2a7824654ef2029a96804",
}
FROZEN_MARKETS = (
    ("mainnet_usdc", "0xc3d688b66703497daa19211eedff47f25384cdc3"),
    ("mainnet_usds", "0x5d409e56d886231adaf00c8775665ad0f9897b56"),
    ("mainnet_usdt", "0x3afdc9bca9213a35503b077a6072f3d0d5ab0840"),
    ("mainnet_wbtc", "0xe85dc543813b8c2cfeaac371517b925a166a9293"),
    ("mainnet_weth", "0xa17581a9e3356d9a858b789d68b4d866e593ae94"),
    ("mainnet_wsteth", "0x3d0bb1ccab520a66e607822fc55bc921738fafe3"),
)
FROZEN_DECISION_POLICY = {
    "all_gates_required": True,
    "pass": "PASS_GOVERNANCE_LOG_INVENTORY_AUTHORIZE_RECEIPT_PAYLOAD_PREFLIGHT_ONLY",
    "fail": "FAIL_GOVERNANCE_LOG_INVENTORY_KEEP_ACCOUNT_AND_RESPONSE_ROWS_LOCKED",
    "authorized_next_stage": "separately_frozen_candidate_receipt_payload_and_finality_preflight",
}
EVENT_CONTRACT: dict[str, dict[str, object]] = {
    "update_asset_borrow_collateral_factor": {
        "signature": "UpdateAssetBorrowCollateralFactor(address,address,uint64,uint64)",
        "topic0": "0x14bba7d3df0797b2f5143e4f2087f29fcd3ee3ec3197d38a7f77f85dc0d0ec63",
        "value_bits": 64,
    },
    "update_asset_liquidate_collateral_factor": {
        "signature": "UpdateAssetLiquidateCollateralFactor(address,address,uint64,uint64)",
        "topic0": "0xbdfea73f1d581ded04f608d47cd124146963b03795e30c9f9e16d57bb1fed652",
        "value_bits": 64,
    },
    "update_asset_supply_cap": {
        "signature": "UpdateAssetSupplyCap(address,address,uint128,uint128)",
        "topic0": "0x561b42b6b7ded5005c55634f0a6bd24d306cb04b04533bab7e1a644b67245486",
        "value_bits": 128,
    },
    "comet_deployed": {
        "signature": "CometDeployed(address,address)",
        "topic0": "0x3da528dfe78562a1f409134989443b5f21ee92023a64b90dedeb2002415189b6",
    },
    "upgraded": {
        "signature": "Upgraded(address)",
        "topic0": "0xbc7cd75a20ee27fd9adebab32041f755214dbc6bffa90cc0225b39da2e5c2d3b",
    },
}
ELIGIBLE_EVENT_TYPES = frozenset(
    {
        "update_asset_borrow_collateral_factor",
        "update_asset_liquidate_collateral_factor",
        "update_asset_supply_cap",
    }
)
ALLOWED_METHODS = frozenset({"eth_chainId", "eth_getBlockByNumber", "eth_getLogs"})
REQUIRED_GATES = frozenset(
    {
        "parent_hashes",
        "ethereum_chain_id",
        "fixed_window_headers",
        "exact_root_partition_plan",
        "complete_unsaturated_partitions",
        "strict_log_decoding",
        "no_duplicate_or_conflicting_logs",
        "at_least_one_provisional_atomic_candidate",
        "request_and_byte_caps",
        "governance_only_access_boundary",
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
        "window",
        "configurator",
        "markets",
        "events",
        "partition_rule",
        "candidate_rule",
        "gates",
        "decision_policy",
        "limitations",
    }
)
PARENT_KEYS = frozenset(
    {
        "exposure_design_path",
        "exposure_design_sha256",
        "chain_summary_path",
        "chain_summary_sha256",
        "source_commit",
    }
)
ACCESS_KEYS = frozenset(
    {
        "chain_rpc_used",
        "governance_log_rows_opened",
        "governance_payload_rows_opened",
        "governance_transaction_or_receipt_rows_opened",
        "governance_call_trace_rows_opened",
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
SOURCE_KEYS = frozenset(
    {
        "blockscout_rpc_url",
        "blockscout_documentation_url",
        "blockscout_terms_url",
        "publicnode_rpc_url",
        "publicnode_documentation_url",
        "maximum_requests_per_second_across_sources",
        "maximum_transport_retries",
        "maximum_http_attempts",
        "maximum_response_bytes",
        "log_response_limit",
        "maximum_normalized_logs",
        "root_partition_block_count",
        "raw_response_payloads_retained",
        "allowed_methods",
        "endpoint_substitution_after_freeze",
        "user_agent",
    }
)
WINDOW_KEYS = frozenset(
    {
        "from_block",
        "to_block",
        "to_block_hash",
        "expected_root_interval_count_per_address",
        "expected_log_address_count",
        "expected_root_log_query_count",
    }
)
PARTITION_KEYS = frozenset(
    {
        "root_intervals_are_inclusive_disjoint_and_complete",
        "exactly_limit_response_is_saturated",
        "saturated_interval_action",
        "saturated_single_block_action",
        "discard_saturated_parent_logs",
    }
)
CANDIDATE_KEYS = frozenset(
    {
        "require_one_eligible_configurator_log_in_transaction",
        "require_one_comet_deployed_log_for_same_proxy_in_transaction",
        "require_one_upgraded_log_for_same_proxy_and_implementation_in_transaction",
        "require_no_other_configurator_state_change_log_in_transaction",
        "require_no_other_frozen_market_upgrade_in_transaction",
        "require_old_value_differs_from_new_value",
        "existing_collateral_conformance_deferred",
        "receipt_payload_spillover_audit_deferred",
    }
)
ADDRESS_PATTERN = re.compile(r"^0x[0-9a-fA-F]{40}$")
HASH_PATTERN = re.compile(r"^0x[0-9a-fA-F]{64}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def load_governance_inventory(path: str | Path) -> dict[str, object]:
    """Load a frozen governance-log inventory manifest."""

    value: object = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("governance inventory root must be a mapping")
    return cast(dict[str, object], value)


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


def normalize_address(value: object, *, path: str) -> str:
    """Return one normalized EVM address."""

    if not isinstance(value, str) or ADDRESS_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{path} must be a 20-byte hexadecimal address")
    return value.lower()


def normalize_hash(value: object, *, path: str) -> str:
    """Return one normalized 32-byte hash."""

    if not isinstance(value, str) or HASH_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{path} must be a 32-byte hexadecimal hash")
    return value.lower()


def decode_quantity(value: object, *, path: str) -> int:
    """Decode a canonical nonnegative JSON-RPC quantity."""

    if not isinstance(value, str) or re.fullmatch(r"0x(?:0|[1-9a-fA-F][0-9a-fA-F]*)", value) is None:
        raise ValueError(f"{path} must be a canonical JSON-RPC quantity")
    return int(value, 16)


def split_inclusive_interval(from_block: int, to_block: int) -> tuple[tuple[int, int], tuple[int, int]]:
    """Bisect one non-singleton inclusive interval without overlap or gaps."""

    if from_block >= to_block:
        raise ValueError("cannot split a singleton or reversed interval")
    midpoint = (from_block + to_block) // 2
    return (from_block, midpoint), (midpoint + 1, to_block)


def root_intervals(from_block: int, to_block: int, block_count: int) -> tuple[tuple[int, int], ...]:
    """Return fixed-width inclusive root partitions."""

    if from_block < 0 or to_block < from_block or block_count <= 0:
        raise ValueError("invalid root-partition arguments")
    return tuple(
        (start, min(start + block_count - 1, to_block))
        for start in range(from_block, to_block + 1, block_count)
    )


def _safe_relative_path(value: object) -> bool:
    return (
        isinstance(value, str)
        and bool(value)
        and not Path(value).is_absolute()
        and ".." not in Path(value).parts
    )


def validate_governance_inventory(manifest: Mapping[str, object]) -> list[str]:
    """Return structural, access-boundary and frozen-value violations."""

    errors: list[str] = []
    if set(manifest) != TOP_LEVEL_KEYS:
        errors.append(f"top level must contain exactly {sorted(TOP_LEVEL_KEYS)}")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must equal {SCHEMA_VERSION}")
    if manifest.get("stage") != STAGE:
        errors.append(f"stage must equal {STAGE}")
    audit_id = manifest.get("audit_id")
    if not isinstance(audit_id, str) or ID_PATTERN.fullmatch(audit_id) is None:
        errors.append("audit_id must be a stable lowercase identifier")
    elif audit_id != AUDIT_ID:
        errors.append(f"audit_id must equal {AUDIT_ID}")
    as_of = manifest.get("as_of")
    if not isinstance(as_of, str) or DATE_PATTERN.fullmatch(as_of) is None:
        errors.append("as_of must be an ISO date")
    elif as_of != AS_OF:
        errors.append(f"as_of must equal {AS_OF}")

    parents = _mapping(manifest.get("parents"))
    if parents is None or set(parents) != PARENT_KEYS:
        errors.append(f"parents must contain exactly {sorted(PARENT_KEYS)}")
        parents = {}
    for key in ("exposure_design_path", "chain_summary_path"):
        if not _safe_relative_path(parents.get(key)):
            errors.append(f"parents.{key} must be a safe relative path")
    for key in ("exposure_design_sha256", "chain_summary_sha256"):
        value = parents.get(key)
        if not isinstance(value, str) or SHA256_PATTERN.fullmatch(value) is None:
            errors.append(f"parents.{key} must be a lowercase SHA-256")
    source_commit = parents.get("source_commit")
    if not isinstance(source_commit, str) or GIT_SHA_PATTERN.fullmatch(source_commit) is None:
        errors.append("parents.source_commit must be a full lowercase Git SHA")
    if parents and dict(parents) != FROZEN_PARENTS:
        errors.append("parents differ from the frozen artifact contract")

    access = _mapping(manifest.get("access_boundary"))
    if access is None or set(access) != ACCESS_KEYS:
        errors.append(f"access_boundary must contain exactly {sorted(ACCESS_KEYS)}")
        access = {}
    for key in ("chain_rpc_used", "governance_log_rows_opened"):
        if access.get(key) is not True:
            errors.append(f"access_boundary.{key} must be true")
    for key in ACCESS_KEYS - {"chain_rpc_used", "governance_log_rows_opened"}:
        if access.get(key) is not False:
            errors.append(f"access_boundary.{key} must be false")

    sources = _mapping(manifest.get("sources"))
    if sources is None or set(sources) != SOURCE_KEYS:
        errors.append(f"sources must contain exactly {sorted(SOURCE_KEYS)}")
        sources = {}
    expected_sources: dict[str, object] = {
        "blockscout_rpc_url": "https://eth.blockscout.com/api/eth-rpc",
        "blockscout_documentation_url": "https://docs.blockscout.com/devs/apis/rpc/eth-rpc",
        "blockscout_terms_url": "https://eaas.blockscout.com/terms-and-conditions",
        "publicnode_rpc_url": "https://ethereum-rpc.publicnode.com",
        "publicnode_documentation_url": "https://ethereum.publicnode.dev/",
        "maximum_requests_per_second_across_sources": 2,
        "maximum_transport_retries": 2,
        "maximum_http_attempts": 2000,
        "maximum_response_bytes": 268_435_456,
        "log_response_limit": 1000,
        "maximum_normalized_logs": 100_000,
        "root_partition_block_count": 250_000,
        "raw_response_payloads_retained": False,
        "endpoint_substitution_after_freeze": False,
        "user_agent": "EcoPhys-V14-Compound-governance-log-inventory/1.0",
    }
    for key, expected in expected_sources.items():
        if sources.get(key) != expected:
            errors.append(f"sources.{key} must equal the frozen value")
    if _strings(sources.get("allowed_methods")) != (
        "eth_chainId",
        "eth_getBlockByNumber",
        "eth_getLogs",
    ):
        errors.append("sources.allowed_methods must equal the frozen ordered method list")

    window = _mapping(manifest.get("window"))
    if window is None or set(window) != WINDOW_KEYS:
        errors.append(f"window must contain exactly {sorted(WINDOW_KEYS)}")
        window = {}
    expected_window: dict[str, object] = {
        "from_block": 14_000_000,
        "to_block": 25_760_572,
        "to_block_hash": "0xd2bb500d88a2c0fa956e04af3e6df36f8e60c4cd82307bcf71180cde466a4ca4",
        "expected_root_interval_count_per_address": 48,
        "expected_log_address_count": 7,
        "expected_root_log_query_count": 336,
    }
    for key, expected in expected_window.items():
        if window.get(key) != expected:
            errors.append(f"window.{key} must equal the frozen value")
    intervals = root_intervals(14_000_000, 25_760_572, 250_000)
    if len(intervals) != 48 or intervals[0] != (14_000_000, 14_249_999):
        errors.append("window root interval arithmetic changed")
    if intervals[-1] != (25_750_000, 25_760_572):
        errors.append("window final root interval changed")

    configurator = _mapping(manifest.get("configurator"))
    if configurator is None or set(configurator) != {"proxy"}:
        errors.append("configurator must contain exactly proxy")
        configurator = {}
    try:
        if normalize_address(configurator.get("proxy"), path="configurator.proxy") != CONFIGURATOR:
            errors.append("configurator.proxy differs from the frozen proxy")
    except ValueError as exc:
        errors.append(str(exc))

    markets = _mapping_list(manifest.get("markets"))
    if markets is None or len(markets) != 6:
        errors.append("markets must contain exactly six mappings")
        markets = []
    market_ids: set[str] = set()
    proxies: set[str] = set()
    normalized_markets: list[tuple[str, str]] = []
    for index, market in enumerate(markets):
        if set(market) != {"market_id", "proxy"}:
            errors.append(f"markets[{index}] must contain exactly market_id and proxy")
        market_id = market.get("market_id")
        if (
            not isinstance(market_id, str)
            or ID_PATTERN.fullmatch(market_id) is None
            or market_id in market_ids
        ):
            errors.append(f"markets[{index}].market_id must be unique and stable")
        else:
            market_ids.add(market_id)
        try:
            proxy = normalize_address(market.get("proxy"), path=f"markets[{index}].proxy")
            if proxy in proxies:
                errors.append(f"markets[{index}].proxy must be unique")
            proxies.add(proxy)
            if isinstance(market_id, str):
                normalized_markets.append((market_id, proxy))
        except ValueError as exc:
            errors.append(str(exc))
    if tuple(normalized_markets) != FROZEN_MARKETS:
        errors.append("markets differ from the frozen ordered market set")

    events = _mapping(manifest.get("events"))
    if events is None or set(events) != set(EVENT_CONTRACT):
        errors.append(f"events must contain exactly {sorted(EVENT_CONTRACT)}")
        events = {}
    for event_id, expected in EVENT_CONTRACT.items():
        event = _mapping(events.get(event_id))
        if event is None or dict(event) != expected:
            errors.append(f"events.{event_id} must equal the frozen source-derived contract")

    partition = _mapping(manifest.get("partition_rule"))
    if partition is None or set(partition) != PARTITION_KEYS:
        errors.append(f"partition_rule must contain exactly {sorted(PARTITION_KEYS)}")
        partition = {}
    expected_partition: dict[str, object] = {
        "root_intervals_are_inclusive_disjoint_and_complete": True,
        "exactly_limit_response_is_saturated": True,
        "saturated_interval_action": "recursively_bisect_inclusive_interval",
        "saturated_single_block_action": "fail",
        "discard_saturated_parent_logs": True,
    }
    if dict(partition) != expected_partition:
        errors.append("partition_rule differs from the frozen saturation contract")

    candidate = _mapping(manifest.get("candidate_rule"))
    if candidate is None or set(candidate) != CANDIDATE_KEYS:
        errors.append(f"candidate_rule must contain exactly {sorted(CANDIDATE_KEYS)}")
        candidate = {}
    if not candidate or any(value is not True for value in candidate.values()):
        errors.append("every candidate_rule flag must be true")

    gates = _strings(manifest.get("gates"))
    if gates is None or frozenset(gates) != REQUIRED_GATES or len(gates) != len(REQUIRED_GATES):
        errors.append(f"gates must contain exactly {sorted(REQUIRED_GATES)}")
    policy = _mapping(manifest.get("decision_policy"))
    if policy is None or set(policy) != {"all_gates_required", "pass", "fail", "authorized_next_stage"}:
        errors.append("decision_policy keys changed")
        policy = {}
    if dict(policy) != FROZEN_DECISION_POLICY:
        errors.append("decision_policy differs from the frozen contract")
    limitations = _strings(manifest.get("limitations"))
    if limitations is None or len(limitations) < 6:
        errors.append("limitations must contain at least six strings")
    return sorted(errors)


def validate_parent_artifacts(manifest: Mapping[str, object], root: str | Path) -> list[str]:
    """Verify the frozen design and chain parents without network access."""

    errors: list[str] = []
    parents = cast(Mapping[str, object], manifest["parents"])
    root_path = Path(root)
    for label, path_key, hash_key in (
        ("exposure design", "exposure_design_path", "exposure_design_sha256"),
        ("chain summary", "chain_summary_path", "chain_summary_sha256"),
    ):
        path = root_path / cast(str, parents[path_key])
        if not path.is_file():
            errors.append(f"{label} parent is missing")
            continue
        if hashlib.sha256(path.read_bytes()).hexdigest() != parents[hash_key]:
            errors.append(f"{label} parent hash differs from the frozen value")
    chain_path = root_path / cast(str, parents["chain_summary_path"])
    if chain_path.is_file():
        value: object = json.loads(chain_path.read_text(encoding="utf-8"))
        chain = _mapping(value)
        if (
            chain is None
            or chain.get("decision") != "PASS_CHAIN_METADATA_AUTHORIZE_EXPOSURE_PROTOCOL_DESIGN_ONLY"
        ):
            errors.append("chain parent decision is not the frozen pass")
    return sorted(errors)


def _hex_bytes(value: object, *, path: str) -> bytes:
    if not isinstance(value, str) or not value.startswith("0x"):
        raise ValueError(f"{path} must be 0x-prefixed hexadecimal bytes")
    body = value[2:]
    if len(body) % 2 or re.fullmatch(r"[0-9a-fA-F]*", body) is None:
        raise ValueError(f"{path} must contain complete hexadecimal bytes")
    return bytes.fromhex(body)


def _topic_address(value: object, *, path: str) -> str:
    word = _hex_bytes(value, path=path)
    if len(word) != 32 or any(word[:12]):
        raise ValueError(f"{path} must be a canonical indexed address")
    return "0x" + word[12:].hex()


def _data_words(value: object, *, count: int, path: str) -> tuple[int, ...]:
    data = _hex_bytes(value, path=path)
    if len(data) != count * 32:
        raise ValueError(f"{path} must contain exactly {count} ABI words")
    return tuple(int.from_bytes(data[index * 32 : (index + 1) * 32], "big") for index in range(count))


def normalize_governance_log(
    raw: Mapping[str, object],
    *,
    expected_address: str,
    market_id: str | None,
    from_block: int,
    to_block: int,
) -> dict[str, object]:
    """Normalize one permitted Configurator or proxy-upgrade log."""

    address = normalize_address(raw.get("address"), path="log.address")
    if address != normalize_address(expected_address, path="expected_address"):
        raise ValueError("log address differs from the requested address")
    topics_value = raw.get("topics")
    if not isinstance(topics_value, list) or not topics_value:
        raise ValueError("log.topics must be a nonempty list")
    topics = tuple(normalize_hash(topic, path="log.topic") for topic in topics_value)
    block_number = decode_quantity(raw.get("blockNumber"), path="log.blockNumber")
    if not from_block <= block_number <= to_block:
        raise ValueError("log block falls outside the requested interval")
    data = raw.get("data")
    data_bytes = _hex_bytes(data, path="log.data")
    removed = raw.get("removed")
    if removed not in (None, False):
        raise ValueError("removed governance log is forbidden")
    record: dict[str, object] = {
        "address": address,
        "market_id": market_id,
        "block_number": block_number,
        "block_hash": normalize_hash(raw.get("blockHash"), path="log.blockHash"),
        "transaction_hash": normalize_hash(raw.get("transactionHash"), path="log.transactionHash"),
        "transaction_index": decode_quantity(raw.get("transactionIndex"), path="log.transactionIndex"),
        "log_index": decode_quantity(raw.get("logIndex"), path="log.logIndex"),
        "topic0": topics[0],
        "topic_count": len(topics),
        "data_byte_count": len(data_bytes),
        "data_sha256": hashlib.sha256(data_bytes).hexdigest(),
    }
    topics_by_id = {cast(str, contract["topic0"]): event_id for event_id, contract in EVENT_CONTRACT.items()}
    event_type = topics_by_id.get(topics[0], "other_configurator")
    if market_id is not None:
        if event_type != "upgraded" or len(topics) != 2 or data_bytes:
            raise ValueError("proxy log must be one canonical Upgraded event")
        record.update(
            {"event_type": "upgraded", "implementation": _topic_address(topics[1], path="upgraded")}
        )
        return record
    if event_type in ELIGIBLE_EVENT_TYPES:
        if len(topics) != 3:
            raise ValueError("eligible Configurator event must contain proxy and asset topics")
        old_value, new_value = _data_words(data, count=2, path="eligible.data")
        value_bits = cast(int, EVENT_CONTRACT[event_type]["value_bits"])
        if old_value >= 2**value_bits or new_value >= 2**value_bits:
            raise ValueError("eligible Configurator value exceeds its declared ABI width")
        record.update(
            {
                "event_type": event_type,
                "comet_proxy": _topic_address(topics[1], path="eligible.comet_proxy"),
                "asset": _topic_address(topics[2], path="eligible.asset"),
                "old_value": old_value,
                "new_value": new_value,
            }
        )
    elif event_type == "comet_deployed":
        if len(topics) != 3 or data_bytes:
            raise ValueError("CometDeployed must contain two indexed addresses and empty data")
        record.update(
            {
                "event_type": event_type,
                "comet_proxy": _topic_address(topics[1], path="deployed.comet_proxy"),
                "implementation": _topic_address(topics[2], path="deployed.implementation"),
            }
        )
    else:
        record["event_type"] = "other_configurator"
    return record


def deduplicate_logs(records: Sequence[Mapping[str, object]]) -> tuple[list[dict[str, object]], int, int]:
    """Deduplicate by canonical log identity while reporting conflicts."""

    by_key: dict[tuple[object, object, object], dict[str, object]] = {}
    duplicate_count = 0
    conflict_count = 0
    for record in records:
        normalized = dict(record)
        key = (record["block_hash"], record["transaction_hash"], record["log_index"])
        previous = by_key.get(key)
        if previous is None:
            by_key[key] = normalized
        elif previous == normalized:
            duplicate_count += 1
        else:
            conflict_count += 1
    ordered = sorted(
        by_key.values(), key=lambda item: (cast(int, item["block_number"]), cast(int, item["log_index"]))
    )
    return ordered, duplicate_count, conflict_count


def provisional_candidates(records: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    """Evaluate the frozen same-transaction log-only candidate rule."""

    configurator_by_tx: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    upgrades_by_tx: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    for record in records:
        tx_hash = cast(str, record["transaction_hash"])
        if record["market_id"] is None:
            configurator_by_tx[tx_hash].append(record)
        else:
            upgrades_by_tx[tx_hash].append(record)
    candidates: list[dict[str, object]] = []
    for record in records:
        event_type = cast(str, record["event_type"])
        if event_type not in ELIGIBLE_EVENT_TYPES:
            continue
        tx_hash = cast(str, record["transaction_hash"])
        proxy = cast(str, record["comet_proxy"])
        config_logs = configurator_by_tx[tx_hash]
        eligible_logs = [item for item in config_logs if item["event_type"] in ELIGIBLE_EVENT_TYPES]
        deployments = [
            item
            for item in config_logs
            if item["event_type"] == "comet_deployed" and item.get("comet_proxy") == proxy
        ]
        upgrades = [item for item in upgrades_by_tx[tx_hash] if item["address"] == proxy]
        matching_upgrade = (
            len(deployments) == 1
            and len(upgrades) == 1
            and deployments[0].get("implementation") == upgrades[0].get("implementation")
        )
        allowed_config_logs = len(config_logs) == 2 and len(deployments) == 1
        checks = {
            "one_eligible_configurator_log": len(eligible_logs) == 1,
            "one_same_proxy_deployment": len(deployments) == 1,
            "one_same_proxy_matching_upgrade": matching_upgrade,
            "no_other_configurator_state_change": allowed_config_logs,
            "no_other_frozen_market_upgrade": len(upgrades_by_tx[tx_hash]) == 1,
            "old_value_differs_from_new_value": record["old_value"] != record["new_value"],
        }
        candidates.append(
            {
                "transaction_hash": tx_hash,
                "block_number": record["block_number"],
                "log_index": record["log_index"],
                "event_type": event_type,
                "comet_proxy": proxy,
                "asset": record["asset"],
                "old_value": record["old_value"],
                "new_value": record["new_value"],
                "implementation": deployments[0]["implementation"] if len(deployments) == 1 else None,
                "checks": checks,
                "provisional_atomic_candidate": all(checks.values()),
                "deferred_checks": [
                    "receipt_and_payload_spillover",
                    "existing_collateral_and_getters",
                    "consensus_finality",
                    "twenty_four_hour_contamination",
                ],
            }
        )
    return candidates


class RpcCollector:
    """Rate-limited multi-provider JSON-RPC client retaining hashes only."""

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

    def call(self, *, url: str, label: str, method: str, params: Sequence[object]) -> object:
        """Issue one permitted request within global rate and volume caps."""

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
                            "label": label,
                            "provider": "blockscout" if "blockscout" in url else "publicnode",
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


def _block_record(value: object, *, expected_number: int, path: str) -> dict[str, object]:
    block = _mapping(value)
    if block is None:
        raise ValueError(f"{path} must be a block mapping")
    number = decode_quantity(block.get("number"), path=f"{path}.number")
    if number != expected_number:
        raise ValueError(f"{path} number differs from the requested number")
    timestamp = decode_quantity(block.get("timestamp"), path=f"{path}.timestamp")
    return {
        "number": number,
        "hash": normalize_hash(block.get("hash"), path=f"{path}.hash"),
        "timestamp_unix": timestamp,
        "timestamp_utc": datetime.fromtimestamp(timestamp, UTC).isoformat().replace("+00:00", "Z"),
    }


def _collect_address_logs(
    rpc: RpcCollector,
    *,
    url: str,
    address: str,
    market_id: str | None,
    intervals: Sequence[tuple[int, int]],
    topic0: str | None,
    response_limit: int,
    maximum_normalized_logs: int,
) -> tuple[list[dict[str, object]], int, int]:
    accepted: list[dict[str, object]] = []
    query_count = 0
    saturated_count = 0

    def visit(interval_from: int, interval_to: int, *, root_index: int, depth: int) -> None:
        nonlocal query_count, saturated_count
        query_count += 1
        log_filter: dict[str, object] = {
            "fromBlock": hex(interval_from),
            "toBlock": hex(interval_to),
            "address": address,
        }
        if topic0 is not None:
            log_filter["topics"] = [topic0]
        result_value = rpc.call(
            url=url,
            label=f"logs:{market_id or 'configurator'}:{root_index}:{depth}:{interval_from}-{interval_to}",
            method="eth_getLogs",
            params=[log_filter],
        )
        if not isinstance(result_value, list):
            raise ValueError("eth_getLogs result must be a list")
        if len(result_value) > response_limit:
            raise RuntimeError("eth_getLogs response exceeded the documented limit")
        if len(result_value) == response_limit:
            saturated_count += 1
            if interval_from == interval_to:
                raise RuntimeError("single-block governance log response remains saturated")
            left, right = split_inclusive_interval(interval_from, interval_to)
            visit(*left, root_index=root_index, depth=depth + 1)
            visit(*right, root_index=root_index, depth=depth + 1)
            return
        for raw in result_value:
            mapped = _mapping(raw)
            if mapped is None:
                raise ValueError("eth_getLogs item must be a mapping")
            accepted.append(
                normalize_governance_log(
                    mapped,
                    expected_address=address,
                    market_id=market_id,
                    from_block=interval_from,
                    to_block=interval_to,
                )
            )
            if len(accepted) > maximum_normalized_logs:
                raise RuntimeError("maximum normalized-log cap exceeded")

    for index, interval in enumerate(intervals):
        visit(*interval, root_index=index, depth=0)
    return accepted, query_count, saturated_count


def collect_governance_inventory(
    manifest: Mapping[str, object],
    *,
    root: str | Path = ".",
) -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, object]]]:
    """Collect only the frozen Configurator and proxy-upgrade logs."""

    errors = validate_governance_inventory(manifest)
    errors.extend(validate_parent_artifacts(manifest, root))
    if errors:
        raise ValueError("invalid governance inventory: " + "; ".join(sorted(set(errors))))
    sources = cast(Mapping[str, object], manifest["sources"])
    window = cast(Mapping[str, object], manifest["window"])
    rpc = RpcCollector(
        user_agent=cast(str, sources["user_agent"]),
        maximum_requests_per_second=float(cast(float, sources["maximum_requests_per_second_across_sources"])),
        maximum_transport_retries=cast(int, sources["maximum_transport_retries"]),
        maximum_http_attempts=cast(int, sources["maximum_http_attempts"]),
        maximum_response_bytes=cast(int, sources["maximum_response_bytes"]),
    )
    publicnode_url = cast(str, sources["publicnode_rpc_url"])
    blockscout_url = cast(str, sources["blockscout_rpc_url"])
    chain_id = rpc.call(url=publicnode_url, label="chain_id", method="eth_chainId", params=[])
    from_block = cast(int, window["from_block"])
    to_block = cast(int, window["to_block"])
    start_header = _block_record(
        rpc.call(
            url=publicnode_url,
            label="window_start_header",
            method="eth_getBlockByNumber",
            params=[hex(from_block), False],
        ),
        expected_number=from_block,
        path="window_start_header",
    )
    end_header = _block_record(
        rpc.call(
            url=publicnode_url,
            label="window_end_header",
            method="eth_getBlockByNumber",
            params=[hex(to_block), False],
        ),
        expected_number=to_block,
        path="window_end_header",
    )
    intervals = root_intervals(
        from_block,
        to_block,
        cast(int, sources["root_partition_block_count"]),
    )
    maximum_logs = cast(int, sources["maximum_normalized_logs"])
    response_limit = cast(int, sources["log_response_limit"])
    all_records: list[dict[str, object]] = []
    query_counts: dict[str, int] = {}
    saturated_counts: dict[str, int] = {}
    configurator_logs, config_queries, config_saturated = _collect_address_logs(
        rpc,
        url=blockscout_url,
        address=CONFIGURATOR,
        market_id=None,
        intervals=intervals,
        topic0=None,
        response_limit=response_limit,
        maximum_normalized_logs=maximum_logs,
    )
    all_records.extend(configurator_logs)
    query_counts["configurator"] = config_queries
    saturated_counts["configurator"] = config_saturated
    upgrade_topic = cast(str, EVENT_CONTRACT["upgraded"]["topic0"])
    markets = cast(Sequence[Mapping[str, object]], manifest["markets"])
    for market in markets:
        market_id = cast(str, market["market_id"])
        proxy = normalize_address(market["proxy"], path=f"{market_id}.proxy")
        records, queries, saturated = _collect_address_logs(
            rpc,
            url=blockscout_url,
            address=proxy,
            market_id=market_id,
            intervals=intervals,
            topic0=upgrade_topic,
            response_limit=response_limit,
            maximum_normalized_logs=maximum_logs - len(all_records),
        )
        all_records.extend(records)
        query_counts[market_id] = queries
        saturated_counts[market_id] = saturated
    records, duplicate_count, conflict_count = deduplicate_logs(all_records)
    candidates = provisional_candidates(records)
    provisional_count = sum(cast(bool, item["provisional_atomic_candidate"]) for item in candidates)
    method_counts = dict(sorted(Counter(cast(str, item["method"]) for item in rpc.records).items()))
    root_query_count = len(intervals) * (1 + len(markets))
    access = cast(Mapping[str, object], manifest["access_boundary"])
    governance_only = (
        access.get("chain_rpc_used") is True
        and access.get("governance_log_rows_opened") is True
        and all(
            value is False
            for key, value in access.items()
            if key not in {"chain_rpc_used", "governance_log_rows_opened"}
        )
    )
    gates = {
        "parent_hashes": True,
        "ethereum_chain_id": chain_id == "0x1",
        "fixed_window_headers": start_header["number"] == from_block
        and end_header["number"] == to_block
        and end_header["hash"] == window["to_block_hash"]
        and cast(int, start_header["timestamp_unix"]) < cast(int, end_header["timestamp_unix"]),
        "exact_root_partition_plan": len(intervals) == window["expected_root_interval_count_per_address"]
        and 1 + len(markets) == window["expected_log_address_count"]
        and root_query_count == window["expected_root_log_query_count"]
        and sum(query_counts.values()) >= root_query_count,
        "complete_unsaturated_partitions": True,
        "strict_log_decoding": True,
        "no_duplicate_or_conflicting_logs": duplicate_count == 0 and conflict_count == 0,
        "at_least_one_provisional_atomic_candidate": provisional_count >= 1,
        "request_and_byte_caps": rpc.http_attempts <= cast(int, sources["maximum_http_attempts"])
        and rpc.response_bytes <= cast(int, sources["maximum_response_bytes"])
        and len(records) <= cast(int, sources["maximum_normalized_logs"]),
        "governance_only_access_boundary": governance_only,
    }
    required_gates = set(cast(Sequence[str], manifest["gates"]))
    policy = cast(Mapping[str, object], manifest["decision_policy"])
    passed = set(gates) == required_gates and all(gates.values())
    event_counts = dict(sorted(Counter(cast(str, item["event_type"]) for item in records).items()))
    market_upgrade_counts = dict(
        sorted(
            Counter(cast(str, item["market_id"]) for item in records if item["market_id"] is not None).items()
        )
    )
    summary = {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "audit_id": manifest["audit_id"],
        "as_of": manifest["as_of"],
        "parents": manifest["parents"],
        "window": {
            "from_block": start_header,
            "to_block": end_header,
            "root_interval_count_per_address": len(intervals),
            "log_address_count": 1 + len(markets),
            "root_log_query_count": root_query_count,
        },
        "inventory": {
            "normalized_log_count": len(records),
            "configurator_log_count": sum(item["market_id"] is None for item in records),
            "proxy_upgrade_log_count": sum(item["market_id"] is not None for item in records),
            "event_type_counts": event_counts,
            "market_upgrade_counts": market_upgrade_counts,
            "duplicate_count": duplicate_count,
            "conflict_count": conflict_count,
            "candidate_count": len(candidates),
            "provisional_atomic_candidate_count": provisional_count,
            "candidate_records": candidates,
        },
        "request_summary": {
            "successful_request_count": len(rpc.records),
            "http_attempt_count": rpc.http_attempts,
            "response_byte_count": rpc.response_bytes,
            "method_counts": method_counts,
            "address_query_counts": query_counts,
            "address_saturated_query_counts": saturated_counts,
            "all_one_attempt": all(item["attempt_count"] == 1 for item in rpc.records),
        },
        "access_boundary": manifest["access_boundary"],
        "gates": gates,
        "gate_counts": {"pass": sum(gates.values()), "fail": sum(not value for value in gates.values())},
        "decision": policy["pass"] if passed else policy["fail"],
        "authorized_next_stage": policy["authorized_next_stage"] if passed else None,
        "limitations": manifest["limitations"],
    }
    return summary, records, rpc.records


def _git_value(root: Path, args: Sequence[str]) -> str:
    result = subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--response-hashes", type=Path, required=True)
    parser.add_argument("--collection-commit")
    return parser


def main() -> None:
    """Run the frozen governance-log inventory from a clean exact worktree."""

    args = _build_parser().parse_args()
    for output in (args.summary, args.inventory, args.response_hashes):
        if output.exists():
            raise FileExistsError(f"refusing to overwrite {output}")
    root = Path.cwd()
    current_commit = _git_value(root, ["rev-parse", "HEAD"])
    if _git_value(root, ["status", "--porcelain"]):
        raise RuntimeError("collection worktree must be clean")
    if args.collection_commit is not None and args.collection_commit != current_commit:
        raise ValueError("collection commit must equal the clean worktree HEAD")
    manifest = load_governance_inventory(args.manifest)
    summary, inventory, responses = collect_governance_inventory(manifest, root=root)
    summary["collection_commit"] = current_commit
    summary["manifest_sha256"] = hashlib.sha256(args.manifest.read_bytes()).hexdigest()
    for output in (args.summary, args.inventory, args.response_hashes):
        output.parent.mkdir(parents=True, exist_ok=True)
    _write_json(args.inventory, inventory)
    _write_json(args.response_hashes, responses)
    _write_json(args.summary, summary)
    print(
        json.dumps(
            {
                "decision": summary["decision"],
                "requests": len(responses),
                "logs": len(inventory),
                "provisional_candidates": cast(Mapping[str, object], summary["inventory"])[
                    "provisional_atomic_candidate_count"
                ],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
