"""Phase C-fix — Loss-noise hypothesis with PROPER sample-size scaling.

The original Phase C (031_chunk_effect) was confounded: max_lag=8 was
hardcoded across all chunks, so chunk=64 and chunk=128 used the SAME
8-lag spectrum on ACF/leverage. Only the *averaging* sample size differed.

This corrected version scales BOTH max_lag and k_frac with chunk so the
loss really sees more "lag spectrum" + more "tail samples" at long
chunks:

| chunk | sim_returns | max_lag | k_frac | hill k ≈ |
|---:|---:|---:|---:|---:|
|  24 |   7 |   6 | 0.50 |  4 |   ← effectively chunk=24's natural ceiling
|  64 |  47 |  20 | 0.20 |  9 |   ← 3x lags, 2x tail samples
| 128 | 111 |  20 | 0.10 | 11 |   ← saturates max_lag, 3x tail samples

Hypothesis (re-test): if longer chunk + more loss samples really reduces
estimator noise, mean should move OR std should drop with chunk.

5 seeds × 3 chunks = 15 configs, single-asset SPX, Sprint 2 path
(memory-bounded so chunk=128 fits easily).

Note: chunk=24 case keeps max_lag=6 because sim_returns=7 can't support
more. The k_frac=0.5 trick gives it ~4 tail samples (vs ~0 with default
k_frac=0.05) — this is the "best chunk=24 can do".

Run on Mac:
    conda run -n ecophys python experiments/033_loss_noise_fix/generate_configs.py
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent

BASE: dict = {
    "simulator": {
        "n_agents": 10000, "d_state": 32, "hidden": 48, "dt": 0.01,
        "gamma_init": 1.0, "temperature_init": 0.05, "init_state_scale": 0.1,
        "lam_dissipation": 0.01, "learn_gamma": True, "learn_temperature": True,
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
        "bptt_custom_function": True,
    },
    "training": {
        "n_iters": 200, "chunk_steps": 24, "warmup_steps": 16,
        "persistent_state": True, "lr": 1.0e-3, "lr_warmup_iters": 10,
        "grad_clip_max_norm": 100.0, "seed": 0, "checkpoint_every_s": 1800,
        "target_dataset": "spx", "target_period": "2015-2026_daily",
        "loss_weights": {
            "w_acf_sq": 1.0, "w_leverage": 0.2, "w_hill": 0.1,
            "max_lag": 8, "hill_k_frac": 0.05,           # overridden
            "w_autocorr_r": 0.5, "w_hill_max": 0.3, "hill_max_target": 10.0,
            "loss_family": "moments",
            "distance_mode": "l1",
            "tail_estimator": "soft_hill",
            "balance_mode": "fixed",
        },
    },
}


# Per-chunk loss-window scaling. Goal: max_lag close to sim_returns floor,
# k_frac large enough to get ≥4 hill tail samples.
CHUNK_KNOBS = {
    24:  {"max_lag": 6,  "hill_k_frac": 0.5},   # sim_returns 7,  hill k ≈ 4
    64:  {"max_lag": 20, "hill_k_frac": 0.2},   # sim_returns 47, hill k ≈ 9
    128: {"max_lag": 20, "hill_k_frac": 0.1},   # sim_returns 111, hill k ≈ 11
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
    print(f"Writing Phase C-fix configs to {HERE}/")
    for chunk, knobs in CHUNK_KNOBS.items():
        for seed in range(5):
            name = f"pcfix_chunk{chunk}_seed{seed}"
            comment = (
                f"Phase C-fix: chunk={chunk}, max_lag={knobs['max_lag']}, "
                f"hill_k_frac={knobs['hill_k_frac']}, seed={seed}. "
                f"Re-test loss-noise hypothesis with proper window scaling."
            )
            write(name, comment, {
                "training": {
                    "chunk_steps": chunk,
                    "seed": seed,
                    "loss_weights": {
                        "max_lag": knobs["max_lag"],
                        "hill_k_frac": knobs["hill_k_frac"],
                    },
                },
            })
            print(f"  {name}: chunk={chunk}, max_lag={knobs['max_lag']}, "
                  f"k_frac={knobs['hill_k_frac']}")
    n = len(list(HERE.glob("config_*.yaml")))
    print(f"\nWrote {n} configs.")


if __name__ == "__main__":
    main()
