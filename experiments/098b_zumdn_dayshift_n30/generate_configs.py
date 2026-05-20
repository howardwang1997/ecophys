"""098b — Zumbach `dn` day-shift refinement at n=30.

Trims the 098 grid (20 cells × 5 seeds, often n=3 after rejections) to
8 paper-critical (s, λ) cells × 30 seeds. The 098 result
`zumdn_s075_lam095=6.67 at n=3` is too noisy to cite; this batch
either confirms it or supersedes it with a cleaner number.

Cells (8 × 30 = 240 cfg, ~2.5-3h on 8-card H20):

| tag                    | reason                                                |
|------------------------|-------------------------------------------------------|
| zumdn_s075_lam095      | current 098 noisy top (mean 6.67 at n=3) — MUST confirm
| zumdn_s100_lam095      | 089 production reference (mean 5.12 at n=48)          |
| zumdn_s050_lam099      | high-λ low-strength corner (098 mean 5.20 at n=5)     |
| zumdn_s075_lam099      | (1) neighbour                                         |
| zumdn_s100_lam099      | 098 mean 5.00 at n=5                                  |
| zumdn_s150_lam095      | higher-strength probe (098 mean 5.00 at n=5)          |
| zumdn_s100_lam090      | lower-λ neighbour (098 mean 5.20 at n=5)              |
| baseline_v3            | n=30 baseline reference (no zumbach)                  |
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_SPX = REPO / "experiments" / "069_gamma_damping_30seed" / "config_T05_g10_seed0.yaml"
OUT = REPO / "experiments" / "098b_zumdn_dayshift_n30"
OUT.mkdir(parents=True, exist_ok=True)


CELLS = [
    ("zumdn_s075_lam095", 0.75, 0.95),
    ("zumdn_s100_lam095", 1.00, 0.95),
    ("zumdn_s050_lam099", 0.50, 0.99),
    ("zumdn_s075_lam099", 0.75, 0.99),
    ("zumdn_s100_lam099", 1.00, 0.99),
    ("zumdn_s150_lam095", 1.50, 0.95),
    ("zumdn_s100_lam090", 1.00, 0.90),
]

N_SEEDS = 30


def main() -> None:
    base_spx = yaml.safe_load(BASE_SPX.read_text())
    n = 0
    for tag, s, lam in CELLS:
        for seed in range(N_SEEDS):
            cfg = copy.deepcopy(base_spx)
            cfg["simulator"]["zumbach_feedback_lambda"] = lam
            cfg["simulator"]["zumbach_feedback_strength"] = s
            cfg["simulator"]["zumbach_feedback_mode"] = "downside"
            cfg["training"]["seed"] = seed
            (OUT / f"config_{tag}_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1

    for seed in range(N_SEEDS):
        cfg = copy.deepcopy(base_spx)
        for k in ("zumbach_feedback_lambda", "zumbach_feedback_strength", "zumbach_feedback_mode"):
            cfg["simulator"].pop(k, None)
        cfg["training"]["seed"] = seed
        (OUT / f"config_baseline_v3_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
        n += 1

    print(f"wrote {n} configs across {len(CELLS) + 1} cells × {N_SEEDS} seeds to {OUT}")


if __name__ == "__main__":
    main()
