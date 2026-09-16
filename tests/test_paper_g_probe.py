from itertools import product

import pytest

from ecomd.paper_g.model import Law, Market, State
from ecomd.paper_g.resolve import expected_probe_cycle, probe_action


@pytest.mark.parametrize("capacity", [2, 8])
def test_probe_is_legal_without_any_external_depth(capacity):
    for q, buy, favorable in product(range(3), (False, True), (False, True)):
        market = Market(capacity, 4, q)
        market.state = State(q, 0, 0)
        value = (102 if favorable else 101) if buy else (98 if favorable else 99)
        action = probe_action(q)
        event = market.step(action, buy, value, False, False, False)
        assert action.hedge == 0 and event.state.bid_depth == event.state.ask_depth == 0
        assert 0 <= event.state.inventory <= 2
        if q == 1:
            inferred = (102 if event.feedback.filled else 101) if buy else (98 if event.feedback.filled else 99)
            assert inferred == value
        elif q == 0:
            assert event.state.inventory == (0 if buy else 1)
        else:
            assert event.state.inventory == (1 if buy else 2)


def test_cycle_formula_and_domain():
    assert expected_probe_cycle(Law(.5, .55, .55)) == pytest.approx(2.1)
    assert expected_probe_cycle(Law(.8, .75, .25)) == pytest.approx(4.0625)
    for p in [.1, .2, .5, .8, .9]:
        assert expected_probe_cycle(Law(p, 1, 1)) <= 1+1/min(p, 1-p)
    with pytest.raises(ValueError):
        expected_probe_cycle(Law(1, .5, .5))
    with pytest.raises(ValueError):
        probe_action(3)
