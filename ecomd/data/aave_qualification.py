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


def extract_solidity_event_definitions(source: str) -> dict[str, dict[str, Any]]:
    """Extract canonical event signatures and indexed positions from Solidity source."""
    without_comments = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    without_comments = re.sub(r"//[^\n]*", "", without_comments)
    definitions: dict[str, dict[str, Any]] = {}
    for match in re.finditer(
        r"\bevent\s+([A-Za-z_][A-Za-z0-9_]*)\s*\((.*?)\)\s*;",
        without_comments,
        flags=re.DOTALL,
    ):
        name = match.group(1)
        raw_parameters = [part.strip() for part in match.group(2).split(",")]
        types: list[str] = []
        indexed_positions: list[int] = []
        for position, raw_parameter in enumerate(raw_parameters):
            if not raw_parameter:
                continue
            tokens = raw_parameter.split()
            if "indexed" in tokens:
                indexed_positions.append(position)
            qualifiers = {"indexed", "memory", "calldata", "storage", "payable"}
            type_tokens = [token for token in tokens if token not in qualifiers]
            if not type_tokens:
                raise ValueError(f"event {name} contains an empty parameter")
            canonical_type = type_tokens[0]
            if canonical_type == "uint":
                canonical_type = "uint256"
            elif canonical_type == "int":
                canonical_type = "int256"
            types.append(canonical_type)
        signature = f"{name}({','.join(types)})"
        definition = {
            "name": name,
            "signature": signature,
            "parameter_types": types,
            "indexed_positions": indexed_positions,
        }
        previous = definitions.get(signature)
        if previous is not None and previous != definition:
            raise ValueError(f"conflicting definitions for event {signature}")
        definitions[signature] = definition
    return definitions


def _balanced_segment(source: str, opening_index: int, *, opening: str, closing: str) -> str:
    if opening_index < 0 or opening_index >= len(source) or source[opening_index] != opening:
        raise ValueError("balanced segment does not start at the requested delimiter")
    depth = 0
    for index in range(opening_index, len(source)):
        character = source[index]
        if character == opening:
            depth += 1
        elif character == closing:
            depth -= 1
            if depth == 0:
                return source[opening_index + 1 : index]
    raise ValueError("unterminated balanced segment")


def _solidity_bps(expression: str) -> int:
    normalized = expression.strip()
    wrapped = re.fullmatch(r"_bpsToRay\(\s*([0-9][0-9_]*)\s*\)", normalized)
    literal = wrapped.group(1) if wrapped is not None else normalized
    if re.fullmatch(r"[0-9][0-9_]*", literal) is None:
        raise ValueError(f"unsupported Solidity basis-point expression: {expression}")
    return int(literal.replace("_", ""))


def extract_rate_strategy_updates(source: str) -> list[dict[str, Any]]:
    """Parse V3 config-engine rate updates without compiling untrusted proposal code."""
    marker = "IAaveV3ConfigEngine.RateStrategyUpdate({"
    updates: list[dict[str, Any]] = []
    search_from = 0
    while True:
        marker_index = source.find(marker, search_from)
        if marker_index < 0:
            break
        opening_index = marker_index + len(marker) - 1
        body = _balanced_segment(source, opening_index, opening="{", closing="}")
        search_from = opening_index + len(body) + 2
        asset_match = re.search(
            r"\basset\s*:\s*AaveV3[A-Za-z0-9_]*Assets\.([A-Za-z0-9_]+)_UNDERLYING\b",
            body,
        )
        if asset_match is None:
            raise ValueError("rate update has no recognized Aave V3 asset constant")
        params_match = re.search(
            r"\bparams\s*:\s*(?:IV3RateStrategyFactory\.RateStrategyParams|"
            r"IAaveV3ConfigEngine\.InterestRateInputData)\s*\(\s*\{",
            body,
        )
        if params_match is None:
            raise ValueError(f"rate update for {asset_match.group(1)} has unknown params type")
        params_opening = params_match.end() - 1
        params_body = _balanced_segment(body, params_opening, opening="{", closing="}")
        fields: dict[str, str] = {}
        for field_match in re.finditer(
            r"\b([A-Za-z_][A-Za-z0-9_]*)\s*:\s*([^,}\n]+)", params_body
        ):
            field = field_match.group(1)
            if field in fields:
                raise ValueError(f"duplicate rate field {field}")
            fields[field] = field_match.group(2).strip()
        if not fields:
            raise ValueError(f"rate update for {asset_match.group(1)} has no fields")
        configured_fields = [
            field for field, value in fields.items() if value != "EngineFlags.KEEP_CURRENT"
        ]
        slope1_bps = (
            _solidity_bps(fields["variableRateSlope1"])
            if "variableRateSlope1" in configured_fields
            else None
        )
        updates.append(
            {
                "asset_alias": asset_match.group(1),
                "configured_change_fields": configured_fields,
                "variable_rate_slope1_bps": slope1_bps,
                "slope1_only": configured_fields == ["variableRateSlope1"],
            }
        )
    return updates


