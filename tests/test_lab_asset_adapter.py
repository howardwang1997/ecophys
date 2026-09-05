"""Adapter and engineering-only robot-pilot conformance tests."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from lab_asset.adapter import AdapterError, client_view, to_request
from lab_asset.matching import ReferenceEngine
from lab_asset.robot_pilot import run_pilot, run_session
from lab_asset.schema import (
    AllocationRule,
    CancelRequest,
    EventType,
    LatencyChoice,
    OrderRequest,
    SessionPrestate,
    Side,
    ThreeClocks,
)


def test_adapter_translates_new_cancel_and_latency_messages() -> None:
    new = to_request(
        {
            "type": "new",
            "actor": "a",
            "client_order_id": "x1",
            "round_id": 2,
            "side": "B",
            "price": 101,
            "quantity": 2,
        },
        event_id=1,
        client_ts=1,
        receipt_ts=2,
        match_ts=3,
    )
    assert isinstance(new, OrderRequest)
    assert new.side == Side.BID and new.round_id == 2
    cancel = to_request(
        {"type": "cancel", "actor": "a", "order_id": "O1", "round_id": 2},
        event_id=2,
        client_ts=4,
        receipt_ts=5,
        match_ts=6,
    )
    assert isinstance(cancel, CancelRequest) and cancel.order_id == "O1"
    latency = to_request(
        {"type": "latency", "actor": "a", "round_id": 2, "investment": 1},
        event_id=3,
        client_ts=7,
        receipt_ts=7,
        match_ts=7,
    )
    assert isinstance(latency, LatencyChoice) and latency.investment == 1


def test_adapter_rejects_malformed_messages() -> None:
    bad_messages: tuple[object, ...] = (
        {
            "type": "new",
            "actor": "",
            "client_order_id": "x",
            "side": "B",
            "price": 1,
            "quantity": 1,
        },
        {
            "type": "new",
            "actor": "a",
            "client_order_id": "x",
            "side": "X",
            "price": 1,
            "quantity": 1,
        },
        {
            "type": "new",
            "actor": "a",
            "client_order_id": "x",
            "side": "B",
            "price": 1.5,
            "quantity": 1,
        },
        {"type": "cancel", "actor": "a", "client_order_id": "x"},
        {"type": "latency", "actor": "a", "investment": 1.2},
        {"type": "snipe", "actor": "a"},
        "not-a-dict",
    )
    for bad in bad_messages:
        try:
            to_request(bad, 1, 1, 1, 1)  # type: ignore[arg-type]
        except AdapterError:
            continue
        raise AssertionError(f"expected AdapterError for {bad!r}")


def _prestate(rule: AllocationRule, seed: int) -> SessionPrestate:
    actors = ("a", "b", "c", "d")
    return SessionPrestate(
        session_id="S",
        seed=seed,
        allocation_rule=rule,
        initial_cash={actor: 100_000 for actor in actors},
        initial_inventory={actor: 100 for actor in actors},
        price_bands=(90, 110),
        actors=actors,
        latency_endowment=2,
        latency_delay_by_investment=(5, 3, 1),
    )


def test_adapter_stream_has_common_request_boundary_aggregate_path() -> None:
    messages: list[dict[str, object]] = [
        {
            "type": "new",
            "actor": "a",
            "client_order_id": "a1",
            "side": "S",
            "price": 101,
            "quantity": 2,
        },
        {
            "type": "new",
            "actor": "b",
            "client_order_id": "b1",
            "side": "S",
            "price": 101,
            "quantity": 2,
        },
        {
            "type": "new",
            "actor": "c",
            "client_order_id": "c1",
            "side": "S",
            "price": 101,
            "quantity": 2,
        },
        {
            "type": "new",
            "actor": "d",
            "client_order_id": "d1",
            "side": "B",
            "price": 101,
            "quantity": 3,
        },
        {"type": "cancel", "actor": "d", "order_id": "O00000004"},
    ]

    def wire(rule: AllocationRule) -> tuple[list[str], list[dict[str, object]]]:
        engine = ReferenceEngine(_prestate(rule, 5))
        boundaries = []
        for i, message in enumerate(messages, start=1):
            request = to_request(message, i, i, i, i)
            if isinstance(request, OrderRequest):
                engine.submit(request)
            elif isinstance(request, CancelRequest):
                engine.cancel(request)
            else:
                engine.choose_latency(request)
            boundaries.append(engine.aggregate_state_digest())
        engine.finish()
        return boundaries, [client_view(record) for record in engine.tape]

    fifo_boundaries, fifo_views = wire(AllocationRule.FIFO)
    random_boundaries, random_views = wire(AllocationRule.RANDOM_UNIT_WITHIN_PRICE)
    assert fifo_boundaries == random_boundaries
    assert len(fifo_views) != len(random_views)
    assert {tuple(sorted(view)) for view in fifo_views} == {
        tuple(sorted(view)) for view in random_views
    }
    assert [view["post_state_hash"] for view in fifo_views] != [
        view["post_state_hash"] for view in random_views
    ]


def test_client_view_flags_semantic_random_unit_draw() -> None:
    engine = ReferenceEngine(_prestate(AllocationRule.RANDOM_UNIT_WITHIN_PRICE, 3))
    engine.submit(OrderRequest(1, "a", "a1", Side.ASK, 101, 2, ThreeClocks(1, 1, 1)))
    engine.submit(OrderRequest(2, "b", "b1", Side.BID, 102, 1, ThreeClocks(2, 2, 2)))
    views = [client_view(record) for record in engine.tape]
    execution_views = [
        view for view in views if view["event_type"] == EventType.EXECUTION.value
    ]
    assert len(execution_views) == 1
    assert execution_views[0]["allocation"] == "draw_recorded"


def test_robot_pilot_replay_validates_and_manifest_is_engineering_only(
    tmp_path: Path,
) -> None:
    _, ok_fifo, samples_fifo = run_session(AllocationRule.FIFO, seed=11, steps=800)
    _, ok_random, samples_random = run_session(
        AllocationRule.RANDOM_UNIT_WITHIN_PRICE, seed=11, steps=800
    )
    assert ok_fifo and ok_random
    assert samples_fifo.executed_units >= 0 and samples_random.executed_units >= 0
    assert len(samples_fifo.spreads) > 0

    manifest = run_pilot(sessions_per_arm=2, steps=400, out_dir=tmp_path)
    assert manifest["engineering_only"] is True
    assert manifest["not_route_evidence"] is True
    assert (tmp_path / "robot_pilot_manifest.json").exists()
    arms = manifest["arms"]
    assert isinstance(arms, dict)
    assert set(arms) == {
        AllocationRule.FIFO.value,
        AllocationRule.RANDOM_UNIT_WITHIN_PRICE.value,
    }
    for arm in arms.values():
        assert isinstance(arm, dict)
        assert arm["all_replays_ok"] is True
