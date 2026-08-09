"""Known-baseline audit for discrete-event invariant gradients."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
Z90 = 1.6448536269514722


def _summary(samples: np.ndarray, truth: float, steps: float) -> dict[str, float]:
    if samples.ndim != 2:
        raise ValueError(f"samples must be (batches, replicates), got {samples.shape}")
    batch_means = samples.mean(axis=1)
    batch_se = samples.std(axis=1, ddof=1) / np.sqrt(samples.shape[1])
    covered = np.abs(batch_means - truth) <= Z90 * batch_se
    mean = float(samples.mean())
    return {
        "mean": mean,
        "truth": truth,
        "bias": mean - truth,
        "relative_bias": (mean - truth) / abs(truth),
        "batch_mean_rmse": float(np.sqrt(np.mean((batch_means - truth) ** 2))),
        "coverage_90": float(covered.mean()),
        "batch_sign_accuracy": float(np.mean(np.sign(batch_means) == np.sign(truth))),
        "replicate_sd": float(samples.std(ddof=1)),
        "mean_simulator_steps": steps,
    }


def _next_two_state(
    state: np.ndarray,
    uniforms: np.ndarray,
    alpha: float,
    beta: float,
) -> tuple[np.ndarray, np.ndarray]:
    from_zero = state == 0
    next_state = np.where(from_zero, uniforms < alpha, uniforms >= beta).astype(np.int8)
    score = np.zeros(state.shape, dtype=np.float64)
    score[from_zero & (next_state == 1)] = 1.0 / alpha
    score[from_zero & (next_state == 0)] = -1.0 / (1.0 - alpha)
    return next_state, score


def _two_state_lr(
    rng: np.random.Generator,
    shape: tuple[int, int],
    alpha: float,
    beta: float,
    steps: int,
    *,
    initial: np.ndarray | None = None,
    initial_score: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    state = np.zeros(shape, dtype=np.int8) if initial is None else initial.copy()
    score = np.zeros(shape, dtype=np.float64)
    if initial_score is not None:
        score += initial_score
    for _ in range(steps):
        state, increment = _next_two_state(state, rng.random(shape), alpha, beta)
        score += increment
    return state, score


def _two_state_burn(
    rng: np.random.Generator,
    shape: tuple[int, int],
    alpha: float,
    beta: float,
    steps: int,
) -> np.ndarray:
    state = np.zeros(shape, dtype=np.int8)
    for _ in range(steps):
        state, _ = _next_two_state(state, rng.random(shape), alpha, beta)
    return state


def _two_state_fd(
    rng: np.random.Generator,
    shape: tuple[int, int],
    alpha: float,
    beta: float,
    steps: int,
    delta: float,
) -> np.ndarray:
    minus = np.zeros(shape, dtype=np.int8)
    plus = np.zeros(shape, dtype=np.int8)
    for _ in range(steps):
        uniforms = rng.random(shape)
        minus, _ = _next_two_state(minus, uniforms, alpha - delta, beta)
        plus, _ = _next_two_state(plus, uniforms, alpha + delta, beta)
    return (plus.astype(np.float64) - minus.astype(np.float64)) / (2.0 * delta)


def _two_state_cell(
    alpha: float,
    beta: float,
    *,
    shape: tuple[int, int],
    short: int,
    long: int,
    seeds: list[np.random.SeedSequence],
) -> dict[str, Any]:
    pi_one = alpha / (alpha + beta)
    truth = beta / (alpha + beta) ** 2
    estimators: dict[str, tuple[np.ndarray, float]] = {}

    rng = np.random.default_rng(seeds[0])
    state, score = _two_state_lr(rng, shape, alpha, beta, short)
    estimators["fresh_short_lr"] = ((state - pi_one) * score, float(short))

    rng = np.random.default_rng(seeds[1])
    initial = _two_state_burn(rng, shape, alpha, beta, long)
    state, score = _two_state_lr(
        rng, shape, alpha, beta, short, initial=initial
    )
    estimators["persistent_detached_lr"] = (
        (state - pi_one) * score,
        float(long + short),
    )

    rng = np.random.default_rng(seeds[2])
    state, score = _two_state_lr(rng, shape, alpha, beta, long + short)
    estimators["full_long_lr"] = (
        (state - pi_one) * score,
        float(long + short),
    )

    rng = np.random.default_rng(seeds[3])
    initial = (rng.random(shape) < pi_one).astype(np.int8)
    dpi = truth
    initial_score = np.where(
        initial == 1,
        dpi / pi_one,
        -dpi / (1.0 - pi_one),
    )
    state, score = _two_state_lr(
        rng,
        shape,
        alpha,
        beta,
        short,
        initial=initial,
        initial_score=initial_score,
    )
    estimators["stationary_oracle_lr"] = (
        (state - pi_one) * score,
        float(short + 1),
    )

    rng = np.random.default_rng(seeds[4])
    estimators["finite_difference_crn"] = (
        _two_state_fd(rng, shape, alpha, beta, long + short, 1e-3),
        float(2 * (long + short)),
    )

    transition = np.array([[1.0 - alpha, alpha], [beta, 1.0 - beta]])
    _, eigenvectors = np.linalg.eig(transition.T)
    stationary = np.real(eigenvectors[:, np.argmin(np.abs(np.linalg.eigvals(transition.T) - 1.0))])
    stationary /= stationary.sum()
    return {
        "alpha": alpha,
        "beta": beta,
        "mixing_sum": alpha + beta,
        "stationary_occupancy": pi_one,
        "truth": truth,
        "numeric_stationary_occupancy": float(stationary[1]),
        "estimators": {
            name: _summary(samples, truth, cost)
            for name, (samples, cost) in estimators.items()
        },
    }


def _jump_step(
    rng: np.random.Generator,
    x: np.ndarray,
    *,
    a: float,
    sigma: float,
    rate: float,
    jump_scale: float,
) -> tuple[np.ndarray, np.ndarray]:
    counts = rng.poisson(rate, size=x.shape)
    innovation = sigma * rng.standard_normal(x.shape)
    jumps = np.sqrt(counts) * jump_scale * rng.standard_normal(x.shape)
    return a * x + innovation + jumps, counts


def _jump_lr(
    rng: np.random.Generator,
    shape: tuple[int, int],
    steps: int,
    *,
    a: float,
    sigma: float,
    rate: float,
    jump_scale: float,
    initial: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    x = np.zeros(shape) if initial is None else initial.copy()
    score = np.zeros(shape)
    for _ in range(steps):
        x, counts = _jump_step(
            rng,
            x,
            a=a,
            sigma=sigma,
            rate=rate,
            jump_scale=jump_scale,
        )
        score += counts / rate - 1.0
    return x, score


def _jump_burn(
    rng: np.random.Generator,
    shape: tuple[int, int],
    steps: int,
    *,
    a: float,
    sigma: float,
    rate: float,
    jump_scale: float,
) -> np.ndarray:
    x = np.zeros(shape)
    for _ in range(steps):
        x, _ = _jump_step(
            rng,
            x,
            a=a,
            sigma=sigma,
            rate=rate,
            jump_scale=jump_scale,
        )
    return x


def _jump_fd(
    rng: np.random.Generator,
    shape: tuple[int, int],
    steps: int,
    *,
    a: float,
    sigma: float,
    rate: float,
    jump_scale: float,
    delta: float,
) -> np.ndarray:
    minus = np.zeros(shape)
    plus = np.zeros(shape)
    for _ in range(steps):
        innovation = sigma * rng.standard_normal(shape)
        base_counts = rng.poisson(rate - delta, size=shape)
        extra_counts = rng.poisson(2.0 * delta, size=shape)
        base_jump = np.sqrt(base_counts) * jump_scale * rng.standard_normal(shape)
        extra_jump = np.sqrt(extra_counts) * jump_scale * rng.standard_normal(shape)
        minus = a * minus + innovation + base_jump
        plus = a * plus + innovation + base_jump + extra_jump
    return (np.square(plus) - np.square(minus)) / (2.0 * delta)


def _jump_cell(
    a: float,
    *,
    shape: tuple[int, int],
    short: int,
    long: int,
    sigma: float,
    rate: float,
    jump_scale: float,
    seeds: list[np.random.SeedSequence],
) -> dict[str, Any]:
    truth = jump_scale**2 / (1.0 - a**2)
    stationary_second = (sigma**2 + rate * jump_scale**2) / (1.0 - a**2)
    estimators: dict[str, tuple[np.ndarray, float]] = {}

    rng = np.random.default_rng(seeds[0])
    x, score = _jump_lr(
        rng,
        shape,
        short,
        a=a,
        sigma=sigma,
        rate=rate,
        jump_scale=jump_scale,
    )
    estimators["fresh_short_lr"] = (
        (np.square(x) - stationary_second) * score,
        float(short),
    )

    rng = np.random.default_rng(seeds[1])
    initial = _jump_burn(
        rng,
        shape,
        long,
        a=a,
        sigma=sigma,
        rate=rate,
        jump_scale=jump_scale,
    )
    x, score = _jump_lr(
        rng,
        shape,
        short,
        a=a,
        sigma=sigma,
        rate=rate,
        jump_scale=jump_scale,
        initial=initial,
    )
    estimators["persistent_detached_lr"] = (
        (np.square(x) - stationary_second) * score,
        float(long + short),
    )

    rng = np.random.default_rng(seeds[2])
    x, score = _jump_lr(
        rng,
        shape,
        long + short,
        a=a,
        sigma=sigma,
        rate=rate,
        jump_scale=jump_scale,
    )
    estimators["full_long_lr"] = (
        (np.square(x) - stationary_second) * score,
        float(long + short),
    )

    rng = np.random.default_rng(seeds[3])
    estimators["finite_difference_coupled"] = (
        _jump_fd(
            rng,
            shape,
            long + short,
            a=a,
            sigma=sigma,
            rate=rate,
            jump_scale=jump_scale,
            delta=0.05,
        ),
        float(2 * (long + short)),
    )

    estimators["naive_pathwise_rate"] = (np.zeros(shape), float(short))
    return {
        "a": a,
        "sigma": sigma,
        "rate": rate,
        "jump_scale": jump_scale,
        "stationary_second_moment": stationary_second,
        "truth": truth,
        "estimators": {
            name: _summary(samples, truth, cost)
            for name, (samples, cost) in estimators.items()
        },
    }


def _torch_forward_parity(seed: int) -> dict[str, Any]:
    def rollout(create_graph: bool) -> tuple[torch.Tensor, torch.Tensor, bool]:
        generator = torch.Generator(device="cpu")
        generator.manual_seed(seed)
        a = torch.tensor(0.8, dtype=torch.float64, requires_grad=True)
        x = torch.zeros(512, dtype=torch.float64)
        for _ in range(64):
            counts = torch.poisson(
                torch.full_like(x, 1.5), generator=generator
            )
            eps = torch.randn(x.shape, dtype=x.dtype, generator=generator)
            jump_z = torch.randn(x.shape, dtype=x.dtype, generator=generator)
            x = a * x + 0.2 * eps + torch.sqrt(counts) * 0.35 * jump_z
        (gradient,) = torch.autograd.grad(
            x.square().mean(), a, create_graph=create_graph
        )
        return x.detach(), generator.get_state().clone(), bool(torch.isfinite(gradient))

    inference_x, inference_rng, inference_gradient = rollout(False)
    training_x, training_rng, training_gradient = rollout(True)
    return {
        "trajectory_exact": bool(torch.equal(inference_x, training_x)),
        "rng_state_exact": bool(torch.equal(inference_rng, training_rng)),
        "finite_gradient_both_modes": inference_gradient and training_gradient,
        "max_abs_difference": float((inference_x - training_x).abs().max()),
    }


def _numeric_formula_checks() -> dict[str, float]:
    delta = 1e-6
    alpha = 0.08
    beta = 0.12
    numeric_two = (
        (alpha + delta) / (alpha + delta + beta)
        - (alpha - delta) / (alpha - delta + beta)
    ) / (2.0 * delta)
    exact_two = beta / (alpha + beta) ** 2
    a = 0.8
    sigma = 0.2
    rate = 1.5
    jump_scale = 0.35

    def stationary_second(local_rate: float) -> float:
        return (sigma**2 + local_rate * jump_scale**2) / (1.0 - a**2)

    numeric_jump = (
        stationary_second(rate + delta) - stationary_second(rate - delta)
    ) / (2.0 * delta)
    exact_jump = jump_scale**2 / (1.0 - a**2)
    return {
        "two_state_relative_error": abs(numeric_two - exact_two) / exact_two,
        "jump_relative_error": abs(numeric_jump - exact_jump) / exact_jump,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--batches", type=int, default=64)
    parser.add_argument("--replicates", type=int, default=512)
    parser.add_argument("--short-horizon", type=int, default=24)
    parser.add_argument("--long-horizon", type=int, default=2_048)
    parser.add_argument("--seed", type=int, default=131_202_608)
    args = parser.parse_args()
    shape = (args.batches, args.replicates)
    root_seed = np.random.SeedSequence(args.seed)
    children = iter(root_seed.spawn(3 * 5 + 3 * 4))
    started = time.perf_counter()

    two_state: dict[str, Any] = {}
    for mixing_sum in (0.8, 0.2, 0.04):
        alpha = 0.4 * mixing_sum
        beta = 0.6 * mixing_sum
        two_state[str(mixing_sum)] = _two_state_cell(
            alpha,
            beta,
            shape=shape,
            short=args.short_horizon,
            long=args.long_horizon,
            seeds=[next(children) for _ in range(5)],
        )

    jump_ou: dict[str, Any] = {}
    for a in (0.2, 0.8, 0.97):
        jump_ou[str(a)] = _jump_cell(
            a,
            shape=shape,
            short=args.short_horizon,
            long=args.long_horizon,
            sigma=0.2,
            rate=1.5,
            jump_scale=0.35,
            seeds=[next(children) for _ in range(4)],
        )

    formula_checks = _numeric_formula_checks()
    parity = _torch_forward_parity(args.seed + 1)
    oracle_pass = all(
        abs(cell["estimators"]["stationary_oracle_lr"]["relative_bias"]) < 0.10
        or cell["estimators"]["stationary_oracle_lr"]["coverage_90"] >= 0.85
        for cell in two_state.values()
    )
    jump_regime_pass: dict[str, bool] = {}
    for regime in ("0.8", "0.97"):
        estimates = jump_ou[regime]["estimators"]
        jump_regime_pass[regime] = any(
            abs(estimates[name]["relative_bias"]) < 0.10
            or estimates[name]["coverage_90"] >= 0.85
            for name in ("full_long_lr", "finite_difference_coupled")
        )
    hard_gates = {
        "formula_checks_below_1e-7": max(formula_checks.values()) < 1e-7,
        "cpu_forward_trajectory_exact": parity["trajectory_exact"],
        "cpu_forward_rng_exact": parity["rng_state_exact"],
        "two_state_stationary_oracle_valid": oracle_pass,
        "jump_medium_established_baseline_valid": jump_regime_pass["0.8"],
        "jump_slow_established_baseline_valid": jump_regime_pass["0.97"],
        "naive_jump_pathwise_labelled_invalid": True,
    }
    payload = {
        "experiment": "131_event_gradient_toys",
        "status": "known_baseline_audit_not_new_method",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "platform": platform.platform(),
        "numpy_version": np.__version__,
        "torch_version": torch.__version__,
        "arguments": vars(args) | {"out": str(args.out)},
        "formula_checks": formula_checks,
        "forward_parity": parity,
        "two_state": two_state,
        "jump_ou": jump_ou,
        "hard_gates": hard_gates,
        "all_hard_gates_pass": all(hard_gates.values()),
        "wall_seconds": time.perf_counter() - started,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    compact: dict[str, Any] = {
        "all_hard_gates_pass": payload["all_hard_gates_pass"],
        "hard_gates": hard_gates,
        "two_state": {
            regime: {
                name: {
                    "rel_bias": round(values["relative_bias"], 4),
                    "coverage": round(values["coverage_90"], 3),
                }
                for name, values in cell["estimators"].items()
            }
            for regime, cell in two_state.items()
        },
        "jump_ou": {
            regime: {
                name: {
                    "rel_bias": round(values["relative_bias"], 4),
                    "coverage": round(values["coverage_90"], 3),
                }
                for name, values in cell["estimators"].items()
            }
            for regime, cell in jump_ou.items()
        },
    }
    print(json.dumps(compact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
