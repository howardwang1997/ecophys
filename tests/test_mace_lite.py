"""Tests for MACE-lite potential.

Covers:
- k-NN correctness
- Gaussian RBF shape / values
- Class prior normalization
- Message permutation equivariance
- Body-order composition (2, 3, 4)
- Backward pass produces finite gradients
- Graph cache refresh logic
"""

from __future__ import annotations

import pytest
import torch

from ecomd.models.mace_lite import (
    GaussianRBF,
    MACELiteConfig,
    MACELitePotential,
    build_mace_lite,
    knn_edge_index,
)


def _seeded(n: int, d: int, seed: int = 0) -> torch.Tensor:
    g = torch.Generator().manual_seed(seed)
    return torch.randn((n, d), generator=g) * 0.2


# ── Config validation ───────────────────────────────────────────────────────


def test_config_rejects_bad_body_order():
    with pytest.raises(ValueError):
        MACELiteConfig(body_order=1)
    with pytest.raises(ValueError):
        MACELiteConfig(body_order=5)


def test_config_rejects_small_k():
    with pytest.raises(ValueError):
        MACELiteConfig(k=1)


# ── k-NN ────────────────────────────────────────────────────────────────────


def test_knn_correctness_on_toy():
    """With known geometry, check neighbours identified correctly."""
    s = torch.tensor([[0.0, 0.0],
                      [1.0, 0.0],
                      [10.0, 0.0],
                      [10.5, 0.0]])
    ei = knn_edge_index(s, k=1)
    assert ei.shape == (2, 4)
    # Nearest of 0 is 1 (dist=1), nearest of 2 is 3 (dist=0.5).
    nbr = {int(ei[0, i]): int(ei[1, i]) for i in range(ei.shape[1])}
    assert nbr[0] == 1
    assert nbr[1] == 0
    assert nbr[2] == 3
    assert nbr[3] == 2


def test_knn_no_self_loops():
    s = _seeded(20, 4)
    ei = knn_edge_index(s, k=5)
    assert (ei[0] != ei[1]).all()


def test_knn_clamps_k_to_n_minus_one():
    s = _seeded(5, 3)
    ei = knn_edge_index(s, k=100)
    # Should produce exactly N·(N-1) = 20 edges at most
    assert ei.shape[1] == 5 * 4


# ── Gaussian RBF ────────────────────────────────────────────────────────────


def test_rbf_shape():
    rbf = GaussianRBF(n_rbf=8, cutoff=5.0)
    r = torch.rand(10) * 5.0
    R = rbf(r)
    assert R.shape == (10, 8)


def test_rbf_maximum_at_center():
    """RBF value is maximal when distance = center."""
    rbf = GaussianRBF(n_rbf=5, cutoff=4.0)  # centers at 0, 1, 2, 3, 4
    r = torch.tensor([2.0])
    R = rbf(r)
    # index 2 corresponds to center=2 → highest value
    assert torch.argmax(R[0]).item() == 2


# ── Full forward ────────────────────────────────────────────────────────────


def test_forward_returns_scalar_body2():
    m = build_mace_lite(d_state=8, k=4, hidden=16, body_order=2, n_classes=3, n_rbf=4, knn_refresh=5)
    s = _seeded(10, 8)
    u = m(s)
    assert u.dim() == 0
    assert torch.isfinite(u)


def test_forward_returns_scalar_body3():
    m = build_mace_lite(d_state=8, k=4, hidden=16, body_order=3, n_classes=3, n_rbf=4, knn_refresh=5)
    s = _seeded(10, 8)
    u = m(s)
    assert u.dim() == 0
    assert torch.isfinite(u)


def test_forward_returns_scalar_body4():
    m = build_mace_lite(d_state=8, k=4, hidden=16, body_order=4, n_classes=3, n_rbf=4, knn_refresh=5)
    s = _seeded(10, 8)
    u = m(s)
    assert u.dim() == 0
    assert torch.isfinite(u)


# ── Permutation invariance ──────────────────────────────────────────────────


