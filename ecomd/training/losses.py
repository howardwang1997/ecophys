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
    # ── Loss redesign knobs (paper-a-loss-redesign 2026-04-26) ────────────
    # See compute_loss() and Family 1-4 docstrings.
    loss_family: str = "moments"             # moments|wasserstein|mmd|sinkhorn|hybrid
    distance_mode: str = "l1"                # l1|mse|huber — for scalar moment terms
    tail_estimator: str = "soft_hill"        # soft_hill|quantile_tail|kurtosis
    kurtosis_target: float = 5.0             # used when tail_estimator="kurtosis"
    # Distribution-distance weights (zero by default → no behaviour change)
    w_wasserstein: float = 0.0
    w_mmd: float = 0.0
    w_sinkhorn: float = 0.0
    wasserstein_scales: tuple[int, ...] = (1, 5, 20)
    mmd_bandwidths: tuple[float, ...] = (0.005, 0.01, 0.02, 0.05)
    sinkhorn_eps: float = 0.01
    sinkhorn_iters: int = 50
    # Inverse-variance / GradNorm balancing across loss components.
    balance_mode: str = "fixed"              # fixed|inv_var (grad_norm TODO)
    balance_warmup: int = 20


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


# ═════════════════════════════════════════════════════════════════════════════
# Loss redesign — paper-a-loss-redesign branch (2026-04-26)
#
# Replacements / additions to ``moment_matching_loss`` to address the failure
# modes identified after the paper-a-solidify multi-seed CI:
#
#   - L1 ``|sim - target|`` provides only sign-gradient (no distance info)
#   - 3 hand-picked moments + relu hinges leave the optimisation
#     under-determined — multiple basins, seed-dependent convergence
#   - Soft-Hill estimator on tiny rollouts (k=1..2 tail samples) is pure noise
#
# Three-family redesign:
#   1. Distribution-distance: 1D Wasserstein at multiple time-scales (replaces
#      hill / aggregational-gaussianity / gain-loss in one term).
#   2. Better tail estimators: quantile-based α and kurtosis proxy.
#   3. Smooth structural penalties (MSE/Huber) replace L1 + relu hinges.
#
# Plus a :class:`LossBalancer` for inverse-variance balancing across components,
# and a unified :func:`compute_loss` dispatcher that respects the new
# ``LossWeights`` flags.
# ═════════════════════════════════════════════════════════════════════════════


# ─────────────────────────────────────────────────────────────────────────────
# Distance-mode dispatch
# ─────────────────────────────────────────────────────────────────────────────


def smooth_dev(sim_value: Tensor, target_value: float | Tensor, mode: str = "mse") -> Tensor:
    """Differentiable deviation between a scalar sim statistic and target.

    ``mode``:
      - ``"mse"``  — squared L2.  Smooth, distance-aware, default for redesign.
      - ``"huber"``— L2 near zero, L1 far.  Robust to outliers.
      - ``"l1"``   — original behavior.  Sign-only gradient (legacy).
    """
    if isinstance(target_value, (int, float)):
        target = torch.as_tensor(float(target_value), device=sim_value.device, dtype=sim_value.dtype)
    else:
        target = target_value.to(sim_value)
    d = sim_value - target
    if mode == "mse":
        return d ** 2
    if mode == "huber":
        return torch.where(d.abs() < 1.0, 0.5 * d ** 2, d.abs() - 0.5)
    if mode == "l1":
        return d.abs()
    raise ValueError(f"unknown distance_mode {mode!r}; expected mse|huber|l1")


# ─────────────────────────────────────────────────────────────────────────────
# Family 1 — Distribution-distance losses (target marginal at multiple scales)
# ─────────────────────────────────────────────────────────────────────────────


