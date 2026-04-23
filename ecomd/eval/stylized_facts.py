"""Stylized-facts evaluation suite (v0 — first 4 of Cont 2001's 11 facts).

Implemented here:
  1. Fat tails          → Hill tail-index estimator (α; typical equity α≈3)
  2. Volatility clustering → ACF of squared returns (slow decay, ~power-law)
  3. Leverage effect    → cross-correlation Corr(r_t, r_{t+τ}^2); expect negative at small τ
  4. Long memory in |r| → DFA Hurst exponent (typical equity H≈0.6–0.7)

Each function takes a 1-D array/Series of log returns (not prices) and returns a
`StylizedFactResult` containing the point estimate, diagnostic arrays, and metadata.
Bootstrap CIs are optional and opt-in (can be expensive on long series).

Conventions:
  - Inputs are numpy arrays of float; pass pd.Series.values if needed
  - Returns are log returns r_t = ln(P_t) - ln(P_{t-1}); NaN-stripped before analysis
  - All outputs are JSON-serialisable via `.to_dict()` so we can dump per-experiment
    reference tables.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

import numpy as np
import numpy.typing as npt


ArrayF = npt.NDArray[np.float64]


# ─────────────────────────────────────────────────────────────────────────────
# Result container
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class StylizedFactResult:
    name: str
    estimate: float
    ci_low: float | None = None
    ci_high: float | None = None
    diagnostic: dict[str, list[float]] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Fat tails — Hill estimator
# ─────────────────────────────────────────────────────────────────────────────


def hill_tail_index(
    returns: ArrayF,
    k_frac: float = 0.05,
    side: str = "both",
    n_bootstrap: int = 0,
    rng_seed: int | None = 0,
) -> StylizedFactResult:
    """Hill estimator for the tail exponent α of |r|.

    H_k = (1/k) Σ_{i=1..k} log(X_{(i)} / X_{(k+1)})     where X_(i) are the top-k
    order statistics of |r| sorted descending. α = 1/H_k.

    Parameters
    ----------
    returns   : 1-D array of log returns
    k_frac    : fraction of the sample used as tail (default 5%)
    side      : 'both' (use |r|), 'positive', or 'negative'
    n_bootstrap : if > 0, compute 95% bootstrap CI for α

    Notes
    -----
    The Hill estimator is sensitive to k. Cont (2001) recommends plotting the Hill
    estimate vs k and looking for a plateau; we return diagnostic arrays so the
    caller can inspect.
    """
    r = _clean(returns)
    if side == "both":
        x = np.abs(r)
    elif side == "positive":
        x = r[r > 0]
    elif side == "negative":
        x = -r[r < 0]
    else:
        raise ValueError(f"side must be 'both'|'positive'|'negative', got {side!r}")

    x = np.sort(x)[::-1]  # descending
    n = x.size
    if n < 50:
        raise ValueError(f"need at least 50 observations for a reliable Hill estimate, got {n}")

    k = max(int(np.floor(k_frac * n)), 10)
    top = x[:k]
    cutoff = x[k]
    if cutoff <= 0:
        raise ValueError("zero cutoff; tail is degenerate")
    hill = float(np.mean(np.log(top / cutoff)))
    alpha = 1.0 / hill

    # diagnostic: Hill plot over a range of k
    ks = np.unique(np.round(np.geomspace(max(10, n // 1000), n // 4, num=40)).astype(int))
    diag_alpha = []
    for kk in ks:
        if kk < n:
            h = float(np.mean(np.log(x[:kk] / x[kk])))
            diag_alpha.append(1.0 / h if h > 0 else float("nan"))
        else:
            diag_alpha.append(float("nan"))

    ci_lo, ci_hi = None, None
    if n_bootstrap > 0:
        rng = np.random.default_rng(rng_seed)
        boot = np.empty(n_bootstrap, dtype=np.float64)
        for b in range(n_bootstrap):
            sample = rng.choice(r, size=r.size, replace=True)
            try:
                sub = hill_tail_index(sample, k_frac=k_frac, side=side, n_bootstrap=0)
                boot[b] = sub.estimate
            except ValueError:
                boot[b] = np.nan
        boot = boot[np.isfinite(boot)]
        ci_lo, ci_hi = float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))

    return StylizedFactResult(
        name="hill_tail_index",
        estimate=alpha,
        ci_low=ci_lo,
        ci_high=ci_hi,
        diagnostic={"ks": ks.tolist(), "alpha_of_k": diag_alpha},
        meta={"n": n, "k": k, "k_frac": k_frac, "side": side},
    )


# ─────────────────────────────────────────────────────────────────────────────
# 2. Volatility clustering — ACF of squared returns
# ─────────────────────────────────────────────────────────────────────────────


def acf_squared_returns(
    returns: ArrayF,
    max_lag: int = 100,
) -> StylizedFactResult:
    """Autocorrelation of r_t^2 at lags 1..max_lag.

    Cont 2001 fact #4: Corr(r_t^2, r_{t-τ}^2) is positive and decays slowly with τ
    (approximately power-law or stretched-exponential). We report the mean ACF
    over lags 1..20 as a single scalar 'estimate', and the full ACF in diagnostic.
    """
    r = _clean(returns)
    x = r ** 2
    x = x - x.mean()
    n = x.size
    if max_lag >= n:
        raise ValueError(f"max_lag={max_lag} >= n={n}")
    denom = float(np.dot(x, x))
    if denom == 0:
        raise ValueError("zero variance")
    acf = np.empty(max_lag + 1, dtype=np.float64)
    acf[0] = 1.0
    for lag in range(1, max_lag + 1):
        acf[lag] = float(np.dot(x[:-lag], x[lag:]) / denom)
    mean_acf_short = float(np.mean(acf[1:21]))
    return StylizedFactResult(
        name="acf_squared_returns",
        estimate=mean_acf_short,
        diagnostic={"lags": list(range(max_lag + 1)), "acf": acf.tolist()},
        meta={"n": n, "max_lag": max_lag, "summary": "mean ACF over lags 1..20"},
    )


# ─────────────────────────────────────────────────────────────────────────────
# 3. Leverage effect — cross-correlation Corr(r_t, r_{t+τ}^2)
# ─────────────────────────────────────────────────────────────────────────────


def leverage_effect(
    returns: ArrayF,
    max_lag: int = 30,
) -> StylizedFactResult:
    """Leverage effect: Corr(r_t, r_{t+τ}^2) for τ = 1..max_lag.

    Cont 2001 fact #6: negative and decaying with τ (negative returns today ↔ higher
    future volatility). We report the sum over lags 1..10 as a compact scalar and
    the full cross-corr in diagnostic.
    """
    r = _clean(returns)
    x = r - r.mean()
    sx = x.std(ddof=0)
    y = r ** 2
    y = y - y.mean()
    sy = y.std(ddof=0)
    if sx == 0 or sy == 0:
        raise ValueError("zero variance")
    n = x.size
    if max_lag >= n:
        raise ValueError(f"max_lag={max_lag} >= n={n}")
    corr = np.empty(max_lag + 1, dtype=np.float64)
    for lag in range(0, max_lag + 1):
        if lag == 0:
            corr[0] = float(np.mean(x * y) / (sx * sy))
        else:
            corr[lag] = float(np.mean(x[:-lag] * y[lag:]) / (sx * sy))
    scalar = float(np.sum(corr[1:11]))  # negative when leverage is present
    return StylizedFactResult(
        name="leverage_effect",
        estimate=scalar,
        diagnostic={"lags": list(range(max_lag + 1)), "corr_r_r2": corr.tolist()},
        meta={"n": n, "max_lag": max_lag, "summary": "sum of corr(r_t, r_{t+τ}^2) for τ=1..10"},
    )


# ─────────────────────────────────────────────────────────────────────────────
# 4. Long memory in |r| — DFA Hurst exponent
# ─────────────────────────────────────────────────────────────────────────────


def dfa_hurst(
    series: ArrayF,
    min_scale: int = 16,
    max_scale_frac: float = 0.1,
    n_scales: int = 20,
    order: int = 1,
) -> StylizedFactResult:
    """Detrended Fluctuation Analysis (DFA) Hurst exponent.

    Standard procedure:
      1. Compute cumulative deviation y(i) = Σ_{k=1..i} (x_k - mean)
      2. For each scale s, partition y into non-overlapping windows of length s
      3. In each window, fit polynomial of given `order`; compute residual RMS
      4. F(s) = RMS over windows
      5. H = slope of log F(s) vs log s

    For |r| of financial returns, Cont 2001 fact #5 predicts H ≈ 0.6–0.7
    (long memory, H > 0.5).
    """
    x = _clean(series)
    n = x.size
    max_scale = int(np.floor(max_scale_frac * n))
    if max_scale <= min_scale:
        raise ValueError(f"max_scale={max_scale} <= min_scale={min_scale} (n={n})")
    y = np.cumsum(x - x.mean())
    scales = np.unique(np.round(np.geomspace(min_scale, max_scale, num=n_scales)).astype(int))
    scales = scales[scales >= min_scale]
    fluct = np.empty(scales.size, dtype=np.float64)
    for i, s in enumerate(scales):
        n_windows = n // s
        if n_windows < 4:
            fluct[i] = np.nan
            continue
        trimmed = y[: n_windows * s].reshape(n_windows, s)
        t = np.arange(s)
        rms = np.empty(n_windows, dtype=np.float64)
        for w in range(n_windows):
            coefs = np.polyfit(t, trimmed[w], order)
            trend = np.polyval(coefs, t)
            rms[w] = float(np.sqrt(np.mean((trimmed[w] - trend) ** 2)))
        fluct[i] = float(np.sqrt(np.mean(rms ** 2)))
    mask = np.isfinite(fluct) & (fluct > 0)
    if mask.sum() < 4:
        raise ValueError("insufficient valid scales for DFA fit")
    log_s = np.log(scales[mask])
    log_f = np.log(fluct[mask])
    slope, intercept = np.polyfit(log_s, log_f, 1)
    return StylizedFactResult(
        name="dfa_hurst",
        estimate=float(slope),
        diagnostic={
            "scales": scales[mask].tolist(),
            "fluctuation": fluct[mask].tolist(),
            "log_s": log_s.tolist(),
            "log_f": log_f.tolist(),
        },
        meta={"n": n, "intercept": float(intercept), "order": order},
    )


# ─────────────────────────────────────────────────────────────────────────────
# Orchestration
# ─────────────────────────────────────────────────────────────────────────────


def compute_all_v0(returns: ArrayF) -> dict[str, StylizedFactResult]:
    """Run the first 4 stylized-facts metrics on log returns.

    For DFA Hurst we pass |r|; for others we pass r directly.
    """
    r = _clean(returns)
    abs_r = np.abs(r)
    return {
        "hill_tail_index": hill_tail_index(r, side="both"),
        "acf_squared_returns": acf_squared_returns(r),
        "leverage_effect": leverage_effect(r),
        "dfa_hurst_abs_r": dfa_hurst(abs_r),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _clean(arr: npt.ArrayLike) -> ArrayF:
    a = np.asarray(arr, dtype=np.float64)
    if a.ndim != 1:
        raise ValueError(f"expected 1-D array, got shape {a.shape}")
    a = a[np.isfinite(a)]
    if a.size == 0:
        raise ValueError("empty array after NaN removal")
    return a


def log_returns_from_prices(prices: npt.ArrayLike) -> ArrayF:
    p = np.asarray(prices, dtype=np.float64)
    return np.diff(np.log(p[np.isfinite(p) & (p > 0)]))
