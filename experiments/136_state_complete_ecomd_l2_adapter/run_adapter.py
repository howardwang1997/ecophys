"""Run the preregistered state-complete EcoMD-to-L2 adapter audit."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import torch

from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator
from ecomd.observation.ecomd_l2_adapter import (
    EcoMDL2Adapter,
    EcoMDL2AdapterConfig,
    EcoMDL2AdapterState,
)
from ecomd.observation.l2_emission import (
    fit_logistic_features,
    logistic_feature_log_likelihood,
    reconstruct_aggregate_book,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = Path(__file__).with_name("ECOMD_L2_ADAPTER_RESULTS.json")
ROOT_SEED = 136_202_608
PARAMETER_SEED = 136_000
N_STREAMS = 8
N_STEPS = 3_000
BURN_IN = 500
TRAIN_FRACTION = 0.60
SIMULATOR_CHUNKS = (137, 499, 61, 803, 1_500)
ADAPTER_CHUNKS = (211, 17, 503, 769, 1_000)
EMISSION_BETA = 2.0


def _config() -> EcoMDConfig:
    return EcoMDConfig(
        n_agents=64,
        d_state=8,
        hidden=16,
        dt=0.005,
        gamma_init=10.0,
        temperature_init=0.05,
        learn_gamma=False,
        learn_temperature=False,
        pairwise_kind="stochastic_mlp",
        sps_k_random=6,
        sps_resample_per_step=True,
        regime_enabled=True,
        regime_d=8,
        regime_update_every=3,
        agent_memory_enabled=True,
        agent_memory_d=8,
        agent_memory_update_every=2,
        global_state_enabled=True,
        global_state_d=8,
        global_state_update_every=3,
        global_state_into_pair=True,
        jump_lambda=2.0,
        jump_scale=0.01,
        memory_kernel_lambda=0.9,
        memory_kernel_strength=0.05,
        microstructure_rho=0.05,
        ar1_whiten_lambda=0.9,
        ar1_whiten_strength=0.05,
        zumbach_feedback_lambda=0.9,
        zumbach_feedback_strength=0.05,
        multi_timescale_enabled=True,
        timescale_fast_frac=0.75,
        timescale_slow_freq=4,
        price_formation_kwargs={
            "beta": 0.02,
            "kappa": 0.5,
            "sigma_price": 0.005,
            "log_raw_excess_demand": True,
        },
    )


def _git_value(*args: str) -> str:
    return subprocess.check_output(
        ("git", *args), cwd=ROOT, text=True, stderr=subprocess.DEVNULL
    ).strip()


def _tree_equal(left: Any, right: Any) -> bool:
    if isinstance(left, torch.Tensor) and isinstance(right, torch.Tensor):
        return bool(torch.equal(left, right))
    if isinstance(left, np.ndarray) and isinstance(right, np.ndarray):
        return bool(np.array_equal(left, right))
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(
            _tree_equal(left[key], right[key]) for key in left
        )
    if isinstance(left, (list, tuple)) and isinstance(right, type(left)):
        return len(left) == len(right) and all(
            _tree_equal(a, b) for a, b in zip(left, right, strict=True)
        )
    return bool(left == right)


def _concatenate_trajectory_parts(parts, field: str) -> torch.Tensor:
    return torch.cat([getattr(part, field) for part in parts])


def _concatenate_stream_parts(parts, field: str) -> np.ndarray:
    return np.concatenate([getattr(part, field) for part in parts], axis=0)


def _visible_regression_arrays(stream) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    visible_indices = np.flatnonzero(stream.event_type != 5)
    visible_types = stream.event_type[visible_indices]
    action = np.where(visible_types == 1, 1, -1)
    signed_flow = stream.direction[visible_indices] * action
    latent = stream.latent[visible_indices]
    return visible_indices[1:], latent[1:], np.column_stack(
        (signed_flow[1:], signed_flow[:-1])
    ).astype(np.int64)


def _fit_models(stream, permutation_seed: int) -> dict[str, Any]:
    absolute_index, latent, flow_pair = _visible_regression_arrays(stream)
    signed_flow = flow_pair[:, 0]
    previous_visible = flow_pair[:, 1].astype(np.float64)
    split = int(TRAIN_FRACTION * stream.n_events)
    train = absolute_index < split
    test = ~train
    feature_sets = {
        "null": np.empty((latent.size, 0), dtype=np.float64),
        "latent": (2.0 * latent)[:, None],
        "observation_only": (2.0 * previous_visible)[:, None],
        "combined": np.column_stack((2.0 * latent, 2.0 * previous_visible)),
    }
    generator = np.random.default_rng(permutation_seed)
    permuted = latent.copy()
    train_values = permuted[train].copy()
    test_values = permuted[test].copy()
    generator.shuffle(train_values)
    generator.shuffle(test_values)
    permuted[train] = train_values
    permuted[test] = test_values
    feature_sets["permuted"] = (2.0 * permuted)[:, None]

    models: dict[str, Any] = {}
    for name, features in feature_sets.items():
        fit = fit_logistic_features(features[train], signed_flow[train])
        heldout_ll = logistic_feature_log_likelihood(
            fit.values, features[test], signed_flow[test]
        ) / int(np.count_nonzero(test))
        models[name] = {
            "coefficients": [float(value) for value in fit.values],
            "converged": fit.converged,
            "iterations": fit.iterations,
            "heldout_log_likelihood_nats_per_visible_event": float(heldout_ll),
        }
    null_ll = float(models["null"]["heldout_log_likelihood_nats_per_visible_event"])
    for model in models.values():
        model["heldout_gain_over_null_nats_per_visible_event"] = float(
            model["heldout_log_likelihood_nats_per_visible_event"] - null_ll
        )

    anchored = np.asarray((0.0, EMISSION_BETA), dtype=np.float64)
    anchored_ll = logistic_feature_log_likelihood(
        anchored, feature_sets["latent"][test], signed_flow[test]
    ) / int(np.count_nonzero(test))
    flipped_ll = logistic_feature_log_likelihood(
        anchored, -feature_sets["latent"][test], signed_flow[test]
    ) / int(np.count_nonzero(test))
    return {
        "n_visible_regression": int(latent.size),
        "n_visible_train": int(np.count_nonzero(train)),
        "n_visible_test": int(np.count_nonzero(test)),
        "models": models,
        "frozen_positive_anchor_minus_flipped_nats_per_visible_event": float(
            anchored_ll - flipped_ll
        ),
    }


def _run_stream(
    simulator: EcoMDSimulator,
    rollout_seed: int,
    emission_seed: int,
) -> dict[str, Any]:
    initial = simulator.init_simulator_state(seed=rollout_seed)
    full_state, full = simulator.rollout_state(
        initial.clone(), N_STEPS, create_graph=False, lightweight=True
    )
    chunk_state = initial.clone()
    trajectory_parts = []
    for length in SIMULATOR_CHUNKS:
        chunk_state, part = simulator.rollout_state(
            chunk_state, length, create_graph=False, lightweight=True
        )
        trajectory_parts.append(part)

    simulator_fields_exact = {
        field: bool(
            torch.equal(
                getattr(full, field),
                _concatenate_trajectory_parts(trajectory_parts, field),
            )
        )
        for field in ("latent_flow_alignment", "excess_demand", "log_returns")
    }
    terminal_state_exact = _tree_equal(
        full_state.to_checkpoint(), chunk_state.to_checkpoint()
    )
    alignment = full.latent_flow_alignment.detach().cpu().numpy().astype(np.float64)
    excess_demand = full.excess_demand.detach().cpu().numpy().astype(np.float64)
    returns = full.log_returns.detach().cpu().numpy().astype(np.float64)
    finite = bool(
        np.isfinite(alignment).all()
        and np.isfinite(excess_demand).all()
        and np.isfinite(returns).all()
    )
    nonzero = alignment != 0.0
    sign_anchor_exact = bool(
        np.array_equal(np.sign(alignment[nonzero]), np.sign(excess_demand[nonzero]))
    )

    adapter = EcoMDL2Adapter(
        EcoMDL2AdapterConfig(dt=simulator.cfg.dt, beta_emit=EMISSION_BETA)
    )
    emitted_latent = alignment[BURN_IN:]
    initial_adapter = adapter.init_state(seed=emission_seed, start_step=BURN_IN)
    adapter_full_state, stream = adapter.emit(
        initial_adapter.clone(), emitted_latent, start_step=BURN_IN
    )
    adapter_state = initial_adapter.clone()
    stream_parts = []
    offset = 0
    for length in ADAPTER_CHUNKS:
        adapter_state, part = adapter.emit(
            adapter_state,
            emitted_latent[offset : offset + length],
            start_step=BURN_IN + offset,
        )
        stream_parts.append(part)
        offset += length
        if offset == 731:
            adapter_state = EcoMDL2AdapterState.from_checkpoint(
                adapter_state.to_checkpoint()
            )
    adapter_fields_exact = {
        field: bool(
            np.array_equal(
                getattr(stream, field),
                _concatenate_stream_parts(stream_parts, field),
            )
        )
        for field in (
            "latent",
            "time",
            "event_type",
            "order_id",
            "size",
            "price",
            "direction",
            "snapshots",
        )
    }
    adapter_terminal_exact = _tree_equal(
        adapter_full_state.to_checkpoint(), adapter_state.to_checkpoint()
    )
    reconstructed = reconstruct_aggregate_book(stream)
    expected_time = (
        BURN_IN + np.arange(stream.n_events, dtype=np.float64) + 1.0
    ) * simulator.cfg.dt
    schema_checks = {
        "reconstruction_exact": bool(np.array_equal(reconstructed, stream.snapshots)),
        "timestamps_exact": bool(np.array_equal(stream.time, expected_time)),
        "order_ids_contiguous": bool(
            np.array_equal(
                stream.order_id,
                np.arange(1, stream.n_events + 1, dtype=np.int64),
            )
        ),
        "queues_positive": bool(
            np.all(stream.snapshots[:, 1::4] > 0)
            and np.all(stream.snapshots[:, 3::4] > 0)
        ),
    }
    regression = _fit_models(stream, emission_seed ^ 0x135136)
    return {
        "rollout_seed": rollout_seed,
        "emission_seed": emission_seed,
        "finite": finite,
        "simulator_fields_exact": simulator_fields_exact,
        "simulator_terminal_state_exact": terminal_state_exact,
        "sign_anchor_exact": sign_anchor_exact,
        "nonzero_alignment_steps": int(np.count_nonzero(nonzero)),
        "alignment_mean_absolute": float(np.mean(np.abs(alignment[BURN_IN:]))),
        "adapter_fields_exact": adapter_fields_exact,
        "adapter_terminal_state_exact": adapter_terminal_exact,
        "schema_checks": schema_checks,
        "minimum_queue": int(
            min(stream.snapshots[:, 1::4].min(), stream.snapshots[:, 3::4].min())
        ),
        "regression": regression,
    }


def _median(values: list[float]) -> float:
    return float(np.median(np.asarray(values, dtype=np.float64)))


def _summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    latent_coefficients = [
        float(record["regression"]["models"]["latent"]["coefficients"][1])
        for record in records
    ]
    observed_coefficients = [
        float(record["regression"]["models"]["combined"]["coefficients"][2])
        for record in records
    ]
    permuted_coefficients = [
        float(record["regression"]["models"]["permuted"]["coefficients"][1])
        for record in records
    ]

    def ll(record: dict[str, Any], model: str) -> float:
        return float(
            record["regression"]["models"][model][
                "heldout_log_likelihood_nats_per_visible_event"
            ]
        )

    return {
        "median_absolute_alignment": _median(
            [float(record["alignment_mean_absolute"]) for record in records]
        ),
        "median_latent_coefficient": _median(latent_coefficients),
        "median_latent_relative_error": _median(
            [abs(value - EMISSION_BETA) / EMISSION_BETA for value in latent_coefficients]
        ),
        "positive_latent_slopes": sum(value > 0.0 for value in latent_coefficients),
        "median_latent_minus_observation_nats": _median(
            [ll(record, "latent") - ll(record, "observation_only") for record in records]
        ),
        "median_combined_minus_latent_nats": _median(
            [ll(record, "combined") - ll(record, "latent") for record in records]
        ),
        "median_absolute_combined_observed_coefficient": _median(
            [abs(value) for value in observed_coefficients]
        ),
        "median_absolute_permuted_coefficient": _median(
            [abs(value) for value in permuted_coefficients]
        ),
        "median_absolute_permuted_gain_over_null_nats": _median(
            [
                abs(
                    float(
                        record["regression"]["models"]["permuted"][
                            "heldout_gain_over_null_nats_per_visible_event"
                        ]
                    )
                )
                for record in records
            ]
        ),
        "median_anchor_minus_flipped_nats": _median(
            [
                float(
                    record["regression"][
                        "frozen_positive_anchor_minus_flipped_nats_per_visible_event"
                    ]
                )
                for record in records
            ]
        ),
        "minimum_queue": min(int(record["minimum_queue"]) for record in records),
    }


def _hard_gates(
    records: list[dict[str, Any]], summary: dict[str, Any]
) -> dict[str, bool]:
    all_models = [
        model
        for record in records
        for model in record["regression"]["models"].values()
    ]
    return {
        "simulator_finite_and_bit_exact": all(
            bool(record["finite"])
            and all(bool(value) for value in record["simulator_fields_exact"].values())
            and bool(record["simulator_terminal_state_exact"])
            for record in records
        ),
        "structural_sign_anchor_exact": all(
            bool(record["sign_anchor_exact"])
            and int(record["nonzero_alignment_steps"]) > 0
            for record in records
        ),
        "adapter_resume_and_schema_exact": all(
            all(bool(value) for value in record["adapter_fields_exact"].values())
            and bool(record["adapter_terminal_state_exact"])
            and all(bool(value) for value in record["schema_checks"].values())
            for record in records
        ),
        "latent_parameter_recovery": (
            float(summary["median_latent_relative_error"]) <= 0.20
            and int(summary["positive_latent_slopes"]) >= 7
        ),
        "latent_beats_observation_only": (
            float(summary["median_latent_minus_observation_nats"]) >= 0.01
            and float(summary["median_combined_minus_latent_nats"]) <= 0.005
            and float(summary["median_absolute_combined_observed_coefficient"]) <= 0.15
        ),
        "permuted_control": (
            float(summary["median_absolute_permuted_coefficient"]) <= 0.20
            and float(summary["median_absolute_permuted_gain_over_null_nats"]) <= 0.003
        ),
        "anchored_sign_beats_flip": (
            float(summary["median_anchor_minus_flipped_nats"]) >= 0.02
        ),
        "all_fits_converged_and_finite": (
            all(bool(model["converged"]) for model in all_models)
            and all(
                np.isfinite(float(value))
                for model in all_models
                for value in (
                    *model["coefficients"],
                    model["heldout_log_likelihood_nats_per_visible_event"],
                    model["heldout_gain_over_null_nats_per_visible_event"],
                )
            )
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    torch.set_num_threads(1)
    torch.manual_seed(PARAMETER_SEED)
    simulator = EcoMDSimulator(_config())
    seed_sequence = np.random.SeedSequence(ROOT_SEED)
    children = seed_sequence.spawn(2 * N_STREAMS)
    seed_pairs = [
        (
            int(children[2 * index].generate_state(1, dtype=np.uint64)[0]),
            int(children[2 * index + 1].generate_state(1, dtype=np.uint64)[0]),
        )
        for index in range(N_STREAMS)
    ]
    started = time.perf_counter()
    records = [
        _run_stream(simulator, rollout_seed, emission_seed)
        for rollout_seed, emission_seed in seed_pairs
    ]
    summary = _summarize(records)
    gates = _hard_gates(records, summary)
    payload = {
        "experiment": 136,
        "title": "state-complete EcoMD-to-L2 adapter",
        "protocol": {
            "root_seed": ROOT_SEED,
            "parameter_seed": PARAMETER_SEED,
            "n_streams": N_STREAMS,
            "n_steps": N_STEPS,
            "burn_in": BURN_IN,
            "emitted_events_per_stream": N_STEPS - BURN_IN,
            "train_fraction": TRAIN_FRACTION,
            "simulator_chunks": list(SIMULATOR_CHUNKS),
            "adapter_chunks": list(ADAPTER_CHUNKS),
            "emission_beta": EMISSION_BETA,
            "simulator_config": asdict(simulator.cfg),
        },
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "torch": torch.__version__,
            "device": "cpu",
            "torch_threads": torch.get_num_threads(),
            "git_sha": _git_value("rev-parse", "HEAD"),
            "git_dirty": bool(_git_value("status", "--porcelain")),
        },
        "summary": summary,
        "hard_gates": gates,
        "all_hard_gates_pass": all(gates.values()),
        "elapsed_seconds": time.perf_counter() - started,
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "summary": summary,
        "hard_gates": gates,
        "all_hard_gates_pass": payload["all_hard_gates_pass"],
        "elapsed_seconds": payload["elapsed_seconds"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
