"""Run and merge the preregistered queue--Hawkes optimizer repair gate."""

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
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, TypeAlias, cast

import numpy as np
import pandas as pd
import scipy
from numpy.typing import NDArray

from ecomd.observation.continuous_time import (
    LOBSTER_MARK_NAMES,
    OptimizerStageResult,
    PointProcessFit,
    bound_constrained_kkt_diagnostics,
    build_queue_feature_design,
    exponential_trace_design,
    fit_linear_hawkes_process,
    fit_queue_reactive_process,
    hawkes_objective_gradient,
    lobster_mark_ids,
    queue_hawkes_objective_gradient,
    run_lbfgsb_stage,
    simulate_exponential_hawkes_cluster,
    strictify_timestamps,
)

FloatArray: TypeAlias = NDArray[np.float64]
IntArray: TypeAlias = NDArray[np.int64]
Objective: TypeAlias = Callable[[FloatArray], tuple[float, FloatArray]]
Bound: TypeAlias = tuple[float | None, float | None]

ROOT = Path(__file__).resolve().parents[2]
SAMPLE_ROOT = ROOT / "data" / "sample" / "LOBSTER"
DEFAULT_OUT = Path(__file__).with_name("OPTIMIZER_KKT_RESULTS.json")
PREREGISTRATION_COMMITS = ("338e0165", "732e1e7b")
README_SHA256 = "fd97b5f49391e11ef52c023ef8f3ca156baac7441b4d52240339f60844244d5b"
BETAS = (0.1, 1.0, 10.0)
TIE_POLICIES = ("nextafter", "capped_uniform")
N_MARKS = len(LOBSTER_MARK_NAMES)
SMOKE_ROWS = 20_000
SENTINEL_LIMIT = 1_024
ROOT_SEED = 139_202_608
SMOKE_ROOT_SEED = 139_202_610
ANCHOR_SEED = 139_202_609
SYNTHETIC_REPLICATES = 8
SYNTHETIC_IMMIGRANT = (0.35, 0.25)
SYNTHETIC_BRANCHING = ((0.22, 0.08), (0.06, 0.18))
SYNTHETIC_BETA = 1.3
SYNTHETIC_BURN_START = -1_000.0
SYNTHETIC_END = 30_000.0
ANCHOR_BURN_START = -500.0
ANCHOR_END = 5_000.0
ACTIVE_TOLERANCE = 1e-10
SELECTION_KKT = 1e-5
STOP_KKT = 1e-7
REFERENCE_SELECTION_KKT = 1e-8
REFERENCE_STOP_KKT = 1e-9
LEGACY_OPTIONS = {
    "maxiter": 300,
    "ftol": 1e-10,
    "gtol": 1e-6,
    "maxls": 40,
    "maxcor": 10,
}
REFINEMENT_OPTIONS = {
    "maxiter": 500,
    "ftol": 1e-15,
    "gtol": 1e-8,
    "maxls": 80,
    "maxcor": 20,
}
MAX_REFINEMENT_STAGES = 6


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
class TrainingPrefix:
    raw_times: FloatArray
    event_type: IntArray
    direction: IntArray
    l1_books: IntArray
    sentinel_times: FloatArray
    total_rows: int
    train_start: int
    train_end: int
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
    return subprocess.check_output(("git", *args), cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _bytes_sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _protocol(*, formal: bool) -> dict[str, Any]:
    return {
        "experiment": 139,
        "formal": formal,
        "preregistration_commits": list(PREREGISTRATION_COMMITS),
        "external_streams": [asdict(spec) for spec in EXTERNAL_STREAMS],
        "readme_sha256": README_SHA256,
        "maximum_source_rows": None if formal else SMOKE_ROWS,
        "timestamp_sentinel_limit": SENTINEL_LIMIT,
        "marks": list(LOBSTER_MARK_NAMES),
        "betas": list(BETAS),
        "tie_policies": list(TIE_POLICIES),
        "split": {"burn": 0.10, "training": 0.50, "unused": 0.40},
        "active_tolerance": ACTIVE_TOLERANCE,
        "selection_kkt": SELECTION_KKT,
        "stop_kkt": STOP_KKT,
        "reference_selection_kkt": REFERENCE_SELECTION_KKT,
        "reference_stop_kkt": REFERENCE_STOP_KKT,
        "legacy_options": LEGACY_OPTIONS,
        "refinement_options": REFINEMENT_OPTIONS,
        "maximum_refinement_stages": MAX_REFINEMENT_STAGES,
        "generated": {
            "root_seed": ROOT_SEED if formal else SMOKE_ROOT_SEED,
            "replicates": SYNTHETIC_REPLICATES if formal else 2,
            "immigrant": list(SYNTHETIC_IMMIGRANT),
            "branching": [list(row) for row in SYNTHETIC_BRANCHING],
            "beta": SYNTHETIC_BETA,
            "burn_start": SYNTHETIC_BURN_START if formal else -200.0,
            "end": SYNTHETIC_END if formal else 3_000.0,
        },
        "cross_node_anchor": {
            "seed": ANCHOR_SEED,
            "burn_start": ANCHOR_BURN_START,
            "end": ANCHOR_END,
        },
        "finite_difference": {"step": 1e-6, "maximum_error": 5e-7},
        "bound_case_maximum_error": 1e-15,
    }


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


def _load_training_prefix(spec: ExternalStreamSpec, *, formal: bool) -> TrainingPrefix:
    path = SAMPLE_ROOT / spec.filename
    archive_sha256 = _sha256(path)
    if archive_sha256 != spec.sha256:
        raise RuntimeError(f"archive hash mismatch for {spec.symbol}")
    total_rows = spec.rows if formal else min(SMOKE_ROWS, spec.rows)
    train_start = int(0.10 * total_rows)
    train_end = int(0.60 * total_rows)
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
                nrows=train_end,
            ).to_numpy()
        with archive.open(book_name) as stream:
            books = pd.read_csv(
                stream,
                header=None,
                usecols=[0, 1, 2, 3],
                dtype=np.int64,
                nrows=train_end,
            ).to_numpy(dtype=np.int64, copy=False)
        with archive.open(message_name) as stream:
            timestamp_values = pd.read_csv(
                stream,
                header=None,
                usecols=[0],
                dtype={0: np.float64},
                nrows=train_end + SENTINEL_LIMIT,
            ).to_numpy(dtype=np.float64, copy=False)[:, 0]
    if messages.shape != (train_end, 3) or books.shape != (train_end, 4):
        raise RuntimeError(f"training-prefix shape mismatch for {spec.symbol}")
    sentinel = timestamp_values[train_end:]
    if sentinel.size < 1:
        raise RuntimeError(f"timestamp sentinel is absent for {spec.symbol}")
    return TrainingPrefix(
        raw_times=np.asarray(messages[:, 0], dtype=np.float64),
        event_type=np.asarray(messages[:, 1], dtype=np.int64),
        direction=np.asarray(messages[:, 2], dtype=np.int64),
        l1_books=np.asarray(books, dtype=np.int64),
        sentinel_times=np.asarray(sentinel, dtype=np.float64),
        total_rows=total_rows,
        train_start=train_start,
        train_end=train_end,
        archive_sha256=archive_sha256,
        readme_sha256=readme_sha256,
    )


