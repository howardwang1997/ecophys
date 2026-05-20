"""098c — Zumbach `dn` fine-grid around 089 anchor (overnight follow-up).

098b is a coarse 8-cell trim at n=30. 098c fills the (s, λ) grid more
densely around the 089 production point `zumdn_s100_lam095=5.12` (n=48),
so the paper §4 dose-response figure has a publication-quality surface
rather than 4 sparse points.

098b coverage (coarse):
  s ∈ {0.5, 0.75, 1.0, 1.5} × λ ∈ {0.9, 0.95, 0.99}

098c adds (fine grid + λ=0.85 corner from original 098):
  - s ∈ {0.6, 0.85, 1.2}  × λ = 0.95   (fine strength scan)
  - s = 1.0 × λ ∈ {0.85, 0.92, 0.97}    (fine λ scan)

Cells (6 × 30 = 180 cfg ≈ 2.5-3h on 8-card H20):

| tag                | reason                                            |
|--------------------|---------------------------------------------------|
| zumdn_s060_lam095  | between 098b's 0.50 and 0.75                      |
| zumdn_s085_lam095  | between 098b's 0.75 and 1.00 (near 089 anchor)    |
| zumdn_s120_lam095  | between 098b's 1.00 and 1.50                      |
| zumdn_s100_lam085  | 098's noisy 5.80 at n=4 — confirm low-λ corner    |
| zumdn_s100_lam092  | between 098b's 0.90 and 0.95                      |
| zumdn_s100_lam097  | between 098b's 0.95 and 0.99                      |

Combined with 098 + 098b coverage, this gives a 5×6 dose-response grid for
Paper A §4 Figure 1c.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_SPX = REPO / "experiments" / "069_gamma_damping_30seed" / "config_T05_g10_seed0.yaml"
OUT = REPO / "experiments" / "098c_zumdn_fine_grid_n30"
OUT.mkdir(parents=True, exist_ok=True)


CELLS = [
    ("zumdn_s060_lam095", 0.60, 0.95),
    ("zumdn_s085_lam095", 0.85, 0.95),
    ("zumdn_s120_lam095", 1.20, 0.95),
    ("zumdn_s100_lam085", 1.00, 0.85),
    ("zumdn_s100_lam092", 1.00, 0.92),
    ("zumdn_s100_lam097", 1.00, 0.97),
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
    print(f"wrote {n} configs across {len(CELLS)} cells × {N_SEEDS} seeds to {OUT}")


if __name__ == "__main__":
    main()
