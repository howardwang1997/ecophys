"""Continuous-time marked point-process utilities for external L2 messages."""

from __future__ import annotations

import heapq
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any, Literal, TypeAlias, cast

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import minimize
from scipy.stats import kstest

FloatArray: TypeAlias = NDArray[np.float64]
IntArray: TypeAlias = NDArray[np.int64]
TimestampPolicy: TypeAlias = Literal["nextafter", "capped_uniform"]
BaseKind: TypeAlias = Literal["constant", "loglinear"]
Objective: TypeAlias = Callable[[FloatArray], tuple[float, FloatArray]]
HessianObjective: TypeAlias = Callable[[FloatArray], tuple[float, FloatArray, FloatArray]]
Bound: TypeAlias = tuple[float | None, float | None]

LOBSTER_MARK_NAMES = (
    "bid_add",
    "ask_add",
    "bid_cancel",
    "ask_cancel",
    "aggressive_buy",
    "aggressive_sell",
)


@dataclass(frozen=True)
class TimestampDiagnostics:
    policy: str
    n_events: int
    zero_increments: int
    tie_groups: int
    largest_group: int
    raw_negative_increments: int
    raw_minimum_positive_interval: float
    adjusted_minimum_interval: float
    maximum_adjustment: float


@dataclass(frozen=True)
class QueueFeatureDesign:
    values: FloatArray
    means: FloatArray
    scales: FloatArray
    source_indices: IntArray


@dataclass(frozen=True)
class PointProcessFit:
    name: str
    base_kind: BaseKind
    base_coefficients: FloatArray
    excitation: FloatArray
    success: bool
    iterations: tuple[int, ...]
    gradient_inf_norm: float
    messages: tuple[str, ...]


@dataclass(frozen=True)
class OptimizerStageResult:
    parameters: FloatArray
    objective: float
    scipy_success: bool
    iterations: int
    function_evaluations: int
    raw_gradient_inf_norm: float
    projected_gradient_inf_norm: float
    complementarity_inf_norm: float
    active_bounds: int
    message: str


@dataclass(frozen=True)
class NewtonIterationResult:
    index: int
    parameters: FloatArray
    objective: float
    raw_gradient_inf_norm: float
    projected_gradient_inf_norm: float
    complementarity_inf_norm: float
    active_bounds: int
    hessian_condition_number: float
    hessian_minimum_eigenvalue: float
    step_size: float | None
    line_search_trials: int
    directional_derivative: float | None
    armijo_satisfied: bool | None


@dataclass(frozen=True)
class ActiveSetNewtonResult:
    parameters: FloatArray
    objective: float
    success: bool
    message: str
    raw_gradient_inf_norm: float
    projected_gradient_inf_norm: float
    complementarity_inf_norm: float
    active_bounds: int
    trace: tuple[NewtonIterationResult, ...]


@dataclass(frozen=True)
class RescalingDiagnostics:
    count: int
    mean: float
    variance: float
    ks_statistic: float
    lag1_correlation: float


def strictify_timestamps(
    raw_times: FloatArray,
    policy: TimestampPolicy,
) -> tuple[FloatArray, TimestampDiagnostics]:
    """Make nondecreasing vendor timestamps strict while preserving row order."""
    raw = np.asarray(raw_times, dtype=np.float64)
    if policy not in ("nextafter", "capped_uniform"):
        raise ValueError(f"unknown timestamp policy: {policy}")
    if raw.ndim != 1 or raw.size < 2 or not np.isfinite(raw).all():
        raise ValueError("timestamps must be a finite vector with at least two events")
    differences = np.diff(raw)
    negative = int(np.count_nonzero(differences < 0.0))
    if negative:
        raise ValueError("raw timestamps are decreasing")
    positive = differences[differences > 0.0]
    if positive.size == 0:
        raise ValueError("timestamps contain no positive interval")
    adjusted = raw.copy()
    zero_increments = int(np.count_nonzero(differences == 0.0))
    tie_groups = 0
    largest_group = 1
    start = 0
    while start < raw.size:
        end = start + 1
        while end < raw.size and raw[end] == raw[start]:
            end += 1
        multiplicity = end - start
        if multiplicity > 1:
            tie_groups += 1
            largest_group = max(largest_group, multiplicity)
            next_distinct = float(raw[end]) if end < raw.size else None
            if policy == "nextafter":
                for index in range(start + 1, end):
                    adjusted[index] = np.nextafter(adjusted[index - 1], np.inf)
            elif policy == "capped_uniform":
                if next_distinct is None:
                    delta = 1e-9
                else:
                    delta = min(1e-9, (next_distinct - float(raw[start])) / (multiplicity + 1))
                if delta <= 0.0 or not np.isfinite(delta):
                    raise RuntimeError("invalid capped-uniform timestamp increment")
                for offset, index in enumerate(range(start + 1, end), start=1):
                    candidate = float(raw[start]) + offset * delta
                    if candidate <= adjusted[index - 1]:
                        candidate = float(np.nextafter(adjusted[index - 1], np.inf))
                    adjusted[index] = candidate
            if next_distinct is not None and adjusted[end - 1] >= next_distinct:
                raise RuntimeError("tie adjustment crossed the next distinct timestamp")
        start = end
    adjusted_differences = np.diff(adjusted)
    if np.any(adjusted_differences <= 0.0):
        raise RuntimeError("adjusted timestamps are not strictly increasing")
    diagnostics = TimestampDiagnostics(
        policy=policy,
        n_events=int(raw.size),
        zero_increments=zero_increments,
        tie_groups=tie_groups,
        largest_group=largest_group,
        raw_negative_increments=negative,
        raw_minimum_positive_interval=float(np.min(positive)),
        adjusted_minimum_interval=float(np.min(adjusted_differences)),
        maximum_adjustment=float(np.max(adjusted - raw)),
    )
    return adjusted, diagnostics


