"""L1-4 — ecomd_v2 SPS edge sampling bound to the rollout step generator.

Closes the honest RNG gap recorded in the D-1 simulator contracts
(papers/proposal/ecomd_reexploration_simulator_contracts_2026-09-06.md §2.4):
``TypedRelationalPotential._sample_edges`` drew ``torch.rand(n, n)`` from the
GLOBAL torch RNG, so byte-identical v2 rollout replay (gates G8/G9) rested on
an assumption about global-RNG consumption order. The fix mirrors the
``StochasticPairwisePotential`` ``_step_generator`` precedent:
``EcoMDSimulator.step`` binds the rollout's seeded generator onto the v2
relational module; with a generator set the SPS path consumes ZERO global RNG;
with None it falls back to the global RNG (same law — different source).

Verified here:
(a) same rollout seed -> byte-identical v2 trajectories, twice on one
    simulator and across two identically-constructed simulators;
(b) rollouts are unaffected by prior perturbation of the global torch RNG
    state, and the global RNG state is bit-unchanged across a seeded rollout
    (zero global-RNG consumption in the path);
(c) different rollout seeds -> different edge draws and trajectories;
(d) legacy fallback: with no generator bound, edge sampling still consumes
    the global RNG (direct ``EcoMDv2Potential``/``_sample_edges`` callers
    keep their pre-L1-4 behavior);
(e) the edge-sampling law is unchanged under the generator source (uniform
    partner distribution, self excluded).
"""

from __future__ import annotations

import pytest
import torch

from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator
from ecomd.models.ecomd_v2 import (
    EcoMDv2Config,
    EcoMDv2Potential,
    TypedRelationalPotential,
    _sample_edges,
)

# ─── Helpers ────────────────────────────────────────────────────────────────


def _make_sim(init_seed: int = 0) -> EcoMDSimulator:
    """Small ecomd_v2 simulator with deterministic parameter init."""
    torch.manual_seed(init_seed)  # parameter init only; rollouts use their own seed
    cfg = EcoMDConfig(
        n_agents=12, d_state=6, hidden=16,
        pairwise_kind="ecomd_v2",
        v2_k_types=3, v2_d_type_emb=4, v2_k_random=5,
        v2_gauge_enforce=False,  # production default
    )
    sim = EcoMDSimulator(cfg)
    sim.eval()
    return sim


def _bytes(t: torch.Tensor) -> bytes:
    return t.detach().cpu().contiguous().numpy().tobytes()


def _perturb_global_rng(seed: int, n: int) -> None:
    torch.manual_seed(seed)
    torch.rand(n)
    torch.randn(n)


# ─── (a) same seed -> byte-identical rollout ────────────────────────────────


def test_same_seed_byte_identical_rollout_on_one_simulator():
    sim = _make_sim()
    traj_a = sim.run(n_steps=6, seed=123)
    traj_b = sim.run(n_steps=6, seed=123)
    assert _bytes(traj_a.log_returns) == _bytes(traj_b.log_returns)
    assert _bytes(traj_a.log_prices) == _bytes(traj_b.log_prices)
    assert _bytes(traj_a.states) == _bytes(traj_b.states)


def test_same_seed_byte_identical_across_identically_constructed_simulators():
    traj_a = _make_sim(init_seed=7).run(n_steps=6, seed=123)
    traj_b = _make_sim(init_seed=7).run(n_steps=6, seed=123)
    assert _bytes(traj_a.log_returns) == _bytes(traj_b.log_returns)
    assert _bytes(traj_a.states) == _bytes(traj_b.states)


# ─── (b) independence from the global RNG state ─────────────────────────────


def test_rollout_unaffected_by_prior_global_rng_perturbation():
    sim = _make_sim()
    _perturb_global_rng(seed=11, n=23)
    traj_a = sim.run(n_steps=6, seed=123)
    _perturb_global_rng(seed=999, n=17)
    traj_b = sim.run(n_steps=6, seed=123)
    assert _bytes(traj_a.log_returns) == _bytes(traj_b.log_returns)
    assert _bytes(traj_a.states) == _bytes(traj_b.states)


def test_seeded_rollout_consumes_zero_global_rng():
    sim = _make_sim()
    torch.manual_seed(5)
    state_before = torch.get_rng_state()
    sim.run(n_steps=6, seed=123)
    assert torch.equal(torch.get_rng_state(), state_before), (
        "seeded ecomd_v2 rollout consumed the global torch RNG "
        "(SPS edge sampling must draw from the rollout generator)"
    )


