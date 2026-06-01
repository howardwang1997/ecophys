"""Tests for the exp-112 tail-clamp probe (the one untested mechanistic lever
against the dynamical fat-tail overshoot; exp 109 proved noise-taming can't fix it).

Covers: OFF bit-exact, the soft clamp actually bounds large returns, mode="rel"
scales with running vol, grad liveness through both rollout paths, no NaN.
"""

from __future__ import annotations

import pytest
import torch

from ecomd.models.price_formation import ExcessDemandParams, ExcessDemandPrice, PriceState


def _state(vol: float = 0.01) -> PriceState:
    z = torch.tensor(0.0)
    return PriceState(
        log_price=z.clone(),
        last_log_return=z.clone(),
        volatility=torch.tensor(vol),
        step=0,
    )


def test_off_is_bit_exact():
    p_off = ExcessDemandParams(tail_clamp_c=0.0)
    p_on = ExcessDemandParams(tail_clamp_c=0.0, tail_clamp_mode="rel")  # c<=0 → skip
    a, b = ExcessDemandPrice(p_off), ExcessDemandPrice(p_on)
    s_prev = torch.randn(40, 4); s_next = torch.randn(40, 4)
    g1 = torch.Generator(); g1.manual_seed(7)
    g2 = torch.Generator(); g2.manual_seed(7)
    r1 = a.step(_state(), s_prev, s_next, generator=g1).aux["log_return"]
    r2 = b.step(_state(), s_prev, s_next, generator=g2).aux["log_return"]
    assert torch.equal(r1, r2)


def test_clamp_bounds_large_return_abs():
    # Force a huge excess demand → a large raw return, then check it's bounded.
    c = 0.02
    p = ExcessDemandParams(beta=5.0, kappa=10.0, sigma_price=0.0,
                           tail_clamp_c=c, tail_clamp_mode="abs")
    price = ExcessDemandPrice(p)
    s_prev = torch.zeros(40, 4)
    s_next = torch.zeros(40, 4); s_next[:, 0] = 1.0  # big coherent position jump
    r = price.step(_state(), s_prev, s_next, generator=torch.Generator().manual_seed(0)).aux["log_return"]
    assert r.abs() < c * 1.0001, f"abs clamp should bound |r| below {c}, got {r.item()}"


def test_rel_clamp_scales_with_volatility():
    # Same forcing, two running-vol levels → the high-vol cap admits a larger move.
    c = 3.0
    p = ExcessDemandParams(beta=5.0, kappa=10.0, sigma_price=0.0,
                           tail_clamp_c=c, tail_clamp_mode="rel")
    price = ExcessDemandPrice(p)
    s_prev = torch.zeros(40, 4); s_next = torch.zeros(40, 4); s_next[:, 0] = 1.0
    r_lo = price.step(_state(vol=0.001), s_prev, s_next,
                      generator=torch.Generator().manual_seed(0)).aux["log_return"]
    r_hi = price.step(_state(vol=0.05), s_prev, s_next,
                      generator=torch.Generator().manual_seed(0)).aux["log_return"]
    assert r_hi.abs() > r_lo.abs(), "rel clamp at higher running vol must admit a larger move"
    assert r_lo.abs() <= c * 0.001 * 1.0001


def test_grad_flows_through_clamp():
    p = ExcessDemandParams(beta=0.5, kappa=1.0, sigma_price=0.005,
                           learnable_beta=True, tail_clamp_c=4.0, tail_clamp_mode="rel")
    price = ExcessDemandPrice(p)
    # Small forcing → operate in the near-linear tanh regime (a saturated clamp
    # correctly has tanh'≈0 and would zero the grad — that is the clamp working,
    # not a plumbing break; we test that it does not block grad when unsaturated).
    s_prev = torch.randn(40, 4) * 0.01; s_next = (torch.randn(40, 4) * 0.01).requires_grad_(True)
    # aux["log_return"] is detached; the live tensor is state.last_log_return.
    r = price.step(_state(), s_prev, s_next, generator=torch.Generator().manual_seed(1)).state.last_log_return
    r.pow(2).backward()
    assert s_next.grad is not None and torch.isfinite(s_next.grad).all()
    # beta_net params should also receive gradient through the clamp
    gb = [pm.grad for pm in price.beta_net.parameters() if pm.grad is not None]
    assert gb and any(g.abs().sum() > 0 for g in gb)


@pytest.mark.parametrize("mode", ["rel", "abs"])
def test_no_nan_over_rollout(mode):
    from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator
    cfg = EcoMDConfig(n_agents=30, d_state=6, hidden=16,
                      price_formation="excess_demand",
                      price_formation_kwargs={"tail_clamp_c": 4.0, "tail_clamp_mode": mode})
    sim = EcoMDSimulator(cfg)
    gen = torch.Generator(); gen.manual_seed(0)
    s = sim.init_state(generator=gen)
    _, _, traj, _ = sim.rollout_chunk(s, s.detach().clone(), sim.init_price(),
                                      n_steps=8, generator=gen, create_graph=True)
    assert torch.isfinite(traj.log_returns).all()
