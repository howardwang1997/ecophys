"""092 — 5-asset cross-asset replication (M3 milestone pulled forward).

Reviewer-2's biggest predictable attack on Paper A is "you only show SPX".
This batch tests whether the post-089 best mechanisms replicate across
5 assets at n=30 each.

Mechanisms (4 best per 089 + 090 hero-cell candidate):
  - zumbach_dn_s10     : 089 best single (mean 5.12 on SPX)
  - b3_k3              : Branch F best stable (mean 4.96 on SPX at n=50)
  - asymdrag_a06       : Branch D best (mean 4.92 on SPX at n=48)
  - pair_zumdn_b3      : 090's hero-cell candidate (composition)

Assets (5):
  - spx     : daily, default reference asset
  - btcusdt : 2024Q1_1m, crypto/intraday → tests timescale generalization
  - eurusd  : daily, FX → tests asset-class generalization
  - gold    : daily, commodity
  - ndx     : daily, equity-tech (alternate equity benchmark for SPX)

Total: 4 cells × 5 assets × 30 seeds = 600 cfg ≈ ~11h H20.

Success criterion (per state doc §3.3 M3 plan):
  ≥3 of 5 assets reach mean ≥ 4.5/11 with the same recipe
  → architectural universality (even if not coverage universality).
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_SPX = REPO / "experiments" / "069_gamma_damping_30seed" / "config_T05_g10_seed0.yaml"
OUT = REPO / "experiments" / "092_5asset_replication_30seed"
OUT.mkdir(parents=True, exist_ok=True)


ASSET_PERIOD = {
    "spx":     "daily",
    "btcusdt": "2024Q1_1m",
    "eurusd":  "daily",
    "gold":    "daily",
    "ndx":     "daily",
}


def apply_asym(cfg, alpha=0.6):
    cfg["simulator"]["asym_drag_alpha"] = alpha


def apply_b3(cfg, k=3, tau=1.0):
    cfg["simulator"]["regime_enabled"] = True
    cfg["simulator"]["regime_discrete_enabled"] = True
    cfg["simulator"]["regime_n_states"] = k
    cfg["simulator"]["regime_gumbel_tau"] = tau


def apply_zumbach_dn(cfg):
    cfg["simulator"]["zumbach_feedback_lambda"] = 0.95
    cfg["simulator"]["zumbach_feedback_strength"] = 1.0
    cfg["simulator"]["zumbach_feedback_mode"] = "downside"


MECHANISMS = [
    ("zumdn",       [apply_zumbach_dn]),
    ("b3",          [lambda c: apply_b3(c, k=3, tau=1.0)]),
    ("asym",        [lambda c: apply_asym(c, alpha=0.6)]),
    ("pair_zumdn_b3", [apply_zumbach_dn, lambda c: apply_b3(c, k=3, tau=1.0)]),
]


def main() -> None:
    base_spx = yaml.safe_load(BASE_SPX.read_text())
    n = 0
    n_cells = 0
    for mech_tag, mods in MECHANISMS:
        for asset, period in ASSET_PERIOD.items():
            tag = f"xa_{asset}_{mech_tag}"
            n_cells += 1
            for seed in range(30):
                cfg = copy.deepcopy(base_spx)
                for fn in mods:
                    fn(cfg)
                cfg["training"]["seed"] = seed
                cfg["training"]["target_dataset"] = asset
                cfg["training"]["target_period"] = period
                (OUT / f"config_{tag}_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
                n += 1
    print(f"wrote {n} configs across {n_cells} cells to {OUT}")


if __name__ == "__main__":
    main()
