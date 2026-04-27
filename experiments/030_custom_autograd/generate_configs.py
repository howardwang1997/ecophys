"""Phase 8 — Custom autograd.Function HBM test.

Tests whether ``bptt_custom_function=True`` reduces peak HBM by bounding
memory at one step's V-graph regardless of chunk_steps. Each config
trains 5 iters; peak HBM in training_log.json's peak_hbm field.

Goal: confirm memory ≤ 5 GB for chunk=128 N=10K (vs ~80 GB at chunk=24
on default path), establishing that the Function approach actually
unlocks long-chunk training even when the standard
torch.utils.checkpoint approach failed.

Run:
    conda run -n ecophys python experiments/030_custom_autograd/generate_configs.py
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
        "twopop_enabled": True,
        "twopop_gamma_scale": [0.7, 1.5, 1.0, 0.5],
        "twopop_temp_scale":  [0.5, 2.0, 1.0, 0.3],
        "v2_type_seed": 42,
        "bptt_checkpoint_every": 0,
        "bptt_custom_function": False,
    },
    "training": {
        "n_iters": 5,
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


PROFILES = [
    # (name, comment, N, chunk, bptt_custom_function)
    ("p8_baseline_n10k_chunk24_default",
     "Baseline reproduction (default path) — ~80 GB target",
     10000, 24, False),
    ("p8_n10k_chunk24_custom",
     "chunk=24 with custom Function — should be ~few GB peak",
     10000, 24, True),
    ("p8_n10k_chunk64_custom",
     "chunk=64 with custom Function — should be ~few GB (vs OOM on default)",
     10000, 64, True),
    ("p8_n10k_chunk128_custom",
     "chunk=128 with custom Function — should be ~few GB",
     10000, 128, True),
    ("p8_n20k_chunk64_custom",
     "N=20K chunk=64 with custom Function — does N scaling stay bounded?",
     20000, 64, True),
    ("p8_n50k_chunk64_custom",
     "N=50K chunk=64 with custom Function — push the envelope",
     50000, 64, True),
]


def main():
    for name, comment, N, chunk, custom in PROFILES:
        cfg = deep_merge(BASE, {
            "simulator": {
                "n_agents": N,
                "bptt_custom_function": custom,
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
        print(f"  {name}: N={N}, chunk={chunk}, custom_function={custom}")
    print(f"\nWrote {len(PROFILES)} configs to {HERE}/")


if __name__ == "__main__":
    main()
