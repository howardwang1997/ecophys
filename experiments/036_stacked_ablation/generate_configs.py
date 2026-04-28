"""Phase F-ablation — what destroys the stacked winner?

Phase 035 stacked all 3 confirmed effects (Sprint 2 + chunk=128 + h96 +
init=0.1) and got mean 2.40/11 — WORSE than any single lever alone
(s01_h96 = 5.00, sprint2 = 3.20, chunk128 = 3.20). Effects are not
additive; some sub-pair has destructive interaction.

This ablation: take the stacked config, remove ONE knob at a time, run
10 seeds per cell. The cell whose mean RECOVERS to ≥ 4-5/11 names the
guilty knob (i.e., that knob is the one that breaks the stack).

| cell             | what we revert        | tests hypothesis                  |
|---               |---                    |---                                |
| `abl_no_sprint2` | bptt_custom_function: false (default path) | "Sprint 2 + long chunk + big h interact badly" |
| `abl_no_chunk128`| chunk=24, max_lag=8, k_frac=0.05 (revert to chunk=24 stack)  | "chunk=128 + h96 + long-BPTT is bad" (most likely) |
| `abl_no_h96`     | hidden=48                                  | "hidden=96 needs different lr/chunk" |
| `abl_no_init01`  | init_state_scale=0.05 (Phase H's 2nd-best) | "init=0.1 interacts only with h96 at chunk=24" |

10 seeds per cell × 4 cells = 40 configs. ~30-60 min on 8-card.

Bonus: `abl_no_chunk128 + abl_no_sprint2` corner gives a 10-seed re-test
of Phase H's s01_h96 winner (was only 2 seeds = mean 5.00). If that
also drops to ~3/11, the original winner was lottery, not a real cell.

Run on Mac:
    conda run -n ecophys python experiments/036_stacked_ablation/generate_configs.py
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent

# ── Stacked-winner BASE (035, mean 2.40, target = recover by removing
#    one knob at a time)
BASE: dict = {
    "simulator": {
        "n_agents": 10000,
        "d_state": 32,
        "hidden": 96,                          # ← knob (h96)
        "dt": 0.01,
        "gamma_init": 1.0,
        "temperature_init": 0.05,
        "init_state_scale": 0.1,               # ← knob (init01)
        "lam_dissipation": 0.01,
        "learn_gamma": True, "learn_temperature": True,
        "noise_dist": "t", "noise_df": 5,
        "price_formation": "excess_demand",
        "price_formation_kwargs": {
            "beta": 0.02, "kappa": 0.5, "sigma_price": 0.005,
            "ewma_alpha": 0.05, "initial_log_price": 0.0,
            "learnable_beta": False, "beta_hidden": 16,
            "hawkes_alpha": 0.1, "hawkes_kappa": 0.3,
        },
        "pairwise_kind": "stochastic_mlp",
        "sps_k_random": 50, "sps_resample_per_step": True,
        "twopop_enabled": True,
        "twopop_gamma_scale": [0.7, 1.5, 1.0, 0.5],
        "twopop_temp_scale":  [0.5, 2.0, 1.0, 0.3],
        "v2_type_seed": 42,
        "bptt_checkpoint_every": 0,
        "bptt_custom_function": True,           # ← knob (sprint2)
    },
    "training": {
        "n_iters": 200,
        "chunk_steps": 128,                     # ← knob (chunk128)
        "warmup_steps": 16,
        "persistent_state": True,
        "lr": 1.0e-3,
        "lr_warmup_iters": 10,
        "grad_clip_max_norm": 100.0,
        "seed": 0,
        "checkpoint_every_s": 1800,
        "target_dataset": "spx",
        "target_period": "2015-2026_daily",
        "loss_weights": {
            "w_acf_sq": 1.0, "w_leverage": 0.2, "w_hill": 0.1,
            "max_lag": 20,                      # ← tied to chunk128
            "hill_k_frac": 0.1,                 # ← tied to chunk128
            "w_autocorr_r": 0.5, "w_hill_max": 0.3, "hill_max_target": 10.0,
            "loss_family": "moments",
            "distance_mode": "l1",
            "tail_estimator": "soft_hill",
            "balance_mode": "fixed",
        },
    },
}


# Per-cell overrides (what to REVERT from the stacked base)
CELLS = {
    "abl_no_sprint2": {
        "simulator": {"bptt_custom_function": False},
    },
    "abl_no_chunk128": {
        "training": {
            "chunk_steps": 24,
            "loss_weights": {
                "max_lag": 8,
                "hill_k_frac": 0.05,
            },
        },
    },
    "abl_no_h96": {
        "simulator": {"hidden": 48},
    },
    "abl_no_init01": {
        "simulator": {"init_state_scale": 0.05},
    },
}


def deep_merge(base, ov):
    out = copy.deepcopy(base)
    for k, v in ov.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def write(name: str, comment: str, overrides: dict) -> None:
    cfg = deep_merge(BASE, overrides)
    p = HERE / f"config_{name}.yaml"
    text = "# " + comment + "\n\n"
    text += yaml.safe_dump(cfg, sort_keys=False, default_flow_style=False)
    p.write_text(text)


def main() -> None:
    print(f"Writing stacked-ablation configs to {HERE}/")
    for cell_name, cell_overrides in CELLS.items():
        for seed in range(10):
            full_overrides = deep_merge(cell_overrides, {"training": {"seed": seed}})
            name = f"{cell_name}_seed{seed}"
            comment = (
                f"Phase F-ablation cell `{cell_name}`: stacked winner with "
                f"one knob reverted, seed={seed}. Override: {cell_overrides}"
            )
            write(name, comment, full_overrides)
        print(f"  {cell_name}: 10 seeds")
    n = len(list(HERE.glob("config_*.yaml")))
    print(f"\nWrote {n} configs (target 40).")


if __name__ == "__main__":
    main()
