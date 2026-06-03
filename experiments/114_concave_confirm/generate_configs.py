"""Exp 114 — 5-asset confirmation of the concave √-impact solve (exp 113 → cross-asset).

exp 113 (SPX, n=30) LANDED: concave price impact β·sign(ED)·s·(|ED|/s)^δ thins the fat-tail
OVERSHOOT into band. The fixed-δ sweep gave a clean linear control law hill ≈ 5.33 − 4.57·δ
(r²=0.98); δ giving the empirical inverse-cubic (hill=3) is δ*≈0.509 — i.e. the Tóth-Lillo-
Bouchaud SQUARE-ROOT law (δ=0.5). concave_d050: hill 13→80% in-band, agg-gauss 27→70%, acf²
preserved, NO ≥20pp collateral, net +1.27 (Welch p=0.0014, d=0.90 — the only cell significant
after Bonferroni). The learnable-δ cell was NOISIER and not significant → the result to carry
forward is FIXED δ=0.5, the theory value, not a fitted one.

This is the pre-registered confirmation gate (no "solve" claim without it; no best-of-N): does the
SAME δ=0.5 reproduce α≈3 across markets? √-impact is empirically universal (TLB), so this is the
universality test the Nature-Physics framing needs, not a checkbox.

Design (~50h on 8×H20, single-card per cfg ≈ 62 min, PARALLEL=8):
  NEW assets {ndx, gold, eurusd, btcusdt} × {baseline, concave_d045, concave_d050} × 30 = 360
  spx × {concave_d045} × 30 = 30   (spx baseline + concave_d050 REUSED from exp 113 — identical
                                    base config + conditions; the 114 scorer reads them from 113/)
  ─────────────────────────────────────────────────────────────────────── total 390 cfg

  • baseline      = control per asset (each asset gets its own baseline for the Welch test)
  • concave_d050  = the champion (√-law) — the cell under confirmation
  • concave_d045  = HARDENS the hill(δ) crossing to 5 points per asset (was 4) AND lets us re-fit
                    the line PER ASSET → is δ*≈0.5 universal, or asset-specific?

btcusdt is 1-minute (different timescale + asset class) → the strongest leg of the universality
test. The other four are daily yfinance. impact_scale + all other sim fields inherit the 113 base.

Gate (per asset, in score_concave_confirm.py): concave_d050 vs that asset's baseline — hill∈[2,4]
AND acf²∈[.15,.55], Welch + Bonferroni. SOLVE-CONFIRMED iff it holds on ≥4/5 assets.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_PATH = REPO / "experiments" / "108_neural_sde_scout" / "config_baseline_mmd_seed0.yaml"
OUT = REPO / "experiments" / "114_concave_confirm"
OUT.mkdir(parents=True, exist_ok=True)

N_SEEDS = 30
REG_EVERY = 4

# asset -> (target_dataset, target_period)
ASSETS = {
    "spx":     ("spx", "2015-2026_daily"),
    "ndx":     ("ndx", "2015-2026_daily"),
    "gold":    ("gold", "2015-2026_daily"),
    "eurusd":  ("eurusd", "2015-2026_daily"),
    "btcusdt": ("btcusdt", "2024Q1_1m"),
}


def concave(delta: float) -> dict:
    return {"impact_concave_enabled": True, "impact_delta_init": delta,
            "impact_delta_learnable": False}


# cell -> price_formation override
CELLS = {
    "baseline":     {},
    "concave_d045": concave(0.45),
    "concave_d050": concave(0.50),
}

# spx baseline + concave_d050 already exist in exp 113 (same base config) → only add d045 for spx.
SKIP = {("spx", "baseline"), ("spx", "concave_d050")}


def main() -> None:
    base = yaml.safe_load(BASE_PATH.read_text())
    n = 0
    for asset, (dataset, period) in ASSETS.items():
        for cell, pf_over in CELLS.items():
            if (asset, cell) in SKIP:
                continue
            for seed in range(N_SEEDS):
                cfg = copy.deepcopy(base)
                cfg["training"]["seed"] = seed
                cfg["training"]["target_dataset"] = dataset
                cfg["training"]["target_period"] = period
                cfg["training"]["rollout_reg_every"] = REG_EVERY
                cfg["simulator"]["price_formation_kwargs"].update(pf_over)
                (OUT / f"config_{asset}_{cell}_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
                n += 1

    est_h = n / 8 * 62 / 60
    print(f"wrote {n} configs to {OUT}")
    print(f"  assets: {', '.join(ASSETS)}  cells: {', '.join(CELLS)}  (spx baseline+d050 reuse 113)")
    print(f"  N={base['simulator']['n_agents']} {base['training']['mixed_precision']} "
          f"reg_every={REG_EVERY}  → ~{est_h:.0f}h on 8×H20 (PARALLEL=8, ~62min/cfg)")


if __name__ == "__main__":
    main()
