"""Tests for the AR(1)-SV baseline."""

from __future__ import annotations

import numpy as np
import pytest

from ecomd.baselines.ar1_sv import AR1SV


def test_shape_finite_and_seed_reproducibility() -> None:
    simulator = AR1SV(mu=0.001, rho=-0.1, alpha=-8.0, phi=0.8, nu=0.3)
    first = simulator.simulate(1000, seed=17, burn_in=50)
    second = simulator.simulate(1000, seed=17, burn_in=50)
    assert first.shape == (1000,)
    assert np.all(np.isfinite(first))
    assert np.array_equal(first, second)


def test_variance_multiplier_changes_identical_seed_initial_state() -> None:
    simulator = AR1SV(mu=0.0, rho=0.0, alpha=-8.0, phi=0.8, nu=0.3)
    low = simulator.simulate(1, seed=17, burn_in=0, initial_variance_multiplier=0.1)
    high = simulator.simulate(1, seed=17, burn_in=0, initial_variance_multiplier=10.0)
    assert np.isclose(abs(high[0]) / abs(low[0]), 10.0)


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"n_steps": 0}, "n_steps"),
        ({"n_steps": 1, "burn_in": -1}, "burn_in"),
        ({"n_steps": 1, "initial_variance_multiplier": float("nan")}, "multiplier"),
    ],
)
def test_invalid_simulation_controls_rejected(
    kwargs: dict[str, int | float],
    message: str,
) -> None:
    simulator = AR1SV()
    with pytest.raises(ValueError, match=message):
        simulator.simulate(**kwargs)
