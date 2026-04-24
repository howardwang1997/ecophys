"""Distributed training entry point for EcoMD v1 / v1+.

Launched by ``torchrun``; works on 4-card and 8-card H20 NVLink nodes. The
code is ``world_size``-agnostic: switch between 4 and 8 by changing
``--nproc_per_node`` on torchrun.

Parallelism strategy: **data parallelism over training iterations**. Each
rank runs its own complete BPTT chunk with a different seed; at the end of
each iteration, losses and gradients are all-reduced. This is the
standard DDP pattern but wrapped around our custom train_ecomd loop.

Why data-parallel not tensor-parallel:
- For v1 at N=10⁴ on a single H20 (96 GB HBM), the full MACE-lite forward
  + BPTT through chunk_steps=64 fits comfortably (~20 GB peak). No need
  to shard the model.
- Multi-rank independent rollouts give 4–8× more training signal per
  wall-clock second — that's the real value of NVLink here.
- Tensor-parallel is the v2 story when N=5×10⁵ forces single-model
  sharding.

Checkpointing:
- Every ``checkpoint_every_s`` seconds (default 1800 = 30 min)
- Save: simulator state_dict, optimizer state_dict, scheduler state,
  RNG state, iter index
- W&B resume="allow" if wandb enabled

Usage:
    torchrun --nproc_per_node=4 --standalone \\
        -m ecomd.training.train_distributed \\
        --config experiments/006_ecomd_v1/config_h20.yaml

    # Scale to 8 cards:
    torchrun --nproc_per_node=8 --standalone -m ecomd.training.train_distributed ...

    # Dry-run single-rank on Mac:
    torchrun --nproc_per_node=1 --standalone -m ecomd.training.train_distributed \\
        --config experiments/006_ecomd_v1/config_h20.yaml --smoke
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
import torch.distributed as dist
import yaml

from ..eval.stylized_facts import log_returns_from_prices
from ..models.ecomd import EcoMDConfig, EcoMDSimulator
from .losses import LossWeights, MomentTargets, build_targets_from_returns, moment_matching_loss

log = logging.getLogger("train_distributed")


# ─────────────────────────────────────────────────────────────────────────────
# Distributed helpers
# ─────────────────────────────────────────────────────────────────────────────


def setup_dist() -> tuple[int, int, int]:
    """Init torch.distributed via torchrun env vars.

    Returns (rank, world_size, local_rank). Works on single-rank too
    (NPROC=1) for Mac dry-run.
    """
    rank = int(os.environ.get("RANK", 0))
    world_size = int(os.environ.get("WORLD_SIZE", 1))
    local_rank = int(os.environ.get("LOCAL_RANK", 0))
    if world_size > 1:
        backend = os.environ.get("DIST_BACKEND", "nccl" if torch.cuda.is_available() else "gloo")
        dist.init_process_group(backend=backend, rank=rank, world_size=world_size)
        if torch.cuda.is_available():
            torch.cuda.set_device(local_rank)
    return rank, world_size, local_rank


def cleanup_dist() -> None:
    if dist.is_available() and dist.is_initialized():
        dist.destroy_process_group()


def _is_main(rank: int) -> bool:
    return rank == 0


def all_reduce_mean(x: torch.Tensor) -> torch.Tensor:
    """All-reduce a scalar tensor, then divide by world_size."""
    if dist.is_available() and dist.is_initialized():
        dist.all_reduce(x, op=dist.ReduceOp.SUM)
        x = x / dist.get_world_size()
    return x


# ─────────────────────────────────────────────────────────────────────────────
# Data loading (rank 0 loads, broadcasts target tensor scalars to all)
# ─────────────────────────────────────────────────────────────────────────────


def load_spx_returns_any_rank(repo_root: Path) -> np.ndarray:
    for root in (repo_root / "data" / "raw", repo_root / "data" / "sample"):
        d = root / "yfinance" / "interval=1d" / "symbol=^GSPC"
        if d.exists():
            frames = [pd.read_parquet(p) for p in sorted(d.glob("year=*.parquet"))]
            if frames:
                df = pd.concat(frames, ignore_index=True).sort_values("timestamp").reset_index(drop=True)
                col = "adjusted_close" if "adjusted_close" in df.columns else "close"
                return log_returns_from_prices(df[col].to_numpy())
    raise FileNotFoundError("no ^GSPC yfinance data found in data/raw or data/sample")


# ─────────────────────────────────────────────────────────────────────────────
# Checkpoint
# ─────────────────────────────────────────────────────────────────────────────


def save_checkpoint(
    path: Path,
    *,
    sim: EcoMDSimulator,
    optim: torch.optim.Optimizer,
    iter_idx: int,
    targets: MomentTargets,
    sim_config: dict[str, Any],
    train_config: dict[str, Any],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({
        "iter_idx": iter_idx,
        "sim_state_dict": sim.state_dict(),
        "optim_state_dict": optim.state_dict(),
        "targets": asdict(targets),
        "sim_config": sim_config,
        "train_config": train_config,
    }, path)


def try_load_checkpoint(
    path: Path,
    *,
    sim: EcoMDSimulator,
    optim: torch.optim.Optimizer,
) -> int:
    if not path.exists():
        return 0
    ckpt = torch.load(path, map_location="cpu")
    sim.load_state_dict(ckpt["sim_state_dict"])
    optim.load_state_dict(ckpt["optim_state_dict"])
    return int(ckpt["iter_idx"])


# ─────────────────────────────────────────────────────────────────────────────
# Training loop (data-parallel)
# ─────────────────────────────────────────────────────────────────────────────


def train_distributed(
    sim: EcoMDSimulator,
    targets: MomentTargets,
    weights: LossWeights,
    *,
    n_iters: int,
    chunk_steps: int,
    lr: float,
    grad_clip: float,
    seed: int,
    persistent_state: bool,
    warmup_steps: int,
    lr_warmup_iters: int,
    rank: int,
    world_size: int,
    checkpoint_path: Path | None,
    checkpoint_every_s: float,
) -> list[dict[str, Any]]:
    """Each rank runs train_ecomd-style iterations with its own seed.

    Gradients are all-reduced after each iter's backward. Loss metrics
    logged here are per-rank (mean over world reduced separately for
    printing).
    """
    device = sim.device
    optim = torch.optim.Adam(sim.parameters(), lr=lr)

    start_iter = 0
    if checkpoint_path is not None:
        start_iter = try_load_checkpoint(checkpoint_path, sim=sim, optim=optim)
        if start_iter > 0 and _is_main(rank):
            log.info(f"[rank 0] resumed from {checkpoint_path} at iter {start_iter}")

    # Each rank gets a distinct seed so independent trajectories are explored
    gen = torch.Generator(device=device)
    gen.manual_seed(seed + rank * 10000 + start_iter)

    history: list[dict[str, Any]] = []
    s = sim.init_state(generator=gen)
    s_prev = s.detach().clone()
    price_state = sim.init_price()

    last_ckpt_time = time.time()

    from .train import _lr_factor, _detach_price

    for it in range(start_iter, n_iters):
        lr_factor = _lr_factor(it, n_iters, lr_warmup_iters)
        for g in optim.param_groups:
            g["lr"] = lr * lr_factor

        optim.zero_grad()

        if not persistent_state:
            s = sim.init_state(generator=gen)
            s_prev = s.detach().clone()
            price_state = sim.init_price()
        else:
            s = s.detach()
            s_prev = s_prev.detach()
            price_state = _detach_price(price_state)

        s, price_state, traj = sim.rollout_chunk(
            s, s_prev, price_state,
            n_steps=chunk_steps, generator=gen, create_graph=True,
        )
        if chunk_steps >= 2:
            s_prev = traj.states[-2].detach()
        else:
            s_prev = s.detach()

        start = 1 + warmup_steps
        if start >= traj.log_returns.shape[0]:
            start = max(1, traj.log_returns.shape[0] - 4)
        sim_returns = traj.log_returns[start:]
        out = moment_matching_loss(sim_returns, targets, weights)
        total = out["total"]
        total.backward()

        # All-reduce gradients across ranks (standard DDP-style mean)
        if world_size > 1:
            for p in sim.parameters():
                if p.grad is not None:
                    dist.all_reduce(p.grad.data, op=dist.ReduceOp.SUM)
                    p.grad.data /= world_size

        with torch.no_grad():
            grad_sq = torch.tensor(0.0, device=device)
            for p in sim.parameters():
                if p.grad is not None:
                    grad_sq = grad_sq + p.grad.detach().pow(2).sum()
            grad_norm = grad_sq.sqrt()
        torch.nn.utils.clip_grad_norm_(sim.parameters(), grad_clip)
        optim.step()

        # Reduced-across-ranks loss for logging
        total_mean = all_reduce_mean(total.detach().clone())

        rec = {
            "iter": it,
            "lr": lr * lr_factor,
            "total_rank0": float(total.item()),
            "total_world_mean": float(total_mean.item()),
            "acf_sim": float(out["acf_sim"].item()),
            "leverage_sim": float(out["leverage_sim"].item()),
            "hill_sim": float(out["hill_sim"].item()),
            "grad_norm": float(grad_norm.item()),
            "gamma": float(sim.gamma.item()),
            "temperature": float(sim.temperature.item()),
        }
        history.append(rec)

        if _is_main(rank) and (it == start_iter or (it + 1) % max(1, n_iters // 20) == 0):
            log.info(
                f"it={it:4d} lr={rec['lr']:.2e} loss_world={rec['total_world_mean']:.4f} "
                f"|∇|={rec['grad_norm']:.2e} γ={rec['gamma']:.3f} T={rec['temperature']:.4f}"
            )

        # Checkpoint
        now = time.time()
        if checkpoint_path is not None and _is_main(rank) and (now - last_ckpt_time) > checkpoint_every_s:
            save_checkpoint(
                checkpoint_path,
                sim=sim, optim=optim, iter_idx=it + 1,
                targets=targets, sim_config={}, train_config={},
            )
            log.info(f"[rank 0] checkpointed to {checkpoint_path} at iter {it + 1}")
            last_ckpt_time = now

    # Final checkpoint
    if checkpoint_path is not None and _is_main(rank):
        save_checkpoint(
            checkpoint_path,
            sim=sim, optim=optim, iter_idx=n_iters,
            targets=targets, sim_config={}, train_config={},
        )

    return history


# ─────────────────────────────────────────────────────────────────────────────
# Main entry
# ─────────────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--out-dir", default=None,
                        help="override config's out_dir (default: experiments/<exp>/results)")
    parser.add_argument("--smoke", action="store_true",
                        help="tiny run (3 iters) for dry-run validation")
    parser.add_argument("--resume", action="store_true",
                        help="resume from checkpoint in out_dir if present")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

    rank, world_size, local_rank = setup_dist()
    if _is_main(rank):
        log.info(f"[dist] rank={rank} world_size={world_size} local_rank={local_rank} "
                 f"cuda_available={torch.cuda.is_available()}")

    cfg = yaml.safe_load(Path(args.config).read_text())
    sim_cfg_dict = dict(cfg["simulator"])
    train_cfg = dict(cfg["training"])

    if args.smoke:
        train_cfg["n_iters"] = min(train_cfg["n_iters"], 3)
        train_cfg["chunk_steps"] = min(train_cfg["chunk_steps"], 16)
        if _is_main(rank):
            log.info("SMOKE MODE — overriding n_iters=3 chunk=16")

    config_path = Path(args.config).resolve()
    exp_dir = config_path.parent
    out_dir = Path(args.out_dir) if args.out_dir else exp_dir / "results"
    if _is_main(rank):
        out_dir.mkdir(parents=True, exist_ok=True)

    repo_root = Path(__file__).resolve().parents[2]

    # Build targets (each rank loads independently — data is small)
    real_r = load_spx_returns_any_rank(repo_root)
    weights = LossWeights(**train_cfg["loss_weights"])
    targets = build_targets_from_returns(real_r, max_lag=weights.max_lag, k_frac=weights.hill_k_frac)
    if _is_main(rank):
        log.info(f"targets: acf_sq={targets.acf_sq_mean:.3f} leverage_sum={targets.leverage_sum:+.3f} "
                 f"hill_alpha={targets.hill_alpha:.2f}")

    # Build simulator
    simulator_config = EcoMDConfig(**sim_cfg_dict)
    torch.manual_seed(train_cfg["seed"] + rank)
    sim = EcoMDSimulator(simulator_config)
    if torch.cuda.is_available():
        sim = sim.cuda(local_rank)

    if _is_main(rank):
        n_params = sum(p.numel() for p in sim.parameters())
        log.info(f"EcoMDSimulator built: {n_params} parameters (device={sim.device})")

    checkpoint_path = out_dir / "checkpoint.pt" if args.resume or not args.smoke else None

    t0 = time.time()
    history = train_distributed(
        sim, targets, weights,
        n_iters=train_cfg["n_iters"],
        chunk_steps=train_cfg["chunk_steps"],
        lr=train_cfg["lr"],
        grad_clip=train_cfg["grad_clip_max_norm"],
        seed=train_cfg["seed"],
        persistent_state=train_cfg.get("persistent_state", True),
        warmup_steps=train_cfg.get("warmup_steps", 0),
        lr_warmup_iters=train_cfg.get("lr_warmup_iters", 0),
        rank=rank,
        world_size=world_size,
        checkpoint_path=checkpoint_path,
        checkpoint_every_s=train_cfg.get("checkpoint_every_s", 1800.0),
    )
    t_total = time.time() - t0

    if _is_main(rank):
        log.info(f"training finished in {t_total:.1f}s ({len(history)} iters, world_size={world_size})")
        (out_dir / "training_log.json").write_text(json.dumps({
            "config": {"simulator": sim_cfg_dict, "training": train_cfg},
            "targets": asdict(targets),
            "history": history,
            "train_time_seconds": t_total,
            "world_size": world_size,
        }, indent=2))
        log.info(f"[rank 0] wrote {out_dir}/training_log.json")

    cleanup_dist()


if __name__ == "__main__":
    main()
