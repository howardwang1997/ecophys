"""[D0 BUILD] Through-M wrapper fixture competence gate + bridge tests (E-3).

Build item E-3 of the D0 build register: the torch composition layer over the
exact reference engine (``ecomd/mechanisms/through_m_wrapper.py``). CPU-legal
pre-D0 spot checks only (single file, second-scale; no batch battery, no GPU,
no training, no market data, no outcome access).

The frozen A-2 exit bundle at experiments/lab_asset_a2/a2_exit_20260905/ is
consumed STRICTLY read-only: per-file sha256 re-verified against
bundle_manifest.json before any claim, fixtures replayed in memory only,
nothing written.

Competence gate (spec section 2.3):
(i) ST forward reproduces the recorded tape byte-exactly at horizon one — G6
    semantics via the lab-asset replay validator, PLUS fill-by-fill bridge
    reproduction with engine-RNG-state threading (both arms, both kernels);
(ii) PAM at noise 0 reduces to the exact kernel (deterministic arms; the
    estimator menu's own scoping).
"""

from __future__ import annotations

import hashlib
import inspect
import json
import sys
from pathlib import Path
from typing import Any, cast

import pytest
import torch
from torch import Tensor

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
for _entry in (str(REPO_ROOT), str(SCRIPTS)):
    if _entry not in sys.path:
        sys.path.insert(0, _entry)

from lab_asset.matching import ReferenceEngine  # noqa: E402
from lab_asset.replay import regenerate, replay  # noqa: E402
from lab_asset.schema import EventType, TapeRecord, record_to_json  # noqa: E402

from ecomd.mechanisms.through_m import (  # noqa: E402
    PINNED_STRAIGHT_THROUGH_SCALE,
    Kernel,
    _perturbed_clearing,
    exact_clearing,
)
from ecomd.mechanisms.through_m_wrapper import (  # noqa: E402
    NOMINAL_LEVEL_PRICE,
    SUBSTREAM_NAME_ORDER,
    BridgeState,
    TrainKernelStream,
    compose_round,
    engine_execute_level,
    perturb_and_map_hook,
    perturb_and_map_level,
    straight_through_hook,
    straight_through_level,
    train_kernel_substream_seed,
)
from tests.test_through_m_estimators import (  # noqa: E402
    _crossed_level_snapshots,
    _dispatch,
    _kernel_for,
    load_arm,
)

BUNDLE = REPO_ROOT / "experiments/lab_asset_a2/a2_exit_20260905"
ARMS = ("fixture_fifo", "fixture_random_unit_within_price")


def _backward(scalar: Tensor) -> None:
    scalar.backward()  # type: ignore[no-untyped-call]


def _grad_of(leaf: Tensor) -> Tensor:
    grad = leaf.grad
    assert grad is not None
    return grad


# ─────────────────────────────────────────────────────────────────────────────
# Read-only bundle integrity
# ─────────────────────────────────────────────────────────────────────────────


def test_frozen_bundle_integrity_read_only() -> None:
    manifest = json.loads((BUNDLE / "bundle_manifest.json").read_text(encoding="utf-8"))
    for relative, expected in manifest["files"].items():
        digest = hashlib.sha256((BUNDLE / str(relative)).read_bytes()).hexdigest()
        assert digest == expected, f"bundle file changed: {relative}"


# ─────────────────────────────────────────────────────────────────────────────
# (i) Fixture competence gate
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("arm", ARMS)
def test_engine_path_reproduces_recorded_tape_byte_exactly(arm: str) -> None:
    """G6 horizon-one semantics: the engine execution path the wrapper drives
    (ReferenceEngine.submit) reproduces the recorded tape record-by-record,
    including every state hash, via the lab-asset replay validator."""

    prestate, tape = load_arm(arm)
    report = replay(prestate, tape)
    assert report.ok, str(report)
    regenerated = regenerate(prestate, tape)
    for produced, recorded in zip(regenerated, tape, strict=True):
        assert produced.sequence == recorded.sequence
        assert produced.event_type == recorded.event_type
        assert produced.pre_state_hash == recorded.pre_state_hash
        assert produced.post_state_hash == recorded.post_state_hash
        assert produced.pre_aggregate_state_hash == recorded.pre_aggregate_state_hash
        assert produced.post_aggregate_state_hash == recorded.post_aggregate_state_hash
        assert record_to_json(produced) == record_to_json(recorded)


