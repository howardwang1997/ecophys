"""Single-card CUDA parity, exact-resume, runtime and memory probe for WP1."""

from __future__ import annotations

import argparse
import io
import json
import platform
import subprocess
import time
from pathlib import Path

import torch

from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator, SimulatorState

ROOT = Path(__file__).resolve().parents[2]


def _config(n_agents: int) -> EcoMDConfig:
    return EcoMDConfig(
        n_agents=n_agents,
        d_state=16,
        hidden=32,
        dt=0.02,
        pairwise_kind="stochastic_mlp",
        sps_k_random=16,
        sps_resample_per_step=False,
        regime_enabled=True,
        regime_d=8,
        regime_update_every=3,
        agent_memory_enabled=True,
        agent_memory_d=8,
        agent_memory_update_every=2,
        global_state_enabled=True,
        global_state_d=8,
        global_state_update_every=3,
        global_state_into_pair=True,
        jump_lambda=2.0,
        jump_scale=0.02,
        memory_kernel_lambda=0.9,
        memory_kernel_strength=0.1,
        microstructure_rho=0.1,
        ar1_whiten_lambda=0.9,
        ar1_whiten_strength=0.1,
        zumbach_feedback_lambda=0.9,
        zumbach_feedback_strength=0.1,
        multi_timescale_enabled=True,
        timescale_fast_frac=0.8,
        timescale_slow_freq=4,
    )


def _max_diff(left: torch.Tensor, right: torch.Tensor) -> float:
    return float((left.detach() - right.detach()).abs().max().cpu())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--n-agents", type=int, default=500)
    parser.add_argument("--parity-steps", type=int, default=32)
    parser.add_argument("--long-steps", type=int, default=512)
    parser.add_argument("--seed", type=int, default=128_500)
    parser.add_argument(
        "--git-sha",
        help="source commit, required when the remote code snapshot has no .git directory",
    )
    args = parser.parse_args()
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for the V100 probe")
    if args.parity_steps <= 11:
        raise ValueError("parity-steps must exceed 11 for the frozen partition")
    if args.long_steps <= 0:
        raise ValueError("long-steps must be positive")

    device = torch.device("cuda:0")
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    sim = EcoMDSimulator(_config(args.n_agents)).to(device)
    initial = sim.init_simulator_state(seed=args.seed)
    torch.cuda.reset_peak_memory_stats(device)
    torch.cuda.synchronize(device)
    started = time.perf_counter()

    full_state, full_traj = sim.rollout_state(
        initial.clone(), args.parity_steps, create_graph=False, lightweight=True
    )
    partition = [3, 7, 1, args.parity_steps - 11]
    chunk_state = initial.clone()
    chunk_returns = []
    for length in partition:
        chunk_state, trajectory = sim.rollout_state(
            chunk_state, length, create_graph=False, lightweight=True
        )
        chunk_returns.append(trajectory.log_returns)
    chunk_returns_tensor = torch.cat(chunk_returns)

    midpoint, first = sim.rollout_state(
        initial.clone(), 11, create_graph=False, lightweight=True
    )
    checkpoint = io.BytesIO()
    torch.save(midpoint.to_checkpoint(), checkpoint)
    checkpoint.seek(0)
    restored = SimulatorState.from_checkpoint(
        torch.load(checkpoint, weights_only=False)
    )
    resumed, second = sim.rollout_state(
        restored,
        args.parity_steps - 11,
        create_graph=False,
        lightweight=True,
    )
    resumed_returns = torch.cat([first.log_returns, second.log_returns])

    inference_state, inference_traj = sim.rollout_state(
        initial.clone(), 12, create_graph=False, lightweight=True
    )
    training_state, training_traj = sim.rollout_state(
        initial.clone(), 12, create_graph=True, lightweight=True
    )
    jump_return_diff = _max_diff(inference_traj.log_returns, training_traj.log_returns)
    jump_state_diff = _max_diff(inference_state.s, training_state.s)
    training_traj.log_returns.square().mean().backward()
    finite_gradients = all(
        parameter.grad is None or bool(torch.isfinite(parameter.grad).all())
        for parameter in sim.parameters()
    )

    long_initial = sim.init_simulator_state(seed=args.seed + 1)
    long_state, long_traj = sim.rollout_state(
        long_initial, args.long_steps, create_graph=False, lightweight=True
    )
    torch.cuda.synchronize(device)
    wall_seconds = time.perf_counter() - started

    checks = {
        "chunk_returns_exact": _max_diff(full_traj.log_returns, chunk_returns_tensor) == 0.0,
        "chunk_final_state_exact": _max_diff(full_state.s, chunk_state.s) == 0.0,
        "resume_returns_exact": _max_diff(full_traj.log_returns, resumed_returns) == 0.0,
        "resume_final_state_exact": _max_diff(full_state.s, resumed.s) == 0.0,
        "jump_create_graph_returns_exact": jump_return_diff == 0.0,
        "jump_create_graph_state_exact": jump_state_diff == 0.0,
        "finite_gradients": finite_gradients,
        "long_rollout_finite": bool(torch.isfinite(long_traj.log_returns).all()),
        "long_clock_exact": long_state.step_idx == args.long_steps,
    }
    payload = {
        "experiment": "128_state_semantics_v100_probe",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_sha": args.git_sha
        or subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "platform": platform.platform(),
        "torch_version": torch.__version__,
        "cuda_version": torch.version.cuda,
        "gpu": torch.cuda.get_device_name(device),
        "arguments": vars(args) | {"out": str(args.out)},
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "max_differences": {
            "chunk_returns": _max_diff(full_traj.log_returns, chunk_returns_tensor),
            "chunk_final_state": _max_diff(full_state.s, chunk_state.s),
            "resume_returns": _max_diff(full_traj.log_returns, resumed_returns),
            "resume_final_state": _max_diff(full_state.s, resumed.s),
            "jump_create_graph_returns": jump_return_diff,
            "jump_create_graph_state": jump_state_diff,
        },
        "wall_seconds": wall_seconds,
        "peak_allocated_bytes": torch.cuda.max_memory_allocated(device),
        "peak_reserved_bytes": torch.cuda.max_memory_reserved(device),
        "long_returns_std": float(long_traj.log_returns.std().cpu()),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
