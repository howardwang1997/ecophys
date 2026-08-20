"""Validation and support metrics for CoW solver-competition records."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from typing import Any


def _hex(value: Any, *, size_bytes: int, label: str) -> str:
    text = str(value).lower()
    if not text.startswith("0x") or len(text) != 2 + 2 * size_bytes:
        raise ValueError(f"invalid {label}: {value}")
    try:
        bytes.fromhex(text[2:])
    except ValueError as error:
        raise ValueError(f"invalid {label}: {value}") from error
    return text


def _quantity(value: Any, *, label: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"invalid {label}: {value}")
    if isinstance(value, int):
        number = value
    else:
        text = str(value)
        try:
            number = int(text, 16) if text.startswith("0x") else int(text)
        except ValueError as error:
            raise ValueError(f"invalid {label}: {value}") from error
    if number < 0:
        raise ValueError(f"invalid {label}: {value}")
    return number


def _decimal_integer(value: Any, *, label: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"invalid {label}: {value}")
    text = str(value)
    if not text.isdecimal():
        raise ValueError(f"invalid {label}: {value}")
    return int(text)


def _mapping(value: Any, *, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object")
    return value


def _sequence(value: Any, *, label: str) -> Sequence[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError(f"{label} must be an array")
    return value


def canonical_json_sha256(payload: Any) -> str:
    """Hash a JSON-compatible object with stable key and separator rules."""
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class SettlementEvent:
    """One source-exact CoW Settlement event returned by an EVM indexer."""

    block_number: int
    log_index: int
    transaction_hash: str
    contract_address: str
    topic0: str

    def identity(self) -> tuple[int, int, str]:
        """Return the deterministic selection and deduplication key."""
        return (self.block_number, self.log_index, self.transaction_hash)


def parse_blockscout_settlement_events(
    payload: Mapping[str, Any],
    *,
    expected_contract: str,
    expected_topic0: str,
    from_block: int,
    to_block: int,
) -> tuple[SettlementEvent, ...]:
    """Validate a Blockscout logs response against the frozen event universe."""
    if from_block < 0 or to_block < from_block:
        raise ValueError("invalid frozen block interval")
    if str(payload.get("status")) != "1" or str(payload.get("message")) != "OK":
        raise ValueError("Blockscout did not return an OK event response")
    rows = _sequence(payload.get("result"), label="Blockscout result")
    contract = _hex(expected_contract, size_bytes=20, label="expected contract")
    topic0 = _hex(expected_topic0, size_bytes=32, label="expected topic0")
    events: list[SettlementEvent] = []
    identities: set[tuple[int, int, str]] = set()
    for raw in rows:
        row = _mapping(raw, label="Blockscout log")
        address = _hex(row.get("address"), size_bytes=20, label="contract address")
        topics = _sequence(row.get("topics"), label="log topics")
        if not topics:
            raise ValueError("Blockscout log has no topic0")
        observed_topic0 = _hex(topics[0], size_bytes=32, label="topic0")
        block_number = _quantity(row.get("blockNumber"), label="block number")
        log_index = _quantity(row.get("logIndex"), label="log index")
        transaction_hash = _hex(row.get("transactionHash"), size_bytes=32, label="transaction hash")
        if address != contract or observed_topic0 != topic0:
            raise ValueError("Blockscout response escaped the frozen contract/topic filter")
        if block_number < from_block or block_number > to_block:
            raise ValueError("Blockscout response escaped the frozen block interval")
        event = SettlementEvent(
            block_number=block_number,
            log_index=log_index,
            transaction_hash=transaction_hash,
            contract_address=address,
            topic0=observed_topic0,
        )
        if event.identity() in identities:
            raise ValueError("Blockscout response contains a duplicate settlement identity")
        identities.add(event.identity())
        events.append(event)
    return tuple(sorted(events, key=SettlementEvent.identity))


@dataclass(frozen=True)
class RemovalObservation:
    """Official leave-one-winning-solver counterfactual for one auction."""

    solver_address: str
    total_winning_score: int
    reference_score: int
    score_loss: int
    valid: bool

    @property
    def criticality(self) -> float | None:
        """Return normalized score loss without clipping invalid observations."""
        if not self.valid:
            return None
        return float(Decimal(self.score_loss) / Decimal(self.total_winning_score))


@dataclass(frozen=True)
class CompetitionSummary:
    """Schema-checked support summary for one queried competition response."""

    auction_id: int
    queried_transaction_hash: str
    transaction_hashes: tuple[str, ...]
    payload_sha256: str
    auction_order_count: int
    solution_count: int
    distinct_solver_count: int
    winner_solution_count: int
    distinct_winning_solver_count: int
    filtered_solution_count: int
    submitted_multi_order_solution_count: int
    eligible_multi_order_solution_count: int
    submitted_coupled: bool
    eligible_coupled: bool
    complete_winner_references: bool
    removals: tuple[RemovalObservation, ...]


@dataclass(frozen=True)
class _Solution:
    solver: str
    score: int
    orders: frozenset[str]
    is_winner: bool
    filtered_out: bool


def _order_ids(raw_orders: Any) -> frozenset[str]:
    orders = _sequence(raw_orders, label="solution orders")
    ids: set[str] = set()
    for raw in orders:
        if isinstance(raw, str):
            order_id = raw.lower()
        else:
            order = _mapping(raw, label="solution order")
            order_id = str(order.get("id", "")).lower()
        if not order_id.startswith("0x") or len(order_id) <= 2:
            raise ValueError("solution order has no valid opaque ID")
        ids.add(order_id)
    return frozenset(ids)


def _is_coupled(solutions: Sequence[_Solution], *, minimum_orders: int) -> bool:
    if minimum_orders < 2:
        raise ValueError("multi-order threshold must be at least two")
    for focal in solutions:
        if len(focal.orders) < minimum_orders:
            continue
        alternatives: set[str] = set()
        for other in solutions:
            if other.solver != focal.solver:
                alternatives.update(other.orders)
        if focal.orders.intersection(alternatives):
            return True
    return False


def summarize_competition(
    payload: Mapping[str, Any],
    *,
    queried_transaction_hash: str,
    required_competition_fields: Sequence[str],
    required_solution_fields: Sequence[str],
    minimum_orders_for_multi_order_solution: int,
) -> CompetitionSummary:
    """Validate one official response and derive preregistered support objects."""
    missing = [field for field in required_competition_fields if field not in payload]
    if missing:
        raise ValueError(f"competition response lacks required fields: {missing}")
    queried_hash = _hex(queried_transaction_hash, size_bytes=32, label="queried transaction hash")
    auction_id = _quantity(payload.get("auctionId"), label="auction ID")
    if auction_id <= 0:
        raise ValueError("auction ID must be positive")
    transaction_hashes = tuple(
        _hex(value, size_bytes=32, label="competition transaction hash")
        for value in _sequence(payload.get("transactionHashes"), label="transaction hashes")
    )
    if queried_hash not in transaction_hashes:
        raise ValueError("queried transaction hash is absent from competition response")

    auction = _mapping(payload.get("auction"), label="auction")
    auction_orders = _sequence(auction.get("orders"), label="auction orders")
    raw_solutions = _sequence(payload.get("solutions"), label="solutions")
    solutions: list[_Solution] = []
    for raw in raw_solutions:
        solution = _mapping(raw, label="solution")
        missing_solution = [field for field in required_solution_fields if field not in solution]
        if missing_solution:
            raise ValueError(f"solution lacks required fields: {missing_solution}")
        is_winner = solution.get("isWinner")
        filtered_out = solution.get("filteredOut")
        if not isinstance(is_winner, bool) or not isinstance(filtered_out, bool):
            raise ValueError("winner and filtering flags must be Boolean")
        solutions.append(
            _Solution(
                solver=_hex(solution.get("solverAddress"), size_bytes=20, label="solver address"),
                score=_decimal_integer(solution.get("score"), label="solution score"),
                orders=_order_ids(solution.get("orders")),
                is_winner=is_winner,
                filtered_out=filtered_out,
            )
        )
    winners = [solution for solution in solutions if solution.is_winner]
    if not winners:
        raise ValueError("competition response has no winning solution")
    total_winning_score = sum(solution.score for solution in winners)
    winning_solvers = sorted({solution.solver for solution in winners})

    raw_references = _mapping(payload.get("referenceScores"), label="reference scores")
    references: dict[str, int] = {}
    for raw_solver, raw_score in raw_references.items():
        solver = _hex(raw_solver, size_bytes=20, label="reference solver address")
        if solver in references:
            raise ValueError("duplicate normalized reference solver address")
        references[solver] = _decimal_integer(raw_score, label="reference score")
    complete_references = all(solver in references for solver in winning_solvers)
    removals: list[RemovalObservation] = []
    for solver in winning_solvers:
        if solver not in references:
            continue
        reference = references[solver]
        loss = total_winning_score - reference
        valid = total_winning_score > 0 and 0 <= loss <= total_winning_score
        removals.append(
            RemovalObservation(
                solver_address=solver,
                total_winning_score=total_winning_score,
                reference_score=reference,
                score_loss=loss,
                valid=valid,
            )
        )

    eligible = [solution for solution in solutions if not solution.filtered_out]
    return CompetitionSummary(
        auction_id=auction_id,
        queried_transaction_hash=queried_hash,
        transaction_hashes=transaction_hashes,
        payload_sha256=canonical_json_sha256(payload),
        auction_order_count=len(auction_orders),
        solution_count=len(solutions),
        distinct_solver_count=len({solution.solver for solution in solutions}),
        winner_solution_count=len(winners),
        distinct_winning_solver_count=len(winning_solvers),
        filtered_solution_count=sum(solution.filtered_out for solution in solutions),
        submitted_multi_order_solution_count=sum(
            len(solution.orders) >= minimum_orders_for_multi_order_solution for solution in solutions
        ),
        eligible_multi_order_solution_count=sum(
            len(solution.orders) >= minimum_orders_for_multi_order_solution for solution in eligible
        ),
        submitted_coupled=_is_coupled(
            solutions,
            minimum_orders=minimum_orders_for_multi_order_solution,
        ),
        eligible_coupled=_is_coupled(
            eligible,
            minimum_orders=minimum_orders_for_multi_order_solution,
        ),
        complete_winner_references=complete_references,
        removals=tuple(removals),
    )


def _at_or_below(observation: RemovalObservation, threshold: float) -> bool:
    return bool(
        observation.valid
        and Decimal(observation.score_loss) / Decimal(observation.total_winning_score)
        <= Decimal(str(threshold))
    )


def _at_or_above(observation: RemovalObservation, threshold: float) -> bool:
    return bool(
        observation.valid
        and Decimal(observation.score_loss) / Decimal(observation.total_winning_score)
        >= Decimal(str(threshold))
    )


def evaluate_t0_support(
    summaries: Sequence[CompetitionSummary],
    *,
    attempted_transaction_count: int,
    membership_failure_count: int,
    gates: Mapping[str, Any],
    low_criticality_maximum: float,
    high_criticality_minimum: float,
) -> dict[str, Any]:
    """Apply the frozen transport, counterfactual and coupling support gates."""
    if attempted_transaction_count < 0 or membership_failure_count < 0:
        raise ValueError("support counts cannot be negative")
    mapped_hashes = {summary.queried_transaction_hash for summary in summaries}
    if len(mapped_hashes) != len(summaries):
        raise ValueError("one transaction hash was summarized more than once")
    if len(mapped_hashes) > attempted_transaction_count:
        raise ValueError("mapped transaction count exceeds attempted count")

    by_auction: dict[int, list[CompetitionSummary]] = defaultdict(list)
    for summary in summaries:
        by_auction[summary.auction_id].append(summary)
    conflicting_auction_ids = sorted(
        auction_id
        for auction_id, rows in by_auction.items()
        if len({row.payload_sha256 for row in rows}) > 1
    )
    unique = [sorted(rows, key=lambda row: row.queried_transaction_hash)[0] for rows in by_auction.values()]
    unique.sort(key=lambda row: row.auction_id)
    removals = [observation for summary in unique for observation in summary.removals]
    valid_removals = [observation for observation in removals if observation.valid]

    mapped_count = len(mapped_hashes)
    competition_count = len(unique)
    mapping_rate = mapped_count / attempted_transaction_count if attempted_transaction_count else 0.0
    complete_reference_count = sum(summary.complete_winner_references for summary in unique)
    complete_reference_fraction = complete_reference_count / competition_count if competition_count else 0.0
    low_count = sum(_at_or_below(observation, low_criticality_maximum) for observation in removals)
    high_count = sum(_at_or_above(observation, high_criticality_minimum) for observation in removals)
    submitted_coupled = sum(summary.submitted_coupled for summary in unique)
    eligible_coupled = sum(summary.eligible_coupled for summary in unique)

    gate_results = {
        "settlement_transaction_support": attempted_transaction_count
        >= int(gates["minimum_unique_settlement_transactions"]),
        "transaction_mapping_rate": mapping_rate >= float(gates["minimum_transaction_mapping_rate"]),
        "distinct_competition_support": competition_count >= int(gates["minimum_distinct_competitions"]),
        "complete_winner_references": complete_reference_fraction
        >= float(gates["minimum_complete_winner_reference_fraction"]),
        "exact_queried_transaction_membership": membership_failure_count == 0,
        "no_conflicting_duplicate_auction_payloads": not conflicting_auction_ids,
        "valid_winner_removal_support": len(valid_removals)
        >= int(gates["minimum_valid_winner_removals"]),
        "low_criticality_support": low_count >= int(gates["minimum_low_criticality_removals"]),
        "high_criticality_support": high_count >= int(gates["minimum_high_criticality_removals"]),
        "submitted_coupling_support": submitted_coupled
        >= int(gates["minimum_submitted_coupled_competitions"]),
        "eligible_coupling_green": eligible_coupled
        >= int(gates["minimum_eligible_coupled_competitions_for_green"]),
    }
    base_gate_names = tuple(name for name in gate_results if name != "eligible_coupling_green")
    base_pass = all(gate_results[name] for name in base_gate_names)
    if base_pass and gate_results["eligible_coupling_green"]:
        decision = "green_freeze_t1_before_any_association_test"
    elif base_pass:
        decision = "amber_constraint_evaporation_fork_original_complexity_route_stops"
    else:
        decision = "red_stop_route_no_window_chain_or_definition_rescue"

    competition_identity = [
        {"auction_id": summary.auction_id, "payload_sha256": summary.payload_sha256} for summary in unique
    ]
    return {
        "metrics": {
            "attempted_settlement_transaction_count": attempted_transaction_count,
            "mapped_settlement_transaction_count": mapped_count,
            "transaction_mapping_rate": mapping_rate,
            "membership_failure_count": membership_failure_count,
            "distinct_competition_count": competition_count,
            "complete_winner_reference_competition_count": complete_reference_count,
            "complete_winner_reference_fraction": complete_reference_fraction,
            "winner_removal_count": len(removals),
            "valid_winner_removal_count": len(valid_removals),
            "invalid_winner_removal_count": len(removals) - len(valid_removals),
            "low_criticality_removal_count": low_count,
            "high_criticality_removal_count": high_count,
            "submitted_coupled_competition_count": submitted_coupled,
            "eligible_coupled_competition_count": eligible_coupled,
            "conflicting_duplicate_auction_count": len(conflicting_auction_ids),
            "conflicting_duplicate_auction_ids": conflicting_auction_ids,
            "competition_identity_sha256": canonical_json_sha256(competition_identity),
        },
        "gates": gate_results,
        "base_support_gates_pass": base_pass,
        "scientific_decision": decision,
    }
