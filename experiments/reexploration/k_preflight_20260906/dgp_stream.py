"""Minimal M0-lumpable request-stream generator for the D1_06 K-variance preflight.

CALIBRATION-GRADE ONLY -- this is NOT the D0-frozen corpus generator. It exists solely
to measure, per PI decision pi_reexploration_d1_authorization_20260906 item D1_06, how
much of the variance of DGP-native consumer statistics is attributable to
allocation-draw replay (the K dimension) versus between-seed stream variance.

Policy class: M0, the strongest-lumpability point of the M0/M1-lumpable class required
by contract C2(a). Each episode's request stream is a pure function of the episode
stream RNG and never feeds back on the realized tape, allocation identity, or any
per-actor post-trade state, so under the resource-slack endowments used here the
executed request stream is exactly kernel- and draw-invariant (the runner verifies this
via the request-boundary aggregate-state-hash invariant). An M1 corpus generator
(anonymous book-state feedback) is the D0 artifact's job; if the D0 generator adds
feedback channels, this preflight must be re-run against it before the K freeze.

Episode shape: three initial ask levels (multi-order pools) plus resting bids; two
resting ask adds; three aggressive marketable buys, each engineered to end strictly
inside a multi-order level (interior rationing, 0 < V* < R*), with a 1/6 single-unit
V* stratum. Pools at every walk target straddle the latency window W by construction.
Determinism: a pure function of (seed_root, episode_index, config); no timestamps, no
absolute paths, sha256-derived substream seeds (version-independent of RNG libraries).
"""

from __future__ import annotations

import hashlib
import random
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lab_asset.schema import (  # noqa: E402
    AllocationRule,
    InitialOrder,
    OrderRequest,
    SessionPrestate,
    Side,
    ThreeClocks,
)

MAKERS = ("M1", "M2", "M3", "M4")
BUYERS = ("B1", "B2")


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


@dataclass(frozen=True)
class EpisodeStream:
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


def derive_seed(*parts: object) -> int:
    """Version-independent deterministic substream seed derivation."""

    payload = "|".join(str(part) for part in parts)
    return int.from_bytes(hashlib.sha256(payload.encode("utf-8")).digest()[:8], "big")


def _submit_request(
    event_id: int, actor: str, side: Side, price: int, quantity: int, tick: int
) -> dict[str, object]:
    return {
        "kind": "submit",
        "event_id": event_id,
        "actor": actor,
        "side": side.value,
        "price": price,
        "quantity": quantity,
        "match_ts": tick,
    }


def _straddles_window(
    members: list[tuple[str, int, int]], window: int
) -> bool:
    return any(clock <= window for _, _, clock in members) and any(
        clock > window for _, _, clock in members
    )


def _draw_v_star(rng: random.Random, pool_total: int, single_unit_prob: float) -> int | None:
    """Interior V* in [1, pool_total - 2], leaving remainder >= 2."""

    if pool_total < 4:
        return None
    if rng.random() < single_unit_prob:
        return 1
    return rng.randint(2, pool_total - 2)


