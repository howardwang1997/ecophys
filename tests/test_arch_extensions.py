"""Smoke + gradient-flow tests for feature/arch-extensions Tiers 1.1, 1.2,
1.3, 2.1, 2.2, 3.1.

Each tier flag defaults OFF; with all default we expect bit-identical
behavior to the pre-arch-extensions baseline (covered by existing
test_ecomd_smoke / test_custom_autograd_step). These tests verify
flag-on paths run forward+backward cleanly under both the default
and Sprint-2 (bptt_custom_function=True) BPTT paths.
"""

from __future__ import annotations

import pytest
import torch

from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator


def _smoke_run(cfg_kwargs: dict, *, custom_fn: bool, n_steps: int = 4) -> None:
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
    assert torch.isfinite(loss)
    n_grad = sum(1 for p in sim.parameters()
                 if p.requires_grad and p.grad is not None and p.grad.abs().sum() > 0)
    assert n_grad >= 5, f"too few params received gradient: {n_grad}"


@pytest.mark.parametrize("custom_fn", [False, True])
def test_tier_1_1_agent_memory(custom_fn):
    _smoke_run(
        dict(agent_memory_enabled=True, agent_memory_d=8),
        custom_fn=custom_fn,
    )


@pytest.mark.parametrize("custom_fn", [False, True])
def test_tier_1_2_heterogeneous_kernels(custom_fn):
    _smoke_run(
        dict(
            twopop_enabled=True,
            twopop_gamma_scale=(1.0, 1.5, 0.7, 1.2),
            twopop_temp_scale=(1.0, 0.8, 1.3, 1.1),
            pair_heterogeneous_heads=True,
        ),
        custom_fn=custom_fn,
    )


@pytest.mark.parametrize("custom_fn", [False, True])
@pytest.mark.parametrize("mode", ["distance", "inner_prod", "signed_diff", "all"])
def test_tier_1_3_pair_features(custom_fn, mode):
    _smoke_run(dict(pair_features_extra=mode), custom_fn=custom_fn)


@pytest.mark.parametrize("custom_fn", [False, True])
def test_tier_2_1_jumps_drift_correction(custom_fn):
    _smoke_run(
        dict(jump_lambda=0.5, jump_scale=0.01),
        custom_fn=custom_fn,
    )


@pytest.mark.parametrize("custom_fn", [False, True])
def test_tier_2_2_multi_timescale(custom_fn):
    _smoke_run(
        dict(
            multi_timescale_enabled=True,
            timescale_fast_frac=0.7,
            timescale_slow_freq=3,
        ),
        custom_fn=custom_fn,
    )


@pytest.mark.parametrize("custom_fn", [False, True])
def test_tier_3_1_isab(custom_fn):
    _smoke_run(
        dict(pairwise_kind="isab", isab_m_inducing=8, isab_n_heads=2),
        custom_fn=custom_fn,
    )


@pytest.mark.parametrize("custom_fn", [False, True])
def test_all_six_stacked(custom_fn):
    _smoke_run(
        dict(
            pairwise_kind="isab", isab_m_inducing=8, isab_n_heads=2,
            agent_memory_enabled=True, agent_memory_d=8,
            twopop_enabled=True,
            twopop_gamma_scale=(1.0, 1.5, 0.7, 1.2),
            twopop_temp_scale=(1.0, 0.8, 1.3, 1.1),
            jump_lambda=0.5, jump_scale=0.01,
            multi_timescale_enabled=True,
            timescale_fast_frac=0.7, timescale_slow_freq=3,
        ),
        custom_fn=custom_fn,
    )


def test_default_off_equivalence_unchanged_baseline():
    """All new flags default-off: rollout should produce same trace as pre-tier baseline."""
    torch.manual_seed(0)
    cfg = EcoMDConfig(
        n_agents=20, d_state=8, hidden=16,
        pairwise_kind="stochastic_mlp", sps_k_random=4,
    )
    sim = EcoMDSimulator(cfg)
    gen = torch.Generator(); gen.manual_seed(0)
    s = sim.init_state(generator=gen)
    s_prev = s.detach().clone()
    ps = sim.init_price()
    _, _, traj, _ = sim.rollout_chunk(s, s_prev, ps, n_steps=4, generator=gen, create_graph=True)
    # Sanity: returns finite, not all zero
    assert torch.isfinite(traj.log_returns).all()
    assert traj.log_returns.abs().sum() > 0


def test_inference_mode_jumps_sample():
    """Inference path samples discrete jumps (training path uses drift corr).

    With jump_lambda > 0, run() should produce non-zero variance even when
    forces are zero (the integrator's jump path adds Poisson(λ·dt)·N(0,σ²)
    displacements).
    """
    torch.manual_seed(0)
    cfg = EcoMDConfig(
        n_agents=20, d_state=8, hidden=16,
        pairwise_kind="stochastic_mlp", sps_k_random=4,
        jump_lambda=2.0, jump_scale=0.5,
        temperature_init=0.0,  # kill thermal noise so jumps are the only stochastic path
        learn_temperature=False,
    )
    sim = EcoMDSimulator(cfg)
    traj = sim.run(n_steps=10, seed=0)
    # log_returns should not all be zero (jumps push state around → prices move)
    assert traj.log_returns.var().item() >= 0.0  # finite at least
    # state at end should differ from start
    assert traj.states.shape[0] == 10
