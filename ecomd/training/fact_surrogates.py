"""Differentiable surrogates for stylized facts not covered by the 3-moment loss.

The 2026-05-26 weekend batch confirmed a ~5.1/11 ceiling. Root cause: the training
objective (:func:`ecomd.training.losses.moment_matching_loss`) optimises only
``acf_sq_mean`` / ``leverage_sum`` / ``hill_alpha`` (≈ facts #6/#9/#2); the other 8
facts never enter the gradient. Matching the *whole return marginal* (Wasserstein,
exp 085) was tried and scored worse than baseline. This module instead provides
**explicit per-fact** differentiable surrogates so the under-covered facts can be put
directly into the loss (Thread 1 of the 102-105 plan).

Each surrogate mirrors the point-estimate semantics of the corresponding numpy
estimator in :mod:`ecomd.eval.stylized_facts` and ships with a surrogate-kill test
(``tests/test_fact_surrogates.py``) asserting it is differentiable AND rank-correlates
(ρ>0.6) with the eval metric. If a surrogate cannot clear that bar it is dropped.

Self-contained on purpose: imports nothing from :mod:`ecomd.training.losses` so that
``losses`` can import *this* without a cycle.
"""

from __future__ import annotations

import torch
from torch import Tensor

_EPS = 1e-12


# ─────────────────────────────────────────────────────────────────────────────
# small primitives (kept local to avoid a losses.py ↔ fact_surrogates.py cycle)
# ─────────────────────────────────────────────────────────────────────────────


