"""071 — T-γ combo "best of both worlds" 30-seed.

E1 finding: T20_g1 inflates score to 5.50 by acf_sq²+cond_kurt cheats but ac_r unchanged.
            T05_g10 gets honest dynamics (Hurst→0.73, leverage flip) but mean only 4.0.
Hypothesis: T20_g10 (high noise floor + 10× damping) might combine the benefits —
honest dynamics PLUS more T-driven volatility-clustering signal that's not pure AR(1).

Cells:
  T10_g10  T=0.10, γ=10 (mid)
  T20_g10  T=0.20, γ=10 (4× T floor + overdamping)
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE = REPO / "experiments" / "064_winner_50seed_repro" / "config_p_4_2__2_1_seed51.yaml"
OUT = REPO / "experiments" / "071_T_gamma_combo"
OUT.mkdir(parents=True, exist_ok=True)

CELLS = [
    ("T10_g10", 0.10, 10.0),
    ("T20_g10", 0.20, 10.0),
]
SEEDS = list(range(30))


def main() -> None:
    base = yaml.safe_load(BASE.read_text())
    n = 0
    for tag, T, g in CELLS:
        for s in SEEDS:
            cfg = copy.deepcopy(base)
            cfg["simulator"]["temperature_init"] = T
            cfg["simulator"]["gamma_init"] = g
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
