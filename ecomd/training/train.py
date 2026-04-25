"""Training loop for EcoMD.

Extracted from ``experiments/003_ecomd_v0/run.py`` so v0.5 (experiment 004) and
future experiments can share it. Supports the v0 minimalist recipe (fresh init
every iter, full-chunk loss) and the v0.5 improvements:

  persistent_state=True   — carry (s, s_prev, price_state) across iters with
                            a .detach() barrier. Each iter starts where the
                            last one ended so the model sees a continuous
                            trajectory rather than re-relaxing from random
                            init every iter.
  warmup_steps=N          — drop the first N steps of every chunk from the
                            loss. Used to stop the optimizer from cheating by
                            putting "virtual match" signal into transient
                            behaviour.
  lr_warmup_iters=N       — linear LR warmup from 0 to peak over N iters,
                            then cosine decay to 10% of peak.
"""

from __future__ import annotations

import logging
import math
from typing import Any

import torch

from ..models.ecomd import EcoMDSimulator
from ..physics.observables import EcoMDTrajectory
from .losses import LossWeights, MomentTargets, moment_matching_loss

log = logging.getLogger(__name__)


def _lr_factor(iter_idx: int, total: int, warmup: int, floor: float = 0.1) -> float:
    if warmup > 0 and iter_idx < warmup:
        return (iter_idx + 1) / max(1, warmup)
    if iter_idx >= total:
        return floor
    progress = (iter_idx - warmup) / max(1, total - warmup)
    return floor + 0.5 * (1 - floor) * (1 + math.cos(math.pi * progress))


def train_ecomd(
    sim: EcoMDSimulator,
    targets: MomentTargets,
    *,
    n_iters: int,
    chunk_steps: int,
    lr: float,
    grad_clip: float,
    weights: LossWeights,
    seed: int,
    persistent_state: bool = False,
    warmup_steps: int = 0,
    lr_warmup_iters: int = 0,
) -> list[dict[str, Any]]:
    """Truncated-BPTT training with optional persistent state and warm-up detach.

    Each iteration:
      - (if persistent_state) detach last iter's s/s_prev/price_state, else reinit
      - rollout ``chunk_steps`` with gradient
      - compute loss on returns[warmup_steps+1:]
      - optimiser step (with optional LR schedule)
    """
    device = sim.device
    optim = torch.optim.Adam(sim.parameters(), lr=lr)
    gen = torch.Generator(device=device)
    gen.manual_seed(seed)

    history: list[dict[str, Any]] = []
    s = sim.init_state(generator=gen)
    s_prev = s.detach().clone()
    price_state = sim.init_price()
    h_regime = sim.init_regime()

    for it in range(n_iters):
        # LR schedule
        lr_factor = _lr_factor(it, n_iters, lr_warmup_iters)
        for g in optim.param_groups:
            g["lr"] = lr * lr_factor

        optim.zero_grad()

        if not persistent_state:
            s = sim.init_state(generator=gen)
            s_prev = s.detach().clone()
            price_state = sim.init_price()
            h_regime = sim.init_regime()
        else:
            # detach gradient across iter boundary; keep values so simulation is continuous
            s = s.detach()
            s_prev = s_prev.detach()
            price_state = _detach_price(price_state)
            if h_regime is not None:
                h_regime = h_regime.detach()

        s, price_state, traj, h_regime = sim.rollout_chunk(
            s, s_prev, price_state,
            n_steps=chunk_steps,
            generator=gen,
            create_graph=True,
            h_regime=h_regime,
        )
        # update s_prev for next iter to be traj.states[-2] (the step before final)
        if chunk_steps >= 2:
            s_prev = traj.states[-2].detach()
        else:
            s_prev = s.detach()

        # Compute loss on returns AFTER warmup; log_returns has length chunk_steps,
        # first is a fresh step (possibly with zero history). Drop `warmup_steps`.
        start = 1 + warmup_steps  # also drop step 0 whose log_return came from init
        if start >= traj.log_returns.shape[0]:
            start = max(1, traj.log_returns.shape[0] - 4)
        sim_returns = traj.log_returns[start:]
        out = moment_matching_loss(sim_returns, targets, weights)
        total = out["total"]
        total.backward()

        with torch.no_grad():
            grad_sq = torch.tensor(0.0)
            for p in sim.parameters():
                if p.grad is not None:
                    grad_sq = grad_sq + p.grad.detach().pow(2).sum()
            grad_norm = grad_sq.sqrt()
        torch.nn.utils.clip_grad_norm_(sim.parameters(), grad_clip)
        optim.step()

        rec = {
            "iter": it,
            "lr": lr * lr_factor,
            "total": float(total.item()),
            "acf_sq_dev": float(out["acf_sq"].item()),
            "leverage_dev": float(out["leverage"].item()),
            "hill_dev": float(out["hill"].item()),
            "acf_sim": float(out["acf_sim"].item()),
            "leverage_sim": float(out["leverage_sim"].item()),
            "hill_sim": float(out["hill_sim"].item()),
            "grad_norm": float(grad_norm.item()),
            "gamma": float(sim.gamma.item()),
            "temperature": float(sim.temperature.item()),
        }
        if "acf_shape" in out:
            rec["acf_shape_pen"] = float(out["acf_shape"].item())
        history.append(rec)
        if it == 0 or (it + 1) % max(1, n_iters // 10) == 0:
            log.info(
                f"it={it:3d} lr={rec['lr']:.2e} total={rec['total']:.4f} "
                f"acf_sim={rec['acf_sim']:+.3f} lev_sim={rec['leverage_sim']:+.3f} "
                f"hill_sim={rec['hill_sim']:.2f} |∇|={rec['grad_norm']:.2e} "
                f"γ={rec['gamma']:.3f} T={rec['temperature']:.4f}"
            )
    return history


def _detach_price(ps: Any) -> Any:
    """Return a copy of the PriceState with all tensor fields detached."""
    # Local import to avoid a circular-import pattern if we later move types.
    from ..models.price_formation import PriceState
    return PriceState(
        log_price=ps.log_price.detach(),
        last_log_return=ps.last_log_return.detach(),
        volatility=ps.volatility.detach(),
        step=ps.step,
        hawkes_memory=(ps.hawkes_memory.detach() if ps.hawkes_memory is not None else None),
        hawkes_memory_long=(ps.hawkes_memory_long.detach()
                            if ps.hawkes_memory_long is not None else None),
    )


__all__ = ["train_ecomd"]
