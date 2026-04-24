"""EcoMD v2 — market-microstructure-derived equivariant potential.

Design derived from 5 market symmetries (plan §SE(3) 无关性 §推导 5 步):

1. **Permutation-within-type**: type-label-conditional permutation invariance.
   Agents with the same τ are exchangeable; agents with different τ are not.
   Reference: Lux-Marchesi 1999, Cont-Bouchaud 2000, Bornholdt 2001.

2. **Log-price gauge invariance**: if s_i[0] is a log-price, then
   s_i[0] → s_i[0] + c must leave all forces unchanged. Enforced
   architecturally: pair kernel φ only sees Δs_ij = s_i − s_j.
   Reference: Ilinski 2001 gauge theory of finance.

3. **Kyle global coupling**: price-impact scales with aggregate demand
   (Kyle 1985). Implemented as V_kyle = λ · ||Σ_i π_θ(s_i, τ_i)||²
   with λ learnable and signed (can go negative for herding regimes).

4. **Type-typed pair coupling**: interactions between fundamentalists and
   chartists differ from fundamentalist-fundamentalist interactions
   (Lux-Marchesi 1999). Implemented as a learned K × K coupling matrix
   T_θ[τ_i, τ_j] multiplying each pair kernel output.

5. **Stochastic pair sampling**: inherits v0.9 SPS — random k-partner
   subsample per agent per step, rescaled by (N-1)/(2k) for unbiased
   estimate of the full-pair potential at O(N·k) memory.

Self-excitation (Hawkes) lives in :mod:`ecomd.models.price_formation` and is
orthogonal to this file.
"""

from __future__ import annotations

from dataclasses import dataclass

import torch
import torch.nn as nn
from torch import Tensor


# ─────────────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class EcoMDv2Config:
    d_state: int = 32
    hidden: int = 64
    # Type structure
    k_types: int = 4                      # number of agent types (fundamentalist,
                                           #   chartist, noise, MM analogue)
    d_type_emb: int = 8                    # dim of learned type embedding
    # Pair kernel
    k_random: int = 50                     # SPS random partners per agent per step
    # Kyle global term
    kyle_enabled: bool = True
    d_pi: int = 4                          # per-agent demand-contribution dim
    kyle_lambda_init: float = 0.01         # initial λ for V_kyle = λ·||Σπ||²
    kyle_lambda_learnable: bool = True
    # Gauge enforcement
    gauge_axis: int = 0                    # which state axis is log-price (gauge-inv)
                                           # -1 to disable gauge; default s[0].
    # Tunable knobs (added 2026-04-25 for quick-tune + H20 ablation)
    phi_init_gain: float = 0.5             # xavier gain for phi_net (pair kernel)
    pi_init_gain: float = 0.5              # xavier gain for pi_net (Kyle demand-contrib)
    T_offdiag_init: float = 0.1            # init scale for off-diagonal entries of T
                                           # (diagonal init = 1.0 kept)


# ─────────────────────────────────────────────────────────────────────────────
# Type embedding + persistent label buffer (managed by EcoMDv2Potential)
# ─────────────────────────────────────────────────────────────────────────────


class TypeEmbedding(nn.Module):
    """Persistent categorical type labels + learned embedding.

    Type labels are registered as a buffer (not a parameter) and do not move
    with agent state. They're sampled uniformly over {0..K-1} at __init__
    and stay fixed across rollouts. This is key: unlike v1's state-derived
    soft types, labels here are **persistent identity**, so Kyle-style
    pair coupling T[τ_i, τ_j] is stable across time.

    Seed the label sampling via the ``torch.Generator`` passed at init,
    so different simulator instances get reproducible label assignments.
    """

    def __init__(self, n_agents: int, k_types: int, d_type_emb: int,
                 generator: torch.Generator | None = None) -> None:
        super().__init__()
        self.n_agents = n_agents
        self.k_types = k_types
        self.d_type_emb = d_type_emb
        # Persistent label buffer
        if generator is not None:
            labels = torch.randint(0, k_types, (n_agents,), generator=generator)
        else:
            labels = torch.randint(0, k_types, (n_agents,))
        self.register_buffer("labels", labels.long(), persistent=True)
        # Learnable embedding matrix (K, d_type_emb)
        self.embedding = nn.Embedding(k_types, d_type_emb)
        nn.init.xavier_uniform_(self.embedding.weight, gain=0.5)

    def forward(self) -> tuple[Tensor, Tensor]:
        """Return (labels[N], embeddings[N, d_type_emb])."""
        emb = self.embedding(self.labels)       # (N, d_type_emb)
        return self.labels, emb

    def resample_labels(self, generator: torch.Generator | None = None) -> None:
        """Re-draw the persistent labels; useful for ablation but not default."""
        device = self.labels.device
        new_labels = torch.randint(
            0, self.k_types, (self.n_agents,),
            device=device,
            generator=generator,
        ).long()
        self.labels.copy_(new_labels)


