"""Frozen event schema for the controlled-market truth asset (A-2 deliverable D-2.1).

Arm-invariant grammar: both allocation arms (FIFO, uniform random within the equal-price tie
set) emit exactly these record types and fields; only allocation identities may differ across
arms on the same request tape. All identifiers are immutable; every accepted action carries
three timestamps (client decision, server receipt, matching) and the pre/post full-book state
hash is computable after every accepted action.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from enum import StrEnum


class Side(StrEnum):
    BID = "B"
    ASK = "S"


class AllocationRule(StrEnum):
    FIFO = "fifo"
    RANDOM_WITHIN_TIE = "random_within_tie"


class RejectionReason(StrEnum):
    """Reason-coded rejections; no free-text rejection channels exist in the grammar."""

    MALFORMED_REQUEST = "malformed_request"
    DUPLICATE_CLIENT_ID = "duplicate_client_id"
    PRICE_OUT_OF_BANDS = "price_out_of_bands"
    NEGATIVE_OR_ZERO_QUANTITY = "negative_or_zero_quantity"
    SELF_TRADE_PREVENTED = "self_trade_prevented"
    INSUFFICIENT_INVENTORY = "insufficient_inventory"


class CancelRejectionReason(StrEnum):
    UNKNOWN_ORDER = "unknown_order"
    ALREADY_FILLED = "already_filled"
    CANCEL_TOO_LATE = "cancel_too_late"


class EventType(StrEnum):
    SESSION_START = "session_start"
    ORDER_REQUEST = "order_request"
    ORDER_ACCEPTED = "order_accepted"
    ORDER_REJECTED = "order_rejected"
    CANCEL_REQUEST = "cancel_request"
    ORDER_CANCELLED = "order_cancelled"
    CANCEL_REJECTED = "cancel_rejected"
    EXECUTION = "execution"
    SESSION_END = "session_end"


@dataclass(frozen=True)
class ThreeClocks:
    """Client decision, server receipt and matching timestamps (monotone integer ticks)."""

    client_ts: int
    receipt_ts: int
    match_ts: int


@dataclass(frozen=True)
class OrderRequest:
    """Aggressive or resting limit order; marketable limits cross on arrival."""

    event_id: int
    actor: str
    client_order_id: str
    side: Side
    price: int
    quantity: int
    clocks: ThreeClocks


@dataclass(frozen=True)
class CancelRequest:
    event_id: int
    actor: str
    client_order_id: str
    clocks: ThreeClocks


@dataclass(frozen=True)
class OrderAccepted:
    event_id: int
    order_id: str
    resting_quantity: int
    clocks: ThreeClocks


@dataclass(frozen=True)
class OrderRejected:
    event_id: int
    reason: RejectionReason
    clocks: ThreeClocks


@dataclass(frozen=True)
class OrderCancelled:
    event_id: int
    order_id: str
    cancelled_quantity: int
    clocks: ThreeClocks


@dataclass(frozen=True)
class CancelRejected:
    event_id: int
    reason: CancelRejectionReason
    clocks: ThreeClocks


@dataclass(frozen=True)
class Execution:
    """One fill of resting quantity; maker allocation differs across arms, grammar does not."""

    event_id: int
    execution_id: str
    aggressor_order_id: str
    maker_order_id: str
    maker_actor: str
    aggressor_actor: str
    side_of_aggressor: Side
    price: int
    quantity: int
    maker_remaining: int
    clocks: ThreeClocks


@dataclass(frozen=True)
class TapeRecord:
    """Universal envelope; payload is one of the typed events above."""

    sequence: int
    event_type: EventType
    payload: dict[str, object] = field(default_factory=dict)
    pre_state_hash: str = ""
    post_state_hash: str = ""


@dataclass(frozen=True)
class SessionPrestate:
    """Replay prestate: everything that determines future paths given the request tape."""

    session_id: str
    seed: int
    allocation_rule: AllocationRule
    initial_cash: dict[str, float]
    initial_inventory: dict[str, int]
    price_bands: tuple[int, int]
    actors: tuple[str, ...]


def state_hash(
    bids: dict[int, list[tuple[str, str, int]]],
    asks: dict[int, list[tuple[str, str, int]]],
    sequence: int,
) -> str:
    """Full-book hash: price levels with order identity, quantity (order-id, actor, qty)."""

    def levels(book: dict[int, list[tuple[str, str, int]]]) -> list[list[object]]:
        out: list[list[object]] = []
        for price in sorted(book):
            rows = [[oid, actor, qty] for oid, actor, qty in sorted(book[price])]
            out.append([price, rows])
        return out

    payload = json.dumps(
        {"sequence": sequence, "bids": levels(bids), "asks": levels(asks)},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def record_to_json(record: TapeRecord) -> str:
    return json.dumps(asdict(record), sort_keys=True, separators=(",", ":"))