def _strict_training_times(prefix: TrainingPrefix, policy: str) -> tuple[FloatArray, dict[str, Any]]:
    last = float(prefix.raw_times[-1])
    equal_count = 0
    while equal_count < prefix.sentinel_times.size and float(prefix.sentinel_times[equal_count]) == last:
        equal_count += 1
    if equal_count >= prefix.sentinel_times.size:
        raise RuntimeError("timestamp sentinel did not reach a distinct time")
    sentinel_count = equal_count + 1
    augmented = np.concatenate((prefix.raw_times, prefix.sentinel_times[:sentinel_count]))
    adjusted, diagnostics = strictify_timestamps(augmented, cast(Any, policy))
    training = adjusted[: prefix.train_end]
    if np.any(np.diff(training) <= 0.0):
        raise RuntimeError("training timestamps are not strictly increasing")
    return training, {
        "policy": policy,
        "timestamp_sentinel_rows": sentinel_count,
        "source_zero_increments": int(np.count_nonzero(np.diff(prefix.raw_times) == 0.0)),
        "training_adjusted_minimum_interval": float(np.min(np.diff(training))),
        "training_maximum_adjustment": float(np.max(training - prefix.raw_times)),
        "augmented_largest_tie_group": diagnostics.largest_group,
    }


def _shift_training_queue(features: FloatArray, *, train_start: int, train_end: int) -> FloatArray:
    values = np.asarray(features, dtype=np.float64)
    if values.ndim != 2 or values.shape[1] != 7 or train_end != values.shape[0]:
        raise ValueError("training queue design has the wrong shape")
    shifted = values.copy()
    length = train_end - train_start
    offset = length // 3
    if offset < 1:
        raise ValueError("training shift is empty")
    shifted[train_start:train_end, 1:5] = np.roll(values[train_start:train_end, 1:5], shift=offset, axis=0)
    return shifted


def _stage_to_dict(result: OptimizerStageResult, index: int) -> dict[str, Any]:
    return {
        "index": index,
        "parameters": result.parameters.tolist(),
        "objective": result.objective,
        "scipy_success": result.scipy_success,
        "iterations": result.iterations,
        "function_evaluations": result.function_evaluations,
        "raw_gradient_inf_norm": result.raw_gradient_inf_norm,
        "projected_gradient_inf_norm": result.projected_gradient_inf_norm,
        "complementarity_inf_norm": result.complementarity_inf_norm,
        "active_bounds": result.active_bounds,
        "message": result.message,
    }