def _aggregate(returns: Tensor, scale: int) -> Tensor:
    """Sum consecutive ``scale`` returns (non-overlapping). scale<=1 is identity."""
    if scale <= 1:
        return returns
    n = (returns.shape[0] // scale) * scale
    if n == 0:
        return returns[:1] * 0.0
    return returns[:n].view(-1, scale).sum(dim=1)


def _excess_kurtosis(x: Tensor) -> Tensor:
    """Excess kurtosis E[(x-μ)⁴]/E[(x-μ)²]² − 3 (Fisher). Differentiable."""
    xc = x - x.mean()
    var = (xc ** 2).mean() + _EPS
    return (xc ** 4).mean() / (var ** 2) - 3.0


# ─────────────────────────────────────────────────────────────────────────────
# #3 gain/loss asymmetry — differentiable skewness
# ─────────────────────────────────────────────────────────────────────────────


def gain_loss_skew(returns: Tensor) -> Tensor:
    """Skewness E[(r-μ)³]/σ³ (Cont fact #3).

    Mirrors the ``estimate`` of :func:`ecomd.eval.stylized_facts.gain_loss_asymmetry`
    (scipy ``skew`` with bias correction → ~identical for large n). Real equity
    indices: skewness < 0 (losses dominate).
    """
    r = returns - returns.mean()
    std = ((r ** 2).mean() + _EPS).sqrt()
    return (r ** 3).mean() / (std ** 3 + _EPS)


# ─────────────────────────────────────────────────────────────────────────────
# #4 aggregational gaussianity — κ(scale=1) − κ(scale=large)
# ─────────────────────────────────────────────────────────────────────────────


def agg_gaussianity(returns: Tensor, scale_large: int = 50) -> Tensor:
    """κ(scale=1) − κ(scale=large), κ = excess kurtosis (Cont fact #4).

    Mirrors :func:`ecomd.eval.stylized_facts.aggregational_gaussianity`'s estimate
    (κ at smallest scale minus κ at largest). Positive ⇒ tails Gaussianise under
    aggregation. ``scale_large`` default 50 needs ≳1500 returns for a stable κ.
    """
    k1 = _excess_kurtosis(returns)
    agg = _aggregate(returns, scale_large)
    if agg.shape[0] < 8:
        return k1 - k1.detach() * 0.0  # not enough blocks → no signal
    kL = _excess_kurtosis(agg)
    return k1 - kL


# ─────────────────────────────────────────────────────────────────────────────
# #5 intermittency / Fano factor — soft-thresholded extreme-event counts
# ─────────────────────────────────────────────────────────────────────────────


def soft_fano(
    returns: Tensor,
    quantile: float = 0.99,
    n_windows: int = 50,
    temp: float | None = None,
) -> Tensor:
    """Soft Fano factor F = var(N)/mean(N) of extreme-event counts (Cont fact #5).

    Mirrors :func:`ecomd.eval.stylized_facts.intermittency_fano` but replaces the
    hard indicator ``|r|>thr`` with ``sigmoid((|r|-thr)/temp)`` so counts are
    differentiable. The threshold itself is a detached empirical quantile (no
    gradient through the threshold; gradient flows through the soft counts). F≈1
    Poisson, F≫1 clustered bursts.
    """
    abs_r = returns.abs()
    thr = torch.quantile(abs_r, quantile).detach()
    if temp is None:
        temp = float((abs_r.std().detach() + _EPS) * 0.1)
    soft_ind = torch.sigmoid((abs_r - thr) / max(temp, _EPS))
    n = soft_ind.shape[0]
    if n < n_windows:
        return torch.ones((), dtype=returns.dtype, device=returns.device)
    w = n // n_windows
    counts = soft_ind[: w * n_windows].view(n_windows, w).sum(dim=1)
    mu = counts.mean()
    var = counts.var(unbiased=True)
    return var / (mu + _EPS)


# ─────────────────────────────────────────────────────────────────────────────
# #8 DFA-Hurst — differentiable detrended fluctuation analysis on |r|
# ─────────────────────────────────────────────────────────────────────────────


def dfa_hurst_surrogate(
    series: Tensor,
    min_scale: int = 16,
    max_scale_frac: float = 0.1,
    n_scales: int = 12,
    max_window: int = 512,
) -> Tensor:
    """Order-1 DFA Hurst exponent (Cont fact #8). Caller passes |r| for ``dfa_hurst_abs_r``.

    Mirrors :func:`ecomd.eval.stylized_facts.dfa_hurst`: cumulative profile, partition
    into non-overlapping windows per scale, order-1 detrend, RMS fluctuation F(s),
    slope of log F vs log s. Detrending uses a constant projection matrix per scale
    (depends only on window length), so gradients flow through the profile. May be
    noisy on short rollouts — flagged ``may be unstable`` in the plan.

    ``max_window`` caps the largest scale so the per-scale s×s projection stays
    bounded — important when called on long *real* return series (minute/L2) where
    ``0.1·n`` could otherwise be tens of thousands and OOM.
    """
    x = series
    n = x.shape[0]
    max_scale = min(int(max_scale_frac * n), max_window)
    if max_scale <= min_scale:
        return torch.zeros((), dtype=x.dtype, device=x.device)
    y = torch.cumsum(x - x.mean(), dim=0)
    scales = sorted(
        {
            int(round(s))
            for s in torch.logspace(
                torch.log10(torch.tensor(float(min_scale))),
                torch.log10(torch.tensor(float(max_scale))),
                n_scales,
            ).tolist()
            if int(round(s)) >= min_scale
        }
    )
    log_s: list[Tensor] = []
    log_f: list[Tensor] = []
    for s in scales:
        nw = n // s
        if nw < 4:
            continue
        W = y[: nw * s].view(nw, s)  # (nw, s)
        t = torch.arange(s, dtype=x.dtype, device=x.device)
        A = torch.stack([torch.ones_like(t), t], dim=1)  # (s, 2)
        proj = A @ torch.linalg.inv(A.T @ A) @ A.T  # (s, s), constant
        resid = W - W @ proj.T  # (nw, s)
        rms = (resid ** 2).mean(dim=1).sqrt()  # (nw,)
        f_s = (rms ** 2).mean().sqrt()
        log_s.append(torch.log(torch.tensor(float(s), dtype=x.dtype, device=x.device)))
        log_f.append(torch.log(f_s + _EPS))
    if len(log_s) < 4:
        return torch.zeros((), dtype=x.dtype, device=x.device)
    ls = torch.stack(log_s)
    lf = torch.stack(log_f)
    ls_c = ls - ls.mean()
    lf_c = lf - lf.mean()
    return (ls_c * lf_c).sum() / ((ls_c ** 2).sum() + _EPS)
