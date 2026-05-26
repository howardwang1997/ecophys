"""Exp 102 — Thread 1: differentiable multi-fact loss (SPX screen, n=30).

Hypothesis (102-105 plan): the ~5.1/11 ceiling is an *objective-coverage* limit —
the loss optimised only acf_sq / leverage / hill (≈ facts #6/#9/#2), so 8 of 11
facts never entered the gradient. Put the under-covered facts in directly via the
new per-fact surrogates (ecomd/training/fact_surrogates.py), and also sweep the
never-tried smooth distance modes (all 9,219 prior configs used distance_mode=l1).

Matching the *whole return marginal* was already tried (exp 085 Wasserstein) and
lost to baseline — so this is explicit *per-fact*, not marginal-matching.

Grid (14 loss cells + baseline_v3 = 15 cells × 30 seeds = 450 cfg, SPX only):

  distance-mode isolation:   d_mse, d_huber                 (moments only)
  single-fact attribution:   mf_skew, mf_fano, mf_agg, mf_dfa  (l1 + one fact)
  all-fact × distance:       mf_all_l1, mf_all_mse, mf_all_huber
  all-fact weight scale:     mf_all_mse_lo, mf_all_mse_hi
  fact subsets (mse):        mf_skewfano (easy/high-failure), mf_aggdfa (floors)

Decision gate (5-28 review): any cell whose SPX mean beats baseline_v3 →
promote to the 5-asset n=30 confirmation (exp 106) where the significance gate
(Δ>0 vs baseline, Bonferroni p<0.05) is applied. If nothing beats baseline even
on SPX, the loss-bottleneck hypothesis is weakened → lean to diagnose framing.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_PATH = REPO / "experiments" / "099b_memk_refinement_n30" / "config_baseline_v3_seed0.yaml"
OUT = REPO / "experiments" / "102_multifact_loss_n30"
OUT.mkdir(parents=True, exist_ok=True)

N_SEEDS = 30

# Default per-fact weights for the "all-fact" cells.
ALL = {"w_gain_loss": 0.3, "w_agg_gauss": 0.3, "w_fano": 0.3, "w_dfa_hurst": 0.2}

# Each cell = loss_weights overrides merged onto the base (moments/l1) weights.
CELLS: dict[str, dict] = {
    # distance-mode isolation (moments only — does smooth distance alone help?)
    "d_mse": {"distance_mode": "mse"},
    "d_huber": {"distance_mode": "huber"},
    # single-fact attribution (l1 + one surrogate)
    "mf_skew": {"w_gain_loss": 0.5},
    "mf_fano": {"w_fano": 0.5},
    "mf_agg": {"w_agg_gauss": 0.5},
    "mf_dfa": {"w_dfa_hurst": 0.5},
    # all four facts × distance mode
    "mf_all_l1": {**ALL},
    "mf_all_mse": {**ALL, "distance_mode": "mse"},
    "mf_all_huber": {**ALL, "distance_mode": "huber"},
    # all four, weight scale (mse)
    "mf_all_mse_lo": {k: v * 0.5 for k, v in ALL.items()} | {"distance_mode": "mse"},
    "mf_all_mse_hi": {k: v * 2.0 for k, v in ALL.items()} | {"distance_mode": "mse"},
    # fact subsets (mse): the easy/high-failure pair vs the floor facts
    "mf_skewfano": {"w_gain_loss": 0.4, "w_fano": 0.4, "distance_mode": "mse"},
    "mf_aggdfa": {"w_agg_gauss": 0.4, "w_dfa_hurst": 0.4, "distance_mode": "mse"},
}


def main() -> None:
    base = yaml.safe_load(BASE_PATH.read_text())
    assert base["training"].get("target_dataset", "spx") == "spx", "102 is SPX-only screen"

    n = 0
    # baseline_v3 reference (loss_weights untouched — moments/l1)
    for seed in range(N_SEEDS):
        cfg = copy.deepcopy(base)
        cfg["training"]["seed"] = seed
        (OUT / f"config_baseline_v3_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
        n += 1

    for tag, overrides in CELLS.items():
        for seed in range(N_SEEDS):
            cfg = copy.deepcopy(base)
            cfg["training"]["loss_weights"].update(overrides)
            cfg["training"]["seed"] = seed
            (OUT / f"config_{tag}_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1

    print(f"wrote {n} configs ({len(CELLS)} cells + baseline) × {N_SEEDS} seeds to {OUT}")


if __name__ == "__main__":
    main()
