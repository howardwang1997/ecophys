"""M0/M1-lumpable DGP request generator (reexploration build item E-2).

Production corpus generator for the ALPHA market cube (preregistration v2
sections 3.2 C2(a)/C4 and 4.1 DGPs D1/D2; simulator contracts section 2.4
"data" substream). Supersedes the calibration-grade
``experiments/reexploration/k_preflight_20260906/dgp_stream.py`` while keeping
its evaluation surface — ``build_episode`` / ``build_prestate`` /
``order_requests`` / ``derive_seed`` plus the duck-typed ``EpisodeStream``
fields consumed by ``run_preflight.analyze_tape`` — so the E-2 preflight
re-run can point at this module with a one-line import swap.

Policy class (contract C2(a), the single load-bearing pairing assumption):
every emitted request is decided from (i) the ANONYMOUS book state (aggregate
per-level quantities only), (ii) the requesting actor's own budgets and the
generator-side ledger of the stream emitted so far — both equivalent to own
inventory/cash feedback under the resource endowments — and (iii) the
episode's named-substream RNG / frozen exogenous series. No decision reads
allocation identity, per-maker fill counts, resting order ids, or any engine
RNG state, so the executed request stream is byte-identical under both
allocation kernels (exact request-level CRN; asserted by construction tests).
Structural lumpability guards:

- role separation: makers only post NON-CROSSING resting orders; aggressors
  only submit walks sized to exactly consumable opposite liquidity, so
  aggressors never rest and self-trade prevention can never fire;
- no cancel/replace/latency requests: order-id-addressed actions are not
  M0-admissible unless keyed to aggregate-observable labels (the R2-C grammar
  clause) and resting-order survival at rationed levels is kernel-dependent;
- taint discipline: a level that has been interior-rationed is never posted-to
  and never re-targeted; the next walk on that side must sweep it fully first.
  Every walk-plan pool snapshot therefore consists of intact posted
  quantities — a pure function of the request stream, kernel-invariant;
- resource slack: per-actor posting/walking unit budgets, endowments and
  induced-value schedule lengths are sized so no validation channel (bands,
  clocks, cash, inventory, induced capacity, self-trade, duplicate ids) can
  ever reject — zero rejections by construction.

``feedback_class`` records the provenance of the anonymous book state read by
the replenishment policy: M1 (the D0 default) projects it from the shadow
engine's realized aggregate state; M0 reads the generator-side ledger of the
emitted stream alone. The two agree by construction (the ledger is
cross-checked against the engine's anonymous book after every submit), so the
emitted stream is identical either way — the empirical form of the R2-C
lumpability concession. ``shadow_rule`` selects the shadow engine's
allocation kernel purely as a verification knob: the emitted stream is
byte-identical under either choice.

RNG discipline (contract C1): all stochastic consumers draw from the RNG-tree
``data`` substream, derived with ``numpy SeedSequence.spawn`` semantics
(``spawn_key = (name_index,)`` over the frozen ordered name tuple; episode
nodes append the episode index). The engine's own ``random.Random(prestate.seed)``
(matching.py:44) is never touched by generation and belongs to the evaluation
draw seeds alone.

D2 synthetic family (PI decision D1_05): ``garch_student_t5`` (both lineages)
and ``multiscale_logvol`` (L2-only) drive per-round walk side and interior
depth from a frozen series simulated by ``ecomd.eval.synthetic_dgps`` into
this SAME generator and engine; ``negative_jump_iid`` is defined in the
registry but excluded from the enumeration (named-but-not-run).

Determinism: an episode is a pure function of (seed_root, episode_index,
config) — no timestamps, no absolute paths; canonical-JSON serialization is
byte-stable for identity checks.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field, replace
from enum import StrEnum
from pathlib import Path
from typing import Any, Final

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
for _entry in (str(REPO_ROOT), str(REPO_ROOT / "scripts")):
    if _entry not in sys.path:
        sys.path.insert(0, _entry)

from lab_asset.matching import ReferenceEngine  # noqa: E402
from lab_asset.schema import (  # noqa: E402
    AllocationRule,
    EventType,
    InitialOrder,
    OrderRequest,
    SessionPrestate,
    Side,
    ThreeClocks,
)

__all__ = [
    "D2_NAMED_NOT_RUN",
    "D2_RUN_VARIANTS",
    "D2_SERIES_REGISTRY",
    "INVARIANT_ROLES",
    "SUBSTREAM_NAMES",
    "SYNTHETIC_D2_FAMILIES",
    "AnonymousBookView",
    "DGPConfig",
    "DgpFamily",
    "EpisodeStream",
    "FeedbackClass",
    "OwnInvariantState",
    "StreamOrder",
    "WalkPlan",
    "build_episode",
    "build_prestate",
    "config_fingerprint",
    "config_for_axis",
    "config_from_mapping",
    "config_to_mapping",
    "d2_series",
    "derive_seed",
    "episode_canonical_json",
    "episode_seed_sequence",
    "generate_episode",
    "named_substream_seed",
    "order_requests",
    "project_anonymous",
    "project_own_invariant",
]


# ─────────────────────────────────────────────────────────────────────────────
# RNG tree (contract C1: named substreams via numpy SeedSequence.spawn)
# ─────────────────────────────────────────────────────────────────────────────


SUBSTREAM_NAMES: Final[tuple[str, ...]] = ("data", "init", "minibatch", "train_kernel")
"""Frozen ordered substream names of the seed tree. ``kernel:1..K`` streams
derive per C2(b) as further children of the seed root and belong to the E-5
seed manifest, not to this module. E-2 consumes ONLY the ``data`` substream."""


def named_substream_seed(seed_root: int, name: str) -> int:
    """Seed of one named substream, using ``SeedSequence.spawn`` derivation.

    ``SeedSequence(entropy=root, spawn_key=(i,))`` is exactly the ``i``-th
    child that ``SeedSequence(root).spawn(n)`` produces, so the derivation is
    pinned to the library call the ops plan freezes without materializing
    sibling substreams this module does not own.
    """

    if name not in SUBSTREAM_NAMES:
        raise ValueError(f"unknown substream {name!r}; expected one of {SUBSTREAM_NAMES}")
    if seed_root < 0:
        raise ValueError("seed_root must be nonnegative")
    child = np.random.SeedSequence(entropy=seed_root, spawn_key=(SUBSTREAM_NAMES.index(name),))
    return int(child.generate_state(1, dtype=np.uint32)[0])


def episode_seed_sequence(seed_root: int, episode_index: int) -> np.random.SeedSequence:
    """Episode node: the ``episode_index``-th child of the ``data`` substream."""

    if episode_index < 0:
        raise ValueError("episode_index must be nonnegative")
    return np.random.SeedSequence(
        entropy=seed_root, spawn_key=(SUBSTREAM_NAMES.index("data"), episode_index)
    )


def derive_seed(*parts: object) -> int:
    """Version-independent seed derivation (byte-compatible with the K-preflight).

    Kept so the E-2 preflight re-run derives evaluation draw seeds exactly as
    ``k_preflight_20260906`` did; never used for substream derivation.
    """

    payload = "|".join(str(part) for part in parts)
    return int.from_bytes(hashlib.sha256(payload.encode("utf-8")).digest()[:8], "big")


# ─────────────────────────────────────────────────────────────────────────────
# Configuration (frozen dataclass; Hydra wiring is build item E-5)
# ─────────────────────────────────────────────────────────────────────────────


class FeedbackClass(StrEnum):
    """M0 = pure stream ledger; M1 = anonymous book state via the shadow engine."""

    M0 = "m0"
    M1 = "m1"


class DgpFamily(StrEnum):
    """D1 = lab-asset episodes; D2 variants per PI decision D1_05."""

    LAB_ASSET = "lab_asset"
    GARCH_STUDENT_T5 = "garch_student_t5"
    MULTISCALE_LOGVOL = "multiscale_logvol"


SYNTHETIC_D2_FAMILIES: Final[frozenset[DgpFamily]] = frozenset(
    {DgpFamily.GARCH_STUDENT_T5, DgpFamily.MULTISCALE_LOGVOL}
)

D2_SERIES_REGISTRY: Final[dict[str, dict[str, object]]] = {
    "garch_student_t5": {
        "innovations": "student_t",
        "degrees_of_freedom": 5,
        "omega": 0.02,
        "alpha": 0.08,
        "beta": 0.90,
        "initial_variance": 1.0,
    },
    "multiscale_logvol": {
        "innovations": "gaussian",
        "ar_coefficients": [0.90, 0.97, 0.99, 0.997],
        "component_weights": [0.10, 0.20, 0.30, 0.40],
        "logvol_scale": 0.50,
    },
    "negative_jump_iid": {
        "innovations": "gaussian_plus_centered_bernoulli_jump",
        "jump_probability": 0.03,
        "jump_amplitude": -6.0,
        "unit_population_variance": True,
    },
}
"""Series laws carried verbatim from configs/evaluator_v2/sample_complexity_v1.yaml
(the frozen registry of the D-1 killer-tests robustness family)."""

D2_RUN_VARIANTS: Final[tuple[str, ...]] = ("garch_student_t5", "multiscale_logvol")
D2_NAMED_NOT_RUN: Final[tuple[str, ...]] = ("negative_jump_iid",)


@dataclass(frozen=True)
class DGPConfig:
    """All knobs of the request generator (episodes, actor mix, rates, bands).

    Defaults implement the ID axis at N = 16 actors (the killer-tests ops list
    moves 16 -> 32 under ``pop_2x``). Integer ranges are INCLUSIVE tuples
    ``(lo, hi)``. ``tick_factor`` implements the tick-2Δ axis by homogeneous
    price dilation (see :func:`config_for_axis`).
    """

    n_rounds: int = 32
    n_makers: int = 10
    n_aggressors: int = 6
    reference_price: int = 1_000
    price_half_band: int = 80
    tick_factor: int = 1
    latency_window_ticks: int = 40
    initial_clock_max: int = 80
    initial_ask_levels: int = 3
    initial_bid_levels: int = 2
    initial_orders_per_level: tuple[int, int] = (2, 3)
    initial_quantity_range: tuple[int, int] = (2, 5)
    level_spacing_range: tuple[int, int] = (1, 2)
    resting_add_rate: float = 0.35
    replenish_orders: int = 2
    replenish_quantity_range: tuple[int, int] = (2, 4)
    spread_gap_ticks: int = 1
    level_lockout_ticks: int = 1
    v_star_single_unit_prob: float = 1.0 / 6.0
    v_star_max_share: float = 0.5
    min_pool_units: int = 4
    maker_unit_budget: int = 120
    aggressor_unit_budget: int = 60
    series_burn_in: int = 200
    series_v_star_scale: float = 4.0
    feedback_class: FeedbackClass = FeedbackClass.M1
    dgp_family: DgpFamily = DgpFamily.LAB_ASSET
    request_tick_start: int = 100
    build_attempts: int = 8
    shadow_rule: AllocationRule = AllocationRule.FIFO

    @property
    def price_bands(self) -> tuple[int, int]:
        return (self.reference_price - self.price_half_band,
                self.reference_price + self.price_half_band)

    def __post_init__(self) -> None:
        checks: tuple[tuple[bool, str], ...] = (
            (self.n_rounds >= 1, "n_rounds must be >= 1"),
            (self.n_makers >= 2, "n_makers must be >= 2"),
            (self.n_aggressors >= 1, "n_aggressors must be >= 1"),
            (self.tick_factor >= 1, "tick_factor must be >= 1"),
            (self.price_half_band >= 8, "price_half_band too tight"),
            (
                self.latency_window_ticks < self.initial_clock_max,
                "latency window must lie strictly inside the arrival-clock range",
            ),
            (
                self.request_tick_start > self.initial_clock_max,
                "request ticks must start after all arrival clocks",
            ),
            (self.initial_orders_per_level[0] >= 2, "levels need >= 2 orders for pools"),
            (
                self.initial_orders_per_level[0] <= self.initial_orders_per_level[1],
                "invalid initial_orders_per_level",
            ),
            (
                self.initial_quantity_range[0] >= 1
                and self.initial_quantity_range[0] <= self.initial_quantity_range[1],
                "invalid initial_quantity_range",
            ),
            (
                self.replenish_quantity_range[0] >= 1
                and self.replenish_quantity_range[0] <= self.replenish_quantity_range[1],
                "invalid replenish_quantity_range",
            ),
            (
                self.level_spacing_range[0] >= 1
                and self.level_spacing_range[0] <= self.level_spacing_range[1],
                "invalid level_spacing_range",
            ),
            (0.0 <= self.v_star_single_unit_prob <= 1.0, "invalid v_star_single_unit_prob"),
            (0.0 < self.v_star_max_share <= 1.0, "invalid v_star_max_share"),
            (self.min_pool_units >= 4, "min_pool_units must be >= 4"),
            (0.0 <= self.resting_add_rate <= 1.0, "invalid resting_add_rate"),
            (
                self.initial_ask_levels * self.level_spacing_range[1] * self.tick_factor
                < self.price_half_band,
                "initial ask ladder does not fit inside the price band",
            ),
            (
                self.initial_bid_levels * self.level_spacing_range[1] * self.tick_factor
                < self.price_half_band,
                "initial bid ladder does not fit inside the price band",
            ),
        )
        for ok, message in checks:
            if not ok:
                raise ValueError(message)


def _coerce_int(value: object) -> int:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    raise ValueError(f"expected an int, got {value!r}")


def _coerce_float(value: object) -> float:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    raise ValueError(f"expected a number, got {value!r}")


def config_from_mapping(raw: Mapping[str, object]) -> DGPConfig:
    """Strict mapping -> config (the E-2 preflight re-run's config surface)."""

    known: dict[str, object] = {
        name: getattr(DGPConfig, name) for name in DGPConfig.__dataclass_fields__
    }
    unknown = sorted(set(raw) - set(known))
    if unknown:
        raise ValueError(f"unknown DGPConfig keys: {unknown}")
    kwargs: dict[str, Any] = {}
    for key, value in raw.items():
        default = known[key]
        if isinstance(default, (FeedbackClass, DgpFamily, AllocationRule)):
            kwargs[key] = type(default)(str(value))
        elif isinstance(default, tuple):
            if not isinstance(value, (list, tuple)):
                raise ValueError(f"config field {key!r} must be a sequence")
            kwargs[key] = tuple(_coerce_int(item) for item in value)
        elif isinstance(default, bool):
            if not isinstance(value, bool):
                raise ValueError(f"config field {key!r} must be a bool")
            kwargs[key] = value
        elif isinstance(default, int):
            kwargs[key] = _coerce_int(value)
        elif isinstance(default, float):
            kwargs[key] = _coerce_float(value)
        else:
            raise ValueError(f"unsupported config field type for {key}")
    return DGPConfig(**kwargs)


def config_to_mapping(cfg: DGPConfig) -> dict[str, object]:
    """JSON-safe mapping (enums to values, tuples to lists)."""

    def convert(value: object) -> object:
        if isinstance(value, StrEnum):
            return value.value
        if isinstance(value, tuple):
            return list(value)
        return value

    return {key: convert(value) for key, value in asdict(cfg).items()}


def config_fingerprint(cfg: DGPConfig) -> str:
    """sha256 over the canonical config JSON (manifest / G3 binding surface)."""

    return hashlib.sha256(
        json.dumps(config_to_mapping(cfg), sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def config_for_axis(base: DGPConfig, axis: str) -> DGPConfig:
    """C4 axis presets. ``id`` returns the base unchanged.

    - ``pop_2x``: prestates regenerated at 2N with the resource envelope and
      induced-value capacities rescaled by the population factor (schedule
      lengths double) and replenishment depth doubling, so aggregate per-round
      activity scales with the market while per-actor slack ratios never
      tighten.
    - ``tick_2x``: homogeneous price dilation by the tick factor — reference
      price, half-band and every generated price offset multiply by 2, so all
      prices sit on the 2Δ lattice and the band width measured in 2Δ ticks is
      invariant (the frozen band-scaling rule of contract C4).
    """

    if axis == "id":
        return base
    if axis == "pop_2x":
        return replace(
            base,
            n_makers=base.n_makers * 2,
            n_aggressors=base.n_aggressors * 2,
            maker_unit_budget=base.maker_unit_budget * 2,
            aggressor_unit_budget=base.aggressor_unit_budget * 2,
            replenish_orders=base.replenish_orders * 2,
        )
    if axis == "tick_2x":
        return replace(
            base,
            tick_factor=base.tick_factor * 2,
            reference_price=base.reference_price * 2,
            price_half_band=base.price_half_band * 2,
        )
    raise ValueError(f"unknown axis {axis!r}; expected id/pop_2x/tick_2x")


# ─────────────────────────────────────────────────────────────────────────────
# Anonymous policy surface (the M0/M1-lumpable input grammar)
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class AnonymousBookView:
    """Aggregate book projection: per price, the TOTAL remaining quantity.

    This is the anonymous level-quantity content of the engine's
    ``aggregate_state_hash`` (schema.py) at a completed-request boundary —
    kernel-invariant under the resource-slack CRN premise. There is
    deliberately no per-order, per-actor or queue-order information here.
    """

    bids: tuple[tuple[int, int], ...]  # (price, total quantity), ascending price
    asks: tuple[tuple[int, int], ...]  # (price, total quantity), ascending price

    @property
    def best_bid(self) -> int | None:
        return self.bids[-1][0] if self.bids else None

    @property
    def best_ask(self) -> int | None:
        return self.asks[0][0] if self.asks else None


@dataclass(frozen=True)
class OwnInvariantState:
    """Requesting actor's own counters, projected from the shadow engine.

    Kernel-invariant by construction for aggressors: an aggressor's executions
    are exactly their own walk's per-level consumption, whose totals depend
    only on aggregate book state. The projector refuses maker actors, whose
    cash/inventory are allocation-dependent (the R2-C off-slack channel).
    """

    actor: str
    cash: int
    inventory: int
    units_bought: int
    units_sold: int


INVARIANT_ROLES: Final[frozenset[str]] = frozenset({"aggressor"})


def project_anonymous(engine: ReferenceEngine) -> AnonymousBookView:
    """Aggregate projection of the shadow engine's books (whitelisted reads)."""

    def levels(book: dict[int, list[tuple[str, str, int]]]) -> tuple[tuple[int, int], ...]:
        return tuple(
            (price, sum(qty for _, _, qty in queue)) for price, queue in sorted(book.items())
        )

    return AnonymousBookView(bids=levels(engine.bids), asks=levels(engine.asks))


def project_own_invariant(engine: ReferenceEngine, actor: str) -> OwnInvariantState:
    """Own-state projection, restricted to roles whose counters are kernel-invariant."""

    if engine.role_of(actor) not in INVARIANT_ROLES:
        raise ValueError(
            f"own-state projection is restricted to invariant roles (aggressors); "
            f"{actor!r} has role {engine.role_of(actor)!r}"
        )
    return OwnInvariantState(
        actor=actor,
        cash=engine.cash[actor],
        inventory=engine.inventory[actor],
        units_bought=engine.units_bought[actor],
        units_sold=engine.units_sold[actor],
    )


# ─────────────────────────────────────────────────────────────────────────────
# Stream record types (strict superset of the K-preflight surface)
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class StreamOrder:
    """A resting order present in the prestate, with pre-session arrival clock."""

    order_id: str
    actor: str
    side: Side
    price: int
    quantity: int
    arrival_clock: int


@dataclass(frozen=True)
class WalkPlan:
    """Ground truth for one aggressive walk (DGP-side, not tape-derivable)."""

    request_index: int
    aggressor_actor: str
    target_price: int
    swept_units: int
    v_star: int
    pool: tuple[tuple[str, int, int], ...]  # (order_id, quantity, arrival_clock)
    round_id: int = 0

    @property
    def r_star(self) -> int:
        return sum(quantity for _, quantity, _ in self.pool)


@dataclass(frozen=True)
class EpisodeStream:
    """One frozen episode. The first 14 fields match the K-preflight layout."""

    seed_root: int
    episode_index: int
    session_stem: str
    actors: tuple[str, ...]
    actor_roles: dict[str, str]
    initial_cash: dict[str, int]
    initial_inventory: dict[str, int]
    price_bands: tuple[int, int]
    latency_window: int
    initial_book: tuple[StreamOrder, ...]
    requests: tuple[dict[str, object], ...]
    walk_plans: tuple[WalkPlan, ...]
    predicted_cleared_volume: int
    initial_order_count: int
    dgp_family: str = DgpFamily.LAB_ASSET.value
    feedback_class: str = FeedbackClass.M1.value
    n_rounds: int = 0
    config_fingerprint: str = ""
    round_has_walk: tuple[bool, ...] = ()
    induced_buy_values: dict[str, tuple[int, ...]] = field(default_factory=dict)
    induced_sell_costs: dict[str, tuple[int, ...]] = field(default_factory=dict)


def episode_canonical_json(stream: EpisodeStream) -> bytes:
    """Byte-stable serialization for determinism / CRN identity checks."""

    def walk_plan_dict(plan: WalkPlan) -> dict[str, object]:
        return {
            "request_index": plan.request_index,
            "round_id": plan.round_id,
            "aggressor_actor": plan.aggressor_actor,
            "target_price": plan.target_price,
            "swept_units": plan.swept_units,
            "v_star": plan.v_star,
            "pool": [list(member) for member in plan.pool],
        }

    payload = {
        "seed_root": stream.seed_root,
        "episode_index": stream.episode_index,
        "session_stem": stream.session_stem,
        "dgp_family": stream.dgp_family,
        "feedback_class": stream.feedback_class,
        "n_rounds": stream.n_rounds,
        "actors": list(stream.actors),
        "actor_roles": stream.actor_roles,
        "initial_cash": stream.initial_cash,
        "initial_inventory": stream.initial_inventory,
        "induced_buy_lengths": {k: len(v) for k, v in stream.induced_buy_values.items()},
        "induced_sell_lengths": {k: len(v) for k, v in stream.induced_sell_costs.items()},
        "price_bands": list(stream.price_bands),
        "latency_window": stream.latency_window,
        "initial_book": [
            [o.order_id, o.actor, o.side.value, o.price, o.quantity, o.arrival_clock]
            for o in stream.initial_book
        ],
        "requests": [dict(spec) for spec in stream.requests],
        "walk_plans": [walk_plan_dict(plan) for plan in stream.walk_plans],
        "predicted_cleared_volume": stream.predicted_cleared_volume,
        "initial_order_count": stream.initial_order_count,
        "config_fingerprint": stream.config_fingerprint,
        "round_has_walk": list(stream.round_has_walk),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def d2_series(
    family: DgpFamily, n_rounds: int, seed: int, burn_in: int
) -> tuple[np.ndarray, np.ndarray]:
    """Frozen synthetic series via ``ecomd.eval.synthetic_dgps.simulate_dgp``.

    ``negative_jump_iid`` is defined in the registry but excluded from the D2
    enumeration (PI decision D1_05: named-but-not-run).
    """

    from ecomd.eval.synthetic_dgps import simulate_dgp

    name = family.value
    if name in D2_NAMED_NOT_RUN:
        raise ValueError(
            f"DGP family {name!r} is named-but-not-run per PI decision D1_05; "
            "it is excluded from the D2 enumeration"
        )
    block = simulate_dgp(
        name, length=n_rounds, burn_in=burn_in, seed=seed, registry=D2_SERIES_REGISTRY
    )
    return np.asarray(block.returns), np.asarray(block.volume)


# ─────────────────────────────────────────────────────────────────────────────
# Generator-internal aggregate ledger (pure function of the request stream)
# ─────────────────────────────────────────────────────────────────────────────


class _Ledger:
    """Aggregate bookkeeping of the stream under construction.

    Mirrors the anonymous level totals of the shadow engine (cross-checked
    after every submit) plus the taint map and per-actor side budgets. Every
    field is a deterministic function of the emitted requests alone — which is
    what makes walk-plan pool snapshots kernel-invariant — and the M0 policy
    reads this object instead of the engine.
    """

    def __init__(
        self, cfg: DGPConfig, makers: tuple[str, ...], aggressors: tuple[str, ...]
    ) -> None:
        self.cfg = cfg
        self.makers = makers
        self.aggressors = aggressors
        self.level_units: dict[tuple[Side, int], int] = {}
        self.level_members: dict[tuple[Side, int], list[tuple[str, int, int]]] = {}
        self.tainted: set[tuple[Side, int]] = set()
        self.posted_units: dict[tuple[str, Side], int] = {
            (actor, side): 0
            for actor in (*makers, *aggressors)
            for side in (Side.BID, Side.ASK)
        }
        self.walked_units: dict[tuple[str, Side], int] = {
            (actor, side): 0 for actor in aggressors for side in (Side.BID, Side.ASK)
        }
        self.submitted = 0
        self.initial_order_count = 0

    # -- budgets -----------------------------------------------------------
    def can_post(self, actor: str, side: Side, quantity: int, *, is_walk: bool) -> bool:
        budget = self.cfg.aggressor_unit_budget if is_walk else self.cfg.maker_unit_budget
        used = self.walked_units[(actor, side)] if is_walk else self.posted_units[(actor, side)]
        return used + quantity <= budget

    # -- posting -----------------------------------------------------------
    def record_post(
        self, order_id: str, actor: str, side: Side, price: int, quantity: int, clock: int
    ) -> None:
        key = (side, price)
        if key in self.tainted:
            raise AssertionError("post onto a tainted (interior-rationed) level")
        self.level_units[key] = self.level_units.get(key, 0) + quantity
        self.level_members.setdefault(key, []).append((order_id, quantity, clock))
        self.posted_units[(actor, side)] += quantity

    def record_walk(self, actor: str, side: Side, quantity: int) -> None:
        self.walked_units[(actor, side)] += quantity

    # -- queries -----------------------------------------------------------
    def levels(self) -> tuple[tuple[tuple[int, int], ...], tuple[tuple[int, int], ...]]:
        """(bids best-first, asks best-first) aggregate ladders."""

        bids = tuple(
            (price, units)
            for (side, price), units in sorted(
                self.level_units.items(), key=lambda item: -item[0][1]
            )
            if side == Side.BID and units > 0
        )
        asks = tuple(
            (price, units)
            for (side, price), units in sorted(self.level_units.items(), key=lambda item: item[0][1])
            if side == Side.ASK and units > 0
        )
        return bids, asks

    def ladder(self, walk_side: Side) -> list[tuple[int, int]]:
        """The walked-against book's levels as (price, units), best level first."""

        book_side = _opposite(walk_side)
        rows = [
            (price, units)
            for (side, price), units in self.level_units.items()
            if side == book_side and units > 0
        ]
        rows.sort(key=lambda row: row[0], reverse=walk_side == Side.ASK)
        return rows

    def split_walk(self, walk_side: Side) -> tuple[list[tuple[int, int]], tuple[int, int] | None]:
        """(swept levels, target level) per the taint discipline.

        Leading tainted levels MUST be swept; leading untainted levels too
        small to interior safely are swept as well (full consumption is
        aggregate-deterministic). The first untainted level with at least
        ``min_pool_units`` becomes the interior target.
        """

        book_side = _opposite(walk_side)
        swept: list[tuple[int, int]] = []
        target: tuple[int, int] | None = None
        for row in self.ladder(walk_side):
            if (book_side, row[0]) in self.tainted or row[1] < self.cfg.min_pool_units:
                swept.append(row)
            else:
                target = row
                break
        return swept, target

    def apply_walk(
        self, walk_side: Side, swept: list[tuple[int, int]], target: tuple[int, int], v_star: int
    ) -> None:
        book_side = _opposite(walk_side)
        for price, units in swept:
            if units <= 0:
                raise AssertionError("sweeping an empty level")
            key = (book_side, price)
            del self.level_units[key]
            del self.level_members[key]
            self.tainted.discard(key)
        key = (book_side, target[0])
        if target[1] - v_star < 1:
            raise AssertionError("interior rationing must leave a positive remainder")
        self.level_units[key] = target[1] - v_star
        self.tainted.add(key)

    def cross_check(self, engine: ReferenceEngine) -> None:
        engine_bids = {
            price: sum(qty for _, _, qty in queue) for price, queue in engine.bids.items()
        }
        engine_asks = {
            price: sum(qty for _, _, qty in queue) for price, queue in engine.asks.items()
        }
        ledger_bids = {
            price: units
            for (side, price), units in self.level_units.items()
            if side == Side.BID and units > 0
        }
        ledger_asks = {
            price: units
            for (side, price), units in self.level_units.items()
            if side == Side.ASK and units > 0
        }
        if engine_bids != ledger_bids or engine_asks != ledger_asks:
            raise AssertionError(
                "generator ledger diverged from the shadow engine's anonymous book"
            )


def _opposite(side: Side) -> Side:
    return Side.ASK if side == Side.BID else Side.BID


# ─────────────────────────────────────────────────────────────────────────────
# Episode construction
# ─────────────────────────────────────────────────────────────────────────────


def _actors(cfg: DGPConfig) -> tuple[tuple[str, ...], tuple[str, ...]]:
    makers = tuple(f"MK{index:02d}" for index in range(cfg.n_makers))
    aggressors = tuple(f"AG{index:02d}" for index in range(cfg.n_aggressors))
    return makers, aggressors


def _initial_book(
    rng: np.random.Generator, cfg: DGPConfig, makers: tuple[str, ...]
) -> tuple[StreamOrder, ...]:
    """Initial ladder. The first member of every pool arrives inside the
    latency window and every other member strictly after it, so all
    initial-book pools straddle the window by construction."""

    tf = cfg.tick_factor
    orders: list[StreamOrder] = []
    counter = 0

    def clock(first_in_level: bool) -> int:
        if first_in_level:
            return int(rng.integers(0, cfg.latency_window_ticks + 1))
        return int(rng.integers(cfg.latency_window_ticks + 1, cfg.initial_clock_max + 1))

    for side, n_levels in ((Side.ASK, cfg.initial_ask_levels), (Side.BID, cfg.initial_bid_levels)):
        offset = 0
        for _ in range(n_levels):
            offset += tf * int(rng.integers(*cfg.level_spacing_range, endpoint=True))
            price = cfg.reference_price + (offset if side == Side.ASK else -offset)
            for index in range(int(rng.integers(*cfg.initial_orders_per_level, endpoint=True))):
                counter += 1
                orders.append(
                    StreamOrder(
                        order_id=f"I{counter:07d}",
                        actor=makers[int(rng.integers(0, len(makers)))],
                        side=side,
                        price=price,
                        quantity=int(rng.integers(*cfg.initial_quantity_range, endpoint=True)),
                        arrival_clock=clock(index == 0),
                    )
                )
    return tuple(orders)


def _endowments(
    cfg: DGPConfig, makers: tuple[str, ...], aggressors: tuple[str, ...]
) -> tuple[dict[str, int], dict[str, int], dict[str, tuple[int, ...]], dict[str, tuple[int, ...]]]:
    """Endowments sized so no validation channel can ever fire (see module doc):

    cash = band_hi x unit budget, inventory = unit budget, and induced-value
    schedule lengths = unit budgets. Per-actor lifetime posting/walking on
    each side is capped at the same budget, which by unit conservation makes
    every cash / inventory / induced-capacity check slack at all times.
    """

    band_hi = cfg.reference_price + cfg.price_half_band
    initial_cash = {
        **{actor: band_hi * cfg.maker_unit_budget for actor in makers},
        **{actor: band_hi * cfg.aggressor_unit_budget for actor in aggressors},
    }
    initial_inventory = {
        **{actor: cfg.maker_unit_budget for actor in makers},
        **{actor: cfg.aggressor_unit_budget for actor in aggressors},
    }
    ref = cfg.reference_price
    induced_buy = {
        **{
            actor: tuple(ref + index for index in range(cfg.maker_unit_budget))
            for actor in makers
        },
        **{
            actor: tuple(ref + index for index in range(cfg.aggressor_unit_budget))
            for actor in aggressors
        },
    }
    induced_sell = {
        **{
            actor: tuple(ref - index for index in range(cfg.maker_unit_budget))
            for actor in makers
        },
        **{
            actor: tuple(ref - index for index in range(cfg.aggressor_unit_budget))
            for actor in aggressors
        },
    }
    return initial_cash, initial_inventory, induced_buy, induced_sell


class _EpisodeBuilder:
    def __init__(
        self,
        seed_root: int,
        episode_index: int,
        cfg: DGPConfig,
        rng: np.random.Generator,
        series: tuple[np.ndarray, np.ndarray] | None,
    ) -> None:
        self.seed_root = seed_root
        self.episode_index = episode_index
        self.cfg = cfg
        self.rng = rng
        self.series = series
        self.series_index = 0
        self.makers, self.aggressors = _actors(cfg)
        self.actors = self.makers + self.aggressors
        self.requests: list[dict[str, object]] = []
        self.walk_plans: list[WalkPlan] = []
        self.round_has_walk: list[bool] = []
        self.event_id = 0
        self.tick = cfg.request_tick_start
        self.shadow_seed = derive_seed(seed_root, "e2-shadow", episode_index)
        self.ledger: _Ledger | None = None
        self.shadow: ReferenceEngine | None = None

    def session_stem(self) -> str:
        return f"e2_{self.seed_root}_{self.episode_index}_{self.cfg.dgp_family.value}"

    # -- request emission ---------------------------------------------------
    def _emit_submit(
        self,
        actor: str,
        side: Side,
        price: int,
        quantity: int,
        round_id: int,
        *,
        is_walk: bool,
    ) -> str:
        """Emit one submit, feed it to the shadow engine, reconcile the ledger.

        The engine assigns order ids ``O%08d`` sequentially over accepted
        requests (initial book first, matching.py ``_next_order_identity``);
        with zero rejections by construction the next id is exactly
        predictable, which is what walk-plan pool snapshots record.
        """

        assert self.ledger is not None and self.shadow is not None
        self.tick += int(self.rng.integers(1, 3))
        self.event_id += 1
        predicted_id = f"O{self.ledger.initial_order_count + self.ledger.submitted + 1:08d}"
        request = OrderRequest(
            event_id=self.event_id,
            actor=actor,
            client_order_id=f"C{self.event_id:04d}",
            side=side,
            price=int(price),
            quantity=int(quantity),
            clocks=ThreeClocks(self.tick, self.tick, self.tick),
            round_id=round_id,
        )
        self.shadow.submit(request)
        if self.shadow.tape[-1].event_type is not EventType.ORDER_ACCEPTED:
            raise AssertionError(
                f"shadow engine rejected a generated request ({actor} {side.value} "
                f"{price}x{quantity}); the slack construction was violated"
            )
        self.requests.append(
            {
                "kind": "submit",
                "event_id": self.event_id,
                "actor": actor,
                "side": side.value,
                "price": int(price),
                "quantity": int(quantity),
                "match_ts": self.tick,
                "round_id": round_id,
                "order_id": predicted_id,
            }
        )
        self.ledger.submitted += 1
        if is_walk:
            self.ledger.record_walk(actor, side, quantity)
        else:
            self.ledger.record_post(predicted_id, actor, side, price, quantity, self.tick)
            self.ledger.cross_check(self.shadow)
        return predicted_id

    # -- anonymous levels (the policy's only book information) ---------------
    def _levels(self) -> tuple[tuple[tuple[int, int], ...], tuple[tuple[int, int], ...]]:
        assert self.ledger is not None and self.shadow is not None
        if self.cfg.feedback_class is FeedbackClass.M1:
            view = project_anonymous(self.shadow)
            bids = tuple(sorted(view.bids, key=lambda row: -row[0]))
            return bids, view.asks
        return self.ledger.levels()

    def _resting_candidates(
        self,
        side: Side,
        own_levels: tuple[tuple[int, int], ...],
        opp_levels: tuple[tuple[int, int], ...],
    ) -> list[int]:
        """Non-crossing, untainted candidate prices for one resting post.

        Rule (identical for M0 and M1; only the source of the aggregate
        levels differs): an inside-the-spread quote that clears the lockout
        above the opposite best (the mean-reversion channel), else joining the
        current best level of the own side (the pool-deepening channel).
        """

        assert self.ledger is not None
        cfg = self.cfg
        sign = 1 if side == Side.ASK else -1
        best_own = own_levels[0][0] if own_levels else None
        opp_best = opp_levels[0][0] if opp_levels else None
        candidates: list[int] = []
        if best_own is not None and opp_best is not None:
            quote = best_own - sign * cfg.spread_gap_ticks * cfg.tick_factor
            lockout = opp_best + sign * cfg.level_lockout_ticks * cfg.tick_factor
            if (quote - lockout) * sign > 0:
                candidates.append(quote)
        if best_own is not None:
            candidates.append(best_own)
        lo, hi = cfg.price_bands
        viable: list[int] = []
        for price in candidates:
            if (side, price) in self.ledger.tainted or not lo <= price <= hi:
                continue
            if opp_best is not None:
                crossed = price <= opp_best if side == Side.ASK else price >= opp_best
                if crossed:
                    continue
            viable.append(price)
        return viable

    def _post_resting(self, side: Side, quantity: int, actor: str, round_id: int) -> None:
        """Post one resting order at a current, non-crossing candidate price.

        The aggregate levels are read at call time (not from a per-round
        snapshot) so the non-crossing rule always sees the state the engine
        will validate against.
        """

        assert self.ledger is not None
        if not self.ledger.can_post(actor, side, quantity, is_walk=False):
            return
        bids, asks = self._levels()
        own = asks if side == Side.ASK else bids
        opp = bids if side == Side.ASK else asks
        for price in self._resting_candidates(side, own, opp):
            self._emit_submit(actor, side, price, quantity, round_id, is_walk=False)
            return

    def _replenish(self, walk_side: Side, round_id: int) -> None:
        """Post resting liquidity: on the side the coming walk will hit, plus
        an optional own-side add (rate knob). The rng draw pattern per round
        is fixed regardless of which posts succeed, so the stream is a pure
        function of the aggregate state trajectory."""

        assert self.ledger is not None
        cfg = self.cfg
        hit_side = _opposite(walk_side)
        for _ in range(cfg.replenish_orders):
            quantity = int(
                self.rng.integers(*cfg.replenish_quantity_range, endpoint=True)
            )
            maker = self.makers[int(self.rng.integers(0, len(self.makers)))]
            self._post_resting(hit_side, quantity, maker, round_id)
        if float(self.rng.random()) < cfg.resting_add_rate:
            quantity = int(
                self.rng.integers(*cfg.replenish_quantity_range, endpoint=True)
            )
            maker = self.makers[int(self.rng.integers(0, len(self.makers)))]
            self._post_resting(walk_side, quantity, maker, round_id)

    # -- walk ---------------------------------------------------------------
    def _draw_v_star(self, r_star: int) -> int:
        cfg = self.cfg
        share_cap = max(1, int(cfg.v_star_max_share * r_star))
        if self.series is not None:
            volume = float(self.series[1][self.series_index])
            target = max(1, round(volume * cfg.series_v_star_scale))
        elif float(self.rng.random()) < cfg.v_star_single_unit_prob:
            target = 1
        else:
            target = int(self.rng.integers(2, share_cap + 1))
        return max(1, min(target, r_star - 1, share_cap))

    def _walk(self, round_id: int, walk_side: Side) -> bool:
        assert self.ledger is not None and self.shadow is not None
        ledger = self.ledger
        swept_levels, target = ledger.split_walk(walk_side)
        if target is None:
            return False
        v_star = self._draw_v_star(target[1])
        swept = sum(units for _, units in swept_levels)
        quantity = swept + v_star
        eligible = [
            actor
            for actor in self.aggressors
            if ledger.can_post(actor, walk_side, quantity, is_walk=True)
        ]
        if not eligible:
            return False
        aggressor = eligible[self.rng.integers(0, len(eligible))]
        pool = tuple(ledger.level_members[(_opposite(walk_side), target[0])])
        request_index = len(self.requests)
        self._emit_submit(aggressor, walk_side, target[0], quantity, round_id, is_walk=True)
        ledger.apply_walk(walk_side, swept_levels, target, v_star)
        ledger.cross_check(self.shadow)
        self.walk_plans.append(
            WalkPlan(
                request_index=request_index,
                aggressor_actor=aggressor,
                target_price=target[0],
                swept_units=swept,
                v_star=v_star,
                pool=pool,
                round_id=round_id,
            )
        )
        return True

    # -- episode ------------------------------------------------------------
    def build(self) -> EpisodeStream:
        cfg = self.cfg
        makers, aggressors = self.makers, self.aggressors

        initial: tuple[StreamOrder, ...] | None = None
        for _ in range(cfg.build_attempts):
            candidate = _initial_book(self.rng, cfg, makers)
            lo, hi = cfg.price_bands
            if all(lo <= order.price <= hi for order in candidate):
                initial = candidate
                break
        if initial is None:
            raise RuntimeError(
                "initial book constraints unsatisfiable after "
                f"{cfg.build_attempts} attempts (seed_root={self.seed_root}, "
                f"episode={self.episode_index})"
            )

        initial_cash, initial_inventory, induced_buy, induced_sell = _endowments(
            cfg, makers, aggressors
        )
        ledger = _Ledger(cfg, makers, aggressors)
        prestate = SessionPrestate(
            session_id=f"{self.session_stem()}:{cfg.shadow_rule.value}:shadow",
            seed=self.shadow_seed,
            allocation_rule=cfg.shadow_rule,
            initial_cash=initial_cash,
            initial_inventory=initial_inventory,
            price_bands=cfg.price_bands,
            actors=self.actors,
            induced_buy_values=induced_buy,
            induced_sell_costs=induced_sell,
            actor_roles={
                **{actor: "maker" for actor in makers},
                **{actor: "aggressor" for actor in aggressors},
            },
            initial_book=tuple(
                InitialOrder(o.order_id, o.actor, o.side, o.price, o.quantity)
                for o in initial
            ),
            schema_version="lab-asset-v3",
        )
        shadow = ReferenceEngine(prestate)
        ledger.initial_order_count = len(initial)
        for order in initial:
            ledger.record_post(
                order.order_id, order.actor, order.side, order.price,
                order.quantity, order.arrival_clock,
            )
        ledger.cross_check(shadow)
        self.ledger = ledger
        self.shadow = shadow

        for round_id in range(cfg.n_rounds):
            if self.series is not None:
                walk_side = (
                    Side.BID if float(self.series[0][self.series_index]) >= 0.0 else Side.ASK
                )
            else:
                walk_side = Side.BID if float(self.rng.random()) < 0.5 else Side.ASK
            self._replenish(walk_side, round_id)
            walked = self._walk(round_id, walk_side)
            self.round_has_walk.append(walked)
            self.series_index += 1

        self.requests.append({"kind": "finish"})
        predicted = sum(plan.swept_units + plan.v_star for plan in self.walk_plans)
        return EpisodeStream(
            seed_root=self.seed_root,
            episode_index=self.episode_index,
            session_stem=self.session_stem(),
            actors=self.actors,
            actor_roles=dict(prestate.actor_roles),
            initial_cash=initial_cash,
            initial_inventory=initial_inventory,
            price_bands=cfg.price_bands,
            latency_window=cfg.latency_window_ticks,
            initial_book=tuple(
                sorted(initial, key=lambda order: (order.arrival_clock, order.order_id))
            ),
            requests=tuple(self.requests),
            walk_plans=tuple(self.walk_plans),
            predicted_cleared_volume=predicted,
            initial_order_count=len(initial),
            dgp_family=cfg.dgp_family.value,
            feedback_class=cfg.feedback_class.value,
            n_rounds=cfg.n_rounds,
            config_fingerprint=config_fingerprint(cfg),
            round_has_walk=tuple(self.round_has_walk),
            induced_buy_values=induced_buy,
            induced_sell_costs=induced_sell,
        )


def _spec_int(spec: Mapping[str, object], key: str, default: int | None = None) -> int:
    value = spec.get(key, default) if default is not None else spec[key]
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"request field {key!r} must be an int, got {value!r}")
    return value


def _as_order_request(spec: Mapping[str, object]) -> OrderRequest:
    event_id = _spec_int(spec, "event_id")
    tick = _spec_int(spec, "match_ts")
    round_value = _spec_int(spec, "round_id", default=0)
    side_value = spec["side"]
    actor_value = spec["actor"]
    if not isinstance(side_value, str) or not isinstance(actor_value, str):
        raise ValueError("request fields 'side' and 'actor' must be strings")
    return OrderRequest(
        event_id=event_id,
        actor=actor_value,
        client_order_id=f"C{event_id:04d}",
        side=Side(side_value),
        price=_spec_int(spec, "price"),
        quantity=_spec_int(spec, "quantity"),
        clocks=ThreeClocks(tick, tick, tick),
        round_id=round_value,
    )


def generate_episode(
    seed_root: int,
    episode_index: int,
    cfg: DGPConfig,
    *,
    shadow_rule: AllocationRule | None = None,
) -> EpisodeStream:
    """Build one episode stream: a pure function of (seed_root, episode_index, cfg).

    ``shadow_rule`` selects the allocation kernel of the INTERNAL shadow engine
    whose anonymous state the M1 policy projects. It is a verification knob
    only: the emitted stream is byte-identical under either choice (exact
    request-level CRN, contract C2(a)); the tests assert this.
    """

    if shadow_rule is not None:
        cfg = replace(cfg, shadow_rule=shadow_rule)
    episode_children = episode_seed_sequence(seed_root, episode_index).spawn(2)
    rng = np.random.Generator(np.random.PCG64(episode_children[0]))
    series: tuple[np.ndarray, np.ndarray] | None = None
    if cfg.dgp_family in SYNTHETIC_D2_FAMILIES:
        series_seed = int(episode_children[1].generate_state(1, dtype=np.uint32)[0])
        series = d2_series(cfg.dgp_family, cfg.n_rounds, series_seed, cfg.series_burn_in)
    builder = _EpisodeBuilder(seed_root, episode_index, cfg, rng, series)
    return builder.build()


def build_episode(seed_root: int, episode_index: int, cfg: Mapping[str, object]) -> EpisodeStream:
    """Preflight-compatible entry point (mapping config -> frozen episode)."""

    return generate_episode(seed_root, episode_index, config_from_mapping(cfg))


def build_prestate(
    stream: EpisodeStream, rule: AllocationRule, draw_seed: int
) -> SessionPrestate:
    """Prestate identical across arms/replays except allocation_rule and draw seed."""

    return SessionPrestate(
        session_id=f"{stream.session_stem}:{rule.value}:{draw_seed}",
        seed=draw_seed,
        allocation_rule=rule,
        initial_cash=dict(stream.initial_cash),
        initial_inventory=dict(stream.initial_inventory),
        price_bands=stream.price_bands,
        actors=stream.actors,
        induced_buy_values=dict(stream.induced_buy_values),
        induced_sell_costs=dict(stream.induced_sell_costs),
        actor_roles=dict(stream.actor_roles),
        initial_book=tuple(
            InitialOrder(o.order_id, o.actor, o.side, o.price, o.quantity)
            for o in stream.initial_book
        ),
        schema_version="lab-asset-v3",
    )


def order_requests(stream: EpisodeStream) -> list[OrderRequest]:
    """The byte-identical request sequence fed to every evaluation of the episode."""

    return [_as_order_request(spec) for spec in stream.requests if spec["kind"] == "submit"]
