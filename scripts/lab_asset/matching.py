"""Deterministic reference CDA kernel for FIFO and random-unit price allocation.

The engine is deterministic given the complete session prestate and request stream.  It
settles cash and inventory, reserves resources for resting orders, preserves FIFO rank after
partial fills, records semantic random-unit draws, and seals every transition.
"""

from __future__ import annotations

import random
from itertools import pairwise

from lab_asset.schema import (
    AllocationRule,
    CancelRejectionReason,
    CancelRequest,
    EventType,
    Execution,
    InformationRelease,
    LatencyChoice,
    LatencyChoiceRejectionReason,
    OrderRequest,
    RejectionReason,
    SessionPrestate,
    Side,
    TapeRecord,
    ThreeClocks,
    aggregate_state_hash,
    prestate_hash,
    state_hash,
)

RestingOrder = tuple[str, str, int]  # order_id, actor, remaining quantity
StateSnapshot = tuple[str, str]


class ReferenceEngine:
    def __init__(self, prestate: SessionPrestate) -> None:
        self._validate_prestate(prestate)
        self.prestate = prestate
        self.prestate_digest = prestate_hash(prestate)
        self.rng = random.Random(prestate.seed)
        self.sequence = 0
        self.bids: dict[int, list[RestingOrder]] = {}
        self.asks: dict[int, list[RestingOrder]] = {}
        self.cash = dict(prestate.initial_cash)
        self.inventory = dict(prestate.initial_inventory)
        self.units_bought = {actor: 0 for actor in prestate.actors}
        self.units_sold = {actor: 0 for actor in prestate.actors}
        self.realized_induced_surplus = {actor: 0 for actor in prestate.actors}
        self.order_meta: dict[str, tuple[str, Side, int]] = {}
        self.order_status: dict[str, str] = {}
        self.used_client_ids: set[str] = set()
        self.latency_choices: dict[tuple[int, str], int] = {}
        self.tape: list[TapeRecord] = []
        self._order_counter = 0
        self._exec_counter = 0
        self.last_match_ts = prestate.scheduler_tick
        self._load_initial_book()
        self._record_and_seal(
            EventType.SESSION_START,
            {
                "session_id": prestate.session_id,
                "schema_version": prestate.schema_version,
                "allocation_rule": prestate.allocation_rule.value,
                "prestate_hash": self.prestate_digest,
            },
        )

    # ------------------------------------------------------------------ public state
    def identity_state_digest(self) -> str:
        return self._hash()

    def aggregate_state_digest(self) -> str:
        return self._aggregate_hash()

    def available_information(self) -> tuple[InformationRelease, ...]:
        """Information releases visible at the current matching tick."""

        return tuple(
            release
            for release in self.prestate.information_schedule
            if release.tick <= self.last_match_ts
        )

    # ------------------------------------------------------------------ state sealing
    def _hash(self) -> str:
        return state_hash(
            prestate_digest=self.prestate_digest,
            bids=self.bids,
            asks=self.asks,
            cash=self.cash,
            inventory=self.inventory,
            units_bought=self.units_bought,
            units_sold=self.units_sold,
            realized_induced_surplus=self.realized_induced_surplus,
            order_meta=self.order_meta,
            order_status=self.order_status,
            used_client_ids=self.used_client_ids,
            latency_choices=self.latency_choices,
            sequence=self.sequence,
            order_counter=self._order_counter,
            execution_counter=self._exec_counter,
            last_match_ts=self.last_match_ts,
            rng_state=self.rng.getstate(),
        )

    def _aggregate_hash(self) -> str:
        return aggregate_state_hash(
            bids=self.bids,
            asks=self.asks,
            cash=self.cash,
            inventory=self.inventory,
            last_match_ts=self.last_match_ts,
        )

    def _snapshot(self) -> StateSnapshot:
        return self._hash(), self._aggregate_hash()

    def _record_and_seal(
        self,
        event_type: EventType,
        payload: dict[str, object],
        before: StateSnapshot | None = None,
    ) -> TapeRecord:
        pre_full, pre_aggregate = before if before is not None else self._snapshot()
        self.sequence += 1
        record = TapeRecord(
            sequence=self.sequence,
            event_type=event_type,
            payload=payload,
            pre_state_hash=pre_full,
            post_state_hash=self._hash(),
            pre_aggregate_state_hash=pre_aggregate,
            post_aggregate_state_hash=self._aggregate_hash(),
        )
        self.tape.append(record)
        return record

    # ------------------------------------------------------------------ book helpers
    def _best(self, side: Side) -> int | None:
        book = self.bids if side == Side.BID else self.asks
        return (max(book) if side == Side.BID else min(book)) if book else None

    @staticmethod
    def _crossed(side: Side, price: int, opp_best: int) -> bool:
        return price >= opp_best if side == Side.BID else price <= opp_best

    def _book(self, side: Side) -> dict[int, list[RestingOrder]]:
        return self.bids if side == Side.BID else self.asks

    def _opp_book(self, side: Side) -> dict[int, list[RestingOrder]]:
        return self.asks if side == Side.BID else self.bids

    def _next_order_identity(self) -> tuple[int, str]:
        counter = self._order_counter + 1
        order_id = f"O{counter:08d}"
        while order_id in self.order_meta:
            counter += 1
            order_id = f"O{counter:08d}"
        return counter, order_id

    # ------------------------------------------------------------------ latency module
    def choose_latency(self, choice: LatencyChoice) -> None:
        reason = self._validate_latency_choice(choice)
        before = self._snapshot()
        if self._valid_clocks(choice.clocks):
            self.last_match_ts = choice.clocks.match_ts
        if reason is not None:
            self._record_and_seal(
                EventType.LATENCY_CHOICE_REJECTED,
                {
                    "event_id": choice.event_id,
                    "actor": choice.actor,
                    "round_id": choice.round_id,
                    "investment": choice.investment,
                    "reason": reason.value,
                    "clocks": vars(choice.clocks),
                },
                before,
            )
            return
        self.latency_choices[(choice.round_id, choice.actor)] = choice.investment
        delay = self.prestate.latency_delay_by_investment[choice.investment]
        self._record_and_seal(
            EventType.LATENCY_CHOICE,
            {
                "event_id": choice.event_id,
                "actor": choice.actor,
                "round_id": choice.round_id,
                "investment": choice.investment,
                "resulting_delay_ticks": delay,
                "clocks": vars(choice.clocks),
            },
            before,
        )

    # ------------------------------------------------------------------ order requests
    def submit(self, request: OrderRequest) -> None:
        reason = self._validate_order(request)
        before_request = self._snapshot()
        if self._valid_clocks(request.clocks):
            self.last_match_ts = request.clocks.match_ts
        self._record_and_seal(
            EventType.ORDER_REQUEST,
            {
                "event_id": request.event_id,
                "actor": request.actor,
                "client_order_id": request.client_order_id,
                "round_id": request.round_id,
                "side": request.side.value,
                "price": request.price,
                "quantity": request.quantity,
                "clocks": vars(request.clocks),
            },
            before_request,
        )
        if reason is not None:
            self._record_and_seal(
                EventType.ORDER_REJECTED,
                {
                    "client_order_id": request.client_order_id,
                    "reason": reason.value,
                    "clocks": vars(request.clocks),
                },
            )
            return

        next_counter, order_id = self._next_order_identity()
        registered = False
        remaining = request.quantity
        opp_side = Side.ASK if request.side == Side.BID else Side.BID
        opp_best = self._best(opp_side)

        while remaining > 0 and opp_best is not None and self._crossed(
            request.side, request.price, opp_best
        ):
            before_execution = self._snapshot()
            maker_index, maker, allocation_draw = self._select_maker(opp_side, opp_best)
            maker_id, maker_actor, maker_qty = maker
            fill = (
                min(remaining, maker_qty)
                if self.prestate.allocation_rule == AllocationRule.FIFO
                else 1
            )
            remaining -= fill
            maker_remaining = maker_qty - fill
            next_exec_counter = self._exec_counter + 1
            execution = Execution(
                event_id=self.sequence + 1,
                execution_id=f"E{next_exec_counter:08d}",
                aggressor_order_id=order_id,
                maker_order_id=maker_id,
                maker_actor=maker_actor,
                aggressor_actor=request.actor,
                side_of_aggressor=request.side,
                price=opp_best,
                quantity=fill,
                maker_remaining=maker_remaining,
                clocks=request.clocks,
                round_id=request.round_id,
            )

            if not registered:
                self._register_order(
                    request=request,
                    order_id=order_id,
                    order_counter=next_counter,
                    status="active",
                )
                registered = True
            self._exec_counter = next_exec_counter
            self._apply_maker_fill(
                side=opp_side,
                price=opp_best,
                index=maker_index,
                maker=maker,
                fill=fill,
            )
            self._settle(
                aggressor_side=request.side,
                aggressor_actor=request.actor,
                maker_actor=maker_actor,
                price=opp_best,
                quantity=fill,
            )
            payload: dict[str, object] = {"execution": vars(execution)}
            if allocation_draw is not None:
                payload["allocation_draw"] = allocation_draw
            self._record_and_seal(EventType.EXECUTION, payload, before_execution)
            opp_best = self._best(opp_side)

        before_acceptance = self._snapshot()
        if not registered:
            self._register_order(
                request=request,
                order_id=order_id,
                order_counter=next_counter,
                status="active",
            )
        if remaining > 0:
            self._book(request.side).setdefault(request.price, []).append(
                (order_id, request.actor, remaining)
            )
            self.order_status[order_id] = "resting"
        else:
            self.order_status[order_id] = "filled"
        self._record_and_seal(
            EventType.ORDER_ACCEPTED,
            {
                "client_order_id": request.client_order_id,
                "order_id": order_id,
                "resting_quantity": remaining,
                "clocks": vars(request.clocks),
            },
            before_acceptance,
        )

    def cancel(self, request: CancelRequest) -> None:
        clock_valid = self._valid_clocks(request.clocks)
        before_request = self._snapshot()
        if clock_valid:
            self.last_match_ts = request.clocks.match_ts
        self._record_and_seal(
            EventType.CANCEL_REQUEST,
            {
                "event_id": request.event_id,
                "actor": request.actor,
                "order_id": request.order_id,
                "round_id": request.round_id,
                "clocks": vars(request.clocks),
            },
            before_request,
        )
        reason = self._cancel_rejection_reason(request, clock_valid)
        if reason is not None:
            self._record_and_seal(
                EventType.CANCEL_REJECTED,
                {
                    "order_id": request.order_id,
                    "reason": reason.value,
                    "clocks": vars(request.clocks),
                },
            )
            return

        actor, side, price = self.order_meta[request.order_id]
        book = self._book(side)
        queue = book[price]
        index = next(i for i, row in enumerate(queue) if row[0] == request.order_id)
        target = queue[index]
        before_cancel = self._snapshot()
        queue.pop(index)
        if not queue:
            del book[price]
        self.order_status[request.order_id] = "cancelled"
        self._record_and_seal(
            EventType.ORDER_CANCELLED,
            {
                "order_id": request.order_id,
                "actor": actor,
                "cancelled_quantity": target[2],
                "clocks": vars(request.clocks),
            },
            before_cancel,
        )

    def finish(self) -> None:
        self._record_and_seal(EventType.SESSION_END, {})

    # ------------------------------------------------------------------ matching internals
    def _select_maker(
        self, side: Side, price: int
    ) -> tuple[int, RestingOrder, dict[str, object] | None]:
        queue = self._book(side)[price]
        if self.prestate.allocation_rule == AllocationRule.FIFO:
            return 0, queue[0], None

        eligible_units = sum(quantity for _, _, quantity in queue)
        selected_unit = self.rng.randrange(eligible_units)
        cumulative = 0
        for index, maker in enumerate(queue):
            cumulative += maker[2]
            if selected_unit < cumulative:
                return index, maker, {
                    "price": price,
                    "eligible_units": eligible_units,
                    "selected_unit": selected_unit,
                    "maker_order_id": maker[0],
                }
        raise AssertionError("random-unit draw exceeded the resting quantity")

    def _apply_maker_fill(
        self,
        *,
        side: Side,
        price: int,
        index: int,
        maker: RestingOrder,
        fill: int,
    ) -> None:
        book = self._book(side)
        queue = book[price]
        maker_id, maker_actor, maker_qty = maker
        maker_remaining = maker_qty - fill
        if maker_remaining > 0:
            queue[index] = (maker_id, maker_actor, maker_remaining)
        else:
            queue.pop(index)
            self.order_status[maker_id] = "filled"
        if not queue:
            del book[price]

    def _settle(
        self,
        *,
        aggressor_side: Side,
        aggressor_actor: str,
        maker_actor: str,
        price: int,
        quantity: int,
    ) -> None:
        if aggressor_side == Side.BID:
            buyer, seller = aggressor_actor, maker_actor
        else:
            buyer, seller = maker_actor, aggressor_actor
        notional = price * quantity
        self.cash[buyer] -= notional
        self.cash[seller] += notional
        self.inventory[buyer] += quantity
        self.inventory[seller] -= quantity
        for _ in range(quantity):
            buy_index = self.units_bought[buyer]
            sell_index = self.units_sold[seller]
            buy_schedule = self.prestate.induced_buy_values.get(buyer)
            sell_schedule = self.prestate.induced_sell_costs.get(seller)
            value = buy_schedule[buy_index] if buy_schedule is not None else price
            cost = sell_schedule[sell_index] if sell_schedule is not None else price
            self.realized_induced_surplus[buyer] += value - price
            self.realized_induced_surplus[seller] += price - cost
            self.units_bought[buyer] += 1
            self.units_sold[seller] += 1

    def _register_order(
        self,
        *,
        request: OrderRequest,
        order_id: str,
        order_counter: int,
        status: str,
    ) -> None:
        self.used_client_ids.add(request.client_order_id)
        self._order_counter = order_counter
        self.order_meta[order_id] = (request.actor, request.side, request.price)
        self.order_status[order_id] = status

    # ------------------------------------------------------------------ validation
    def _validate_order(self, request: OrderRequest) -> RejectionReason | None:
        if request.actor not in self.prestate.actors:
            return RejectionReason.UNKNOWN_ACTOR
        if request.quantity <= 0:
            return RejectionReason.NEGATIVE_OR_ZERO_QUANTITY
        lo, hi = self.prestate.price_bands
        if not (lo <= request.price <= hi):
            return RejectionReason.PRICE_OUT_OF_BANDS
        if not self._valid_clocks(request.clocks):
            return RejectionReason.INVALID_CLOCKS
        if request.client_order_id in self.used_client_ids:
            return RejectionReason.DUPLICATE_CLIENT_ID
        if request.side == Side.BID:
            available_cash = self.cash[request.actor] - self._reserved_cash(request.actor)
            if request.price * request.quantity > available_cash:
                return RejectionReason.INSUFFICIENT_CASH
            buy_schedule = self.prestate.induced_buy_values.get(request.actor)
            if buy_schedule is not None:
                available_units = (
                    len(buy_schedule)
                    - self.units_bought[request.actor]
                    - self._reserved_bid_units(request.actor)
                )
                if request.quantity > available_units:
                    return RejectionReason.INDUCED_BUY_CAPACITY_EXCEEDED
        else:
            available_inventory = (
                self.inventory[request.actor] - self._reserved_inventory(request.actor)
            )
            if request.quantity > available_inventory:
                return RejectionReason.INSUFFICIENT_INVENTORY
            sell_schedule = self.prestate.induced_sell_costs.get(request.actor)
            if sell_schedule is not None:
                available_units = (
                    len(sell_schedule)
                    - self.units_sold[request.actor]
                    - self._reserved_inventory(request.actor)
                )
                if request.quantity > available_units:
                    return RejectionReason.INDUCED_SELL_CAPACITY_EXCEEDED
        if self._would_self_trade(request):
            return RejectionReason.SELF_TRADE_PREVENTED
        return None

    def _would_self_trade(self, request: OrderRequest) -> bool:
        for price, orders in self._opp_book(request.side).items():
            if self._crossed(request.side, request.price, price) and any(
                actor == request.actor for _, actor, _ in orders
            ):
                return True
        return False

    def _cancel_rejection_reason(
        self, request: CancelRequest, clock_valid: bool
    ) -> CancelRejectionReason | None:
        if not clock_valid:
            return CancelRejectionReason.INVALID_CLOCKS
        meta = self.order_meta.get(request.order_id)
        if meta is None:
            return CancelRejectionReason.UNKNOWN_ORDER
        if meta[0] != request.actor:
            return CancelRejectionReason.NOT_OWNER
        status = self.order_status[request.order_id]
        if status == "filled":
            return CancelRejectionReason.ALREADY_FILLED
        if status == "cancelled":
            return CancelRejectionReason.ALREADY_CANCELLED
        if status != "resting":
            return CancelRejectionReason.CANCEL_TOO_LATE
        return None

    def _validate_latency_choice(
        self, choice: LatencyChoice
    ) -> LatencyChoiceRejectionReason | None:
        if choice.actor not in self.prestate.actors:
            return LatencyChoiceRejectionReason.UNKNOWN_ACTOR
        if not self._valid_clocks(choice.clocks):
            return LatencyChoiceRejectionReason.INVALID_CLOCKS
        if (choice.round_id, choice.actor) in self.latency_choices:
            return LatencyChoiceRejectionReason.DUPLICATE_CHOICE
        if not 0 <= choice.investment < len(self.prestate.latency_delay_by_investment):
            return LatencyChoiceRejectionReason.INVALID_INVESTMENT
        if choice.investment > self.prestate.latency_endowment:
            return LatencyChoiceRejectionReason.INVALID_INVESTMENT
        return None

    def _valid_clocks(self, clocks: ThreeClocks) -> bool:
        client_ts = clocks.client_ts
        receipt_ts = clocks.receipt_ts
        match_ts = clocks.match_ts
        return (
            isinstance(client_ts, int)
            and isinstance(receipt_ts, int)
            and isinstance(match_ts, int)
            and 0 <= client_ts <= receipt_ts <= match_ts
            and match_ts >= self.last_match_ts
        )

    def _reserved_cash(self, actor: str) -> int:
        return sum(
            price * quantity
            for price, orders in self.bids.items()
            for _, owner, quantity in orders
            if owner == actor
        )

    def _reserved_inventory(self, actor: str) -> int:
        return sum(
            quantity
            for orders in self.asks.values()
            for _, owner, quantity in orders
            if owner == actor
        )

    def _reserved_bid_units(self, actor: str) -> int:
        return sum(
            quantity
            for orders in self.bids.values()
            for _, owner, quantity in orders
            if owner == actor
        )

    # ------------------------------------------------------------------ prestate
    @staticmethod
    def _validate_prestate(prestate: SessionPrestate) -> None:
        if not prestate.session_id or len(set(prestate.actors)) != len(prestate.actors):
            raise ValueError("session_id and unique actors are required")
        actors = set(prestate.actors)
        if set(prestate.initial_cash) != actors or set(prestate.initial_inventory) != actors:
            raise ValueError("cash and inventory maps must exactly match actors")
        if any(value < 0 for value in prestate.initial_cash.values()) or any(
            value < 0 for value in prestate.initial_inventory.values()
        ):
            raise ValueError("initial cash and inventory must be nonnegative")
        lo, hi = prestate.price_bands
        if lo > hi:
            raise ValueError("invalid price bands")
        if not set(prestate.induced_buy_values).issubset(actors) or not set(
            prestate.induced_sell_costs
        ).issubset(actors):
            raise ValueError("induced-value maps contain an unknown actor")
        if any(
            later.tick < earlier.tick
            for earlier, later in zip(
                prestate.information_schedule,
                prestate.information_schedule[1:],
                strict=False,
            )
        ):
            raise ValueError("information releases must be ordered by tick")
        delays = prestate.latency_delay_by_investment
        if prestate.latency_endowment < 0 or (
            delays and prestate.latency_endowment >= len(delays)
        ):
            raise ValueError("latency endowment must index the frozen delay schedule")
        if any(delay < 0 for delay in delays) or any(
            later > earlier for earlier, later in pairwise(delays)
        ):
            raise ValueError("larger latency investment cannot produce a longer delay")

        seen: set[str] = set()
        bid_liability = {actor: 0 for actor in actors}
        ask_quantity = {actor: 0 for actor in actors}
        best_bid: int | None = None
        best_ask: int | None = None
        for order in prestate.initial_book:
            if order.order_id in seen or order.actor not in actors or order.quantity <= 0:
                raise ValueError("invalid initial order")
            if not lo <= order.price <= hi:
                raise ValueError("initial order outside price bands")
            seen.add(order.order_id)
            if order.side == Side.BID:
                bid_liability[order.actor] += order.price * order.quantity
                best_bid = order.price if best_bid is None else max(best_bid, order.price)
            else:
                ask_quantity[order.actor] += order.quantity
                best_ask = order.price if best_ask is None else min(best_ask, order.price)
        if best_bid is not None and best_ask is not None and best_bid >= best_ask:
            raise ValueError("initial book must not be crossed")
        if any(bid_liability[a] > prestate.initial_cash[a] for a in actors):
            raise ValueError("initial bids exceed available cash")
        if any(ask_quantity[a] > prestate.initial_inventory[a] for a in actors):
            raise ValueError("initial asks exceed available inventory")
        if any(
            actor in prestate.induced_buy_values
            and sum(
                order.quantity
                for order in prestate.initial_book
                if order.actor == actor and order.side == Side.BID
            )
            > len(prestate.induced_buy_values[actor])
            for actor in actors
        ):
            raise ValueError("initial bids exceed induced buy capacity")
        if any(
            actor in prestate.induced_sell_costs
            and ask_quantity[actor] > len(prestate.induced_sell_costs[actor])
            for actor in actors
        ):
            raise ValueError("initial asks exceed induced sell capacity")

    def _load_initial_book(self) -> None:
        for order in self.prestate.initial_book:
            self._book(order.side).setdefault(order.price, []).append(
                (order.order_id, order.actor, order.quantity)
            )
            self.order_meta[order.order_id] = (order.actor, order.side, order.price)
            self.order_status[order.order_id] = "resting"
        self._order_counter = len(self.prestate.initial_book)