def _run_start(
    objective: Objective,
    initial: FloatArray,
    bounds: Sequence[Bound],
    *,
    selection_kkt: float,
    stop_kkt: float,
) -> dict[str, Any]:
    legacy = run_lbfgsb_stage(
        objective,
        initial,
        bounds,
        maxiter=300,
        ftol=1e-10,
        gtol=1e-6,
        maxls=40,
        maxcor=10,
        active_tolerance=ACTIVE_TOLERANCE,
    )
    endpoints = [legacy]
    current = legacy.parameters
    while endpoints[-1].projected_gradient_inf_norm > stop_kkt and len(endpoints) <= MAX_REFINEMENT_STAGES:
        refined = run_lbfgsb_stage(
            objective,
            current,
            bounds,
            maxiter=500,
            ftol=1e-15,
            gtol=1e-8,
            maxls=80,
            maxcor=20,
            active_tolerance=ACTIVE_TOLERANCE,
        )
        endpoints.append(refined)
        current = refined.parameters
    qualified = [
        (index, endpoint)
        for index, endpoint in enumerate(endpoints)
        if endpoint.projected_gradient_inf_norm <= selection_kkt
    ]
    pool = qualified or list(enumerate(endpoints))
    selected_index, selected = min(pool, key=lambda item: item[1].objective)
    return {
        "legacy": _stage_to_dict(legacy, 0),
        "refinements": [
            _stage_to_dict(endpoint, index) for index, endpoint in enumerate(endpoints[1:], start=1)
        ],
        "selected": _stage_to_dict(selected, selected_index),
        "qualified": bool(qualified),
        "stages_run": len(endpoints),
    }


def _fit_to_dict(fit: PointProcessFit) -> dict[str, Any]:
    return {
        "base_kind": fit.base_kind,
        "base_coefficients": fit.base_coefficients.tolist(),
        "excitation": fit.excitation.tolist(),
        "success": fit.success,
        "iterations": list(fit.iterations),
        "raw_gradient_inf_norm": fit.gradient_inf_norm,
        "messages": list(fit.messages),
    }


def _fit_real_design(
    times: FloatArray,
    marks: IntArray,
    traces: FloatArray,
    integrals: FloatArray,
    queue_features: FloatArray,
    queue_fit: PointProcessFit,
    hawkes_fit: PointProcessFit,
    *,
    train_start: int,
    train_end: int,
    design_name: str,
) -> dict[str, Any]:
    intervals = times[train_start:train_end] - times[train_start - 1 : train_end - 1]
    window_marks = marks[train_start:train_end]
    window_traces = traces[train_start:train_end]
    window_integrals = integrals[train_start:train_end]
    queue = queue_features[train_start:train_end]
    integrated = np.sum(window_integrals, axis=0)
    duration = float(np.sum(intervals))
    trace_scales = np.maximum(integrated / duration, 1e-8)
    n_queue = queue.shape[1]
    n_trace = traces.shape[1]
    bounds: list[Bound] = [
        *([(None, None)] * n_queue),
        *([(0.0, None)] * n_trace),
    ]
    coefficients = np.empty((N_MARKS, n_queue), dtype=np.float64)
    excitation = np.empty((N_MARKS, n_trace), dtype=np.float64)
    targets: list[dict[str, Any]] = []
    for target in range(N_MARKS):
        target_mask = window_marks == target
        target_queue = queue[target_mask]
        target_traces = window_traces[target_mask] / trace_scales
        objective = cast(
            Objective,
            lambda values, target_queue=target_queue, target_traces=target_traces: (
                queue_hawkes_objective_gradient(
                    values,
                    target_queue,
                    target_traces,
                    queue,
                    intervals,
                    integrated / trace_scales,
                    train_end - train_start,
                )
            ),
        )
        queue_start = np.concatenate(
            (queue_fit.base_coefficients[target], np.zeros(n_trace, dtype=np.float64))
        )
        hawkes_theta = np.zeros(n_queue, dtype=np.float64)
        hawkes_theta[0] = np.log(max(float(hawkes_fit.base_coefficients[target]), 1e-12))
        hawkes_start = np.concatenate((hawkes_theta, hawkes_fit.excitation[target] * trace_scales))
        starts = {
            "queue": _run_start(
                objective,
                queue_start,
                bounds,
                selection_kkt=SELECTION_KKT,
                stop_kkt=STOP_KKT,
            ),
            "hawkes": _run_start(
                objective,
                hawkes_start,
                bounds,
                selection_kkt=SELECTION_KKT,
                stop_kkt=STOP_KKT,
            ),
        }
        qualified_starts = [(name, start) for name, start in starts.items() if bool(start["qualified"])]
        pool = qualified_starts or list(starts.items())
        selected_name, selected_start = min(pool, key=lambda item: float(item[1]["selected"]["objective"]))
        selected = cast(dict[str, Any], selected_start["selected"])
        selected_parameters = np.asarray(selected["parameters"], dtype=np.float64)
        coefficients[target] = selected_parameters[:n_queue]
        excitation[target] = selected_parameters[n_queue:] / trace_scales
        legacy_objective = min(float(start["legacy"]["objective"]) for start in starts.values())
        both_qualified = all(bool(start["qualified"]) for start in starts.values())
        start_gap = (
            abs(
                float(starts["queue"]["selected"]["objective"])
                - float(starts["hawkes"]["selected"]["objective"])
            )
            if both_qualified
            else None
        )
        targets.append(
            {
                "target": target,
                "mark": LOBSTER_MARK_NAMES[target],
                "starts": starts,
                "selected_start": selected_name,
                "selected": selected,
                "legacy_objective": legacy_objective,
                "objective_improvement": legacy_objective - float(selected["objective"]),
                "both_starts_qualified": both_qualified,
                "start_objective_gap": start_gap,
            }
        )
    selected_objectives = [float(target["selected"]["objective"]) for target in targets]
    return {
        "design": design_name,
        "targets": targets,
        "base_coefficients": coefficients.tolist(),
        "excitation": excitation.tolist(),
        "training_log_likelihood_nats_per_interval": -float(
            np.sum(np.asarray(selected_objectives, dtype=np.float64))
        ),
        "maximum_selected_projected_kkt": max(
            float(target["selected"]["projected_gradient_inf_norm"]) for target in targets
        ),
        "maximum_selected_complementarity": max(
            float(target["selected"]["complementarity_inf_norm"]) for target in targets
        ),
    }


