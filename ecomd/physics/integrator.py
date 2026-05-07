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


def _sample_levy_symmetric(
    shape: tuple[int, ...],
    alpha: float,
    *,
    generator: torch.Generator | None,
    device: torch.device,
    dtype: torch.dtype,
) -> Tensor:
    """Symmetric α-stable variate via Chambers-Mallows-Stuck (CMS).

    Reference: Chambers, Mallows & Stuck (1976), JASA 71, 340-344.
    For symmetric β=0, scale=1 stable with α ∈ (0, 2]:

        U  ~ Uniform(-π/2, π/2)
        W  ~ Exp(1)
        X  = sin(α U) / (cos U)^{1/α} · ( cos((1-α) U) / W )^{(1-α)/α}

    α=2 → Normal(0, 2) (note variance 2, not 1). Returned variate has
    UNIT scale parameter γ_stable=1 (NOT unit variance — variance is
    infinite for α<2). Caller must adopt a Stratonovich-style scale
    convention; we adjust by α-dependent factor so that for α=2 the
    returned variate matches torch.randn(...) (mean 0, var 1).

    Differentiable: U and W enter via tan/cos/exp/log — autograd works,
    but the result is the noise variate itself; downstream losses should
    typically use detached returns or work in distributional space.
    """
    if not (0.0 < alpha <= 2.0):
        raise ValueError(f"levy alpha must be in (0, 2], got {alpha}")
    eps = 1e-7
    u = (torch.rand(shape, generator=generator, device=device, dtype=dtype) - 0.5) * (math.pi - 2 * eps)
    w = -torch.log(torch.rand(shape, generator=generator, device=device, dtype=dtype).clamp_min(eps))
    if abs(alpha - 1.0) < 1e-6:
        x = torch.tan(u)
    elif abs(alpha - 2.0) < 1e-6:
        # CMS at α=2 reduces to sqrt(2)·sin(2u)/sqrt(W) which has variance 2.
        # Rescale by 1/sqrt(2) so caller sees a unit-variance Normal-equivalent.
        x = torch.sqrt(torch.tensor(2.0, device=device, dtype=dtype)) * torch.sin(2 * u) / torch.sqrt(w)
        x = x * (1.0 / math.sqrt(2.0))
    else:
        a = alpha
        sin_au = torch.sin(a * u)
        cos_u = torch.cos(u).clamp_min(eps)
        cos_diff = torch.cos((1.0 - a) * u).clamp_min(eps)
        x = (sin_au / cos_u.pow(1.0 / a)) * (cos_diff / w).pow((1.0 - a) / a)
    return x


