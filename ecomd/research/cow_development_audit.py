"""Schema and retention audit for frozen CoW solver-competition samples."""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import cast

TOP_LEVEL_FIELDS = (
    "auctionId",
    "auctionStartBlock",
    "auctionDeadlineBlock",
    "transactionHashes",
    "auction",
    "solutions",
)
SOLUTION_FIELDS = (
    "ranking",
    "solverAddress",
    "score",
    "referenceScore",
    "txHash",
    "orders",
    "isWinner",
    "filteredOut",
)


def _integer(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _nonnegative_integer_text(value: object) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return value >= 0
    return isinstance(value, str) and value.isdigit()


def _nonzero_hex_address(value: object) -> str | None:
    if not isinstance(value, str) or not value.startswith("0x") or len(value) != 42:
        return None
    try:
        integer = int(value, 16)
    except ValueError:
        return None
    return value.lower() if integer != 0 else None


def audit_competition_payload(
    payload: Mapping[str, object],
    *,
    requested_auction_id: int,
) -> dict[str, object]:
    """Audit one V2 competition payload without normalizing away failures or nulls."""

    errors: list[str] = []
    missing_top = [key for key in TOP_LEVEL_FIELDS if key not in payload]
    if missing_top:
        errors.append(f"missing top-level fields: {missing_top}")
    auction_id = _integer(payload.get("auctionId"))
    if auction_id is None:
        errors.append("auctionId must be an integer")
    elif auction_id != requested_auction_id:
        errors.append("payload auctionId does not match requested ID")
    start_block = _integer(payload.get("auctionStartBlock"))
    deadline_block = _integer(payload.get("auctionDeadlineBlock"))
    if start_block is None or start_block <= 0:
        errors.append("auctionStartBlock must be positive")
    if deadline_block is None or deadline_block <= 0:
        errors.append("auctionDeadlineBlock must be positive")
    if start_block is not None and deadline_block is not None and start_block > deadline_block:
        errors.append("auction start block exceeds deadline block")

    transaction_hashes = payload.get("transactionHashes")
    if not isinstance(transaction_hashes, list) or any(
        not isinstance(item, str) for item in transaction_hashes
    ):
        errors.append("transactionHashes must be a string list")
        transaction_count = 0
    else:
        transaction_count = len(transaction_hashes)

    auction = payload.get("auction")
    auction_order_count = 0
    auction_price_count = 0
    if not isinstance(auction, Mapping):
        errors.append("auction must be a mapping")
    else:
        orders = auction.get("orders")
        prices = auction.get("prices")
        if not isinstance(orders, list):
            errors.append("auction.orders must be a list")
        else:
            auction_order_count = len(orders)
        if not isinstance(prices, Mapping):
            errors.append("auction.prices must be a mapping")
        else:
            auction_price_count = len(prices)

    solutions = payload.get("solutions")
    solution_count = 0
    winner_count = 0
    filtered_count = 0
    null_tx_count = 0
    zero_or_missing_address_count = 0
    solver_addresses: set[str] = set()
    rankings: list[float] = []
    missing_solution_fields = 0
    invalid_solution_fields = 0
    if not isinstance(solutions, list):
        errors.append("solutions must be a list")
    else:
        solution_count = len(solutions)
        for index, solution in enumerate(solutions):
            if not isinstance(solution, Mapping):
                errors.append(f"solutions[{index}] must be a mapping")
                invalid_solution_fields += 1
                continue
            missing = [key for key in SOLUTION_FIELDS if key not in solution]
            missing_solution_fields += len(missing)
            if missing:
                errors.append(f"solutions[{index}] missing fields: {missing}")
            ranking = solution.get("ranking")
            if isinstance(ranking, bool) or not isinstance(ranking, (int, float)):
                errors.append(f"solutions[{index}].ranking must be numeric")
                invalid_solution_fields += 1
            elif not math.isfinite(float(ranking)):
                errors.append(f"solutions[{index}].ranking must be finite")
                invalid_solution_fields += 1
            else:
                rankings.append(float(ranking))
            if not _nonnegative_integer_text(solution.get("score")):
                errors.append(f"solutions[{index}].score must be a nonnegative integer string")
                invalid_solution_fields += 1
            reference_score = solution.get("referenceScore")
            if reference_score is not None and not _nonnegative_integer_text(reference_score):
                errors.append(f"solutions[{index}].referenceScore is invalid")
                invalid_solution_fields += 1
            address = _nonzero_hex_address(solution.get("solverAddress"))
            if address is None:
                zero_or_missing_address_count += 1
            else:
                solver_addresses.add(address)
            tx_hash = solution.get("txHash")
            if tx_hash is None:
                null_tx_count += 1
            elif not isinstance(tx_hash, str):
                errors.append(f"solutions[{index}].txHash must be a string or null")
                invalid_solution_fields += 1
            if not isinstance(solution.get("orders"), list):
                errors.append(f"solutions[{index}].orders must be a list")
                invalid_solution_fields += 1
            if not isinstance(solution.get("isWinner"), bool):
                errors.append(f"solutions[{index}].isWinner must be boolean")
                invalid_solution_fields += 1
            elif solution["isWinner"]:
                winner_count += 1
            if not isinstance(solution.get("filteredOut"), bool):
                errors.append(f"solutions[{index}].filteredOut must be boolean")
                invalid_solution_fields += 1
            elif solution["filteredOut"]:
                filtered_count += 1

    return {
        "parse_ok": not errors,
        "errors": errors,
        "requested_auction_id": requested_auction_id,
        "payload_auction_id": auction_id,
        "auction_start_block": start_block,
        "auction_deadline_block": deadline_block,
        "transaction_count": transaction_count,
        "auction_order_count": auction_order_count,
        "auction_price_count": auction_price_count,
        "solution_count": solution_count,
        "winner_count": winner_count,
        "filtered_solution_count": filtered_count,
        "null_solution_tx_count": null_tx_count,
        "zero_or_missing_solver_address_count": zero_or_missing_address_count,
        "unique_solver_address_count": len(solver_addresses),
        "unique_ranking_count": len(set(rankings)),
        "missing_solution_field_count": missing_solution_fields,
        "invalid_solution_field_count": invalid_solution_fields,
    }


def parse_utc_timestamp(value: object) -> datetime | None:
    """Parse the contract's required `Z` timestamps."""

    if not isinstance(value, str) or not value.endswith("Z"):
        return None
    try:
        parsed = datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    except ValueError:
        return None
    return parsed if parsed.tzinfo == UTC else None


def _sha256_or_none(value: object) -> str | None:
    if not isinstance(value, str) or len(value) != 64:
        return None
    return value if all(character in "0123456789abcdef" for character in value) else None


def summarize_initial_sample(
    entries: Sequence[Mapping[str, object]],
    *,
    expected_ids: Sequence[int],
    block_timestamps: Mapping[int, int],
    cutoff_utc: str,
    minimum_http_200_coverage: float,
    ledger_sha256: str,
    block_response_sha256: str | None,
) -> dict[str, object]:
    """Summarize the exact frozen sample and evaluate only preregistered gates."""

    if _sha256_or_none(ledger_sha256) is None:
        raise ValueError("ledger_sha256 must be a SHA-256 digest")
    if block_response_sha256 is not None and _sha256_or_none(block_response_sha256) is None:
        raise ValueError("block_response_sha256 must be a SHA-256 digest or null")
    cutoff = parse_utc_timestamp(cutoff_utc)
    if cutoff is None:
        raise ValueError("cutoff_utc must be a UTC timestamp ending in Z")
    expected = list(expected_ids)
    requested_raw = [entry.get("auction_id") for entry in entries]
    requested_are_integers = all(
        isinstance(value, int) and not isinstance(value, bool) for value in requested_raw
    )
    requested = cast(list[int], requested_raw) if requested_are_integers else []
    exact_request_ledger = requested == expected and len(set(requested)) == len(expected)
    http_200 = [entry for entry in entries if entry.get("http_status") == 200]
    parsed = [entry for entry in http_200 if entry.get("parse_ok") is True]
    payload_ids = [
        cast(int, entry["payload_auction_id"])
        for entry in parsed
        if isinstance(entry.get("payload_auction_id"), int)
        and not isinstance(entry.get("payload_auction_id"), bool)
    ]
    duplicate_payload_ids = len(payload_ids) - len(set(payload_ids))
    id_match_count = sum(
        entry.get("auction_id") == entry.get("payload_auction_id") for entry in parsed
    )
    start_blocks = [
        cast(int, entry["auction_start_block"])
        for entry in parsed
        if isinstance(entry.get("auction_start_block"), int)
        and not isinstance(entry.get("auction_start_block"), bool)
    ]
    missing_block_timestamps = sorted(set(start_blocks) - set(block_timestamps))
    cutoff_epoch = int(cutoff.timestamp())
    available_timestamps = [block_timestamps[block] for block in start_blocks if block in block_timestamps]
    all_available_pre_cutoff = bool(available_timestamps) and all(
        timestamp < cutoff_epoch for timestamp in available_timestamps
    )
    status_counts: dict[str, int] = {}
    for entry in entries:
        status = str(entry.get("http_status"))
        status_counts[status] = status_counts.get(status, 0) + 1
    parse_rate = len(parsed) / len(http_200) if http_200 else 0.0
    coverage = len(http_200) / len(expected) if expected else 0.0
    id_match_rate = id_match_count / len(parsed) if parsed else 0.0
    gates = {
        "exact_request_ledger": exact_request_ledger,
        "http_200_coverage": coverage >= minimum_http_200_coverage,
        "parse_rate_among_http_200": parse_rate == 1.0,
        "requested_id_matches_payload": id_match_rate == 1.0,
        "duplicate_payload_ids": duplicate_payload_ids == 0,
        "every_available_auction_precedes_cutoff": (
            all_available_pre_cutoff and not missing_block_timestamps
        ),
        "every_request_outcome_retained": len(entries) == len(expected),
    }
    aggregate_fields = (
        "solution_count",
        "winner_count",
        "filtered_solution_count",
        "null_solution_tx_count",
        "zero_or_missing_solver_address_count",
        "auction_order_count",
    )
    totals = {
        field: sum(
            cast(int, entry[field])
            for entry in parsed
            if isinstance(entry.get(field), int) and not isinstance(entry.get(field), bool)
        )
        for field in aggregate_fields
    }
    return {
        "schema": "ecophys-cow-initial-development-audit/v1",
        "scientific_role": "development_only_no_confirmation_claim",
        "requested_count": len(expected),
        "ledger_count": len(entries),
        "http_status_counts": status_counts,
        "http_200_count": len(http_200),
        "http_200_coverage": coverage,
        "parsed_http_200_count": len(parsed),
        "parse_rate_among_http_200": parse_rate,
        "requested_id_match_rate": id_match_rate,
        "duplicate_payload_id_count": duplicate_payload_ids,
        "auction_id_minimum": min(payload_ids, default=None),
        "auction_id_maximum": max(payload_ids, default=None),
        "start_block_minimum": min(start_blocks, default=None),
        "start_block_maximum": max(start_blocks, default=None),
        "block_timestamp_count": len(block_timestamps),
        "missing_block_timestamps": missing_block_timestamps,
        "cutoff_utc": cutoff_utc,
        "aggregate_diagnostics": totals,
        "ledger_sha256": ledger_sha256,
        "block_response_sha256": block_response_sha256,
        "gates": gates,
        "pass": all(gates.values()),
    }


def canonical_json_sha256(payload: object) -> str:
    """Hash a JSON-safe payload in canonical form."""

    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def parse_block_timestamp_response(
    raw: bytes,
    blocks: Sequence[int],
) -> tuple[dict[int, int], str | None]:
    """Parse a fixed Ethereum batch response while preserving provider failures."""

    try:
        payload: object = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as parse_error:
        return {}, f"invalid JSON: {type(parse_error).__name__}: {parse_error}"
    if not isinstance(payload, list):
        if isinstance(payload, dict) and isinstance(payload.get("error"), dict):
            provider_error = cast(dict[str, object], payload["error"])
            return {}, (
                f"provider error code={provider_error.get('code')}: "
                f"{provider_error.get('message')}"
            )
        return {}, "Ethereum batch response is not a list"
    timestamps: dict[int, int] = {}
    for item in payload:
        if not isinstance(item, dict):
            continue
        item_id = item.get("id")
        result = item.get("result")
        if isinstance(item_id, int) and 0 <= item_id < len(blocks) and isinstance(result, dict):
            timestamp = result.get("timestamp")
            if isinstance(timestamp, str):
                try:
                    timestamps[blocks[item_id]] = int(timestamp, 16)
                except ValueError:
                    continue
    missing = len(blocks) - len(timestamps)
    result_error = None if missing == 0 else f"missing {missing} of {len(blocks)} block timestamps"
    return timestamps, result_error
