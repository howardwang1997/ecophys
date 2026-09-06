"""Through-M wrapper: the torch composition bridge onto ReferenceEngine (E-3).

Build item E-3 of the D0 build register (simulator contracts section 2.3 items
L1-3a/L1-3b and section 4; prereg v2 section 5). This module is the
composition layer EXTERNAL to ``ecomd/models/ecomd_v2.py`` and ``ecomd.py``
(both untouched): it intercepts a predicted round-t flow tensor, executes it
through the exact integer engine ``M`` — ``scripts/lab_asset/matching.py``
``ReferenceEngine.submit`` with allocation kernel ``fifo`` or
``random_unit_within_price`` — and returns the engine's post-round anonymous
state and conserving channels as torch tensors for the next input.

Bridge granularity (the frozen hook shape): ``ecomd.models.fact_surrogate``
pins ``MechanismEstimator = Callable[[Tensor, int], Tensor]`` — "resting
quantities of one touched level, demand -> allocation" — so the engine bridge
is per PRICE LEVEL. One call builds a synthetic single-level lab-asset-v3
session (one resting ask per nonzero slot at ``level_price`` in slot order, a
buyer aggressor "AGG" submitting exactly ``demand`` at ``level_price``, cash
and inventory endowments sized so no validation channel can ever fire) and
submits that single order through the unmodified engine. Multi-level rounds
compose by per-level calls threading ``rng_state`` (the random-unit kernel's
draw stream is the engine RNG state itself, which ``state_hash`` binds into
every record). The aggressor side is fixed to BUY: within-level fills,
allocations and channels are side-symmetric, and pins make the synthetic
session a pure function of its arguments.

Estimator composition (consume, never re-implement): forward is ALWAYS the
engine's exact integer output; backward reuses the frozen autograd Functions
of ``ecomd.mechanisms.through_m`` — ``_StraightThrough`` (pinned-scale masked
identity) for the primary estimator and ``_PerturbAndMap`` (mask of the
perturbed-MAP selection) for the audit estimator, whose noise comes from
``_perturbed_clearing`` at the pinned sigma. Scale value, noise law and mask
rule are therefore the module-level frozen constants of ``through_m``, and
the seed discipline below makes every stochastic consumer draw from the named
``train_kernel`` substream.

RNG discipline (contract C1; E-2's derivation): ``TrainKernelStream`` walks
the children of the seed tree's ``train_kernel`` node —
``SeedSequence(entropy=root, spawn_key=(3, k))``, child ``k`` consumed at the
``k``-th mechanism call — and splits each child into (engine draw seed, PAM
noise seed). The stream is estimator-blind and advances once per call, so the
same call sequence replays identically across all through-M arms within a
seed (C2 note 3). Stateful ``rng_state`` threading (for tape reproduction)
and stateless explicit seeds are both byte-deterministic.

Determinism: every entry point is CPU-only, has no global-RNG consumer, and
is a pure function of its explicit arguments; identical inputs give
byte-identical outputs (tapes, allocations, gradients).

The fixture competence gate for this module lives in
``tests/test_through_m_wrapper.py``: (i) ST forward reproduces the recorded
frozen-bundle tapes byte-exactly at horizon one (G6 semantics via the
lab-asset replay validator plus fill-by-fill bridge reproduction with RNG
threading); (ii) PAM at noise 0 reduces to the exact kernel on deterministic
arms. No training, no models persisted, no market data, no outcome access.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Final, cast

import numpy as np
import torch
from torch import Tensor

from ..models.fact_surrogate import MechanismEstimator
from .through_m import (
    PINNED_PERTURB_AND_MAP_SIGMA,
    PINNED_STRAIGHT_THROUGH_SCALE,
    Fill,
    Kernel,
    _PerturbAndMap,
    _perturbed_clearing,
    _StraightThrough,
    _validated_quantities,
)

__all__ = [
    "BRIDGE_SCHEMA_VERSION",
    "CHANNEL_ORDER",
    "NOMINAL_LEVEL_PRICE",
    "SUBSTREAM_NAME_ORDER",
    "BridgeState",
    "LevelOutcome",
    "TrainKernelStream",
    "compose_round",
    "engine_execute_level",
    "perturb_and_map_hook",
    "perturb_and_map_level",
    "straight_through_hook",
    "straight_through_level",
    "train_kernel_substream_seed",
]

BRIDGE_SCHEMA_VERSION: Final[str] = "lab-asset-v3"
CHANNEL_ORDER: Final[tuple[str, ...]] = ("volume_units", "cash_ticks")
SUBSTREAM_NAME_ORDER: Final[tuple[str, ...]] = ("data", "init", "minibatch", "train_kernel")
TRAIN_KERNEL_SPAWN_KEY: Final[int] = SUBSTREAM_NAME_ORDER.index("train_kernel")
BRIDGE_SESSION_ID: Final[str] = "ecomd.mechanisms.through_m_wrapper"
BRIDGE_CLIENT_ORDER_ID: Final[str] = "THROUGH-M-BRIDGE-1"
AGGRESSOR_ACTOR: Final[str] = "AGG"
NOMINAL_LEVEL_PRICE: Final[int] = 1
RandomState = tuple[Any, ...]


# ─────────────────────────────────────────────────────────────────────────────
# RNG tree: the named train_kernel substream (contract C1 / C2 note 3)
# ─────────────────────────────────────────────────────────────────────────────


def train_kernel_substream_seed(seed_root: int, *tail: int) -> int:
    """Seed of the ``train_kernel`` substream node (E-2's derivation).

    ``SeedSequence(entropy=root, spawn_key=(3, *tail))`` — exactly the
    ``spawn`` children of the frozen ordered name tuple, so the seed equals
    ``lab_asset.dgp_request_generator.named_substream_seed(root,
    "train_kernel")`` at ``tail=()``.
    """

    if seed_root < 0:
        raise ValueError("seed_root must be nonnegative")
    if any(part < 0 for part in tail):
        raise ValueError("tail indices must be nonnegative")
    child = np.random.SeedSequence(entropy=seed_root, spawn_key=(TRAIN_KERNEL_SPAWN_KEY, *tail))
    return int(child.generate_state(1, dtype=np.uint32)[0])


class TrainKernelStream:
    """One seed-spawned ``train_kernel`` stream replayed across through-M arms.

    Call ``k`` draws child ``k`` of the ``train_kernel`` node and splits it
    into (engine draw seed, PAM noise seed). Advancement is estimator-blind:
    both estimators on the same stream position see the same split, and the
    same call sequence replays byte-identically.
    """

    def __init__(self, seed_root: int) -> None:
        if seed_root < 0:
            raise ValueError("seed_root must be nonnegative")
        self._seed_root = seed_root
        self._calls = 0

    @property
    def seed_root(self) -> int:
        return self._seed_root

    @property
    def calls(self) -> int:
        return self._calls

    @property
    def substream_seed(self) -> int:
        return train_kernel_substream_seed(self._seed_root)

    def next_call_seeds(self) -> tuple[int, int]:
        child = np.random.SeedSequence(
            entropy=self._seed_root, spawn_key=(TRAIN_KERNEL_SPAWN_KEY, self._calls)
        )
        self._calls += 1
        state = child.generate_state(2, dtype=np.uint32)
        return int(state[0]), int(state[1])


# ─────────────────────────────────────────────────────────────────────────────
# Bridge outcomes and round-state composition
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class LevelOutcome:
    """One level-clearing through the exact engine.

    ``allocation`` is the engine's integer output in ``quantities.dtype``
    (autograd-attached in the estimator entry points; a detached cast in
    :func:`engine_execute_level`); ``allocation_exact`` is the int64 truth.
    ``resting_after`` is the post-round anonymous state (per-slot remaining
    resting quantities). ``channels_delta`` is the (2,) int64 conserving
    increment in ``CHANNEL_ORDER``. ``cash_delta``/``inventory_delta`` are the
    engine's integer-exact zero-sum ledger deltas (audit surface).
    ``post_rng_state``/``post_aggregate_digest``/``engine_tape`` are the
    engine's post-round state fingerprint (the RNG state is bound into every
    record's state hash) and the full serialized bridge tape.
    """

    allocation: Tensor
    allocation_exact: Tensor
    filled_mask: Tensor
    fills: tuple[Fill, ...]
    resting_after: Tensor
    channels_delta: Tensor
    executed_units: int
    cash_delta: tuple[tuple[str, int], ...]
    inventory_delta: tuple[tuple[str, int], ...]
    post_rng_state: RandomState
    post_aggregate_digest: str
    engine_tape: tuple[str, ...]


@dataclass(frozen=True)
class BridgeState:
    """Post-round state handed to the next input: conserving channels plus the
    engine-truth resting grid of the most recent level."""

    channels: Tensor
    resting: Tensor


def compose_round(state: BridgeState | None, outcome: LevelOutcome) -> BridgeState:
    """Fold one level outcome into the threaded bridge state (integer-exact)."""

    base = state.channels if state is not None else torch.zeros(2, dtype=torch.int64)
    return BridgeState(
        channels=base + outcome.channels_delta,
        resting=outcome.resting_after,
    )


# ─────────────────────────────────────────────────────────────────────────────
# The Python<->torch engine bridge
# ─────────────────────────────────────────────────────────────────────────────


def _maker_actor(slot: int) -> str:
    return f"MK{slot}"


def _maker_order_id(slot: int) -> str:
    return f"K{slot:04d}"


def _slot_from_order_id(order_id: str) -> int:
    return int(order_id[1:])


def _ensure_lab_asset_importable() -> None:
    """Make ``scripts/lab_asset`` importable from contexts that do not carry
    the scripts path (e.g. ecomd training loops calling the hooks)."""

    scripts = Path(__file__).resolve().parents[2] / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))


def engine_execute_level(
    quantities: Tensor,
    demand: int,
    *,
    level_price: int,
    kernel: Kernel,
    engine_seed: int = 0,
    rng_state: RandomState | None = None,
) -> LevelOutcome:
    """Execute one touched level through the exact integer engine.

    Builds the synthetic single-level session (module docstring), injects
    ``rng_state`` into the engine RNG when supplied (tape reproduction),
    submits one marketable buy order of size ``demand`` at ``level_price``
    through ``ReferenceEngine.submit``, and reads the engine's post-round
    state. Pure forward: no autograd, no estimator backward, no stochastic
    consumer besides the engine's own RNG. ``quantities`` may be integer or
    floating dtype (integer-valued either way).
    """

    _ensure_lab_asset_importable()
    from lab_asset.matching import ReferenceEngine
    from lab_asset.schema import (
        AllocationRule,
        EventType,
        InitialOrder,
        OrderRequest,
        SessionPrestate,
        Side,
        ThreeClocks,
        record_to_json,
    )

    resting = _validated_quantities(quantities)
    if not isinstance(demand, int) or isinstance(demand, bool) or demand < 1:
        raise ValueError("incoming demand must be a positive integer")
    if level_price < 1:
        raise ValueError("level_price must be a positive integer tick")
    if engine_seed < 0:
        raise ValueError("engine_seed must be nonnegative")

    actors = (
        AGGRESSOR_ACTOR,
        *(_maker_actor(slot) for slot, qty in enumerate(resting) if qty > 0),
    )
    # Endowment slack: the aggressor can always pay for the full demand and
    # every maker holds its own resting quantity, so no validation channel
    # (bands, cash, inventory, self-trade, duplicate ids) can ever fire.
    cash = level_price * demand + 1
    inventory = sum(resting) + 1
    prestate = SessionPrestate(
        session_id=BRIDGE_SESSION_ID,
        seed=engine_seed,
        allocation_rule=AllocationRule(kernel.value),
        initial_cash={actor: cash for actor in actors},
        initial_inventory={actor: inventory for actor in actors},
        price_bands=(level_price, level_price),
        actors=actors,
        initial_book=tuple(
            InitialOrder(
                order_id=_maker_order_id(slot),
                actor=_maker_actor(slot),
                side=Side.ASK,
                price=level_price,
                quantity=qty,
            )
            for slot, qty in enumerate(resting)
            if qty > 0
        ),
        actor_roles={actor: "aggressor" if actor == AGGRESSOR_ACTOR else "maker"
                     for actor in actors},
        schema_version=BRIDGE_SCHEMA_VERSION,
    )
    engine = ReferenceEngine(prestate)
    if rng_state is not None:
        engine.rng.setstate(rng_state)
    cash_before = dict(engine.cash)
    inventory_before = dict(engine.inventory)
    engine.submit(
        OrderRequest(
            event_id=1,
            actor=AGGRESSOR_ACTOR,
            client_order_id=BRIDGE_CLIENT_ORDER_ID,
            side=Side.BID,
            price=level_price,
            quantity=demand,
            clocks=ThreeClocks(0, 0, 0),
            round_id=0,
        )
    )

    slots = len(resting)
    allocation: list[int] = [0] * slots
    fills: list[Fill] = []
    for record in engine.tape:
        if record.event_type is not EventType.EXECUTION:
            continue
        payload = record.payload
        execution = payload["execution"]
        if not isinstance(execution, dict):
            raise TypeError("bridge engine produced a non-mapping execution payload")
        slot = _slot_from_order_id(str(execution["maker_order_id"]))
        quantity = int(execution["quantity"])
        allocation[slot] += quantity
        draw = payload.get("allocation_draw")
        eligible = int(draw["eligible_units"]) if isinstance(draw, dict) else None
        selected = int(draw["selected_unit"]) if isinstance(draw, dict) else None
        fills.append(
            Fill(
                queue_index=slot,
                quantity=quantity,
                maker_remaining_after=int(execution["maker_remaining"]),
                eligible_units=eligible,
                selected_unit=selected,
            )
        )

    resting_after = [0] * slots
    for order_id, _actor, remaining in engine.asks.get(level_price, []):
        resting_after[_slot_from_order_id(order_id)] = int(remaining)

    allocation_exact = torch.tensor(allocation, dtype=torch.int64)
    executed_units = int(allocation_exact.sum().item())
    cash_delta = tuple(
        sorted(
            (actor, int(engine.cash[actor]) - int(cash_before[actor]))
            for actor in engine.cash
        )
    )
    inventory_delta = tuple(
        sorted(
            (actor, int(engine.inventory[actor]) - int(inventory_before[actor]))
            for actor in engine.inventory
        )
    )
    return LevelOutcome(
        allocation=allocation_exact.to(dtype=quantities.dtype),
        allocation_exact=allocation_exact,
        filled_mask=allocation_exact > 0,
        fills=tuple(fills),
        resting_after=torch.tensor(resting_after, dtype=torch.int64),
        channels_delta=torch.tensor(
            (executed_units, level_price * executed_units), dtype=torch.int64
        ),
        executed_units=executed_units,
        cash_delta=cash_delta,
        inventory_delta=inventory_delta,
        post_rng_state=engine.rng.getstate(),
        post_aggregate_digest=engine.aggregate_state_digest(),
        engine_tape=tuple(record_to_json(record) for record in engine.tape),
    )


def _require_floating(quantities: Tensor) -> None:
    if not quantities.is_floating_point():
        raise ValueError(
            "autograd through-M entry points require a floating-point quantities tensor"
        )


def straight_through_level(
    quantities: Tensor,
    demand: int,
    *,
    level_price: int,
    kernel: Kernel,
    engine_seed: int = 0,
    rng_state: RandomState | None = None,
) -> LevelOutcome:
    """Primary estimator (ST): exact engine forward, pinned-scale masked-identity
    backward (``through_m._StraightThrough`` at ``PINNED_STRAIGHT_THROUGH_SCALE``)."""

    _require_floating(quantities)
    outcome = engine_execute_level(
        quantities,
        demand,
        level_price=level_price,
        kernel=kernel,
        engine_seed=engine_seed,
        rng_state=rng_state,
    )
    allocation = cast(
        Tensor,
        _StraightThrough.apply(  # type: ignore[no-untyped-call]
            quantities,
            outcome.allocation_exact,
            outcome.filled_mask,
            PINNED_STRAIGHT_THROUGH_SCALE,
        ),
    )
    return replace(outcome, allocation=allocation)


def perturb_and_map_level(
    quantities: Tensor,
    demand: int,
    *,
    level_price: int,
    kernel: Kernel,
    pam_seed: int,
    engine_seed: int = 0,
    rng_state: RandomState | None = None,
) -> LevelOutcome:
    """Audit estimator (PAM): exact engine forward, perturbed-MAP-mask backward.

    The noise is ``_perturbed_clearing`` at the pinned sigma from the seed
    supplied by the ``train_kernel`` substream (explicit here; the hook below
    derives it). The forward allocation is ALWAYS the engine output — the
    perturbed clearing supplies only the backward mask, per the E-3 contract.
    """

    _require_floating(quantities)
    if pam_seed < 0:
        raise ValueError("pam_seed must be nonnegative")
    outcome = engine_execute_level(
        quantities,
        demand,
        level_price=level_price,
        kernel=kernel,
        engine_seed=engine_seed,
        rng_state=rng_state,
    )
    perturbed = _perturbed_clearing(
        quantities.detach(),
        demand,
        kernel,
        sigma=PINNED_PERTURB_AND_MAP_SIGMA,
        seed=pam_seed,
    )
    allocation = cast(
        Tensor,
        _PerturbAndMap.apply(  # type: ignore[no-untyped-call]
            quantities, outcome.allocation_exact, perturbed.filled_mask
        ),
    )
    return replace(outcome, allocation=allocation)


# ─────────────────────────────────────────────────────────────────────────────
# MechanismEstimator hooks (the frozen L2-2 attach surface)
# ─────────────────────────────────────────────────────────────────────────────


def _resolve_stream(
    stream: TrainKernelStream | None, seed_root: int | None
) -> TrainKernelStream:
    if (stream is None) == (seed_root is None):
        raise ValueError("provide exactly one of stream or seed_root")
    if stream is not None:
        return stream
    return TrainKernelStream(cast(int, seed_root))


def straight_through_hook(
    *,
    kernel: Kernel,
    stream: TrainKernelStream | None = None,
    seed_root: int | None = None,
) -> MechanismEstimator:
    """Factory of the ST ``MechanismEstimator`` (exact ``Callable[[Tensor, int],
    Tensor]`` hook shape; kernel-blind inputs, kernel bound at construction).

    The engine runs at ``NOMINAL_LEVEL_PRICE``: within-level allocations are
    price-invariant, and cash channels at true prices are composed by the
    caller (``RecurrentFactSurrogate`` multiplies allocations by slot prices).
    """

    source = _resolve_stream(stream, seed_root)

    def mechanism(quantities: Tensor, demand: int) -> Tensor:
        engine_seed, _pam_seed = source.next_call_seeds()
        return straight_through_level(
            quantities,
            demand,
            level_price=NOMINAL_LEVEL_PRICE,
            kernel=kernel,
            engine_seed=engine_seed,
        ).allocation

    return mechanism


def perturb_and_map_hook(
    *,
    kernel: Kernel,
    stream: TrainKernelStream | None = None,
    seed_root: int | None = None,
) -> MechanismEstimator:
    """Factory of the PAM ``MechanismEstimator`` (same frozen hook shape)."""

    source = _resolve_stream(stream, seed_root)

    def mechanism(quantities: Tensor, demand: int) -> Tensor:
        engine_seed, pam_seed = source.next_call_seeds()
        return perturb_and_map_level(
            quantities,
            demand,
            level_price=NOMINAL_LEVEL_PRICE,
            kernel=kernel,
            pam_seed=pam_seed,
            engine_seed=engine_seed,
        ).allocation

    return mechanism
