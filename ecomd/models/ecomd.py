"""EcoMD v0 simulator — composes potentials + integrator + price formation.

The simulator is deliberately thin: heavy lifting happens in the components,
this class just orchestrates the per-step loop and wires forces into the
integrator.

Usage
-----
>>> sim = EcoMDSimulator(n_agents=200, d_state=32)
>>> traj = sim.run(n_steps=500, seed=0)
>>> traj.log_returns_np().shape
(500,)

For training, use ``rollout_chunk`` to get a differentiable trajectory of a
chunk of steps (state and price are both differentiable). ``run`` is the
no-grad inference entry point used by evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import torch
import torch.nn as nn
from torch import Tensor

from ..physics.integrator import LangevinIntegrator, OverdampedLangevin
from ..physics.observables import EcoMDTrajectory, TrajectoryRecorder
from .agent_memory import AgentMemoryConfig, AgentMemoryGRU
from .ecomd_v2 import EcoMDv2Config, EcoMDv2Potential
from .global_state import GlobalStateConfig, GlobalStateGRU
from .isab_pairwise import ISABPairwisePotential
from .mace_lite import MACELitePotential, build_mace_lite
from .regime_latent import (
    DiscreteRegimeGRU,
    DiscreteRegimeGRUConfig,
    RegimeGRU,
    RegimeGRUConfig,
    RegimeReadHead,
)
from .potentials import (
    StochasticPairwisePotential,
    ConservativePotential,
    DissipationParams,
    DissipationPotential,
    ExternalPotential,
    PowerLawExternalPotential,
    PairwisePotential,
    conservative_forces,
    dissipative_forces,
)
from .price_formation import (
    PriceFormation,
    PriceState,
    build_price_formation,
)


@dataclass(frozen=True)
class EcoMDConfig:
    n_agents: int = 200
    d_state: int = 32
    hidden: int = 64
    dt: float = 0.01
    gamma_init: float = 1.0
    temperature_init: float = 0.1
    init_state_scale: float = 0.1
    price_formation: str = "excess_demand"   # 'excess_demand' or 'readout'
    price_formation_kwargs: dict[str, Any] = field(default_factory=dict)
    lam_dissipation: float = 0.01
    learn_gamma: bool = True
    learn_temperature: bool = True
    noise_dist: str = "normal"               # 'normal' | 't' (Student-t, v0.6+) | 'levy' (α-stable, v4)
    noise_df: int = 5                        # only used when noise_dist='t'
    # V4 mechanism 1 — symmetric α-stable (Lévy) noise via Chambers-Mallows-
    # Stuck. α=2 ≈ Normal; α<2 is heavy-tailed (infinite variance for α<2).
    # Targets hill_tail_index (target band [2, 4]); the Hill estimator
    # recovers α directly when noise dominates the return distribution.
    # Clipped at ±levy_clip to keep Langevin updates finite — set high enough
    # to preserve heavy-tail signal but low enough that single rare draws
    # don't blow up downstream eval (GARCH residual fits etc.).
    noise_levy_alpha: float = 1.7
    noise_levy_clip: float = 50.0
    # V4 mechanism 2 — asymmetric drag γ(Δp). γ_eff = γ · (1 − α·sign(Δp)),
    # so down moves shrink γ (liquidity vacuum, larger noise per unit time)
    # while up moves enlarge γ (slower regime). Targets leverage_effect
    # (target band [-6, -0.5], current pass ~30%). α∈(-1, 1); α=0 disables.
    asym_drag_alpha: float = 0.0
    # V4 mechanism 3 — memory kernel. Noise scale modulates by
    # (1 + memory_kernel_strength · EMA_λ(|Δs|)), where the EMA decays at
    # rate λ. Targets zumbach_asymmetry (current pass ~10%) and
    # acf_squared_returns. Both knobs zero → no-op.
    memory_kernel_lambda: float = 0.0
    memory_kernel_strength: float = 0.0
    # B-round mechanism 1 — microstructure / bid-ask bounce noise. Replaces
    # the integrator's ε with ε_eff = ε - rho · ε_{t-1}, inducing a small
    # lag-1 NEGATIVE autocorrelation in returns that mimics real-world
    # market microstructure. Targets autocorr_returns (target band
    # [-0.1, 0.20]; v3 baseline mean +0.38). Default 0.0 disables.
    microstructure_rho: float = 0.0
    # M1.1 — AR(1) drift whitening. The v3 baseline shows AR(1) ρ̂≈0.9 in
    # returns (every cell across Branches D/E/F μ ≈ 0.4 vs band [-0.1, 0.2]),
    # caused by smooth force-field drift propagating through price formation.
    # We subtract `ar1_whiten_strength` × EMA_λ(drift) from the per-step
    # drift, acting as a high-pass filter that breaks the autocorrelation
    # chain. λ controls EMA memory; strength controls how much to subtract.
    # Targets autocorr_returns architectural floor. Both = 0 → no-op.
    ar1_whiten_lambda: float = 0.0
    ar1_whiten_strength: float = 0.0
    # M1.2 — Zumbach causal-asymmetry feedback. The v3 baseline shows
    # zumbach_asymmetry μ < 0 (wrong sign vs band [+0.001, +0.5]) for every
    # cell, because no mechanism produces the time-asymmetric coupling
    # required (past coarse vol → future fine vol > reverse). We boost
    # noise scale by an EMA of past r² (price-level), past-only by
    # construction. mode='abs' uses r²; mode='downside' uses max(0,-r)²
    # (leverage-asymmetric variant). Both = 0 → no-op.
    zumbach_feedback_lambda: float = 0.0
    zumbach_feedback_strength: float = 0.0
    zumbach_feedback_mode: str = "abs"  # 'abs' | 'downside'
    # B-round mechanism 4 — power-law external potential. Replaces the MLP
    # external potential with V_ext(s) = w_mlp · MLP + w_pow · |s|^α / α.
    # Sub-linear restoring force at large |s| produces fat-tailed return
    # distributions intrinsically (not just through noise). Targets
    # hill_tail_index (target band [2, 4]; v3 / Lévy baselines fail).
    # Default off reproduces v3 behavior exactly.
    power_law_external: bool = False
    power_law_alpha: float = 1.5
    power_law_w_pow: float = 0.5
    power_law_w_mlp: float = 1.0
    # B-round mechanism 3 — discrete Gumbel-softmax regime. Replaces the
    # continuous regime GRU with K-state discrete switching. Each state
    # has its own learned d_regime embedding consumed by RegimeReadHead.
    # Targets aggregational_gaussianity (band [10, 200]; v4 winners hit
    # 300+ because no quiet regime exists). When enabled, requires
    # regime_enabled=True (the simulator branches on the new flag inside
    # the regime block). Default off reproduces continuous-GRU behavior.
    regime_discrete_enabled: bool = False
    regime_n_states: int = 3
    regime_gumbel_tau: float = 1.0
    # v1 (MACE-lite) settings — only used when pairwise_kind == "mace_lite"
    pairwise_kind: str = "mlp"               # 'mlp' (v0.x) or 'mace_lite' (v1+)
    mace_k: int = 16                         # k-NN neighbours
    mace_body_order: int = 2                 # 2, 3, or 4
    mace_n_classes: int = 4                  # K agent-type classes
    mace_n_rbf: int = 8                      # Gaussian RBF centers
    mace_knn_refresh: int = 10               # steps between k-NN recomputes
    mace_use_layernorm: bool = True          # LN on h^(1) before tensor products (ablation)
    # F1-F4 force-magnitude fixes — defaults preserve original v1 behaviour
    mace_readout_mode: str = "per_node"      # 'per_node' | 'per_edge' | 'hybrid'
    mace_readout_multiplier: float = 1.0     # F1: multiply V output by this
    mace_readout_init_gain: float = 0.5      # F2: xavier gain for readout last layer
    # v0.9 StochasticPairwisePotential — random pair sampling for scaling
    sps_k_random: int = 50                   # random partners per agent per step
    sps_resample_per_step: bool = True       # resample edges every forward?
    # v2 EcoMDv2Potential — market-microstructure-derived architecture
    v2_k_types: int = 4                      # number of persistent agent types
    v2_d_type_emb: int = 8                   # learned type embedding dim
    v2_d_pi: int = 4                         # Kyle per-agent demand-contrib dim
    v2_k_random: int = 50                    # SPS random partners in v2 relational layer
    v2_kyle_enabled: bool = True             # include Kyle global (λ·||Σπ||²)?
    v2_kyle_lambda_init: float = 0.01        # initial Kyle λ
    v2_kyle_lambda_learnable: bool = True
    v2_gauge_axis: int = 0                   # state axis enforced gauge-invariant (log-price)
    v2_type_seed: int = 42                   # seed for initial type-label sampling
    v2_phi_init_gain: float = 0.5            # xavier gain for pair kernel MLP
    v2_pi_init_gain: float = 0.5             # xavier gain for Kyle π MLP
    v2_T_offdiag_init: float = 0.1           # init scale for T off-diagonal
    v2_gauge_enforce: bool = False           # if True: Δs only pair input; False: full (s_i, s_j)
    v2_T_init_mode: str = "eye_plus_noise"   # 'eye_plus_noise' | 'ones' | 'uniform'
    # v3 regime-switching slow latent (P3) — non-stationary regime carrier
    regime_enabled: bool = False             # off = legacy v0/v1 behavior
    regime_d: int = 16                       # latent dimension
    regime_update_every: int = 8             # GRU stepped every k sim steps
    regime_init_gain: float = 0.1            # init scale for GRU
    regime_modulate_gamma: bool = True       # γ_eff = γ * head_γ(h_regime)
    regime_modulate_temp: bool = True        # T_eff = T * head_T(h_regime)
    regime_modulate_kappa: bool = True       # Hawkes excitation_mul = head_κ(h_regime)
    # v3 two-population per-type γ, T (P4) — heterogeneous Langevin per agent type.
    # Uses v2's persistent K=4 type embedding; no K×K coupling needed.
    # If twopop_enabled and pairwise_kind != ecomd_v2, we still build a type
    # vector of length k_types using v2_type_seed.
    twopop_enabled: bool = False
    twopop_gamma_scale: tuple = (1.0, 1.0, 1.0, 1.0)  # per-type multiplier on γ
    twopop_temp_scale: tuple  = (1.0, 1.0, 1.0, 1.0)  # per-type multiplier on T
    # BPTT gradient checkpointing (paper-a-loss-redesign 2026-04-26):
    # 0 = off (store all activations, original behavior).
    # K > 0 = wrap rollout_chunk in groups of K steps via
    #   torch.utils.checkpoint(use_reentrant=False) — but this has been
    #   shown empirically (2026-04-27) to fail for EcoMD because
    #   create_graph=True in conservative_forces pins V-graphs across
    #   group boundaries via the s_next.grad_fn chain.
    # Recommended: leave at 0 unless you understand the OOM tradeoff.
    bptt_checkpoint_every: int = 0
    # v4 adiabatic timescale separation. When > 1, each outer step runs
    # ``inner_steps_per_price`` agent-dynamics steps (force + integrator)
    # against a frozen slow state, then ONE price formation step. Targets
    # AR(1) drift: per outer step the return is the sum of N independent
    # agent walks, decorrelating across outer steps.
    inner_steps_per_price: int = 1
    # ── feature/arch-extensions (2026-04-28) — six architectural tiers ──────
    # All default OFF: when all flags below take their defaults, simulator
    # output is bit-identical to the pre-arch-extensions baseline.
    #
    # Tier 1.1 — Per-agent GRU memory. Each agent carries h_i ∈ R^d_memory
    #   updated every `agent_memory_update_every` sim steps from (s_i,
    #   log_return, vol). Aggregated read enters the external potential's
    #   context. Hypothesis: helps DFA Hurst, zumbach, autocorr facts.
    agent_memory_enabled: bool = False
    agent_memory_d: int = 16
    agent_memory_update_every: int = 1
    # Tier 1.2 — Heterogeneous (type-aware) pairwise kernel heads. Routes
    #   each pair (src, dst) to one of K² last-layer heads based on
    #   (type_src, type_dst). Requires twopop_enabled=True (the type_idx
    #   buffer is reused). Hypothesis: helps volume_corr, gain_loss.
    pair_heterogeneous_heads: bool = False
    # Tier 1.3 — Extra pair features. "none" reproduces baseline behavior.
    #   "distance" appends ||Δs||, "inner_prod" appends ⟨s_i, s_j⟩,
    #   "signed_diff" replaces |Δs| with Δs (asymmetric), "all" combines.
    pair_features_extra: str = "none"
    # Pair-MLP input LayerNorm — REQUIRED for stable inference rollouts when
    # using ``pair_features_extra='all'`` or extra-feature variants. Without
    # it, the MLP overfits to the small-state training distribution
    # (init_state_scale ~ 0.1, chunk_steps=24) and extrapolates badly during
    # the 4000-step inference rollout, where state drifts out of the training
    # regime → forces explode → NaN. Default OFF preserves baseline
    # equivalence; tier_1_3_features_all should set this True.
    pair_input_layernorm: bool = False
    # Tier 2.1 — Compound-Poisson jumps. Training mode uses a tanh-coupled
    #   drift correction; inference mode samples discrete jumps. Both
    #   zero ⇒ no-op. Hypothesis: helps hill, gain_loss, autocorr.
    jump_lambda: float = 0.0
    jump_scale: float = 0.0
    # Tier 2.2 — Multi-timescale per-agent mask. A `timescale_fast_frac`
    #   fraction of agents always update; the rest update every
    #   `timescale_slow_freq` steps. All agents always contribute to forces.
    #   Hypothesis: helps DFA, zumbach (multi-scale temporal structure).
    multi_timescale_enabled: bool = False
    timescale_fast_frac: float = 0.8
    timescale_slow_freq: int = 4
    # Tier 3.1 — ISAB attention pairwise. Activate by setting
    #   pairwise_kind="isab". Memory O(N·M) via M learnable inducing points.
    isab_m_inducing: int = 64
    isab_n_heads: int = 4
    # Tier 4.1 — MEGNet-style global state. Distinct from h_regime
    #   (modulates γ, T, κ scalars) and h_agent (per-agent memory): u is a
    #   global vector updated from aggregated agent state + market scalars,
    #   and is concatenated INTO the pair kernel + external context so the
    #   V surface itself is shaped by global "phase". Hypothesis: lets one
    #   network instantiate different ``φ(s_i, s_j)`` shapes at different
    #   times — addresses the orthogonal-basin ceiling directly.
    global_state_enabled: bool = False
    global_state_d: int = 16
    global_state_update_every: int = 1
    global_state_into_pair: bool = True   # if False, u only feeds external
    # Tier 4.2 — dynamic graph via learned soft edge gating on the SPS pool.
    #   Only consumed when pairwise_kind == "stochastic_mlp". Each random
    #   edge (i, j) is weighted by ``w_ij = σ(gate_mlp(s_i, s_j, |Δs|, u))``
    #   and rescaled by 1/gate_init_p so E[w·phi] ≈ E[phi] at init.
    edge_gating_enabled: bool = False
    edge_gating_init_p: float = 0.7
    edge_gating_input_u: bool = True   # if False, gate ignores u even when 4.1 active
    # Custom autograd.Function-based per-step BPTT (Sprint 2, 2026-04-27):
    # When True, replaces ``rollout_chunk``'s standard ``sim.step()`` call
    # with ``EcoMDStepFunction.apply()``. Each step runs forward in
    # ``no_grad`` (no V-graph kept); backward locally rebuilds the V-graph
    # ONE step at a time and propagates gradients via torch.autograd.grad
    # with explicit grad outputs — releases the local graph after each
    # step's backward. Peak memory ≈ ONE step's V-graph (~3.5 GB at
    # N=10K) regardless of chunk_steps. Compute overhead ~2× (forward is
    # cheaper than baseline; backward repeats forward).
    # IMPORTANT: this changes WHERE gradients flow. Trainer's loss must
    # only differentiate ``traj.log_returns`` (the only output that
    # carries grad through the Function chain). The per-step diagnostic
    # channels (states, f_cons, f_diss, f_stoch, velocities) become
    # detached. This matches our actual training loss but breaks tests
    # that try to differentiate other channels.
    bptt_custom_function: bool = False


class EcoMDSimulator(nn.Module):
    """Top-level EcoMD simulator.

    Aggregates a conservative potential (pairwise + external), a dissipative
    potential, a Langevin integrator, and a price-formation mechanism. γ and T
    are optionally learnable scalars.
    """

    def __init__(
        self,
        config: EcoMDConfig | None = None,
        integrator: LangevinIntegrator | None = None,
        price_formation: PriceFormation | None = None,
    ) -> None:
        super().__init__()
        self.cfg = config or EcoMDConfig()
        d = self.cfg.d_state
        # price formation chosen first because external potential needs its context_dim
        self.price_formation: PriceFormation = price_formation or build_price_formation(
            self.cfg.price_formation, d=d, **self.cfg.price_formation_kwargs
        )
        if isinstance(self.price_formation, nn.Module):
            # register as child so its params are included in self.parameters()
            self.add_module("_price_formation_mod", self.price_formation)

        # Tier 1.2: prebuild persistent agent type_idx if either Tier 1.2
        # heads or twopop are enabled. We use the twopop seed for both so
        # heads share types with twopop γ/T (the natural physical reading).
        K_types = len(self.cfg.twopop_gamma_scale)
        type_idx_buf: Tensor | None = None
        if self.cfg.pair_heterogeneous_heads or self.cfg.twopop_enabled:
            gen_t = torch.Generator().manual_seed(self.cfg.v2_type_seed)
            type_idx_buf = torch.randint(0, K_types, (self.cfg.n_agents,), generator=gen_t)

        # Tier 4.1: pairwise modules consume u when both
        # ``global_state_enabled`` AND ``global_state_into_pair`` are True.
        d_global_in_pair = (
            self.cfg.global_state_d
            if (self.cfg.global_state_enabled and self.cfg.global_state_into_pair)
            else 0
        )

        pairwise: nn.Module
        if self.cfg.pairwise_kind == "mlp":
            pairwise = PairwisePotential(d=d, hidden=self.cfg.hidden)
        elif self.cfg.pairwise_kind == "stochastic_mlp":
            if self.cfg.pair_heterogeneous_heads:
                assert type_idx_buf is not None
            pairwise = StochasticPairwisePotential(
                d=d, hidden=self.cfg.hidden,
                k_random=self.cfg.sps_k_random,
                resample_per_step=self.cfg.sps_resample_per_step,
                type_aware_heads=self.cfg.pair_heterogeneous_heads,
                type_idx=type_idx_buf,
                n_types=K_types,
                pair_features_extra=self.cfg.pair_features_extra,
                d_global_in=d_global_in_pair,
                edge_gating=self.cfg.edge_gating_enabled,
                gate_init_p=self.cfg.edge_gating_init_p,
                gate_input_u=self.cfg.edge_gating_input_u,
                input_layernorm=self.cfg.pair_input_layernorm,
            )
        elif self.cfg.pairwise_kind == "isab":
            pairwise = ISABPairwisePotential(
                d=d,
                hidden=self.cfg.hidden,
                m_inducing=self.cfg.isab_m_inducing,
                n_heads=self.cfg.isab_n_heads,
                d_global_in=d_global_in_pair,
            )
        elif self.cfg.pairwise_kind == "ecomd_v2":
            v2_cfg = EcoMDv2Config(
                d_state=d,
                hidden=self.cfg.hidden,
                k_types=self.cfg.v2_k_types,
                d_type_emb=self.cfg.v2_d_type_emb,
                d_pi=self.cfg.v2_d_pi,
                k_random=self.cfg.v2_k_random,
                kyle_enabled=self.cfg.v2_kyle_enabled,
                kyle_lambda_init=self.cfg.v2_kyle_lambda_init,
                kyle_lambda_learnable=self.cfg.v2_kyle_lambda_learnable,
                gauge_axis=self.cfg.v2_gauge_axis,
                phi_init_gain=self.cfg.v2_phi_init_gain,
                pi_init_gain=self.cfg.v2_pi_init_gain,
                T_offdiag_init=self.cfg.v2_T_offdiag_init,
                gauge_enforce=self.cfg.v2_gauge_enforce,
                T_init_mode=self.cfg.v2_T_init_mode,
            )
            type_gen = torch.Generator().manual_seed(self.cfg.v2_type_seed)
            pairwise = EcoMDv2Potential(
                n_agents=self.cfg.n_agents,
                config=v2_cfg,
                type_gen=type_gen,
            )
        elif self.cfg.pairwise_kind == "mace_lite":
            pairwise = build_mace_lite(
                d_state=d,
                k=self.cfg.mace_k,
                hidden=self.cfg.hidden,
                body_order=self.cfg.mace_body_order,
                n_classes=self.cfg.mace_n_classes,
                n_rbf=self.cfg.mace_n_rbf,
                knn_refresh=self.cfg.mace_knn_refresh,
                use_layernorm=self.cfg.mace_use_layernorm,
                readout_mode=self.cfg.mace_readout_mode,
                readout_multiplier=self.cfg.mace_readout_multiplier,
                readout_init_gain=self.cfg.mace_readout_init_gain,
            )
        else:
            raise ValueError(
                f"unknown pairwise_kind {self.cfg.pairwise_kind!r}; "
                f"expected 'mlp' | 'stochastic_mlp' | 'mace_lite' | 'ecomd_v2' | 'isab'"
            )
        ext_ctx_dim = self.price_formation.context_dim
        if self.cfg.agent_memory_enabled:
            ext_ctx_dim += self.cfg.agent_memory_d
        # Tier 4.1: external also consumes u (always, when enabled — the
        # ``global_state_into_pair`` flag only gates the pair side).
        if self.cfg.global_state_enabled:
            ext_ctx_dim += self.cfg.global_state_d
        if self.cfg.power_law_external:
            external = PowerLawExternalPotential(
                d=d, context_dim=ext_ctx_dim, hidden=self.cfg.hidden,
                alpha=self.cfg.power_law_alpha,
                w_pow=self.cfg.power_law_w_pow,
                w_mlp=self.cfg.power_law_w_mlp,
            )
        else:
            external = ExternalPotential(
                d=d, context_dim=ext_ctx_dim, hidden=self.cfg.hidden
            )
        self.potential = ConservativePotential(pairwise, external)
        self.dissipation = DissipationPotential(DissipationParams(lam=self.cfg.lam_dissipation))

        self.integrator = integrator or OverdampedLangevin(
            noise_dist=self.cfg.noise_dist,
            noise_df=self.cfg.noise_df,
            levy_alpha=self.cfg.noise_levy_alpha,
            levy_clip=self.cfg.noise_levy_clip,
            jump_lambda=self.cfg.jump_lambda,
            jump_scale=self.cfg.jump_scale,
            asym_drag_alpha=self.cfg.asym_drag_alpha,
            memory_kernel_lambda=self.cfg.memory_kernel_lambda,
            memory_kernel_strength=self.cfg.memory_kernel_strength,
            microstructure_rho=self.cfg.microstructure_rho,
            ar1_whiten_lambda=self.cfg.ar1_whiten_lambda,
            ar1_whiten_strength=self.cfg.ar1_whiten_strength,
            zumbach_feedback_lambda=self.cfg.zumbach_feedback_lambda,
            zumbach_feedback_strength=self.cfg.zumbach_feedback_strength,
            zumbach_feedback_mode=self.cfg.zumbach_feedback_mode,
        )

        # learnable log-parametrised γ, T (positivity by construction)
        log_gamma = torch.tensor(float(torch.log(torch.tensor(self.cfg.gamma_init))))
        log_T = torch.tensor(float(torch.log(torch.tensor(self.cfg.temperature_init))))
        self.log_gamma = nn.Parameter(log_gamma, requires_grad=self.cfg.learn_gamma)
        self.log_temperature = nn.Parameter(log_T, requires_grad=self.cfg.learn_temperature)

        # v3 regime latent (P3 + P5 T_eff head share infrastructure)
        # When ``regime_discrete_enabled`` is True, swap the continuous
        # GRU for the B-round DiscreteRegimeGRU. State carried as logits
        # of size ``regime_n_states``; read heads consume the d_regime
        # embedding produced by ``regime_gru.read(h)``.
        self.regime_gru: RegimeGRU | DiscreteRegimeGRU | None = None
        self.regime_head_gamma: RegimeReadHead | None = None
        self.regime_head_T: RegimeReadHead | None = None
        self.regime_head_kappa: RegimeReadHead | None = None
        if self.cfg.regime_enabled:
            if self.cfg.regime_discrete_enabled:
                self.regime_gru = DiscreteRegimeGRU(DiscreteRegimeGRUConfig(
                    n_states=self.cfg.regime_n_states,
                    d_regime=self.cfg.regime_d,
                    update_every=self.cfg.regime_update_every,
                    init_gain=self.cfg.regime_init_gain,
                    gumbel_tau=self.cfg.regime_gumbel_tau,
                ))
            else:
                self.regime_gru = RegimeGRU(RegimeGRUConfig(
                    d_regime=self.cfg.regime_d,
                    update_every=self.cfg.regime_update_every,
                    init_gain=self.cfg.regime_init_gain,
                ))
            if self.cfg.regime_modulate_gamma:
                self.regime_head_gamma = RegimeReadHead(self.cfg.regime_d)
            if self.cfg.regime_modulate_temp:
                self.regime_head_T = RegimeReadHead(self.cfg.regime_d)
            if self.cfg.regime_modulate_kappa:
                self.regime_head_kappa = RegimeReadHead(self.cfg.regime_d)

        # v3 two-population per-type γ, T (P4)
        if self.cfg.twopop_enabled:
            K = len(self.cfg.twopop_gamma_scale)
            assert K == len(self.cfg.twopop_temp_scale), \
                "twopop_gamma_scale and twopop_temp_scale must have the same length"
            assert K == K_types, "twopop_gamma_scale length must match K_types prebuild"
            assert type_idx_buf is not None
            self.register_buffer("twopop_type_idx", type_idx_buf, persistent=False)
            self.register_buffer(
                "twopop_gamma_per_type",
                torch.tensor(list(self.cfg.twopop_gamma_scale), dtype=torch.float32),
                persistent=False,
            )
            self.register_buffer(
                "twopop_temp_per_type",
                torch.tensor(list(self.cfg.twopop_temp_scale), dtype=torch.float32),
                persistent=False,
            )
        else:
            self.twopop_type_idx = None

        # Tier 1.1 — per-agent GRU memory.
        self.agent_memory: AgentMemoryGRU | None = None
        if self.cfg.agent_memory_enabled:
            self.agent_memory = AgentMemoryGRU(
                d_state=d,
                config=AgentMemoryConfig(
                    d_memory=self.cfg.agent_memory_d,
                    update_every=self.cfg.agent_memory_update_every,
                ),
            )

        # Tier 4.1 — MEGNet-style global state.
        self.global_state: GlobalStateGRU | None = None
        if self.cfg.global_state_enabled:
            self.global_state = GlobalStateGRU(
                d_state=d,
                config=GlobalStateConfig(
                    d_global=self.cfg.global_state_d,
                    update_every=self.cfg.global_state_update_every,
                ),
                d_agent=(self.cfg.agent_memory_d if self.cfg.agent_memory_enabled else 0),
            )

        # Tier 2.2 — multi-timescale fast/slow agent mask. ``is_fast_agent``
        # is a (N,) bool buffer derived from a deterministic seed so the
        # split is reproducible across runs with the same v2_type_seed.
        if self.cfg.multi_timescale_enabled:
            gen_mt = torch.Generator().manual_seed(self.cfg.v2_type_seed + 1)
            n_fast = int(round(self.cfg.timescale_fast_frac * self.cfg.n_agents))
            perm = torch.randperm(self.cfg.n_agents, generator=gen_mt)
            mask = torch.zeros(self.cfg.n_agents, dtype=torch.bool)
            mask[perm[:n_fast]] = True
            self.register_buffer("is_fast_agent", mask, persistent=False)
        else:
            self.is_fast_agent = None

    # ── Properties ─────────────────────────────────────────────────────────

    @property
    def gamma(self) -> Tensor:
        return torch.exp(self.log_gamma)

    @property
    def temperature(self) -> Tensor:
        return torch.exp(self.log_temperature)

    @property
    def device(self) -> torch.device:
        return next(self.parameters()).device

    # ── Initialisation ─────────────────────────────────────────────────────

    def init_state(self, generator: torch.Generator | None = None) -> Tensor:
        s = torch.randn(
            (self.cfg.n_agents, self.cfg.d_state),
            generator=generator,
            device=self.device,
            dtype=torch.float32,
        ) * self.cfg.init_state_scale
        return s

    def init_price(self) -> PriceState:
        return self.price_formation.init_state(device=self.device, dtype=torch.float32)

    def init_regime(self) -> Tensor | None:
        """Initial slow-regime latent. None when regime is disabled."""
        if self.regime_gru is None:
            return None
        return self.regime_gru.init_h(self.device, torch.float32)

    def init_agent_memory(self) -> Tensor | None:
        """Initial per-agent memory. None when Tier 1.1 is disabled."""
        if self.agent_memory is None:
            return None
        return self.agent_memory.init_h(self.cfg.n_agents, self.device, torch.float32)

    def init_global_state(self) -> Tensor | None:
        """Initial MEGNet-style global state vector. None when Tier 4.1 is disabled."""
        if self.global_state is None:
            return None
        return self.global_state.init_h(self.device, torch.float32)

    # ── Step ───────────────────────────────────────────────────────────────

    def step(
        self,
        s: Tensor,
        s_prev: Tensor,
        price_state: PriceState,
        *,
        generator: torch.Generator | None = None,
        create_graph: bool = True,
        h_regime: Tensor | None = None,
        h_agent: Tensor | None = None,
        h_global: Tensor | None = None,
        step_idx: int = 0,
    ) -> tuple[Tensor, PriceState, dict[str, Tensor], Tensor | None, Tensor | None, Tensor | None]:
        """Advance one step. Returns (s_next, price_state_next, record_dict,
        h_regime_next, h_agent_next).

        v3 additions:
        - ``h_regime``: optional slow regime latent. If passed and
          ``regime_enabled``, it gets updated every ``regime_update_every`` steps.
          Used by read-heads to modulate γ, T, and Hawkes excitation strength.
        - ``step_idx``: integer step counter inside the rollout. Drives the
          regime GRU's "slow update" cadence.

        feature/arch-extensions:
        - ``h_agent``: optional per-agent GRU memory of shape
          (N, d_memory). Updated every ``agent_memory_update_every`` steps;
          its mean-pool is appended to the external potential's context.

        v4 (adiabatic timescale separation):
        - ``cfg.inner_steps_per_price`` (default 1): when > 1, the agent
          dynamics (force + integrator) iterates this many times against a
          FROZEN slow state (price_state, regime, agent_memory, global_state)
          before a single price formation update. Models the physical
          ε-separation: many fast agent decisions per slow market-clearing.
          Targets the AR(1) drift root cause: per outer-step the realized
          return is the sum of ``inner_steps`` independent agent walks,
          producing a much more random-walk-like return series.
        """
        # Tier 1.1: update per-agent memory before computing forces so the
        # current step's potential sees this step's memory readout.
        h_agent_next = h_agent
        if self.agent_memory is not None and h_agent is not None:
            h_agent_next = self.agent_memory.maybe_step(
                h_agent, step_idx, s,
                price_state.last_log_return, price_state.volatility,
            )

        # Tier 4.1: update MEGNet-style global state before computing forces
        # so V uses this step's u.
        h_global_next = h_global
        if self.global_state is not None and h_global is not None:
            h_global_next = self.global_state.maybe_step(
                h_global, step_idx, s,
                price_state.last_log_return, price_state.volatility,
                h_agent=h_agent_next,
            )

        ctx_parts = [price_state.log_price, price_state.volatility, price_state.last_log_return]
        context = torch.stack(ctx_parts)
        if self.agent_memory is not None and h_agent_next is not None:
            mem_global = self.agent_memory.read_global(h_agent_next)
            context = torch.cat([context, mem_global], dim=0)
        if self.global_state is not None and h_global_next is not None:
            context = torch.cat([context, h_global_next], dim=0)
        # Pair-side: only when global_state_into_pair is True does the pair
        # kernel see u. (External always sees u via context above.)
        u_for_pair = (
            h_global_next
            if (self.global_state is not None
                and h_global_next is not None
                and self.cfg.global_state_into_pair)
            else None
        )
        # Compute γ_eff, T_eff (per-step optional regime modulation)
        T_eff: Tensor | float = self.temperature
        gamma_eff: Tensor | float = self.gamma
        excitation_mul: Tensor | float = 1.0
        h_regime_next = h_regime

        if self.regime_gru is not None and h_regime is not None:
            # market_stats: (vol, |last_r|, log_ret_signed, autocorr_proxy)
            ret = price_state.last_log_return
            stats = torch.stack([
                price_state.volatility,
                ret.abs(),
                ret,
                ret * (price_state.last_log_return.detach()),  # r·r_{t-1} proxy
            ])
            h_regime_next = self.regime_gru.maybe_step(h_regime, step_idx, stats)
            # B3 separation: persistent state may be logits (DiscreteRegimeGRU)
            # or the latent itself (RegimeGRU). Both classes implement
            # ``read(h)`` to return the d_regime vector consumed by read heads.
            h_regime_emb = self.regime_gru.read(h_regime_next)
            if self.regime_head_gamma is not None:
                gamma_eff = self.gamma * self.regime_head_gamma(h_regime_emb)
            if self.regime_head_T is not None:
                T_eff = self.temperature * self.regime_head_T(h_regime_emb)
            if self.regime_head_kappa is not None:
                excitation_mul = self.regime_head_kappa(h_regime_emb)

        # Two-population per-type γ, T (broadcast (N,) to multiply T/γ per agent)
        if self.cfg.twopop_enabled and self.twopop_type_idx is not None:
            gamma_mul_per_agent = self.twopop_gamma_per_type[self.twopop_type_idx]
            T_mul_per_agent = self.twopop_temp_per_type[self.twopop_type_idx]
            # broadcast to (N, 1) so integrator can use per-agent γ
            base_gamma = gamma_eff if isinstance(gamma_eff, Tensor) else torch.tensor(
                float(gamma_eff), device=s.device, dtype=s.dtype)
            base_T = T_eff if isinstance(T_eff, Tensor) else torch.tensor(
                float(T_eff), device=s.device, dtype=s.dtype)
            gamma_eff = (base_gamma * gamma_mul_per_agent).unsqueeze(-1)
            T_eff = (base_T * T_mul_per_agent).unsqueeze(-1)

        # Tier 2.2: build update_mask if multi-timescale enabled.
        update_mask: Tensor | None = None
        if self.cfg.multi_timescale_enabled and self.is_fast_agent is not None:
            slow_should_update = (step_idx % max(1, self.cfg.timescale_slow_freq) == 0)
            if slow_should_update:
                update_mask = None  # everyone updates this step
            else:
                update_mask = self.is_fast_agent  # only fast agents

        # v4 adiabatic: inner agent dynamics loop. inner_steps_per_price=1
        # reproduces the original single-step semantics exactly.
        inner_n = max(1, int(self.cfg.inner_steps_per_price))
        s_outer_in = s
        s_running = s
        s_prev_running = s_prev
        last_step_out = None
        for _inner_idx in range(inner_n):
            f_cons = conservative_forces(
                self.potential, s_running, context,
                create_graph=create_graph, u_global=u_for_pair,
            )
            f_diss = dissipative_forces(
                self.dissipation, s_running, s_prev_running, create_graph=create_graph,
            )
            last_step_out = self.integrator.step(
                s=s_running,
                f_cons=f_cons,
                f_diss=f_diss,
                T=T_eff,
                gamma=gamma_eff,
                dt=self.cfg.dt,
                generator=generator,
                update_mask=update_mask,
                create_graph=create_graph,
            )
            s_prev_running = s_running
            s_running = last_step_out.s_next
        step_out = last_step_out  # last inner step's IntegratorStep (forces, velocity)

        price_step = self.price_formation.step(
            state=price_state,
            s_prev=s_outer_in,
            s_next=s_running,
            generator=generator,
            excitation_mul=excitation_mul,
        )

        # V4 mechanism 2: feed the latest log return back to the integrator so
        # the next step's γ_eff can react to the sign of the most recent
        # market move. Cheap (scalar copy), no graph allocation.
        if hasattr(self.integrator, "update_price_signal"):
            self.integrator.update_price_signal(price_step.state.last_log_return)

        record = {
            "s": step_out.s_next,
            "f_cons": step_out.f_cons,
            "f_diss": step_out.f_diss,
            "f_stoch": step_out.f_stoch,
            "velocity": step_out.velocity,
            "log_price": price_step.state.log_price,
            "log_return": price_step.state.last_log_return,
            "volume": price_step.aux["volume"],
            "excess_demand": price_step.aux["excess_demand"],
        }
        return step_out.s_next, price_step.state, record, h_regime_next, h_agent_next, h_global_next

    # ── Rollouts ───────────────────────────────────────────────────────────

    def _reset_potential_cache(self) -> None:
        """Invalidate any graph/edge caches before a fresh rollout."""
        pairwise = getattr(self.potential, "pairwise", None)
        if isinstance(pairwise, MACELitePotential):
            pairwise.reset_graph_cache()
        elif isinstance(pairwise, StochasticPairwisePotential):
            pairwise.reset_edge_cache()
        elif isinstance(pairwise, ISABPairwisePotential):
            pairwise.reset_edge_cache()

    def rollout_chunk(
        self,
        s: Tensor,
        s_prev: Tensor,
        price_state: PriceState,
        n_steps: int,
        *,
        generator: torch.Generator | None = None,
        create_graph: bool = True,
        h_regime: Tensor | None = None,
        h_agent: Tensor | None = None,
        h_global: Tensor | None = None,
    ) -> tuple[Tensor, PriceState, EcoMDTrajectory, Tensor | None]:
        """Differentiable chunk rollout — returns (s_final, price_state_final,
        traj, h_regime_final). ``h_regime_final`` is None when regime disabled.

        When ``self.cfg.bptt_checkpoint_every > 0`` and ``create_graph=True``,
        rolls out in groups of K steps wrapped in
        ``torch.utils.checkpoint.checkpoint(use_reentrant=False)`` —
        activations are recomputed during backward instead of stored,
        trading ~1.5× compute for ~K× memory savings. RNG state of the
        custom ``generator`` is manually snapshotted before each group and
        restored on the recompute pass to keep gradients deterministic.

        IMPORTANT: under checkpointing, the generator's *post-rollout* state
        ends up at the START of the last group after backward (because
        recompute rewinds it). The training loop is responsible for
        snapshotting the post-forward state and restoring it after
        backward when ``bptt_checkpoint_every > 0``.
        """
        self._reset_potential_cache()
        if h_regime is None and self.regime_gru is not None:
            h_regime = self.init_regime()
        if h_agent is None and self.agent_memory is not None:
            h_agent = self.init_agent_memory()
        if h_global is None and self.global_state is not None:
            h_global = self.init_global_state()
        recorder = TrajectoryRecorder(dt=self.cfg.dt, meta={"n_steps": n_steps})

        K = int(self.cfg.bptt_checkpoint_every) if create_graph else 0
        use_custom_fn = bool(self.cfg.bptt_custom_function) and create_graph

        if use_custom_fn:
            # Sprint 2 path: per-step custom autograd.Function. Memory bounded
            # by ONE step's V-graph regardless of chunk_steps. Diagnostic
            # channels (f_cons, velocities, etc.) are detached — see
            # bptt_step_function.py docstring.
            from .bptt_step_function import step_via_function
            zero_aux = lambda shape, dtype=s.dtype: torch.zeros(
                shape, device=s.device, dtype=dtype
            )
            for k in range(n_steps):
                (s_next, s_prev_next, price_state,
                 h_regime, h_agent, h_global, log_return) = step_via_function(
                    self, s, s_prev, price_state,
                    generator=generator,
                    h_regime=h_regime, h_agent=h_agent, h_global=h_global,
                    step_idx=k,
                )
                # Recorder gets log_return live; aux channels detached
                # placeholders to keep schema compatible with downstream code.
                # NOTE: any consumer of f_cons / states etc. with gradient
                # expectation will fail under bptt_custom_function=True.
                recorder.record(
                    s=s_next.detach(),
                    f_cons=zero_aux(s_next.shape),
                    f_diss=zero_aux(s_next.shape),
                    f_stoch=zero_aux(s_next.shape),
                    velocity=zero_aux(s_next.shape),
                    log_price=price_state.log_price,
                    log_return=log_return,
                    volume=zero_aux(()),
                    excess_demand=zero_aux(()),
                )
                s_prev = s_prev_next
                s = s_next
            return s, price_state, recorder.finalize(), h_regime

        if K <= 0:
            # Original (no-checkpoint) path
            for k in range(n_steps):
                s_next, price_state, rec, h_regime, h_agent, h_global = self.step(
                    s, s_prev, price_state,
                    generator=generator,
                    create_graph=create_graph,
                    h_regime=h_regime,
                    h_agent=h_agent,
                    h_global=h_global,
                    step_idx=k,
                )
                recorder.record(
                    s=rec["s"],
                    f_cons=rec["f_cons"],
                    f_diss=rec["f_diss"],
                    f_stoch=rec["f_stoch"],
                    velocity=rec["velocity"],
                    log_price=rec["log_price"],
                    log_return=rec["log_return"],
                    volume=rec["volume"],
                    excess_demand=rec["excess_demand"],
                )
                s_prev = s
                s = s_next
            return s, price_state, recorder.finalize(), h_regime

        # ── Grouped-checkpoint path ────────────────────────────────────────
        has_hawkes = price_state.hawkes_memory is not None
        has_hawkes_long = price_state.hawkes_memory_long is not None
        has_regime = h_regime is not None
        has_agent = h_agent is not None
        has_global = h_global is not None
        # Placeholder zero tensor for h_regime / h_agent / h_global when
        # disabled (so we always pass tensors through checkpoint, never None).
        zero_h = torch.zeros((), device=s.device, dtype=s.dtype)
        h_reg_tensor = h_regime if has_regime else zero_h
        zero_h_agent = torch.zeros((self.cfg.n_agents, self.cfg.agent_memory_d),
                                   device=s.device, dtype=s.dtype)
        h_agent_tensor = h_agent if has_agent else zero_h_agent
        zero_h_global = torch.zeros((self.cfg.global_state_d,),
                                    device=s.device, dtype=s.dtype)
        h_global_tensor = h_global if has_global else zero_h_global

        # Reference to the simulator (avoid `self` capture issues when
        # defining the closure inside a loop body).
        sim_self = self

        step_offset = 0
        while step_offset < n_steps:
            this_group = min(K, n_steps - step_offset)
            local_step_start = step_offset

            # Snapshot RNG so backward's recompute reproduces the same noise.
            # `.clone()` decouples from the generator's internal storage so a
            # later set_state() on the same generator doesn't mutate it.
            if generator is not None:
                gen_state_before = generator.get_state().clone()
            else:
                gen_state_before = None

            def _run_group(
                s_in, s_prev_in,
                lp_in, llr_in, vol_in, hk_in, hkl_in,
                h_reg_in,
                h_agent_in,
                h_global_in,
                # Closure-captured constants (bound at definition time):
                _step_start=local_step_start,
                _this_group=this_group,
                _gen=generator,
                _gen_state=gen_state_before,
                _has_hawkes=has_hawkes,
                _has_hawkes_long=has_hawkes_long,
                _has_regime=has_regime,
                _has_agent=has_agent,
                _has_global=has_global,
                _create_graph=create_graph,
                _sim=sim_self,
            ):
                # Restore RNG state at start of group — happens both on
                # initial forward (no-op, gen already there) and on recompute
                # during backward (rewinds gen).
                if _gen is not None and _gen_state is not None:
                    _gen.set_state(_gen_state)

                ps_local = PriceState.from_tensors(
                    (lp_in, llr_in, vol_in, hk_in, hkl_in),
                    step=_step_start,
                    has_hawkes=_has_hawkes,
                    has_hawkes_long=_has_hawkes_long,
                )
                h_reg_local = h_reg_in if _has_regime else None
                h_agent_local = h_agent_in if _has_agent else None
                h_global_local = h_global_in if _has_global else None

                states_list: list[Tensor] = []
                f_cons_list: list[Tensor] = []
                f_diss_list: list[Tensor] = []
                f_stoch_list: list[Tensor] = []
                velocities_list: list[Tensor] = []
                log_prices_list: list[Tensor] = []
                log_returns_list: list[Tensor] = []
                volumes_list: list[Tensor] = []
                excess_demand_list: list[Tensor] = []

                s_local = s_in
                s_prev_local = s_prev_in

                for k in range(_this_group):
                    (s_next, ps_local, rec,
                     h_reg_local, h_agent_local, h_global_local) = _sim.step(
                        s_local, s_prev_local, ps_local,
                        generator=_gen, create_graph=_create_graph,
                        h_regime=h_reg_local, h_agent=h_agent_local,
                        h_global=h_global_local,
                        step_idx=_step_start + k,
                    )
                    states_list.append(rec["s"])
                    f_cons_list.append(rec["f_cons"])
                    f_diss_list.append(rec["f_diss"])
                    f_stoch_list.append(rec["f_stoch"])
                    velocities_list.append(rec["velocity"])
                    log_prices_list.append(rec["log_price"])
                    log_returns_list.append(rec["log_return"])
                    volumes_list.append(rec["volume"])
                    excess_demand_list.append(rec["excess_demand"])
                    s_prev_local = s_local
                    s_local = s_next

                ps_t = ps_local.to_tensors()
                h_reg_out = h_reg_local if (_has_regime and h_reg_local is not None) \
                    else torch.zeros((), device=s_local.device, dtype=s_local.dtype)
                h_agent_out = h_agent_local if (_has_agent and h_agent_local is not None) \
                    else torch.zeros((sim_self.cfg.n_agents, sim_self.cfg.agent_memory_d),
                                     device=s_local.device, dtype=s_local.dtype)
                h_global_out = h_global_local if (_has_global and h_global_local is not None) \
                    else torch.zeros((sim_self.cfg.global_state_d,),
                                     device=s_local.device, dtype=s_local.dtype)

                return (
                    s_local, s_prev_local,
                    ps_t[0], ps_t[1], ps_t[2], ps_t[3], ps_t[4],
                    h_reg_out,
                    h_agent_out,
                    h_global_out,
                    torch.stack(states_list),
                    torch.stack(f_cons_list),
                    torch.stack(f_diss_list),
                    torch.stack(f_stoch_list),
                    torch.stack(velocities_list),
                    torch.stack(log_prices_list),
                    torch.stack(log_returns_list),
                    torch.stack(volumes_list),
                    torch.stack(excess_demand_list),
                )

            ps_in_t = price_state.to_tensors()
            outputs = torch.utils.checkpoint.checkpoint(
                _run_group,
                s, s_prev,
                ps_in_t[0], ps_in_t[1], ps_in_t[2], ps_in_t[3], ps_in_t[4],
                h_reg_tensor,
                h_agent_tensor,
                h_global_tensor,
                use_reentrant=False,
            )

            (s, s_prev,
             lp_out, llr_out, vol_out, hk_out, hkl_out,
             h_reg_tensor,
             h_agent_tensor,
             h_global_tensor,
             states_stack, f_cons_stack, f_diss_stack, f_stoch_stack,
             velocities_stack, log_prices_stack, log_returns_stack,
             volumes_stack, excess_demand_stack) = outputs

            price_state = PriceState.from_tensors(
                (lp_out, llr_out, vol_out, hk_out, hkl_out),
                step=step_offset + this_group,
                has_hawkes=has_hawkes,
                has_hawkes_long=has_hawkes_long,
            )
            if has_regime:
                h_regime = h_reg_tensor
            # else: h_regime stays None
            if has_agent:
                h_agent = h_agent_tensor
            # else: h_agent stays None
            if has_global:
                h_global = h_global_tensor
            # else: h_global stays None

            # Append this group's K stacked records into the global recorder.
            for k in range(this_group):
                recorder.record(
                    s=states_stack[k],
                    f_cons=f_cons_stack[k],
                    f_diss=f_diss_stack[k],
                    f_stoch=f_stoch_stack[k],
                    velocity=velocities_stack[k],
                    log_price=log_prices_stack[k],
                    log_return=log_returns_stack[k],
                    volume=volumes_stack[k],
                    excess_demand=excess_demand_stack[k],
                )

            step_offset += this_group

        return s, price_state, recorder.finalize(), h_regime

    @torch.no_grad()
    def run(
        self,
        n_steps: int,
        seed: int | None = None,
        s_init: Tensor | None = None,
    ) -> EcoMDTrajectory:
        """Forward-only inference rollout. No gradients retained."""
        device = self.device
        if seed is not None:
            generator = torch.Generator(device=device)
            generator.manual_seed(seed)
        else:
            generator = None

        s = s_init if s_init is not None else self.init_state(generator=generator)
        s_prev = s.detach().clone()
        price_state = self.init_price()
        h_regime = self.init_regime()
        h_agent = self.init_agent_memory()
        h_global = self.init_global_state()

        self._reset_potential_cache()
        if hasattr(self.integrator, "reset_state"):
            self.integrator.reset_state()
        recorder = TrajectoryRecorder(
            dt=self.cfg.dt,
            meta={"n_steps": n_steps, "seed": seed if seed is not None else -1,
                  "n_agents": self.cfg.n_agents, "d_state": self.cfg.d_state},
        )
        for k in range(n_steps):
            s_next, price_state, rec, h_regime, h_agent, h_global = self.step(
                s, s_prev, price_state,
                generator=generator,
                create_graph=False,
                h_regime=h_regime,
                h_agent=h_agent,
                h_global=h_global,
                step_idx=k,
            )
            recorder.record(
                s=rec["s"].detach(),
                f_cons=rec["f_cons"].detach(),
                f_diss=rec["f_diss"].detach(),
                f_stoch=rec["f_stoch"].detach(),
                velocity=rec["velocity"].detach(),
                log_price=rec["log_price"].detach(),
                log_return=rec["log_return"].detach(),
                volume=rec["volume"].detach(),
                excess_demand=rec["excess_demand"].detach(),
            )
            s_prev = s
            s = s_next
        return recorder.finalize()
