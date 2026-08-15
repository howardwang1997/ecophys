"""Outcome-locked preperiod support checks for the Uniswap v3 fee event."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import cast

import yaml

from ecomd.research.uniswap_v3_fee_treatment import (
    canonical_json_sha256,
    decode_quantity,
    normalize_address,
    normalize_hash,
)

SCHEMA_VERSION = "ecophys-uniswap-v3-preperiod-support/v1"
CENSUS_SCHEMA_VERSION = "ecophys-uniswap-v3-preperiod-exposure-census/v1"
FROZEN_STAGE = "frozen_before_sample_pool_preperiod_log_access"
SWAP_TOPIC = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"
MINT_TOPIC = "0x7a53080ba414158be7ec69b987b5fb7d07dee101fe85488f0853ae16239d0bde"
BURN_TOPIC = "0x0c396cd989a39f4459b5fa1aed6a9a8dcdbc45908acfd67e028cd568da98982c"
POOL_COLLECT_TOPIC = "0x70935338e69775456a85ddef226c395fb668b63fa0115f5f20610b388e6ca9c0"
INCREASE_TOPIC = "0x3067048beee31b25b2f1681f88dac838c8bba36af25bfb2b7cf7473a5847e35f"
DECREASE_TOPIC = "0x26f6a048ee9138f2c0ce266f322cb99228e8d619ae2bff30c67f8dcf9d2377b4"
NPM_COLLECT_TOPIC = "0x40d0efd1a53d60ecbf40971b9daf7dc90178c3aadc7aab1765632738fa8b8f01"
TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
POOL_EVENT_TOPICS = {
    "swap": SWAP_TOPIC,
    "mint": MINT_TOPIC,
    "burn": BURN_TOPIC,
    "collect": POOL_COLLECT_TOPIC,
}
POOL_ACTION_BY_TOPIC = {
    MINT_TOPIC: "mint",
    BURN_TOPIC: "burn",
    POOL_COLLECT_TOPIC: "collect",
}
NPM_ACTION_BY_TOPIC = {
    INCREASE_TOPIC: "mint",
    DECREASE_TOPIC: "burn",
    NPM_COLLECT_TOPIC: "collect",
}
ZERO_ADDRESS = "0x" + "0" * 40


def load_contract(path: Path) -> dict[str, object]:
    """Load one frozen U1a contract."""

    payload: object = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("preperiod support contract root must be a mapping")
    return cast(dict[str, object], payload)


def contract_sha256(path: Path) -> str:
    """Hash exact contract bytes."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def _mapping(value: object, *, path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{path} must be a mapping")
    return cast(Mapping[str, object], value)


def _sequence(value: object, *, path: str) -> Sequence[object]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ValueError(f"{path} must be a sequence")
    return cast(Sequence[object], value)