class OverdampedLangevin:
    """Euler-Maruyama overdamped Langevin step.

    s_{t+1} = s + (f_cons + f_diss) / gamma * dt + sqrt(2 T dt / gamma) * eps

    Noise ε has unit variance by construction in either noise distribution
    (Gaussian or Student-t), preserving the fluctuation-dissipation relation.

    Optional Tier 2.1 compound-Poisson jumps (when ``jump_lambda > 0`` and
    ``jump_scale > 0``):
      - Training mode (``create_graph=True`` upstream): a deterministic
        drift correction ``-λ · jump_scale_drift · dt`` is subtracted from
        the position update. This is consistent with E[J]=0 jumps but
        keeps a shape-coupling that the trainer can backprop through
        (otherwise an additive constant adds nothing learnable).
      - Inference mode: sample ``K ~ Poisson(λ·dt)`` per agent per step,
        each ``J_k ~ N(0, jump_scale²)``, add to position. The same
        ``generator`` is used so replay is deterministic.

    Optional Tier 2.2 per-agent update mask (``update_mask``): boolean
    vector of shape (N,) controlling which agents move on this step. All
    agents still contribute to forces; masked-off agents simply retain
    their current ``s``. Used to build slow/fast multi-timescale
    populations.
    """

    def __init__(
        self,
        noise_dist: Literal["normal", "t", "levy"] = "normal",
        noise_df: int = 5,
        levy_alpha: float = 1.7,
        levy_clip: float = 50.0,
        jump_lambda: float = 0.0,
        jump_scale: float = 0.0,
        asym_drag_alpha: float = 0.0,
        memory_kernel_lambda: float = 0.0,
        memory_kernel_strength: float = 0.0,
    ) -> None:
        if noise_dist not in ("normal", "t", "levy"):
            raise ValueError(f"noise_dist must be 'normal'|'t'|'levy', got {noise_dist!r}")
        if noise_dist == "t" and (not isinstance(noise_df, int) or noise_df <= 2):
            raise ValueError(f"noise_df must be integer > 2 for Student-t, got {noise_df}")
        if noise_dist == "levy" and not (0.0 < levy_alpha <= 2.0):
            raise ValueError(f"levy_alpha must be in (0, 2], got {levy_alpha}")
        if jump_lambda < 0.0 or jump_scale < 0.0:
            raise ValueError(f"jump_lambda and jump_scale must be ≥ 0, got {jump_lambda}, {jump_scale}")
        if not -1.0 < asym_drag_alpha < 1.0:
            raise ValueError(f"asym_drag_alpha must be in (-1, 1), got {asym_drag_alpha}")
        if not 0.0 <= memory_kernel_lambda < 1.0:
            raise ValueError(f"memory_kernel_lambda must be in [0, 1), got {memory_kernel_lambda}")
        self.noise_dist = noise_dist
        self.noise_df = noise_df
        self.levy_alpha = float(levy_alpha)
        self.levy_clip = float(levy_clip)
        self.jump_lambda = float(jump_lambda)
        self.jump_scale = float(jump_scale)
        self.asym_drag_alpha = float(asym_drag_alpha)
        self.memory_kernel_lambda = float(memory_kernel_lambda)
        self.memory_kernel_strength = float(memory_kernel_strength)
        # Memory kernel state — EMA of |Δs| across calls. Initialized lazily
        # on the first step to match s shape/device. Reset by simulator
        # between rollouts via :meth:`reset_state`.
        self._mem_ema: Tensor | None = None
        # Last Δprice signal (scalar tensor). Updated by simulator via
        # :meth:`update_price_signal` when asymmetric drag is enabled.
        self._last_price_delta: float = 0.0

    def reset_state(self) -> None:
        """Clear path-dependent buffers. Call before a fresh rollout so the
        memory kernel and asymmetric-drag price signal don't leak across
        episodes within the same simulator instance.
        """
        self._mem_ema = None
        self._last_price_delta = 0.0

    def update_price_signal(self, log_return: float | Tensor) -> None:
        """Hook called by simulator after each price-formation step. Stores
        the most recent log-return so the next ``step`` can modulate γ via
        ``asym_drag_alpha``. Cheap (scalar copy); no allocations.
        """
        if isinstance(log_return, Tensor):
            try:
                self._last_price_delta = float(log_return.detach().item())
            except Exception:
                self._last_price_delta = 0.0
        else:
            self._last_price_delta = float(log_return)

    def _sample_noise(
        self,
        shape: tuple[int, ...],
        generator: torch.Generator | None,
        device: torch.device,
        dtype: torch.dtype,
    ) -> Tensor:
        if self.noise_dist == "normal":
            return torch.randn(shape, generator=generator, device=device, dtype=dtype)
        if self.noise_dist == "t":
            return _sample_unit_t(shape, self.noise_df, generator=generator, device=device, dtype=dtype)
        # Lévy: scale-1 symmetric α-stable, then clip extreme tails so a
        # single rare draw doesn't blow up Langevin updates and break the
        # downstream eval (which assumes finite variance for KS distance,
        # GARCH residuals, etc.). The clip preserves heavy-tail signal up to
        # ~50σ-equivalent; tune via levy_clip.
        x = _sample_levy_symmetric(shape, self.levy_alpha,
                                   generator=generator, device=device, dtype=dtype)
        if self.levy_clip > 0:
            x = torch.clamp(x, min=-self.levy_clip, max=self.levy_clip)
        return x

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
        update_mask: Tensor | None = None,
        create_graph: bool = True,
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

        # V4 mechanism 2: asymmetric drag γ_eff = γ · (1 + α·sign(Δp_recent)).
        # Down moves (Δp<0) → γ ↓ → larger σ_noise ∝ 1/√γ on the next step
        # (liquidity evaporation, leverage effect); up moves → γ ↑ → smaller
        # noise. This is the correct sign for negative corr(r_t, r²_{t+k}).
        # Floor at 0.05 prevents γ→0 instability when α≈1.
        if abs(self.asym_drag_alpha) > 0.0 and self._last_price_delta != 0.0:
            sign = 1.0 if self._last_price_delta > 0.0 else -1.0
            mul = max(0.05, 1.0 + self.asym_drag_alpha * sign)
            gamma_t = gamma_t * mul

        # V4 mechanism 3: memory kernel. EMA of |Δs| modulates noise scale,
        # echoing recent volatility into the next step. Targets zumbach
        # asymmetry and acf_squared_returns. Updates are detached from the
        # graph so the kernel acts as a slow exogenous modulator and we
        # don't accumulate BPTT memory across the entire rollout.
        mem_boost: Tensor | float = 0.0
        if self.memory_kernel_strength > 0.0 and self.memory_kernel_lambda > 0.0:
            if self._mem_ema is None or self._mem_ema.shape != s.shape:
                self._mem_ema = torch.zeros_like(s)
            mem_boost = self.memory_kernel_strength * self._mem_ema

        noise_scale = torch.sqrt(2.0 * T_t * dt / gamma_t) * (1.0 + mem_boost)
        eps = self._sample_noise(tuple(s.shape), generator, s.device, s.dtype)
        stoch_displacement = noise_scale * eps

        drift = (f_cons + f_diss) / gamma_t * dt

        # Tier 2.1: compound-Poisson jumps.
        jump_disp = None
        if self.jump_lambda > 0.0 and self.jump_scale > 0.0:
            if create_graph:
                # Training mode: deterministic drift correction. We multiply by
                # |s| element-wise so the correction is shape-coupled and
                # backprop through state actually has a learnable gradient
                # path (not a pure constant). Magnitude controlled by
                # λ·jump_scale·dt.
                drift_correct = -(self.jump_lambda * self.jump_scale * dt) * torch.tanh(s)
                drift = drift + drift_correct
            else:
                # Inference: sample compound-Poisson jumps per agent per dim.
                k = torch.poisson(
                    torch.full(tuple(s.shape), self.jump_lambda * dt,
                               device=s.device, dtype=s.dtype),
                    generator=generator,
                )
                # Sum of k iid N(0, σ²) ≡ N(0, k·σ²); equivalently sqrt(k)·σ·Z.
                z = torch.randn(tuple(s.shape), generator=generator,
                                device=s.device, dtype=s.dtype)
                jump_disp = torch.sqrt(k) * self.jump_scale * z

        s_next = s + drift + stoch_displacement
        if jump_disp is not None:
            s_next = s_next + jump_disp

        # Tier 2.2: per-agent update mask (slow/fast multi-timescale).
        if update_mask is not None:
            if update_mask.dim() != 1 or update_mask.shape[0] != s.shape[0]:
                raise ValueError(
                    f"update_mask must be (N,)={s.shape[0]}, got {tuple(update_mask.shape)}"
                )
            mask = update_mask.to(dtype=s.dtype).unsqueeze(-1)  # (N, 1)
            s_next = mask * s_next + (1.0 - mask) * s

        # V4 mechanism 3: update memory-kernel EMA. Detached so it doesn't
        # carry gradient across the entire rollout.
        if self.memory_kernel_strength > 0.0 and self.memory_kernel_lambda > 0.0:
            ds_mag = (s_next - s).detach().abs()
            if self._mem_ema is None or self._mem_ema.shape != ds_mag.shape:
                self._mem_ema = ds_mag
            else:
                lam = self.memory_kernel_lambda
                self._mem_ema = lam * self._mem_ema + (1.0 - lam) * ds_mag

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
