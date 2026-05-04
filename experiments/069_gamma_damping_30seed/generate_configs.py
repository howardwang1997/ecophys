"""069 — γ damping 30-seed sweep.

Hypothesis (from E1, n=6): γ=10 (γ·dt=0.10) cuts ac_r 0.58→0.34 AND brings
Hurst into physical range AND flips leverage sign. Confirm at lottery-rule
n=30 and find the sweet spot in γ ∈ {3, 5, 10, 15, 20}.

Cells:
  T05_g3   freezeTG_T0.05_g3   γ·dt = 0.03
  T05_g5   freezeTG_T0.05_g5   γ·dt = 0.05
  T05_g10  freezeTG_T0.05_g10  γ·dt = 0.10  (E1 best)
  T05_g15  freezeTG_T0.05_g15  γ·dt = 0.15
  T05_g20  freezeTG_T0.05_g20  γ·dt = 0.20
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE = REPO / "experiments" / "064_winner_50seed_repro" / "config_p_4_2__2_1_seed51.yaml"
OUT = REPO / "experiments" / "069_gamma_damping_30seed"
OUT.mkdir(parents=True, exist_ok=True)

GAMMAS = [3.0, 5.0, 10.0, 15.0, 20.0]
SEEDS = list(range(30))


def main() -> None:
    base = yaml.safe_load(BASE.read_text())
    n = 0
    for g in GAMMAS:
        tag = f"T05_g{int(g)}"
        for s in SEEDS:
            cfg = copy.deepcopy(base)
            cfg["simulator"]["temperature_init"] = 0.05
            cfg["simulator"]["gamma_init"] = float(g)
            cfg["simulator"]["learn_temperature"] = False
            cfg["simulator"]["learn_gamma"] = False
            cfg["training"]["seed"] = s
            (OUT / f"config_{tag}_seed{s}.yaml").write_text(
                yaml.safe_dump(cfg, sort_keys=False)
            )
            n += 1
    print(f"wrote {n} configs to {OUT}")


if __name__ == "__main__":
    main()
