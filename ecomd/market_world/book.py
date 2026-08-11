"""A minimal exact price--time-priority exchange kernel."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Literal, TypeAlias

Side: TypeAlias = Literal["buy", "sell"]


@dataclass(frozen=True)
class ExchangeRules:
    tick_size: int
    maker_fee_bps: float = 0.0
    taker_fee_bps: float = 0.0
    cancel_nonconforming_on_tick_change: bool = True

    def __post_init__(self) -> None:
        if self.tick_size <= 0:
            raise ValueError("tick_size must be positive")
        if self.maker_fee_bps < -100.0 or self.taker_fee_bps < -100.0:
            raise ValueError("fee rebates below -100 bps are unsupported")


@dataclass
class Account:
    cash: float
    inventory: int

    def __post_init__(self) -> None:
        if self.cash < 0.0 or self.inventory < 0:
            raise ValueError("initial cash and inventory must be nonnegative")


@dataclass
class RestingOrder:
    order_id: int
    agent_id: int
    side: Side
    price: int
    remaining: int
    sequence: int


@dataclass(frozen=True)
class Fill:
    maker_order_id: int
    maker_agent_id: int
    taker_agent_id: int
    taker_side: Side
    price: int
    quantity: int
    maker_fee: float
    taker_fee: float


@dataclass(frozen=True)
class BookSnapshot:
    best_bid: int | None
    best_ask: int | None
    spread: int | None
    bid_top_depth: int
    ask_top_depth: int
    total_bid_depth: int
    total_ask_depth: int
    resting_orders: int
    last_trade_price: int | None
    exchange_cash: float


class LimitOrderBook:
    """Individual-order book with exact matching and account settlement."""

    def __init__(self, rules: ExchangeRules, accounts: dict[int, Account]) -> None:
        if not accounts:
            raise ValueError("at least one account is required")
        self.rules = rules
        self.accounts = {
            agent_id: Account(cash=account.cash, inventory=account.inventory)
            for agent_id, account in accounts.items()
        }
        self._orders: dict[int, RestingOrder] = {}
        self._bids: dict[int, deque[int]] = {}
        self._asks: dict[int, deque[int]] = {}
        self._sequence = 0
        self.exchange_cash = 0.0
        self.last_trade_price: int | None = None
        self._initial_cash = sum(account.cash for account in self.accounts.values())
        self._initial_inventory = sum(account.inventory for account in self.accounts.values())

    @property
    def active_order_ids(self) -> tuple[int, ...]:
        return tuple(sorted(self._orders))

    @property
    def best_bid(self) -> int | None:
        self._clean_empty_levels("buy")
        return max(self._bids) if self._bids else None

    @property
    def best_ask(self) -> int | None:
        self._clean_empty_levels("sell")
        return min(self._asks) if self._asks else None

    def order(self, order_id: int) -> RestingOrder:
        try:
            return self._orders[order_id]
        except KeyError as error:
            raise KeyError(f"unknown active order {order_id}") from error

    def _queues(self, side: Side) -> dict[int, deque[int]]:
        return self._bids if side == "buy" else self._asks

    def _clean_level(self, side: Side, price: int) -> None:
        queues = self._queues(side)
        queue = queues.get(price)
        if queue is None:
            return
        while queue and queue[0] not in self._orders:
            queue.popleft()
        if not queue:
            del queues[price]

    def _clean_empty_levels(self, side: Side) -> None:
        for price in tuple(self._queues(side)):
            self._clean_level(side, price)

    def _reserved_cash(self, agent_id: int) -> float:
        fee_fraction = max(0.0, self.rules.maker_fee_bps, self.rules.taker_fee_bps) / 10_000.0
        return sum(
            order.price * order.remaining * (1.0 + fee_fraction)
            for order in self._orders.values()
            if order.agent_id == agent_id and order.side == "buy"
        )

    def _reserved_inventory(self, agent_id: int) -> int:
        return sum(
            order.remaining
            for order in self._orders.values()
            if order.agent_id == agent_id and order.side == "sell"
        )

    def _require_agent(self, agent_id: int) -> Account:
        try:
            return self.accounts[agent_id]
        except KeyError as error:
            raise ValueError(f"unknown agent {agent_id}") from error

    def _validate_limit_order(
        self,
        order_id: int,
        agent_id: int,
        side: Side,
        price: int,
        quantity: int,
    ) -> None:
        if side not in ("buy", "sell"):
            raise ValueError(f"unsupported side: {side}")
        if order_id in self._orders:
            raise ValueError(f"duplicate active order_id {order_id}")
        if price <= 0 or price % self.rules.tick_size != 0:
            raise ValueError("limit price violates the active tick grid")
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        account = self._require_agent(agent_id)
        if side == "buy":
            fee_fraction = max(0.0, self.rules.maker_fee_bps, self.rules.taker_fee_bps) / 10_000.0
            required = price * quantity * (1.0 + fee_fraction)
            available = account.cash - self._reserved_cash(agent_id)
            if available + 1e-9 < required:
                raise ValueError("insufficient unreserved cash")
        else:
            available_inventory = account.inventory - self._reserved_inventory(agent_id)
            if available_inventory < quantity:
                raise ValueError("insufficient unreserved inventory")

    def submit_limit(
        self,
        order_id: int,
        agent_id: int,
        side: Side,
        price: int,
        quantity: int,
    ) -> tuple[Fill, ...]:
        self._validate_limit_order(order_id, agent_id, side, price, quantity)
        fills, remaining = self._match(agent_id, side, quantity, price)
        if remaining:
            order = RestingOrder(
                order_id=order_id,
                agent_id=agent_id,
                side=side,
                price=price,
                remaining=remaining,
                sequence=self._sequence,
            )
            self._sequence += 1
            self._orders[order_id] = order
            self._queues(side).setdefault(price, deque()).append(order_id)
        return tuple(fills)

    def submit_market(
        self,
        agent_id: int,
        side: Side,
        quantity: int,
    ) -> tuple[Fill, ...]:
        if side not in ("buy", "sell") or quantity <= 0:
            raise ValueError("market order requires a valid side and positive quantity")
        account = self._require_agent(agent_id)
        executable = self._marketable_quantity(side, quantity)
        if side == "sell":
            available_inventory = account.inventory - self._reserved_inventory(agent_id)
            if available_inventory < executable:
                raise ValueError("insufficient unreserved inventory")
        else:
            estimated_cost = self._market_buy_cost(executable)
            available_cash = account.cash - self._reserved_cash(agent_id)
            if available_cash + 1e-9 < estimated_cost:
                raise ValueError("insufficient unreserved cash")
        fills, _ = self._match(agent_id, side, executable, None)
        return tuple(fills)

    def _marketable_quantity(self, side: Side, requested: int) -> int:
        opposite = "sell" if side == "buy" else "buy"
        available = sum(
            order.remaining for order in self._orders.values() if order.side == opposite
        )
        return min(requested, available)

    def _market_buy_cost(self, quantity: int) -> float:
        remaining = quantity
        cost = 0.0
        for price in sorted(self._asks):
            for order_id in self._asks[price]:
                order = self._orders.get(order_id)
                if order is None:
                    continue
                filled = min(remaining, order.remaining)
                cost += filled * price
                remaining -= filled
                if remaining == 0:
                    fee = cost * max(0.0, self.rules.taker_fee_bps) / 10_000.0
                    return cost + fee
        fee = cost * max(0.0, self.rules.taker_fee_bps) / 10_000.0
        return cost + fee

    def _crosses(self, side: Side, resting_price: int, limit_price: int | None) -> bool:
        if limit_price is None:
            return True
        if side == "buy":
            return resting_price <= limit_price
        return resting_price >= limit_price

    def _best_opposite(self, side: Side) -> tuple[Side, int] | None:
        opposite: Side = "sell" if side == "buy" else "buy"
        price = self.best_ask if opposite == "sell" else self.best_bid
        return None if price is None else (opposite, price)

    def _match(
        self,
        taker_agent_id: int,
        taker_side: Side,
        quantity: int,
        limit_price: int | None,
    ) -> tuple[list[Fill], int]:
        fills: list[Fill] = []
        remaining = quantity
        while remaining > 0:
            best = self._best_opposite(taker_side)
            if best is None:
                break
            maker_side, price = best
            if not self._crosses(taker_side, price, limit_price):
                break
            self._clean_level(maker_side, price)
            queue = self._queues(maker_side).get(price)
            if not queue:
                continue
            maker_id = queue[0]
            maker = self._orders[maker_id]
            filled = min(remaining, maker.remaining)
            fill = self._settle(maker, taker_agent_id, taker_side, price, filled)
            fills.append(fill)
            maker.remaining -= filled
            remaining -= filled
            self.last_trade_price = price
            if maker.remaining == 0:
                del self._orders[maker_id]
                queue.popleft()
                if not queue:
                    del self._queues(maker_side)[price]
        return fills, remaining

    def _settle(
        self,
        maker: RestingOrder,
        taker_agent_id: int,
        taker_side: Side,
        price: int,
        quantity: int,
    ) -> Fill:
        maker_account = self.accounts[maker.agent_id]
        taker_account = self.accounts[taker_agent_id]
        notional = float(price * quantity)
        maker_fee = notional * self.rules.maker_fee_bps / 10_000.0
        taker_fee = notional * self.rules.taker_fee_bps / 10_000.0
        if taker_side == "buy":
            buyer, seller = taker_account, maker_account
            buyer_fee, seller_fee = taker_fee, maker_fee
        else:
            buyer, seller = maker_account, taker_account
            buyer_fee, seller_fee = maker_fee, taker_fee
        buyer.cash -= notional + buyer_fee
        buyer.inventory += quantity
        seller.cash += notional - seller_fee
        seller.inventory -= quantity
        self.exchange_cash += maker_fee + taker_fee
        return Fill(
            maker_order_id=maker.order_id,
            maker_agent_id=maker.agent_id,
            taker_agent_id=taker_agent_id,
            taker_side=taker_side,
            price=price,
            quantity=quantity,
            maker_fee=maker_fee,
            taker_fee=taker_fee,
        )

    def cancel(
        self,
        order_id: int,
        agent_id: int,
        quantity: int | None = None,
    ) -> int:
        order = self.order(order_id)
        if order.agent_id != agent_id:
            raise ValueError("only the owner may cancel an order")
        cancelled = order.remaining if quantity is None else quantity
        if cancelled <= 0 or cancelled > order.remaining:
            raise ValueError("invalid cancellation quantity")
        order.remaining -= cancelled
        if order.remaining == 0:
            del self._orders[order_id]
            self._clean_level(order.side, order.price)
        return cancelled

    def change_rules(self, rules: ExchangeRules) -> tuple[int, ...]:
        cancelled: list[int] = []
        if rules.tick_size != self.rules.tick_size and rules.cancel_nonconforming_on_tick_change:
            for order_id, order in tuple(self._orders.items()):
                if order.price % rules.tick_size:
                    self.cancel(order_id, order.agent_id)
                    cancelled.append(order_id)
        self.rules = rules
        return tuple(sorted(cancelled))

    def _depth_at(self, side: Side, price: int | None) -> int:
        if price is None:
            return 0
        return sum(
            self._orders[order_id].remaining
            for order_id in self._queues(side).get(price, ())
            if order_id in self._orders
        )

    def snapshot(self) -> BookSnapshot:
        best_bid = self.best_bid
        best_ask = self.best_ask
        return BookSnapshot(
            best_bid=best_bid,
            best_ask=best_ask,
            spread=None if best_bid is None or best_ask is None else best_ask - best_bid,
            bid_top_depth=self._depth_at("buy", best_bid),
            ask_top_depth=self._depth_at("sell", best_ask),
            total_bid_depth=sum(
                order.remaining for order in self._orders.values() if order.side == "buy"
            ),
            total_ask_depth=sum(
                order.remaining for order in self._orders.values() if order.side == "sell"
            ),
            resting_orders=len(self._orders),
            last_trade_price=self.last_trade_price,
            exchange_cash=self.exchange_cash,
        )

    def invariant_violations(self) -> tuple[str, ...]:
        violations: list[str] = []
        queued: set[int] = set()
        for side, queues in (("buy", self._bids), ("sell", self._asks)):
            for price, queue in queues.items():
                for order_id in queue:
                    order = self._orders.get(order_id)
                    if order is None:
                        continue
                    queued.add(order_id)
                    if order.side != side or order.price != price:
                        violations.append("queue_order_mismatch")
        for order_id, order in self._orders.items():
            if order_id not in queued:
                violations.append("active_order_missing_from_queue")
            if order.remaining <= 0:
                violations.append("nonpositive_depth")
            if order.price <= 0 or order.price % self.rules.tick_size:
                violations.append("tick_grid")
        best_bid = self.best_bid
        best_ask = self.best_ask
        if best_bid is not None and best_ask is not None and best_bid >= best_ask:
            violations.append("crossed_book")
        total_cash = sum(account.cash for account in self.accounts.values()) + self.exchange_cash
        if abs(total_cash - self._initial_cash) > max(1e-6, abs(self._initial_cash) * 1e-12):
            violations.append("cash_conservation")
        total_inventory = sum(account.inventory for account in self.accounts.values())
        if total_inventory != self._initial_inventory:
            violations.append("inventory_conservation")
        if any(account.cash < -1e-7 for account in self.accounts.values()):
            violations.append("negative_cash")
        if any(account.inventory < 0 for account in self.accounts.values()):
            violations.append("negative_inventory")
        return tuple(sorted(set(violations)))
