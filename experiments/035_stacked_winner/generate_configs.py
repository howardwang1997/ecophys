"""Phase E — stacked-winner multi-seed CI.

Stacks ALL three confirmed effects from Phase 032/033/034:

  1. Sprint 2 path  (Phase 034: mean +0.8 vs default; contamination IS real)
  2. chunk=128 + max_lag=20 + hill_k_frac=0.1  (Phase 033: std × 0.52 with
     proper window scaling at long chunk)
  3. hidden=96 + init_state_scale=0.1  (Phase H: best ablation cell mean
     5.00, also reaches the only 6/11 score across all of today's runs)

Plus the existing C4 architecture defaults (twopop, Hawkes).

Test: 10 seeds × single stacked config. If effects are at least partially
additive, expected mean ~5-6/11 (vs Phase H individual lever ~3/11,
Phase 034 sprint2 alone 3.20, Phase 033 chunk=128 alone 3.20). This is
the paper §5 candidate.

Decision rule:
  - If mean ≥ 5/11 across 10 seeds with std ≤ 1.5 → matches GARCH 5-7/11
    baseline; paper story holds. Move to multi-arch + N-scale + universality
    next.
  - If mean ~4-4.5/11 → effects partially compose but don't hit GARCH
    parity. Still useful but reframes paper.
  - If mean ~3/11 → effects are not additive (maybe they hit the same
    bottleneck differently). Need deeper architectural intervention.

Run on Mac:
    conda run -n ecophys python experiments/035_stacked_winner/generate_configs.py
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent

# Stacked winner config — combines confirmed effects from 3 phases.
BASE: dict = {
    "simulator": {
        "n_agents": 10000,
        "d_state": 32,
        # ★ Phase H finding: hidden=96 dominates hidden=48 for all init scales
        "hidden": 96,
        "dt": 0.01,
        "gamma_init": 1.0,
        "temperature_init": 0.05,
        # ★ Phase H finding: init_state_scale=0.1 + hidden=96 cell = mean 5.00
        "init_state_scale": 0.1,
        "lam_dissipation": 0.01,
        "learn_gamma": True,
        "learn_temperature": True,
        "noise_dist": "t",
        "noise_df": 5,
        "price_formation": "excess_demand",
        "price_formation_kwargs": {
            "beta": 0.02, "kappa": 0.5, "sigma_price": 0.005,
            "ewma_alpha": 0.05, "initial_log_price": 0.0,
            "learnable_beta": False, "beta_hidden": 16,
            "hawkes_alpha": 0.1, "hawkes_kappa": 0.3,
        },
        "pairwise_kind": "stochastic_mlp",
        "sps_k_random": 50,
        "sps_resample_per_step": True,
        "twopop_enabled": True,
        "twopop_gamma_scale": [0.7, 1.5, 1.0, 0.5],
        "twopop_temp_scale":  [0.5, 2.0, 1.0, 0.3],
        "v2_type_seed": 42,
        "bptt_checkpoint_every": 0,
        # ★ Phase 034 finding: Sprint 2 path mean +0.8 over default
        "bptt_custom_function": True,
    },
    "training": {
        "n_iters": 200,
        # ★ Phase 033 finding: chunk=128 + scaled max_lag → std × 0.52
        "chunk_steps": 128,
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
            # ★ Phase 033 scaling: max_lag uses long-chunk capacity;
            # k_frac=0.1 gives ~11 hill tail samples at chunk=128
            "max_lag": 20,
            "hill_k_frac": 0.1,
            "w_autocorr_r": 0.5, "w_hill_max": 0.3, "hill_max_target": 10.0,
            "loss_family": "moments",
            "distance_mode": "l1",
            "tail_estimator": "soft_hill",
            "balance_mode": "fixed",
        },
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
    print(f"Writing stacked-winner configs to {HERE}/")
    for seed in range(10):
        name = f"sw_stacked_seed{seed}"
        comment = (
            f"Phase E stacked winner: Sprint 2 + chunk=128 + max_lag=20 + "
            f"hill_k_frac=0.1 + hidden=96 + init_state_scale=0.1, seed={seed}. "
            f"Combined from Phase 032/033/034 winners."
        )
        write(name, comment, {"training": {"seed": seed}})
        print(f"  {name}")
    n = len(list(HERE.glob("config_*.yaml")))
    print(f"\nWrote {n} configs.")


if __name__ == "__main__":
    main()
