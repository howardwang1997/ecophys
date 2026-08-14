from __future__ import annotations

from ecomd.research.cow_development_audit import (
    audit_competition_payload,
    canonical_json_sha256,
    summarize_initial_sample,
)


def _payload(auction_id: int) -> dict[str, object]:
    return {
        "auctionId": auction_id,
        "auctionStartBlock": 100,
        "auctionDeadlineBlock": 105,
        "transactionHashes": ["0xabc"],
        "auction": {"orders": [{"uid": "one"}], "prices": {"0xtoken": "1"}},
        "solutions": [
            {
                "ranking": 1,
                "solverAddress": "0x0000000000000000000000000000000000000001",
                "score": "100",
                "referenceScore": None,
                "txHash": "0xabc",
                "orders": [],
                "isWinner": True,
                "filteredOut": False,
            }
        ],
    }


def test_competition_payload_audit_preserves_winners_and_nullability() -> None:
    audit = audit_competition_payload(_payload(42), requested_auction_id=42)

    assert audit["parse_ok"] is True
    assert audit["winner_count"] == 1
    assert audit["solution_count"] == 1
    assert audit["auction_start_block"] == 100


def test_competition_payload_audit_rejects_id_and_field_failures() -> None:
    payload = _payload(41)
    solutions = payload["solutions"]
    assert isinstance(solutions, list)
    solution = solutions[0]
    assert isinstance(solution, dict)
    del solution["filteredOut"]

    audit = audit_competition_payload(payload, requested_auction_id=42)

    assert audit["parse_ok"] is False
    errors = audit["errors"]
    assert isinstance(errors, list)
    assert any("does not match" in error for error in errors)
    assert any("missing fields" in error for error in errors)


def test_initial_summary_uses_exact_ledger_and_block_cutoff() -> None:
    entries = []
    for auction_id in (42, 41):
        audit = audit_competition_payload(_payload(auction_id), requested_auction_id=auction_id)
        entries.append({"auction_id": auction_id, "http_status": 200, **audit})
    summary = summarize_initial_sample(
        entries,
        expected_ids=[42, 41],
        block_timestamps={100: 1_700_000_000},
        cutoff_utc="2026-08-14T07:00:00Z",
        minimum_http_200_coverage=0.8,
        ledger_sha256="a" * 64,
        block_response_sha256="b" * 64,
    )

    assert summary["pass"] is True
    assert summary["http_200_coverage"] == 1.0
    assert summary["aggregate_diagnostics"] == {
        "solution_count": 2,
        "winner_count": 2,
        "filtered_solution_count": 0,
        "null_solution_tx_count": 0,
        "zero_or_missing_solver_address_count": 0,
        "auction_order_count": 2,
    }
    assert canonical_json_sha256([42, 41]) == canonical_json_sha256([42, 41])


def test_initial_summary_retains_a_missing_request_without_replacement() -> None:
    audit = audit_competition_payload(_payload(42), requested_auction_id=42)
    entries = [
        {"auction_id": 42, "http_status": 200, **audit},
        {"auction_id": 41, "http_status": 404, "parse_ok": False},
    ]
    summary = summarize_initial_sample(
        entries,
        expected_ids=[42, 41],
        block_timestamps={100: 1_700_000_000},
        cutoff_utc="2026-08-14T07:00:00Z",
        minimum_http_200_coverage=0.5,
        ledger_sha256="a" * 64,
        block_response_sha256="b" * 64,
    )

    assert summary["pass"] is True
    assert summary["http_status_counts"] == {"200": 1, "404": 1}