_BridgeRound = tuple[
    list[tuple[int, int, list[tuple[str, int]]]], tuple[Any, ...], list[TapeRecord]
]


def _bridge_rounds(arm: str) -> list[_BridgeRound]:
    """Shadow-replay the arm; per crossing request capture (crossed-level
    snapshots, pre-request engine RNG state, recorded execution records)."""

    prestate, tape = load_arm(arm)
    assert replay(prestate, tape).ok
    engine = ReferenceEngine(prestate)
    rounds: list[_BridgeRound] = []
    for record in tape:
        snapshots = None
        rng_state = None
        if record.event_type == EventType.ORDER_REQUEST:
            snapshots = _crossed_level_snapshots(engine, record)
            rng_state = engine.rng.getstate()
        before = len(engine.tape)
        _dispatch(engine, record)
        executions = [
            r for r in engine.tape[before:] if r.event_type == EventType.EXECUTION
        ]
        if executions:
            assert snapshots is not None and rng_state is not None
            rounds.append((snapshots, rng_state, executions))
    return rounds


@pytest.mark.parametrize("arm", ARMS)
def test_bridge_reproduces_recorded_round_fills_exactly(arm: str) -> None:
    """The wrapper's engine bridge reproduces every recorded execution
    fill-by-fill, walking the crossed levels best-first and threading the
    engine RNG state across levels (the random-unit draw stream)."""

    kernel = _kernel_for(arm)
    rounds = _bridge_rounds(arm)
    assert rounds
    for snapshots, rng_state, executions in rounds:
        threaded: tuple[Any, ...] | None = (
            rng_state if kernel is Kernel.RANDOM_UNIT_WITHIN_PRICE else None
        )
        cursor = 0
        for price, demand, queue in snapshots:
            quantities = torch.tensor([float(resting) for _, resting in queue])
            outcome = engine_execute_level(
                quantities, demand, level_price=price, kernel=kernel, rng_state=threaded
            )
            level_records = executions[cursor : cursor + len(outcome.fills)]
            assert len(outcome.fills) == len(level_records)
            for fill, recorded in zip(outcome.fills, level_records, strict=True):
                payload = recorded.payload
                execution = payload["execution"]
                assert isinstance(execution, dict)
                assert [order_id for order_id, _ in queue][fill.queue_index] == str(
                    execution["maker_order_id"]
                )
                assert fill.quantity == int(execution["quantity"])
                assert fill.maker_remaining_after == int(execution["maker_remaining"])
                if fill.selected_unit is not None:
                    draw = payload["allocation_draw"]
                    assert isinstance(draw, dict)
                    assert fill.eligible_units == int(draw["eligible_units"])
                    assert fill.selected_unit == int(draw["selected_unit"])
            threaded = outcome.post_rng_state
            cursor += len(outcome.fills)
        assert cursor == len(executions)


# ─────────────────────────────────────────────────────────────────────────────
# (ii) PAM noise-zero reduction
# ─────────────────────────────────────────────────────────────────────────────


