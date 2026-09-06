"""Read-only fixture competence gate for the through-M estimator menu (D1_07 / KT-A4).

The frozen A-2 exit bundle at experiments/lab_asset_a2/a2_exit_20260905/ is consumed
STRICTLY read-only: this suite verifies the bundle's manifest hashes before any
estimator claim, replays fixtures in memory only, and writes nothing. No training,
no models, no GPU: it executes the reference engine on CPU exactly as the frozen
conformance suite (tests/test_lab_asset_conformance.py) does.
"""

from __future__ import annotations

import hashlib
import inspect
import json
import sys
from pathlib import Path
from typing import Any

import pytest
import torch

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from lab_asset.matching import ReferenceEngine  # noqa: E402
from lab_asset.replay import replay  # noqa: E402
from lab_asset.schema import (  # noqa: E402
    AllocationRule,
    CancelRequest,
    EventType,
    InformationRelease,
    InitialOrder,
    LatencyChoice,
    OrderRequest,
    ReplaceRequest,
    SessionPrestate,
    Side,
    TapeRecord,
    ThreeClocks,
    prestate_from_json,
)

from ecomd.mechanisms.through_m import (  # noqa: E402
    PINNED_PERTURB_AND_MAP_SEED,
    PINNED_PERTURB_AND_MAP_SIGMA,
    PINNED_STRAIGHT_THROUGH_SCALE,
    ClearingOutcome,
    Fill,
    Kernel,
    _perturbed_clearing,
    exact_clearing,
    perturb_and_map_through_m,
    straight_through_through_m,
)

BUNDLE = REPO_ROOT / "experiments/lab_asset_a2/a2_exit_20260905"
ARMS = ("fixture_fifo", "fixture_random_unit_within_price")


def _kernel_for(arm: str) -> Kernel:
    rule = AllocationRule("fifo" if arm == "fixture_fifo" else "random_unit_within_price")
    return Kernel(rule.value)


