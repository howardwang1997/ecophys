"""Outcome-blind qualification helpers for Aave rate interventions."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from decimal import Decimal
from pathlib import Path
from typing import Any


def canonical_sha256(value: Any) -> str:
    """Return a deterministic SHA-256 digest for a JSON-compatible value."""
    normalized = json.loads(json.dumps(value, allow_nan=False))
    encoded = json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def normalize_address(value: str) -> str:
    """Normalize and validate an EVM address without applying a checksum transform."""
    normalized = value.lower()
    if re.fullmatch(r"0x[0-9a-f]{40}", normalized) is None:
        raise ValueError(f"invalid EVM address: {value}")
    return normalized


def address_topic(value: str) -> str:
    """Encode an indexed address as a 32-byte EVM log topic."""
    return "0x" + "0" * 24 + normalize_address(value)[2:]


def _normalize_topic(value: str) -> str:
    normalized = value.lower()
    if re.fullmatch(r"0x[0-9a-f]{64}", normalized) is None:
        raise ValueError(f"invalid EVM log topic: {value}")
    return normalized


def _hex_quantity(value: Any, *, field: str) -> int:
    if not isinstance(value, str) or re.fullmatch(r"0x[0-9a-fA-F]+", value) is None:
        raise ValueError(f"invalid {field}: {value}")
    return int(value, 16)


def summarize_preperiod_activity(
    windows: Sequence[Mapping[str, Any]],
    *,
    pool_address: str,
    assets: Mapping[str, str],
    borrow_topic: str,
    repay_topic: str,
    minimum_weekly_borrow_events: int,
    minimum_weekly_repay_events: int,
    minimum_weekly_unique_debt_users: int,
    minimum_total_actions: int,
    minimum_total_unique_debt_users: int,
) -> dict[str, Any]:
    """Reduce pre-period logs to frozen activity counts without retaining log values."""
    if not windows:
        raise ValueError("at least one pre-period window is required")
    thresholds = (
        minimum_weekly_borrow_events,
        minimum_weekly_repay_events,
        minimum_weekly_unique_debt_users,
        minimum_total_actions,
        minimum_total_unique_debt_users,
    )
    if any(value < 0 for value in thresholds):
        raise ValueError("activity thresholds must be non-negative")

    normalized_pool = normalize_address(pool_address)
    asset_topics = {
        address_topic(address): str(symbol) for symbol, address in sorted(assets.items())
    }
    if len(asset_topics) != len(assets):
        raise ValueError("asset addresses must be unique")
    event_topics = {
        _normalize_topic(borrow_topic): "borrow",
        _normalize_topic(repay_topic): "repay",
    }
    if len(event_topics) != 2:
        raise ValueError("Borrow and Repay topics must differ")

    symbols = sorted(assets)
    weekly_summaries: dict[str, list[dict[str, Any]]] = {symbol: [] for symbol in symbols}
    total_borrow = {symbol: 0 for symbol in symbols}
    total_repay = {symbol: 0 for symbol in symbols}
    total_users: dict[str, set[str]] = {symbol: set() for symbol in symbols}
    seen_log_ids: set[tuple[str, str, int]] = set()
    previous_end: int | None = None

    for week_index, window in enumerate(windows, start=1):
        start_block = int(window["start_block"])
        end_block_exclusive = int(window["end_block_exclusive"])
        if start_block < 0 or end_block_exclusive <= start_block:
            raise ValueError(f"invalid block window {start_block}:{end_block_exclusive}")
        if previous_end is not None and start_block != previous_end:
            raise ValueError("pre-period block windows must be contiguous")
        previous_end = end_block_exclusive
        logs = window.get("logs")
        if not isinstance(logs, Sequence) or isinstance(logs, (str, bytes)):
            raise ValueError("window logs must be a sequence")
        week_borrow = {symbol: 0 for symbol in symbols}
        week_repay = {symbol: 0 for symbol in symbols}
        week_users: dict[str, set[str]] = {symbol: set() for symbol in symbols}

        for raw_log in logs:
            if not isinstance(raw_log, Mapping):
                raise ValueError("each log must be a mapping")
            if raw_log.get("removed") is True:
                raise ValueError("removed logs are forbidden in a formal activity screen")
            if normalize_address(str(raw_log.get("address"))) != normalized_pool:
                raise ValueError("RPC returned a log from an unexpected contract")
            topics = raw_log.get("topics")
            if not isinstance(topics, Sequence) or isinstance(topics, (str, bytes)):
                raise ValueError("log topics must be a sequence")
            if len(topics) < 3:
                raise ValueError("Borrow/Repay log has fewer than three topics")
            normalized_topics = [_normalize_topic(str(topic)) for topic in topics]
            event_name = event_topics.get(normalized_topics[0])
            symbol = asset_topics.get(normalized_topics[1])
            if event_name is None or symbol is None:
                raise ValueError("RPC returned an unexpected event or reserve")
            block_number = _hex_quantity(raw_log.get("blockNumber"), field="blockNumber")
            if not start_block <= block_number < end_block_exclusive:
                raise ValueError("RPC returned a log outside its requested week")
            block_hash = _normalize_topic(str(raw_log.get("blockHash")))
            transaction_hash = _normalize_topic(str(raw_log.get("transactionHash")))
            log_index = _hex_quantity(raw_log.get("logIndex"), field="logIndex")
            identity = (block_hash, transaction_hash, log_index)
            if identity in seen_log_ids:
                raise ValueError("duplicate log returned across RPC chunks")
            seen_log_ids.add(identity)

            debt_user = normalized_topics[2]
            if event_name == "borrow":
                week_borrow[symbol] += 1
                total_borrow[symbol] += 1
            else:
                week_repay[symbol] += 1
                total_repay[symbol] += 1
            week_users[symbol].add(debt_user)
            total_users[symbol].add(debt_user)

        for symbol in symbols:
            borrow_events = week_borrow[symbol]
            repay_events = week_repay[symbol]
            unique_users = len(week_users[symbol])
            weekly_eligible = (
                borrow_events >= minimum_weekly_borrow_events
                and repay_events >= minimum_weekly_repay_events
                and unique_users >= minimum_weekly_unique_debt_users
            )
            weekly_summaries[symbol].append(
                {
                    "week_index": week_index,
                    "start_block": start_block,
                    "end_block_exclusive": end_block_exclusive,
                    "borrow_events": borrow_events,
                    "repay_events": repay_events,
                    "combined_actions": borrow_events + repay_events,
                    "unique_debt_users": unique_users,
                    "weekly_activity_eligible": weekly_eligible,
                }
            )

    summaries: dict[str, Any] = {}
    for symbol in symbols:
        symbol_total_borrow = total_borrow[symbol]
        symbol_total_repay = total_repay[symbol]
        total_actions = symbol_total_borrow + symbol_total_repay
        total_unique_users = len(total_users[symbol])
        weeks = weekly_summaries[symbol]
        summaries[symbol] = {
            "weeks": weeks,
            "total_borrow_events": symbol_total_borrow,
            "total_repay_events": symbol_total_repay,
            "total_combined_actions": total_actions,
            "total_unique_debt_users": total_unique_users,
            "all_weeks_meet_activity_floor": all(
                bool(week["weekly_activity_eligible"]) for week in weeks
            ),
            "activity_eligible": (
                all(bool(week["weekly_activity_eligible"]) for week in weeks)
                and total_actions >= minimum_total_actions
                and total_unique_users >= minimum_total_unique_debt_users
            ),
            "retained_fields": [
                "block_window",
                "borrow_event_count",
                "repay_event_count",
                "unique_debt_user_count",
            ],
            "retained_addresses_amounts_transactions_or_raw_logs": False,
        }
    return summaries


def _percent_to_bps(value: str) -> int:
    match = re.fullmatch(r"(-?[0-9]+(?:\.[0-9]+)?)\s*%", value.strip())
    if match is None:
        raise ValueError(f"not a percentage: {value}")
    bps = Decimal(match.group(1)) * 100
    if bps != bps.to_integral_value():
        raise ValueError(f"percentage is not an integral number of basis points: {value}")
    return int(bps)


def _asset_section(markdown: str, symbol: str) -> str:
    pattern = re.compile(
        rf"^####\s+{re.escape(symbol)}\s+\([^\n]*\)\s*$\n(.*?)(?=^####\s+|^##\s+|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    matches = pattern.findall(markdown)
    if len(matches) != 1:
        raise ValueError(f"expected one diff section for {symbol}, found {len(matches)}")
    return str(matches[0])


def audit_asset_rate_change(
    markdown: str,
    *,
    symbol: str,
    expected_before_bps: int,
    expected_after_bps: int,
) -> dict[str, Any]:
    """Verify that an asset section changes only the configured slope-1 policy field."""
    section = _asset_section(markdown, symbol)
    changed_rows: list[dict[str, str]] = []
    for line in section.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 3 or cells[0] in {"description", "---"}:
            continue
        if cells[1] != cells[2]:
            changed_rows.append({"field": cells[0], "before": cells[1], "after": cells[2]})

    policy_rows = [
        row
        for row in changed_rows
        if row["field"]
        not in {
            "baseStableBorrowRate",
            "interestRate",
            "interestRateStrategy",
            "maxVariableBorrowRate",
        }
    ]
    if len(policy_rows) != 1 or policy_rows[0]["field"] != "variableRateSlope1":
        raise ValueError(f"{symbol} has unexpected configured changes: {policy_rows}")
    row = policy_rows[0]
    before_bps = _percent_to_bps(row["before"])
    after_bps = _percent_to_bps(row["after"])
    if (before_bps, after_bps) != (expected_before_bps, expected_after_bps):
        raise ValueError(
            f"{symbol} slope-1 change is {before_bps}->{after_bps} bps, expected "
            f"{expected_before_bps}->{expected_after_bps}"
        )
    return {
        "symbol": symbol,
        "slope1_before_bps": before_bps,
        "slope1_after_bps": after_bps,
        "slope1_delta_bps": after_bps - before_bps,
        "configured_change_fields": ["variableRateSlope1"],
        "derived_or_deployment_rows": [
            row for row in changed_rows if row["field"] != "variableRateSlope1"
        ],
        "clean_singleton_configured_change": True,
    }


def extract_implementation_reference(description: str) -> tuple[str, str]:
    """Extract the unique proposal-source commit and directory from cached AIP text."""
    commits = set(re.findall(r"/blob/([0-9a-f]{40})/", description))
    directories = set(re.findall(r"/src/([^/]+)/", description))
    if len(commits) != 1 or len(directories) != 1:
        raise ValueError(
            f"expected one implementation commit/directory, found {commits} and {directories}"
        )
    return next(iter(commits)), next(iter(directories))


def load_json(path: Path) -> Any:
    """Load a JSON file with an explicit UTF-8 contract."""
    return json.loads(path.read_text(encoding="utf-8"))


def find_payload_execution(
    cache_root: Path,
    *,
    proposal_id: int,
    chain_id: int,
) -> dict[str, Any]:
    """Resolve one executed proposal payload to its exact target-chain event."""
    ui_root = cache_root / "cache" / "ui" / "mainnet"
    proposals = load_json(
        cache_root
        / "cache"
        / "1"
        / "proposals"
        / "0x9AEE0B04504CeF83A65AC3f0e838D0593BCb2BC7.json"
    )
    proposal = proposals.get(str(proposal_id))
    if not isinstance(proposal, dict) or proposal.get("state") != 4:
        raise ValueError(f"proposal {proposal_id} is not in executed state 4")

    payload_map = load_json(ui_root / "proposals_payloads.json")["data"]
    candidates = [
        row for row in payload_map.get(str(proposal_id), []) if int(row["chainId"]) == chain_id
    ]
    if len(candidates) != 1:
        raise ValueError(
            f"proposal {proposal_id} has {len(candidates)} payloads on chain {chain_id}"
        )
    payload = candidates[0]
    controller = normalize_address(str(payload["payloadsController"]))
    payload_id = int(payload["id"])

    payload_files = [
        path
        for path in (cache_root / "cache" / str(chain_id) / "payloads").glob("*.json")
        if normalize_address(path.stem) == controller
    ]
    if len(payload_files) != 1:
        raise ValueError(f"could not uniquely resolve payload cache for {controller}")
    payload_record = load_json(payload_files[0]).get(str(payload_id))
    if not isinstance(payload_record, dict) or int(payload_record.get("executedAt", 0)) <= 0:
        raise ValueError(f"payload {payload_id} has no execution timestamp")

    matches: list[dict[str, Any]] = []
    for event_file in (cache_root / "cache" / str(chain_id) / "events").glob("*.json"):
        for event in load_json(event_file):
            args = event.get("args", {})
            if (
                event.get("eventName") == "PayloadExecuted"
                and normalize_address(str(event["address"])) == controller
                and int(args.get("payloadId", -1)) == payload_id
            ):
                matches.append(event)
    if len(matches) != 1:
        raise ValueError(f"payload {payload_id} has {len(matches)} PayloadExecuted events")
    event = matches[0]

    list_rows = load_json(ui_root / "list_view_proposals.json")["proposals"]
    list_matches = [row for row in list_rows if int(row["id"]) == proposal_id]
    if len(list_matches) != 1:
        raise ValueError(f"proposal {proposal_id} is absent or duplicated in the list cache")
    list_row = list_matches[0]
    ipfs_record = load_json(ui_root / "ipfs" / f"{list_row['ipfsHash']}.json")
    implementation_commit, implementation_directory = extract_implementation_reference(
        str(ipfs_record["description"])
    )
    return {
        "proposal_id": proposal_id,
        "title": str(list_row["title"]),
        "ipfs_digest": str(list_row["ipfsHash"]),
        "ipfs_description_sha256": hashlib.sha256(
            str(ipfs_record["description"]).encode()
        ).hexdigest(),
        "discussion": ipfs_record.get("discussions"),
        "implementation_commit": implementation_commit,
        "implementation_directory": implementation_directory,
        "chain_id": chain_id,
        "payload_id": payload_id,
        "payloads_controller": controller,
        "executed_at_unix": int(payload_record["executedAt"]),
        "execution_block": int(event["blockNumber"]),
        "execution_transaction_hash": str(event["transactionHash"]),
        "execution_block_hash": str(event["blockHash"]),
    }
