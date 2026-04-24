"""Tests for differentiable moment-matching losses."""

from __future__ import annotations

import numpy as np
import torch

from ecomd.training.losses import (
    LossWeights,
    MomentTargets,
    acf_sq_mean,
    build_targets_from_returns,
    leverage_effect_sum,
    moment_matching_loss,
    soft_hill_tail_index,
)


def _garch_like_returns(n: int = 500, seed: int = 0) -> torch.Tensor:
    rng = np.random.default_rng(seed)
    eps = rng.standard_normal(n)
    sigma2 = np.empty(n)
    sigma2[0] = 1.0
    r = np.empty(n)
    r[0] = np.sqrt(sigma2[0]) * eps[0]
    for t in range(1, n):
        sigma2[t] = 0.01 + 0.1 * r[t - 1] ** 2 + 0.85 * sigma2[t - 1]
        r[t] = np.sqrt(sigma2[t]) * eps[t]
    return torch.tensor(r, dtype=torch.float32)


# ── acf_sq_mean ─────────────────────────────────────────────────────────────


def test_acf_sq_iid_is_near_zero():
    torch.manual_seed(0)
    r = torch.randn(2000)
    v = acf_sq_mean(r, max_lag=20)
    assert v.item() == torch.allclose(v, torch.tensor(0.0), atol=0.1) or abs(v.item()) < 0.1


def test_acf_sq_garch_is_positive():
    r = _garch_like_returns(n=1500)
    v = acf_sq_mean(r, max_lag=20)
    assert v.item() > 0.05


def test_acf_sq_differentiable():
    r = torch.randn(200, requires_grad=True)
    v = acf_sq_mean(r, max_lag=10)
    v.backward()
    assert r.grad is not None
    assert torch.isfinite(r.grad).all()


# ── leverage_effect_sum ─────────────────────────────────────────────────────


def test_leverage_iid_is_small():
    torch.manual_seed(0)
    r = torch.randn(2000)
    v = leverage_effect_sum(r, max_lag=20)
    assert abs(v.item()) < 2.0  # summed over 20 lags, IID gives ~0


def test_leverage_differentiable():
    r = torch.randn(200, requires_grad=True)
    v = leverage_effect_sum(r, max_lag=10)
    v.backward()
    assert r.grad is not None
    assert torch.isfinite(r.grad).all()


# ── soft_hill_tail_index ────────────────────────────────────────────────────


def test_hill_differentiable():
    torch.manual_seed(0)
    r = _garch_like_returns(n=500).clone().detach().requires_grad_(True)
    alpha = soft_hill_tail_index(r, k_frac=0.05)
    alpha.backward()
    assert r.grad is not None
    assert torch.isfinite(r.grad).all()


def test_hill_student_t_roughly_matches_df():
    """For Student-t with df=4, Hill estimator should give α ≈ 4."""
    rng = np.random.default_rng(0)
    r = torch.tensor(rng.standard_t(df=4, size=5000), dtype=torch.float32)
    alpha = soft_hill_tail_index(r, k_frac=0.05, temperature=0.1)
    # tolerance is loose because soft Hill with k_frac=0.05 has some bias
    assert 1.5 < alpha.item() < 8.0


# ── moment_matching_loss ────────────────────────────────────────────────────


def test_loss_backwards_to_returns():
    torch.manual_seed(0)
    r = torch.randn(400, requires_grad=True)
    targets = MomentTargets(acf_sq_mean=0.2, leverage_sum=-0.8, hill_alpha=3.0)
    out = moment_matching_loss(r, targets, LossWeights())
    out["total"].backward()
    assert r.grad is not None
    assert torch.isfinite(r.grad).all()


def test_loss_decreases_when_returns_match_targets():
    """Sanity: if sim returns are drawn from a GARCH, loss against its own
    computed targets should be near zero."""
    r = _garch_like_returns(n=1500)
    targets = build_targets_from_returns(r.numpy())
    out = moment_matching_loss(r, targets, LossWeights())
    # should be tiny since targets came from this exact series
    assert out["total"].item() < 0.1


def test_build_targets_returns_valid():
    r = _garch_like_returns(n=500)
    t = build_targets_from_returns(r.numpy())
    assert np.isfinite(t.acf_sq_mean)
    assert np.isfinite(t.leverage_sum)
    assert np.isfinite(t.hill_alpha)