# ─────────────────────────────────────────────────────────────────────────────
# Random edge sampling (reused from v0.9 SPS design)
# ─────────────────────────────────────────────────────────────────────────────


def _sample_edges(n: int, k: int, device: torch.device) -> Tensor:
    """Return (2, N·k) long tensor of random (src, dst) pairs with src != dst.

    Uniform sampling per-row via torch.rand + topk (drops self via -inf). Same
    helper as :class:`ecomd.models.potentials.StochasticPairwisePotential`.
    """
    k_eff = min(k, n - 1)
    rand = torch.rand(n, n, device=device)
    rand.fill_diagonal_(-1.0)
    _, idx = torch.topk(rand, k=k_eff + 1, dim=1, largest=True)
    idx = idx[:, :k_eff]
    src = torch.arange(n, device=device).unsqueeze(1).expand(n, k_eff).reshape(-1)
    dst = idx.reshape(-1)
    return torch.stack([src, dst], dim=0)


# ─────────────────────────────────────────────────────────────────────────────
# Kyle global term: V_kyle = λ · ||Σ_i π_θ(s_i, τ_i)||²
# ─────────────────────────────────────────────────────────────────────────────


class KyleGlobalPotential(nn.Module):
    """Kyle-style aggregate-demand potential.

    V_kyle(s, τ) = λ · ||(1/N) · Σ_i π_θ(s_i, τ_i)||²

    ``π_θ`` is a learned per-agent "demand contribution" in R^{d_pi}, taking
    (state, type_embedding) → vector. The (1/N) normalization makes V scale
    intensive — λ interpretable across different N.

    λ is a learnable scalar (signed), initialised near 0. Training decides
    whether it's positive (anti-herding) or negative (herding).
    """

    def __init__(self, d_state: int, d_type_emb: int, d_pi: int, hidden: int,
                 lambda_init: float = 0.01, lambda_learnable: bool = True,
                 init_gain: float = 0.5) -> None:
        super().__init__()
        self.d_pi = d_pi
        self.pi_net = nn.Sequential(
            nn.Linear(d_state + d_type_emb, hidden),
            nn.SiLU(),
            nn.Linear(hidden, d_pi),
        )
        for m in self.pi_net.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight, gain=init_gain)
                nn.init.zeros_(m.bias)
        # λ as a raw scalar; learnable or buffer
        if lambda_learnable:
            self.lambda_raw = nn.Parameter(torch.tensor(float(lambda_init)))
        else:
            self.register_buffer("lambda_raw", torch.tensor(float(lambda_init)))

    def forward(self, s: Tensor, type_emb: Tensor, gauge_axis: int = -1) -> Tensor:
        """Returns V_kyle scalar.

        If ``gauge_axis >= 0``, the corresponding state axis is mean-centered
        before being fed to ``π_θ``, so that a uniform shift s_i[axis] += c
        for all agents leaves the potential invariant (log-price gauge).
        """
        if gauge_axis >= 0:
            s_for_pi = s.clone()
            col = s[:, gauge_axis] - s[:, gauge_axis].mean()
            s_for_pi = torch.cat([
                s_for_pi[:, :gauge_axis], col.unsqueeze(1), s_for_pi[:, gauge_axis + 1:]
            ], dim=-1)
        else:
            s_for_pi = s
        # π_i = MLP([s_i_gauge, τ_embed_i]) ∈ R^{d_pi}
        inp = torch.cat([s_for_pi, type_emb], dim=-1)          # (N, d_state + d_type_emb)
        pi = self.pi_net(inp)                                  # (N, d_pi)
        n = pi.shape[0]
        agg = pi.sum(dim=0) / max(n, 1)                        # (d_pi,) — mean, scale-inv
        return self.lambda_raw * (agg * agg).sum()             # scalar


# ─────────────────────────────────────────────────────────────────────────────
# Typed relational pair kernel with gauge enforcement
# ─────────────────────────────────────────────────────────────────────────────


