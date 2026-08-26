"""Conformance fixture suite for the truth-asset reference engine (A-2 deliverable D-2.4).

Covers: golden scenarios (marketable cross, partial fills, tie-set allocation
distribution, cancel semantics, reason-coded rejections, duplicate client IDs, self-trade
prevention), grammar arm-invariance across allocation arms, bit-level determinism under a
fixed seed, and exact deterministic replay of recorded tapes.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from lab_asset.matching import ReferenceEngine
from lab_asset.replay import replay
from lab_asset.schema import (
    AllocationRule,
    CancelRequest,
    EventType,
    OrderRequest,
    SessionPrestate,
    Side,
    ThreeClocks,
)


def make_prestate(rule: AllocationRule, seed: int = 7) -> SessionPrestate:
    return SessionPrestate(
        session_id="S0001",
        seed=seed,
        allocation_rule=rule,
        initial_cash={"a": 10_000.0, "b": 10_000.0, "c": 10_000.0, "d": 10_000.0},
        initial_inventory={"a": 0, "b": 0, "c": 0, "d": 0},
        price_bands=(90, 110),
        actors=("a", "b", "c", "d"),
    )



def _as_int(value: object) -> int:
    assert isinstance(value, int)
    return value


def sub(payload: dict[str, object], key: str) -> dict[str, object]:
    value = payload[key]
    assert isinstance(value, dict)
    return value


def clocks(t: int) -> ThreeClocks:
    return ThreeClocks(client_ts=t, receipt_ts=t, match_ts=t)


def buy(actor: str, oid: str, price: int, qty: int, t: int) -> OrderRequest:
    return OrderRequest(
        event_id=t, actor=actor, client_order_id=oid, side=Side.BID,
        price=price, quantity=qty, clocks=clocks(t),
    )


def sell(actor: str, oid: str, price: int, qty: int, t: int) -> OrderRequest:
    return OrderRequest(
        event_id=t, actor=actor, client_order_id=oid, side=Side.ASK,
        price=price, quantity=qty, clocks=clocks(t),
    )


def events(engine: ReferenceEngine, etype: EventType) -> list[dict[str, object]]:
    return [r.payload for r in engine.tape if r.event_type == etype]


def test_golden_marketable_cross_fills_best_ask() -> None:
    engine = ReferenceEngine(make_prestate(AllocationRule.FIFO))
    engine.submit(sell("a", "a1", 101, 5, 1))
    engine.submit(buy("b", "b1", 102, 3, 2))
    engine.finish()
    execs = events(engine, EventType.EXECUTION)
    assert len(execs) == 1
    ex = execs[0]["execution"]
    assert isinstance(ex, dict)
    assert ex["price"] == 101 and ex["quantity"] == 3
    assert ex["maker_actor"] == "a" and ex["aggressor_actor"] == "b"
    assert ex["maker_remaining"] == 2


def test_partial_fill_chain_and_rejections() -> None:
    engine = ReferenceEngine(make_prestate(AllocationRule.FIFO))
    engine.submit(sell("a", "a1", 101, 5, 1))
    engine.submit(sell("a", "a2", 102, 5, 2))
    engine.submit(buy("b", "b1", 101, 8, 3))
    engine.submit(buy("b", "b1", 101, 8, 4))       # duplicate client id
    engine.submit(buy("b", "b2", 200, 1, 5))       # out of bands
    engine.submit(buy("b", "b3", 101, 0, 6))       # non-positive qty
    engine.finish()
    execs = events(engine, EventType.EXECUTION)
    assert len(execs) == 1
    ex = execs[0]["execution"]
    assert isinstance(ex, dict)
    assert ex["price"] == 101 and ex["quantity"] == 5 and ex["maker_remaining"] == 0
    accepted = events(engine, EventType.ORDER_ACCEPTED)
    assert accepted[-1]["resting_quantity"] == 3  # residual buy rests at 101
    reasons = {p["reason"] for p in events(engine, EventType.ORDER_REJECTED)}
    assert reasons == {"duplicate_client_id", "price_out_of_bands", "negative_or_zero_quantity"}


def test_self_trade_prevention_on_occupied_touch() -> None:
    engine = ReferenceEngine(make_prestate(AllocationRule.FIFO))
    engine.submit(sell("a", "a1", 101, 5, 1))
    engine.submit(buy("a", "a2", 102, 1, 2))  # only own order at touch
    engine.finish()
    assert {p["reason"] for p in events(engine, EventType.ORDER_REJECTED)} == {
        "self_trade_prevented"
    }


def test_cancel_semantics_and_unknown_order() -> None:
    engine = ReferenceEngine(make_prestate(AllocationRule.FIFO))
    engine.submit(sell("a", "a1", 101, 5, 1))
    engine.cancel(CancelRequest(event_id=2, actor="a", client_order_id="O00000001", clocks=clocks(2)))
    engine.cancel(CancelRequest(event_id=3, actor="a", client_order_id="O00000001", clocks=clocks(3)))
    engine.cancel(CancelRequest(event_id=4, actor="b", client_order_id="nope", clocks=clocks(4)))
    engine.finish()
    cancelled = events(engine, EventType.ORDER_CANCELLED)
    rejected = events(engine, EventType.CANCEL_REJECTED)
    assert len(cancelled) == 1 and cancelled[0]["cancelled_quantity"] == 5
    assert {p["reason"] for p in rejected} == {"already_filled", "unknown_order"}


def test_fifo_tie_set_is_arrival_ordered() -> None:
    engine = ReferenceEngine(make_prestate(AllocationRule.FIFO))
    engine.submit(sell("a", "a1", 101, 1, 1))
    engine.submit(sell("b", "b1", 101, 1, 2))
    engine.submit(sell("c", "c1", 101, 1, 3))
    engine.submit(buy("d", "d1", 101, 2, 4))
    engine.finish()
    makers = [str(sub(p, "execution")["maker_actor"]) for p in events(engine, EventType.EXECUTION)]
    assert makers == ["a", "b"]


def test_random_tie_set_draws_are_uniform_and_recorded() -> None:
    counts: Counter[str] = Counter()
    draw_indices: Counter[int] = Counter()
    for seed in range(600):
        engine = ReferenceEngine(make_prestate(AllocationRule.RANDOM_WITHIN_TIE, seed=seed))
        engine.submit(sell("a", "a1", 101, 1, 1))
        engine.submit(sell("b", "b1", 101, 1, 2))
        engine.submit(buy("d", "d1", 101, 1, 3))
        execs = events(engine, EventType.EXECUTION)
        assert len(execs) == 1
        counts[str(sub(execs[0], "execution")["maker_actor"])] += 1
        draw = sub(execs[0], "allocation_draw")
        draw_indices[_as_int(draw["index"])] += 1
    assert set(counts) == {"a", "b"}
    a, b = counts["a"], counts["b"]
    assert 0.4 <= a / (a + b) <= 0.6
    assert set(draw_indices) == {0, 1}


def test_grammar_arm_invariance() -> None:
    """Same request tape, both arms: identical grammar fields; only allocation may differ."""

    def run(rule: AllocationRule, seed: int) -> list[tuple[str, object, object]]:
        engine = ReferenceEngine(make_prestate(rule, seed=seed))
        engine.submit(sell("a", "a1", 101, 3, 1))
        engine.submit(sell("b", "b1", 101, 3, 2))
        engine.submit(sell("c", "c1", 102, 2, 3))
        engine.submit(buy("d", "d1", 102, 4, 4))
        engine.submit(buy("d", "d2", 101, 3, 5))
        engine.cancel(CancelRequest(event_id=6, actor="d", client_order_id="O00000004", clocks=clocks(6)))
        engine.finish()
        return [
            (r.event_type.value, r.payload.get("price"), r.payload.get("reason", ""))
            for r in engine.tape
        ]

    fifo = run(AllocationRule.FIFO, 11)
    rand = run(AllocationRule.RANDOM_WITHIN_TIE, 11)
    assert fifo == rand


def test_aggregate_paths_identical_across_arms() -> None:
    """Executions' prices and quantities (aggregate observables) match across arms."""

    def run(rule: AllocationRule, seed: int) -> list[tuple[int, int]]:
        engine = ReferenceEngine(make_prestate(rule, seed=seed))
        engine.submit(sell("a", "a1", 101, 2, 1))
        engine.submit(sell("b", "b1", 101, 2, 2))
        engine.submit(sell("c", "c1", 101, 2, 3))
        engine.submit(buy("d", "d1", 102, 4, 4))
        engine.finish()
        return [
            (
                _as_int(sub(p, "execution")["price"]),
                _as_int(sub(p, "execution")["quantity"]),
            )
            for p in events(engine, EventType.EXECUTION)
        ]

    assert run(AllocationRule.FIFO, 5) == run(AllocationRule.RANDOM_WITHIN_TIE, 5)
    assert run(AllocationRule.RANDOM_WITHIN_TIE, 5) == run(AllocationRule.RANDOM_WITHIN_TIE, 5)