def _run_external(spec: ExternalStreamSpec, *, formal: bool) -> dict[str, Any]:
    started = time.perf_counter()
    prefix = _load_training_prefix(spec, formal=formal)
    marks = lobster_mark_ids(prefix.event_type, prefix.direction)
    queue_design = build_queue_feature_design(
        prefix.raw_times,
        prefix.l1_books,
        train_start=prefix.train_start,
        train_end=prefix.train_end,
        archive_start=spec.archive_start,
        archive_end=spec.archive_end,
    )
    shifted = _shift_training_queue(
        queue_design.values,
        train_start=prefix.train_start,
        train_end=prefix.train_end,
    )
    policies: dict[str, Any] = {}
    for policy in TIE_POLICIES:
        adjusted, timestamp_diagnostics = _strict_training_times(prefix, policy)
        duration = adjusted[prefix.train_end - 1] - adjusted[prefix.train_start - 1]
        rate_scale = (prefix.train_end - prefix.train_start) / duration
        normalized = (adjusted - adjusted[0]) * rate_scale
        traces, integrals = exponential_trace_design(normalized, marks, N_MARKS, BETAS)
        n_trace = traces.shape[1]
        queue_fit = fit_queue_reactive_process(
            normalized,
            marks,
            queue_design.values,
            start=prefix.train_start,
            end=prefix.train_end,
            n_marks=N_MARKS,
            n_trace_features=n_trace,
        )
        shifted_queue_fit = fit_queue_reactive_process(
            normalized,
            marks,
            shifted,
            start=prefix.train_start,
            end=prefix.train_end,
            n_marks=N_MARKS,
            n_trace_features=n_trace,
            name="queue_reactive_shifted_internal",
        )
        hawkes_fit = fit_linear_hawkes_process(
            normalized,
            marks,
            traces,
            integrals,
            start=prefix.train_start,
            end=prefix.train_end,
            n_marks=N_MARKS,
            n_scales=len(BETAS),
            diagonal=False,
            name="hawkes_full",
        )
        policies[policy] = {
            "timestamp": timestamp_diagnostics,
            "rate_scale_events_per_second": rate_scale,
            "seed_fits": {
                "queue": _fit_to_dict(queue_fit),
                "shifted_queue": _fit_to_dict(shifted_queue_fit),
                "hawkes": _fit_to_dict(hawkes_fit),
            },
            "designs": {
                "aligned": _fit_real_design(
                    normalized,
                    marks,
                    traces,
                    integrals,
                    queue_design.values,
                    queue_fit,
                    hawkes_fit,
                    train_start=prefix.train_start,
                    train_end=prefix.train_end,
                    design_name="aligned",
                ),
                "shifted": _fit_real_design(
                    normalized,
                    marks,
                    traces,
                    integrals,
                    shifted,
                    shifted_queue_fit,
                    hawkes_fit,
                    train_start=prefix.train_start,
                    train_end=prefix.train_end,
                    design_name="shifted",
                ),
            },
        }
    return {
        "symbol": spec.symbol,
        "level": spec.level,
        "shard": spec.shard,
        "archive": str((SAMPLE_ROOT / spec.filename).relative_to(ROOT)),
        "archive_sha256": prefix.archive_sha256,
        "archive_sha256_exact": prefix.archive_sha256 == spec.sha256,
        "readme_sha256": prefix.readme_sha256,
        "readme_sha256_exact": prefix.readme_sha256 == README_SHA256,
        "source_rows": prefix.total_rows,
        "train_start": prefix.train_start,
        "train_end": prefix.train_end,
        "materialized_message_rows": int(prefix.raw_times.size),
        "materialized_book_rows": int(prefix.l1_books.shape[0]),
        "maximum_materialized_message_row": int(prefix.raw_times.size - 1),
        "maximum_materialized_book_row": int(prefix.l1_books.shape[0] - 1),
        "timestamp_sentinel_capacity": int(prefix.sentinel_times.size),
        "mark_counts_in_materialized_prefix": np.bincount(marks, minlength=N_MARKS).tolist(),
        "queue_source_indices_exact": bool(
            np.array_equal(
                queue_design.source_indices[1:],
                np.arange(prefix.train_end - 1, dtype=np.int64),
            )
        ),
        "policies": policies,
        "elapsed_seconds": time.perf_counter() - started,
    }


