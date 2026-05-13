"""Unit tests for ecomd/risk/var_backtest.py and samplers (M1.4).

The math correctness tests use synthetic data where the true distribution
is known, so the expected VaR/ES + test statistics can be computed
analytically.
"""

from __future__ import annotations

import numpy as np
import pytest
from scipy.stats import norm

from ecomd.risk import (
    HistoricalSampler,
    christoffersen_cc_test,
    christoffersen_ind_test,
    kupiec_pof_test,
    rolling_backtest,
    var_es_from_paths,
)


# ──────────────────────────────────────────────────────────────────────────
# var_es_from_paths
# ──────────────────────────────────────────────────────────────────────────


def test_var_es_normal_paths_match_analytic() -> None:
    """For iid N(0, σ²) returns at horizon=1, VaR_α should match -σ·Φ⁻¹(1-α)."""
    rng = np.random.default_rng(0)
    sigma = 0.02
    n = 50_000
    paths = rng.normal(scale=sigma, size=(n, 1))
    var, es = var_es_from_paths(paths, alpha=0.95)
    # Analytic VaR_95: -sigma * Phi^-1(0.05) = sigma * 1.645
    expected_var = sigma * (-norm.ppf(0.05))
    assert abs(var - expected_var) < 0.001, f"VaR={var:.5f} vs analytic {expected_var:.5f}"
    # Analytic ES_95 for normal: sigma * phi(z_alpha) / (1-alpha)
    expected_es = sigma * norm.pdf(norm.ppf(0.05)) / 0.05
    assert abs(es - expected_es) < 0.002


def test_var_grows_with_horizon() -> None:
    """For iid normal, VaR over H days should scale roughly as √H · σ · 1.645."""
    rng = np.random.default_rng(0)
    sigma = 0.02
    n_paths = 20_000
    var_1d, _ = var_es_from_paths(rng.normal(scale=sigma, size=(n_paths, 1)), alpha=0.95)
    var_5d, _ = var_es_from_paths(rng.normal(scale=sigma, size=(n_paths, 5)), alpha=0.95)
    # 5d VaR should be roughly √5 ≈ 2.24× the 1d VaR
    ratio = var_5d / var_1d
    assert 1.8 < ratio < 2.7, f"5d/1d VaR ratio {ratio:.2f} outside [1.8, 2.7]"


def test_var_es_relationship() -> None:
    """ES ≥ VaR by definition (expected loss in tail ≥ tail threshold)."""
    rng = np.random.default_rng(0)
    paths = rng.normal(scale=0.02, size=(10_000, 1))
    var, es = var_es_from_paths(paths, alpha=0.95)
    assert es >= var


# ──────────────────────────────────────────────────────────────────────────
# Kupiec POF test
# ──────────────────────────────────────────────────────────────────────────


def test_kupiec_passes_when_violation_rate_matches() -> None:
    """500 trials with exactly 25 violations ≈ 5% expected → high p-value."""
    n = 500
    violations = np.zeros(n, dtype=int)
    rng = np.random.default_rng(0)
    idx = rng.choice(n, size=25, replace=False)
    violations[idx] = 1
    lr, p = kupiec_pof_test(violations, alpha=0.95)
    assert p > 0.5, f"Kupiec should not reject: p={p:.4f}"


def test_kupiec_rejects_when_too_many_violations() -> None:
    """500 trials with 75 violations (15% vs 5% expected) → tiny p-value."""
    n = 500
    violations = np.zeros(n, dtype=int)
    violations[:75] = 1
    lr, p = kupiec_pof_test(violations, alpha=0.95)
    assert p < 0.001, f"Kupiec should reject: p={p:.4e}"


def test_kupiec_rejects_when_too_few_violations() -> None:
    """500 trials with 5 violations (1% vs 5% expected) → small p-value."""
    n = 500
    violations = np.zeros(n, dtype=int)
    violations[:5] = 1
    lr, p = kupiec_pof_test(violations, alpha=0.95)
    assert p < 0.01, f"Kupiec should reject: p={p:.4e}"


def test_kupiec_handles_zero_violations() -> None:
    """No violations at all (n=500, alpha=0.95) → reject (expected ~25)."""
    violations = np.zeros(500, dtype=int)
    lr, p = kupiec_pof_test(violations, alpha=0.95)
    assert p < 0.001


# ──────────────────────────────────────────────────────────────────────────
# Christoffersen Independence test
# ──────────────────────────────────────────────────────────────────────────


