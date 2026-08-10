from __future__ import annotations

from collections.abc import Callable
from typing import TypeAlias

import numpy as np
import pytest
from numpy.typing import NDArray

from ecomd.observation.continuous_time import (
    bound_constrained_kkt_diagnostics,
    branching_spectral_radius,
    build_queue_feature_design,
    circular_shift_queue_state,
    exponential_trace_design,
    fit_linear_hawkes_process,
    fit_poisson_process,
    hawkes_objective_gradient,
    hawkes_objective_gradient_hessian,
    lobster_mark_ids,
    point_process_log_likelihood,
    queue_hawkes_objective_gradient,
    queue_objective_gradient,
    run_active_set_newton,
    run_lbfgsb_stage,
    simulate_exponential_hawkes_cluster,
    strictify_timestamps,
    time_rescaling_diagnostics,
)

FloatArray: TypeAlias = NDArray[np.float64]


def _finite_difference(
    objective: Callable[[FloatArray], tuple[float, FloatArray]],
    values: FloatArray,
    epsilon: float = 1e-6,
) -> FloatArray:
    gradient = np.empty_like(values)
    for index in range(values.size):
        plus = values.copy()
        minus = values.copy()
        plus[index] += epsilon
        minus[index] -= epsilon
        gradient[index] = (objective(plus)[0] - objective(minus)[0]) / (2.0 * epsilon)
    return gradient


@pytest.mark.parametrize("policy", ["nextafter", "capped_uniform"])  # type: ignore[untyped-decorator]
def test_timestamp_ties_become_strict_without_crossing(policy: str) -> None:
    raw = np.asarray((1.0, 1.0, 1.0, 1.1, 1.1, 2.0), dtype=np.float64)
    adjusted, diagnostics = strictify_timestamps(raw, policy)  # type: ignore[arg-type]
    assert np.all(np.diff(adjusted) > 0.0)
    assert adjusted[0] == raw[0]
    assert adjusted[3] == raw[3]
    assert adjusted[5] == raw[5]
    assert adjusted[2] < raw[3]
    assert adjusted[4] < raw[5]
    assert diagnostics.zero_increments == 3
    assert diagnostics.tie_groups == 2
    assert diagnostics.largest_group == 3


def test_timestamp_validation_rejects_bad_input() -> None:
    with pytest.raises(ValueError, match="decreasing"):
        strictify_timestamps(np.asarray((1.0, 0.9)), "nextafter")
    with pytest.raises(ValueError, match="unknown"):
        strictify_timestamps(
            np.asarray((1.0, 2.0)),
            "random",  # type: ignore[arg-type]
        )


def test_lobster_external_sign_mapping() -> None:
    event = np.asarray((1, 1, 2, 3, 4, 4, 5, 5), dtype=np.int64)
    direction = np.asarray((1, -1, 1, -1, -1, 1, -1, 1), dtype=np.int64)
    assert np.array_equal(
        lobster_mark_ids(event, direction),
        np.asarray((0, 1, 2, 3, 4, 5, 4, 5), dtype=np.int64),
    )
    with pytest.raises(ValueError, match="1--5"):
        lobster_mark_ids(np.asarray((7,), dtype=np.int64), np.asarray((-1,), dtype=np.int64))


def test_exponential_trace_and_compensator_are_exact() -> None:
    times = np.asarray((0.0, 0.2, 0.7), dtype=np.float64)
    marks = np.asarray((0, 1, 0), dtype=np.int64)
    traces, integrals = exponential_trace_design(times, marks, 2, (2.0,))
    expected_traces = np.asarray(
        (
            (0.0, 0.0),
            (2.0 * np.exp(-0.4), 0.0),
            (2.0 * np.exp(-1.4), 2.0 * np.exp(-1.0)),
        ),
        dtype=np.float64,
    )
    expected_integrals = np.asarray(
        (
            (0.0, 0.0),
            (1.0 - np.exp(-0.4), 0.0),
            (
                np.exp(-0.4) * (1.0 - np.exp(-1.0)),
                1.0 - np.exp(-1.0),
            ),
        ),
        dtype=np.float64,
    )
    assert np.allclose(traces, expected_traces, atol=1e-14)
    assert np.allclose(integrals, expected_integrals, atol=1e-14)


