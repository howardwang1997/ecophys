"""Analytic AR(1) invariant-gradient baseline audit."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import time
from collections.abc import Callable
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "experiments" / "129_invariant_gradient_toys" / "AR1_RESULTS.json"


def truth(a: float, sigma: float) -> tuple[float, float]:
    variance = sigma**2 / (1.0 - a**2)
    derivative = 2.0 * a * sigma**2 / (1.0 - a**2) ** 2
    return variance, derivative


def pathwise_final(
    noise: np.ndarray,
    a: float,
    sigma: float,
    *,
    x0: np.ndarray | None = None,
    tangent0: np.ndarray | None = None,
) -> np.ndarray:
    n_rep = noise.shape[0]
    x = np.zeros(n_rep) if x0 is None else x0.copy()
    tangent = np.zeros(n_rep) if tangent0 is None else tangent0.copy()
    for step in range(noise.shape[1]):
        tangent = x + a * tangent
        x = a * x + sigma * noise[:, step]
    return 2.0 * x * tangent


def fresh_short(rng: np.random.Generator, n: int, a: float, sigma: float, h: int) -> tuple[np.ndarray, float]:
    return pathwise_final(rng.standard_normal((n, h)), a, sigma), float(h)


def persistent_detached(
    rng: np.random.Generator, n: int, a: float, sigma: float, h: int, burn: int
) -> tuple[np.ndarray, float]:
    noise = rng.standard_normal((n, burn + h))
    x = np.zeros(n)
    for step in range(burn):
        x = a * x + sigma * noise[:, step]
    estimate = pathwise_final(noise[:, burn:], a, sigma, x0=x, tangent0=np.zeros(n))
    return estimate, float(burn + h)


def full_long(
    rng: np.random.Generator, n: int, a: float, sigma: float, h: int, burn: int
) -> tuple[np.ndarray, float]:
    noise = rng.standard_normal((n, burn + h))
    return pathwise_final(noise, a, sigma), float(burn + h)


def stationary_oracle(
    rng: np.random.Generator, n: int, a: float, sigma: float, h: int
) -> tuple[np.ndarray, float]:
    eps0 = rng.standard_normal(n)
    scale = sigma / np.sqrt(1.0 - a**2)
    dscale = sigma * a / (1.0 - a**2) ** 1.5
    x0 = scale * eps0
    tangent0 = dscale * eps0
    noise = rng.standard_normal((n, h))
    return pathwise_final(noise, a, sigma, x0=x0, tangent0=tangent0), float(h + 1)


def finite_difference_crn(
    rng: np.random.Generator,
    n: int,
    a: float,
    sigma: float,
    h: int,
    burn: int,
    delta: float,
) -> tuple[np.ndarray, float]:
    noise = rng.standard_normal((n, burn + h))

    def final_square(coef: float) -> np.ndarray:
        x = np.zeros(n)
        for step in range(noise.shape[1]):
            x = coef * x + sigma * noise[:, step]
        return x * x

    estimate = (final_square(a + delta) - final_square(a - delta)) / (2.0 * delta)
    return estimate, float(2 * (burn + h))


def _suffix_gradient(noise: np.ndarray, a: float, sigma: float, length: int) -> float:
    x = 0.0
    tangent = 0.0
    for eps in noise[-length:]:
        tangent = x + a * tangent
        x = a * x + sigma * eps
    return 2.0 * x * tangent


def rhee_glynn_linear(
    rng: np.random.Generator, n: int, a: float, sigma: float
) -> tuple[np.ndarray, float]:
    q = min(0.995, max(0.6, a * a + 0.02))
    levels = rng.geometric(1.0 - q, size=n) - 1
    estimates = np.empty(n)
    costs = np.empty(n)
    for rep, top in enumerate(levels):
        noise = rng.standard_normal(int(top) + 1)
        previous = _suffix_gradient(noise, a, sigma, 1)
        estimate = previous
        cost = 1
        for level in range(1, int(top) + 1):
            current = _suffix_gradient(noise, a, sigma, level + 1)
            estimate += (current - previous) / (q**level)
            previous = current
            cost += level + 1
        estimates[rep] = estimate
        costs[rep] = cost
    return estimates, float(costs.mean())


def summarize(samples: np.ndarray, exact: float, mean_steps: float) -> dict[str, float]:
    mean = float(samples.mean())
    bias = mean - exact
    sd = float(samples.std(ddof=1))
    n = len(samples)
    return {
        "mean": mean,
        "truth": exact,
        "bias": bias,
        "relative_bias": bias / abs(exact),
        "replicate_sd": sd,
        "standard_error": sd / np.sqrt(n),
        "rmse_of_mean": float(np.sqrt(bias * bias + sd * sd / n)),
        "sign_accuracy": float(np.mean(np.sign(samples) == np.sign(exact))),
        "mean_simulator_steps": mean_steps,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--replicates", type=int, default=2_000)
    parser.add_argument("--short-horizon", type=int, default=24)
    parser.add_argument("--long-horizon", type=int, default=2_048)
    parser.add_argument("--sigma", type=float, default=0.3)
    parser.add_argument("--seed", type=int, default=129_202_608)
    args = parser.parse_args()

    estimators: dict[str, Callable[..., tuple[np.ndarray, float]]] = {
        "fresh_short": lambda rng, n, a, s: fresh_short(rng, n, a, s, args.short_horizon),
        "persistent_detached": lambda rng, n, a, s: persistent_detached(
            rng, n, a, s, args.short_horizon, args.long_horizon
        ),
        "full_long": lambda rng, n, a, s: full_long(
            rng, n, a, s, args.short_horizon, args.long_horizon
        ),
        "stationary_oracle": lambda rng, n, a, s: stationary_oracle(
            rng, n, a, s, args.short_horizon
        ),
        "finite_difference_crn": lambda rng, n, a, s: finite_difference_crn(
            rng, n, a, s, args.short_horizon, args.long_horizon, 1e-4
        ),
        "rhee_glynn_linear": rhee_glynn_linear,
    }

    started = time.perf_counter()
    results: dict[str, dict[str, dict[str, float]]] = {}
    seed_sequence = np.random.SeedSequence(args.seed)
    children = iter(seed_sequence.spawn(3 * len(estimators)))
    for a in (0.2, 0.8, 0.97):
        _, exact = truth(a, args.sigma)
        regime: dict[str, dict[str, float]] = {}
        for name, estimator in estimators.items():
            rng = np.random.default_rng(next(children))
            samples, mean_steps = estimator(rng, args.replicates, a, args.sigma)
            regime[name] = summarize(samples, exact, mean_steps)
        results[str(a)] = regime

    payload = {
        "experiment": "129_invariant_gradient_toys",
        "status": "known_baseline_audit_not_new_method",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "platform": platform.platform(),
        "arguments": vars(args) | {"out": str(args.out)},
        "truth_formula": "2*a*sigma^2/(1-a^2)^2",
        "wall_seconds": time.perf_counter() - started,
        "results": results,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    compact = {
        a: {
            name: {
                "rel_bias": round(metrics["relative_bias"], 4),
                "rmse_mean": round(metrics["rmse_of_mean"], 4),
                "steps": round(metrics["mean_simulator_steps"], 1),
            }
            for name, metrics in regime.items()
        }
        for a, regime in results.items()
    }
    print(json.dumps({"out": str(args.out), "results": compact}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

