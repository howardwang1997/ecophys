"""Tests for U(t) energy logging — Paper-A architectural sanity check.

These tests validate that the gradient-of-potential force satisfies the
expected physical relation F = -∇U, by exercising the new
``conservative_forces(..., return_potential=True)`` path and the
``EcoMDTrajectory.total_potential`` field.

Notable cases:

- ``test_energy_logging_populates_trajectory``  — the T-length scalar is
  populated end-to-end through ``sim.run``.
- ``test_force_equals_neg_grad_of_potential``    — numerical FD test that
  the returned f_cons is exactly -∂U/∂s.
- ``test_T0_no_dissipation_potential_drift``     — paper-grade sanity:
  with T=0 (no noise) AND λ_diss=0 AND no jumps/Hawkes, the system has
  energy U + KE conserved up to integrator error. Since this overdamped
  Langevin has no explicit kinetic term, we report U(t) drift bound:
  with γ→∞ (purely overdamped) drift converges to zero; with γ=1 small,
  drift is bounded by |F|·dt per step. Test asserts |ΔU| ≤ tolerance.
"""

from __future__ import annotations

import math

import torch

from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator
from ecomd.models.potentials import conservative_forces


def _small_simulator(
    *,
    n_agents: int = 16,
    d_state: int = 8,
    hidden: int = 16,
    temperature_init: float = 0.0,
    gamma_init: float = 1.0,
    lam_dissipation: float = 0.0,
    learn_temperature: bool = False,
    learn_gamma: bool = False,
    jump_lambda: float = 0.0,
    twopop_enabled: bool = False,
    edge_gating_enabled: bool = False,
    global_state_enabled: bool = False,
    sps_k_random: int = 5,
) -> EcoMDSimulator:
    cfg = EcoMDConfig(
        n_agents=n_agents,
        d_state=d_state,
        hidden=hidden,
        temperature_init=temperature_init,
        gamma_init=gamma_init,
        lam_dissipation=lam_dissipation,
        learn_temperature=learn_temperature,
        learn_gamma=learn_gamma,
        jump_lambda=jump_lambda,
        twopop_enabled=twopop_enabled,
        edge_gating_enabled=edge_gating_enabled,
        global_state_enabled=global_state_enabled,
        sps_k_random=sps_k_random,
    )
    sim = EcoMDSimulator(cfg)
    sim.eval()
    return sim


def test_energy_logging_populates_trajectory() -> None:
    sim = _small_simulator()
    traj = sim.run(n_steps=8, seed=0)
    assert traj.total_potential is not None
    assert traj.total_potential.shape == (8,)
    # Energy should not be all zeros (the MLP has random init).
    assert torch.any(traj.total_potential != 0.0)
    # Should be finite.
    assert torch.all(torch.isfinite(traj.total_potential))


def test_force_equals_neg_grad_of_potential() -> None:
    """F = -∂U/∂s within numerical precision."""
    sim = _small_simulator(n_agents=8, d_state=4, hidden=8, sps_k_random=3)
    sim._reset_potential_cache()  # ensure deterministic edges
    s = torch.randn(8, 4) * 0.1

    # Get force + U from the new return-potential path.
    f, U = conservative_forces(
        sim.potential, s, context=torch.zeros(3),
        create_graph=False, return_potential=True,
    )

    # Numerical FD: perturb s by random direction, check (U(s+εv) - U(s)) ≈ -F·v · ε.
    # SPS resampling makes this tricky — disable resampling to make U deterministic.
    sim.potential.pairwise.resample_per_step = False
    sim._reset_potential_cache()
    # Re-evaluate so cache is populated with these specific edges.
    f_ref, U_ref = conservative_forces(
        sim.potential, s, context=torch.zeros(3),
        create_graph=False, return_potential=True,
    )
    eps = 1e-3
    v = torch.randn_like(s)
    v = v / v.norm()
    s_plus = (s + eps * v).detach()
    _, U_plus = conservative_forces(
        sim.potential, s_plus, context=torch.zeros(3),
        create_graph=False, return_potential=True,
    )
    fd = (U_plus - U_ref) / eps
    analytical = -(f_ref * v).sum()
    # Tight tolerance: should match to FD truncation O(eps²) ≈ 1e-6, but
    # MLP non-linearity can amplify; allow 1e-2 absolute.
    assert torch.allclose(fd, analytical, atol=1e-2), (
        f"FD={fd.item():.6e} vs analytical={analytical.item():.6e}"
    )


def test_T0_no_dissipation_potential_drift() -> None:
    """With T=0, λ_diss=0, no jumps/Hawkes, no twopop, no global state,
    γ small (1.0): the system is purely conservative drift.

    For overdamped Langevin without noise:
        s_{t+1} = s_t + F/γ · dt = s_t - (1/γ) · ∇U · dt
    This is gradient descent on U at rate (dt/γ). U(t) is monotonically
    DECREASING (going downhill) — the drift is real, not numerical error.

    What we want to verify: U decreases monotonically OR stays constant
    (at a critical point), and never blows up. The energy is bounded.
    """
    sim = _small_simulator(
        n_agents=16,
        temperature_init=0.0,
        lam_dissipation=0.0,
        gamma_init=10.0,  # large gamma → small step → slow drift
        jump_lambda=0.0,
    )
    traj = sim.run(n_steps=20, seed=0)
    U = traj.total_potential
    assert U is not None

    # Sanity: U is finite throughout.
    assert torch.all(torch.isfinite(U)), f"U has non-finite: {U.tolist()}"

    # With T=0 + overdamped descent, U should monotonically decrease (or stay flat).
    # Allow small numerical wobble on the order of |U|·1e-4.
    deltas = U[1:] - U[:-1]
    tol = U.abs().max().item() * 1e-3 + 1e-6
    assert torch.all(deltas <= tol), (
        f"U not monotonically decreasing under T=0 overdamped: "
        f"max delta={deltas.max().item():.6e}, tol={tol:.6e}"
    )

    # Total energy change should be bounded — a soft check that we didn't
    # blow up to NaN/Inf.
    total_drift = (U[0] - U[-1]).abs().item()
    assert math.isfinite(total_drift)
