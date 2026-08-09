"""Run the preregistered latent-flow misspecification stress."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import time
from pathlib import Path
from typing import Any, TypeAlias, cast

import numpy as np
from numpy.typing import NDArray

from ecomd.observation.l2_emission import (
    fit_logistic_features,
    logistic_feature_log_likelihood,
    simulate_latent_ar1,
)

FloatArray: TypeAlias = NDArray[np.float64]
IntArray: TypeAlias = NDArray[np.int64]

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = Path(__file__).with_name("MISSPECIFICATION_RESULTS.json")
ROOT_SEED = 135_202_608
RHO_VALUES = (0.0, 0.8, 0.98)
TRUTH_FAMILIES = (
    "latent_current",
    "observation_only",
    "combined",
    "latent_lagged",
    "latent_even",
    "null",
)
N_STREAMS = 8
N_EVENTS = 30_000
TRAIN_FRACTION = 0.60
MODEL_NAMES = (
    "null",
    "latent_current",
    "observation_only",
    "combined",
    "latent_lagged_oracle",
    "latent_even_oracle",
)


def _git_value(*args: str) -> str:
    return subprocess.check_output(
        ("git", *args), cwd=ROOT, text=True, stderr=subprocess.DEVNULL
    ).strip()


def _generate_signed_flow(
    truth: str,
    latent: FloatArray,
    latent_lag: FloatArray,
    generator: np.random.Generator,
) -> tuple[IntArray, IntArray]:
    signed_flow = np.empty(latent.size, dtype=np.int64)
    observed_lag = np.empty(latent.size, dtype=np.int64)
    previous = int(generator.choice(np.asarray((-1, 1), dtype=np.int64)))
    for index in range(latent.size):
        observed_lag[index] = previous
        if truth == "latent_current":
            logit = 2.0 * 0.8 * latent[index]
        elif truth == "observation_only":
            logit = 2.0 * 0.8 * previous
        elif truth == "combined":
            logit = 2.0 * (0.6 * latent[index] + 0.6 * previous)
        elif truth == "latent_lagged":
            logit = 2.0 * 0.8 * latent_lag[index]
        elif truth == "latent_even":
            logit = 2.0 * 0.6 * (latent[index] * latent[index] - 1.0)
        elif truth == "null":
            logit = 0.0
        else:
            raise ValueError(f"unknown truth family: {truth}")
        probability = 1.0 / (1.0 + np.exp(-np.clip(logit, -40.0, 40.0)))
        previous = 1 if generator.random() < probability else -1
        signed_flow[index] = previous
    return signed_flow, observed_lag


def _features(
    latent: FloatArray,
    latent_lag: FloatArray,
    observed_lag: IntArray,
) -> dict[str, FloatArray]:
    empty = np.empty((latent.size, 0), dtype=np.float64)
    current = (2.0 * latent)[:, None]
    observed = (2.0 * observed_lag.astype(np.float64))[:, None]
    lagged = (2.0 * latent_lag)[:, None]
    even = (2.0 * (latent * latent - 1.0))[:, None]
    return {
        "null": empty,
        "latent_current": current,
        "observation_only": observed,
        "combined": np.column_stack((current, observed)),
        "latent_lagged_oracle": lagged,
        "latent_even_oracle": even,
    }


def _analyse_stream(
    truth: str,
    rho: float,
    seed: int,
) -> dict[str, Any]:
    generator = np.random.default_rng(seed)
    latent_path = simulate_latent_ar1(N_EVENTS + 1, rho, generator)
    latent_lag = latent_path[:-1]
    latent = latent_path[1:]
    signed_flow, observed_lag = _generate_signed_flow(
        truth, latent, latent_lag, generator
    )
    feature_sets = _features(latent, latent_lag, observed_lag)
    split = int(TRAIN_FRACTION * N_EVENTS)
    models: dict[str, Any] = {}
    for name in MODEL_NAMES:
        features = feature_sets[name]
        fit = fit_logistic_features(features[:split], signed_flow[:split])
        heldout_ll = logistic_feature_log_likelihood(
            fit.values, features[split:], signed_flow[split:]
        ) / (N_EVENTS - split)
        models[name] = {
            "coefficients": [float(value) for value in fit.values],
            "converged": fit.converged,
            "iterations": fit.iterations,
            "heldout_log_likelihood_nats_per_event": float(heldout_ll),
        }
    null_ll = float(models["null"]["heldout_log_likelihood_nats_per_event"])
    for model in models.values():
        model["heldout_gain_over_null_nats_per_event"] = float(
            model["heldout_log_likelihood_nats_per_event"] - null_ll
        )
    return {
        "truth": truth,
        "rho": rho,
        "seed": seed,
        "n_events": N_EVENTS,
        "n_train": split,
        "n_test": N_EVENTS - split,
        "models": models,
    }


def _median(values: list[float]) -> float:
    return float(np.median(np.asarray(values, dtype=np.float64)))


def _summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for truth in TRUTH_FAMILIES:
        for rho in RHO_VALUES:
            cell = [
                record
                for record in records
                if record["truth"] == truth and record["rho"] == rho
            ]
            model_summary: dict[str, Any] = {}
            for name in MODEL_NAMES:
                model_summary[name] = {
                    "median_coefficients": [
                        _median(
                            [
                                float(record["models"][name]["coefficients"][index])
                                for record in cell
                            ]
                        )
                        for index in range(len(cell[0]["models"][name]["coefficients"]))
                    ],
                    "median_heldout_gain_over_null_nats_per_event": _median(
                        [
                            float(
                                record["models"][name][
                                    "heldout_gain_over_null_nats_per_event"
                                ]
                            )
                            for record in cell
                        ]
                    ),
                }
            ll = {
                name: [
                    float(
                        record["models"][name][
                            "heldout_log_likelihood_nats_per_event"
                        ]
                    )
                    for record in cell
                ]
                for name in MODEL_NAMES
            }
            pairwise = {
                "latent_minus_observation": _median(
                    [a - b for a, b in zip(ll["latent_current"], ll["observation_only"], strict=True)]
                ),
                "observation_minus_latent": _median(
                    [a - b for a, b in zip(ll["observation_only"], ll["latent_current"], strict=True)]
                ),
                "combined_minus_latent": _median(
                    [a - b for a, b in zip(ll["combined"], ll["latent_current"], strict=True)]
                ),
                "combined_minus_observation": _median(
                    [a - b for a, b in zip(ll["combined"], ll["observation_only"], strict=True)]
                ),
                "lagged_minus_current": _median(
                    [a - b for a, b in zip(ll["latent_lagged_oracle"], ll["latent_current"], strict=True)]
                ),
                "even_minus_current": _median(
                    [a - b for a, b in zip(ll["latent_even_oracle"], ll["latent_current"], strict=True)]
                ),
            }
            positive_gains = [
                max(
                    0.0,
                    *(
                        float(record["models"][name]["heldout_gain_over_null_nats_per_event"])
                        for name in MODEL_NAMES
                        if name != "null"
                    ),
                )
                for record in cell
            ]
            summary[f"truth={truth},rho={rho:.2f}"] = {
                "models": model_summary,
                "pairwise_heldout_nats_per_event": pairwise,
                "median_largest_positive_gain_over_null": _median(positive_gains),
            }
    return summary


def _cell(summary: dict[str, Any], truth: str, rho: float) -> dict[str, Any]:
    return cast(dict[str, Any], summary[f"truth={truth},rho={rho:.2f}"])


def _relative_error(value: float, truth: float) -> float:
    return abs(value - truth) / abs(truth)


def _hard_gates(
    records: list[dict[str, Any]],
    summary: dict[str, Any],
) -> dict[str, bool]:
    exact_counts = all(
        record["n_events"] == N_EVENTS
        and record["n_train"] == int(TRAIN_FRACTION * N_EVENTS)
        and record["n_test"] == N_EVENTS - int(TRAIN_FRACTION * N_EVENTS)
        for record in records
    )
    all_converged = all(
        bool(model["converged"])
        for record in records
        for model in record["models"].values()
    )
    all_finite = all(
        np.isfinite(float(value))
        for record in records
        for model in record["models"].values()
        for value in (
            *model["coefficients"],
            model["heldout_log_likelihood_nats_per_event"],
            model["heldout_gain_over_null_nats_per_event"],
        )
    )

    latent_current = []
    observation_only = []
    combined = []
    lagged = []
    even = []
    null = []
    for rho in RHO_VALUES:
        current_cell = _cell(summary, "latent_current", rho)
        current_models = current_cell["models"]
        current_pairwise = current_cell["pairwise_heldout_nats_per_event"]
        latent_current.append(
            _relative_error(
                float(current_models["latent_current"]["median_coefficients"][1]),
                0.8,
            )
            <= 0.075
            and float(current_pairwise["latent_minus_observation"]) >= 0.03
            and float(current_pairwise["combined_minus_latent"]) <= 0.003
        )

        observed_cell = _cell(summary, "observation_only", rho)
        observed_models = observed_cell["models"]
        observed_pairwise = observed_cell["pairwise_heldout_nats_per_event"]
        observation_only.append(
            _relative_error(
                float(observed_models["observation_only"]["median_coefficients"][1]),
                0.8,
            )
            <= 0.075
            and float(observed_pairwise["observation_minus_latent"]) >= 0.08
            and abs(float(observed_models["combined"]["median_coefficients"][1])) <= 0.08
            and float(observed_pairwise["combined_minus_observation"]) <= 0.003
        )

        combined_cell = _cell(summary, "combined", rho)
        combined_models = combined_cell["models"]
        combined_pairwise = combined_cell["pairwise_heldout_nats_per_event"]
        combined.append(
            _relative_error(
                float(combined_models["combined"]["median_coefficients"][1]),
                0.6,
            )
            <= 0.10
            and _relative_error(
                float(combined_models["combined"]["median_coefficients"][2]),
                0.6,
            )
            <= 0.10
            and float(combined_pairwise["combined_minus_latent"]) >= 0.02
            and float(combined_pairwise["combined_minus_observation"]) >= 0.02
        )

        lagged_cell = _cell(summary, "latent_lagged", rho)
        lagged_models = lagged_cell["models"]
        lagged_pairwise = lagged_cell["pairwise_heldout_nats_per_event"]
        lagged.append(
            _relative_error(
                float(lagged_models["latent_lagged_oracle"]["median_coefficients"][1]),
                0.8,
            )
            <= 0.075
            and (
                rho == 0.98
                or float(lagged_pairwise["lagged_minus_current"]) >= 0.03
            )
        )

        even_cell = _cell(summary, "latent_even", rho)
        even_models = even_cell["models"]
        even_pairwise = even_cell["pairwise_heldout_nats_per_event"]
        even.append(
            _relative_error(
                float(even_models["latent_even_oracle"]["median_coefficients"][1]),
                0.6,
            )
            <= 0.10
            and float(even_pairwise["even_minus_current"]) >= 0.05
            and abs(float(even_models["latent_current"]["median_coefficients"][1])) <= 0.08
        )

        null_cell = _cell(summary, "null", rho)
        null_models = null_cell["models"]
        null.append(
            float(null_cell["median_largest_positive_gain_over_null"]) <= 0.001
            and all(
                all(abs(float(value)) <= 0.05 for value in model["median_coefficients"][1:])
                for name, model in null_models.items()
                if name != "null"
            )
        )
    return {
        "all_counts_exact": exact_counts,
        "all_fits_converged": all_converged,
        "all_values_finite": all_finite,
        "latent_current_truth": all(latent_current),
        "observation_only_truth": all(observation_only),
        "combined_truth": all(combined),
        "lagged_truth": all(lagged),
        "even_truth": all(even),
        "null_truth": all(null),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    started = time.perf_counter()
    seed_sequence = np.random.SeedSequence(ROOT_SEED)
    children = seed_sequence.spawn(len(TRUTH_FAMILIES) * len(RHO_VALUES) * N_STREAMS)
    records: list[dict[str, Any]] = []
    child_index = 0
    for truth in TRUTH_FAMILIES:
        for rho in RHO_VALUES:
            for _ in range(N_STREAMS):
                seed = int(children[child_index].generate_state(1, dtype=np.uint64)[0])
                child_index += 1
                records.append(_analyse_stream(truth, rho, seed))
    summary = _summarize(records)
    gates = _hard_gates(records, summary)
    payload = {
        "experiment": 135,
        "title": "latent-flow misspecification and observation-only stress",
        "protocol": {
            "root_seed": ROOT_SEED,
            "rho_values": list(RHO_VALUES),
            "truth_families": list(TRUTH_FAMILIES),
            "n_streams_per_cell": N_STREAMS,
            "n_events_per_stream": N_EVENTS,
            "train_fraction": TRAIN_FRACTION,
            "total_streams": len(records),
            "total_events": len(records) * N_EVENTS,
        },
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "git_sha": _git_value("rev-parse", "HEAD"),
            "git_dirty": bool(_git_value("status", "--porcelain")),
        },
        "cell_summary": summary,
        "hard_gates": gates,
        "all_hard_gates_pass": all(gates.values()),
        "elapsed_seconds": time.perf_counter() - started,
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: payload[key] for key in ("hard_gates", "all_hard_gates_pass", "elapsed_seconds")}, indent=2))


if __name__ == "__main__":
    main()