def test_independence_passes_for_iid_violations() -> None:
    """Random Bernoulli violations should pass independence test."""
    rng = np.random.default_rng(0)
    violations = (rng.random(1000) < 0.05).astype(int)
    lr, p = christoffersen_ind_test(violations)
    assert p > 0.05, f"iid violations should pass: p={p:.4f}"


def test_independence_rejects_clustered_violations() -> None:
    """Clustered violations: violations come in runs of 5."""
    n = 1000
    violations = np.zeros(n, dtype=int)
    # Clusters of 5 consecutive violations every 100 steps
    for start in range(0, n, 100):
        violations[start:start + 5] = 1
    lr, p = christoffersen_ind_test(violations)
    assert p < 0.01, f"clustered violations should reject: p={p:.4f}"


# ──────────────────────────────────────────────────────────────────────────
# Conditional coverage (combined)
# ──────────────────────────────────────────────────────────────────────────


def test_cc_combines_pof_and_ind() -> None:
    """CC LR = POF LR + IND LR; CC p computed under chi2(df=2)."""
    rng = np.random.default_rng(0)
    violations = (rng.random(500) < 0.05).astype(int)
    pof_lr, _ = kupiec_pof_test(violations, alpha=0.95)
    ind_lr, _ = christoffersen_ind_test(violations)
    cc_lr, _ = christoffersen_cc_test(violations, alpha=0.95)
    assert abs(cc_lr - (pof_lr + ind_lr)) < 1e-9


# ──────────────────────────────────────────────────────────────────────────
# Rolling backtest end-to-end
# ──────────────────────────────────────────────────────────────────────────


def test_rolling_backtest_with_historical_sampler_passes_on_iid_data() -> None:
    """Historical Simulation on iid normal returns should pass all 3 tests."""
    rng = np.random.default_rng(0)
    n = 2500
    r = rng.normal(scale=0.01, size=n)
    sampler = HistoricalSampler(window=250)
    res = rolling_backtest(
        sampler=sampler.sample, real_returns=r,
        horizon=1, alpha=0.95, n_paths=500,
        train_window=500, sampler_name="hist", stride=2,
    )
    # On stationary iid data, historical sim should pass Kupiec
    # (rate matches expected) and independence (no clustering)
    assert res.passes_kupiec, (
        f"Kupiec failed: rate={res.violation_rate:.3f} expected={1-res.alpha:.3f}, p={res.kupiec_p:.4f}"
    )
    assert res.passes_independence, f"Indep failed: p={res.christoffersen_ind_p:.4f}"


def test_rolling_backtest_returns_arrays_of_correct_length() -> None:
    rng = np.random.default_rng(0)
    n = 1000
    r = rng.normal(scale=0.01, size=n)
    sampler = HistoricalSampler(window=200)
    res = rolling_backtest(
        sampler=sampler.sample, real_returns=r,
        horizon=1, alpha=0.95, n_paths=200, train_window=300, stride=1,
    )
    expected_n = n - 300 - 1 + 1  # train_window=300, horizon=1, stride=1
    assert res.n_predictions == expected_n
    assert res.var_series.size == expected_n
    assert res.es_series.size == expected_n
    assert res.actual_returns.size == expected_n
    assert res.violations.size == expected_n


def test_rolling_backtest_rejects_too_short_series() -> None:
    sampler = HistoricalSampler(window=100)
    with pytest.raises(ValueError):
        rolling_backtest(
            sampler=sampler.sample, real_returns=np.zeros(50),
            horizon=1, alpha=0.95, n_paths=100, train_window=100,
        )


# ──────────────────────────────────────────────────────────────────────────
# Sampler smoke
# ──────────────────────────────────────────────────────────────────────────


def test_historical_sampler_shape() -> None:
    s = HistoricalSampler(window=100)
    past = np.linspace(-0.05, 0.05, 200)
    out = s.sample(past, horizon=5, n_paths=50, seed=0)
    assert out.shape == (50, 5)
    assert np.all((out >= past[-100:].min()) & (out <= past[-100:].max()))


def test_historical_sampler_reproducibility() -> None:
    s = HistoricalSampler(window=100)
    past = np.linspace(-0.05, 0.05, 200)
    a = s.sample(past, horizon=5, n_paths=20, seed=42)
    b = s.sample(past, horizon=5, n_paths=20, seed=42)
    assert np.array_equal(a, b)
