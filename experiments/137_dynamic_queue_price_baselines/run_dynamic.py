"""Run and merge the preregistered dynamic queue/price baseline stress."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import time
from dataclasses import asdict, fields
from pathlib import Path
from typing import Any, TypeAlias, cast

import numpy as np
from numpy.typing import NDArray

from ecomd.observation.dynamic_l2 import (
    DynamicL2Config,
    DynamicL2Generator,
    DynamicL2State,
    DynamicL2Stream,
    reconstruct_dynamic_l2,
)
from ecomd.observation.l2_emission import (
    fit_logistic_features,
    logistic_feature_log_likelihood,
    simulate_latent_ar1,
)

FloatArray: TypeAlias = NDArray[np.float64]
BoolArray: TypeAlias = NDArray[np.bool_]
Array: TypeAlias = NDArray[Any]

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = Path(__file__).with_name("DYNAMIC_QUEUE_RESULTS.json")
ROOT_SEED = 137_202_608
SMOKE_ROOT_SEED = 137_202_609
N_EVENTS = 40_000
SMOKE_EVENTS = 3_000
N_REPLICATES = 8
TRAIN_FRACTION = 0.60
TRUTHS = ("latent_incremental", "observation_only")
RHO_VALUES = (0.60, 0.95)
CENSOR_RATES = (0.0, 0.20)
MODEL_NAMES = (
    "null",
    "latent_current",
    "latent_lag3",
    "queue_reactive",
    "marked_hawkes",
    "observation_full",
    "combined_current",
    "combined_lag3",
    "combined_permuted",
)
PREREGISTRATION_COMMITS = (
    "69266f26",
    "fc9aff87",
)


def _git_value(*args: str) -> str:
    return subprocess.check_output(
        ("git", *args), cwd=ROOT, text=True, stderr=subprocess.DEVNULL
    ).strip()


def _protocol(*, formal: bool) -> dict[str, Any]:
    return {
        "experiment": 137,
        "formal": formal,
        "root_seed": ROOT_SEED if formal else SMOKE_ROOT_SEED,
        "n_events": N_EVENTS if formal else SMOKE_EVENTS,
        "n_replicates": N_REPLICATES if formal else 1,
        "train_fraction": TRAIN_FRACTION,
        "truths": list(TRUTHS),
        "rho_values": list(RHO_VALUES),
        "censor_rates": list(CENSOR_RATES),
        "model_names": list(MODEL_NAMES),
        "book_config": asdict(DynamicL2Config()),
        "chunks": [137, 499, 61, 803, 1_500, "remainder"],
        "resume_after": 1_500,
        "preregistration_commits": list(PREREGISTRATION_COMMITS),
    }


def _protocol_hash(protocol: dict[str, Any]) -> str:
    encoded = json.dumps(
        protocol, sort_keys=True, separators=(",", ":")
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def _stream_specs(*, formal: bool) -> list[dict[str, Any]]:
    n_replicates = N_REPLICATES if formal else 1
    root_seed = ROOT_SEED if formal else SMOKE_ROOT_SEED
    cells = [
        (truth, rho, censor_rate, replicate)
        for truth in TRUTHS
        for rho in RHO_VALUES
        for censor_rate in CENSOR_RATES
        for replicate in range(n_replicates)
    ]
    children = np.random.SeedSequence(root_seed).spawn(len(cells))
    specs: list[dict[str, Any]] = []
    for stream_id, (cell, child) in enumerate(zip(cells, children, strict=True)):
        truth, rho, censor_rate, replicate = cell
        seeds = child.generate_state(3, dtype=np.uint64)
        specs.append(
            {
                "stream_id": stream_id,
                "truth": truth,
                "rho": rho,
                "censor_rate": censor_rate,
                "replicate": replicate,
                "latent_seed": int(seeds[0]),
                "event_seed": int(seeds[1]),
                "permutation_seed": int(seeds[2]),
            }
        )
    return specs


def _tree_equal(left: Any, right: Any) -> bool:
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


def _concatenate_streams(parts: list[DynamicL2Stream]) -> DynamicL2Stream:
    values: dict[str, Any] = {}
    for field in fields(DynamicL2Stream):
        values[field.name] = np.concatenate(
            [cast(Array, getattr(part, field.name)) for part in parts], axis=0
        )
    return DynamicL2Stream(**values)


def _chunk_lengths(n_events: int) -> tuple[int, ...]:
    frozen = (137, 499, 61, 803, 1_500)
    frozen_total = sum(frozen)
    if n_events < frozen_total:
        raise ValueError("event count is shorter than frozen chunk prefix")
    remainder = n_events - frozen_total
    return frozen if remainder == 0 else (*frozen, remainder)


def _feature_sets(
    stream: DynamicL2Stream,
    latent_lag3: FloatArray,
    train: BoolArray,
    test: BoolArray,
    *,
    permutation_seed: int,
) -> dict[str, FloatArray]:
    n_events = stream.n_events
    latent_current = (2.0 * stream.latent)[:, None]
    latent_lagged = (2.0 * latent_lag3)[:, None]
    queue = np.column_stack(
        (2.0 * stream.pre_imbalance, stream.pre_log_depth_ratio)
    )
    marked_hawkes = 2.0 * stream.pre_observed_traces
    observation = np.column_stack((queue, marked_hawkes))
    permuted = stream.latent.copy()
    generator = np.random.default_rng(permutation_seed)
    train_values = permuted[train].copy()
    test_values = permuted[test].copy()
    generator.shuffle(train_values)
    generator.shuffle(test_values)
    permuted[train] = train_values
    permuted[test] = test_values
    return {
        "null": np.empty((n_events, 0), dtype=np.float64),
        "latent_current": latent_current,
        "latent_lag3": latent_lagged,
        "queue_reactive": queue,
        "marked_hawkes": marked_hawkes,
        "observation_full": observation,
        "combined_current": np.column_stack((latent_current, observation)),
        "combined_lag3": np.column_stack((latent_lagged, observation)),
        "combined_permuted": np.column_stack((2.0 * permuted, observation)),
    }


def _fit_models(
    stream: DynamicL2Stream,
    latent_lag3: FloatArray,
    *,
    permutation_seed: int,
    n_events: int,
) -> tuple[dict[str, Any], int, int]:
    split = int(TRAIN_FRACTION * n_events)
    train = stream.retained & (stream.event_index < split)
    test = stream.retained & (stream.event_index >= split)
    if np.count_nonzero(train) < 2 or np.count_nonzero(test) < 2:
        raise RuntimeError("insufficient retained events for fitting")
    feature_sets = _feature_sets(
        stream,
        latent_lag3,
        train,
        test,
        permutation_seed=permutation_seed,
    )
    models: dict[str, Any] = {}
    for name in MODEL_NAMES:
        features = feature_sets[name]
        fit = fit_logistic_features(features[train], stream.signed_flow[train])
        heldout = logistic_feature_log_likelihood(
            fit.values, features[test], stream.signed_flow[test]
        ) / int(np.count_nonzero(test))
        models[name] = {
            "coefficients": [float(value) for value in fit.values],
            "converged": fit.converged,
            "iterations": fit.iterations,
            "heldout_log_likelihood_nats_per_event": float(heldout),
        }
    null_ll = float(models["null"]["heldout_log_likelihood_nats_per_event"])
    for model in models.values():
        model["heldout_gain_over_null_nats_per_event"] = float(
            model["heldout_log_likelihood_nats_per_event"] - null_ll
        )
    return models, int(np.count_nonzero(train)), int(np.count_nonzero(test))


def _run_stream(spec: dict[str, Any], *, formal: bool) -> dict[str, Any]:
    n_events = N_EVENTS if formal else SMOKE_EVENTS
    latent_generator = np.random.default_rng(int(spec["latent_seed"]))
    latent_path = simulate_latent_ar1(
        n_events + 3, float(spec["rho"]), latent_generator
    )
    latent_current = latent_path[3:]
    latent_lag3 = latent_path[:-3]
    config = DynamicL2Config()
    operator = DynamicL2Generator(
        config,
        cast(Any, spec["truth"]),
        censor_rate=float(spec["censor_rate"]),
    )
    initial = operator.init_state(seed=int(spec["event_seed"]))
    full_state, full = operator.emit(
        initial.clone(), latent_current, start_event=0
    )

    chunk_state = initial.clone()
    parts: list[DynamicL2Stream] = []
    offset = 0
    for length in _chunk_lengths(n_events):
        chunk_state, part = operator.emit(
            chunk_state,
            latent_current[offset : offset + length],
            start_event=offset,
        )
        parts.append(part)
        offset += length
        if offset == 1_500:
            chunk_state = DynamicL2State.from_checkpoint(
                chunk_state.to_checkpoint()
            )
    chunked = _concatenate_streams(parts)
    field_exact = {
        field.name: bool(
            np.array_equal(getattr(full, field.name), getattr(chunked, field.name))
        )
        for field in fields(DynamicL2Stream)
    }
    terminal_exact = _tree_equal(
        full_state.to_checkpoint(), chunk_state.to_checkpoint()
    )
    reconstructed_books, reconstructed_mid, reconstructed_moves = (
        reconstruct_dynamic_l2(full, config)
    )
    reconstruction_exact = bool(
        np.array_equal(reconstructed_books, full.snapshots)
        and np.array_equal(reconstructed_mid, full.mid_tick)
        and np.array_equal(reconstructed_moves, full.price_move)
    )
    models, n_train, n_test = _fit_models(
        full,
        latent_lag3,
        permutation_seed=int(spec["permutation_seed"]),
        n_events=n_events,
    )
    moving = full.price_move != 0
    nonzero_moves = full.price_move[moving]
    all_model_values = [
        value
        for model in models.values()
        for value in (
            *model["coefficients"],
            model["heldout_log_likelihood_nats_per_event"],
            model["heldout_gain_over_null_nats_per_event"],
        )
    ]
    return {
        **spec,
        "n_events": n_events,
        "n_retained": int(np.count_nonzero(full.retained)),
        "n_train": n_train,
        "n_test": n_test,
        "field_exact": field_exact,
        "terminal_state_exact": terminal_exact,
        "reconstruction_exact": reconstruction_exact,
        "queues_positive": bool(
            np.all(full.snapshots[:, 1::4] > 0)
            and np.all(full.snapshots[:, 3::4] > 0)
        ),
        "move_sign_exact": bool(
            np.array_equal(nonzero_moves, full.signed_flow[moving])
        ),
        "up_moves": int(np.count_nonzero(full.price_move == 1)),
        "down_moves": int(np.count_nonzero(full.price_move == -1)),
        "move_rate": float(np.mean(moving)),
        "models": models,
        "all_fits_converged": all(
            bool(model["converged"]) for model in models.values()
        ),
        "all_values_finite": bool(
            np.isfinite(np.asarray(all_model_values, dtype=np.float64)).all()
        ),
    }


def _median(values: list[float]) -> float:
    return float(np.median(np.asarray(values, dtype=np.float64)))


def _cell_key(truth: str, rho: float, censor_rate: float) -> str:
    return f"truth={truth},rho={rho:.2f},censor={censor_rate:.2f}"


def _summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for truth in TRUTHS:
        for rho in RHO_VALUES:
            for censor_rate in CENSOR_RATES:
                cell = [
                    record
                    for record in records
                    if record["truth"] == truth
                    and record["rho"] == rho
                    and record["censor_rate"] == censor_rate
                ]
                models: dict[str, Any] = {}
                for name in MODEL_NAMES:
                    n_coefficients = len(cell[0]["models"][name]["coefficients"])
                    models[name] = {
                        "median_coefficients": [
                            _median(
                                [
                                    float(
                                        record["models"][name]["coefficients"][index]
                                    )
                                    for record in cell
                                ]
                            )
                            for index in range(n_coefficients)
                        ],
                        "median_absolute_coefficients": [
                            _median(
                                [
                                    abs(
                                        float(
                                            record["models"][name]["coefficients"][
                                                index
                                            ]
                                        )
                                    )
                                    for record in cell
                                ]
                            )
                            for index in range(n_coefficients)
                        ],
                        "median_heldout_log_likelihood_nats_per_event": _median(
                            [
                                float(
                                    record["models"][name][
                                        "heldout_log_likelihood_nats_per_event"
                                    ]
                                )
                                for record in cell
                            ]
                        ),
                    }

                def ll(record: dict[str, Any], model: str) -> float:
                    return float(
                        record["models"][model][
                            "heldout_log_likelihood_nats_per_event"
                        ]
                    )

                pairwise = {
                    "combined_current_minus_observation_full": _median(
                        [
                            ll(record, "combined_current")
                            - ll(record, "observation_full")
                            for record in cell
                        ]
                    ),
                    "combined_current_minus_latent_current": _median(
                        [
                            ll(record, "combined_current")
                            - ll(record, "latent_current")
                            for record in cell
                        ]
                    ),
                    "observation_full_minus_latent_current": _median(
                        [
                            ll(record, "observation_full")
                            - ll(record, "latent_current")
                            for record in cell
                        ]
                    ),
                    "combined_permuted_minus_observation_full": _median(
                        [
                            ll(record, "combined_permuted")
                            - ll(record, "observation_full")
                            for record in cell
                        ]
                    ),
                    "absolute_combined_permuted_minus_observation_full": _median(
                        [
                            abs(
                                ll(record, "combined_permuted")
                                - ll(record, "observation_full")
                            )
                            for record in cell
                        ]
                    ),
                    "combined_current_minus_combined_lag3": _median(
                        [
                            ll(record, "combined_current")
                            - ll(record, "combined_lag3")
                            for record in cell
                        ]
                    ),
                }
                summary[_cell_key(truth, rho, censor_rate)] = {
                    "n_streams": len(cell),
                    "models": models,
                    "pairwise_heldout_nats_per_event": pairwise,
                    "median_move_rate": _median(
                        [float(record["move_rate"]) for record in cell]
                    ),
                    "minimum_up_moves": min(int(record["up_moves"]) for record in cell),
                    "minimum_down_moves": min(
                        int(record["down_moves"]) for record in cell
                    ),
                }
    return summary


def _hard_gates(
    records: list[dict[str, Any]], summary: dict[str, Any]
) -> dict[str, bool]:
    expected_streams = len(TRUTHS) * len(RHO_VALUES) * len(CENSOR_RATES) * N_REPLICATES
    stream_ids = [int(record["stream_id"]) for record in records]
    counts_and_fits = (
        len(records) == expected_streams
        and sorted(stream_ids) == list(range(expected_streams))
        and all(
            int(record["n_events"]) == N_EVENTS
            and int(record["n_train"]) + int(record["n_test"])
            == int(record["n_retained"])
            and bool(record["all_fits_converged"])
            and bool(record["all_values_finite"])
            for record in records
        )
    )
    state_exact = all(
        all(bool(value) for value in record["field_exact"].values())
        and bool(record["terminal_state_exact"])
        for record in records
    )
    reconstruction_and_moves = all(
        bool(record["reconstruction_exact"])
        and bool(record["queues_positive"])
        and bool(record["move_sign_exact"])
        and int(record["up_moves"]) > 0
        and int(record["down_moves"]) > 0
        for record in records
    ) and all(
        0.002 <= float(cell["median_move_rate"]) <= 0.050
        for cell in summary.values()
    )

    latent_incremental = True
    latent_parameter_recovery = True
    observation_only = True
    permuted_control = True
    lag_identification = True
    censoring_survival = True
    for rho in RHO_VALUES:
        for censor_rate in CENSOR_RATES:
            latent_cell = summary[
                _cell_key("latent_incremental", rho, censor_rate)
            ]
            latent_pairwise = latent_cell["pairwise_heldout_nats_per_event"]
            latent_cell_pass = (
                float(
                    latent_pairwise[
                        "combined_current_minus_observation_full"
                    ]
                )
                >= 0.015
                and float(
                    latent_pairwise[
                        "combined_current_minus_latent_current"
                    ]
                )
                >= 0.005
            )
            latent_incremental &= latent_cell_pass
            observation_cell = summary[
                _cell_key("observation_only", rho, censor_rate)
            ]
            observation_pairwise = observation_cell[
                "pairwise_heldout_nats_per_event"
            ]
            observation_latent = float(
                observation_cell["models"]["combined_current"][
                    "median_absolute_coefficients"
                ][1]
            )
            observation_cell_pass = (
                float(
                    observation_pairwise[
                        "observation_full_minus_latent_current"
                    ]
                )
                >= 0.020
                and float(
                    observation_pairwise[
                        "combined_current_minus_observation_full"
                    ]
                )
                <= 0.003
                and abs(observation_latent) <= 0.08
            )
            observation_only &= observation_cell_pass
            cell_permutation_pass = True
            for truth in TRUTHS:
                cell = summary[_cell_key(truth, rho, censor_rate)]
                pairwise = cell["pairwise_heldout_nats_per_event"]
                permuted_coefficient = float(
                    cell["models"]["combined_permuted"][
                        "median_absolute_coefficients"
                    ][1]
                )
                truth_permutation_pass = (
                    float(
                        pairwise[
                            "absolute_combined_permuted_minus_observation_full"
                        ]
                    )
                    <= 0.003
                    and permuted_coefficient <= 0.10
                )
                cell_permutation_pass &= truth_permutation_pass
                permuted_control &= truth_permutation_pass
            if rho == 0.60:
                lag_identification &= (
                    float(
                        latent_pairwise[
                            "combined_current_minus_combined_lag3"
                        ]
                    )
                    >= 0.010
                )
            if censor_rate == 0.20:
                censoring_survival &= (
                    latent_cell_pass
                    and observation_cell_pass
                    and cell_permutation_pass
                )

        zero_censor_cell = summary[_cell_key("latent_incremental", rho, 0.0)]
        latent_coefficient = float(
            zero_censor_cell["models"]["combined_current"][
                "median_coefficients"
            ][1]
        )
        matching_records = [
            record
            for record in records
            if record["truth"] == "latent_incremental"
            and record["rho"] == rho
            and record["censor_rate"] == 0.0
        ]
        positive_signs = sum(
            float(
                record["models"]["combined_current"]["coefficients"][1]
            )
            > 0.0
            for record in matching_records
        )
        latent_parameter_recovery &= (
            abs(latent_coefficient - 0.65) / 0.65 <= 0.15
            and positive_signs >= 7
        )
    return {
        "counts_fits_and_merge_complete": bool(counts_and_fits),
        "chunk_resume_state_exact": bool(state_exact),
        "reconstruction_and_price_moves": bool(reconstruction_and_moves),
        "latent_incremental_truth": bool(latent_incremental),
        "latent_parameter_recovery": bool(latent_parameter_recovery),
        "observation_only_truth": bool(observation_only),
        "permuted_control": bool(permuted_control),
        "lag3_identification_rho_0p60": bool(lag_identification),
        "censoring_survival": bool(censoring_survival),
    }


def _run_shard(args: argparse.Namespace) -> None:
    formal = not bool(args.smoke)
    if formal and args.n_shards != 2:
        raise ValueError("formal exp137 requires exactly two shards")
    if not 0 <= args.shard_index < args.n_shards:
        raise ValueError("invalid shard index")
    protocol = _protocol(formal=formal)
    specs = [
        spec
        for spec in _stream_specs(formal=formal)
        if int(spec["stream_id"]) % args.n_shards == args.shard_index
    ]
    started = time.perf_counter()
    records = [_run_stream(spec, formal=formal) for spec in specs]
    git_sha = _git_value("rev-parse", "HEAD")
    git_dirty = bool(_git_value("status", "--porcelain"))
    payload = {
        "experiment": 137,
        "title": "dynamic queue/price bridge with strong observation baselines",
        "formal": formal,
        "protocol": protocol,
        "protocol_hash": _protocol_hash(protocol),
        "shard": {
            "index": args.shard_index,
            "n_shards": args.n_shards,
            "stream_ids": [int(record["stream_id"]) for record in records],
        },
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "platform": platform.platform(),
            "hostname": platform.node(),
            "cpu_count": os.cpu_count(),
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
            "omp_num_threads": os.environ.get("OMP_NUM_THREADS"),
            "openblas_num_threads": os.environ.get("OPENBLAS_NUM_THREADS"),
            "mkl_num_threads": os.environ.get("MKL_NUM_THREADS"),
            "git_sha": git_sha,
            "git_dirty": git_dirty,
        },
        "elapsed_seconds": time.perf_counter() - started,
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "formal": formal,
                "shard": payload["shard"],
                "git_sha": git_sha,
                "git_dirty": git_dirty,
                "elapsed_seconds": payload["elapsed_seconds"],
                "local_structural_pass": all(
                    all(bool(value) for value in record["field_exact"].values())
                    and bool(record["terminal_state_exact"])
                    and bool(record["reconstruction_exact"])
                    for record in records
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )


def _merge(args: argparse.Namespace) -> None:
    if len(args.merge) != 2:
        raise ValueError("formal exp137 merge requires two shard files")
    shards = [json.loads(path.read_text()) for path in args.merge]
    if not all(bool(shard["formal"]) for shard in shards):
        raise ValueError("smoke output cannot enter the formal merge")
    protocol_hashes = {str(shard["protocol_hash"]) for shard in shards}
    if len(protocol_hashes) != 1:
        raise ValueError("shard protocol hashes differ")
    git_shas = {str(shard["environment"]["git_sha"]) for shard in shards}
    if git_shas != {args.expected_git_sha}:
        raise ValueError(f"unexpected shard git SHAs: {sorted(git_shas)}")
    if any(bool(shard["environment"]["git_dirty"]) for shard in shards):
        raise ValueError("dirty formal shard is forbidden")
    if any(
        shard["environment"]["cuda_visible_devices"] not in ("", "-1")
        or shard["environment"]["omp_num_threads"] != "1"
        or shard["environment"]["openblas_num_threads"] != "1"
        or shard["environment"]["mkl_num_threads"] != "1"
        for shard in shards
    ):
        raise ValueError("formal shard did not use the frozen CPU/thread settings")
    shard_indices = {int(shard["shard"]["index"]) for shard in shards}
    if shard_indices != {0, 1} or any(
        int(shard["shard"]["n_shards"]) != 2 for shard in shards
    ):
        raise ValueError("formal shard manifest is incomplete")
    records = [record for shard in shards for record in shard["records"]]
    stream_ids = [int(record["stream_id"]) for record in records]
    if len(stream_ids) != len(set(stream_ids)):
        raise ValueError("duplicate stream in formal merge")
    expected_streams = (
        len(TRUTHS) * len(RHO_VALUES) * len(CENSOR_RATES) * N_REPLICATES
    )
    if set(stream_ids) != set(range(expected_streams)):
        raise ValueError("missing or unexpected stream in formal merge")
    for shard in shards:
        manifest_ids = {int(value) for value in shard["shard"]["stream_ids"]}
        record_ids = {int(record["stream_id"]) for record in shard["records"]}
        shard_index = int(shard["shard"]["index"])
        if manifest_ids != record_ids or any(
            stream_id % 2 != shard_index for stream_id in record_ids
        ):
            raise ValueError("shard stream manifest does not match records")
    if any(int(record["n_events"]) != N_EVENTS for record in records):
        raise ValueError("unexpected formal event count")
    summary = _summarize(records)
    gates = _hard_gates(records, summary)
    payload = {
        "experiment": 137,
        "title": "dynamic queue/price bridge with strong observation baselines",
        "formal": True,
        "protocol": shards[0]["protocol"],
        "protocol_hash": shards[0]["protocol_hash"],
        "git_sha": args.expected_git_sha,
        "source_shards": [str(path) for path in args.merge],
        "source_environments": [shard["environment"] for shard in shards],
        "total_worker_seconds": sum(
            float(shard["elapsed_seconds"]) for shard in shards
        ),
        "summary": summary,
        "hard_gates": gates,
        "all_hard_gates_pass": all(gates.values()),
        "records": sorted(records, key=lambda record: int(record["stream_id"])),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "all_hard_gates_pass": payload["all_hard_gates_pass"],
                "hard_gates": gates,
                "summary": summary,
                "total_worker_seconds": payload["total_worker_seconds"],
            },
            indent=2,
            sort_keys=True,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--shard-index", type=int)
    parser.add_argument("--n-shards", type=int, default=2)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--merge", type=Path, nargs="+")
    parser.add_argument("--expected-git-sha")
    args = parser.parse_args()
    if args.merge:
        if not args.expected_git_sha:
            raise ValueError("--expected-git-sha is required for merge")
        _merge(args)
    else:
        if args.shard_index is None:
            raise ValueError("--shard-index is required for shard execution")
        _run_shard(args)


if __name__ == "__main__":
    main()
