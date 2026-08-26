"""Synthetic robot-pilot pipeline (A-2, engineering-only).

Runs deterministic zero-intelligence robot sessions through the reference engine under both
allocation arms, computes the frozen session-statistics vector (sampled event-by-event),
validates exact deterministic replay of every session, and writes a manifest labeled
ENGINEERING-ONLY.

Robot-pilot outputs are engineering evidence for the pipeline only. They are not route
evidence, not laboratory outcomes, and must never be cited as scientific results about human
markets or simulator validity.
"""

from __future__ import annotations

import json
import random
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lab_asset.adapter import to_request
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

ACTORS = ("r1", "r2", "r3", "r4", "r5", "r6")


@dataclass(frozen=True)
class SessionSamples:
    spreads: list[int]
    depths: list[int]
    cancels: int
    executions: int
    tape_length: int


def _best(book: dict[int, list[tuple[str, str, int]]], is_bid: bool) -> int | None:
    return (max(book) if is_bid else min(book)) if book else None


def run_session(
    rule: AllocationRule, seed: int, steps: int = 20_000
) -> tuple[ReferenceEngine, bool, SessionSamples]:
    """One ZI robot session: state-dependent quotes and uniform-exchangeable cancels."""
    rng = random.Random(seed)
    prestate = SessionPrestate(
        session_id=f"PILOT-{rule.value}-{seed}",
        seed=seed,
        allocation_rule=rule,
        initial_cash={a: 10_000.0 for a in ACTORS},
        initial_inventory={a: 0 for a in ACTORS},
        price_bands=(90, 110),
        actors=ACTORS,
    )
    engine = ReferenceEngine(prestate)
    spreads: list[int] = []
    depths: list[int] = []
    cancels = 0
    executions = 0
    def resting_count() -> int:
        return sum(
            len(orders) for book in (engine.bids, engine.asks) for orders in book.values()
        )

    def sample() -> None:
        bb, ba = _best(engine.bids, True), _best(engine.asks, False)
        if bb is not None and ba is not None:
            spreads.append(ba - bb)
            depths.append(len(engine.bids[bb]) + len(engine.asks[ba]))

    for t in range(steps):
        bb, ba = _best(engine.bids, True), _best(engine.asks, False)
        spread = max((ba - bb) if (bb is not None and ba is not None) else 2, 1)
        arrival_rate = 1.0 * (1.0 + spread)
        market_rate = 0.6
        cancel_rate = 0.05 * resting_count()
        total = arrival_rate + market_rate + cancel_rate
        u = rng.random() * total
        next_event = t + 1
        if u < arrival_rate:
            is_bid = rng.random() < 0.5
            r = rng.random()
            if is_bid:
                base = bb if bb is not None else 99
                price = base + 1 if r < 0.30 else (base if r < 0.80 else base - 1)
            else:
                base = ba if ba is not None else 101
                price = base - 1 if r < 0.30 else (base if r < 0.80 else base + 1)
            engine.submit(
                OrderRequest(
                    event_id=next_event,
                    actor=ACTORS[rng.randrange(len(ACTORS))],
                    client_order_id=f"C{next_event:09d}",
                    side=Side.BID if is_bid else Side.ASK,
                    price=max(90, min(110, price)),
                    quantity=1,
                    clocks=ThreeClocks(t, t, t),
                )
            )
        elif u < arrival_rate + market_rate:
            is_buy = rng.random() < 0.5
            if is_buy and ba is not None:
                engine.submit(
                    OrderRequest(
                        event_id=next_event,
                        actor=ACTORS[rng.randrange(len(ACTORS))],
                        client_order_id=f"C{next_event:09d}",
                        side=Side.BID,
                        price=ba + 2,
                        quantity=1,
                        clocks=ThreeClocks(t, t, t),
                    )
                )
            elif not is_buy and bb is not None:
                engine.submit(
                    OrderRequest(
                        event_id=next_event,
                        actor=ACTORS[rng.randrange(len(ACTORS))],
                        client_order_id=f"C{next_event:09d}",
                        side=Side.ASK,
                        price=bb - 2,
                        quantity=1,
                        clocks=ThreeClocks(t, t, t),
                    )
                )
        else:
            resting_ids = [
                (oid, actor)
                for book in (engine.bids, engine.asks)
                for orders in book.values()
                for oid, actor, _ in orders
            ]
            if resting_ids:
                oid, owner = resting_ids[rng.randrange(len(resting_ids))]
                cancel_request = to_request(
                    {"type": "cancel", "actor": owner, "client_order_id": oid},
                    event_id=next_event,
                    client_ts=t,
                    receipt_ts=t,
                    match_ts=t,
                )
                assert isinstance(cancel_request, CancelRequest)
                engine.cancel(cancel_request)
        sample()
    for record in engine.tape:
        if record.event_type == EventType.EXECUTION:
            executions += 1
        elif record.event_type == EventType.ORDER_CANCELLED:
            cancels += 1
    engine.finish()
    report = replay(prestate, engine.tape)
    samples = SessionSamples(
        spreads=spreads,
        depths=depths,
        cancels=cancels,
        executions=executions,
        tape_length=len(engine.tape),
    )
    return engine, report.ok, samples


def session_statistics(samples: SessionSamples, steps: int) -> dict[str, float]:
    return {
        "mean_spread_ticks": sum(samples.spreads) / max(len(samples.spreads), 1),
        "mean_touch_depth_orders": sum(samples.depths) / max(len(samples.depths), 1),
        "cancel_intensity": samples.cancels / max(samples.tape_length, 1),
        "executions": float(samples.executions),
        "tape_length": float(samples.tape_length),
        "steps": float(steps),
    }


def run_pilot(
    sessions_per_arm: int = 4,
    steps: int = 5_000,
    base_seed: int = 20260827,
    out_dir: Path | None = None,
) -> dict[str, object]:
    """Run paired-seed robot sessions under both arms; validate replays; write manifest."""
    arms: dict[str, object] = {}
    for rule in (AllocationRule.FIFO, AllocationRule.RANDOM_WITHIN_TIE):
        stats: list[dict[str, float]] = []
        replays_ok = True
        for i in range(sessions_per_arm):
            seed = base_seed + i  # paired seeds across arms
            _, ok, samples = run_session(rule, seed=seed, steps=steps)
            replays_ok = replays_ok and ok
            stats.append(session_statistics(samples, steps))
        arms[rule.value] = {
            "sessions": sessions_per_arm,
            "all_replays_ok": replays_ok,
            "mean": {key: sum(s[key] for s in stats) / len(stats) for key in stats[0]},
        }
    manifest: dict[str, object] = {
        "label": "lab_asset_robot_pilot",
        "engineering_only": True,
        "not_route_evidence": True,
        "arms": arms,
    }
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "robot_pilot_manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n"
        )
    return manifest


def main() -> None:
    manifest = run_pilot(out_dir=Path("output/lab_asset_pilot"))
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
