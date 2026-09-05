"""Conformance tests for the repaired lab-asset mechanism kernel."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from lab_asset.matching import ReferenceEngine
from lab_asset.priority_race import expected_race_payoff, race_best_response
from lab_asset.replay import replay
from lab_asset.schema import (
    AllocationRule,
    CancelRequest,
    EventType,
    InformationRelease,
    InitialOrder,
    LatencyChoice,
    OrderRequest,
    SessionPrestate,
    Side,
    ThreeClocks,
)


def make_prestate(rule: AllocationRule, seed: int = 7) -> SessionPrestate:
    actors = ("a", "b", "c", "d")
    return SessionPrestate(
        session_id="S0001",
        seed=seed,
        allocation_rule=rule,
        initial_cash={actor: 100_000 for actor in actors},
        initial_inventory={actor: 100 for actor in actors},
        price_bands=(90, 110),
        actors=actors,
        induced_buy_values={actor: tuple(110 for _ in range(200)) for actor in actors},
        induced_sell_costs={actor: tuple(90 for _ in range(200)) for actor in actors},
        information_schedule=(InformationRelease(0, "fundamental", 100),),
        scheduler_seed=17,
        scheduler_tick=0,
        scheduler_state="round-0-ready",
        assignment_key_commitment="test-commitment",
        latency_endowment=2,
        latency_delay_by_investment=(5, 3, 1),
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
    return OrderRequest(t, actor, oid, Side.BID, price, qty, clocks(t))


def sell(actor: str, oid: str, price: int, qty: int, t: int) -> OrderRequest:
    return OrderRequest(t, actor, oid, Side.ASK, price, qty, clocks(t))


def events(engine: ReferenceEngine, etype: EventType) -> list[dict[str, object]]:
    return [record.payload for record in engine.tape if record.event_type == etype]


def maker_actors(engine: ReferenceEngine) -> list[str]:
    return [
        str(sub(payload, "execution")["maker_actor"])
        for payload in events(engine, EventType.EXECUTION)
    ]


def test_session_start_commits_complete_prestate() -> None:
    engine = ReferenceEngine(make_prestate(AllocationRule.FIFO))
    start = engine.tape[0]
    assert start.event_type == EventType.SESSION_START
    assert start.payload["prestate_hash"] == engine.prestate_digest
    assert start.pre_state_hash != start.post_state_hash


def test_golden_marketable_cross_settles_holdings() -> None:
    engine = ReferenceEngine(make_prestate(AllocationRule.FIFO))
    engine.submit(sell("a", "a1", 101, 5, 1))
    engine.submit(buy("b", "b1", 102, 3, 2))
    engine.finish()
    execs = events(engine, EventType.EXECUTION)
    assert len(execs) == 1
    execution = sub(execs[0], "execution")
    assert execution["price"] == 101 and execution["quantity"] == 3
    assert execution["maker_actor"] == "a" and execution["maker_remaining"] == 2
    assert engine.cash["a"] == 100_303 and engine.cash["b"] == 99_697
    assert engine.inventory["a"] == 97 and engine.inventory["b"] == 103
    assert engine.realized_induced_surplus["a"] == 33
    assert engine.realized_induced_surplus["b"] == 27
    assert engine.available_information()[0].label == "fundamental"


def test_partial_fill_chain_and_basic_rejections() -> None:
    engine = ReferenceEngine(make_prestate(AllocationRule.FIFO))
    engine.submit(sell("a", "a1", 101, 5, 1))
    engine.submit(sell("a", "a2", 102, 5, 2))
    engine.submit(buy("b", "b1", 101, 8, 3))
    engine.submit(buy("b", "b1", 101, 8, 4))
    engine.submit(buy("b", "b2", 200, 1, 5))
    engine.submit(buy("b", "b3", 101, 0, 6))
    execs = events(engine, EventType.EXECUTION)
    assert len(execs) == 1
    execution = sub(execs[0], "execution")
    assert execution["quantity"] == 5 and execution["maker_remaining"] == 0
    assert events(engine, EventType.ORDER_ACCEPTED)[-1]["resting_quantity"] == 3
    reasons = {payload["reason"] for payload in events(engine, EventType.ORDER_REJECTED)}
    assert reasons == {
        "duplicate_client_id",
        "price_out_of_bands",
        "negative_or_zero_quantity",
    }


def test_cash_inventory_actor_and_clock_constraints() -> None:
    prestate = SessionPrestate(
        session_id="resource-test",
        seed=1,
        allocation_rule=AllocationRule.FIFO,
        initial_cash={"buyer": 100, "seller": 0},
        initial_inventory={"buyer": 0, "seller": 2},
        price_bands=(1, 100),
        actors=("buyer", "seller"),
    )
    engine = ReferenceEngine(prestate)
    engine.submit(buy("buyer", "too-costly", 60, 2, 1))
    engine.submit(sell("seller", "too-large", 50, 3, 2))
    engine.submit(buy("ghost", "unknown", 50, 1, 3))
    engine.submit(
        OrderRequest(
            4,
            "buyer",
            "bad-clock",
            Side.BID,
            50,
            1,
            ThreeClocks(5, 4, 6),
        )
    )
    reasons = [payload["reason"] for payload in events(engine, EventType.ORDER_REJECTED)]
    assert reasons == [
        "insufficient_cash",
        "insufficient_inventory",
        "unknown_actor",
        "invalid_clocks",
    ]


def test_induced_value_unit_capacities_are_enforced() -> None:
    prestate = SessionPrestate(
        session_id="value-capacity",
        seed=2,
        allocation_rule=AllocationRule.FIFO,
        initial_cash={"buyer": 10_000, "seller": 0},
        initial_inventory={"buyer": 0, "seller": 10},
        price_bands=(1, 100),
        actors=("buyer", "seller"),
        induced_buy_values={"buyer": (100,)},
        induced_sell_costs={"seller": (1,)},
    )
    engine = ReferenceEngine(prestate)
    engine.submit(buy("buyer", "too-many-buys", 50, 2, 1))
    engine.submit(sell("seller", "too-many-sales", 50, 2, 2))
    assert [payload["reason"] for payload in events(engine, EventType.ORDER_REJECTED)] == [
        "induced_buy_capacity_exceeded",
        "induced_sell_capacity_exceeded",
    ]


def test_self_trade_prevention_covers_every_crossed_level() -> None:
    engine = ReferenceEngine(make_prestate(AllocationRule.FIFO))
    engine.submit(sell("b", "b1", 100, 1, 1))
    engine.submit(sell("a", "a1", 101, 1, 2))
    engine.submit(buy("a", "a2", 102, 1, 3))
    assert {payload["reason"] for payload in events(engine, EventType.ORDER_REJECTED)} == {
        "self_trade_prevented"
    }


def test_cancel_lifecycle_and_ownership() -> None:
    engine = ReferenceEngine(make_prestate(AllocationRule.FIFO))
    engine.submit(sell("a", "a1", 101, 5, 1))
    engine.cancel(CancelRequest(2, "b", "O00000001", clocks(2)))
    engine.cancel(CancelRequest(3, "a", "O00000001", clocks(3)))
    engine.cancel(CancelRequest(4, "a", "O00000001", clocks(4)))
    engine.cancel(CancelRequest(5, "b", "nope", clocks(5)))
    assert len(events(engine, EventType.ORDER_CANCELLED)) == 1
    reasons = [payload["reason"] for payload in events(engine, EventType.CANCEL_REJECTED)]
    assert reasons == ["not_owner", "already_cancelled", "unknown_order"]


def test_fifo_is_arrival_ordered_and_partial_maker_keeps_priority() -> None:
    engine = ReferenceEngine(make_prestate(AllocationRule.FIFO))
    engine.submit(sell("a", "a1", 101, 5, 1))
    engine.submit(sell("b", "b1", 101, 5, 2))
    engine.submit(buy("c", "c1", 101, 2, 3))
    engine.submit(buy("d", "d1", 101, 1, 4))
    assert maker_actors(engine) == ["a", "a"]
    assert engine.asks[101] == [
        ("O00000001", "a", 2),
        ("O00000002", "b", 5),
    ]


def test_random_unit_draws_are_quantity_weighted_and_recorded() -> None:
    counts: Counter[str] = Counter()
    selected_units: set[int] = set()
    for seed in range(800):
        engine = ReferenceEngine(
            make_prestate(AllocationRule.RANDOM_UNIT_WITHIN_PRICE, seed=seed)
        )
        engine.submit(sell("a", "a1", 101, 3, 1))
        engine.submit(sell("b", "b1", 101, 1, 2))
        engine.submit(buy("d", "d1", 101, 1, 3))
        execution = events(engine, EventType.EXECUTION)[0]
        counts[str(sub(execution, "execution")["maker_actor"])] += 1
        draw = sub(execution, "allocation_draw")
        assert draw["eligible_units"] == 4
        selected_units.add(_as_int(draw["selected_unit"]))
    share_a = counts["a"] / sum(counts.values())
    assert 0.70 <= share_a <= 0.80
    assert selected_units == {0, 1, 2, 3}


def test_random_unit_allocation_is_invariant_to_contiguous_child_splitting() -> None:
    def selected_actor(seed: int, split: bool) -> str:
        engine = ReferenceEngine(
            make_prestate(AllocationRule.RANDOM_UNIT_WITHIN_PRICE, seed=seed)
        )
        if split:
            for i in range(3):
                engine.submit(sell("a", f"a{i}", 101, 1, i + 1))
            t = 4
        else:
            engine.submit(sell("a", "a", 101, 3, 1))
            t = 2
        engine.submit(sell("b", "b", 101, 1, t))
        engine.submit(buy("d", "d", 101, 1, t + 1))
        return maker_actors(engine)[0]

    for seed in range(100):
        assert selected_actor(seed, split=False) == selected_actor(seed, split=True)


def test_identity_hash_preserves_fifo_order_while_aggregate_hash_does_not() -> None:
    first = ReferenceEngine(make_prestate(AllocationRule.FIFO, seed=1))
    second = ReferenceEngine(make_prestate(AllocationRule.FIFO, seed=1))
    first.submit(sell("a", "x", 101, 1, 1))
    first.submit(sell("b", "y", 101, 1, 2))
    second.submit(sell("b", "x", 101, 1, 1))
    second.submit(sell("a", "y", 101, 1, 2))
    assert first.identity_state_digest() != second.identity_state_digest()
    assert first.aggregate_state_digest() == second.aggregate_state_digest()


def test_aggregate_state_matches_across_arms_at_request_boundaries() -> None:
    requests = [
        sell("a", "a1", 101, 3, 1),
        sell("b", "b1", 101, 3, 2),
        sell("c", "c1", 102, 2, 3),
        buy("d", "d1", 102, 4, 4),
        buy("d", "d2", 101, 1, 5),
    ]

    def path(rule: AllocationRule) -> tuple[list[str], ReferenceEngine]:
        engine = ReferenceEngine(make_prestate(rule, seed=11))
        digests = []
        for request in requests:
            engine.submit(request)
            digests.append(engine.aggregate_state_digest())
        return digests, engine

    fifo_path, fifo = path(AllocationRule.FIFO)
    random_path, random_engine = path(AllocationRule.RANDOM_UNIT_WITHIN_PRICE)
    assert fifo_path == random_path
    assert fifo.identity_state_digest() != random_engine.identity_state_digest()
    assert len(events(fifo, EventType.EXECUTION)) != len(
        events(random_engine, EventType.EXECUTION)
    )


def test_latency_choice_is_recorded_rejected_and_replayable() -> None:
    prestate = make_prestate(AllocationRule.FIFO, seed=9)
    engine = ReferenceEngine(prestate)
    engine.choose_latency(LatencyChoice(1, "a", 1, 2, clocks(1)))
    engine.choose_latency(LatencyChoice(2, "a", 1, 1, clocks(2)))
    engine.finish()
    accepted = events(engine, EventType.LATENCY_CHOICE)
    rejected = events(engine, EventType.LATENCY_CHOICE_REJECTED)
    assert accepted[0]["resulting_delay_ticks"] == 1
    assert rejected[0]["reason"] == "duplicate_choice"
    assert replay(prestate, engine.tape).ok


def test_isolated_race_removes_the_marginal_return_to_speed() -> None:
    assert race_best_response(
        rule=AllocationRule.FIFO,
        other_investments=(0,),
        delay_by_investment=(5, 3, 1),
        execution_prize=10,
        cost_per_unit=1,
    ) == 1
    assert (
        race_best_response(
            rule=AllocationRule.RANDOM_UNIT_WITHIN_PRICE,
            other_investments=(0,),
            delay_by_investment=(5, 3, 1),
            execution_prize=10,
            cost_per_unit=1,
        )
        == 0
    )
    random_payoffs = [
        expected_race_payoff(
            rule=AllocationRule.RANDOM_UNIT_WITHIN_PRICE,
            investment=investment,
            other_investments=(0,),
            delay_by_investment=(5, 3, 1),
            execution_prize=10,
            cost_per_unit=1,
        )
        for investment in range(3)
    ]
    assert random_payoffs == [5.0, 4.0, 3.0]


def test_initial_book_is_loaded_and_resource_checked() -> None:
    prestate = SessionPrestate(
        session_id="initial-book",
        seed=4,
        allocation_rule=AllocationRule.FIFO,
        initial_cash={"a": 1_000, "b": 1_000},
        initial_inventory={"a": 3, "b": 3},
        price_bands=(90, 110),
        actors=("a", "b"),
        initial_book=(InitialOrder("seed-ask", "a", Side.ASK, 101, 2),),
    )
    engine = ReferenceEngine(prestate)
    assert engine.asks[101] == [("seed-ask", "a", 2)]
    engine.submit(buy("b", "b1", 101, 1, 1))
    assert maker_actors(engine) == ["a"]


def test_bit_level_determinism_and_hash_chain() -> None:
    def tape(rule: AllocationRule, seed: int) -> list[tuple[object, ...]]:
        engine = ReferenceEngine(make_prestate(rule, seed=seed))
        engine.submit(sell("a", "a1", 101, 2, 1))
        engine.submit(sell("b", "b1", 101, 2, 2))
        engine.submit(buy("c", "c1", 102, 3, 3))
        engine.finish()
        for previous, current in zip(engine.tape, engine.tape[1:], strict=False):
            assert previous.post_state_hash == current.pre_state_hash
        return [
            (
                record.sequence,
                record.event_type,
                record.payload,
                record.pre_state_hash,
                record.post_state_hash,
            )
            for record in engine.tape
        ]

    for rule in (AllocationRule.FIFO, AllocationRule.RANDOM_UNIT_WITHIN_PRICE):
        assert tape(rule, 42) == tape(rule, 42)


def test_deterministic_replay_reproduces_recorded_tape() -> None:
    for rule in (AllocationRule.FIFO, AllocationRule.RANDOM_UNIT_WITHIN_PRICE):
        prestate = make_prestate(rule, seed=99)
        engine = ReferenceEngine(prestate)
        engine.submit(sell("a", "a1", 101, 2, 1))
        engine.submit(sell("b", "b1", 101, 2, 2))
        engine.submit(sell("c", "c1", 102, 2, 3))
        engine.submit(buy("d", "d1", 102, 4, 4))
        engine.cancel(CancelRequest(5, "d", "O00000004", clocks(5)))
        engine.finish()
        report = replay(prestate, engine.tape)
        assert report.ok, str(report)
        assert report.events_replayed == 6


def test_replay_detects_tampered_tape() -> None:
    prestate = make_prestate(AllocationRule.FIFO, seed=99)
    engine = ReferenceEngine(prestate)
    engine.submit(sell("a", "a1", 101, 2, 1))
    engine.submit(buy("d", "d1", 101, 1, 2))
    engine.finish()
    tampered = []
    for record in engine.tape:
        if record.event_type == EventType.EXECUTION:
            payload = dict(record.payload)
            execution = dict(sub(payload, "execution"))
            execution["quantity"] = 2
            payload["execution"] = execution
            tampered.append(
                type(record)(
                    sequence=record.sequence,
                    event_type=record.event_type,
                    payload=payload,
                    pre_state_hash=record.pre_state_hash,
                    post_state_hash=record.post_state_hash,
                    pre_aggregate_state_hash=record.pre_aggregate_state_hash,
                    post_aggregate_state_hash=record.post_aggregate_state_hash,
                )
            )
        else:
            tampered.append(record)
    assert not replay(prestate, tampered).ok
