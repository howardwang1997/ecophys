"""VaR/ES estimation + Kupiec/Christoffersen backtests.

Designed for Paper A's secondary downstream task. The sampler abstraction
keeps the harness model-agnostic — any callable
``sampler(past_returns: np.ndarray, horizon: int, n_paths: int, seed: int)
→ np.ndarray of shape (n_paths, horizon)`` can be plugged in.

Conventions
-----------
- Returns are LOG returns (small numbers, ≈ ±0.05 daily).
- VaR and ES are reported as POSITIVE loss quantities (a 1d VaR_95 of
  0.025 means "95% of days the loss is no worse than 2.5%").
- A "violation" at time t is: actual cumulative loss over horizon H
  starting at t exceeded the predicted VaR (i.e. realised return < -VaR).
- Test p-values: under H₀ "model is correctly calibrated" we expect
  p > 0.05. Reject (model is broken) when p < 0.05.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np
from scipy.stats import chi2

# Sampler signature: (past_returns, horizon, n_paths, seed) -> (n_paths, horizon)
Sampler = Callable[[np.ndarray, int, int, int], np.ndarray]


# ──────────────────────────────────────────────────────────────────────────
# Core VaR / ES from sampled paths
# ──────────────────────────────────────────────────────────────────────────


def var_es_from_paths(paths: np.ndarray, alpha: float = 0.95) -> tuple[float, float]:
    """Compute VaR_α and ES_α (positive loss quantities) from sampled paths.

    Args:
        paths: shape (n_paths, horizon) — simulated log returns
        alpha: confidence level (e.g. 0.95 for VaR_95)

    Returns:
        (var, es) — both positive when there's downside risk; can be negative
        if the distribution has positive cumulative drift (rare for daily returns).
    """
    if paths.ndim != 2:
        raise ValueError(f"paths must be 2-D (n_paths, horizon), got shape {paths.shape}")
    cum = paths.sum(axis=1)  # cumulative log return per path
    var = -float(np.quantile(cum, 1.0 - alpha))
    tail = cum[cum < -var] if (cum < -var).any() else cum[cum <= -var]
    es = -float(tail.mean()) if tail.size > 0 else var
    return var, es


# ──────────────────────────────────────────────────────────────────────────
# Backtest statistical tests
# ──────────────────────────────────────────────────────────────────────────


def kupiec_pof_test(violations: np.ndarray, alpha: float) -> tuple[float, float]:
    """Kupiec (1995) Proportion-Of-Failures unconditional coverage LR test.

    H₀: violation rate = 1 - alpha (i.e. model correctly calibrated).
    Returns (LR statistic, p-value). χ² df=1.
    """
    v = np.asarray(violations, dtype=int).ravel()
    n = v.size
    x = int(v.sum())
    if n == 0:
        return float("nan"), float("nan")
    p_expected = 1.0 - alpha
    p_observed = x / n if n > 0 else 0.0
    if x == 0:
        # log(0) trap; degenerate case — treat as zero LR if expected violations near 0,
        # otherwise highly significant rejection.
        if p_expected == 0:
            return 0.0, 1.0
        lr = -2.0 * n * np.log(1.0 - p_expected)
    elif x == n:
        if p_expected == 1.0:
            return 0.0, 1.0
        lr = -2.0 * n * np.log(p_expected)
    else:
        ll_obs = x * np.log(p_observed) + (n - x) * np.log(1.0 - p_observed)
        ll_exp = x * np.log(p_expected) + (n - x) * np.log(1.0 - p_expected)
        lr = -2.0 * (ll_exp - ll_obs)
    p_value = float(1.0 - chi2.cdf(lr, df=1))
    return float(lr), p_value


def christoffersen_ind_test(violations: np.ndarray) -> tuple[float, float]:
    """Christoffersen (1998) independence LR test.

    H₀: violations form an iid Bernoulli sequence (no clustering).
    Tests whether P(violation_t | violation_{t-1}=1) ≠ P(violation_t | violation_{t-1}=0).
    Returns (LR statistic, p-value). χ² df=1.
    """
    v = np.asarray(violations, dtype=int).ravel()
    if v.size < 2:
        return float("nan"), float("nan")

    # Transition counts
    n00 = n01 = n10 = n11 = 0
    for i in range(1, v.size):
        prev, curr = v[i - 1], v[i]
        if prev == 0 and curr == 0:
            n00 += 1
        elif prev == 0 and curr == 1:
            n01 += 1
        elif prev == 1 and curr == 0:
            n10 += 1
        else:
            n11 += 1

    # Estimated transition probabilities
    p01 = n01 / (n00 + n01) if (n00 + n01) > 0 else 0.0
    p11 = n11 / (n10 + n11) if (n10 + n11) > 0 else 0.0
    p_uncond = (n01 + n11) / (n00 + n01 + n10 + n11) if (n00 + n01 + n10 + n11) > 0 else 0.0

    # Log-likelihoods
    def _safe_log(p: float, count: int) -> float:
        if count == 0:
            return 0.0
        if p <= 0.0:
            return -1e9 if count > 0 else 0.0
        return count * np.log(p)

    # Restricted (independence): both transitions use p_uncond
    ll_restricted = (
        _safe_log(1.0 - p_uncond, n00 + n10)
        + _safe_log(p_uncond, n01 + n11)
    )
    # Unrestricted (Markov chain): different probs from state 0 vs state 1
    ll_unrestricted = (
        _safe_log(1.0 - p01, n00) + _safe_log(p01, n01)
        + _safe_log(1.0 - p11, n10) + _safe_log(p11, n11)
    )

    if not (np.isfinite(ll_restricted) and np.isfinite(ll_unrestricted)):
        return float("nan"), float("nan")
    lr = -2.0 * (ll_restricted - ll_unrestricted)
    # Numerical guard: tiny negative LR from float roundoff
    lr = max(lr, 0.0)
    p_value = float(1.0 - chi2.cdf(lr, df=1))
    return float(lr), p_value


def christoffersen_cc_test(violations: np.ndarray, alpha: float) -> tuple[float, float]:
    """Christoffersen Conditional Coverage = Kupiec POF + Independence.

    Combined LR test of unconditional coverage AND independence.
    Returns (LR statistic, p-value). χ² df=2.
    """
    lr_pof, _ = kupiec_pof_test(violations, alpha)
    lr_ind, _ = christoffersen_ind_test(violations)
    if not (np.isfinite(lr_pof) and np.isfinite(lr_ind)):
        return float("nan"), float("nan")
    lr_cc = lr_pof + lr_ind
    p_value = float(1.0 - chi2.cdf(lr_cc, df=2))
    return float(lr_cc), p_value


# ──────────────────────────────────────────────────────────────────────────
# Rolling backtest
# ──────────────────────────────────────────────────────────────────────────


@dataclass
class BacktestResult:
    """Results of a rolling VaR backtest."""

    sampler_name: str
    alpha: float
    horizon: int
    n_paths: int
    train_window: int
    n_predictions: int
    n_violations: int
    expected_violations: float
    var_series: np.ndarray = field(repr=False)
    es_series: np.ndarray = field(repr=False)
    actual_returns: np.ndarray = field(repr=False)
    violations: np.ndarray = field(repr=False)
    kupiec_lr: float = float("nan")
    kupiec_p: float = float("nan")
    christoffersen_ind_lr: float = float("nan")
    christoffersen_ind_p: float = float("nan")
    christoffersen_cc_lr: float = float("nan")
    christoffersen_cc_p: float = float("nan")

    @property
    def violation_rate(self) -> float:
        return self.n_violations / max(self.n_predictions, 1)

    @property
    def passes_kupiec(self) -> bool:
        return bool(np.isfinite(self.kupiec_p) and self.kupiec_p > 0.05)

    @property
    def passes_independence(self) -> bool:
        return bool(np.isfinite(self.christoffersen_ind_p) and self.christoffersen_ind_p > 0.05)

    @property
    def passes_cc(self) -> bool:
        return bool(np.isfinite(self.christoffersen_cc_p) and self.christoffersen_cc_p > 0.05)


def rolling_backtest(
    sampler: Sampler,
    real_returns: np.ndarray,
    horizon: int = 1,
    alpha: float = 0.95,
    n_paths: int = 1000,
    train_window: int = 500,
    sampler_name: str = "sampler",
    seed: int = 0,
    stride: int = 1,
) -> BacktestResult:
    """Walk-forward backtest of a VaR sampler against realised returns.

    At each time t in [train_window, n - horizon] (in steps of `stride`):
      1. Pass real_returns[:t] as past + sample n_paths × horizon ahead
      2. Compute VaR_α and ES_α from sampled cumulative returns
      3. Compare to actual cumulative return real_returns[t : t+horizon].sum()
      4. Record violation if actual < -VaR

    Returns a BacktestResult with all per-step VaRs/ESs and the three tests.
    """
    r = np.asarray(real_returns, dtype=np.float64).ravel()
    n = r.size
    if n < train_window + horizon:
        raise ValueError(
            f"need n ≥ train_window + horizon = {train_window + horizon}, got {n}"
        )
    if not 0 < alpha < 1:
        raise ValueError(f"alpha must be in (0, 1), got {alpha}")

    var_list: list[float] = []
    es_list: list[float] = []
    actual_list: list[float] = []
    viol_list: list[int] = []

    for t in range(train_window, n - horizon + 1, stride):
        past = r[:t]
        paths = sampler(past, horizon, n_paths, seed + t)
        var, es = var_es_from_paths(paths, alpha)
        actual = float(r[t : t + horizon].sum())
        var_list.append(var)
        es_list.append(es)
        actual_list.append(actual)
        viol_list.append(int(actual < -var))

    var_arr = np.asarray(var_list)
    es_arr = np.asarray(es_list)
    actual_arr = np.asarray(actual_list)
    viol_arr = np.asarray(viol_list, dtype=int)

    n_pred = viol_arr.size
    n_viol = int(viol_arr.sum())
    expected = (1.0 - alpha) * n_pred

    kup_lr, kup_p = kupiec_pof_test(viol_arr, alpha)
    ind_lr, ind_p = christoffersen_ind_test(viol_arr)
    cc_lr, cc_p = christoffersen_cc_test(viol_arr, alpha)

    return BacktestResult(
        sampler_name=sampler_name,
        alpha=alpha,
        horizon=horizon,
        n_paths=n_paths,
        train_window=train_window,
        n_predictions=n_pred,
        n_violations=n_viol,
        expected_violations=expected,
        var_series=var_arr,
        es_series=es_arr,
        actual_returns=actual_arr,
        violations=viol_arr,
        kupiec_lr=kup_lr,
        kupiec_p=kup_p,
        christoffersen_ind_lr=ind_lr,
        christoffersen_ind_p=ind_p,
        christoffersen_cc_lr=cc_lr,
        christoffersen_cc_p=cc_p,
    )


# ──────────────────────────────────────────────────────────────────────────
# Reporting
# ──────────────────────────────────────────────────────────────────────────


def print_report(result: BacktestResult) -> str:
    """Pretty-print a single backtest result. Returns the string for capture."""
    r = result
    rate = 100.0 * r.violation_rate
    expected_rate = 100.0 * (1.0 - r.alpha)
    lines = [
        f"VaR backtest — {r.sampler_name}",
        f"  alpha={r.alpha:.2f}  horizon={r.horizon}d  n_paths={r.n_paths}  train_window={r.train_window}",
        f"  n_predictions={r.n_predictions}  n_violations={r.n_violations} (expected ≈ {r.expected_violations:.1f})",
        f"  observed rate={rate:.2f}% vs expected {expected_rate:.2f}%",
        f"  mean VaR={r.var_series.mean():.4f}  mean ES={r.es_series.mean():.4f}",
        f"  Kupiec POF      LR={r.kupiec_lr:6.3f}  p={r.kupiec_p:.4f}  → {'PASS' if r.passes_kupiec else 'REJECT'}",
        f"  Christoffersen IND  LR={r.christoffersen_ind_lr:6.3f}  p={r.christoffersen_ind_p:.4f}  → {'PASS' if r.passes_independence else 'REJECT'}",
        f"  Christoffersen CC   LR={r.christoffersen_cc_lr:6.3f}  p={r.christoffersen_cc_p:.4f}  → {'PASS' if r.passes_cc else 'REJECT'}",
    ]
    out = "\n".join(lines)
    print(out)
    return out


# ──────────────────────────────────────────────────────────────────────────
# CLI smoke test
# ──────────────────────────────────────────────────────────────────────────


def _smoke() -> None:
    """Quick sanity check: backtest historical-bootstrap on iid synthetic data.

    With truly stationary returns, Historical Simulation must pass Kupiec
    (rate matches expected) and Independence (no clustering). If either
    fails, something in the test math is off.
    """
    import sys

    from ecomd.risk.samplers import HistoricalSampler

    rng = np.random.default_rng(0)
    n = 2500
    # Stationary iid returns — gold standard test for the harness math.
    r = rng.normal(scale=0.01, size=n)
    sampler = HistoricalSampler(window=250)
    res = rolling_backtest(
        sampler=sampler.sample, real_returns=r,
        horizon=1, alpha=0.95, n_paths=500, train_window=500,
        sampler_name="HistoricalSampler(window=250)",
        stride=2,
    )
    print_report(res)
    sys.exit(0 if (res.passes_kupiec and res.passes_independence) else 1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="VaR backtest module")
    parser.add_argument("--smoke", action="store_true", help="Run smoke test on synthetic data")
    args = parser.parse_args()
    if args.smoke:
        _smoke()
    else:
        print("Usage: python -m ecomd.risk.var_backtest --smoke")