def test_pam_noise_zero_reduces_to_exact_kernel() -> None:
    pools = [
        torch.tensor([2.0, 3.0, 4.0]),
        torch.tensor([5.0, 4.0, 3.0, 2.0]),
        torch.tensor([7.0]),
        torch.tensor([1.0, 1.0, 1.0, 1.0, 1.0]),
    ]
    for pool in pools:
        total = int(pool.sum())
        for demand in range(1, total + 2):
            exact = exact_clearing(pool, demand, Kernel.FIFO)
            limit = _perturbed_clearing(
                pool, demand, Kernel.FIFO, sigma=0.0, seed=0
            )
            assert torch.equal(limit.allocation, exact.allocation)
            assert torch.equal(limit.filled_mask, exact.filled_mask)

    # Deterministic-arm equivalence through the wrapper: the PAM backward mask
    # at zero noise equals the engine's exact cleared mask.
    quantities = torch.tensor([3.0, 5.0, 2.0])
    outcome = engine_execute_level(quantities, 6, level_price=7, kernel=Kernel.FIFO)
    limit = _perturbed_clearing(quantities, 6, Kernel.FIFO, sigma=0.0, seed=0)
    assert torch.equal(limit.filled_mask, outcome.filled_mask)

    # Single-maker pools: both kernels collapse to the same allocation, so
    # zero-noise PAM matches the exact kernel on this stratum too (draws are
    # pinned to the only maker).
    single = torch.tensor([6.0])
    assert torch.equal(
        _perturbed_clearing(single, 4, Kernel.FIFO, sigma=0.0, seed=0).allocation,
        exact_clearing(single, 4, Kernel.FIFO).allocation,
    )
    assert torch.equal(
        _perturbed_clearing(single, 4, Kernel.RANDOM_UNIT_WITHIN_PRICE, sigma=0.0, seed=0).allocation,
        exact_clearing(single, 4, Kernel.RANDOM_UNIT_WITHIN_PRICE, draws=[0, 0, 0, 0]).allocation,
    )

    # Multi-maker random-unit pools: sigma=0 reduces to the kernel-fixed
    # depleting-argmax MAP rule (NOT the draw law) — hand-computed here:
    # (2,5,1) walks argmax -> slot 1 three times, then the (2,2,1) tie
    # resolves to the lower index (torch.argmax's pinned CPU behavior).
    pool = torch.tensor([2.0, 5.0, 1.0])
    assert _perturbed_clearing(
        pool, 3, Kernel.RANDOM_UNIT_WITHIN_PRICE, sigma=0.0, seed=0
    ).allocation.tolist() == [0, 3, 0]
    assert _perturbed_clearing(
        pool, 4, Kernel.RANDOM_UNIT_WITHIN_PRICE, sigma=0.0, seed=0
    ).allocation.tolist() == [1, 3, 0]


# ─────────────────────────────────────────────────────────────────────────────
# ST backward: masked identity with the pinned scale
# ─────────────────────────────────────────────────────────────────────────────


def test_straight_through_backward_is_masked_identity_with_pinned_scale() -> None:
    weights = torch.tensor([1.0, 2.0, 3.0])

    quantities = torch.tensor([3.0, 5.0, 2.0], requires_grad=True)
    outcome = straight_through_level(quantities, 6, level_price=7, kernel=Kernel.FIFO)
    # Hand-computed forward: FIFO fills (3, 3, 0) — third slot never cleared.
    assert torch.equal(outcome.allocation.detach(), torch.tensor([3.0, 3.0, 0.0]))
    _backward((outcome.allocation * weights).sum())
    assert torch.equal(
        _grad_of(quantities),
        PINNED_STRAIGHT_THROUGH_SCALE * weights * torch.tensor([1.0, 1.0, 0.0]),
    )

    # Random-unit kernel: same masked-identity law, mask derived from the
    # engine's realized allocation.
    quantities = torch.tensor([2.0, 4.0, 1.0], requires_grad=True)
    outcome = straight_through_level(
        quantities,
        3,
        level_price=9,
        kernel=Kernel.RANDOM_UNIT_WITHIN_PRICE,
        engine_seed=5,
    )
    mask = (outcome.allocation.detach() > 0).to(torch.float64)
    _backward((outcome.allocation * weights).sum())
    assert torch.equal(
        _grad_of(quantities), PINNED_STRAIGHT_THROUGH_SCALE * weights * mask
    )

    # The hook variant is the same estimator.
    hook = straight_through_hook(kernel=Kernel.FIFO, seed_root=11000)
    quantities = torch.tensor([3.0, 5.0, 2.0], requires_grad=True)
    _backward((hook(quantities, 6) * weights).sum())
    assert torch.equal(_grad_of(quantities), torch.tensor([1.0, 2.0, 0.0]))


