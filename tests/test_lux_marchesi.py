"""Tests for the Lux-Marchesi 1999/2000 baseline ABM."""

from __future__ import annotations

import numpy as np
import pytest

from ecomd.baselines.lux_marchesi import (
    LuxMarchesi1999,
    LuxMarchesiParams,
)


@pytest.fixture
def short_run():
    sim = LuxMarchesi1999()
    return sim.run(n_steps=2000, dt=0.01, seed=0)


class TestBasics:
    def test_runs_without_error(self, short_run) -> None:
        assert short_run.log_price.shape == (2000,)
        assert short_run.n_fundamentalist.shape == (2000,)

    def test_agent_conservation(self, short_run) -> None:
        total = short_run.n_fundamentalist + short_run.n_optimist + short_run.n_pessimist
        n = LuxMarchesiParams().n_agents
        assert np.all(total == n), f"unique totals: {np.unique(total)}"

    def test_non_negative_populations(self, short_run) -> None:
        assert short_run.n_fundamentalist.min() >= 0
        assert short_run.n_optimist.min() >= 0
        assert short_run.n_pessimist.min() >= 0

    def test_opinion_index_bounded(self, short_run) -> None:
        x = short_run.opinion_index
        assert x.min() >= -1.0 - 1e-9
        assert x.max() <= 1.0 + 1e-9

    def test_returns_finite_and_bounded(self, short_run) -> None:
        r = short_run.log_returns
        assert np.all(np.isfinite(r))
        # Shouldn't be exploding; daily-scale log returns < 0.5 (50%) even with clustering
        assert np.abs(r).max() < 1.0, f"max |r|={np.abs(r).max()}"

    def test_seed_reproducibility(self) -> None:
        sim = LuxMarchesi1999()
        t1 = sim.run(n_steps=500, dt=0.01, seed=123)
        t2 = sim.run(n_steps=500, dt=0.01, seed=123)
        assert np.allclose(t1.log_price, t2.log_price)

    def test_different_seeds_diverge(self) -> None:
        sim = LuxMarchesi1999()
        t1 = sim.run(n_steps=500, dt=0.01, seed=1)
        t2 = sim.run(n_steps=500, dt=0.01, seed=2)
        assert not np.allclose(t1.log_price, t2.log_price)


class TestParameterValidation:
    def test_tiny_n_agents_raises(self) -> None:
        with pytest.raises(ValueError, match="n_agents"):
            LuxMarchesi1999(LuxMarchesiParams(n_agents=5))

    def test_bad_init_fractions_raise(self) -> None:
        with pytest.raises(ValueError, match="init fractions"):
            LuxMarchesi1999(LuxMarchesiParams(
                init_fraction_fundamentalist=0.7,
                init_fraction_optimist=0.5,
            ))


class TestHerdingLimit:
    """If herding is strong and trend-chasing / switching are zero, the chartist
    population should collapse into one polarity (|x| large) or the other."""

    def test_strong_herding_yields_polarization(self) -> None:
        params = LuxMarchesiParams(
            alpha_1=3.0,    # strong herding
            alpha_2=0.0,    # no trend chasing
            alpha_3=0.0,    # freeze chartist ↔ fundamentalist switching
            v2=0.0,         # no ± ↔ f transitions at all
            init_fraction_fundamentalist=0.5,
            init_fraction_optimist=0.25,   # neutral start
        )
        sim = LuxMarchesi1999(params)
        traj = sim.run(n_steps=3000, dt=0.01, seed=7)
        # After a warm-up, |x| should be substantial (|x| > 0.3) on average
        x_late = np.abs(traj.opinion_index[1000:])
        assert x_late.mean() > 0.3, f"|x| mean late = {x_late.mean()}"
