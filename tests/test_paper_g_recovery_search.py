from fractions import Fraction

import pytest

from ecomd.paper_g.recovery_search import bayesian_value, minimax_regret, sequence_values


@pytest.mark.parametrize("horizon", [0, 1, 2, 17, 256])
def test_no_recovery_creates_no_comparator_advantage(horizon):
    assert minimax_regret(horizon, 0, .5) == 0
    assert bayesian_value(horizon, 0, .5) == 0


@pytest.mark.parametrize("horizon", [1, 5, 31])
def test_identical_worlds_match_direct_first_success_value(horizon):
    probability, reward = .2, 3
    direct_value = sum((1-probability)**n*probability*(horizon-n-1)*reward for n in range(horizon-1))
    assert bayesian_value(horizon, probability, 0, reward) == pytest.approx(direct_value)
    assert minimax_regret(horizon, probability, 0, reward) == 0


def test_end_of_round_timing_and_single_decision_risk():
    assert minimax_regret(1, .2, .5, 3) == pytest.approx(0)
    assert bayesian_value(1, .2, .5, 3) == pytest.approx(0)
    assert minimax_regret(2, .2, .5, 3) == pytest.approx(.3)
    assert bayesian_value(2, .2, .5, 3) == pytest.approx(.6)


def test_first_success_rewards_for_fixed_and_alternating_choices():
    high, low = Fraction(3, 10), Fraction(1, 10)
    assert sequence_values((0, 0), high, low) == (Fraction(81, 100), Fraction(29, 100))
    assert sequence_values((0, 1), high, low) == (Fraction(67, 100), Fraction(47, 100))


@pytest.mark.parametrize("restore,separation", [(-.1, .5), (.5, 1), (.9, .5), (float("nan"), .5)])
def test_invalid_restoration_contract_is_rejected(restore, separation):
    with pytest.raises(ValueError):
        minimax_regret(8, restore, separation)
