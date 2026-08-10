"""Run and merge the preregistered external continuous-time baseline gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import resource
import subprocess
import time
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, TypeAlias, cast

import numpy as np
import pandas as pd
import scipy
from numpy.typing import NDArray

from ecomd.observation.continuous_time import (
    LOBSTER_MARK_NAMES,
    PointProcessFit,
    QueueFeatureDesign,
    branching_spectral_radius,
    build_queue_feature_design,
    circular_shift_queue_state,
    exponential_trace_design,
    fit_linear_hawkes_process,
    fit_poisson_process,
    fit_queue_hawkes_process,
    fit_queue_reactive_process,
    lobster_mark_ids,
    point_process_log_likelihood,
    simulate_exponential_hawkes_cluster,
    strictify_timestamps,
    time_rescaling_diagnostics,
)

FloatArray: TypeAlias = NDArray[np.float64]
IntArray: TypeAlias = NDArray[np.int64]

ROOT = Path(__file__).resolve().parents[2]
SAMPLE_ROOT = ROOT / "data" / "sample" / "LOBSTER"
DEFAULT_OUT = Path(__file__).with_name("EXTERNAL_CT_RESULTS.json")
ROOT_SEED = 138_202_608
SMOKE_ROOT_SEED = 138_202_609
PREREGISTRATION_COMMITS = ("e4fa739b",)
README_SHA256 = "fd97b5f49391e11ef52c023ef8f3ca156baac7441b4d52240339f60844244d5b"
TIE_POLICIES = ("nextafter", "capped_uniform")
BETAS = (0.1, 1.0, 10.0)
N_MARKS = len(LOBSTER_MARK_NAMES)
MODEL_NAMES = (
    "poisson",
    "queue_reactive",
    "hawkes_diagonal",
    "hawkes_full",
    "queue_hawkes_full",
    "queue_hawkes_shifted",
)
SMOKE_ROWS = 20_000
SYNTHETIC_REPLICATES = 8
SYNTHETIC_IMMIGRANT = (0.35, 0.25)
SYNTHETIC_BRANCHING = ((0.22, 0.08), (0.06, 0.18))
SYNTHETIC_BETA = 1.3
SYNTHETIC_BURN_START = -1_000.0
SYNTHETIC_END = 30_000.0


@dataclass(frozen=True)
class ExternalStreamSpec:
    symbol: str
    level: int
    filename: str
    sha256: str
    rows: int
    first_time: float
    last_time: float
    zero_increments: int
    archive_start: float
    archive_end: float
    shard: int


@dataclass(frozen=True)
class ExternalData:
    times: FloatArray
    event_type: IntArray
    direction: IntArray
    l1_books: IntArray
    archive_sha256: str
    readme_sha256: str


EXTERNAL_STREAMS = (
    ExternalStreamSpec(
        "AAPL",
        10,
        "LOBSTER_SampleFile_AAPL_2012-06-21_10.zip",
        "326839316d67d7819ca0541ffdf73cdb044d6ae4105cce0ef9c615e8848e9d43",
        400_391,
        34_200.004241176,
        57_599.913117637,
        16_062,
        34_200.0,
        57_600.0,
        1,
    ),
    ExternalStreamSpec(
        "AMZN",
        10,
        "LOBSTER_SampleFile_AMZN_2012-06-21_10.zip",
        "5cff62a609b27aef82285382ad646c4c2facc0a692a60bedda633de64c4aa54f",
        269_748,
        34_200.017459617,
        57_599.95935965,
        8_483,
        34_200.0,
        57_600.0,
        1,
    ),
    ExternalStreamSpec(
        "GOOG",
        10,
        "LOBSTER_SampleFile_GOOG_2012-06-21_10.zip",
        "2fa66b61c7c4d4cd3f19180aaa7f5937a26355f81b2ac8e4a84e36550e8dde4a",
        147_916,
        34_200.015105074,
        57_599.871751084,
        8_537,
        34_200.0,
        57_600.0,
        0,
    ),
    ExternalStreamSpec(
        "MSFT",
        10,
        "LOBSTER_SampleFile_MSFT_2012-06-21_10.zip",
        "0825e00ec83cb8ac8b53fd1efb7f2138b7848659e625c49621ebd9b55757be4c",
        668_765,
        34_200.01399412,
        57_599.907796528,
        57_203,
        34_200.0,
        57_600.0,
        1,
    ),
    ExternalStreamSpec(
        "SPY",
        50,
        "LOBSTER_SampleFile_SPY_2012-06-21_50.zip",
        "2d562be866e6285aa6ca1e37a9a2ec4a6503b156a230948879beaf2431c7b991",
        1_154_737,
        34_200.005929046,
        37_799.980010264,
        123_250,
        34_200.0,
        37_800.0,
        0,
    ),
)


def _git_value(*args: str) -> str:
    return subprocess.check_output(
        ("git", *args), cwd=ROOT, text=True, stderr=subprocess.DEVNULL
    ).strip()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _bytes_sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _protocol(*, formal: bool) -> dict[str, Any]:
    return {
        "experiment": 138,
        "formal": formal,
        "root_seed": ROOT_SEED if formal else SMOKE_ROOT_SEED,
        "external_streams": [asdict(spec) for spec in EXTERNAL_STREAMS],
        "max_rows": None if formal else SMOKE_ROWS,
        "readme_sha256": README_SHA256,
        "tie_policies": list(TIE_POLICIES),
        "marks": list(LOBSTER_MARK_NAMES),
        "betas": list(BETAS),
        "split": {"burn": 0.10, "train": 0.50, "test": 0.40},
        "models": list(MODEL_NAMES),
        "queue_state_shift_fraction": 1.0 / 3.0,
        "optimizer": {
            "method": "L-BFGS-B",
            "maxiter": 300,
            "ftol": 1e-10,
            "gtol": 1e-6,
            "maxls": 40,
        },
        "synthetic": {
            "n_replicates": SYNTHETIC_REPLICATES if formal else 2,
            "immigrant_rates": list(SYNTHETIC_IMMIGRANT),
            "branching": [list(row) for row in SYNTHETIC_BRANCHING],
            "beta": SYNTHETIC_BETA,
            "burn_start": SYNTHETIC_BURN_START if formal else -200.0,
            "end_time": SYNTHETIC_END if formal else 3_000.0,
        },
        "preregistration_commits": list(PREREGISTRATION_COMMITS),
    }


def _protocol_hash(protocol: dict[str, Any]) -> str:
    encoded = json.dumps(protocol, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _csv_members(archive: zipfile.ZipFile) -> tuple[str, str, str]:
    names = archive.namelist()
    message = next(
        (name for name in names if "message" in name.lower() and name.endswith(".csv")),
        None,
    )
    book = next(
        (name for name in names if "orderbook" in name.lower() and name.endswith(".csv")),
        None,
    )
    readme = next(
        (name for name in names if "readme" in name.lower() and name.endswith(".txt")),
        None,
    )
    if message is None or book is None or readme is None:
        raise ValueError("LOBSTER archive lacks a required member")
    return message, book, readme


def _load_external(spec: ExternalStreamSpec, *, formal: bool) -> ExternalData:
    path = SAMPLE_ROOT / spec.filename
    archive_sha256 = _sha256(path)
    if archive_sha256 != spec.sha256:
        raise RuntimeError(f"archive hash mismatch for {spec.symbol}")
    nrows = None if formal else SMOKE_ROWS
    with zipfile.ZipFile(path) as archive:
        message_name, book_name, readme_name = _csv_members(archive)
        readme_sha256 = _bytes_sha256(archive.read(readme_name))
        if readme_sha256 != README_SHA256:
            raise RuntimeError(f"ReadMe hash mismatch for {spec.symbol}")
        with archive.open(message_name) as stream:
            messages = pd.read_csv(
                stream,
                header=None,
                usecols=[0, 1, 5],
                dtype={0: np.float64, 1: np.int64, 5: np.int64},
                nrows=nrows,
            ).to_numpy()
        with archive.open(book_name) as stream:
            books = pd.read_csv(
                stream,
                header=None,
                usecols=[0, 1, 2, 3],
                dtype=np.int64,
                nrows=nrows,
            ).to_numpy(dtype=np.int64, copy=False)
    if messages.shape[0] != books.shape[0] or messages.shape[1] != 3:
        raise RuntimeError(f"message/book row mismatch for {spec.symbol}")
    if formal and messages.shape[0] != spec.rows:
        raise RuntimeError(f"formal row count mismatch for {spec.symbol}")
    return ExternalData(
        times=np.asarray(messages[:, 0], dtype=np.float64),
        event_type=np.asarray(messages[:, 1], dtype=np.int64),
        direction=np.asarray(messages[:, 2], dtype=np.int64),
        l1_books=np.asarray(books, dtype=np.int64),
        archive_sha256=archive_sha256,
        readme_sha256=readme_sha256,
    )


def _fit_to_dict(fit: PointProcessFit) -> dict[str, Any]:
    return {
        "name": fit.name,
        "base_kind": fit.base_kind,
        "base_coefficients": fit.base_coefficients.tolist(),
        "excitation": fit.excitation.tolist(),
        "success": fit.success,
        "iterations": list(fit.iterations),
        "gradient_inf_norm": fit.gradient_inf_norm,
        "messages": list(fit.messages),
    }


def _fit_policy(
    spec: ExternalStreamSpec,
    data: ExternalData,
    marks: IntArray,
    queue_design: QueueFeatureDesign,
    shifted_queue: FloatArray,
    *,
    policy: str,
    train_start: int,
    train_end: int,
    test_end: int,
) -> dict[str, Any]:
    adjusted, timestamp_diagnostics = strictify_timestamps(
        data.times, cast(Any, policy)
    )
    train_duration = adjusted[train_end - 1] - adjusted[train_start - 1]
    rate_scale = (train_end - train_start) / train_duration
    normalized_times = (adjusted - adjusted[0]) * rate_scale
    traces, integrals = exponential_trace_design(
        normalized_times, marks, N_MARKS, BETAS
    )
    n_trace = traces.shape[1]
    poisson = fit_poisson_process(
        normalized_times,
        marks,
        start=train_start,
        end=train_end,
        n_marks=N_MARKS,
        n_trace_features=n_trace,
    )
    queue = fit_queue_reactive_process(
        normalized_times,
        marks,
        queue_design.values,
        start=train_start,
        end=train_end,
        n_marks=N_MARKS,
        n_trace_features=n_trace,
    )
    diagonal = fit_linear_hawkes_process(
        normalized_times,
        marks,
        traces,
        integrals,
        start=train_start,
        end=train_end,
        n_marks=N_MARKS,
        n_scales=len(BETAS),
        diagonal=True,
        name="hawkes_diagonal",
    )
    full = fit_linear_hawkes_process(
        normalized_times,
        marks,
        traces,
        integrals,
        start=train_start,
        end=train_end,
        n_marks=N_MARKS,
        n_scales=len(BETAS),
        diagonal=False,
        name="hawkes_full",
    )
    combined = fit_queue_hawkes_process(
        normalized_times,
        marks,
        traces,
        integrals,
        queue_design.values,
        queue,
        full,
        start=train_start,
        end=train_end,
        n_marks=N_MARKS,
        name="queue_hawkes_full",
    )
    shifted_queue_fit = fit_queue_reactive_process(
        normalized_times,
        marks,
        shifted_queue,
        start=train_start,
        end=train_end,
        n_marks=N_MARKS,
        n_trace_features=n_trace,
        name="queue_reactive_shifted_internal",
    )
    shifted = fit_queue_hawkes_process(
        normalized_times,
        marks,
        traces,
        integrals,
        shifted_queue,
        shifted_queue_fit,
        full,
        start=train_start,
        end=train_end,
        n_marks=N_MARKS,
        name="queue_hawkes_shifted",
    )
    fits = {
        "poisson": poisson,
        "queue_reactive": queue,
        "hawkes_diagonal": diagonal,
        "hawkes_full": full,
        "queue_hawkes_full": combined,
        "queue_hawkes_shifted": shifted,
    }
    model_results: dict[str, Any] = {}
    for name, fit in fits.items():
        model_queue = shifted_queue if name == "queue_hawkes_shifted" else queue_design.values
        train_ll = point_process_log_likelihood(
            fit,
            normalized_times,
            marks,
            traces,
            integrals,
            model_queue,
            start=train_start,
            end=train_end,
        ) / (train_end - train_start)
        test_ll = point_process_log_likelihood(
            fit,
            normalized_times,
            marks,
            traces,
            integrals,
            model_queue,
            start=train_end,
            end=test_end,
        ) / (test_end - train_end)
        rescaling = time_rescaling_diagnostics(
            fit,
            normalized_times,
            marks,
            traces,
            integrals,
            model_queue,
            start=train_end,
            end=test_end,
        )
        model_results[name] = {
            "fit": _fit_to_dict(fit),
            "train_log_likelihood_nats_per_event": train_ll,
            "test_log_likelihood_nats_per_event": test_ll,
            "branching_spectral_radius": branching_spectral_radius(
                fit.excitation, n_marks=N_MARKS, n_scales=len(BETAS)
            ),
            "test_time_rescaling": asdict(rescaling),
        }

    def train(name: str) -> float:
        return float(model_results[name]["train_log_likelihood_nats_per_event"])

    def test(name: str) -> float:
        return float(model_results[name]["test_log_likelihood_nats_per_event"])

    nesting = {
        "hawkes_full_minus_hawkes_diagonal": train("hawkes_full")
        - train("hawkes_diagonal"),
        "hawkes_full_minus_poisson": train("hawkes_full") - train("poisson"),
        "queue_reactive_minus_poisson": train("queue_reactive") - train("poisson"),
        "queue_hawkes_full_minus_hawkes_full": train("queue_hawkes_full")
        - train("hawkes_full"),
        "queue_hawkes_full_minus_queue_reactive": train("queue_hawkes_full")
        - train("queue_reactive"),
    }
    heldout = {
        "queue_hawkes_full_minus_queue_hawkes_shifted": test("queue_hawkes_full")
        - test("queue_hawkes_shifted"),
        "queue_hawkes_full_minus_hawkes_full": test("queue_hawkes_full")
        - test("hawkes_full"),
        "hawkes_full_minus_poisson": test("hawkes_full") - test("poisson"),
        "queue_reactive_minus_poisson": test("queue_reactive") - test("poisson"),
    }
    all_finite = bool(
        np.isfinite(
            np.asarray(
                [
                    value
                    for result in model_results.values()
                    for value in (
                        result["train_log_likelihood_nats_per_event"],
                        result["test_log_likelihood_nats_per_event"],
                        result["branching_spectral_radius"],
                        result["fit"]["gradient_inf_norm"],
                        *result["test_time_rescaling"].values(),
                    )
                ],
                dtype=np.float64,
            )
        ).all()
    )
    return {
        "policy": policy,
        "timestamp_diagnostics": asdict(timestamp_diagnostics),
        "train_rate_scale_events_per_second": rate_scale,
        "models": model_results,
        "training_nesting_nats_per_event": nesting,
        "heldout_pairwise_nats_per_event": heldout,
        "all_values_finite": all_finite,
    }


def _run_external(spec: ExternalStreamSpec, *, formal: bool) -> dict[str, Any]:
    started = time.perf_counter()
    data = _load_external(spec, formal=formal)
    n_events = data.times.size
    train_start = int(0.10 * n_events)
    train_end = int(0.60 * n_events)
    test_end = n_events
    marks = lobster_mark_ids(data.event_type, data.direction)
    queue_design = build_queue_feature_design(
        data.times,
        data.l1_books,
        train_start=train_start,
        train_end=train_end,
        archive_start=spec.archive_start,
        archive_end=spec.archive_end,
    )
    shifted_queue = circular_shift_queue_state(
        queue_design.values,
        train_start=train_start,
        train_end=train_end,
        test_end=test_end,
    )
    raw_differences = np.diff(data.times)
    metadata_exact = (
        (not formal or n_events == spec.rows)
        and (not formal or float(data.times[0]) == spec.first_time)
        and (not formal or float(data.times[-1]) == spec.last_time)
        and (not formal or int(np.count_nonzero(raw_differences == 0.0)) == spec.zero_increments)
    )
    no_lookahead_exact = bool(
        np.array_equal(
            queue_design.source_indices[1:],
            np.arange(n_events - 1, dtype=np.int64),
        )
    )
    policies = {
        policy: _fit_policy(
            spec,
            data,
            marks,
            queue_design,
            shifted_queue,
            policy=policy,
            train_start=train_start,
            train_end=train_end,
            test_end=test_end,
        )
        for policy in TIE_POLICIES
    }
    return {
        "symbol": spec.symbol,
        "level": spec.level,
        "shard": spec.shard,
        "archive": str((SAMPLE_ROOT / spec.filename).relative_to(ROOT)),
        "archive_sha256": data.archive_sha256,
        "archive_sha256_exact": data.archive_sha256 == spec.sha256,
        "readme_sha256": data.readme_sha256,
        "readme_sha256_exact": data.readme_sha256 == README_SHA256,
        "n_events": int(n_events),
        "train_start": train_start,
        "train_end": train_end,
        "test_end": test_end,
        "raw_first_time": float(data.times[0]),
        "raw_last_time": float(data.times[-1]),
        "raw_negative_increments": int(np.count_nonzero(raw_differences < 0.0)),
        "raw_zero_increments": int(np.count_nonzero(raw_differences == 0.0)),
        "metadata_exact": metadata_exact,
        "mark_counts": np.bincount(marks, minlength=N_MARKS).tolist(),
        "all_messages_mapped": int(marks.size) == int(n_events),
        "queue_feature_means": queue_design.means.tolist(),
        "queue_feature_scales": queue_design.scales.tolist(),
        "no_lookahead_source_indices_exact": no_lookahead_exact,
        "policies": policies,
        "elapsed_seconds": time.perf_counter() - started,
    }


def _synthetic_seed(replicate: int, *, formal: bool) -> int:
    n_replicates = SYNTHETIC_REPLICATES if formal else 2
    root_seed = ROOT_SEED if formal else SMOKE_ROOT_SEED
    children = np.random.SeedSequence(root_seed).spawn(n_replicates)
    return int(children[replicate].generate_state(1, dtype=np.uint64)[0])


def _run_synthetic(replicate: int, *, formal: bool) -> dict[str, Any]:
    started = time.perf_counter()
    seed = _synthetic_seed(replicate, formal=formal)
    generator = np.random.default_rng(seed)
    burn_start = SYNTHETIC_BURN_START if formal else -200.0
    end_time = SYNTHETIC_END if formal else 3_000.0
    truth = np.asarray(SYNTHETIC_BRANCHING, dtype=np.float64)
    times, marks = simulate_exponential_hawkes_cluster(
        SYNTHETIC_IMMIGRANT,
        truth,
        SYNTHETIC_BETA,
        burn_start=burn_start,
        end_time=end_time,
        generator=generator,
    )
    train_start = int(0.10 * times.size)
    train_end = int(0.60 * times.size)
    traces, integrals = exponential_trace_design(times, marks, 2, (SYNTHETIC_BETA,))
    poisson = fit_poisson_process(
        times,
        marks,
        start=train_start,
        end=train_end,
        n_marks=2,
        n_trace_features=2,
    )
    hawkes = fit_linear_hawkes_process(
        times,
        marks,
        traces,
        integrals,
        start=train_start,
        end=train_end,
        n_marks=2,
        n_scales=1,
        diagonal=False,
        name="hawkes_full",
    )
    dummy_queue = np.ones((times.size, 1), dtype=np.float64)
    test_count = int(times.size - train_end)

    def test_likelihood(fit: PointProcessFit) -> float:
        return float(
            point_process_log_likelihood(
                fit,
                times,
                marks,
                traces,
                integrals,
                dummy_queue,
                start=train_end,
                end=times.size,
            )
        ) / test_count

    rescaling = time_rescaling_diagnostics(
        hawkes,
        times,
        marks,
        traces,
        integrals,
        dummy_queue,
        start=train_end,
        end=times.size,
    )
    return {
        "replicate": replicate,
        "shard": replicate % 2,
        "seed": seed,
        "n_events": int(times.size),
        "mark_counts": np.bincount(marks, minlength=2).tolist(),
        "train_start": train_start,
        "train_end": train_end,
        "immigrant_estimate": hawkes.base_coefficients.tolist(),
        "branching_estimate": hawkes.excitation.reshape(2, 2).tolist(),
        "hawkes_fit": _fit_to_dict(hawkes),
        "poisson_test_log_likelihood_nats_per_event": test_likelihood(poisson),
        "hawkes_test_log_likelihood_nats_per_event": test_likelihood(hawkes),
        "hawkes_minus_poisson_test_nats_per_event": test_likelihood(hawkes)
        - test_likelihood(poisson),
        "test_time_rescaling": asdict(rescaling),
        "all_values_finite": bool(
            np.isfinite(
                np.asarray(
                    (
                        *hawkes.base_coefficients,
                        *hawkes.excitation.reshape(-1),
                        test_likelihood(poisson),
                        test_likelihood(hawkes),
                        *asdict(rescaling).values(),
                    ),
                    dtype=np.float64,
                )
            ).all()
        ),
        "elapsed_seconds": time.perf_counter() - started,
    }


def _environment() -> dict[str, Any]:
    return {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scipy": scipy.__version__,
        "platform": platform.platform(),
        "hostname": platform.node(),
        "cpu_count": os.cpu_count(),
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "omp_num_threads": os.environ.get("OMP_NUM_THREADS"),
        "openblas_num_threads": os.environ.get("OPENBLAS_NUM_THREADS"),
        "mkl_num_threads": os.environ.get("MKL_NUM_THREADS"),
        "git_sha": _git_value("rev-parse", "HEAD"),
        "git_dirty": bool(_git_value("status", "--porcelain")),
    }


def _run_shard(args: argparse.Namespace) -> None:
    formal = not bool(args.smoke)
    if formal and args.n_shards != 2:
        raise ValueError("formal exp138 requires exactly two shards")
    if not 0 <= args.shard_index < args.n_shards:
        raise ValueError("invalid shard index")
    protocol = _protocol(formal=formal)
    started = time.perf_counter()
    real = [
        _run_external(spec, formal=formal)
        for spec in EXTERNAL_STREAMS
        if spec.shard == args.shard_index
    ]
    n_replicates = SYNTHETIC_REPLICATES if formal else 2
    synthetic = [
        _run_synthetic(replicate, formal=formal)
        for replicate in range(n_replicates)
        if replicate % args.n_shards == args.shard_index
    ]
    payload = {
        "experiment": 138,
        "title": "external continuous-time queue/Hawkes baseline gate",
        "formal": formal,
        "protocol": protocol,
        "protocol_hash": _protocol_hash(protocol),
        "shard": {
            "index": args.shard_index,
            "n_shards": args.n_shards,
            "symbols": [record["symbol"] for record in real],
            "synthetic_replicates": [record["replicate"] for record in synthetic],
        },
        "environment": _environment(),
        "peak_rss_raw": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "elapsed_seconds": time.perf_counter() - started,
        "real_records": real,
        "synthetic_records": synthetic,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "formal": formal,
                "shard": payload["shard"],
                "environment": payload["environment"],
                "elapsed_seconds": payload["elapsed_seconds"],
                "local_structural_pass": all(
                    record["metadata_exact"]
                    and record["no_lookahead_source_indices_exact"]
                    and all(
                        policy["all_values_finite"]
                        for policy in record["policies"].values()
                    )
                    for record in real
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )


def _median(values: list[float]) -> float:
    return float(np.median(np.asarray(values, dtype=np.float64)))


def _synthetic_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    immigrant_truth = np.asarray(SYNTHETIC_IMMIGRANT, dtype=np.float64)
    branching_truth = np.asarray(SYNTHETIC_BRANCHING, dtype=np.float64)
    immigrant_estimates = np.asarray(
        [record["immigrant_estimate"] for record in records], dtype=np.float64
    )
    branching_estimates = np.asarray(
        [record["branching_estimate"] for record in records], dtype=np.float64
    )
    immigrant_relative_error = np.median(
        np.abs(immigrant_estimates - immigrant_truth) / immigrant_truth, axis=0
    )
    branching_relative_error = np.median(
        np.abs(branching_estimates - branching_truth) / branching_truth, axis=0
    )
    return {
        "n_records": len(records),
        "immigrant_median_relative_error": immigrant_relative_error.tolist(),
        "branching_median_relative_error": branching_relative_error.tolist(),
        "median_hawkes_minus_poisson_test_nats_per_event": _median(
            [float(record["hawkes_minus_poisson_test_nats_per_event"]) for record in records]
        ),
        "median_rescaling_mean": _median(
            [float(record["test_time_rescaling"]["mean"]) for record in records]
        ),
        "median_rescaling_ks": _median(
            [float(record["test_time_rescaling"]["ks_statistic"]) for record in records]
        ),
        "median_absolute_rescaling_lag1": _median(
            [abs(float(record["test_time_rescaling"]["lag1_correlation"])) for record in records]
        ),
        "minimum_events": min(int(record["n_events"]) for record in records),
    }


def _real_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    policy_summary: dict[str, Any] = {}
    for policy in TIE_POLICIES:
        alignment = [
            float(
                record["policies"][policy]["heldout_pairwise_nats_per_event"][
                    "queue_hawkes_full_minus_queue_hawkes_shifted"
                ]
            )
            for record in records
        ]
        incremental = [
            float(
                record["policies"][policy]["heldout_pairwise_nats_per_event"][
                    "queue_hawkes_full_minus_hawkes_full"
                ]
            )
            for record in records
        ]
        policy_summary[policy] = {
            "median_aligned_minus_shifted_queue_hawkes": _median(alignment),
            "median_queue_hawkes_minus_hawkes": _median(incremental),
            "per_symbol_aligned_minus_shifted": {
                record["symbol"]: value
                for record, value in zip(records, alignment, strict=True)
            },
            "per_symbol_queue_hawkes_minus_hawkes": {
                record["symbol"]: value
                for record, value in zip(records, incremental, strict=True)
            },
        }
    return policy_summary


def _hard_gates(
    real_records: list[dict[str, Any]],
    synthetic_records: list[dict[str, Any]],
    synthetic_summary: dict[str, Any],
    real_summary: dict[str, Any],
) -> dict[str, bool]:
    manifest = (
        len(real_records) == len(EXTERNAL_STREAMS)
        and {record["symbol"] for record in real_records}
        == {spec.symbol for spec in EXTERNAL_STREAMS}
        and sum(int(record["n_events"]) for record in real_records)
        == sum(spec.rows for spec in EXTERNAL_STREAMS)
        and all(
            bool(record["archive_sha256_exact"])
            and bool(record["readme_sha256_exact"])
            and bool(record["metadata_exact"])
            for record in real_records
        )
    )
    timestamps_and_marks = all(
        int(record["raw_negative_increments"]) == 0
        and bool(record["all_messages_mapped"])
        and len(record["mark_counts"]) == N_MARKS
        and all(
            policy["timestamp_diagnostics"]["adjusted_minimum_interval"] > 0.0
            and policy["timestamp_diagnostics"]["raw_negative_increments"] == 0
            for policy in record["policies"].values()
        )
        for record in real_records
    )
    split_and_lookahead = all(
        bool(record["no_lookahead_source_indices_exact"])
        and int(record["train_start"]) == int(0.10 * int(record["n_events"]))
        and int(record["train_end"]) == int(0.60 * int(record["n_events"]))
        and int(record["test_end"]) == int(record["n_events"])
        for record in real_records
    )
    generated = (
        len(synthetic_records) == SYNTHETIC_REPLICATES
        and {int(record["replicate"]) for record in synthetic_records}
        == set(range(SYNTHETIC_REPLICATES))
        and all(
            bool(record["all_values_finite"])
            and (
                bool(record["hawkes_fit"]["success"])
                or float(record["hawkes_fit"]["gradient_inf_norm"]) <= 1e-5
            )
            for record in synthetic_records
        )
        and max(synthetic_summary["immigrant_median_relative_error"]) <= 0.15
        and float(
            np.max(
                np.asarray(
                    synthetic_summary["branching_median_relative_error"],
                    dtype=np.float64,
                )
            )
        )
        <= 0.25
        and synthetic_summary["median_hawkes_minus_poisson_test_nats_per_event"]
        >= 0.005
        and 0.90 <= synthetic_summary["median_rescaling_mean"] <= 1.10
        and synthetic_summary["median_rescaling_ks"] <= 0.05
        and synthetic_summary["median_absolute_rescaling_lag1"] <= 0.05
    )
    real_fits = all(
        bool(policy["all_values_finite"])
        and all(
            bool(model["fit"]["success"])
            or float(model["fit"]["gradient_inf_norm"]) <= 1e-5
            for model in policy["models"].values()
        )
        for record in real_records
        for policy in record["policies"].values()
    )
    nesting = all(
        min(float(value) for value in policy["training_nesting_nats_per_event"].values())
        >= -1e-7
        for record in real_records
        for policy in record["policies"].values()
    )
    aligned_queue = all(
        float(real_summary[policy]["median_aligned_minus_shifted_queue_hawkes"])
        >= 0.0
        for policy in TIE_POLICIES
    )
    primary_increment = float(
        real_summary["nextafter"]["median_queue_hawkes_minus_hawkes"]
    )
    sensitivity_increment = float(
        real_summary["capped_uniform"]["median_queue_hawkes_minus_hawkes"]
    )
    tie_robustness = (
        np.sign(primary_increment) == np.sign(sensitivity_increment)
        and abs(primary_increment - sensitivity_increment) <= 0.002
    )
    complete_reporting = all(
        set(record["policies"]) == set(TIE_POLICIES)
        and all(set(policy["models"]) == set(MODEL_NAMES) for policy in record["policies"].values())
        for record in real_records
    )
    return {
        "manifest_and_provenance_exact": bool(manifest),
        "timestamps_and_external_marks_exact": bool(timestamps_and_marks),
        "split_and_no_lookahead_exact": bool(split_and_lookahead),
        "generated_hawkes_recovery": bool(generated),
        "real_fits_finite_and_converged": bool(real_fits),
        "training_nesting": bool(nesting),
        "aligned_queue_control": bool(aligned_queue),
        "tie_policy_robustness": bool(tie_robustness),
        "complete_unfavorable_reporting": bool(complete_reporting),
    }


def _merge(args: argparse.Namespace) -> None:
    if len(args.merge) != 2:
        raise ValueError("formal exp138 merge requires two shard files")
    shards = [json.loads(path.read_text()) for path in args.merge]
    if not all(bool(shard["formal"]) for shard in shards):
        raise ValueError("smoke output cannot enter formal merge")
    if {str(shard["protocol_hash"]) for shard in shards}.__len__() != 1:
        raise ValueError("shard protocol hashes differ")
    if {str(shard["environment"]["git_sha"]) for shard in shards} != {
        args.expected_git_sha
    }:
        raise ValueError("formal shard git SHA mismatch")
    if any(bool(shard["environment"]["git_dirty"]) for shard in shards):
        raise ValueError("dirty formal shard is forbidden")
    if any(
        shard["environment"]["cuda_visible_devices"] not in ("", "-1")
        or shard["environment"]["omp_num_threads"] != "1"
        or shard["environment"]["openblas_num_threads"] != "1"
        or shard["environment"]["mkl_num_threads"] != "1"
        for shard in shards
    ):
        raise ValueError("formal shard did not use frozen CPU settings")
    if {int(shard["shard"]["index"]) for shard in shards} != {0, 1} or any(
        int(shard["shard"]["n_shards"]) != 2 for shard in shards
    ):
        raise ValueError("formal shard manifest is incomplete")
    real_records = [record for shard in shards for record in shard["real_records"]]
    synthetic_records = [
        record for shard in shards for record in shard["synthetic_records"]
    ]
    if len({record["symbol"] for record in real_records}) != len(real_records):
        raise ValueError("duplicate real stream")
    if len({record["replicate"] for record in synthetic_records}) != len(
        synthetic_records
    ):
        raise ValueError("duplicate synthetic replicate")
    for record in real_records:
        expected = next(spec for spec in EXTERNAL_STREAMS if spec.symbol == record["symbol"])
        if int(record["shard"]) != expected.shard:
            raise ValueError("real stream is in the wrong shard")
    if any(int(record["shard"]) != int(record["replicate"]) % 2 for record in synthetic_records):
        raise ValueError("synthetic replicate is in the wrong shard")
    real_records.sort(key=lambda record: str(record["symbol"]))
    synthetic_records.sort(key=lambda record: int(record["replicate"]))
    synthetic_summary = _synthetic_summary(synthetic_records)
    real_summary = _real_summary(real_records)
    gates = _hard_gates(
        real_records, synthetic_records, synthetic_summary, real_summary
    )
    payload = {
        "experiment": 138,
        "title": "external continuous-time queue/Hawkes baseline gate",
        "formal": True,
        "protocol": shards[0]["protocol"],
        "protocol_hash": shards[0]["protocol_hash"],
        "git_sha": args.expected_git_sha,
        "source_shards": [str(path) for path in args.merge],
        "source_environments": [shard["environment"] for shard in shards],
        "total_worker_seconds": sum(float(shard["elapsed_seconds"]) for shard in shards),
        "synthetic_summary": synthetic_summary,
        "real_summary": real_summary,
        "hard_gates": gates,
        "all_hard_gates_pass": all(gates.values()),
        "real_records": real_records,
        "synthetic_records": synthetic_records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "all_hard_gates_pass": payload["all_hard_gates_pass"],
                "hard_gates": gates,
                "synthetic_summary": synthetic_summary,
                "real_summary": real_summary,
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
