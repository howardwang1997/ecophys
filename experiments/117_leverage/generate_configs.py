"""Exp 117 — leverage-effect recovery as the SECOND mechanism (restores Paper A's "≥2 mechanisms
= method" leg after SV-composition broke in exp 115/119).

The concave √-impact solve (113/114, δ=0.5) fixes the tail overshoot but does nothing for the
leverage effect (Σ Corr(r_t, r²_{t+τ}) < 0, target band [-6,-0.5]) — one of the 3 hardest facts
(~27% baseline pass). The integrator already ships two leverage mechanisms (no new physics):
  • asym_drag_alpha:   γ_eff = γ·(1+α·sign(Δp_recent)) — down moves lower γ → larger subsequent
                       moves → vol spikes after drops (leverage). (ecomd/physics/integrator.py:344)
  • zumbach_feedback_mode='downside': only down moves boost future vol (Zumbach × leverage).

This experiment composes each leverage mechanism ON TOP OF the concave_d050 solve and asks: does
leverage_effect enter [-6,-0.5] WITHOUT undoing the concave tail fix (hill must stay [2,4], acf²
[0.15,0.55], agg preserved)? That collateral-free composition is the method claim. concave_only is
the control. The base already carries w_leverage=0.2 in the loss, so training targets leverage; the
mechanism just gives the model the knob to satisfy it.

Recipe identical to 113/114/115 (108 baseline_mmd base + rollout_reg_every=4); scored vs the
concave_only control with scripts/score_leverage.py. Start on spx (dev/confirm); cross-asset next
window if it composes.

Usage:
  python experiments/117_leverage/generate_configs.py --assets spx --n-seeds 20
"""
from __future__ import annotations

import argparse
import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_PATH = REPO / "experiments" / "108_neural_sde_scout" / "config_baseline_mmd_seed0.yaml"
OUT = REPO / "experiments" / "117_leverage"

REG_EVERY = 4
CONCAVE = {"impact_concave_enabled": True, "impact_delta_init": 0.50,
           "impact_delta_learnable": False}

# cell -> integrator/leverage overrides ADDED to the concave solve (all keys are EcoMDConfig fields)
LEVER = {
    "concave_only": {},                                            # control
    "asym03":       {"asym_drag_alpha": 0.3},
    "asym05":       {"asym_drag_alpha": 0.5},
    "asym07":       {"asym_drag_alpha": 0.7},
    "zumbdown":     {"zumbach_feedback_lambda": 0.92, "zumbach_feedback_strength": 0.6,
                     "zumbach_feedback_mode": "downside"},
    "asym_zumb":    {"asym_drag_alpha": 0.4, "zumbach_feedback_lambda": 0.92,
                     "zumbach_feedback_strength": 0.4, "zumbach_feedback_mode": "downside"},
}

ASSETS = {
    "spx":     ("spx", "2015-2026_daily"),
    "ndx":     ("ndx", "2015-2026_daily"),
    "gold":    ("gold", "2015-2026_daily"),
    "eurusd":  ("eurusd", "2015-2026_daily"),
    "btcusdt": ("btcusdt", "2024Q1_1m"),
}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--assets", nargs="+", default=["spx"], choices=list(ASSETS))
    ap.add_argument("--cells", nargs="+", default=list(LEVER), choices=list(LEVER))
    ap.add_argument("--n-seeds", type=int, default=20)
    ap.add_argument("--seed-start", type=int, default=0)
    args = ap.parse_args()

    base = yaml.safe_load(BASE_PATH.read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0
    for asset in args.assets:
        dataset, period = ASSETS[asset]
        for cell in args.cells:
            for seed in range(args.seed_start, args.seed_start + args.n_seeds):
                cfg = copy.deepcopy(base)
                cfg["training"]["seed"] = seed
                cfg["training"]["target_dataset"] = dataset
                cfg["training"]["target_period"] = period
                cfg["training"]["rollout_reg_every"] = REG_EVERY
                cfg["simulator"]["price_formation_kwargs"].update(CONCAVE)
                cfg["simulator"].update(LEVER[cell])  # integrator knobs live at simulator top level
                (OUT / f"config_{asset}_{cell}_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
                n += 1

    est_h = n * 62 / 60
    print(f"wrote {n} configs to {OUT}  assets={args.assets} cells={args.cells} "
          f"n_seeds={args.n_seeds}")
    print(f"  recipe: concave_d050 + leverage knob, reg_every={REG_EVERY} (identical base to 113/114)")
    print(f"  ≈ {est_h:.0f} card-hours (~{est_h/8:.1f}h on 8 cards)")


if __name__ == "__main__":
    main()
