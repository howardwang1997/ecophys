"""081 — cross-asset: BTC 2017-2026 daily.

Test generalization by training on BTC instead of SPX. Use the same
T05_g10 cell from 069 as the base config, but swap the dataset. BTC
has higher volatility (~3-5× SPX) and different tail behavior, so we
expect lower pass rates but non-zero if the physics is universal.

We also test one v4 combo cell: levy_alpha=1.7 + asym_drag_alpha=0.6
+ memory_kernel (λ=0.95, strength=1.0) to see if the mechanisms help
on BTC.

2 cells × 30 seeds = 60 configs.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE = REPO / "experiments" / "069_gamma_damping_30seed" / "config_T05_g10_seed0.yaml"
OUT = REPO / "experiments" / "081_btc_30seed"
OUT.mkdir(parents=True, exist_ok=True)

CELLS = [
    # (tag, levy_alpha, asym_drag_alpha, mem_kernel_lambda, mem_kernel_strength)
    ("btc_baseline", None, None, None, None),
    ("btc_v4combo", 1.7, 0.6, 0.95, 1.0),
]
SEEDS = list(range(30))


def main() -> None:
    base = yaml.safe_load(BASE.read_text())
    n = 0
    for tag, levy, asym, mem_lam, mem_str in CELLS:
        for s in SEEDS:
            cfg = copy.deepcopy(base)
            # swap dataset to BTC
            cfg["training"]["target_dataset"] = "btc"
            cfg["training"]["target_period"] = "2017-2026_daily"
            # apply v4 mechanisms if specified
            if levy is not None:
                cfg["simulator"]["levy_alpha"] = levy
            if asym is not None:
                cfg["simulator"]["asym_drag_alpha"] = asym
            if mem_lam is not None:
                cfg["simulator"]["memory_kernel_lambda"] = mem_lam
                cfg["simulator"]["memory_kernel_strength"] = mem_str
            cfg["training"]["seed"] = s
            (OUT / f"config_{tag}_seed{s}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1
    print(f"wrote {n} configs to {OUT}")


if __name__ == "__main__":
    main()
