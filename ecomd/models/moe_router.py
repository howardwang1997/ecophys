"""Heterogeneous-node MoE router for EcoMD (exp 110, Path B2 tournament entrant).

Hypothesis (exp 108 diagnosis): the fat-tail floor (hill #2) is an OVERSHOOT to
α<2 (infinite variance) caused by agent-level Student-t + jumps. A finite-variance
**mixture of normals** is leptokurtic with FINITE variance, so heterogeneous agents
(a soft, learned, market-state-dependent mixture over K (gamma, temperature)
experts) can recover fat-but-finite tails — letting us turn DOWN noise_df / jumps
and land hill in [2,4].

`AgentExpertRouter` is the soft/learned generalization of two-population (which
routes per-agent gamma/T via a HARD type_idx lookup). It returns per-agent (N,1)
multipliers on gamma/T that feed the existing integrator path — so the integrator
is untouched. A load-balance regularizer (Switch-Transformer importance loss)
prevents expert collapse. An optional information-asymmetry channel feeds a noisy
fundamental signal to a subset of agents' gate (a non-equilibrium-steady-state
source, Paper-B value).

OFF (moe_enabled=False) ⟹ router not built ⟹ bit-exact prior behaviour.
"""

from __future__ import annotations

import torch
import torch.nn as nn
from torch import Tensor


class AgentExpertRouter(nn.Module):
    def __init__(
        self,
        d_state: int,
        n_experts: int = 4,
        hidden: int = 32,
        ctx_dim: int = 2,           # [volatility, last_log_return]
        log_scale_clip: float = 1.5,
        info_asym: bool = False,
    ) -> None:
        super().__init__()
        self.n_experts = int(n_experts)
        self.log_scale_clip = float(log_scale_clip)
        self.info_asym = bool(info_asym)
        in_dim = d_state + ctx_dim + (1 if info_asym else 0)
        self.gate = nn.Sequential(
            nn.Linear(in_dim, hidden), nn.SiLU(), nn.Linear(hidden, self.n_experts)
        )
        # Init gate near zero → near-uniform routing at start (no collapse).
        for m in self.gate.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight, gain=0.1)
                nn.init.zeros_(m.bias)
        # Per-expert log multipliers on gamma / temperature (start at 0 = neutral).
        self.log_gamma_scale = nn.Parameter(torch.zeros(self.n_experts))
        self.log_temp_scale = nn.Parameter(torch.zeros(self.n_experts))

    def _weights(self, s: Tensor, ctx: Tensor, info_signal: Tensor | None) -> Tensor:
        n = s.size(0)
        feats = [s, ctx.unsqueeze(0).expand(n, -1)]
        if self.info_asym:
            sig = info_signal if info_signal is not None else torch.zeros(n, 1, device=s.device, dtype=s.dtype)
            feats.append(sig if sig.dim() == 2 else sig.unsqueeze(-1))
        x = torch.cat(feats, dim=-1)
        return torch.softmax(self.gate(x), dim=-1)            # (N, K)

    def forward(
        self, s: Tensor, ctx: Tensor, info_signal: Tensor | None = None
    ) -> tuple[Tensor, Tensor]:
        """Return per-agent (gamma_mul, temp_mul), each (N,1), bounded by exp(±clip)."""
        w = self._weights(s, ctx, info_signal)                # (N, K)
        c = self.log_scale_clip
        log_g = (w * self.log_gamma_scale).sum(-1, keepdim=True).clamp(-c, c)
        log_t = (w * self.log_temp_scale).sum(-1, keepdim=True).clamp(-c, c)
        return torch.exp(log_g), torch.exp(log_t)

    def load_balance(self, s: Tensor, ctx: Tensor, info_signal: Tensor | None = None) -> Tensor:
        """Switch-Transformer importance loss: K·Σ_k mean_usage_k² − 1 ≥ 0,
        minimized (=0) at uniform average expert usage. Prevents expert collapse."""
        w = self._weights(s, ctx, info_signal)                # (N, K)
        usage = w.mean(dim=0)                                 # (K,)
        return self.n_experts * (usage * usage).sum() - 1.0


__all__ = ["AgentExpertRouter"]