class TypedRelationalPotential(nn.Module):
    """Pair-sum potential with learned type-coupling matrix T and gauge-inv input.

    V_rel(s, τ) = (N-1)/(2k) · Σ_{(i,j) ∈ E_random} T_θ[τ_i, τ_j] · φ_θ(Δs_ij, τ_i, τ_j)

    where Δs_ij = s_i − s_j is the **only** state-dependent input (so the
    kernel is automatically invariant under log-price gauge s_i[0] += c).
    Note: we use full Δs (all d_state dims) but the gauge axis can be optionally
    zeroed out from s before constructing Δs — see ``gauge_axis``.

    ``T_θ`` is a K × K learnable matrix applied as a scalar multiplier per edge.
    Initialisation: T ≈ 1/K·ones so no type pair dominates at init.
    """

    def __init__(self, d_state: int, k_types: int, d_type_emb: int,
                 hidden: int, k_random: int,
                 phi_init_gain: float = 0.5,
                 T_offdiag_init: float = 0.1) -> None:
        super().__init__()
        self.d_state = d_state
        self.k_random = k_random
        # φ_θ takes Δs_ij + τ_emb_i + τ_emb_j → scalar per edge
        phi_in = d_state + 2 * d_type_emb
        self.phi_net = nn.Sequential(
            nn.Linear(phi_in, hidden),
            nn.SiLU(),
            nn.Linear(hidden, hidden),
            nn.SiLU(),
            nn.Linear(hidden, 1),
        )
        for m in self.phi_net.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight, gain=phi_init_gain)
                nn.init.zeros_(m.bias)
        # T_θ: K × K learnable coupling matrix. Diag = 1, off-diag controlled by init scale.
        self.T = nn.Parameter(torch.eye(k_types) + T_offdiag_init * torch.randn(k_types, k_types))

    def forward(self, s: Tensor, type_labels: Tensor, type_emb: Tensor,
                gauge_axis: int = 0) -> Tensor:
        """V_rel as a scalar."""
        n = s.shape[0]
        edges = _sample_edges(n, self.k_random, s.device).detach()
        src, dst = edges[0], edges[1]                          # (E,)
        E = src.shape[0]

        # Δs with optional gauge: zero out the gauge_axis BEFORE subtraction
        # is incorrect (s_i - s_j on that axis IS already gauge-invariant).
        # Leaving full Δs works: s_i[0] - s_j[0] is gauge-inv automatically.
        # But if we want to drop the log-price axis entirely from the force,
        # use gauge_axis = -1 logic (handled above). Here we keep full Δs.
        delta_s = s[src] - s[dst]                              # (E, d_state)

        # Type embeddings for src and dst
        tau_src = type_emb[src]                                # (E, d_type_emb)
        tau_dst = type_emb[dst]                                # (E, d_type_emb)

        # Symmetric kernel: φ(Δs, τ_i, τ_j) + φ(-Δs, τ_j, τ_i), averaged
        inp_ij = torch.cat([delta_s, tau_src, tau_dst], dim=-1)   # (E, d+2K')
        inp_ji = torch.cat([-delta_s, tau_dst, tau_src], dim=-1)
        phi_ij = self.phi_net(inp_ij).squeeze(-1)              # (E,)
        phi_ji = self.phi_net(inp_ji).squeeze(-1)              # (E,)
        phi = 0.5 * (phi_ij + phi_ji)

        # Type-coupling multiplier per edge: T[τ_i, τ_j]
        # Symmetrize T for stability: T_sym = 0.5*(T + T.T)
        T_sym = 0.5 * (self.T + self.T.T)
        coupling = T_sym[type_labels[src], type_labels[dst]]   # (E,)

        # Weighted edge sum, with unbiased rescaling (N-1)/(2k)
        scale = (n - 1) / (2.0 * self.k_random)
        return scale * (coupling * phi).sum()


# ─────────────────────────────────────────────────────────────────────────────
# Top-level EcoMD v2 potential (Kyle + Typed + Gauge in one module)
# ─────────────────────────────────────────────────────────────────────────────


class EcoMDv2Potential(nn.Module):
    """Full EcoMD v2 potential = V_kyle + V_relational.

    Persistent type labels + type embedding live here. Forward signature
    matches the ``Potential`` protocol used by ConservativePotential.
    """

    def __init__(self, n_agents: int, config: EcoMDv2Config | None = None,
                 type_gen: torch.Generator | None = None) -> None:
        super().__init__()
        self.cfg = config or EcoMDv2Config()
        c = self.cfg
        self.n_agents = n_agents

        # Persistent types + learned embedding
        self.types = TypeEmbedding(n_agents, c.k_types, c.d_type_emb, generator=type_gen)

        # Kyle global term
        self.kyle = KyleGlobalPotential(
            d_state=c.d_state, d_type_emb=c.d_type_emb, d_pi=c.d_pi,
            hidden=c.hidden, lambda_init=c.kyle_lambda_init,
            lambda_learnable=c.kyle_lambda_learnable,
            init_gain=c.pi_init_gain,
        ) if c.kyle_enabled else None

        # Typed relational pair term
        self.rel = TypedRelationalPotential(
            d_state=c.d_state, k_types=c.k_types, d_type_emb=c.d_type_emb,
            hidden=c.hidden, k_random=c.k_random,
            phi_init_gain=c.phi_init_gain,
            T_offdiag_init=c.T_offdiag_init,
        )

    def forward(self, s: Tensor, context: Tensor | None = None) -> Tensor:
        del context  # v2 pair-potential is context-free; context handled by V_external
        labels, emb = self.types()                             # (N,) and (N, d_type_emb)
        v = s.new_zeros(())
        if self.kyle is not None:
            v = v + self.kyle(s, emb, gauge_axis=self.cfg.gauge_axis)
        v = v + self.rel(s, labels, emb, gauge_axis=self.cfg.gauge_axis)
        return v


__all__ = [
    "EcoMDv2Config",
    "EcoMDv2Potential",
    "KyleGlobalPotential",
    "TypedRelationalPotential",
    "TypeEmbedding",
]