def _direct_hawkes_reference(
    times: FloatArray,
    marks: IntArray,
    traces: FloatArray,
    integrals: FloatArray,
    *,
    start: int,
    end: int,
) -> list[dict[str, Any]]:
    intervals = times[start:end] - times[start - 1 : end - 1]
    window_marks = marks[start:end]
    window_traces = traces[start:end]
    integrated = np.sum(integrals[start:end], axis=0)
    duration = float(np.sum(intervals))
    trace_scales = np.maximum(integrated / duration, 1e-8)
    references: list[dict[str, Any]] = []
    for target in range(2):
        target_features = window_traces[window_marks == target] / trace_scales
        target_integrated = integrated / trace_scales
        rate = target_features.shape[0] / duration
        objective = cast(
            Objective,
            lambda values, target_features=target_features, target_integrated=target_integrated: (
                hawkes_objective_gradient(
                    values,
                    target_features,
                    target_integrated,
                    duration,
                    end - start,
                )
            ),
        )
        initial = np.concatenate(([max(rate, 1e-10)], np.zeros(trace_scales.size, dtype=np.float64)))
        bounds: list[Bound] = [
            (1e-12, None),
            *([(0.0, None)] * trace_scales.size),
        ]
        run = _run_start(
            objective,
            initial,
            bounds,
            selection_kkt=REFERENCE_SELECTION_KKT,
            stop_kkt=REFERENCE_STOP_KKT,
        )
        selected = cast(dict[str, Any], run["selected"])
        parameters = np.asarray(selected["parameters"], dtype=np.float64)
        references.append(
            {
                "target": target,
                "run": run,
                "base": float(parameters[0]),
                "excitation": (parameters[1:] / trace_scales).tolist(),
                "trace_scales": trace_scales.tolist(),
            }
        )
    return references


def _combined_equivalence(
    times: FloatArray,
    marks: IntArray,
    traces: FloatArray,
    integrals: FloatArray,
    references: list[dict[str, Any]],
    *,
    start: int,
    end: int,
) -> list[dict[str, Any]]:
    intervals = times[start:end] - times[start - 1 : end - 1]
    window_marks = marks[start:end]
    window_traces = traces[start:end]
    integrated = np.sum(integrals[start:end], axis=0)
    duration = float(np.sum(intervals))
    trace_scales = np.maximum(integrated / duration, 1e-8)
    queue: FloatArray = np.ones((end - start, 1), dtype=np.float64)
    bounds: list[Bound] = [
        (None, None),
        *([(0.0, None)] * trace_scales.size),
    ]
    results: list[dict[str, Any]] = []
    for target, reference in enumerate(references):
        target_mask = window_marks == target
        target_queue = queue[target_mask]
        target_traces = window_traces[target_mask] / trace_scales
        objective = cast(
            Objective,
            lambda values, target_queue=target_queue, target_traces=target_traces: (
                queue_hawkes_objective_gradient(
                    values,
                    target_queue,
                    target_traces,
                    queue,
                    intervals,
                    integrated / trace_scales,
                    end - start,
                )
            ),
        )
        rate = target_queue.shape[0] / duration
        queue_start = np.concatenate(
            ([np.log(max(rate, 1e-12))], np.zeros(trace_scales.size, dtype=np.float64))
        )
        hawkes_start = np.concatenate(
            (
                [np.log(max(float(reference["base"]), 1e-12))],
                np.asarray(reference["excitation"], dtype=np.float64) * trace_scales,
            )
        )
        starts = {
            "queue": _run_start(
                objective,
                queue_start,
                bounds,
                selection_kkt=STOP_KKT,
                stop_kkt=STOP_KKT,
            ),
            "hawkes": _run_start(
                objective,
                hawkes_start,
                bounds,
                selection_kkt=STOP_KKT,
                stop_kkt=STOP_KKT,
            ),
        }
        reference_objective = float(reference["run"]["selected"]["objective"])
        results.append(
            {
                "target": target,
                "reference_objective": reference_objective,
                "starts": starts,
                "objective_differences": {
                    name: float(start_result["selected"]["objective"]) - reference_objective
                    for name, start_result in starts.items()
                },
            }
        )
    return results


def _synthetic_seed(replicate: int, *, formal: bool) -> int:
    count = SYNTHETIC_REPLICATES if formal else 2
    root = ROOT_SEED if formal else SMOKE_ROOT_SEED
    children = np.random.SeedSequence(root).spawn(count)
    return int(children[replicate].generate_state(1, dtype=np.uint64)[0])


