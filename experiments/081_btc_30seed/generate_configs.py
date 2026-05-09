"""081 — cross-asset: BTC 1-minute (2024 Q1).

Test generalization by training on BTC instead of SPX. Use the same
T05_g10 cell from 069 as the base config, but swap the dataset to the
ONLY BTC return series this repo has in data/raw/: BTCUSDT 1-minute
for 2024 Q1 (≈ 130k returns vs SPX's 2.8k daily). We do NOT have daily
BTC parquet shards.

The trainer dispatch in `train_distributed.load_real_returns` only
recognises `dataset == "btcusdt"` paired with `period == "2024Q1_1m"`;
any other value silently falls back to SPX. Earlier 081 configs used
`btc` / `2017-2026_daily` and silently trained on SPX while logging
`target_dataset: btc` — the cross-asset story was fake. This generator
is the corrected version.

Cells:
- `btc_baseline`: pure v3 (no Lévy, no asym, no memk)
- `btc_v4combo`:  noise_dist=levy + noise_levy_alpha=1.7 + asym_drag_alpha=0.6
                  + memory_kernel(λ=0.95, strength=1.0)

The v4combo cell uses the SAME field names as 077_levy_noise_30seed and
078_asym_drag_30seed so they match what the integrator actually reads.
The PRIOR generator wrote `levy_alpha: 1.7` (wrong key, ignored by
EcoMDConfig) and `noise_dist: t` (no Lévy active). That bug is fixed
here.

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
    # (tag, levy_alpha or None, asym_drag_alpha or None, memk(λ, strength) or None)
    ("btc_baseline", None, None, None),
    ("btc_v4combo",  1.7,  0.6,  (0.95, 1.0)),
]
SEEDS = list(range(30))


def main() -> None:
    base = yaml.safe_load(BASE.read_text())
    n = 0
    for tag, levy_alpha, asym_alpha, memk in CELLS:
        for s in SEEDS:
            cfg = copy.deepcopy(base)

            # --- Dataset (use the trainer's recognised keys) ---
            cfg["training"]["target_dataset"] = "btcusdt"
            cfg["training"]["target_period"] = "2024Q1_1m"

            # --- V4 mechanisms (using the field names EcoMDConfig actually reads) ---
            if levy_alpha is not None:
                cfg["simulator"]["noise_dist"] = "levy"
                cfg["simulator"]["noise_levy_alpha"] = levy_alpha
                cfg["simulator"]["noise_levy_clip"] = 50.0
            if asym_alpha is not None:
                cfg["simulator"]["asym_drag_alpha"] = asym_alpha
            if memk is not None:
                cfg["simulator"]["memory_kernel_lambda"] = memk[0]
                cfg["simulator"]["memory_kernel_strength"] = memk[1]

            cfg["training"]["seed"] = s
            (OUT / f"config_{tag}_seed{s}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1
    print(f"wrote {n} configs to {OUT}")


if __name__ == "__main__":
    main()