def _attempt_episode(
    rng: random.Random, seed_root: int, episode_index: int, cfg: Mapping[str, object]
) -> EpisodeStream | None:
    ref = int(cfg["reference_price"])
    half_band = int(cfg["price_half_band"])
    window = int(cfg["latency_window_ticks"])
    clock_max = int(cfg["initial_clock_max"])
    qty_lo, qty_hi = (int(x) for x in cfg["initial_quantity_range"])
    single_unit_prob = float(cfg["v_star_single_unit_prob"])
    start_tick = int(cfg["request_tick_start"])

    p1 = ref + rng.randint(1, 2)
    p2 = p1 + rng.randint(1, 2)
    p3 = p2 + rng.randint(1, 2)
    if p3 > ref + half_band:
        return None

    initial: list[StreamOrder] = []
    level_members: dict[int, list[tuple[str, int, int]]] = {}
    counter = 0
    for price in (p1, p2, p3):
        for _ in range(rng.randint(2, 3)):
            counter += 1
            order = StreamOrder(
                order_id=f"I{counter:07d}",
                actor=MAKERS[rng.randrange(len(MAKERS))],
                side=Side.ASK,
                price=price,
                quantity=rng.randint(qty_lo, qty_hi),
                arrival_clock=rng.randint(0, clock_max),
            )
            initial.append(order)
            level_members.setdefault(price, []).append(
                (order.order_id, order.quantity, order.arrival_clock)
            )
    for _ in range(rng.randint(1, 2)):
        counter += 1
        order = StreamOrder(
            order_id=f"I{counter:07d}",
            actor=BUYERS[rng.randrange(len(BUYERS))],
            side=Side.BID,
            price=ref - rng.randint(1, 3),
            quantity=rng.randint(2, 4),
            arrival_clock=rng.randint(0, clock_max),
        )
        initial.append(order)

    level_qty = {
        price: sum(qty for _, qty, _ in members) for price, members in level_members.items()
    }
    requests: list[dict[str, object]] = []
    walk_plans: list[WalkPlan] = []
    tick = start_tick
    event_id = 0
    n_initial = len(initial)

    def predicted_engine_id() -> str:
        return f"O{n_initial + len(requests) + 1:08d}"

    # Resting ask add #1 (deepens the p1 or p2 pool).
    tick += rng.randint(1, 3)
    event_id += 1
    add_price = (p1, p2)[rng.randrange(2)]
    add_qty = rng.randint(2, 4)
    add_actor = MAKERS[rng.randrange(len(MAKERS))]
    level_members[add_price].append((predicted_engine_id(), add_qty, tick))
    level_qty[add_price] += add_qty
    requests.append(
        _submit_request(event_id, add_actor, Side.ASK, add_price, add_qty, tick)
    )

    # Optional resting bid add (never crosses; buyers own no asks).
    if rng.random() < 0.5:
        tick += rng.randint(1, 3)
        event_id += 1
        requests.append(
            _submit_request(
                event_id,
                BUYERS[rng.randrange(len(BUYERS))],
                Side.BID,
                ref - rng.randint(1, 3),
                rng.randint(2, 3),
                tick,
            )
        )

    # Aggressive walk #1: B1 stops strictly inside the best-ask pool.
    tick += rng.randint(1, 3)
    event_id += 1
    v1 = _draw_v_star(rng, level_qty[p1], single_unit_prob)
    if v1 is None or not _straddles_window(level_members[p1], window):
        return None
    walk_plans.append(
        WalkPlan(
            request_index=len(requests),
            aggressor_actor="B1",
            target_price=p1,
            swept_units=0,
            v_star=v1,
            pool=tuple(level_members[p1]),
        )
    )
    requests.append(_submit_request(event_id, "B1", Side.BID, p1, v1, tick))
    level_qty[p1] -= v1

    # Resting ask add #2 at p2.
    tick += rng.randint(1, 3)
    event_id += 1
    add2_qty = rng.randint(2, 4)
    add2_actor = MAKERS[rng.randrange(len(MAKERS))]
    level_members[p2].append((predicted_engine_id(), add2_qty, tick))
    level_qty[p2] += add2_qty
    requests.append(_submit_request(event_id, add2_actor, Side.ASK, p2, add2_qty, tick))

    # Aggressive walk #2: B2 sweeps the p1 remainder, stops strictly inside p2.
    tick += rng.randint(1, 3)
    event_id += 1
    swept1 = level_qty[p1]
    v2 = _draw_v_star(rng, level_qty[p2], single_unit_prob)
    if v2 is None or not _straddles_window(level_members[p2], window):
        return None
    walk_plans.append(
        WalkPlan(
            request_index=len(requests),
            aggressor_actor="B2",
            target_price=p2,
            swept_units=swept1,
            v_star=v2,
            pool=tuple(level_members[p2]),
        )
    )
    requests.append(
        _submit_request(event_id, "B2", Side.BID, p2, swept1 + v2, tick)
    )
    level_qty[p1] = 0
    level_qty[p2] -= v2

    # Aggressive walk #3: B1 sweeps the p2 remainder, stops strictly inside p3.
    tick += rng.randint(1, 3)
    event_id += 1
    swept2 = level_qty[p2]
    v3 = _draw_v_star(rng, level_qty[p3], single_unit_prob)
    if v3 is None or not _straddles_window(level_members[p3], window):
        return None
    walk_plans.append(
        WalkPlan(
            request_index=len(requests),
            aggressor_actor="B1",
            target_price=p3,
            swept_units=swept2,
            v_star=v3,
            pool=tuple(level_members[p3]),
        )
    )
    requests.append(
        _submit_request(event_id, "B1", Side.BID, p3, swept2 + v3, tick)
    )
    level_qty[p2] = 0
    level_qty[p3] -= v3

    requests.append({"kind": "finish"})

    predicted_cleared = sum(plan.swept_units + plan.v_star for plan in walk_plans)
    sorted_book = tuple(sorted(initial, key=lambda o: (o.arrival_clock, o.order_id)))
    actors = MAKERS + BUYERS
    return EpisodeStream(
        seed_root=seed_root,
        episode_index=episode_index,
        session_stem=f"kp_{seed_root}_{episode_index}",
        actors=actors,
        actor_roles={actor: ("maker" if actor in MAKERS else "aggressor") for actor in actors},
        initial_cash={
            actor: int(cfg["aggressor_cash"]) if actor in BUYERS else int(cfg["maker_cash"])
            for actor in actors
        },
        initial_inventory={
            actor: (
                int(cfg["aggressor_inventory"]) if actor in BUYERS else int(cfg["maker_inventory"])
            )
            for actor in actors
        },
        price_bands=(ref - half_band, ref + half_band),
        latency_window=window,
        initial_book=sorted_book,
        requests=tuple(requests),
        walk_plans=tuple(walk_plans),
        predicted_cleared_volume=predicted_cleared,
        initial_order_count=n_initial,
    )


