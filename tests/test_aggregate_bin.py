from __future__ import annotations

import json
from dataclasses import fields, replace

import numpy as np
import pytest

from ecomd.observation.aggregate_bin import (
    FIT_WARNING,
    AggregateBinAccumulator,
    AggregateBinAccumulatorState,
    AggregateBinConfig,
    AggregateBinObservations,
    AggregateEventRows,
    FrozenPrefixSplit,
    MarketSizeUnit,
    SimulatorBinPredictors,
    aggregate_event_rows,
    evaluate_p3_measurement,
    fit_p3_measurement,
    measurement_fit_hash,
)


def _hand_rows() -> AggregateEventRows:
    return AggregateEventRows(
        time_seconds=np.asarray((0, 15, 59.5, 60, 60, 119.999, 180, 239.999, 240, 300, 359.999)),
        event_type=np.asarray((1, 1, 4, 2, 5, 3, 4, 1, 5, 2, 1), dtype=np.int64),
        size=np.asarray((10, 12, 7, 3, 5, 4, 9, 11, 6, 2, 8), dtype=np.int64),
        direction=np.asarray((1, -1, -1, 1, 1, -1, 1, 1, -1, -1, -1), dtype=np.int64),
        midpoint_after=np.asarray((100, 100, 101, 101, 100, 100, 99, 99, 100, 100, 102)),
    )


def _hand_config() -> AggregateBinConfig:
    return AggregateBinConfig(
        start_seconds=0.0,
        end_seconds=360.0,
        bin_width_seconds=60.0,
        initial_midpoint=100.0,
        size_unit=MarketSizeUnit.SHARES,
    )


def test_hand_fixture_batch_chunk_and_checkpoint() -> None:
    rows = _hand_rows()
    config = _hand_config()
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
    expected_return = np.log(expected_close / np.asarray((100, 101, 100, 100, 99, 100)))
    np.testing.assert_array_equal(batch.close_midpoint, expected_close)
    np.testing.assert_array_equal(batch.executed_volume, expected_volume)
    np.testing.assert_array_equal(batch.mark_counts, expected_counts)
    np.testing.assert_allclose(batch.log_mid_return, expected_return, rtol=0.0, atol=2e-15)

    accumulator = AggregateBinAccumulator(config)
    state = accumulator.init_state()
    offset = 0
    for index, length in enumerate((1, 3, 1, 4, 2)):
        state = accumulator.update(state, rows.slice(offset, offset + length))
        offset += length
        if index == 1:
            payload = json.loads(json.dumps(state.to_checkpoint(), allow_nan=False))
            state = AggregateBinAccumulatorState.from_checkpoint(payload)
    chunk_state, chunked = accumulator.finalize(state)
    np.testing.assert_array_equal(chunked.mark_counts, batch.mark_counts)
    np.testing.assert_array_equal(chunked.executed_volume, batch.executed_volume)
    np.testing.assert_array_equal(chunked.close_midpoint, batch.close_midpoint)
    np.testing.assert_array_equal(chunked.log_mid_return, batch.log_mid_return)
    assert chunk_state.to_checkpoint() == batch_state.to_checkpoint()


def test_schema_and_half_open_boundary_rejections() -> None:
    with pytest.raises(ValueError, match="integral"):
        AggregateBinConfig(0.0, 61.0, 60.0, 100.0, MarketSizeUnit.SHARES)
    with pytest.raises(ValueError, match="integer dtype"):
        replace(_hand_rows(), size=np.asarray([1.5] * 11))
    with pytest.raises(ValueError, match="nondecreasing"):
        replace(_hand_rows(), time_seconds=np.asarray((0, 15, 14, 60, 60, 119, 180, 200, 240, 300, 350)))
    with pytest.raises(ValueError, match="positive"):
        replace(_hand_rows(), midpoint_after=np.asarray((0,) + (100,) * 10))

    accumulator = AggregateBinAccumulator(_hand_config())
    endpoint = AggregateEventRows(
        time_seconds=np.asarray((360.0,)),
        event_type=np.asarray((1,), dtype=np.int64),
        size=np.asarray((1,), dtype=np.int64),
        direction=np.asarray((1,), dtype=np.int64),
        midpoint_after=np.asarray((100.0,)),
    )
    with pytest.raises(ValueError, match="half-open"):
        accumulator.update(accumulator.init_state(), endpoint)


