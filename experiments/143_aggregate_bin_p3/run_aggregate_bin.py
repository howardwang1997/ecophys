"""Run the preregistered aggregate-bin P3 reconstruction and fit gate."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import resource
import subprocess
import sys
import time
from collections.abc import Sequence
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

for thread_variable in (
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[thread_variable] = "1"

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
from numpy.typing import NDArray  # noqa: E402

from ecomd.observation.aggregate_bin import (  # noqa: E402
    FIT_WARNING,
    AggregateBinAccumulator,
    AggregateBinAccumulatorState,
    AggregateBinConfig,
    AggregateBinObservations,
    AggregateEventRows,
    BinomialChannelFit,
    FrozenPrefixSplit,
    GaussianChannelFit,
    MarketSizeUnit,
    ModelFamily,
    P3MeasurementFit,
    SimulatorBinPredictors,
    aggregate_event_rows,
    evaluate_p3_measurement,
    fit_p3_measurement,
    measurement_fit_hash,
    measurement_fit_to_dict,
    training_prefix_hash,
)

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]

PREREG = Path(__file__).with_name("PREREG.md")
RESULT_PATH = Path(__file__).with_name("AGGREGATE_BIN_RESULTS.json")
REPORT_PATH = Path(__file__).with_name("RESULTS.md")
PREREG_COMMIT = "6d56a0b4"
FORMAL_ROOT_SEED = 143_202_608
SMOKE_ROOT_SEED = 143_202_609
N_BINS = 4_096
TRAIN_END = 2_457
BIN_WIDTH_SECONDS = 60.0
INITIAL_MIDPOINT = 100.0
CHUNK_CYCLE = (1, 997, 37, 4_096, 13, 251)
CHECKPOINT_AFTER_ROWS = 10_003
POSITIVE_MARKS = (0, 3, 4)
NEGATIVE_MARKS = (1, 2, 5)
MARK_EVENT_TYPE = np.asarray((1, 1, 2, 2, 4, 4), dtype=np.int64)
MARK_DIRECTION = np.asarray((1, -1, 1, -1, -1, 1), dtype=np.int64)


@dataclass(frozen=True)
class GeneratedFixture:
    predictors: SimulatorBinPredictors
    reference: AggregateBinObservations
    rows: AggregateEventRows
    config: AggregateBinConfig
    summary: dict[str, Any]


def _git_value(*args: str) -> str:
    return subprocess.check_output(
        ("git", *args), cwd=ROOT, text=True, stderr=subprocess.DEVNULL
    ).strip()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _stationary_ar1(
    n_values: int, rho: float, generator: np.random.Generator
) -> FloatArray:
    values = np.empty(n_values, dtype=np.float64)
    values[0] = generator.standard_normal()
    scale = float(np.sqrt(1.0 - rho * rho))
    innovations = generator.standard_normal(n_values - 1)
    for index in range(1, n_values):
        values[index] = rho * values[index - 1] + scale * innovations[index - 1]
    return values


def _ensure_execution(counts: IntArray, positive: int, total: int) -> None:
    if int(counts[4] + counts[5]) > 0:
        return
    if positive > 0:
        source = 0 if counts[0] > 0 else 3
        counts[source] -= 1
        counts[4] += 1
    else:
        if total <= 0:
            raise RuntimeError("generated bin has no marks")
        source = 1 if counts[1] > 0 else 2
        counts[source] -= 1
        counts[5] += 1


def _raw_rows_from_bins(
    root_sequence: np.random.SeedSequence,
    returns: FloatArray,
    volumes: IntArray,
    mark_counts: IntArray,
) -> tuple[AggregateEventRows, FloatArray, dict[str, int]]:
    shuffle_generator = np.random.default_rng(root_sequence)
    total_rows = int(mark_counts.sum())
    time_seconds = np.empty(total_rows, dtype=np.float64)
    event_type = np.empty(total_rows, dtype=np.int64)
    size = np.ones(total_rows, dtype=np.int64)
    direction = np.empty(total_rows, dtype=np.int64)
    midpoint_after = np.empty(total_rows, dtype=np.float64)
    closes = np.empty(returns.size, dtype=np.float64)
    offset = 0
    previous_close = INITIAL_MIDPOINT
    tie_increments = 0
    for bin_index in range(returns.size):
        counts = mark_counts[bin_index]
        marks = np.repeat(np.arange(6, dtype=np.int64), counts)
        shuffle_generator.shuffle(marks)
        n_rows = int(marks.size)
        local_time = (np.arange(n_rows, dtype=np.float64) + 1.0) / (n_rows + 1.0)
        for tie_start in range(0, n_rows - 1, 8):
            local_time[tie_start + 1] = local_time[tie_start]
            tie_increments += 1
        row_slice = slice(offset, offset + n_rows)
        time_seconds[row_slice] = BIN_WIDTH_SECONDS * (bin_index + local_time)
        event_type[row_slice] = MARK_EVENT_TYPE[marks]
        direction[row_slice] = MARK_DIRECTION[marks]
        execution_positions = np.flatnonzero(np.isin(marks, (4, 5)))
        n_executions = int(execution_positions.size)
        if n_executions < 1 or int(volumes[bin_index]) < n_executions:
            raise RuntimeError("generated executed volume cannot be allocated")
        quotient, remainder = divmod(int(volumes[bin_index]), n_executions)
        local_sizes = np.ones(n_rows, dtype=np.int64)
        local_sizes[execution_positions] = quotient
        local_sizes[execution_positions[:remainder]] += 1
        size[row_slice] = local_sizes
        current_close = previous_close * float(np.exp(returns[bin_index]))
        closes[bin_index] = current_close
        midpoint_after[row_slice] = previous_close
        midpoint_after[offset + n_rows - 1] = current_close
        previous_close = current_close
        offset += n_rows
    if offset != total_rows:
        raise RuntimeError("generated raw-row allocation differs")
    rows = AggregateEventRows(
        time_seconds=time_seconds,
        event_type=event_type,
        size=size,
        direction=direction,
        midpoint_after=midpoint_after,
    )
    return rows, closes, {
        "n_rows": total_rows,
        "zero_time_increments": int(np.count_nonzero(np.diff(time_seconds) == 0.0)),
        "constructed_tie_pairs": tie_increments,
    }


def _generate_fixture(root_seed: int) -> GeneratedFixture:
    children = np.random.SeedSequence(root_seed).spawn(9)
    return_latent = _stationary_ar1(N_BINS, 0.30, np.random.default_rng(children[0]))
    volume_latent = _stationary_ar1(N_BINS, 0.55, np.random.default_rng(children[1]))
    alignment_latent = _stationary_ar1(N_BINS, 0.40, np.random.default_rng(children[2]))
    x_return = 0.01 * return_latent
    x_volume = 3.5 + 0.35 * volume_latent
    alignment = np.tanh(0.9 * alignment_latent)
    observed_return = (
        0.0001
        + 1.25 * x_return
        + np.random.default_rng(children[3]).normal(0.0, 0.004, N_BINS)
    )
    observed_log_volume = (
        0.65
        + 0.82 * x_volume
        + np.random.default_rng(children[4]).normal(0.0, 0.12, N_BINS)
    )
    provisional_volume = np.rint(np.expm1(observed_log_volume)).astype(np.int64)
    count_mean = np.exp(2.6 + 0.20 * (x_volume - 3.5))
    total_marks = 12 + np.random.default_rng(children[5]).poisson(count_mean)
    probability_positive = 1.0 / (1.0 + np.exp(-(-0.15 + 1.70 * alignment)))
    positive_marks = np.random.default_rng(children[6]).binomial(
        total_marks, probability_positive
    )
    category_generator = np.random.default_rng(children[7])
    mark_counts = np.zeros((N_BINS, 6), dtype=np.int64)
    for index in range(N_BINS):
        positive = int(positive_marks[index])
        total = int(total_marks[index])
        mark_counts[index, POSITIVE_MARKS] = category_generator.multinomial(
            positive, (0.40, 0.30, 0.30)
        )
        mark_counts[index, NEGATIVE_MARKS] = category_generator.multinomial(
            total - positive, (0.40, 0.30, 0.30)
        )
        _ensure_execution(mark_counts[index], positive, total)
    execution_counts = mark_counts[:, (4, 5)].sum(axis=1, dtype=np.int64)
    observed_volume = np.maximum(provisional_volume, execution_counts).astype(np.int64)
    rows, closes, row_summary = _raw_rows_from_bins(
        children[8], observed_return, observed_volume, mark_counts
    )
    config = AggregateBinConfig(
        start_seconds=0.0,
        end_seconds=N_BINS * BIN_WIDTH_SECONDS,
        bin_width_seconds=BIN_WIDTH_SECONDS,
        initial_midpoint=INITIAL_MIDPOINT,
        size_unit=MarketSizeUnit.SHARES,
    )
    starts = BIN_WIDTH_SECONDS * np.arange(N_BINS, dtype=np.float64)
    reference = AggregateBinObservations(
        bin_start_seconds=starts,
        bin_end_seconds=starts + BIN_WIDTH_SECONDS,
        close_midpoint=closes,
        log_mid_return=observed_return,
        executed_volume=observed_volume,
        mark_counts=mark_counts,
        size_unit=MarketSizeUnit.SHARES,
    )
    predictors = SimulatorBinPredictors(
        log_return=x_return,
        volume_model_units=np.expm1(x_volume),
        latent_flow_alignment=alignment,
    )
    summary: dict[str, Any] = {
        **row_summary,
        "root_seed": root_seed,
        "n_bins": N_BINS,
        "train_end": TRAIN_END,
        "total_marks": int(total_marks.sum()),
        "total_executed_volume_shares": int(observed_volume.sum()),
        "minimum_marks_per_bin": int(total_marks.min()),
        "maximum_marks_per_bin": int(total_marks.max()),
        "minimum_execution_count_per_bin": int(execution_counts.min()),
        "volume_floor_adjustments": int(np.count_nonzero(observed_volume != provisional_volume)),
    }
    return GeneratedFixture(predictors, reference, rows, config, summary)


def _hand_fixture() -> tuple[AggregateEventRows, AggregateBinConfig]:
    rows = AggregateEventRows(
        time_seconds=np.asarray(
            (0, 15, 59.5, 60, 60, 119.999, 180, 239.999, 240, 300, 359.999),
            dtype=np.float64,
        ),
        event_type=np.asarray((1, 1, 4, 2, 5, 3, 4, 1, 5, 2, 1), dtype=np.int64),
        size=np.asarray((10, 12, 7, 3, 5, 4, 9, 11, 6, 2, 8), dtype=np.int64),
        direction=np.asarray((1, -1, -1, 1, 1, -1, 1, 1, -1, -1, -1), dtype=np.int64),
        midpoint_after=np.asarray(
            (100, 100, 101, 101, 100, 100, 99, 99, 100, 100, 102),
            dtype=np.float64,
        ),
    )
    config = AggregateBinConfig(
        start_seconds=0.0,
        end_seconds=360.0,
        bin_width_seconds=60.0,
        initial_midpoint=100.0,
        size_unit=MarketSizeUnit.SHARES,
    )
    return rows, config


def _observation_comparison(
    left: AggregateBinObservations, right: AggregateBinObservations
) -> dict[str, Any]:
    return {
        "bin_start_bit_exact": bool(np.array_equal(left.bin_start_seconds, right.bin_start_seconds)),
        "bin_end_bit_exact": bool(np.array_equal(left.bin_end_seconds, right.bin_end_seconds)),
        "close_bit_exact": bool(np.array_equal(left.close_midpoint, right.close_midpoint)),
        "return_bit_exact": bool(np.array_equal(left.log_mid_return, right.log_mid_return)),
        "volume_bit_exact": bool(np.array_equal(left.executed_volume, right.executed_volume)),
        "marks_bit_exact": bool(np.array_equal(left.mark_counts, right.mark_counts)),
        "maximum_close_absolute_error": float(
            np.max(np.abs(left.close_midpoint - right.close_midpoint))
        ),
        "maximum_return_absolute_error": float(
            np.max(np.abs(left.log_mid_return - right.log_mid_return))
        ),
    }


def _check_hand_fixture() -> dict[str, Any]:
    rows, config = _hand_fixture()
    batch_state, batch = aggregate_event_rows(rows, config)
    expected_close = np.asarray((101, 100, 100, 99, 100, 102), dtype=np.float64)
    expected_volume = np.asarray((7, 5, 0, 9, 6, 0), dtype=np.int64)
    expected_counts = np.asarray(
        (
            (1, 1, 0, 0, 1, 0),
            (0, 0, 1, 1, 0, 1),
            (0, 0, 0, 0, 0, 0),
            (1, 0, 0, 0, 0, 1),
            (0, 0, 0, 0, 1, 0),
            (0, 1, 0, 1, 0, 0),
        ),
        dtype=np.int64,
    )
    preceding = np.asarray((100, 101, 100, 100, 99, 100), dtype=np.float64)
    expected_return = np.log(expected_close / preceding)
    accumulator = AggregateBinAccumulator(config)
    state = accumulator.init_state()
    offset = 0
    checkpoint_json_safe = False
    for index, length in enumerate((1, 3, 1, 4, 2)):
        state = accumulator.update(state, rows.slice(offset, offset + length))
        offset += length
        if index == 1:
            serialized = json.dumps(state.to_checkpoint(), allow_nan=False, sort_keys=True)
            state = AggregateBinAccumulatorState.from_checkpoint(json.loads(serialized))
            checkpoint_json_safe = True
    chunk_state, chunked = accumulator.finalize(state)
    comparison = _observation_comparison(batch, chunked)
    exact_expected = {
        "closes": bool(np.array_equal(batch.close_midpoint, expected_close)),
        "volume": bool(np.array_equal(batch.executed_volume, expected_volume)),
        "marks": bool(np.array_equal(batch.mark_counts, expected_counts)),
        "returns_within_2e_15": bool(
            np.max(np.abs(batch.log_mid_return - expected_return)) <= 2e-15
        ),
        "empty_bin_carry": bool(batch.close_midpoint[2] == batch.close_midpoint[1]),
    }
    passed = bool(
        all(exact_expected.values())
        and checkpoint_json_safe
        and all(
            comparison[key]
            for key in (
                "bin_start_bit_exact",
                "bin_end_bit_exact",
                "close_bit_exact",
                "return_bit_exact",
                "volume_bit_exact",
                "marks_bit_exact",
            )
        )
        and batch_state.to_checkpoint() == chunk_state.to_checkpoint()
    )
    return {
        "expected": exact_expected,
        "chunk_comparison": comparison,
        "checkpoint_json_safe": checkpoint_json_safe,
        "terminal_state_exact": batch_state.to_checkpoint() == chunk_state.to_checkpoint(),
        "observed_closes": batch.close_midpoint.tolist(),
        "observed_returns": batch.log_mid_return.tolist(),
        "observed_volume": batch.executed_volume.tolist(),
        "observed_mark_counts": batch.mark_counts.tolist(),
        "passed": passed,
    }


def _check_schema_rejections() -> dict[str, Any]:
    rows, config = _hand_fixture()
    cases: dict[str, Any] = {}

    def rejects(name: str, callback: Any) -> None:
        error_type: str | None = None
        message: str | None = None
        try:
            callback()
        except (ValueError, RuntimeError) as error:
            error_type = type(error).__name__
            message = str(error)
        cases[name] = {
            "rejected": error_type is not None,
            "error_type": error_type,
            "message": message,
        }

    rejects(
        "nonintegral_bins",
        lambda: AggregateBinConfig(0.0, 61.0, 60.0, 100.0, MarketSizeUnit.SHARES),
    )
    rejects("invalid_unit", lambda: MarketSizeUnit("model_coordinate"))
    rejects("noninteger_size", lambda: replace(rows, size=np.full(rows.n_events, 1.5)))
    rejects("zero_size", lambda: replace(rows, size=np.zeros(rows.n_events, dtype=np.int64)))
    rejects(
        "decreasing_time",
        lambda: replace(rows, time_seconds=np.asarray((0, 15, 14, 60, 60, 119, 180, 200, 240, 300, 350))),
    )
    invalid_time = rows.time_seconds.copy()
    invalid_time[0] = np.nan
    rejects("nonfinite_time", lambda: replace(rows, time_seconds=invalid_time))
    invalid_midpoint = rows.midpoint_after.copy()
    invalid_midpoint[0] = 0.0
    rejects("nonpositive_midpoint", lambda: replace(rows, midpoint_after=invalid_midpoint))
    invalid_type = rows.event_type.copy()
    invalid_type[0] = 6
    rejects("invalid_event_type", lambda: replace(rows, event_type=invalid_type))
    invalid_direction = rows.direction.copy()
    invalid_direction[0] = 0
    rejects("invalid_direction", lambda: replace(rows, direction=invalid_direction))
    endpoint = replace(rows.slice(0, 1), time_seconds=np.asarray((config.end_seconds,)))
    rejects(
        "right_endpoint",
        lambda: AggregateBinAccumulator(config).update(
            AggregateBinAccumulator(config).init_state(), endpoint
        ),
    )
    accumulator = AggregateBinAccumulator(config)
    state = accumulator.update(accumulator.init_state(), rows)
    final_state, _ = accumulator.finalize(state)
    rejects("update_after_finalize", lambda: accumulator.update(final_state, rows.slice(0, 1)))
    rejects("second_finalize", lambda: accumulator.finalize(final_state))
    return {
        "cases": cases,
        "passed": len(cases) == 12 and all(item["rejected"] for item in cases.values()),
    }


def _chunked_generated(
    fixture: GeneratedFixture,
) -> tuple[AggregateBinAccumulatorState, AggregateBinObservations, dict[str, Any]]:
    accumulator = AggregateBinAccumulator(fixture.config)
    state = accumulator.init_state()
    offset = 0
    cycle_index = 0
    restored = False
    chunks: list[int] = []
    while offset < fixture.rows.n_events:
        length = min(CHUNK_CYCLE[cycle_index % len(CHUNK_CYCLE)], fixture.rows.n_events - offset)
        if offset < CHECKPOINT_AFTER_ROWS < offset + length:
            length = CHECKPOINT_AFTER_ROWS - offset
        state = accumulator.update(state, fixture.rows.slice(offset, offset + length))
        chunks.append(length)
        offset += length
        cycle_index += 1
        if offset == CHECKPOINT_AFTER_ROWS and not restored:
            serialized = json.dumps(state.to_checkpoint(), sort_keys=True, allow_nan=False)
            state = AggregateBinAccumulatorState.from_checkpoint(json.loads(serialized))
            restored = True
    terminal, observations = accumulator.finalize(state)
    post_finalize_update_rejected = False
    post_finalize_second_rejected = False
    try:
        accumulator.update(terminal, fixture.rows.slice(0, 1))
    except RuntimeError:
        post_finalize_update_rejected = True
    try:
        accumulator.finalize(terminal)
    except RuntimeError:
        post_finalize_second_rejected = True
    return terminal, observations, {
        "chunk_lengths": chunks,
        "checkpoint_after_rows": CHECKPOINT_AFTER_ROWS,
        "checkpoint_restored": restored,
        "post_finalize_update_rejected": post_finalize_update_rejected,
        "post_finalize_second_rejected": post_finalize_second_rejected,
    }


def _check_reconstruction(fixture: GeneratedFixture) -> dict[str, Any]:
    batch_state, reconstructed = aggregate_event_rows(fixture.rows, fixture.config)
    chunk_state, chunked, chunk_metadata = _chunked_generated(fixture)
    reference_comparison = _observation_comparison(reconstructed, fixture.reference)
    chunk_comparison = _observation_comparison(reconstructed, chunked)
    reconstruction_passed = bool(
        reference_comparison["volume_bit_exact"]
        and reference_comparison["marks_bit_exact"]
        and reference_comparison["maximum_close_absolute_error"] <= 5e-13
        and reference_comparison["maximum_return_absolute_error"] <= 5e-13
    )
    state_passed = bool(
        all(
            chunk_comparison[key]
            for key in (
                "bin_start_bit_exact",
                "bin_end_bit_exact",
                "close_bit_exact",
                "return_bit_exact",
                "volume_bit_exact",
                "marks_bit_exact",
            )
        )
        and batch_state.to_checkpoint() == chunk_state.to_checkpoint()
        and chunk_metadata["checkpoint_restored"]
        and chunk_metadata["post_finalize_update_rejected"]
        and chunk_metadata["post_finalize_second_rejected"]
    )
    return {
        "reference_comparison": reference_comparison,
        "chunk_comparison": chunk_comparison,
        "terminal_state_exact": batch_state.to_checkpoint() == chunk_state.to_checkpoint(),
        "chunk_metadata": chunk_metadata,
        "reconstruction_passed": reconstruction_passed,
        "state_completeness_passed": state_passed,
        "observations": reconstructed,
    }


def _gaussian_fit(
    fit: P3MeasurementFit, channel: str, family: ModelFamily
) -> GaussianChannelFit:
    candidates = fit.return_fits if channel == "return" else fit.volume_fits
    matches = [item for item in candidates if item.family is family]
    if len(matches) != 1:
        raise RuntimeError("missing Gaussian fit")
    return matches[0]


def _binomial_fit(fit: P3MeasurementFit, family: ModelFamily) -> BinomialChannelFit:
    matches = [item for item in fit.direction_fits if item.family is family]
    if len(matches) != 1:
        raise RuntimeError("missing grouped-binomial fit")
    return matches[0]


def _corrupt_heldout(
    observations: AggregateBinObservations, split: FrozenPrefixSplit
) -> AggregateBinObservations:
    returns = observations.log_mid_return.copy()
    volume = observations.executed_volume.copy()
    counts = observations.mark_counts.copy()
    returns[split.test_start :] += 10.0
    volume[split.test_start :] += 1_000_000_000
    counts[split.test_start :] = counts[split.test_start :, (1, 0, 3, 2, 5, 4)]
    return replace(
        observations,
        log_mid_return=returns,
        executed_volume=volume,
        mark_counts=counts,
    )


def _corrupt_training(
    observations: AggregateBinObservations,
) -> AggregateBinObservations:
    returns = observations.log_mid_return.copy()
    volume = observations.executed_volume.copy()
    counts = observations.mark_counts.copy()
    returns[100] += 0.1
    volume[100] *= 10
    counts[100] = counts[100, (1, 0, 3, 2, 5, 4)]
    return replace(
        observations,
        log_mid_return=returns,
        executed_volume=volume,
        mark_counts=counts,
    )


def _check_fit(
    predictors: SimulatorBinPredictors,
    observations: AggregateBinObservations,
) -> dict[str, Any]:
    split = FrozenPrefixSplit(n_bins=N_BINS, train_end=TRAIN_END)
    fit = fit_p3_measurement(predictors, observations, split)
    fit_hash = measurement_fit_hash(fit)
    anchored = evaluate_p3_measurement(fit, predictors, observations, split)
    sign_flipped = evaluate_p3_measurement(
        fit, predictors, observations, split, directional_sign=-1.0
    )
    return_latent = _gaussian_fit(fit, "return", ModelFamily.LATENT)
    volume_latent = _gaussian_fit(fit, "volume", ModelFamily.LATENT)
    direction_latent = _binomial_fit(fit, ModelFamily.LATENT)
    recovery_checks = {
        "return_intercept": abs(float(return_latent.coefficients[0]) - 0.0001) <= 5e-4,
        "return_slope": abs(float(return_latent.coefficients[1]) / 1.25 - 1.0) <= 0.05,
        "return_sigma": abs(return_latent.sigma / 0.004 - 1.0) <= 0.10,
        "volume_intercept": abs(float(volume_latent.coefficients[0]) - 0.65) <= 0.08,
        "volume_slope": abs(float(volume_latent.coefficients[1]) / 0.82 - 1.0) <= 0.05,
        "volume_sigma": abs(volume_latent.sigma / 0.12 - 1.0) <= 0.15,
        "direction_intercept": abs(float(direction_latent.coefficients[0]) + 0.15) <= 0.08,
        "direction_slope": abs(float(direction_latent.coefficients[1]) / 1.70 - 1.0) <= 0.05,
        "all_converged": all(
            item.converged
            for item in fit.return_fits + fit.volume_fits + fit.direction_fits
        ),
        "direction_within_100": all(item.iterations <= 100 for item in fit.direction_fits),
        "all_finite": all(
            np.isfinite(item.coefficients).all()
            for item in fit.return_fits + fit.volume_fits + fit.direction_fits
        ),
    }
    latent_score = anchored[ModelFamily.LATENT.value]
    observation_score = anchored[ModelFamily.OBSERVATION_ONLY.value]
    combined_score = anchored[ModelFamily.COMBINED.value]
    controls = {
        "return_rmse_ratio": latent_score["return_rmse"] / observation_score["return_rmse"],
        "volume_rmse_ratio": latent_score["log_volume_rmse"]
        / observation_score["log_volume_rmse"],
        "direction_latent_minus_observation_nats_per_event": (
            latent_score["direction_log_likelihood_nats_per_event"]
            - observation_score["direction_log_likelihood_nats_per_event"]
        ),
        "combined_return_over_latent_rmse": combined_score["return_rmse"]
        / latent_score["return_rmse"],
        "combined_volume_over_latent_rmse": combined_score["log_volume_rmse"]
        / latent_score["log_volume_rmse"],
        "combined_minus_latent_direction_nats_per_event": (
            combined_score["direction_log_likelihood_nats_per_event"]
            - latent_score["direction_log_likelihood_nats_per_event"]
        ),
        "anchored_minus_flipped_direction_nats_per_event": (
            latent_score["direction_log_likelihood_nats_per_event"]
            - sign_flipped[ModelFamily.LATENT.value][
                "direction_log_likelihood_nats_per_event"
            ]
        ),
    }
    control_checks = {
        "return_observation_only": controls["return_rmse_ratio"] <= 0.60,
        "volume_observation_only": controls["volume_rmse_ratio"] <= 0.65,
        "direction_observation_only": controls[
            "direction_latent_minus_observation_nats_per_event"
        ]
        >= 0.02,
        "combined_return": controls["combined_return_over_latent_rmse"] <= 1.02,
        "combined_volume": controls["combined_volume_over_latent_rmse"] <= 1.02,
        "combined_direction": controls[
            "combined_minus_latent_direction_nats_per_event"
        ]
        >= -0.002,
        "sign_flip": controls["anchored_minus_flipped_direction_nats_per_event"]
        >= 0.05,
    }
    heldout_fit = fit_p3_measurement(
        predictors, _corrupt_heldout(observations, split), split
    )
    training_fit = fit_p3_measurement(predictors, _corrupt_training(observations), split)
    heldout_hash = measurement_fit_hash(heldout_fit)
    training_hash = measurement_fit_hash(training_fit)
    firewall = {
        "fit_hash": fit_hash,
        "heldout_corruption_fit_hash": heldout_hash,
        "training_corruption_fit_hash": training_hash,
        "heldout_fit_bit_exact": measurement_fit_to_dict(heldout_fit)
        == measurement_fit_to_dict(fit),
        "heldout_hash_exact": heldout_hash == fit_hash,
        "training_hash_changed": training_hash != fit_hash,
        "prefix_hash_recomputed_exact": fit.training_prefix_sha256
        == training_prefix_hash(predictors, observations, split),
        "train_end": fit.train_end,
        "test_start": fit.test_start,
    }
    test_x_return = predictors.log_return[split.test_start :]
    return_prediction = (
        return_latent.coefficients[0] + return_latent.coefficients[1] * test_x_return
    )
    rescaled_prediction = return_latent.coefficients[0] + (
        return_latent.coefficients[1] / 7.0
    ) * (7.0 * test_x_return)
    test_x_volume = predictors.log_volume_predictor[split.test_start :]
    volume_prediction = (
        volume_latent.coefficients[0] + volume_latent.coefficients[1] * test_x_volume
    )
    rescaled_volume_prediction = volume_latent.coefficients[0] + (
        volume_latent.coefficients[1] / 7.0
    ) * (7.0 * test_x_volume)
    return_gauge_error = float(np.max(np.abs(return_prediction - rescaled_prediction)))
    volume_gauge_error = float(
        np.max(np.abs(volume_prediction - rescaled_volume_prediction))
    )
    gauge = {
        "return_maximum_absolute_error": return_gauge_error,
        "volume_maximum_absolute_error": volume_gauge_error,
        "warning": fit.warning,
        "passed": bool(
            return_gauge_error <= 1e-12
            and volume_gauge_error <= 1e-12
            and fit.warning == FIT_WARNING
        ),
    }
    return {
        "fit": measurement_fit_to_dict(fit),
        "fit_hash": fit_hash,
        "anchored_heldout": anchored,
        "sign_flipped_heldout": sign_flipped,
        "recovery_checks": recovery_checks,
        "recovery_passed": all(recovery_checks.values()),
        "control_values": controls,
        "control_checks": control_checks,
        "controls_passed": all(control_checks.values()),
        "firewall": firewall,
        "firewall_passed": bool(
            firewall["heldout_fit_bit_exact"]
            and firewall["heldout_hash_exact"]
            and firewall["training_hash_changed"]
            and firewall["prefix_hash_recomputed_exact"]
            and firewall["train_end"] == TRAIN_END
            and firewall["test_start"] == TRAIN_END
        ),
        "gauge": gauge,
    }


def _run_quality_checks() -> dict[str, Any]:
    commands = {
        "pytest": (
            sys.executable,
            "-m",
            "pytest",
            "tests/test_aggregate_bin.py",
            "-q",
        ),
        "ruff": (
            sys.executable,
            "-m",
            "ruff",
            "check",
            "ecomd/observation/__init__.py",
            "ecomd/observation/aggregate_bin.py",
            "tests/test_aggregate_bin.py",
            "experiments/143_aggregate_bin_p3/run_aggregate_bin.py",
        ),
        "mypy": (
            sys.executable,
            "-m",
            "mypy",
            "--strict",
            "ecomd/observation/__init__.py",
            "ecomd/observation/aggregate_bin.py",
            "experiments/143_aggregate_bin_p3/run_aggregate_bin.py",
        ),
    }
    records: dict[str, Any] = {}
    for name, command in commands.items():
        completed = subprocess.run(
            command, cwd=ROOT, check=False, capture_output=True, text=True
        )
        records[name] = {
            "command": list(command),
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    return {
        "records": records,
        "passed": all(item["returncode"] == 0 for item in records.values()),
    }


def _environment() -> dict[str, Any]:
    packages: dict[str, str | None] = {}
    for name in ("numpy", "pytest", "ruff", "mypy"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    return {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "executable": sys.executable,
        "conda_default_env": os.environ.get("CONDA_DEFAULT_ENV"),
        "thread_variables": {
            name: os.environ[name]
            for name in (
                "OMP_NUM_THREADS",
                "MKL_NUM_THREADS",
                "OPENBLAS_NUM_THREADS",
                "NUMEXPR_NUM_THREADS",
            )
        },
        "packages": packages,
    }


def _human_report(result: dict[str, Any]) -> str:
    gate_lines = "\n".join(
        f"- G{index}: {'PASS' if passed else 'FAIL'} — {name}"
        for index, (name, passed) in enumerate(result["gates"].items(), start=1)
    )
    controls = result["measurement"]["control_values"]
    recovery = result["measurement"]["fit"]
    return f"""# Experiment 143 — results

