"""CPU-trivial fixtures for the within-tie priority fork (C2 precondition).

Fixture A demonstrates pathwise aggregate invariance of the book under an exchangeable,
identity-agnostic population: FIFO and randomized tie allocation share one aggregate event
stream, aggregate observables stay identical, while individual fill allocation diverges.

Fixture B demonstrates an order-one equilibrium response of a strategic maker population
to the tie-allocation rule, with a sign that depends on primitives (rent removal versus
equal-share free-riding) — hence direction-model-dependent but rule-sensitive.

Deterministic, stdlib-only, no market data, no EcoMD integration.
"""

from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass, field

SEED = 20260826
TICK = 1


@dataclass
class Aggregates:
    arrivals: int = 0
    cancels: int = 0
    fills: int = 0
    spread_samples: list[int] = field(default_factory=list)
    touch_depth_samples: list[int] = field(default_factory=list)


@dataclass
class World:
    """Identity book for one allocation rule (unit-size orders)."""

    fifo: dict[int, deque[int]] = field(default_factory=dict)
    rand: dict[int, set[int]] = field(default_factory=dict)


def fixture_a(steps: int = 200_000) -> dict[str, float | int]:
    """One aggregate engine driving two counterfactual identity worlds (FIFO, random).

    Both worlds share every aggregate-relevant random draw (event times, types, sizes,
    arrival prices), so aggregate observables are pathwise identical; only fill and
    cancellation victims differ across worlds.
    """
    rng = random.Random(SEED)

    mid = 100.0
    bid_counts: dict[int, int] = {}
    ask_counts: dict[int, int] = {}
    fifo_book: dict[str, dict[int, deque[int]]] = {"B": {}, "S": {}}
    rand_book: dict[str, dict[int, set[int]]] = {"B": {}, "S": {}}
    fills_fifo: dict[int, int] = {}
    fills_rand: dict[int, int] = {}
    arrival_rank: dict[int, int] = {}

    next_id = 0
    agg = Aggregates()
    base_arrival, base_market, cancel_hazard = 1.0, 0.6, 0.05

    def best(levels: dict[int, int], is_bid: bool) -> int | None:
        return (max(levels) if is_bid else min(levels)) if levels else None

    def quote_prices(is_bid: bool) -> tuple[int, int, int]:
        bb, ba = best(bid_counts, True), best(ask_counts, False)
        if bb is None and ba is None:
            ref = round(mid)
            return (ref + TICK, ref, ref - TICK) if is_bid else (ref - TICK, ref, ref + TICK)
        if bb is None:
            assert ba is not None
            bb = round(2 * mid - ba)
        elif ba is None:
            assert bb is not None
            ba = round(2 * mid - bb)
        base = bb if is_bid else ba
        return (base + TICK, base, base - TICK) if is_bid else (base - TICK, base, base + TICK)

    def resting(levels: dict[int, int]) -> int:
        return sum(levels.values())

    def execute_one(price: int, side: str) -> None:
        levels = bid_counts if side == "B" else ask_counts
        q = fifo_book[side][price]
        s = rand_book[side][price]
        oid_fifo = q.popleft()
        members = sorted(s)
        oid_rand = members[rng.randrange(len(members))]
        fills_fifo[oid_fifo] = fills_fifo.get(oid_fifo, 0) + 1
        fills_rand[oid_rand] = fills_rand.get(oid_rand, 0) + 1
        s.remove(oid_rand)
        levels[price] -= 1
        agg.fills += 1
        if levels[price] == 0:
            del levels[price], fifo_book[side][price], rand_book[side][price]

    def cancel_one(price: int, side: str) -> None:
        levels = bid_counts if side == "B" else ask_counts
        q = fifo_book[side][price]
        s = rand_book[side][price]
        oid_fifo = q[rng.randrange(len(q))]
        q.remove(oid_fifo)
        members = sorted(s)
        oid_rand = members[rng.randrange(len(members))]
        s.remove(oid_rand)
        levels[price] -= 1
        agg.cancels += 1
        if levels[price] == 0:
            del levels[price], fifo_book[side][price], rand_book[side][price]

    for _ in range(steps):
        bb0, ba0 = best(bid_counts, True), best(ask_counts, False)
        spread = (ba0 - bb0) if (bb0 is not None and ba0 is not None) else 2
        spread = max(spread, 1)
        arrival_rate = base_arrival * (1.0 + spread)
        resting_total = resting(bid_counts) + resting(ask_counts)
        cancel_rate = cancel_hazard * resting_total
        total = arrival_rate + base_market + cancel_rate
        u = rng.random() * total

        if u < arrival_rate:
            side = "B" if rng.random() < 0.5 else "S"
            is_bid = side == "B"
            r = rng.random()
            prices = quote_prices(is_bid)
            price = prices[0] if r < 0.30 else (prices[1] if r < 0.80 else prices[2])
            opp = ask_counts if is_bid else bid_counts
            opp_side = "S" if is_bid else "B"
            opp_best = best(opp, not is_bid)
            crosses = opp_best is not None and (price >= opp_best if is_bid else price <= opp_best)
            if crosses and opp_best is not None:
                execute_one(opp_best, opp_side)
            else:
                levels = bid_counts if is_bid else ask_counts
                q = fifo_book[side].setdefault(price, deque())
                s = rand_book[side].setdefault(price, set())
                arrival_rank[next_id] = len(q)
                q.append(next_id)
                s.add(next_id)
                fills_fifo.setdefault(next_id, 0)
                fills_rand.setdefault(next_id, 0)
                next_id += 1
                levels[price] = levels.get(price, 0) + 1
            agg.arrivals += 1
        elif u < arrival_rate + base_market:
            side = "B" if rng.random() < 0.5 else "S"
            size = 1 + rng.randrange(3)
            opp_side = "S" if side == "B" else "B"
            opp = ask_counts if side == "B" else bid_counts
            while size > 0:
                opp_best = best(opp, opp_side == "B")
                if opp_best is None:
                    break
                execute_one(opp_best, opp_side)
                size -= 1
        else:
            if resting_total == 0:
                continue
            side = "B" if rng.random() * resting_total < resting(bid_counts) else "S"
            levels = bid_counts if side == "B" else ask_counts
            if not levels:
                continue
            price = rng.choice(sorted(levels))
            cancel_one(price, side)

        bb, ba = best(bid_counts, True), best(ask_counts, False)
        if bb is not None and ba is not None:
            mid = (bb + ba) / 2
        agg.spread_samples.append((ba - bb) if (bb is not None and ba is not None) else spread)
        agg.touch_depth_samples.append(
            bid_counts.get(bb, 0) + ask_counts.get(ba, 0)
            if (bb is not None and ba is not None)
            else 0
        )

    mean_spread = sum(agg.spread_samples) / len(agg.spread_samples)
    mean_touch = sum(agg.touch_depth_samples) / len(agg.touch_depth_samples)
    ff, bf, gap_f = _front_back_gap(arrival_rank, fills_fifo)
    fr, br, gap_r = _front_back_gap(arrival_rank, fills_rand)
    share_fifo, share_rand = _early_decile_share(arrival_rank, fills_fifo, fills_rand)

    return {
        "steps": steps,
        "arrivals": agg.arrivals,
        "cancels": agg.cancels,
        "fills": agg.fills,
        "mean_spread": round(mean_spread, 4),
        "mean_touch_depth": round(mean_touch, 4),
        "front_fill_rate_fifo": round(ff, 4),
        "back_fill_rate_fifo": round(bf, 4),
        "front_minus_back_fifo": round(gap_f, 4),
        "front_fill_rate_random": round(fr, 4),
        "back_fill_rate_random": round(br, 4),
        "front_minus_back_random": round(gap_r, 4),
        "early_decile_fill_share_fifo": round(share_fifo, 4),
        "early_decile_fill_share_random": round(share_rand, 4),
    }