def lobster_mark_ids(event_type: IntArray, direction: IntArray) -> IntArray:
    """Map vendor event type/direction to the six preregistered marks."""
    event = np.asarray(event_type, dtype=np.int64)
    side = np.asarray(direction, dtype=np.int64)
    if event.ndim != 1 or side.shape != event.shape or event.size < 1:
        raise ValueError("event type and direction must be aligned vectors")
    if np.any(~np.isin(event, (1, 2, 3, 4, 5))):
        raise ValueError("only LOBSTER event types 1--5 are accepted")
    if np.any(~np.isin(side, (-1, 1))):
        raise ValueError("LOBSTER direction must be -1 or +1")
    marks = np.empty(event.size, dtype=np.int64)
    additions = event == 1
    cancellations = np.isin(event, (2, 3))
    executions = np.isin(event, (4, 5))
    marks[additions & (side == 1)] = 0
    marks[additions & (side == -1)] = 1
    marks[cancellations & (side == 1)] = 2
    marks[cancellations & (side == -1)] = 3
    marks[executions & (side == -1)] = 4
    marks[executions & (side == 1)] = 5
    if np.any((marks < 0) | (marks >= len(LOBSTER_MARK_NAMES))):
        raise RuntimeError("a LOBSTER message did not map to exactly one mark")
    return marks


def exponential_trace_design(
    times: FloatArray,
    marks: IntArray,
    n_marks: int,
    betas: Sequence[float],
) -> tuple[FloatArray, FloatArray]:
    """Return pre-event exponential traces and exact per-interval integrals."""
    event_times = np.asarray(times, dtype=np.float64)
    event_marks = np.asarray(marks, dtype=np.int64)
    decay_rates = np.asarray(tuple(betas), dtype=np.float64)
    if event_times.ndim != 1 or event_marks.shape != event_times.shape:
        raise ValueError("times and marks must be aligned vectors")
    if event_times.size < 2 or np.any(np.diff(event_times) <= 0.0):
        raise ValueError("times must be strictly increasing")
    if n_marks < 1 or np.any((event_marks < 0) | (event_marks >= n_marks)):
        raise ValueError("mark is outside the declared range")
    if decay_rates.ndim != 1 or decay_rates.size < 1 or np.any(decay_rates <= 0.0):
        raise ValueError("decay rates must be positive")
    n_features = n_marks * decay_rates.size
    traces = np.zeros((event_times.size, n_features), dtype=np.float64)
    integrals = np.zeros_like(traces)
    after_event = np.zeros((n_marks, decay_rates.size), dtype=np.float64)
    after_event[event_marks[0]] += decay_rates
    for index in range(1, event_times.size):
        delta = float(event_times[index] - event_times[index - 1])
        decay = np.exp(-decay_rates * delta)
        interval = after_event * (-np.expm1(-decay_rates * delta) / decay_rates)
        integrals[index] = interval.reshape(-1)
        after_event *= decay
        traces[index] = after_event.reshape(-1)
        after_event[event_marks[index]] += decay_rates
    return traces, integrals


def build_queue_feature_design(
    raw_times: FloatArray,
    l1_books: IntArray,
    *,
    train_start: int,
    train_end: int,
    archive_start: float,
    archive_end: float,
) -> QueueFeatureDesign:
    """Build train-standardized interval features from the preceding L1 book."""
    times = np.asarray(raw_times, dtype=np.float64)
    books = np.asarray(l1_books, dtype=np.int64)
    if times.ndim != 1 or books.shape != (times.size, 4) or times.size < 3:
        raise ValueError("L1 books must have one four-column row per timestamp")
    if not 1 <= train_start < train_end <= times.size:
        raise ValueError("invalid training bounds")
    if archive_end <= archive_start:
        raise ValueError("invalid archive window")
    pre = books[:-1]
    ask_price = pre[:, 0].astype(np.float64)
    ask_size = pre[:, 1].astype(np.float64)
    bid_price = pre[:, 2].astype(np.float64)
    bid_size = pre[:, 3].astype(np.float64)
    if np.any(ask_price <= bid_price) or np.any(ask_size < 0.0) or np.any(bid_size < 0.0):
        raise ValueError("invalid pre-event L1 book")
    total = ask_size + bid_size
    state = np.column_stack(
        (
            (bid_size - ask_size) / np.maximum(total, 1.0),
            np.log((bid_size + 1.0) / (ask_size + 1.0)),
            np.log1p(total),
            np.log(np.maximum(ask_price - bid_price, 1.0)),
        )
    )
    fraction = (times[:-1] - archive_start) / (archive_end - archive_start)
    clock = np.column_stack((np.sin(2.0 * np.pi * fraction), np.cos(2.0 * np.pi * fraction)))
    raw_features = np.empty((times.size, 6), dtype=np.float64)
    raw_features[1:] = np.column_stack((state, clock))
    raw_features[0] = raw_features[1]
    training = raw_features[train_start:train_end]
    means = np.mean(training, axis=0)
    scales = np.std(training, axis=0)
    if not np.isfinite(means).all() or not np.isfinite(scales).all():
        raise RuntimeError("queue feature normalizer is non-finite")
    if np.any(scales <= 1e-12):
        raise RuntimeError("queue feature has near-zero training scale")
    standardized = (raw_features - means) / scales
    values = np.column_stack((np.ones(times.size, dtype=np.float64), standardized))
    source_indices: IntArray = np.arange(times.size, dtype=np.int64) - 1
    source_indices[0] = -1
    return QueueFeatureDesign(values, means, scales, source_indices)


