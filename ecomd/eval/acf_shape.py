"""ACF shape constraint + Ljung-Box statistic.

Prevents the Goodhart failure mode identified 2026-04-24 Session 17: a
simulator can satisfy a single-number ``acf_sq_mean`` target by producing
a FLAT autocorrelation curve (constant-variance noise regime) rather than
the real peak-and-decay structure of vol clustering. Real SPX daily ACF(r²)
peaks ~0.45 at lag 1 and decays to ~0.11 at lag 16; the ratio of 2-4× is a
universal signature of genuine clustering.

Two utilities:

1. ``acf_shape_loss``:  differentiable loss that penalizes flat ACF(r²).
   Penalty = max(0, target_ratio - measured_ratio) where
   measured_ratio = acf[1] / (|acf[max_lag]| + eps).
   Smooth, non-negative, zero when peak-decay is strong.

2. ``ljung_box_stat``:  non-differentiable statistic for reporting;
   gives a chi-squared test statistic and p-value for the null
   "returns are white noise" at a given set of lags.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
from torch import Tensor


# ─── Differentiable shape loss ─────────────────────────────────────────────


def acf_squared_per_lag(returns: Tensor, max_lag: int = 16) -> Tensor:
    """Per-lag ACF of squared returns. Returns a Tensor of shape (max_lag,).

    Differentiable in ``returns``. Output index 0 corresponds to lag 1.
    """
    r2 = returns ** 2
    r2_c = r2 - r2.mean()
    var = (r2_c ** 2).mean().clamp(min=1e-12)
    n = r2.shape[0]
    lags: list[Tensor] = []
    for tau in range(1, max_lag + 1):
        if tau >= n:
            break
        cov = (r2_c[:-tau] * r2_c[tau:]).mean()
        lags.append(cov / var)
    return torch.stack(lags)


def acf_shape_loss(
    returns: Tensor,
    target_ratio: float = 2.0,
    lag_peak: int = 1,
    lag_tail: int = 10,
    eps: float = 1e-3,
) -> Tensor:
    """Hinge-style penalty for flat ACF(r²) curves.

    We require ACF(r²)[lag_peak] / |ACF(r²)[lag_tail]| ≥ ``target_ratio``.
    Real SPX gives ~2.1; GARCH ~1.9; v0.6 ~1.7; but v1 H hybrid gave ~1.0
    (flat). Values > target_ratio give zero loss; below gives linear penalty.

    Differentiable.
    """
    curve = acf_squared_per_lag(returns, max_lag=max(lag_peak, lag_tail))
    if lag_peak > curve.shape[0] or lag_tail > curve.shape[0]:
        return returns.new_zeros(())
    a_peak = curve[lag_peak - 1]
    a_tail = curve[lag_tail - 1]
    # Ratio is ill-defined if a_tail near zero; use (|a_tail| + eps) in denom
    ratio = a_peak / (a_tail.abs() + eps)
    # Hinge: penalize when ratio below target
    return torch.relu(target_ratio - ratio)


# ─── Non-differentiable diagnostics ─────────────────────────────────────────


@dataclass
class LjungBoxResult:
    statistic: float  # Q_K
    dof: int          # degrees of freedom = K
    p_value: float    # from chi-sq survival
    lags_tested: int
    n_samples: int
    reject_white_noise: bool   # p < 0.05 means not white noise


def _chi2_sf(x: float, df: int) -> float:
    """Chi-squared survival function 1 - CDF. scipy.stats is a project dep."""
    try:
        from scipy.stats import chi2
        return float(chi2.sf(x, df))
    except ImportError:
        # Fallback: very loose approximation (should not be reached given pyproject deps)
        import math
        if x <= 0:
            return 1.0
        mean = df
        if x > 10 * mean:
            return 0.0
        if x < 0.01 * mean:
            return 1.0
        # crude linear interp on log-scale; only used if scipy missing
        return max(0.0, min(1.0, math.exp(-x / (2 * mean))))


def ljung_box_stat(returns: np.ndarray | Tensor, lags: int = 10,
                   squared: bool = True) -> LjungBoxResult:
    """Ljung-Box Q-statistic for autocorrelation significance.

    By default tests ACF of r² (squared returns) to detect vol clustering
    against the null "independent heteroscedastic returns". Set squared=False
    to test the raw return series.

    Args:
        returns: 1-D array/tensor of log returns.
        lags: number of lags K to include in the Q statistic.
        squared: if True, test r² autocorrelation; else test r autocorrelation.

    Returns:
        LjungBoxResult with chi-squared statistic, DoF, p-value.
    """
    if isinstance(returns, Tensor):
        r = returns.detach().cpu().numpy()
    else:
        r = np.asarray(returns)
    if squared:
        x = r ** 2
    else:
        x = r
    x = x - x.mean()
    n = len(x)
    var = (x * x).mean()
    if var <= 0:
        return LjungBoxResult(0.0, lags, 1.0, lags, n, False)
    # Sample ACF rho_k for k = 1..K
    rhos = []
    for k in range(1, lags + 1):
        if k >= n:
            break
        cov = (x[:-k] * x[k:]).mean()
        rhos.append(cov / var)
    actual_lags = len(rhos)
    if actual_lags == 0:
        return LjungBoxResult(0.0, 0, 1.0, 0, n, False)
    # Q = n(n+2) Σ_{k=1..K} ρ_k² / (n-k)
    q = 0.0
    for k, rho in enumerate(rhos, start=1):
        q += (rho * rho) / max(n - k, 1)
    q = n * (n + 2) * q
    p = _chi2_sf(q, actual_lags)
    return LjungBoxResult(
        statistic=float(q),
        dof=actual_lags,
        p_value=float(p),
        lags_tested=actual_lags,
        n_samples=n,
        reject_white_noise=bool(p < 0.05),
    )


__all__ = [
    "acf_squared_per_lag",
    "acf_shape_loss",
    "LjungBoxResult",
    "ljung_box_stat",
]
