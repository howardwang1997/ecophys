"""L2 recurrent fact-surrogate (build item L2-1, code-only pre-D0).

The second simulator lineage of the reexploration program (experiment plan
section 2; simulator contracts section 3): a recurrent next-state/increment
predictor over lab-asset-v3 ``F_exec`` streams — execution payloads +
``allocation_draw`` + pre/post BBO prices (PI decision D1_01) — carrying one
hidden state per clearing round and decoding deterministically at eval
(contract C2(d): no sampling heads).

What the existing library implies, followed rather than invented:
``ecomd/training/fact_surrogates.py`` is a library of four differentiable
per-fact surrogate *functions* (``gain_loss_skew``, ``agg_gaussianity``,
``soft_fano``, ``dfa_hurst_surrogate``) that each consume a 1-D return series.
A model that is to be trained by them must decode a per-round scalar return
series; the fact losses (composed in the trainer via
``ecomd.training.losses.multi_fact_terms``, the same path L1 uses) are computed
on that decoded series. The conserving-channel endpoint (contract C5:
channels = {volume units, cash ticks}) requires BOTH coordinate heads
({absolute next state, increment} — contract C3's cube needs all four trained
arms per lineage), and through-M training (contract C3/C16, estimator menu
D1_07) requires per-round integer-lattice flow and demand decodes that the
frozen estimators of ``ecomd.mechanisms.through_m`` can consume.

Recurrence idioms follow ``ecomd/models/agent_memory.py`` (``nn.GRUCell``,
near-zero xavier init, zero bias) and ``regime_latent.py`` (single-cell state,
``maybe_step`` cadence). Every stochastic consumer is either absent (decode is
deterministic; ``h_0`` defaults to zeros) or explicitly generator-threaded
(parameter init), satisfying the L2-3 no-global-RNG requirement from day one.

This module is validated by CPU smoke only (PI decision D1_13): forward pass
plus a single synthetic-batch gradient step. No training run, checkpoint
persistence, GPU, or market-data access is authorized by this file.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import cast

import torch
import torch.nn as nn
from torch import Tensor

__all__ = [
    "FEXEC_ROUND_FEATURES",
    "FactSurrogateBatch",
    "FactSurrogateConfig",
    "FactSurrogateOutput",
    "MechanismEstimator",
    "RecurrentFactSurrogate",
    "fexec_round_features",
    "lattice_ste",
]


# ─────────────────────────────────────────────────────────────────────────────
# F_exec → per-clearing-round feature map (the L2 input grammar)
# ─────────────────────────────────────────────────────────────────────────────


FEXEC_ROUND_FEATURES: tuple[str, ...] = (
    "has_execution",
    "log_n_exec",
    "log_volume",
    "aggressor_buy_share",
    "draw_volume_share",
    "pre_spread_ticks",
    "post_spread_ticks",
    "spread_change",
    "mid_move_ticks",
    "best_bid_move",
    "best_ask_move",
    "vwap_rel_spread",
    "log_maker_residual",
    "quotes_missing",
)
"""Frozen feature map: pure per-round functions of the F_exec payload fields.

Mapping from the lab-asset-v3 ``execution`` payload (frozen
``schema_spec.json``: ``[execution, aggressor_role, maker_role, allocation_draw?,
pre_best_bid, pre_best_ask, post_best_bid, post_best_ask]``, nested
``execution`` dict per ``scripts/lab_asset/matching.py``):

- ``has_execution`` — 1.0 iff the round has at least one execution record
  (the all-zero feature vector is the documented no-event token).
- ``log_n_exec`` — ``log1p`` of the round's execution-record count.
- ``log_volume`` — ``log1p`` of ``sum(execution.quantity)``.
- ``aggressor_buy_share`` — volume share with ``execution.side_of_aggressor
  == "B"``.
- ``draw_volume_share`` — volume share of records carrying an
  ``allocation_draw`` payload (the kernel-identity channel: 0 under fifo,
  1 under random-unit per-unit records).
- ``pre_spread_ticks`` / ``post_spread_ticks`` — ask - bid from the round's
  FIRST record's pre-quotes and LAST record's post-quotes. If a quote side is
  ``None`` (empty book side), the spread is 0 and the mid falls back to the
  surviving side (0.0 if both are ``None``); ``quotes_missing`` flags this.
- ``spread_change`` — post minus pre spread.
- ``mid_move_ticks`` — post-mid minus pre-mid under the same fallback rule.
- ``best_bid_move`` / ``best_ask_move`` — post minus pre per side (0.0 when
  either side is ``None``).
