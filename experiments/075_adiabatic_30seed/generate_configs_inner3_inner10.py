"""075 leftover — adiabatic inner_3 / inner_10 cells.

Branch C only ran inner_1_g10 and inner_5_g10. The 30-seed results showed
inner_1 mean=4.60/11 (max=8/11 ×2) and inner_5 mean=4.07/11 (max=7/11),
so adiabatic helps marginally at low inner-step counts. We need inner_3
(between the two) and inner_10 (extending the gradient) to pin down
whether there's a real adiabatic-strength → fact-pass relationship.

4 cells in total once these run; 60 new cfgs at ~14min each ≈ 1.75h on 8-card.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE = REPO / "experiments" / "064_winner_50seed_repro" / "config_p_4_2__2_1_seed51.yaml"
OUT = REPO / "experiments" / "075_adiabatic_30seed"
OUT.mkdir(parents=True, exist_ok=True)

INNER_STEPS = [3, 10]
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
            (OUT / f"config_{tag}_seed{s}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1
    print(f"wrote {n} configs to {OUT}")


if __name__ == "__main__":
    main()