# ─────────────────────────────────────────────────────────────────────────────
# PAM gradients + substream determinism
# ─────────────────────────────────────────────────────────────────────────────


def test_pam_gradient_finiteness_and_substream_determinism() -> None:
    weights = torch.tensor([4.0, 1.0, 3.0, 2.0])
    demands = (1, 3, 10)
    for kernel in (Kernel.FIFO, Kernel.RANDOM_UNIT_WITHIN_PRICE):
        first = perturb_and_map_hook(kernel=kernel, seed_root=11000)
        replayed = perturb_and_map_hook(kernel=kernel, seed_root=11000)
        for demand in demands:
            source = torch.tensor([4.0, 1.0, 3.0, 2.0], requires_grad=True)
            mirror = torch.tensor([4.0, 1.0, 3.0, 2.0], requires_grad=True)
            allocation = first(source, demand)
            mirror_allocation = replayed(mirror, demand)
            assert torch.equal(allocation, mirror_allocation)
            _backward((allocation * weights).sum())
            _backward((mirror_allocation * weights).sum())
            assert bool(torch.isfinite(_grad_of(source)).all())
            assert torch.equal(_grad_of(source), _grad_of(mirror))

    # Different roots derive different substream seeds (stream separation).
    assert train_kernel_substream_seed(11000) != train_kernel_substream_seed(12000)

    # Explicit-seed entry point: byte-identical allocations across calls.
    quantities = torch.tensor([4.0, 1.0, 3.0, 2.0], requires_grad=True)
    again = torch.tensor([4.0, 1.0, 3.0, 2.0], requires_grad=True)
    wrapped_a = perturb_and_map_level(
        quantities, 3, level_price=5, kernel=Kernel.RANDOM_UNIT_WITHIN_PRICE, pam_seed=7
    )
    wrapped_b = perturb_and_map_level(
        again, 3, level_price=5, kernel=Kernel.RANDOM_UNIT_WITHIN_PRICE, pam_seed=7
    )
    assert torch.equal(wrapped_a.allocation, wrapped_b.allocation)
    # Forward is the engine's exact integer output regardless of PAM noise.
    exact = engine_execute_level(
        torch.tensor([4.0, 1.0, 3.0, 2.0]),
        3,
        level_price=5,
        kernel=Kernel.RANDOM_UNIT_WITHIN_PRICE,
        engine_seed=0,
    )
    assert torch.equal(wrapped_a.allocation_exact, exact.allocation_exact)


def test_rng_tree_matches_e2_derivation() -> None:
    from lab_asset.dgp_request_generator import SUBSTREAM_NAMES, named_substream_seed

    assert SUBSTREAM_NAME_ORDER == SUBSTREAM_NAMES
    for root in (0, 1, 42, 11000, 11029, 12000, 20260905):
        assert train_kernel_substream_seed(root) == named_substream_seed(
            root, "train_kernel"
        )

    stream = TrainKernelStream(11000)
    mirror = TrainKernelStream(11000)
    calls = [stream.next_call_seeds() for _ in range(4)]
    assert calls == [mirror.next_call_seeds() for _ in range(4)]
    assert stream.calls == 4
    # Child k of the train_kernel node: tail-indexed derivation agrees.
    assert train_kernel_substream_seed(11000, 2) != train_kernel_substream_seed(11000, 3)


# ─────────────────────────────────────────────────────────────────────────────
# Kernel-blindness of the input interface
# ─────────────────────────────────────────────────────────────────────────────