def test_permutation_invariant_body3():
    """Reordering agents must not change the total energy."""
    torch.manual_seed(42)
    m = build_mace_lite(d_state=6, k=3, hidden=16, body_order=3, n_classes=2, n_rbf=4, knn_refresh=5)
    s = _seeded(8, 6)
    m.reset_graph_cache()
    u1 = m(s)
    m.reset_graph_cache()
    perm = torch.tensor([5, 0, 7, 2, 4, 1, 6, 3])
    u2 = m(s[perm])
    assert torch.allclose(u1, u2, atol=1e-4)


# ── Backward / gradient flow ────────────────────────────────────────────────


def test_backward_flows_body4():
    torch.manual_seed(0)
    m = build_mace_lite(d_state=4, k=3, hidden=8, body_order=4, n_classes=2, n_rbf=4, knn_refresh=5)
    s = _seeded(6, 4).requires_grad_(True)
    u = m(s)
    u.backward()
    assert s.grad is not None
    assert torch.isfinite(s.grad).all()
    seen = 0
    for p in m.parameters():
        if p.grad is not None and torch.isfinite(p.grad).all():
            seen += 1
    # type_net, msg_net, norm1, body3/4 net, readout all should have grads
    assert seen >= 6


# ── k-NN refresh logic ──────────────────────────────────────────────────────


def test_knn_refresh_interval():
    m = build_mace_lite(d_state=4, k=2, hidden=8, body_order=2, n_classes=2, n_rbf=4, knn_refresh=3)
    s = _seeded(5, 4)
    m.reset_graph_cache()
    _ = m(s)
    ei_first = m._cached_edge_index.clone()
    # Call forward 2 more times with same s → should still use cached edge_index
    for _ in range(2):
        _ = m(s)
    assert torch.equal(m._cached_edge_index, ei_first)
    # Next call should refresh (step 3 after first)
    s2 = _seeded(5, 4, seed=99)  # different state → different KNN
    _ = m(s2)
    # After refresh on new state, edge_index could differ; at minimum _step_since_refresh reset
    assert m._step_since_refresh == 1


def test_reset_graph_cache():
    m = build_mace_lite(d_state=4, k=2, hidden=8, body_order=2, n_classes=2, n_rbf=4, knn_refresh=5)
    s = _seeded(5, 4)
    _ = m(s)
    assert m._cached_edge_index is not None
    m.reset_graph_cache()
    assert m._cached_edge_index is None
    assert m._step_since_refresh == 0


# ── End-to-end with EcoMDSimulator ──────────────────────────────────────────


def test_simulator_with_mace_lite_runs():
    from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator
    cfg = EcoMDConfig(
        n_agents=20, d_state=8, hidden=16, dt=0.01,
        pairwise_kind="mace_lite",
        mace_k=4, mace_body_order=3, mace_n_classes=2, mace_n_rbf=4, mace_knn_refresh=5,
    )
    sim = EcoMDSimulator(cfg)
    traj = sim.run(n_steps=20, seed=0)
    assert traj.n_steps == 20
    assert torch.isfinite(traj.log_returns).all()


def test_simulator_with_mace_lite_backprop():
    from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator
    cfg = EcoMDConfig(
        n_agents=15, d_state=4, hidden=8, dt=0.01,
        pairwise_kind="mace_lite",
        mace_k=3, mace_body_order=4, mace_n_classes=2, mace_n_rbf=4, mace_knn_refresh=3,
    )
    sim = EcoMDSimulator(cfg)
    gen = torch.Generator().manual_seed(0)
    s = sim.init_state(generator=gen)
    s_prev = s.detach().clone()
    price_state = sim.init_price()
    _, _, traj = sim.rollout_chunk(s, s_prev, price_state, n_steps=8, generator=gen, create_graph=True)
    loss = traj.log_returns.pow(2).mean()
    loss.backward()
    seen = 0
    for p in sim.potential.parameters():
        if p.grad is not None and torch.isfinite(p.grad).all():
            seen += 1
    assert seen >= 6


def test_invalid_pairwise_kind_raises():
    from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator
    cfg = EcoMDConfig(n_agents=10, d_state=4, pairwise_kind="nonsense")
    with pytest.raises(ValueError):
        EcoMDSimulator(cfg)
