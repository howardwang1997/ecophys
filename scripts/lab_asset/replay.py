"""Deterministic replay validator (A-2 deliverable D-2.3).

Re-executes a recorded tape's request stream from the session prestate and verifies that
every record's event type, payload and post-action full-book state hash are reproduced
exactly. Any mismatch voids the session per the capability-build plan, Part 4.
"""

from __future__ import annotations

from dataclasses import dataclass

from lab_asset.matching import ReferenceEngine
from lab_asset.schema import (
    CancelRequest,
    EventType,
    LatencyChoice,
    OrderRequest,
    ReplaceRequest,
    SessionPrestate,
    Side,
    TapeRecord,
    ThreeClocks,
)


@dataclass(frozen=True)
class ReplayReport:
    ok: bool
    events_replayed: int
    first_mismatch_sequence: int | None

    def __str__(self) -> str:
        if self.ok:
            return f"replay OK: {self.events_replayed} records, tape reproduced exactly"
        return f"replay FAILED at sequence {self.first_mismatch_sequence}"


def _subdict(payload: dict[str, object], key: str) -> dict[str, object]:
    value = payload[key]
    assert isinstance(value, dict)
    return value


def _as_int(value: object) -> int:
    assert isinstance(value, int)
    return value


def _as_str(value: object) -> str:
    assert isinstance(value, str)
    return value


def _clocks(payload: dict[str, object]) -> ThreeClocks:
    raw = _subdict(payload, "clocks")
    return ThreeClocks(
        client_ts=_as_int(raw["client_ts"]),
        receipt_ts=_as_int(raw["receipt_ts"]),
        match_ts=_as_int(raw["match_ts"]),
    )


def replay(prestate: SessionPrestate, tape: list[TapeRecord]) -> ReplayReport:
    """Re-execute the request stream and compare the regenerated tape record-by-record.

    A faithful replay must match event types, payloads and post-state hashes exactly:
    the engine is deterministic given (prestate, request stream), and the prestate pins
    the allocation arm and seed.
    """
    engine = ReferenceEngine(prestate)
    replayed = 0
    for record in tape:
        if record.event_type == EventType.ORDER_REQUEST:
            payload = record.payload
            engine.submit(
                OrderRequest(
                    event_id=_as_int(payload["event_id"]),
                    actor=_as_str(payload["actor"]),
                    client_order_id=_as_str(payload["client_order_id"]),
                    side=Side(_as_str(payload["side"])),
                    price=_as_int(payload["price"]),
                    quantity=_as_int(payload["quantity"]),
                    clocks=_clocks(payload),
                    round_id=_as_int(payload["round_id"]),
                )
            )
        elif record.event_type == EventType.CANCEL_REQUEST:
            payload = record.payload
            engine.cancel(
                CancelRequest(
                    event_id=_as_int(payload["event_id"]),
                    actor=_as_str(payload["actor"]),
                    order_id=_as_str(payload["order_id"]),
                    clocks=_clocks(payload),
                    round_id=_as_int(payload["round_id"]),
                )
            )
        elif record.event_type == EventType.REPLACE_REQUEST:
            payload = record.payload
            engine.replace(
                ReplaceRequest(
                    event_id=_as_int(payload["event_id"]),
                    actor=_as_str(payload["actor"]),
                    replaces_order_id=_as_str(payload["replaces_order_id"]),
                    client_order_id=_as_str(payload["client_order_id"]),
                    side=Side(_as_str(payload["side"])),
                    price=_as_int(payload["price"]),
                    quantity=_as_int(payload["quantity"]),
                    clocks=_clocks(payload),
                    round_id=_as_int(payload["round_id"]),
                )
            )
        elif record.event_type in (
            EventType.LATENCY_CHOICE,
            EventType.LATENCY_CHOICE_REJECTED,
        ):
            payload = record.payload
            engine.choose_latency(
                LatencyChoice(
                    event_id=_as_int(payload["event_id"]),
                    actor=_as_str(payload["actor"]),
                    round_id=_as_int(payload["round_id"]),
                    investment=_as_int(payload["investment"]),
                    clocks=_clocks(payload),
                )
            )
        elif record.event_type == EventType.SESSION_END:
            engine.finish()
        else:
            continue
        replayed += 1
    if len(engine.tape) != len(tape) or replayed == 0:
        return ReplayReport(False, replayed, None)
    for regenerated, recorded in zip(engine.tape, tape, strict=True):
        if (
            regenerated.sequence != recorded.sequence
            or regenerated.event_type != recorded.event_type
            or regenerated.pre_state_hash != recorded.pre_state_hash
            or regenerated.post_state_hash != recorded.post_state_hash
            or regenerated.pre_aggregate_state_hash != recorded.pre_aggregate_state_hash
            or regenerated.post_aggregate_state_hash != recorded.post_aggregate_state_hash
            or regenerated.payload != recorded.payload
        ):
            return ReplayReport(False, replayed, recorded.sequence)
    return ReplayReport(True, replayed, None)
