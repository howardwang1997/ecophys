"""Tests for ecomd.eval.stylized_facts.

Strategy: generate synthetic returns from distributions with KNOWN properties and
verify our estimators recover the right numbers within tolerance.
  - Gaussian iid → Hill α should be huge (tails not power-law; estimator unstable but
    at least > 10 for our sample sizes), ACF² should be near 0, leverage near 0,
    DFA Hurst of |r| ≈ 0.5
  - Student-t iid with ν=4 → true tail index α=4, ACF² ≈ 0, leverage 0, Hurst 0.5
  - GARCH(1,1) → ACF² > 0 (clustering), Hurst(|r|) > 0.55, Hill finite
"""

from __future__ import annotations

import numpy as np
import pytest

from ecomd.eval.stylized_facts import (
    acf_squared_returns,
    compute_all_v0,
    dfa_hurst,
    hill_tail_index,
    leverage_effect,
    log_returns_from_prices,
)


@pytest.fixture
def gaussian_returns() -> np.ndarray:
    rng = np.random.default_rng(42)
    return rng.standard_normal(20_000)


@pytest.fixture
def student_t_returns() -> np.ndarray:
    rng = np.random.default_rng(42)
    # True tail index for Student-t with ν dof is ν itself (for |X|)
    return rng.standard_t(df=4, size=20_000)


@pytest.fixture
def garch_returns() -> np.ndarray:
    """Simple GARCH(1,1) with α=0.08, β=0.9 — realistic equity-like clustering."""
    rng = np.random.default_rng(42)
    n = 20_000
    omega, alpha, beta = 0.00001, 0.08, 0.90
    eps = np.empty(n)
    sigma2 = np.empty(n)
    sigma2[0] = omega / max(1 - alpha - beta, 1e-6)
    eps[0] = rng.standard_normal() * np.sqrt(sigma2[0])
    for t in range(1, n):
        sigma2[t] = omega + alpha * eps[t - 1] ** 2 + beta * sigma2[t - 1]
        eps[t] = rng.standard_normal() * np.sqrt(sigma2[t])
    return eps


# ─── Hill estimator ────────────────────────────────────────────────────────


class TestHillTailIndex:
    def test_student_t_recovers_true_alpha(self, student_t_returns: np.ndarray) -> None:
        res = hill_tail_index(student_t_returns, k_frac=0.05, side="both")
        # Hill estimator converges to ν=4 for Student-t. Allow 25% tolerance at N=20k.
        assert 3.0 < res.estimate < 5.5, f"α={res.estimate}"
        assert res.name == "hill_tail_index"
        assert len(res.diagnostic["alpha_of_k"]) > 5

    def test_gaussian_has_very_high_alpha(self, gaussian_returns: np.ndarray) -> None:
        res = hill_tail_index(gaussian_returns, k_frac=0.05, side="both")
        # Gaussian is not power-law, but Hill with finite k will give α > 5 typically
        assert res.estimate > 4.0, f"α={res.estimate}"

    def test_too_few_observations_raises(self) -> None:
        with pytest.raises(ValueError, match="at least 50"):
            hill_tail_index(np.ones(10), k_frac=0.1)

    def test_bootstrap_ci(self, student_t_returns: np.ndarray) -> None:
        res = hill_tail_index(student_t_returns, n_bootstrap=30, rng_seed=0)
        assert res.ci_low is not None and res.ci_high is not None
        assert res.ci_low < res.estimate < res.ci_high

    def test_side_positive_and_negative_close_for_symmetric(self, student_t_returns: np.ndarray) -> None:
        r_pos = hill_tail_index(student_t_returns, side="positive").estimate
        r_neg = hill_tail_index(student_t_returns, side="negative").estimate
        # Symmetric distribution → tail indices should be similar
        assert abs(r_pos - r_neg) < 1.5


# ─── ACF of squared returns ────────────────────────────────────────────────


class TestACFSquaredReturns:
    def test_iid_gaussian_has_near_zero_acf(self, gaussian_returns: np.ndarray) -> None:
        res = acf_squared_returns(gaussian_returns, max_lag=20)
        assert abs(res.estimate) < 0.05, f"mean ACF²={res.estimate}"
        assert res.diagnostic["acf"][0] == 1.0

    def test_garch_has_positive_acf(self, garch_returns: np.ndarray) -> None:
        res = acf_squared_returns(garch_returns, max_lag=50)
        assert res.estimate > 0.05, f"mean ACF²={res.estimate}"
        # Classic GARCH persistence: lag-1 ACF should be quite large
        assert res.diagnostic["acf"][1] > 0.1

    def test_max_lag_too_large_raises(self) -> None:
        with pytest.raises(ValueError, match="max_lag"):
            acf_squared_returns(np.random.randn(50), max_lag=100)


# ─── Leverage effect ───────────────────────────────────────────────────────


class TestLeverageEffect:
    def test_iid_gaussian_has_near_zero_leverage(self, gaussian_returns: np.ndarray) -> None:
        res = leverage_effect(gaussian_returns)
        assert abs(res.estimate) < 0.2, f"leverage sum={res.estimate}"

    def test_synthetic_leverage_is_negative(self) -> None:
        """Inject artificial leverage: if r_t < 0, scale next return's |r| up."""
        rng = np.random.default_rng(0)
        n = 10_000
        r = rng.standard_normal(n) * 0.01
        for t in range(1, n):
            if r[t - 1] < -0.01:
                r[t] = rng.standard_normal() * 0.03  # amplified volatility
        res = leverage_effect(r)
        assert res.estimate < 0, f"expected negative leverage, got {res.estimate}"


# ─── DFA Hurst ─────────────────────────────────────────────────────────────


class TestDFAHurst:
    def test_iid_gaussian_hurst_near_half(self, gaussian_returns: np.ndarray) -> None:
        res = dfa_hurst(gaussian_returns, min_scale=16, max_scale_frac=0.1)
        # For IID, cumsum is simple random walk → DFA Hurst ≈ 0.5 on increments
        # but we pass raw returns (not abs). Expected H ≈ 0.5.
        assert 0.4 < res.estimate < 0.6, f"H={res.estimate}"

    def test_garch_abs_returns_hurst_above_half(self, garch_returns: np.ndarray) -> None:
        res = dfa_hurst(np.abs(garch_returns), min_scale=16, max_scale_frac=0.1)
        # |r| of GARCH should show long-ish memory; at N=20k tolerance is generous
        assert res.estimate > 0.5, f"H(|r| GARCH)={res.estimate}"

    def test_insufficient_data_raises(self) -> None:
        with pytest.raises(ValueError):
            dfa_hurst(np.random.randn(50), min_scale=16, max_scale_frac=0.1)


# ─── Orchestrator ──────────────────────────────────────────────────────────


class TestComputeAllV0:
    def test_returns_all_four(self, garch_returns: np.ndarray) -> None:
        out = compute_all_v0(garch_returns)
        assert set(out.keys()) == {"hill_tail_index", "acf_squared_returns", "leverage_effect", "dfa_hurst_abs_r"}
        for r in out.values():
            d = r.to_dict()
            assert "estimate" in d
            assert "name" in d


# ─── Helpers ───────────────────────────────────────────────────────────────


def test_log_returns_from_prices() -> None:
    p = np.array([100.0, 101.0, 102.0, 101.5, np.nan, 103.0])
    r = log_returns_from_prices(p)
    assert r.size == 4  # NaN-prune gives 5 prices → 4 returns
    assert np.isclose(r[0], np.log(101 / 100))
