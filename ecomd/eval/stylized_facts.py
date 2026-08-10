"""Stylized-facts evaluation suite — covers all 11 Cont (2001) facts.

Mapping to Cont 2001 (see `references/notes/cont_2001_stylized_facts.md`):
   #1 Absence of autocorrelation   → `autocorr_returns`
   #2 Heavy tails                  → `hill_tail_index`
   #3 Gain/loss asymmetry          → `gain_loss_asymmetry`
   #4 Aggregational Gaussianity    → `aggregational_gaussianity`
   #5 Intermittency                → `intermittency_fano`
   #6 Volatility clustering        → `acf_squared_returns`
   #7 Conditional heavy tails      → `conditional_kurtosis`  (GARCH(1,1) residuals)
   #8 Long memory in |r|           → `dfa_hurst`  (+ `dfa_hurst_multi_order` for order sweep)
   #9 Leverage effect              → `leverage_effect`
  #10 Volume/volatility correlation→ `volume_volatility_corr`  (needs volume input)
  #11 Zumbach / time-scale asym.   → `zumbach_asymmetry`

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

from collections.abc import Callable
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
    diagnostic: dict[str, list[float] | list[int]] = field(default_factory=dict)
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
# DFA multi-order (diagnostic for non-stationary Hurst inflation)
# ─────────────────────────────────────────────────────────────────────────────


def dfa_hurst_multi_order(
    series: ArrayF,
    orders: tuple[int, ...] = (1, 2, 3),
    min_scale: int = 16,
    max_scale_frac: float = 0.1,
) -> dict[int, StylizedFactResult]:
    """Run DFA at several polynomial detrending orders.

    For a truly long-memory stationary process, H is invariant under order
    choice. Large drops in H when going from order=1 to order=2/3 indicate
    that what order-1 DFA reported as "long memory" was actually uncorrected
    cross-window trend (non-stationarity) — this is the canonical diagnostic
    for the SPX/BTC H≈0.98 anomaly noted in logs/2026-04-23.md.
    """
    return {o: dfa_hurst(series, min_scale=min_scale, max_scale_frac=max_scale_frac, order=o) for o in orders}


# ─────────────────────────────────────────────────────────────────────────────
# 5. Absence of autocorrelation in returns (Cont fact #1)
# ─────────────────────────────────────────────────────────────────────────────


def autocorr_returns(
    returns: ArrayF,
    max_lag: int = 30,
    ljung_box_lag: int = 20,
) -> StylizedFactResult:
    """ACF of raw returns, plus Ljung-Box test for joint whiteness.

    Cont 2001 fact #1: linear autocorrelations of asset returns are often
    insignificant, except at very small intraday timescales (≤ ~20 min).
    We report (a) mean |ACF(r_t, r_{t-τ})| over τ=1..20 as a scalar estimate
    (small → returns are near-white), (b) the Ljung-Box Q-statistic at
    `ljung_box_lag` lags and its p-value in meta.
    """
    r = _clean(returns)
    x = r - r.mean()
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

    # Ljung-Box Q at `ljung_box_lag` lags: Q = n(n+2) Σ ρ_k² / (n-k)
    acf_short = acf[1:ljung_box_lag + 1]
    q_stat = float(n * (n + 2) * np.sum(acf_short ** 2 / (n - np.arange(1, ljung_box_lag + 1))))
    # p-value from chi-squared with df=ljung_box_lag
    from scipy.stats import chi2
    p_value = float(chi2.sf(q_stat, df=ljung_box_lag))

    mean_abs_acf = float(np.mean(np.abs(acf[1:21])))
    return StylizedFactResult(
        name="autocorr_returns",
        estimate=mean_abs_acf,
        diagnostic={"lags": list(range(max_lag + 1)), "acf": acf.tolist()},
        meta={
            "n": n,
            "max_lag": max_lag,
            "ljung_box_lag": ljung_box_lag,
            "ljung_box_q": q_stat,
            "ljung_box_p": p_value,
            "summary": "mean |ACF(r)| over lags 1..20 (small = white); LB-p > 0.05 = consistent with no autocorrelation",
        },
    )


# ─────────────────────────────────────────────────────────────────────────────
# 6. Gain/loss asymmetry (Cont fact #3)
# ─────────────────────────────────────────────────────────────────────────────


def gain_loss_asymmetry(
    returns: ArrayF,
    tail_quantiles: tuple[float, ...] = (0.01, 0.005, 0.001),
) -> StylizedFactResult:
    """Skewness + tail-quantile ratio.

    Cont 2001 fact #3: large drawdowns but not equally large upward moves.
    Expected at daily+ frequency and on indices: skewness < 0, and the
    left-tail |quantile| > right-tail quantile at small p.
    MITRE 2023 finds this does NOT hold cleanly for individual intraday stocks.
    """
    r = _clean(returns)
    from scipy.stats import skew
    sk = float(skew(r, bias=False))
    ratios = {}
    for q in tail_quantiles:
        left = float(-np.quantile(r, q))           # |negative tail at p=q|
        right = float(np.quantile(r, 1.0 - q))     # positive tail at p=1-q
        ratios[f"left/right_q{q}"] = left / right if right > 0 else float("inf")
    return StylizedFactResult(
        name="gain_loss_asymmetry",
        estimate=sk,
        diagnostic={"tail_ratios": list(ratios.values()), "tail_quantiles": list(tail_quantiles)},
        meta={
            "n": int(r.size),
            "skewness": sk,
            "left_right_ratios": ratios,
            "summary": "skewness < 0 and left/right_q0.01 > 1 → gain/loss asymmetric (losses dominate)",
        },
    )


# ─────────────────────────────────────────────────────────────────────────────
# 7. Aggregational Gaussianity (Cont fact #4)
# ─────────────────────────────────────────────────────────────────────────────


def aggregational_gaussianity(
    returns: ArrayF,
    scales: tuple[int, ...] = (1, 5, 10, 25, 50, 100),
) -> StylizedFactResult:
    """Excess kurtosis as a function of aggregation scale.

    Cont 2001 fact #4: as Δt grows, distribution of r(Δt) approaches Gaussian.
    Estimate: κ(scale=1) − κ(scale=max) (large positive = clear Gaussianisation).
    Diagnostic: excess kurtosis at each scale.
    """
    from scipy.stats import kurtosis
    r = _clean(returns)
    ks: list[float] = []
    scales_ok: list[int] = []
    ks_norm_stats: list[float] = []
    for s in scales:
        if s < 1:
            continue
        # Non-overlapping aggregation of s consecutive returns
        n_blocks = r.size // s
        if n_blocks < 30:
            ks.append(float("nan"))
            ks_norm_stats.append(float("nan"))
            scales_ok.append(s)
            continue
        agg = r[: n_blocks * s].reshape(n_blocks, s).sum(axis=1)
        ks.append(float(kurtosis(agg, fisher=True, bias=False)))  # excess kurtosis (0 = Gaussian)
        # KS distance to standard normal of z-scored returns
        z = (agg - agg.mean()) / (agg.std(ddof=1) if agg.std(ddof=1) > 0 else 1.0)
        from scipy.stats import kstest
        ks_norm_stats.append(float(kstest(z, "norm").statistic))
        scales_ok.append(s)

    finite = [k for k in ks if np.isfinite(k)]
    estimate = float(finite[0] - finite[-1]) if len(finite) >= 2 else float("nan")
    return StylizedFactResult(
        name="aggregational_gaussianity",
        estimate=estimate,
        diagnostic={"scales": scales_ok, "excess_kurtosis": ks, "ks_to_normal": ks_norm_stats},
        meta={
            "n": int(r.size),
            "summary": "estimate = κ(scale=1) − κ(scale=max); > 0 means kurtosis decays toward Gaussian",
        },
    )


# ─────────────────────────────────────────────────────────────────────────────
# 8. Intermittency / Fano factor for extreme events (Cont fact #5)
# ─────────────────────────────────────────────────────────────────────────────


def intermittency_fano(
    returns: ArrayF,
    quantile: float = 0.99,
    n_windows: int = 100,
) -> StylizedFactResult:
    """Fano factor F = var(N) / mean(N) for extreme-event counts per window.

    Cont 2001 fact #5: irregular bursts of volatility; extreme events cluster.
    Define extremes as |r| > quantile(|r|, 0.99). Poisson-like (no clustering)
    gives F ≈ 1; clustered bursts give F >> 1.
    MITRE 2023 reports F ∈ [2.6, 4.7] for 1-min Dow stocks and 27-60 at tick.
    """
    r = _clean(returns)
    if not 0.5 < quantile < 1.0:
        raise ValueError("quantile must be in (0.5, 1.0)")
    if n_windows < 10:
        raise ValueError("need n_windows ≥ 10 for a meaningful Fano estimate")
    abs_r = np.abs(r)
    thr = float(np.quantile(abs_r, quantile))
    indicator = (abs_r > thr).astype(np.int64)
    n = indicator.size
    if n < n_windows:
        raise ValueError(f"n={n} < n_windows={n_windows}")
    # Non-overlapping windows
    w = n // n_windows
    counts = indicator[: w * n_windows].reshape(n_windows, w).sum(axis=1)
    mu = float(counts.mean())
    var = float(counts.var(ddof=1))
    fano = var / mu if mu > 0 else float("inf")
    return StylizedFactResult(
        name="intermittency_fano",
        estimate=fano,
        diagnostic={"counts": counts.tolist()},
        meta={
            "n": n,
            "quantile": quantile,
            "threshold_abs_r": thr,
            "n_windows": n_windows,
            "window_size": int(w),
            "mean_count_per_window": mu,
            "summary": "F = var(N)/mean(N); F>1 clustering, F=1 Poisson",
        },
    )


# ─────────────────────────────────────────────────────────────────────────────
# 9. Conditional heavy tails — kurtosis of GARCH residuals (Cont fact #7)
# ─────────────────────────────────────────────────────────────────────────────


def conditional_kurtosis(
    returns: ArrayF,
    rescale_to_percent: bool = True,
) -> StylizedFactResult:
    """Excess kurtosis of GARCH(1,1)-standardised residuals.

    Cont 2001 fact #7: even after removing volatility clustering (GARCH),
    residuals are still heavy-tailed but less so than the unconditional
    distribution.

    Implementation: `arch.arch_model(r, vol='GARCH', p=1, q=1, mean='Zero')`.
    `rescale_to_percent=True` multiplies r by 100 to improve numerical
    conditioning (arch package often complains otherwise on daily log returns).
    """
    from arch import arch_model
    from scipy.stats import kurtosis
    r = _clean(returns)
    scale = 100.0 if rescale_to_percent else 1.0
    model = arch_model(r * scale, vol="GARCH", p=1, q=1, mean="Zero", rescale=False)
    try:
        res = model.fit(disp="off", show_warning=False)
    except Exception as exc:  # noqa: BLE001 — GARCH optimizer can fail on pathological data
        raise RuntimeError(f"GARCH(1,1) fit failed: {exc}") from exc
    cond_vol = res.conditional_volatility  # array length = len(r)
    # Standardised residuals (note: arch returns residuals already de-meaned under mean='Zero')
    resid = r * scale
    std_resid = np.asarray(resid) / np.asarray(cond_vol)
    unconditional_k = float(kurtosis(r, fisher=True, bias=False))
    conditional_k = float(kurtosis(std_resid, fisher=True, bias=False))
    return StylizedFactResult(
        name="conditional_kurtosis",
        estimate=conditional_k,
        diagnostic={"conditional_vol_path_summary": [float(cond_vol.min()), float(cond_vol.mean()), float(cond_vol.max())]},
        meta={
            "n": int(r.size),
            "unconditional_excess_kurtosis": unconditional_k,
            "conditional_excess_kurtosis": conditional_k,
            "kurtosis_reduction_ratio": conditional_k / unconditional_k if unconditional_k != 0 else float("nan"),
            "garch_params": {k: float(v) for k, v in res.params.items()},
            "summary": "both should be > 0; conditional < unconditional (tails reduced but still heavy)",
        },
    )


# ─────────────────────────────────────────────────────────────────────────────
# 10. Volume / volatility correlation (Cont fact #10)
# ─────────────────────────────────────────────────────────────────────────────


def volume_volatility_corr(
    returns: ArrayF,
    volume: ArrayF,
    max_lag: int = 5,
) -> StylizedFactResult:
    """Contemporaneous and lagged correlation between trading volume and |r|.

    Cont 2001 fact #10: trading volume is positively correlated with every
    volatility proxy. Expected contemporaneous corr(V, |r|) ∈ [0.2, 0.6].
    MITRE 2023: strong in clock time; weak/variable in event (trade-clock) time.
    """
    r = _clean(returns)
    v = _clean(volume)
    if v.size != r.size:
        raise ValueError(f"returns and volume must have same length, got {r.size} and {v.size}")
    abs_r = np.abs(r)
    # Contemporaneous
    contemp = float(np.corrcoef(v, abs_r)[0, 1])
    # Cross-correlation at lags: V[t] vs |r|[t+lag], lag ∈ [-max_lag, max_lag]
    cross: list[float] = []
    for lag in range(-max_lag, max_lag + 1):
        if lag < 0:
            x, y = v[-lag:], abs_r[: v.size + lag]
        elif lag > 0:
            x, y = v[: v.size - lag], abs_r[lag:]
        else:
            x, y = v, abs_r
        if x.size > 2:
            cross.append(float(np.corrcoef(x, y)[0, 1]))
        else:
            cross.append(float("nan"))
    return StylizedFactResult(
        name="volume_volatility_corr",
        estimate=contemp,
        diagnostic={"lags": list(range(-max_lag, max_lag + 1)), "cross_corr_v_abs_r": cross},
        meta={
            "n": int(r.size),
            "contemporaneous_corr_v_absr": contemp,
            "summary": "positive (≥0.2) = volume–volatility link confirmed",
        },
    )


# ─────────────────────────────────────────────────────────────────────────────
# 11. Zumbach / asymmetry in timescales (Cont fact #11)
# ─────────────────────────────────────────────────────────────────────────────


def zumbach_asymmetry(
    returns: ArrayF,
    coarse_window: int = 30,
    max_lag: int = 20,
) -> StylizedFactResult:
    """Asymmetry in the volatility correlation across timescales.

    Let σ_coarse(t) = mean r² over a *past* window of size `coarse_window`,
    separated from time t by a gap of (max_lag + 1) so that σ_coarse(t) and
    σ_fine(t + τ) = r(t+τ)² never share any data point for |τ| ≤ max_lag.
    Without this gap, IID returns would show a spurious negative D(τ) from
    shared-sample correlation at small negative τ.

    A(τ) = corr(σ_coarse(t), σ_fine(t + τ))
    D(τ) = A(τ) − A(−τ)

    Cont 2001 fact #11 (Zumbach effect): coarse-scale volatility predicts
    fine-scale volatility better than the reverse, so D(τ) > 0 for positive τ.
    MITRE 2023 finds this effect weak/inconsistent for individual intraday
    stocks; stronger for indices and aggregated data.
    """
    r = _clean(returns)
    n = r.size
    if coarse_window < 2:
        raise ValueError("coarse_window must be ≥ 2")
    fine = r ** 2
    gap = max_lag + 1  # ensures coarse window end and fine point are always ≥ gap apart
    cw = coarse_window
    # For each reference time t, coarse window spans [t - gap - cw + 1, t - gap]
    # Valid t range: need t - gap - cw + 1 ≥ 0 AND t + max_lag ≤ n - 1
    t_lo = gap + cw - 1
    t_hi = n - 1 - max_lag
    m = t_hi - t_lo + 1
    if m < 100:
        raise ValueError(
            f"series too short for zumbach_asymmetry: n={n}, cw={cw}, max_lag={max_lag} → only {m} reference times"
        )

    csum = np.concatenate(([0.0], np.cumsum(fine)))
    # coarse_arr[i] = coarse at reference time t = t_lo + i
    # = mean(fine[t - gap - cw + 1 .. t - gap]) = (csum[t-gap+1] - csum[t-gap-cw+1]) / cw
    ts = np.arange(t_lo, t_hi + 1)
    coarse_arr = (csum[ts - gap + 1] - csum[ts - gap - cw + 1]) / cw

    lags = list(range(-max_lag, max_lag + 1))
    A: list[float] = []
    for tau in lags:
        fine_arr = fine[ts + tau]
        if coarse_arr.std() > 0 and fine_arr.std() > 0:
            A.append(float(np.corrcoef(coarse_arr, fine_arr)[0, 1]))
        else:
            A.append(float("nan"))
    A_arr = np.asarray(A)
    D_pos: list[float] = []
    for k in range(1, max_lag + 1):
        a_pos = A_arr[max_lag + k]   # A(+k)
        a_neg = A_arr[max_lag - k]   # A(-k)
        D_pos.append(float(a_pos - a_neg))
    mean_d = float(np.nanmean(D_pos[:10]))
    return StylizedFactResult(
        name="zumbach_asymmetry",
        estimate=mean_d,
        diagnostic={"lags": lags, "A_of_tau": A, "D_of_tau_positive": D_pos},
        meta={
            "n": n,
            "coarse_window": coarse_window,
            "max_lag": max_lag,
            "gap": gap,
            "n_reference_times": int(m),
            "summary": "mean D(τ) over τ=1..10 with gap removing overlap bias; D>0 ⇒ Zumbach",
        },
    )


# ─────────────────────────────────────────────────────────────────────────────
# Orchestration
# ─────────────────────────────────────────────────────────────────────────────


def compute_all_v0(returns: ArrayF) -> dict[str, StylizedFactResult]:
    """Run the first 4 stylized-facts metrics on log returns (legacy v0).

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


