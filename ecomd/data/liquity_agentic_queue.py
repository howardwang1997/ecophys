"""Outcome-blind decoding and support gates for Liquity V2 priority queues."""

from __future__ import annotations

import re
from bisect import bisect_left
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import Any

from ecomd.data.aave_agent_guardrail import (
    address_from_topic,
    normalize_hex_data,
    normalize_topic,
)
from ecomd.data.aave_qualification import normalize_address

TROVE_EVENT_WORDS = {
    "TroveOperation": 7,
    "BatchedTroveUpdated": 6,
    "BatchUpdated": 7,
    "Redemption": 6,
}


def _hex_quantity(value: Any, *, field: str) -> int:
    if not isinstance(value, str) or re.fullmatch(r"0x(?:0|[1-9a-fA-F][0-9a-fA-F]*)", value) is None:
        raise ValueError(f"invalid {field}: {value}")
    return int(value, 16)


def _static_words(data: Any, expected_words: int) -> list[bytes]:
    normalized = normalize_hex_data(str(data))
    blob = bytes.fromhex(normalized[2:])
    if len(blob) != expected_words * 32:
        raise ValueError(f"event data contains {len(blob) // 32} ABI words; expected {expected_words}")
    return [blob[index * 32 : (index + 1) * 32] for index in range(expected_words)]


def _uint8_word(word: bytes, *, field: str) -> int:
    value = int.from_bytes(word, "big")
    if value >= 2**8:
        raise ValueError(f"{field} is not a canonical uint8: {value}")
    return value


def _address_word(word: bytes, *, field: str) -> str:
    if any(word[:12]):
        raise ValueError(f"{field} has non-zero ABI padding")
    return normalize_address("0x" + word[12:].hex())


def log_identity(event: Mapping[str, Any]) -> tuple[str, str, int, str, str]:
    """Return the canonical identity used for independent-RPC replication."""
    return (
        normalize_topic(str(event["block_hash"])),
        normalize_topic(str(event["transaction_hash"])),
        int(event["log_index"]),
        normalize_address(str(event["contract_address"])),
        normalize_topic(str(event["topic0"])),
    )


def decode_support_log(
    raw_log: Mapping[str, Any],
    *,
    branches_by_trove_manager: Mapping[str, str],
    signatures_by_topic: Mapping[str, str],
    trove_operations_by_code: Mapping[int, str],
    batch_operations_by_code: Mapping[int, str],
    from_block: int,
    to_block: int,
) -> dict[str, Any]:
    """Decode only event identity, operation class, Trove ID, and manager identity."""
    if raw_log.get("removed") is not False:
        raise ValueError("formal logs must be canonical and not removed")
    address = normalize_address(str(raw_log.get("address")))
    normalized_branches = {
        normalize_address(manager): str(branch) for manager, branch in branches_by_trove_manager.items()
    }
    branch = normalized_branches.get(address)
    if branch is None:
        raise ValueError(f"log came from an unexpected TroveManager: {address}")

    topics_value = raw_log.get("topics")
    if not isinstance(topics_value, Sequence) or isinstance(topics_value, (str, bytes)) or not topics_value:
        raise ValueError("log topics must be a nonempty sequence")
    topics = [normalize_topic(str(value)) for value in topics_value]
    normalized_signatures = {
        normalize_topic(topic): str(event_name) for topic, event_name in signatures_by_topic.items()
    }
    event_name = normalized_signatures.get(topics[0])
    if event_name not in TROVE_EVENT_WORDS:
        raise ValueError(f"unexpected event topic: {topics[0]}")

    expected_topics = 1 if event_name == "Redemption" else 2
    if len(topics) != expected_topics:
        raise ValueError(f"{event_name} has {len(topics)} topics; expected {expected_topics}")
    words = _static_words(raw_log.get("data"), TROVE_EVENT_WORDS[event_name])
    block_number = _hex_quantity(raw_log.get("blockNumber"), field="blockNumber")
    if not from_block <= block_number <= to_block:
        raise ValueError("log lies outside the frozen block interval")

    event: dict[str, Any] = {
        "event_name": event_name,
        "branch": branch,
        "block_number": block_number,
        "block_hash": normalize_topic(str(raw_log.get("blockHash"))),
        "transaction_hash": normalize_topic(str(raw_log.get("transactionHash"))),
        "transaction_index": _hex_quantity(raw_log.get("transactionIndex"), field="transactionIndex"),
        "log_index": _hex_quantity(raw_log.get("logIndex"), field="logIndex"),
        "contract_address": address,
        "topic0": topics[0],
    }
    if event_name in {"TroveOperation", "BatchedTroveUpdated"}:
        event["trove_id"] = topics[1]
    if event_name == "TroveOperation":
        operation = _uint8_word(words[0], field="TroveOperation operation")
        if operation not in trove_operations_by_code:
            raise ValueError(f"unknown TroveOperation code: {operation}")
        event["operation"] = operation
        event["operation_name"] = trove_operations_by_code[operation]
    elif event_name == "BatchedTroveUpdated":
        event["interest_batch_manager"] = _address_word(words[0], field="BatchedTroveUpdated manager")
    elif event_name == "BatchUpdated":
        event["interest_batch_manager"] = address_from_topic(topics[1])
        operation = _uint8_word(words[0], field="BatchUpdated operation")
        if operation not in batch_operations_by_code:
            raise ValueError(f"unknown BatchUpdated code: {operation}")
        event["operation"] = operation
        event["operation_name"] = batch_operations_by_code[operation]
    return event


