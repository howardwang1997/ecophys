"""End-to-end smoke tests for EcoMDSimulator."""

from __future__ import annotations

import pytest
import torch

from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator


def test_run_returns_trajectory():
    cfg = EcoMDConfig(n_agents=20, d_state=8, hidden=16, dt=0.01)
    sim = EcoMDSimulator(cfg)
    traj = sim.run(n_steps=50, seed=0)
    assert traj.n_steps == 50
    assert traj.n_agents == 20
    assert traj.d_state == 8
    assert torch.isfinite(traj.states).all()
    assert torch.isfinite(traj.log_returns).all()
    assert torch.isfinite(traj.log_prices).all()


def test_run_reproducible_with_seed():
    cfg = EcoMDConfig(n_agents=10, d_state=6, hidden=8)
    sim = EcoMDSimulator(cfg)
    traj1 = sim.run(n_steps=20, seed=42)
    traj2 = sim.run(n_steps=20, seed=42)
    assert torch.allclose(traj1.log_prices, traj2.log_prices)


def test_rollout_chunk_gives_grad():
    """Chunk rollout must be differentiable into the simulator parameters."""
    cfg = EcoMDConfig(n_agents=10, d_state=4, hidden=8)
    sim = EcoMDSimulator(cfg)
    gen = torch.Generator().manual_seed(0)
    s = sim.init_state(generator=gen)
    s_prev = s.detach().clone()
    price_state = sim.init_price()

    _, _, traj = sim.rollout_chunk(s, s_prev, price_state, n_steps=16, generator=gen, create_graph=True)
    loss = traj.log_returns.pow(2).mean()
    loss.backward()

    # At least the potential params should have non-None gradients.
    seen = 0
    for p in sim.potential.parameters():
        if p.grad is not None and torch.isfinite(p.grad).all():
            seen += 1
    assert seen >= 4


def test_learnable_gamma_T_have_grad():
    cfg = EcoMDConfig(n_agents=8, d_state=4, hidden=8, learn_gamma=True, learn_temperature=True)
    sim = EcoMDSimulator(cfg)
    gen = torch.Generator().manual_seed(0)
    s = sim.init_state(generator=gen)
    s_prev = s.detach().clone()
    price_state = sim.init_price()
    _, _, traj = sim.rollout_chunk(s, s_prev, price_state, n_steps=8, generator=gen, create_graph=True)
    loss = (traj.velocities ** 2).mean()
    loss.backward()
    assert sim.log_gamma.grad is not None
    assert sim.log_temperature.grad is not None
    assert torch.isfinite(sim.log_gamma.grad)
    assert torch.isfinite(sim.log_temperature.grad)


def test_log_returns_finite_under_high_noise():
    cfg = EcoMDConfig(n_agents=15, d_state=6, hidden=8, temperature_init=0.5)
    sim = EcoMDSimulator(cfg)
    traj = sim.run(n_steps=100, seed=7)
    assert torch.isfinite(traj.log_returns).all()
    # Volume should be non-negative (absolute ΔPos sum)
    assert (traj.volumes >= 0).all()


def test_force_decomposition_finite():
    cfg = EcoMDConfig(n_agents=12, d_state=4, hidden=8)
    sim = EcoMDSimulator(cfg)
    traj = sim.run(n_steps=25, seed=3)
    assert torch.isfinite(traj.f_cons).all()
    assert torch.isfinite(traj.f_diss).all()
    assert torch.isfinite(traj.f_stoch).all()


def test_readout_price_mode_runs():
    cfg = EcoMDConfig(n_agents=10, d_state=4, hidden=8, price_formation="readout")
    sim = EcoMDSimulator(cfg)
    traj = sim.run(n_steps=30, seed=0)
    assert traj.n_steps == 30
    assert torch.isfinite(traj.log_returns).all()
