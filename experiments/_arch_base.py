"""Shared base config + helpers for the feature/arch-extensions overnight
batch (experiments/037..044).

All 8 dirs branch off the same base = ``abl_no_chunk128`` from 036:
chunk=24, hidden=96, init_state_scale=0.1, Sprint 2 custom autograd,
twopop+Hawkes, default loss family. Confirmed mean=3.20 (10 seeds) on
2026-04-28 — the best reproducible "best basin" baseline we have.

Each tier dir flips ONE set of flags and runs ``n_seeds`` seeds.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml


# ── BASE = abl_no_chunk128 (036), mean 3.20 ─────────────────────────────
BASE: dict[str, Any] = {
    "simulator": {
        "n_agents": 10000,
        "d_state": 32,
        "hidden": 96,
        "dt": 0.01,
        "gamma_init": 1.0,
        "temperature_init": 0.05,
        "init_state_scale": 0.1,
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
        "bptt_custom_function": True,
    },
    "training": {
        "n_iters": 200,
        "chunk_steps": 24,
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
            "max_lag": 8,
            "hill_k_frac": 0.05,
            "w_autocorr_r": 0.5, "w_hill_max": 0.3, "hill_max_target": 10.0,
            "loss_family": "moments",
            "distance_mode": "l1",
            "tail_estimator": "soft_hill",
            "balance_mode": "fixed",
        },
    },
}


# ── Tier overrides (one cell per tier) ──────────────────────────────────
TIER_OVERRIDES: dict[str, dict] = {
    "tier_1_1_memory": {
        "simulator": {
            "agent_memory_enabled": True,
            "agent_memory_d": 16,
            "agent_memory_update_every": 1,
        },
    },
    "tier_1_2_kernels": {
        "simulator": {
            "pair_heterogeneous_heads": True,
        },
    },
    "tier_1_3_features_all": {
        "simulator": {
            "pair_features_extra": "all",
        },
    },
    "tier_2_1_jumps": {
        "simulator": {
            "jump_lambda": 0.5,
            "jump_scale": 0.01,
        },
    },
    "tier_2_2_multitimescale": {
        "simulator": {
            "multi_timescale_enabled": True,
            "timescale_fast_frac": 0.8,
            "timescale_slow_freq": 4,
        },
    },
    "tier_3_1_isab": {
        "simulator": {
            "pairwise_kind": "isab",
            "isab_m_inducing": 64,
            "isab_n_heads": 4,
            # ISAB has its own internal hidden — keep cfg.hidden for the
            # external potential. Pair_heterogeneous_heads/pair_features_extra
            # are ignored under pairwise_kind=isab (they only apply to
            # stochastic_mlp).
        },
    },
    "tier_4_1_megnet": {
        "simulator": {
            "global_state_enabled": True,
            "global_state_d": 16,
            "global_state_update_every": 1,
            "global_state_into_pair": True,
        },
    },
    "tier_4_1_megnet_external_only": {
        # Ablation: u feeds external context but NOT pair kernel. Lets us
        # measure the marginal value of pair-side global awareness vs.
        # external-side global awareness.
        "simulator": {
            "global_state_enabled": True,
            "global_state_d": 16,
            "global_state_update_every": 1,
            "global_state_into_pair": False,
        },
    },
}


def deep_merge(base: dict, ov: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in ov.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def stack_overrides(*tier_keys: str) -> dict:
    """Compose multiple tier overrides into one. Right-most wins on conflicts."""
    out: dict = {}
    for k in tier_keys:
        out = deep_merge(out, TIER_OVERRIDES[k])
    return out


def write_config(out_dir: Path, name: str, comment: str, overrides: dict) -> None:
    cfg = deep_merge(BASE, overrides)
    p = out_dir / f"config_{name}.yaml"
    text = "# " + comment + "\n\n"
    text += yaml.safe_dump(cfg, sort_keys=False, default_flow_style=False)
    p.write_text(text)


def emit_seeded(
    out_dir: Path,
    cell_name: str,
    cell_overrides: dict,
    n_seeds: int,
    comment_prefix: str,
) -> int:
    """Write n_seeds copies of cell_overrides under names f'{cell_name}_seed{s}'."""
    n = 0
    for seed in range(n_seeds):
        seeded = deep_merge(cell_overrides, {"training": {"seed": seed}})
        name = f"{cell_name}_seed{seed}"
        write_config(out_dir, name, f"{comment_prefix}, seed={seed}", seeded)
        n += 1
    return n