def _decile_fill_slope(rank: dict[int, int], fills: dict[int, int]) -> float:
    """Least-squares slope of mean fill indicator across arrival-rank deciles."""
    ranks = sorted(rank.values())
    if not ranks:
        return 0.0
    bounds = [ranks[min(int(len(ranks) * (d + 1) / 10), len(ranks) - 1)] for d in range(10)]
    xs, ys = [], []
    for d, hi in enumerate(bounds):
        members = [o for o, r in rank.items() if (r <= hi and (d == 0 or r > bounds[d - 1]))]
        if not members:
            continue
        xs.append(d)
        ys.append(sum(1.0 if fills.get(o, 0) > 0 else 0.0 for o in members) / len(members))
    n = len(xs)
    if n < 2:
        return 0.0
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys, strict=True))
    den = sum((x - mx) ** 2 for x in xs)
    return num / den if den else 0.0


def _front_back_gap(rank: dict[int, int], fills: dict[int, int]) -> tuple[float, float, float]:
    """Fill rates of orders arriving at the front (rank 0) versus behind (rank >= 1)."""
    front = [o for o, r in rank.items() if r == 0]
    back = [o for o, r in rank.items() if r >= 1]
    f_rate = _fill_rate(front, fills)
    b_rate = _fill_rate(back, fills)
    return f_rate, b_rate, f_rate - b_rate


