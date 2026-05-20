"""099b — Memory kernel refinement at n=30 (overnight follow-up to 099 n=5).

099 ran 20 cells × 5 seeds. After rejections, several cells had n=3-5 and
4 cells tied at mean 5.80 — the seed-count lottery makes this surface
useless for paper claims. 099b trims to 8 paper-critical cells × 30 seeds
+ a baseline reference to settle whether memk has a real operating point
or is correctly disqualified.

Cells (9 × 30 = 270 cfg ≈ 5-6h on 8-card H20):

| tag                | reason                                                 |
|--------------------|--------------------------------------------------------|
| baseline_v3        | n=30 reference (no memory kernel)                      |
| memk_s025_lam095   | 099 mean 5.80 at n=5 (lowest strength tie)             |
| memk_s050_lam090   | 099 mean 5.80 at n=5                                   |
| memk_s075_lam095   | 099 mean 5.80 at n=5 (mid strength)                    |
| memk_s100_lam085   | 099 mean 5.80 at n=5 (089 strength, low λ)             |
| memk_s050_lam099   | 099 mean 5.60 at n=5 (high λ neighbour)                |
| memk_s100_lam099   | 099 mean 5.40 at n=5 (089 strength, high λ)            |
| memk_s025_lam090   | 099 mean 5.00 at n=5 (low strength, low λ corner)      |
| memk_s075_lam090   | 099 mean 5.20 at n=5 (mid both, gap-filler)            |
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_SPX = REPO / "experiments" / "069_gamma_damping_30seed" / "config_T05_g10_seed0.yaml"
OUT = REPO / "experiments" / "099b_memk_refinement_n30"
OUT.mkdir(parents=True, exist_ok=True)


CELLS = [
    ("memk_s025_lam095", 0.25, 0.95),
    ("memk_s050_lam090", 0.50, 0.90),
    ("memk_s075_lam095", 0.75, 0.95),
    ("memk_s100_lam085", 1.00, 0.85),
    ("memk_s050_lam099", 0.50, 0.99),
    ("memk_s100_lam099", 1.00, 0.99),
    ("memk_s025_lam090", 0.25, 0.90),
    ("memk_s075_lam090", 0.75, 0.90),
]

N_SEEDS = 30


def main() -> None:
    base_spx = yaml.safe_load(BASE_SPX.read_text())
    n = 0
    for tag, s, lam in CELLS:
        for seed in range(N_SEEDS):
            cfg = copy.deepcopy(base_spx)
            cfg["simulator"]["memory_kernel_lambda"] = lam
            cfg["simulator"]["memory_kernel_strength"] = s
            cfg["training"]["seed"] = seed
            (OUT / f"config_{tag}_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1

    for seed in range(N_SEEDS):
        cfg = copy.deepcopy(base_spx)
        for k in ("memory_kernel_lambda", "memory_kernel_strength"):
            cfg["simulator"].pop(k, None)
        cfg["training"]["seed"] = seed
        (OUT / f"config_baseline_v3_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
        n += 1

    print(f"wrote {n} configs across {len(CELLS) + 1} cells × {N_SEEDS} seeds to {OUT}")


if __name__ == "__main__":
    main()
