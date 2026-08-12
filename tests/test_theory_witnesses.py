import numpy as np
import pytest

from ecomd.research.theory_witnesses import (
    fixed_operator_order_witness,
    stacked_observability_witness,
)


def test_stacked_observability_is_exactly_the_ordinary_gramian() -> None:
    result = stacked_observability_witness(
        [[[1.0, 0.0]], [[0.0, 1.0]]],
        expected_single_ranks=(1, 1),
        expected_stacked_rank=2,
        expected_stacked_eigenvalues=(1.0, 1.0),
        absolute_tolerance=1.0e-12,
    )

    assert result.matches_expected
    assert result.direct_gramian_max_abs_error == 0.0


def test_fixed_nonadaptive_operators_have_nonzero_order_effect() -> None:
    result = fixed_operator_order_witness(
        [1.0, 0.0],
        [[0.9, 0.1], [0.2, 0.8]],
        [[0.6, 0.4], [0.05, 0.95]],
        [0.0, 1.0],
        expected_ab=0.455,
        expected_ba=0.38,
        expected_difference=0.075,
        absolute_tolerance=1.0e-12,
    )

    assert result.matches_expected
    assert np.isclose(result.difference, 0.075, rtol=0.0, atol=1.0e-12)
    assert result.operator_a_row_stochastic
    assert result.operator_b_row_stochastic


def test_order_witness_rejects_inconsistent_dimensions() -> None:
    with pytest.raises(ValueError, match="same state dimension"):
        fixed_operator_order_witness(
            [1.0, 0.0],
            [[1.0, 0.0], [0.0, 1.0]],
            [[1.0]],
            [0.0, 1.0],
            expected_ab=0.0,
            expected_ba=0.0,
            expected_difference=0.0,
            absolute_tolerance=1.0e-12,
        )
