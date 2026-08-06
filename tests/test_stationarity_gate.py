"""Tests for the frozen exp127 stationarity gate."""

from __future__ import annotations

import numpy as np
import pytest

from ecomd.eval.stationarity_gate import (
    GateConfig,
    delay_vectors,
    evaluate_stationarity_gate,
    fit_stationarity_gate,
    gate_fit_from_dict,
    multivariate_energy_distance,
    score_fixed_length,
)


def _small_config() -> GateConfig:
    return GateConfig(
        block_length=40,
        gate_starts=(0, 40, 80, 120, 160, 200),
        late_starts=(240, 280, 320, 360),
        max_w_star=160,
        persistence_blocks=3,
        tolerance_quantile=0.95,
        bootstrap_replicates=200,
        bootstrap_seed=17,
    )


def test_delay_vectors_shape_and_values() -> None:
    returns = np.array([-2.0, 3.0, -4.0, 5.0], dtype=np.float64)
    got = delay_vectors(returns)
    expected = np.array([[-2.0, 2.0, 3.0], [3.0, 3.0, 4.0], [-4.0, 4.0, 5.0]])
    assert np.array_equal(got, expected)


def test_energy_distance_identical_and_shifted() -> None:
    rng = np.random.default_rng(3)
    x = rng.normal(size=(80, 3))
    assert multivariate_energy_distance(x, x) == pytest.approx(0.0, abs=1e-12)
    assert multivariate_energy_distance(x, x + 4.0) > 5.0


def test_gate_detects_strong_initial_transient() -> None:
    rng = np.random.default_rng(9)
    trajectories = rng.normal(size=(16, 400))
    trajectories[:, :120] += 20.0
    fit = fit_stationarity_gate(trajectories, _small_config())
    assert fit.w_star == 120
    assert fit.calibration_distance_medians[0] > fit.tolerance
    assert fit.calibration_distance_medians[3] <= fit.tolerance


def test_gate_accepts_stationary_start_and_evaluates_heldout() -> None:
    rng = np.random.default_rng(11)
    calibration = rng.normal(size=(32, 400))
    heldout = rng.normal(size=(32, 400))
    fit = fit_stationarity_gate(calibration, _small_config())
    evaluation = evaluate_stationarity_gate(heldout, fit)
    assert fit.w_star == 0
    assert evaluation.frozen_w_star == 0
    assert len(evaluation.distance_medians) == len(_small_config().gate_starts)


def test_gate_fit_serialization_roundtrip() -> None:
    rng = np.random.default_rng(21)
    fit = fit_stationarity_gate(rng.normal(size=(8, 400)), _small_config())
    restored = gate_fit_from_dict(fit.to_dict())
    assert restored == fit


def test_fixed_length_scoring_rejects_short_slice() -> None:
    rng = np.random.default_rng(5)
    returns = rng.standard_t(df=5, size=500)
    facts = score_fixed_length(returns, w=100, length=300)
    assert facts["hill_tail_index"]["meta"]["n"] == 300
    assert facts["hill_tail_index"]["meta"]["k_frac"] == pytest.approx(0.05)
    with pytest.raises(ValueError, match="invalid fixed-length slice"):
        score_fixed_length(returns, w=250, length=300)


def test_gate_rejects_too_short_trajectories() -> None:
    with pytest.raises(ValueError, match="need at least 400 returns"):
        fit_stationarity_gate(np.ones((4, 399)), _small_config())
