"""M1.3 — Distributional distance metrics for evaluation (NeurIPS 2027 plan).

Standard distributional distances on simulated vs real returns, used to
augment the 11-fact pass/fail scoring with continuous metrics that the ML
audience expects (MMD, KS, Wasserstein-1, ACF distance, Hurst distance).

These are *evaluation* metrics: pure numpy, no autograd. The training-time
counterparts in ``ecomd/training/losses.py`` are torch-based for
differentiability; we deliberately don't share code paths to keep the
evaluation pipeline independent of training-side numerics.

Designed for use from ``scripts/score_*.py``: each function takes 1-D
return arrays and returns a single non-negative scalar (lower = closer
distributions).
"""

from __future__ import annotations

from typing import Sequence

import numpy as np
from scipy.stats import ks_2samp


def _clean(x: np.ndarray) -> np.ndarray:
    """Drop NaN/inf, return contiguous float64."""
    arr = np.asarray(x, dtype=np.float64).ravel()
    return arr[np.isfinite(arr)]


def wasserstein1d_np(sim: np.ndarray, real: np.ndarray) -> float:
    """1-D Wasserstein-1 distance via sorted-L1 with quantile resampling.

    Pure-numpy mirror of ``ecomd.training.losses.wasserstein1d``. Uses
    linear interpolation in quantile space when sample sizes differ.
    """
    s = np.sort(_clean(sim))
    r = np.sort(_clean(real))
    if s.size == 0 or r.size == 0:
        return float("nan")
    n = min(s.size, r.size)
    if s.size != n:
        s = np.interp(np.linspace(0, 1, n), np.linspace(0, 1, s.size), s)
    if r.size != n:
        r = np.interp(np.linspace(0, 1, n), np.linspace(0, 1, r.size), r)
    return float(np.mean(np.abs(s - r)))


def mmd_returns(
    sim: np.ndarray,
    real: np.ndarray,
    bandwidths: Sequence[float] = (0.005, 0.01, 0.02, 0.05),
    n_subsample: int = 4000,
    seed: int = 0,
) -> float:
    """Maximum Mean Discrepancy² with multi-bandwidth Gaussian kernel.

    Returns biased MMD² estimator (sum over kernel matrices). Multi-
    bandwidth handles the wide range of return magnitudes (intraday vs
    daily). Subsamples to ``n_subsample`` per side to keep the O(n²)
    kernel matrix tractable; default 4000² = 16M floats = 128MB at f64.

    Reference: Gretton et al., JMLR 2012.
    """
    s = _clean(sim)
    r = _clean(real)
    if s.size < 2 or r.size < 2:
        return float("nan")
    rng = np.random.default_rng(seed)
    if s.size > n_subsample:
        s = rng.choice(s, n_subsample, replace=False)
    if r.size > n_subsample:
        r = rng.choice(r, n_subsample, replace=False)
    s = s[:, None]
    r = r[:, None]
    # Squared-distance matrices
    dss = ((s - s.T) ** 2)
    drr = ((r - r.T) ** 2)
    dsr = ((s - r.T) ** 2)
    mmd2 = 0.0
    for h in bandwidths:
        gamma = 1.0 / (2.0 * h * h)
        kss = np.exp(-gamma * dss).mean()
        krr = np.exp(-gamma * drr).mean()
        ksr = np.exp(-gamma * dsr).mean()
        mmd2 += kss + krr - 2 * ksr
    return float(max(0.0, mmd2 / len(bandwidths)))


def ks_tail(sim: np.ndarray, real: np.ndarray, q: float = 0.95) -> float:
    """KS distance between the two TAILS (|x| > quantile q of |real|).

    Standard KS on full distribution masks tail mismatches because most
    mass is in the body. Conditioning on the tail makes the metric
    sensitive to the heavy-tailed regime that drives crash dynamics.
    Default q=0.95 → top 5% of |real| by magnitude.

    Returns the KS statistic D ∈ [0, 1] (lower is better).
    """
    s = _clean(sim)
    r = _clean(real)
    if s.size < 10 or r.size < 10:
        return float("nan")
    thresh = np.quantile(np.abs(r), q)
    s_tail = s[np.abs(s) > thresh]
    r_tail = r[np.abs(r) > thresh]
    if s_tail.size < 5 or r_tail.size < 5:
        return float("nan")
    res = ks_2samp(s_tail, r_tail)
    return float(res.statistic)


