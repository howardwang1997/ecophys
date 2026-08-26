"""Adapter and robot-pilot conformance tests (A-2 deliverables D-2b and the pilot gate)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from lab_asset.adapter import (
    AdapterError,
    client_view,
    to_request,
)
from lab_asset.matching import ReferenceEngine
from lab_asset.robot_pilot import run_pilot, run_session
from lab_asset.schema import (
    AllocationRule,
    CancelRequest,
    EventType,
    OrderRequest,
    Side,
)


def test_adapter_translates_new_and_cancel_messages() -> None:
    new = to_request(
        {"type": "new", "actor": "a", "client_order_id": "x1", "side": "B",
         "price": 101, "quantity": 2},
        event_id=1, client_ts=1, receipt_ts=2, match_ts=3,
    )
    assert isinstance(new, OrderRequest)
    assert new.side == Side.BID and new.price == 101 and new.quantity == 2
    cancel = to_request(
        {"type": "cancel", "actor": "a", "client_order_id": "x1"},
        event_id=2, client_ts=4, receipt_ts=5, match_ts=6,
    )
    assert isinstance(cancel, CancelRequest)


def test_adapter_rejects_malformed_messages() -> None:
    for bad in (
        {"type": "new", "actor": "", "client_order_id": "x", "side": "B", "price": 1, "quantity": 1},
        {"type": "new", "actor": "a", "client_order_id": "x", "side": "X", "price": 1, "quantity": 1},
        {"type": "new", "actor": "a", "client_order_id": "x", "side": "B", "price": 1.5, "quantity": 1},
        {"type": "snipe", "actor": "a", "client_order_id": "x"},
        "not-a-dict",
    ):
        try:
            to_request(bad, 1, 1, 1, 1)  # type: ignore[arg-type]
        except AdapterError:
            continue
        raise AssertionError(f"expected AdapterError for {bad!r}")


def test_adapter_stream_is_arm_invariant() -> None:
    """Same message stream, both arms: aggregate-layer paths identical (Lemma 1 machine
    check); only identity-layer allocation may differ."""

    messages: list[dict[str, object]] = [
        {"type": "new", "actor": "a", "client_order_id": "a1", "side": "S", "price": 101, "quantity": 2},
        {"type": "new", "actor": "b", "client_order_id": "b1", "side": "S", "price": 101, "quantity": 2},
        {"type": "new", "actor": "c", "client_order_id": "c1", "side": "S", "price": 101, "quantity": 2},
        {"type": "new", "actor": "d", "client_order_id": "d1", "side": "B", "price": 101, "quantity": 3},
        {"type": "cancel", "actor": "d", "client_order_id": "O00000004"},
    ]

    def wire(rule: AllocationRule, seed: int) -> list[dict[str, object]]:
        engine = ReferenceEngine(_prestate(rule, seed))
        for i, message in enumerate(messages, start=1):
            request = to_request(message, event_id=i, client_ts=i, receipt_ts=i, match_ts=i)
            if isinstance(request, OrderRequest):
                engine.submit(request)
            else:
                engine.cancel(request)
        engine.finish()
        return [client_view(r) for r in engine.tape]

    fifo_views = wire(AllocationRule.FIFO, 5)
    rand_views = wire(AllocationRule.RANDOM_WITHIN_TIE, 5)
    stripped_fifo = [_strip_allocation(v) for v in fifo_views]
    stripped_rand = [_strip_allocation(v) for v in rand_views]
    assert stripped_fifo == stripped_rand
    # Aggregate-layer hashes identical at every sequence across arms.
    agg_fifo = [v["post_aggregate_state_hash"] for v in fifo_views]
    agg_rand = [v["post_aggregate_state_hash"] for v in rand_views]
    assert agg_fifo == agg_rand
    # Identity-layer hashes genuinely diverge somewhere (allocation differs).
    id_fifo = [v["post_state_hash"] for v in fifo_views]
    id_rand = [v["post_state_hash"] for v in rand_views]
    assert id_fifo != id_rand


def _strip_allocation(view: dict[str, object]) -> dict[str, object]:
    out = {k: v for k, v in view.items() if k != "post_state_hash"}
    payload = out.get("payload")
    if isinstance(payload, dict) and "execution" in payload:
        execution = dict(payload["execution"])
        execution.pop("maker_order_id", None)
        execution.pop("maker_actor", None)
        payload = dict(payload)
        payload["execution"] = execution
        payload.pop("allocation_draw", None)
        out["payload"] = payload
    out.pop("allocation", None)
    return out


def _prestate(rule: AllocationRule, seed: int):  # type: ignore[no-untyped-def]
    from lab_asset.schema import SessionPrestate

    return SessionPrestate(
        session_id="S",
        seed=seed,
        allocation_rule=rule,
        initial_cash={"a": 0.0, "b": 0.0, "c": 0.0, "d": 0.0},
        initial_inventory={"a": 0, "b": 0, "c": 0, "d": 0},
        price_bands=(90, 110),
        actors=("a", "b", "c", "d"),
    )


def test_client_view_flags_allocation_channel() -> None:
    from lab_asset.schema import OrderRequest, SessionPrestate, Side, ThreeClocks

    engine = ReferenceEngine(
        SessionPrestate(
            session_id="S",
            seed=3,
            allocation_rule=AllocationRule.RANDOM_WITHIN_TIE,
            initial_cash={"a": 0.0, "b": 0.0},
            initial_inventory={"a": 0, "b": 0},
            price_bands=(90, 110),
            actors=("a", "b"),
        )
    )
    engine.submit(OrderRequest(1, "a", "a1", Side.ASK, 101, 2, ThreeClocks(1, 1, 1)))
    engine.submit(OrderRequest(2, "b", "b1", Side.BID, 102, 1, ThreeClocks(2, 2, 2)))
    views = [client_view(r) for r in engine.tape]
    exec_views = [v for v in views if v["event_type"] == EventType.EXECUTION.value]
    assert len(exec_views) == 1
    assert exec_views[0]["allocation"] == "draw_recorded"


def test_robot_pilot_replay_validates_and_manifest_is_engineering_only(
    tmp_path: Path,
) -> None:
    _, ok_fifo, samples_fifo = run_session(
        AllocationRule.FIFO, seed=11, steps=800
    )
    _, ok_rand, samples_rand = run_session(
        AllocationRule.RANDOM_WITHIN_TIE, seed=11, steps=800
    )
    assert ok_fifo and ok_rand
    assert samples_fifo.executions >= 0 and samples_rand.executions >= 0
    assert len(samples_fifo.spreads) > 0

    manifest = run_pilot(sessions_per_arm=2, steps=400, out_dir=tmp_path)
    assert manifest["engineering_only"] is True
    assert manifest["not_route_evidence"] is True
    written = tmp_path / "robot_pilot_manifest.json"
    assert written.exists()
    arms = manifest["arms"]
    assert isinstance(arms, dict)
    assert set(arms) == {AllocationRule.FIFO.value, AllocationRule.RANDOM_WITHIN_TIE.value}
    for arm in arms.values():
        assert isinstance(arm, dict)
        assert arm["all_replays_ok"] is True
