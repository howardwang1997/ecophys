"""Phase H — Architecture / training-regime sweep.

The "loss redesign null" finding (commit a016713) showed seed dominates
under default architecture/regime: seed1 always 5/11, seed0/2 stuck at
2-3/11, no loss variant moved the mean. This phase tests whether
architecture/regime perturbations shift the basin distribution.

~36 configs across four groups:

  ph_lr (8)        — lr ∈ {3e-4, 1e-3, 3e-3, 1e-2} × seeds {0, 1}
                      → does seed1's 5/11 generalise across lrs? Does
                        a different lr unlock seed0/2's basin?

  ph_iters (6)     — n_iters ∈ {200, 400, 800} × seeds {0, 1}
                      → convergence vs Goodhart trade-off; the original
                        D series (n_iters=400) was uniformly worse,
                        suggesting Goodhart, but confirm with controlled
                        comparison.

  ph_init (12)     — init_state_scale ∈ {0.05, 0.1, 0.5} × hidden ∈
                      {48, 96} × seeds {0, 1}
                      → initialisation basin sensitivity.

  ph_n_seeds (10)  — best (lr, hidden) × 10 seeds {0..9}
                      → distribution of seed outcomes; is seed1's 5/11
                        a one-off, or robust under more seeds?

Default chunk = 128 (assumes Phase C confirmed Sprint 2 + chunk=128
works). If Phase C says chunk=24 is fine, change CHUNK_DEFAULT below.

Run on Mac:
    conda run -n ecophys python experiments/032_arch_regime_sweep/generate_configs.py
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent

# Phase H assumes Phase C declared chunk=128 the winner (= default loss
# operating with sim_returns length 111). If Phase C reveals chunk
# doesn't matter, edit CHUNK_DEFAULT to 24 and regenerate.
CHUNK_DEFAULT = 128

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
        "bptt_custom_function": True,
    },
    "training": {
        "n_iters": 200,
        "chunk_steps": CHUNK_DEFAULT,
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


# ── Group 1: lr sweep ────────────────────────────────────────────────
def gen_ph_lr() -> None:
    print("ph_lr — learning rate × seed (8 configs)")
    for lr in (3e-4, 1e-3, 3e-3, 1e-2):
        lr_tag = f"{lr:.0e}".replace("e-0", "e-").replace("e+0", "e+")
        for seed in (0, 1):
            name = f"ph_lr_{lr_tag}_seed{seed}"
            write(name,
                  f"Phase H lr sweep: lr={lr}, seed={seed}",
                  {"training": {"lr": lr, "seed": seed}})


# ── Group 2: n_iters sweep ───────────────────────────────────────────
def gen_ph_iters() -> None:
    print("ph_iters — training duration × seed (6 configs)")
    for n_iters in (200, 400, 800):
        for seed in (0, 1):
            name = f"ph_iters_{n_iters}_seed{seed}"
            write(name,
                  f"Phase H iters sweep: n_iters={n_iters}, seed={seed}",
                  {"training": {"n_iters": n_iters, "seed": seed}})


# ── Group 3: init_state_scale × hidden ────────────────────────────────
def gen_ph_init() -> None:
    print("ph_init — init_state_scale × hidden × seed (12 configs)")
    for init_scale in (0.05, 0.1, 0.5):
        scale_tag = str(init_scale).replace(".", "")
        for hidden in (48, 96):
            for seed in (0, 1):
                name = f"ph_init_s{scale_tag}_h{hidden}_seed{seed}"
                write(name,
                      f"Phase H init sweep: init_state_scale={init_scale}, "
                      f"hidden={hidden}, seed={seed}",
                      {
                          "simulator": {
                              "init_state_scale": init_scale,
                              "hidden": hidden,
                          },
                          "training": {"seed": seed},
                      })


# ── Group 4: 10-seed distribution at default config ───────────────────
def gen_ph_n_seeds() -> None:
    """Use default (lr, hidden) — same as the "best" until lr-sweep
    overrides — across 10 seeds. Characterises the distribution of
    outcomes under a fixed architecture/regime; tests whether seed1's
    5/11 is a robust attractor or a one-off lottery winner."""
    print("ph_n_seeds — 10 seeds at default config (10 configs)")
    for seed in range(10):
        name = f"ph_n_seeds_default_seed{seed}"
        write(name,
              f"Phase H 10-seed distribution: default config (lr=1e-3, "
              f"hidden=48), seed={seed}",
              {"training": {"seed": seed}})


def main() -> None:
    print(f"Generating Phase H configs to {HERE}/  (CHUNK_DEFAULT={CHUNK_DEFAULT})")
    gen_ph_lr()
    gen_ph_iters()
    gen_ph_init()
    gen_ph_n_seeds()
    n = len(list(HERE.glob("config_*.yaml")))
    print(f"\nWrote {n} configs (target ~36).")


if __name__ == "__main__":
    main()