def circular_shift_queue_state(
    features: FloatArray,
    *,
    train_start: int,
    train_end: int,
    test_end: int,
) -> FloatArray:
    """Shift four queue-state columns while retaining clock alignment."""
    values = np.asarray(features, dtype=np.float64)
    if values.ndim != 2 or values.shape[1] != 7:
        raise ValueError("expected intercept, four state and two clock features")
    if not 1 <= train_start < train_end < test_end <= values.shape[0]:
        raise ValueError("invalid split bounds")
    shifted = values.copy()
    for start, end in ((train_start, train_end), (train_end, test_end)):
        length = end - start
        offset = length // 3
        if offset < 1:
            raise ValueError("split is too short for the frozen shift")
        shifted[start:end, 1:5] = np.roll(values[start:end, 1:5], shift=offset, axis=0)
    return shifted


def _window_arrays(
    times: FloatArray,
    marks: IntArray,
    traces: FloatArray,
    interval_integrals: FloatArray,
    start: int,
    end: int,
) -> tuple[FloatArray, IntArray, FloatArray, FloatArray, FloatArray]:
    if not 1 <= start < end <= times.size:
        raise ValueError("invalid point-process window")
    if marks.shape != times.shape or traces.shape != interval_integrals.shape:
        raise ValueError("point-process arrays are misaligned")
    if traces.shape[0] != times.size:
        raise ValueError("trace rows do not match event times")
    event_times = times[start:end]
    previous_times = times[start - 1 : end - 1]
    return (
        event_times - previous_times,
        marks[start:end],
        traces[start:end],
        interval_integrals[start:end],
        event_times,
    )


def hawkes_objective_gradient(
    parameters: FloatArray,
    event_features: FloatArray,
    integrated_features: FloatArray,
    duration: float,
    normalizer: int,
) -> tuple[float, FloatArray]:
    """Negative target-mark Hawkes likelihood and analytic gradient."""
    values = np.asarray(parameters, dtype=np.float64)
    features = np.asarray(event_features, dtype=np.float64)
    integrated = np.asarray(integrated_features, dtype=np.float64)
    if values.size != integrated.size + 1 or features.shape[1] != integrated.size:
        raise ValueError("Hawkes objective dimensions are inconsistent")
    mu = float(values[0])
    alpha = values[1:]
    intensity = mu + features @ alpha
    if mu <= 0.0 or np.any(alpha < 0.0) or np.any(intensity <= 0.0):
        return float("inf"), np.full_like(values, np.nan)
    objective = (
        -float(np.sum(np.log(intensity))) + mu * duration + float(np.dot(alpha, integrated))
    ) / normalizer
    inverse = 1.0 / intensity
    gradient = np.empty_like(values)
    gradient[0] = (-float(np.sum(inverse)) + duration) / normalizer
    gradient[1:] = (-features.T @ inverse + integrated) / normalizer
    return objective, gradient


def hawkes_objective_gradient_hessian(
    parameters: FloatArray,
    event_features: FloatArray,
    integrated_features: FloatArray,
    duration: float,
    normalizer: int,
) -> tuple[float, FloatArray, FloatArray]:
    """Negative Hawkes likelihood with its analytic gradient and Hessian."""
    values = np.asarray(parameters, dtype=np.float64)
    features = np.asarray(event_features, dtype=np.float64)
    integrated = np.asarray(integrated_features, dtype=np.float64)
    if values.size != integrated.size + 1 or features.shape[1] != integrated.size:
        raise ValueError("Hawkes objective dimensions are inconsistent")
    if normalizer < 1 or duration <= 0.0 or not np.isfinite(duration):
        raise ValueError("Hawkes duration and normalizer must be positive")
    design = np.column_stack((np.ones(features.shape[0], dtype=np.float64), features))
    compensator = np.concatenate(([duration], integrated))
    intensity = design @ values
    if values[0] <= 0.0 or np.any(values[1:] < 0.0) or np.any(intensity <= 0.0):
        invalid = np.full_like(values, np.nan)
        return float("inf"), invalid, np.full((values.size, values.size), np.nan)
    inverse = 1.0 / intensity
    objective = (-float(np.sum(np.log(intensity))) + float(np.dot(compensator, values))) / normalizer
    gradient = (-design.T @ inverse + compensator) / normalizer
    hessian = (design.T * np.square(inverse)) @ design / normalizer
    return objective, np.asarray(gradient, dtype=np.float64), np.asarray(hessian, dtype=np.float64)


def queue_objective_gradient(
    parameters: FloatArray,
    event_queue: FloatArray,
    all_queue: FloatArray,
    interval_lengths: FloatArray,
    normalizer: int,
) -> tuple[float, FloatArray]:
    """Negative target-mark queue-reactive likelihood and gradient."""
    theta = np.asarray(parameters, dtype=np.float64)
    event_values = np.asarray(event_queue, dtype=np.float64)
    all_values = np.asarray(all_queue, dtype=np.float64)
    intervals = np.asarray(interval_lengths, dtype=np.float64)
    linear = all_values @ theta
    with np.errstate(over="ignore", invalid="ignore"):
        intensity = np.exp(linear)
    if not np.isfinite(intensity).all():
        return float("inf"), np.full_like(theta, np.nan)
    objective = (-float(np.sum(event_values @ theta)) + float(np.dot(intensity, intervals))) / normalizer
    gradient = (-np.sum(event_values, axis=0) + all_values.T @ (intensity * intervals)) / normalizer
    return objective, np.asarray(gradient, dtype=np.float64)


