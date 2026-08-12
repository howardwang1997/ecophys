"""Tests for BPTT gradient checkpointing in `rollout_chunk`.

The make-or-break test is :func:`test_gradient_equivalence_K8_vs_no_ckpt` —
it verifies that running with `bptt_checkpoint_every=K` produces gradients
indistinguishable (up to fp32 noise) from the non-checkpointed path.

Without these tests passing, we cannot trust ablation results that use
checkpointing for memory.
"""

from __future__ import annotations

import pytest
import torch

from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator


def _build_two_simulators(cfg_kwargs: dict, K: int) -> tuple[EcoMDSimulator, EcoMDSimulator]:
    """Build two identically-initialised simulators differing only in
    ``bptt_checkpoint_every`` (0 vs K).

    Identical init relies on torch.manual_seed before each construction.
    """
    torch.manual_seed(123)
    sim_no_ckpt = EcoMDSimulator(EcoMDConfig(bptt_checkpoint_every=0, **cfg_kwargs))
    torch.manual_seed(123)
    sim_ckpt = EcoMDSimulator(EcoMDConfig(bptt_checkpoint_every=K, **cfg_kwargs))

    # Sanity: same param values
    for p1, p2 in zip(sim_no_ckpt.parameters(), sim_ckpt.parameters()):
        assert torch.equal(p1.data, p2.data), "simulators must start identical"
    return sim_no_ckpt, sim_ckpt


def _rollout_and_backward(
    sim: EcoMDSimulator,
    *,
    n_steps: int,
    seed: int,
    n_agents: int,
    d_state: int,
) -> dict[str, torch.Tensor]:
    """Run one rollout + backward; return dict of param.name → grad.clone()."""
    sim.zero_grad(set_to_none=True)
    gen = torch.Generator().manual_seed(seed)
    init_gen = torch.Generator().manual_seed(seed + 999)
    s = sim.init_state(generator=init_gen)
    s_prev = s.detach().clone()
    price_state = sim.init_price()
    _, _, traj, _ = sim.rollout_chunk(
        s, s_prev, price_state,
        n_steps=n_steps, generator=gen, create_graph=True,
    )
    # Loss touching multiple traj fields (states + log_returns + velocities)
    # so gradients flow through everything.
    loss = (
        traj.log_returns.pow(2).mean()
        + 0.1 * traj.states.pow(2).mean()
        + 0.01 * traj.velocities.pow(2).mean()
    )
    loss.backward()
    grads = {}
    for name, p in sim.named_parameters():
        if p.grad is not None:
            grads[name] = p.grad.detach().clone()
    return grads


def test_gradient_equivalence_K8_vs_no_ckpt():
    """The critical test. K=8 grouped checkpoint must produce gradients
    matching the no-checkpoint version up to fp32 noise."""
    cfg = dict(
        n_agents=20,
        d_state=8,
        hidden=16,
        dt=0.01,
        gamma_init=1.0,
        temperature_init=0.05,
        # avoid high-cost components for this test
        pairwise_kind="mlp",
    )
    K = 8
    sim_a, sim_b = _build_two_simulators(cfg, K)

    grads_a = _rollout_and_backward(sim_a, n_steps=24, seed=7,
                                    n_agents=cfg["n_agents"], d_state=cfg["d_state"])
    grads_b = _rollout_and_backward(sim_b, n_steps=24, seed=7,
                                    n_agents=cfg["n_agents"], d_state=cfg["d_state"])

    assert set(grads_a.keys()) == set(grads_b.keys()), (
        "param sets must match"
    )
    max_abs_diff = 0.0
    max_rel_diff = 0.0
    worst_param = ""
    for name in grads_a:
        ga, gb = grads_a[name], grads_b[name]
        assert ga.shape == gb.shape, name
        abs_diff = (ga - gb).abs().max().item()
        denom = ga.abs().max().item() + 1e-8
        rel_diff = abs_diff / denom
        if rel_diff > max_rel_diff:
            max_rel_diff = rel_diff
            max_abs_diff = abs_diff
            worst_param = name
    print(f"\n  worst param: {worst_param}")
    print(f"  max_abs_diff: {max_abs_diff:.3e}")
    print(f"  max_rel_diff: {max_rel_diff:.3e}")
    # fp32 noise budget: 1e-4 relative is generous for a 24-step chain
    assert max_rel_diff < 1e-4, (
        f"gradient mismatch too large at param {worst_param!r}: "
        f"abs={max_abs_diff:.3e} rel={max_rel_diff:.3e}"
    )


