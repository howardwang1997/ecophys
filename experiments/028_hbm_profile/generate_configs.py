"""Generate Phase 6 HBM profiling configs.

Each config trains for only 3 iters with checkpoint saving disabled —
just enough to capture peak GPU memory via torch.cuda.max_memory_allocated.

Goal: get a (N, chunk_steps, K) → peak HBM ground-truth table to
calibrate our memory model and decide whether spatial-sharded pairwise
is needed for Phase 4 N=50K (or higher N in follow-up).

Output configs go to experiments/028_hbm_profile/. Each runs ~30s
on H20 (3 iters, no eval); peak HBM read from training_log.json's
new "peak_hbm" field.

Run on Mac:
    conda run -n ecophys python experiments/028_hbm_profile/generate_configs.py
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent

# Same C4 base as Phase 1 — single-asset SPX, multi-asset off.
BASE: dict = {
    "simulator": {
        "n_agents": 10000,
        "d_state": 32,
        "hidden": 48,
        "dt": 0.01,
        "gamma_init": 1.0,
        "temperature_init": 0.05,
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
    },
    "training": {
        "n_iters": 3,                # JUST 3 ITERS — only need peak HBM
        "chunk_steps": 24,
        "warmup_steps": 16,
        "persistent_state": True,
        "lr": 1.0e-3,
        "lr_warmup_iters": 1,        # too short to matter
        "grad_clip_max_norm": 100.0,
        "seed": 0,
        "checkpoint_every_s": 999999, # disable periodic ckpt save
        "target_dataset": "spx",
        "target_period": "2015-2026_daily",
        "loss_weights": {
            "w_acf_sq": 1.0, "w_leverage": 0.2, "w_hill": 0.1,
            "max_lag": 8, "hill_k_frac": 0.05,
            "w_autocorr_r": 0.5, "w_hill_max": 0.3, "hill_max_target": 10.0,
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


# 6 profile points covering the (N, chunk, K) corners we care about
PROFILES = [
    # (name, comment, N, chunk, K)
    ("p6_baseline_n10k_chunk24_K0",
     "Baseline reproduction — should be ~85 GB on H20 (calibration)",
     10000, 24, 0),
    ("p6_n10k_chunk128_K8",
     "Phase 1 chunk128 — predicted ~28 GB",
     10000, 128, 8),
    ("p6_n10k_chunk128_K4",
     "K halved vs above — predicted ~14 GB (verifies K linearity)",
     10000, 128, 4),
    ("p6_n20k_chunk128_K8",
     "N doubled vs phase1 — predicted ~56 GB (verifies N linearity)",
     20000, 128, 8),
    ("p6_n50k_chunk128_K4",
     "Phase 4 N=50K analog — predicted ~70 GB (tight)",
     50000, 128, 4),
    ("p6_n100k_chunk64_K2",
     "Beyond Phase 4 — predicted ~70 GB; if OOM, sets ceiling for now",
     100000, 64, 2),
]


def main():
    for name, comment, N, chunk, K in PROFILES:
        cfg = deep_merge(BASE, {
            "simulator": {
                "n_agents": N,
                "bptt_checkpoint_every": K,
            },
            "training": {
                "chunk_steps": chunk,
                # warmup must be < chunk; clamp.
                "warmup_steps": min(BASE["training"]["warmup_steps"], chunk - 4),
            },
        })
        p = HERE / f"config_{name}.yaml"
        text = "# " + comment + "\n\n"
        text += yaml.safe_dump(cfg, sort_keys=False, default_flow_style=False)
        p.write_text(text)
        print(f"  {name}: N={N}, chunk={chunk}, K={K}")
    print(f"\nWrote {len(PROFILES)} configs to {HERE}/")


if __name__ == "__main__":
    main()