def _address_from_data_word_zero(data: str) -> str:
    normalized = data.lower()
    if re.fullmatch(r"0x[0-9a-f]*", normalized) is None or len(normalized) < 66:
        raise ValueError("event data lacks a complete ABI word")
    return normalize_address("0x" + normalized[26:66])


def _address_from_topic(topic: str) -> str:
    return normalize_address("0x" + _normalize_topic(topic)[-40:])


def reduce_policy_logs(
    logs: Sequence[Mapping[str, Any]],
    *,
    contract_addresses: Mapping[str, str],
    topic_definitions: Mapping[str, Mapping[str, Any]],
    selected_assets: Mapping[str, str],
    selected_tokens: Mapping[str, Sequence[str]],
    start_block: int,
    end_block_inclusive: int,
    block_timestamps: Mapping[int, int],
) -> list[dict[str, Any]]:
    """Sanitize configuration logs while retaining policy provenance only."""
    if start_block < 0 or end_block_inclusive < start_block:
        raise ValueError("invalid policy-ledger block interval")
    normalized_contracts = {
        normalize_address(address): str(group)
        for group, address in contract_addresses.items()
    }
    if len(normalized_contracts) != len(contract_addresses):
        raise ValueError("policy contract addresses must be unique")
    normalized_topics = {
        _normalize_topic(topic): dict(definition)
        for topic, definition in topic_definitions.items()
    }
    asset_lookup = {
        normalize_address(address): str(symbol)
        for symbol, address in selected_assets.items()
    }
    token_lookup: dict[str, str] = {}
    for token_symbol, addresses in selected_tokens.items():
        for address in addresses:
            normalized = normalize_address(address)
            if normalized in token_lookup:
                raise ValueError("selected policy tokens must be unique")
            token_lookup[normalized] = str(token_symbol)

    sanitized: list[dict[str, Any]] = []
    seen: set[tuple[str, str, int]] = set()
    for raw_log in logs:
        if raw_log.get("removed") is True:
            raise ValueError("removed logs are forbidden in a formal policy ledger")
        address = normalize_address(str(raw_log.get("address")))
        contract_group = normalized_contracts.get(address)
        if contract_group is None:
            raise ValueError("RPC returned a log from an unexpected policy contract")
        raw_topics = raw_log.get("topics")
        if not isinstance(raw_topics, Sequence) or isinstance(raw_topics, (str, bytes)):
            raise ValueError("policy log topics must be a sequence")
        if not raw_topics:
            raise ValueError("policy log has no signature topic")
        topics = [_normalize_topic(str(topic)) for topic in raw_topics]
        definition = normalized_topics.get(topics[0])
        if definition is None:
            raise ValueError("RPC returned an unexpected policy event")
        if str(definition["contract_group"]) != contract_group:
            raise ValueError("policy event topic came from the wrong contract group")
        block_number = _hex_quantity(raw_log.get("blockNumber"), field="blockNumber")
        if not start_block <= block_number <= end_block_inclusive:
            raise ValueError("RPC returned a policy log outside the requested interval")
        if block_number not in block_timestamps:
            raise ValueError(f"policy block {block_number} has no verified timestamp")
        transaction_hash = _normalize_topic(str(raw_log.get("transactionHash")))
        block_hash = _normalize_topic(str(raw_log.get("blockHash")))
        log_index = _hex_quantity(raw_log.get("logIndex"), field="logIndex")
        identity = (block_hash, transaction_hash, log_index)
        if identity in seen:
            raise ValueError("duplicate policy log returned across RPC chunks")
        seen.add(identity)

        scope_rule = str(definition["scope_rule"])
        symbol: str | None = None
        if scope_rule == "asset_topic":
            if len(topics) < 2:
                raise ValueError("asset-scoped policy event lacks indexed asset")
            symbol = asset_lookup.get(_address_from_topic(topics[1]))
            scope = "selected_asset" if symbol is not None else "other_asset"
        elif scope_rule == "asset_data_word_zero":
            symbol = asset_lookup.get(_address_from_data_word_zero(str(raw_log.get("data"))))
            scope = "selected_asset" if symbol is not None else "other_asset"
        elif scope_rule == "reward_asset_topic":
            if len(topics) < 2:
                raise ValueError("reward event lacks indexed configured asset")
            symbol = token_lookup.get(_address_from_topic(topics[1]))
            scope = "selected_asset" if symbol is not None else "other_reward_asset"
        elif scope_rule == "global":
            scope = "global"
        else:
            raise ValueError(f"unknown policy scope rule: {scope_rule}")

        raw_data = str(raw_log.get("data"))
        if re.fullmatch(r"0x[0-9a-fA-F]*", raw_data) is None:
            raise ValueError("policy event has malformed data")
        sanitized.append(
            {
                "event_signature": str(definition["signature"]),
                "event_name": str(definition["name"]),
                "contract_group": contract_group,
                "scope": scope,
                "symbol": symbol,
                "block_number": block_number,
                "block_timestamp": int(block_timestamps[block_number]),
                "transaction_hash": transaction_hash,
                "policy_data_sha256": hashlib.sha256(raw_data.lower().encode()).hexdigest(),
            }
        )
    return sorted(
        sanitized,
        key=lambda row: (
            int(row["block_number"]),
            str(row["transaction_hash"]),
            str(row["event_signature"]),
            str(row["symbol"]),
        ),
    )