def test_gradient_equivalence_K1_per_step():
    """K=1 (per-step checkpoint) must also match no-checkpoint."""
    cfg = dict(n_agents=15, d_state=6, hidden=12, pairwise_kind="mlp")
    sim_a, sim_b = _build_two_simulators(cfg, K=1)

    grads_a = _rollout_and_backward(sim_a, n_steps=12, seed=3,
                                    n_agents=cfg["n_agents"], d_state=cfg["d_state"])
    grads_b = _rollout_and_backward(sim_b, n_steps=12, seed=3,
                                    n_agents=cfg["n_agents"], d_state=cfg["d_state"])

    for name in grads_a:
        ga, gb = grads_a[name], grads_b[name]
        denom = ga.abs().max().item() + 1e-8
        rel = (ga - gb).abs().max().item() / denom
        assert rel < 1e-4, f"{name}: rel diff {rel:.3e}"


def test_rng_determinism_under_checkpoint():
    """Running rollout twice with K=8 from same seed must produce identical
    log_returns. Confirms manual generator save/restore is correct."""
    cfg = EcoMDConfig(n_agents=12, d_state=6, hidden=8, bptt_checkpoint_every=8,
                      pairwise_kind="mlp")
    torch.manual_seed(0)
    sim = EcoMDSimulator(cfg)

    def _one_rollout():
        gen = torch.Generator().manual_seed(11)
        init_gen = torch.Generator().manual_seed(22)
        s = sim.init_state(generator=init_gen)
        s_prev = s.detach().clone()
        price_state = sim.init_price()
        _, _, traj, _ = sim.rollout_chunk(
            s, s_prev, price_state,
            n_steps=24, generator=gen, create_graph=True,
        )
        return traj.log_returns.detach().clone()

    lr1 = _one_rollout()
    lr2 = _one_rollout()
    assert torch.equal(lr1, lr2), (
        f"checkpointed rollouts not bit-equal across calls; "
        f"max diff = {(lr1 - lr2).abs().max().item():.3e}"
    )


def test_hawkes_path_under_checkpoint():
    """When the price formation has Hawkes memory enabled, checkpointing
    must still produce equivalent gradients (covers `has_hawkes=True` path)."""
    pf_kwargs = dict(
        beta=0.02, kappa=0.5, sigma_price=0.005, ewma_alpha=0.05,
        hawkes_alpha=0.1, hawkes_kappa=0.3,
    )
    cfg_kw = dict(
        n_agents=12, d_state=6, hidden=8, dt=0.01,
        pairwise_kind="mlp",
        price_formation="excess_demand",
        price_formation_kwargs=pf_kwargs,
    )
    sim_a, sim_b = _build_two_simulators(cfg_kw, K=4)
    grads_a = _rollout_and_backward(sim_a, n_steps=12, seed=5,
                                    n_agents=12, d_state=6)
    grads_b = _rollout_and_backward(sim_b, n_steps=12, seed=5,
                                    n_agents=12, d_state=6)
    for name in grads_a:
        rel = (grads_a[name] - grads_b[name]).abs().max().item() / (
            grads_a[name].abs().max().item() + 1e-8
        )
        assert rel < 1e-4, f"hawkes path mismatch at {name}: rel={rel:.3e}"


@pytest.mark.slow
def test_chunk_64_runs_under_checkpoint():
    """Sanity: a 64-step checkpointed chunk completes at CI-scale N."""
    cfg = EcoMDConfig(
        n_agents=64, d_state=16, hidden=24,
        pairwise_kind="mlp",
        bptt_checkpoint_every=8,
    )
    sim = EcoMDSimulator(cfg)
    gen = torch.Generator().manual_seed(0)
    init_gen = torch.Generator().manual_seed(1)
    s = sim.init_state(generator=init_gen)
    s_prev = s.detach().clone()
    price_state = sim.init_price()
    _, _, traj, _ = sim.rollout_chunk(
        s, s_prev, price_state,
        n_steps=64, generator=gen, create_graph=True,
    )
    assert traj.log_returns.shape[0] == 64
    loss = traj.log_returns.pow(2).mean()
    loss.backward()  # exercises the checkpointed backward path
    # Ensure at least one parameter's grad is finite
    found = False
    for p in sim.parameters():
        if p.grad is not None and torch.isfinite(p.grad).all():
            found = True
            break
    assert found
