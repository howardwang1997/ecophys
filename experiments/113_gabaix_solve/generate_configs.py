"""Exp 113 — Gabaix mechanism-level solve (the best-result swing).

After the tournament closed the solve arc by attacking the loss/noise/paradigm layer
(never the tail-setting mechanism), this changes the MECHANISM that sets the tail
exponent. Gabaix-Gopikrishnan-Plerou-Stanley (Nature 2003): the inverse-cubic law
(α≈3) emerges from Zipf large-trader sizes × square-root price impact — two ingredients
the homogeneous-linear model lacks. Both enlarge the reachable set; ζ (mass exponent)
and δ (impact concavity) are LEARNABLE and calibrated by the existing soft_hill tail
term (loss-on-fixed-mechanism was falsified, exp 107 — loss must calibrate an enlarged
mechanism, not force an unreachable output).

Mechanistic prediction (verify in the N=10K overshoot regime, hill_base≈1.4):
  concave impact  → compresses synchronized bursts → hill UP (fixes overshoot)
  het masses ALONE→ whales fatten aggregate flow   → hill DOWN (wrong alone)
  BOTH, calibrated→ balance to α≈3 while masses' persistent whale-flow KEEPS acf2
                    (concave and masses have opposite effects on tails AND clustering
                    → plausibly DECOUPLES the Pareto pair the clamp could not).

Built on the 108 baseline_mmd cfg (N=10K fp32, hybrid+MMD long-rollout, custom-fn BPTT).
The loss already carries soft_hill (w_hill); ζ/δ join sim.parameters() so they are
calibrated automatically. NOTE: ζ/δ ranges (mass_zeta_init, impact_delta_init) should be
re-centered once exp 112 Part B returns the measured α(N)/α(κ) scaling — placeholders here.

Cells (6 × 30 seeds = 180 cfg, SPX, N=10K fp32, MMD long-rollout every=4):
  baseline             mechanisms OFF                         -> control (≈ overshoot)
  concave_learn        concave impact, δ learnable            -> isolate impact (hill↑)
  hetmass_learn        het masses, ζ learnable                -> isolate masses (hill↓)
  gabaix_learn         both, ζ+δ learnable (soft_hill-calib)  -> THE bet
  gabaix_theory_fixed  both FIXED at theory ζ=1.0, δ=0.5      -> does the GGPS value work
                                                                 out-of-the-box (no calib)?
  gabaix_learn_stronghill  both learnable + w_hill boosted 3× -> stronger tail calibration
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_PATH = REPO / "experiments" / "108_neural_sde_scout" / "config_baseline_mmd_seed0.yaml"
OUT = REPO / "experiments" / "113_gabaix_solve"
OUT.mkdir(parents=True, exist_ok=True)

N_SEEDS = 30
REG_EVERY = 4

# cell -> (price_formation_kwargs override, w_hill multiplier)
CELLS: dict[str, tuple[dict, float]] = {
    "baseline":               ({}, 1.0),
    "concave_learn":          ({"impact_concave_enabled": True, "impact_delta_init": 0.7,
                                "impact_delta_learnable": True}, 1.0),
    "hetmass_learn":          ({"het_mass_enabled": True, "mass_zeta_init": 2.0,
                                "mass_zeta_learnable": True}, 1.0),
    "gabaix_learn":           ({"het_mass_enabled": True, "mass_zeta_init": 1.8,
                                "mass_zeta_learnable": True, "impact_concave_enabled": True,
                                "impact_delta_init": 0.7, "impact_delta_learnable": True}, 1.0),
    "gabaix_theory_fixed":    ({"het_mass_enabled": True, "mass_zeta_init": 1.0,
                                "mass_zeta_learnable": False, "impact_concave_enabled": True,
                                "impact_delta_init": 0.5, "impact_delta_learnable": False}, 1.0),
    "gabaix_learn_stronghill":({"het_mass_enabled": True, "mass_zeta_init": 1.8,
                                "mass_zeta_learnable": True, "impact_concave_enabled": True,
                                "impact_delta_init": 0.7, "impact_delta_learnable": True}, 3.0),
}


def main() -> None:
    base = yaml.safe_load(BASE_PATH.read_text())
    assert base["training"].get("target_dataset", "spx") == "spx", "113 is SPX-only"
    base_w_hill = float(base["training"]["loss_weights"].get("w_hill", 0.1))

    n = 0
    for tag, (pf_over, whill_mul) in CELLS.items():
        for seed in range(N_SEEDS):
            cfg = copy.deepcopy(base)
            cfg["training"]["seed"] = seed
            cfg["training"]["rollout_reg_every"] = REG_EVERY
            cfg["training"]["loss_weights"]["w_hill"] = base_w_hill * whill_mul
            cfg["simulator"]["price_formation_kwargs"].update(pf_over)
            cfg["simulator"]["price_formation_kwargs"]["mass_seed"] = 1000 + seed
            (OUT / f"config_{tag}_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1

    print(f"wrote {n} configs ({len(CELLS)} cells × {N_SEEDS} seeds) to {OUT}")
    print(f"  N={base['simulator']['n_agents']} {base['training']['mixed_precision']} "
          f"reg_every={REG_EVERY} base_w_hill={base_w_hill}  cells:", ", ".join(CELLS))


if __name__ == "__main__":
    main()
