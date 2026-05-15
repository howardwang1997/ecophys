"""098 — Zumbach `dn` strength × λ refinement (SOTA single-mech dose-response).

089 found `attr_zumbach_dn_s10` is the best single mech (mean 5.12,
strength=1.0, λ=0.95). 089 only tested ONE `dn` setting; refine the
dose-response around the SOTA to find:
  (a) whether a lower-strength dn variant is also competitive (cheaper
      Pareto trade);
  (b) whether λ matters at all (EMA memory length sensitivity).

Cells (5 strengths × 4 λ = 20 cells × 5 seeds = 100 cfg ≈ ~1.5h H20):
  zumdn_s{05, 075, 10, 15, 20}_lam{85, 90, 95, 99}

The 5 strengths span 0.5× to 2× the 089 SOTA. λ values span 0.85
(shorter memory, ~7 step EMA) to 0.99 (longer memory, ~100 step EMA).

Output: dose-response surface for §4 Zumbach-mechanism discussion. If
mean is flat across the grid, our 089 single setting was robust. If
sharply peaked, the SOTA is fragile (paper risk-register R2 fallback).
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_SPX = REPO / "experiments" / "069_gamma_damping_30seed" / "config_T05_g10_seed0.yaml"
OUT = REPO / "experiments" / "098_zumbach_dn_refinement_20seed"
OUT.mkdir(parents=True, exist_ok=True)


STRENGTHS = [0.5, 0.75, 1.0, 1.5, 2.0]
LAMBDAS = [0.85, 0.90, 0.95, 0.99]


def main() -> None:
    base_spx = yaml.safe_load(BASE_SPX.read_text())
    n = 0
    n_cells = 0
    for s in STRENGTHS:
        for lam in LAMBDAS:
            s_tag = f"{s:.2f}".replace(".", "")
            lam_tag = f"{lam:.2f}".replace(".", "")
            tag = f"zumdn_s{s_tag}_lam{lam_tag}"
            n_cells += 1
            for seed in range(5):
                cfg = copy.deepcopy(base_spx)
                cfg["simulator"]["zumbach_feedback_lambda"] = lam
                cfg["simulator"]["zumbach_feedback_strength"] = s
                cfg["simulator"]["zumbach_feedback_mode"] = "downside"
                cfg["training"]["seed"] = seed
                (OUT / f"config_{tag}_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
                n += 1
    print(f"wrote {n} configs across {n_cells} (s × λ) cells to {OUT}")


if __name__ == "__main__":
    main()
