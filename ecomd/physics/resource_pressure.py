from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


def _vector(values: Sequence[float] | FloatArray, *, name: str) -> FloatArray:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 1 or array.size == 0:
        raise ValueError(f"{name} must be a non-empty one-dimensional array")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain only finite values")
    return array


def _target(target_utilization: float) -> float:
    if not np.isfinite(target_utilization) or not 0.0 < target_utilization < 1.0:
        raise ValueError("target_utilization must lie strictly between zero and one")
    return float(target_utilization)


def utilization(
    borrowed_assets: Sequence[float] | FloatArray,
    supplied_assets: Sequence[float] | FloatArray,
) -> FloatArray:
    borrowed = _vector(borrowed_assets, name="borrowed_assets")
    supplied = _vector(supplied_assets, name="supplied_assets")
    if borrowed.shape != supplied.shape:
        raise ValueError("borrowed_assets and supplied_assets must have the same shape")
    if np.any(borrowed < 0.0):
        raise ValueError("borrowed_assets must be non-negative")
    if np.any(supplied <= 0.0):
        raise ValueError("supplied_assets must be positive")
    return borrowed / supplied


def control_pressure(
    borrowed_assets: Sequence[float] | FloatArray,
    supplied_assets: Sequence[float] | FloatArray,
    target_utilization: float,
) -> FloatArray:
    borrowed = _vector(borrowed_assets, name="borrowed_assets")
    supplied = _vector(supplied_assets, name="supplied_assets")
    if borrowed.shape != supplied.shape:
        raise ValueError("borrowed_assets and supplied_assets must have the same shape")
    if np.any(borrowed < 0.0) or np.any(supplied <= 0.0):
        raise ValueError("borrowed_assets must be non-negative and supplied_assets positive")
    return borrowed - _target(target_utilization) * supplied


def apply_allocation_flows(
    supplied_assets: Sequence[float] | FloatArray,
    flows: Sequence[Sequence[float]] | FloatArray,
) -> FloatArray:
    supplied = _vector(supplied_assets, name="supplied_assets")
    matrix = np.asarray(flows, dtype=np.float64)
    if matrix.shape != (supplied.size, supplied.size):
        raise ValueError("flows must be a square matrix matching supplied_assets")
    if not np.all(np.isfinite(matrix)) or np.any(matrix < 0.0):
        raise ValueError("flows must be finite and non-negative")
    if np.any(np.diag(matrix) != 0.0):
        raise ValueError("flows must have a zero diagonal")
    outflow = matrix.sum(axis=1)
    if np.any(outflow >= supplied):
        raise ValueError("each market must retain positive supplied assets")
    updated = supplied - outflow + matrix.sum(axis=0)
    if np.any(updated <= 0.0):
        raise ValueError("allocation produced non-positive supplied assets")
    return np.asarray(updated, dtype=np.float64)


def pressure_continuity_residual(
    borrowed_assets: Sequence[float] | FloatArray,
    supplied_assets: Sequence[float] | FloatArray,
    flows: Sequence[Sequence[float]] | FloatArray,
    target_utilization: float,
) -> FloatArray:
    supplied = _vector(supplied_assets, name="supplied_assets")
    matrix = np.asarray(flows, dtype=np.float64)
    updated = apply_allocation_flows(supplied, matrix)
    before = control_pressure(borrowed_assets, supplied, target_utilization)
    after = control_pressure(borrowed_assets, updated, target_utilization)
    predicted_change = _target(target_utilization) * (matrix.sum(axis=1) - matrix.sum(axis=0))
    return np.asarray(after - before - predicted_change, dtype=np.float64)


def equalized_supply(
    borrowed_assets: Sequence[float] | FloatArray,
    total_supplied_assets: float,
) -> FloatArray:
    borrowed = _vector(borrowed_assets, name="borrowed_assets")
    if np.any(borrowed <= 0.0):
        raise ValueError("borrowed_assets must be positive for exact utilization equalization")
    if not np.isfinite(total_supplied_assets) or total_supplied_assets <= 0.0:
        raise ValueError("total_supplied_assets must be positive and finite")
    total_borrowed = float(borrowed.sum())
    aggregate_utilization = total_borrowed / float(total_supplied_assets)
    if not 0.0 < aggregate_utilization <= 1.0:
        raise ValueError("aggregate utilization must lie in (0, 1]")
    return borrowed / aggregate_utilization


def utilization_minimax_lower_bound(
    borrowed_assets: Sequence[float] | FloatArray,
    supplied_assets: Sequence[float] | FloatArray,
    target_utilization: float,
) -> float:
    borrowed = _vector(borrowed_assets, name="borrowed_assets")
    supplied = _vector(supplied_assets, name="supplied_assets")
    if borrowed.shape != supplied.shape:
        raise ValueError("borrowed_assets and supplied_assets must have the same shape")
    if np.any(borrowed < 0.0) or np.any(supplied <= 0.0):
        raise ValueError("borrowed_assets must be non-negative and supplied_assets positive")
    aggregate_utilization = float(borrowed.sum() / supplied.sum())
    return abs(aggregate_utilization - _target(target_utilization))


def morpho_normalized_error(
    utilizations: Sequence[float] | FloatArray,
    target_utilization: float,
) -> FloatArray:
    values = _vector(utilizations, name="utilizations")
    target = _target(target_utilization)
    if np.any(values < 0.0) or np.any(values > 1.0):
        raise ValueError("utilizations must lie in [0, 1]")
    denominators = np.where(values > target, 1.0 - target, target)
    return (values - target) / denominators


def advance_log_rate_at_target(
    log_rate_at_target: Sequence[float] | FloatArray,
    utilizations: Sequence[float] | FloatArray,
    *,
    target_utilization: float,
    adjustment_speed_per_second: float,
    elapsed_seconds: float,
) -> FloatArray:
    log_rates = _vector(log_rate_at_target, name="log_rate_at_target")
    errors = morpho_normalized_error(utilizations, target_utilization)
    if log_rates.shape != errors.shape:
        raise ValueError("log_rate_at_target and utilizations must have the same shape")
    if not np.isfinite(adjustment_speed_per_second) or adjustment_speed_per_second < 0.0:
        raise ValueError("adjustment_speed_per_second must be finite and non-negative")
    if not np.isfinite(elapsed_seconds) or elapsed_seconds < 0.0:
        raise ValueError("elapsed_seconds must be finite and non-negative")
    return log_rates + adjustment_speed_per_second * elapsed_seconds * errors