def _run_generated(
    replicate: int,
    *,
    formal: bool,
    anchor: bool = False,
) -> dict[str, Any]:
    started = time.perf_counter()
    seed = ANCHOR_SEED if anchor else _synthetic_seed(replicate, formal=formal)
    generator = np.random.default_rng(seed)
    burn_start = ANCHOR_BURN_START if anchor else (SYNTHETIC_BURN_START if formal else -200.0)
    end_time = ANCHOR_END if anchor else (SYNTHETIC_END if formal else 3_000.0)
    times, marks = simulate_exponential_hawkes_cluster(
        SYNTHETIC_IMMIGRANT,
        np.asarray(SYNTHETIC_BRANCHING, dtype=np.float64),
        SYNTHETIC_BETA,
        burn_start=burn_start,
        end_time=end_time,
        generator=generator,
    )
    train_start = int(0.10 * times.size)
    train_end = int(0.60 * times.size)
    traces, integrals = exponential_trace_design(times, marks, 2, (SYNTHETIC_BETA,))
    references = _direct_hawkes_reference(
        times,
        marks,
        traces,
        integrals,
        start=train_start,
        end=train_end,
    )
    combined = _combined_equivalence(
        times,
        marks,
        traces,
        integrals,
        references,
        start=train_start,
        end=train_end,
    )
    result = {
        "replicate": replicate,
        "seed": seed,
        "shard": None if anchor else replicate % 2,
        "n_events": int(times.size),
        "train_start": train_start,
        "train_end": train_end,
        "mark_counts": np.bincount(marks, minlength=2).tolist(),
        "references": references,
        "combined": combined,
    }
    if not anchor:
        result["elapsed_seconds"] = time.perf_counter() - started
    return result


def _finite_difference(objective: Objective, values: FloatArray, epsilon: float) -> FloatArray:
    result = np.empty_like(values)
    for index in range(values.size):
        plus = values.copy()
        minus = values.copy()
        plus[index] += epsilon
        minus[index] -= epsilon
        result[index] = (objective(plus)[0] - objective(minus)[0]) / (2.0 * epsilon)
    return result


def _self_check() -> dict[str, float]:
    all_queue = np.asarray(
        ((1.0, -0.4), (1.0, 0.2), (1.0, 0.7), (1.0, -0.1)),
        dtype=np.float64,
    )
    event_queue = all_queue[[0, 2]]
    event_traces = np.asarray(((0.2, 0.1), (0.4, 0.6)), dtype=np.float64)
    intervals = np.asarray((0.2, 0.4, 0.3, 0.5), dtype=np.float64)
    integrated = np.asarray((1.4, 0.8), dtype=np.float64)
    values = np.asarray((-0.3, 0.2, 0.1, 0.15), dtype=np.float64)

    def objective(candidate: FloatArray) -> tuple[float, FloatArray]:
        return queue_hawkes_objective_gradient(
            candidate,
            event_queue,
            event_traces,
            all_queue,
            intervals,
            integrated,
            4,
        )

    analytic = objective(values)[1]
    numeric = _finite_difference(objective, values, 1e-6)
    parameters = np.asarray((0.0, 0.0, 2.0, 3.0), dtype=np.float64)
    gradient = np.asarray((0.2, 0.5, -0.4, -0.3), dtype=np.float64)
    observed = np.asarray(
        bound_constrained_kkt_diagnostics(
            parameters,
            gradient,
            ((None, None), (0.0, None), (0.0, None), (None, 3.0)),
        ),
        dtype=np.float64,
    )
    expected = np.asarray((0.5, 0.4, 0.8, 2.0), dtype=np.float64)
    return {
        "finite_difference_maximum_absolute_error": float(np.max(np.abs(analytic - numeric))),
        "bound_case_maximum_absolute_error": float(np.max(np.abs(observed - expected))),
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


def _assert_formal_environment(environment: dict[str, Any], expected_sha: str) -> None:
    if environment["git_sha"] != expected_sha or environment["git_dirty"]:
        raise RuntimeError("formal run requires the clean expected implementation SHA")
    if environment["cuda_visible_devices"] != "-1":
        raise RuntimeError("formal run requires CUDA_VISIBLE_DEVICES=-1")
    for key in ("omp_num_threads", "openblas_num_threads", "mkl_num_threads"):
        if environment[key] != "1":
            raise RuntimeError(f"formal run requires {key}=1")


def _run_shard(args: argparse.Namespace) -> None:
    formal = not bool(args.smoke)
    if args.n_shards != 2 or not 0 <= args.shard_index < 2:
        raise ValueError("exp139 requires exactly two valid shards")
    environment = _environment()
    if formal:
        if args.expected_git_sha is None:
            raise ValueError("formal run requires --expected-git-sha")
        _assert_formal_environment(environment, args.expected_git_sha)
    protocol = _protocol(formal=formal)
    started = time.perf_counter()
    real_records = [
        _run_external(spec, formal=formal) for spec in EXTERNAL_STREAMS if spec.shard == args.shard_index
    ]
    replicate_count = SYNTHETIC_REPLICATES if formal else 2
    generated_records = [
        _run_generated(replicate, formal=formal)
        for replicate in range(replicate_count)
        if replicate % 2 == args.shard_index
    ]
    anchor = _run_generated(0, formal=formal, anchor=True)
    payload = {
        "experiment": 139,
        "title": "queue--Hawkes optimizer and projected-KKT repair",
        "formal": formal,
        "protocol": protocol,
        "protocol_hash": _canonical_hash(protocol),
        "shard": {
            "index": args.shard_index,
            "n_shards": args.n_shards,
            "symbols": [record["symbol"] for record in real_records],
            "generated_replicates": [record["replicate"] for record in generated_records],
        },
        "environment": environment,
        "self_check": _self_check(),
        "anchor": anchor,
        "anchor_hash": _canonical_hash(anchor),
        "real_records": real_records,
        "generated_records": generated_records,
        "peak_rss_raw": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "elapsed_seconds": time.perf_counter() - started,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "formal": formal,
                "protocol_hash": payload["protocol_hash"],
                "shard": payload["shard"],
                "environment": environment,
                "self_check": payload["self_check"],
                "anchor_hash": payload["anchor_hash"],
                "elapsed_seconds": payload["elapsed_seconds"],
            },
            indent=2,
            sort_keys=True,
        )
    )


