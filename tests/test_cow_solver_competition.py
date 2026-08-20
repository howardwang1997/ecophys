from __future__ import annotations

from dataclasses import replace
from typing import Any

import pytest

from ecomd.data.cow_solver_competition import (
    CompetitionSummary,
    RemovalObservation,
    evaluate_t0_support,
    parse_blockscout_settlement_events,
    semantic_competition_sha256,
    summarize_competition,
)

CONTRACT = "0x" + "90" * 20
TOPIC0 = "0x" + "40" * 32
TX = "0x" + "71" * 32
OTHER_TX = "0x" + "72" * 32
SOLVER_A = "0x" + "a1" * 20
SOLVER_B = "0x" + "b2" * 20
SOLVER_C = "0x" + "c3" * 20
ORDER_A = "0x" + "11" * 56
ORDER_B = "0x" + "22" * 56

REQUIRED_COMPETITION = (
    "auctionId",
    "auctionStartBlock",
    "auctionDeadlineBlock",
    "transactionHashes",
    "referenceScores",
    "auction",
    "solutions",
)
REQUIRED_SOLUTION = (
    "ranking",
    "solverAddress",
    "score",
    "referenceScore",
    "txHash",
    "orders",
    "isWinner",
    "filteredOut",
)
GATES = {
    "minimum_unique_settlement_transactions": 200,
    "minimum_transaction_mapping_rate": 0.98,
    "minimum_distinct_competitions": 180,
    "minimum_complete_winner_reference_fraction": 0.90,
    "minimum_valid_winner_removals": 100,
    "minimum_low_criticality_removals": 20,
    "minimum_high_criticality_removals": 20,
    "minimum_submitted_coupled_competitions": 30,
    "minimum_eligible_coupled_competitions_for_green": 10,
}


def _blockscout_payload() -> dict[str, Any]:
    return {
        "status": "1",
        "message": "OK",
        "result": [
            {
                "address": CONTRACT,
                "blockNumber": "0x64",
                "logIndex": "0x3",
                "transactionHash": TX,
                "topics": [TOPIC0, "0x" + "00" * 32],
            },
            {
                "address": CONTRACT.upper().replace("0X", "0x"),
                "blockNumber": "0x63",
                "logIndex": "0x2",
                "transactionHash": OTHER_TX,
                "topics": [TOPIC0],
            },
        ],
    }


def _solution(
    solver: str,
    score: int,
    orders: list[str],
    *,
    winner: bool,
    filtered: bool,
) -> dict[str, Any]:
    return {
        "ranking": 1,
        "solverAddress": solver,
        "score": str(score),
        "referenceScore": None,
        "txHash": TX if winner else None,
        "orders": [{"id": order} for order in orders],
        "isWinner": winner,
        "filteredOut": filtered,
    }


def _competition_payload(*, coupled_filtered: bool = False) -> dict[str, Any]:
    return {
        "auctionId": 123,
        "auctionStartBlock": 99,
        "auctionDeadlineBlock": 102,
        "transactionHashes": [TX],
        "referenceScores": {SOLVER_A: "70", SOLVER_B: "80"},
        "auction": {"orders": [ORDER_A, ORDER_B], "prices": {}},
        "solutions": [
            _solution(SOLVER_A, 60, [ORDER_A], winner=True, filtered=False),
            _solution(SOLVER_B, 40, [ORDER_B], winner=True, filtered=False),
            _solution(
                SOLVER_C,
                95,
                [ORDER_A, ORDER_B],
                winner=False,
                filtered=coupled_filtered,
            ),
        ],
    }


def _summarize(payload: dict[str, Any] | None = None) -> CompetitionSummary:
    return summarize_competition(
        _competition_payload() if payload is None else payload,
        queried_transaction_hash=TX,
        required_competition_fields=REQUIRED_COMPETITION,
        required_solution_fields=REQUIRED_SOLUTION,
        minimum_orders_for_multi_order_solution=2,
    )


def test_parses_and_sorts_exact_settlement_events() -> None:
    events = parse_blockscout_settlement_events(
        _blockscout_payload(),
        expected_contract=CONTRACT,
        expected_topic0=TOPIC0,
        from_block=99,
        to_block=100,
    )
    assert [event.block_number for event in events] == [99, 100]
    assert [event.transaction_hash for event in events] == [OTHER_TX, TX]


def test_rejects_event_outside_frozen_universe() -> None:
    payload = _blockscout_payload()
    payload["result"][0]["address"] = "0x" + "ff" * 20
    with pytest.raises(ValueError, match="escaped the frozen contract/topic filter"):
        parse_blockscout_settlement_events(
            payload,
            expected_contract=CONTRACT,
            expected_topic0=TOPIC0,
            from_block=99,
            to_block=100,
        )


def test_summarizes_official_removals_and_coupling() -> None:
    summary = _summarize()
    assert summary.auction_id == 123
    assert summary.solution_count == 3
    assert summary.distinct_solver_count == 3
    assert summary.winner_solution_count == 2
    assert summary.submitted_multi_order_solution_count == 1
    assert summary.eligible_multi_order_solution_count == 1
    assert summary.submitted_coupled is True
    assert summary.eligible_coupled is True
    assert summary.complete_winner_references is True
    assert [observation.total_winning_score for observation in summary.removals] == [100, 100]
    assert [observation.score_loss for observation in summary.removals] == [30, 20]
    assert [observation.criticality for observation in summary.removals] == pytest.approx([0.3, 0.2])


