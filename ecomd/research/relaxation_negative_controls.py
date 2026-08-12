"""Non-adaptive counterexamples for relaxation-exceedance attribution."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class HiddenSlowModeResult:
    """Diagnostics for an omitted fixed slow mode outside a declared envelope."""

    lags: tuple[int, ...]
    baseline_envelope: tuple[float, ...]
    hidden_response: tuple[float, ...]
    exceedance_margins: tuple[float, ...]
    no_adaptive_update: bool
    matches_expected: bool

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-safe representation."""

        return {
            "lags": list(self.lags),
            "baseline_envelope": list(self.baseline_envelope),
            "hidden_response": list(self.hidden_response),
            "exceedance_margins": list(self.exceedance_margins),
            "no_adaptive_update": self.no_adaptive_update,
            "matches_expected": self.matches_expected,
        }


@dataclass(frozen=True)
class FixedClockResult:
    """Diagnostics for a fixed Markov clock reproducing a finite response path."""

    transition_matrix: FloatArray
    reproduced_path: tuple[float, ...]
    target_path: tuple[float, ...]
    maximum_absolute_error: float
    dobrushin_coefficient: float
    row_stochastic: bool
    time_homogeneous: bool
    no_adaptive_update: bool
    matches_expected: bool

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-safe representation."""

        return {
            "transition_matrix": self.transition_matrix.tolist(),
            "reproduced_path": list(self.reproduced_path),
            "target_path": list(self.target_path),
            "maximum_absolute_error": self.maximum_absolute_error,
            "dobrushin_coefficient": self.dobrushin_coefficient,
            "row_stochastic": self.row_stochastic,
            "time_homogeneous": self.time_homogeneous,
            "no_adaptive_update": self.no_adaptive_update,
            "matches_expected": self.matches_expected,
        }


def _finite_scalar(value: float, *, name: str) -> float:
    scalar = float(value)
    if not np.isfinite(scalar):
        raise ValueError(f"{name} must be finite")
    return scalar


def _validate_tolerance(absolute_tolerance: float) -> float:
    tolerance = _finite_scalar(absolute_tolerance, name="absolute_tolerance")
    if tolerance <= 0.0:
        raise ValueError("absolute_tolerance must be positive")
    return tolerance


def hidden_slow_mode_witness(
    *,
    baseline_contraction: float,
    hidden_contraction: float,
    initial_amplitude: float,
    lags: Sequence[int],
    absolute_tolerance: float,
) -> HiddenSlowModeResult:
    """Show envelope exceedance from a fixed omitted mode with slower contraction."""

    tolerance = _validate_tolerance(absolute_tolerance)
    baseline = _finite_scalar(baseline_contraction, name="baseline_contraction")
    hidden = _finite_scalar(hidden_contraction, name="hidden_contraction")
    amplitude = _finite_scalar(initial_amplitude, name="initial_amplitude")
    frozen_lags = tuple(lags)
    if not frozen_lags or any(isinstance(lag, bool) or not isinstance(lag, int) or lag <= 0 for lag in frozen_lags):
        raise ValueError("lags must be a non-empty sequence of positive integers")
    if not 0.0 <= baseline < hidden < 1.0:
        raise ValueError("contractions must satisfy 0 <= baseline < hidden < 1")
    if amplitude <= 0.0:
        raise ValueError("initial_amplitude must be positive")

    baseline_envelope = tuple(amplitude * baseline**lag for lag in frozen_lags)
    hidden_response = tuple(amplitude * hidden**lag for lag in frozen_lags)
    margins = tuple(response - envelope for response, envelope in zip(hidden_response, baseline_envelope, strict=True))
    matches_expected = all(margin > tolerance for margin in margins)
    return HiddenSlowModeResult(
        lags=frozen_lags,
        baseline_envelope=baseline_envelope,
        hidden_response=hidden_response,
        exceedance_margins=margins,
        no_adaptive_update=True,
        matches_expected=matches_expected,
    )


def _row_stochastic(matrix: FloatArray, *, absolute_tolerance: float) -> bool:
    return bool(
        matrix.ndim == 2
        and matrix.shape[0] == matrix.shape[1]
        and np.all(matrix >= -absolute_tolerance)
        and np.allclose(
            matrix.sum(axis=1),
            np.ones(matrix.shape[0], dtype=np.float64),
            rtol=0.0,
            atol=absolute_tolerance,
        )
    )


def dobrushin_coefficient(matrix: object, *, absolute_tolerance: float) -> float:
    """Return the total-variation contraction coefficient of a row kernel."""

    tolerance = _validate_tolerance(absolute_tolerance)
    operator = np.asarray(matrix, dtype=np.float64)
    if not np.isfinite(operator).all() or not _row_stochastic(operator, absolute_tolerance=tolerance):
        raise ValueError("matrix must be a finite row-stochastic square matrix")
    row_distances = np.abs(operator[:, None, :] - operator[None, :, :]).sum(axis=2)
    return float(0.5 * np.max(row_distances))


def fixed_clock_chain_witness(
    residual_path: Sequence[float],
    *,
    expected_dobrushin: float,
    absolute_tolerance: float,
) -> FixedClockResult:
    """Represent any declared finite path with a fixed deterministic clock chain."""

    tolerance = _validate_tolerance(absolute_tolerance)
    target = np.asarray(tuple(residual_path), dtype=np.float64)
    if target.ndim != 1 or target.size < 2 or not np.isfinite(target).all():
        raise ValueError("residual_path must contain at least two finite values")
    expected = _finite_scalar(expected_dobrushin, name="expected_dobrushin")

    state_count = int(target.size)
    transition = np.zeros((state_count, state_count), dtype=np.float64)
    transition[np.arange(state_count - 1), np.arange(1, state_count)] = 1.0
    transition[-1, -1] = 1.0
    initial = np.zeros(state_count, dtype=np.float64)
    initial[0] = 1.0

    distribution = initial.copy()
    reproduced: list[float] = []
    for _ in range(state_count):
        reproduced.append(float(distribution @ target))
        distribution = distribution @ transition

    reproduced_array = np.asarray(reproduced, dtype=np.float64)
    maximum_error = float(np.max(np.abs(reproduced_array - target)))
    is_stochastic = _row_stochastic(transition, absolute_tolerance=tolerance)
    coefficient = dobrushin_coefficient(transition, absolute_tolerance=tolerance)
    matches_expected = (
        is_stochastic
        and maximum_error <= tolerance
        and np.isclose(coefficient, expected, rtol=0.0, atol=tolerance)
    )
    return FixedClockResult(
        transition_matrix=transition,
        reproduced_path=tuple(reproduced),
        target_path=tuple(float(value) for value in target),
        maximum_absolute_error=maximum_error,
        dobrushin_coefficient=coefficient,
        row_stochastic=is_stochastic,
        time_homogeneous=True,
        no_adaptive_update=True,
        matches_expected=bool(matches_expected),
    )