def compute_all(
    returns: ArrayF,
    volume: ArrayF | None = None,
    skip: tuple[str, ...] = (),
) -> dict[str, StylizedFactResult]:
    """Run all 11 Cont-2001 stylized-facts metrics.

    Parameters
    ----------
    returns : ArrayF
        1-D log returns.
    volume : ArrayF or None
        If provided, must align with `returns`; enables #10 volume/volatility.
        If None, #10 is silently skipped.
    skip : tuple of str
        Names of metrics to skip (e.g. ``("conditional_kurtosis",)`` if
        GARCH fit is too slow on a large series).
    """
    r = _clean(returns)
    abs_r = np.abs(r)
    out: dict[str, StylizedFactResult] = {}

    def _run(name: str, fn: Callable[[], StylizedFactResult]) -> None:
        if name in skip:
            return
        try:
            out[name] = fn()
        except Exception as exc:  # noqa: BLE001 — one metric failure shouldn't kill the batch
            out[name] = StylizedFactResult(
                name=name,
                estimate=float("nan"),
                meta={"error": f"{type(exc).__name__}: {exc}"},
            )

    _run("autocorr_returns",            lambda: autocorr_returns(r))                    # #1
    _run("hill_tail_index",             lambda: hill_tail_index(r, side="both"))        # #2
    _run("gain_loss_asymmetry",         lambda: gain_loss_asymmetry(r))                 # #3
    _run("aggregational_gaussianity",   lambda: aggregational_gaussianity(r))           # #4
    _run("intermittency_fano",          lambda: intermittency_fano(r))                  # #5
    _run("acf_squared_returns",         lambda: acf_squared_returns(r))                 # #6
    _run("conditional_kurtosis",        lambda: conditional_kurtosis(r))                # #7
    _run("dfa_hurst_abs_r",             lambda: dfa_hurst(abs_r))                       # #8
    _run("leverage_effect",             lambda: leverage_effect(r))                     # #9
    if volume is not None:
        _run("volume_volatility_corr",  lambda: volume_volatility_corr(r, volume))      # #10
    _run("zumbach_asymmetry",           lambda: zumbach_asymmetry(r))                   # #11
    return out


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
