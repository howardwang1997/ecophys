"""070 — rollout_reg 30-seed retest.

The 057 sweep produced ONE positive signal in the long-weekend batch:
  rr_s120_w10_e5: mean 6.83/11 (n=6 — lottery zone)

Confirm/refute at n=30 and probe nearby cells. From 057 yaml convention:
  s120 = rollout_reg_steps=120
  w10  = rollout_reg_weight=0.10  (NOT 10 — the integer is weight × 100)
  e5   = rollout_reg_every=5

Cells:
  rr_s120_w5_e5   weight=0.05, half the orig
  rr_s120_w10_e5  weight=0.10  (the original 6.83 cell)
  rr_s120_w20_e5  weight=0.20, double
  rr_s240_w10_e5  longer horizon, same weight
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE = REPO / "experiments" / "064_winner_50seed_repro" / "config_p_4_2__2_1_seed51.yaml"
OUT = REPO / "experiments" / "070_rr_30seed_retest"
OUT.mkdir(parents=True, exist_ok=True)

CELLS = [
    ("rr_s120_w5_e5",  120, 0.05, 5),
    ("rr_s120_w10_e5", 120, 0.10, 5),
    ("rr_s120_w20_e5", 120, 0.20, 5),
    ("rr_s240_w10_e5", 240, 0.10, 5),
]
SEEDS = list(range(30))


def main() -> None:
    base = yaml.safe_load(BASE.read_text())
    n = 0
    for tag, steps, weight, every in CELLS:
        for s in SEEDS:
            cfg = copy.deepcopy(base)
            cfg["training"]["rollout_reg_enabled"] = True
            cfg["training"]["rollout_reg_steps"] = steps
            cfg["training"]["rollout_reg_chunk"] = 24
            cfg["training"]["rollout_reg_weight"] = weight
            cfg["training"]["rollout_reg_every"] = every
            cfg["training"]["seed"] = s
            (OUT / f"config_{tag}_seed{s}.yaml").write_text(
                yaml.safe_dump(cfg, sort_keys=False)
            )
            n += 1
    print(f"wrote {n} configs to {OUT}")


if __name__ == "__main__":
    main()