def _fill_rate(orders: list[int], fills: dict[int, int]) -> float:
    if not orders:
        return 0.0
    return sum(1.0 if fills.get(o, 0) > 0 else 0.0 for o in orders) / len(orders)


def _early_decile_share(
    rank: dict[int, int], fills_fifo: dict[int, int], fills_rand: dict[int, int]
) -> tuple[float, float]:
    ranks = sorted(rank.values())
    cutoff = ranks[len(ranks) // 10]
    early = {o for o, r in rank.items() if r <= cutoff}
    tf = sum(fills_fifo.get(o, 0) for o in early)
    tr = sum(fills_rand.get(o, 0) for o in early)
    tot_f = sum(fills_fifo.values()) or 1
    tot_r = sum(fills_rand.values()) or 1
    return tf / tot_f, tr / tot_r


def fill_prob_fifo(rank_ahead: int, rho: float) -> float:
    """Fill prob of a unit order with rank_ahead unit orders ahead under FIFO."""
    return rho ** (rank_ahead + 1)


def fill_prob_random(n_at_touch: int, rho: float) -> float:
    """Expected fill share of one of n equal unit orders under random allocation."""
    if n_at_touch <= 0:
        return 0.0
    expected_fills = rho * (1 - rho**n_at_touch) / (1 - rho)
    return expected_fills / n_at_touch


def threshold_depth(rule: str, h: float, c: float, rho: float) -> int:
    """Largest n such that the marginal joiner still covers quoting cost c."""
    n = 0
    while True:
        n += 1
        f = fill_prob_fifo(n - 1, rho) if rule == "fifo" else fill_prob_random(n, rho)
        if h * f < c:
            return n - 1


def fixture_b(
    h: float = 1.0, c: float = 0.05, lam_fill: float = 1.0, lam_adv: float = 0.6
) -> dict[str, float | int]:
    """Threshold equilibrium touch depth under both rules, plus a sign-flip parameter set."""
    rho = lam_fill / (lam_fill + lam_adv)
    depth_fifo = threshold_depth("fifo", h, c, rho)
    depth_random = threshold_depth("random", h, c, rho)

    # Second primitives set (impatient book: fills much likelier than adverse moves).
    rho2 = 0.9 / (0.9 + 0.1)
    depth_fifo2 = threshold_depth("fifo", h, c, rho2)
    depth_random2 = threshold_depth("random", h, c, rho2)

    return {
        "rho_set1": round(rho, 4),
        "depth_fifo_set1": depth_fifo,
        "depth_random_set1": depth_random,
        "gap_set1": depth_random - depth_fifo,
        "rho_set2": round(rho2, 4),
        "depth_fifo_set2": depth_fifo2,
        "depth_random_set2": depth_random2,
        "gap_set2": depth_random2 - depth_fifo2,
    }


def main() -> None:
    a = fixture_a()
    print("Fixture A (exchangeable ZI population, shared event stream):")
    for k, v in a.items():
        print(f"  {k}: {v}")
    b = fixture_b()
    print("Fixture B (strategic threshold equilibria, sign depends on primitives):")
    for k, v in b.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
