"""Tests for v4 adiabatic timescale separation + collective coordinate price.

Two distinct features both addressing AR(1) drift root cause:

1. Adiabatic separation: ``cfg.inner_steps_per_price > 1`` runs N agent
   updates per price update. Per outer step the realized return is the
   sum of N independent agent walks → much closer to random walk.

2. Collective coordinate price: ``price_formation='collective'`` replaces
   hand-crafted ``ED = κ·Σ(Δs[:,0])`` with a learned mean-field
   ``ED = Σ_i weight_i · intent_i(s_i)`` that uses the FULL agent state.
   Permutation-invariant by construction.
"""

from __future__ import annotations

import math

import torch

from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator
from ecomd.models.price_formation import (
    CollectiveParams,
    CollectivePrice,
    PriceState,
)


def _small(
    *,
    inner_steps_per_price: int = 1,
    price_formation: str = "excess_demand",
    price_kwargs: dict | None = None,
) -> EcoMDSimulator:
    cfg = EcoMDConfig(
        n_agents=24,
        d_state=8,
        hidden=16,
        twopop_enabled=False,
        edge_gating_enabled=False,
        global_state_enabled=False,
        sps_k_random=5,
        jump_lambda=0.0,
        inner_steps_per_price=inner_steps_per_price,
        price_formation=price_formation,
        price_formation_kwargs=price_kwargs or {},
    )
    sim = EcoMDSimulator(cfg)
    sim.eval()
    return sim


# ─── Adiabatic ─────────────────────────────────────────────────────────────


def test_adiabatic_inner1_matches_baseline_shape() -> None:
    """inner_steps_per_price=1 reproduces baseline behavior (shape, finiteness)."""
    sim = _small(inner_steps_per_price=1)
    traj = sim.run(n_steps=8, seed=0)
    assert traj.log_returns.shape == (8,)
    assert torch.all(torch.isfinite(traj.log_returns))


def test_adiabatic_inner5_increases_per_outer_motion() -> None:
    """With 5× more agent steps per price update, the realized return per
    outer step has larger magnitude (more accumulated motion). Sanity check
    that the inner loop actually runs."""
    torch.manual_seed(42)
    sim1 = _small(inner_steps_per_price=1)
    traj1 = sim1.run(n_steps=20, seed=0)
    torch.manual_seed(42)
    sim5 = _small(inner_steps_per_price=5)
    traj5 = sim5.run(n_steps=20, seed=0)
    std1 = traj1.log_returns.std().item()
    std5 = traj5.log_returns.std().item()
    # inner=5 should have ≥1.5× the std (in practice ~2-5×; allow loose)
    assert std5 > 1.5 * std1, f"inner=5 std={std5:.4f} not > 1.5x inner=1 std={std1:.4f}"


# ─── Collective price ──────────────────────────────────────────────────────


def test_collective_price_basic_step() -> None:
    """CollectivePrice produces valid PriceStepResult with finite values."""
    torch.manual_seed(0)
    pf = CollectivePrice(d=8, params=CollectiveParams(beta=0.5))
    state = pf.init_state(torch.device("cpu"), torch.float32)
    s_prev = torch.randn(20, 8) * 0.1
    s_next = s_prev + torch.randn_like(s_prev) * 0.01
    out = pf.step(state, s_prev, s_next, generator=None)
    assert torch.isfinite(out.state.log_price)
    assert torch.isfinite(out.state.last_log_return)
    assert torch.isfinite(out.aux["volume"])
    assert torch.isfinite(out.aux["excess_demand"])
    # context: (log_price, vol, last_log_return) — 3-D
    assert out.context.shape == (3,)


def test_collective_price_permutation_invariant() -> None:
    """ED and volume must be invariant under agent reordering."""
    torch.manual_seed(0)
    pf = CollectivePrice(d=8, params=CollectiveParams(beta=0.5, sigma_price=0.0))
    state = pf.init_state(torch.device("cpu"), torch.float32)
    s_prev = torch.randn(16, 8) * 0.1
    s_next = s_prev + torch.randn_like(s_prev) * 0.01

    g1 = torch.Generator().manual_seed(0)
    g2 = torch.Generator().manual_seed(0)
    out1 = pf.step(state, s_prev, s_next, generator=g1)

    perm = torch.randperm(16)
    out2 = pf.step(state, s_prev[perm], s_next[perm], generator=g2)

    # ED and volume should match within numerical precision.
    assert torch.allclose(out1.aux["excess_demand"], out2.aux["excess_demand"], atol=1e-5), (
        f"ED not perm-invariant: {out1.aux['excess_demand']:.6f} vs "
        f"{out2.aux['excess_demand']:.6f}"
    )
    assert torch.allclose(out1.aux["volume"], out2.aux["volume"], atol=1e-5)


def test_collective_price_through_simulator() -> None:
    """End-to-end: simulator with price_formation='collective' runs and the
    aux dict makes it through the recorder."""
    sim = _small(
        price_formation="collective",
        price_kwargs={"beta": 0.5, "sigma_price": 0.005, "intent_hidden": 8},
    )
    traj = sim.run(n_steps=8, seed=0)
    assert traj.log_returns.shape == (8,)
    assert torch.all(torch.isfinite(traj.log_returns))
    assert traj.excess_demand.shape == (8,)


def test_collective_plus_adiabatic() -> None:
    """The two v4 features compose without breaking."""
    sim = _small(
        inner_steps_per_price=5,
        price_formation="collective",
        price_kwargs={"beta": 0.5, "sigma_price": 0.005},
    )
    traj = sim.run(n_steps=8, seed=0)
    assert torch.all(torch.isfinite(traj.log_returns))
    # With inner=5 + collective, return std should be O(1e-2), not blow up.
    assert traj.log_returns.abs().max().item() < 1.0
