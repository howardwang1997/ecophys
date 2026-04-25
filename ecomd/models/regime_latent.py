"""Slow regime-switching latent (GRU) for non-stationary market state.

Plan v3 §Phase B: a slow latent variable h_regime ∈ R^d_regime that
captures the current market "regime" (high/low vol, trending/ranging,
crisis/calm). Modulates Hawkes self-excitation strength κ and Langevin
parameters γ, T so the simulator can produce different behaviour in
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
  heads in ExcessDemandPrice (κ_eff(h)) and EcoMDSimulator (γ_eff(h),
  T_eff(h)). The heads are owned by their consumers, not by RegimeGRU.

The latent's rank is broadcast to all positions in the rollout. This
is the "global regime" interpretation; a per-region or per-cluster
regime would need a different design (out of scope for v3).
"""

from __future__ import annotations

from dataclasses import dataclass

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
        h_new = self.cell(x, h.unsqueeze(0)).squeeze(0)
        return h_new


class RegimeReadHead(nn.Module):
    """Small MLP turning h_regime → scalar multiplier for a given param.

    Used by ExcessDemandPrice for κ_eff(h_regime) and by EcoMDSimulator
    for γ_eff(h_regime), T_eff(h_regime). Output is bounded via softplus
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