def queue_hawkes_objective_gradient(
    parameters: FloatArray,
    event_queue: FloatArray,
    event_traces: FloatArray,
    all_queue: FloatArray,
    interval_lengths: FloatArray,
    integrated_traces: FloatArray,
    normalizer: int,
) -> tuple[float, FloatArray]:
    """Negative target-mark queue-Hawkes likelihood and analytic gradient."""
    values = np.asarray(parameters, dtype=np.float64)
    n_queue = all_queue.shape[1]
    theta = values[:n_queue]
    alpha = values[n_queue:]
    if event_traces.shape[1] != alpha.size or integrated_traces.size != alpha.size:
        raise ValueError("queue-Hawkes dimensions are inconsistent")
    if np.any(alpha < 0.0):
        return float("inf"), np.full_like(values, np.nan)
    all_linear = all_queue @ theta
    event_linear = event_queue @ theta
    with np.errstate(over="ignore", invalid="ignore"):
        all_base = np.exp(all_linear)
        event_base = np.exp(event_linear)
    event_intensity = event_base + event_traces @ alpha
    if not np.isfinite(all_base).all() or np.any(event_intensity <= 0.0):
        return float("inf"), np.full_like(values, np.nan)
    objective = (
        -float(np.sum(np.log(event_intensity)))
        + float(np.dot(all_base, interval_lengths))
        + float(np.dot(alpha, integrated_traces))
    ) / normalizer
    inverse = 1.0 / event_intensity
    queue_gradient = (
        -event_queue.T @ (event_base * inverse) + all_queue.T @ (all_base * interval_lengths)
    ) / normalizer
    excitation_gradient = (-event_traces.T @ inverse + integrated_traces) / normalizer
    return objective, np.concatenate((queue_gradient, excitation_gradient))


def bound_constrained_kkt_diagnostics(
    parameters: FloatArray,
    gradient: FloatArray,
    bounds: Sequence[Bound],
    *,
    active_tolerance: float = 1e-10,
) -> tuple[float, float, float, int]:
    """Return raw, projected, complementarity and active-bound diagnostics."""
    values = np.asarray(parameters, dtype=np.float64)
    derivatives = np.asarray(gradient, dtype=np.float64)
    if values.ndim != 1 or derivatives.shape != values.shape:
        raise ValueError("parameters and gradient must be aligned vectors")
    if len(bounds) != values.size:
        raise ValueError("bounds do not match parameter count")
    if active_tolerance < 0.0 or not np.isfinite(active_tolerance):
        raise ValueError("active tolerance must be finite and nonnegative")
    if not np.isfinite(values).all() or not np.isfinite(derivatives).all():
        return float("inf"), float("inf"), float("inf"), 0
    projected = derivatives.copy()
    complementarity: list[float] = []
    active = 0
    for index, (lower, upper) in enumerate(bounds):
        value = float(values[index])
        derivative = float(derivatives[index])
        if lower is not None:
            if value < lower - active_tolerance:
                raise ValueError("parameter violates its lower bound")
            distance = max(value - lower, 0.0)
            complementarity.append(abs(distance * derivative))
            if distance <= active_tolerance:
                active += 1
                if derivative > 0.0:
                    projected[index] = 0.0
        if upper is not None:
            if value > upper + active_tolerance:
                raise ValueError("parameter violates its upper bound")
            distance = max(upper - value, 0.0)
            complementarity.append(abs(distance * derivative))
            if distance <= active_tolerance:
                active += 1
                if derivative < 0.0:
                    projected[index] = 0.0
    raw_norm = float(np.max(np.abs(derivatives))) if derivatives.size else 0.0
    projected_norm = float(np.max(np.abs(projected))) if projected.size else 0.0
    complementarity_norm = max(complementarity, default=0.0)
    return raw_norm, projected_norm, complementarity_norm, active


def run_lbfgsb_stage(
    objective: Objective,
    initial: FloatArray,
    bounds: Sequence[Bound],
    *,
    maxiter: int,
    ftol: float,
    gtol: float,
    maxls: int,
    maxcor: int = 10,
    active_tolerance: float = 1e-10,
) -> OptimizerStageResult:
    """Run one deterministic L-BFGS-B stage and recompute KKT diagnostics."""
    if maxiter < 1 or maxls < 1 or maxcor < 1:
        raise ValueError("optimizer iteration settings must be positive")
    result = minimize(
        objective,
        np.asarray(initial, dtype=np.float64),
        method="L-BFGS-B",
        jac=True,
        bounds=list(bounds),
        options={
            "maxiter": maxiter,
            "ftol": ftol,
            "gtol": gtol,
            "maxls": maxls,
            "maxcor": maxcor,
        },
    )
    parameters = np.asarray(result.x, dtype=np.float64)
    value, gradient = objective(parameters)
    raw, projected, complementarity, active = bound_constrained_kkt_diagnostics(
        parameters,
        gradient,
        bounds,
        active_tolerance=active_tolerance,
    )
    return OptimizerStageResult(
        parameters=parameters,
        objective=float(value),
        scipy_success=bool(result.success),
        iterations=int(result.nit),
        function_evaluations=int(result.nfev),
        raw_gradient_inf_norm=raw,
        projected_gradient_inf_norm=projected,
        complementarity_inf_norm=complementarity,
        active_bounds=active,
        message=str(result.message),
    )


