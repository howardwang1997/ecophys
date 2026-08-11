"""Controlled intervention worlds for Experiment 141."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from itertools import pairwise
from typing import Literal, TypeAlias

import numpy as np
from numpy.typing import NDArray

from .book import Account, ExchangeRules, LimitOrderBook, Side

TruthFamily: TypeAlias = Literal["none", "single_rate", "two_rate", "confounded"]
ResponseKind: TypeAlias = Literal["frozen", "instant", "single_rate", "two_rate"]

PRIMARY_COMPONENTS = (
    "market_early",
    "market_middle",
    "market_late",
    "cancel_early",
    "cancel_middle",
    "cancel_late",
)


@dataclass(frozen=True)
class WorldSettings:
    n_agents: int
    initial_mid_price: int
    initial_tick_size: int
    post_tick_size: int
    initial_cash: float
    initial_inventory: int
    initial_levels_per_side: int
    initial_orders_per_level: int
    order_quantity: int
    events_per_epoch: int
    pre_epochs: int
    post_epochs: int
    baseline_market_probability: float
    baseline_cancel_probability: float
    target_slope: float
    single_rate: float
    two_rate_fast: float
    two_rate_slow: float
    two_rate_fast_weight: float
    confound_probability_shift: float
    confound_epochs: int

    def __post_init__(self) -> None:
        if self.n_agents < 2:
            raise ValueError("n_agents must be at least two")
        if self.events_per_epoch <= 0 or self.pre_epochs <= 0 or self.post_epochs <= 0:
            raise ValueError("epoch counts must be positive")
        probabilities = (
            self.baseline_market_probability,
            self.baseline_cancel_probability,
        )
        if any(probability <= 0.0 or probability >= 1.0 for probability in probabilities):
            raise ValueError("baseline probabilities must lie strictly between zero and one")
        rates = (self.single_rate, self.two_rate_fast, self.two_rate_slow)
        if any(rate <= 0.0 or rate >= 1.0 for rate in rates):
            raise ValueError("adaptation rates must lie strictly between zero and one")
        if not 0.0 <= self.two_rate_fast_weight <= 1.0:
            raise ValueError("two_rate_fast_weight must lie in [0, 1]")


@dataclass(frozen=True)
class ResponseParameters:
    kind: ResponseKind
    target_slope: float = 0.0
    rate: float = 0.0
    fast_rate: float = 0.0
    slow_rate: float = 0.0
    fast_weight: float = 0.0

    def shift(self, post_epoch: int, magnitude: float) -> float:
        if post_epoch < 0 or self.kind == "frozen":
            return 0.0
        target = self.target_slope * magnitude
        if self.kind == "instant":
            return target
        if self.kind == "single_rate":
            return target * (1.0 - (1.0 - self.rate) ** (post_epoch + 1))
        fast = 1.0 - (1.0 - self.fast_rate) ** (post_epoch + 1)
        slow = 1.0 - (1.0 - self.slow_rate) ** (post_epoch + 1)
        return target * (self.fast_weight * fast + (1.0 - self.fast_weight) * slow)


@dataclass(frozen=True)
class EpochMetrics:
    epoch: int
    is_post: bool
    market_orders: int
    cancel_orders: int
    limit_orders: int
    fills: int
    volume: int
    mean_spread: float
    mean_top_depth: float
    fee_revenue: float
    rule_cancellations: int

    @property
    def market_fraction(self) -> float:
        total = self.market_orders + self.cancel_orders + self.limit_orders
        return self.market_orders / total

    @property
    def cancel_fraction(self) -> float:
        total = self.market_orders + self.cancel_orders + self.limit_orders
        return self.cancel_orders / total


@dataclass(frozen=True)
class SimulationResult:
    seed: int
    magnitude: float
    intervention: bool
    response: ResponseParameters
    confounded: bool
    epochs: tuple[EpochMetrics, ...]
    mechanics_violations: tuple[str, ...]
    event_digest: str

    def primary_effect(self, counterfactual: SimulationResult) -> tuple[float, ...]:
        if len(self.epochs) != len(counterfactual.epochs):
            raise ValueError("paired paths have different epoch counts")
        own_post = self.epochs[-sum(epoch.is_post for epoch in self.epochs) :]
        paired_post = counterfactual.epochs[-sum(epoch.is_post for epoch in counterfactual.epochs) :]
        if len(own_post) < 6:
            raise ValueError("at least six post-intervention epochs are required")
        boundaries = (0, 3, max(4, len(own_post) // 2), len(own_post))
        output: list[float] = []
        for field in ("market_fraction", "cancel_fraction"):
            for start, stop in pairwise(boundaries):
                own = np.mean([getattr(epoch, field) for epoch in own_post[start:stop]])
                paired = np.mean([getattr(epoch, field) for epoch in paired_post[start:stop]])
                output.append(float(own - paired))
        return tuple(output)

    def to_dict(self) -> dict[str, object]:
        return {
            "seed": self.seed,
            "magnitude": self.magnitude,
            "intervention": self.intervention,
            "response": asdict(self.response),
            "confounded": self.confounded,
            "epochs": [asdict(epoch) for epoch in self.epochs],
            "mechanics_violations": list(self.mechanics_violations),
            "event_digest": self.event_digest,
        }


def truth_response(settings: WorldSettings, family: TruthFamily) -> ResponseParameters:
    if family == "none":
        return ResponseParameters(kind="frozen")
    if family in ("single_rate", "confounded"):
        return ResponseParameters(
            kind="single_rate",
            target_slope=settings.target_slope,
            rate=settings.single_rate,
        )
    if family == "two_rate":
        return ResponseParameters(
            kind="two_rate",
            target_slope=settings.target_slope,
            fast_rate=settings.two_rate_fast,
            slow_rate=settings.two_rate_slow,
            fast_weight=settings.two_rate_fast_weight,
        )
    raise ValueError(f"unknown truth family: {family}")


def candidate_response(
    candidate: Literal["frozen", "instant", "multiclock"],
    target_slope: float,
    rate: float,
) -> ResponseParameters:
    if candidate == "frozen":
        return ResponseParameters(kind="frozen")
    if candidate == "instant":
        return ResponseParameters(kind="instant", target_slope=target_slope)
    return ResponseParameters(kind="single_rate", target_slope=target_slope, rate=rate)


def _logit(probability: float) -> float:
    return math.log(probability / (1.0 - probability))


def _sigmoid(value: float) -> float:
    if value >= 0.0:
        return 1.0 / (1.0 + math.exp(-value))
    exponential = math.exp(value)
    return exponential / (1.0 + exponential)


def expected_market_probability(
    settings: WorldSettings,
    response: ResponseParameters,
    magnitude: float,
    post_epoch: int,
    *,
    confounded: bool = False,
) -> float:
    probability = _sigmoid(
        _logit(settings.baseline_market_probability) + response.shift(post_epoch, magnitude)
    )
    if confounded and 0 <= post_epoch < settings.confound_epochs:
        probability += settings.confound_probability_shift
    return min(0.94, max(0.01, probability))


def _initial_book(settings: WorldSettings) -> tuple[LimitOrderBook, int]:
    accounts = {
        agent_id: Account(
            cash=settings.initial_cash,
            inventory=settings.initial_inventory,
        )
        for agent_id in range(settings.n_agents)
    }
    book = LimitOrderBook(ExchangeRules(tick_size=settings.initial_tick_size), accounts)
    order_id = 1
    for level in range(1, settings.initial_levels_per_side + 1):
        bid = settings.initial_mid_price - level * settings.initial_tick_size
        ask = settings.initial_mid_price + level * settings.initial_tick_size
        for slot in range(settings.initial_orders_per_level):
            buyer = (2 * slot + level) % settings.n_agents
            seller = (2 * slot + level + 1) % settings.n_agents
            book.submit_limit(order_id, buyer, "buy", bid, settings.order_quantity)
            order_id += 1
            book.submit_limit(order_id, seller, "sell", ask, settings.order_quantity)
            order_id += 1
    return book, order_id


def _top_maker(book: LimitOrderBook, side: Side) -> int | None:
    target_price = book.best_ask if side == "buy" else book.best_bid
    opposite = "sell" if side == "buy" else "buy"
    if target_price is None:
        return None
    candidates = (
        book.order(order_id)
        for order_id in book.active_order_ids
        if book.order(order_id).side == opposite and book.order(order_id).price == target_price
    )
    first = min(candidates, key=lambda order: order.sequence, default=None)
    return None if first is None else first.agent_id


def _choose_agent(settings: WorldSettings, uniform: float, excluded: int | None = None) -> int:
    agent = min(settings.n_agents - 1, int(uniform * settings.n_agents))
    if excluded is not None and agent == excluded:
        agent = (agent + 1) % settings.n_agents
    return agent


def _passive_price(
    book: LimitOrderBook,
    settings: WorldSettings,
    side: Side,
    level: int,
) -> int:
    tick = book.rules.tick_size
    if side == "buy":
        ceiling = (
            book.best_ask - tick
            if book.best_ask is not None
            else (book.last_trade_price or settings.initial_mid_price) // tick * tick - tick
        )
        return max(tick, ceiling - level * tick)
    floor = (
        book.best_bid + tick
        if book.best_bid is not None
        else math.ceil((book.last_trade_price or settings.initial_mid_price) / tick) * tick + tick
    )
    return floor + level * tick


def _submit_limit_event(
    book: LimitOrderBook,
    settings: WorldSettings,
    order_id: int,
    side: Side,
    uniforms: NDArray[np.float64],
) -> tuple[int, int, int]:
    aggressive = uniforms[4] < 0.25
    opposite_price = book.best_ask if side == "buy" else book.best_bid
    excluded = _top_maker(book, side) if aggressive and opposite_price is not None else None
    agent = _choose_agent(settings, float(uniforms[2]), excluded)
    level = min(3, int(uniforms[3] * 4.0))
    price = opposite_price if aggressive and opposite_price is not None else _passive_price(
        book, settings, side, level
    )
    fills = book.submit_limit(order_id, agent, side, price, settings.order_quantity)
    return order_id + 1, len(fills), sum(fill.quantity for fill in fills)


def simulate_path(
    settings: WorldSettings,
    seed: int,
    magnitude: float,
    response: ResponseParameters,
    *,
    intervention: bool,
    confounded: bool = False,
) -> SimulationResult:
    """Simulate one path while checking exchange invariants after every event."""

    if magnitude < 0.0:
        raise ValueError("intervention magnitude must be nonnegative")
    rng = np.random.default_rng(seed)
    book, next_order_id = _initial_book(settings)
    metrics: list[EpochMetrics] = []
    violations: set[str] = set(book.invariant_violations())
    digest = hashlib.sha256()
    total_epochs = settings.pre_epochs + settings.post_epochs

    for epoch in range(total_epochs):
        is_post = epoch >= settings.pre_epochs
        post_epoch = epoch - settings.pre_epochs
        rule_cancellations = 0
        if intervention and epoch == settings.pre_epochs:
            cancelled = book.change_rules(ExchangeRules(tick_size=settings.post_tick_size))
            rule_cancellations = len(cancelled)
            digest.update(json.dumps(cancelled, separators=(",", ":")).encode())

        active_response = response if intervention else ResponseParameters(kind="frozen")
        market_probability = expected_market_probability(
            settings,
            active_response,
            magnitude,
            post_epoch if is_post else -1,
            confounded=intervention and confounded,
        )
        cancel_probability = settings.baseline_cancel_probability + 0.5 * (
            settings.baseline_market_probability - market_probability
        )
        cancel_probability = min(0.40, max(0.05, cancel_probability))

        market_orders = 0
        cancel_orders = 0
        limit_orders = 0
        fill_count = 0
        volume = 0
        spread_sum = 0.0
        top_depth_sum = 0.0
        spread_observations = 0
        fee_start = book.exchange_cash

        for _ in range(settings.events_per_epoch):
            uniforms = rng.random(8)
            side: Side = "buy" if uniforms[1] < 0.5 else "sell"
            action = float(uniforms[0])
            if action < market_probability:
                excluded = _top_maker(book, side)
                if excluded is None:
                    next_order_id, fills, filled_volume = _submit_limit_event(
                        book, settings, next_order_id, side, uniforms
                    )
                    limit_orders += 1
                else:
                    agent = _choose_agent(settings, float(uniforms[2]), excluded)
                    fills_data = book.submit_market(agent, side, settings.order_quantity)
                    fills = len(fills_data)
                    filled_volume = sum(fill.quantity for fill in fills_data)
                    market_orders += 1
            elif action < market_probability + cancel_probability and book.active_order_ids:
                active = book.active_order_ids
                index = min(len(active) - 1, int(uniforms[2] * len(active)))
                order = book.order(active[index])
                book.cancel(order.order_id, order.agent_id)
                cancel_orders += 1
                fills = 0
                filled_volume = 0
            else:
                next_order_id, fills, filled_volume = _submit_limit_event(
                    book, settings, next_order_id, side, uniforms
                )
                limit_orders += 1

            fill_count += fills
            volume += filled_volume
            event_violations = book.invariant_violations()
            violations.update(event_violations)
            snapshot = book.snapshot()
            if snapshot.spread is not None:
                spread_sum += snapshot.spread
                spread_observations += 1
            top_depth_sum += snapshot.bid_top_depth + snapshot.ask_top_depth
            digest.update(
                f"{action:.17g}|{side}|{market_orders}|{cancel_orders}|{limit_orders}|"
                f"{filled_volume}|{snapshot.best_bid}|{snapshot.best_ask};".encode()
            )

        metrics.append(
            EpochMetrics(
                epoch=epoch,
                is_post=is_post,
                market_orders=market_orders,
                cancel_orders=cancel_orders,
                limit_orders=limit_orders,
                fills=fill_count,
                volume=volume,
                mean_spread=(spread_sum / spread_observations if spread_observations else math.nan),
                mean_top_depth=top_depth_sum / settings.events_per_epoch,
                fee_revenue=book.exchange_cash - fee_start,
                rule_cancellations=rule_cancellations,
            )
        )

    return SimulationResult(
        seed=seed,
        magnitude=magnitude,
        intervention=intervention,
        response=response,
        confounded=confounded,
        epochs=tuple(metrics),
        mechanics_violations=tuple(sorted(violations)),
        event_digest=digest.hexdigest(),
    )


def anchor_signature(result: SimulationResult) -> str:
    payload = {
        "seed": result.seed,
        "magnitude": result.magnitude,
        "event_digest": result.event_digest,
        "counts": [
            [
                epoch.market_orders,
                epoch.cancel_orders,
                epoch.limit_orders,
                epoch.fills,
                epoch.volume,
                epoch.rule_cancellations,
            ]
            for epoch in result.epochs
        ],
        "violations": result.mechanics_violations,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(canonical).hexdigest()
