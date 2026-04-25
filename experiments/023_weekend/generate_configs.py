"""Generate ~60 weekend H20 configs from a compact spec.

Series:
  E (5)  — C4 multi-seed (variance estimate on 7/10 win)
  F (15) — push C4 past 8/10 (zumbach loss, hyperparam tweaks, capacity)
  G (10) — multi-asset universality (4-5 assets, asymmetric weights, isolation)
  H (5)  — N scaling (20K, 50K, with C4 + F3 best)
  I (8)  — architectural composition (C4 + regime + mshawkes combos)
  J (6)  — negative result documentation (over-train, under-train, tight clip)
  K (5)  — mid-iter checkpoints (loss/facts misalignment evidence)

C4 = config_c4_multi_asset_twopop.yaml; current 7/10 winner.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
HERE.mkdir(parents=True, exist_ok=True)

# ─── C4 baseline (canonical 7/10 from overnight batch) ─────────────────────
C4_BASE = {
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
            "beta": 0.02,
            "kappa": 0.5,
            "sigma_price": 0.005,
            "ewma_alpha": 0.05,
            "initial_log_price": 0.0,
            "learnable_beta": False,
            "beta_hidden": 16,
            "hawkes_alpha": 0.1,
            "hawkes_kappa": 0.3,
        },
        "pairwise_kind": "stochastic_mlp",
        "sps_k_random": 50,
        "sps_resample_per_step": True,
        "twopop_enabled": True,
        "twopop_gamma_scale": [0.7, 1.5, 1.0, 0.5],
        "twopop_temp_scale":  [0.5, 2.0, 1.0, 0.3],
        "v2_type_seed": 42,
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
        "joint_assets": [
            {"dataset": "spx",     "period": "2015-2026_daily", "weight": 1.0},
            {"dataset": "btcusdt", "period": "2024Q1_1m",        "weight": 1.0},
            {"dataset": "ethusdt", "period": "2024Q1_1m",        "weight": 1.0},
        ],
        "loss_weights": {
            "w_acf_sq": 1.0,
            "w_leverage": 0.2,
            "w_hill": 0.1,
            "max_lag": 8,
            "hill_k_frac": 0.05,
            "w_autocorr_r": 0.5,
            "w_hill_max": 0.3,
            "hill_max_target": 10.0,
        },
    },
}


def deep_merge(base: dict, overrides: dict) -> dict:
    """Recursively merge overrides into a deep copy of base."""
    out = copy.deepcopy(base)
    for k, v in overrides.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def write(name: str, comment: str, overrides: dict) -> None:
    cfg = deep_merge(C4_BASE, overrides)
    p = HERE / f"config_{name}.yaml"
    text = "# " + comment.replace("\n", "\n# ") + "\n\n"
    text += yaml.safe_dump(cfg, sort_keys=False, default_flow_style=False)
    p.write_text(text)
    print(f"  {name}")


# ─── E series — multi-seed C4 (variance test) ──────────────────────────────
def gen_E():
    print("E series — multi-seed C4")
    for seed in range(5):
        write(f"e{seed}_c4_seed{seed}",
              f"E{seed}: C4 with seed={seed} — multi-seed variance estimate",
              {"training": {"seed": seed}})


# ─── F series — push past 8/10 ─────────────────────────────────────────────
def gen_F():
    print("F series — push C4 past 8/10")
    # F0: stronger autocorr penalty
    write("f0_high_autocorr_w",
          "F0: w_autocorr_r=1.5 (was 0.5) — try harder on fact #1",
          {"training": {"loss_weights": {"w_autocorr_r": 1.5}}})
    # F1: zumbach loss alone
    write("f1_zumbach_only",
          "F1: w_zumbach=1.0, target=0.05 — fix #11 reverse sign",
          {"training": {"loss_weights": {"w_zumbach": 1.0}}})
    # F2: zumbach stronger
    write("f2_zumbach_strong",
          "F2: w_zumbach=2.0 — even stronger Zumbach pull",
          {"training": {"loss_weights": {"w_zumbach": 2.0}}})
    # F3: ALL extras
    write("f3_all_extras",
          "F3: w_autocorr_r=1.5 + w_zumbach=1.0 + w_acf_shape=0.3 — kitchen sink loss",
          {"training": {"loss_weights": {
              "w_autocorr_r": 1.5,
              "w_zumbach": 1.0,
              "w_acf_shape": 0.3,
              "acf_shape_target_ratio": 2.0,
          }}})
    # F4: bigger MLP hidden
    write("f4_hidden64",
          "F4: hidden=64 (was 48) — ~75% more pair-kernel capacity",
          {"simulator": {"hidden": 64}})
    # F5: hidden=96
    write("f5_hidden96",
          "F5: hidden=96 (was 48) — 2× pair-kernel capacity",
          {"simulator": {"hidden": 96}})
    # F6: bigger d_state
    write("f6_dstate64",
          "F6: d_state=64 (was 32) — 2× agent feature dim",
          {"simulator": {"d_state": 64}})
    # F7: more SPS partners
    write("f7_sps100",
          "F7: sps_k_random=100 (was 50) — denser pair sampling",
          {"simulator": {"sps_k_random": 100}})
    # F8: 200 SPS partners
    write("f8_sps200",
          "F8: sps_k_random=200 — pushing toward dense",
          {"simulator": {"sps_k_random": 200}})
    # F9: slower lr
    write("f9_lr5e4",
          "F9: lr=5e-4 (was 1e-3) — slower learning, may avoid late-iter blow-up",
          {"training": {"lr": 5.0e-4}})
    # F10: longer warmup
    write("f10_warmup30",
          "F10: lr_warmup_iters=30 (was 10) — gentler ramp",
          {"training": {"lr_warmup_iters": 30}})
    # F11: chunk_steps=32 (push BPTT length, may OOM on H20 — fallback to 24)
    write("f11_chunk32",
          "F11: chunk_steps=32 (was 24) — longer BPTT; H20 may OOM, fallback chunk=24",
          {"training": {"chunk_steps": 32}})
    # F12: no persistent state
    write("f12_no_persist",
          "F12: persistent_state=False — re-init each iter, no carry-over BPTT",
          {"training": {"persistent_state": False}})
    # F13: tight clip
    write("f13_clip10",
          "F13: grad_clip=10 (was 100) — tighter clip, less late-iter divergence",
          {"training": {"grad_clip_max_norm": 10.0}})
    # F14: F3 + F4 (best loss + bigger hidden)
    write("f14_f3_plus_hidden64",
          "F14: F3 (kitchen-sink loss) + hidden=64 — combo if both individually help",
          {"simulator": {"hidden": 64},
           "training": {"loss_weights": {
               "w_autocorr_r": 1.5, "w_zumbach": 1.0,
               "w_acf_shape": 0.3, "acf_shape_target_ratio": 2.0,
           }}})


# ─── G series — multi-asset universality ───────────────────────────────────
def gen_G():
    print("G series — universality scaling")
    base_assets = [
        {"dataset": "spx", "period": "2015-2026_daily", "weight": 1.0},
        {"dataset": "btcusdt", "period": "2024Q1_1m", "weight": 1.0},
        {"dataset": "ethusdt", "period": "2024Q1_1m", "weight": 1.0},
    ]
    # G0: SPX-only (control — single-asset C4)
    write("g0_spx_only",
          "G0: single-asset SPX, C4 architecture — control for multi-asset benefit",
          {"training": {"joint_assets": [base_assets[0]]}})
    # G1: BTC + ETH only (crypto-only)
    write("g1_crypto_only",
          "G1: BTC+ETH only (no SPX) — pure crypto universality",
          {"training": {"joint_assets": base_assets[1:]}})
    # G2: SPX 2× + BTC + ETH
    write("g2_spx_weighted",
          "G2: SPX weight=2 (others 1) — equity-emphasized multi-asset",
          {"training": {"joint_assets": [
              {"dataset": "spx", "period": "2015-2026_daily", "weight": 2.0},
              base_assets[1], base_assets[2],
          ]}})
    # G3: BTC and ETH 2× (crypto-emphasized)
    write("g3_crypto_weighted",
          "G3: crypto-emphasized — SPX 1, BTC 2, ETH 2",
          {"training": {"joint_assets": [
              base_assets[0],
              {"dataset": "btcusdt", "period": "2024Q1_1m", "weight": 2.0},
              {"dataset": "ethusdt", "period": "2024Q1_1m", "weight": 2.0},
          ]}})
    # G4: SPX + BTC only (2-asset)
    write("g4_spx_btc",
          "G4: SPX+BTC only (2-asset)",
          {"training": {"joint_assets": [base_assets[0], base_assets[1]]}})
    # G5: SPX + ETH only
    write("g5_spx_eth",
          "G5: SPX+ETH only",
          {"training": {"joint_assets": [base_assets[0], base_assets[2]]}})
    # G6: BTC-only
    write("g6_btc_only",
          "G6: BTC-only — single crypto",
          {"training": {"joint_assets": [base_assets[1]]}})
    # G7: ETH-only
    write("g7_eth_only",
          "G7: ETH-only",
          {"training": {"joint_assets": [base_assets[2]]}})
    # G8: all 3 + zumbach loss (best loss + universality)
    write("g8_all3_zumbach",
          "G8: SPX+BTC+ETH + zumbach loss — universality + push past 7/10",
          {"training": {"loss_weights": {"w_zumbach": 1.0}}})
    # G9: 3-asset + extra realizations target (more eval steps)
    write("g9_all3_no_twopop",
          "G9: SPX+BTC+ETH WITHOUT twopop — isolate multi-asset benefit (vs C1 baseline)",
          {"simulator": {"twopop_enabled": False}})


# ─── H series — N scaling ─────────────────────────────────────────────────
def gen_H():
    print("H series — N scaling")
    # H0: N=20K (chunk_steps=20 to leave HBM headroom)
    write("h0_n20k",
          "H0: N=20K, chunk_steps=20 (HBM headroom)",
          {"simulator": {"n_agents": 20000},
           "training": {"chunk_steps": 20}})
    # H1: N=50K (chunk=14)
    write("h1_n50k",
          "H1: N=50K, chunk_steps=14 — pushing NVLink HBM",
          {"simulator": {"n_agents": 50000},
           "training": {"chunk_steps": 14}})
    # H2: N=20K + F3 expanded loss
    write("h2_n20k_f3loss",
          "H2: N=20K + F3 kitchen-sink loss",
          {"simulator": {"n_agents": 20000},
           "training": {
               "chunk_steps": 20,
               "loss_weights": {
                   "w_autocorr_r": 1.5, "w_zumbach": 1.0,
                   "w_acf_shape": 0.3, "acf_shape_target_ratio": 2.0,
               },
           }})
    # H3: N=50K + F3 expanded loss
    write("h3_n50k_f3loss",
          "H3: N=50K + F3 kitchen-sink loss",
          {"simulator": {"n_agents": 50000},
           "training": {
               "chunk_steps": 14,
               "loss_weights": {
                   "w_autocorr_r": 1.5, "w_zumbach": 1.0,
                   "w_acf_shape": 0.3, "acf_shape_target_ratio": 2.0,
               },
           }})
    # H4: N=100K — yolo, may OOM
    write("h4_n100k_yolo",
          "H4: N=100K, chunk_steps=8 — pushing the limit; may OOM",
          {"simulator": {"n_agents": 100000},
           "training": {"chunk_steps": 8, "lr_warmup_iters": 20}})


# ─── I series — architectural composition ──────────────────────────────────
def gen_I():
    print("I series — architectural composition with C4 base")
    # I0: C4 + conservative regime (B3-style)
    write("i0_c4_plus_regime",
          "I0: C4 + conservative regime (init_gain=0.02, update_every=16)",
          {"simulator": {
              "regime_enabled": True, "regime_d": 16,
              "regime_update_every": 16, "regime_init_gain": 0.02,
              "regime_modulate_gamma": True, "regime_modulate_temp": True,
              "regime_modulate_kappa": True,
          }})
    # I1: C4 + conservative mshawkes (B2-style)
    write("i1_c4_plus_mshawkes",
          "I1: C4 + conservative multi-scale Hawkes (κ_long=0.05, α_long=0.005)",
          {"simulator": {"price_formation_kwargs": {
              "hawkes_alpha_long": 0.005, "hawkes_kappa_long": 0.05,
          }}})
    # I2: C4 + regime + mshawkes (all conservative)
    write("i2_c4_full_conservative",
          "I2: C4 + conservative regime + conservative mshawkes (kitchen-sink with brakes)",
          {"simulator": {
              "regime_enabled": True, "regime_d": 16,
              "regime_update_every": 16, "regime_init_gain": 0.02,
              "regime_modulate_gamma": True, "regime_modulate_temp": True,
              "regime_modulate_kappa": True,
              "price_formation_kwargs": {
                  "hawkes_alpha_long": 0.005, "hawkes_kappa_long": 0.05,
              },
          }})
    # I3: I2 + zumbach loss
    write("i3_full_conservative_zumbach",
          "I3: I2 + w_zumbach=1.0 — full features + extra loss term",
          {"simulator": {
              "regime_enabled": True, "regime_d": 16,
              "regime_update_every": 16, "regime_init_gain": 0.02,
              "regime_modulate_gamma": True, "regime_modulate_temp": True,
              "regime_modulate_kappa": True,
              "price_formation_kwargs": {
                  "hawkes_alpha_long": 0.005, "hawkes_kappa_long": 0.05,
              },
          },
           "training": {"loss_weights": {"w_zumbach": 1.0}}})
    # I4: NO twopop, just multi-asset + exp-loss (isolate twopop)
    write("i4_no_twopop",
          "I4: multi-asset + exp-loss WITHOUT twopop — isolate twopop's contribution",
          {"simulator": {"twopop_enabled": False}})
    # I5: regime + exp-loss only
    write("i5_regime_only",
          "I5: regime (no twopop, no mshawkes) + exp-loss",
          {"simulator": {
              "twopop_enabled": False,
              "regime_enabled": True, "regime_d": 16,
              "regime_update_every": 16, "regime_init_gain": 0.02,
              "regime_modulate_gamma": True, "regime_modulate_temp": True,
              "regime_modulate_kappa": True,
          }})
    # I6: mshawkes + exp-loss only
    write("i6_mshawkes_only",
          "I6: conservative mshawkes (no twopop, no regime) + exp-loss",
          {"simulator": {
              "twopop_enabled": False,
              "price_formation_kwargs": {
                  "hawkes_alpha_long": 0.005, "hawkes_kappa_long": 0.05,
              },
          }})
    # I7: Tighter twopop spread (between B4 ±10% and A4 wild)
    write("i7_twopop_medium",
          "I7: twopop with medium spread γ=(0.8,1.2,1.0,0.85) T=(1.2,0.8,1.0,1.3)",
          {"simulator": {
              "twopop_gamma_scale": [0.8, 1.2, 1.0, 0.85],
              "twopop_temp_scale":  [1.2, 0.8, 1.0, 1.3],
          }})


# ─── J series — over/under-train + clip studies ────────────────────────────
def gen_J():
    print("J series — over/under-train and ablation studies")
    # J0: C4 with 400 iters (over-train)
    write("j0_c4_400iter",
          "J0: C4 + 400 iter — does exp-loss prevent over-fit?",
          {"training": {"n_iters": 400}})
    # J1: 600 iter
    write("j1_c4_600iter",
          "J1: C4 + 600 iter — extreme over-train",
          {"training": {"n_iters": 600}})
    # J2: 100 iter (under-train)
    write("j2_c4_100iter",
          "J2: C4 + 100 iter — under-train, see if 100 enough",
          {"training": {"n_iters": 100}})
    # J3: very tight clip
    write("j3_c4_clip1",
          "J3: C4 + grad_clip=1.0 — paper notes 'clip caps lr' but maybe v3 wants tight",
          {"training": {"grad_clip_max_norm": 1.0}})
    # J4: AdamW + weight decay
    write("j4_c4_no_persist",
          "J4: C4 + persistent_state=False — completely fresh BPTT each iter",
          {"training": {"persistent_state": False, "n_iters": 300}})
    # J5: A4 with 400 iters (over-train WITHOUT exp-loss — does loss save?)
    write("j5_a4_400iter",
          "J5: A4 architecture (no exp-loss) + 400 iter — control for J0",
          {"training": {
              "n_iters": 400,
              "loss_weights": {
                  "w_autocorr_r": 0.0, "w_hill_max": 0.0,
              },
          }})


# ─── K series — mid-iter scoring ────────────────────────────────────────
def gen_K():
    print("K series — mid-iter checkpoint analysis")
    # Train C4 for various lengths so we can score each
    for n in [50, 100, 150, 200, 300]:
        write(f"k_iter{n}",
              f"K_iter{n}: C4 stopped at iter={n} — track when over-fit kicks in",
              {"training": {"n_iters": n}})


def main() -> None:
    print(f"writing configs to {HERE}/")
    print()
    gen_E()
    gen_F()
    gen_G()
    gen_H()
    gen_I()
    gen_J()
    gen_K()
    n = len(list(HERE.glob("config_*.yaml")))
    print(f"\ntotal: {n} configs generated under {HERE}/")


if __name__ == "__main__":
    main()