def test_analytic_point_process_gradients_match_finite_difference() -> None:
    event_trace = np.asarray(((0.2, 0.5), (0.7, 0.1), (0.4, 0.3)))
    integrated = np.asarray((1.4, 0.8))
    hawkes_values = np.asarray((0.8, 0.15, 0.12))

    def hawkes_objective(values: FloatArray) -> tuple[float, FloatArray]:
        return hawkes_objective_gradient(values, event_trace, integrated, 3.2, 7)

    assert np.allclose(
        hawkes_objective(hawkes_values)[1],
        _finite_difference(hawkes_objective, hawkes_values),
        atol=1e-8,
    )

    all_queue = np.asarray(((1.0, -0.4), (1.0, 0.2), (1.0, 0.7), (1.0, -0.1)))
    event_queue = all_queue[[0, 2]]
    intervals = np.asarray((0.2, 0.4, 0.3, 0.5))
    queue_values = np.asarray((-0.3, 0.2))

    def queue_objective(values: FloatArray) -> tuple[float, FloatArray]:
        return queue_objective_gradient(values, event_queue, all_queue, intervals, 4)

    assert np.allclose(
        queue_objective(queue_values)[1],
        _finite_difference(queue_objective, queue_values),
        atol=1e-8,
    )

    event_hawkes = np.asarray(((0.2, 0.1), (0.4, 0.6)))
    combined_values = np.asarray((-0.3, 0.2, 0.1, 0.15))

    def combined_objective(values: FloatArray) -> tuple[float, FloatArray]:
        return queue_hawkes_objective_gradient(
            values,
            event_queue,
            event_hawkes,
            all_queue,
            intervals,
            integrated,
            4,
        )

    assert np.allclose(
        combined_objective(combined_values)[1],
        _finite_difference(combined_objective, combined_values),
        atol=2e-8,
    )


def test_projected_kkt_handles_active_lower_and_upper_bounds() -> None:
    parameters = np.asarray((0.0, 0.0, 2.0, 3.0), dtype=np.float64)
    gradient = np.asarray((0.2, 0.5, -0.4, -0.3), dtype=np.float64)
    raw, projected, complementarity, active = bound_constrained_kkt_diagnostics(
        parameters,
        gradient,
        ((None, None), (0.0, None), (0.0, None), (None, 3.0)),
    )
    assert raw == 0.5
    assert projected == 0.4
    assert complementarity == 0.8
    assert active == 2


def test_hawkes_analytic_hessian_matches_gradient_difference() -> None:
    event_trace = np.asarray(((0.2, 0.5), (0.7, 0.1), (0.4, 0.3)), dtype=np.float64)
    integrated = np.asarray((1.4, 0.8), dtype=np.float64)
    values = np.asarray((0.8, 0.15, 0.12), dtype=np.float64)
    objective, gradient, hessian = hawkes_objective_gradient_hessian(
        values,
        event_trace,
        integrated,
        3.2,
        7,
    )
    plain_objective, plain_gradient = hawkes_objective_gradient(
        values,
        event_trace,
        integrated,
        3.2,
        7,
    )
    numerical = np.empty_like(hessian)
    for index in range(values.size):
        plus = values.copy()
        minus = values.copy()
        plus[index] += 1e-6
        minus[index] -= 1e-6
        plus_gradient = hawkes_objective_gradient_hessian(
            plus,
            event_trace,
            integrated,
            3.2,
            7,
        )[1]
        minus_gradient = hawkes_objective_gradient_hessian(
            minus,
            event_trace,
            integrated,
            3.2,
            7,
        )[1]
        numerical[:, index] = (plus_gradient - minus_gradient) / (2e-6)
    assert np.isclose(objective, plain_objective, atol=1e-15, rtol=0.0)
    assert np.allclose(gradient, plain_gradient, atol=1e-15, rtol=0.0)
    assert np.allclose(hessian, numerical, atol=1e-9)
    assert np.allclose(hessian, hessian.T, atol=1e-15)


def test_active_set_newton_reaches_bound_constrained_kkt() -> None:
    def objective(values: FloatArray) -> tuple[float, FloatArray, FloatArray]:
        difference = values - np.asarray((2.0, -1.0), dtype=np.float64)
        return (
            0.5 * float(np.dot(difference, difference)),
            difference,
            np.eye(2, dtype=np.float64),
        )

    result = run_active_set_newton(
        objective,
        np.asarray((0.0, 2.0), dtype=np.float64),
        np.asarray((-10.0, 0.0), dtype=np.float64),
        maxiter=8,
        stop_kkt=1e-11,
        active_tolerance=1e-12,
        armijo_constant=1e-4,
        backtrack_factor=0.5,
        max_line_search_trials=60,
    )
    assert result.success
    assert np.allclose(result.parameters, (2.0, 0.0), atol=1e-12)
    assert result.raw_gradient_inf_norm == 1.0
    assert result.projected_gradient_inf_norm <= 1e-12
    assert result.complementarity_inf_norm <= 1e-12
    assert result.active_bounds == 1
    accepted = [iteration for iteration in result.trace if iteration.step_size is not None]
    assert len(accepted) == 2
    assert all(iteration.armijo_satisfied for iteration in accepted)


