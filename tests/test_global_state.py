"""Smoke + gradient-flow tests for Tier 4.1 (MEGNet-style global state).

Default-off equivalence is covered by ``test_arch_extensions``'s
baseline test — when ``global_state_enabled=False`` (default), the
simulator runs unchanged. These tests cover flag-on behaviour under
both BPTT paths and composition with other tiers.
"""

from __future__ import annotations

import pytest
import torch

from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator


def _run(cfg_kwargs: dict, *, custom_fn: bool, n_steps: int = 4) -> dict:
    base = dict(
        n_agents=20, d_state=8, hidden=16,
        pairwise_kind="stochastic_mlp", sps_k_random=4,
        bptt_custom_function=custom_fn,
    )
    base.update(cfg_kwargs)
    cfg = EcoMDConfig(**base)
    sim = EcoMDSimulator(cfg)
    gen = torch.Generator(); gen.manual_seed(0)
    s = sim.init_state(generator=gen)
    s_prev = s.detach().clone()
    ps = sim.init_price()
    _, _, traj, _ = sim.rollout_chunk(
        s, s_prev, ps, n_steps=n_steps, generator=gen, create_graph=True,
    )
    loss = traj.log_returns.pow(2).sum()
    loss.backward()
    n_grad = sum(1 for p in sim.parameters()
                 if p.requires_grad and p.grad is not None and p.grad.abs().sum() > 0)
    n_total = sum(1 for p in sim.parameters() if p.requires_grad)
    return dict(loss=loss.item(), n_grad=n_grad, n_total=n_total)


@pytest.mark.parametrize("custom_fn", [False, True])
def test_tier_4_1_global_state_alone(custom_fn):
    out = _run(
        dict(global_state_enabled=True, global_state_d=8, global_state_into_pair=True),
        custom_fn=custom_fn,
    )
    assert out["loss"] > 0
    # Need to see global_state params (proj + GRU + cell biases) get gradient,
    # plus pair MLP and external MLP. Demand at least 8 nonzero-grad params.
    assert out["n_grad"] >= 8


@pytest.mark.parametrize("custom_fn", [False, True])
def test_tier_4_1_external_only_no_pair_injection(custom_fn):
    """When global_state_into_pair=False, u still feeds external context."""
    out = _run(
        dict(global_state_enabled=True, global_state_d=8, global_state_into_pair=False),
        custom_fn=custom_fn,
    )
    assert out["loss"] > 0
    assert out["n_grad"] >= 8


def test_tier_4_1_with_isab_pair_kernel():
    out = _run(
        dict(
            pairwise_kind="isab", isab_m_inducing=8, isab_n_heads=2,
            global_state_enabled=True, global_state_d=8, global_state_into_pair=True,
        ),
        custom_fn=True,
    )
    assert out["loss"] > 0
    # ISAB params + global_state params should all get grad.
    assert out["n_grad"] >= 12


def test_tier_4_1_composes_with_agent_memory():
    """Tier 1.1 + 4.1 stacked: u also consumes ⟨h_agent⟩ as input."""
    out = _run(
        dict(
            agent_memory_enabled=True, agent_memory_d=8,
            global_state_enabled=True, global_state_d=8, global_state_into_pair=True,
        ),
        custom_fn=True,
    )
    assert out["loss"] > 0
    assert out["n_grad"] >= 12


def test_tier_4_1_default_off_equivalence():
    """Building a simulator with default config should match pre-Tier-4.1
    behaviour bit-for-bit (exercised by the existing test suite). Here we
    just sanity-check that the new flags default to False/0/etc."""
    cfg = EcoMDConfig()
    assert cfg.global_state_enabled is False
    assert cfg.global_state_d == 16
    assert cfg.global_state_update_every == 1
    assert cfg.global_state_into_pair is True


def test_tier_4_1_global_state_propagates_across_steps():
    """h_global at end of rollout must be different from initial zeros once
    the GRU has run for n_steps (otherwise the latent isn't doing anything)."""
    cfg = EcoMDConfig(
        n_agents=20, d_state=8, hidden=16,
        pairwise_kind="stochastic_mlp", sps_k_random=4,
        global_state_enabled=True, global_state_d=8, global_state_into_pair=True,
        bptt_custom_function=False,
    )
    sim = EcoMDSimulator(cfg)
    gen = torch.Generator(); gen.manual_seed(0)
    s = sim.init_state(generator=gen)
    s_prev = s.detach().clone()
    ps = sim.init_price()
    h_init = sim.init_global_state()
    assert h_init is not None
    assert torch.allclose(h_init, torch.zeros_like(h_init))

    # Walk a few steps and check h_global moved
    h_global = h_init
    for k in range(4):
        _, ps, _, _, _, h_global = sim.step(
            s, s_prev, ps, generator=gen, create_graph=False,
            h_global=h_global, step_idx=k,
        )
    assert not torch.allclose(h_global, h_init), "h_global must update over a rollout"
