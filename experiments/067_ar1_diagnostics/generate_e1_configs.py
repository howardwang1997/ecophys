"""Generate E1 configs: same as 064 winner, but with frozen (T, gamma) at
several values, to test whether autocorr=0.6 is structural (independent of
training-time T-suppression) or a stable attractor.

Variants:
  freezeTG_T05_g1   — sanity: same as init, no learning (should reproduce 5/11, ac=0.6)
  freezeTG_T20_g1   — 4× noise floor (loose Langevin)
  freezeTG_T05_g10  — 10× damping → push toward overdamped (γ·dt = 0.1 vs 0.01)
  freezeTG_T05_g100 — 100× damping → fully overdamped (γ·dt = 1.0)

Each × 6 seeds = 24 runs total.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE = REPO / "experiments" / "064_winner_50seed_repro" / "config_p_4_2__2_1_seed51.yaml"
OUT_DIR = REPO / "experiments" / "067_ar1_diagnostics"
OUT_DIR.mkdir(parents=True, exist_ok=True)

VARIANTS = [
    ("freezeTG_T05_g1",   0.05, 1.0),
    ("freezeTG_T20_g1",   0.20, 1.0),
    ("freezeTG_T05_g10",  0.05, 10.0),
    ("freezeTG_T05_g100", 0.05, 100.0),
]
SEEDS = [0, 1, 2, 3, 4, 5]


def main() -> None:
    base = yaml.safe_load(BASE.read_text())
    n = 0
    for tag, T, g in VARIANTS:
        for s in SEEDS:
            cfg = copy.deepcopy(base)
            cfg["simulator"]["temperature_init"] = T
            cfg["simulator"]["gamma_init"] = g
            cfg["simulator"]["learn_temperature"] = False
            cfg["simulator"]["learn_gamma"] = False
            cfg["training"]["seed"] = s
            cfg["training"]["target_dataset"] = base["training"]["target_dataset"]
            out = OUT_DIR / f"config_{tag}_seed{s}.yaml"
            out.write_text(yaml.safe_dump(cfg, sort_keys=False))
            n += 1
    print(f"wrote {n} configs to {OUT_DIR}")


if __name__ == "__main__":
    main()
