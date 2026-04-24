"""Langevin integrators for EcoMD.

Supports the Phase-2 overdamped Langevin dynamics used in v0, and leaves the
:class:`LangevinIntegrator` protocol in place so Phase 4 can drop in an
underdamped (Kramers) integrator without touching the simulator.

Notation
--------
s        : state tensor (N, d)
f_cons   : conservative force -∇V_cons (N, d)
f_diss   : dissipative force -∇V_diss (N, d)   [optional; defaults to 0]
T        : temperature, scalar or (N, d) broadcastable
gamma    : friction, scalar
dt       : step size, scalar

Overdamped Langevin update (Euler-Maruyama):

    s_{t+1} = s_t + (f_cons + f_diss) * dt / gamma + √(2 T dt / gamma) * ε

with ε ~ N(0, I) by default. From v0.6 onward, ε can be a unit-variance
Student-t random variate (set ``noise_dist='t'``); this preserves the
Einstein relation ⟨ε²⟩ = 1 while injecting heavy tails that the Gaussian
integrator cannot reproduce (stylized facts #2 Hill-α, #5 Fano).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal, Protocol

import torch
from torch import Tensor

# ─────────────────────────────────────────────────────────────────────────────
# Step output
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class IntegratorStep:
    """All per-step quantities the simulator needs to log."""

    s_next: Tensor          # (N, d)
    f_cons: Tensor          # (N, d), detached-or-not depending on create_graph
    f_diss: Tensor          # (N, d)
    f_stoch: Tensor         # (N, d), the realized noise force (pre-dt scaling removed)
    velocity: Tensor        # (N, d) = (s_next - s) / dt


# ─────────────────────────────────────────────────────────────────────────────
# Protocol
# ─────────────────────────────────────────────────────────────────────────────


class LangevinIntegrator(Protocol):
    def step(
        self,
        s: Tensor,
        f_cons: Tensor,
        f_diss: Tensor,
        *,
        T: Tensor | float,
        gamma: Tensor | float,
        dt: float,
        generator: torch.Generator | None = None,
    ) -> IntegratorStep: ...


# ─────────────────────────────────────────────────────────────────────────────
# Overdamped Langevin (v0 default)
# ─────────────────────────────────────────────────────────────────────────────


def _sample_unit_t(
    shape: tuple[int, ...],
    df: int,
    *,
    generator: torch.Generator | None,
    device: torch.device,
    dtype: torch.dtype,
) -> Tensor:
    """Unit-variance Student-t via x / sqrt(χ²_df / df), then var-normalized.

    Composed from :func:`torch.randn` so the given ``generator`` governs the
    sampling — this keeps experiments seed-reproducible. Requires integer
    df > 2 so the distribution has finite variance.
    """
    if not isinstance(df, int) or df <= 2:
        raise ValueError(f"Student-t df must be integer > 2, got {df}")
    x = torch.randn(shape, generator=generator, device=device, dtype=dtype)
    chi_sq = torch.zeros(shape, device=device, dtype=dtype)
    for _ in range(df):
        z = torch.randn(shape, generator=generator, device=device, dtype=dtype)
        chi_sq = chi_sq + z * z
    t = x / torch.sqrt(chi_sq / df)
    return t / math.sqrt(df / (df - 2.0))


class OverdampedLangevin:
    """Euler-Maruyama overdamped Langevin step.

    s_{t+1} = s + (f_cons + f_diss) / gamma * dt + sqrt(2 T dt / gamma) * eps

    Noise ε has unit variance by construction in either noise distribution
    (Gaussian or Student-t), preserving the fluctuation-dissipation relation.
    """

    def __init__(
        self,
        noise_dist: Literal["normal", "t"] = "normal",
        noise_df: int = 5,
    ) -> None:
        if noise_dist not in ("normal", "t"):
            raise ValueError(f"noise_dist must be 'normal' or 't', got {noise_dist!r}")
        if noise_dist == "t" and (not isinstance(noise_df, int) or noise_df <= 2):
            raise ValueError(f"noise_df must be integer > 2 for Student-t, got {noise_df}")
        self.noise_dist = noise_dist
        self.noise_df = noise_df

    def _sample_noise(
        self,
        shape: tuple[int, ...],
        generator: torch.Generator | None,
        device: torch.device,
        dtype: torch.dtype,
    ) -> Tensor:
        if self.noise_dist == "normal":
            return torch.randn(shape, generator=generator, device=device, dtype=dtype)
        return _sample_unit_t(shape, self.noise_df, generator=generator, device=device, dtype=dtype)

    def step(
        self,
        s: Tensor,
        f_cons: Tensor,
        f_diss: Tensor,
        *,
        T: Tensor | float,
        gamma: Tensor | float,
        dt: float,
        generator: torch.Generator | None = None,
    ) -> IntegratorStep:
        if f_cons.shape != s.shape:
            raise ValueError(f"f_cons shape {f_cons.shape} != state shape {s.shape}")
        if f_diss.shape != s.shape:
            raise ValueError(f"f_diss shape {f_diss.shape} != state shape {s.shape}")

        T_t = torch.as_tensor(T, device=s.device, dtype=s.dtype)
        gamma_t = torch.as_tensor(gamma, device=s.device, dtype=s.dtype)
        # clamp to avoid divide-by-zero from misconfigured runs
        gamma_t = torch.clamp(gamma_t, min=1e-6)
        T_t = torch.clamp(T_t, min=0.0)

        noise_scale = torch.sqrt(2.0 * T_t * dt / gamma_t)
        eps = self._sample_noise(tuple(s.shape), generator, s.device, s.dtype)
        stoch_displacement = noise_scale * eps

        drift = (f_cons + f_diss) / gamma_t * dt
        s_next = s + drift + stoch_displacement

        # record forces in consistent units (force, not displacement)
        f_stoch = stoch_displacement / dt * gamma_t
        velocity = (s_next - s) / dt

        return IntegratorStep(
            s_next=s_next,
            f_cons=f_cons,
            f_diss=f_diss,
            f_stoch=f_stoch,
            velocity=velocity,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Underdamped placeholder
# ─────────────────────────────────────────────────────────────────────────────


class UnderdampedLangevin:
    """Velocity-Verlet-like underdamped integrator — stub for Phase 4.

    Raises NotImplementedError; defined so the Protocol has an alternative
    registered implementation. Filling this in is part of the fluctuation
    theorem work package (plan_v2 §Phase 4).
    """

    def step(
        self,
        s: Tensor,
        f_cons: Tensor,
        f_diss: Tensor,
        *,
        T: Tensor | float,
        gamma: Tensor | float,
        dt: float,
        generator: torch.Generator | None = None,
    ) -> IntegratorStep:
        raise NotImplementedError("UnderdampedLangevin reserved for Phase 4; use OverdampedLangevin in v0")
