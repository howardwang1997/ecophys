"""One uninterrupted or resumed stage for experiment 133."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import torch
import torch.distributed as dist

from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator
from ecomd.training.losses import LossWeights, MomentTargets
from ecomd.training.train_distributed import (
    cleanup_dist,
    setup_dist,
    train_distributed,
)


def experiment_config() -> EcoMDConfig:
    return EcoMDConfig(
        n_agents=12,
        d_state=4,
        hidden=8,
        dt=0.005,
        pairwise_kind="stochastic_mlp",
        sps_k_random=4,
        sps_resample_per_step=False,
        regime_enabled=True,
        regime_d=4,
        regime_update_every=2,
        agent_memory_enabled=True,
        agent_memory_d=4,
        agent_memory_update_every=2,
        global_state_enabled=True,
        global_state_d=4,
        global_state_update_every=3,
        global_state_into_pair=True,
        jump_lambda=2.0,
        jump_scale=0.01,
        memory_kernel_lambda=0.8,
        memory_kernel_strength=0.1,
        microstructure_rho=0.1,
        ar1_whiten_lambda=0.8,
        ar1_whiten_strength=0.1,
        zumbach_feedback_lambda=0.8,
        zumbach_feedback_strength=0.1,
        multi_timescale_enabled=True,
        timescale_fast_frac=0.75,
        timescale_slow_freq=3,
    )


def _model_digest(sim: EcoMDSimulator) -> str:
    digest = hashlib.sha256()
    for name, value in sorted(sim.state_dict().items()):
        digest.update(name.encode())
        digest.update(value.detach().cpu().contiguous().numpy().tobytes())
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--stage-record", type=Path, required=True)
    parser.add_argument("--n-iters", type=int, required=True)
    parser.add_argument("--stop-after", type=int)
    parser.add_argument("--seed", type=int, default=133_010)
    parser.add_argument("--device", choices=("cpu", "cuda"), required=True)
    args = parser.parse_args()
    torch.set_num_threads(1)
    rank, world_size, local_rank = setup_dist()
    try:
        torch.manual_seed(args.seed)
        sim = EcoMDSimulator(experiment_config())
        if args.device == "cuda":
            if not torch.cuda.is_available():
                raise RuntimeError("CUDA stage requested but unavailable")
            sim = sim.cuda(local_rank)
        targets = MomentTargets(
            acf_sq_mean=0.08,
            leverage_sum=-0.05,
            hill_alpha=3.2,
        )
        weights = LossWeights(
            w_acf_sq=1.0,
            w_leverage=0.1,
            w_hill=0.05,
            max_lag=3,
            hill_k_frac=0.2,
        )
        history = train_distributed(
            sim,
            targets,
            weights,
            n_iters=args.n_iters,
            chunk_steps=16,
            lr=5e-4,
            grad_clip=10.0,
            seed=args.seed,
            persistent_state=True,
            warmup_steps=0,
            lr_warmup_iters=0,
            rank=rank,
            world_size=world_size,
            checkpoint_path=args.checkpoint,
            checkpoint_every_s=1e12,
            state_complete=True,
            sim_config={"experiment": 133},
            train_config={"n_iters": args.n_iters, "state_complete": True},
            stop_after_iter=args.stop_after,
        )
        digest = _model_digest(sim)
        digests: list[str | None] | None = [None] * world_size if rank == 0 else None
        if world_size > 1:
            dist.gather_object(digest, digests, dst=0)
            dist.barrier()
        elif digests is not None:
            digests[0] = digest
        if rank == 0:
            args.stage_record.parent.mkdir(parents=True, exist_ok=True)
            args.stage_record.write_text(
                json.dumps(
                    {
                        "n_iters": args.n_iters,
                        "stop_after": args.stop_after,
                        "world_size": world_size,
                        "device": args.device,
                        "history": history,
                        "model_digests_by_rank": digests,
                        "ranks_synchronized": len(set(digests or [])) == 1,
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n"
            )
    finally:
        cleanup_dist()


if __name__ == "__main__":
    main()
