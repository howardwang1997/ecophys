"""Phase C — chunk effect on quality under Sprint 2 (custom Function).

15 configs: 3 chunks × 5 seeds, single-asset SPX 2015-2026 daily, default
loss (legacy moments + soft_hill + L1 — same as l2a baseline). Sprint 2's
custom Function provides bounded memory regardless of chunk_steps, so we
finally get to test:

    chunk=24  → sim_returns length 7   (today's broken-loss regime)
    chunk=64  → sim_returns length 47  (intermediate)
    chunk=128 → sim_returns length 111 (~16x the data for fact estimators)

Hypothesis: longer chunk → less estimator noise → tighter 5-seed CI and
possibly higher mean. If both are null, loss-noise is NOT the bottleneck
(answer to the loss-redesign-was-null finding).

Run on Mac:
    conda run -n ecophys python experiments/031_chunk_effect/generate_configs.py
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent

# C4-style baseline matching the l2a 8/11 winner's architecture, but
# single-asset SPX (no multi-asset noise) and Sprint 2 path.
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
        # Sprint 2 path: per-step custom autograd.Function bounds memory
        # at one step's V-graph regardless of chunk_steps.
        "bptt_checkpoint_every": 0,
        "bptt_custom_function": True,
    },
    "training": {
        "n_iters": 200,
        "chunk_steps": 24,         # overridden per group
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
            # Legacy default loss — soft_hill + L1, same as l2a baseline.
            # No w2 / mmd / quantile_tail / kurtosis here on purpose:
            # we're isolating the chunk-effect, not retesting loss design.
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
    print(f"Generating Phase C configs to {HERE}/")
    for chunk in (24, 64, 128):
        for seed in range(5):
            name = f"pc_chunk{chunk}_seed{seed}"
            comment = (
                f"Phase C: chunk={chunk}, seed={seed}, Sprint 2 (custom Function). "
                f"sim_returns length = chunk - warmup_steps - 1 = {chunk - 17}."
            )
            write(name, comment, {
                "training": {
                    "chunk_steps": chunk,
                    "seed": seed,
                },
            })
            print(f"  {name}")
    n = len(list(HERE.glob("config_*.yaml")))
    print(f"\nWrote {n} configs.")


if __name__ == "__main__":
    main()