**Decision:** **{result['decision']}**
**Implementation:** `{result['provenance']['implementation_git_sha']}`
**Protocol SHA-256:** `{result['provenance']['protocol_sha256']}`

## Gate outcomes

{gate_lines}

## Reconstruction

- Generated bins / raw rows: {result['generation']['n_bins']} / {result['generation']['n_rows']}
- Mark counts exact: {result['reconstruction']['reference_comparison']['marks_bit_exact']}
- Executed share volume exact: {result['reconstruction']['reference_comparison']['volume_bit_exact']}
- Maximum return error: {result['reconstruction']['reference_comparison']['maximum_return_absolute_error']:.3e}
- Chunk/checkpoint return bit-exact: {result['reconstruction']['chunk_comparison']['return_bit_exact']}

## Train-only P3 controls

- Return latent/observation-only RMSE ratio: {controls['return_rmse_ratio']:.6f}
- Log-volume latent/observation-only RMSE ratio: {controls['volume_rmse_ratio']:.6f}
- Direction latent minus observation-only: {controls['direction_latent_minus_observation_nats_per_event']:.6f} nats/event
- Anchored minus sign-flipped direction: {controls['anchored_minus_flipped_direction_nats_per_event']:.6f} nats/event
- Held-out corruption left fit exact: {result['measurement']['firewall']['heldout_fit_bit_exact']}
- Training corruption changed fit hash: {result['measurement']['firewall']['training_hash_changed']}
- Identifiability warning: `{recovery['warning']}`

