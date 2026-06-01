"""Tests for the exp-113 Gabaix mechanism-level solve: heterogeneous agent masses
(Zipf/Pareto sizes) + concave (square-root) price impact. These enlarge the model's
reachable set so a tail-matching loss can calibrate ζ/δ toward the inverse-cubic law.

Covers: OFF bit-exact, masses normalized + heavier tail at smaller ζ, concave map
compresses large flow + is monotone, grad to ζ/δ through both rollout paths, no NaN.
"""

from __future__ import annotations

import math

import pytest
import torch

from ecomd.models.price_formation import ExcessDemandParams, ExcessDemandPrice, PriceState


def _state(vol: float = 0.01) -> PriceState:
    z = torch.tensor(0.0)
    return PriceState(log_price=z.clone(), last_log_return=z.clone(),
                      volatility=torch.tensor(vol), step=0)


def test_off_is_bit_exact():
    a = ExcessDemandPrice(ExcessDemandParams())  # both mechanisms off
    b = ExcessDemandPrice(ExcessDemandParams(het_mass_enabled=False,
                                             impact_concave_enabled=False))
    s_prev = torch.randn(60, 4); s_next = torch.randn(60, 4)
    g1 = torch.Generator(); g1.manual_seed(3)
    g2 = torch.Generator(); g2.manual_seed(3)
    r1 = a.step(_state(), s_prev, s_next, generator=g1).aux["log_return"]
    r2 = b.step(_state(), s_prev, s_next, generator=g2).aux["log_return"]
    assert torch.equal(r1, r2)
    assert not hasattr(a, "mass_log_zeta") and not hasattr(a, "impact_logit_delta")


def test_masses_normalized_and_heavier_tail_at_small_zeta():
    n = 5000
    hi = ExcessDemandPrice(ExcessDemandParams(het_mass_enabled=True, mass_zeta_init=3.0))
    lo = ExcessDemandPrice(ExcessDemandParams(het_mass_enabled=True, mass_zeta_init=1.1))
    w_hi = hi._agent_masses(n, torch.device("cpu"), torch.float32)
    w_lo = lo._agent_masses(n, torch.device("cpu"), torch.float32)
    # Σw = n (scale-invariant in ζ)
    assert abs(float(w_hi.sum()) - n) < 1.0 and abs(float(w_lo.sum()) - n) < 1.0
    # smaller ζ → more concentrated mass (the top whale holds a larger share)
    assert float(w_lo.max()) > float(w_hi.max())
    assert float(w_lo.max() / w_lo.mean()) > float(w_hi.max() / w_hi.mean())


def test_concave_impact_compresses_large_flow_and_monotone():
    p = ExcessDemandParams(impact_concave_enabled=True, impact_delta_init=0.5, impact_scale=0.5)
    price = ExcessDemandPrice(p)
    small = price._concave_impact(torch.tensor(0.5))   # ~ at the scale → near-linear
    big = price._concave_impact(torch.tensor(20.0))    # >> scale → compressed
    # concavity: the big move is compressed far below its linear value
    assert float(big) < 20.0
    # compression ratio grows with magnitude (sub-linear)
    assert float(big) / 20.0 < float(small) / 0.5
    # monotone increasing + sign-preserving
    xs = torch.tensor([-10.0, -1.0, 0.0, 1.0, 10.0])
    ys = torch.stack([price._concave_impact(x) for x in xs])
    assert torch.all(ys[1:] - ys[:-1] > 0)
    assert float(price._concave_impact(torch.tensor(-3.0))) < 0


def _sim(kwargs: dict, *, custom_fn: bool, n_steps: int = 6, seed: int = 0):
    from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator
    cfg = EcoMDConfig(n_agents=40, d_state=8, hidden=16,
                      pairwise_kind="stochastic_mlp", sps_k_random=4,
                      bptt_custom_function=custom_fn,
                      price_formation="excess_demand", price_formation_kwargs=kwargs)
    sim = EcoMDSimulator(cfg)
    gen = torch.Generator(); gen.manual_seed(seed)
    s = sim.init_state(generator=gen)
    _, _, traj, _ = sim.rollout_chunk(s, s.detach().clone(), sim.init_price(),
                                      n_steps=n_steps, generator=gen, create_graph=True)
    return sim, traj


@pytest.mark.parametrize("custom_fn", [False, True])
def test_grad_to_zeta_and_delta(custom_fn):
    sim, traj = _sim({"het_mass_enabled": True, "mass_zeta_init": 1.8,
                      "impact_concave_enabled": True, "impact_delta_init": 0.6},
                     custom_fn=custom_fn)
    pf = sim.price_formation
    assert pf.mass_log_zeta.requires_grad and pf.impact_logit_delta.requires_grad
    traj.log_returns.pow(2).sum().backward()
    assert pf.mass_log_zeta.grad is not None and pf.mass_log_zeta.grad.abs().item() > 0
    assert pf.impact_logit_delta.grad is not None and pf.impact_logit_delta.grad.abs().item() > 0
    assert torch.isfinite(traj.log_returns).all()


@pytest.mark.parametrize("kwargs", [
    {"het_mass_enabled": True, "mass_zeta_init": 1.2},
    {"impact_concave_enabled": True, "impact_delta_init": 0.5},
    {"het_mass_enabled": True, "impact_concave_enabled": True},
])
def test_no_nan_over_rollout(kwargs):
    _, traj = _sim(kwargs, custom_fn=False, n_steps=10)
    assert torch.isfinite(traj.log_returns).all()


def test_fixed_zeta_not_learnable():
    p = ExcessDemandParams(het_mass_enabled=True, mass_zeta_learnable=False,
                           impact_concave_enabled=True, impact_delta_learnable=False)
    price = ExcessDemandPrice(p)
    assert not price.mass_log_zeta.requires_grad
    assert not price.impact_logit_delta.requires_grad
    # ζ value preserved
    assert math.isclose(float(torch.exp(price.mass_log_zeta)), p.mass_zeta_init, rel_tol=1e-5)
