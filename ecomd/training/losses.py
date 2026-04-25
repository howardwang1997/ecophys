"""Differentiable moment-matching losses for EcoMD v0 training.

We need gradients that flow from the simulator's output returns back into the
potential parameters. The :mod:`ecomd.eval.stylized_facts` implementations are
numpy-based and report point estimates; this module provides differentiable
(torch) estimators of the same facts suitable for training.

Included:

- :func:`acf_sq_mean` — mean ACF(r²) over lags 1..K. Differentiable by direct FFT-free sum.
- :func:`leverage_effect_sum` — Σ_τ Corr(r_t, r²_{t+τ}) over τ ∈ 1..K.
- :func:`soft_hill_tail_index` — smooth Hill tail exponent estimator via soft
  top-k ordering. Differentiable.

And a high-level :func:`moment_matching_loss` that bundles them against real-
data targets using user-configurable weights.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
from torch import Tensor

# ─────────────────────────────────────────────────────────────────────────────
# ACF of squared returns
# ─────────────────────────────────────────────────────────────────────────────


def acf_sq_mean(returns: Tensor, max_lag: int = 20) -> Tensor:
    """Mean of ACF(|r|²) over lags 1..max_lag. Differentiable.

    Matches the stylized fact #6 estimator in numpy; see
    :func:`ecomd.eval.stylized_facts.acf_squared_returns`.
    """
    r2 = returns ** 2
    r2_centered = r2 - r2.mean()
    variance = (r2_centered ** 2).mean()
    # add small epsilon to avoid div-by-zero at initialization when returns may be zero
    variance = variance + 1e-12
    acf_vals = []
    n = r2.shape[0]
    for tau in range(1, max_lag + 1):
        if tau >= n:
            break
        cov = (r2_centered[:-tau] * r2_centered[tau:]).mean()
        acf_vals.append(cov / variance)
    return torch.stack(acf_vals).mean()


def autocorr_returns_lag1(returns: Tensor) -> Tensor:
    """Lag-1 autocorrelation of *raw* returns (NOT squared).

    Stylized fact #1: real markets have near-zero return autocorrelation.
    Used as a soft penalty term — anything outside ~[-0.05, 0.05] is bad.
    """
    r = returns - returns.mean()
    var = (r ** 2).mean() + 1e-12
    cov_lag1 = (r[:-1] * r[1:]).mean()
    return cov_lag1 / var


def zumbach_asymmetry_diff(
    returns: Tensor, coarse_window: int = 30, max_lag: int = 20,
    avg_lags: int = 10,
) -> Tensor:
    """Differentiable Zumbach asymmetry estimator (Cont fact #11).

    D̄ = mean over τ=1..avg_lags of [A(+τ) - A(-τ)]
    A(τ) = corr(σ_coarse(t), σ_fine(t+τ))   where σ_coarse is mean r²
    over a past window of size ``coarse_window`` separated by gap=max_lag+1.

    Real markets: D̄ > 0 (Zumbach effect — past coarse vol predicts future
    fine vol better than the reverse). Used as loss term to nudge sim
    above ~+0.01.

    Mirrors :func:`ecomd.eval.stylized_facts.zumbach_asymmetry`.
    """
    fine = returns ** 2
    n = returns.shape[0]
    gap = max_lag + 1
    cw = coarse_window
    t_lo = gap + cw - 1
    t_hi = n - 1 - max_lag
    m = t_hi - t_lo + 1
    if m < 50:
        return torch.zeros((), dtype=returns.dtype, device=returns.device)

    csum = torch.cat([
        torch.zeros(1, dtype=returns.dtype, device=returns.device),
        torch.cumsum(fine, dim=0),
    ])
    ts = torch.arange(t_lo, t_hi + 1, device=returns.device)
    coarse = (csum[ts - gap + 1] - csum[ts - gap - cw + 1]) / cw
    cmean = coarse.mean()
    cdev = coarse - cmean
    cstd = (cdev ** 2).mean().sqrt() + 1e-12

    D_terms = []
    K = min(avg_lags, max_lag)
    for k in range(1, K + 1):
        f_pos = fine[ts + k]
        f_neg = fine[ts - k]
        for fa, sign in ((f_pos, +1.0), (f_neg, -1.0)):
            pass  # placeholder — handled below
        # A(+k)
        fpd = f_pos - f_pos.mean()
        fps = (fpd ** 2).mean().sqrt() + 1e-12
        a_pos = (cdev * fpd).mean() / (cstd * fps)
        # A(-k)
        fnd = f_neg - f_neg.mean()
        fns = (fnd ** 2).mean().sqrt() + 1e-12
        a_neg = (cdev * fnd).mean() / (cstd * fns)
        D_terms.append(a_pos - a_neg)
    return torch.stack(D_terms).mean()


# ─────────────────────────────────────────────────────────────────────────────
# Leverage effect
# ─────────────────────────────────────────────────────────────────────────────


def leverage_effect_sum(returns: Tensor, max_lag: int = 20) -> Tensor:
    """Σ_{τ=1..max_lag} Corr(r_t, r²_{t+τ}). Differentiable.

    In real equity markets this sum is strongly negative (≈ -0.9 on SPX daily).
    """
    r = returns - returns.mean()
    r2 = returns ** 2
    r2 = r2 - r2.mean()
    std_r = torch.sqrt((r ** 2).mean() + 1e-12)
    std_r2 = torch.sqrt((r2 ** 2).mean() + 1e-12)
    vals = []
    n = returns.shape[0]
    for tau in range(1, max_lag + 1):
        if tau >= n:
            break
        c = (r[:-tau] * r2[tau:]).mean()
        vals.append(c / (std_r * std_r2))
    return torch.stack(vals).sum()


# ─────────────────────────────────────────────────────────────────────────────
# Soft Hill tail index
# ─────────────────────────────────────────────────────────────────────────────


def soft_hill_tail_index(
    returns: Tensor,
    k_frac: float = 0.05,
    eps: float = 1e-6,
    temperature: float = 1.0,
) -> Tensor:
    """Differentiable Hill estimator for the tail exponent α of |r|.

    Strategy: sort |r| descending (differentiable via torch.sort); smooth-select
    top-k via a soft indicator that's 1 for i<k and 0 otherwise. Use a sigmoid
    as the soft mask.
    """
    abs_r = returns.abs() + eps
    sorted_abs, _ = torch.sort(abs_r, descending=True)
    n = sorted_abs.shape[0]
    k = max(int(k_frac * n), 5)
    k = min(k, n - 1)

    # soft mask over sorted indices
    idx = torch.arange(n, device=returns.device, dtype=returns.dtype)
    soft_mask = torch.sigmoid((k - idx) / temperature)

    x_kp1 = sorted_abs[k]
    log_ratio = torch.log(sorted_abs / (x_kp1 + eps))
    # H_k = mean over top-k of log_ratio — approximated by soft_mask-weighted mean
    weighted_sum = (soft_mask * log_ratio).sum()
    weight_total = soft_mask.sum() + 1e-12
    H = weighted_sum / weight_total
    alpha = 1.0 / (H + eps)
    return alpha


# ─────────────────────────────────────────────────────────────────────────────
# Moment-matching loss
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class MomentTargets:
    """Reference values from real data (SPX, BTC, etc.)."""

    acf_sq_mean: float
    leverage_sum: float
    hill_alpha: float


@dataclass(frozen=True)
class LossWeights:
    w_acf_sq: float = 1.0
    w_leverage: float = 0.2
    w_hill: float = 0.1
    max_lag: int = 20
    hill_k_frac: float = 0.05
    # Optional ACF-shape penalty to prevent flat-regime Goodhart failure
    # (added 2026-04-25). See :mod:`ecomd.eval.acf_shape`.
    w_acf_shape: float = 0.0                 # 0 disables
    acf_shape_target_ratio: float = 2.0      # acf[peak]/|acf[tail]| must be ≥ this
    acf_shape_lag_peak: int = 1              # numerator lag
    acf_shape_lag_tail: int = 10             # denominator lag
    # v3 (2026-04-26 night): expanded loss to fight Goodhart from v3 features.
    # When v3 features add capacity, the simulator over-fits the 3 base
    # moments while breaking #1 autocorr_r + #2 hill upper bound.
    # w_autocorr_r: penalty on |lag-1 ACF of raw returns| (target ≈ 0)
    w_autocorr_r: float = 0.0                # 0 disables
    # w_hill_max: relu penalty on (hill - hill_max_target). Hill exploding
    # to 100+ in simulator means tails too thin → big loss term, but the
    # MAE penalty above is dominated by other moments. Hard ceiling here.
    w_hill_max: float = 0.0
    hill_max_target: float = 10.0            # cap simulator hill at this
    # v3 (2026-04-26): zumbach asymmetry penalty. Hinge loss against
    # zumbach_target — positive when sim D̄ < target. Real markets: D̄≈+0.05.
    w_zumbach: float = 0.0                   # 0 disables
    zumbach_target: float = 0.05
    zumbach_coarse_window: int = 30
    zumbach_avg_lags: int = 10


def moment_matching_loss(
    sim_returns: Tensor,
    targets: MomentTargets,
    weights: LossWeights | None = None,
) -> dict[str, Tensor]:
    """Compute total moment-matching loss and per-component contributions.

    Returns a dict with keys:
      - ``total``
      - ``acf_sq``   (|sim - target|)
      - ``leverage`` (|sim - target|)
      - ``hill``     (|sim - target|)
    """
    w = weights or LossWeights()
    acf_sim = acf_sq_mean(sim_returns, max_lag=w.max_lag)
    lev_sim = leverage_effect_sum(sim_returns, max_lag=w.max_lag)
    hill_sim = soft_hill_tail_index(sim_returns, k_frac=w.hill_k_frac)

    dev_acf = (acf_sim - targets.acf_sq_mean).abs()
    dev_lev = (lev_sim - targets.leverage_sum).abs()
    dev_hill = (hill_sim - targets.hill_alpha).abs()

    total = w.w_acf_sq * dev_acf + w.w_leverage * dev_lev + w.w_hill * dev_hill
    out: dict[str, Tensor] = {
        "acf_sq": dev_acf,
        "leverage": dev_lev,
        "hill": dev_hill,
        "acf_sim": acf_sim.detach(),
        "leverage_sim": lev_sim.detach(),
        "hill_sim": hill_sim.detach(),
    }

    # ACF-shape penalty (optional; disabled when w_acf_shape=0)
    if w.w_acf_shape > 0.0:
        from ..eval.acf_shape import acf_shape_loss
        shape_pen = acf_shape_loss(
            sim_returns,
            target_ratio=w.acf_shape_target_ratio,
            lag_peak=w.acf_shape_lag_peak,
            lag_tail=w.acf_shape_lag_tail,
        )
        total = total + w.w_acf_shape * shape_pen
        out["acf_shape"] = shape_pen

    # v3: penalize raw-return lag-1 autocorr (Cont fact #1)
    if w.w_autocorr_r > 0.0:
        ar = autocorr_returns_lag1(sim_returns)
        ar_pen = ar.abs()
        total = total + w.w_autocorr_r * ar_pen
        out["autocorr_r"] = ar.detach()
        out["autocorr_r_pen"] = ar_pen

    # v3: hard ceiling on hill via relu(hill - hill_max_target)
    if w.w_hill_max > 0.0:
        hill_excess = torch.relu(hill_sim - w.hill_max_target)
        total = total + w.w_hill_max * hill_excess
        out["hill_excess"] = hill_excess

    # v3 (weekend): zumbach asymmetry penalty — hinge below target
    if w.w_zumbach > 0.0:
        zum = zumbach_asymmetry_diff(
            sim_returns,
            coarse_window=w.zumbach_coarse_window,
            max_lag=w.max_lag,
            avg_lags=w.zumbach_avg_lags,
        )
        zum_pen = torch.relu(w.zumbach_target - zum)
        total = total + w.w_zumbach * zum_pen
        out["zumbach_sim"] = zum.detach()
        out["zumbach_pen"] = zum_pen

    out["total"] = total
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Helpers to build targets from numpy returns
# ─────────────────────────────────────────────────────────────────────────────


def build_targets_from_returns(
    returns_np: np.ndarray,
    max_lag: int = 20,
    k_frac: float = 0.05,
) -> MomentTargets:
    """Compute the three target moments on a numpy returns array."""
    r = torch.as_tensor(np.asarray(returns_np, dtype=np.float64), dtype=torch.float32)
    with torch.no_grad():
        acf = float(acf_sq_mean(r, max_lag=max_lag).item())
        lev = float(leverage_effect_sum(r, max_lag=max_lag).item())
        hill = float(soft_hill_tail_index(r, k_frac=k_frac).item())
    return MomentTargets(acf_sq_mean=acf, leverage_sum=lev, hill_alpha=hill)
