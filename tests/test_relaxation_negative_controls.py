import numpy as np
import pytest

from ecomd.research.relaxation_negative_controls import (
    dobrushin_coefficient,
    fixed_clock_chain_witness,
    hidden_slow_mode_witness,
)


def test_hidden_fixed_slow_mode_exceeds_faster_declared_envelope() -> None:
    result = hidden_slow_mode_witness(
        baseline_contraction=0.6,
        hidden_contraction=0.9,
        initial_amplitude=1.0,
        lags=range(1, 9),
        absolute_tolerance=1.0e-12,
    )

    assert result.matches_expected
    assert result.no_adaptive_update
    assert all(margin > 0.0 for margin in result.exceedance_margins)
    assert np.isclose(result.hidden_response[-1], 0.9**8, rtol=0.0, atol=1.0e-12)


def test_fixed_clock_chain_exactly_reproduces_arbitrary_finite_path() -> None:
    target = [0.25, -0.10, 0.60, 0.20, -0.35, 0.05]
    result = fixed_clock_chain_witness(
        target,
        expected_dobrushin=1.0,
        absolute_tolerance=1.0e-12,
    )

    assert result.matches_expected
    assert result.no_adaptive_update
    assert result.time_homogeneous
    assert result.maximum_absolute_error == 0.0
    assert result.reproduced_path == tuple(target)


def test_dobrushin_coefficient_of_uniform_kernel_is_zero() -> None:
    coefficient = dobrushin_coefficient(
        [[0.5, 0.5], [0.5, 0.5]],
        absolute_tolerance=1.0e-12,
    )

    assert coefficient == 0.0


def test_hidden_slow_mode_rejects_invalid_contraction_order() -> None:
    with pytest.raises(ValueError, match="baseline < hidden"):
        hidden_slow_mode_witness(
            baseline_contraction=0.9,
            hidden_contraction=0.6,
            initial_amplitude=1.0,
            lags=[1],
            absolute_tolerance=1.0e-12,
        )

