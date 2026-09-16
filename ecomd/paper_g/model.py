"""Independent event accounting and a finite-state analytic reference."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class Law:
    buy_probability: float
    buyer_high_probability: float
    seller_low_probability: float

    def __post_init__(self) -> None:
        if not all(0 <= x <= 1 for x in self.values()):
            raise ValueError("probabilities must lie in [0,1]")

    def values(self) -> tuple[float, float, float]:
        return (self.buy_probability, self.buyer_high_probability, self.seller_low_probability)


@dataclass(frozen=True)
class State:
    inventory: int
    bid_depth: int
    ask_depth: int


@dataclass(frozen=True)
class Action:
    hedge: int
    bid: int
    ask: int


ACTIONS = tuple(Action(h, b, a) for h, b, a in product((-1, 0, 1), (0, 98, 99), (0, 101, 102)))


@dataclass(frozen=True)
class Feedback:
    customer_buy: bool
    filled: bool
    willingness: int | None


@dataclass(frozen=True)
class EventResult:
    state: State
    reward: int
    feedback: Feedback


class Market:
    """Cash-settled event implementation, independent of the analytic transition builder."""

    def __init__(self, capacity: int, horizon: int, initial_inventory: int = 1) -> None:
        if capacity < 1 or not 0 <= initial_inventory <= capacity or horizon < 1:
            raise ValueError("invalid initial market")
        self.capacity = capacity
        self.state = State(initial_inventory, 1, 1)
        endowment = 103 * (2 * horizon + capacity)
        self.cash = [endowment] * 4
        self.inventory = [initial_inventory, 2 * horizon + capacity, 0, horizon]
        self.initial_cash_total = sum(self.cash)
        self.initial_inventory_total = sum(self.inventory)
        self.initial_dealer_cash = endowment
        self.initial_dealer_inventory = initial_inventory

    def step(
        self, action: Action, customer_buy: bool, willingness: int,
        refill_bid: bool, refill_ask: bool, reveal: bool,
    ) -> EventResult:
        q, db, da = self.state.inventory, self.state.bid_depth, self.state.ask_depth
        if action not in ACTIONS or willingness not in ((101, 102) if customer_buy else (98, 99)):
            raise ValueError("invalid action or customer type")
        if action.hedge == 1 and (not da or q == self.capacity):
            raise ValueError("unavailable buy hedge")
        if action.hedge == -1 and (not db or q == 0):
            raise ValueError("unavailable sell hedge")
        after_hedge = q + action.hedge
        if (action.bid and after_hedge == self.capacity) or (action.ask and after_hedge == 0):
            raise ValueError("quote exceeds inventory bounds")
        old_wealth = self.cash[0] + 100 * self.inventory[0]
        if action.hedge == 1:
            self._transfer(1, 0, 101)
            da = 0
        elif action.hedge == -1:
            self._transfer(0, 1, 99)
            db = 0
        filled = False
        if customer_buy and action.ask and willingness >= action.ask:
            self._transfer(0, 2, action.ask)
            filled = True
        elif not customer_buy and action.bid and willingness <= action.bid:
            self._transfer(3, 0, action.bid)
            filled = True
        self.state = State(self.inventory[0], int(bool(db) or refill_bid), int(bool(da) or refill_ask))
        self.check_accounts()
        reward = self.cash[0] + 100 * self.inventory[0] - old_wealth
        return EventResult(self.state, reward, Feedback(customer_buy, filled, willingness if reveal else None))

    def _transfer(self, seller: int, buyer: int, price: int) -> None:
        if self.inventory[seller] < 1 or self.cash[buyer] < price:
            raise ValueError("unfunded counterparty")
        self.inventory[seller] -= 1
        self.inventory[buyer] += 1
        self.cash[seller] += price
        self.cash[buyer] -= price

    def check_accounts(self) -> None:
        if sum(self.cash) != self.initial_cash_total or sum(self.inventory) != self.initial_inventory_total:
            raise AssertionError("accounting conservation violated")
        if min(self.cash) < 0 or min(self.inventory) < 0 or not 0 <= self.inventory[0] <= self.capacity:
            raise AssertionError("resource bound violated")

    def wealth(self) -> int:
        return self.cash[0] - self.initial_dealer_cash + 100 * (self.inventory[0] - self.initial_dealer_inventory)


class TabularModel:
    """Analytic expectation kernel; does not call the event implementation."""

    def __init__(self, capacity: int, refill_probability: float) -> None:
        if capacity < 1 or not 0 <= refill_probability <= 1:
            raise ValueError("invalid capacity or replenishment")
        self.capacity = capacity
        self.rho = refill_probability
        self.states = tuple(State(q, b, a) for q, b, a in product(range(capacity + 1), (0, 1), (0, 1)))
        self.index = {s: i for i, s in enumerate(self.states)}
        self.legal = np.zeros((len(self.states), len(ACTIONS)), dtype=bool)
        for i, s in enumerate(self.states):
            for j, a in enumerate(ACTIONS):
                q = s.inventory + a.hedge
                self.legal[i, j] = (
                    0 <= q <= capacity and (a.hedge != -1 or s.bid_depth == 1)
                    and (a.hedge != 1 or s.ask_depth == 1)
                    and (not a.bid or q < capacity) and (not a.ask or q > 0)
                )

    def kernel(self, law: Law) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        size = len(self.states)
        transition = np.zeros((size, len(ACTIONS), size), dtype=np.float64)
        reward = np.zeros((size, len(ACTIONS)), dtype=np.float64)
        p, high, low = law.values()
        types = ((True, 102, p * high), (True, 101, p * (1-high)),
                 (False, 98, (1-p)*low), (False, 99, (1-p)*(1-low)))
        for i, s in enumerate(self.states):
            for j, a in enumerate(ACTIONS):
                if not self.legal[i, j]:
                    continue
                qh = s.inventory + a.hedge
                db, da = (0 if a.hedge == -1 else s.bid_depth), (0 if a.hedge == 1 else s.ask_depth)
                pb, pa = (1.0 if db else self.rho), (1.0 if da else self.rho)
                for buy, value, weight in types:
                    delta = -1 if buy and a.ask and value >= a.ask else 0
                    if not buy and a.bid and value <= a.bid:
                        delta = 1
                    gain = -abs(a.hedge) + (100-a.bid if delta == 1 else a.ask-100 if delta == -1 else 0)
                    reward[i, j] += weight * gain
                    for nb, na in product((0, 1), repeat=2):
                        probability = weight * (pb if nb else 1-pb) * (pa if na else 1-pa)
                        transition[i, j, self.index[State(qh+delta, nb, na)]] += probability
        return transition, reward

    def solve(self, law: Law, horizon: int) -> tuple[NDArray[np.float64], NDArray[np.uint8]]:
        if horizon < 0:
            raise ValueError("negative horizon")
        transition, reward = self.kernel(law)
        values = np.zeros((horizon+1, len(self.states)), dtype=np.float64)
        policy = np.zeros((horizon+1, len(self.states)), dtype=np.uint8)
        for h in range(1, horizon+1):
            scores = reward + np.einsum("sak,k->sa", transition, values[h-1], optimize=False)
            scores[~self.legal] = -np.inf
            policy[h] = np.argmax(scores, axis=1)
            values[h] = scores[np.arange(len(self.states)), policy[h]]
        return values, policy
