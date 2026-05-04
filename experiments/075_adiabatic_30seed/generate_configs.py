"""075 — adiabatic timescale separation 30-seed sweep.

Hypothesis: AR(1) drift comes from the per-outer-step return being a SINGLE
agent step, so neighboring returns are correlated through the slow agent
state. Adiabatic separation: many fast agent steps (inner_n) per ONE price
update. Per outer step the return = sum of inner_n independent walks →
random-walk-like.

Cells (combine with E1's γ=10 fix to isolate adiabatic contribution):
  inner_1_g10   — control (γ=10 only, no adiabatic)
  inner_5_g10   — γ=10 + 5 inner agent steps per price step
  inner_10_g10  — γ=10 + 10 inner steps
  inner_20_g10  — γ=10 + 20 inner steps

All cells freeze T=0.05/γ=10 (E1's overdamped fix). 4 cells × 30 seeds = 120 cfgs.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE = REPO / "experiments" / "064_winner_50seed_repro" / "config_p_4_2__2_1_seed51.yaml"
OUT = REPO / "experiments" / "075_adiabatic_30seed"
OUT.mkdir(parents=True, exist_ok=True)

INNER_STEPS = [1, 5, 10, 20]
SEEDS = list(range(30))


def main() -> None:
    base = yaml.safe_load(BASE.read_text())
    n = 0
    for inner in INNER_STEPS:
        tag = f"inner_{inner}_g10"
        for s in SEEDS:
            cfg = copy.deepcopy(base)
            cfg["simulator"]["temperature_init"] = 0.05
            cfg["simulator"]["gamma_init"] = 10.0
            cfg["simulator"]["learn_temperature"] = False
            cfg["simulator"]["learn_gamma"] = False
            cfg["simulator"]["inner_steps_per_price"] = inner
            cfg["training"]["seed"] = s
            (OUT / f"config_{tag}_seed{s}.yaml").write_text(
                yaml.safe_dump(cfg, sort_keys=False)
            )
            n += 1
    print(f"wrote {n} configs to {OUT}")


if __name__ == "__main__":
    main()
