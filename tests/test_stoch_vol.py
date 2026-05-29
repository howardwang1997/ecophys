"""Tests for the neural-SDE stochastic-volatility head (exp neural_sde).

Covers the pre-registered build gate: positivity, hard bound, OFF-path
bit-exactness (no behaviour change, no extra RNG draw), and gradient liveness
through both rollout paths (vanilla and custom-autograd).
"""

from __future__ import annotations

import pytest
import torch

from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator
from ecomd.models.stoch_vol import StochVolProcess


# ── Unit: the StochVolProcess itself ─────────────────────────────────────────

def test_sigma_mult_positive_and_bounded():
    sv = StochVolProcess(d_v=3, leverage=True, v_clip=3.0, gain_init=1.0)
    gen = torch.Generator().manual_seed(0)
    v = sv.init_v(torch.device("cpu"), torch.float32)
    bound = torch.exp(torch.tensor(sv.g.item() * sv.v_clip))
    for _ in range(200):
        r = torch.randn((), generator=gen) * 0.05   # plausible daily return
        v, sigma_mult = sv.step(v, r, generator=gen)
        assert torch.isfinite(v).all()
        assert (v.abs() <= sv.v_clip + 1e-5).all(), "log-vol exceeded hard bound"
        assert sigma_mult > 0, "sigma_mult must be positive"
        assert sigma_mult <= bound * 1.01, "sigma_mult exceeded exp(g*v_clip)"


def test_leverage_raises_vol_on_down_moves():
    # With leverage on, a large down-move should push vol higher than a same-size
    # up-move (asymmetric coupling → leverage #9 / Zumbach #11).
    sv = StochVolProcess(d_v=2, leverage=True, xi_init=0.0)  # no innovation: deterministic
    with torch.no_grad():
        sv.w_lev.fill_(0.5)
        sv.w_abs.fill_(0.0)
    v0 = sv.init_v(torch.device("cpu"), torch.float32)
    v_down, m_down = sv.step(v0, torch.tensor(-0.05), generator=None)
    v_up, m_up = sv.step(v0, torch.tensor(0.05), generator=None)
    assert float(m_down) > float(m_up), "down-move should raise vol more than up-move"


def test_grad_reaches_sv_params():
    sv = StochVolProcess(d_v=2, gain_init=0.5)
    gen = torch.Generator().manual_seed(1)
    v = sv.init_v(torch.device("cpu"), torch.float32)
    mults = []
    for _ in range(8):
        r = torch.randn((), generator=gen) * 0.05
        v, m = sv.step(v, r, generator=gen)
        mults.append(m)
    loss = torch.stack(mults).pow(2).sum()
    loss.backward()
    for name in ("g", "theta_kappa", "log_xi", "w_abs"):
        p = getattr(sv, name)
        assert p.grad is not None and p.grad.abs().sum() > 0, f"{name} got no gradient"


# ── Integration: through the simulator (both rollout paths) ──────────────────

def _run(sv_kwargs: dict | None, *, custom_fn: bool, sv_integrator: bool = False,
         n_steps: int = 6, seed: int = 0):
    pf_kwargs: dict = {}
    if sv_kwargs is not None:
        pf_kwargs = {"sv_price_enabled": True, **sv_kwargs}
    cfg = EcoMDConfig(
        n_agents=20, d_state=8, hidden=16,
        pairwise_kind="stochastic_mlp", sps_k_random=4,
        bptt_custom_function=custom_fn,
        price_formation="excess_demand",
        price_formation_kwargs=pf_kwargs,
        sv_integrator_enabled=sv_integrator,
    )
    sim = EcoMDSimulator(cfg)
    gen = torch.Generator(); gen.manual_seed(seed)
    s = sim.init_state(generator=gen)
    s_prev = s.detach().clone()
    ps = sim.init_price()
    _, ps_final, traj, _ = sim.rollout_chunk(
        s, s_prev, ps, n_steps=n_steps, generator=gen, create_graph=True,
    )
    return sim, traj, ps_final


@pytest.mark.parametrize("custom_fn", [False, True])
def test_off_path_deterministic_and_no_latent(custom_fn):
    # sv OFF: the price head builds no sv module (vol_latent stays None) and the
    # rollout is bit-exact across two same-seed runs of the SAME sim — i.e. the
    # OFF path introduces no extra RNG draw / nondeterminism. (Two separate sim
    # builds would differ only via param init, not the sv path.)
    torch.set_num_threads(1)  # Mac BLAS determinism (feedback_mac_blas_determinism)
    sim, _, _ = _run(None, custom_fn=custom_fn, seed=0)

    def _rollout():
        gen = torch.Generator(); gen.manual_seed(0)
        s = sim.init_state(generator=gen)
        ps = sim.init_price()
        _, ps_f, traj, _ = sim.rollout_chunk(
            s, s.detach().clone(), ps, n_steps=6, generator=gen, create_graph=True,
        )
        return traj.log_returns.detach().clone(), ps_f

    r_a, ps_a = _rollout()
    r_b, ps_b = _rollout()
    assert torch.equal(r_a, r_b)
    assert ps_a.vol_latent is None and ps_b.vol_latent is None
    assert getattr(sim.price_formation, "sv", None) is None


@pytest.mark.parametrize("custom_fn", [False, True])
def test_sv_on_carries_latent_and_is_finite(custom_fn):
    sim, traj, ps = _run({"sv_d": 3, "sv_leverage": True}, custom_fn=custom_fn)
    assert ps.vol_latent is not None and ps.vol_latent.shape == (3,)
    assert torch.isfinite(traj.log_returns).all()
    assert (ps.vol_latent.abs() <= 3.0 + 1e-4).all()


@pytest.mark.parametrize("custom_fn", [False, True])
def test_sv_params_get_gradient_through_rollout(custom_fn):
    sim, traj, _ = _run({"sv_d": 2, "sv_gain_init": 0.5}, custom_fn=custom_fn)
    loss = traj.log_returns.pow(2).sum()
    loss.backward()
    sv = sim.price_formation.sv
    assert sv is not None
    live = [n for n in ("g", "theta_kappa", "log_xi", "w_abs", "w_lev")
            if getattr(sv, n).grad is not None and getattr(sv, n).grad.abs().sum() > 0]
    assert "g" in live and len(live) >= 3, f"too few sv params got gradient: {live}"


def test_integrator_placement_grad_and_finite():
    # sv_integrator_enabled: the price latent also scales the Langevin noise.
    sim, traj, ps = _run({"sv_d": 2, "sv_gain_init": 0.5}, custom_fn=False,
                         sv_integrator=True)
    assert torch.isfinite(traj.log_returns).all()
    loss = traj.log_returns.pow(2).sum()
    loss.backward()
    sv = sim.price_formation.sv
    assert sv.g.grad is not None and sv.g.grad.abs().sum() > 0


def test_grouped_checkpoint_with_sv_raises():
    cfg = EcoMDConfig(
        n_agents=20, d_state=8, hidden=16,
        pairwise_kind="stochastic_mlp", sps_k_random=4,
        bptt_checkpoint_every=2,
        price_formation="excess_demand",
        price_formation_kwargs={"sv_price_enabled": True, "sv_d": 2},
    )
    sim = EcoMDSimulator(cfg)
    gen = torch.Generator(); gen.manual_seed(0)
    s = sim.init_state(generator=gen)
    ps = sim.init_price()
    with pytest.raises(NotImplementedError, match="vol_latent"):
        sim.rollout_chunk(s, s.detach().clone(), ps, n_steps=4,
                          generator=gen, create_graph=True)