- ``vwap_rel_spread`` — ``(sum(price·quantity)/volume - pre_mid) /
  max(pre_spread, 1)``.
- ``log_maker_residual`` — ``log1p`` of ``sum(execution.maker_remaining)``.

No feature depends on another round, another tape, or any state outside the
payload fields: the map is a pure function of one round's F_exec records, so
the shared corpus projector (build item E-1) can emit it for both lineages.
"""


def _execution_int(execution: Mapping[str, object], key: str) -> int:
    value = execution[key]
    if not isinstance(value, int):
        raise ValueError(f"execution.{key} must be an int, got {value!r}")
    return value


def _quote_mid_spread(bid: int | None, ask: int | None) -> tuple[float, float]:
    if bid is None and ask is None:
        return 0.0, 0.0
    if bid is None or ask is None:
        survivor = cast(int, ask if bid is None else bid)
        return float(survivor), 0.0
    return (bid + ask) / 2.0, float(ask - bid)


def fexec_round_features(
    payloads: Sequence[Mapping[str, object]],
    *,
    dtype: torch.dtype = torch.float32,
) -> Tensor:
    """Project one clearing round's F_exec execution payloads to features.

    Parameters
    ----------
    payloads:
        The round's ``execution``-type tape payload dicts, in tape order.
        An empty sequence yields the documented no-event token (all zeros
        with ``has_execution == 0``).
    dtype:
        Output dtype; float32 by default (the model's working dtype).
    """

    if len(payloads) == 0:
        return torch.zeros(len(FEXEC_ROUND_FEATURES), dtype=dtype)

    volume = 0
    buy_volume = 0
    draw_volume = 0
    notional = 0
    maker_residual = 0
    for payload in payloads:
        raw = payload.get("execution")
        if not isinstance(raw, Mapping):
            raise ValueError("execution payload must carry an 'execution' mapping")
        quantity = _execution_int(raw, "quantity")
        price = _execution_int(raw, "price")
        volume += quantity
        notional += price * quantity
        maker_residual += _execution_int(raw, "maker_remaining")
        side = raw["side_of_aggressor"]
        if side == "B":
            buy_volume += quantity
        elif side != "S":
            raise ValueError(f"side_of_aggressor must be 'B' or 'S', got {side!r}")
        if "allocation_draw" in payload:
            draw_volume += quantity

    # pre-quotes come from the round's first record, post-quotes from its last
    def as_optional_int(record: Mapping[str, object], key: str) -> int | None:
        value = record[key]
        if value is None or isinstance(value, int):
            return value
        raise ValueError(f"{key} must be an int or None, got {value!r}")

    pre_bid = as_optional_int(payloads[0], "pre_best_bid")
    pre_ask = as_optional_int(payloads[0], "pre_best_ask")
    post_bid = as_optional_int(payloads[-1], "post_best_bid")
    post_ask = as_optional_int(payloads[-1], "post_best_ask")
    quotes_missing = (
        1.0
        if any(value is None for value in (pre_bid, pre_ask, post_bid, post_ask))
        else 0.0
    )

    pre_mid, pre_spread = _quote_mid_spread(pre_bid, pre_ask)
    post_mid, post_spread = _quote_mid_spread(post_bid, post_ask)

    def move(pre: int | None, post: int | None) -> float:
        if pre is None or post is None:
            return 0.0
        return float(post - pre)

    vwap = notional / volume if volume > 0 else pre_mid
    features = [
        1.0,
        math.log1p(len(payloads)),
        math.log1p(volume),
        buy_volume / volume if volume > 0 else 0.0,
        draw_volume / volume if volume > 0 else 0.0,
        pre_spread,
        post_spread,
        post_spread - pre_spread,
        post_mid - pre_mid,
        move(pre_bid, post_bid),
        move(pre_ask, post_ask),
        (vwap - pre_mid) / max(pre_spread, 1.0),
        math.log1p(maker_residual),
        quotes_missing,
    ]
    return torch.tensor(features, dtype=dtype)


# ─────────────────────────────────────────────────────────────────────────────
# Config, batch, output contracts
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class FactSurrogateConfig:
    """Frozen L2 architecture hyperparameters (contract: frozen at D0).

    ``n_channels`` is fixed at 2 by contract C5 (volume units, cash ticks);
    ``n_slots`` is the touched-level queue-slot capacity of the corpus adapter
    (build item E-1): ragged queues are right-padded with quantity-0 slots,
    which the through-M estimators treat as never-clearable.
    """

    d_hidden: int = 64
    n_channels: int = 2
    n_slots: int = 8
    init_gain: float = 0.1


MechanismEstimator = Callable[[Tensor, int], Tensor]
"""Through-M hook: (resting quantities of one touched level, demand) → allocation.

Matches the frozen estimator menu signatures
``ecomd.mechanisms.through_m.straight_through_through_m`` /
``perturb_and_map_through_m`` partial-applied over (kernel, draws/seed); the
shared engine-bridge wrapper (build item E-3) exposes the same call shape.
"""


@dataclass(frozen=True)
class FactSurrogateBatch:
    """One teacher-forced training batch of clearing-round sequences.

    ``features`` carries the F_exec feature map per round (see
    :data:`FEXEC_ROUND_FEATURES`); ``channels`` the observed conserving-channel
    state *after* each round; ``channels_init`` the pre-session channel state
    (base of the ABS/mechanism absolute predictions; zero base when ``None``);
    ``slot_prices`` the integer tick price per queue slot, consumed only by
    the through-M cash channel.
    """

    features: Tensor        # (B, T, d_features)
    channels: Tensor        # (B, T, n_channels)
    slot_prices: Tensor     # (B, T, n_slots), integer-valued
    channels_init: Tensor | None = None  # (B, n_channels)


@dataclass(frozen=True)
class FactSurrogateOutput:
    """Per-round decodes. Every tensor at index ``t`` is the prediction FOR
    round ``t`` decoded from the hidden state that encodes rounds ``< t``
    (strictly pre-round information; no within-round leakage)."""

    returns: Tensor                  # (B, T) decoded round log-returns
    abs_channels: Tensor             # (B, T, C) ABS head decode
    inc_channels: Tensor             # (B, T, C) INC head decode
    flow: Tensor                     # (B, T, S) resting quantities, integer lattice
    demand: Tensor                   # (B, T) executable demand, integer lattice
    hidden: Tensor                   # (B, d_hidden) post-episode state
    mechanism_channels: Tensor | None = None  # (B, T, C), through-M enforcement only


# ─────────────────────────────────────────────────────────────────────────────
# Model
# ─────────────────────────────────────────────────────────────────────────────


def lattice_ste(x: Tensor) -> Tensor:
    """Exact-forward/surrogate-backward rounding onto the integer lattice.

    Forward is ``round(x)`` (the engine lattice of through-M's validated
    quantities); backward is the identity — the same discipline as the frozen
    estimator menu, applied one layer earlier so continuous head outputs can
    enter the exact integer mechanism.
    """

    return x + (torch.round(x) - x).detach()


class RecurrentFactSurrogate(nn.Module):
    """GRU-over-clearing-rounds fact surrogate with deterministic decode.

    Update: ``h_{t+1} = GRUCell(x_t, h_t)`` with ``h_0 = 0`` (config-pinned;
    contract C2(d) deterministic decode). Decode from the pre-round state:
    scalar return (fact-loss surface), ABS/INC conserving-channel heads
    (contract C3 coordinate cube), and integer-lattice flow/demand heads
    (through-M attachment at the recurrent head's per-step flow output,
    simulator contracts section 3.3).
    """

    def __init__(
        self,
        config: FactSurrogateConfig | None = None,
        *,
        generator: torch.Generator | None = None,
    ) -> None:
        super().__init__()
        self.cfg = config or FactSurrogateConfig()
        if self.cfg.d_hidden < 1:
            raise ValueError(f"d_hidden must be ≥ 1, got {self.cfg.d_hidden}")
        if self.cfg.n_slots < 1:
            raise ValueError(f"n_slots must be ≥ 1, got {self.cfg.n_slots}")
        d_features = len(FEXEC_ROUND_FEATURES)
        # nn.Module constructors draw from the GLOBAL stream for their default
        # init; snapshot/restore makes the explicit generator the sole
        # effective randomness source (L2-3: no global-RNG consumers).
        global_state = torch.get_rng_state() if generator is not None else None
        self.cell = nn.GRUCell(d_features, self.cfg.d_hidden)
        self.return_head = nn.Linear(self.cfg.d_hidden, 1)
        self.abs_head = nn.Linear(self.cfg.d_hidden, self.cfg.n_channels)
        self.inc_head = nn.Linear(self.cfg.d_hidden, self.cfg.n_channels)
        self.flow_head = nn.Linear(self.cfg.d_hidden, self.cfg.n_slots)
        self.demand_head = nn.Linear(self.cfg.d_hidden, 1)
        if generator is not None and global_state is not None:
            torch.set_rng_state(global_state)
            self.reset_parameters(generator)

    def reset_parameters(self, generator: torch.Generator) -> None:
        """Deterministic parameter init drawn solely from ``generator``.

        Mirrors :class:`ecomd.models.agent_memory.AgentMemoryGRU`: xavier
        (gain ``init_gain``) for 2-D weights, zero biases. Passing the
        init-substream generator satisfies L2-3 (construction snapshots and
        restores the global stream, so the init substream is the only
        effective randomness source); construction without a generator keeps
        PyTorch default init and is reserved for throwaway test instances.
        """

        for module in (self.cell,):
            for parameter in module.parameters():
                if parameter.dim() >= 2:
                    nn.init.xavier_uniform_(parameter, gain=self.cfg.init_gain, generator=generator)
                else:
                    nn.init.zeros_(parameter)
        for head in (self.return_head, self.abs_head, self.inc_head,
                     self.flow_head, self.demand_head):
            nn.init.xavier_uniform_(head.weight, gain=self.cfg.init_gain, generator=generator)
            nn.init.zeros_(head.bias)

    def init_hidden(
        self,
        batch_size: int,
        *,
        device: torch.device | None = None,
        dtype: torch.dtype | None = None,
        generator: torch.Generator | None = None,
    ) -> Tensor:
        """``h_0``: zeros (config default, C2(d)). A ``generator`` draws an
        iid normal ``h_0`` instead — reserved for ablations; eval decode of
        the frozen configuration is the zeros path."""

        if generator is not None:
            return torch.randn(
                batch_size, self.cfg.d_hidden, generator=generator, device=device, dtype=dtype
            )
        return torch.zeros(batch_size, self.cfg.d_hidden, device=device, dtype=dtype)

    def forward(
        self,
        batch: FactSurrogateBatch,
        *,
        mechanism: MechanismEstimator | None = None,
    ) -> FactSurrogateOutput:
        """Teacher-forced rollout over ``T`` clearing rounds.

        ``mechanism=None`` is the raw enforcement arm. When a through-M
        estimator hook is supplied, each round's lattice flow/demand decode is
        executed through it and the returned ``mechanism_channels`` carries
        the exact-integer conserving-channel update (volume = cleared units,
        cash = cleared units * slot price), cumulated from
        ``batch.channels_init`` (zero base when absent).
        """

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

        h = self.init_hidden(batch_size, device=features.device, dtype=features.dtype)
        returns: list[Tensor] = []
        abs_rows: list[Tensor] = []
        inc_rows: list[Tensor] = []
        flow_rows: list[Tensor] = []
        demand_rows: list[Tensor] = []
        mechanism_rows: list[Tensor] = []
        for step in range(n_rounds):
            returns.append(self.return_head(h).squeeze(-1))
            abs_rows.append(self.abs_head(h))
            inc_rows.append(self.inc_head(h))
            flow = lattice_ste(torch.nn.functional.softplus(self.flow_head(h)))
            demand = torch.clamp(
                lattice_ste(torch.nn.functional.softplus(self.demand_head(h).squeeze(-1))),
                min=1.0,
            )
            flow_rows.append(flow)
            demand_rows.append(demand)
            if mechanism is not None:
                for episode in range(batch_size):
                    allocation = mechanism(
                        flow[episode], int(demand[episode].detach().item())
                    )
                    cash_increment = (allocation * slot_prices[episode, step]).sum()
                    mechanism_rows.append(
                        torch.stack((allocation.sum().unsqueeze(0), cash_increment.unsqueeze(0)))
                    )
            h = cast(Tensor, self.cell(features[:, step], h))

        output_returns = torch.stack(returns, dim=1)
        output_abs = torch.stack(abs_rows, dim=1)
        output_inc = torch.stack(inc_rows, dim=1)
        output_flow = torch.stack(flow_rows, dim=1)
        output_demand = torch.stack(demand_rows, dim=1)
        mechanism_channels: Tensor | None = None
        if mechanism is not None and mechanism_rows:
            # mechanism_rows is step-major (episode inner): (T·B, C) → (T, B, C) → (B, T, C)
            increments = (
                torch.stack(mechanism_rows)
                .view(n_rounds, batch_size, self.cfg.n_channels)
                .permute(1, 0, 2)
            )
            base = (
                batch.channels_init.unsqueeze(1)
                if batch.channels_init is not None
                else torch.zeros(
                    batch_size, 1, self.cfg.n_channels,
                    device=increments.device, dtype=increments.dtype,
                )
            )
            mechanism_channels = base + torch.cumsum(increments, dim=1)
        return FactSurrogateOutput(
            returns=output_returns,
            abs_channels=output_abs,
            inc_channels=output_inc,
            flow=output_flow,
            demand=output_demand,
            hidden=h,
            mechanism_channels=mechanism_channels,
        )