def run_active_set_newton(
    objective: HessianObjective,
    initial: FloatArray,
    lower_bounds: FloatArray,
    *,
    maxiter: int,
    stop_kkt: float,
    active_tolerance: float,
    armijo_constant: float,
    backtrack_factor: float,
    max_line_search_trials: int,
) -> ActiveSetNewtonResult:
    """Polish a lower-bounded convex optimum with analytic-Hessian Newton steps."""
    values = np.asarray(initial, dtype=np.float64).copy()
    lower = np.asarray(lower_bounds, dtype=np.float64)
    if values.ndim != 1 or lower.shape != values.shape:
        raise ValueError("initial values and lower bounds must be aligned vectors")
    if not np.isfinite(values).all() or not np.isfinite(lower).all():
        raise ValueError("initial values and lower bounds must be finite")
    if np.any(values < lower - active_tolerance):
        raise ValueError("initial value violates a lower bound")
    if maxiter < 1 or max_line_search_trials < 1:
        raise ValueError("Newton iteration settings must be positive")
    if stop_kkt <= 0.0 or active_tolerance < 0.0:
        raise ValueError("Newton tolerances are invalid")
    if not 0.0 < armijo_constant < 1.0 or not 0.0 < backtrack_factor < 1.0:
        raise ValueError("line-search constants must lie strictly between zero and one")
    bounds: tuple[Bound, ...] = tuple((float(bound), None) for bound in lower)
    trace: list[NewtonIterationResult] = []

    def evaluate(candidate: FloatArray) -> tuple[float, FloatArray, FloatArray, tuple[float, float, float, int]]:
        value, gradient, hessian = objective(candidate)
        derivatives = np.asarray(gradient, dtype=np.float64)
        curvature = np.asarray(hessian, dtype=np.float64)
        if derivatives.shape != candidate.shape or curvature.shape != (candidate.size, candidate.size):
            raise ValueError("Newton objective returned inconsistent derivative dimensions")
        diagnostics = bound_constrained_kkt_diagnostics(
            candidate,
            derivatives,
            bounds,
            active_tolerance=active_tolerance,
        )
        return float(value), derivatives, curvature, diagnostics

    def append_snapshot(
        index: int,
        value: float,
        gradient: FloatArray,
        hessian: FloatArray,
        diagnostics: tuple[float, float, float, int],
        *,
        step_size: float | None,
        line_search_trials: int,
        directional_derivative: float | None,
        armijo_satisfied: bool | None,
    ) -> None:
        if np.isfinite(hessian).all():
            symmetric = 0.5 * (hessian + hessian.T)
            eigenvalues = np.linalg.eigvalsh(symmetric)
            minimum_eigenvalue = float(np.min(eigenvalues))
            condition = float(np.linalg.cond(hessian))
        else:
            minimum_eigenvalue = float("nan")
            condition = float("inf")
        raw, projected, complementarity, active = diagnostics
        trace.append(
            NewtonIterationResult(
                index=index,
                parameters=values.copy(),
                objective=value,
                raw_gradient_inf_norm=raw,
                projected_gradient_inf_norm=projected,
                complementarity_inf_norm=complementarity,
                active_bounds=active,
                hessian_condition_number=condition,
                hessian_minimum_eigenvalue=minimum_eigenvalue,
                step_size=step_size,
                line_search_trials=line_search_trials,
                directional_derivative=directional_derivative,
                armijo_satisfied=armijo_satisfied,
            )
        )

    def finish(message: str, success: bool) -> ActiveSetNewtonResult:
        final = trace[-1]
        return ActiveSetNewtonResult(
            parameters=values.copy(),
            objective=final.objective,
            success=success,
            message=message,
            raw_gradient_inf_norm=final.raw_gradient_inf_norm,
            projected_gradient_inf_norm=final.projected_gradient_inf_norm,
            complementarity_inf_norm=final.complementarity_inf_norm,
            active_bounds=final.active_bounds,
            trace=tuple(trace),
        )

    for iteration in range(maxiter):
        value, gradient, hessian, diagnostics = evaluate(values)
        if not np.isfinite(value) or not np.isfinite(gradient).all() or not np.isfinite(hessian).all():
            append_snapshot(
                iteration,
                value,
                gradient,
                hessian,
                diagnostics,
                step_size=None,
                line_search_trials=0,
                directional_derivative=None,
                armijo_satisfied=False,
            )
            return finish("nonfinite objective or derivatives", False)
        if diagnostics[1] <= stop_kkt:
            append_snapshot(
                iteration,
                value,
                gradient,
                hessian,
                diagnostics,
                step_size=None,
                line_search_trials=0,
                directional_derivative=None,
                armijo_satisfied=None,
            )
            return finish("projected KKT target reached", True)

        active = (values <= lower + active_tolerance) & (gradient > 0.0)
        direction = np.zeros_like(values)
        while True:
            free = ~active
            if not np.any(free):
                append_snapshot(
                    iteration,
                    value,
                    gradient,
                    hessian,
                    diagnostics,
                    step_size=None,
                    line_search_trials=0,
                    directional_derivative=None,
                    armijo_satisfied=False,
                )
                return finish("active set contains every coordinate", False)
            try:
                direction.fill(0.0)
                direction[free] = np.linalg.solve(
                    hessian[np.ix_(free, free)],
                    -gradient[free],
                )
            except np.linalg.LinAlgError:
                append_snapshot(
                    iteration,
                    value,
                    gradient,
                    hessian,
                    diagnostics,
                    step_size=None,
                    line_search_trials=0,
                    directional_derivative=None,
                    armijo_satisfied=False,
                )
                return finish("singular free Hessian", False)
            newly_blocked = free & (values <= lower + active_tolerance) & (direction < 0.0)
            if not np.any(newly_blocked):
                break
            active |= newly_blocked

        directional = float(np.dot(gradient, direction))
        if not np.isfinite(direction).all() or not np.isfinite(directional) or directional >= 0.0:
            append_snapshot(
                iteration,
                value,
                gradient,
                hessian,
                diagnostics,
                step_size=None,
                line_search_trials=0,
                directional_derivative=directional,
                armijo_satisfied=False,
            )
            return finish("Newton direction is not strict descent", False)

        negative = direction < 0.0
        step = 1.0
        if np.any(negative):
            feasible = (values[negative] - lower[negative]) / -direction[negative]
            step = min(step, float(np.min(feasible)))
        if not np.isfinite(step) or step <= 0.0:
            append_snapshot(
                iteration,
                value,
                gradient,
                hessian,
                diagnostics,
                step_size=step,
                line_search_trials=0,
                directional_derivative=directional,
                armijo_satisfied=False,
            )
            return finish("Newton direction has no positive feasible step", False)

        accepted = False
        stagnated = False
        trials = 0
        candidate = values.copy()
        for trial in range(1, max_line_search_trials + 1):
            trials = trial
            candidate = np.maximum(values + step * direction, lower)
            if np.array_equal(candidate, values):
                stagnated = True
                break
            candidate_value, candidate_gradient, candidate_hessian, _ = evaluate(candidate)
            if (
                np.isfinite(candidate_value)
                and np.isfinite(candidate_gradient).all()
                and np.isfinite(candidate_hessian).all()
                and candidate_value <= value + armijo_constant * step * directional
            ):
                accepted = True
                break
            step *= backtrack_factor
        append_snapshot(
            iteration,
            value,
            gradient,
            hessian,
            diagnostics,
            step_size=step,
            line_search_trials=trials,
            directional_derivative=directional,
            armijo_satisfied=accepted,
        )
        if stagnated:
            return finish("Newton candidate is bit-identical at float precision", False)
        if not accepted:
            return finish("Armijo line search failed", False)
        values = candidate

    value, gradient, hessian, diagnostics = evaluate(values)
    append_snapshot(
        maxiter,
        value,
        gradient,
        hessian,
        diagnostics,
        step_size=None,
        line_search_trials=0,
        directional_derivative=None,
        armijo_satisfied=None,
    )
    return finish("maximum Newton iterations reached", diagnostics[1] <= stop_kkt)


