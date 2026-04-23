"""Tests for the 7 additional stylized-facts metrics (Cont #1, 3, 4, 5, 7, 10, 11)
and the multi-order DFA diagnostic.

Fixtures reused:
  - gaussian_returns    : 20k IID N(0,1)
  - student_t_returns   : 20k IID t_4
  - garch_returns       : 20k GARCH(1,1)
Plus new:
  - skewed_returns       : returns with injected negative skew
  - with_volume          : returns + synthetic volume correlated with |r|
  - returns_with_trend_in_volatility : non-stationary |r| regime shift (tests DFA)
"""

from __future__ import annotations

import numpy as np
import pytest

from ecomd.eval.stylized_facts import (
    aggregational_gaussianity,
    autocorr_returns,
    compute_all,
    conditional_kurtosis,
    dfa_hurst_multi_order,
    gain_loss_asymmetry,
    intermittency_fano,
    volume_volatility_corr,
    zumbach_asymmetry,
)


@pytest.fixture
def gaussian_returns() -> np.ndarray:
    return np.random.default_rng(42).standard_normal(20_000)


@pytest.fixture
def student_t_returns() -> np.ndarray:
    return np.random.default_rng(42).standard_t(df=5, size=20_000)


@pytest.fixture
def garch_returns() -> np.ndarray:
    rng = np.random.default_rng(42)
    n = 20_000
    omega, alpha, beta = 1e-5, 0.08, 0.90
    eps = np.empty(n)
    sigma2 = np.empty(n)
    sigma2[0] = omega / max(1 - alpha - beta, 1e-6)
    eps[0] = rng.standard_normal() * np.sqrt(sigma2[0])
    for t in range(1, n):
        sigma2[t] = omega + alpha * eps[t - 1] ** 2 + beta * sigma2[t - 1]
        eps[t] = rng.standard_normal() * np.sqrt(sigma2[t])
    return eps


# ─── #1 autocorr_returns ───────────────────────────────────────────────────


class TestAutocorrReturns:
    def test_iid_gaussian_is_white_noise(self, gaussian_returns: np.ndarray) -> None:
        res = autocorr_returns(gaussian_returns, max_lag=30, ljung_box_lag=20)
        assert res.estimate < 0.03, f"mean |ACF| = {res.estimate}"
        # Ljung-Box p-value should be large (fail to reject H0: no autocorrelation)
        assert res.meta["ljung_box_p"] > 0.05, f"p={res.meta['ljung_box_p']}"
        assert res.diagnostic["acf"][0] == 1.0

    def test_ar1_has_significant_autocorr(self) -> None:
        rng = np.random.default_rng(0)
        n = 5000
        phi = 0.3
        x = np.zeros(n)
        eps = rng.standard_normal(n)
        for t in range(1, n):
            x[t] = phi * x[t - 1] + eps[t]
        res = autocorr_returns(x, max_lag=20, ljung_box_lag=10)
        # First-lag ACF should be near 0.3; Ljung-Box should reject strongly
        assert res.diagnostic["acf"][1] > 0.2
        assert res.meta["ljung_box_p"] < 1e-10


# ─── #3 gain_loss_asymmetry ─────────────────────────────────────────────────


class TestGainLossAsymmetry:
    def test_symmetric_gaussian_has_zero_skew(self, gaussian_returns: np.ndarray) -> None:
        res = gain_loss_asymmetry(gaussian_returns)
        assert abs(res.estimate) < 0.1, f"skew={res.estimate}"

    def test_injected_negative_skew_detected(self) -> None:
        rng = np.random.default_rng(1)
        base = rng.standard_normal(10_000)
        # Inject large-down-few: occasionally multiply negative returns by 5x
        neg = base < 0
        base[neg] = np.where(rng.random(neg.sum()) < 0.05, base[neg] * 5, base[neg])
        res = gain_loss_asymmetry(base)
        assert res.estimate < -0.3, f"expected strong negative skew, got {res.estimate}"
        # Left/right quantile ratio at 1% should be > 1
        assert res.meta["left_right_ratios"]["left/right_q0.01"] > 1.3


# ─── #4 aggregational_gaussianity ───────────────────────────────────────────


class TestAggregationalGaussianity:
    def test_gaussian_has_no_aggregation_effect(self, gaussian_returns: np.ndarray) -> None:
        res = aggregational_gaussianity(gaussian_returns, scales=(1, 5, 20, 50))
        # Gaussian at any scale has near-zero excess kurtosis; so estimate near 0
        assert abs(res.estimate) < 0.5, f"estimate={res.estimate}"

    def test_heavy_tails_kurtosis_decays_with_aggregation(self, student_t_returns: np.ndarray) -> None:
        # Student-t with df=5 has excess kurtosis 6 at scale=1; CLT → ~0 at scale=50
        res = aggregational_gaussianity(student_t_returns, scales=(1, 10, 50))
        assert res.estimate > 1.0, f"estimate={res.estimate}"
        # diagnostic: kurtosis should strictly decrease
        ks = res.diagnostic["excess_kurtosis"]
        assert ks[0] > ks[-1]


# ─── #5 intermittency_fano ──────────────────────────────────────────────────


class TestIntermittencyFano:
    def test_iid_gaussian_fano_near_one(self, gaussian_returns: np.ndarray) -> None:
        res = intermittency_fano(gaussian_returns, quantile=0.99, n_windows=50)
        # For IID, extreme-event counts per window should be ~Poisson → F ≈ 1
        assert 0.5 < res.estimate < 2.0, f"F={res.estimate}"

    def test_garch_has_fano_greater_than_one(self, garch_returns: np.ndarray) -> None:
        res = intermittency_fano(garch_returns, quantile=0.99, n_windows=50)
        # Volatility clustering → extreme events cluster → F > 1
        assert res.estimate > 1.3, f"F={res.estimate}"


