"""094 — VaR holdout training (clean train-test split for M1.4 VaR backtest).

The 089 attribution batch trains on SPX 2015-2026_daily. Running
`var_backtest` on 2018-2026 with those checkpoints leaks information
(8 years of overlap). 094 retrains the 8 best post-089 cells on SPX
2010-2017 only; downstream VaR backtest on 2018-2026 is then a clean
out-of-sample test.

Cells (8 best post-089 × 12 seeds = 96 cfg, ~1.5h H20):

  Reference:
    var_baseline_v3              — v3 control, retrained on 2010-2017

  V4 + B-round best singles:
    var_zumdn_s10                — Zumbach `dn` solo (best single in 089)
    var_b3_k3                    — B3 k=3
    var_asymdrag_a06             — asymdrag α=0.6
    var_ar1_s05                  — AR(1) s05 (massive fact-trader)
    var_powerlaw_a15             — power-law α=1.5

  Patch pairs from 090:
    var_pair_zumdn_b3            — Zumbach `dn` + B3
    var_pair_zumdn_asym          — Zumbach `dn` + asymdrag

Total: 8 cells × 12 seeds = 96 cfg.

Downstream (Mac-side, post-batch): for each cell, load checkpoint as
EcoMDSampler, then `python -m ecomd.risk.var_backtest --asset spx
--period 2018-2026 --checkpoint <path>` → Kupiec/Christoffersen + per-cell
violation table.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_SPX = REPO / "experiments" / "069_gamma_damping_30seed" / "config_T05_g10_seed0.yaml"
OUT = REPO / "experiments" / "094_var_holdout_12seed"
OUT.mkdir(parents=True, exist_ok=True)

HOLDOUT_PERIOD = "2010-2017_daily"


def apply_asym(cfg, alpha=0.6):
    cfg["simulator"]["asym_drag_alpha"] = alpha


def apply_powerlaw(cfg, alpha=1.5, w_pow=0.5, w_mlp=1.0):
    cfg["simulator"]["power_law_external"] = True
    cfg["simulator"]["power_law_alpha"] = alpha
    cfg["simulator"]["power_law_w_pow"] = w_pow
    cfg["simulator"]["power_law_w_mlp"] = w_mlp


def apply_b3(cfg, k=3, tau=1.0):
    cfg["simulator"]["regime_enabled"] = True
    cfg["simulator"]["regime_discrete_enabled"] = True
    cfg["simulator"]["regime_n_states"] = k
    cfg["simulator"]["regime_gumbel_tau"] = tau


def apply_ar1_whiten(cfg, lam=0.9, strength=0.5):
    cfg["simulator"]["ar1_whiten_lambda"] = lam
    cfg["simulator"]["ar1_whiten_strength"] = strength


def apply_zumbach(cfg, lam=0.95, strength=1.0, mode="downside"):
    cfg["simulator"]["zumbach_feedback_lambda"] = lam
    cfg["simulator"]["zumbach_feedback_strength"] = strength
    cfg["simulator"]["zumbach_feedback_mode"] = mode


CELLS = [
    ("var_baseline_v3",       12, []),
    ("var_zumdn_s10",         12, [(apply_zumbach,    {"lam": 0.95, "strength": 1.0, "mode": "downside"})]),
    ("var_b3_k3",             12, [(apply_b3,         {"k": 3, "tau": 1.0})]),
    ("var_asymdrag_a06",      12, [(apply_asym,       {"alpha": 0.6})]),
    ("var_ar1_s05",           12, [(apply_ar1_whiten, {"lam": 0.9, "strength": 0.5})]),
    ("var_powerlaw_a15",      12, [(apply_powerlaw,   {"alpha": 1.5})]),
    ("var_pair_zumdn_b3",     12, [(apply_zumbach,    {"lam": 0.95, "strength": 1.0, "mode": "downside"}),
                                    (apply_b3,         {"k": 3, "tau": 1.0})]),
    ("var_pair_zumdn_asym",   12, [(apply_zumbach,    {"lam": 0.95, "strength": 1.0, "mode": "downside"}),
                                    (apply_asym,       {"alpha": 0.6})]),
]


def main() -> None:
    base_spx = yaml.safe_load(BASE_SPX.read_text())
    n = 0
    for tag, n_seeds, mods in CELLS:
        for s in range(n_seeds):
            cfg = copy.deepcopy(base_spx)
            for fn, kwargs in mods:
                fn(cfg, **kwargs)
            cfg["training"]["seed"] = s
            cfg["training"]["target_period"] = HOLDOUT_PERIOD
            (OUT / f"config_{tag}_seed{s}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1
    print(f"wrote {n} configs across {len(CELLS)} cells to {OUT} (period={HOLDOUT_PERIOD})")


if __name__ == "__main__":
    main()
