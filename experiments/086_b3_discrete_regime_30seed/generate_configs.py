"""086 — B3 discrete Gumbel-softmax regime sweep.

The aggregational_gaussianity fact (band [10, 200]) is consistently
overshot by v4 cells (mean 300+). Diagnosis: the continuous regime GRU
smears all market states into one persistent high-vol regime; there's
no "quiet" period, so aggregated returns stay too leptokurtic.

B3 replaces the continuous GRU with K-state Gumbel-softmax discrete
switching. Each state has its own learned d_regime embedding consumed
by the existing read heads. K=3 covers (calm, normal, stress); K=5
gives finer granularity at the cost of more parameters to fit.

3 cells × 30 seeds = 90 cfg.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE = REPO / "experiments" / "069_gamma_damping_30seed" / "config_T05_g10_seed0.yaml"
COMBO_BASE = REPO / "experiments" / "082_v4_combo_30seed" / "config_combo_full_seed0.yaml"
OUT = REPO / "experiments" / "086_b3_discrete_regime_30seed"
OUT.mkdir(parents=True, exist_ok=True)

# Cells:
#  - k3_pure: discrete K=3 only, otherwise v3 baseline. Tests B3 in isolation.
#  - k3_combo: K=3 + combo_full mechanisms. Headline cell.
#  - k5_combo: K=5 + combo_full. Tests whether more states help.
CELLS = [
    ("b3_k3_pure",  3, False),
    ("b3_k3_combo", 3, True),
    ("b3_k5_combo", 5, True),
]
SEEDS = list(range(30))


def main() -> None:
    base_pure = yaml.safe_load(BASE.read_text())
    base_combo = yaml.safe_load(COMBO_BASE.read_text())
    n = 0
    for tag, k, use_combo in CELLS:
        base = base_combo if use_combo else base_pure
        for s in SEEDS:
            cfg = copy.deepcopy(base)
            # Enable the regime infrastructure first (v3 default is False).
            # Without this, regime_gru is None and the discrete flag has no effect.
            cfg["simulator"]["regime_enabled"] = True
            cfg["simulator"]["regime_discrete_enabled"] = True
            cfg["simulator"]["regime_n_states"] = k
            cfg["simulator"]["regime_gumbel_tau"] = 1.0
            cfg["training"]["seed"] = s
            (OUT / f"config_{tag}_seed{s}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1
    print(f"wrote {n} configs to {OUT}")


if __name__ == "__main__":
    main()