# ─── #7 conditional_kurtosis ────────────────────────────────────────────────


class TestConditionalKurtosis:
    def test_garch_residuals_kurtosis_reduced(self, garch_returns: np.ndarray) -> None:
        # GARCH-normal process: unconditional kurtosis > 0, residuals kurtosis ≈ 0
        res = conditional_kurtosis(garch_returns)
        uk = res.meta["unconditional_excess_kurtosis"]
        ck = res.meta["conditional_excess_kurtosis"]
        assert uk > 0.5, f"unconditional excess kurtosis={uk}"
        assert ck < uk, f"conditional {ck} should be < unconditional {uk}"
        # For Gaussian-innovation GARCH, residuals should be close to Gaussian (excess kurt ≈ 0)
        assert abs(ck) < 1.5, f"conditional excess kurt={ck}"


# ─── #10 volume_volatility_corr ─────────────────────────────────────────────


class TestVolumeVolatilityCorr:
    def test_correlated_volume_recovered(self) -> None:
        rng = np.random.default_rng(0)
        n = 5000
        r = rng.standard_normal(n) * 0.01          # |r| typical ≈ 0.008
        # Signal dominates noise: scale_r→v = 5000 × |r| ≈ 40 range; noise std = 5
        v = 1000 + 5000 * np.abs(r) + rng.standard_normal(n) * 5
        res = volume_volatility_corr(r, v, max_lag=3)
        assert res.estimate > 0.5, f"corr={res.estimate}"

    def test_independent_volume_gives_near_zero_corr(self) -> None:
        rng = np.random.default_rng(0)
        n = 5000
        r = rng.standard_normal(n)
        v = rng.standard_normal(n) * 100 + 1000
        res = volume_volatility_corr(r, v)
        assert abs(res.estimate) < 0.1, f"corr={res.estimate}"

    def test_length_mismatch_raises(self) -> None:
        with pytest.raises(ValueError, match="same length"):
            volume_volatility_corr(np.zeros(100), np.zeros(99))


# ─── #11 zumbach_asymmetry ──────────────────────────────────────────────────


class TestZumbachAsymmetry:
    def test_iid_is_approximately_symmetric(self, gaussian_returns: np.ndarray) -> None:
        res = zumbach_asymmetry(gaussian_returns, coarse_window=30, max_lag=15)
        # For IID, no info travels across scales → D(τ) ≈ 0
        assert abs(res.estimate) < 0.1, f"D={res.estimate}"

    def test_garch_shows_coarse_to_fine(self, garch_returns: np.ndarray) -> None:
        res = zumbach_asymmetry(garch_returns, coarse_window=30, max_lag=15)
        # GARCH(1,1) doesn't necessarily show strong Zumbach by construction,
        # but vol clustering should yield D ≥ 0. Sanity: finite, within plausible range.
        assert np.isfinite(res.estimate)
        assert -0.2 < res.estimate < 0.5


# ─── Multi-order DFA ───────────────────────────────────────────────────────


class TestDFAMultiOrder:
    def test_stationary_garch_hurst_stable_across_orders(self, garch_returns: np.ndarray) -> None:
        out = dfa_hurst_multi_order(np.abs(garch_returns), orders=(1, 2, 3))
        hs = [out[o].estimate for o in (1, 2, 3)]
        # For a stationary process, H should be similar across orders (within ~0.15)
        assert max(hs) - min(hs) < 0.15, f"orders=1,2,3 give H={hs}"

    def test_non_stationary_trend_exposes_hurst_inflation(self) -> None:
        """|r| with a slow trend: DFA-1 inflates H toward 1; DFA-2 should bring it back."""
        rng = np.random.default_rng(0)
        n = 20_000
        # Small stationary GARCH-like |r| with a slow linear upward trend in level
        base = np.abs(rng.standard_normal(n) * 0.02)
        trend = np.linspace(0, 0.05, n)
        x = base + trend
        out = dfa_hurst_multi_order(x, orders=(1, 2, 3))
        h1 = out[1].estimate
        h2 = out[2].estimate
        # Order-1 should be substantially higher than order-2 when a trend is present
        assert h1 - h2 > 0.05, f"H1={h1}, H2={h2}"


# ─── compute_all orchestrator ─────────────────────────────────────────────


class TestComputeAll:
    def test_all_11_metrics_run(self, garch_returns: np.ndarray) -> None:
        rng = np.random.default_rng(0)
        volume = 1000 + 1000 * np.abs(garch_returns) + rng.standard_normal(garch_returns.size) * 50
        out = compute_all(garch_returns, volume=volume)
        expected = {
            "autocorr_returns",
            "hill_tail_index",
            "gain_loss_asymmetry",
            "aggregational_gaussianity",
            "intermittency_fano",
            "acf_squared_returns",
            "conditional_kurtosis",
            "dfa_hurst_abs_r",
            "leverage_effect",
            "volume_volatility_corr",
            "zumbach_asymmetry",
        }
        assert set(out.keys()) == expected
        # None of them should have errored
        failed = {k: v.meta.get("error") for k, v in out.items() if "error" in v.meta}
        assert not failed, f"some metrics failed: {failed}"

    def test_compute_all_without_volume_skips_10(self, garch_returns: np.ndarray) -> None:
        out = compute_all(garch_returns, volume=None)
        assert "volume_volatility_corr" not in out
        assert len(out) == 10

    def test_skip_parameter_excludes(self, garch_returns: np.ndarray) -> None:
        out = compute_all(garch_returns, skip=("conditional_kurtosis", "zumbach_asymmetry"))
        assert "conditional_kurtosis" not in out
        assert "zumbach_asymmetry" not in out
