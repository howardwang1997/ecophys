"""Diagnose CUDA parity tolerance and long-rollout failure without changing gates."""

from __future__ import annotations

import argparse
import json
import platform
import time
from dataclasses import replace
from pathlib import Path
from typing import Any

import torch
from run_v100_probe import _config, _max_diff

from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator


def _finite_tensor(value: torch.Tensor | None) -> bool:
    return value is None or bool(torch.isfinite(value).all())


def _max_abs(value: torch.Tensor | None) -> float | None:
    if value is None or not _finite_tensor(value):
        return None
    return float(value.detach().abs().max().cpu())


def _parity(config: EcoMDConfig, seed: int, steps: int) -> dict[str, Any]:
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    sim = EcoMDSimulator(config).cuda()
    initial = sim.init_simulator_state(seed=seed)
    inference_state, inference_traj = sim.rollout_state(
        initial.clone(), steps, create_graph=False, lightweight=True
    )
    training_state, training_traj = sim.rollout_state(
        initial.clone(), steps, create_graph=True, lightweight=True
    )
    return {
        "return_max_abs_diff": _max_diff(
            inference_traj.log_returns, training_traj.log_returns
        ),
        "state_max_abs_diff": _max_diff(inference_state.s, training_state.s),
        "rng_state_exact": bool(
            torch.equal(inference_state.rng_state, training_state.rng_state)
        ),
    }


def _stability(config: EcoMDConfig, seed: int, steps: int) -> dict[str, Any]:
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    sim = EcoMDSimulator(config).cuda()
    state = sim.init_simulator_state(seed=seed)
    trace: list[dict[str, Any]] = []
    first_nonfinite: int | None = None
    for step in range(1, steps + 1):
        state, trajectory = sim.rollout_state(
            state, 1, create_graph=False, lightweight=True
        )
        fields = {
            "s": state.s,
            "log_price": state.price_state.log_price,
            "log_return": trajectory.log_returns[-1],
            "h_regime": state.h_regime,
            "h_agent": state.h_agent,
            "h_global": state.h_global,
        }
        finite = all(_finite_tensor(value) for value in fields.values())
        if step in {1, 8, 16, 32, 64, 128, 256, 384, steps} or not finite:
            trace.append(
                {
                    "step": step,
                    "finite": finite,
                    "max_abs": {
                        name: _max_abs(value) for name, value in fields.items()
                    },
                }
            )
        if not finite:
            first_nonfinite = step
            break
    return {
        "completed_steps": state.step_idx,
        "first_nonfinite_step": first_nonfinite,
        "all_finite": first_nonfinite is None,
        "trace": trace,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--git-sha", required=True)
    parser.add_argument("--n-agents", type=int, default=500)
    parser.add_argument("--steps", type=int, default=512)
    parser.add_argument("--seed", type=int, default=128_501)
    args = parser.parse_args()
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required")

    full = _config(args.n_agents)
    variants = {
        "full": full,
        "no_jumps": replace(full, jump_lambda=0.0, jump_scale=0.0),
        "no_feedback": replace(
            full,
            memory_kernel_lambda=0.0,
            memory_kernel_strength=0.0,
            microstructure_rho=0.0,
            ar1_whiten_lambda=0.0,
            ar1_whiten_strength=0.0,
            zumbach_feedback_lambda=0.0,
            zumbach_feedback_strength=0.0,
        ),
        "no_recurrent_latents": replace(
            full,
            regime_enabled=False,
            agent_memory_enabled=False,
            global_state_enabled=False,
            global_state_into_pair=False,
        ),
        "quarter_dt": replace(full, dt=full.dt / 4.0),
    }
    started = time.perf_counter()
    parity = {
        "full": _parity(full, args.seed, 12),
        "no_jumps": _parity(variants["no_jumps"], args.seed, 12),
    }
    stability = {
        name: _stability(config, args.seed + 1, args.steps)
        for name, config in variants.items()
    }
    payload = {
        "experiment": "128_state_semantics_v100_diagnostic",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_sha": args.git_sha,
        "platform": platform.platform(),
        "torch_version": torch.__version__,
        "cuda_version": torch.version.cuda,
        "gpu": torch.cuda.get_device_name(0),
        "arguments": vars(args) | {"out": str(args.out)},
        "parity": parity,
        "stability": stability,
        "wall_seconds": time.perf_counter() - started,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