def test_input_interface_is_kernel_blind() -> None:
    hooks = {
        kernel: straight_through_hook(kernel=kernel, seed_root=7)
        for kernel in (Kernel.FIFO, Kernel.RANDOM_UNIT_WITHIN_PRICE)
    }
    for hook in hooks.values():
        parameters = list(inspect.signature(hook).parameters)
        assert parameters == ["quantities", "demand"]
        pool = torch.tensor([2.0, 3.0])
        allocation = hook(pool, 2)
        assert allocation.shape == pool.shape
        assert allocation.dtype == pool.dtype
        with pytest.raises(ValueError):
            hook(torch.tensor([1.5, 2.0]), 2)  # off the integer lattice
        with pytest.raises(ValueError):
            hook(pool, 0)  # demand must be positive

    # Single-maker pools: the two kernels allocate identically (the collapse
    # stratum where the draw law and FIFO agree), so the input interface
    # carries no kernel channel.
    single = torch.tensor([5.0])
    for demand in (1, 3, 5, 9):
        fifo = hooks[Kernel.FIFO](single, demand)
        random_unit = hooks[Kernel.RANDOM_UNIT_WITHIN_PRICE](single, demand)
        assert torch.equal(fifo.detach(), random_unit.detach())


# ─────────────────────────────────────────────────────────────────────────────
# Integer-exact conservation through the bridge
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "kernel", (Kernel.FIFO, Kernel.RANDOM_UNIT_WITHIN_PRICE)
)
def test_integer_exact_conservation_through_bridge(kernel: Kernel) -> None:
    pools = [[3, 5, 2], [1, 1, 4], [6], [2, 2, 2, 2], [0, 3, 0]]
    price = 7
    for pool in pools:
        for demand in (1, 4, 10):
            outcome = engine_execute_level(
                torch.tensor([float(qty) for qty in pool]),
                demand,
                level_price=price,
                kernel=kernel,
                engine_seed=11,
            )
            executed = min(demand, sum(pool))
            assert outcome.executed_units == executed
            assert int(outcome.allocation_exact.sum()) == executed
            assert outcome.channels_delta.dtype == torch.int64
            assert outcome.channels_delta.tolist() == [executed, price * executed]
            assert outcome.resting_after.dtype == torch.int64
            assert outcome.resting_after.tolist() == [
                qty - filled
                for qty, filled in zip(pool, outcome.allocation_exact.tolist(), strict=True)
            ]
            assert sum(delta for _, delta in outcome.cash_delta) == 0
            assert sum(delta for _, delta in outcome.inventory_delta) == 0
            assert dict(outcome.cash_delta)["AGG"] == -price * executed
            assert dict(outcome.inventory_delta)["AGG"] == executed


def test_multiround_compose_channels_accumulate_integer_exact() -> None:
    flows = [([4, 3], 2, 5), ([2, 3], 4, 5), ([1, 2], 3, 6)]
    state: BridgeState | None = None
    expected_volume = 0
    expected_cash = 0
    for pool, demand, price in flows:
        outcome = engine_execute_level(
            torch.tensor([float(qty) for qty in pool]),
            demand,
            level_price=price,
            kernel=Kernel.FIFO,
        )
        state = compose_round(state, outcome)
        executed = min(demand, sum(pool))
        expected_volume += executed
        expected_cash += price * executed
        assert state is not None
        assert state.channels.dtype == torch.int64
        assert state.channels.tolist() == [expected_volume, expected_cash]
        assert torch.equal(state.resting, outcome.resting_after)


def test_engine_bridge_byte_determinism() -> None:
    quantities = torch.tensor([2.0, 4.0, 1.0])
    first = engine_execute_level(
        quantities, 3, level_price=9, kernel=Kernel.RANDOM_UNIT_WITHIN_PRICE, engine_seed=5
    )
    second = engine_execute_level(
        quantities, 3, level_price=9, kernel=Kernel.RANDOM_UNIT_WITHIN_PRICE, engine_seed=5
    )
    assert first.engine_tape == second.engine_tape
    assert torch.equal(first.allocation_exact, second.allocation_exact)
    assert first.post_aggregate_digest == second.post_aggregate_digest
    assert first.post_rng_state == second.post_rng_state

    # rng_state injection pins the draw stream across calls.
    resumed_a = engine_execute_level(
        quantities, 3, level_price=9, kernel=Kernel.RANDOM_UNIT_WITHIN_PRICE,
        rng_state=first.post_rng_state,
    )
    resumed_b = engine_execute_level(
        quantities, 3, level_price=9, kernel=Kernel.RANDOM_UNIT_WITHIN_PRICE,
        rng_state=first.post_rng_state,
    )
    assert resumed_a.engine_tape == resumed_b.engine_tape
    assert torch.equal(resumed_a.allocation_exact, resumed_b.allocation_exact)
    assert resumed_a.post_rng_state == resumed_b.post_rng_state