def _contains_forbidden_real_key(value: Any) -> bool:
    if isinstance(value, dict):
        for key, nested in value.items():
            lowered = str(key).lower()
            if "test" in lowered or "heldout" in lowered:
                return True
            if _contains_forbidden_real_key(nested):
                return True
    elif isinstance(value, list):
        return any(_contains_forbidden_real_key(item) for item in value)
    return False


def _iter_real_targets(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        target
        for record in records
        for policy in record["policies"].values()
        for design in policy["designs"].values()
        for target in design["targets"]
    ]


def _generated_gate(records: list[dict[str, Any]]) -> bool:
    for record in records:
        for reference in record["references"]:
            selected = reference["run"]["selected"]
            if float(selected["projected_gradient_inf_norm"]) > REFERENCE_SELECTION_KKT:
                return False
        for target in record["combined"]:
            for name in ("queue", "hawkes"):
                selected = target["starts"][name]["selected"]
                if float(selected["projected_gradient_inf_norm"]) > STOP_KKT:
                    return False
                if abs(float(target["objective_differences"][name])) > 1e-7:
                    return False
    return True


def _finite_tree(value: Any) -> bool:
    if isinstance(value, dict):
        return all(_finite_tree(item) for item in value.values())
    if isinstance(value, list):
        return all(_finite_tree(item) for item in value)
    if isinstance(value, float):
        return bool(np.isfinite(value))
    return True