def test_filtering_can_remove_eligible_coupling_without_erasing_submission() -> None:
    summary = _summarize(_competition_payload(coupled_filtered=True))
    assert summary.submitted_coupled is True
    assert summary.eligible_coupled is False
    assert summary.submitted_multi_order_solution_count == 1
    assert summary.eligible_multi_order_solution_count == 0


def test_missing_query_membership_is_fatal() -> None:
    payload = _competition_payload()
    payload["transactionHashes"] = [OTHER_TX]
    with pytest.raises(ValueError, match="queried transaction hash is absent"):
        _summarize(payload)


def test_semantic_hash_ignores_transaction_and_solution_array_order() -> None:
    left = _competition_payload()
    left["transactionHashes"] = [TX, OTHER_TX]
    right = _competition_payload()
    right["transactionHashes"] = [OTHER_TX, TX]
    right["solutions"] = list(reversed(right["solutions"]))
    assert semantic_competition_sha256(left) == semantic_competition_sha256(right)

    right["solutions"][0]["score"] = "999"
    assert semantic_competition_sha256(left) != semantic_competition_sha256(right)


def test_reference_above_winning_total_is_invalid_not_clipped() -> None:
    payload = _competition_payload()
    payload["referenceScores"][SOLVER_A] = "101"
    summary = _summarize(payload)
    first = summary.removals[0]
    assert first.valid is False
    assert first.score_loss == -1
    assert first.criticality is None


def _support_rows(*, eligible_coupled: int, submitted_coupled: int) -> list[CompetitionSummary]:
    base = _summarize()
    rows: list[CompetitionSummary] = []
    for index in range(200):
        transaction_hash = "0x" + f"{index + 1:064x}"
        is_submitted = index < submitted_coupled
        is_eligible = index < eligible_coupled
        if index < 30:
            removal = RemovalObservation(
                solver_address=SOLVER_A,
                total_winning_score=100_000,
                reference_score=99_950,
                score_loss=50,
                valid=True,
            )
        else:
            removal = RemovalObservation(
                solver_address=SOLVER_A,
                total_winning_score=100_000,
                reference_score=90_000,
                score_loss=10_000,
                valid=True,
            )
        rows.append(
            replace(
                base,
                auction_id=1_000 + index,
                queried_transaction_hash=transaction_hash,
                transaction_hashes=(transaction_hash,),
                payload_sha256=f"{index + 1:064x}",
                semantic_payload_sha256=f"{index + 1:064x}",
                submitted_coupled=is_submitted,
                eligible_coupled=is_eligible,
                removals=(removal,),
            )
        )
    return rows


def test_evaluator_applies_green_amber_and_red_forks() -> None:
    green = evaluate_t0_support(
        _support_rows(eligible_coupled=12, submitted_coupled=40),
        attempted_transaction_count=200,
        membership_failure_count=0,
        gates=GATES,
        low_criticality_maximum=0.001,
        high_criticality_minimum=0.01,
    )
    assert green["base_support_gates_pass"] is True
    assert green["gates"]["eligible_coupling_green"] is True
    assert green["scientific_decision"] == "green_freeze_t1_before_any_association_test"

    amber = evaluate_t0_support(
        _support_rows(eligible_coupled=0, submitted_coupled=40),
        attempted_transaction_count=200,
        membership_failure_count=0,
        gates=GATES,
        low_criticality_maximum=0.001,
        high_criticality_minimum=0.01,
    )
    assert amber["base_support_gates_pass"] is True
    assert amber["scientific_decision"].startswith("amber_constraint_evaporation")

    red = evaluate_t0_support(
        _support_rows(eligible_coupled=0, submitted_coupled=0),
        attempted_transaction_count=200,
        membership_failure_count=0,
        gates=GATES,
        low_criticality_maximum=0.001,
        high_criticality_minimum=0.01,
    )
    assert red["base_support_gates_pass"] is False
    assert red["scientific_decision"].startswith("red_stop_route")


def test_conflicting_duplicate_auction_payload_is_fail_visible() -> None:
    base = _summarize()
    duplicate = replace(
        base,
        queried_transaction_hash=OTHER_TX,
        transaction_hashes=(TX, OTHER_TX),
        payload_sha256="f" * 64,
        semantic_payload_sha256="f" * 64,
    )
    result = evaluate_t0_support(
        [base, duplicate],
        attempted_transaction_count=2,
        membership_failure_count=0,
        gates={
            **GATES,
            "minimum_unique_settlement_transactions": 1,
            "minimum_transaction_mapping_rate": 0.0,
            "minimum_distinct_competitions": 1,
            "minimum_complete_winner_reference_fraction": 0.0,
            "minimum_valid_winner_removals": 1,
            "minimum_low_criticality_removals": 0,
            "minimum_high_criticality_removals": 0,
            "minimum_submitted_coupled_competitions": 1,
            "minimum_eligible_coupled_competitions_for_green": 1,
        },
        low_criticality_maximum=0.001,
        high_criticality_minimum=0.01,
    )
    assert result["metrics"]["conflicting_duplicate_auction_count"] == 1
    assert result["gates"]["no_conflicting_duplicate_auction_payloads"] is False
    assert result["scientific_decision"].startswith("red_stop_route")
