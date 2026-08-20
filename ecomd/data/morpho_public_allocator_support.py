"""Outcome-blind event identity logic for Morpho Public Allocator support audits."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, TypeAlias

LogIdentity: TypeAlias = tuple[str, str, int, str, tuple[str, ...]]
DirectedEdge: TypeAlias = tuple[str, str]


def _hex(value: Any, *, size_bytes: int, label: str) -> str:
    text = str(value).lower()
    if len(text) != 2 + 2 * size_bytes or not text.startswith("0x"):
        raise ValueError(f"invalid {label}: {value}")
    try:
        bytes.fromhex(text[2:])
    except ValueError as error:
        raise ValueError(f"invalid {label}: {value}") from error
    return text


def _quantity(value: Any, *, label: str) -> int:
    text = str(value)
    if not text.startswith("0x"):
        raise ValueError(f"invalid {label}: {value}")
    try:
        number = int(text, 16)
    except ValueError as error:
        raise ValueError(f"invalid {label}: {value}") from error
    if number < 0:
        raise ValueError(f"invalid {label}: {value}")
    return number


def sanitize_rpc_log(raw: Mapping[str, Any], *, block_timestamp: int | None = None) -> dict[str, Any]:
    """Retain only identity fields from an EVM RPC log and never access its data word."""
    if raw.get("removed") is True:
        raise ValueError("removed RPC log cannot enter a finalized identity audit")
    raw_topics = raw.get("topics")
    if not isinstance(raw_topics, Sequence) or isinstance(raw_topics, (str, bytes)):
        raise ValueError("RPC log topics must be a sequence")
    topics = [_hex(value, size_bytes=32, label="topic") for value in raw_topics]
    event: dict[str, Any] = {
        "block_number": _quantity(raw.get("blockNumber"), label="block number"),
        "block_hash": _hex(raw.get("blockHash"), size_bytes=32, label="block hash"),
        "transaction_hash": _hex(raw.get("transactionHash"), size_bytes=32, label="transaction hash"),
        "transaction_index": _quantity(raw.get("transactionIndex"), label="transaction index"),
        "log_index": _quantity(raw.get("logIndex"), label="log index"),
        "contract_address": _hex(raw.get("address"), size_bytes=20, label="contract address"),
        "topics": topics,
    }
    event["topic0"] = topics[0] if topics else None
    if block_timestamp is not None:
        if block_timestamp < 0:
            raise ValueError("block timestamp cannot be negative")
        event["block_timestamp"] = block_timestamp
    return event


def canonical_log_identity(log: Mapping[str, Any]) -> LogIdentity:
    """Return a complete topic-level canonical identity for one sanitized log."""
    topics = log.get("topics")
    if not isinstance(topics, Sequence) or isinstance(topics, (str, bytes)) or not topics:
        raise ValueError("sanitized log has no full topic sequence")
    normalized_topics = tuple(_hex(value, size_bytes=32, label="topic") for value in topics)
    log_index = int(log.get("log_index", -1))
    if log_index < 0:
        raise ValueError("sanitized log has an invalid log index")
    return (
        _hex(log.get("block_hash"), size_bytes=32, label="block hash"),
        _hex(log.get("transaction_hash"), size_bytes=32, label="transaction hash"),
        log_index,
        _hex(log.get("contract_address"), size_bytes=20, label="contract address"),
        normalized_topics,
    )


def canonical_identity_digest(identities: Iterable[LogIdentity]) -> str:
    """Hash a sorted, duplicate-free canonical identity set."""
    normalized = sorted(set(identities))
    payload = [[a, tx, index, contract, list(topics)] for a, tx, index, contract, topics in normalized]
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(encoded).hexdigest()


def canonical_string_digest(values: Iterable[str | DirectedEdge]) -> str:
    """Hash a sorted set of opaque identities without exposing its members."""
    encoded_values: list[str | list[str]] = []
    for value in set(values):
        encoded_values.append(list(value) if isinstance(value, tuple) else value)
    encoded_values.sort(key=lambda value: json.dumps(value, separators=(",", ":")))
    encoded = json.dumps(encoded_values, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class AllocationGroup:
    """One source-exact Public Allocator terminal and its preceding withdrawals."""

    sender_topic: str
    vault_topic: str
    target_market_topic: str
    donor_market_topics: tuple[str, ...]
    terminal_log_index: int
    matched_borrow_log_indices: tuple[int, ...]

    @property
    def target_matched(self) -> bool:
        return bool(self.matched_borrow_log_indices)


@dataclass(frozen=True)
class TransactionClassification:
    """Outcome-blind classification of all relevant logs in one transaction receipt."""

    transaction_hash: str
    block_timestamp: int
    sequence_units: int
    classified_sequences: int
    groups: tuple[AllocationGroup, ...]
    issues: tuple[str, ...]

    @property
    def unclassified_sequences(self) -> int:
        return self.sequence_units - self.classified_sequences

    @property
    def is_candidate(self) -> bool:
        return any(group.target_matched for group in self.groups)


def _topics(log: Mapping[str, Any], *, expected: int) -> tuple[str, ...]:
    raw = log.get("topics")
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)) or len(raw) != expected:
        raise ValueError(f"event must have exactly {expected} topics")
    return tuple(_hex(value, size_bytes=32, label="topic") for value in raw)


def _topic0(log: Mapping[str, Any]) -> str:
    raw = log.get("topics")
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)) or not raw:
        raise ValueError("event must have at least one topic")
    return _hex(raw[0], size_bytes=32, label="topic0")


def classify_transaction_logs(
    logs: Sequence[Mapping[str, Any]],
    *,
    public_allocator: str,
    morpho: str,
    withdrawal_topic0: str,
    terminal_topic0: str,
    borrow_topic0: str,
) -> TransactionClassification:
    """Group Public Allocator calls and find later target-matched Morpho borrows."""
    if not logs:
        raise ValueError("transaction receipt has no logs")
    allocator = _hex(public_allocator, size_bytes=20, label="Public Allocator address")
    morpho_address = _hex(morpho, size_bytes=20, label="Morpho address")
    withdrawal_topic = _hex(withdrawal_topic0, size_bytes=32, label="withdrawal topic")
    terminal_topic = _hex(terminal_topic0, size_bytes=32, label="terminal topic")
    borrow_topic = _hex(borrow_topic0, size_bytes=32, label="borrow topic")

    ordered = sorted(logs, key=lambda log: int(log.get("log_index", -1)))
    transaction_hashes = {
        _hex(log.get("transaction_hash"), size_bytes=32, label="transaction hash") for log in ordered
    }
    timestamps = {int(log.get("block_timestamp", -1)) for log in ordered}
    if len(transaction_hashes) != 1 or len(timestamps) != 1 or min(timestamps) < 0:
        raise ValueError("receipt logs must share one transaction hash and nonnegative timestamp")
    transaction_hash = next(iter(transaction_hashes))
    block_timestamp = next(iter(timestamps))

    pending: list[tuple[str, str, str]] = []
    provisional: list[tuple[str, str, str, tuple[str, ...], int]] = []
    issues: list[str] = []
    sequence_units = 0
    for log in ordered:
        address = _hex(log.get("contract_address"), size_bytes=20, label="contract address")
        if address != allocator:
            continue
        topic0 = _topic0(log)
        if topic0 == withdrawal_topic:
            topics = _topics(log, expected=4)
            pending.append((topics[1], topics[2], topics[3]))
            continue
        if topic0 != terminal_topic:
            continue
        topics = _topics(log, expected=4)
        sequence_units += 1
        if not pending:
            issues.append(f"terminal_without_withdrawal:{int(log['log_index'])}")
            continue
        sender, vault, target = topics[1], topics[2], topics[3]
        if any(item_sender != sender or item_vault != vault for item_sender, item_vault, _ in pending):
            issues.append(f"sender_or_vault_mismatch:{int(log['log_index'])}")
            pending.clear()
            continue
        donors = tuple(item_donor for _, _, item_donor in pending)
        provisional.append((sender, vault, target, donors, int(log["log_index"])))
        pending.clear()

    if pending:
        sequence_units += 1
        issues.append("withdrawals_without_terminal")

    borrow_logs: list[tuple[int, str]] = []
    for log in ordered:
        address = _hex(log.get("contract_address"), size_bytes=20, label="contract address")
        if address != morpho_address or _topic0(log) != borrow_topic:
            continue
        topics = _topics(log, expected=4)
        borrow_logs.append((int(log["log_index"]), topics[1]))

    groups = tuple(
        AllocationGroup(
            sender_topic=sender,
            vault_topic=vault,
            target_market_topic=target,
            donor_market_topics=donors,
            terminal_log_index=terminal_index,
            matched_borrow_log_indices=tuple(
                index for index, market in borrow_logs if index > terminal_index and market == target
            ),
        )
        for sender, vault, target, donors, terminal_index in provisional
    )
    return TransactionClassification(
        transaction_hash=transaction_hash,
        block_timestamp=block_timestamp,
        sequence_units=sequence_units,
        classified_sequences=len(groups),
        groups=groups,
        issues=tuple(issues),
    )


@dataclass(frozen=True)
class ChainSupport:
    """Aggregate identity support without exposing raw transactions or graph labels."""

    public_allocator_transactions: frozenset[str]
    candidate_transactions: frozenset[str]
    vaults: frozenset[str]
    edges: frozenset[DirectedEdge]
    active_dates: frozenset[str]
    first_timestamp: int | None
    last_timestamp: int | None
    sequence_units: int
    classified_sequences: int
    matched_groups: int

    @property
    def classification_rate(self) -> float:
        return self.classified_sequences / self.sequence_units if self.sequence_units else 0.0

    @property
    def active_span_days(self) -> float:
        if self.first_timestamp is None or self.last_timestamp is None:
            return 0.0
        return (self.last_timestamp - self.first_timestamp) / 86_400.0

    def summary(self) -> dict[str, Any]:
        """Return aggregate counts and digests only."""
        return {
            "public_allocator_transaction_count": len(self.public_allocator_transactions),
            "candidate_transaction_count": len(self.candidate_transactions),
            "candidate_transaction_sha256": canonical_string_digest(self.candidate_transactions),
            "distinct_vault_count": len(self.vaults),
            "vault_identity_sha256": canonical_string_digest(self.vaults),
            "distinct_directed_edge_count": len(self.edges),
            "directed_edge_identity_sha256": canonical_string_digest(self.edges),
            "active_utc_date_count": len(self.active_dates),
            "first_candidate_utc": (
                None
                if self.first_timestamp is None
                else datetime.fromtimestamp(self.first_timestamp, UTC).isoformat()
            ),
            "last_candidate_utc": (
                None
                if self.last_timestamp is None
                else datetime.fromtimestamp(self.last_timestamp, UTC).isoformat()
            ),
            "active_span_days": self.active_span_days,
            "sequence_units": self.sequence_units,
            "classified_sequences": self.classified_sequences,
            "classification_rate": self.classification_rate,
            "target_matched_group_count": self.matched_groups,
        }


def summarize_chain_support(
    classifications: Sequence[TransactionClassification],
) -> ChainSupport:
    """Aggregate classifications into the frozen D0 statistical units."""
    transactions = frozenset(item.transaction_hash for item in classifications)
    candidates = frozenset(item.transaction_hash for item in classifications if item.is_candidate)
    vaults: set[str] = set()
    edges: set[DirectedEdge] = set()
    timestamps: list[int] = []
    matched_groups = 0
    for item in classifications:
        if item.is_candidate:
            timestamps.append(item.block_timestamp)
        for group in item.groups:
            if not group.target_matched:
                continue
            matched_groups += 1
            vaults.add(group.vault_topic)
            edges.update((donor, group.target_market_topic) for donor in group.donor_market_topics)
    dates = frozenset(datetime.fromtimestamp(value, UTC).date().isoformat() for value in timestamps)
    return ChainSupport(
        public_allocator_transactions=transactions,
        candidate_transactions=candidates,
        vaults=frozenset(vaults),
        edges=frozenset(edges),
        active_dates=dates,
        first_timestamp=min(timestamps) if timestamps else None,
        last_timestamp=max(timestamps) if timestamps else None,
        sequence_units=sum(item.sequence_units for item in classifications),
        classified_sequences=sum(item.classified_sequences for item in classifications),
        matched_groups=matched_groups,
    )
