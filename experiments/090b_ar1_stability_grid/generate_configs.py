"""090b — AR(1) whitening stability grid.

089 found that `attr_ar1_s03` (λ=0.9, strength=0.3) lifts autocorr_returns
24% → 87% but 35/50 seeds blow up (70% rejection). The mechanism works
for what we built it for; the instability is a parameter-envelope issue.

This sub-batch sweeps a (strength × lambda) grid to find a stable
operating point with comparable autocorr lift. Also tests a drift-clip
variant that bounds the EMA-subtraction term.

Cells (6 total, 120 cfg ≈ ~2h H20):

  Low-strength × varying lambda (faster λ = noisier EMA estimate):
    ar1_s02_l85       — strength=0.20, λ=0.85
    ar1_s02_l95       — strength=0.20, λ=0.95
    ar1_s025_l90      — strength=0.25, λ=0.90 (between 089 s03 and stable)
    ar1_s025_l95      — strength=0.25, λ=0.95

  Drift-clip variants (cap the whitening contribution magnitude):
    ar1_s03_clip      — strength=0.30, λ=0.90, clip via integrator-side
                        (replicates 089 ar1_s03 with clip added)
    ar1_s05_clip      — strength=0.50, λ=0.90, clip variant of 089 ar1_s05

Total: 6 cells × 20 seeds = 120 cfg.

NOTE: drift-clip is wired via `ar1_whiten_clip` (added in M1.1.1 — see
ecomd/physics/integrator.py). If the integrator doesn't support clip yet,
the launcher will fail preflight and we'll add the knob first.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_SPX = REPO / "experiments" / "069_gamma_damping_30seed" / "config_T05_g10_seed0.yaml"
OUT = REPO / "experiments" / "090b_ar1_stability_grid"
OUT.mkdir(parents=True, exist_ok=True)


def apply_ar1_whiten(cfg, lam=0.9, strength=0.5, clip=None):
    cfg["simulator"]["ar1_whiten_lambda"] = lam
    cfg["simulator"]["ar1_whiten_strength"] = strength
    if clip is not None:
        cfg["simulator"]["ar1_whiten_clip"] = clip


CELLS = [
    ("ar1_s02_l85",  20, [(apply_ar1_whiten, {"lam": 0.85, "strength": 0.20})]),
    ("ar1_s02_l95",  20, [(apply_ar1_whiten, {"lam": 0.95, "strength": 0.20})]),
    ("ar1_s025_l90", 20, [(apply_ar1_whiten, {"lam": 0.90, "strength": 0.25})]),
    ("ar1_s025_l95", 20, [(apply_ar1_whiten, {"lam": 0.95, "strength": 0.25})]),
    ("ar1_s03_clip", 20, [(apply_ar1_whiten, {"lam": 0.90, "strength": 0.30, "clip": 1.0})]),
    ("ar1_s05_clip", 20, [(apply_ar1_whiten, {"lam": 0.90, "strength": 0.50, "clip": 1.0})]),
]


def main() -> None:
    base_spx = yaml.safe_load(BASE_SPX.read_text())
    n = 0
    for tag, n_seeds, mods in CELLS:
        for s in range(n_seeds):
            cfg = copy.deepcopy(base_spx)
            for fn, kwargs in mods:
                fn(cfg, **kwargs)
            cfg["training"]["seed"] = s
            (OUT / f"config_{tag}_seed{s}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1
    print(f"wrote {n} configs across {len(CELLS)} cells to {OUT}")


if __name__ == "__main__":
    main()
