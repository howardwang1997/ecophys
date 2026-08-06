"""Tests for the experiment-127 classical stationarity comparator."""

from __future__ import annotations

import numpy as np
import pytest

from ecomd.eval.stationarity_baselines import (
    ADFKPSSConfig,
    fit_adf_kpss_gate,
    select_persistent_start,
)


def test_select_persistent_start() -> None:
    passes = np.array([False, False, True, True, True, False], dtype=np.bool_)
    selected = select_persistent_start(
        passes,
        starts=(0, 10, 20, 30, 40, 50),
        max_start=30,
        block_length=10,
        persistence_blocks=3,
    )
    assert selected == 20


def test_select_persistent_start_returns_none() -> None:
    passes = np.array([False, True, True, False], dtype=np.bool_)
    assert select_persistent_start(passes, (0, 10, 20, 30), 20, 10, 3) is None


def test_adf_kpss_gate_accepts_white_noise() -> None:
    rng = np.random.default_rng(91)
    returns = rng.normal(size=(6, 800))
    config = ADFKPSSConfig(
        block_length=100,
        gate_starts=(0, 100, 200, 300, 400, 500),
        max_w_star=300,
        persistence_blocks=3,
        trajectory_pass_fraction=0.5,
        adf_maxlag=3,
    )
    fit = fit_adf_kpss_gate(returns, config)
    assert fit.w_star == 0
    assert fit.n_calibration_trajectories == 6


def test_adf_kpss_gate_validates_length() -> None:
    with pytest.raises(ValueError, match="need at least"):
        fit_adf_kpss_gate(np.ones((4, 499)))
