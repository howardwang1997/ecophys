"""Scheduled-sampling regularizer for BPTT rollouts (Track B-β, Paper A).

During training, with curriculum probability p(iter) that ramps from 0 to
``max_prob`` over ``warmup_iters`` outer iterations, each rollout step's
stochastic force ``f_stoch`` is widened by ``sigma_mult`` (>1) to inject
out-of-distribution noise. This is a Bengio-style exposure-bias regularizer
adapted to Langevin dynamics: instead of mixing teacher-forced ground-truth
states, we widen the noise channel so the network learns to recover from
larger excursions than the standard diffusion would produce.

Hyperparameters (set via EcoMDConfig):

- ``ss_max_prob`` ∈ [0, 1]: peak fraction of steps that get widened
- ``ss_ramp_schedule`` ∈ {"linear", "cosine"}: how p(iter) grows from 0 to max
- ``ss_warmup_iters``: outer training iters before p reaches ``ss_max_prob``
- ``ss_sigma_mult``: multiplier on noise scale when a step fires
  (1.0 = off, 1.5 = mild widening, 2.0+ = aggressive)

The state object is pure-Python (no torch state). Bernoulli sampling lives in
``EcoMDSimulator.rollout_chunk`` so the generator's RNG stream stays the
single source of truth for reproducibility.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, cast

if TYPE_CHECKING:
    from ..models.ecomd import EcoMDConfig


RampSchedule = Literal["linear", "cosine"]


@dataclass(frozen=True)
class ScheduledSamplingState:
    """Stateless schedule descriptor. Caller passes ``iter_idx`` per call."""

    max_prob: float = 0.0
    ramp_schedule: RampSchedule = "linear"
    warmup_iters: int = 32
    sigma_mult: float = 1.5

    def __post_init__(self) -> None:
        if not 0.0 <= self.max_prob <= 1.0:
            raise ValueError(f"max_prob must be in [0, 1], got {self.max_prob}")
        if self.ramp_schedule not in ("linear", "cosine"):
            raise ValueError(
                f"ramp_schedule must be 'linear' or 'cosine', got {self.ramp_schedule!r}"
            )
        if self.warmup_iters < 0:
            raise ValueError(f"warmup_iters must be ≥ 0, got {self.warmup_iters}")
        if self.sigma_mult < 1.0:
            raise ValueError(
                f"sigma_mult must be ≥ 1.0 (widening only), got {self.sigma_mult}"
            )

    def get_prob(self, iter_idx: int) -> float:
        """Probability that any given step within outer iter ``iter_idx`` gets
        its noise widened. Monotonically non-decreasing in ``iter_idx`` until
        it plateaus at ``max_prob`` after ``warmup_iters``.
        """
        if iter_idx < 0:
            raise ValueError(f"iter_idx must be ≥ 0, got {iter_idx}")
        if self.max_prob == 0.0:
            return 0.0
        if self.warmup_iters == 0:
            return self.max_prob
        frac = min(iter_idx / self.warmup_iters, 1.0)
        if self.ramp_schedule == "linear":
            return self.max_prob * frac
        # cosine: smooth S-curve, 0 at frac=0, max_prob at frac=1
        return self.max_prob * 0.5 * (1.0 - math.cos(math.pi * frac))

    @property
    def enabled(self) -> bool:
        return self.max_prob > 0.0 and self.sigma_mult > 1.0


def state_from_config(cfg: EcoMDConfig) -> ScheduledSamplingState | None:
    """Build a state from an EcoMDConfig (or any object with matching fields).

    Returns ``None`` if scheduled sampling is disabled in the config — callers
    should treat ``None`` as the no-op path (no extra branches in hot loops).
    """
    if not getattr(cfg, "scheduled_sampling_enabled", False):
        return None
    return ScheduledSamplingState(
        max_prob=float(cfg.ss_max_prob),
        ramp_schedule=cast(RampSchedule, cfg.ss_ramp_schedule),
        warmup_iters=int(cfg.ss_warmup_iters),
        sigma_mult=float(cfg.ss_sigma_mult),
    )