## Interpretation

This result validates generated aggregate-bin reconstruction and a train-only P3 measurement implementation.
It does not validate EcoMD on market data, event/order mechanics, latent-agent recovery, audit novelty or market
physics. Event/order support remains FAIL; external evidence remains F4.
"""


def _run(root_seed: int, *, formal: bool) -> dict[str, Any]:
    started = time.perf_counter()
    dirty_before = _git_value("status", "--porcelain", "--untracked-files=all")
    implementation_sha = _git_value("rev-parse", "HEAD")
    prereg_is_ancestor = (
        subprocess.run(
            ("git", "merge-base", "--is-ancestor", PREREG_COMMIT, implementation_sha),
            cwd=ROOT,
            check=False,
        ).returncode
        == 0
    )
    if formal and dirty_before:
        raise RuntimeError("formal run requires a clean implementation tree")
    if formal and (RESULT_PATH.exists() or REPORT_PATH.exists()):
        raise RuntimeError("formal result already exists; refusing a second run")

    schema = _check_schema_rejections()
    hand = _check_hand_fixture()
    fixture = _generate_fixture(root_seed)
    reconstruction = _check_reconstruction(fixture)
    observations = reconstruction.pop("observations")
    if not isinstance(observations, AggregateBinObservations):
        raise TypeError("reconstruction did not return aggregate observations")
    measurement = _check_fit(fixture.predictors, observations)
    quality = _run_quality_checks()
    chronology = bool(
        not formal
        or (
            prereg_is_ancestor
            and implementation_sha != _git_value("rev-parse", PREREG_COMMIT)
            and not dirty_before
        )
    )
    complete_reporting = bool(
        len(schema["cases"]) == 12
        and fixture.summary["n_bins"] == N_BINS
        and measurement["fit"]["train_end"] == TRAIN_END
        and len(measurement["fit"]["return_fits"]) == 3
        and len(measurement["fit"]["volume_fits"]) == 3
        and len(measurement["fit"]["direction_fits"]) == 3
    )
    gates = {
        "chronology_provenance": chronology,
        "schema_units_clock": bool(schema["passed"]),
        "hand_fixture": bool(hand["passed"]),
        "generated_reconstruction": bool(reconstruction["reconstruction_passed"]),
        "state_completeness": bool(reconstruction["state_completeness_passed"]),
        "train_only_firewall": bool(measurement["firewall_passed"]),
        "parameter_recovery": bool(measurement["recovery_passed"]),
        "negative_controls": bool(measurement["controls_passed"]),
        "identifiability": bool(measurement["gauge"]["passed"]),
        "code_quality_complete_reporting": bool(quality["passed"] and complete_reporting),
    }
    decision = "PASS" if all(gates.values()) else "FAIL"
    elapsed = time.perf_counter() - started
    result: dict[str, Any] = {
        "experiment": 143,
        "name": "aggregate_bin_p3_reconstruction_and_measurement",
        "mode": "formal" if formal else "smoke",
        "decision": decision,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "provenance": {
            "preregistration_commit": PREREG_COMMIT,
            "preregistration_is_ancestor": prereg_is_ancestor,
            "protocol_path": str(PREREG.relative_to(ROOT)),
            "protocol_sha256": _sha256(PREREG),
            "implementation_git_sha": implementation_sha,
            "dirty_before_run": bool(dirty_before),
            "dirty_entries_before_run": dirty_before.splitlines(),
            "root_seed": root_seed,
            "external_data_read": False,
            "current_event_adapter_called": False,
        },
        "environment": _environment(),
        "schema_rejections": schema,
        "hand_fixture": hand,
        "generation": fixture.summary,
        "reconstruction": reconstruction,
        "measurement": measurement,
        "quality": quality,
        "gates": gates,
        "resources": {
            "wall_seconds": elapsed,
            "peak_rss_raw": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "peak_rss_unit": "bytes_on_macos_kib_on_linux",
            "gpu_used": False,
        },
        "interpretation": (
            "A PASS validates synthetic aggregate-bin P3 implementation only. It does not establish external "
            "predictive value, event/order semantics, recovered agents, novelty or market physics."
        ),
    }
    if formal:
        RESULT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        REPORT_PATH.write_text(_human_report(result))
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args(argv)
    result = _run(SMOKE_ROOT_SEED if args.smoke else FORMAL_ROOT_SEED, formal=not args.smoke)
    print(
        json.dumps(
            {"mode": result["mode"], "decision": result["decision"], "gates": result["gates"]},
            indent=2,
        )
    )
    return 0 if result["decision"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