_GLOBAL_MATERIAL_EVENTS = {
    ("pool_configurator", "EModeCategoryAdded"),
    ("pool_configurator", "EModeCategoryIsolationChanged"),
    ("oracle", "FallbackOracleUpdated"),
    ("addresses_provider", "PoolUpdated"),
    ("addresses_provider", "PoolConfiguratorUpdated"),
    ("addresses_provider", "PriceOracleUpdated"),
    ("addresses_provider", "PriceOracleSentinelUpdated"),
}


def classify_clean_policy_windows(
    policy_events: Sequence[Mapping[str, Any]],
    units: Sequence[Mapping[str, Any]],
    *,
    exclusion_pre_seconds: int,
    minimum_clean_post_seconds: int,
    target_post_seconds: int,
) -> list[dict[str, Any]]:
    """Apply the frozen target, contamination and administrative-censoring rules."""
    if not 0 < minimum_clean_post_seconds <= target_post_seconds:
        raise ValueError("clean-post duration must be positive and no longer than target follow-up")
    if exclusion_pre_seconds < 0:
        raise ValueError("exclusion pre-period cannot be negative")
    target_names = {"ReserveInterestRateStrategyChanged", "ReserveInterestRateDataChanged"}
    results: list[dict[str, Any]] = []
    for unit in units:
        proposal_id = int(unit["proposal_id"])
        symbol = str(unit["symbol"])
        execution_block = int(unit["execution_block"])
        execution_timestamp = int(unit["execution_timestamp"])
        execution_transaction_hash = _normalize_topic(str(unit["execution_transaction_hash"]))

        exact_targets = [
            event
            for event in policy_events
            if str(event["event_name"]) in target_names
            and event.get("symbol") == symbol
            and int(event["block_number"]) == execution_block
            and str(event["transaction_hash"]).lower() == execution_transaction_hash
        ]
        material_events: list[Mapping[str, Any]] = []
        for event in policy_events:
            is_exact_target = event in exact_targets
            if is_exact_target:
                continue
            event_scope = str(event["scope"])
            event_group = str(event["contract_group"])
            event_name = str(event["event_name"])
            if (
                event_scope == "selected_asset" and event.get("symbol") == symbol
            ) or (
                event_scope == "global"
                and (event_group, event_name) in _GLOBAL_MATERIAL_EVENTS
            ):
                material_events.append(event)

        exclusion_start = execution_timestamp - exclusion_pre_seconds
        clean_post_end = execution_timestamp + minimum_clean_post_seconds
        target_post_end = execution_timestamp + target_post_seconds
        contaminating = [
            event
            for event in material_events
            if exclusion_start <= int(event["block_timestamp"]) <= clean_post_end
        ]
        later = sorted(
            (
                event
                for event in material_events
                if clean_post_end < int(event["block_timestamp"]) < target_post_end
            ),
            key=lambda event: (int(event["block_timestamp"]), int(event["block_number"])),
        )
        first_later = later[0] if later else None
        target_matches_exactly_once = len(exact_targets) == 1
        eligible = target_matches_exactly_once and not contaminating
        censor_timestamp = (
            int(first_later["block_timestamp"])
            if eligible and first_later is not None
            else target_post_end if eligible else None
        )
        results.append(
            {
                "proposal_id": proposal_id,
                "symbol": symbol,
                "cohort": str(unit["cohort"]),
                "execution_block": execution_block,
                "execution_timestamp": execution_timestamp,
                "execution_transaction_hash": execution_transaction_hash,
                "exact_target_event_count": len(exact_targets),
                "target_matches_exactly_once": target_matches_exactly_once,
                "contaminating_events": [dict(event) for event in contaminating],
                "contaminating_event_count": len(contaminating),
                "administrative_censor_event": (
                    dict(first_later) if eligible and first_later is not None else None
                ),
                "administrative_censor_timestamp": censor_timestamp,
                "clean_followup_seconds": (
                    censor_timestamp - execution_timestamp
                    if censor_timestamp is not None
                    else 0
                ),
                "clean_window_eligible": eligible,
            }
        )
    return results


