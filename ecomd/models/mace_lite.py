"""MACE-lite: k-NN + RBF + K-class + higher-body potential for EcoMD v1.

This module drops in as a replacement for :class:`PairwisePotential` when
``EcoMDConfig.pairwise_kind == "mace_lite"``. Design principles:

- **Sparsity**: instead of v0.x's O(N²) all-pair interactions, we use a
  k-nearest-neighbour graph in feature space (k=16-32). Brings the model
  from N ≤ 10³ (v0.6 limit) to N ≤ 5×10⁵ feasible on H20 NVLink.
- **Higher-body via tensor product** (MACE trick): h⁽¹⁾ ⊙ h⁽¹⁾ gives 3-body
  and h⁽¹⁾ ⊙ h⁽¹⁾ ⊙ h⁽¹⁾ gives 4-body features at O(N·k) cost, avoiding
  explicit triangle / quadruple enumeration.
- **Structured class prior**: soft K-class assignment z_i ∈ simplex(K)
  lets message function specialise by agent type (fundamentalist /
  chartist / noise trader / MM analogue), addressing the identifiability
  concern flagged in plan v3 §critical risks.
- **Stable training**: k-NN edges computed with ``.detach()`` so graph
  changes don't propagate spurious gradients; LayerNorm on h⁽¹⁾ before
  higher-body products so tensor products don't blow up.

Reference: Batatia et al. (MACE, NeurIPS 2022) — we strip the SO(3) tensor
products (no physical-space rotations in feature space) but keep the
ACE-style higher-body expansion.
"""

from __future__ import annotations

from dataclasses import dataclass

import torch
import torch.nn as nn
from torch import Tensor


@dataclass(frozen=True)
class MACELiteConfig:
    d_state: int = 32
    k: int = 16                      # k-NN neighbours (Mac 16, H20 32)
    hidden: int = 64                 # MLP hidden dim
    feature_dim: int = 64            # F — message / node feature dim
    n_classes: int = 4               # K agent types
    n_rbf: int = 8                   # B Gaussian RBF centers
    rbf_cutoff: float = 5.0          # RBF centers span [0, cutoff]
    body_order: int = 2              # 2, 3, or 4 — which higher-body features to include
    knn_refresh: int = 10            # recompute k-NN every N steps
    use_layernorm: bool = True       # LayerNorm on h^(1) before tensor products (ablation D)

    def __post_init__(self) -> None:
        if self.body_order not in (2, 3, 4):
            raise ValueError(f"body_order must be 2, 3, or 4; got {self.body_order}")
        if self.k < 2:
            raise ValueError(f"k must be ≥ 2; got {self.k}")


# ─────────────────────────────────────────────────────────────────────────────
# Gaussian RBF
# ─────────────────────────────────────────────────────────────────────────────


class GaussianRBF(nn.Module):
    """Expand a scalar distance onto B Gaussian basis functions.

    Centers evenly spaced on [0, cutoff]; widths fixed to spacing/2.
    """

    def __init__(self, n_rbf: int, cutoff: float) -> None:
        super().__init__()
        centers = torch.linspace(0.0, cutoff, n_rbf)
        width = torch.tensor(cutoff / max(1, n_rbf - 1) / 2.0)
        self.register_buffer("centers", centers)
        self.register_buffer("width", width)

    def forward(self, r: Tensor) -> Tensor:
        # r: (E,)  → (E, B)
        diff = r.unsqueeze(-1) - self.centers
        return torch.exp(-0.5 * (diff / self.width).pow(2))


# ─────────────────────────────────────────────────────────────────────────────
# k-NN graph in feature space
# ─────────────────────────────────────────────────────────────────────────────


def knn_edge_index(s: Tensor, k: int, chunk_size: int = 2048) -> Tensor:
    """Return edge_index of shape (2, N·k) giving i → j for each agent's k nearest.

    Distance = Euclidean in feature space. Self-loops excluded.
    Result is detached (we don't backprop through graph selection).
    Computes distances in chunks to keep peak memory O(chunk_size * N * d)
    instead of O(N² * d).
    """
    with torch.no_grad():
        n = s.shape[0]
        if k >= n:
            k = n - 1
        nbr_parts: list[Tensor] = []
        for start in range(0, n, chunk_size):
            end = min(start + chunk_size, n)
            diff = s[start:end].unsqueeze(1) - s.unsqueeze(0)  # (chunk, N, d)
            d2 = diff.pow(2).sum(dim=-1)                        # (chunk, N)
            # exclude self-loops within this chunk
            rows = torch.arange(end - start, device=s.device)
            d2[rows, rows + start] = float("inf")
            _, idx = torch.topk(d2, k=k, dim=1, largest=False)
            nbr_parts.append(idx)
        nbr_idx = torch.cat(nbr_parts, dim=0)                   # (N, k)
        src = torch.arange(n, device=s.device).unsqueeze(1).expand(n, k).reshape(-1)
        dst = nbr_idx.reshape(-1)
        return torch.stack([src, dst], dim=0)                   # (2, N·k)


# ─────────────────────────────────────────────────────────────────────────────
# MACE-lite main module
# ─────────────────────────────────────────────────────────────────────────────


