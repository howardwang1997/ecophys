"""Phase Contamination — paired Sprint 2 vs default at chunk=24.

Original "contamination test" was an apples-to-oranges comparison
between Phase 1 (45 configs, default path, 3 seeds) and Phase C
(15 configs, Sprint 2 path, 5 seeds). NOT a clean comparison.

This corrected version: SAME single config (default loss, chunk=24,
single-asset SPX, C4 architecture) × 10 seeds × {default path,
Sprint 2 path}. Paired 10-seed comparison.

| group | chunk | bptt_custom_function | seeds | configs |
|---|---:|---|---:|---:|
| ct_default | 24 | False | 0..9 | 10 |
| ct_sprint2 | 24 | True  | 0..9 | 10 |
| **total**  |    |       |      | **20** |

Hypothesis (re-test): Sprint 2's clean per-step gradients (no cross-step
grad_fn pinning, no contamination) should yield lower 10-seed std. If
both paths give similar std, contamination doesn't matter for our task.

If Sprint 2 std ≪ default std → contamination IS a real source of seed
variance, switch to Sprint 2 going forward.
If Sprint 2 std ≈ default std → contamination is irrelevant, default
path is fine (and faster).

Per config: ~3-4 min training + 30s eval. Total 20 configs ÷ 8 parallel
≈ 2 rounds × 4min = ~10 min training + 5 min eval. ~15-20 min total.

Run on Mac:
    conda run -n ecophys python experiments/034_contamination_paired/generate_configs.py
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
        "bptt_custom_function": False,            # overridden per group
    },
    "training": {
        "n_iters": 200, "chunk_steps": 24, "warmup_steps": 16,
        "persistent_state": True, "lr": 1.0e-3, "lr_warmup_iters": 10,
        "grad_clip_max_norm": 100.0, "seed": 0, "checkpoint_every_s": 1800,
        "target_dataset": "spx", "target_period": "2015-2026_daily",
        "loss_weights": {
            "w_acf_sq": 1.0, "w_leverage": 0.2, "w_hill": 0.1,
            "max_lag": 8, "hill_k_frac": 0.05,
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
    print(f"Writing contamination-paired configs to {HERE}/")
    for path_tag, custom_function in [("default", False), ("sprint2", True)]:
        for seed in range(10):
            name = f"ct_{path_tag}_seed{seed}"
            comment = (
                f"Contamination paired test: {path_tag} path, chunk=24, "
                f"seed={seed}. bptt_custom_function={custom_function}."
            )
            write(name, comment, {
                "simulator": {"bptt_custom_function": custom_function},
                "training": {"seed": seed},
            })
            print(f"  {name}: bptt_custom_function={custom_function}")
    n = len(list(HERE.glob("config_*.yaml")))
    print(f"\nWrote {n} configs.")


if __name__ == "__main__":
    main()
