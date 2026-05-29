"""Learned stochastic-volatility / Neural-SDE latent for EcoMD (exp neural_sde).

Motivation
----------
The ~5.1/11 stylized-fact ceiling is paradigm-level (ABIDES ~2-3/11) and the
*failing* facts are all volatility-structure facts: fat tails (#2), aggregational
gaussianity (#4), intermittency/Fano (#5), DFA long-memory (#8). The simulator's
volatility is currently a fixed, hand-designed, *detached* noise scale. This
module makes the volatility process itself **learned, differentiable,
multi-timescale, and return-coupled** — the textbook generative cause of exactly
those facts — while staying a physics-readable object (a multiplicative-noise
overdamped-Langevin / log-OU stochastic-volatility SDE; sigma^2 * T reads as a
state-dependent effective temperature for Paper B).

The latent is a vector of K log-vol components, each a mean-reverting (OU) process
with its OWN timescale kappa_k. A superposition of OU vols at distinct timescales
gives slowly-decaying |r| autocorrelation -> long memory (DFA #8) and slow
kurtosis decay under aggregation (agg-gauss #4); a single timescale Gaussianizes
too fast to hit both. A stochastic innovation makes conditional returns
heavy-tailed (#2, #5); an asymmetric coupling to past returns (down-moves raise
vol) gives leverage (#9) / Zumbach (#11).

Stability is by construction (the recurring aggregational_gaussianity>1000 blow-up
is the #1 risk): each log-vol component is hard-bounded by a tanh clamp, the
mixing weights are a softmax (sum 1), and the return-scale multiplier is
exp(g * vbar) with vbar in [-v_clip, v_clip], so the multiplier is finite by
construction (<= exp(g * v_clip)).
"""

from __future__ import annotations

import torch
import torch.nn as nn
from torch import Tensor


class StochVolProcess(nn.Module):
    """Multi-timescale, mean-reverting, leverage-coupled log-OU latent volatility.

    ``step(v_prev, last_log_return, generator) -> (v_next, sigma_mult)`` where
    ``v_next`` is the (K,) log-vol latent and ``sigma_mult`` is a positive scalar
    that multiplies the base return scale (``sigma_eff = sigma_price * sigma_mult``).

    Nothing here is ``.detach()``-ed: the whole process must carry gradient so the
    distribution/multi-fact losses can shape the volatility dynamics.
    """

    def __init__(
        self,
        d_v: int = 2,
        *,
        state_dep: bool = False,
        leverage: bool = True,
        v_clip: float = 3.0,
        kappa_init: tuple[float, ...] = (0.5, 0.1, 0.02),
        xi_init: float = 0.1,
        gain_init: float = 0.5,
        mlp_hidden: int = 8,
    ) -> None:
        super().__init__()
        self.d_v = int(d_v)
        self.state_dep = bool(state_dep)
        self.leverage = bool(leverage)
        self.v_clip = float(v_clip)

        # Per-component mean-reversion rate kappa_k = sigmoid(theta_kappa) in (0,1).
        # Distinct timescales (fast..slow) so the superposition spans scales.
        k_init = list(kappa_init[: self.d_v])
        while len(k_init) < self.d_v:  # pad if fewer inits than components
            k_init.append(k_init[-1] * 0.2)
        k_t = torch.tensor(k_init, dtype=torch.float32).clamp(1e-3, 1 - 1e-3)
        self.theta_kappa = nn.Parameter(torch.log(k_t) - torch.log1p(-k_t))  # logit

        self.mu = nn.Parameter(torch.zeros(self.d_v))            # per-component mean log-vol
        self.w_abs = nn.Parameter(torch.full((self.d_v,), 0.1))  # |r| drive
        self.w_lev = nn.Parameter(torch.full((self.d_v,), 0.1))  # relu(-r) leverage drive
        self.theta_a = nn.Parameter(torch.zeros(self.d_v))       # softmax mixing logits -> weights
        self.log_xi = nn.Parameter(torch.full((self.d_v,), float(torch.log(torch.tensor(xi_init)))))
        self.g = nn.Parameter(torch.tensor(float(gain_init)))    # global gain on log-vol -> scale

        if self.state_dep:
            # Shared small MLP applied per component: features (d_v, 4) -> (d_v, 1).
            self.mlp = nn.Sequential(
                nn.Linear(4, mlp_hidden), nn.SiLU(), nn.Linear(mlp_hidden, 1)
            )
            for m in self.mlp.modules():
                if isinstance(m, nn.Linear):
                    nn.init.xavier_uniform_(m.weight, gain=0.1)
                    nn.init.zeros_(m.bias)
        else:
            self.mlp = None

    def init_v(self, device: torch.device, dtype: torch.dtype) -> Tensor:
        return torch.zeros(self.d_v, device=device, dtype=dtype)

    def vbar(self, v: Tensor) -> Tensor:
        """Softmax-mixed scalar log-vol from a (K,) latent — the same aggregate
        used to form sigma_mult. Used by the integrator-level placement to scale
        the agent-state Langevin noise from the price head's latent."""
        weights = torch.softmax(self.theta_a.to(v.dtype), dim=0)
        return (weights * v).sum()

    def step(
        self,
        v_prev: Tensor,
        last_log_return: Tensor,
        generator: torch.Generator | None = None,
    ) -> tuple[Tensor, Tensor]:
        dtype, device = v_prev.dtype, v_prev.device
        kappa = torch.sigmoid(self.theta_kappa).to(dtype)          # (d_v,)
        r = last_log_return                                        # scalar
        drive = self.w_abs.to(dtype) * r.abs()
        if self.leverage:
            drive = drive + self.w_lev.to(dtype) * torch.relu(-r)  # down-moves raise vol

        extra: Tensor | float = 0.0
        if self.mlp is not None:
            vbar_prev = v_prev.mean().expand(self.d_v)
            feats = torch.stack([
                r.abs().expand(self.d_v),
                r.expand(self.d_v),
                v_prev,
                vbar_prev,
            ], dim=-1)                                             # (d_v, 4)
            extra = self.mlp(feats).squeeze(-1)                    # (d_v,)

        xi = torch.exp(self.log_xi).to(dtype)
        z = torch.randn(self.d_v, generator=generator, device=device, dtype=dtype)
        v_raw = (1.0 - kappa) * v_prev + kappa * (self.mu.to(dtype) + drive + extra) + xi * z
        v_next = self.v_clip * torch.tanh(v_raw / self.v_clip)     # hard bound (-v_clip, v_clip)

        weights = torch.softmax(self.theta_a.to(dtype), dim=0)     # (d_v,), sum 1
        vbar = (weights * v_next).sum()                            # scalar in [-v_clip, v_clip]
        sigma_mult = torch.exp(self.g.to(dtype) * vbar)            # positive, <= exp(g*v_clip)
        return v_next, sigma_mult