def build_episode(
    seed_root: int, episode_index: int, cfg: Mapping[str, object]
) -> EpisodeStream:
    """Deterministically build one episode stream (pure function of the inputs)."""

    rng = random.Random(derive_seed(seed_root, "stream", episode_index))
    attempts = int(cfg["build_attempts"])
    for _ in range(attempts):
        stream = _attempt_episode(rng, seed_root, episode_index, cfg)
        if stream is not None:
            return stream
    raise RuntimeError(
        f"episode constraints unsatisfiable after {attempts} attempts "
        f"(seed_root={seed_root}, episode={episode_index})"
    )


def build_prestate(
    stream: EpisodeStream, rule: AllocationRule, draw_seed: int
) -> SessionPrestate:
    """Prestate identical across arms/replays except allocation_rule and draw seed."""

    initial_book = tuple(
        InitialOrder(
            order_id=order.order_id,
            actor=order.actor,
            side=order.side,
            price=order.price,
            quantity=order.quantity,
        )
        for order in stream.initial_book
    )
    return SessionPrestate(
        session_id=f"{stream.session_stem}:{rule.value}:{draw_seed}",
        seed=draw_seed,
        allocation_rule=rule,
        initial_cash=dict(stream.initial_cash),
        initial_inventory=dict(stream.initial_inventory),
        price_bands=stream.price_bands,
        actors=stream.actors,
        actor_roles=dict(stream.actor_roles),
        initial_book=initial_book,
        schema_version="lab-asset-v3.1",
    )


def order_requests(stream: EpisodeStream) -> list[OrderRequest]:
    """The byte-identical request sequence fed to every evaluation of the episode."""

    requests: list[OrderRequest] = []
    for spec in stream.requests:
        if spec["kind"] != "submit":
            continue
        assert isinstance(spec, dict)
        tick = int(spec["match_ts"])
        clocks = ThreeClocks(tick, tick, tick)
        requests.append(
            OrderRequest(
                event_id=int(spec["event_id"]),
                actor=str(spec["actor"]),
                client_order_id=f"C{len(requests) + 1:04d}",
                side=Side(str(spec["side"])),
                price=int(spec["price"]),
                quantity=int(spec["quantity"]),
                clocks=clocks,
            )
        )
    return requests


__all__ = [
    "EpisodeStream",
    "StreamOrder",
    "WalkPlan",
    "build_episode",
    "build_prestate",
    "derive_seed",
    "order_requests",
]