def acf_distance(
    sim: np.ndarray,
    real: np.ndarray,
    lags: Sequence[int] = (1, 2, 5, 10, 20, 50),
    on_squared: bool = False,
) -> float:
    """L1 distance between empirical autocorrelation functions at given lags.

    Compares ACF of returns (or returns² if ``on_squared=True``) between
    simulated and real series. ACF on squared returns probes volatility
    clustering (Cont 2001 fact #6); ACF on raw returns probes
    autocorr_returns (fact #1).
    """
    s = _clean(sim)
    r = _clean(real)
    if s.size < max(lags) + 10 or r.size < max(lags) + 10:
        return float("nan")
    if on_squared:
        s = s * s
        r = r * r
    s = s - s.mean()
    r = r - r.mean()
    s_var = (s * s).sum()
    r_var = (r * r).sum()
    if s_var == 0 or r_var == 0:
        return float("nan")
    diffs = []
    for k in lags:
        s_acf = float((s[k:] * s[:-k]).sum() / s_var)
        r_acf = float((r[k:] * r[:-k]).sum() / r_var)
        diffs.append(abs(s_acf - r_acf))
    return float(np.mean(diffs))


def hurst_distance(sim: np.ndarray, real: np.ndarray) -> float:
    """Absolute difference of DFA-Hurst exponent estimates on |returns|.

    Uses windowed standard-deviation regression on log-spaced scales
    (a simplified DFA proxy that's robust on short series). Ground-truth
    Hurst for memoryless returns is 0.5; financial returns typically
    show 0.6-0.9 on |r|.
    """
    s = _clean(sim)
    r = _clean(real)
    if s.size < 100 or r.size < 100:
        return float("nan")
    h_s = _windowed_hurst(np.abs(s))
    h_r = _windowed_hurst(np.abs(r))
    if not np.isfinite(h_s) or not np.isfinite(h_r):
        return float("nan")
    return float(abs(h_s - h_r))


def _windowed_hurst(x: np.ndarray) -> float:
    """Hurst exponent via std vs window-size log-log regression.

    For x[t] iid: std(x_window) ≈ const → slope 0 → H ≈ 0.5.
    For long-memory: std(x_window) ∝ window^H.
    """
    n = x.size
    scales = np.unique(np.geomspace(8, max(8, n // 4), num=10).astype(int))
    stds = []
    used = []
    for w in scales:
        m = n // w
        if m < 4:
            continue
        chunks = x[: m * w].reshape(m, w)
        stds.append(chunks.std(axis=1).mean())
        used.append(w)
    if len(used) < 3:
        return float("nan")
    log_w = np.log(np.array(used))
    log_s = np.log(np.array(stds))
    # Linear fit slope
    slope, _ = np.polyfit(log_w, log_s, 1)
    return float(slope)


def all_distances(sim: np.ndarray, real: np.ndarray) -> dict[str, float]:
    """Compute all five distributional distances in one call.

    Convenience wrapper used by `scripts/score_continuous.py`. Returns
    dict[str, float] of {wasserstein, mmd, ks_tail, acf_l1, acf2_l1,
    hurst}.
    """
    return {
        "wasserstein": wasserstein1d_np(sim, real),
        "mmd": mmd_returns(sim, real),
        "ks_tail": ks_tail(sim, real),
        "acf_l1": acf_distance(sim, real, on_squared=False),
        "acf2_l1": acf_distance(sim, real, on_squared=True),
        "hurst_dist": hurst_distance(sim, real),
    }
