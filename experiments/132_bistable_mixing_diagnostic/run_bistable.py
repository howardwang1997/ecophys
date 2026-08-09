"""Fail-visible mixing diagnostic for a bistable Langevin toy system."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import time
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]


def _reference(temperature: float, theta: float) -> dict[str, float]:
    grid = np.linspace(-4.0, 4.0, 200_001, dtype=np.float64)
    potential = 0.25 * grid**4 - 0.5 * grid**2 - theta * grid
    log_weight = -potential / temperature
    weight = np.exp(log_weight - log_weight.max())
    normalizer = float(np.trapezoid(weight, grid))
    density = weight / normalizer
    observable = np.tanh(3.0 * grid)
    mean_observable = float(np.trapezoid(observable * density, grid))
    mean_x = float(np.trapezoid(grid * density, grid))
    mean_fx = float(np.trapezoid(observable * grid * density, grid))
    gradient = (mean_fx - mean_observable * mean_x) / temperature
    occupancy = float(np.trapezoid((grid > 0.0) * density, grid))
    left_edge = grid <= -3.9
    right_edge = grid >= 3.9
    boundary_mass = float(
        np.trapezoid(density[left_edge], grid[left_edge])
        + np.trapezoid(density[right_edge], grid[right_edge])
    )
    return {
        "mean_observable": mean_observable,
        "right_well_occupancy": occupancy,
        "gradient": gradient,
        "boundary_mass_abs_x_ge_3_9": boundary_mass,
    }


def _step(
    x: np.ndarray,
    tangent: np.ndarray,
    noise: np.ndarray,
    *,
    theta: float,
    temperature: float,
    dt: float,
) -> tuple[np.ndarray, np.ndarray]:
    tangent_next = (1.0 + dt * (-3.0 * x * x + 1.0)) * tangent + dt
    x_next = (
        x
        + dt * (-x * x * x + x + theta)
        + np.sqrt(2.0 * temperature * dt) * noise
    )
    return x_next, tangent_next


def _gradient_summary(batch_estimates: np.ndarray, truth: float) -> dict[str, float]:
    relative_errors = (batch_estimates - truth) / abs(truth)
    return {
        "mean": float(batch_estimates.mean()),
        "truth": truth,
        "relative_bias": float(relative_errors.mean()),
        "batch_rmse": float(np.sqrt(np.mean((batch_estimates - truth) ** 2))),
        "batch_sd": float(batch_estimates.std(ddof=1)),
        "sign_accuracy": float(np.mean(np.sign(batch_estimates) == np.sign(truth))),
        "median_absolute_relative_error": float(np.median(np.abs(relative_errors))),
    }


def _short_gradient(
    rng: np.random.Generator,
    shape: tuple[int, int],
    *,
    theta: float,
    temperature: float,
    dt: float,
    horizon: int,
    burn: int,
    persistent: bool,
) -> np.ndarray:
    if persistent:
        initial_group = np.arange(shape[1]) >= shape[1] // 2
        x = np.broadcast_to(np.where(initial_group, 1.0, -1.0), shape).copy()
        tangent = np.zeros(shape)
        for _ in range(burn):
            x, tangent = _step(
                x,
                tangent,
                rng.standard_normal(shape),
                theta=theta,
                temperature=temperature,
                dt=dt,
            )
        tangent.fill(0.0)
    else:
        x = np.zeros(shape)
        tangent = np.zeros(shape)
    for _ in range(horizon):
        x, tangent = _step(
            x,
            tangent,
            rng.standard_normal(shape),
            theta=theta,
            temperature=temperature,
            dt=dt,
        )
    observable = np.tanh(3.0 * x)
    gradient = 3.0 * (1.0 - observable * observable) * tangent
    return gradient.mean(axis=1)


def _full_run(
    rng: np.random.Generator,
    shape: tuple[int, int],
    *,
    theta: float,
    temperature: float,
    dt: float,
    steps: int,
    burn: int,
    stride: int,
) -> dict[str, Any]:
    initial_group = np.arange(shape[1]) >= shape[1] // 2
    x = np.broadcast_to(np.where(initial_group, 1.0, -1.0), shape).copy()
    tangent = np.zeros(shape)
    modes: list[np.ndarray] = []
    gradient_sum = np.zeros(shape)
    n_samples = 0
    for step in range(steps):
        x, tangent = _step(
            x,
            tangent,
            rng.standard_normal(shape),
            theta=theta,
            temperature=temperature,
            dt=dt,
        )
        if not np.isfinite(x).all() or not np.isfinite(tangent).all():
            raise FloatingPointError(f"non-finite bistable state at step {step + 1}")
        if step + 1 > burn and (step + 1 - burn) % stride == 0:
            observable = np.tanh(3.0 * x)
            gradient_sum += 3.0 * (1.0 - observable * observable) * tangent
            modes.append(x > 0.0)
            n_samples += 1
    if n_samples < 4:
        raise ValueError("not enough retained samples for split diagnostics")

    mode = np.stack(modes, axis=0)
    left_occupancy = mode[:, :, ~initial_group].mean(axis=(0, 2))
    right_occupancy = mode[:, :, initial_group].mean(axis=(0, 2))
    group_discrepancy = np.abs(left_occupancy - right_occupancy)
    half = n_samples // 2
    first_occupancy = mode[:half].mean(axis=(0, 2))
    second_occupancy = mode[half:].mean(axis=(0, 2))
    half_discrepancy = np.abs(first_occupancy - second_occupancy)
    switches = np.count_nonzero(mode[1:] != mode[:-1], axis=(0, 2))

    mode_float = mode.astype(np.float64)
    batch_mean = mode_float.mean(axis=(0, 2))
    centered_now = mode_float[1:] - batch_mean[None, :, None]
    centered_lag = mode_float[:-1] - batch_mean[None, :, None]
    covariance = np.mean(centered_now * centered_lag, axis=(0, 2))
    variance = np.mean(
        (mode_float - batch_mean[None, :, None]) ** 2,
        axis=(0, 2),
    )
    rho = np.zeros(shape[0])
    nonconstant = variance > 1e-12
    rho[nonconstant] = np.clip(
        covariance[nonconstant] / variance[nonconstant], -0.99, 0.999
    )
    raw_observations = n_samples * shape[1]
    ess = np.zeros(shape[0])
    ess[nonconstant] = raw_observations * (
        (1.0 - rho[nonconstant]) / (1.0 + rho[nonconstant])
    )
    resolved = (
        (group_discrepancy <= 0.10)
        & (half_discrepancy <= 0.10)
        & (switches >= 64)
        & (ess >= 128.0)
    )
    return {
        "batch_gradient": (gradient_sum / n_samples).mean(axis=1),
        "resolved": resolved,
        "group_occupancy_difference": group_discrepancy,
        "half_occupancy_difference": half_discrepancy,
        "switches": switches,
        "mode_ess": ess,
        "retained_samples_per_chain": n_samples,
    }


def _diagnostic_summary(
    full: dict[str, Any],
    truth: float,
) -> dict[str, Any]:
    estimates = full["batch_gradient"]
    resolved = full["resolved"]
    accurate = (
        (np.sign(estimates) == np.sign(truth))
        & (np.abs(estimates - truth) / abs(truth) <= 0.25)
    )
    false_safe = resolved & ~accurate

    def stats(values: np.ndarray) -> dict[str, float]:
        return {
            "min": float(np.min(values)),
            "median": float(np.median(values)),
            "max": float(np.max(values)),
        }

    resolved_errors = np.abs(estimates[resolved] - truth) / abs(truth)
    return {
        "resolved_rate": float(resolved.mean()),
        "accurate_rate": float(accurate.mean()),
        "false_safe_rate": float(false_safe.mean()),
        "resolved_median_absolute_relative_error": (
            float(np.median(resolved_errors)) if resolved_errors.size else None
        ),
        "group_occupancy_difference": stats(full["group_occupancy_difference"]),
        "half_occupancy_difference": stats(full["half_occupancy_difference"]),
        "total_switches": stats(full["switches"]),
        "mode_ess": stats(full["mode_ess"]),
        "retained_samples_per_chain": full["retained_samples_per_chain"],
    }


def _temperature_cell(
    temperature: float,
    *,
    shape: tuple[int, int],
    theta: float,
    dt: float,
    steps: int,
    burn: int,
    stride: int,
    short: int,
    persistent_burn: int,
    seeds: list[np.random.SeedSequence],
) -> dict[str, Any]:
    reference = _reference(temperature, theta)
    full = _full_run(
        np.random.default_rng(seeds[0]),
        shape,
        theta=theta,
        temperature=temperature,
        dt=dt,
        steps=steps,
        burn=burn,
        stride=stride,
    )
    fresh = _short_gradient(
        np.random.default_rng(seeds[1]),
        shape,
        theta=theta,
        temperature=temperature,
        dt=dt,
        horizon=short,
        burn=0,
        persistent=False,
    )
    persistent = _short_gradient(
        np.random.default_rng(seeds[2]),
        shape,
        theta=theta,
        temperature=temperature,
        dt=dt,
        horizon=short,
        burn=persistent_burn,
        persistent=True,
    )
    truth = reference["gradient"]
    return {
        "temperature": temperature,
        "reference": reference,
        "gradients": {
            "fresh_short": _gradient_summary(fresh, truth),
            "persistent_detached": _gradient_summary(persistent, truth),
            "full_long": _gradient_summary(full["batch_gradient"], truth),
        },
        "diagnostic": _diagnostic_summary(full, truth),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--batches", type=int, default=64)
    parser.add_argument("--chains", type=int, default=64)
    parser.add_argument("--steps", type=int, default=4_096)
    parser.add_argument("--burn", type=int, default=1_024)
    parser.add_argument("--stride", type=int, default=8)
    parser.add_argument("--short-horizon", type=int, default=24)
    parser.add_argument("--persistent-burn", type=int, default=2_048)
    parser.add_argument("--theta", type=float, default=0.05)
    parser.add_argument("--dt", type=float, default=0.005)
    parser.add_argument("--seed", type=int, default=132_202_608)
    args = parser.parse_args()
    if args.chains % 2:
        raise ValueError("chains must be even for balanced initial wells")
    if args.burn >= args.steps:
        raise ValueError("burn must be smaller than steps")

    shape = (args.batches, args.chains)
    root_seed = np.random.SeedSequence(args.seed)
    children = iter(root_seed.spawn(9))
    started = time.perf_counter()
    cells: dict[str, Any] = {}
    for label, temperature in (("easy", 0.50), ("medium", 0.15), ("hard", 0.04)):
        cells[label] = _temperature_cell(
            temperature,
            shape=shape,
            theta=args.theta,
            dt=args.dt,
            steps=args.steps,
            burn=args.burn,
            stride=args.stride,
            short=args.short_horizon,
            persistent_burn=args.persistent_burn,
            seeds=[next(children) for _ in range(3)],
        )

    easy = cells["easy"]["diagnostic"]
    hard = cells["hard"]["diagnostic"]
    boundary_max = max(
        cell["reference"]["boundary_mass_abs_x_ge_3_9"]
        for cell in cells.values()
    )
    hard_gates = {
        "grid_boundary_mass_below_1e-10": boundary_max < 1e-10,
        "hard_false_safe_rate_below_0_05": hard["false_safe_rate"] < 0.05,
        "easy_resolved_rate_at_least_0_80": easy["resolved_rate"] >= 0.80,
        "easy_resolved_median_relative_error_at_most_0_25": (
            easy["resolved_median_absolute_relative_error"] is not None
            and easy["resolved_median_absolute_relative_error"] <= 0.25
        ),
    }
    payload = {
        "experiment": "132_bistable_mixing_diagnostic",
        "status": "diagnostic_audit_not_new_estimator",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "platform": platform.platform(),
        "numpy_version": np.__version__,
        "arguments": vars(args) | {"out": str(args.out)},
        "cells": cells,
        "hard_gates": hard_gates,
        "all_hard_gates_pass": all(hard_gates.values()),
        "wall_seconds": time.perf_counter() - started,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    compact = {
        "all_hard_gates_pass": payload["all_hard_gates_pass"],
        "hard_gates": hard_gates,
        "cells": {
            label: {
                "truth": round(cell["reference"]["gradient"], 6),
                "gradient_relative_bias": {
                    name: round(values["relative_bias"], 4)
                    for name, values in cell["gradients"].items()
                },
                "diagnostic": cell["diagnostic"],
            }
            for label, cell in cells.items()
        },
    }
    print(json.dumps(compact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