def test_finalization_is_terminal() -> None:
    accumulator = AggregateBinAccumulator(_hand_config())
    state = accumulator.update(accumulator.init_state(), _hand_rows())
    final_state, _ = accumulator.finalize(state)
    with pytest.raises(RuntimeError, match="finalized"):
        accumulator.finalize(final_state)
    with pytest.raises(RuntimeError, match="finalized"):
        accumulator.update(final_state, _hand_rows().slice(0, 1))


def _small_measurement_fixture() -> tuple[
    SimulatorBinPredictors, AggregateBinObservations, FrozenPrefixSplit
]:
    generator = np.random.default_rng(1430)
    n_bins = 200
    x_return = generator.normal(0.0, 0.01, n_bins)
    x_volume = generator.normal(3.5, 0.25, n_bins)
    alignment = np.tanh(generator.normal(0.0, 0.8, n_bins))
    observed_return = 0.0001 + 1.25 * x_return + generator.normal(0.0, 0.002, n_bins)
    volume = np.rint(np.expm1(0.65 + 0.82 * x_volume + generator.normal(0.0, 0.05, n_bins))).astype(
        np.int64
    )
    total = np.full(n_bins, 30, dtype=np.int64)
    probability = 1.0 / (1.0 + np.exp(-(-0.15 + 1.7 * alignment)))
    positive = generator.binomial(total, probability).astype(np.int64)
    counts = np.zeros((n_bins, 6), dtype=np.int64)
    counts[:, 0] = positive
    counts[:, 1] = total - positive
    close = 100.0 * np.exp(np.cumsum(observed_return))
    observations = AggregateBinObservations(
        bin_start_seconds=60.0 * np.arange(n_bins),
        bin_end_seconds=60.0 * (np.arange(n_bins) + 1),
        close_midpoint=close,
        log_mid_return=observed_return,
        executed_volume=volume,
        mark_counts=counts,
        size_unit=MarketSizeUnit.SHARES,
    )
    predictors = SimulatorBinPredictors(
        log_return=x_return,
        volume_model_units=np.expm1(x_volume),
        latent_flow_alignment=alignment,
    )
    return predictors, observations, FrozenPrefixSplit(n_bins=n_bins, train_end=120)


def test_fit_is_prefix_only_and_scores_all_families() -> None:
    predictors, observations, split = _small_measurement_fixture()
    fit = fit_p3_measurement(predictors, observations, split)
    assert fit.warning == FIT_WARNING
    assert all(item.converged for item in fit.return_fits + fit.volume_fits + fit.direction_fits)
    scores = evaluate_p3_measurement(fit, predictors, observations, split)
    assert set(scores) == {"latent", "observation_only", "combined"}

    corrupted_return = observations.log_mid_return.copy()
    corrupted_volume = observations.executed_volume.copy()
    corrupted_counts = observations.mark_counts.copy()
    corrupted_return[split.test_start :] += 10.0
    corrupted_volume[split.test_start :] += 1_000_000_000
    corrupted_counts[split.test_start :, (0, 1)] = corrupted_counts[
        split.test_start :, (1, 0)
    ]
    corrupted = replace(
        observations,
        log_mid_return=corrupted_return,
        executed_volume=corrupted_volume,
        mark_counts=corrupted_counts,
    )
    assert measurement_fit_hash(fit_p3_measurement(predictors, corrupted, split)) == measurement_fit_hash(
        fit
    )


def test_aggregate_object_has_no_order_identity() -> None:
    names = {field.name for field in fields(AggregateBinObservations)}
    assert "order_id" not in names
    assert "event_id" not in names