def test_active_set_newton_rejects_bit_identical_candidate() -> None:
    def objective(values: FloatArray) -> tuple[float, FloatArray, FloatArray]:
        return (
            1.0,
            np.full_like(values, 1e-20),
            np.eye(values.size, dtype=np.float64),
        )

    result = run_active_set_newton(
        objective,
        np.asarray((1.0,), dtype=np.float64),
        np.asarray((0.0,), dtype=np.float64),
        maxiter=8,
        stop_kkt=1e-25,
        active_tolerance=1e-12,
        armijo_constant=1e-4,
        backtrack_factor=0.5,
        max_line_search_trials=60,
    )
    assert not result.success
    assert result.message == "Newton candidate is bit-identical at float precision"
    assert len(result.trace) == 1
    assert result.trace[0].armijo_satisfied is False
    assert result.trace[0].line_search_trials == 1


def test_lbfgsb_stage_recomputes_projected_kkt() -> None:
    def objective(values: FloatArray) -> tuple[float, FloatArray]:
        difference = values - np.asarray((2.0, -1.0), dtype=np.float64)
        return float(np.dot(difference, difference)), 2.0 * difference

    result = run_lbfgsb_stage(
        objective,
        np.asarray((0.0, 2.0), dtype=np.float64),
        ((None, None), (0.0, None)),
        maxiter=100,
        ftol=1e-15,
        gtol=1e-10,
        maxls=40,
    )
    assert np.allclose(result.parameters, (2.0, 0.0), atol=1e-10)
    assert result.raw_gradient_inf_norm >= 1.9
    assert result.projected_gradient_inf_norm <= 1e-10
    assert result.complementarity_inf_norm <= 1e-10
    assert result.active_bounds == 1


def test_queue_features_use_only_preceding_book_and_shift_state_only() -> None:
    times = np.arange(12, dtype=np.float64) + 34_200.0
    books: NDArray[np.int64] = np.empty((12, 4), dtype=np.int64)
    for index in range(12):
        books[index] = (10_020 + index % 3, 20 + index, 10_000 - index % 2, 30 + 2 * index)
    first = build_queue_feature_design(
        times,
        books,
        train_start=2,
        train_end=8,
        archive_start=34_200.0,
        archive_end=34_220.0,
    )
    changed = books.copy()
    changed[9, 1] += 100
    second = build_queue_feature_design(
        times,
        changed,
        train_start=2,
        train_end=8,
        archive_start=34_200.0,
        archive_end=34_220.0,
    )
    assert first.source_indices[9] == 8
    assert first.source_indices[10] == 9
    assert np.array_equal(first.values[9], second.values[9])
    assert not np.array_equal(first.values[10], second.values[10])
    shifted = circular_shift_queue_state(first.values, train_start=2, train_end=8, test_end=12)
    assert np.array_equal(shifted[:, 0], first.values[:, 0])
    assert np.array_equal(shifted[:, 5:], first.values[:, 5:])
    assert np.allclose(
        np.sort(shifted[2:8, 1:5], axis=0),
        np.sort(first.values[2:8, 1:5], axis=0),
    )


def test_synthetic_hawkes_fit_and_likelihood_are_finite() -> None:
    generator = np.random.default_rng(138)
    truth = np.asarray(((0.22, 0.08), (0.06, 0.18)), dtype=np.float64)
    times, marks = simulate_exponential_hawkes_cluster(
        (0.35, 0.25),
        truth,
        1.3,
        burn_start=-200.0,
        end_time=4_000.0,
        generator=generator,
    )
    assert times.size > 2_000
    traces, integrals = exponential_trace_design(times, marks, 2, (1.3,))
    train_start = int(0.10 * times.size)
    train_end = int(0.60 * times.size)
    poisson = fit_poisson_process(
        times,
        marks,
        start=train_start,
        end=train_end,
        n_marks=2,
        n_trace_features=2,
    )
    hawkes = fit_linear_hawkes_process(
        times,
        marks,
        traces,
        integrals,
        start=train_start,
        end=train_end,
        n_marks=2,
        n_scales=1,
        diagonal=False,
        name="hawkes_full",
    )
    queue = np.ones((times.size, 1), dtype=np.float64)
    train_poisson = point_process_log_likelihood(
        poisson,
        times,
        marks,
        traces,
        integrals,
        queue,
        start=train_start,
        end=train_end,
    )
    train_hawkes = point_process_log_likelihood(
        hawkes,
        times,
        marks,
        traces,
        integrals,
        queue,
        start=train_start,
        end=train_end,
    )
    assert hawkes.success or hawkes.gradient_inf_norm <= 1e-5
    assert train_hawkes >= train_poisson - 1e-8
    assert branching_spectral_radius(hawkes.excitation, n_marks=2, n_scales=1) < 1.0
    diagnostics = time_rescaling_diagnostics(
        hawkes,
        times,
        marks,
        traces,
        integrals,
        queue,
        start=train_end,
        end=times.size,
    )
    assert diagnostics.count == times.size - train_end
    assert np.isfinite(
        np.asarray(
            (
                diagnostics.mean,
                diagnostics.variance,
                diagnostics.ks_statistic,
                diagnostics.lag1_correlation,
            )
        )
    ).all()
