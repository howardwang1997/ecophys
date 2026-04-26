"""Generate Paper A solidify configs (L/M/N/O/P/Q series, ~60 configs).

Series:
  L (15) — Multi-seed CI baselines (5 seeds × {v0.8, v1.0 Hawkes, C4})
  M (10) — 5+ market universality
  N (8)  — Crash OOS validation
  O (12) — Architectural follow-up (sign_mode, volume_mode, regime kyle)
  P (4)  — Direct baselines (GARCH+ABIDES if available; Shi NH deferred)
  Q (10) — Hyperparam refine around C4

ALSO present in this directory (NOT generated here, copied from
experiments/023_weekend/ during weekend rerun-failed integration):
  R (12) — Rerun of weekend's 12 failed configs.
           R0-R4 = F4-F8 originals (rerun fresh; launcher wipes ckpt).
           R5-R11 = OOM-shrunk *_safe versions of F11/F14/H0-H4.
           Launcher (h20_paper_a_solidify.sh) handles them automatically.

Run on Mac:
  conda run -n ecophys python experiments/025_paper_a_solidify/generate_configs.py
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent

# ─── Canonical bases ────────────────────────────────────────────────────

# C4 base (current 8/11 winner, multi-asset twopop+exp-loss)
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
    },
    "training": {
        "n_iters": 200, "chunk_steps": 24, "warmup_steps": 16,
        "persistent_state": True, "lr": 1.0e-3, "lr_warmup_iters": 10,
        "grad_clip_max_norm": 100.0, "seed": 0, "checkpoint_every_s": 1800,
        "joint_assets": [
            {"dataset": "spx",     "period": "2015-2026_daily", "weight": 1.0},
            {"dataset": "btcusdt", "period": "2024Q1_1m",        "weight": 1.0},
            {"dataset": "ethusdt", "period": "2024Q1_1m",        "weight": 1.0},
        ],
        "loss_weights": {
            "w_acf_sq": 1.0, "w_leverage": 0.2, "w_hill": 0.1,
            "max_lag": 8, "hill_k_frac": 0.05,
            "w_autocorr_r": 0.5, "w_hill_max": 0.3, "hill_max_target": 10.0,
        },
    },
}

# v1.0 Hawkes single-asset SPX (anchor for v0.6 + Hawkes; no twopop)
V10_HAWKES_BASE: dict = copy.deepcopy(C4_BASE)
V10_HAWKES_BASE["simulator"]["twopop_enabled"] = False
V10_HAWKES_BASE["training"].pop("joint_assets", None)
V10_HAWKES_BASE["training"]["target_dataset"] = "spx"
V10_HAWKES_BASE["training"]["target_period"] = "2015-2026_daily"
# Strip extended-loss (the original v1.0 didn't have it)
for k in ("w_autocorr_r", "w_hill_max"):
    V10_HAWKES_BASE["training"]["loss_weights"].pop(k, None)
V10_HAWKES_BASE["training"]["loss_weights"].pop("hill_max_target", None)

# v0.8 Pairwise — no Hawkes, no twopop, no exp-loss
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


def write(name: str, comment: str, base: dict, overrides: dict | None = None) -> None:
    cfg = deep_merge(base, overrides or {})
    p = HERE / f"config_{name}.yaml"
    text = "# " + comment.replace("\n", "\n# ") + "\n\n"
    text += yaml.safe_dump(cfg, sort_keys=False, default_flow_style=False)
    p.write_text(text)
    print(f"  {name}")


# ─── L series: multi-seed CI baselines (5 × 3 = 15) ────────────────────
def gen_L() -> None:
    print("L series — multi-seed CI baselines")
    for seed in range(5):
        write(f"l0{chr(ord('a')+seed)}_v08_seed{seed}",
              f"L0{chr(ord('a')+seed)}: v0.8 Pairwise (single-asset SPX), seed={seed}",
              V08_BASE, {"training": {"seed": seed}})
    for seed in range(5):
        write(f"l1{chr(ord('a')+seed)}_v10hawkes_seed{seed}",
              f"L1{chr(ord('a')+seed)}: v1.0 Hawkes (single-asset SPX), seed={seed}",
              V10_HAWKES_BASE, {"training": {"seed": seed}})
    for seed in range(5):
        write(f"l2{chr(ord('a')+seed)}_c4_seed{seed}",
              f"L2{chr(ord('a')+seed)}: C4 multi-asset (3 markets), seed={seed}",
              C4_BASE, {"training": {"seed": seed}})


# ─── M series: 5+ market universality (10) ─────────────────────────────
def _asset(ds, pd_, w=1.0):
    return {"dataset": ds, "period": pd_, "weight": w}


def gen_M() -> None:
    print("M series — universality (5+ markets)")
    SPX = _asset("spx", "2015-2026_daily")
    BTC = _asset("btcusdt", "2024Q1_1m")
    ETH = _asset("ethusdt", "2024Q1_1m")
    DAX = _asset("dax", "2015-2026_daily")
    EU = _asset("stoxx50", "2015-2026_daily")
    HSI = _asset("hsi", "2015-2026_daily")
    NIK = _asset("nikkei", "2015-2026_daily")
    GLD = _asset("gold", "2015-2026_daily")
    QQQ = _asset("qqq", "2015-2026_daily")
    IWM = _asset("iwm", "2015-2026_daily")

    write("m0_3eu_us_equity",
          "M0: SPX + DAX + EuroSTOXX (3 EU/US equity)",
          C4_BASE, {"training": {"joint_assets": [SPX, DAX, EU]}})
    write("m1_4global_equity",
          "M1: SPX + DAX + HSI + Nikkei (4 global equity)",
          C4_BASE, {"training": {"joint_assets": [SPX, DAX, HSI, NIK]}})
    write("m2_5equity",
          "M2: SPX + DAX + EuroSTOXX + HSI + Nikkei (5 equity universality)",
          C4_BASE, {"training": {"joint_assets": [SPX, DAX, EU, HSI, NIK]}})
    write("m3_7mixed",
          "M3: 5 equity + BTC + ETH (7 markets, full universality)",
          C4_BASE, {"training": {"joint_assets": [SPX, DAX, EU, HSI, NIK, BTC, ETH]}})
    SPX_x2 = _asset("spx", "2015-2026_daily", 2.0)
    write("m4_anchor_weighted",
          "M4: M3 with SPX weight=2 (anchor-weighted multi-asset)",
          C4_BASE, {"training": {"joint_assets": [SPX_x2, DAX, EU, HSI, NIK, BTC, ETH]}})
    write("m5_no_spx",
          "M5: 4 global equity + 2 crypto (NO SPX) — out-of-anchor universality",
          C4_BASE, {"training": {"joint_assets": [DAX, EU, HSI, NIK, BTC, ETH]}})
    write("m6_low_corr_3",
          "M6: SPX + GLD + 1.0 (low-correlation 2-asset; gold + equity)",
          C4_BASE, {"training": {"joint_assets": [SPX, GLD]}})
    write("m7_v10_7market",
          "M7: M3 7-market with v1.0 Hawkes (no v3 features) — control",
          V10_HAWKES_BASE,
          {"training": {"joint_assets": [SPX, DAX, EU, HSI, NIK, BTC, ETH]}})
    write("m8_signflip_5equity",
          "M8: M2 5-equity with sign-flipping Hawkes (cross with O series)",
          C4_BASE,
          {"simulator": {"price_formation_kwargs": {"hawkes_sign_mode": "flipping"}},
           "training": {"joint_assets": [SPX, DAX, EU, HSI, NIK]}})
    write("m9_5us_multi",
          "M9: SPX + QQQ + IWM + DAX + EuroSTOXX (5 large-mid cap mix)",
          C4_BASE,
          {"training": {"joint_assets": [SPX, QQQ, IWM, DAX, EU]}})


# ─── N series: crash OOS (8) ────────────────────────────────────────────
def gen_N() -> None:
    print("N series — crash OOS")
    SPX_15_19 = _asset("spx", "2015-2019_daily")
    SPX_15_21 = _asset("spx", "2015-2021_daily")
    SPX_15_22 = _asset("spx", "2015-2022_daily")
    DAX_15_19 = _asset("dax", "2015-2019_daily")
    EU_15_19 = _asset("stoxx50", "2015-2019_daily")
    HSI_15_19 = _asset("hsi", "2015-2019_daily")
    NIK_15_19 = _asset("nikkei", "2015-2019_daily")

    write("n0_c4_train1519",
          "N0: C4 single-asset SPX 2015-2019 → eval 2020 H1 (COVID)",
          C4_BASE,
          {"training": {"joint_assets": [SPX_15_19]}})
    write("n1_c4_train1521",
          "N1: C4 single-asset SPX 2015-2021 → eval 2022 (LUNA)",
          C4_BASE,
          {"training": {"joint_assets": [SPX_15_21]}})
    write("n2_c4_train1522",
          "N2: C4 single-asset SPX 2015-2022 → eval 2023 (SVB)",
          C4_BASE,
          {"training": {"joint_assets": [SPX_15_22]}})
    write("n3_c4_multi_train1519",
          "N3: C4 multi-asset 2015-2019 (5 equity) → eval 2020 H1",
          C4_BASE,
          {"training": {"joint_assets": [SPX_15_19, DAX_15_19, EU_15_19, HSI_15_19, NIK_15_19]}})
    write("n4_v10_train1519",
          "N4: v1.0 Hawkes SPX 2015-2019 (control vs N0)",
          V10_HAWKES_BASE,
          {"training": {"target_dataset": "spx", "target_period": "2015-2019_daily"}})
    write("n5_v08_train1519",
          "N5: v0.8 SPX 2015-2019 (control vs N0)",
          V08_BASE,
          {"training": {"target_dataset": "spx", "target_period": "2015-2019_daily"}})
    write("n6_c4_train1522_recent",
          "N6: C4 single-asset SPX 2015-2022 → eval 2024 (recent unseen)",
          C4_BASE,
          {"training": {"joint_assets": [SPX_15_22]}})
    write("n7_btc_train_h1",
          "N7: C4 BTC-only — train 2024 Q1 (early), eval Q3-Q4 (FTX/SBF)",
          C4_BASE,
          {"training": {"joint_assets": [_asset("btcusdt", "2024Q1_1m")]}})


# ─── O series: architectural follow-up (12) ────────────────────────────
def gen_O() -> None:
    print("O series — architectural follow-up (sign_mode, volume_mode, kyle)")
    # O0-O2 sign-flipping Hawkes
    write("o0_signflip",
          "O0: C4 + sign_mode=flipping (mean-reverting Hawkes; fix #1 autocorr_r)",
          C4_BASE,
          {"simulator": {"price_formation_kwargs": {"hawkes_sign_mode": "flipping"}}})
    write("o1_signflip_kappa05",
          "O1: O0 with κ=0.5 (stronger flip)",
          C4_BASE,
          {"simulator": {"price_formation_kwargs": {
              "hawkes_sign_mode": "flipping", "hawkes_kappa": 0.5}}})
    write("o2_signnone",
          "O2: C4 + sign_mode=none (magnitude-only Hawkes; pure clustering)",
          C4_BASE,
          {"simulator": {"price_formation_kwargs": {"hawkes_sign_mode": "none"}}})
    # O3-O5 price-driven volume
    write("o3_vol_price",
          "O3: C4 + volume_mode=price_driven (volume = N·|Δp|; fix #2)",
          C4_BASE,
          {"simulator": {"price_formation_kwargs": {"volume_mode": "price_driven"}}})
    write("o4_vol_price_signflip",
          "O4: O3 + sign_flip Hawkes (combined #1+#2 fix)",
          C4_BASE,
          {"simulator": {"price_formation_kwargs": {
              "volume_mode": "price_driven", "hawkes_sign_mode": "flipping"}}})
    write("o5_vol_price_signnone",
          "O5: O3 + sign_none Hawkes (combined #1+#2 alt)",
          C4_BASE,
          {"simulator": {"price_formation_kwargs": {
              "volume_mode": "price_driven", "hawkes_sign_mode": "none"}}})
    # O6-O8 narrower twopop spread
    write("o6_twopop_narrow",
          "O6: C4 with narrow twopop spread (γ=0.85,1.15,1.0,0.95) — vol_corr fix probe",
          C4_BASE,
          {"simulator": {
              "twopop_gamma_scale": [0.85, 1.15, 1.0, 0.95],
              "twopop_temp_scale":  [1.05, 0.85, 1.0, 1.10]}})
    write("o7_no_twopop_signflip",
          "O7: NO twopop + sign_flip — pure single-arch fix attempt",
          C4_BASE,
          {"simulator": {"twopop_enabled": False,
                         "price_formation_kwargs": {"hawkes_sign_mode": "flipping"}}})
    write("o8_twopop_K2",
          "O8: K=2 twopop (Lux-Marchesi style — fundamentalist + chartist)",
          C4_BASE,
          {"simulator": {
              "twopop_gamma_scale": [0.7, 1.3], "twopop_temp_scale": [0.5, 2.0]}})
    # O9-O11 — placeholders for future Kyle revisit (require code change)
    # For now we test variant configs with kyle_enabled=true on top of C4.
    write("o9_kyle_small",
          "O9: C4 + Kyle global enabled (small λ=0.001) — revisit after v2 negative result",
          C4_BASE,
          {"simulator": {
              "pairwise_kind": "ecomd_v2",
              "v2_kyle_enabled": True, "v2_kyle_lambda_init": 0.001,
              "v2_T_init_mode": "ones", "v2_gauge_enforce": False,
              "v2_phi_init_gain": 1.0}})
    write("o10_kyle_medium",
          "O10: O9 with λ=0.01",
          C4_BASE,
          {"simulator": {
              "pairwise_kind": "ecomd_v2",
              "v2_kyle_enabled": True, "v2_kyle_lambda_init": 0.01,
              "v2_T_init_mode": "ones", "v2_gauge_enforce": False,
              "v2_phi_init_gain": 1.0}})
    write("o11_kyle_large",
          "O11: O9 with λ=0.05 (the original v2.0 default — failed before, retry)",
          C4_BASE,
          {"simulator": {
              "pairwise_kind": "ecomd_v2",
              "v2_kyle_enabled": True, "v2_kyle_lambda_init": 0.05,
              "v2_T_init_mode": "ones", "v2_gauge_enforce": False,
              "v2_phi_init_gain": 1.0}})


# ─── P series: direct baselines (4) ────────────────────────────────────
def gen_P() -> None:
    print("P series — direct baselines")
    # P0: GARCH already in /experiments/000_reference_values/ — re-eval, no new config
    # P1: Shi 2024 NH — defer to follow-up; placeholder config
    # P2: Multi-asset Shi NH — defer
    # P3: ABIDES — defer (not pip-installable cleanly)
    # We DO create a placeholder config for P0 GARCH redo
    write("p0_garch_baseline_redo",
          "P0: GARCH(1,1)-t baseline re-eval with full 11 facts (existing 000_ref data)",
          V08_BASE, {"training": {"n_iters": 1}})  # dummy; this config marks evaluation only
    write("p1_shi_nh_placeholder",
          "P1: PLACEHOLDER for Shi 2024 NH (deferred — need ~500-line baseline impl)",
          V10_HAWKES_BASE)
    write("p2_shi_nh_multiasset_placeholder",
          "P2: PLACEHOLDER for Shi 2024 NH multi-asset (deferred)",
          V10_HAWKES_BASE)
    write("p3_abides_placeholder",
          "P3: PLACEHOLDER for ABIDES single-market (deferred — not pip-installable)",
          V08_BASE)


# ─── Q series: hyperparam refine (10) ──────────────────────────────────
def gen_Q() -> None:
    print("Q series — hyperparam refine around C4")
    # Q0-Q2 lr
    for i, lr in enumerate([3e-4, 1e-3, 3e-3]):
        write(f"q{i}_lr{lr}", f"Q{i}: C4 with lr={lr}",
              C4_BASE, {"training": {"lr": lr}})
    # Q3-Q4 chunk_steps
    for i, c in zip([3, 4], [16, 48]):
        write(f"q{i}_chunk{c}", f"Q{i}: C4 with chunk_steps={c}",
              C4_BASE, {"training": {"chunk_steps": c}})
    # Q5-Q6 K twopop
    write("q5_K2_twopop",
          "Q5: K=2 twopop (Lux-Marchesi: fundamentalist + chartist only)",
          C4_BASE,
          {"simulator": {
              "twopop_gamma_scale": [0.7, 1.3], "twopop_temp_scale": [0.5, 2.0]}})
    write("q6_K8_twopop",
          "Q6: K=8 twopop (granular)",
          C4_BASE,
          {"simulator": {
              "twopop_gamma_scale": [0.5, 0.7, 0.9, 1.0, 1.0, 1.1, 1.3, 1.5],
              "twopop_temp_scale":  [2.0, 1.5, 1.2, 1.0, 1.0, 0.8, 0.5, 0.3]}})
    # Q7-Q9 Kyle λ if O series is promising
    for i, lam in zip([7, 8, 9], [0.001, 0.005, 0.02]):
        write(f"q{i}_kyle_lam{lam}",
              f"Q{i}: C4 + Kyle λ={lam} (ecomd_v2 pairwise; rerun if O9-O11 promising)",
              C4_BASE,
              {"simulator": {
                  "pairwise_kind": "ecomd_v2",
                  "v2_kyle_enabled": True, "v2_kyle_lambda_init": lam,
                  "v2_T_init_mode": "ones", "v2_gauge_enforce": False,
                  "v2_phi_init_gain": 1.0}})


def main() -> None:
    print(f"writing configs to {HERE}/")
    print()
    gen_L(); gen_M(); gen_N(); gen_O(); gen_P(); gen_Q()
    n = len(list(HERE.glob("config_*.yaml")))
    print(f"\ntotal: {n} configs generated")


if __name__ == "__main__":
    main()
