"""Slow regime-switching latent (GRU) for non-stationary market state.

Plan v3 §Phase B: a slow latent variable h_regime ∈ R^d_regime that
captures the current market "regime" (high/low vol, trending/ranging,
crisis/calm). Modulates Hawkes self-excitation and Langevin parameters
so the simulator can produce different behaviour in
different regimes without changing its weights.

Design choices
--------------
- **Slow update**: GRU is updated every ``update_every`` simulator steps,
  not every step. This forces the latent to vary on a slower time scale
  than per-step price dynamics — necessary for the "stationary weights +
  slow latent carries non-stationarity" decomposition.
- **Aggregate stats input**: takes per-window market features (vol, |r|
  mean, log-return, returns autocorr proxy) — never raw agent state.
- **Read heads**: output `h_regime` is consumed by separate small MLP
  heads in ExcessDemandPrice and EcoMDSimulator (effective friction and
  T_eff(h)). The heads are owned by their consumers, not by RegimeGRU.

The latent's rank is broadcast to all positions in the rollout. This
is the "global regime" interpretation; a per-region or per-cluster
regime would need a different design (out of scope for v3).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

import torch
import torch.nn as nn
from torch import Tensor


@dataclass(frozen=True)
class RegimeGRUConfig:
    d_regime: int = 16
    d_input: int = 4         # (vol, |r|_ema, log_ret, ret_autocorr_proxy)
    update_every: int = 8    # only step the GRU every k simulator steps
    init_gain: float = 0.1   # small init so untrained GRU passes through


class RegimeGRU(nn.Module):
    """Single GRUCell that updates a slow regime latent.

    State: ``h ∈ R^d_regime`` (per-rollout scalar — not per-agent).
    Update: ``h_{t+1} = GRUCell(input_t, h_t)`` every ``update_every`` steps.

    Inputs to GRUCell are aggregate market stats. We use a small set
    chosen to be regime-discriminative: instantaneous volatility, the
    EWMA of |r|, the latest log-return, and a short-window squared-
    return correlation proxy.
    """

    def __init__(self, config: RegimeGRUConfig | None = None) -> None:
        super().__init__()
        self.cfg = config or RegimeGRUConfig()
        self.cell = nn.GRUCell(self.cfg.d_input, self.cfg.d_regime)
        # init GRU near-zero so untrained = no effect
        for p in self.cell.parameters():
            if p.dim() >= 2:
                nn.init.xavier_uniform_(p, gain=self.cfg.init_gain)
            else:
                nn.init.zeros_(p)

    def init_h(self, device: torch.device, dtype: torch.dtype) -> Tensor:
        return torch.zeros(self.cfg.d_regime, device=device, dtype=dtype)

    def maybe_step(self, h: Tensor, step_idx: int, market_stats: Tensor) -> Tensor:
        """Step the GRU only every ``update_every`` simulator steps.

        ``market_stats`` is a 1-D tensor of shape (d_input,). h has shape
        (d_regime,). We unsqueeze to add batch dim 1 for GRUCell.
        """
        if step_idx % self.cfg.update_every != 0:
            return h
        x = market_stats.unsqueeze(0)
        h_new = cast(Tensor, self.cell(x, h.unsqueeze(0)).squeeze(0))
        return h_new

    def read(self, h: Tensor) -> Tensor:
        """Project the persistent state onto the d_regime vector consumed
        by :class:`RegimeReadHead`. For RegimeGRU this is the identity."""
        return h


class RegimeReadHead(nn.Module):
    """Small MLP turning h_regime → scalar multiplier for a given param.

    Used by ExcessDemandPrice and by EcoMDSimulator for effective friction
    and temperature. Output is bounded via softplus
    around 1.0 so the multiplier stays positive.
    """

    def __init__(self, d_regime: int, hidden: int = 16, init_gain: float = 0.1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_regime, hidden),
            nn.SiLU(),
            nn.Linear(hidden, 1),
        )
        for m in self.net.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight, gain=init_gain)
                nn.init.zeros_(m.bias)

    def forward(self, h_regime: Tensor) -> Tensor:
        """Returns a positive scalar multiplier centred near 1.0."""
        raw = self.net(h_regime).squeeze()
        # exp(0.1 * raw) — stays close to 1 when MLP outputs near 0
        # clamped for stability
        return torch.exp(torch.clamp(0.1 * raw, min=-2.0, max=2.0))


# ─────────────────────────────────────────────────────────────────────────────
# B-round mechanism 3 — discrete Gumbel-softmax regime switching
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class DiscreteRegimeGRUConfig:
    """Discrete K-state regime selector.

    n_states K∈{3, 5} typical. The GRU updates K-dim logits; a
    Gumbel-softmax sample produces a soft one-hot over the K states.
    Each state maps via a learned embedding to the d_regime vector that
    downstream RegimeReadHead consumes — so this is a drop-in replacement
    for :class:`RegimeGRU` without changing read-head plumbing.

    Targets aggregational_gaussianity (band [10, 200]; v4 winners at
    300+). The continuous GRU smears regime states together; discrete
    switching produces genuine "quiet" vs "active" periods, restoring
    the GARCH-like tail-of-aggregated-returns shape.
    """

    n_states: int = 3
    d_regime: int = 16        # output embedding dim (matches RegimeGRU.d_regime)
    d_input: int = 4
    update_every: int = 8
    init_gain: float = 0.1
    gumbel_tau: float = 1.0   # softmax temperature; lower → harder switching


class DiscreteRegimeGRU(nn.Module):
    """GRUCell over K-dim logits + Gumbel-softmax + learned state embeddings.

    State carried by simulator: ``h`` of shape (n_states,) — the logits.

    Forward path inside maybe_step / read:
        logits_{t+1} = GRUCell(market_stats, logits_t)         # (n_states,)
        soft_one_hot = gumbel_softmax(logits, τ)               # (n_states,) on simplex
        h_regime_emb = soft_one_hot @ state_embed_table        # (d_regime,)

    Backward: `gumbel_softmax` is differentiable (Jang+Maddison 2017), so
    gradients flow through the soft sample.

    Note: ``maybe_step`` returns the **logits** (the persistent state).
    ``read(h)`` produces the embedding consumed by RegimeReadHead. The
    EcoMDSimulator must call ``regime_gru.read(h_regime_next)`` before
    feeding to read heads. This separation keeps the persistent state
    rank consistent with logits while letting the read heads consume
    the d_regime embedding.
    """

    def __init__(self, config: DiscreteRegimeGRUConfig | None = None) -> None:
        super().__init__()
        self.cfg = config or DiscreteRegimeGRUConfig()
        if self.cfg.n_states < 2:
            raise ValueError(f"n_states must be ≥ 2, got {self.cfg.n_states}")
        if self.cfg.gumbel_tau <= 0:
            raise ValueError(f"gumbel_tau must be > 0, got {self.cfg.gumbel_tau}")
        # GRU cell over K-dim logits
        self.cell = nn.GRUCell(self.cfg.d_input, self.cfg.n_states)
        for p in self.cell.parameters():
            if p.dim() >= 2:
                nn.init.xavier_uniform_(p, gain=self.cfg.init_gain)
            else:
                nn.init.zeros_(p)
        # K learnable state embeddings → d_regime
        self.state_embed = nn.Parameter(
            torch.randn(self.cfg.n_states, self.cfg.d_regime) * self.cfg.init_gain
        )

    def init_h(self, device: torch.device, dtype: torch.dtype) -> Tensor:
        """Initial logits — uniform (softmax → 1/K each)."""
        return torch.zeros(self.cfg.n_states, device=device, dtype=dtype)

    def maybe_step(self, h: Tensor, step_idx: int, market_stats: Tensor) -> Tensor:
        """Update logits every ``update_every`` steps.

        Returns the new logits (shape (n_states,)). The simulator calls
        :meth:`read` to project these to d_regime before passing to the
        read heads.
        """
        if step_idx % self.cfg.update_every != 0:
            return h
        x = market_stats.unsqueeze(0)
        new_logits = cast(Tensor, self.cell(x, h.unsqueeze(0)).squeeze(0))
        return new_logits

    def read(self, h: Tensor) -> Tensor:
        """Project logits → soft one-hot → d_regime embedding."""
        soft = torch.nn.functional.gumbel_softmax(
            h, tau=self.cfg.gumbel_tau, hard=False, dim=-1
        )
        return soft @ self.state_embed
