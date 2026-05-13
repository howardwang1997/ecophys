"""Unit tests for ecomd/eval/distributional_metrics.py (M1.3)."""

from __future__ import annotations

import numpy as np

from ecomd.eval.distributional_metrics import (
    acf_distance,
    all_distances,
    hurst_distance,
    ks_tail,
    mmd_returns,
    wasserstein1d_np,
)


def test_wasserstein_zero_for_identical() -> None:
    rng = np.random.default_rng(0)
    x = rng.normal(size=1000)
    assert wasserstein1d_np(x, x) < 1e-10


def test_wasserstein_increases_with_shift() -> None:
    rng = np.random.default_rng(0)
    x = rng.normal(size=1000)
    d_small = wasserstein1d_np(x, x + 0.1)
    d_large = wasserstein1d_np(x, x + 1.0)
    assert 0 < d_small < d_large


def test_wasserstein_handles_unequal_sample_sizes() -> None:
    rng = np.random.default_rng(0)
    x = rng.normal(size=1000)
    y = rng.normal(size=500)
    d = wasserstein1d_np(x, y)
    assert np.isfinite(d) and d >= 0


def test_mmd_zero_for_same_distribution() -> None:
    rng = np.random.default_rng(0)
    x = rng.normal(size=2000)
    y = rng.normal(size=2000)  # different sample, same distribution
    # Two iid normal samples: MMD² should be near zero (within sampling noise)
    d = mmd_returns(x, y)
    assert d < 0.05


def test_mmd_positive_for_different_distributions() -> None:
    rng = np.random.default_rng(0)
    x = rng.normal(size=2000)
    y = rng.standard_t(df=3, size=2000) * 0.5  # heavier tails
    same = mmd_returns(x, rng.normal(size=2000))
    diff = mmd_returns(x, y)
    # Different distributions should be measurably more separated than two
    # iid normal samples; absolute scale depends on bandwidth choice.
    assert diff > 3 * same, f"diff={diff:.5f} should clearly exceed same={same:.5f}"


def test_ks_tail_distinguishes_tail_heaviness() -> None:
    rng = np.random.default_rng(0)
    real = rng.standard_t(df=5, size=5000) * 0.01
    sim_normal = rng.normal(size=5000) * 0.01
    sim_heavy = rng.standard_t(df=4, size=5000) * 0.01
    d_normal_vs_real = ks_tail(sim_normal, real)
    d_heavy_vs_real = ks_tail(sim_heavy, real)
    # Heavy sim should be closer to the t-distributed real than gaussian sim
    assert d_heavy_vs_real < d_normal_vs_real
    assert 0 <= d_heavy_vs_real <= 1
    assert 0 <= d_normal_vs_real <= 1


def test_acf_distance_zero_for_identical() -> None:
    rng = np.random.default_rng(0)
    x = rng.normal(size=2000)
    assert acf_distance(x, x) < 1e-10


def test_acf_distance_detects_autocorrelation() -> None:
    rng = np.random.default_rng(0)
    n = 3000
    iid = rng.normal(size=n)
    # AR(1) with rho=0.9
    ar1 = np.zeros(n)
    eps = rng.normal(size=n)
    for t in range(1, n):
        ar1[t] = 0.9 * ar1[t - 1] + eps[t]
    d = acf_distance(iid, ar1)
    assert d > 0.1, f"expected ACF distance > 0.1 for iid vs AR(0.9), got {d:.4f}"


def test_hurst_distance_finite() -> None:
    rng = np.random.default_rng(0)
    x = rng.normal(size=2000)
    y = rng.normal(size=2000)
    d = hurst_distance(x, y)
    assert np.isfinite(d) and d >= 0


def test_all_distances_returns_full_dict() -> None:
    rng = np.random.default_rng(0)
    x = rng.normal(size=1000)
    y = rng.normal(size=1000)
    d = all_distances(x, y)
    assert set(d.keys()) == {"wasserstein", "mmd", "ks_tail", "acf_l1", "acf2_l1", "hurst_dist"}
    for k, v in d.items():
        assert np.isfinite(v) or np.isnan(v), f"{k}: {v}"


def test_handles_short_series_gracefully() -> None:
    """Tiny sample sizes should return NaN, not crash."""
    x = np.array([0.1, 0.2])
    y = np.array([0.3, 0.4])
    d = all_distances(x, y)
    # Most metrics should be NaN; wasserstein should still work for small n
    assert np.isnan(d["mmd"]) or np.isfinite(d["mmd"])
    assert np.isnan(d["acf_l1"])  # not enough lags
    assert np.isnan(d["hurst_dist"])  # too short
