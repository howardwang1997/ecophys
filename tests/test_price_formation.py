"""Tests for price-formation mechanisms."""

from __future__ import annotations

import pytest
import torch

from ecomd.models.price_formation import (
    ExcessDemandParams,
    ExcessDemandPrice,
    PriceFormation,
    ReadoutPrice,
    build_price_formation,
)


def _state(n: int, d: int, seed: int = 0) -> torch.Tensor:
    g = torch.Generator().manual_seed(seed)
    return torch.randn((n, d), generator=g) * 0.1


# ── ExcessDemandPrice ───────────────────────────────────────────────────────


def test_excess_demand_context_dim():
    pf = ExcessDemandPrice()
    assert pf.context_dim == 3


def test_excess_demand_init_state():
    pf = ExcessDemandPrice(ExcessDemandParams(initial_log_price=1.5))
    st = pf.init_state(device=torch.device("cpu"), dtype=torch.float32)
    assert float(st.log_price) == pytest.approx(1.5)
    assert int(st.step) == 0


def test_excess_demand_step_shape():
    pf = ExcessDemandPrice()
    s_prev = _state(10, 8, seed=0)
    s_next = _state(10, 8, seed=1)
    st = pf.init_state(device=s_prev.device, dtype=s_prev.dtype)

    out = pf.step(st, s_prev, s_next, generator=torch.Generator().manual_seed(0))
    assert out.state.step == 1
    assert out.context.shape == (3,)
    assert "volume" in out.aux
    assert "excess_demand" in out.aux
    assert torch.isfinite(out.context).all()


def test_excess_demand_volume_is_total_absolute_dpos():
    pf = ExcessDemandPrice(ExcessDemandParams(sigma_price=0.0))  # no noise for determinism
    d = 4
    s_prev = torch.zeros(3, d)
    s_next = torch.tensor([[1.0, 0.0, 0.0, 0.0],
                           [-2.0, 0.0, 0.0, 0.0],
                           [0.5, 0.0, 0.0, 0.0]])
    st = pf.init_state(device=s_prev.device, dtype=s_prev.dtype)
    out = pf.step(st, s_prev, s_next, generator=torch.Generator().manual_seed(0))
    assert float(out.aux["volume"]) == pytest.approx(3.5, abs=1e-6)
    # ED is signed sum: 1 - 2 + 0.5 = -0.5
    assert float(out.aux["excess_demand"]) == pytest.approx(-0.5, abs=1e-6)


def test_excess_demand_noise_zero_is_deterministic():
    pf = ExcessDemandPrice(ExcessDemandParams(sigma_price=0.0))
    s_prev = _state(5, 4, seed=0)
    s_next = _state(5, 4, seed=2)
    st = pf.init_state(device=s_prev.device, dtype=s_prev.dtype)
    out1 = pf.step(st, s_prev, s_next, generator=torch.Generator().manual_seed(0))
    st2 = pf.init_state(device=s_prev.device, dtype=s_prev.dtype)
    out2 = pf.step(st2, s_prev, s_next, generator=torch.Generator().manual_seed(999))
    assert torch.allclose(out1.state.log_price, out2.state.log_price)


# ── ReadoutPrice ────────────────────────────────────────────────────────────


def test_readout_price_context_dim():
    pf = ReadoutPrice(d=8)
    assert pf.context_dim == 3


def test_readout_step_shape_and_finite():
    pf = ReadoutPrice(d=8)
    s_prev = _state(6, 8, seed=0)
    s_next = _state(6, 8, seed=1)
    st = pf.init_state(device=s_prev.device, dtype=s_prev.dtype)
    out = pf.step(st, s_prev, s_next, generator=torch.Generator().manual_seed(0))
    assert out.context.shape == (3,)
    assert torch.isfinite(out.context).all()


# ── Registry ────────────────────────────────────────────────────────────────


def test_registry_excess_demand():
    pf: PriceFormation = build_price_formation("excess_demand", d=16)
    assert isinstance(pf, ExcessDemandPrice)


def test_registry_readout():
    pf: PriceFormation = build_price_formation("readout", d=16)
    assert isinstance(pf, ReadoutPrice)


def test_registry_unknown():
    with pytest.raises(ValueError):
        build_price_formation("nonsense", d=4)


# ── v0.6: learnable β ───────────────────────────────────────────────────────


def test_excess_demand_learnable_beta_has_params():
    pf = ExcessDemandPrice(ExcessDemandParams(learnable_beta=True))
    params = list(pf.parameters())
    assert len(params) >= 2  # at least one Linear's weight+bias


def test_excess_demand_learnable_beta_starts_near_base():
    """At initialization, β_net outputs ≈ 0 → factor ≈ 1 → β_eff ≈ β_base."""
    torch.manual_seed(0)
    pf = ExcessDemandPrice(ExcessDemandParams(beta=0.3, learnable_beta=True))
    st = pf.init_state(device=torch.device("cpu"), dtype=torch.float32)
    beta = pf._effective_beta(st)
    assert abs(float(beta.detach()) - 0.3) < 0.1


def test_excess_demand_learnable_beta_backprops():
    """β-net must receive gradient so it can learn regime-dependent response."""
    torch.manual_seed(0)
    pf = ExcessDemandPrice(ExcessDemandParams(beta=0.5, learnable_beta=True))
    s_prev = _state(5, 4, seed=0)
    s_next = _state(5, 4, seed=1) + 0.05  # nonzero ΔPos
    st = pf.init_state(device=s_prev.device, dtype=s_prev.dtype)
    out = pf.step(st, s_prev, s_next, generator=torch.Generator().manual_seed(0))
    out.state.log_price.backward()
    has_grad = any(p.grad is not None and torch.isfinite(p.grad).all()
                   for p in pf.beta_net.parameters())
    assert has_grad


def test_excess_demand_constant_beta_has_no_beta_net():
    pf = ExcessDemandPrice(ExcessDemandParams(learnable_beta=False))
    assert pf.beta_net is None


def test_excess_demand_aux_reports_beta_eff():
    pf = ExcessDemandPrice(ExcessDemandParams(beta=0.5, learnable_beta=True))
    s_prev = _state(4, 3, seed=0)
    s_next = _state(4, 3, seed=1)
    st = pf.init_state(device=s_prev.device, dtype=s_prev.dtype)
    out = pf.step(st, s_prev, s_next, generator=torch.Generator().manual_seed(0))
    assert "beta_eff" in out.aux
    assert torch.isfinite(out.aux["beta_eff"])
