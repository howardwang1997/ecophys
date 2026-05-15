"""099 — Memory kernel strength × λ refinement.

089 had only one memk setting (λ=0.95, strength=1.0) → mean 4.56 with
Δ=-0.26 vs baseline (worst of the 089 single mechs). The Branch E expansion
plan (2026-05-09) referenced multiple memk strengths but never executed a
clean grid. 099 fills this in.

Cells (5 strengths × 4 λ = 20 cells × 5 seeds = 100 cfg ≈ ~1.5h H20):
  memk_s{025, 05, 075, 10, 15}_lam{85, 90, 95, 99}

If any grid point has mean > 4.82 (089 baseline), memk has a working
operating point we missed. If all are < 4.82, memk is properly
disqualified as a constructive mechanism (paper writes: "we ablated
λ × strength and found no operating point lifts pass count over
baseline").
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_SPX = REPO / "experiments" / "069_gamma_damping_30seed" / "config_T05_g10_seed0.yaml"
OUT = REPO / "experiments" / "099_memk_refinement_5seed"
OUT.mkdir(parents=True, exist_ok=True)


STRENGTHS = [0.25, 0.5, 0.75, 1.0, 1.5]
LAMBDAS = [0.85, 0.90, 0.95, 0.99]


def main() -> None:
    base_spx = yaml.safe_load(BASE_SPX.read_text())
    n = 0
    n_cells = 0
    for s in STRENGTHS:
        for lam in LAMBDAS:
            s_tag = f"{s:.2f}".replace(".", "")
            lam_tag = f"{lam:.2f}".replace(".", "")
            tag = f"memk_s{s_tag}_lam{lam_tag}"
            n_cells += 1
            for seed in range(5):
                cfg = copy.deepcopy(base_spx)
                cfg["simulator"]["memory_kernel_lambda"] = lam
                cfg["simulator"]["memory_kernel_strength"] = s
                cfg["training"]["seed"] = seed
                (OUT / f"config_{tag}_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
                n += 1
    print(f"wrote {n} configs across {n_cells} (s × λ) cells to {OUT}")


if __name__ == "__main__":
    main()
