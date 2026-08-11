from __future__ import annotations

import pytest

from ecomd.market_world import Account, ExchangeRules, LimitOrderBook


def _book(*, maker_fee_bps: float = 0.0, taker_fee_bps: float = 0.0) -> LimitOrderBook:
    accounts = {
        0: Account(cash=100_000.0, inventory=100),
        1: Account(cash=100_000.0, inventory=100),
        2: Account(cash=100_000.0, inventory=100),
    }
    return LimitOrderBook(
        ExchangeRules(
            tick_size=1,
            maker_fee_bps=maker_fee_bps,
            taker_fee_bps=taker_fee_bps,
        ),
        accounts,
    )


def test_price_time_priority_and_partial_fill() -> None:
    book = _book()
    book.submit_limit(10, 0, "sell", 101, 5)
    book.submit_limit(11, 1, "sell", 101, 7)

    fills = book.submit_market(2, "buy", 8)

    assert [(fill.maker_order_id, fill.quantity) for fill in fills] == [(10, 5), (11, 3)]
    assert book.order(11).remaining == 4
    assert book.snapshot().ask_top_depth == 4
    assert book.invariant_violations() == ()


def test_settlement_conserves_cash_and_inventory_with_fees() -> None:
    book = _book(maker_fee_bps=-1.0, taker_fee_bps=3.0)
    initial_cash = sum(account.cash for account in book.accounts.values())
    initial_inventory = sum(account.inventory for account in book.accounts.values())
    book.submit_limit(1, 0, "sell", 100, 10)

    fills = book.submit_market(1, "buy", 10)

    assert len(fills) == 1
    assert book.accounts[0].cash == pytest.approx(101_000.1)
    assert book.accounts[1].cash == pytest.approx(98_999.7)
    assert book.exchange_cash == pytest.approx(0.2)
    assert sum(account.cash for account in book.accounts.values()) + book.exchange_cash == pytest.approx(
        initial_cash
    )
    assert sum(account.inventory for account in book.accounts.values()) == initial_inventory
    assert book.invariant_violations() == ()


def test_rejects_unfunded_and_unauthorized_orders() -> None:
    book = _book()
    book.accounts[0].cash = 5.0
    book.accounts[1].inventory = 0

    with pytest.raises(ValueError, match="cash"):
        book.submit_limit(1, 0, "buy", 100, 1)
    with pytest.raises(ValueError, match="inventory"):
        book.submit_limit(2, 1, "sell", 100, 1)

    book.submit_limit(3, 2, "buy", 99, 1)
    with pytest.raises(ValueError, match="owner"):
        book.cancel(3, 0)


def test_tick_change_cancels_only_nonconforming_orders() -> None:
    book = _book()
    book.submit_limit(1, 0, "buy", 99, 2)
    book.submit_limit(2, 1, "buy", 98, 2)
    book.submit_limit(3, 2, "sell", 101, 2)
    book.submit_limit(4, 0, "sell", 102, 2)

    cancelled = book.change_rules(ExchangeRules(tick_size=2))

    assert cancelled == (1, 3)
    assert book.active_order_ids == (2, 4)
    assert book.invariant_violations() == ()
