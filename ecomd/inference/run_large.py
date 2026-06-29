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
    # exp 123 driven-transient: inject a shock mid-rollout (no-op unless --shock-step set).
    parser.add_argument("--shock-step", type=int, default=None,
                        help="step at which to inject a shock (exp 123); None = no shock (control)")
    parser.add_argument("--shock-type",
                        choices=["state_kick", "price_jump", "news",
                                 "temperature_spike", "liquidity_drop"],
                        default="state_kick")
    parser.add_argument("--shock-mag", type=float, default=6.0,
                        help="state_kick/price_jump: magnitude in σ-units; news: Δfundamental; "
                             "temperature_spike: T multiplier (>1); liquidity_drop: friction-drop "
                             "dose d (γ multiplied by 1/d, so larger d = stronger drop)")
    parser.add_argument("--shock-dur", type=int, default=1,
                        help="temperature_spike/liquidity_drop: number of steps the transient "
                             "multiplier stays on before auto-clearing (system then relaxes)")
    parser.add_argument("--shock-frac", type=float, default=0.1,
                        help="state_kick: fraction of agents displaced")
    parser.add_argument("--shock-sign", type=float, default=-1.0,
                        help="price_jump: gap direction (-1 = down/crash; tail index is sign-blind)")
    parser.add_argument("--shock-every", type=int, default=0,
                        help="if >0, repeat the shock every N steps from --shock-step to end "
                             "(multi-transient-per-rollout variant)")
    # exp 125 root-cause ablations: inference-time config overrides on a trained
    # checkpoint (fixed learned dynamics). --noise-* probes whether a heavy
    # microscopic bath fattens the *steady-state* aggregate tail (Route A);
    # --n-agents probes CLT self-averaging at fixed dynamics (steady α_ED vs N).
    parser.add_argument("--noise-dist", choices=["normal", "t", "levy"], default=None,
                        help="override the bath noise distribution at inference")
    parser.add_argument("--noise-df", type=int, default=None, help="Student-t df (with --noise-dist t)")
    parser.add_argument("--noise-levy-alpha", type=float, default=None,
                        help="α-stable index in (0,2] (with --noise-dist levy)")
    parser.add_argument("--n-agents", type=int, default=None,
                        help="override the number of agents N (CLT self-averaging probe)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

    rank, world_size, local_rank = setup_dist()
    if rank == 0:
        log.info(f"[dist] world_size={world_size} cuda={torch.cuda.is_available()}")

    ckpt_path = Path(args.ckpt).resolve()
    cfg = yaml.safe_load(Path(args.config).read_text())
    sim_cfg_dict = dict(cfg["simulator"])
    # exp 125 inference-time overrides (fixed trained dynamics; see CLI help).
    if args.noise_dist is not None:
        sim_cfg_dict["noise_dist"] = args.noise_dist
    if args.noise_df is not None:
        sim_cfg_dict["noise_df"] = args.noise_df
    if args.noise_levy_alpha is not None:
        sim_cfg_dict["noise_levy_alpha"] = args.noise_levy_alpha
    if args.n_agents is not None:
        sim_cfg_dict["n_agents"] = args.n_agents
    simulator_config = EcoMDConfig(**sim_cfg_dict)
    if rank == 0 and any(v is not None for v in
                         (args.noise_dist, args.noise_df, args.noise_levy_alpha, args.n_agents)):
        log.info(f"[exp125] overrides: noise_dist={sim_cfg_dict.get('noise_dist')} "
                 f"noise_df={sim_cfg_dict.get('noise_df')} "
                 f"levy_alpha={sim_cfg_dict.get('noise_levy_alpha')} "
                 f"n_agents={sim_cfg_dict.get('n_agents')}")

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

    # exp 123: build the shock schedule once (persists across this rank's rollouts).
    if args.shock_step is not None:
        if args.shock_type == "news":
            spec = {"type": "news", "delta_f": args.shock_mag}
        elif args.shock_type == "price_jump":
            spec = {"type": "price_jump", "mag": args.shock_mag, "sign": args.shock_sign}
        elif args.shock_type == "temperature_spike":
            spec = {"type": "temperature_spike", "mult": args.shock_mag, "dur": args.shock_dur}
        elif args.shock_type == "liquidity_drop":
            # dose d → friction multiplied by 1/d (larger d = stronger liquidity drop)
            spec = {"type": "liquidity_drop", "mult": 1.0 / args.shock_mag, "dur": args.shock_dur}
        else:
            spec = {"type": "state_kick", "frac": args.shock_frac, "mag": args.shock_mag}
        steps = (range(args.shock_step, args.n_steps, args.shock_every)
                 if args.shock_every > 0 else [args.shock_step])
        sim._shock_schedule = {int(k): spec for k in steps}
        if rank == 0:
            log.info(f"[exp123] shock {spec} at steps {list(sim._shock_schedule)}")

    rank_results = []
    for r_idx in range(args.n_realizations_per_rank):
        seed = args.seed_base + rank * 1000 + r_idx
        t0 = time.time()
        # lightweight: run_large only consumes the (T,) scalar series (returns/volumes/
        # log_prices/excess_demand); dropping the (T,N,d) tensors avoids OOM at N=10⁴.
        traj = sim.run(n_steps=args.n_steps, seed=seed, lightweight=True)
        dt = time.time() - t0
        returns = traj.log_returns_np()[1:]
        volumes = traj.volumes_np()[1:]
        traj_np = None
        if args.save_trajectory:
            traj_np = {
                "log_returns": returns,
                "volumes": volumes,
                "log_prices": traj.log_prices.detach().cpu().numpy(),
                "excess_demand": traj.excess_demand.detach().cpu().numpy(),
                # exp 123 (P1): 1 if excess_demand is the raw pre-impact tail (ζ_ED).
                "ed_is_raw": int(getattr(traj, "meta", {}).get("ed_is_raw", 0)),
                # exp 123 Route-A: signed order-flow imbalance ρ∈[-1,1] (drop step 0).
                "ofi": traj.ofi_np()[1:],
            }
        del traj
        facts = compute_all(returns, volume=volumes)
        rank_results.append({
            "rank": rank,
            "seed": seed,
            "n_steps": args.n_steps,
            "rollout_time_s": dt,
            "facts": {k: v.to_dict() for k, v in facts.items()},
        })
        del returns, volumes, facts
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        log.info(f"[rank {rank}] rollout {r_idx+1}/{args.n_realizations_per_rank} "
                 f"seed={seed} took {dt:.1f}s")

        if args.save_trajectory and traj_np is not None:
            traj_path = out_dir / f"trajectory_rank{rank}_r{r_idx}.npz"
            np.savez_compressed(
                traj_path,
                seed=seed, n_steps=args.n_steps, rank=rank,
                **traj_np,
            )
            log.info(f"[rank {rank}] saved trajectory → {traj_path.name}")
            del traj_np

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