class MACELitePotential(nn.Module):
    """V_pairwise(s) via k-NN + RBF + K-class + higher-body expansion."""

    def __init__(self, config: MACELiteConfig | None = None) -> None:
        super().__init__()
        self.cfg = config or MACELiteConfig()
        c = self.cfg
        d = c.d_state
        F = c.feature_dim
        K = c.n_classes

        # Agent-type soft prior: s_i → z_i ∈ simplex(K)
        self.type_net = nn.Sequential(
            nn.Linear(d, c.hidden), nn.SiLU(),
            nn.Linear(c.hidden, K),
        )

        # Radial basis
        self.rbf = GaussianRBF(c.n_rbf, c.rbf_cutoff)

        # 2-body message: [z_i, z_j, R_ij, s_i - s_j] → F
        msg_in = 2 * K + c.n_rbf + d
        self.msg_net = nn.Sequential(
            nn.Linear(msg_in, c.hidden), nn.SiLU(),
            nn.Linear(c.hidden, c.hidden), nn.SiLU(),
            nn.Linear(c.hidden, F),
        )

        # LayerNorm on h⁽¹⁾ before tensor products (prevents blow-up).
        # Disable via use_layernorm=False for ablation studies.
        self.norm1 = nn.LayerNorm(F) if (c.body_order >= 3 and c.use_layernorm) else None

        # Higher-body readouts (only if body_order allows)
        self.body3_net: nn.Module | None = None
        self.body4_net: nn.Module | None = None
        if c.body_order >= 3:
            self.body3_net = nn.Sequential(
                nn.Linear(F, c.hidden), nn.SiLU(),
                nn.Linear(c.hidden, F),
            )
        if c.body_order >= 4:
            self.body4_net = nn.Sequential(
                nn.Linear(F, c.hidden), nn.SiLU(),
                nn.Linear(c.hidden, F),
            )

        # Readout: concat([h⁽¹⁾, h⁽²⁾, h⁽³⁾, z_i]) → scalar per agent
        readout_in = F + (F if c.body_order >= 3 else 0) + (F if c.body_order >= 4 else 0) + K
        self.readout = nn.Sequential(
            nn.Linear(readout_in, c.hidden), nn.SiLU(),
            nn.Linear(c.hidden, 1),
        )

        self._init_weights()

        # Cache for k-NN refresh
        self._cached_edge_index: Tensor | None = None
        self._step_since_refresh: int = 0

    def _init_weights(self) -> None:
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight, gain=0.5)
                nn.init.zeros_(m.bias)

    # ── Graph ────────────────────────────────────────────────────────────

    def _maybe_refresh_knn(self, s: Tensor) -> Tensor:
        if self._cached_edge_index is None or self._step_since_refresh >= self.cfg.knn_refresh:
            self._cached_edge_index = knn_edge_index(s, self.cfg.k)
            self._step_since_refresh = 0
        self._step_since_refresh += 1
        return self._cached_edge_index

    def reset_graph_cache(self) -> None:
        """Call at the start of each rollout to avoid leaking graph across runs."""
        self._cached_edge_index = None
        self._step_since_refresh = 0

    # ── Forward ──────────────────────────────────────────────────────────

    def forward(self, s: Tensor, context: Tensor | None = None) -> Tensor:
        del context  # MACE-lite V_pairwise is context-free (V_external handles context)
        c = self.cfg
        n = s.shape[0]

        edge_index = self._maybe_refresh_knn(s)
        src, dst = edge_index[0], edge_index[1]                # (E,)

        # (1) Type prior z_i
        z = torch.softmax(self.type_net(s), dim=-1)            # (N, K)
        z_src = z[src]                                          # (E, K)
        z_dst = z[dst]                                          # (E, K)

        # (2) Relative vector + distance
        rel = s[src] - s[dst]                                   # (E, d)
        r = rel.pow(2).sum(dim=-1).clamp(min=1e-12).sqrt()     # (E,)
        R = self.rbf(r)                                          # (E, B)

        # (3) 2-body message
        msg_in = torch.cat([z_src, z_dst, R, rel], dim=-1)     # (E, 2K+B+d)
        m = self.msg_net(msg_in)                                 # (E, F)

        # (4) h⁽¹⁾ = Σ_{j ∈ N_k(i)} m_ij   (sum aggregation with index_add)
        h1 = torch.zeros(n, c.feature_dim, device=s.device, dtype=s.dtype)
        h1.index_add_(0, src, m)                                # (N, F)

        # (5) Higher-body features
        feats: list[Tensor] = [h1]

        if c.body_order >= 3:
            assert self.body3_net is not None
            h1_norm = self.norm1(h1) if self.norm1 is not None else h1
            h2_raw = h1_norm * h1_norm                           # elementwise product
            h2 = self.body3_net(h2_raw)
            feats.append(h2)

        if c.body_order >= 4:
            assert self.body4_net is not None
            h1_norm = self.norm1(h1) if self.norm1 is not None else h1
            h3_raw = h1_norm * h1_norm * h1_norm
            h3 = self.body4_net(h3_raw)
            feats.append(h3)

        # (6) Per-agent readout
        u_in = torch.cat([*feats, z], dim=-1)                   # (N, readout_in)
        u_i = self.readout(u_in).squeeze(-1)                    # (N,)

        # (7) V_pairwise = sum of per-agent potentials
        return u_i.sum()


# ─────────────────────────────────────────────────────────────────────────────
# Factory helper (called by EcoMDSimulator)
# ─────────────────────────────────────────────────────────────────────────────


def build_mace_lite(
    d_state: int,
    k: int,
    hidden: int,
    body_order: int,
    n_classes: int,
    n_rbf: int,
    knn_refresh: int,
    use_layernorm: bool = True,
) -> MACELitePotential:
    cfg = MACELiteConfig(
        d_state=d_state,
        k=k,
        hidden=hidden,
        feature_dim=hidden,      # keep F = hidden for simplicity
        n_classes=n_classes,
        n_rbf=n_rbf,
        body_order=body_order,
        knn_refresh=knn_refresh,
        use_layernorm=use_layernorm,
    )
    return MACELitePotential(cfg)
