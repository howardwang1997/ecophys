"""Phase 7 — Spatial-checkpoint memory tests.

Tests whether spatial-sharded pairwise potential lets us push chunk_steps
and N beyond the chunk=24 N=10K = 80 GB ceiling found yesterday.

Each config trains 5 iters and writes peak HBM via training_log.json's
peak_hbm field. Memory floor for current arch is 80 GB at chunk=24 N=10K
B=0 (no spatial batching). This phase tests whether B > 0 unlocks larger
chunk and N.

Run:
    conda run -n ecophys python experiments/029_spatial_checkpoint/generate_configs.py
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent

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
        "sps_spatial_batch_size": 0,        # default off
        "twopop_enabled": True,
        "twopop_gamma_scale": [0.7, 1.5, 1.0, 0.5],
        "twopop_temp_scale":  [0.5, 2.0, 1.0, 0.3],
        "v2_type_seed": 42,
        "bptt_checkpoint_every": 0,
    },
    "training": {
        "n_iters": 5,                       # short — peak HBM in <1min
        "chunk_steps": 24,
        "warmup_steps": 16,
        "persistent_state": True,
        "lr": 1.0e-3,
        "lr_warmup_iters": 1,
        "grad_clip_max_norm": 100.0,
        "seed": 0,
        "checkpoint_every_s": 999999,
        "target_dataset": "spx",
        "target_period": "2015-2026_daily",
        "loss_weights": {
            "w_acf_sq": 1.0, "w_leverage": 0.2, "w_hill": 0.1,
            "max_lag": 8, "hill_k_frac": 0.05,
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


# Test grid: each row should print its peak HBM. Spatial batch B in number
# of EDGES (not agents). At N=10K k=50, total edges = 500K.
PROFILES = [
    # (name, comment, N, chunk, K_bptt, B_spatial)
    ("p7_baseline_n10k_chunk24_B0",
     "Baseline reproduction (no spatial sharding) — should match 80 GB",
     10000, 24, 0, 0),
    ("p7_n10k_chunk24_B100k",
     "Spatial B=100K (5 batches) at chunk=24 — does B alone reduce memory?",
     10000, 24, 0, 100_000),
    ("p7_n10k_chunk24_B50k",
     "Spatial B=50K (10 batches) at chunk=24 — finer batching",
     10000, 24, 0, 50_000),
    ("p7_n10k_chunk64_B50k",
     "chunk=64 + B=50K — does spatial enable longer chunks?",
     10000, 64, 0, 50_000),
    ("p7_n10k_chunk128_B50k",
     "chunk=128 + B=50K — push chunk further",
     10000, 128, 0, 50_000),
    ("p7_n10k_chunk64_B50k_K8",
     "chunk=64 + B=50K + BPTT K=8 — combine spatial + temporal sharding",
     10000, 64, 8, 50_000),
    ("p7_n20k_chunk24_B50k",
     "N=20K + B=50K — does spatial enable larger N at chunk=24?",
     20000, 24, 0, 50_000),
    ("p7_n50k_chunk24_B50k",
     "N=50K + B=50K — push N further",
     50000, 24, 0, 50_000),
]


def main():
    for name, comment, N, chunk, K_bptt, B in PROFILES:
        cfg = deep_merge(BASE, {
            "simulator": {
                "n_agents": N,
                "bptt_checkpoint_every": K_bptt,
                "sps_spatial_batch_size": B,
            },
            "training": {
                "chunk_steps": chunk,
                "warmup_steps": min(BASE["training"]["warmup_steps"], chunk - 4),
            },
        })
        p = HERE / f"config_{name}.yaml"
        text = "# " + comment + "\n\n"
        text += yaml.safe_dump(cfg, sort_keys=False, default_flow_style=False)
        p.write_text(text)
        print(f"  {name}: N={N}, chunk={chunk}, K_bptt={K_bptt}, B={B}")
    print(f"\nWrote {len(PROFILES)} configs to {HERE}/")


if __name__ == "__main__":
    main()
