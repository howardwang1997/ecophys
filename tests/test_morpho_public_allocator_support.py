from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest

from ecomd.data.morpho_public_allocator_support import (
    TransactionClassification,
    canonical_identity_digest,
    canonical_log_identity,
    classify_transaction_logs,
    sanitize_rpc_log,
    summarize_chain_support,
)

ALLOCATOR = "0x" + "11" * 20
MORPHO = "0x" + "22" * 20
OTHER = "0x" + "33" * 20
WITHDRAWAL = "0x" + "41" * 32
TERMINAL = "0x" + "42" * 32
BORROW = "0x" + "43" * 32
SENDER = "0x" + "51" * 32
VAULT = "0x" + "52" * 32
OTHER_VAULT = "0x" + "53" * 32
DONOR_A = "0x" + "61" * 32
DONOR_B = "0x" + "62" * 32
TARGET = "0x" + "63" * 32
OTHER_TARGET = "0x" + "64" * 32
TX = "0x" + "71" * 32
BLOCK = "0x" + "72" * 32


def _log(index: int, address: str, topics: list[str], *, timestamp: int = 1_700_000_000) -> dict[str, Any]:
    return {
        "block_number": 100,
        "block_hash": BLOCK,
        "block_timestamp": timestamp,
        "transaction_hash": TX,
        "transaction_index": 2,
        "log_index": index,
        "contract_address": address,
        "topic0": topics[0],
        "topics": topics,
    }


def _classify(logs: list[dict[str, Any]]) -> TransactionClassification:
    return classify_transaction_logs(
        logs,
        public_allocator=ALLOCATOR,
        morpho=MORPHO,
        withdrawal_topic0=WITHDRAWAL,
        terminal_topic0=TERMINAL,
        borrow_topic0=BORROW,
    )


def test_groups_withdrawals_and_matches_only_later_target_borrow() -> None:
    result = _classify(
        [
            _log(2, ALLOCATOR, [WITHDRAWAL, SENDER, VAULT, DONOR_A]),
            _log(3, ALLOCATOR, [WITHDRAWAL, SENDER, VAULT, DONOR_B]),
            _log(8, ALLOCATOR, [TERMINAL, SENDER, VAULT, TARGET]),
            _log(9, MORPHO, [BORROW, OTHER_TARGET, SENDER, VAULT]),
            _log(10, MORPHO, [BORROW, TARGET, SENDER, VAULT]),
        ]
    )

    assert result.sequence_units == 1
    assert result.classified_sequences == 1
    assert result.unclassified_sequences == 0
    assert result.is_candidate is True
    assert result.groups[0].donor_market_topics == (DONOR_A, DONOR_B)
    assert result.groups[0].matched_borrow_log_indices == (10,)


def test_terminal_without_matching_borrow_is_classified_control() -> None:
    result = _classify(
        [
            _log(2, ALLOCATOR, [WITHDRAWAL, SENDER, VAULT, DONOR_A]),
            _log(8, ALLOCATOR, [TERMINAL, SENDER, VAULT, TARGET]),
            _log(9, MORPHO, [BORROW, OTHER_TARGET, SENDER, VAULT]),
        ]
    )

    assert result.classified_sequences == 1
    assert result.is_candidate is False
    assert result.issues == ()


def test_unrelated_logs_with_other_topic_arity_are_ignored() -> None:
    result = _classify(
        [
            _log(1, OTHER, ["0x" + "01" * 32]),
            _log(2, ALLOCATOR, [WITHDRAWAL, SENDER, VAULT, DONOR_A]),
            _log(4, OTHER, ["0x" + "02" * 32, SENDER, VAULT]),
            _log(8, ALLOCATOR, [TERMINAL, SENDER, VAULT, TARGET]),
            _log(10, MORPHO, [BORROW, TARGET, SENDER, VAULT]),
        ]
    )

    assert result.is_candidate is True
    assert result.classified_sequences == 1


@pytest.mark.parametrize(
    "logs, issue",
    [
        ([_log(8, ALLOCATOR, [TERMINAL, SENDER, VAULT, TARGET])], "terminal_without_withdrawal"),
        ([_log(2, ALLOCATOR, [WITHDRAWAL, SENDER, VAULT, DONOR_A])], "withdrawals_without_terminal"),
        (
            [
                _log(2, ALLOCATOR, [WITHDRAWAL, SENDER, OTHER_VAULT, DONOR_A]),
                _log(8, ALLOCATOR, [TERMINAL, SENDER, VAULT, TARGET]),
            ],
            "sender_or_vault_mismatch",
        ),
    ],
)
def test_unclassified_sequences_are_fail_visible(logs: list[dict[str, Any]], issue: str) -> None:
    result = _classify(logs)
    assert result.sequence_units == 1
    assert result.classified_sequences == 0
    assert result.unclassified_sequences == 1
    assert result.issues[0].startswith(issue)


def test_chain_summary_uses_transactions_vaults_edges_and_dates() -> None:
    first = int(datetime(2025, 1, 1, tzinfo=UTC).timestamp())
    second = int(datetime(2025, 4, 2, tzinfo=UTC).timestamp())
    one = _classify(
        [
            _log(2, ALLOCATOR, [WITHDRAWAL, SENDER, VAULT, DONOR_A], timestamp=first),
            _log(8, ALLOCATOR, [TERMINAL, SENDER, VAULT, TARGET], timestamp=first),
            _log(10, MORPHO, [BORROW, TARGET, SENDER, VAULT], timestamp=first),
        ]
    )
    two_logs = [
        {**_log(2, ALLOCATOR, [WITHDRAWAL, SENDER, VAULT, DONOR_B], timestamp=second)},
        {**_log(8, ALLOCATOR, [TERMINAL, SENDER, VAULT, TARGET], timestamp=second)},
        {**_log(10, MORPHO, [BORROW, TARGET, SENDER, VAULT], timestamp=second)},
    ]
    for log in two_logs:
        log["transaction_hash"] = "0x" + "73" * 32
    two = _classify(two_logs)

    support = summarize_chain_support([one, two])
    summary = support.summary()
    assert summary["candidate_transaction_count"] == 2
    assert summary["distinct_vault_count"] == 1
    assert summary["distinct_directed_edge_count"] == 2
    assert summary["active_utc_date_count"] == 2
    assert summary["active_span_days"] == pytest.approx(91.0)
    assert summary["classification_rate"] == 1.0


def test_rpc_sanitizer_ignores_data_and_identity_hash_is_order_invariant() -> None:
    raw = {
        "blockNumber": "0x64",
        "blockHash": BLOCK,
        "transactionHash": TX,
        "transactionIndex": "0x2",
        "logIndex": "0x3",
        "address": ALLOCATOR,
        "topics": [TERMINAL, SENDER, VAULT, TARGET],
        "data": "0x" + "ff" * 32,
    }
    sanitized = sanitize_rpc_log(raw, block_timestamp=1234)
    assert "data" not in sanitized
    identity = canonical_log_identity(sanitized)
    assert canonical_identity_digest([identity, identity]) == canonical_identity_digest([identity])


def test_rpc_sanitizer_allows_unrelated_anonymous_log() -> None:
    raw = {
        "blockNumber": "0x64",
        "blockHash": BLOCK,
        "transactionHash": TX,
        "transactionIndex": "0x2",
        "logIndex": "0x3",
        "address": OTHER,
        "topics": [],
        "data": "0x",
    }
    sanitized = sanitize_rpc_log(raw, block_timestamp=1234)
    assert sanitized["topics"] == []
    assert sanitized["topic0"] is None
