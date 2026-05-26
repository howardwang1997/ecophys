"""Surrogate-kill tests for the Thread-1 multi-fact loss surrogates.

Each surrogate in :mod:`ecomd.training.fact_surrogates` must satisfy two gates,
per the 102-105 plan:

1. **Differentiable** — a gradient flows to a ``requires_grad`` input and is finite.
2. **Faithful** — rank-correlates (Spearman ρ > 0.6) with the corresponding numpy
   eval metric in :mod:`ecomd.eval.stylized_facts` across a battery of synthetic
   return series spanning the relevant property (skew, kurtosis-decay, clustering,
   long-memory). A surrogate that cannot clear ρ>0.6 is not a valid training signal
   and is dropped.
"""

from __future__ import annotations

import numpy as np
import torch
from scipy.stats import spearmanr

from ecomd.eval import stylized_facts as sf
from ecomd.training import fact_surrogates as fs

_RHO_MIN = 0.6


def _series_bank(n: int = 6000, seed: int = 0) -> list[np.ndarray]:
    """A battery of synthetic return series with varied stylized properties."""
    rng = np.random.default_rng(seed)
    bank: list[np.ndarray] = []
    # Gaussian white noise (control)
    bank.append(rng.normal(0, 0.01, n))
    # Negatively skewed (gain/loss asymmetry), several strengths
    for a in (0.5, 1.5, 3.0):
        g = rng.gamma(shape=2.0, scale=0.01, size=n)
        bank.append(-(g - g.mean()) * a + rng.normal(0, 0.002, n))
    # Heavy-tailed Student-t, varied df → varied kurtosis
    for df in (3.0, 5.0, 12.0):
        bank.append(rng.standard_t(df, n) * 0.01)
    # Volatility-clustered (stationary GARCH(1,1): β + α < 1), variance capped
    # so float64 cannot overflow to inf on a fat-tailed ε draw.
    for beta in (0.80, 0.88, 0.93):
        alpha = 0.05  # β + α ≤ 0.98 < 1 → stationary
        var = np.empty(n)
        var[0] = 1e-4
        eps = rng.normal(0, 1, n)
        ret = np.empty(n)
        ret[0] = eps[0] * np.sqrt(var[0])
        var_cap = 1.0  # hard ceiling: |ret| stays O(few) — no overflow
        for t in range(1, n):
            var[t] = min(1e-6 + alpha * (ret[t - 1] ** 2) + beta * var[t - 1], var_cap)
            ret[t] = eps[t] * np.sqrt(var[t])
        bank.append(ret)
    # Long-memory-ish via fractional-noise approx (cumsum of AR(1))
    for rho in (0.0, 0.3, 0.6):
        e = rng.normal(0, 0.01, n)
        x = np.empty(n)
        x[0] = e[0]
        for t in range(1, n):
            x[t] = rho * x[t - 1] + e[t]
        bank.append(x)
    return bank


def _assert_differentiable(fn, series: np.ndarray) -> None:
    r = torch.tensor(series, dtype=torch.float32, requires_grad=True)
    val = fn(r)
    assert val.requires_grad, f"{fn.__name__}: output not differentiable"
    assert torch.isfinite(val), f"{fn.__name__}: non-finite value {val}"
    val.backward()
    assert r.grad is not None and torch.isfinite(r.grad).all(), f"{fn.__name__}: bad grad"


def _spearman(surrogate, eval_estimate, key: str | None = None) -> float:
    bank = _series_bank()
    s_vals, e_vals = [], []
    for series in bank:
        with torch.no_grad():
            sv = float(surrogate(torch.tensor(series, dtype=torch.float32)).item())
        ev = eval_estimate(series)
        if not (np.isfinite(sv) and np.isfinite(ev)):
            continue
        s_vals.append(sv)
        e_vals.append(ev)
    rho, _ = spearmanr(s_vals, e_vals)
    return float(rho)


# ── #3 gain/loss asymmetry (skewness) ────────────────────────────────────────


def test_gain_loss_skew_differentiable():
    for series in _series_bank():
        _assert_differentiable(fs.gain_loss_skew, series)


def test_gain_loss_skew_faithful():
    rho = _spearman(fs.gain_loss_skew, lambda r: sf.gain_loss_asymmetry(r).estimate)
    assert rho > _RHO_MIN, f"gain_loss_skew ρ={rho:.2f} ≤ {_RHO_MIN}"


# ── #4 aggregational gaussianity ──────────────────────────────────────────────


def test_agg_gaussianity_differentiable():
    for series in _series_bank():
        _assert_differentiable(fs.agg_gaussianity, series)


def test_agg_gaussianity_faithful():
    rho = _spearman(fs.agg_gaussianity, lambda r: sf.aggregational_gaussianity(r).estimate)
    assert rho > _RHO_MIN, f"agg_gaussianity ρ={rho:.2f} ≤ {_RHO_MIN}"


# ── #5 intermittency / Fano ───────────────────────────────────────────────────


def test_soft_fano_differentiable():
    for series in _series_bank():
        _assert_differentiable(fs.soft_fano, series)


def test_soft_fano_faithful():
    rho = _spearman(
        lambda r: fs.soft_fano(r, n_windows=50),
        lambda r: sf.intermittency_fano(r, n_windows=50).estimate,
    )
    assert rho > _RHO_MIN, f"soft_fano ρ={rho:.2f} ≤ {_RHO_MIN}"


# ── #8 DFA-Hurst (on |r|) ─────────────────────────────────────────────────────


def test_dfa_hurst_differentiable():
    for series in _series_bank():
        _assert_differentiable(lambda r: fs.dfa_hurst_surrogate(r.abs()), series)


def test_dfa_hurst_faithful():
    rho = _spearman(
        lambda r: fs.dfa_hurst_surrogate(r.abs()),
        lambda r: sf.dfa_hurst(np.abs(r)).estimate,
    )
    assert rho > _RHO_MIN, f"dfa_hurst ρ={rho:.2f} ≤ {_RHO_MIN}"
