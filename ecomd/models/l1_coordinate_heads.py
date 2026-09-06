"""L1 ABS/INC supervised coordinate heads (build item L1-2, code-only pre-D0).

The two trained coordinate arms of lineage L1 (EcoMD v2) on the reexploration
cube: contract C3's axis ``c`` is a property of the trained prediction head's
target, and simulator contracts section 2.2 records that no supervised
next-state/increment head existed — L1's only training objective was
stylized-fact moment matching on self-rollouts. This module supplies the two
heads: predict ``x_{t+1}`` (ABSOLUTE) vs predict ``x_{t+1} - x_t`` (INCREMENT)
on the conserving-channel targets of contract C5 ({total executed volume
units, total executed cash ticks} per clearing round), mechanically supported
by the same next-state/increment pairing the integrator already materializes
(``s_next`` and its increment, integrator.py:445-470).

Input grammar is the lineage-invariant corpus surface: the per-round feature
matrix is the frozen 14-feature map
:data:`ecomd.models.fact_surrogate.FEXEC_ROUND_FEATURES` (emitted by the E-1
projector), batched through :class:`~ecomd.models.fact_surrogate.FactSurrogateBatch`
so both lineages consume identical tensors. Where L2 carries a recurrent
hidden state across rounds, L1's potential surface is stateless per round:
the decode for round ``t`` is a function of round ``t``'s features and the
observed PRE-round channel state ``x_t`` only (strictly pre-round
information; no within-round leakage). The module also decodes the per-round
flow tensor ``z_t`` and executable demand on the integer lattice (the L1-1
adapter spec assigns ``z_t`` to L1-2) in the exact grammar the frozen
through-M estimators consume — the mechanism execution itself is build item
E-3/L1-3a/b and is deliberately NOT wired here.

Decode is deterministic (contract C2(d): no sampling heads). Construction
with an explicit ``generator`` (the init substream, L1-2's RNG binding (i))
is the sole effective randomness source for parameter init; construction
without one keeps PyTorch default init for throwaway test instances.

Validation scope is CPU smoke only (PI decision D1_13): forward pass plus a
single synthetic-batch gradient step. No training run, checkpoint
persistence, GPU, or market-data access is authorized by this file.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

import torch
import torch.nn as nn
from torch import Tensor

from .fact_surrogate import FEXEC_ROUND_FEATURES, FactSurrogateBatch, lattice_ste

__all__ = [
    "L1CoordinateHeads",
    "L1CoordinateHeadsConfig",
    "L1CoordinateOutput",
]


@dataclass(frozen=True)
class L1CoordinateHeadsConfig:
    """Frozen L1 head architecture hyperparameters (contract: frozen at D0).

    Mirrors :class:`ecomd.models.fact_surrogate.FactSurrogateConfig` field for
    field so the two lineages' corpus-facing surfaces stay aligned:
    ``n_channels`` is fixed at 2 by contract C5, ``n_slots`` is the E-1
    padding capacity, ``init_gain`` the xavier gain of the generator-threaded
    parameter init.
    """

    d_hidden: int = 64
    n_channels: int = 2
    n_slots: int = 8
    init_gain: float = 0.1


@dataclass(frozen=True)
class L1CoordinateOutput:
    """Per-round decodes. Every tensor at index ``t`` is the prediction FOR
    round ``t`` decoded from round ``t``'s features and the strictly pre-round
    observed channel state (no within-round leakage)."""

    abs_channels: Tensor   # (B, T, C) ABS head decode: prediction of x_{t+1}
    inc_channels: Tensor   # (B, T, C) INC head decode: prediction of x_{t+1} - x_t
    flow: Tensor           # (B, T, S) resting quantities z_t, integer lattice
    demand: Tensor         # (B, T) executable demand, integer lattice


class L1CoordinateHeads(nn.Module):
    """Stateless per-round ABS/INC coordinate heads over the L1 corpus surface.

    Encoder: the L1 MLP-potential idiom (``ecomd/models/potentials.py``) over
    ``concat(features_t, x_t)`` — SiLU MLP, xavier init, zero bias. Heads: ABS
    (absolute next channel state), INC (increment), and the integer-lattice
    flow/demand decodes for the through-M composition point (contracts 2.3).
    """

    def __init__(
        self,
        config: L1CoordinateHeadsConfig | None = None,
        *,
        generator: torch.Generator | None = None,
    ) -> None:
        super().__init__()
        self.cfg = config or L1CoordinateHeadsConfig()
        if self.cfg.d_hidden < 1:
            raise ValueError(f"d_hidden must be >= 1, got {self.cfg.d_hidden}")
        if self.cfg.n_channels < 1:
            raise ValueError(f"n_channels must be >= 1, got {self.cfg.n_channels}")
        if self.cfg.n_slots < 1:
            raise ValueError(f"n_slots must be >= 1, got {self.cfg.n_slots}")
        d_features = len(FEXEC_ROUND_FEATURES)
        # nn.Module constructors draw from the GLOBAL stream for their default
        # init; snapshot/restore makes the explicit generator the sole
        # effective randomness source (the simulator contracts 2.4 lesson).
        global_state = torch.get_rng_state() if generator is not None else None
        self.encoder = nn.Sequential(
            nn.Linear(d_features + self.cfg.n_channels, self.cfg.d_hidden),
            nn.SiLU(),
            nn.Linear(self.cfg.d_hidden, self.cfg.d_hidden),
            nn.SiLU(),
        )
        self.abs_head = nn.Linear(self.cfg.d_hidden, self.cfg.n_channels)
        self.inc_head = nn.Linear(self.cfg.d_hidden, self.cfg.n_channels)
        self.flow_head = nn.Linear(self.cfg.d_hidden, self.cfg.n_slots)
        self.demand_head = nn.Linear(self.cfg.d_hidden, 1)
        if generator is not None and global_state is not None:
            torch.set_rng_state(global_state)
            self.reset_parameters(generator)

    def reset_parameters(self, generator: torch.Generator) -> None:
        """Deterministic parameter init drawn solely from ``generator``.

        Mirrors :class:`ecomd.models.fact_surrogate.RecurrentFactSurrogate`:
        xavier (gain ``init_gain``) for 2-D weights, zero biases. Passing the
        init-substream generator satisfies the L1-2 RNG binding (i) —
        construction snapshots and restores the global stream, so the named
        substream is the only effective randomness source.
        """

        for module in self.encoder:
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight, gain=self.cfg.init_gain, generator=generator)
                nn.init.zeros_(module.bias)
        for head in (self.abs_head, self.inc_head, self.flow_head, self.demand_head):
            nn.init.xavier_uniform_(head.weight, gain=self.cfg.init_gain, generator=generator)
            nn.init.zeros_(head.bias)

    def pre_round_base(self, batch: FactSurrogateBatch) -> Tensor:
        """Observed pre-round channel state ``x_t`` as a ``(B, T, C)`` tensor.

        ``x_0`` is ``batch.channels_init`` (the E-4 conserving-channel state at
        session start; zero base when absent, matching the E-1 zero-base
        cumsum); ``x_t = channels[:, t-1]`` afterwards.
        """

        channels = batch.channels
        if batch.channels_init is not None:
            first = batch.channels_init.unsqueeze(1)
        else:
            first = torch.zeros_like(channels[:, :1])
        previous = torch.cat((first, channels[:, :-1]), dim=1)
        return previous.to(dtype=batch.features.dtype)

    def forward(self, batch: FactSurrogateBatch) -> L1CoordinateOutput:
        """Teacher-forced deterministic decode over ``T`` clearing rounds."""

        features = batch.features
        channels = batch.channels
        slot_prices = batch.slot_prices
        if features.ndim != 3 or features.shape[2] != len(FEXEC_ROUND_FEATURES):
            raise ValueError(
                f"features must be (B, T, {len(FEXEC_ROUND_FEATURES)}), got {tuple(features.shape)}"
            )
        batch_size, n_rounds, _ = features.shape
        if channels.shape != (batch_size, n_rounds, self.cfg.n_channels):
            raise ValueError(
                f"channels must be (B, T, {self.cfg.n_channels}), got {tuple(channels.shape)}"
            )
        if slot_prices.shape != (batch_size, n_rounds, self.cfg.n_slots):
            raise ValueError(
                f"slot_prices must be (B, T, {self.cfg.n_slots}), got {tuple(slot_prices.shape)}"
            )
        if batch.channels_init is not None and (
            batch.channels_init.shape != (batch_size, self.cfg.n_channels)
        ):
            raise ValueError(
                "channels_init must be (B, n_channels), got "
                f"{tuple(batch.channels_init.shape)}"
            )

        base = self.pre_round_base(batch)
        hidden = cast(Tensor, self.encoder(torch.cat((features, base), dim=-1)))
        abs_channels = self.abs_head(hidden)
        inc_channels = self.inc_head(hidden)
        flow = lattice_ste(torch.nn.functional.softplus(self.flow_head(hidden)))
        demand = torch.clamp(
            lattice_ste(torch.nn.functional.softplus(self.demand_head(hidden).squeeze(-1))),
            min=1.0,
        )
        return L1CoordinateOutput(
            abs_channels=abs_channels,
            inc_channels=inc_channels,
            flow=flow,
            demand=demand,
        )
