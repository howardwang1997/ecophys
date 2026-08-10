"""Per-agent GRU memory (Tier 1.1 of feature/arch-extensions).

Modeled on RegimeGRU (regime_latent.py:43-79), but operating on a per-agent
state ``h_agent`` of shape ``(N, d_memory)`` instead of a global scalar
``(d_regime,)``. The intent is to give each agent short-term memory of its
own log-return history so the model can produce dynamics that need
agent-level temporal correlation (DFA Hurst, zumbach asymmetry, autocorr
of returns).

Inputs to the GRU are per-agent features: a small projection of the
current agent state (s_i) plus broadcast market context (log_return,
volatility). The latent feeds into the external potential's context via
a small read-head that aggregates h_agent across agents.

Notes
-----
- Slow-update cadence (``update_every``) is supported, mirroring RegimeGRU.
- Init-near-zero weights so untrained = no effect; the simulator output is
  bit-identical to the pre-Tier-1.1 baseline when the flag is off.
- ``init_h`` returns shape ``(n_agents, d_memory)`` — the simulator passes
  ``cfg.n_agents`` so init can build the right-sized buffer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

import torch
import torch.nn as nn
from torch import Tensor


@dataclass(frozen=True)
class AgentMemoryConfig:
    d_memory: int = 16
    d_state_proj: int = 4   # project s_i to d_state_proj for input to GRU
    d_input: int = 6        # d_state_proj + 2 (log_return, vol)
    update_every: int = 1
    init_gain: float = 0.1


class AgentMemoryGRU(nn.Module):
    """Per-agent GRU. Each of N agents carries its own h_i ∈ R^d_memory.

    State: ``h in R^{N x d_memory}``.
    Update: ``h_{t+1} = GRUCell(input_t, h_t)`` every ``update_every`` steps.

    Inputs per agent are a low-rank projection of the agent's current
    state (so each agent gets its own "view") concatenated with the
    market scalars (log_return, vol). Aggregate-across-agents readout
    is provided by ``read_global`` for the external potential's context.
    """

    def __init__(
        self,
        d_state: int,
        config: AgentMemoryConfig | None = None,
    ) -> None:
        super().__init__()
        self.cfg = config or AgentMemoryConfig()
        self.d_state = d_state
        self.proj = nn.Linear(d_state, self.cfg.d_state_proj)
        self.cell = nn.GRUCell(self.cfg.d_input, self.cfg.d_memory)
        for p in self.cell.parameters():
            if p.dim() >= 2:
                nn.init.xavier_uniform_(p, gain=self.cfg.init_gain)
            else:
                nn.init.zeros_(p)
        nn.init.xavier_uniform_(self.proj.weight, gain=self.cfg.init_gain)
        nn.init.zeros_(self.proj.bias)

    def init_h(self, n_agents: int, device: torch.device, dtype: torch.dtype) -> Tensor:
        return torch.zeros(n_agents, self.cfg.d_memory, device=device, dtype=dtype)

    def maybe_step(
        self,
        h_agent: Tensor,
        step_idx: int,
        s: Tensor,
        log_return: Tensor,
        volatility: Tensor,
    ) -> Tensor:
        """Step the per-agent GRU only every ``update_every`` simulator steps.

        Parameters
        ----------
        h_agent : (N, d_memory)
        s : (N, d_state) — current agent state
        log_return, volatility : scalar tensors broadcast to all agents
        """
        if step_idx % self.cfg.update_every != 0:
            return h_agent
        n = s.shape[0]
        s_proj = self.proj(s)  # (N, d_state_proj)
        # broadcast scalars to (N, 1) each
        lr = log_return.expand(n).unsqueeze(-1)
        vol = volatility.expand(n).unsqueeze(-1)
        x = torch.cat([s_proj, lr, vol], dim=-1)  # (N, d_input)
        return cast(Tensor, self.cell(x, h_agent))

    def read_global(self, h_agent: Tensor) -> Tensor:
        """Mean-pool h_agent over agents → (d_memory,) for external context."""
        return h_agent.mean(dim=0)
