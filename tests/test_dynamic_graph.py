"""Smoke + gradient-flow tests for Tier 4.2 (Gated Stochastic Pairwise).

Default-off: ``edge_gating_enabled=False`` ⟹ output bit-identical to
pre-Tier-4.2 baseline. Flag-on: per-edge gate w_ij = σ(g(s_i, s_j, u))
multiplies the pair kernel φ, rescaled by 1/gate_init_p so the
estimator stays approximately unbiased at init.
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
    gate_has_grad = any(
        name.startswith("potential.pairwise.gate_mlp")
        and p.grad is not None and p.grad.abs().sum() > 0
        for name, p in sim.named_parameters()
    )
    return dict(loss=loss.item(), n_grad=n_grad, n_total=n_total,
                gate_has_grad=gate_has_grad, sim=sim, traj=traj)


def test_default_off_equivalence():
    """edge_gating_enabled=False (default) ⟹ output unchanged from pre-4.2 baseline."""
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
    # Hardcoded reference value; re-pinned 2026-09-20 (PI-approved,
    # pi_battery_v3_dispositions_20260920) from 0.263843 after the L1-4 RNG
    # fix (commit 15e139928) invalidated the old constant — battery v3 record
    # section 2.1, papers/proposal/ecomd_reexploration_d0_regression_battery_2026-09-19.md.
    assert abs(traj.log_returns.sum().item() - 0.075823) < 1e-4


@pytest.mark.parametrize("custom_fn", [False, True])
def test_tier_4_2_alone(custom_fn):
    out = _run(
        dict(edge_gating_enabled=True, edge_gating_init_p=0.7, edge_gating_input_u=False),
        custom_fn=custom_fn,
    )
    assert out["loss"] > 0
    assert out["gate_has_grad"], "gate MLP must receive nonzero gradient"
    # Most params should get gradient (a couple may stay zero — e.g. first-layer
    # gate bias near init can have very small grad).
    assert out["n_grad"] >= out["n_total"] - 2


@pytest.mark.parametrize("custom_fn", [False, True])
def test_tier_4_2_composes_with_tier_4_1(custom_fn):
    out = _run(
        dict(
            edge_gating_enabled=True, edge_gating_init_p=0.7, edge_gating_input_u=True,
            global_state_enabled=True, global_state_d=8, global_state_into_pair=True,
        ),
        custom_fn=custom_fn,
    )
    assert out["loss"] > 0
    assert out["gate_has_grad"]
    # With gate seeing u, gradient should flow back through both gate_mlp
    # AND global_state.cell.
    has_global = any(
        name.startswith("global_state")
        and p.grad is not None and p.grad.abs().sum() > 0
        for name, p in out["sim"].named_parameters()
    )
    assert has_global, "global_state.cell must receive gradient when gate sees u"


def test_gate_input_u_false_isolates_pair_signal():
    """Even with global_state_enabled, when edge_gating_input_u=False the gate
    must not depend on u — useful as ablation."""
    out = _run(
        dict(
            edge_gating_enabled=True, edge_gating_init_p=0.7, edge_gating_input_u=False,
            global_state_enabled=True, global_state_d=8, global_state_into_pair=True,
        ),
        custom_fn=False,
    )
    sim = out["sim"]
    # gate_mlp's first linear should have input dim = 3*d (no u)
    pw = sim.potential.pairwise
    assert pw.gate_mlp[0].in_features == 3 * pw.d


def test_init_close_to_baseline_at_zero_grad():
    """At step 0, with init bias = logit(0.7), σ ≈ 0.7 and rescale 1/0.7
    ⟹ V_with_gate ≈ V_without_gate. Verify within tolerance over a 1-step
    rollout (variance is large; we just check magnitudes are comparable)."""
    torch.manual_seed(0)
    cfg_off = EcoMDConfig(
        n_agents=20, d_state=8, hidden=16,
        pairwise_kind="stochastic_mlp", sps_k_random=4,
    )
    sim_off = EcoMDSimulator(cfg_off)

    torch.manual_seed(0)
    cfg_on = EcoMDConfig(
        n_agents=20, d_state=8, hidden=16,
        pairwise_kind="stochastic_mlp", sps_k_random=4,
        edge_gating_enabled=True, edge_gating_init_p=0.7,
    )
    sim_on = EcoMDSimulator(cfg_on)

    # Force same agent states + prices.
    g = torch.Generator(); g.manual_seed(0)
    s = torch.randn(20, 8, generator=g) * 0.1

    # Compute V from both at the same s. Expect the gated V's magnitude
    # to be within an order of magnitude of the ungated V (rescale keeps
    # them on the same scale at init).
    g.manual_seed(0)
    sim_off.potential.pairwise._sample_edges_gen = g
    g2 = torch.Generator(); g2.manual_seed(0)

    v_off = sim_off.potential.pairwise(s).item()
    # Reset edge cache + use same seed for on
    sim_on.potential.pairwise.reset_edge_cache()
    v_on = sim_on.potential.pairwise(s).item()
    # Magnitudes comparable: |log(v_on/v_off)| < log(5) at init.
    if abs(v_off) > 1e-6:
        ratio = abs(v_on / v_off)
        assert 0.2 < ratio < 5.0, f"V ratio {ratio} outside reasonable range at init"


def test_default_flags():
    cfg = EcoMDConfig()
    assert cfg.edge_gating_enabled is False
    assert cfg.edge_gating_init_p == 0.7
    assert cfg.edge_gating_input_u is True
