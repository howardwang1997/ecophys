"""Lux-Marchesi (1999/2000) agent-based market model — our first baseline.

Reference:
  Lux, T. & Marchesi, M. (1999) "Scaling and criticality in a stochastic
    multi-agent model of a financial market," Nature 397, 498-500.
  Lux, T. & Marchesi, M. (2000) "Volatility clustering in financial markets:
    A microsimulation of interacting agents," Int. J. Theor. Appl. Finance
    3, 675-702. (the detailed description we follow)

Model
-----
N interacting agents partitioned into:
  - Fundamentalists    (n_f): believe in an exogenous fair value p_f, demand
    ∝ γ · (p_f − p).
  - Optimist chartists (n_cp): always buy a fixed parcel t_c
  - Pessimist chartists (n_cn): always sell a fixed parcel t_c

with n_f + n_cp + n_cn = N.

Opinion index     x = (n_cp − n_cn) / (n_cp + n_cn)
Excess demand     ED = t_c · (n_cp − n_cn) + n_f · γ · (p_f − p)
Price update      Δp = β · ED · Δt + σ · √Δt · ξ      (Euler-Maruyama)

Transition rates (pairwise, continuous time → tau-leap with step Δt):
  +  ↔ −  among chartists  (herding + momentum)
      U1 = α1 x + α2 / v1 · (Δp / Δt) / p
      π(+→−) = v1 · (n_cn / N) · exp(+U1)
      π(−→+) = v1 · (n_cp / N) · exp(−U1)
  ± ↔ f  between chartists and fundamentalists  (profit differential)
      r_hat = dividend/price ratio seen by fundamentalists; see paper
      U21 = α3 · ( (r + (Δp/Δt)/v2) / p − R − s · ((p_f − p)/p)² )    (+ ↔ f)
      U22 = α3 · ( R − (r + (Δp/Δt)/v2) / p − s · ((p_f − p)/p)² )    (− ↔ f)
      π(+→f) = v2 · (n_f/N) · exp(+U21)
      π(f→+) = v2 · (n_cp/N) · exp(−U21)
      π(−→f) = v2 · (n_f/N) · exp(+U22)
      π(f→−) = v2 · (n_cn/N) · exp(−U22)

We simulate with Poisson tau-leap: for each transition rate r_k, draw the
number of transitions in Δt from Poisson(r_k · N_source · Δt), clamped to the
source population.

Numerical stability
-------------------
U1/U21/U22 are clipped to ±U_CLIP to avoid exp() overflow when price moves
are extreme; this is a standard practice in ABM implementations and does
not change the asymptotic dynamics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import numpy.typing as npt


@dataclass(frozen=True)
class LuxMarchesiParams:
    """Default parameters near Lux & Marchesi (2000, Int. J. Theor. Appl. Finance).

    Price state is LINEAR price (not log). Returns are ex-post log differences.
    """

    n_agents: int = 500
    # Price dynamics (linear-price space; paper table 1)
    beta: float = 0.5         # market-maker price response to excess demand
    t_c: float = 0.01         # chartist per-agent trading size (shares-ish)
    gamma: float = 0.01       # fundamentalist trading intensity
    sigma_price: float = 0.005 # relative (multiplicative) noise on price
    # Transition intensities
    v1: float = 3.0           # base rate for chartist ↔ chartist flips
    v2: float = 2.0           # base rate for chartist ↔ fundamentalist
    alpha_1: float = 0.6      # herding strength
    alpha_2: float = 0.2      # trend chasing strength
    alpha_3: float = 0.5      # chartist/fundamentalist switch scaling
    # Fundamentals (linear price units)
    p_f: float = 10.0         # fundamental price level, constant in baseline
    r_div: float = 0.0004     # dividend rate (per tick)
    R_rf: float = 0.0004      # risk-free rate (per tick)
    s_risk: float = 0.75      # fundamentalists' perceived risk premium
    # Numerical safety
    u_clip: float = 10.0      # clamp exponents to [-u_clip, +u_clip]
    min_price: float = 1e-4   # floor on price; emits a warning if reached
    # Init
    init_fraction_fundamentalist: float = 0.5
    init_fraction_optimist: float = 0.25  # optimists + pessimists = remainder


@dataclass
class LuxMarchesiState:
    """Mutable state of a single simulation step.

    `price` is the LINEAR price level. Returns are computed ex-post as log diffs.
    `last_dp` is the most recent Δprice (absolute, not relative).
    """
    price: float
    n_f: int
    n_cp: int  # optimist chartists
    n_cn: int  # pessimist chartists
    last_dp: float = 0.0

    @property
    def n_c(self) -> int:
        return self.n_cp + self.n_cn

    @property
    def opinion_x(self) -> float:
        nc = self.n_c
        if nc == 0:
            return 0.0
        return (self.n_cp - self.n_cn) / nc

    def check_conservation(self, N: int) -> None:
        total = self.n_f + self.n_cp + self.n_cn
        if total != N:
            raise RuntimeError(f"agent count drifted: {total} != {N}")
        if min(self.n_f, self.n_cp, self.n_cn) < 0:
            raise RuntimeError(f"negative population: f={self.n_f} +={self.n_cp} -={self.n_cn}")


@dataclass
class LuxMarchesiTrajectory:
    log_price: npt.NDArray[np.float64]
    n_fundamentalist: npt.NDArray[np.int64]
    n_optimist: npt.NDArray[np.int64]
    n_pessimist: npt.NDArray[np.int64]
    dt: float
    params: dict[str, Any] = field(default_factory=dict)

    @property
    def price(self) -> npt.NDArray[np.float64]:
        return np.exp(self.log_price)

    @property
    def log_returns(self) -> npt.NDArray[np.float64]:
        return np.diff(self.log_price)

    @property
    def opinion_index(self) -> npt.NDArray[np.float64]:
        nc = self.n_optimist + self.n_pessimist
        out = np.zeros_like(nc, dtype=np.float64)
        mask = nc > 0
        out[mask] = (self.n_optimist[mask] - self.n_pessimist[mask]) / nc[mask]
        return out


# ─────────────────────────────────────────────────────────────────────────────
# Simulator
# ─────────────────────────────────────────────────────────────────────────────


class LuxMarchesi1999:
    """Agent-based simulator. Call `.run(n_steps, dt, seed)` → LuxMarchesiTrajectory."""

    def __init__(self, params: LuxMarchesiParams | None = None) -> None:
        self.params = params or LuxMarchesiParams()
        self._validate()

    def _validate(self) -> None:
        p = self.params
        if p.n_agents < 10:
            raise ValueError(f"n_agents={p.n_agents} too small")
        if not 0 <= p.init_fraction_fundamentalist <= 1:
            raise ValueError("init_fraction_fundamentalist must be in [0, 1]")
        if not 0 <= p.init_fraction_optimist <= 1:
            raise ValueError("init_fraction_optimist must be in [0, 1]")
        if p.init_fraction_fundamentalist + p.init_fraction_optimist > 1:
            raise ValueError("init fractions sum > 1")

    def _initial_state(self, p0: float) -> LuxMarchesiState:
        p = self.params
        n_f = int(p.n_agents * p.init_fraction_fundamentalist)
        n_cp = int(p.n_agents * p.init_fraction_optimist)
        n_cn = p.n_agents - n_f - n_cp
        return LuxMarchesiState(price=p0, n_f=n_f, n_cp=n_cp, n_cn=n_cn)

    def run(
        self,
        n_steps: int,
        dt: float = 0.01,
        seed: int | None = None,
        p0: float | None = None,
    ) -> LuxMarchesiTrajectory:
        p = self.params
        rng = np.random.default_rng(seed)
        state = self._initial_state(p0 if p0 is not None else p.p_f)

        price_arr = np.empty(n_steps, dtype=np.float64)
        n_f_arr = np.empty(n_steps, dtype=np.int64)
        n_cp_arr = np.empty(n_steps, dtype=np.int64)
        n_cn_arr = np.empty(n_steps, dtype=np.int64)

        for t in range(n_steps):
            price_arr[t] = state.price
            n_f_arr[t] = state.n_f
            n_cp_arr[t] = state.n_cp
            n_cn_arr[t] = state.n_cn

            # Compute transition counts in [t, t+dt) using the PREVIOUS step's Δp
            self._apply_transitions(state, rng, dt)

            # Price update: geometric Brownian motion-like — multiplicative noise,
            # additive drift from excess demand.
            ed = self._excess_demand(state)
            noise = rng.standard_normal() * p.sigma_price * state.price * np.sqrt(dt)
            dp = p.beta * ed * dt + noise
            state.last_dp = dp
            state.price = max(state.price + dp, p.min_price)
            state.check_conservation(p.n_agents)

        return LuxMarchesiTrajectory(
            log_price=np.log(price_arr),
            n_fundamentalist=n_f_arr,
            n_optimist=n_cp_arr,
            n_pessimist=n_cn_arr,
            dt=dt,
            params=_params_to_dict(p),
        )

    # ── Components ──────────────────────────────────────────────────────

    def _excess_demand(self, state: LuxMarchesiState) -> float:
        p = self.params
        chartist_demand = p.t_c * (state.n_cp - state.n_cn)
        fundamentalist_demand = state.n_f * p.gamma * (p.p_f - state.price)
        return chartist_demand + fundamentalist_demand

    def _apply_transitions(
        self,
        state: LuxMarchesiState,
        rng: np.random.Generator,
        dt: float,
    ) -> None:
        p = self.params
        x = state.opinion_x
        dp_dt = state.last_dp / dt if dt > 0 else 0.0
        price = max(state.price, p.min_price)
        mispricing_sq = ((p.p_f - price) / price) ** 2

        u1 = p.alpha_1 * x + (p.alpha_2 / p.v1) * (dp_dt / price)
        u1 = float(np.clip(u1, -p.u_clip, p.u_clip))
        # Chartist ↔ fundamentalist: fully disabled if v2 == 0
        if p.v2 > 0:
            profit_gap = (p.r_div + dp_dt / p.v2) / price - p.R_rf
            u21 = float(np.clip(p.alpha_3 * (profit_gap - p.s_risk * mispricing_sq), -p.u_clip, p.u_clip))
            u22 = float(np.clip(p.alpha_3 * (-profit_gap - p.s_risk * mispricing_sq), -p.u_clip, p.u_clip))
        else:
            u21 = u22 = 0.0

        # Rates × source population × dt → expected transitions.
        # Convention (Lux 1995; Lux-Marchesi 2000): π_{S→T} ∝ exp(+U_T) so
        # agents flow TOWARD the opinion with higher utility U. With
        # U_1 = α_1 x + ..., x>0 (more optimists) means U_1>0 → more − flow to +.
        n_total = float(p.n_agents)
        exp_pairs: list[tuple[str, float]] = [
            ("cp_to_cn", p.v1 * (state.n_cn / n_total) * np.exp(-u1) * state.n_cp * dt),
            ("cn_to_cp", p.v1 * (state.n_cp / n_total) * np.exp(+u1) * state.n_cn * dt),
        ]
        if p.v2 > 0:
            exp_pairs.extend([
                ("cp_to_f",  p.v2 * (state.n_f  / n_total) * np.exp(-u21) * state.n_cp * dt),
                ("f_to_cp",  p.v2 * (state.n_cp / n_total) * np.exp(+u21) * state.n_f  * dt),
                ("cn_to_f",  p.v2 * (state.n_f  / n_total) * np.exp(-u22) * state.n_cn * dt),
                ("f_to_cn",  p.v2 * (state.n_cn / n_total) * np.exp(+u22) * state.n_f  * dt),
            ])
        else:
            exp_pairs.extend([
                ("cp_to_f", 0.0), ("f_to_cp", 0.0), ("cn_to_f", 0.0), ("f_to_cn", 0.0),
            ])

        # Draw Poisson counts
        counts = {name: int(rng.poisson(max(expected, 0.0))) for name, expected in exp_pairs}

        # Clamp against source population (cannot transition more agents than exist)
        counts["cp_to_cn"] = min(counts["cp_to_cn"], state.n_cp)
        counts["cp_to_f"]  = min(counts["cp_to_f"],  state.n_cp - counts["cp_to_cn"])
        counts["cn_to_cp"] = min(counts["cn_to_cp"], state.n_cn)
        counts["cn_to_f"]  = min(counts["cn_to_f"],  state.n_cn - counts["cn_to_cp"])
        counts["f_to_cp"]  = min(counts["f_to_cp"],  state.n_f)
        counts["f_to_cn"]  = min(counts["f_to_cn"],  state.n_f - counts["f_to_cp"])

        # Apply to state
        state.n_cp += (-counts["cp_to_cn"] - counts["cp_to_f"]
                       + counts["cn_to_cp"] + counts["f_to_cp"])
        state.n_cn += (-counts["cn_to_cp"] - counts["cn_to_f"]
                       + counts["cp_to_cn"] + counts["f_to_cn"])
        state.n_f  += (-counts["f_to_cp"] - counts["f_to_cn"]
                       + counts["cp_to_f"] + counts["cn_to_f"])


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _params_to_dict(p: LuxMarchesiParams) -> dict[str, Any]:
    return {f.name: getattr(p, f.name) for f in p.__dataclass_fields__.values()}
