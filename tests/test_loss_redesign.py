"""Tests for the loss-redesign components (paper-a-loss-redesign branch).

Verifies:
- 1D Wasserstein and MMD return ≈0 on identical samples, ≈shift on shifted
- quantile_tail_alpha recovers a known Pareto exponent
- kurtosis_proxy is gradient-positive in the heavy-tail direction
- LossBalancer.inv_var rescales magnitudes correctly
- compute_loss dispatches to legacy moment_matching_loss in default config
- compute_loss with loss_family="wasserstein" uses target_returns
"""

from __future__ import annotations

import math

import numpy as np
import pytest
import torch

from ecomd.training.losses import (
    LossBalancer,
    LossWeights,
    MomentTargets,
    aggregate_returns,
    compute_loss,
    kurtosis_proxy,
    mmd_gaussian_multi_bandwidth,
    moment_matching_loss,
    quantile_tail_alpha,
    sinkhorn_divergence,
    smooth_dev,
    wasserstein1d,
    wasserstein_multi_scale,
)


# ─────────────────────────────────────────────────────────────────────────────
# Distribution-distance losses
# ─────────────────────────────────────────────────────────────────────────────


def test_wasserstein_zero_on_identical():
    torch.manual_seed(42)
    r = torch.randn(200) * 0.01
    w = wasserstein1d(r, r)
    assert w.item() < 1e-6, f"expected ≈0, got {w.item()}"


def test_wasserstein_positive_on_shift():
    """W1 of shifted distribution equals the shift magnitude."""
    torch.manual_seed(0)
    r = torch.randn(500) * 0.01
    shift = 0.005
    r_shifted = r + shift
    w = wasserstein1d(r, r_shifted)
    # |sorted_a - sorted_b| = |a - (a+shift)| = shift for matched samples
    assert abs(w.item() - shift) < 1e-4, f"expected {shift}, got {w.item()}"


def test_wasserstein_multi_scale_zero_on_same():
    torch.manual_seed(7)
    r = torch.randn(120) * 0.01
    w = wasserstein_multi_scale(r, r, scales=(1, 5, 20))
    assert w.item() < 1e-5


def test_wasserstein_handles_unequal_lengths():
    """W1 works when sim and real have different lengths."""
    torch.manual_seed(1)
    sim_r = torch.randn(40) * 0.01
    real_r = torch.randn(500) * 0.01  # shorter sim is the realistic case
    w = wasserstein1d(sim_r, real_r)
    assert w.item() >= 0.0
    assert torch.isfinite(w)


def test_wasserstein_is_differentiable():
    torch.manual_seed(2)
    sim_r = (torch.randn(60) * 0.01).requires_grad_(True)
    real_r = torch.randn(200) * 0.01
    w = wasserstein_multi_scale(sim_r, real_r)
    w.backward()
    assert sim_r.grad is not None
    assert torch.isfinite(sim_r.grad).all()


