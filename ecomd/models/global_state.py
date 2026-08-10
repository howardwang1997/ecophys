"""MEGNet-style global state (Tier 4.1 of feature/megnet-global-state).

Adds a global state vector ``u ∈ R^d_global`` that — distinctly from
``h_regime`` and ``h_agent`` — is updated FROM aggregated agent state +
energy quantities and feeds INTO both the pairwise and external
potentials directly. This realises the MEGNet/Battaglia GraphNet
"global state" axis missing from the current EcoMD architecture.

Design choices vs. existing latents
-----------------------------------

| latent | input | output | shapes V? |
|---|---|---|---|
| ``h_regime`` | market_stats (price summary) | scalar rate multipliers | NO (modulates rates only) |
| ``h_agent`` | per-agent (s_i, log_return, vol) | mean-pooled into external context | partial (only external) |
| ``u`` (this) | aggregated ⟨s⟩ + market_stats + (optional) ⟨h_agent⟩ | concatenated into pair AND external inputs | YES (changes V surface itself) |

The pair-side injection is the one that's genuinely new vs.
Tiers 1.1/3.1: u enters every pair kernel evaluation, so the same
`(s_i, s_j)` produces a different V at different points in the
trajectory. That's the structural mechanism we expect to break the
orthogonal-basin ceiling — different fact basins need different
``φ(s_i, s_j)`` shape, and ``u`` lets one network instantiate all
of them.

Update cadence
--------------
``update_every`` mirrors ``RegimeGRU``: only step the GRU every k
simulator steps, otherwise pass through. Keeps u as a slow-moving
global "phase" that the V surface conforms to.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

import torch
import torch.nn as nn
from torch import Tensor


@dataclass(frozen=True)
class GlobalStateConfig:
    d_global: int = 16
    d_state_proj: int = 8     # project ⟨s⟩ to d_state_proj
    update_every: int = 1
    init_gain: float = 0.1
    # Whether to consume aggregated h_agent (Tier 1.1) when available.
    use_agent_pool: bool = True


class GlobalStateGRU(nn.Module):
    """Global state vector u, updated by a GRUCell from aggregate features.

    Inputs the cell consumes (concatenated):
      - ``proj(⟨s⟩)`` — projection of mean agent state across N agents (d_state_proj)
      - market scalars ``[volatility, |last_log_return|, last_log_return]`` (3)
      - mean-pooled ``h_agent`` if Tier 1.1 active (d_agent), else zeros

    The cell input dim is therefore
      ``d_state_proj + 3 + (d_agent if use_agent_pool else 0)``.

    Output u is a (d_global,) vector. Consumers
    (StochasticPairwisePotential, ISABPairwisePotential, ExternalPotential)
    concatenate u along the appropriate input dim.
    """

    def __init__(
        self,
        d_state: int,
        config: GlobalStateConfig | None = None,
        d_agent: int = 0,
    ) -> None:
        super().__init__()
        self.cfg = config or GlobalStateConfig()
        self.d_state = d_state
        self.d_agent = int(d_agent) if self.cfg.use_agent_pool else 0
        self.proj = nn.Linear(d_state, self.cfg.d_state_proj)
        d_input = self.cfg.d_state_proj + 3 + self.d_agent
        self.cell = nn.GRUCell(d_input, self.cfg.d_global)
        for p in self.cell.parameters():
            if p.dim() >= 2:
                nn.init.xavier_uniform_(p, gain=self.cfg.init_gain)
            else:
                nn.init.zeros_(p)
        nn.init.xavier_uniform_(self.proj.weight, gain=self.cfg.init_gain)
        nn.init.zeros_(self.proj.bias)

    def init_h(self, device: torch.device, dtype: torch.dtype) -> Tensor:
        return torch.zeros(self.cfg.d_global, device=device, dtype=dtype)

    def maybe_step(
        self,
        u: Tensor,
        step_idx: int,
        s: Tensor,
        log_return: Tensor,
        volatility: Tensor,
        h_agent: Tensor | None = None,
    ) -> Tensor:
        if step_idx % self.cfg.update_every != 0:
            return u
        s_mean = s.mean(dim=0)                           # (d_state,)
        s_proj = self.proj(s_mean)                       # (d_state_proj,)
        market = torch.stack([volatility, log_return.abs(), log_return])  # (3,)
        parts = [s_proj, market]
        if self.cfg.use_agent_pool and h_agent is not None and self.d_agent > 0:
            parts.append(h_agent.mean(dim=0))            # (d_agent,)
        elif self.cfg.use_agent_pool and self.d_agent > 0:
            # h_agent absent at runtime but cell expects d_agent input — pad zeros
            parts.append(torch.zeros(self.d_agent, device=u.device, dtype=u.dtype))
        x = torch.cat(parts, dim=0).unsqueeze(0)         # (1, d_input)
        return cast(Tensor, self.cell(x, u.unsqueeze(0)).squeeze(0))