# ─── (c) different seeds -> different draws ─────────────────────────────────


def test_different_seeds_give_different_trajectories():
    sim = _make_sim()
    traj_a = sim.run(n_steps=6, seed=123)
    traj_b = sim.run(n_steps=6, seed=124)
    assert _bytes(traj_a.log_returns) != _bytes(traj_b.log_returns)


def test_different_seeds_give_different_edge_draws():
    gen_a = torch.Generator().manual_seed(1)
    gen_b = torch.Generator().manual_seed(2)
    edges_a = _sample_edges(12, 5, torch.device("cpu"), generator=gen_a)
    edges_b = _sample_edges(12, 5, torch.device("cpu"), generator=gen_b)
    assert not torch.equal(edges_a, edges_b)


# ─── (d) legacy fallback: no generator -> global RNG ────────────────────────


def test_unbound_sampler_falls_back_to_global_rng():
    rel = TypedRelationalPotential(
        d_state=6, k_types=3, d_type_emb=4, hidden=16, k_random=5,
    )
    assert rel._step_generator is None
    torch.manual_seed(5)
    state_before = torch.get_rng_state()
    edges_a = _sample_edges(12, 5, torch.device("cpu"))
    assert not torch.equal(torch.get_rng_state(), state_before), (
        "generatorless fallback must consume the global RNG (pre-L1-4 behavior)"
    )
    torch.manual_seed(5)
    edges_b = _sample_edges(12, 5, torch.device("cpu"))
    assert torch.equal(edges_a, edges_b)


def test_direct_potential_call_with_generator_reproducible_and_global_free():
    cfg = EcoMDv2Config(d_state=6, hidden=16, k_types=3, d_type_emb=4, k_random=5)
    type_gen = torch.Generator().manual_seed(0)
    pot = EcoMDv2Potential(n_agents=12, config=cfg, type_gen=type_gen)
    torch.manual_seed(0)
    s = torch.randn(12, 6) * 0.3

    torch.manual_seed(77)
    global_before = torch.get_rng_state()
    gen = torch.Generator().manual_seed(9)
    pot.rel._step_generator = gen
    v_a = pot(s).item()
    assert torch.equal(torch.get_rng_state(), global_before), (
        "bound potential consumed the global RNG"
    )

    gen2 = torch.Generator().manual_seed(9)
    pot.rel._step_generator = gen2
    v_b = pot(s).item()
    assert v_a == v_b, "same step-generator seed must reproduce V exactly"

    gen3 = torch.Generator().manual_seed(10)
    pot.rel._step_generator = gen3
    v_c = pot(s).item()
    assert v_a != v_c, "different step-generator seed should change the sampled edges"


def test_step_binds_rollout_generator_to_relational_module():
    sim = _make_sim()
    gen = torch.Generator().manual_seed(3)
    s = sim.init_state(generator=gen)
    price_state = sim.init_price()
    sim.step(s, s.detach().clone(), price_state, generator=gen, create_graph=False)
    rel = sim.potential.pairwise.rel
    assert isinstance(rel, TypedRelationalPotential)
    assert rel._step_generator is gen


# ─── (e) same law: uniform partner distribution under the generator ────────


def test_edge_law_unchanged_under_generator_source():
    n, k = 12, 3
    counts = torch.zeros(n, n, dtype=torch.long)
    n_draws = 200
    for seed in range(n_draws):
        gen = torch.Generator().manual_seed(seed)
        edges = _sample_edges(n, k, torch.device("cpu"), generator=gen)
        for src, dst in edges.t().tolist():
            counts[src, dst] += 1
    expected = n_draws * k / (n - 1)
    for i in range(n):
        assert counts[i, i] == 0, "self-edge sampled"
        others = torch.cat([counts[i, :i], counts[i, i + 1:]])
        assert others.min() >= 0.5 * expected, (
            f"partner law skewed low for agent {i}: min {others.min()} < {0.5 * expected}"
        )
        assert others.max() <= 1.5 * expected, (
            f"partner law skewed high for agent {i}: max {others.max()} > {1.5 * expected}"
        )


@pytest.mark.parametrize("k_random", [3, 5, 11])
def test_edges_shape_and_no_self_loops(k_random):
    gen = torch.Generator().manual_seed(0)
    n = 12
    edges = _sample_edges(n, k_random, torch.device("cpu"), generator=gen)
    k_eff = min(k_random, n - 1)
    assert edges.shape == (2, n * k_eff)
    assert (edges[0] != edges[1]).all()
