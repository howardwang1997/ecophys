"""Outcome-free analytic fixture for the treatment-native costly-speed module."""

from __future__ import annotations

from lab_asset.schema import AllocationRule


def expected_race_payoff(
    *,
    rule: AllocationRule,
    investment: int,
    other_investments: tuple[int, ...],
    delay_by_investment: tuple[int, ...],
    execution_prize: int,
    cost_per_unit: int,
) -> float:
    """Expected payoff when all same-price unit orders rest before one execution.

    FIFO pays the earliest arrival, splitting a deterministic tie equally. Random-unit
    allocation gives every resting unit the same chance, independent of arrival time.
    """

    all_investments = (investment, *other_investments)
    if any(not 0 <= effort < len(delay_by_investment) for effort in all_investments):
        raise ValueError("investment does not index the delay schedule")
    cost = cost_per_unit * investment
    if rule == AllocationRule.RANDOM_UNIT_WITHIN_PRICE:
        return execution_prize / len(all_investments) - cost

    own_delay = delay_by_investment[investment]
    delays = tuple(delay_by_investment[effort] for effort in all_investments)
    fastest = min(delays)
    if own_delay != fastest:
        return -float(cost)
    tied_fastest = sum(delay == fastest for delay in delays)
    return execution_prize / tied_fastest - cost


def race_best_response(
    *,
    rule: AllocationRule,
    other_investments: tuple[int, ...],
    delay_by_investment: tuple[int, ...],
    execution_prize: int,
    cost_per_unit: int,
) -> int:
    """Lowest investment attaining the maximum expected payoff."""

    payoffs = [
        expected_race_payoff(
            rule=rule,
            investment=investment,
            other_investments=other_investments,
            delay_by_investment=delay_by_investment,
            execution_prize=execution_prize,
            cost_per_unit=cost_per_unit,
        )
        for investment in range(len(delay_by_investment))
    ]
    return max(range(len(payoffs)), key=lambda investment: (payoffs[investment], -investment))
