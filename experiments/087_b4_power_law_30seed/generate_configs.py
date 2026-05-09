"""087 — B4 power-law external potential sweep.

The hill_tail_index fact (band [2, 4]) is the worst-failing fact in v3
and v4 alike — Lévy noise alone gets only 1-2/30 seeds in band, because
the Hill estimator is dominated by AR(1) drift contamination at finite
sample size. B4 replaces the standard MLP-only ExternalPotential with

    V_ext(s) = w_mlp · MLP(s, ctx) + w_pow · Σ_i |s_i|^α / α

For α<2, ∇V_pow ∝ sign(s)·|s|^(α-1) is sub-linear: the restoring force
weakens at large |s|, so excursions don't get aggressively pulled back.
This produces fat-tailed return distributions intrinsically (i.e. via
the dynamics, not just via noise distribution). Stacking with B1
microstructure (which fixes AR(1)) is expected to be the combination
that finally pushes hill into [2, 4].

3 cells × 30 seeds = 90 cfg.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE = REPO / "experiments" / "069_gamma_damping_30seed" / "config_T05_g10_seed0.yaml"
COMBO_BASE = REPO / "experiments" / "082_v4_combo_30seed" / "config_combo_full_seed0.yaml"
OUT = REPO / "experiments" / "087_b4_power_law_30seed"
OUT.mkdir(parents=True, exist_ok=True)

# Cells:
#  - alpha13_pure: α=1.3 (heavy fat tails), otherwise v3 baseline.
#  - alpha15_combo: α=1.5 + combo_full. Headline cell.
#  - alpha18_combo: α=1.8 (gentler) + combo_full. Tests dose-response.
CELLS = [
    ("b4_alpha13_pure",  1.3, False),
    ("b4_alpha15_combo", 1.5, True),
    ("b4_alpha18_combo", 1.8, True),
]
SEEDS = list(range(30))


def main() -> None:
    base_pure = yaml.safe_load(BASE.read_text())
    base_combo = yaml.safe_load(COMBO_BASE.read_text())
    n = 0
    for tag, alpha, use_combo in CELLS:
        base = base_combo if use_combo else base_pure
        for s in SEEDS:
            cfg = copy.deepcopy(base)
            cfg["simulator"]["power_law_external"] = True
            cfg["simulator"]["power_law_alpha"] = alpha
            cfg["simulator"]["power_law_w_pow"] = 0.5
            cfg["simulator"]["power_law_w_mlp"] = 1.0
            cfg["training"]["seed"] = s
            (OUT / f"config_{tag}_seed{s}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1
    print(f"wrote {n} configs to {OUT}")


if __name__ == "__main__":
    main()