def _merge(args: argparse.Namespace) -> None:
    if len(args.merge) != 2:
        raise ValueError("exp139 merge requires exactly two shard files")
    if args.expected_git_sha is None:
        raise ValueError("merge requires --expected-git-sha")
    shards = [json.loads(path.read_text()) for path in args.merge]
    shards.sort(key=lambda shard: int(shard["shard"]["index"]))
    protocol_hashes = {str(shard["protocol_hash"]) for shard in shards}
    protocols = {_canonical_hash(shard["protocol"]) for shard in shards}
    environments = [cast(dict[str, Any], shard["environment"]) for shard in shards]
    expected_owners = {
        0: (["GOOG", "SPY"], [0, 2, 4, 6]),
        1: (["AAPL", "AMZN", "MSFT"], [1, 3, 5, 7]),
    }
    ownership_exact = all(
        shard["shard"]["symbols"] == expected_owners[index][0]
        and shard["shard"]["generated_replicates"] == expected_owners[index][1]
        for index, shard in enumerate(shards)
    )
    environment_exact = all(
        environment["git_sha"] == args.expected_git_sha
        and not environment["git_dirty"]
        and environment["cuda_visible_devices"] == "-1"
        and environment["omp_num_threads"] == "1"
        and environment["openblas_num_threads"] == "1"
        and environment["mkl_num_threads"] == "1"
        for environment in environments
    )
    real_records = [record for shard in shards for record in shard["real_records"]]
    real_records.sort(key=lambda record: str(record["symbol"]))
    generated_records = [record for shard in shards for record in shard["generated_records"]]
    generated_records.sort(key=lambda record: int(record["replicate"]))
    expected_rows = {spec.symbol: spec.rows for spec in EXTERNAL_STREAMS}
    expected_hashes = {spec.symbol: spec.sha256 for spec in EXTERNAL_STREAMS}
    chronology_provenance = (
        all(bool(shard["formal"]) for shard in shards)
        and len(protocol_hashes) == 1
        and len(protocols) == 1
        and protocol_hashes == protocols
        and environment_exact
        and ownership_exact
        and [record["symbol"] for record in real_records] == ["AAPL", "AMZN", "GOOG", "MSFT", "SPY"]
        and all(
            record["source_rows"] == expected_rows[record["symbol"]]
            and record["archive_sha256"] == expected_hashes[record["symbol"]]
            and record["archive_sha256_exact"]
            and record["readme_sha256"] == README_SHA256
            and record["readme_sha256_exact"]
            for record in real_records
        )
    )
    no_real_access = all(
        record["materialized_message_rows"] == record["train_end"]
        and record["materialized_book_rows"] == record["train_end"]
        and record["maximum_materialized_message_row"] == record["train_end"] - 1
        and record["maximum_materialized_book_row"] == record["train_end"] - 1
        and record["queue_source_indices_exact"]
        and not _contains_forbidden_real_key(record)
        for record in real_records
    )
    self_checks = [shard["self_check"] for shard in shards]
    gradient_kkt = all(
        float(check["finite_difference_maximum_absolute_error"]) <= 5e-7
        and float(check["bound_case_maximum_absolute_error"]) <= 1e-15
        for check in self_checks
    )
    generated_equivalence = len(generated_records) == 8 and _generated_gate(generated_records)
    targets = _iter_real_targets(real_records)
    selected_convergence = len(targets) == 120 and all(
        float(target["selected"]["projected_gradient_inf_norm"]) <= SELECTION_KKT
        and float(target["selected"]["complementarity_inf_norm"]) <= SELECTION_KKT
        for target in targets
    )
    no_regression = len(targets) == 120 and all(
        float(target["selected"]["objective"]) <= float(target["legacy_objective"]) + 1e-10
        for target in targets
    )
    dual_targets = [target for target in targets if target["both_starts_qualified"]]
    gaps = [float(target["start_objective_gap"]) for target in dual_targets]
    start_robustness = (
        len(dual_targets) >= 114
        and bool(gaps)
        and max(gaps) <= 1e-5
        and float(np.median(np.asarray(gaps, dtype=np.float64))) <= 1e-6
    )
    anchor_hashes = [str(shard["anchor_hash"]) for shard in shards]
    cross_node = len(set(anchor_hashes)) == 1 and all(
        _canonical_hash(shard["anchor"]) == shard["anchor_hash"] for shard in shards
    )
    complete = (
        len(real_records) == 5
        and len(targets) == 120
        and all(
            set(target["starts"]) == {"queue", "hawkes"}
            and all(
                int(start["stages_run"]) == 1 + len(start["refinements"])
                for start in target["starts"].values()
            )
            for target in targets
        )
        and _finite_tree(real_records)
        and _finite_tree(generated_records)
    )
    hard_gates = {
        "chronology_and_provenance_exact": chronology_provenance,
        "no_real_test_access": no_real_access,
        "gradient_and_kkt_correct": gradient_kkt,
        "generated_equivalence": generated_equivalence,
        "real_selected_convergence": selected_convergence,
        "no_objective_regression": no_regression,
        "start_robustness": start_robustness,
        "cross_node_determinism": cross_node,
        "complete_unfavorable_reporting": complete,
    }
    selected_kkt = [float(target["selected"]["projected_gradient_inf_norm"]) for target in targets]
    selected_complementarity = [float(target["selected"]["complementarity_inf_norm"]) for target in targets]
    improvements = [float(target["objective_improvement"]) for target in targets]
    real_summary = {
        "n_targets": len(targets),
        "dual_qualified_targets": len(dual_targets),
        "maximum_selected_projected_kkt": max(selected_kkt),
        "median_selected_projected_kkt": float(np.median(np.asarray(selected_kkt, dtype=np.float64))),
        "maximum_selected_complementarity": max(selected_complementarity),
        "minimum_objective_improvement": min(improvements),
        "median_objective_improvement": float(np.median(np.asarray(improvements, dtype=np.float64))),
        "maximum_dual_start_objective_gap": max(gaps) if gaps else None,
        "median_dual_start_objective_gap": (
            float(np.median(np.asarray(gaps, dtype=np.float64))) if gaps else None
        ),
    }
    generated_differences = [
        abs(float(difference))
        for record in generated_records
        for target in record["combined"]
        for difference in target["objective_differences"].values()
    ]
    generated_summary = {
        "n_records": len(generated_records),
        "maximum_absolute_objective_difference": max(generated_differences),
        "maximum_reference_projected_kkt": max(
            float(reference["run"]["selected"]["projected_gradient_inf_norm"])
            for record in generated_records
            for reference in record["references"]
        ),
        "maximum_combined_projected_kkt": max(
            float(start["selected"]["projected_gradient_inf_norm"])
            for record in generated_records
            for target in record["combined"]
            for start in target["starts"].values()
        ),
    }
    merged = {
        "experiment": 139,
        "title": "queue--Hawkes optimizer and projected-KKT repair",
        "formal": True,
        "git_sha": args.expected_git_sha,
        "protocol": shards[0]["protocol"],
        "protocol_hash": shards[0]["protocol_hash"],
        "source_shards": [str(path) for path in args.merge],
        "source_environments": environments,
        "self_checks": self_checks,
        "anchor_hash": anchor_hashes[0],
        "real_records": real_records,
        "generated_records": generated_records,
        "real_summary": real_summary,
        "generated_summary": generated_summary,
        "hard_gates": hard_gates,
        "all_hard_gates_pass": all(hard_gates.values()),
        "total_worker_seconds": float(sum(float(shard["elapsed_seconds"]) for shard in shards)),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(merged, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "all_hard_gates_pass": merged["all_hard_gates_pass"],
                "hard_gates": hard_gates,
                "real_summary": real_summary,
                "generated_summary": generated_summary,
                "total_worker_seconds": merged["total_worker_seconds"],
            },
            indent=2,
            sort_keys=True,
        )
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard-index", type=int)
    parser.add_argument("--n-shards", type=int, default=2)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--expected-git-sha")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--merge", type=Path, nargs="*")
    return parser


def main() -> None:
    args = _parser().parse_args()
    if args.merge:
        _merge(args)
        return
    if args.shard_index is None:
        raise ValueError("shard execution requires --shard-index")
    _run_shard(args)


if __name__ == "__main__":
    main()
