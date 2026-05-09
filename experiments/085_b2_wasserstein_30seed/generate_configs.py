"""085 — B2 Wasserstein-loss training family.

B2 swaps the moment-matching loss for a continuous distributional
distance. The existing `ecomd/training/losses.py` already supports
loss_family ∈ {moments, wasserstein, mmd, sinkhorn, hybrid} via
`compute_loss()`. This experiment is configs-only.

Hypothesis: the Cont-2001 stylized facts are non-linear functionals of
the return distribution; matching moments is a coarse surrogate. A
direct distributional distance (sliced-Wasserstein-2) should give
uniform 5–15% lift across all facts, including those v4 mechanisms
struggle with.

The hybrid cell (moments + wasserstein) is the most defensible for
reviewers — keeps the well-conditioned moment loss as regularizer
while adding W2 for shape matching.

3 cells × 30 seeds = 90 cfg.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE = REPO / "experiments" / "069_gamma_damping_30seed" / "config_T05_g10_seed0.yaml"
COMBO_BASE = REPO / "experiments" / "082_v4_combo_30seed" / "config_combo_full_seed0.yaml"
OUT = REPO / "experiments" / "085_b2_wasserstein_30seed"
OUT.mkdir(parents=True, exist_ok=True)

# Cells:
#  - wasserstein_pure: Family=wasserstein, v3 baseline simulator. Tests
#    whether the loss alone (without v4 mechanisms) lifts performance.
#  - wasserstein_combo: Family=wasserstein + combo_full mechanisms. Pure W2.
#  - hybrid_combo: Family=hybrid (moments + W2). Reviewer-defensible.
CELLS = [
    ("b2_wasserstein_pure",  "wasserstein", False),
    ("b2_wasserstein_combo", "wasserstein", True),
    ("b2_hybrid_combo",      "hybrid",      True),
]
SEEDS = list(range(30))


def main() -> None:
    base_pure = yaml.safe_load(BASE.read_text())
    base_combo = yaml.safe_load(COMBO_BASE.read_text())
    n = 0
    for tag, family, use_combo in CELLS:
        base = base_combo if use_combo else base_pure
        for s in SEEDS:
            cfg = copy.deepcopy(base)
            cfg["training"]["loss_weights"]["loss_family"] = family
            # Wasserstein weight needs to be > 0 for the family to take effect
            cfg["training"]["loss_weights"]["w_wasserstein"] = 1.0
            # Multi-scale Wasserstein on aggregated returns at scales [1, 5, 20]
            # is the default; let losses.py pick it up via wasserstein_scales.
            if family == "hybrid":
                # Keep a small moments contribution as regularizer
                cfg["training"]["loss_weights"]["w_acf_sq"] = 0.5
                cfg["training"]["loss_weights"]["w_leverage"] = 0.1
                cfg["training"]["loss_weights"]["w_hill"] = 0.05
            cfg["training"]["seed"] = s
            (OUT / f"config_{tag}_seed{s}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1
    print(f"wrote {n} configs to {OUT}")


if __name__ == "__main__":
    main()
