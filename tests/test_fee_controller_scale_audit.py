from __future__ import annotations

import pytest

from ecomd.research.fee_controller_scale_audit import (
    DECLARED_SCHEDULES,
    build_scale_audit,
    continuous_schedule_metrics,
    exact_grid_audit,
    standardized_fee,
)


def test_declared_schedule_continuous_metrics_match_audit() -> None:
    metrics = [continuous_schedule_metrics(schedule) for schedule in DECLARED_SCHEDULES]
    assert [metric["maximum_over_target"] for metric in metrics] == [1.5, 1.5, 1.5]
    assert [metric["update_fraction_over_target"] for metric in metrics] == pytest.approx(
        [834_619.3333333334, 834_619.3, 834_619.3571428572]
    )
    assert [metric["full_block_log_step"] for metric in metrics] == pytest.approx(
        [0.07852202481133172, 0.07852202794741458, 0.07852202257132123]
    )
    assert [metric["full_block_relative_change"] for metric in metrics] == pytest.approx(
        [0.08168717885593169, 0.08168718224814753, 0.08168717643292034]
    )


def test_exact_standardized_grids_match_nontriviality_audit() -> None:
    audit = exact_grid_audit()
    assert audit["quarter_grid"] == {
        "minimum": 0.0,
        "maximum": 64.0,
        "step": 0.25,
        "all_exact_fees_equal": True,
    }
    integer = audit["integer_grid"]
    assert isinstance(integer, dict)
    assert integer["first_difference_state"] == 74
    assert integer["first_difference_values"] == [111_442, 111_442, 111_441]
    assert integer["maximum_relative_spread"] == pytest.approx(2.150405339682748e-05)
    assert integer["maximum_spread_state"] == 2_000


def test_standardized_fee_rejects_fractional_excess_and_audit_is_outcome_free() -> None:
    assert standardized_fee(DECLARED_SCHEDULES[0], 0) == 1
    with pytest.raises(ValueError, match="integer excess"):
        standardized_fee(DECLARED_SCHEDULES[0], 1, 7)
    payload = build_scale_audit()
    assert payload["schema_version"] == "ecophys-fee-controller-scale-audit/v1"
    assert payload["scope"] == "protocol constants only; no chain outcomes"