def aggregate_returns(returns: Tensor, scale: int) -> Tensor:
    """Sum consecutive ``scale`` returns → multi-scale aggregation.

    For log-returns, summing across ``scale`` consecutive bars gives the
    log-return over a ``scale``-day window. Used for matching the
    aggregational-gaussianity property (Cont fact #7).
    """
    if scale <= 1:
        return returns
    n = (returns.shape[0] // scale) * scale
    if n == 0:
        return returns[:1] * 0.0  # return empty-ish to skip
    return returns[:n].view(-1, scale).sum(dim=1)


def wasserstein1d(sim_returns: Tensor, real_returns: Tensor) -> Tensor:
    """1D Wasserstein-1 (sliced L1) between two sample sets.

    Closed-form via sorted L1: W1(F_a, F_b) = (1/n) Σ |a_(i) - b_(i)| when
    both samples have equal length; we interpolate to the smaller length
    via uniform-quantile resampling.

    Differentiable: torch.sort returns gradients via the sort permutation.
    """
    if sim_returns.numel() == 0 or real_returns.numel() == 0:
        return torch.zeros((), device=sim_returns.device, dtype=sim_returns.dtype)

    sim_sorted, _ = torch.sort(sim_returns)
    real_sorted, _ = torch.sort(real_returns)

    n_sim = sim_sorted.shape[0]
    n_real = real_sorted.shape[0]
    n = min(n_sim, n_real)

    # Resample to common length n via linear interpolation in quantile-space.
    if n_sim != n:
        sim_aligned = _quantile_resample(sim_sorted, n)
    else:
        sim_aligned = sim_sorted
    if n_real != n:
        real_aligned = _quantile_resample(real_sorted, n)
    else:
        real_aligned = real_sorted

    return (sim_aligned - real_aligned).abs().mean()


def _quantile_resample(sorted_x: Tensor, n_target: int) -> Tensor:
    """Take a sorted 1-D tensor and resample to ``n_target`` points by
    linear interpolation along the empirical quantile axis."""
    n_src = sorted_x.shape[0]
    if n_src == n_target:
        return sorted_x
    # Source quantile positions q_src ∈ [0, 1], target q_tgt ∈ [0, 1]
    q_src = torch.linspace(0.0, 1.0, n_src, device=sorted_x.device, dtype=sorted_x.dtype)
    q_tgt = torch.linspace(0.0, 1.0, n_target, device=sorted_x.device, dtype=sorted_x.dtype)
    # For each q in q_tgt, find bracketing indices in q_src and lerp
    # bucketize returns indices in [0, n_src]; clamp to valid bracket range.
    idx_hi = torch.bucketize(q_tgt, q_src).clamp(min=1, max=n_src - 1)
    idx_lo = idx_hi - 1
    q_lo = q_src[idx_lo]
    q_hi = q_src[idx_hi]
    x_lo = sorted_x[idx_lo]
    x_hi = sorted_x[idx_hi]
    span = (q_hi - q_lo).clamp(min=1e-12)
    w = ((q_tgt - q_lo) / span).clamp(0.0, 1.0)
    return x_lo + w * (x_hi - x_lo)


def wasserstein_multi_scale(
    sim_returns: Tensor,
    real_returns: Tensor,
    scales: tuple[int, ...] = (1, 5, 20),
) -> Tensor:
    """Mean of W1 distances at each aggregation scale.

    By matching the marginal at multiple time-scales, this single term
    constrains heavy tails (scale=1), aggregational gaussianity (scale=5,
    20), and the gain-loss asymmetry (scale=1 skewness) simultaneously.
    """
    losses = []
    for s in scales:
        sim_s = aggregate_returns(sim_returns, s)
        real_s = aggregate_returns(real_returns, s)
        if sim_s.shape[0] >= 4 and real_s.shape[0] >= 4:
            losses.append(wasserstein1d(sim_s, real_s))
    if not losses:
        return torch.zeros((), device=sim_returns.device, dtype=sim_returns.dtype)
    return torch.stack(losses).mean()


def mmd_gaussian_multi_bandwidth(
    sim_returns: Tensor,
    real_returns: Tensor,
    bandwidths: tuple[float, ...] = (0.005, 0.01, 0.02, 0.05),
    n_subsample: int = 200,
) -> Tensor:
    """Maximum Mean Discrepancy (squared) with multi-bandwidth Gaussian kernel.

    Subsamples each side to ``n_subsample`` for tractable O(n²) cost.
    Differentiable end-to-end (subsampling is by slicing the head; for
    ``sim_returns`` whose order is meaningful this is actually a hot-window
    sample, but for matching marginals that's acceptable).
    """
    n = min(sim_returns.shape[0], real_returns.shape[0], n_subsample)
    if n < 4:
        return torch.zeros((), device=sim_returns.device, dtype=sim_returns.dtype)
    s = sim_returns[:n].unsqueeze(1) - sim_returns[:n].unsqueeze(0)  # (n, n)
    r = real_returns[:n].unsqueeze(1) - real_returns[:n].unsqueeze(0)
    sr = sim_returns[:n].unsqueeze(1) - real_returns[:n].unsqueeze(0)
    mmd2 = torch.zeros((), device=sim_returns.device, dtype=sim_returns.dtype)
    for h in bandwidths:
        denom = 2.0 * h * h
        Kss = torch.exp(-(s ** 2) / denom).mean()
        Krr = torch.exp(-(r ** 2) / denom).mean()
        Ksr = torch.exp(-(sr ** 2) / denom).mean()
        mmd2 = mmd2 + (Kss + Krr - 2.0 * Ksr)
    return mmd2 / float(len(bandwidths))


def sinkhorn_divergence(
    sim_returns: Tensor,
    real_returns: Tensor,
    eps: float = 0.01,
    n_iters: int = 50,
    n_subsample: int = 200,
) -> Tensor:
    """Entropic OT cost via Sinkhorn iterations. Smoother than W1, useful
    when sample sizes differ. Subsampled to O(n²).

    Returns the Sinkhorn cost ⟨π, C⟩ where π is the optimal transport plan
    and C_ij = |sim_i - real_j|. Fully differentiable.
    """
    n = min(sim_returns.shape[0], real_returns.shape[0], n_subsample)
    if n < 4:
        return torch.zeros((), device=sim_returns.device, dtype=sim_returns.dtype)
    x = sim_returns[:n]
    y = real_returns[:n]
    C = (x.unsqueeze(1) - y.unsqueeze(0)).abs()  # (n, n)
    # Uniform marginals (n,)
    a = torch.full((n,), 1.0 / n, device=x.device, dtype=x.dtype)
    b = torch.full((n,), 1.0 / n, device=x.device, dtype=x.dtype)
    log_a = torch.log(a)
    log_b = torch.log(b)
    K = -C / eps  # log-kernel
    log_u = torch.zeros_like(a)
    log_v = torch.zeros_like(b)
    for _ in range(n_iters):
        log_u = log_a - torch.logsumexp(K + log_v.unsqueeze(0), dim=1)
        log_v = log_b - torch.logsumexp(K + log_u.unsqueeze(1), dim=0)
    # Transport plan π = exp(log_u + K + log_v)
    log_pi = log_u.unsqueeze(1) + K + log_v.unsqueeze(0)
    pi = torch.exp(log_pi)
    return (pi * C).sum()


# ─────────────────────────────────────────────────────────────────────────────
# Family 2 — Better tail estimators (replace soft Hill on small samples)
# ─────────────────────────────────────────────────────────────────────────────


def quantile_tail_alpha(
    returns: Tensor,
    q_low: float = 0.90,
    eps: float = 1e-8,
) -> Tensor:
    """Tail exponent α from log-log fit of empirical CCDF in the upper tail.

    For Pareto-tailed distributions, P(|r|>x) ∝ x^(-α). Fitting log P vs
    log x in the upper tail (top (1-q_low) fraction of |r|) gives a
    smoother, lower-variance estimate than Hill's MLE on tiny tail samples.

    More stable than ``soft_hill_tail_index`` when only ~50-100 returns
    are available.
    """
    abs_r = returns.abs() + eps
    sorted_r, _ = torch.sort(abs_r, descending=True)
    n = sorted_r.shape[0]
    n_tail = max(int((1.0 - q_low) * n), 4)
    n_tail = min(n_tail, n - 1)
    tail_vals = sorted_r[:n_tail]
    log_x = torch.log(tail_vals)
    # Empirical CCDF at the i-th largest value: P̂(|r|>x_i) = i/n
    # log P = log(i/n) for i = 1..n_tail
    i_vals = torch.arange(1, n_tail + 1, device=returns.device, dtype=returns.dtype)
    log_p = torch.log(i_vals / float(n))
    # Linear regression: log_p = -α · log_x + c → slope = -α
    log_x_c = log_x - log_x.mean()
    log_p_c = log_p - log_p.mean()
    denom = (log_x_c ** 2).sum() + 1e-12
    slope = (log_x_c * log_p_c).sum() / denom
    return -slope  # α > 0


def kurtosis_proxy(returns: Tensor, eps: float = 1e-12) -> Tensor:
    """Excess kurtosis E[r⁴]/E[r²]² - 3 as a tail-heaviness proxy.

    Lower variance than Hill on small samples (uses all data, not just
    tail). Higher kurtosis = heavier tails. Real markets: ~2-10 daily.
    """
    r = returns - returns.mean()
    var = (r ** 2).mean() + eps
    return (r ** 4).mean() / (var ** 2) - 3.0


# ─────────────────────────────────────────────────────────────────────────────
# Family 4 — Loss balancer
# ─────────────────────────────────────────────────────────────────────────────


class LossBalancer:
    """Tracks per-component loss magnitudes; produces re-balanced weights.

    Modes:
      - ``"fixed"``: returns the base weights unchanged (pass-through).
      - ``"inv_var"``: scale each component's weight by 1/std(loss_value)
        over the last ``warmup`` iters. Equalises learning signal magnitudes
        across loss terms with very different natural scales (e.g. acf ~
        0.05 vs hill ~ 5).

    Usage:
        balancer = LossBalancer(mode="inv_var")
        for it in iters:
            loss_dict = compute_loss(...)
            ws = balancer.update_and_get_weights(loss_dict, base_weights)
            total = sum(ws[k] * loss_dict[k] for k in loss_dict)
    """

    def __init__(self, mode: str = "fixed", warmup: int = 20):
        self.mode = mode
        self.warmup = warmup
        self.history: dict[str, list[float]] = {}

    def update_and_get_weights(
        self,
        loss_dict: dict[str, Tensor],
        base_weights: dict[str, float],
    ) -> dict[str, float]:
        if self.mode == "fixed":
            return dict(base_weights)
        # Track magnitude
        for k, v in loss_dict.items():
            if k in base_weights and base_weights[k] > 0:
                self.history.setdefault(k, []).append(float(v.detach().abs().item()))
        # Wait until warmup
        if any(len(self.history.get(k, [])) < self.warmup
               for k, w in base_weights.items() if w > 0):
            return dict(base_weights)
        if self.mode == "inv_var":
            # weight ∝ base / running_std (avoids dividing by 0)
            weights = {}
            for k, base in base_weights.items():
                if base <= 0 or k not in self.history:
                    weights[k] = base
                    continue
                hist = self.history[k][-self.warmup:]
                std_k = max(float(np.std(hist)), 1e-6)
                weights[k] = base / std_k
            # Renormalise so sum(weights) == sum(base) (preserve overall scale)
            base_sum = sum(base_weights.values())
            new_sum = sum(weights.values()) + 1e-12
            scale = base_sum / new_sum if base_sum > 0 else 1.0
            return {k: w * scale for k, w in weights.items()}
        raise ValueError(f"unknown balance_mode {self.mode!r}; expected fixed|inv_var")


# ─────────────────────────────────────────────────────────────────────────────
# Extended LossWeights — adds redesign knobs
# ─────────────────────────────────────────────────────────────────────────────
#
# The original ``LossWeights`` above is preserved (all defaults make
# moment-matching behave as before). The redesign adds new fields with
# zero defaults so existing configs continue to work unchanged.
#
# We don't redefine LossWeights here — instead, the file ends with the
# original (which now needs the new fields appended). Done in a separate
# Edit to keep this section clean.


# ─────────────────────────────────────────────────────────────────────────────
# Unified compute_loss dispatcher
# ─────────────────────────────────────────────────────────────────────────────


def compute_loss(
    sim_returns: Tensor,
    target_returns: Tensor | None,
    targets: MomentTargets,
    weights: "LossWeights",
) -> dict[str, Tensor]:
    """Unified loss computation supporting redesigned components.

    Behavior depends on ``weights`` flags:

    - ``loss_family == "moments"`` (default): identical to legacy
      :func:`moment_matching_loss` — backwards-compatible.
    - ``"wasserstein"``: pure W1 multi-scale on returns vs ``target_returns``.
      Requires ``target_returns`` to be a torch tensor of real returns.
    - ``"mmd"``: MMD-only, similar requirement.
    - ``"sinkhorn"``: Sinkhorn divergence on returns.
    - ``"hybrid"``: distribution distance + smooth structure facts (best of both).

    The ``distance_mode`` and ``tail_estimator`` knobs control how the
    structural facts (acf², leverage, hill / quantile-tail / kurtosis,
    autocorr_r, zumbach) are penalised in hybrid / moments families.

    Returns a dict containing component values and ``"total"``.
    """
    family = getattr(weights, "loss_family", "moments")
    distance_mode = getattr(weights, "distance_mode", "l1")
    tail_estimator = getattr(weights, "tail_estimator", "soft_hill")

    # Backward-compat fast-path: if family is "moments" AND distance_mode
    # is "l1" AND tail_estimator is "soft_hill", route to legacy.
    if family == "moments" and distance_mode == "l1" and tail_estimator == "soft_hill":
        return moment_matching_loss(sim_returns, targets, weights)

    out: dict[str, Tensor] = {}
    total = torch.zeros((), device=sim_returns.device, dtype=sim_returns.dtype)

    # ── Distribution-distance term (Family 1) ─────────────────────────────
    if family in ("wasserstein", "hybrid") and getattr(weights, "w_wasserstein", 0.0) > 0:
        if target_returns is None:
            raise ValueError("wasserstein loss requires target_returns")
        scales = tuple(getattr(weights, "wasserstein_scales", (1, 5, 20)))
        w_term = wasserstein_multi_scale(sim_returns, target_returns.to(sim_returns), scales)
        out["wasserstein"] = w_term
        total = total + weights.w_wasserstein * w_term

    if family in ("mmd", "hybrid") and getattr(weights, "w_mmd", 0.0) > 0:
        if target_returns is None:
            raise ValueError("mmd loss requires target_returns")
        bandwidths = tuple(getattr(weights, "mmd_bandwidths", (0.005, 0.01, 0.02, 0.05)))
        m_term = mmd_gaussian_multi_bandwidth(
            sim_returns, target_returns.to(sim_returns), bandwidths
        )
        out["mmd"] = m_term
        total = total + weights.w_mmd * m_term

    if family in ("sinkhorn", "hybrid") and getattr(weights, "w_sinkhorn", 0.0) > 0:
        if target_returns is None:
            raise ValueError("sinkhorn loss requires target_returns")
        s_eps = float(getattr(weights, "sinkhorn_eps", 0.01))
        s_iters = int(getattr(weights, "sinkhorn_iters", 50))
        s_term = sinkhorn_divergence(
            sim_returns, target_returns.to(sim_returns), eps=s_eps, n_iters=s_iters,
        )
        out["sinkhorn"] = s_term
        total = total + weights.w_sinkhorn * s_term

    # ── Structural penalties (Family 3 — smooth dev) ──────────────────────
    # ACF² (always smooth dev when not in pure-moments mode)
    if weights.w_acf_sq > 0:
        acf_sim = acf_sq_mean(sim_returns, max_lag=weights.max_lag)
        dev_acf = smooth_dev(acf_sim, targets.acf_sq_mean, mode=distance_mode)
        out["acf_sq"] = dev_acf
        out["acf_sim"] = acf_sim.detach()
        total = total + weights.w_acf_sq * dev_acf

    if weights.w_leverage > 0:
        lev_sim = leverage_effect_sum(sim_returns, max_lag=weights.max_lag)
        dev_lev = smooth_dev(lev_sim, targets.leverage_sum, mode=distance_mode)
        out["leverage"] = dev_lev
        out["leverage_sim"] = lev_sim.detach()
        total = total + weights.w_leverage * dev_lev

    # Tail term (only when family is "moments" or "hybrid"; pure-distribution
    # families let W1/MMD carry the tail signal).
    if family in ("moments", "hybrid") and weights.w_hill > 0:
        if tail_estimator == "soft_hill":
            tail_sim = soft_hill_tail_index(sim_returns, k_frac=weights.hill_k_frac)
            target_tail = targets.hill_alpha
        elif tail_estimator == "quantile_tail":
            tail_sim = quantile_tail_alpha(sim_returns, q_low=0.90)
            target_tail = targets.hill_alpha  # reusing the field as α target
        elif tail_estimator == "kurtosis":
            tail_sim = kurtosis_proxy(sim_returns)
            # Proxy target: real markets typically 5-20 excess kurtosis daily.
            target_tail = float(getattr(weights, "kurtosis_target", 5.0))
        else:
            raise ValueError(f"unknown tail_estimator {tail_estimator!r}")
        dev_tail = smooth_dev(tail_sim, target_tail, mode=distance_mode)
        out["hill"] = dev_tail  # keep "hill" key for back-compat downstream
        out["hill_sim"] = tail_sim.detach()
        total = total + weights.w_hill * dev_tail
    else:
        # Even when not used in loss, expose a hill_sim placeholder for logging
        if "hill_sim" not in out:
            with torch.no_grad():
                out["hill_sim"] = soft_hill_tail_index(
                    sim_returns, k_frac=weights.hill_k_frac
                ).detach()

    # autocorr_r (raw-return lag-1 autocorr) — already smooth dev (target=0)
    if weights.w_autocorr_r > 0:
        ar = autocorr_returns_lag1(sim_returns)
        ar_pen = smooth_dev(ar, 0.0, mode=distance_mode)
        out["autocorr_r"] = ar.detach()
        out["autocorr_r_pen"] = ar_pen
        total = total + weights.w_autocorr_r * ar_pen

    # Hill ceiling (kept as L1 hinge — target is "hill < hill_max", which
    # naturally maps to relu).
    if weights.w_hill_max > 0 and tail_estimator == "soft_hill":
        hill_sim = out.get("hill_sim", soft_hill_tail_index(
            sim_returns, k_frac=weights.hill_k_frac
        ).detach())
        excess = torch.relu(hill_sim - weights.hill_max_target)
        out["hill_excess"] = excess
        total = total + weights.w_hill_max * excess

    # Zumbach — kept as hinge (one-sided constraint: D̄ ≥ target)
    if weights.w_zumbach > 0:
        zum = zumbach_asymmetry_diff(
            sim_returns,
            coarse_window=weights.zumbach_coarse_window,
            max_lag=weights.max_lag,
            avg_lags=weights.zumbach_avg_lags,
        )
        zum_pen = torch.relu(weights.zumbach_target - zum)
        out["zumbach_sim"] = zum.detach()
        out["zumbach_pen"] = zum_pen
        total = total + weights.w_zumbach * zum_pen

    out["total"] = total
    return out
