"""Price-formation mechanisms for EcoMD.

Two implementations ship in v0:

1. :class:`ExcessDemandPrice` (default) — the mechanism used by all v0
   experiments. Treats ``s_i[0]`` as each agent's position; price moves as in
   Lux-Marchesi 1999:

       dp = beta · ED · dt + sigma · sqrt(dt) · ξ
       ED = kappa · Σ_i (s_i_next[0] - s_i_prev[0])

   Naturally exposes volume (= total |ΔPos|) for stylized fact #10.

2. :class:`ReadoutPrice` (ablation) — price is a learned function of
   aggregate statistics of s. No conservation laws. Present for Paper A's
   ablation study; not used as the default.

Both mechanisms implement :class:`PriceFormation`. The simulator asks the
mechanism to ``init_state`` and then calls ``step`` each integrator step with
the *previous* and *current* agent states.

Volume convention
-----------------
``aux["volume"]`` is the total absolute position change across all agents.
Matches the common empirical proxy (shares traded).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

import torch
import torch.nn as nn
from torch import Tensor

# ─────────────────────────────────────────────────────────────────────────────
# Shared types
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class PriceState:
    log_price: Tensor   # scalar Tensor
    last_log_return: Tensor  # scalar Tensor
    volatility: Tensor  # scalar Tensor — EWMA of |r|
    step: int = 0
    # v1.0 (Hawkes self-excitation, optional): memory of past-vol-weighted shocks.
    # If the price module uses it, this tracks Σ_k exp(-(t-t_k)/τ)·|r_k|.
    hawkes_memory: Tensor | None = None
    # v3 multi-scale Hawkes: optional second EMA channel with longer τ
    hawkes_memory_long: Tensor | None = None


@dataclass
class PriceStepResult:
    state: PriceState
    context: Tensor     # (context_dim,) feeding back to ExternalPotential
    aux: dict[str, Tensor]  # extras: volume, excess_demand, etc.


class PriceFormation(Protocol):
    @property
    def context_dim(self) -> int: ...

    def init_state(self, device: torch.device, dtype: torch.dtype) -> PriceState: ...

    def step(
        self,
        state: PriceState,
        s_prev: Tensor,
        s_next: Tensor,
        generator: torch.Generator | None = None,
        excitation_mul: Tensor | float = 1.0,
    ) -> PriceStepResult: ...


# ─────────────────────────────────────────────────────────────────────────────
# ExcessDemandPrice (v0 default)
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ExcessDemandParams:
    beta: float = 0.5           # market-maker price response to excess demand (base value)
    kappa: float = 1.0          # scales ΔPos into ED
    sigma_price: float = 0.005  # residual noise on price (lognormal)
    ewma_alpha: float = 0.05    # volatility EWMA weight on |r|
    initial_log_price: float = 0.0
    # v0.6: state-dependent β(vol, last_return). When enabled, effective β is
    #       beta_base * softplus(mlp([vol, last_r])) / softplus(0), which preserves
    #       β ≈ beta_base at MLP init but lets the market maker's response vary
    #       with regime. Reduces spurious return autocorrelation (#1 ACF).
    learnable_beta: bool = False
    beta_hidden: int = 16
    # v1.0 Hawkes self-excitation: adds a deterministic, differentiable
    # "excitation" term to log_ret that grows with recent |r|. Models Hawkes-
    # like vol clustering without discrete jumps (so backprop stays clean).
    #   log_ret = β·ED - 0.5σ² + σ·η  +  κ · memory_t
    #   memory_{t+1} = (1-α) · memory_t + α · |log_ret_core_t|
    # hawkes_kappa = 0 disables (backwards-compat). Recommended start: α=0.1, κ=0.3.
    hawkes_alpha: float = 0.0           # EMA decay rate (0 = disabled)
    hawkes_kappa: float = 0.0           # excitation strength in log-ret units
    # v3 multi-scale Hawkes (Bacry-Muzy 2015 multi-exponential): a SECOND
    # exponential channel with smaller alpha (= longer time scale) added to
    # the base hawkes_kappa channel. Captures longer-memory effects (zumbach
    # asymmetry, ACF tail shape) that single-exp can't represent.
    #   excitation = κ·memory_t + κ_long·memory_long_t
    #   memory_long_{t+1} = (1-α_long)·memory_long_t + α_long·|log_ret_core_t|
    # hawkes_kappa_long = 0 disables. Recommended: α_long=0.01, κ_long=0.2.
    hawkes_alpha_long: float = 0.0
    hawkes_kappa_long: float = 0.0


class ExcessDemandPrice(nn.Module):
    """Lux-Marchesi-style linear-price market-maker with multiplicative noise.

    Interprets ``s_i[0]`` as agent i's position (signed). The first entry of
    the state vector therefore has a physical meaning under this mechanism —
    the simulator will report both the resulting price series and the volume
    series derived from Σ |Δpos|.
    """

    def __init__(self, params: ExcessDemandParams | None = None) -> None:
        super().__init__()
        self.params = params or ExcessDemandParams()
        if self.params.learnable_beta:
            self.beta_net: nn.Module | None = nn.Sequential(
                nn.Linear(2, self.params.beta_hidden),
                nn.SiLU(),
                nn.Linear(self.params.beta_hidden, 1),
            )
            # Init last layer near zero so β_eff ≈ β_base at start
            for m in self.beta_net.modules():
                if isinstance(m, nn.Linear):
                    nn.init.xavier_uniform_(m.weight, gain=0.1)
                    nn.init.zeros_(m.bias)
        else:
            self.beta_net = None

    @property
    def context_dim(self) -> int:
        # (log_price, vol, last_log_return)
        return 3

    def init_state(self, device: torch.device, dtype: torch.dtype) -> PriceState:
        hawkes_mem: Tensor | None = None
        hawkes_mem_long: Tensor | None = None
        if self.params.hawkes_alpha > 0.0:
            hawkes_mem = torch.zeros((), device=device, dtype=dtype)
        if self.params.hawkes_alpha_long > 0.0:
            hawkes_mem_long = torch.zeros((), device=device, dtype=dtype)
        return PriceState(
            log_price=torch.tensor(self.params.initial_log_price, device=device, dtype=dtype),
            last_log_return=torch.tensor(0.0, device=device, dtype=dtype),
            volatility=torch.tensor(self.params.sigma_price, device=device, dtype=dtype),
            step=0,
            hawkes_memory=hawkes_mem,
            hawkes_memory_long=hawkes_mem_long,
        )

    def _effective_beta(self, state: PriceState) -> Tensor:
        base = torch.as_tensor(self.params.beta, device=state.log_price.device, dtype=state.log_price.dtype)
        if self.beta_net is None:
            return base
        inp = torch.stack([state.volatility, state.last_log_return])
        raw = self.beta_net(inp).squeeze()
        # Multiplicative perturbation centered at 1; clamped to [0.1×, 5×] base for stability.
        factor = torch.clamp(torch.exp(raw), min=0.1, max=5.0)
        return base * factor

    def step(
        self,
        state: PriceState,
        s_prev: Tensor,
        s_next: Tensor,
        generator: torch.Generator | None = None,
        excitation_mul: Tensor | float = 1.0,
    ) -> PriceStepResult:
        """Advance one step. ``excitation_mul`` multiplicatively scales the
        Hawkes excitation term per step — used by the regime latent (P3)
        to modulate self-excitation strength with regime."""
        p = self.params
        pos_prev = s_prev[:, 0]
        pos_next = s_next[:, 0]
        dpos = pos_next - pos_prev
        excess_demand = p.kappa * dpos.sum()
        volume = dpos.abs().sum()

        beta_eff = self._effective_beta(state)

        # Log-price step: log p_{t+1} = log p_t + β · ED · dt - 0.5 σ² + σ · η
        # With dt absorbed into β for v0 (we use unit dt for the price step).
        eta = torch.randn((), generator=generator, device=s_next.device, dtype=s_next.dtype)
        log_ret_core = beta_eff * excess_demand - 0.5 * p.sigma_price ** 2 + p.sigma_price * eta

        # v1.0 Hawkes self-excitation (optional, off when hawkes_alpha=0).
        # Memory tracks EMA of |past log-ret|. Adds sign-coherent excitation:
        # boosts same-direction moves when recent vol was high, decays over time.
        # `memory_prev` is carried in the PriceState; the simulator detaches
        # across iteration boundaries via persistent_state, so BPTT chain
        # only spans one chunk (same as vol EWMA).
        # v3 multi-scale: second EMA channel with longer time scale (smaller α).
        excitation = torch.zeros((), device=s_next.device, dtype=s_next.dtype)
        if p.hawkes_alpha > 0.0:
            mem_prev = state.hawkes_memory
            if mem_prev is None:
                mem_prev = torch.zeros((), device=s_next.device, dtype=s_next.dtype)
            excitation = excitation + p.hawkes_kappa * mem_prev * torch.sign(log_ret_core)
            hawkes_mem_next = (1 - p.hawkes_alpha) * mem_prev + p.hawkes_alpha * log_ret_core.abs()
        else:
            hawkes_mem_next = state.hawkes_memory

        if p.hawkes_alpha_long > 0.0:
            mem_long_prev = state.hawkes_memory_long
            if mem_long_prev is None:
                mem_long_prev = torch.zeros((), device=s_next.device, dtype=s_next.dtype)
            excitation = excitation + p.hawkes_kappa_long * mem_long_prev * torch.sign(log_ret_core)
            hawkes_mem_long_next = (
                (1 - p.hawkes_alpha_long) * mem_long_prev
                + p.hawkes_alpha_long * log_ret_core.abs()
            )
        else:
            hawkes_mem_long_next = state.hawkes_memory_long

        if p.hawkes_alpha > 0.0 or p.hawkes_alpha_long > 0.0:
            log_ret = log_ret_core + excitation_mul * excitation
        else:
            log_ret = log_ret_core

        log_price_next = state.log_price + log_ret

        vol_next = (1 - p.ewma_alpha) * state.volatility + p.ewma_alpha * log_ret.abs()

        new_state = PriceState(
            log_price=log_price_next,
            last_log_return=log_ret,
            volatility=vol_next,
            step=state.step + 1,
            hawkes_memory=hawkes_mem_next,
            hawkes_memory_long=hawkes_mem_long_next,
        )
        context = torch.stack([log_price_next, vol_next, log_ret])
        aux: dict[str, Tensor] = {
            "excess_demand": excess_demand.detach(),
            "volume": volume.detach(),
            "log_return": log_ret.detach(),
            "beta_eff": beta_eff.detach(),
        }
        return PriceStepResult(state=new_state, context=context, aux=aux)


# ─────────────────────────────────────────────────────────────────────────────
# ReadoutPrice (ablation)
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ReadoutParams:
    sigma_price: float = 0.005
    ewma_alpha: float = 0.05
    initial_log_price: float = 0.0


class ReadoutPrice(nn.Module):
    """Fully-learned price readout on aggregate statistics of s.

    Price log-return at step t:
        r_t = MLP_φ([mean(s), std(s), r_{t-1}, vol_{t-1}]) + σ · η

    No conservation law; not differentiable through a market-clearing process.
    Provided as an ablation control — used to demonstrate in Paper A that
    imposing the designated-position ED mechanism is causally important for the
    emergent stylized facts.
    """

    def __init__(self, d: int, params: ReadoutParams | None = None, hidden: int = 32) -> None:
        super().__init__()
        self.d = d
        self.params = params or ReadoutParams()
        self.net = nn.Sequential(
            nn.Linear(2 * d + 2, hidden),
            nn.SiLU(),
            nn.Linear(hidden, 1),
        )
        for m in self.net.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight, gain=0.5)
                nn.init.zeros_(m.bias)

    @property
    def context_dim(self) -> int:
        return 3

    def init_state(self, device: torch.device, dtype: torch.dtype) -> PriceState:
        return PriceState(
            log_price=torch.tensor(self.params.initial_log_price, device=device, dtype=dtype),
            last_log_return=torch.tensor(0.0, device=device, dtype=dtype),
            volatility=torch.tensor(self.params.sigma_price, device=device, dtype=dtype),
            step=0,
        )

    def step(
        self,
        state: PriceState,
        s_prev: Tensor,
        s_next: Tensor,
        generator: torch.Generator | None = None,
        excitation_mul: Tensor | float = 1.0,
    ) -> PriceStepResult:
        p = self.params
        mean = s_next.mean(dim=0)
        std = s_next.std(dim=0)
        inp = torch.cat([mean, std, state.last_log_return.unsqueeze(0), state.volatility.unsqueeze(0)])
        raw = self.net(inp).squeeze()
        eta = torch.randn((), generator=generator, device=s_next.device, dtype=s_next.dtype)
        log_ret = raw + p.sigma_price * eta

        log_price_next = state.log_price + log_ret
        vol_next = (1 - p.ewma_alpha) * state.volatility + p.ewma_alpha * log_ret.abs()

        new_state = PriceState(
            log_price=log_price_next,
            last_log_return=log_ret,
            volatility=vol_next,
            step=state.step + 1,
        )
        context = torch.stack([log_price_next, vol_next, log_ret])
        # no natural volume/ED from readout; report zeros for interface compat
        aux: dict[str, Tensor] = {
            "excess_demand": torch.zeros((), device=s_next.device, dtype=s_next.dtype),
            "volume": (s_next[:, 0] - s_prev[:, 0]).abs().sum().detach(),
            "log_return": log_ret.detach(),
        }
        return PriceStepResult(state=new_state, context=context, aux=aux)


# ─────────────────────────────────────────────────────────────────────────────
# Registry (for Hydra config)
# ─────────────────────────────────────────────────────────────────────────────


def build_price_formation(kind: str, d: int, **kwargs: Any) -> PriceFormation:
    if kind == "excess_demand":
        params = ExcessDemandParams(**kwargs) if kwargs else None
        return ExcessDemandPrice(params)
    if kind == "readout":
        params = ReadoutParams(**kwargs) if kwargs else None
        return ReadoutPrice(d=d, params=params)
    raise ValueError(f"unknown price formation {kind!r}; expected 'excess_demand' or 'readout'")