def load_arm(arm: str) -> tuple[SessionPrestate, list[TapeRecord]]:
    raw_prestate = (BUNDLE / arm / "prestate.json").read_text(encoding="utf-8")
    prestate = prestate_from_json(raw_prestate)
    tape: list[TapeRecord] = []
    for line in (BUNDLE / arm / "tape.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        raw = json.loads(line)
        tape.append(
            TapeRecord(
                sequence=int(raw["sequence"]),
                event_type=EventType(str(raw["event_type"])),
                payload=dict[str, Any](raw["payload"]),
                pre_state_hash=str(raw["pre_state_hash"]),
                post_state_hash=str(raw["post_state_hash"]),
                pre_aggregate_state_hash=str(raw["pre_aggregate_state_hash"]),
                post_aggregate_state_hash=str(raw["post_aggregate_state_hash"]),
            )
        )
    return prestate, tape


def _dispatch(engine: ReferenceEngine, record: TapeRecord) -> None:
    payload = record.payload

    def as_int(key: str) -> int:
        value = payload[key]
        assert isinstance(value, int)
        return value

    def as_str(key: str) -> str:
        value = payload[key]
        assert isinstance(value, str)
        return value

    needs_clocks = record.event_type in (
        EventType.ORDER_REQUEST,
        EventType.CANCEL_REQUEST,
        EventType.REPLACE_REQUEST,
        EventType.LATENCY_CHOICE,
        EventType.LATENCY_CHOICE_REJECTED,
    )
    clocks = ThreeClocks(client_ts=0, receipt_ts=0, match_ts=0)
    if needs_clocks:
        clocks_raw = payload["clocks"]
        assert isinstance(clocks_raw, dict)
        clocks = ThreeClocks(
            client_ts=int(clocks_raw["client_ts"]),
            receipt_ts=int(clocks_raw["receipt_ts"]),
            match_ts=int(clocks_raw["match_ts"]),
        )
    if record.event_type == EventType.ORDER_REQUEST:
        engine.submit(
            OrderRequest(
                event_id=as_int("event_id"),
                actor=as_str("actor"),
                client_order_id=as_str("client_order_id"),
                side=Side(as_str("side")),
                price=as_int("price"),
                quantity=as_int("quantity"),
                clocks=clocks,
                round_id=as_int("round_id"),
            )
        )
    elif record.event_type == EventType.CANCEL_REQUEST:
        engine.cancel(
            CancelRequest(
                event_id=as_int("event_id"),
                actor=as_str("actor"),
                order_id=as_str("order_id"),
                clocks=clocks,
                round_id=as_int("round_id"),
            )
        )
    elif record.event_type == EventType.REPLACE_REQUEST:
        engine.replace(
            ReplaceRequest(
                event_id=as_int("event_id"),
                actor=as_str("actor"),
                replaces_order_id=as_str("replaces_order_id"),
                client_order_id=as_str("client_order_id"),
                side=Side(as_str("side")),
                price=as_int("price"),
                quantity=as_int("quantity"),
                clocks=clocks,
                round_id=as_int("round_id"),
            )
        )
    elif record.event_type in (
        EventType.LATENCY_CHOICE,
        EventType.LATENCY_CHOICE_REJECTED,
    ):
        engine.choose_latency(
            LatencyChoice(
                event_id=as_int("event_id"),
                actor=as_str("actor"),
                round_id=as_int("round_id"),
                investment=as_int("investment"),
                clocks=clocks,
            )
        )
    elif record.event_type == EventType.SESSION_END:
        engine.finish()


def _crossed_level_snapshots(
    engine: ReferenceEngine, record: TapeRecord
) -> list[tuple[int, int, list[tuple[str, int]]]]:
    """Best-first walk of the crossed opposite levels before an order request.

    Mirrors the engine's matching loop: each entry is (price, incoming demand at
    that level, queue of (order_id, resting_quantity) in FIFO rank).
    """

    payload = record.payload
    side = str(payload["side"])
    price = int(payload["price"])
    quantity = int(payload["quantity"])
    book = engine.asks if side == Side.BID.value else engine.bids
    levels = (
        [level for level in sorted(book) if level <= price]
        if side == Side.BID.value
        else [level for level in sorted(book, reverse=True) if level >= price]
    )
    snapshots: list[tuple[int, int, list[tuple[str, int]]]] = []
    remaining = quantity
    for level in levels:
        if remaining <= 0:
            break
        queue = [(order_id, resting) for order_id, _actor, resting in book[level]]
        snapshots.append((level, remaining, queue))
        remaining -= sum(resting for _order_id, resting in queue)
    return snapshots


Group = tuple[Kernel, list[tuple[int, int, list[tuple[str, int]]]], list[TapeRecord]]


def _fixture_execution_groups(arm: str) -> tuple[SessionPrestate, list[Group]]:
    """Replay the frozen arm and group recorded executions by generating request."""

    prestate, tape = load_arm(arm)
    assert replay(prestate, tape).ok
    engine = ReferenceEngine(prestate)
    kernel = _kernel_for(arm)
    groups: list[Group] = []
    for record in tape:
        snapshots = None
        if record.event_type == EventType.ORDER_REQUEST:
            snapshots = _crossed_level_snapshots(engine, record)
        before = len(engine.tape)
        _dispatch(engine, record)
        executions = [
            engine_record
            for engine_record in engine.tape[before:]
            if engine_record.event_type == EventType.EXECUTION
        ]
        if executions:
            assert snapshots is not None, "fixture executions must follow an order request"
            groups.append((kernel, snapshots, executions))
    return prestate, groups


def _draw_stream(kernel: Kernel, records: list[TapeRecord]) -> list[int]:
    if kernel is Kernel.FIFO:
        return []
    draws: list[int] = []
    for record in records:
        draw = record.payload.get("allocation_draw")
        assert isinstance(draw, dict), "random-unit executions must record the draw"
        selected = draw["selected_unit"]
        assert isinstance(selected, int)
        draws.append(selected)
    return draws


def _assert_fills_match_executions(
    fills: list[Fill], executions: list[TapeRecord], queue_ids: list[str]
) -> None:
    assert len(fills) == len(executions)
    for fill, record in zip(fills, executions, strict=True):
        execution = record.payload["execution"]
        assert isinstance(execution, dict)
        assert queue_ids[fill.queue_index] == str(execution["maker_order_id"])
        assert fill.quantity == int(execution["quantity"])
        assert fill.maker_remaining_after == int(execution["maker_remaining"])
        if fill.selected_unit is not None:
            draw = record.payload.get("allocation_draw")
            assert isinstance(draw, dict)
            assert fill.eligible_units == int(draw["eligible_units"])
            assert fill.selected_unit == int(draw["selected_unit"])


def _level_outcomes(
    kernel: Kernel,
    snapshots: list[tuple[int, int, list[tuple[str, int]]]],
    draws: list[int],
) -> list[tuple[ClearingOutcome, list[str]]]:
    """Exact clearing over the crossed levels, splitting the draw stream."""

    results: list[tuple[ClearingOutcome, list[str]]] = []
    cursor = 0
    for _price, demand, queue in snapshots:
        quantities = torch.tensor(
            [float(resting) for _oid, resting in queue], dtype=torch.float64
        )
        level_total = int(sum(resting for _oid, resting in queue))
        executed = min(demand, level_total)
        level_draws: tuple[int, ...] | None = None
        if kernel is Kernel.RANDOM_UNIT_WITHIN_PRICE:
            level_draws = tuple(draws[cursor : cursor + executed])
            cursor += executed
        outcome = exact_clearing(quantities, demand, kernel, level_draws)
        results.append((outcome, [oid for oid, _resting in queue]))
    return results


def _recorded_per_maker_quantities(
    queue: list[tuple[str, int]], executions: list[TapeRecord]
) -> list[float]:
    recorded = {order_id: 0 for order_id, _resting in queue}
    for record in executions:
        execution = record.payload["execution"]
        assert isinstance(execution, dict)
        maker = str(execution["maker_order_id"])
        assert maker in recorded
        recorded[maker] += int(execution["quantity"])
    return [float(recorded[order_id]) for order_id, _resting in queue]


# ---------------------------------------------------------------- fixture gate


def test_frozen_bundle_integrity_read_only() -> None:
    manifest = json.loads((BUNDLE / "bundle_manifest.json").read_text(encoding="utf-8"))
    files = manifest["files"]
    assert isinstance(files, dict) and len(files) == 7
    for relative, expected in files.items():
        digest = hashlib.sha256((BUNDLE / str(relative)).read_bytes()).hexdigest()
        assert digest == str(expected), relative
    assert manifest["fixtures"]["fixture_fifo"]["records"] == 21
    assert manifest["fixtures"]["fixture_random_unit_within_price"]["records"] == 22


@pytest.mark.parametrize("arm", ARMS)
def test_forward_exactness_reproduces_recorded_allocations(arm: str) -> None:
    """Every execution payload of the frozen arm is reproduced fill-by-fill."""

    _prestate, groups = _fixture_execution_groups(arm)
    assert groups, "frozen fixtures must contain at least one clearing group"
    for kernel, snapshots, executions in groups:
        draws = _draw_stream(kernel, executions)
        outcomes = _level_outcomes(kernel, snapshots, draws)
        cursor = 0
        for outcome, queue_ids in outcomes:
            fills = list(outcome.fills)
            _assert_fills_match_executions(
                fills, executions[cursor : cursor + len(fills)], queue_ids
            )
            assert int(outcome.allocation.sum()) == sum(fill.quantity for fill in fills)
            cursor += len(fills)
        assert cursor == len(executions)


@pytest.mark.parametrize("arm", ARMS)
def test_straight_through_forward_is_tape_exact(arm: str) -> None:
    """The public ST estimator's forward output equals the recorded allocation."""

    _prestate, groups = _fixture_execution_groups(arm)
    for kernel, snapshots, executions in groups:
        draws = _draw_stream(kernel, executions)
        outcomes = _level_outcomes(kernel, snapshots, draws)
        cursor = 0
        for outcome, _ids in outcomes:
            fills = list(outcome.fills)
            level_executions = executions[cursor : cursor + len(fills)]
            demand = snapshots[0][1]
            queue = snapshots[0][2]
            quantities = torch.tensor(
                [float(resting) for _oid, resting in queue], dtype=torch.float32
            )
            level_draws = tuple(draws) if kernel is Kernel.RANDOM_UNIT_WITHIN_PRICE else None
            allocation = straight_through_through_m(
                quantities, demand, kernel, level_draws
            )
            expected = torch.tensor(
                _recorded_per_maker_quantities(queue, level_executions),
                dtype=torch.float32,
            )
            assert torch.equal(allocation.detach(), expected)
            assert allocation.dtype == torch.float32
            cursor += len(fills)


@pytest.mark.parametrize("arm", ARMS)
def test_perturb_and_map_forward_on_fixtures(arm: str) -> None:
    """PAM reproduces the frozen fixtures' allocations because every touched
    level in both arms is single-maker, so perturbation cannot reorder it."""

    _prestate, groups = _fixture_execution_groups(arm)
    kernel = _kernel_for(arm)
    for _kernel, snapshots, executions in groups:
        draws = _draw_stream(kernel, executions)
        outcomes = _level_outcomes(_kernel, snapshots, draws)
        cursor = 0
        for outcome, _queue_ids in outcomes:
            fills = list(outcome.fills)
            level_executions = executions[cursor : cursor + len(fills)]
            queue = snapshots[0][2]
            quantities = torch.tensor(
                [float(resting) for _oid, resting in queue], dtype=torch.float64
            )
            pam = perturb_and_map_through_m(quantities, snapshots[0][1], kernel)
            expected = torch.tensor(
                _recorded_per_maker_quantities(queue, level_executions),
                dtype=torch.float64,
            )
            assert torch.equal(pam.detach(), expected)
            assert int(pam.sum()) == int(outcome.allocation.sum())
            cursor += len(fills)


# ------------------------------------------------------- synthetic autograd gate


def test_straight_through_gradient_identity_on_cleared_zero_on_uncleared() -> None:
    quantities = torch.tensor([3.0, 5.0, 2.0], requires_grad=True)
    weights = torch.tensor([1.0, 2.0, 3.0])
    allocation = straight_through_through_m(quantities, 6, Kernel.FIFO)
    assert torch.equal(allocation.detach(), torch.tensor([3.0, 3.0, 0.0]))
    (allocation * weights).sum().backward()
    assert quantities.grad is not None
    expected = PINNED_STRAIGHT_THROUGH_SCALE * weights * torch.tensor([1.0, 1.0, 0.0])
    assert torch.equal(quantities.grad, expected)
    uncleared = quantities.grad[allocation.detach() == 0]
    assert uncleared.numel() >= 1
    assert bool((uncleared == 0).all()), "uncleared coordinates must have exact zero grad"


def test_straight_through_random_unit_mask_and_draw_exactness() -> None:
    quantities = torch.tensor([2.0, 1.0, 3.0], requires_grad=True)
    weights = torch.tensor([0.5, -1.5, 2.0])
    allocation = straight_through_through_m(
        quantities, 2, Kernel.RANDOM_UNIT_WITHIN_PRICE, draws=(0, 1)
    )
    assert torch.equal(allocation.detach(), torch.tensor([1.0, 1.0, 0.0]))
    (allocation * weights).sum().backward()
    assert quantities.grad is not None
    assert torch.equal(
        quantities.grad,
        PINNED_STRAIGHT_THROUGH_SCALE * weights * torch.tensor([1.0, 1.0, 0.0]),
    )


def test_straight_through_scale_pinned_no_learned_scale() -> None:
    parameters = inspect.signature(straight_through_through_m).parameters
    assert "scale" not in parameters, "no caller-configurable scale may exist"
    assert PINNED_STRAIGHT_THROUGH_SCALE == 1.0
    quantities = torch.tensor([4.0], requires_grad=True)
    first = straight_through_through_m(quantities, 2, Kernel.FIFO)
    second = straight_through_through_m(quantities, 2, Kernel.FIFO)
    assert torch.equal(first.detach(), second.detach())
    first.backward(torch.tensor([3.0]))
    assert quantities.grad is not None
    assert torch.equal(
        quantities.grad, torch.tensor([PINNED_STRAIGHT_THROUGH_SCALE * 3.0])
    )


def test_perturb_and_map_sigma_limit_recovers_exact_mechanism_on_deterministic_arm() -> None:
    quantities = torch.tensor([2.0, 3.0, 4.0], dtype=torch.float64)
    exact = exact_clearing(quantities, 5, Kernel.FIFO)
    assert torch.equal(exact.allocation.to(torch.float64), torch.tensor([2.0, 3.0, 0.0]))
    for sigma in (1e-3, 1e-6, 1e-9, 0.0):
        limit = _perturbed_clearing(
            quantities, 5, Kernel.FIFO, sigma=sigma, seed=PINNED_PERTURB_AND_MAP_SEED
        )
        assert torch.equal(limit.allocation, exact.allocation)
        assert [fill.quantity for fill in limit.fills] == [
            fill.quantity for fill in exact.fills
        ]
        assert [fill.queue_index for fill in limit.fills] == [
            fill.queue_index for fill in exact.fills
        ]


def test_perturb_and_map_sigma_limit_on_fifo_fixture_recovers_recorded_allocation() -> None:
    _prestate, groups = _fixture_execution_groups("fixture_fifo")
    _kernel, snapshots, executions = groups[0]
    queue = snapshots[0][2]
    quantities = torch.tensor(
        [float(resting) for _oid, resting in queue], dtype=torch.float64
    )
    limit = _perturbed_clearing(
        quantities, snapshots[0][1], Kernel.FIFO, sigma=0.0, seed=PINNED_PERTURB_AND_MAP_SEED
    )
    expected = torch.tensor(
        _recorded_per_maker_quantities(queue, executions), dtype=torch.float64
    )
    assert torch.equal(limit.allocation.to(torch.float64), expected)


def test_perturb_and_map_same_seed_same_output_and_conservation() -> None:
    quantities = torch.tensor([2.0, 5.0, 1.0, 3.0], dtype=torch.float64)
    first = perturb_and_map_through_m(quantities, 4, Kernel.FIFO, seed=20260906)
    second = perturb_and_map_through_m(quantities, 4, Kernel.FIFO, seed=20260906)
    assert torch.equal(first, second)
    total = int(quantities.sum())
    for kernel in (Kernel.FIFO, Kernel.RANDOM_UNIT_WITHIN_PRICE):
        allocation = perturb_and_map_through_m(
            quantities, 4, kernel, seed=PINNED_PERTURB_AND_MAP_SEED
        )
        assert int(allocation.sum()) == min(4, total)
        assert bool(torch.equal(allocation > 0, (allocation > 0)))


def test_perturb_and_map_sigma_pinned() -> None:
    parameters = inspect.signature(perturb_and_map_through_m).parameters
    assert "sigma" not in parameters, "no caller-configurable sigma may exist"
    assert PINNED_PERTURB_AND_MAP_SIGMA == 1.0
    quantities = torch.tensor([2.0, 5.0, 1.0, 3.0], dtype=torch.float64)
    public = perturb_and_map_through_m(quantities, 3, Kernel.FIFO, seed=7)
    internal = _perturbed_clearing(
        quantities, 3, Kernel.FIFO, sigma=PINNED_PERTURB_AND_MAP_SIGMA, seed=7
    )
    assert torch.equal(public.detach(), internal.allocation.to(torch.float64))


def test_perturb_and_map_backward_is_masked_identity() -> None:
    quantities = torch.tensor([2.0, 5.0, 1.0], requires_grad=True)
    weights = torch.tensor([0.25, 0.5, 4.0])
    allocation = perturb_and_map_through_m(
        quantities, 4, Kernel.FIFO, seed=PINNED_PERTURB_AND_MAP_SEED
    )
    (allocation * weights).sum().backward()
    assert quantities.grad is not None
    expected = weights * (allocation.detach() > 0).to(weights.dtype)
    assert torch.equal(quantities.grad, expected)
    uncleared = quantities.grad[allocation.detach() == 0]
    if uncleared.numel():
        assert bool((uncleared == 0).all())


def test_cpu_device_guard() -> None:
    meta = torch.zeros(3, device="meta")
    with pytest.raises(ValueError, match="CPU-only"):
        straight_through_through_m(meta, 1, Kernel.FIFO)
    with pytest.raises(ValueError, match="CPU-only"):
        perturb_and_map_through_m(meta, 1, Kernel.FIFO)


def test_determinism_repeated_calls_bitwise() -> None:
    for kernel, draws in (
        (Kernel.FIFO, None),
        (Kernel.RANDOM_UNIT_WITHIN_PRICE, (0, 1)),
    ):
        quantities = torch.tensor([2.0, 1.0, 3.0], dtype=torch.float64)
        first = straight_through_through_m(quantities, 2, kernel, draws)
        second = straight_through_through_m(quantities, 2, kernel, draws)
        assert torch.equal(first, second)
        pam_first = perturb_and_map_through_m(quantities, 2, kernel)
        pam_second = perturb_and_map_through_m(quantities, 2, kernel)
        assert torch.equal(pam_first, pam_second)


def test_random_unit_draw_stream_validation() -> None:
    quantities = torch.tensor([2.0, 1.0])
    with pytest.raises(ValueError, match="draw stream"):
        exact_clearing(quantities, 2, Kernel.RANDOM_UNIT_WITHIN_PRICE, None)
    with pytest.raises(ValueError, match="does not match"):
        exact_clearing(quantities, 2, Kernel.RANDOM_UNIT_WITHIN_PRICE, draws=(0,))
    with pytest.raises(ValueError, match="outside eligible"):
        exact_clearing(quantities, 2, Kernel.RANDOM_UNIT_WITHIN_PRICE, draws=(0, 3))
    with pytest.raises(ValueError, match="outside eligible"):
        exact_clearing(quantities, 2, Kernel.RANDOM_UNIT_WITHIN_PRICE, draws=(0, -1))


# -------------------------------------- engine cross-check beyond the fixtures


def _multi_maker_prestate(rule: AllocationRule) -> SessionPrestate:
    actors = ("a", "b", "c", "d")
    return SessionPrestate(
        session_id="ESTIMATOR-ENGINE-CHECK",
        seed=11,
        allocation_rule=rule,
        initial_cash={actor: 100_000 for actor in actors},
        initial_inventory={actor: 100 for actor in actors},
        price_bands=(90, 110),
        actors=actors,
        induced_buy_values={"a": tuple(110 for _ in range(50))},
        induced_sell_costs={
            "b": tuple(90 for _ in range(50)),
            "c": tuple(90 for _ in range(50)),
            "d": tuple(90 for _ in range(50)),
        },
        information_schedule=(InformationRelease(0, "fundamental", 100),),
        initial_book=(
            InitialOrder("MA1", "b", Side.ASK, 101, 2),
            InitialOrder("MA2", "c", Side.ASK, 101, 3),
            InitialOrder("MA3", "d", Side.ASK, 101, 4),
        ),
        scheduler_seed=17,
        scheduler_tick=0,
        scheduler_state="check",
        assignment_key_commitment="check",
        latency_endowment=2,
        latency_delay_by_investment=(5, 3, 1),
    )


@pytest.mark.parametrize(
    ("rule", "kernel"),
    [
        (AllocationRule.FIFO, Kernel.FIFO),
        (AllocationRule.RANDOM_UNIT_WITHIN_PRICE, Kernel.RANDOM_UNIT_WITHIN_PRICE),
    ],
)
def test_exact_clearing_matches_engine_multi_maker_rationed_level(
    rule: AllocationRule, kernel: Kernel
) -> None:
    engine = ReferenceEngine(_multi_maker_prestate(rule))
    clocks = ThreeClocks(client_ts=1, receipt_ts=1, match_ts=1)
    engine.submit(
        OrderRequest(
            event_id=1,
            actor="a",
            client_order_id="buy-1",
            side=Side.BID,
            price=101,
            quantity=5,
            clocks=clocks,
            round_id=0,
        )
    )
    executions = [r for r in engine.tape if r.event_type == EventType.EXECUTION]
    assert executions, "the rationed multi-maker level must execute"
    quantities = torch.tensor([2.0, 3.0, 4.0], dtype=torch.float64)
    draws: tuple[int, ...] | None = None
    if kernel is Kernel.RANDOM_UNIT_WITHIN_PRICE:
        draws = tuple(_draw_stream(kernel, executions))
    outcome = exact_clearing(quantities, 5, kernel, draws)
    queue_ids = ["MA1", "MA2", "MA3"]
    _assert_fills_match_executions(list(outcome.fills), executions, queue_ids)
    assert int(outcome.allocation.sum()) == 5
    if kernel is Kernel.FIFO:
        # Only the FIFO kernel deterministically never clears MA3 on this
        # rationed level; random-unit may draw any resting unit.
        assert outcome.allocation.tolist()[2] == 0
        assert bool(outcome.filled_mask.tolist()[2]) is False