def test_invalid_inputs_rejected() -> None:
    valid = torch.tensor([2.0, 3.0])
    with pytest.raises(ValueError):
        engine_execute_level(torch.tensor([1.5, 2.0]), 2, level_price=5, kernel=Kernel.FIFO)
    with pytest.raises(ValueError):
        engine_execute_level(valid, 0, level_price=5, kernel=Kernel.FIFO)
    with pytest.raises(ValueError):
        # bool demand passes mypy (bool subclasses int) but is rejected at runtime
        engine_execute_level(valid, True, level_price=5, kernel=Kernel.FIFO)
    with pytest.raises(ValueError):
        engine_execute_level(valid, 2, level_price=0, kernel=Kernel.FIFO)
    with pytest.raises(ValueError):
        engine_execute_level(valid, 2, level_price=5, kernel=Kernel.FIFO, engine_seed=-1)
    with pytest.raises(ValueError):
        straight_through_level(
            torch.tensor([2, 3], dtype=torch.int64), 2, level_price=5, kernel=Kernel.FIFO
        )
    with pytest.raises(ValueError):
        perturb_and_map_level(
            valid, 2, level_price=5, kernel=Kernel.FIFO, pam_seed=-2
        )
    with pytest.raises(ValueError):
        straight_through_hook(kernel=Kernel.FIFO)
    with pytest.raises(ValueError):
        straight_through_hook(
            kernel=Kernel.FIFO, stream=TrainKernelStream(1), seed_root=1
        )


# ─────────────────────────────────────────────────────────────────────────────
# L2-2 attach surface: hooks plug into RecurrentFactSurrogate
# ─────────────────────────────────────────────────────────────────────────────


def test_hooks_attach_to_recurrent_fact_surrogate() -> None:
    from ecomd.models.fact_surrogate import (
        FEXEC_ROUND_FEATURES,
        FactSurrogateBatch,
        FactSurrogateConfig,
        RecurrentFactSurrogate,
    )

    generator = torch.Generator().manual_seed(7)
    model = RecurrentFactSurrogate(
        FactSurrogateConfig(d_hidden=4, n_slots=3), generator=generator
    )
    batch = FactSurrogateBatch(
        features=torch.randn(1, 2, len(FEXEC_ROUND_FEATURES), generator=generator),
        channels=torch.zeros(1, 2, 2),
        slot_prices=torch.tensor([[[5.0, 0.0, 0.0], [6.0, 0.0, 0.0]]]),
        channels_init=torch.zeros(1, 2),
    )
    for hook_factory in (straight_through_hook, perturb_and_map_hook):
        for kernel in (Kernel.FIFO, Kernel.RANDOM_UNIT_WITHIN_PRICE):
            hook = hook_factory(kernel=kernel, seed_root=11000)
            output = model(batch, mechanism=hook)
            assert output.mechanism_channels is not None
            values = cast(Tensor, output.mechanism_channels)
            assert values.shape == (1, 2, 2)
            assert bool(torch.isfinite(values).all())
            assert torch.equal(values, torch.round(values))  # integer lattice
            _backward(values.sum())
            grads = [p.grad for p in model.parameters() if p.grad is not None]
            assert grads and all(bool(torch.isfinite(g).all()) for g in grads)
            model.zero_grad(set_to_none=True)
    assert NOMINAL_LEVEL_PRICE == 1
