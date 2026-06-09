"""Exp 121 — sanity-check S6: across-regime / time-universality of the concave √-impact solve.

plan_v3 §6.2 S6 ("across-regime split: train/test period ν consistent"). For Paper A: is the concave
solve (hill into [2,4] + acf² preserved, δ*≈0.5) a property of the LEARNED MECHANISM, or an artifact
of fitting the full 2015–2026 window? Train baseline + concave_d050 on two disjoint regimes and check
the gate holds — and is consistent — in BOTH. A reviewer-2's first overfit question, answered.

Two regimes via the loader's period sub-range support (`_parse_period`: 'YYYY-YYYY_daily'):
  2015-2020_daily (incl. 2018 vol, 2020 COVID)  vs  2021-2026_daily (incl. 2022 drawdown).
btc is EXCLUDED — 2024Q1 (3 months) is too short to split into regimes.

Recipe identical to 113/114 (108 baseline_mmd base + rollout_reg_every=4, fixed δ=0.5). Configs go in
per-regime SUBDIRS (experiments/121_heldout_regime/{r1,r2}/) so score_concave_confirm.py scores each
regime independently (point it at .../r1 then .../r2). The solve is time-universal iff concave_d050
passes hill∈[2,4] AND acf²∈[.15,.55] vs its baseline in BOTH, with consistent hill (|Δhill| small).

Usage:
  python experiments/121_heldout_regime/generate_configs.py --assets spx ndx gold eurusd --n-seeds 15
  for r in r1 r2; do bash scripts/h20_run_phase.sh experiments/121_heldout_regime/$r; done
"""
from __future__ import annotations

import argparse
import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_PATH = REPO / "experiments" / "108_neural_sde_scout" / "config_baseline_mmd_seed0.yaml"
OUT = REPO / "experiments" / "121_heldout_regime"

REG_EVERY = 4
CONCAVE = {"impact_concave_enabled": True, "impact_delta_init": 0.50,
           "impact_delta_learnable": False}
CELLS = {"baseline": {}, "concave_d050": CONCAVE}

# regime label -> period string (loader parses 'YYYY-YYYY_daily' to inclusive year bounds)
REGIMES = {"r1": "2015-2020_daily", "r2": "2021-2026_daily"}

# daily-equity assets only (btc 2024Q1 too short to split into regimes)
ASSETS = {"spx": "spx", "ndx": "ndx", "gold": "gold", "eurusd": "eurusd"}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--assets", nargs="+", default=list(ASSETS), choices=list(ASSETS))
    ap.add_argument("--cells", nargs="+", default=list(CELLS), choices=list(CELLS))
    ap.add_argument("--regimes", nargs="+", default=list(REGIMES), choices=list(REGIMES))
    ap.add_argument("--n-seeds", type=int, default=15)
    ap.add_argument("--seed-start", type=int, default=0)
    args = ap.parse_args()

    base = yaml.safe_load(BASE_PATH.read_text())
    n = 0
    for regime in args.regimes:
        period = REGIMES[regime]
        # per-regime SUBDIR (like 118's per-asset subdirs) so score_concave_confirm.py — which globs
        # results_{asset}_{cell}_seed* — scores each regime independently: point it at .../r1 then .../r2.
        rdir = OUT / regime
        rdir.mkdir(parents=True, exist_ok=True)
        for asset in args.assets:
            for cell in args.cells:
                for seed in range(args.seed_start, args.seed_start + args.n_seeds):
                    cfg = copy.deepcopy(base)
                    cfg["training"]["seed"] = seed
                    cfg["training"]["target_dataset"] = ASSETS[asset]
                    cfg["training"]["target_period"] = period
                    cfg["training"]["rollout_reg_every"] = REG_EVERY
                    cfg["simulator"]["price_formation_kwargs"].update(CELLS[cell])
                    (rdir / f"config_{asset}_{cell}_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
                    n += 1

    est_h = n * 62 / 60
    print(f"wrote {n} configs to {OUT}  assets={args.assets} regimes={args.regimes} "
          f"cells={args.cells} n_seeds={args.n_seeds}")
    print(f"  recipe: 108 base + reg_every={REG_EVERY}, δ=0.5 (identical to 113/114)")
    print(f"  ≈ {est_h:.0f} card-hours (~{est_h/8:.1f}h on 8 cards)")


if __name__ == "__main__":
    main()
