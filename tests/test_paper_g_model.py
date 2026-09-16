from functools import lru_cache
from itertools import product

import numpy as np
import pytest

from ecomd.paper_g.learning import Belief
from ecomd.paper_g.model import ACTIONS, Action, Feedback, Law, Market, State, TabularModel


def events(law: Law, rho: float):
    for buy, favorable, rb, ra in product((False, True), repeat=4):
        p = law.buy_probability if buy else 1-law.buy_probability
        theta = law.buyer_high_probability if buy else law.seller_low_probability
        p *= theta if favorable else 1-theta
        p *= (rho if rb else 1-rho)*(rho if ra else 1-rho)
        value = (102 if favorable else 101) if buy else (98 if favorable else 99)
        yield buy, value, rb, ra, p


@pytest.mark.parametrize("rho", [0.0, 0.1, 1.0])
def test_independent_event_distribution_matches_analytic_kernel(rho):
    law = Law(0.8, 0.75, 0.25)
    model = TabularModel(2, rho)
    p, rewards = model.kernel(law)
    for i, state in enumerate(model.states):
        for j, action in enumerate(ACTIONS):
            if not model.legal[i, j]:
                market = Market(2, 4, state.inventory)
                market.state = state
                with pytest.raises(ValueError):
                    market.step(action, True, 102, False, False, False)
                continue
            expected_p = np.zeros(len(model.states))
            expected_r = 0.0
            for buy, value, rb, ra, weight in events(law, rho):
                market = Market(2, 4, state.inventory)
                market.state = state
                result = market.step(action, buy, value, rb, ra, False)
                expected_p[model.index[result.state]] += weight
                expected_r += weight*result.reward
                assert result.reward == market.wealth()
                assert -1 <= result.reward <= 2
                assert result.feedback.willingness is None
            np.testing.assert_allclose(p[i, j], expected_p, atol=1e-14, rtol=0)
            assert abs(expected_r-rewards[i, j]) < 1e-14
            assert abs(p[i, j].sum()-1) < 1e-14


def test_oracle_against_short_policy_tree_and_manual_one_round():
    law, rho = Law(0.5, 0.55, 0.55), 0.1
    model = TabularModel(2, rho)
    values, _ = model.solve(law, 3)

    @lru_cache(None)
    def tree(state, remaining):
        if not remaining:
            return 0.0
        candidates = []
        for action in ACTIONS:
            gain = 0.0
            legal = True
            for buy, value, rb, ra, weight in events(law, rho):
                market = Market(2, 8, state.inventory)
                market.state = state
                try:
                    result = market.step(action, buy, value, rb, ra, False)
                except ValueError:
                    legal = False
                    break
                gain += weight*(result.reward + tree(result.state, remaining-1))
            if legal:
                candidates.append(gain)
        return max(candidates)

    assert values[1, model.index[State(1, 1, 1)]] == pytest.approx(1.1)
    for i, state in enumerate(model.states):
        assert values[3, i] == pytest.approx(tree(state, 3), abs=1e-10)


def test_hedge_has_real_cost_and_quotes_use_post_hedge_inventory():
    market = Market(2, 4, 0)
    result = market.step(Action(1, 0, 102), True, 102, False, False, False)
    assert result.reward == 1
    assert result.state == State(0, 1, 0)
    with pytest.raises(ValueError, match="unavailable buy"):
        market.step(Action(1, 0, 102), True, 102, False, False, False)


def test_narrow_fill_does_not_reveal_willingness():
    belief = Belief()
    belief.update(Action(0, 99, 101), Feedback(True, True, None))
    np.testing.assert_array_equal(belief.counts, [[2, 1], [1, 1], [1, 1]])
    belief.update(Action(0, 99, 102), Feedback(True, False, None))
    np.testing.assert_array_equal(belief.counts[1], [1, 2])
    belief.update(Action(0, 0, 0), Feedback(False, False, None))
    np.testing.assert_array_equal(belief.counts[2], [1, 1])
    belief.update(Action(0, 0, 0), Feedback(False, False, 98))
    np.testing.assert_array_equal(belief.counts[2], [2, 1])


def test_hidden_types_produce_identical_actual_feed_when_narrow_quotes_fill():
    feeds = []
    for willingness in (101, 102):
        market = Market(2, 4)
        feeds.append(market.step(Action(0, 99, 101), True, willingness, True, True, False).feedback)
    assert feeds[0] == feeds[1]


def test_no_inventory_resets_in_repeated_rounds():
    market = Market(2, 4)
    market.step(Action(0, 0, 102), True, 102, True, True, False)
    assert market.state.inventory == 0
    with pytest.raises(ValueError, match="quote exceeds"):
        market.step(Action(0, 0, 102), True, 102, True, True, False)


def test_reveal_does_not_change_physical_transition_or_reward():
    a = Action(0, 98, 102)
    left = Market(2, 2).step(a, False, 99, True, False, False)
    right = Market(2, 2).step(a, False, 99, True, False, True)
    assert left.state == right.state and left.reward == right.reward
    assert left.feedback.willingness is None and right.feedback.willingness == 99
