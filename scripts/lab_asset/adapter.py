"""Message-level adapter binding for the platform fork (A-2 deliverable D-2b).

Defines the client<->engine message protocol that any hardened platform fork (for example
an oTree-based implementation seeded from the audited domidt/CDA layout) must speak. The
reference engine consumes typed requests; the adapter translates plain client message
dicts into typed requests and tape records into client-visible event payloads.

The protocol schema is arm-invariant. Random-unit allocation may emit more unit execution
records than FIFO, so cross-arm invariance is checked at completed-request boundaries rather
than by requiring record-by-record equality.
"""

from __future__ import annotations

from lab_asset.schema import (
    CancelRequest,
    EventType,
    LatencyChoice,
    OrderRequest,
    Side,
    TapeRecord,
    ThreeClocks,
)

ClientNewMessage = dict[str, object]
ClientCancelMessage = dict[str, object]
ClientMessage = ClientNewMessage | ClientCancelMessage

__all__ = [
    "AdapterError",
    "ClientMessage",
    "client_view",
    "to_request",
]


class AdapterError(ValueError):
    """Raised on malformed client messages; mapped to reason-coded rejections upstream."""


def to_request(
    message: ClientMessage,
    event_id: int,
    client_ts: int,
    receipt_ts: int,
    match_ts: int,
) -> OrderRequest | CancelRequest | LatencyChoice:
    """Translate a client message dict into a typed engine request.

    New-order message: {"type": "new", "actor", "client_order_id", "round_id",
                        "side": "B"|"S", "price", "quantity"}
    Cancel message:    {"type": "cancel", "actor", "order_id", "round_id"}
    Latency message:   {"type": "latency", "actor", "round_id", "investment"}
    """
    if not isinstance(message, dict):
        raise AdapterError("message must be a dict")
    kind = message.get("type")
    actor = message.get("actor")
    if not isinstance(actor, str) or not actor:
        raise AdapterError("actor must be a non-empty string")
    round_id = message.get("round_id", 0)
    if not isinstance(round_id, int) or round_id < 0:
        raise AdapterError("round_id must be a nonnegative integer")
    clocks = ThreeClocks(
        client_ts=client_ts, receipt_ts=receipt_ts, match_ts=match_ts
    )
    if kind == "new":
        client_order_id = message.get("client_order_id")
        side_raw = message.get("side")
        price = message.get("price")
        quantity = message.get("quantity")
        if not isinstance(client_order_id, str) or not client_order_id:
            raise AdapterError("client_order_id must be a non-empty string")
        if side_raw not in ("B", "S"):
            raise AdapterError("side must be 'B' or 'S'")
        if not isinstance(price, int) or not isinstance(quantity, int):
            raise AdapterError("price and quantity must be integers")
        return OrderRequest(
            event_id=event_id,
            actor=actor,
            client_order_id=client_order_id,
            side=Side(side_raw),
            price=price,
            quantity=quantity,
            clocks=clocks,
            round_id=round_id,
        )
    if kind == "cancel":
        order_id = message.get("order_id")
        if not isinstance(order_id, str) or not order_id:
            raise AdapterError("order_id must be a non-empty string")
        return CancelRequest(
            event_id=event_id,
            actor=actor,
            order_id=order_id,
            clocks=clocks,
            round_id=round_id,
        )
    if kind == "latency":
        investment = message.get("investment")
        if not isinstance(investment, int):
            raise AdapterError("investment must be an integer")
        return LatencyChoice(
            event_id=event_id,
            actor=actor,
            round_id=round_id,
            investment=investment,
            clocks=clocks,
        )
    raise AdapterError("type must be 'new', 'cancel', or 'latency'")


def client_view(record: TapeRecord) -> dict[str, object]:
    """Map a tape record to the client-visible payload of the public event stream.

    Everything in the tape is public in the released asset (post-release), so the view is
    the record itself plus the event type; kept explicit so the fork's wire format has one
    canonical definition.
    """
    view: dict[str, object] = {
        "sequence": record.sequence,
        "event_type": record.event_type.value,
        "pre_state_hash": record.pre_state_hash,
        "post_state_hash": record.post_state_hash,
        "pre_aggregate_state_hash": record.pre_aggregate_state_hash,
        "post_aggregate_state_hash": record.post_aggregate_state_hash,
    }
    if record.event_type in (EventType.EXECUTION,):
        view["allocation"] = "draw_recorded" if "allocation_draw" in record.payload else "fifo"
    view["payload"] = record.payload
    return view
