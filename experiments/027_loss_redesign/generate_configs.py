"""Generate loss-redesign + BPTT-checkpoint ablation configs (~110 configs).

Phases:
  Phase 1 (~45) — single-axis sweeps to find best loss design
                  · loss_family: l1-moments / MSE-moments / Huber-moments / W2-only / W2+MMD-hybrid
                  · tail_estimator: soft_hill / quantile_tail / kurtosis
                  · distance_mode: l1 / mse / huber
                  · chunk_steps × K: 24-K0 / 64-K8 / 128-K16
                  · balance_mode: fixed / inv_var
  Phase 2 (~45) — top 3 winners × 3 archs (C4 / v0.8 / v1.0) × 5 seeds
  Phase 4 (~10) — top-1 × N=20K / N=50K × 5 seeds (scale validation)
  Phase 5 (~9)  — top-1 × {3-eu, 5-equity, 7-mixed} × 3 seeds (universality)

All configs are single-asset SPX 2015-2026_daily by default (Phase 1 / 2 / 4).
Phase 5 explicitly varies the joint_assets list.

Total ≈ 109 configs.

Run on Mac:
  conda run -n ecophys python experiments/027_loss_redesign/generate_configs.py
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent

# ─── Canonical bases (mirror experiments/025/generate_configs.py) ──────


C4_BASE: dict = {
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
        # NEW: BPTT gradient checkpointing — 0 = off, K>0 = group every K steps.
        "bptt_checkpoint_every": 0,
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
            # Legacy moment-matching (default — matches l2a baseline)
            "w_acf_sq": 1.0,
            "w_leverage": 0.2,
            "w_hill": 0.1,
            "max_lag": 8,
            "hill_k_frac": 0.05,
            "w_autocorr_r": 0.5,
            "w_hill_max": 0.3,
            "hill_max_target": 10.0,
            # Loss-redesign defaults — all off / legacy.
            "loss_family": "moments",
            "distance_mode": "l1",
            "tail_estimator": "soft_hill",
            "balance_mode": "fixed",
            "balance_warmup": 20,
            "w_wasserstein": 0.0,
            "w_mmd": 0.0,
            "w_sinkhorn": 0.0,
        },
    },
}

V10_HAWKES_BASE: dict = copy.deepcopy(C4_BASE)
V10_HAWKES_BASE["simulator"]["twopop_enabled"] = False
# Strip extended-loss to reproduce v1.0 baseline behaviour
for k in ("w_autocorr_r", "w_hill_max", "hill_max_target"):
    V10_HAWKES_BASE["training"]["loss_weights"].pop(k, None)

V08_BASE: dict = copy.deepcopy(V10_HAWKES_BASE)
V08_BASE["simulator"]["price_formation_kwargs"]["hawkes_alpha"] = 0.0
V08_BASE["simulator"]["price_formation_kwargs"]["hawkes_kappa"] = 0.0


def deep_merge(base: dict, ov: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in ov.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def write(phase: str, name: str, comment: str, base: dict, overrides: dict | None = None) -> None:
    cfg = deep_merge(base, overrides or {})
    p = HERE / phase / f"config_{name}.yaml"
    text = "# " + comment.replace("\n", "\n# ") + "\n\n"
    text += yaml.safe_dump(cfg, sort_keys=False, default_flow_style=False)
    p.write_text(text)


# ═════════════════════════════════════════════════════════════════════════════
# PHASE 1 — single-axis sweeps to find best loss design (~45 configs)
# ═════════════════════════════════════════════════════════════════════════════


# Seeds for Phase 1 sweeps (3 seeds is enough to detect signal vs noise).
P1_SEEDS = [0, 1, 2]

# Common Phase-1 base: C4 single-asset SPX (so we don't conflate with multi-
# asset effects). We compare loss designs head-to-head on identical data.
P1_BASE: dict = copy.deepcopy(C4_BASE)
P1_BASE["training"].pop("joint_assets", None)
P1_BASE["training"]["target_dataset"] = "spx"
P1_BASE["training"]["target_period"] = "2015-2026_daily"
# When loss_family != "moments", we need target_returns wired through —
# the trainer will load this dataset on its own.


def gen_phase1_loss_family():
    """Axis 1 — loss family. 4 variants × 3 seeds = 12 configs."""
    print("Phase 1 / loss_family axis (12 configs)")
    variants = [
        ("l1_legacy", "L1 moments + soft_hill (legacy baseline)", {
            "loss_family": "moments", "distance_mode": "l1",
            "tail_estimator": "soft_hill",
        }),
        ("mse_moments", "MSE moments + soft_hill", {
            "loss_family": "moments", "distance_mode": "mse",
            "tail_estimator": "soft_hill",
        }),
        ("huber_moments", "Huber moments + soft_hill", {
            "loss_family": "moments", "distance_mode": "huber",
            "tail_estimator": "soft_hill",
        }),
        ("w2_only", "Wasserstein-only (no structural facts)", {
            "loss_family": "wasserstein",
            "w_acf_sq": 0.0, "w_leverage": 0.0, "w_hill": 0.0,
            "w_autocorr_r": 0.0, "w_hill_max": 0.0,
            "w_wasserstein": 1.0,
            "wasserstein_scales": [1, 5, 20],
        }),
    ]
    for name, label, lw_over in variants:
        for s in P1_SEEDS:
            write(
                "phase1",
                f"p1_lf_{name}_seed{s}",
                f"Phase1 loss_family axis: {label} (seed={s})",
                P1_BASE,
                {"training": {"seed": s, "loss_weights": lw_over}},
            )


def gen_phase1_tail_estimator():
    """Axis 2 — tail estimator (within hybrid family). 3 × 3 = 9 configs."""
    print("Phase 1 / tail_estimator axis (9 configs)")
    HYBRID_BASE_LW = {
        "loss_family": "hybrid", "distance_mode": "mse",
        "w_wasserstein": 1.0, "wasserstein_scales": [1, 5, 20],
        "w_acf_sq": 0.5, "w_leverage": 0.2, "w_hill": 0.1,
        "w_autocorr_r": 0.5,
    }
    variants = [
        ("softhill", "Hybrid + soft_hill", "soft_hill"),
        ("quantile", "Hybrid + quantile_tail (lower variance)", "quantile_tail"),
        ("kurtosis", "Hybrid + kurtosis_proxy (no tail dependence)", "kurtosis"),
    ]
    for name, label, est in variants:
        lw = {**HYBRID_BASE_LW, "tail_estimator": est}
        for s in P1_SEEDS:
            write(
                "phase1",
                f"p1_te_{name}_seed{s}",
                f"Phase1 tail_estimator axis: {label} (seed={s})",
                P1_BASE,
                {"training": {"seed": s, "loss_weights": lw}},
            )


def gen_phase1_distance_mode():
    """Axis 3 — distance mode (within hybrid + quantile_tail). 3 × 3 = 9 configs."""
    print("Phase 1 / distance_mode axis (9 configs)")
    HYBRID_QT_LW = {
        "loss_family": "hybrid",
        "tail_estimator": "quantile_tail",
        "w_wasserstein": 1.0, "wasserstein_scales": [1, 5, 20],
        "w_acf_sq": 0.5, "w_leverage": 0.2, "w_hill": 0.1,
        "w_autocorr_r": 0.5,
    }
    variants = [
        ("l1", "L1 distance"),
        ("mse", "MSE distance (smooth)"),
        ("huber", "Huber distance (robust)"),
    ]
    for name, label in variants:
        lw = {**HYBRID_QT_LW, "distance_mode": name}
        for s in P1_SEEDS:
            write(
                "phase1",
                f"p1_dm_{name}_seed{s}",
                f"Phase1 distance_mode axis: {label} (seed={s})",
                P1_BASE,
                {"training": {"seed": s, "loss_weights": lw}},
            )


def gen_phase1_chunk_bptt():
    """Axis 4 — chunk_steps × BPTT checkpointing. 3 × 3 = 9 configs.

    Tests whether longer rollouts (with BPTT-checkpoint memory unlock)
    improve loss landscape stability. This is the *critical* axis for our
    "the loss components are evaluated on too-few returns" hypothesis.
    """
    print("Phase 1 / chunk_steps × BPTT axis (9 configs)")
    HYBRID_QT_MSE = {
        "loss_family": "hybrid",
        "distance_mode": "mse",
        "tail_estimator": "quantile_tail",
        "w_wasserstein": 1.0, "wasserstein_scales": [1, 5, 20],
        "w_acf_sq": 0.5, "w_leverage": 0.2, "w_hill": 0.1,
        "w_autocorr_r": 0.5,
    }
    variants = [
        ("chunk24_K0", "chunk=24 (current), no BPTT checkpoint", 24, 0),
        ("chunk64_K8", "chunk=64, BPTT K=8 (memory ÷ 8, compute × 1.5)", 64, 8),
        ("chunk128_K16", "chunk=128, BPTT K=16", 128, 16),
    ]
    for name, label, chunk, K in variants:
        for s in P1_SEEDS:
            write(
                "phase1",
                f"p1_ch_{name}_seed{s}",
                f"Phase1 chunk×BPTT axis: {label} (seed={s})",
                P1_BASE,
                {
                    "simulator": {"bptt_checkpoint_every": K},
                    "training": {
                        "seed": s,
                        "chunk_steps": chunk,
                        # warmup_steps=16 for chunk=24 left only 7 returns;
                        # for longer chunks, 16 still leaves more (47 / 111).
                        "warmup_steps": 16,
                        "loss_weights": HYBRID_QT_MSE,
                    },
                },
            )


def gen_phase1_balance_mode():
    """Axis 5 — loss balancer (best loss design + chunk=64-K8). 2 × 3 = 6."""
    print("Phase 1 / balance_mode axis (6 configs)")
    BEST_LW_FIXED = {
        "loss_family": "hybrid",
        "distance_mode": "mse",
        "tail_estimator": "quantile_tail",
        "balance_mode": "fixed",
        "w_wasserstein": 1.0, "wasserstein_scales": [1, 5, 20],
        "w_acf_sq": 0.5, "w_leverage": 0.2, "w_hill": 0.1,
        "w_autocorr_r": 0.5,
    }
    BEST_LW_INVVAR = {**BEST_LW_FIXED, "balance_mode": "inv_var", "balance_warmup": 20}
    variants = [
        ("fixed", "Fixed weights (hand-tuned)", BEST_LW_FIXED),
        ("invvar", "Inverse-variance balancing across loss terms", BEST_LW_INVVAR),
    ]
    for name, label, lw in variants:
        for s in P1_SEEDS:
            write(
                "phase1",
                f"p1_bal_{name}_seed{s}",
                f"Phase1 balance_mode axis: {label} (seed={s})",
                P1_BASE,
                {
                    "simulator": {"bptt_checkpoint_every": 8},
                    "training": {
                        "seed": s,
                        "chunk_steps": 64,
                        "warmup_steps": 16,
                        "loss_weights": lw,
                    },
                },
            )


# ═════════════════════════════════════════════════════════════════════════════
# PHASE 2 — top 3 winners × 3 archs × 5 seeds = 45 configs
# ═════════════════════════════════════════════════════════════════════════════
#
# Top 3 are speculative until Phase 1 results land. We ship 3 plausible
# winners with descriptive names; the launcher's SKIP_DONE means we can
# disable obvious losers post-Phase-1.
# ═════════════════════════════════════════════════════════════════════════════


P2_SEEDS = [0, 1, 2, 3, 4]


def gen_phase2_winners():
    """Top 3 candidate loss designs × 3 architectures × 5 seeds."""
    print("Phase 2 / multi-seed CI on top winners (45 configs)")
    candidates = [
        ("w1", "hybrid + W2 + quantile_tail + MSE + chunk64-K8 + invvar", {
            "simulator": {"bptt_checkpoint_every": 8},
            "training": {
                "chunk_steps": 64, "warmup_steps": 16,
                "loss_weights": {
                    "loss_family": "hybrid", "distance_mode": "mse",
                    "tail_estimator": "quantile_tail",
                    "balance_mode": "inv_var", "balance_warmup": 20,
                    "w_wasserstein": 1.0, "wasserstein_scales": [1, 5, 20],
                    "w_acf_sq": 0.5, "w_leverage": 0.2, "w_hill": 0.1,
                    "w_autocorr_r": 0.5,
                },
            },
        }),
        ("w2", "hybrid + W2 + soft_hill + MSE + chunk64-K8 + fixed", {
            "simulator": {"bptt_checkpoint_every": 8},
            "training": {
                "chunk_steps": 64, "warmup_steps": 16,
                "loss_weights": {
                    "loss_family": "hybrid", "distance_mode": "mse",
                    "tail_estimator": "soft_hill",
                    "balance_mode": "fixed",
                    "w_wasserstein": 1.0, "wasserstein_scales": [1, 5, 20],
                    "w_acf_sq": 0.5, "w_leverage": 0.2, "w_hill": 0.1,
                    "w_autocorr_r": 0.5,
                },
            },
        }),
        ("w3", "moments + MSE + quantile_tail + chunk64-K8", {
            "simulator": {"bptt_checkpoint_every": 8},
            "training": {
                "chunk_steps": 64, "warmup_steps": 16,
                "loss_weights": {
                    "loss_family": "moments", "distance_mode": "mse",
                    "tail_estimator": "quantile_tail",
                    "balance_mode": "fixed",
                    "w_acf_sq": 1.0, "w_leverage": 0.2, "w_hill": 0.1,
                    "w_autocorr_r": 0.5,
                },
            },
        }),
    ]
    archs = [("c4", C4_BASE), ("v10", V10_HAWKES_BASE), ("v08", V08_BASE)]
    for cand_id, cand_label, cand_over in candidates:
        for arch_id, arch_base in archs:
            for s in P2_SEEDS:
                # Re-target single-asset SPX for fair comparison (drop multi-asset)
                arch_p2 = copy.deepcopy(arch_base)
                arch_p2["training"].pop("joint_assets", None)
                arch_p2["training"]["target_dataset"] = "spx"
                arch_p2["training"]["target_period"] = "2015-2026_daily"
                write(
                    "phase2",
                    f"p2_{cand_id}_{arch_id}_seed{s}",
                    f"Phase2 winner {cand_id} ({cand_label}) on {arch_id} seed={s}",
                    arch_p2,
                    cand_over | {"training": {**cand_over.get("training", {}), "seed": s}},
                )


# ═════════════════════════════════════════════════════════════════════════════
# PHASE 4 — N-scale validation (10 configs)
# ═════════════════════════════════════════════════════════════════════════════


def gen_phase4_scale():
    """Top-1 winner × N=20K, N=50K × 5 seeds. Tests whether scaling N
    further reduces fact-estimator variance under the new loss design."""
    print("Phase 4 / scale validation (10 configs)")
    WINNER_OVER = {
        "simulator": {
            "bptt_checkpoint_every": 8,
        },
        "training": {
            "chunk_steps": 64, "warmup_steps": 16,
            "loss_weights": {
                "loss_family": "hybrid", "distance_mode": "mse",
                "tail_estimator": "quantile_tail",
                "balance_mode": "inv_var", "balance_warmup": 20,
                "w_wasserstein": 1.0, "wasserstein_scales": [1, 5, 20],
                "w_acf_sq": 0.5, "w_leverage": 0.2, "w_hill": 0.1,
                "w_autocorr_r": 0.5,
            },
        },
    }
    base = copy.deepcopy(C4_BASE)
    base["training"].pop("joint_assets", None)
    base["training"]["target_dataset"] = "spx"
    base["training"]["target_period"] = "2015-2026_daily"

    for N in (20000, 50000):
        for s in [0, 1, 2, 3, 4]:
            over = copy.deepcopy(WINNER_OVER)
            over["simulator"]["n_agents"] = N
            # Larger N may need larger K to keep memory bounded; bump K=16
            # for N=50K to stay under HBM at chunk=64.
            if N >= 50_000:
                over["simulator"]["bptt_checkpoint_every"] = 16
            over["training"]["seed"] = s
            write(
                "phase4",
                f"p4_n{N // 1000}k_seed{s}",
                f"Phase4 scale validation: N={N}, winner config, seed={s}",
                base,
                over,
            )


# ═════════════════════════════════════════════════════════════════════════════
# PHASE 5 — multi-asset universality re-check (9 configs)
# ═════════════════════════════════════════════════════════════════════════════


def gen_phase5_universality():
    print("Phase 5 / universality (9 configs)")

    def _asset(ds, pd_, w=1.0):
        return {"dataset": ds, "period": pd_, "weight": w}

    SPX = _asset("spx", "2015-2026_daily")
    DAX = _asset("dax", "2015-2026_daily")
    EU = _asset("stoxx50", "2015-2026_daily")
    HSI = _asset("hsi", "2015-2026_daily")
    NIK = _asset("nikkei", "2015-2026_daily")
    BTC = _asset("btcusdt", "2024Q1_1m")
    ETH = _asset("ethusdt", "2024Q1_1m")

    asset_sets = [
        ("3eu", "SPX + DAX + EuroSTOXX (3 EU/US)", [SPX, DAX, EU]),
        ("5equity", "SPX + DAX + EuroSTOXX + HSI + Nikkei (5 equity)",
         [SPX, DAX, EU, HSI, NIK]),
        ("7mixed", "5 equity + BTC + ETH (7 mixed)",
         [SPX, DAX, EU, HSI, NIK, BTC, ETH]),
    ]
    WINNER_OVER = {
        "simulator": {"bptt_checkpoint_every": 8},
        "training": {
            "chunk_steps": 64, "warmup_steps": 16,
            "loss_weights": {
                "loss_family": "hybrid", "distance_mode": "mse",
                "tail_estimator": "quantile_tail",
                "balance_mode": "inv_var", "balance_warmup": 20,
                "w_wasserstein": 1.0, "wasserstein_scales": [1, 5, 20],
                "w_acf_sq": 0.5, "w_leverage": 0.2, "w_hill": 0.1,
                "w_autocorr_r": 0.5,
            },
        },
    }

    for set_id, label, assets in asset_sets:
        for s in [0, 1, 2]:
            over = copy.deepcopy(WINNER_OVER)
            over["training"]["joint_assets"] = assets
            over["training"]["seed"] = s
            # joint_assets implies removing single-asset target keys
            over["training"].pop("target_dataset", None)
            over["training"].pop("target_period", None)
            write(
                "phase5",
                f"p5_{set_id}_seed{s}",
                f"Phase5 universality: {label}, winner config, seed={s}",
                C4_BASE,
                over,
            )


def main() -> None:
    print(f"Writing configs to {HERE}/")
    print()
    gen_phase1_loss_family()
    gen_phase1_tail_estimator()
    gen_phase1_distance_mode()
    gen_phase1_chunk_bptt()
    gen_phase1_balance_mode()
    print()
    gen_phase2_winners()
    print()
    gen_phase4_scale()
    print()
    gen_phase5_universality()
    print()
    # Count generated
    for ph in ("phase1", "phase2", "phase4", "phase5"):
        n = len(list((HERE / ph).glob("config_*.yaml")))
        print(f"  {ph}: {n} configs")


if __name__ == "__main__":
    main()
