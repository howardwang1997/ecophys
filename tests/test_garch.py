"""Tests for GARCH(1,1) baseline."""

from __future__ import annotations

import numpy as np
import pytest

from ecomd.baselines.garch import GARCH11, GARCH11Params


class TestParams:
    def test_stationarity_required(self) -> None:
        with pytest.raises(ValueError, match="stationarity"):
            GARCH11Params(omega=1e-6, alpha=0.5, beta=0.51)

    def test_negative_params_rejected(self) -> None:
        with pytest.raises(ValueError):
            GARCH11Params(omega=-1e-6, alpha=0.1, beta=0.8)
        with pytest.raises(ValueError):
            GARCH11Params(omega=1e-6, alpha=-0.1, beta=0.8)

    def test_student_t_needs_nu(self) -> None:
        with pytest.raises(ValueError, match="nu"):
            GARCH11Params(omega=1e-6, alpha=0.1, beta=0.8, dist="t")

    def test_unconditional_variance(self) -> None:
        p = GARCH11Params(omega=1e-4, alpha=0.05, beta=0.90)
        # ω / (1 - α - β) = 1e-4 / 0.05 = 2e-3
        assert np.isclose(p.unconditional_variance(), 2e-3)


class TestSimulate:
    def test_shape_and_finite(self) -> None:
        sim = GARCH11(omega=1e-6, alpha=0.08, beta=0.90)
        r = sim.simulate(n_steps=2000, seed=0, burn_in=200)
        assert r.shape == (2000,)
        assert np.all(np.isfinite(r))

    def test_seed_reproducibility(self) -> None:
        sim = GARCH11(omega=1e-6, alpha=0.08, beta=0.90)
        r1 = sim.simulate(1000, seed=42)
        r2 = sim.simulate(1000, seed=42)
        assert np.allclose(r1, r2)

    def test_student_t_produces_fatter_tails(self) -> None:
        from scipy.stats import kurtosis
        sim_n = GARCH11(omega=1e-6, alpha=0.05, beta=0.90, dist="normal")
        sim_t = GARCH11(omega=1e-6, alpha=0.05, beta=0.90, dist="t", nu=4.5)
        r_n = sim_n.simulate(20_000, seed=1)
        r_t = sim_t.simulate(20_000, seed=1)
        k_n = kurtosis(r_n, fisher=True)
        k_t = kurtosis(r_t, fisher=True)
        assert k_t > k_n + 2.0, f"t kurtosis {k_t} not meaningfully > normal {k_n}"

    def test_volatility_clustering_present(self) -> None:
        sim = GARCH11(omega=1e-6, alpha=0.08, beta=0.90)
        r = sim.simulate(20_000, seed=1)
        r2 = r ** 2
        x = r2 - r2.mean()
        acf1 = float(np.dot(x[:-1], x[1:]) / np.dot(x, x))
        # GARCH(1,1) at α+β=0.98 should show strong ACF in r²
        assert acf1 > 0.05, f"ACF(r²) lag-1 = {acf1}"


class TestFit:
    def test_roundtrip_fit_and_simulate(self) -> None:
        # Generate synthetic returns from a known GARCH, fit, re-simulate, check stats
        true_sim = GARCH11(omega=2e-6, alpha=0.07, beta=0.91)
        true_r = true_sim.simulate(10_000, seed=0)
        # Fit with Normal innovations (matches what we generated)
        fitted = GARCH11.fit(true_r, dist="normal")
        # Fitted params should be in the ballpark (not exact — finite sample)
        assert 0.02 < fitted.params.alpha < 0.15, f"α̂={fitted.params.alpha}"
        assert 0.80 < fitted.params.beta < 0.98, f"β̂={fitted.params.beta}"
        assert fitted.params.alpha + fitted.params.beta > 0.9
        # Simulating from fit should still be stationary and well-behaved
        r_sim = fitted.simulate(5000, seed=7)
        assert np.all(np.isfinite(r_sim))
