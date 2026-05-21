"""Modern-Hopfield regime selector (Track B-α, Paper A "solve" half).

Replaces the black-box ``RegimeGRU`` with an attention-based regime
attractor module. Hypothesis (paper_a_next_steps_2026-05-21.md §5): the
v3 Pareto ceiling at 5.5-5.6/11 is partly driven by *mechanism
interference* — agents in different market regimes need different
forces, but a single mechanism mix applied uniformly creates conflicting
gradients. Modern-Hopfield (Ramsauer et al. 2020) lets regime states be
attractors of an energy landscape: explicit, interpretable, with sharp
attention enabling each regime to use a near-pure mechanism subset.

Design (matches paper_a_next_steps §5.2):

  q_t   = MLP_q(market_stats_t)              ∈ R^{d_regime}
  Z     = [z_1, ..., z_K]                    ∈ R^{K×d_regime}   (learned)
  α_t   = softmax(q_t @ Z^T · β / √d_regime) ∈ Δ^{K-1}
  h_t   = α_t @ Z                            ∈ R^{d_regime}

The K learned prototypes ARE the regimes. The same downstream
``RegimeReadHead`` plumbing (γ_mult, T_mult, κ_mult per h_regime) is
reused unchanged — the "K mechanism mixes" claim in the spec is delivered
implicitly: for sharp β, h_t ≈ z_{argmax(q·Z^T)}, so the read heads
produce one of K distinct (γ, T, κ) modulations.

Interface matches ``RegimeGRU`` / ``DiscreteRegimeGRU`` (init_h, maybe_step,
read) so this is a drop-in replacement selected via ``regime_kind="hopfield"``
in :class:`EcoMDConfig`.

Pure feed-forward (no recurrence): the persistent state is just the
last-computed h embedding. Update cadence still gated by ``update_every``
to keep the slow-regime time-scale assumption.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor


@dataclass(frozen=True)
class HopfieldRegimeConfig:
    """Hopfield-attention regime selector hyperparameters.

    Args:
        d_regime: embedding dim — must match read-head expectations.
        n_prototypes: K. Spec recommends K∈{4, 8}; K=4 is a reasonable
            first pilot (Hamilton-style "expansion / contraction /
            recession / recovery" macro regimes).
        d_input: market_stats input dim. Matches RegimeGRU's d_input=4.
        update_every: step gating, identical semantics to RegimeGRU.
        beta: softmax inverse temperature. Spec recommends β=8 (sharp
            Hopfield); lower β diffuses attention across multiple
            prototypes (smoother regime transitions).
        query_hidden: hidden dim of the query MLP.
        init_gain: xavier_uniform gain for prototypes and query MLP.
            Small init ⇒ near-uniform attention ⇒ ≈identity regime read
            for untrained networks (matches RegimeGRU's near-zero init
            philosophy).
    """

    d_regime: int = 16
    n_prototypes: int = 4
    d_input: int = 4
    update_every: int = 8
    beta: float = 8.0
    query_hidden: int = 16
    init_gain: float = 0.1


class HopfieldRegime(nn.Module):
    """Modern-Hopfield regime attractor module.

    State: ``h ∈ R^d_regime`` — the most recently attended embedding.
    Update: every ``update_every`` simulator steps,
        h ← softmax(MLP_q(stats) @ Z^T · β / √d) @ Z
    """

    def __init__(self, config: HopfieldRegimeConfig | None = None) -> None:
        super().__init__()
        self.cfg = config or HopfieldRegimeConfig()
        if self.cfg.n_prototypes < 2:
            raise ValueError(
                f"n_prototypes must be ≥ 2, got {self.cfg.n_prototypes}"
            )
        if self.cfg.beta <= 0:
            raise ValueError(f"beta must be > 0, got {self.cfg.beta}")

        # Learned prototype bank Z ∈ R^(K, d_regime). Small init ⇒ near-
        # uniform energy → near-uniform attention → ≈no-op at start.
        self.prototypes = nn.Parameter(
            torch.randn(self.cfg.n_prototypes, self.cfg.d_regime)
            * self.cfg.init_gain
        )

        # Query MLP: market_stats → d_regime vector for prototype scoring.
        self.query_mlp = nn.Sequential(
            nn.Linear(self.cfg.d_input, self.cfg.query_hidden),
            nn.SiLU(),
            nn.Linear(self.cfg.query_hidden, self.cfg.d_regime),
        )
        for m in self.query_mlp.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight, gain=self.cfg.init_gain)
                nn.init.zeros_(m.bias)

    # ── RegimeGRU-compatible interface ─────────────────────────────────

    def init_h(self, device: torch.device, dtype: torch.dtype) -> Tensor:
        return torch.zeros(self.cfg.d_regime, device=device, dtype=dtype)

    def maybe_step(self, h: Tensor, step_idx: int, market_stats: Tensor) -> Tensor:
        """Recompute h via Hopfield attention every ``update_every`` steps."""
        if step_idx % self.cfg.update_every != 0:
            return h
        q = self.query_mlp(market_stats)                     # (d_regime,)
        # Score q against each prototype z_k. sqrt(d) normalisation keeps
        # scores ≈ O(1) at init; β scales sharpness independently.
        scores = (q @ self.prototypes.T) * (
            self.cfg.beta / math.sqrt(self.cfg.d_regime)
        )                                                     # (K,)
        alpha = torch.softmax(scores, dim=-1)                # (K,) on simplex
        h_new = alpha @ self.prototypes                      # (d_regime,)
        return h_new

    def read(self, h: Tensor) -> Tensor:
        """Identity — h is already in d_regime space (unlike DiscreteRegimeGRU
        whose persistent state is logits)."""
        return h

    # ── Diagnostics & regularization ───────────────────────────────────

    def attention(self, market_stats: Tensor) -> Tensor:
        """Return the soft attention vector α ∈ Δ^{K-1} for a given
        market_stats. Used for B-α.4 attribution plots (paper Figure 2)."""
        q = self.query_mlp(market_stats)
        scores = (q @ self.prototypes.T) * (
            self.cfg.beta / math.sqrt(self.cfg.d_regime)
        )
        return torch.softmax(scores, dim=-1)

    def prototype_collapse_loss(self) -> Tensor:
        """Mean off-diagonal pairwise cosine similarity across K prototypes.

        Used as a regularizer (or just a diagnostic): if this is ≥ 0.9 at
        the end of training, the prototypes have collapsed and the
        Hopfield is effectively K=1 (a regression to no-regime). Spec
        kill criterion (paper_a_next_steps §5.4): mean cosine sim > 0.9
        → stop and demote B-α to future work.
        """
        Z = self.prototypes
        Zn = F.normalize(Z, dim=-1, eps=1e-8)
        sim = Zn @ Zn.T                                       # (K, K)
        K = Z.shape[0]
        mask = ~torch.eye(K, dtype=torch.bool, device=Z.device)
        return sim[mask].mean()
