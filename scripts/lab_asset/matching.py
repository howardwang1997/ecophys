"""Reference continuous-double-auction engine with two within-tie allocation arms (D-2.2).

Deterministic given (request tape, arm, seed). The event grammar is arm-invariant: on the
same request tape both arms emit identical record types, quantities, prices and timings;
only maker allocation identities (and the semantic draw record for the random arm) differ.
The tape is self-contained: every request record precedes its response records, so the
deterministic replay validator can re-execute the tape alone.
"""

from __future__ import annotations

import random

from lab_asset.schema import (
    AllocationRule,
    CancelRejectionReason,
    CancelRequest,
    EventType,
    Execution,
    OrderRequest,
    RejectionReason,
    SessionPrestate,
    Side,
    TapeRecord,
    aggregate_state_hash,
    state_hash,
)

RestingOrder = tuple[str, str, int]  # (order_id, actor, quantity) in arrival order


class ReferenceEngine:
    def __init__(self, prestate: SessionPrestate) -> None:
        self.prestate = prestate
        self.rng = random.Random(prestate.seed)
        self.sequence = 0
        self.bids: dict[int, list[RestingOrder]] = {}
        self.asks: dict[int, list[RestingOrder]] = {}
        self.order_meta: dict[str, tuple[str, Side, int]] = {}
        self.used_client_ids: set[str] = set()
        self.tape: list[TapeRecord] = []
        self._order_counter = 0
        self._exec_counter = 0
        self._last_draw: tuple[int, int, str] | None = None
        self._record_and_seal(EventType.SESSION_START, {})

    # ------------------------------------------------------------------ helpers
    def _hash(self) -> str:
        return state_hash(self.bids, self.asks, self.sequence)

    def _aggregate_hash(self) -> str:
        return aggregate_state_hash(self.bids, self.asks, self.sequence)

    def _record_and_seal(self, event_type: EventType, payload: dict[str, object]) -> TapeRecord:
        pre = self._hash()
        self.sequence += 1
        record = TapeRecord(
            sequence=self.sequence,
            event_type=event_type,
            payload=payload,
            pre_state_hash=pre,
            post_state_hash="",
            post_aggregate_state_hash="",
        )
        self.tape.append(record)
        object.__setattr__(record, "post_state_hash", self._hash())
        object.__setattr__(record, "post_aggregate_state_hash", self._aggregate_hash())
        return record

    def _best(self, side: Side) -> int | None:
        book = self.bids if side == Side.BID else self.asks
        return (max(book) if side == Side.BID else min(book)) if book else None

    def _crossed(self, side: Side, price: int, opp_best: int) -> bool:
        return price >= opp_best if side == Side.BID else price <= opp_best

    def _opp_book(self, side: Side) -> dict[int, list[RestingOrder]]:
        return self.asks if side == Side.BID else self.bids

    # ------------------------------------------------------------------ requests
    def submit(self, request: OrderRequest) -> None:
        self._record_and_seal(
            EventType.ORDER_REQUEST,
            {
                "event_id": request.event_id,
                "actor": request.actor,
                "client_order_id": request.client_order_id,
                "side": request.side.value,
                "price": request.price,
                "quantity": request.quantity,
                "clocks": vars(request.clocks),
            },
        )
        reason = self._validate(request)
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
        self.used_client_ids.add(request.client_order_id)
        self._order_counter += 1
        order_id = f"O{self._order_counter:08d}"
        self.order_meta[order_id] = (request.actor, request.side, request.price)
        remaining = request.quantity
        opp = Side.ASK if request.side == Side.BID else Side.BID
        opp_best = self._best(opp)
        while remaining > 0 and opp_best is not None and self._crossed(
            request.side, request.price, opp_best
        ):
            maker_id, maker_actor, maker_qty = self._pop_maker(opp, opp_best)
            fill = min(remaining, maker_qty)
            remaining -= fill
            self._exec_counter += 1
            execution = Execution(
                event_id=self.sequence + 1,
                execution_id=f"E{self._exec_counter:08d}",
                aggressor_order_id=order_id,
                maker_order_id=maker_id,
                maker_actor=maker_actor,
                aggressor_actor=request.actor,
                side_of_aggressor=request.side,
                price=opp_best,
                quantity=fill,
                maker_remaining=maker_qty - fill,
                clocks=request.clocks,
            )
            payload: dict[str, object] = {"execution": vars(execution)}
            if (
                self._last_draw is not None
                and self.prestate.allocation_rule == AllocationRule.RANDOM_WITHIN_TIE
            ):
                price_draw, index_draw, maker_draw = self._last_draw
                payload["allocation_draw"] = {
                    "price": price_draw,
                    "index": index_draw,
                    "maker_order_id": maker_draw,
                }
                self._last_draw = None
            if execution.maker_remaining > 0:
                self._opp_book(request.side).setdefault(opp_best, []).append(
                    (maker_id, maker_actor, execution.maker_remaining)
                )
            self._record_and_seal(EventType.EXECUTION, payload)
            opp_best = self._best(opp)
        if remaining > 0:
            book = self.bids if request.side == Side.BID else self.asks
            book.setdefault(request.price, []).append((order_id, request.actor, remaining))
        self._record_and_seal(
            EventType.ORDER_ACCEPTED,
            {
                "client_order_id": request.client_order_id,
                "order_id": order_id,
                "resting_quantity": remaining,
                "clocks": vars(request.clocks),
            },
        )

    def cancel(self, request: CancelRequest) -> None:
        self._record_and_seal(
            EventType.CANCEL_REQUEST,
            {
                "event_id": request.event_id,
                "actor": request.actor,
                "client_order_id": request.client_order_id,
                "clocks": vars(request.clocks),
            },
        )
        target_book: dict[int, list[RestingOrder]] | None = None
        target_price: int | None = None
        target: RestingOrder | None = None
        for book in (self.bids, self.asks):
            for price, orders in book.items():
                for candidate in orders:
                    if candidate[0] == request.client_order_id and candidate[1] == request.actor:
                        target_book, target_price, target = book, price, candidate
                        break
                if target is not None:
                    break
            if target is not None:
                break
        if target_book is None or target_price is None or target is None:
            reason = (
                CancelRejectionReason.ALREADY_FILLED
                if request.client_order_id in self.order_meta
                and self._order_is_fully_filled(request.client_order_id)
                else CancelRejectionReason.UNKNOWN_ORDER
            )
            self._record_and_seal(
                EventType.CANCEL_REJECTED,
                {
                    "client_order_id": request.client_order_id,
                    "reason": reason.value,
                    "clocks": vars(request.clocks),
                },
            )
            return
        target_book[target_price].remove(target)
        if not target_book[target_price]:
            del target_book[target_price]
        self._record_and_seal(
            EventType.ORDER_CANCELLED,
            {
                "order_id": target[0],
                "cancelled_quantity": target[2],
                "clocks": vars(request.clocks),
            },
        )

    def finish(self) -> None:
        self._record_and_seal(EventType.SESSION_END, {})

    # ------------------------------------------------------------------ internals
    def _order_is_fully_filled(self, order_id: str) -> bool:
        for book in (self.bids, self.asks):
            for orders in book.values():
                if any(oid == order_id for oid, _, _ in orders):
                    return False
        return True

    def _validate(self, request: OrderRequest) -> RejectionReason | None:
        if request.quantity <= 0:
            return RejectionReason.NEGATIVE_OR_ZERO_QUANTITY
        lo, hi = self.prestate.price_bands
        if not (lo <= request.price <= hi):
            return RejectionReason.PRICE_OUT_OF_BANDS
        if request.client_order_id in self.used_client_ids:
            return RejectionReason.DUPLICATE_CLIENT_ID
        opp_best = self._best(Side.ASK if request.side == Side.BID else Side.BID)
        if opp_best is not None and self._crossed(request.side, request.price, opp_best):
            makers = self._opp_book(request.side).get(opp_best, [])
            if makers and all(actor == request.actor for _, actor, _ in makers):
                return RejectionReason.SELF_TRADE_PREVENTED
        return None

    def _pop_maker(self, side: Side, price: int) -> RestingOrder:
        """Allocation arm: FIFO pops arrival order; random pops a uniform tie-set member.

        The random draw is a semantic event recorded with its execution so third parties
        can replay the tape exactly.
        """
        book = self.bids if side == Side.BID else self.asks
        queue = book[price]
        if self.prestate.allocation_rule == AllocationRule.FIFO:
            maker = queue.pop(0)
            self._last_draw = None
        else:
            index = self.rng.randrange(len(queue))
            maker = queue.pop(index)
            self._last_draw = (price, index, maker[0])
        if not queue:
            del book[price]
        return maker