def _run_optimizer(
    objective: Objective,
    initial: FloatArray,
    bounds: Sequence[Bound],
) -> tuple[FloatArray, float, bool, int, float, str]:
    result = minimize(
        objective,
        np.asarray(initial, dtype=np.float64),
        method="L-BFGS-B",
        jac=True,
        bounds=list(bounds),
        options={"maxiter": 300, "ftol": 1e-10, "gtol": 1e-6, "maxls": 40},
    )
    parameters = np.asarray(result.x, dtype=np.float64)
    value, gradient = objective(parameters)
    gradient_norm = float(np.max(np.abs(gradient)))
    return (
        parameters,
        float(value),
        bool(result.success),
        int(result.nit),
        gradient_norm,
        str(result.message),
    )


def fit_poisson_process(
    times: FloatArray,
    marks: IntArray,
    *,
    start: int,
    end: int,
    n_marks: int,
    n_trace_features: int,
    name: str = "poisson",
) -> PointProcessFit:
    """Fit constant marked-Poisson intensities analytically."""
    duration = float(times[end - 1] - times[start - 1])
    if duration <= 0.0:
        raise ValueError("Poisson training window has non-positive duration")
    counts = np.bincount(marks[start:end], minlength=n_marks).astype(np.float64)
    if np.any(counts <= 0.0):
        raise ValueError("every mark needs at least one training event")
    rates = counts / duration
    return PointProcessFit(
        name=name,
        base_kind="constant",
        base_coefficients=rates,
        excitation=np.zeros((n_marks, n_trace_features), dtype=np.float64),
        success=True,
        iterations=tuple(0 for _ in range(n_marks)),
        gradient_inf_norm=0.0,
        messages=tuple("analytic MLE" for _ in range(n_marks)),
    )


def fit_queue_reactive_process(
    times: FloatArray,
    marks: IntArray,
    queue_features: FloatArray,
    *,
    start: int,
    end: int,
    n_marks: int,
    n_trace_features: int,
    name: str = "queue_reactive",
) -> PointProcessFit:
    """Fit a piecewise-constant log-linear queue-reactive process."""
    intervals = times[start:end] - times[start - 1 : end - 1]
    queue = queue_features[start:end]
    window_marks = marks[start:end]
    duration = float(np.sum(intervals))
    coefficients = np.empty((n_marks, queue.shape[1]), dtype=np.float64)
    successes: list[bool] = []
    iterations: list[int] = []
    gradients: list[float] = []
    messages: list[str] = []
    normalizer = end - start
    for target in range(n_marks):
        target_queue = queue[window_marks == target]
        rate = target_queue.shape[0] / duration
        initial = np.zeros(queue.shape[1], dtype=np.float64)
        initial[0] = np.log(max(rate, 1e-12))
        objective = cast(
            Objective,
            lambda values, target_queue=target_queue: queue_objective_gradient(
                values, target_queue, queue, intervals, normalizer
            ),
        )
        fitted, _, success, n_iter, gradient, message = _run_optimizer(
            objective, initial, [(None, None)] * initial.size
        )
        coefficients[target] = fitted
        successes.append(success)
        iterations.append(n_iter)
        gradients.append(gradient)
        messages.append(message)
    return PointProcessFit(
        name=name,
        base_kind="loglinear",
        base_coefficients=coefficients,
        excitation=np.zeros((n_marks, n_trace_features), dtype=np.float64),
        success=all(successes),
        iterations=tuple(iterations),
        gradient_inf_norm=max(gradients),
        messages=tuple(messages),
    )


