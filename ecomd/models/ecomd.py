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
from .ecomd_v2 import EcoMDv2Config, EcoMDv2Potential
from .mace_lite import MACELitePotential, build_mace_lite
from .regime_latent import RegimeGRU, RegimeGRUConfig, RegimeReadHead
from .potentials import (
    StochasticPairwisePotential,
    ConservativePotential,
    DissipationParams,
    DissipationPotential,
    ExternalPotential,
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
    noise_dist: str = "normal"               # 'normal' or 't' (Student-t, v0.6+)
    noise_df: int = 5                        # only used when noise_dist='t'
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
    # Spatial-checkpoint sharding (paper-a-2026-04-27):
    # 0 = off (process all edges at once, original behaviour).
    # B > 0 = process pairwise edges in chunks of B, wrap each in
    #   torch.utils.checkpoint so per-batch MLP intermediates get
    #   recomputed on backward. Reduces peak pairwise forward memory
    #   from O(N×k) to O(B). Recommended values: 50_000 to 200_000 edges.
    sps_spatial_batch_size: int = 0
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
    #   torch.utils.checkpoint(use_reentrant=False) — recompute activations
    #   during backward instead of storing them. Memory drops ~K-fold,
    #   compute increases ~1.5×. Unlocks chunk_steps=64-128 at N=20K-50K.
    # Recommended: K=8 for chunk=64, K=16 for chunk=128.
    bptt_checkpoint_every: int = 0


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

        pairwise: nn.Module
        if self.cfg.pairwise_kind == "mlp":
            pairwise = PairwisePotential(d=d, hidden=self.cfg.hidden)
        elif self.cfg.pairwise_kind == "stochastic_mlp":
            pairwise = StochasticPairwisePotential(
                d=d, hidden=self.cfg.hidden,
                k_random=self.cfg.sps_k_random,
                resample_per_step=self.cfg.sps_resample_per_step,
                spatial_batch_size=self.cfg.sps_spatial_batch_size,
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
                f"expected 'mlp' | 'stochastic_mlp' | 'mace_lite' | 'ecomd_v2'"
            )
        external = ExternalPotential(
            d=d, context_dim=self.price_formation.context_dim, hidden=self.cfg.hidden
        )
        self.potential = ConservativePotential(pairwise, external)
        self.dissipation = DissipationPotential(DissipationParams(lam=self.cfg.lam_dissipation))

        self.integrator = integrator or OverdampedLangevin(
            noise_dist=self.cfg.noise_dist, noise_df=self.cfg.noise_df
        )

        # learnable log-parametrised γ, T (positivity by construction)
        log_gamma = torch.tensor(float(torch.log(torch.tensor(self.cfg.gamma_init))))
        log_T = torch.tensor(float(torch.log(torch.tensor(self.cfg.temperature_init))))
        self.log_gamma = nn.Parameter(log_gamma, requires_grad=self.cfg.learn_gamma)
        self.log_temperature = nn.Parameter(log_T, requires_grad=self.cfg.learn_temperature)

        # v3 regime latent (P3 + P5 T_eff head share infrastructure)
        self.regime_gru: RegimeGRU | None = None
        self.regime_head_gamma: RegimeReadHead | None = None
        self.regime_head_T: RegimeReadHead | None = None
        self.regime_head_kappa: RegimeReadHead | None = None
        if self.cfg.regime_enabled:
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
            gen = torch.Generator().manual_seed(self.cfg.v2_type_seed)
            type_idx = torch.randint(0, K, (self.cfg.n_agents,), generator=gen)
            self.register_buffer("twopop_type_idx", type_idx, persistent=False)
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
        step_idx: int = 0,
    ) -> tuple[Tensor, PriceState, dict[str, Tensor], Tensor | None]:
        """Advance one step. Returns (s_next, price_state_next, record_dict, h_regime_next).

        v3 additions:
        - ``h_regime``: optional slow regime latent. If passed and
          ``regime_enabled``, it gets updated every ``regime_update_every`` steps.
          Used by read-heads to modulate γ, T, and Hawkes excitation strength.
        - ``step_idx``: integer step counter inside the rollout. Drives the
          regime GRU's "slow update" cadence.
        """
        context = torch.stack([price_state.log_price, price_state.volatility, price_state.last_log_return])
        f_cons = conservative_forces(self.potential, s, context, create_graph=create_graph)
        f_diss = dissipative_forces(self.dissipation, s, s_prev, create_graph=create_graph)

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
            if self.regime_head_gamma is not None:
                gamma_eff = self.gamma * self.regime_head_gamma(h_regime_next)
            if self.regime_head_T is not None:
                T_eff = self.temperature * self.regime_head_T(h_regime_next)
            if self.regime_head_kappa is not None:
                excitation_mul = self.regime_head_kappa(h_regime_next)

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

        step_out = self.integrator.step(
            s=s,
            f_cons=f_cons,
            f_diss=f_diss,
            T=T_eff,
            gamma=gamma_eff,
            dt=self.cfg.dt,
            generator=generator,
        )

        price_step = self.price_formation.step(
            state=price_state,
            s_prev=s,
            s_next=step_out.s_next,
            generator=generator,
            excitation_mul=excitation_mul,
        )

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
        return step_out.s_next, price_step.state, record, h_regime_next

    # ── Rollouts ───────────────────────────────────────────────────────────

    def _reset_potential_cache(self) -> None:
        """Invalidate any graph/edge caches before a fresh rollout."""
        pairwise = getattr(self.potential, "pairwise", None)
        if isinstance(pairwise, MACELitePotential):
            pairwise.reset_graph_cache()
        elif isinstance(pairwise, StochasticPairwisePotential):
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
        recorder = TrajectoryRecorder(dt=self.cfg.dt, meta={"n_steps": n_steps})

        K = int(self.cfg.bptt_checkpoint_every) if create_graph else 0
        if K <= 0:
            # Original (no-checkpoint) path
            for k in range(n_steps):
                s_next, price_state, rec, h_regime = self.step(
                    s, s_prev, price_state,
                    generator=generator,
                    create_graph=create_graph,
                    h_regime=h_regime,
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
        # Placeholder zero tensor for h_regime when disabled (so we always
        # pass tensors through checkpoint, never None).
        zero_h = torch.zeros((), device=s.device, dtype=s.dtype)
        h_reg_tensor = h_regime if has_regime else zero_h

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
                # Closure-captured constants (bound at definition time):
                _step_start=local_step_start,
                _this_group=this_group,
                _gen=generator,
                _gen_state=gen_state_before,
                _has_hawkes=has_hawkes,
                _has_hawkes_long=has_hawkes_long,
                _has_regime=has_regime,
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
                    s_next, ps_local, rec, h_reg_local = _sim.step(
                        s_local, s_prev_local, ps_local,
                        generator=_gen, create_graph=_create_graph,
                        h_regime=h_reg_local, step_idx=_step_start + k,
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

                return (
                    s_local, s_prev_local,
                    ps_t[0], ps_t[1], ps_t[2], ps_t[3], ps_t[4],
                    h_reg_out,
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
                use_reentrant=False,
            )

            (s, s_prev,
             lp_out, llr_out, vol_out, hk_out, hkl_out,
             h_reg_tensor,
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

        self._reset_potential_cache()
        recorder = TrajectoryRecorder(
            dt=self.cfg.dt,
            meta={"n_steps": n_steps, "seed": seed if seed is not None else -1,
                  "n_agents": self.cfg.n_agents, "d_state": self.cfg.d_state},
        )
        for k in range(n_steps):
            s_next, price_state, rec, h_regime = self.step(
                s, s_prev, price_state,
                generator=generator,
                create_graph=False,
                h_regime=h_regime,
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