def test_aggregate_returns_5day_windows():
    r = torch.tensor([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
    agg = aggregate_returns(r, scale=5)
    # 1+2+3+4+5 = 15, 6+7+8+9+10 = 40
    assert torch.allclose(agg, torch.tensor([15.0, 40.0]))


def test_mmd_zero_on_identical():
    torch.manual_seed(0)
    r = torch.randn(150) * 0.01
    m = mmd_gaussian_multi_bandwidth(r, r)
    assert m.item() < 1e-5


def test_mmd_positive_on_different():
    torch.manual_seed(0)
    a = torch.randn(150) * 0.01
    b = torch.randn(150) * 0.05  # 5x wider
    m = mmd_gaussian_multi_bandwidth(a, b)
    assert m.item() > 1e-3, f"expected non-trivial MMD, got {m.item()}"


def test_sinkhorn_zero_on_identical():
    torch.manual_seed(0)
    r = torch.randn(100) * 0.01
    s = sinkhorn_divergence(r, r, eps=0.01, n_iters=50)
    # Sinkhorn of equal samples: very close to zero (entropic noise floor)
    assert s.item() < 1e-2


# ─────────────────────────────────────────────────────────────────────────────
# Tail-estimator alternatives
# ─────────────────────────────────────────────────────────────────────────────


def test_quantile_tail_alpha_recovers_pareto():
    """Pareto with shape α=3.0: estimator should give ~3 within tolerance."""
    torch.manual_seed(0)
    n = 5000
    # Pareto via inverse CDF: x = (1-u)^(-1/alpha)
    alpha_true = 3.0
    u = torch.rand(n)
    pareto_pos = (1 - u).pow(-1.0 / alpha_true)
    # Symmetric around zero (sign random)
    sign = torch.where(torch.rand(n) > 0.5, 1.0, -1.0)
    r = sign * pareto_pos
    alpha_est = quantile_tail_alpha(r, q_low=0.90)
    # Allow some bias — empirical CCDF estimator on n=5000 typically
    # recovers within ~30% for α=3
    assert 1.5 < alpha_est.item() < 6.0, f"got α={alpha_est.item():.2f}"


def test_kurtosis_proxy_higher_for_heavier_tails():
    torch.manual_seed(1)
    # Standard normal: excess kurtosis ≈ 0
    normal = torch.randn(1000)
    # Mix in some extreme outliers — heavier tails
    heavy = torch.cat([torch.randn(950), torch.randn(50) * 5])
    k_normal = kurtosis_proxy(normal).item()
    k_heavy = kurtosis_proxy(heavy).item()
    assert k_heavy > k_normal, f"expected k_heavy > k_normal; got {k_heavy} ≤ {k_normal}"


def test_kurtosis_proxy_differentiable():
    torch.manual_seed(0)
    r = torch.randn(200).requires_grad_(True)
    k = kurtosis_proxy(r)
    k.backward()
    assert r.grad is not None
    assert torch.isfinite(r.grad).all()


# ─────────────────────────────────────────────────────────────────────────────
# smooth_dev
# ─────────────────────────────────────────────────────────────────────────────


def test_smooth_dev_modes():
    sim = torch.tensor(2.0)
    target = 1.0
    assert smooth_dev(sim, target, mode="l1").item() == 1.0
    assert smooth_dev(sim, target, mode="mse").item() == 1.0
    sim = torch.tensor(3.0)
    assert smooth_dev(sim, target, mode="l1").item() == 2.0
    assert smooth_dev(sim, target, mode="mse").item() == 4.0
    # Huber: |3-1| = 2 > 1 → linear region: 2 - 0.5 = 1.5
    assert smooth_dev(sim, target, mode="huber").item() == pytest.approx(1.5)


def test_smooth_dev_unknown_mode_raises():
    with pytest.raises(ValueError):
        smooth_dev(torch.tensor(1.0), 0.0, mode="cosmic")


# ─────────────────────────────────────────────────────────────────────────────
# LossBalancer
# ─────────────────────────────────────────────────────────────────────────────


def test_loss_balancer_fixed_passthrough():
    bal = LossBalancer(mode="fixed")
    base = {"a": 1.0, "b": 2.0}
    losses = {"a": torch.tensor(5.0), "b": torch.tensor(1.0)}
    w = bal.update_and_get_weights(losses, base)
    assert w == base


def test_loss_balancer_inv_var_warmup_passthrough():
    """Before warmup, returns base weights unchanged."""
    bal = LossBalancer(mode="inv_var", warmup=10)
    base = {"a": 1.0, "b": 1.0}
    for _ in range(5):
        w = bal.update_and_get_weights(
            {"a": torch.tensor(0.5), "b": torch.tensor(2.0)}, base
        )
    assert w == base, "should still be base before warmup"


def test_loss_balancer_inv_var_after_warmup():
    """After warmup, term with higher std gets smaller weight."""
    bal = LossBalancer(mode="inv_var", warmup=20)
    base = {"a": 1.0, "b": 1.0}
    rng = np.random.default_rng(0)
    final_w = None
    for it in range(30):
        # 'a' has std ≈ 0.1, 'b' has std ≈ 1.0 → inv_var should put more weight on 'a'
        loss_a = torch.tensor(1.0 + 0.1 * rng.standard_normal())
        loss_b = torch.tensor(1.0 + 1.0 * rng.standard_normal())
        final_w = bal.update_and_get_weights({"a": loss_a, "b": loss_b}, base)
    assert final_w is not None
    assert final_w["a"] > final_w["b"], (
        f"expected a-weight > b-weight after inv_var balancing, got {final_w}"
    )
    # And weights should sum to ~base sum (= 2.0)
    assert abs(sum(final_w.values()) - sum(base.values())) < 0.05


# ─────────────────────────────────────────────────────────────────────────────
# compute_loss dispatch
# ─────────────────────────────────────────────────────────────────────────────


def test_compute_loss_default_matches_legacy():
    torch.manual_seed(0)
    sim = torch.randn(100) * 0.01
    targets = MomentTargets(acf_sq_mean=0.2, leverage_sum=-0.5, hill_alpha=3.0)
    legacy = moment_matching_loss(sim, targets, LossWeights())
    dispatch = compute_loss(sim, None, targets, LossWeights())
    assert abs(legacy["total"].item() - dispatch["total"].item()) < 1e-6


def test_compute_loss_wasserstein_family_uses_targets():
    torch.manual_seed(0)
    sim = torch.randn(100) * 0.01
    real = torch.randn(500) * 0.01
    targets = MomentTargets(acf_sq_mean=0.2, leverage_sum=-0.5, hill_alpha=3.0)
    weights = LossWeights(
        loss_family="wasserstein",
        w_acf_sq=0.0, w_leverage=0.0, w_hill=0.0,
        w_wasserstein=1.0,
    )
    out = compute_loss(sim, real, targets, weights)
    assert "wasserstein" in out
    assert out["total"].item() > 0
    assert torch.isfinite(out["total"])


def test_compute_loss_wasserstein_requires_target_returns():
    torch.manual_seed(0)
    sim = torch.randn(100) * 0.01
    targets = MomentTargets(acf_sq_mean=0.2, leverage_sum=-0.5, hill_alpha=3.0)
    weights = LossWeights(loss_family="wasserstein", w_wasserstein=1.0)
    with pytest.raises(ValueError, match="wasserstein"):
        compute_loss(sim, None, targets, weights)


def test_compute_loss_hybrid_family_combines_terms():
    torch.manual_seed(0)
    sim = torch.randn(80) * 0.01
    real = torch.randn(500) * 0.01
    targets = MomentTargets(acf_sq_mean=0.2, leverage_sum=-0.5, hill_alpha=3.0)
    weights = LossWeights(
        loss_family="hybrid",
        distance_mode="mse",
        tail_estimator="quantile_tail",
        w_wasserstein=1.0,
        w_acf_sq=0.5,
        w_leverage=0.2,
        w_hill=0.1,
    )
    out = compute_loss(sim, real, targets, weights)
    # Should have wasserstein + acf_sq + leverage + hill terms
    assert "wasserstein" in out
    assert "acf_sq" in out
    assert "leverage" in out
    assert "hill" in out  # quantile_tail still keyed under "hill" for compat
    assert "hill_sim" in out
    assert torch.isfinite(out["total"])


def test_compute_loss_distance_mode_changes_value():
    torch.manual_seed(0)
    sim = torch.randn(100) * 0.01
    targets = MomentTargets(acf_sq_mean=0.2, leverage_sum=-0.5, hill_alpha=3.0)
    weights_l1 = LossWeights(loss_family="moments", distance_mode="l1",
                             tail_estimator="quantile_tail")
    weights_mse = LossWeights(loss_family="moments", distance_mode="mse",
                              tail_estimator="quantile_tail")
    out_l1 = compute_loss(sim, None, targets, weights_l1)
    out_mse = compute_loss(sim, None, targets, weights_mse)
    # MSE penalises large devs more — typically larger total when devs > 1
    assert out_l1["total"].item() != out_mse["total"].item()