def assess_clean_panel(
    units: Sequence[Mapping[str, Any]],
    *,
    minimum_total: int,
    minimum_primary: int,
    minimum_reverse: int,
    minimum_assets_per_proposal: int,
) -> dict[str, Any]:
    """Evaluate the frozen Aave clean-panel arithmetic without fallback tiers."""
    eligible = [unit for unit in units if bool(unit["clean_window_eligible"])]
    primary = sum(str(unit["cohort"]) == "primary_rate_decrease" for unit in eligible)
    reverse = sum(str(unit["cohort"]) == "reverse_sign" for unit in eligible)
    proposal_ids = sorted({int(unit["proposal_id"]) for unit in units})
    by_proposal = {
        str(proposal_id): sum(int(unit["proposal_id"]) == proposal_id for unit in eligible)
        for proposal_id in proposal_ids
    }
    checks = {
        "minimum_total_clean_units": len(eligible) >= minimum_total,
        "minimum_primary_clean_units": primary >= minimum_primary,
        "minimum_reverse_sign_clean_units": reverse >= minimum_reverse,
        "minimum_clean_assets_per_proposal": all(
            count >= minimum_assets_per_proposal for count in by_proposal.values()
        ),
    }
    return {
        "passed": all(checks.values()),
        "eligible_unit_count": len(eligible),
        "eligible_primary_unit_count": primary,
        "eligible_reverse_sign_unit_count": reverse,
        "eligible_units_by_proposal": by_proposal,
        "decision_checks": checks,
    }