def _integer(value: object, *, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{path} must be an integer")
    return value


def _normalized_topics(value: object, *, path: str, allow_empty: bool = False) -> tuple[str, ...]:
    raw_topics = list(_sequence(value, path=path))
    while raw_topics and raw_topics[-1] is None:
        raw_topics.pop()
    if any(topic is None for topic in raw_topics):
        raise ValueError(f"{path} contains a non-trailing null topic")
    topics = tuple(normalize_hash(topic, path=path) for topic in raw_topics)
    if not topics and not allow_empty:
        raise ValueError(f"{path} cannot be empty")
    return topics


def _topics(value: object, *, path: str) -> tuple[str, ...]:
    return _normalized_topics(value, path=path)


def _topic_address(topic: object, *, path: str) -> str:
    normalized = normalize_hash(topic, path=path)
    if normalized[2:26] != "0" * 24:
        raise ValueError(f"{path} is not a canonical indexed address")
    return "0x" + normalized[-40:]


def _topic_uint(topic: object, *, path: str) -> int:
    return int(normalize_hash(topic, path=path), 16)


def hash_file(path: Path) -> str:
    """Return SHA-256 for a local provenance input."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict[str, object]]:
    """Load a strict JSON-lines file."""

    rows: list[dict[str, object]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        payload: object = json.loads(line)
        if not isinstance(payload, dict):
            raise ValueError(f"JSONL row {line_number} must be a mapping")
        rows.append(cast(dict[str, object], payload))
    return rows


def select_hash_stratified_pools(
    treatment_rows: Sequence[Mapping[str, object]],
    *,
    salt: str,
    allowed_fee_values: Sequence[int],
    pools_per_fee_value: int,
) -> list[dict[str, object]]:
    """Select an outcome-blind, fee-stratified pool subset from the U0 ledger."""

    if not salt or pools_per_fee_value <= 0:
        raise ValueError("selection salt and pools_per_fee_value must be positive")
    selected: list[dict[str, object]] = []
    for fee_value in allowed_fee_values:
        candidates: list[tuple[str, str]] = []
        for row in treatment_rows:
            if row.get("packed_fee_value") != fee_value:
                continue
            pool = normalize_address(row.get("pool_address"), path="treatment.pool_address")
            score = hashlib.sha256(f"{salt}|{pool}".encode()).hexdigest()
            candidates.append((score, pool))
        candidates.sort()
        if len(candidates) < pools_per_fee_value:
            raise ValueError(f"fee value {fee_value} has too few treatment pools")
        selected.extend(
            {
                "pool_address": pool,
                "packed_fee_value": fee_value,
                "selection_sha256": score,
            }
            for score, pool in candidates[:pools_per_fee_value]
        )
    return selected


def validate_frozen_contract(
    contract: Mapping[str, object],
    treatment_rows: Sequence[Mapping[str, object]],
    *,
    treatment_ledger_sha256: str,
) -> tuple[str, ...]:
    """Validate U1a scope, deterministic sample and all outcome locks."""

    errors: list[str] = []
    if contract.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if contract.get("stage") != FROZEN_STAGE:
        errors.append(f"stage must be {FROZEN_STAGE}")
    if contract.get("result") is not None:
        errors.append("result must be null before sampled-pool preperiod access")
    try:
        parent = _mapping(contract.get("parent"), path="parent")
        selection = _mapping(contract.get("selection"), path="selection")
        window = _mapping(contract.get("window"), path="window")
        contracts = _mapping(contract.get("contracts"), path="contracts")
        events = _mapping(contract.get("events"), path="events")
        identity = _mapping(contract.get("identity_sample"), path="identity_sample")
        sources = _mapping(contract.get("sources"), path="sources")
        preflight = _mapping(contract.get("transport_preflight"), path="transport_preflight")
        gates = _mapping(contract.get("gates"), path="gates")
        access = _mapping(contract.get("access_boundary"), path="access_boundary")
    except ValueError as error:
        errors.append(str(error))
        return tuple(errors)

    if parent.get("treatment_ledger_sha256") != treatment_ledger_sha256:
        errors.append("parent treatment ledger SHA-256 differs from local U0 input")
    if parent.get("treatment_row_count") != len(treatment_rows) or len(treatment_rows) != 1000:
        errors.append("parent treatment ledger must contain exactly 1,000 rows")
    if {row.get("transition") for row in treatment_rows} != {"activated_from_zero"}:
        errors.append("all parent rows must remain activated_from_zero")

    try:
        raw_fee_values = _sequence(selection.get("allowed_packed_fee_values"), path="allowed fees")
        allowed_fees = [_integer(value, path="allowed fee") for value in raw_fee_values]
        per_fee = _integer(selection.get("pools_per_fee_value"), path="pools_per_fee_value")
        expected_sample = select_hash_stratified_pools(
            treatment_rows,
            salt=cast(str, selection.get("salt")),
            allowed_fee_values=allowed_fees,
            pools_per_fee_value=per_fee,
        )
        manifest_sample = [
            dict(_mapping(row, path="selection.pools"))
            for row in _sequence(selection.get("pools"), path="selection.pools")
        ]
        if expected_sample != manifest_sample:
            errors.append("selection.pools differs from the deterministic U0-ledger sample")
        if selection.get("sample_rows_sha256") != canonical_json_sha256(expected_sample):
            errors.append("selection.sample_rows_sha256 differs from the deterministic sample")
        if selection.get("total_pools") != len(expected_sample) or len(expected_sample) != 16:
            errors.append("selection must retain exactly 16 pools")
    except (TypeError, ValueError) as error:
        errors.append(str(error))

    from_block = window.get("from_block")
    to_block = window.get("to_block")
    treatment_block = window.get("treatment_block_excluded")
    if (from_block, to_block, treatment_block) != (24548777, 24599176, 24599177):
        errors.append("window must remain the 50,400 blocks immediately before treatment")
    if window.get("inclusive_block_count") != 50400:
        errors.append("window.inclusive_block_count must remain 50,400")

    try:
        npm = normalize_address(
            contracts.get("nonfungible_position_manager"), path="nonfungible_position_manager"
        )
        if npm != "0xc36442b4a4522e871399cd717abdd847ab11fe88":
            errors.append("NonfungiblePositionManager address changed")
    except ValueError as error:
        errors.append(str(error))

    expected_pool_topics = {
        "swap": SWAP_TOPIC,
        "mint": MINT_TOPIC,
        "burn": BURN_TOPIC,
        "collect": POOL_COLLECT_TOPIC,
    }
    try:
        pool_events = _mapping(events.get("pool"), path="events.pool")
        npm_events = _mapping(events.get("position_manager"), path="events.position_manager")
        for name, topic in expected_pool_topics.items():
            spec = _mapping(pool_events.get(name), path=f"events.pool.{name}")
            if spec.get("topic0") != topic:
                errors.append(f"events.pool.{name}.topic0 changed")
        expected_npm_topics = {
            "mint": INCREASE_TOPIC,
            "burn": DECREASE_TOPIC,
            "collect": NPM_COLLECT_TOPIC,
            "transfer": TRANSFER_TOPIC,
        }
        for name, topic in expected_npm_topics.items():
            spec = _mapping(npm_events.get(name), path=f"events.position_manager.{name}")
            if spec.get("topic0") != topic:
                errors.append(f"events.position_manager.{name}.topic0 changed")
    except ValueError as error:
        errors.append(str(error))

    if identity.get("maximum_transactions") != 64 or identity.get("minimum_eligible_transactions") != 32:
        errors.append("identity transaction sample must remain capped at 64 with minimum 32")
    if sources.get("log_response_limit") != 1000 or sources.get("maximum_http_attempts") != 2000:
        errors.append("source response/request ceilings changed")
    if sources.get("maximum_response_bytes") != 134217728:
        errors.append("source byte ceiling changed")
    if sources.get("maximum_normalized_pool_events") != 250000:
        errors.append("source normalized-event ceiling changed")
    if preflight.get("sampled_pool_preperiod_logs_accessed") is not False:
        errors.append("transport preflight must not access sampled-pool preperiod logs")
    if preflight.get("preflight_used_only_already_consumed_u0_mechanism_transactions") is not True:
        errors.append("transport preflight scope changed")
    expected_preflight_hashes = {
        "adapter_log_query_sha256": "f813fa5f8910a1165f5f0a0371a010ef01732633f570d1977c33e2c05541fad9",
        "governance_transaction_log_sha256": (
            "d1dc9acd18968b569c80a664cb2595c02da937cc7a602903eae56cdc8684f2ef"
        ),
        "empty_adapter_log_query_sha256": (
            "1531ed0377c1e4056d99e9eccb0f7f2e65e72763593de740e3c1103cae3d691d"
        ),
    }
    for key, hash_value in expected_preflight_hashes.items():
        if preflight.get(key) != hash_value:
            errors.append(f"transport_preflight.{key} changed")

    required_true = (
        "exact_sample_membership",
        "exact_pre_treatment_window",
        "complete_unsaturated_log_partitions",
    )
    for key in required_true:
        if gates.get(key) is not True:
            errors.append(f"gates.{key} must remain true")
    expected_thresholds = {
        "duplicate_or_conflicting_log_count_max": 0,
        "minimum_swap_active_pools": 8,
        "minimum_position_active_pools": 8,
        "minimum_position_action_logs": 64,
        "minimum_npm_position_action_share": 0.50,
        "minimum_eligible_npm_action_transactions": 32,
        "minimum_exact_pool_to_token_pair_rate": 0.80,
        "minimum_owner_after_transaction_resolution_rate": 0.95,
    }
    for key, threshold_value in expected_thresholds.items():
        if gates.get(key) != threshold_value:
            errors.append(f"gates.{key} changed")
    required_false = (
        "swap_amount_or_price_fields_decoded",
        "liquidity_or_token_amount_fields_decoded",
        "post_treatment_pool_events_opened",
        "post_treatment_responses_opened",
        "control_pool_behavior_opened",
        "outcome_model_training_authorized",
        "transaction_calldata_decoded",
    )
    for key in required_false:
        if access.get(key) is not False:
            errors.append(f"access_boundary.{key} must remain false")
    if access.get("gpu_hours_authorized") != 0 or access.get("paid_data_authorized") is not False:
        errors.append("GPU and paid-data access must remain unauthorized")
    return tuple(errors)


def split_inclusive_interval(from_block: int, to_block: int) -> tuple[tuple[int, int], tuple[int, int]]:
    """Bisect a saturated inclusive block interval without overlap or gaps."""

    if from_block >= to_block:
        raise ValueError("cannot split a single-block or reversed interval")
    midpoint = (from_block + to_block) // 2
    return (from_block, midpoint), (midpoint + 1, to_block)


def normalize_legacy_log(
    raw: Mapping[str, object],
    *,
    event_type: str,
    expected_address: str,
    expected_topic0: str,
    from_block: int,
    to_block: int,
) -> dict[str, object]:
    """Normalize one Blockscout legacy log without decoding amount/price data."""

    address = normalize_address(raw.get("address"), path="legacy.address")
    if address != normalize_address(expected_address, path="expected_address"):
        raise ValueError("legacy log address differs from requested address")
    topics = _topics(raw.get("topics"), path="legacy.topics")
    if topics[0] != normalize_hash(expected_topic0, path="expected_topic0"):
        raise ValueError("legacy log topic0 differs from requested event")
    block_number = decode_quantity(raw.get("blockNumber"), path="legacy.blockNumber")
    if not from_block <= block_number <= to_block:
        raise ValueError("legacy log falls outside requested block interval")
    transaction_index = decode_quantity(raw.get("transactionIndex"), path="legacy.transactionIndex")
    log_index = decode_quantity(raw.get("logIndex"), path="legacy.logIndex")
    transaction_hash = normalize_hash(raw.get("transactionHash"), path="legacy.transactionHash")
    data = raw.get("data")
    if not isinstance(data, str) or not data.startswith("0x"):
        raise ValueError("legacy log data must be 0x-prefixed")
    manager_owner: str | None = None
    if event_type in {"mint", "burn", "collect"}:
        if len(topics) < 2:
            raise ValueError("position-action pool log is missing owner topic")
        manager_owner = _topic_address(topics[1], path="pool.manager_owner")
    return {
        "pool_address": address,
        "event_type": event_type,
        "block_number": block_number,
        "transaction_index": transaction_index,
        "log_index": log_index,
        "transaction_hash": transaction_hash,
        "manager_owner": manager_owner,
        "topics": list(topics),
        "data_sha256": hashlib.sha256(data.encode()).hexdigest(),
    }


def _v2_log_address(raw: Mapping[str, object]) -> str:
    address_value = raw.get("address")
    if isinstance(address_value, str):
        return normalize_address(address_value, path="transaction_log.address")
    address = _mapping(address_value, path="transaction_log.address")
    return normalize_address(address.get("hash"), path="transaction_log.address.hash")


def normalize_transaction_log(raw: Mapping[str, object], *, expected_tx_hash: str) -> dict[str, object]:
    """Normalize one Blockscout v2 transaction log for event pairing."""

    tx_hash = normalize_hash(raw.get("transaction_hash"), path="transaction_log.transaction_hash")
    if tx_hash != normalize_hash(expected_tx_hash, path="expected_tx_hash"):
        raise ValueError("transaction log belongs to another transaction")
    block_number = _integer(raw.get("block_number"), path="transaction_log.block_number")
    log_index = _integer(raw.get("index"), path="transaction_log.index")
    topics = _normalized_topics(raw.get("topics"), path="transaction_log.topics", allow_empty=True)
    return {
        "address": _v2_log_address(raw),
        "block_number": block_number,
        "log_index": log_index,
        "transaction_hash": tx_hash,
        "topics": list(topics),
    }


def deduplicate_pool_events(
    events: Sequence[Mapping[str, object]],
) -> tuple[list[dict[str, object]], int, int]:
    """Deduplicate exact log identities while counting conflicting duplicates."""

    by_key: dict[tuple[str, str, int], dict[str, object]] = {}
    duplicate_count = 0
    conflict_count = 0
    for event in events:
        normalized = dict(event)
        key = (
            normalize_address(event.get("pool_address"), path="event.pool_address"),
            normalize_hash(event.get("transaction_hash"), path="event.transaction_hash"),
            _integer(event.get("log_index"), path="event.log_index"),
        )
        prior = by_key.get(key)
        if prior is None:
            by_key[key] = normalized
        elif prior == normalized:
            duplicate_count += 1
        else:
            conflict_count += 1
    ordered = sorted(
        by_key.values(),
        key=lambda row: (
            cast(int, row["block_number"]),
            cast(int, row["transaction_index"]),
            cast(int, row["log_index"]),
            cast(str, row["pool_address"]),
        ),
    )
    return ordered, duplicate_count, conflict_count


def build_pool_support_rows(
    sample_rows: Sequence[Mapping[str, object]],
    events: Sequence[Mapping[str, object]],
    *,
    npm_address: str,
) -> list[dict[str, object]]:
    """Aggregate preperiod activity and manager-layer coverage by sampled pool."""

    npm = normalize_address(npm_address, path="npm_address")
    by_pool: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    for event in events:
        by_pool[normalize_address(event.get("pool_address"), path="event.pool_address")].append(event)
    output: list[dict[str, object]] = []
    for sample in sample_rows:
        pool = normalize_address(sample.get("pool_address"), path="sample.pool_address")
        pool_events = by_pool.get(pool, [])
        counts = Counter(str(event.get("event_type")) for event in pool_events)
        position_events = [
            event for event in pool_events if event.get("event_type") in {"mint", "burn", "collect"}
        ]
        owners = Counter(str(event.get("manager_owner")) for event in position_events)
        npm_count = owners[npm]
        output.append(
            {
                "pool_address": pool,
                "packed_fee_value": _integer(sample.get("packed_fee_value"), path="sample.packed_fee_value"),
                "swap_count": counts["swap"],
                "mint_count": counts["mint"],
                "burn_count": counts["burn"],
                "collect_count": counts["collect"],
                "position_action_count": len(position_events),
                "npm_position_action_count": npm_count,
                "npm_position_action_share": (npm_count / len(position_events) if position_events else None),
                "distinct_manager_owner_count": len(owners),
                "manager_owner_counts": dict(sorted(owners.items())),
                "pool_event_identity_sha256": canonical_json_sha256(
                    [
                        {
                            "event_type": event.get("event_type"),
                            "block_number": event.get("block_number"),
                            "transaction_index": event.get("transaction_index"),
                            "log_index": event.get("log_index"),
                            "transaction_hash": event.get("transaction_hash"),
                            "data_sha256": event.get("data_sha256"),
                        }
                        for event in pool_events
                    ]
                ),
            }
        )
    return output


def select_identity_transactions(
    pool_events: Sequence[Mapping[str, object]],
    *,
    npm_address: str,
    salt: str,
    maximum_transactions: int,
) -> tuple[list[str], int]:
    """Hash-sample unique NPM-managed preperiod action transactions."""

    npm = normalize_address(npm_address, path="npm_address")
    eligible = {
        normalize_hash(event.get("transaction_hash"), path="event.transaction_hash")
        for event in pool_events
        if event.get("event_type") in {"mint", "burn", "collect"} and event.get("manager_owner") == npm
    }
    ranked = sorted(
        (hashlib.sha256(f"{salt}|{tx_hash}".encode()).hexdigest(), tx_hash) for tx_hash in eligible
    )
    return [tx_hash for _, tx_hash in ranked[:maximum_transactions]], len(eligible)


def pair_sampled_pool_actions(
    transaction_logs: Sequence[Mapping[str, object]],
    sampled_events: Sequence[Mapping[str, object]],
    *,
    npm_address: str,
) -> dict[tuple[str, int], dict[str, object]]:
    """Pair sampled pool actions to following NPM token-ID events within one transaction."""

    npm = normalize_address(npm_address, path="npm_address")
    ordered = sorted(transaction_logs, key=lambda log: _integer(log.get("log_index"), path="log_index"))
    pending: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    paired: dict[tuple[str, int], int] = {}
    seen_full_pool_keys: set[tuple[str, int]] = set()
    for log in ordered:
        topics = _normalized_topics(log.get("topics"), path="transaction_log.topics", allow_empty=True)
        if not topics:
            continue
        address = normalize_address(log.get("address"), path="transaction_log.address")
        log_index = _integer(log.get("log_index"), path="transaction_log.log_index")
        pool_action = POOL_ACTION_BY_TOPIC.get(topics[0])
        if pool_action is not None and len(topics) >= 2:
            owner = _topic_address(topics[1], path="transaction_log.pool_owner")
            if owner == npm:
                pending[pool_action].append(log)
                seen_full_pool_keys.add((address, log_index))
            continue
        npm_action = NPM_ACTION_BY_TOPIC.get(topics[0])
        if address != npm or npm_action is None:
            continue
        candidates = pending[npm_action]
        if not candidates:
            continue
        pool_log = candidates.pop()
        pool_key = (
            normalize_address(pool_log.get("address"), path="paired.pool_address"),
            _integer(pool_log.get("log_index"), path="paired.pool_log_index"),
        )
        if len(topics) < 2:
            raise ValueError("NPM action event is missing indexed token ID")
        paired[pool_key] = _topic_uint(topics[1], path="npm.token_id")

    results: dict[tuple[str, int], dict[str, object]] = {}
    for event in sampled_events:
        pool = normalize_address(event.get("pool_address"), path="sampled_event.pool_address")
        log_index = _integer(event.get("log_index"), path="sampled_event.log_index")
        key = (pool, log_index)
        if key not in seen_full_pool_keys:
            results[key] = {"pair_status": "sample_pool_event_missing_from_transaction_logs"}
        elif key not in paired:
            results[key] = {"pair_status": "no_matching_npm_token_event"}
        else:
            results[key] = {"pair_status": "exact", "token_id": paired[key]}
    return results


def resolve_transfer_owners(
    transfer_events: Sequence[Mapping[str, object]],
    *,
    token_id: int,
    action_block: int,
    action_transaction_index: int,
    action_log_index: int,
) -> dict[str, object]:
    """Resolve NFT owner immediately before the pool action and after its transaction."""

    decoded: list[tuple[tuple[int, int, int], str]] = []
    for event in transfer_events:
        topics = _topics(event.get("topics"), path="transfer.topics")
        if len(topics) != 4 or topics[0] != TRANSFER_TOPIC:
            raise ValueError("token transfer history contains a non-ERC721 Transfer event")
        if _topic_uint(topics[3], path="transfer.token_id") != token_id:
            raise ValueError("token transfer history contains another token ID")
        position = (
            _integer(event.get("block_number"), path="transfer.block_number"),
            _integer(event.get("transaction_index"), path="transfer.transaction_index"),
            _integer(event.get("log_index"), path="transfer.log_index"),
        )
        decoded.append((position, _topic_address(topics[2], path="transfer.to")))
    decoded.sort()
    action_position = (action_block, action_transaction_index, action_log_index)
    transaction_end = (action_block, action_transaction_index, 2**63 - 1)
    before = [owner for position, owner in decoded if position < action_position]
    after = [owner for position, owner in decoded if position <= transaction_end]
    owner_before = before[-1] if before and before[-1] != ZERO_ADDRESS else None
    owner_after = after[-1] if after and after[-1] != ZERO_ADDRESS else None
    return {
        "owner_before_action": owner_before,
        "owner_after_transaction": owner_after,
        "transfer_event_count_through_action_block": len(decoded),
    }


def summarize_preperiod_support(
    pool_support_rows: Sequence[Mapping[str, object]],
    identity_rows: Sequence[Mapping[str, object]],
    *,
    expected_pool_count: int,
    eligible_identity_transaction_count: int,
    selected_identity_transaction_count: int,
    maximum_identity_transactions: int,
    duplicate_log_count: int,
    conflicting_log_count: int,
    complete_unsaturated_partitions: bool,
    minimum_swap_active_pools: int,
    minimum_position_active_pools: int,
    minimum_position_action_logs: int,
    minimum_npm_position_action_share: float,
    minimum_eligible_npm_action_transactions: int,
    minimum_exact_pool_to_token_pair_rate: float,
    minimum_owner_after_transaction_resolution_rate: float,
) -> dict[str, object]:
    """Apply the frozen U1a support and identity feasibility gates."""

    swap_active = sum(int(cast(int, row.get("swap_count"))) > 0 for row in pool_support_rows)
    position_active = sum(int(cast(int, row.get("position_action_count"))) > 0 for row in pool_support_rows)
    position_actions = sum(int(cast(int, row.get("position_action_count"))) for row in pool_support_rows)
    npm_actions = sum(int(cast(int, row.get("npm_position_action_count"))) for row in pool_support_rows)
    npm_share = npm_actions / position_actions if position_actions else 0.0
    exact_pairs = sum(row.get("pair_status") == "exact" for row in identity_rows)
    pair_rate = exact_pairs / len(identity_rows) if identity_rows else 0.0
    owner_resolved = sum(
        row.get("pair_status") == "exact" and row.get("owner_after_transaction") is not None
        for row in identity_rows
    )
    owner_rate = owner_resolved / exact_pairs if exact_pairs else 0.0
    gates = {
        "exact_sample_pool_count": len(pool_support_rows) == expected_pool_count,
        "complete_unsaturated_log_partitions": complete_unsaturated_partitions,
        "no_duplicate_or_conflicting_logs": duplicate_log_count == 0 and conflicting_log_count == 0,
        "minimum_swap_active_pools": swap_active >= minimum_swap_active_pools,
        "minimum_position_active_pools": position_active >= minimum_position_active_pools,
        "minimum_position_action_logs": position_actions >= minimum_position_action_logs,
        "minimum_npm_position_action_share": npm_share >= minimum_npm_position_action_share,
        "minimum_eligible_npm_action_transactions": (
            eligible_identity_transaction_count >= minimum_eligible_npm_action_transactions
        ),
        "exact_identity_transaction_sample_size": selected_identity_transaction_count
        == min(maximum_identity_transactions, eligible_identity_transaction_count),
        "minimum_exact_pool_to_token_pair_rate": pair_rate >= minimum_exact_pool_to_token_pair_rate,
        "minimum_owner_after_transaction_resolution_rate": (
            owner_rate >= minimum_owner_after_transaction_resolution_rate
        ),
    }
    passed = all(gates.values())
    return {
        "schema_version": "ecophys-uniswap-v3-preperiod-support-result/v1",
        "decision": (
            "PASS_PREPERIOD_SUPPORT_IDENTITY_FEASIBILITY_FREEZE_U1B_DESIGN"
            if passed
            else "FAIL_PREPERIOD_SUPPORT_OR_IDENTITY_FEASIBILITY_NO_RESPONSE_ACCESS"
        ),
        "pass": passed,
        "pool_count": len(pool_support_rows),
        "swap_active_pool_count": swap_active,
        "position_active_pool_count": position_active,
        "position_action_log_count": position_actions,
        "npm_position_action_log_count": npm_actions,
        "npm_position_action_share": npm_share,
        "eligible_identity_transaction_count": eligible_identity_transaction_count,
        "selected_identity_transaction_count": selected_identity_transaction_count,
        "identity_action_row_count": len(identity_rows),
        "exact_pool_to_token_pair_count": exact_pairs,
        "exact_pool_to_token_pair_rate": pair_rate,
        "owner_after_transaction_resolved_count": owner_resolved,
        "owner_after_transaction_resolution_rate": owner_rate,
        "duplicate_log_count": duplicate_log_count,
        "conflicting_log_count": conflicting_log_count,
        "control_source_status": "UNRESOLVED_NOT_PART_OF_U1A",
        "gates": gates,
    }


def census_population_rows(
    treatment_rows: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Project the exact U0 ledger into the frozen exposure-census population."""

    return [
        {
            "pool_address": normalize_address(row.get("pool_address"), path="treatment.pool_address"),
            "packed_fee_value": _integer(row.get("packed_fee_value"), path="treatment.packed_fee_value"),
            "treatment_transaction_hash": normalize_hash(
                row.get("transaction_hash"), path="treatment.transaction_hash"
            ),
            "calldata_index": _integer(row.get("calldata_index"), path="treatment.calldata_index"),
        }
        for row in treatment_rows
    ]


def validate_exposure_census_contract(
    contract: Mapping[str, object],
    treatment_rows: Sequence[Mapping[str, object]],
    *,
    treatment_ledger_sha256: str,
    u1a_summary_sha256: str,
) -> tuple[str, ...]:
    """Validate the full-population route reset and its response locks."""

    errors: list[str] = []
    if contract.get("schema_version") != CENSUS_SCHEMA_VERSION:
        errors.append(f"schema_version must be {CENSUS_SCHEMA_VERSION}")
    if contract.get("stage") != "frozen_before_full_population_preperiod_log_access":
        errors.append("census stage changed")
    if contract.get("result") is not None:
        errors.append("census result must be null before full-population access")
    try:
        parents = _mapping(contract.get("parents"), path="parents")
        population = _mapping(contract.get("population"), path="population")
        window = _mapping(contract.get("window"), path="window")
        events = _mapping(contract.get("events"), path="events")
        sources = _mapping(contract.get("sources"), path="sources")
        preflight = _mapping(contract.get("transport_preflight"), path="transport_preflight")
        gates = _mapping(contract.get("gates"), path="gates")
        access = _mapping(contract.get("access_boundary"), path="access_boundary")
    except ValueError as error:
        errors.append(str(error))
        return tuple(errors)

    if parents.get("u0_treatment_ledger_sha256") != treatment_ledger_sha256:
        errors.append("census U0 ledger hash differs from local parent")
    if parents.get("u1a_summary_sha256") != u1a_summary_sha256:
        errors.append("census U1a summary hash differs from local parent")
    if parents.get("u1a_decision") != "FAIL_PREPERIOD_SUPPORT_OR_IDENTITY_FEASIBILITY_NO_RESPONSE_ACCESS":
        errors.append("census U1a parent decision changed")
    if parents.get("thresholds_informed_by_u1a_pilot") is not True:
        errors.append("census must disclose pilot-informed thresholds")
    if parents.get("development_not_pristine_confirmation") is not True:
        errors.append("census must remain development, not pristine confirmation")

    try:
        rows = census_population_rows(treatment_rows)
        if len(rows) != 1000 or len({row["pool_address"] for row in rows}) != 1000:
            errors.append("census parent must contain exactly 1,000 unique pools")
        if population.get("population_rows_sha256") != canonical_json_sha256(rows):
            errors.append("population_rows_sha256 differs from exact U0 population")
        if population.get("pool_count") != 1000 or population.get("unique_pool_count") != 1000:
            errors.append("population count must remain exactly 1,000")
        fee_counts = Counter(int(cast(int, row["packed_fee_value"])) for row in rows)
        if fee_counts != Counter({68: 107, 102: 893}):
            errors.append("census population fee counts changed")
        if population.get("packed_fee_value_counts") != {"68": 107, "102": 893}:
            errors.append("population.packed_fee_value_counts changed")
        if {row.get("transition") for row in treatment_rows} != {"activated_from_zero"}:
            errors.append("census parent transition class changed")
    except ValueError as error:
        errors.append(str(error))

    if (
        window.get("from_block"),
        window.get("to_block"),
        window.get("treatment_block_excluded"),
    ) != (24548777, 24599176, 24599177):
        errors.append("census window must remain the exact U1a preperiod")
    if window.get("inclusive_block_count") != 50400:
        errors.append("census window length changed")
    if window.get("treatment_timestamp_utc") != "2026-03-06T15:01:11Z":
        errors.append("census treatment timestamp changed")
    expected_topics = {
        "swap": SWAP_TOPIC,
        "mint": MINT_TOPIC,
        "burn": BURN_TOPIC,
        "collect": POOL_COLLECT_TOPIC,
    }
    for event_name, topic in expected_topics.items():
        if events.get(event_name) != topic:
            errors.append(f"events.{event_name} changed")
    if events.get("position_manager_owner_topic_index") != 1:
        errors.append("position manager owner topic index changed")
    try:
        if (
            normalize_address(events.get("nonfungible_position_manager"), path="events.npm")
            != "0xc36442b4a4522e871399cd717abdd847ab11fe88"
        ):
            errors.append("NonfungiblePositionManager address changed")
    except ValueError as error:
        errors.append(str(error))
    if list(_sequence(events.get("topic0_or_order"), path="events.topic0_or_order")) != [
        "swap",
        "mint",
        "burn",
        "collect",
    ]:
        errors.append("topic0 OR order changed")

    expected_source_limits: dict[str, object] = {
        "blockscout_eth_rpc_url": "https://eth.blockscout.com/api/eth-rpc",
        "publicnode_rpc_url": "https://ethereum-rpc.publicnode.com",
        "maximum_requests_per_second_across_sources": 2.0,
        "maximum_transport_retries": 2,
        "log_response_limit": 1000,
        "maximum_http_attempts": 5000,
        "maximum_response_bytes": 536870912,
        "maximum_normalized_events": 1000000,
        "raw_response_payloads_retained": False,
        "saturated_response_rule": ("recursively_bisect_inclusive_block_interval_until_below_limit"),
        "user_agent": "EcoPhys-uniswap-U1R-exposure-census/1.0",
    }
    for key, expected_value in expected_source_limits.items():
        if sources.get(key) != expected_value:
            errors.append(f"sources.{key} changed")
    expected_preflight: dict[str, object] = {
        "single_address_topic_query_sha256": (
            "fb17b4f618a95738ac6f86da86cdf3180f2f82a2ec521aa63e4c81e6c0e0a5d6"
        ),
        "address_array_supported": False,
        "address_array_response_sha256": ("7b321448e48353551f8709c054bd75f911dec664bd53a4dbf391a1303cc2ca4a"),
        "topic0_or_supported": True,
        "topic0_or_response_sha256": ("92afa3ef96c1a3fafb467d1b5305992540aa2886710aa1d3c95f8d92c4735306"),
        "full_window_empty_adapter_query_supported": True,
        "full_window_empty_adapter_query_count": 0,
        "full_window_empty_adapter_query_request_sha256": (
            "fd8c7639e72e019232606f143f93739221ca1493ac6f645c17f54d76adf6cd39"
        ),
        "full_window_empty_adapter_query_response_sha256": (
            "1d407881e1579aec62be88c0d44de3bd55bd15007b937e53903e60223785c886"
        ),
    }
    for key, expected_value in expected_preflight.items():
        if preflight.get(key) != expected_value:
            errors.append(f"transport_preflight.{key} changed")
    if preflight.get("used_only_already_consumed_u0_mechanism_data") is not True:
        errors.append("census transport preflight scope changed")
    if preflight.get("sampled_or_remaining_pool_preperiod_opened_by_preflight") is not False:
        errors.append("census transport preflight accessed forbidden pool preperiod")
    expected_wide_attempts = [
        {
            "from_block": 24548713,
            "to_block": 24599176,
            "request_sha256": "25f4f48a248bc83d84a243f1905bc40b3762623d65500f3393d0cc0285743ea5",
            "response_count": 0,
            "response_sha256": "1d407881e1579aec62be88c0d44de3bd55bd15007b937e53903e60223785c886",
            "note": "disclosed_initial_lower_bound_hex_transcription_error_adapter_only",
        },
        {
            "from_block": 24548777,
            "to_block": 24599176,
            "request_sha256": "fd8c7639e72e019232606f143f93739221ca1493ac6f645c17f54d76adf6cd39",
            "response_count": 0,
            "response_sha256": "1d407881e1579aec62be88c0d44de3bd55bd15007b937e53903e60223785c886",
            "note": "exact_frozen_window_adapter_only",
        },
    ]
    if list(_sequence(preflight.get("wide_interval_probe_attempts"), path="wide attempts")) != (
        expected_wide_attempts
    ):
        errors.append("transport_preflight.wide_interval_probe_attempts changed")

    expected_gates: dict[str, object] = {
        "exact_population_membership": True,
        "exact_pre_treatment_window": True,
        "complete_unsaturated_partitions": True,
        "duplicate_or_conflicting_log_count_max": 0,
        "minimum_swap_active_pools": 50,
        "minimum_position_active_pools": 20,
        "minimum_position_action_logs": 200,
        "minimum_swap_active_pools_per_fee_value": 5,
        "minimum_position_active_pools_per_fee_value": 2,
        "minimum_npm_position_action_share": 0.50,
        "maximum_single_pool_swap_count_share": 0.25,
        "maximum_single_pool_position_action_count_share": 0.50,
    }
    for key, expected_value in expected_gates.items():
        if gates.get(key) != expected_value:
            errors.append(f"gates.{key} changed")
    required_false = (
        "swap_amount_or_price_fields_decoded",
        "liquidity_or_token_amount_fields_decoded",
        "transaction_sender_or_calldata_opened",
        "non_npm_manager_addresses_retained",
        "token_id_or_transfer_history_opened",
        "control_pool_behavior_opened",
        "post_treatment_pool_events_opened",
        "post_treatment_responses_opened",
        "outcome_model_training_authorized",
    )
    for key in required_false:
        if access.get(key) is not False:
            errors.append(f"access_boundary.{key} must remain false")
    if access.get("full_u0_population_preperiod_pool_events_opened") is not True:
        errors.append("full U0 population preperiod access disclosure changed")
    if list(_sequence(access.get("event_types_opened"), path="access event types")) != [
        "swap",
        "mint",
        "burn",
        "collect",
    ]:
        errors.append("access_boundary.event_types_opened changed")
    if access.get("indexed_pool_participant_fields_transferred_but_discarded") is not True:
        errors.append("indexed pool participant fields must be disclosed as transferred and discarded")
    if access.get("gpu_hours_authorized") != 0 or access.get("paid_data_authorized") is not False:
        errors.append("census GPU and paid-data access must remain unauthorized")
    return tuple(errors)


def normalize_rpc_pool_log(
    raw: Mapping[str, object],
    *,
    expected_pool: str,
    allowed_topics: Mapping[str, str],
    from_block: int,
    to_block: int,
) -> dict[str, object]:
    """Normalize one standard JSON-RPC pool log without decoding numerical event data."""

    pool = normalize_address(raw.get("address"), path="rpc_log.address")
    if pool != normalize_address(expected_pool, path="expected_pool"):
        raise ValueError("RPC log address differs from requested pool")
    topics = _topics(raw.get("topics"), path="rpc_log.topics")
    topic_to_event = {normalize_hash(topic): name for name, topic in allowed_topics.items()}
    event_type = topic_to_event.get(topics[0])
    if event_type is None:
        raise ValueError("RPC log topic0 is outside the frozen event set")
    block_number = decode_quantity(raw.get("blockNumber"), path="rpc_log.blockNumber")
    if not from_block <= block_number <= to_block:
        raise ValueError("RPC log falls outside its requested interval")
    if raw.get("removed") is not False:
        raise ValueError("RPC log must be finalized and not removed")
    data = raw.get("data")
    if not isinstance(data, str) or not data.startswith("0x"):
        raise ValueError("RPC log data must be 0x-prefixed")
    manager_owner: str | None = None
    if event_type in {"mint", "burn", "collect"}:
        if len(topics) < 2:
            raise ValueError("position action is missing its manager-owner topic")
        manager_owner = _topic_address(topics[1], path="rpc_log.manager_owner")
    return {
        "pool_address": pool,
        "event_type": event_type,
        "block_number": block_number,
        "block_hash": normalize_hash(raw.get("blockHash"), path="rpc_log.blockHash"),
        "transaction_index": decode_quantity(raw.get("transactionIndex"), path="rpc_log.transactionIndex"),
        "log_index": decode_quantity(raw.get("logIndex"), path="rpc_log.logIndex"),
        "transaction_hash": normalize_hash(raw.get("transactionHash"), path="rpc_log.transactionHash"),
        "manager_owner": manager_owner,
        "data_sha256": hashlib.sha256(data.encode()).hexdigest(),
    }


def build_exposure_census_row(
    population_row: Mapping[str, object],
    events: Sequence[Mapping[str, object]],
    *,
    npm_address: str,
) -> dict[str, object]:
    """Aggregate one pool's preperiod economic-exposure evidence."""

    pool = normalize_address(population_row.get("pool_address"), path="population.pool_address")
    if any(event.get("pool_address") != pool for event in events):
        raise ValueError("census row received an event from another pool")
    counts = Counter(str(event.get("event_type")) for event in events)
    position_events = [event for event in events if event.get("event_type") in {"mint", "burn", "collect"}]
    owners = Counter(str(event.get("manager_owner")) for event in position_events)
    npm = normalize_address(npm_address, path="npm_address")
    position_count = len(position_events)
    return {
        **dict(population_row),
        "swap_count": counts["swap"],
        "mint_count": counts["mint"],
        "burn_count": counts["burn"],
        "collect_count": counts["collect"],
        "position_action_count": position_count,
        "swap_active": counts["swap"] > 0,
        "position_active": position_count > 0,
        "economically_exposed_preperiod": counts["swap"] > 0 or position_count > 0,
        "npm_position_action_count": owners[npm],
        "npm_position_action_share": owners[npm] / position_count if position_count else None,
        "distinct_manager_owner_count": len(owners),
        "pool_event_identity_sha256": canonical_json_sha256(events),
    }


def summarize_exposure_census(
    census_rows: Sequence[Mapping[str, object]],
    *,
    duplicate_log_count: int,
    conflicting_log_count: int,
    complete_unsaturated_partitions: bool,
    minimum_swap_active_pools: int,
    minimum_position_active_pools: int,
    minimum_position_action_logs: int,
    minimum_swap_active_pools_per_fee_value: int,
    minimum_position_active_pools_per_fee_value: int,
    minimum_npm_position_action_share: float,
    maximum_single_pool_swap_count_share: float,
    maximum_single_pool_position_action_count_share: float,
) -> dict[str, object]:
    """Apply full-population exposure-support gates."""

    swap_counts = [int(cast(int, row.get("swap_count"))) for row in census_rows]
    position_counts = [int(cast(int, row.get("position_action_count"))) for row in census_rows]
    total_swaps = sum(swap_counts)
    total_positions = sum(position_counts)
    swap_active = sum(count > 0 for count in swap_counts)
    position_active = sum(count > 0 for count in position_counts)
    exposed = sum(bool(row.get("economically_exposed_preperiod")) for row in census_rows)
    npm_actions = sum(int(cast(int, row.get("npm_position_action_count"))) for row in census_rows)
    npm_share = npm_actions / total_positions if total_positions else 0.0
    largest_swap_share = max(swap_counts, default=0) / total_swaps if total_swaps else 1.0
    largest_position_share = max(position_counts, default=0) / total_positions if total_positions else 1.0
    by_fee: dict[str, dict[str, int]] = {}
    for fee_value in (68, 102):
        fee_rows = [row for row in census_rows if row.get("packed_fee_value") == fee_value]
        by_fee[str(fee_value)] = {
            "pool_count": len(fee_rows),
            "swap_active_pool_count": sum(bool(row.get("swap_active")) for row in fee_rows),
            "position_active_pool_count": sum(bool(row.get("position_active")) for row in fee_rows),
            "economically_exposed_pool_count": sum(
                bool(row.get("economically_exposed_preperiod")) for row in fee_rows
            ),
            "swap_count": sum(int(cast(int, row.get("swap_count"))) for row in fee_rows),
            "position_action_count": sum(
                int(cast(int, row.get("position_action_count"))) for row in fee_rows
            ),
        }
    gates = {
        "exact_population_count": len(census_rows) == 1000,
        "complete_unsaturated_partitions": complete_unsaturated_partitions,
        "no_duplicate_or_conflicting_logs": duplicate_log_count == 0 and conflicting_log_count == 0,
        "minimum_swap_active_pools": swap_active >= minimum_swap_active_pools,
        "minimum_position_active_pools": position_active >= minimum_position_active_pools,
        "minimum_position_action_logs": total_positions >= minimum_position_action_logs,
        "minimum_swap_active_pools_each_fee": all(
            values["swap_active_pool_count"] >= minimum_swap_active_pools_per_fee_value
            for values in by_fee.values()
        ),
        "minimum_position_active_pools_each_fee": all(
            values["position_active_pool_count"] >= minimum_position_active_pools_per_fee_value
            for values in by_fee.values()
        ),
        "minimum_npm_position_action_share": npm_share >= minimum_npm_position_action_share,
        "maximum_single_pool_swap_count_share": (largest_swap_share <= maximum_single_pool_swap_count_share),
        "maximum_single_pool_position_action_count_share": (
            largest_position_share <= maximum_single_pool_position_action_count_share
        ),
    }
    passed = all(gates.values())
    return {
        "schema_version": "ecophys-uniswap-v3-preperiod-exposure-census-result/v1",
        "decision": (
            "PASS_FULL_PREPERIOD_EXPOSURE_SUPPORT_FREEZE_CONTROL_AND_IDENTITY_DESIGN"
            if passed
            else "FAIL_FULL_PREPERIOD_EXPOSURE_SUPPORT_KEEP_UNISWAP_M2_ONLY"
        ),
        "pass": passed,
        "population_pool_count": len(census_rows),
        "swap_active_pool_count": swap_active,
        "position_active_pool_count": position_active,
        "economically_exposed_pool_count": exposed,
        "swap_count": total_swaps,
        "position_action_count": total_positions,
        "npm_position_action_count": npm_actions,
        "npm_position_action_share": npm_share,
        "largest_pool_swap_count_share": largest_swap_share,
        "largest_pool_position_action_count_share": largest_position_share,
        "by_packed_fee_value": by_fee,
        "duplicate_log_count": duplicate_log_count,
        "conflicting_log_count": conflicting_log_count,
        "identity_status": "NOT_OPENED_IN_EXPOSURE_CENSUS",
        "control_source_status": "UNRESOLVED_SEPARATE_GATE_REQUIRED",
        "gates": gates,
    }
