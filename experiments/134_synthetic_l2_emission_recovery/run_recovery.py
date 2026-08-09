"""Run the preregistered synthetic L2 emission and recovery audit."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import time
from pathlib import Path
from typing import Any

import numpy as np

from ecomd.observation.l2_emission import (
    AggregateL2EmissionConfig,
    SyntheticL2Stream,
    bernoulli_log_likelihood,
    emit_aggregate_l2,
    fit_flow_slope,
    fit_level_decay,
    fit_size_model,
    poisson_log_likelihood_without_constant,
    reconstruct_aggregate_book,
    simulate_latent_ar1,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = Path(__file__).with_name("SYNTHETIC_L2_RESULTS.json")
ROOT_SEED = 134_202_608
RHO_VALUES = (0.0, 0.8, 0.98)
BETA_VALUES = (0.0, 0.5, 1.0)
N_STREAMS = 8
N_EVENTS = 30_000
TRAIN_FRACTION = 0.60


def _extract_visible(
    stream: SyntheticL2Stream,
    config: AggregateL2EmissionConfig,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    visible = stream.event_type != 5
    action = np.where(stream.event_type == 1, 1, -1)
    signed_flow = stream.direction * action
    level = np.where(
        stream.direction == 1,
        config.best_bid - stream.price,
        stream.price - config.best_ask,
    ).astype(np.int64)
    if np.any((level < 0) | (level >= config.n_levels)):
        raise RuntimeError("emitted message has an invalid displayed level")
    return visible, action, signed_flow, level


def _previous_snapshots(stream: SyntheticL2Stream) -> np.ndarray:
    previous = np.empty_like(stream.snapshots)
    previous[0] = stream.initial_book
    previous[1:] = stream.snapshots[:-1]
    return previous


def _analyse_stream(
    *,
    rho: float,
    beta_true: float,
    seed: int,
    config: AggregateL2EmissionConfig,
) -> dict[str, Any]:
    generator = np.random.default_rng(seed)
    latent = simulate_latent_ar1(N_EVENTS, rho, generator)
    stream = emit_aggregate_l2(latent, beta_true, config, generator)
    reconstructed = reconstruct_aggregate_book(stream)
    visible, _, signed_flow, level = _extract_visible(stream, config)
    split = int(TRAIN_FRACTION * N_EVENTS)
    train = np.arange(N_EVENTS) < split
    test = ~train
    visible_train = visible & train
    visible_test = visible & test

    beta_fit = fit_flow_slope(latent[visible_train], signed_flow[visible_train])
    beta_estimate = float(beta_fit.values[0])
    q_model_ll = bernoulli_log_likelihood(
        beta_estimate,
        latent[visible_test],
        signed_flow[visible_test],
    )
    q_null_ll = bernoulli_log_likelihood(
        0.0,
        latent[visible_test],
        signed_flow[visible_test],
    )
    q_gain = (q_model_ll - q_null_ll) / int(np.count_nonzero(visible_test))

    hidden_train = stream.event_type[train] == 5
    p_hidden = float(hidden_train.mean())
    train_visible_events = stream.event_type[visible_train]
    p_add = float(np.mean(train_visible_events == 1))
    train_removals = train_visible_events[train_visible_events != 1]
    removal_probabilities = {
        str(event_type): float(np.mean(train_removals == event_type))
        for event_type in (2, 3, 4)
    }
    eta_fit = fit_level_decay(level[visible_train], config.n_levels)

    size_fit = fit_size_model(latent[train], stream.size[train])
    log_mu_estimate, gamma_estimate = (float(value) for value in size_fit.values)
    null_log_mu = float(np.log(np.mean(stream.size[train] - 1)))
    size_model_ll = poisson_log_likelihood_without_constant(
        log_mu_estimate,
        gamma_estimate,
        latent[test],
        stream.size[test],
    )
    size_null_ll = poisson_log_likelihood_without_constant(
        null_log_mu,
        0.0,
        latent[test],
        stream.size[test],
    )
    size_gain = (size_model_ll - size_null_ll) / int(np.count_nonzero(test))

    permuted_train = latent[train].copy()
    permuted_test = latent[test].copy()
    generator.shuffle(permuted_train)
    generator.shuffle(permuted_test)
    train_visible_local = visible[train]
    test_visible_local = visible[test]
    permuted_fit = fit_flow_slope(
        permuted_train[train_visible_local],
        signed_flow[visible_train],
    )
    permuted_beta = float(permuted_fit.values[0])
    permuted_model_ll = bernoulli_log_likelihood(
        permuted_beta,
        permuted_test[test_visible_local],
        signed_flow[visible_test],
    )
    permuted_null_ll = bernoulli_log_likelihood(
        0.0,
        permuted_test[test_visible_local],
        signed_flow[visible_test],
    )
    permuted_gain = (
        permuted_model_ll - permuted_null_ll
    ) / int(np.count_nonzero(visible_test))

    flipped_fit = fit_flow_slope(-latent[visible_train], signed_flow[visible_train])
    flipped_beta = float(flipped_fit.values[0])
    flipped_ll = bernoulli_log_likelihood(
        flipped_beta,
        -latent[visible_test],
        signed_flow[visible_test],
    )
    gauge_ll_difference = abs(flipped_ll - q_model_ll) / int(
        np.count_nonzero(visible_test)
    )

    previous = _previous_snapshots(stream)
    hidden = stream.event_type == 5
    hidden_changed = int(np.count_nonzero(np.any(stream.snapshots[hidden] != previous[hidden], axis=1)))
    queue_sizes = np.concatenate((stream.snapshots[:, 1::4], stream.snapshots[:, 3::4]), axis=1)
    return {
        "rho": rho,
        "beta_true": beta_true,
        "seed": seed,
        "n_events": N_EVENTS,
        "n_train": split,
        "n_test": N_EVENTS - split,
        "n_visible_train": int(np.count_nonzero(visible_train)),
        "n_visible_test": int(np.count_nonzero(visible_test)),
        "reconstruction": {
            "bit_exact": bool(np.array_equal(reconstructed, stream.snapshots)),
            "max_absolute_difference": int(
                np.max(np.abs(reconstructed - stream.snapshots))
            ),
            "hidden_events": int(np.count_nonzero(hidden)),
            "hidden_changed": hidden_changed,
            "minimum_queue": int(queue_sizes.min()),
        },
        "fit": {
            "beta": beta_estimate,
            "p_hidden": p_hidden,
            "p_add": p_add,
            "removal_probabilities": removal_probabilities,
            "eta": float(eta_fit.values[0]),
            "log_mu": log_mu_estimate,
            "gamma": gamma_estimate,
        },
        "heldout_gain_nats_per_event": {
            "signed_flow_vs_beta_zero": float(q_gain),
            "size_vs_gamma_zero": float(size_gain),
        },
        "permuted_latent_control": {
            "beta": permuted_beta,
            "heldout_gain_nats_per_visible_event": float(permuted_gain),
        },
        "sign_gauge_control": {
            "flipped_beta": flipped_beta,
            "slope_sum_absolute": abs(flipped_beta + beta_estimate),
            "heldout_ll_difference_per_visible_event": float(gauge_ll_difference),
        },
        "solver": {
            "beta_converged": beta_fit.converged,
            "beta_iterations": beta_fit.iterations,
            "permuted_beta_converged": permuted_fit.converged,
            "flipped_beta_converged": flipped_fit.converged,
            "eta_converged": eta_fit.converged,
            "eta_iterations": eta_fit.iterations,
            "size_converged": size_fit.converged,
            "size_iterations": size_fit.iterations,
        },
    }


def _cell_records(
    records: list[dict[str, Any]],
    rho: float,
    beta: float,
) -> list[dict[str, Any]]:
    return [
        record
        for record in records
        if record["rho"] == rho and record["beta_true"] == beta
    ]


def _median(values: list[float]) -> float:
    return float(np.median(np.asarray(values, dtype=np.float64)))


def _summarize_cells(records: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for rho in RHO_VALUES:
        for beta in BETA_VALUES:
            cell = _cell_records(records, rho, beta)
            beta_estimates = [float(record["fit"]["beta"]) for record in cell]
            q_gains = [
                float(record["heldout_gain_nats_per_event"]["signed_flow_vs_beta_zero"])
                for record in cell
            ]
            permuted_betas = [
                float(record["permuted_latent_control"]["beta"])
                for record in cell
            ]
            permuted_gains = [
                float(
                    record["permuted_latent_control"][
                        "heldout_gain_nats_per_visible_event"
                    ]
                )
                for record in cell
            ]
            key = f"rho={rho:.2f},beta={beta:.2f}"
            summary[key] = {
                "median_beta": _median(beta_estimates),
                "median_absolute_beta_error": _median(
                    [abs(estimate - beta) for estimate in beta_estimates]
                ),
                "median_absolute_relative_beta_error": (
                    _median([abs(estimate - beta) / beta for estimate in beta_estimates])
                    if beta > 0.0
                    else None
                ),
                "correct_sign_streams": (
                    sum(estimate > 0.0 for estimate in beta_estimates)
                    if beta > 0.0
                    else None
                ),
                "median_q_gain_nats": _median(q_gains),
                "median_permuted_absolute_beta": _median(
                    [abs(value) for value in permuted_betas]
                ),
                "median_permuted_gain_nats": _median(permuted_gains),
            }
    return summary


def _all_numeric_finite(value: Any) -> bool:
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return True
    if isinstance(value, (int, float)):
        return bool(np.isfinite(value))
    if isinstance(value, dict):
        return all(_all_numeric_finite(item) for item in value.values())
    if isinstance(value, list):
        return all(_all_numeric_finite(item) for item in value)
    return True


def _aggregate_summary(
    records: list[dict[str, Any]],
    config: AggregateL2EmissionConfig,
) -> dict[str, Any]:
    probability_truth = {
        "p_hidden": config.p_hidden,
        "p_add": config.p_add,
        "removal_2": config.removal_probabilities[0],
        "removal_3": config.removal_probabilities[1],
        "removal_4": config.removal_probabilities[2],
    }
    probability_estimates = {
        "p_hidden": [float(record["fit"]["p_hidden"]) for record in records],
        "p_add": [float(record["fit"]["p_add"]) for record in records],
        **{
            f"removal_{event_type}": [
                float(record["fit"]["removal_probabilities"][str(event_type)])
                for record in records
            ]
            for event_type in (2, 3, 4)
        },
    }
    return {
        "median_absolute_probability_errors": {
            name: _median([abs(value - probability_truth[name]) for value in values])
            for name, values in probability_estimates.items()
        },
        "median_absolute_eta_error": _median(
            [abs(float(record["fit"]["eta"]) - config.eta) for record in records]
        ),
        "median_absolute_relative_gamma_error": _median(
            [
                abs(float(record["fit"]["gamma"]) - config.gamma) / config.gamma
                for record in records
            ]
        ),
        "median_size_gain_nats": _median(
            [
                float(
                    record["heldout_gain_nats_per_event"]["size_vs_gamma_zero"]
                )
                for record in records
            ]
        ),
        "maximum_gauge_slope_sum": max(
            float(record["sign_gauge_control"]["slope_sum_absolute"])
            for record in records
        ),
        "maximum_gauge_ll_difference_per_event": max(
            float(
                record["sign_gauge_control"][
                    "heldout_ll_difference_per_visible_event"
                ]
            )
            for record in records
        ),
        "minimum_queue": min(
            int(record["reconstruction"]["minimum_queue"]) for record in records
        ),
    }


def _hard_gates(
    records: list[dict[str, Any]],
    cell_summary: dict[str, Any],
    aggregate_summary: dict[str, Any],
) -> dict[str, bool]:
    nonzero_beta_cells = [
        cell_summary[f"rho={rho:.2f},beta={beta:.2f}"]
        for rho in RHO_VALUES
        for beta in (0.5, 1.0)
    ]
    zero_beta_cells = [
        cell_summary[f"rho={rho:.2f},beta=0.00"] for rho in RHO_VALUES
    ]
    return {
        "reconstruction_and_hidden_invariance_exact": all(
            record["reconstruction"]["bit_exact"]
            and record["reconstruction"]["hidden_changed"] == 0
            and record["reconstruction"]["minimum_queue"] > 0
            for record in records
        ),
        "nonzero_beta_recovery_and_sign": all(
            cell["median_absolute_relative_beta_error"] <= 0.10
            and cell["correct_sign_streams"] >= 7
            for cell in nonzero_beta_cells
        ),
        "zero_beta_recovery": all(
            cell["median_absolute_beta_error"] <= 0.05 for cell in zero_beta_cells
        ),
        "heldout_flow_likelihood_gain": all(
            cell_summary[f"rho={rho:.2f},beta=0.50"]["median_q_gain_nats"]
            >= 0.04
            and cell_summary[f"rho={rho:.2f},beta=1.00"]["median_q_gain_nats"]
            >= 0.12
            and abs(
                cell_summary[f"rho={rho:.2f},beta=0.00"]["median_q_gain_nats"]
            )
            <= 0.002
            for rho in RHO_VALUES
        ),
        "permuted_latent_kills_signal": all(
            cell["median_permuted_absolute_beta"] <= 0.05
            and abs(cell["median_permuted_gain_nats"]) <= 0.002
            for cell in nonzero_beta_cells
        ),
        "sign_gauge_control_exact": all(
            record["sign_gauge_control"]["slope_sum_absolute"] <= 1e-8
            and record["sign_gauge_control"][
                "heldout_ll_difference_per_visible_event"
            ]
            <= 1e-12
            for record in records
        ),
        "categorical_and_level_parameters_recovered": (
            all(
                error <= 0.02
                for error in aggregate_summary[
                    "median_absolute_probability_errors"
                ].values()
            )
            and aggregate_summary["median_absolute_eta_error"] <= 0.05
        ),
        "size_parameter_recovered_and_predictive": (
            aggregate_summary["median_absolute_relative_gamma_error"] <= 0.15
            and aggregate_summary["median_size_gain_nats"] > 0.0
        ),
        "all_solvers_converged": all(
            record["solver"][key]
            for record in records
            for key in (
                "beta_converged",
                "permuted_beta_converged",
                "flipped_beta_converged",
                "eta_converged",
                "size_converged",
            )
        ),
        "all_reported_values_finite": _all_numeric_finite(records),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    started = time.perf_counter()
    config = AggregateL2EmissionConfig()
    design = [(rho, beta) for rho in RHO_VALUES for beta in BETA_VALUES]
    children = np.random.SeedSequence(ROOT_SEED).spawn(len(design) * N_STREAMS)
    records: list[dict[str, Any]] = []
    child_index = 0
    for rho, beta in design:
        for _ in range(N_STREAMS):
            seed = int(children[child_index].generate_state(1, dtype=np.uint64)[0])
            child_index += 1
            records.append(
                _analyse_stream(
                    rho=rho,
                    beta_true=beta,
                    seed=seed,
                    config=config,
                )
            )

    cell_summary = _summarize_cells(records)
    aggregate_summary = _aggregate_summary(records, config)
    gates = _hard_gates(records, cell_summary, aggregate_summary)
    payload = {
        "experiment": "134_synthetic_l2_emission_recovery",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "platform": platform.platform(),
        "numpy_version": np.__version__,
        "design": {
            "root_seed": ROOT_SEED,
            "rho_values": RHO_VALUES,
            "beta_values": BETA_VALUES,
            "streams_per_cell": N_STREAMS,
            "events_per_stream": N_EVENTS,
            "train_fraction": TRAIN_FRACTION,
            "config": {
                "n_levels": config.n_levels,
                "initial_queue": config.initial_queue,
                "best_bid": config.best_bid,
                "best_ask": config.best_ask,
                "p_hidden": config.p_hidden,
                "p_add": config.p_add,
                "removal_probabilities": config.removal_probabilities,
                "eta": config.eta,
                "log_mu": config.log_mu,
                "gamma": config.gamma,
            },
        },
        "hard_gates": gates,
        "all_hard_gates_pass": all(gates.values()),
        "cell_summary": cell_summary,
        "aggregate_summary": aggregate_summary,
        "records": records,
        "wall_seconds": time.perf_counter() - started,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "out": str(args.out),
                "all_hard_gates_pass": payload["all_hard_gates_pass"],
                "hard_gates": gates,
                "cell_summary": cell_summary,
                "aggregate_summary": aggregate_summary,
                "wall_seconds": payload["wall_seconds"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
