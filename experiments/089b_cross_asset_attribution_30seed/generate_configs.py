"""089b — single-mechanism attribution on BTC + EURUSD (cross-asset Figure 1).

089 produced the 16-cell × 11-fact attribution matrix on SPX. This
sibling batch repeats the 8 most-informative single-mechanism cells on
BTC and EURUSD — the two assets most different from SPX (1m crypto +
daily FX). Output: per-asset 8×11 mechanism-fact attribution heatmaps.

Critical for paper §5: makes "mechanisms are specialists" claim
asset-independent, not SPX-specific.

Cells (8 single mechs × 2 assets × 30 seeds = 480 cfg ≈ ~9h H20):

  attr_<asset>_baseline_v3         — control
  attr_<asset>_zumbach_dn_s10      — 089 SOTA single
  attr_<asset>_b3_k3               — Branch F best stable
  attr_<asset>_asymdrag_a06        — Branch D best
  attr_<asset>_ar1_s05             — biggest fact-trader
  attr_<asset>_powerlaw_a15        — B4
  attr_<asset>_levy_a17            — Lévy α-stable
  attr_<asset>_memk_l095_s10       — memory kernel

Output: post-batch, run `scripts/score_attribution.py` per asset's
results dir → two new 8×11 matrices for §5 cross-asset table.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_SPX = REPO / "experiments" / "069_gamma_damping_30seed" / "config_T05_g10_seed0.yaml"
OUT = REPO / "experiments" / "089b_cross_asset_attribution_30seed"
OUT.mkdir(parents=True, exist_ok=True)


ASSET_PERIOD = {
    "btcusdt": "2024Q1_1m",
    "eurusd":  "daily",
}


def apply_levy(cfg, alpha=1.7):
    cfg["simulator"]["noise_dist"] = "levy"
    cfg["simulator"]["noise_levy_alpha"] = alpha
    cfg["simulator"]["noise_levy_clip"] = 50.0


def apply_asym(cfg, alpha=0.6):
    cfg["simulator"]["asym_drag_alpha"] = alpha


def apply_memk(cfg, lam=0.95, strength=1.0):
    cfg["simulator"]["memory_kernel_lambda"] = lam
    cfg["simulator"]["memory_kernel_strength"] = strength


def apply_powerlaw(cfg, alpha=1.5):
    cfg["simulator"]["power_law_external"] = True
    cfg["simulator"]["power_law_alpha"] = alpha
    cfg["simulator"]["power_law_w_pow"] = 0.5
    cfg["simulator"]["power_law_w_mlp"] = 1.0


def apply_b3(cfg, k=3, tau=1.0):
    cfg["simulator"]["regime_enabled"] = True
    cfg["simulator"]["regime_discrete_enabled"] = True
    cfg["simulator"]["regime_n_states"] = k
    cfg["simulator"]["regime_gumbel_tau"] = tau


def apply_ar1_whiten(cfg, lam=0.9, strength=0.5):
    cfg["simulator"]["ar1_whiten_lambda"] = lam
    cfg["simulator"]["ar1_whiten_strength"] = strength


def apply_zumbach_dn(cfg):
    cfg["simulator"]["zumbach_feedback_lambda"] = 0.95
    cfg["simulator"]["zumbach_feedback_strength"] = 1.0
    cfg["simulator"]["zumbach_feedback_mode"] = "downside"


# (mech_tag, mods)
MECHANISMS = [
    ("baseline_v3",     []),
    ("zumbach_dn_s10",  [apply_zumbach_dn]),
    ("b3_k3",           [lambda c: apply_b3(c, k=3, tau=1.0)]),
    ("asymdrag_a06",    [lambda c: apply_asym(c, alpha=0.6)]),
    ("ar1_s05",         [lambda c: apply_ar1_whiten(c, lam=0.9, strength=0.5)]),
    ("powerlaw_a15",    [lambda c: apply_powerlaw(c, alpha=1.5)]),
    ("levy_a17",        [lambda c: apply_levy(c, alpha=1.7)]),
    ("memk_l095_s10",   [lambda c: apply_memk(c, lam=0.95, strength=1.0)]),
]


def main() -> None:
    base_spx = yaml.safe_load(BASE_SPX.read_text())
    n = 0
    n_cells = 0
    for asset, period in ASSET_PERIOD.items():
        for mech_tag, mods in MECHANISMS:
            tag = f"attr_{asset}_{mech_tag}"
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
