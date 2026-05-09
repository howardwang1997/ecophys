"""083 — Asymmetric drag fine grid (dose-response refinement).

Branch D found that asym_drag_alpha is the strongest single mechanism:
  - α=0.3 mean=4.57 max=9
  - α=0.6 mean=5.10 max=9 ×3 (best so far) but std=2.12
  - α=0.9 mean=4.17 (over-strong, breaks acf_sq)

This sweep fills in the missing α values to identify the sweet spot
between mean lift and stability. Provides the §4.3 ablation figure
showing the mean-vs-α curve.

3 cells × 30 seeds = 90 cfg.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE = REPO / "experiments" / "069_gamma_damping_30seed" / "config_T05_g10_seed0.yaml"
OUT = REPO / "experiments" / "083_asym_drag_finegrid_30seed"
OUT.mkdir(parents=True, exist_ok=True)

# (tag, asym_drag_alpha)
CELLS = [
    ("asymdrag_a04", 0.4),
    ("asymdrag_a05", 0.5),
    ("asymdrag_a07", 0.7),
]
SEEDS = list(range(30))


def main() -> None:
    base = yaml.safe_load(BASE.read_text())
    n = 0
    for tag, alpha in CELLS:
        for s in SEEDS:
            cfg = copy.deepcopy(base)
            cfg["simulator"]["asym_drag_alpha"] = alpha
            cfg["training"]["seed"] = s
            (OUT / f"config_{tag}_seed{s}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1
    print(f"wrote {n} configs to {OUT}")


if __name__ == "__main__":
    main()
