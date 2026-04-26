"""Multi-rank inference / evaluation runner for trained EcoMD v1 checkpoints.

Each rank produces an independent rollout (different seed). Outputs are
written per-rank to avoid any coordination overhead; downstream analysis
merges them.

Stylized-facts computation stays CPU-only (numpy-based compute_all), so
after rollout we detach, move to CPU, and compute per-realization.

Usage (H20):
    torchrun --nproc_per_node=${NPROC:-4} --standalone \\
        -m ecomd.inference.run_large \\
        --ckpt experiments/006_ecomd_v1/results/checkpoint.pt \\
        --config experiments/006_ecomd_v1/config_h20.yaml \\
        --n-steps 4000 \\
        --n-realizations-per-rank 2

On 4 cards × 2 per-rank realizations = 8 total rollouts.
On 8 cards × 2 per-rank = 16 rollouts.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import time
from pathlib import Path

import numpy as np
import torch
import torch.distributed as dist
import yaml

from ..eval.stylized_facts import compute_all
from ..models.ecomd import EcoMDConfig, EcoMDSimulator

log = logging.getLogger("inference_run_large")


def setup_dist() -> tuple[int, int, int]:
    rank = int(os.environ.get("RANK", 0))
    world_size = int(os.environ.get("WORLD_SIZE", 1))
    local_rank = int(os.environ.get("LOCAL_RANK", 0))
    if world_size > 1:
        # NCCL 2.19.3 on current H20 node fails with 4+ ranks (Cuda 101 invalid device ordinal).
        # DIST_BACKEND env var mirrors train_distributed.py override.
        backend = os.environ.get("DIST_BACKEND", "nccl" if torch.cuda.is_available() else "gloo")
        dist.init_process_group(backend=backend, rank=rank, world_size=world_size)
        if torch.cuda.is_available():
            torch.cuda.set_device(local_rank)
    return rank, world_size, local_rank


def cleanup_dist() -> None:
    if dist.is_available() and dist.is_initialized():
        dist.destroy_process_group()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ckpt", required=True, help="path to checkpoint.pt from train_distributed")
    parser.add_argument("--config", required=True, help="simulator config YAML")
    parser.add_argument("--n-steps", type=int, default=4000)
    parser.add_argument("--n-realizations-per-rank", type=int, default=2)
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--seed-base", type=int, default=10_000)
    parser.add_argument("--save-trajectory", action="store_true",
                        help="save (returns, volumes, log_prices) of each "
                             "realization as compressed npz for offline analysis")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

    rank, world_size, local_rank = setup_dist()
    if rank == 0:
        log.info(f"[dist] world_size={world_size} cuda={torch.cuda.is_available()}")

    ckpt_path = Path(args.ckpt).resolve()
    cfg = yaml.safe_load(Path(args.config).read_text())
    sim_cfg_dict = dict(cfg["simulator"])
    simulator_config = EcoMDConfig(**sim_cfg_dict)

    out_dir = Path(args.out_dir) if args.out_dir else ckpt_path.parent
    if rank == 0:
        out_dir.mkdir(parents=True, exist_ok=True)

    sim = EcoMDSimulator(simulator_config)
    ckpt = torch.load(ckpt_path, map_location="cpu")
    sim.load_state_dict(ckpt["sim_state_dict"])
    if torch.cuda.is_available():
        sim = sim.cuda(local_rank)
    sim.eval()

    if rank == 0:
        log.info(f"loaded checkpoint iter={ckpt.get('iter_idx', '?')} from {ckpt_path}")

    rank_results = []
    for r_idx in range(args.n_realizations_per_rank):
        seed = args.seed_base + rank * 1000 + r_idx
        t0 = time.time()
        traj = sim.run(n_steps=args.n_steps, seed=seed)
        dt = time.time() - t0
        returns = traj.log_returns_np()[1:]
        volumes = traj.volumes_np()[1:]
        facts = compute_all(returns, volume=volumes)
        rank_results.append({
            "rank": rank,
            "seed": seed,
            "n_steps": args.n_steps,
            "rollout_time_s": dt,
            "facts": {k: v.to_dict() for k, v in facts.items()},
        })
        log.info(f"[rank {rank}] rollout {r_idx+1}/{args.n_realizations_per_rank} "
                 f"seed={seed} took {dt:.1f}s")

        if args.save_trajectory:
            traj_path = out_dir / f"trajectory_rank{rank}_r{r_idx}.npz"
            np.savez_compressed(
                traj_path,
                log_returns=returns,
                volumes=volumes,
                log_prices=traj.log_prices.detach().cpu().numpy(),
                excess_demand=traj.excess_demand.detach().cpu().numpy(),
                seed=seed, n_steps=args.n_steps, rank=rank,
            )
            log.info(f"[rank {rank}] saved trajectory → {traj_path.name}")

    per_rank_path = out_dir / f"inference_rank_{rank}.json"
    per_rank_path.write_text(json.dumps(rank_results, indent=2))
    log.info(f"[rank {rank}] wrote {per_rank_path}")

    # Rank 0 waits for all, then merges + aggregates
    if world_size > 1:
        dist.barrier()

    if rank == 0:
        all_results: list[dict] = []
        for r in range(world_size):
            p = out_dir / f"inference_rank_{r}.json"
            if p.exists():
                all_results.extend(json.loads(p.read_text()))
        keys = list(all_results[0]["facts"].keys())
        aggregated: dict[str, dict[str, float]] = {}
        for k in keys:
            vals = [float(r["facts"][k]["estimate"])
                    for r in all_results
                    if isinstance(r["facts"][k].get("estimate"), (int, float))
                    and np.isfinite(r["facts"][k].get("estimate"))]
            if vals:
                aggregated[k] = {"mean": float(np.mean(vals)),
                                 "std": float(np.std(vals)),
                                 "n": len(vals)}
        merged_path = out_dir / "inference_merged.json"
        merged_path.write_text(json.dumps({
            "aggregated": aggregated,
            "n_total_rollouts": len(all_results),
            "realizations": all_results,
        }, indent=2))
        log.info(f"[rank 0] merged {len(all_results)} rollouts → {merged_path}")

    cleanup_dist()


if __name__ == "__main__":
    main()
