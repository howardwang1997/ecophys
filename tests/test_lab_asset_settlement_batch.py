"""Settlement batching preserves complete engine state and event bytes."""
from __future__ import annotations

from dataclasses import replace

from tests.test_lab_asset_conformance import buy, make_prestate, sell
from lab_asset.matching import ReferenceEngine
from lab_asset.schema import AllocationRule, Side, record_to_json


class UnitSettlementEngine(ReferenceEngine):
    def _settle(self, *, aggressor_side: Side, aggressor_actor: str,
                maker_actor: str, price: int, quantity: int) -> None:
        buyer, seller = ((aggressor_actor, maker_actor) if aggressor_side == Side.BID
                         else (maker_actor, aggressor_actor))
        self.cash[buyer] -= price * quantity
        self.cash[seller] += price * quantity
        self.inventory[buyer] += quantity
        self.inventory[seller] -= quantity
        for _ in range(quantity):
            buy_schedule = self.prestate.induced_buy_values.get(buyer)
            sell_schedule = self.prestate.induced_sell_costs.get(seller)
            value = buy_schedule[self.units_bought[buyer]] if buy_schedule is not None else price
            cost = sell_schedule[self.units_sold[seller]] if sell_schedule is not None else price
            self.realized_induced_surplus[buyer] += value - price
            self.realized_induced_surplus[seller] += price - cost
            self.units_bought[buyer] += 1
            self.units_sold[seller] += 1


def test_batched_settlement_matches_unit_reference() -> None:
    for rule in (AllocationRule.FIFO, AllocationRule.RANDOM_UNIT_WITHIN_PRICE):
        for take, rest in ((buy, sell), (sell, buy)):
            for buy_values, sell_costs in ((False, False), (True, False), (False, True), (True, True)):
                original = make_prestate(rule)
                prestate = replace(
                    original,
                    induced_buy_values=original.induced_buy_values if buy_values else {},
                    induced_sell_costs=original.induced_sell_costs if sell_costs else {},
                )
                expected, actual = UnitSettlementEngine(prestate), ReferenceEngine(prestate)
                for engine in (expected, actual):
                    engine.submit(rest("a", "maker-a", 100, 30, 1))
                    engine.submit(rest("c", "maker-c", 100, 30, 2))
                    engine.submit(take("b", "take-one", 100, 17, 3))
                    engine.submit(take("b", "take-two", 100, 25, 4))
                    engine.finish()
                assert [record_to_json(r) for r in actual.tape] == [record_to_json(r) for r in expected.tape]
                for field in ("cash", "inventory", "units_bought", "units_sold", "realized_induced_surplus"):
                    assert getattr(actual, field) == getattr(expected, field)
                assert actual.rng.getstate() == expected.rng.getstate()
                assert actual.identity_state_digest() == expected.identity_state_digest()
                assert actual.aggregate_state_digest() == expected.aggregate_state_digest()
