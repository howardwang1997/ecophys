"""Run the zero-cost five-arm semantics preflight on existing SPX/BTC data."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import torch

from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator
from ecomd.training.losses import (
    LossWeights,
    build_targets_from_returns,
    moment_matching_loss,
)
from ecomd.training.train import train_ecomd
from ecomd.training.train_distributed import load_real_returns

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "experiments" / "128_state_semantics_preflight" / "CPU_PREFLIGHT_RESULTS.json"

ARMS: dict[str, dict[str, bool]] = {
    "A_historical": {
        "state_complete": False,
        "legacy_force": True,
        "legacy_jump": True,
    },
    "Aprime_force": {
        "state_complete": False,
        "legacy_force": False,
        "legacy_jump": True,
    },
    "B_state_force": {
        "state_complete": True,
        "legacy_force": False,
        "legacy_jump": True,
    },
    "C_jump_force": {
        "state_complete": False,
        "legacy_force": False,
        "legacy_jump": False,
    },
    "D_combined": {
        "state_complete": True,
        "legacy_force": False,
        "legacy_jump": False,
    },
}

MARKETS = {
    "spx": "2015-2026_daily",
    "btcusdt": "2024Q1_1m",
}


def _config(arm: dict[str, bool]) -> EcoMDConfig:
    return EcoMDConfig(
        n_agents=32,
        d_state=8,
        hidden=16,
        dt=0.02,
        pairwise_kind="stochastic_mlp",
        sps_k_random=6,
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
        jump_lambda=4.0,
        jump_scale=0.03,
        jump_legacy_train_proxy=arm["legacy_jump"],
        legacy_total_derivative_force=arm["legacy_force"],
        memory_kernel_lambda=0.9,
        memory_kernel_strength=0.1,
        microstructure_rho=0.1,
        ar1_whiten_lambda=0.9,
        ar1_whiten_strength=0.1,
        zumbach_feedback_lambda=0.9,
        zumbach_feedback_strength=0.1,
        multi_timescale_enabled=True,
        timescale_fast_frac=0.75,
        timescale_slow_freq=4,
    )


def _parameter_hash(sim: EcoMDSimulator) -> str:
    digest = hashlib.sha256()
    for name, tensor in sorted(sim.state_dict().items()):
        digest.update(name.encode("utf-8"))
        value = tensor.detach().cpu().contiguous()
        digest.update(str(value.dtype).encode("ascii"))
        digest.update(np.asarray(value.shape, dtype=np.int64).tobytes())
        digest.update(value.numpy().tobytes())
    return digest.hexdigest()


def _finite_mapping(values: dict[str, Any]) -> bool:
    for value in values.values():
        if isinstance(value, (float, int)) and not np.isfinite(float(value)):
            return False
    return True


def run_cell(
    market: str,
    period: str,
    arm_name: str,
    arm: dict[str, bool],
    seed: int,
    *,
    n_iters: int,
    chunk_steps: int,
    eval_steps: int,
) -> dict[str, Any]:
    returns = load_real_returns(ROOT, market, period)
    weights = LossWeights(
        w_acf_sq=1.0,
        w_leverage=0.1,
        w_hill=0.05,
        max_lag=5,
        hill_k_frac=0.2,
    )
    targets = build_targets_from_returns(
        returns, max_lag=weights.max_lag, k_frac=weights.hill_k_frac,
        include_multi_fact=False,
    )

    torch.manual_seed(seed)
    cfg = _config(arm)
    sim = EcoMDSimulator(cfg)
    initial_hash = _parameter_hash(sim)
    started = time.perf_counter()
    history = train_ecomd(
        sim,
        targets,
        n_iters=n_iters,
        chunk_steps=chunk_steps,
        lr=1e-3,
        grad_clip=10.0,
        weights=weights,
        seed=seed + 100_000,
        persistent_state=True,
        state_complete=arm["state_complete"],
        warmup_steps=0,
        lr_warmup_iters=0,
    )
    train_seconds = time.perf_counter() - started

    with torch.no_grad():
        trajectory = sim.run(n_steps=eval_steps, seed=seed + 200_000, lightweight=True)
        evaluation = moment_matching_loss(trajectory.log_returns[1:], targets, weights)
    eval_values = {key: float(value.item()) for key, value in evaluation.items()}
    final = history[-1]
    finite = _finite_mapping(final) and _finite_mapping(eval_values)
    return {
        "market": market,
        "period": period,
        "arm": arm_name,
        "factors": arm,
        "seed": seed,
        "n_target_returns": len(returns),
        "train_seconds": train_seconds,
        "initial_parameter_hash": initial_hash,
        "final_parameter_hash": _parameter_hash(sim),
        "final_train": final,
        "evaluation": eval_values,
        "finite": finite,
        "config": asdict(cfg),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--seeds", type=int, nargs="+", default=[13001])
    parser.add_argument("--markets", nargs="+", choices=sorted(MARKETS), default=list(MARKETS))
    parser.add_argument("--n-iters", type=int, default=4)
    parser.add_argument("--chunk-steps", type=int, default=32)
    parser.add_argument("--eval-steps", type=int, default=256)
    parser.add_argument("--threads", type=int, default=2)
    args = parser.parse_args()
    torch.set_num_threads(args.threads)

    cells = []
    for market in args.markets:
        for seed in args.seeds:
            for arm_name, arm in ARMS.items():
                cells.append(run_cell(
                    market, MARKETS[market], arm_name, arm, seed,
                    n_iters=args.n_iters,
                    chunk_steps=args.chunk_steps,
                    eval_steps=args.eval_steps,
                ))

    by_market_seed: dict[str, dict[str, float]] = {}
    for market in args.markets:
        for seed in args.seeds:
            selected = [c for c in cells if c["market"] == market and c["seed"] == seed]
            key = f"{market}:{seed}"
            losses = {c["arm"]: c["evaluation"]["total"] for c in selected}
            by_market_seed[key] = {
                "force_effect_Aprime_minus_A": losses["Aprime_force"] - losses["A_historical"],
                "state_effect_B_minus_Aprime": losses["B_state_force"] - losses["Aprime_force"],
                "jump_effect_C_minus_Aprime": losses["C_jump_force"] - losses["Aprime_force"],
                "combined_minus_A": losses["D_combined"] - losses["A_historical"],
            }

    payload = {
        "experiment": "128_state_semantics_preflight",
        "status": "mechanics_only_not_confirmatory",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "dirty_worktree_expected": True,
        "platform": platform.platform(),
        "torch_version": torch.__version__,
        "device": "cpu",
        "arguments": vars(args) | {"out": str(args.out)},
        "all_cells_finite": all(c["finite"] for c in cells),
        "n_cells": len(cells),
        "contrasts": by_market_seed,
        "cells": cells,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "out": str(args.out),
        "n_cells": len(cells),
        "all_cells_finite": payload["all_cells_finite"],
        "contrasts": by_market_seed,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

