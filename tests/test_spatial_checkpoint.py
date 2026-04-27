"""Tests for spatial-checkpoint sharding in StochasticPairwisePotential.

The make-or-break test is :func:`test_gradient_equivalence_B_vs_no_batch`
— spatial batching with `torch.utils.checkpoint` per batch must produce
gradients indistinguishable from the no-batch path up to fp32 noise.

Spatial sharding doesn't necessarily fix the BPTT memory problem (which
is rooted in `create_graph=True` pinning V-graphs across steps), but it
DOES reduce per-step pairwise forward memory and is a useful complement.
"""

from __future__ import annotations

import torch

from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator
from ecomd.models.potentials import StochasticPairwisePotential


def _build_two_potentials(d: int, hidden: int, k: int, B: int) -> tuple[
    StochasticPairwisePotential, StochasticPairwisePotential
]:
    torch.manual_seed(7)
    p_no = StochasticPairwisePotential(d=d, hidden=hidden, k_random=k,
                                       resample_per_step=False,
                                       spatial_batch_size=0)
    torch.manual_seed(7)
    p_yes = StochasticPairwisePotential(d=d, hidden=hidden, k_random=k,
                                        resample_per_step=False,
                                        spatial_batch_size=B)
    # Sanity: same params at init
    for a, b in zip(p_no.parameters(), p_yes.parameters()):
        assert torch.equal(a, b)
    return p_no, p_yes


def _force_same_edges(p_no, p_yes, n: int, device: torch.device, seed: int = 999):
    """Both potentials use resample_per_step=False; pre-populate their
    edge caches from the same RNG state so they sample identically."""
    torch.manual_seed(seed)
    edges = p_no._sample_edges(n, device).detach()
    p_no._cached_edges = edges
    p_yes._cached_edges = edges.clone()


def test_gradient_equivalence_B_vs_no_batch():
    """Spatial-batched output and gradients must match no-batch."""
    n, d, hidden, k = 80, 6, 8, 12
    B = 100  # → ~10 spatial batches at E = 80 * 12 = 960
    p_no, p_yes = _build_two_potentials(d, hidden, k, B)
    _force_same_edges(p_no, p_yes, n, device=torch.device("cpu"))

    torch.manual_seed(99)
    s = torch.randn(n, d, requires_grad=True)
    s_clone = s.detach().clone().requires_grad_(True)

    V_no = p_no(s)
    V_yes = p_yes(s_clone)

    # Forward values must match
    assert torch.allclose(V_no, V_yes, rtol=1e-5, atol=1e-6), \
        f"V mismatch: V_no={V_no.item()}, V_yes={V_yes.item()}"

    # Backward gradients to s and to params must match
    V_no.backward()
    V_yes.backward()

    # s grads
    g_no = s.grad
    g_yes = s_clone.grad
    rel = (g_no - g_yes).abs().max().item() / (g_no.abs().max().item() + 1e-8)
    assert rel < 1e-5, f"∂V/∂s rel diff = {rel}"

    # param grads
    for (n1, p1), (n2, p2) in zip(p_no.named_parameters(), p_yes.named_parameters()):
        assert n1 == n2
        ga = p1.grad
        gb = p2.grad
        if ga is None and gb is None:
            continue
        rel = (ga - gb).abs().max().item() / (ga.abs().max().item() + 1e-8)
        assert rel < 1e-5, f"param {n1} rel diff = {rel}"


def test_create_graph_equivalence():
    """The conservative_forces use `create_graph=True`. Spatial batching
    must produce ∇V (= -f_cons) values identical to no-batch."""
    from ecomd.models.potentials import conservative_forces
    n, d, hidden, k = 60, 4, 8, 8
    B = 80  # → batches of 80 edges at E = 60*8 = 480
    p_no, p_yes = _build_two_potentials(d, hidden, k, B)
    _force_same_edges(p_no, p_yes, n, device=torch.device("cpu"))

    torch.manual_seed(5)
    s = torch.randn(n, d, requires_grad=True)
    s_clone = s.detach().clone().requires_grad_(True)

    f_no = conservative_forces(p_no, s, context=None, create_graph=True)
    f_yes = conservative_forces(p_yes, s_clone, context=None, create_graph=True)
    rel = (f_no - f_yes).abs().max().item() / (f_no.abs().max().item() + 1e-8)
    assert rel < 1e-5, f"f_cons rel diff = {rel}"

    # Now backward through f_cons (second-order grad to params)
    loss_no = (f_no ** 2).sum()
    loss_yes = (f_yes ** 2).sum()
    loss_no.backward()
    loss_yes.backward()
    for (n1, p1), (n2, p2) in zip(p_no.named_parameters(), p_yes.named_parameters()):
        if p1.grad is None and p2.grad is None:
            continue
        rel = (p1.grad - p2.grad).abs().max().item() / (p1.grad.abs().max().item() + 1e-8)
        assert rel < 1e-4, f"second-order grad on {n1} rel diff = {rel}"


def test_b_zero_is_passthrough():
    """B=0 should be identical to original (no checkpoint)."""
    p = StochasticPairwisePotential(d=8, hidden=8, k_random=8,
                                    resample_per_step=True,
                                    spatial_batch_size=0)
    assert p.spatial_batch_size == 0
    s = torch.randn(50, 8, requires_grad=True)
    V = p(s)
    V.backward()
    assert torch.isfinite(V).all()
    assert torch.isfinite(s.grad).all()


def test_simulator_wires_spatial_batch_size():
    """Verify EcoMDConfig.sps_spatial_batch_size flows to the potential."""
    cfg = EcoMDConfig(
        n_agents=20, d_state=4, hidden=4,
        pairwise_kind="stochastic_mlp",
        sps_k_random=4,
        sps_spatial_batch_size=24,
    )
    sim = EcoMDSimulator(cfg)
    pw = sim.potential.pairwise
    assert isinstance(pw, StochasticPairwisePotential)
    assert pw.spatial_batch_size == 24


def test_full_step_with_spatial_batch_grads():
    """Run a full sim step with spatial batching enabled — ensure
    end-to-end gradient flow works."""
    cfg = EcoMDConfig(
        n_agents=20, d_state=4, hidden=8,
        pairwise_kind="stochastic_mlp",
        sps_k_random=8,
        sps_spatial_batch_size=24,  # ~6 batches at E = 20*8 = 160
    )
    sim = EcoMDSimulator(cfg)
    gen = torch.Generator().manual_seed(0)
    ig = torch.Generator().manual_seed(1)
    s = sim.init_state(generator=ig)
    s_prev = s.detach().clone()
    ps = sim.init_price()
    _, _, traj, _ = sim.rollout_chunk(s, s_prev, ps, n_steps=8,
                                      generator=gen, create_graph=True)
    loss = traj.log_returns.pow(2).mean()
    loss.backward()
    n_grad = sum(1 for p in sim.parameters()
                 if p.grad is not None and torch.isfinite(p.grad).all())
    n_total = sum(1 for p in sim.parameters() if p.requires_grad)
    assert n_grad >= n_total - 2, f"too few params got grad: {n_grad}/{n_total}"