def test_bit_level_determinism() -> None:
    def tape(rule: AllocationRule, seed: int) -> str:
        engine = ReferenceEngine(make_prestate(rule, seed=seed))
        engine.submit(sell("a", "a1", 101, 2, 1))
        engine.submit(sell("b", "b1", 101, 2, 2))
        engine.submit(buy("c", "c1", 102, 3, 3))
        engine.finish()
        return "\n".join(
            f"{r.sequence}|{r.event_type.value}|{r.pre_state_hash}|{r.post_state_hash}"
            for r in engine.tape
        )

    assert tape(AllocationRule.FIFO, 42) == tape(AllocationRule.FIFO, 42)
    assert tape(AllocationRule.RANDOM_WITHIN_TIE, 42) == tape(
        AllocationRule.RANDOM_WITHIN_TIE, 42
    )


def test_deterministic_replay_reproduces_recorded_tape() -> None:
    for rule in (AllocationRule.FIFO, AllocationRule.RANDOM_WITHIN_TIE):
        engine = ReferenceEngine(make_prestate(rule, seed=99))
        engine.submit(sell("a", "a1", 101, 2, 1))
        engine.submit(sell("b", "b1", 101, 2, 2))
        engine.submit(sell("c", "c1", 102, 2, 3))
        engine.submit(buy("d", "d1", 102, 4, 4))
        engine.cancel(CancelRequest(event_id=5, actor="d", client_order_id="O00000004", clocks=clocks(5)))
        engine.finish()
        report = replay(make_prestate(rule, seed=99), engine.tape)
        assert report.ok, str(report)
        assert report.events_replayed == 6  # 4 submits + 1 cancel + session end


def test_replay_detects_tampered_tape() -> None:
    engine = ReferenceEngine(make_prestate(AllocationRule.FIFO, seed=99))
    engine.submit(sell("a", "a1", 101, 2, 1))
    engine.submit(buy("d", "d1", 101, 1, 2))
    engine.finish()
    tampered = []
    for r in engine.tape:
        if r.event_type == EventType.EXECUTION:
            payload = dict(r.payload)
            execution = dict(sub(payload, "execution"))
            execution["quantity"] = 2
            payload["execution"] = execution
            tampered.append(
                type(r)(
                    sequence=r.sequence,
                    event_type=r.event_type,
                    payload=payload,
                    pre_state_hash=r.pre_state_hash,
                    post_state_hash=r.post_state_hash,
                )
            )
        else:
            tampered.append(r)
    report = replay(make_prestate(AllocationRule.FIFO, seed=99), tampered)
    assert not report.ok