def fit_linear_hawkes_process(
    times: FloatArray,
    marks: IntArray,
    traces: FloatArray,
    interval_integrals: FloatArray,
    *,
    start: int,
    end: int,
    n_marks: int,
    n_scales: int,
    diagonal: bool,
    name: str,
) -> PointProcessFit:
    """Fit nonnegative linear Hawkes intensities with fixed exponential scales."""
    intervals, window_marks, window_traces, window_integrals, _ = _window_arrays(
        times, marks, traces, interval_integrals, start, end
    )
    duration = float(np.sum(intervals))
    integrated = np.sum(window_integrals, axis=0)
    n_features = traces.shape[1]
    excitation = np.zeros((n_marks, n_features), dtype=np.float64)
    rates: FloatArray = np.empty(n_marks, dtype=np.float64)
    successes: list[bool] = []
    iterations: list[int] = []
    gradients: list[float] = []
    messages: list[str] = []
    normalizer = end - start
    for target in range(n_marks):
        indices = np.arange(target * n_scales, (target + 1) * n_scales) if diagonal else np.arange(n_features)
        feature_scales = np.maximum(integrated[indices] / duration, 1e-8)
        target_features = window_traces[window_marks == target][:, indices] / feature_scales
        target_integrated = integrated[indices] / feature_scales
        rate = target_features.shape[0] / duration
        initial = np.concatenate(([max(rate, 1e-10)], np.zeros(indices.size)))
        objective = cast(
            Objective,
            lambda values, target_features=target_features, target_integrated=target_integrated: (
                hawkes_objective_gradient(
                    values,
                    target_features,
                    target_integrated,
                    duration,
                    normalizer,
                )
            ),
        )
        fitted, _, success, n_iter, gradient, message = _run_optimizer(
            objective,
            initial,
            [(1e-12, None), *([(0.0, None)] * indices.size)],
        )
        rates[target] = fitted[0]
        excitation[target, indices] = fitted[1:] / feature_scales
        successes.append(success)
        iterations.append(n_iter)
        gradients.append(gradient)
        messages.append(message)
    return PointProcessFit(
        name=name,
        base_kind="constant",
        base_coefficients=rates,
        excitation=excitation,
        success=all(successes),
        iterations=tuple(iterations),
        gradient_inf_norm=max(gradients),
        messages=tuple(messages),
    )


def fit_queue_hawkes_process(
    times: FloatArray,
    marks: IntArray,
    traces: FloatArray,
    interval_integrals: FloatArray,
    queue_features: FloatArray,
    queue_fit: PointProcessFit,
    hawkes_fit: PointProcessFit,
    *,
    start: int,
    end: int,
    n_marks: int,
    name: str,
) -> PointProcessFit:
    """Fit the additive queue-reactive plus full Hawkes process from two starts."""
    intervals, window_marks, window_traces, window_integrals, _ = _window_arrays(
        times, marks, traces, interval_integrals, start, end
    )
    queue = queue_features[start:end]
    integrated = np.sum(window_integrals, axis=0)
    duration = float(np.sum(intervals))
    trace_scales = np.maximum(integrated / duration, 1e-8)
    n_queue = queue.shape[1]
    n_trace = traces.shape[1]
    coefficients = np.empty((n_marks, n_queue), dtype=np.float64)
    excitation = np.empty((n_marks, n_trace), dtype=np.float64)
    successes: list[bool] = []
    iterations: list[int] = []
    gradients: list[float] = []
    messages: list[str] = []
    normalizer = end - start
    for target in range(n_marks):
        target_mask = window_marks == target
        target_queue = queue[target_mask]
        target_traces = window_traces[target_mask] / trace_scales
        objective = cast(
            Objective,
            lambda values, target_queue=target_queue, target_traces=target_traces: (
                queue_hawkes_objective_gradient(
                    values,
                    target_queue,
                    target_traces,
                    queue,
                    intervals,
                    integrated / trace_scales,
                    normalizer,
                )
            ),
        )
        queue_start = np.concatenate((queue_fit.base_coefficients[target], np.zeros(n_trace)))
        hawkes_theta = np.zeros(n_queue, dtype=np.float64)
        hawkes_theta[0] = np.log(max(float(hawkes_fit.base_coefficients[target]), 1e-12))
        hawkes_start = np.concatenate((hawkes_theta, hawkes_fit.excitation[target] * trace_scales))
        bounds: list[Bound] = [
            *([(None, None)] * n_queue),
            *([(0.0, None)] * n_trace),
        ]
        candidates = [
            _run_optimizer(objective, queue_start, bounds),
            _run_optimizer(objective, hawkes_start, bounds),
        ]
        selected = min(candidates, key=lambda result: result[1])
        fitted, _, success, n_iter, gradient, message = selected
        coefficients[target] = fitted[:n_queue]
        excitation[target] = fitted[n_queue:] / trace_scales
        successes.append(success)
        iterations.append(n_iter)
        gradients.append(gradient)
        messages.append(message)
    return PointProcessFit(
        name=name,
        base_kind="loglinear",
        base_coefficients=coefficients,
        excitation=excitation,
        success=all(successes),
        iterations=tuple(iterations),
        gradient_inf_norm=max(gradients),
        messages=tuple(messages),
    )


