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

    # ── Step ───────────────────────────────────────────────────────────────

    def step(
        self,
        s: Tensor,
        s_prev: Tensor,
        price_state: PriceState,
        *,
        generator: torch.Generator | None = None,
        create_graph: bool = True,
    ) -> tuple[Tensor, PriceState, dict[str, Tensor]]:
        """Advance one step. Returns (s_next, price_state_next, record_dict)."""
        context = torch.stack([price_state.log_price, price_state.volatility, price_state.last_log_return])
        f_cons = conservative_forces(self.potential, s, context, create_graph=create_graph)
        f_diss = dissipative_forces(self.dissipation, s, s_prev, create_graph=create_graph)

        step_out = self.integrator.step(
            s=s,
            f_cons=f_cons,
            f_diss=f_diss,
            T=self.temperature,
            gamma=self.gamma,
            dt=self.cfg.dt,
            generator=generator,
        )

        price_step = self.price_formation.step(
            state=price_state,
            s_prev=s,
            s_next=step_out.s_next,
            generator=generator,
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
        return step_out.s_next, price_step.state, record

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
    ) -> tuple[Tensor, PriceState, EcoMDTrajectory]:
        """Differentiable chunk rollout — returns (s_final, price_state_final, traj)."""
        self._reset_potential_cache()
        recorder = TrajectoryRecorder(dt=self.cfg.dt, meta={"n_steps": n_steps})
        for _ in range(n_steps):
            s_next, price_state, rec = self.step(
                s, s_prev, price_state,
                generator=generator,
                create_graph=create_graph,
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
        return s, price_state, recorder.finalize()

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

        self._reset_potential_cache()
        recorder = TrajectoryRecorder(
            dt=self.cfg.dt,
            meta={"n_steps": n_steps, "seed": seed if seed is not None else -1,
                  "n_agents": self.cfg.n_agents, "d_state": self.cfg.d_state},
        )
        for _ in range(n_steps):
            s_next, price_state, rec = self.step(
                s, s_prev, price_state,
                generator=generator,
                create_graph=False,
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