def _utc_date(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp, UTC).date().isoformat()


def _check(
    name: str,
    observed: int | float,
    threshold: int | float,
) -> dict[str, Any]:
    return {
        "name": name,
        "observed": observed,
        "threshold": threshold,
        "passed": observed >= threshold,
    }


def summarize_agentic_queue_support(
    events: Sequence[Mapping[str, Any]],
    *,
    official_arms_by_branch: Mapping[str, str],
    thresholds: Mapping[str, int | float],
    redemption_proximity_seconds: int,
    raw_event_count: int | None = None,
) -> dict[str, Any]:
    """Summarize frozen sample support without using numerical protocol outcomes."""
    expected_thresholds = {
        "minimum_unique_opened_troves",
        "minimum_unique_ever_batched_troves",
        "minimum_unique_official_arm_troves",
        "minimum_official_arm_troves_each_qualifying_branch",
        "minimum_official_arm_trove_branches",
        "minimum_registered_batch_managers",
        "minimum_distinct_batch_managers_with_two_rate_updates",
        "minimum_official_arm_rate_updates",
        "minimum_official_arm_rate_updates_each_qualifying_branch",
        "minimum_official_arm_update_branches",
        "minimum_manual_interest_rate_adjustments",
        "minimum_unique_manual_interest_rate_troves",
        "minimum_redemption_transactions",
        "minimum_redemption_utc_dates",
        "minimum_redemption_branches",
        "minimum_redemption_proximal_official_arm_updates",
        "minimum_proximal_update_utc_dates",
        "minimum_proximal_update_branches",
        "minimum_event_classification_rate",
    }
    if set(thresholds) != expected_thresholds:
        missing = sorted(expected_thresholds - set(thresholds))
        extra = sorted(set(thresholds) - expected_thresholds)
        raise ValueError(f"support thresholds differ from schema: missing={missing}, extra={extra}")
    if redemption_proximity_seconds <= 0:
        raise ValueError("redemption proximity must be positive")

    normalized_arms = {
        str(branch): normalize_address(address) for branch, address in official_arms_by_branch.items()
    }
    opened: set[tuple[str, str]] = set()
    ever_batched: set[tuple[str, str]] = set()
    official_arm_troves: set[tuple[str, str]] = set()
    official_arm_troves_by_branch: dict[str, set[str]] = {branch: set() for branch in normalized_arms}
    registered_managers: set[tuple[str, str]] = set()
    rate_updates_by_manager: Counter[tuple[str, str]] = Counter()
    official_arm_updates: list[Mapping[str, Any]] = []
    official_arm_updates_by_branch: Counter[str] = Counter()
    manual_adjustment_count = 0
    manual_troves: set[tuple[str, str]] = set()
    redemptions: list[Mapping[str, Any]] = []

    for event in events:
        event_name = str(event["event_name"])
        branch = str(event["branch"])
        if branch not in normalized_arms:
            raise ValueError(f"event has an unconfigured branch: {branch}")
        if event_name == "TroveOperation":
            key = (branch, str(event["trove_id"]))
            operation = int(event["operation"])
            if operation in {0, 7}:
                opened.add(key)
            if operation == 3:
                manual_adjustment_count += 1
                manual_troves.add(key)
        elif event_name == "BatchedTroveUpdated":
            key = (branch, str(event["trove_id"]))
            manager = normalize_address(str(event["interest_batch_manager"]))
            ever_batched.add(key)
            if manager == normalized_arms[branch]:
                official_arm_troves.add(key)
                official_arm_troves_by_branch[branch].add(str(event["trove_id"]))
        elif event_name == "BatchUpdated":
            manager = normalize_address(str(event["interest_batch_manager"]))
            manager_key = (branch, manager)
            operation = int(event["operation"])
            if operation == 0:
                registered_managers.add(manager_key)
            if operation == 2:
                rate_updates_by_manager[manager_key] += 1
                if manager == normalized_arms[branch]:
                    if "block_timestamp" not in event:
                        raise ValueError("official ARM rate update lacks a canonical timestamp")
                    official_arm_updates.append(event)
                    official_arm_updates_by_branch[branch] += 1
        elif event_name == "Redemption":
            if "block_timestamp" not in event:
                raise ValueError("redemption event lacks a canonical timestamp")
            redemptions.append(event)
        else:
            raise ValueError(f"unclassified support event: {event_name}")

    redemption_timestamps_by_branch: dict[str, list[int]] = {branch: [] for branch in normalized_arms}
    for event in redemptions:
        redemption_timestamps_by_branch[str(event["branch"])].append(int(event["block_timestamp"]))
    for values in redemption_timestamps_by_branch.values():
        values.sort()

    proximal_updates: list[Mapping[str, Any]] = []
    for event in official_arm_updates:
        timestamp = int(event["block_timestamp"])
        candidates = redemption_timestamps_by_branch[str(event["branch"])]
        insertion = bisect_left(candidates, timestamp)
        neighbors = candidates[max(0, insertion - 1) : insertion + 1]
        if any(abs(timestamp - candidate) <= redemption_proximity_seconds for candidate in neighbors):
            proximal_updates.append(event)

    arm_trove_minimum = int(thresholds["minimum_official_arm_troves_each_qualifying_branch"])
    arm_trove_branches = sum(
        len(values) >= arm_trove_minimum for values in official_arm_troves_by_branch.values()
    )
    arm_update_minimum = int(thresholds["minimum_official_arm_rate_updates_each_qualifying_branch"])
    arm_update_branches = sum(
        count >= arm_update_minimum for count in official_arm_updates_by_branch.values()
    )
    managers_with_two_updates = sum(count >= 2 for count in rate_updates_by_manager.values())
    redemption_transactions = {str(event["transaction_hash"]) for event in redemptions}
    redemption_dates = {_utc_date(int(event["block_timestamp"])) for event in redemptions}
    redemption_branches = {str(event["branch"]) for event in redemptions}
    proximal_dates = {_utc_date(int(event["block_timestamp"])) for event in proximal_updates}
    proximal_branches = {str(event["branch"]) for event in proximal_updates}
    classified = len(events)
    denominator = classified if raw_event_count is None else raw_event_count
    if denominator <= 0:
        raise ValueError("support audit requires at least one raw event")
    classification_rate = classified / denominator

    metrics: dict[str, int | float] = {
        "unique_opened_troves": len(opened),
        "unique_ever_batched_troves": len(ever_batched),
        "unique_official_arm_troves": len(official_arm_troves),
        "official_arm_trove_branches": arm_trove_branches,
        "registered_batch_managers": len(registered_managers),
        "distinct_batch_managers_with_two_rate_updates": managers_with_two_updates,
        "official_arm_rate_updates": len(official_arm_updates),
        "official_arm_update_branches": arm_update_branches,
        "manual_interest_rate_adjustments": manual_adjustment_count,
        "unique_manual_interest_rate_troves": len(manual_troves),
        "redemption_transactions": len(redemption_transactions),
        "redemption_utc_dates": len(redemption_dates),
        "redemption_branches": len(redemption_branches),
        "redemption_proximal_official_arm_updates": len(proximal_updates),
        "proximal_update_utc_dates": len(proximal_dates),
        "proximal_update_branches": len(proximal_branches),
        "event_classification_rate": classification_rate,
    }
    threshold_by_metric = {
        "unique_opened_troves": "minimum_unique_opened_troves",
        "unique_ever_batched_troves": "minimum_unique_ever_batched_troves",
        "unique_official_arm_troves": "minimum_unique_official_arm_troves",
        "official_arm_trove_branches": "minimum_official_arm_trove_branches",
        "registered_batch_managers": "minimum_registered_batch_managers",
        "distinct_batch_managers_with_two_rate_updates": (
            "minimum_distinct_batch_managers_with_two_rate_updates"
        ),
        "official_arm_rate_updates": "minimum_official_arm_rate_updates",
        "official_arm_update_branches": "minimum_official_arm_update_branches",
        "manual_interest_rate_adjustments": "minimum_manual_interest_rate_adjustments",
        "unique_manual_interest_rate_troves": "minimum_unique_manual_interest_rate_troves",
        "redemption_transactions": "minimum_redemption_transactions",
        "redemption_utc_dates": "minimum_redemption_utc_dates",
        "redemption_branches": "minimum_redemption_branches",
        "redemption_proximal_official_arm_updates": ("minimum_redemption_proximal_official_arm_updates"),
        "proximal_update_utc_dates": "minimum_proximal_update_utc_dates",
        "proximal_update_branches": "minimum_proximal_update_branches",
        "event_classification_rate": "minimum_event_classification_rate",
    }
    checks = [
        _check(metric, observed, thresholds[threshold_by_metric[metric]])
        for metric, observed in metrics.items()
    ]
    return {
        "passed": all(bool(check["passed"]) for check in checks),
        "checks": checks,
        "metrics": metrics,
        "by_branch": {
            "unique_official_arm_troves": {
                branch: len(values) for branch, values in sorted(official_arm_troves_by_branch.items())
            },
            "official_arm_rate_updates": dict(sorted(official_arm_updates_by_branch.items())),
            "redemption_events": dict(sorted(Counter(str(event["branch"]) for event in redemptions).items())),
            "redemption_proximal_official_arm_updates": dict(
                sorted(Counter(str(event["branch"]) for event in proximal_updates).items())
            ),
        },
        "rate_updates_by_manager": {
            f"{branch}:{manager}": count
            for (branch, manager), count in sorted(rate_updates_by_manager.items())
        },
        "contains_numerical_protocol_outcomes": False,
    }