def point_process_log_likelihood(
    fit: PointProcessFit,
    times: FloatArray,
    marks: IntArray,
    traces: FloatArray,
    interval_integrals: FloatArray,
    queue_features: FloatArray,
    *,
    start: int,
    end: int,
) -> float:
    """Evaluate exact marked point-process log likelihood over an index window."""
    intervals, window_marks, window_traces, window_integrals, _ = _window_arrays(
        times, marks, traces, interval_integrals, start, end
    )
    queue = queue_features[start:end]
    if fit.base_kind == "constant":
        base = np.broadcast_to(
            fit.base_coefficients[None, :], (window_marks.size, fit.base_coefficients.size)
        )
        base_compensator = float(np.sum(fit.base_coefficients) * np.sum(intervals))
    else:
        base = np.exp(queue @ fit.base_coefficients.T)
        base_compensator = float(np.sum(base * intervals[:, None]))
    excitation = window_traces @ fit.excitation.T
    intensity = base + excitation
    actual = intensity[np.arange(window_marks.size), window_marks]
    if np.any(actual <= 0.0) or not np.isfinite(actual).all():
        raise RuntimeError("point-process intensity is invalid")
    integrated = np.sum(window_integrals, axis=0)
    excitation_compensator = float(np.sum(fit.excitation * integrated[None, :]))
    return float(np.sum(np.log(actual)) - base_compensator - excitation_compensator)


def time_rescaling_diagnostics(
    fit: PointProcessFit,
    times: FloatArray,
    marks: IntArray,
    traces: FloatArray,
    interval_integrals: FloatArray,
    queue_features: FloatArray,
    *,
    start: int,
    end: int,
) -> RescalingDiagnostics:
    """Summarize integrated total intensity between held-out events."""
    intervals, _, _, window_integrals, _ = _window_arrays(
        times, marks, traces, interval_integrals, start, end
    )
    queue = queue_features[start:end]
    if fit.base_kind == "constant":
        base_total = np.full(intervals.size, float(np.sum(fit.base_coefficients)), dtype=np.float64)
    else:
        base_total = np.sum(np.exp(queue @ fit.base_coefficients.T), axis=1)
    excitation_weights = np.sum(fit.excitation, axis=0)
    residuals = base_total * intervals + window_integrals @ excitation_weights
    if np.any(residuals < 0.0) or not np.isfinite(residuals).all():
        raise RuntimeError("time-rescaling residual is invalid")
    if residuals.size < 3 or np.std(residuals[:-1]) == 0.0 or np.std(residuals[1:]) == 0.0:
        lag = 0.0
    else:
        lag = float(np.corrcoef(residuals[:-1], residuals[1:])[0, 1])
    test_result = cast(Any, kstest(residuals, "expon"))
    return RescalingDiagnostics(
        count=int(residuals.size),
        mean=float(np.mean(residuals)),
        variance=float(np.var(residuals)),
        ks_statistic=float(test_result.statistic),
        lag1_correlation=lag,
    )


def branching_spectral_radius(
    excitation: FloatArray,
    *,
    n_marks: int,
    n_scales: int,
) -> float:
    """Return the spectral radius of the integrated branching matrix."""
    values = np.asarray(excitation, dtype=np.float64)
    if values.shape != (n_marks, n_marks * n_scales):
        raise ValueError("excitation matrix has the wrong shape")
    branching = values.reshape(n_marks, n_marks, n_scales).sum(axis=2)
    return float(np.max(np.abs(np.linalg.eigvals(branching))))


def simulate_exponential_hawkes_cluster(
    immigrant_rates: Sequence[float],
    branching: FloatArray,
    beta: float,
    *,
    burn_start: float,
    end_time: float,
    generator: np.random.Generator,
) -> tuple[FloatArray, IntArray]:
    """Simulate a multivariate exponential Hawkes process by Poisson clusters."""
    rates = np.asarray(tuple(immigrant_rates), dtype=np.float64)
    matrix = np.asarray(branching, dtype=np.float64)
    n_marks = rates.size
    if rates.ndim != 1 or n_marks < 1 or np.any(rates <= 0.0):
        raise ValueError("immigrant rates must be positive")
    if matrix.shape != (n_marks, n_marks) or np.any(matrix < 0.0):
        raise ValueError("branching matrix is invalid")
    if beta <= 0.0 or burn_start >= 0.0 or end_time <= 0.0:
        raise ValueError("simulation time/decay parameters are invalid")
    if float(np.max(np.abs(np.linalg.eigvals(matrix)))) >= 1.0:
        raise ValueError("branching matrix is not stationary")
    heap: list[tuple[float, int, int]] = []
    serial = 0
    span = end_time - burn_start
    for mark, rate in enumerate(rates):
        count = int(generator.poisson(rate * span))
        for event_time in generator.uniform(burn_start, end_time, size=count):
            heapq.heappush(heap, (float(event_time), serial, mark))
            serial += 1
    retained_times: list[float] = []
    retained_marks: list[int] = []
    while heap:
        event_time, _, source = heapq.heappop(heap)
        if event_time >= 0.0:
            retained_times.append(event_time)
            retained_marks.append(source)
        for target in range(n_marks):
            count = int(generator.poisson(matrix[target, source]))
            if count == 0:
                continue
            child_times = event_time + generator.exponential(1.0 / beta, size=count)
            for child_time in child_times:
                if child_time <= end_time:
                    heapq.heappush(heap, (float(child_time), serial, target))
                    serial += 1
    return (
        np.asarray(retained_times, dtype=np.float64),
        np.asarray(retained_marks, dtype=np.int64),
    )
