"""Tests for the heterogeneous-node MoE router (exp 110, Path B2).

Covers: router output bounded, load-balance ≥0 & minimized at uniform routing,
OFF-path determinism (router not built), grad liveness through both rollout paths,
and the load-balance hook surface.
"""

from __future__ import annotations

import pytest
import torch

from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator
from ecomd.models.moe_router import AgentExpertRouter


def test_router_output_bounded():
    r = AgentExpertRouter(d_state=8, n_experts=4, log_scale_clip=1.5)
    s = torch.randn(50, 8)
    ctx = torch.tensor([0.01, -0.02])
    gmul, tmul = r(s, ctx)
    assert gmul.shape == (50, 1) and tmul.shape == (50, 1)
    bound = torch.exp(torch.tensor(1.5))
    assert (gmul > 0).all() and (gmul <= bound * 1.001).all()
    assert (tmul > 0).all() and (tmul <= bound * 1.001).all()


def test_load_balance_nonneg_and_minimized_at_uniform():
    r = AgentExpertRouter(d_state=8, n_experts=4)
    s = torch.randn(200, 8)
    ctx = torch.zeros(2)
    lb = r.load_balance(s, ctx)
    assert lb >= -1e-5, "load-balance importance loss must be >= 0"
    # Near-uniform gate (zero-init) → lb near 0; a collapsed gate → lb large.
    with torch.no_grad():
        r.gate[-1].bias.copy_(torch.tensor([10.0, 0.0, 0.0, 0.0]))  # collapse to expert 0
    lb_collapsed = r.load_balance(s, ctx)
    assert float(lb_collapsed) > float(lb), "collapsed routing should raise the load-balance loss"


def test_grad_reaches_router_params():
    r = AgentExpertRouter(d_state=8, n_experts=4)
    s = torch.randn(50, 8)
    ctx = torch.tensor([0.01, 0.0])
    gmul, tmul = r(s, ctx)
    (gmul.sum() + tmul.sum() + r.load_balance(s, ctx)).backward()
    assert r.log_gamma_scale.grad is not None and r.log_gamma_scale.grad.abs().sum() > 0
    assert r.gate[0].weight.grad is not None and r.gate[0].weight.grad.abs().sum() > 0


def _run(moe_kwargs: dict | None, *, custom_fn: bool, n_steps: int = 6, seed: int = 0):
    base = dict(
        n_agents=20, d_state=8, hidden=16,
        pairwise_kind="stochastic_mlp", sps_k_random=4,
        bptt_custom_function=custom_fn,
    )
    if moe_kwargs is not None:
        base.update({"moe_enabled": True, **moe_kwargs})
    cfg = EcoMDConfig(**base)
    sim = EcoMDSimulator(cfg)
    gen = torch.Generator(); gen.manual_seed(seed)
    s = sim.init_state(generator=gen)
    _, _, traj, _ = sim.rollout_chunk(
        s, s.detach().clone(), sim.init_price(), n_steps=n_steps,
        generator=gen, create_graph=True,
    )
    return sim, traj


@pytest.mark.parametrize("custom_fn", [False, True])
def test_off_path_deterministic(custom_fn):
    torch.set_num_threads(1)
    sim, _ = _run(None, custom_fn=custom_fn)
    assert sim.moe_router is None

    def _roll():
        gen = torch.Generator(); gen.manual_seed(0)
        s = sim.init_state(generator=gen)
        _, _, traj, _ = sim.rollout_chunk(s, s.detach().clone(), sim.init_price(),
                                          n_steps=6, generator=gen, create_graph=True)
        return traj.log_returns.detach().clone()
    assert torch.equal(_roll(), _roll())


@pytest.mark.parametrize("custom_fn", [False, True])
def test_moe_grad_through_rollout(custom_fn):
    sim, traj = _run({"moe_n_experts": 4}, custom_fn=custom_fn)
    assert sim.moe_router is not None
    loss = traj.log_returns.pow(2).sum()
    # include the load-balance term (the trainer hook)
    lb = sim.moe_load_balance(sim.init_state(generator=torch.Generator().manual_seed(1)))
    (loss + 0.01 * lb).backward()
    assert sim.moe_router.log_gamma_scale.grad is not None
    assert sim.moe_router.log_gamma_scale.grad.abs().sum() > 0
    assert torch.isfinite(traj.log_returns).all()


def test_info_asym_channel_builds_and_runs():
    sim, traj = _run({"moe_n_experts": 3, "info_asym_enabled": True,
                      "info_asym_frac": 0.5}, custom_fn=False)
    assert sim.is_informed is not None and sim.is_informed.sum() > 0
    assert torch.isfinite(traj.log_returns).all()
    # fundamental should have evolved off zero over the rollout
    assert sim._fundamental != 0.0
