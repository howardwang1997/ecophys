"""ISAB-style attention pairwise potential (Tier 3.1 of feature/arch-extensions).

Induced Set Attention Block (ISAB) from Set Transformer (Lee et al.
ICML 2019). Two cross-attention layers via M < N learned inducing points
make the cost O(N·M) instead of O(N²), without giving up global
information flow (every agent influences every other through the
inducing-point bottleneck).

Why manual attention (einsum + softmax) instead of
``torch.nn.functional.scaled_dot_product_attention``: we need
``create_graph=True`` double-backward to compute forces F = -∇V via
``torch.autograd.grad``. PyTorch's fused SDPA backends (FlashAttention,
mem-efficient) currently break double-backward. The MATH backend
supports it, but to avoid backend-version surprises we just write the
attention by hand. At M=64 the einsum cost is negligible.

Memory budget (N=10K, M=64, d=32, fp32):
- attention scores (one head): 10K x 64 x 4B = 2.5 MB per layer
- attended output: 10K x 32 x 4B = 1.3 MB per layer
- multi-head h=4 gives a factor of 4 (still tiny)

Output: a scalar V_pair to be plugged into the ConservativePotential.
"""

from __future__ import annotations

import math
from typing import cast

import torch
import torch.nn as nn
from torch import Tensor


class _MultiHeadCrossAttn(nn.Module):
    """Multi-head cross-attention: queries Q attend to keys/values KV.

    Shapes:
        Q: (Lq, d_in)
        KV: (Lkv, d_in)
        out: (Lq, d_out)

    Implements attention manually (matmul + softmax + matmul) so
    create_graph=True double-backward works without depending on the
    backend selection of ``scaled_dot_product_attention``.
    """

    def __init__(self, d_in: int, d_out: int, n_heads: int = 4, init_gain: float = 0.5):
        super().__init__()
        assert d_out % n_heads == 0, f"d_out {d_out} must be divisible by n_heads {n_heads}"
        self.n_heads = n_heads
        self.d_head = d_out // n_heads
        self.d_out = d_out
        self.q_proj = nn.Linear(d_in, d_out, bias=False)
        self.k_proj = nn.Linear(d_in, d_out, bias=False)
        self.v_proj = nn.Linear(d_in, d_out, bias=False)
        self.o_proj = nn.Linear(d_out, d_out, bias=False)
        for m in (self.q_proj, self.k_proj, self.v_proj, self.o_proj):
            nn.init.xavier_uniform_(m.weight, gain=init_gain)

    def forward(self, q_in: Tensor, kv_in: Tensor) -> Tensor:
        length_q = q_in.shape[0]
        length_kv = kv_in.shape[0]
        n_heads = self.n_heads
        d_head = self.d_head

        q = self.q_proj(q_in).view(length_q, n_heads, d_head).transpose(0, 1)
        k = self.k_proj(kv_in).view(length_kv, n_heads, d_head).transpose(0, 1)
        v = self.v_proj(kv_in).view(length_kv, n_heads, d_head).transpose(0, 1)

        scale = 1.0 / math.sqrt(d_head)
        scores = torch.einsum("hqd,hkd->hqk", q, k) * scale          # (H, Lq, Lkv)
        attn = torch.softmax(scores, dim=-1)
        attended = torch.einsum("hqk,hkd->hqd", attn, v)             # (H, Lq, D)

        out = attended.transpose(0, 1).contiguous().view(length_q, n_heads * d_head)
        return cast(Tensor, self.o_proj(out))


class ISABPairwisePotential(nn.Module):
    """Induced Set Attention Block as a permutation-invariant pair potential.

    Architecture (single ISAB block, sufficient for our O(N·M) target):
        I (M, d_attn)  — learnable inducing points
        H = CrossAttn(Q=I, KV=X')        # (M, d_attn)   compress
        Y = CrossAttn(Q=X', KV=H)        # (N, d_attn)   broadcast
        v_i = MLP_readout(Y_i)           # (N, 1)
        V   = sum_i v_i                  # scalar

    where X' = MLP_in(s) projects each agent's state to d_attn.

    Output is a scalar to plug into ConservativePotential alongside the
    external potential.
    """

    def __init__(
        self,
        d: int,
        hidden: int = 64,
        m_inducing: int = 64,
        n_heads: int = 4,
        init_gain: float = 0.5,
        d_global_in: int = 0,
    ) -> None:
        super().__init__()
        self.d = d
        self.hidden = hidden
        self.m = m_inducing
        self.d_global_in = int(d_global_in)

        # input projection. Tier 4.1: when d_global_in>0, broadcast u and
        # concatenate to each per-agent state before projection.
        self.in_proj = nn.Sequential(
            nn.Linear(d + self.d_global_in, hidden),
            nn.SiLU(),
        )
        # learnable inducing points
        self.I = nn.Parameter(torch.randn(m_inducing, hidden) * (init_gain / math.sqrt(hidden)))
        self.compress = _MultiHeadCrossAttn(hidden, hidden, n_heads, init_gain=init_gain)
        self.broadcast = _MultiHeadCrossAttn(hidden, hidden, n_heads, init_gain=init_gain)
        self.readout = nn.Sequential(
            nn.Linear(hidden, hidden),
            nn.SiLU(),
            nn.Linear(hidden, 1),
        )
        for m in self.in_proj.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight, gain=init_gain)
                nn.init.zeros_(m.bias)
        for m in self.readout.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight, gain=init_gain)
                nn.init.zeros_(m.bias)

    def reset_edge_cache(self) -> None:  # protocol parity with StochasticPairwisePotential
        return

    def forward(self, s: Tensor, context: Tensor | None = None) -> Tensor:
        # Tier 4.1: when d_global_in>0, simulator passes the global state u
        # via the context channel (1-D, length d_global_in).
        n, d = s.shape
        assert d == self.d, f"expected last dim {self.d}, got {d}"

        if self.d_global_in > 0:
            u = (
                torch.zeros(self.d_global_in, device=s.device, dtype=s.dtype)
                if context is None
                else context
            )
            u_b = u.unsqueeze(0).expand(n, self.d_global_in)
            x_in = torch.cat([s, u_b], dim=-1)
        else:
            x_in = s

        x = self.in_proj(x_in)                       # (N, hidden)
        h = self.compress(self.I, x)                 # (M, hidden)
        y = self.broadcast(x, h)                     # (N, hidden)
        v = self.readout(y).squeeze(-1)              # (N,)
        return cast(Tensor, v.sum())
