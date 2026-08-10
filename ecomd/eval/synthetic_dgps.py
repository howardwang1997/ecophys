"""Controlled synthetic processes for evaluator instrument calibration."""

from __future__ import annotations

from typing import Any, cast

import numpy as np
import numpy.typing as npt

from .evaluator_v2 import SeriesBlock

ArrayF = npt.NDArray[np.float64]


def simulate_dgp(
    name: str,
    *,
    length: int,
    burn_in: int,
    seed: int,
    registry: dict[str, dict[str, Any]],
) -> SeriesBlock:
    """Simulate one frozen DGP path and aligned synthetic volume."""
    if length <= 0 or burn_in < 0:
        raise ValueError("length must be positive and burn_in non-negative")
    if name not in registry:
        raise ValueError(f"unknown DGP: {name}")
    config = registry[name]
    rng = np.random.default_rng(seed)
    total = length + burn_in

    if name == "gaussian_iid":
        returns = rng.normal(size=total)
        volume = _independent_volume(total, rng)
    elif name in {"student_t3_iid", "student_t5_iid"}:
        df = float(config["degrees_of_freedom"])
        returns = _student_innovations(total, df, rng)
        volume = _independent_volume(total, rng)
    elif name == "negative_jump_iid":
        probability = float(config["jump_probability"])
        amplitude = float(config["jump_amplitude"])
        jump = rng.binomial(1, probability, size=total).astype(np.float64)
        returns = rng.normal(size=total) + amplitude * (jump - probability)
        returns /= np.sqrt(1.0 + amplitude**2 * probability * (1.0 - probability))
        volume = _independent_volume(total, rng)
    elif name in {"garch_gaussian", "garch_student_t5", "gjr_garch"}:
        innovations = _innovations_from_config(total, config, rng)
        returns = _garch_returns(innovations, config)
        volume = _independent_volume(total, rng)
    elif name == "multiscale_logvol":
        returns = _multiscale_logvol(total, config, rng)
        volume = _independent_volume(total, rng)
    elif name in {"garch_volume_coupled", "garch_volume_independent"}:
        base_name = str(config["returns"])
        base_config = registry[base_name]
        innovations = _innovations_from_config(total, base_config, rng)
        returns = _garch_returns(innovations, base_config)
        if name == "garch_volume_coupled":
            noise_scale = float(config["volume_noise_scale"])
            volume = np.abs(returns) + noise_scale * np.abs(rng.normal(size=total))
        else:
            volume = _independent_volume(total, rng)
    else:
        raise ValueError(f"DGP is declared but not implemented: {name}")

    selected_returns = np.asarray(returns[burn_in:], dtype=np.float64)
    selected_volume = np.asarray(volume[burn_in:], dtype=np.float64)
    if selected_returns.size != length or selected_volume.size != length:
        raise RuntimeError("DGP slicing produced the wrong path length")
    if not np.all(np.isfinite(selected_returns)) or not np.all(np.isfinite(selected_volume)):
        raise RuntimeError(f"{name} produced a non-finite path")
    if np.std(selected_returns, ddof=0) <= 0.0:
        raise RuntimeError(f"{name} produced degenerate returns")
    if np.ptp(selected_volume) <= 0.0:
        raise RuntimeError(f"{name} produced degenerate volume")
    return SeriesBlock(returns=selected_returns, volume=selected_volume)


def _innovations_from_config(
    size: int,
    config: dict[str, Any],
    rng: np.random.Generator,
) -> ArrayF:
    innovations = str(config["innovations"])
    if innovations == "gaussian":
        return np.asarray(rng.normal(size=size), dtype=np.float64)
    if innovations == "student_t":
        return _student_innovations(size, float(config["degrees_of_freedom"]), rng)
    raise ValueError(f"unknown innovations: {innovations}")


def _student_innovations(
    size: int,
    degrees_of_freedom: float,
    rng: np.random.Generator,
) -> ArrayF:
    if degrees_of_freedom <= 2.0:
        raise ValueError("unit-variance Student innovations require df > 2")
    scale = np.sqrt((degrees_of_freedom - 2.0) / degrees_of_freedom)
    return np.asarray(rng.standard_t(degrees_of_freedom, size=size) * scale, dtype=np.float64)


def _garch_returns(innovations: ArrayF, config: dict[str, Any]) -> ArrayF:
    omega = float(config["omega"])
    alpha = float(config["alpha"])
    beta = float(config["beta"])
    gamma = float(config.get("gamma_negative", 0.0))
    variance = float(config["initial_variance"])
    if omega <= 0.0 or alpha < 0.0 or beta < 0.0 or gamma < 0.0 or variance <= 0.0:
        raise ValueError("invalid GARCH parameters")
    if alpha + beta + 0.5 * gamma >= 1.0:
        raise ValueError("GARCH/GJR second-moment stationarity condition fails")
    returns = np.empty(innovations.size, dtype=np.float64)
    for index, innovation in enumerate(innovations):
        value = np.sqrt(variance) * float(innovation)
        returns[index] = value
        asymmetric = gamma * value**2 if value < 0.0 else 0.0
        variance = omega + alpha * value**2 + asymmetric + beta * variance
        if not np.isfinite(variance) or variance <= 0.0:
            raise RuntimeError("GARCH variance became invalid")
    return returns


def _multiscale_logvol(
    size: int,
    config: dict[str, Any],
    rng: np.random.Generator,
) -> ArrayF:
    coefficients = np.asarray(config["ar_coefficients"], dtype=np.float64)
    weights = np.asarray(config["component_weights"], dtype=np.float64)
    if coefficients.ndim != 1 or weights.shape != coefficients.shape:
        raise ValueError("multiscale coefficient/weight shape mismatch")
    if np.any(coefficients <= 0.0) or np.any(coefficients >= 1.0):
        raise ValueError("multiscale AR coefficients must be in (0, 1)")
    if not np.isclose(weights.sum(), 1.0):
        raise ValueError("multiscale component weights must sum to one")
    states = np.zeros(coefficients.size, dtype=np.float64)
    logvol = np.empty(size, dtype=np.float64)
    innovation_scale = np.sqrt(1.0 - coefficients**2)
    for index in range(size):
        states = coefficients * states + innovation_scale * rng.normal(
            size=coefficients.size
        )
        logvol[index] = float(np.dot(weights, states))
    scale = float(config["logvol_scale"])
    return np.asarray(np.exp(scale * logvol) * rng.normal(size=size), dtype=np.float64)


def _independent_volume(size: int, rng: np.random.Generator) -> ArrayF:
    return np.asarray(np.abs(rng.normal(size=size)), dtype=np.float64)


def dgp_registry(raw: object) -> dict[str, dict[str, Any]]:
    """Validate and type the YAML DGP registry."""
    if not isinstance(raw, dict) or not all(
        isinstance(name, str) and isinstance(config, dict)
        for name, config in raw.items()
    ):
        raise ValueError("DGP registry must map names to objects")
    return cast(dict[str, dict[str, Any]], raw)


__all__ = ["dgp_registry", "simulate_dgp"]
