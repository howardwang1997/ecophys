"""Per-step entropy production rate σ̇(t) for EcoMD trajectories.

Paper B uses this as a primary observable: σ̇(t) ≈ ⟨F_diss · v⟩ / T_eff is
the rate of entropy generation (in units of k_B per dt). At equilibrium
σ̇ → 0; far from equilibrium (during a market crash) σ̇ peaks.

This module provides differentiable + numpy variants and a per-particle
breakdown (Paper B's "channel decomposition" — which agent populations
produce most of the dissipation).

References
----------
- Seifert, Stochastic Thermodynamics (2012, Rep. Prog. Phys.)
- Maskawa, J. (Entropy 2025, 27(4), 435) — empirical IFT on volatility cascade
- Plan v3 §Phase 4 — Paper B's entropy-production claim
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
from torch import Tensor

from ..physics.observables import EcoMDTrajectory


@dataclass
class EntropyProductionStats:
    """Aggregated entropy-production statistics over a trajectory.

    All units: k_B per dt, for consistency with Seifert.
    """

    sigma_dot_mean: float
    sigma_dot_std: float
    sigma_dot_per_step: np.ndarray         # (T,)
    sigma_dot_per_particle: np.ndarray     # (N,) — time-mean per particle
    sigma_dot_by_type: dict[int, float]    # type_id → mean σ̇ (only if types provided)
    T_eff_used: float                       # the temperature scalar used


def entropy_production_per_step(
    f_diss: Tensor, velocities: Tensor, T_eff: Tensor | float,
) -> Tensor:
    """Per-step entropy production σ̇_t = mean over particles of (F_diss · v)/T.

    Shapes:
      f_diss      (T, N, d)
      velocities  (T, N, d)
      T_eff       scalar Tensor or float
    Returns:
      (T,) tensor of per-step σ̇.
    """
    if isinstance(T_eff, (int, float)):
        T_eff = torch.tensor(float(T_eff), dtype=f_diss.dtype, device=f_diss.device)
    # F_diss · v summed over the d axis, mean over particles
    inner = (f_diss * velocities).sum(dim=-1)        # (T, N)
    sigma_dot = inner.mean(dim=-1) / (T_eff + 1e-12)  # (T,)
    return sigma_dot


def entropy_production_per_particle(
    f_diss: Tensor, velocities: Tensor, T_eff: Tensor | float,
) -> Tensor:
    """Per-particle σ̇ averaged over time. Returns (N,)."""
    if isinstance(T_eff, (int, float)):
        T_eff = torch.tensor(float(T_eff), dtype=f_diss.dtype, device=f_diss.device)
    inner = (f_diss * velocities).sum(dim=-1)        # (T, N)
    return inner.mean(dim=0) / (T_eff + 1e-12)


def compute_entropy_production_stats(
    traj: EcoMDTrajectory,
    T_eff: float,
    type_idx: np.ndarray | None = None,
) -> EntropyProductionStats:
    """Full statistics from a trajectory + scalar T.

    ``type_idx`` (N,) optional; if provided, also reports σ̇ averaged
    per type for the v3 two-population analysis.
    """
    sd = entropy_production_per_step(traj.f_diss, traj.velocities, T_eff).detach().cpu().numpy()
    spp = entropy_production_per_particle(traj.f_diss, traj.velocities, T_eff).detach().cpu().numpy()
    by_type: dict[int, float] = {}
    if type_idx is not None:
        type_idx = np.asarray(type_idx)
        for k in np.unique(type_idx):
            mask = type_idx == k
            if mask.any():
                by_type[int(k)] = float(spp[mask].mean())
    return EntropyProductionStats(
        sigma_dot_mean=float(sd.mean()),
        sigma_dot_std=float(sd.std()),
        sigma_dot_per_step=sd,
        sigma_dot_per_particle=spp,
        sigma_dot_by_type=by_type,
        T_eff_used=float(T_eff),
    )


def per_channel_force_decomposition(traj: EcoMDTrajectory) -> dict[str, float]:
    """Mean force magnitude per channel over the trajectory.

    Useful for Paper A's "force probe" figure — shows which channel
    (conservative pair, dissipative friction, stochastic noise) dominates
    the dynamics at each phase of training.
    """
    return {
        "f_cons_mean_abs": traj.f_cons.detach().abs().mean().item(),
        "f_diss_mean_abs": traj.f_diss.detach().abs().mean().item(),
        "f_stoch_mean_abs": traj.f_stoch.detach().abs().mean().item(),
        "velocity_mean_abs": traj.velocities.detach().abs().mean().item(),
    }
