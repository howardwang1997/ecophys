"""090 — patch composition (post-089 hero-cell hunt).

After 089 landed (2026-05-15), the safest patch seed is `zumbach_dn_s10`
(mean 5.12, no fact dropped ≥-13pp vs baseline). The biggest fact-mover
is `ar1_s05` (zumbach +37pp, hill +57pp, acf² +31pp) but it breaks ckur
-47pp. Branch F's best pair was asymdrag + B3 (`pair_AB`, mean 5.18 at
n=28). 090 composes these along the most promising axes to find the
first hero cell at mean ≥ 5.5.

Cells (8 total, 240 cfg ≈ ~3.5h H20):

  Patch × existing best singles:
    pair_zumdn_b3         — Zumbach `dn` + B3 k=3
    pair_zumdn_asym       — Zumbach `dn` + asymdrag α=0.6
    pair_ar1_b3           — AR(1) s05 + B3 k=3
    pair_ar1_asym         — AR(1) s05 + asymdrag α=0.6

  Two-patches composition:
    pair_zumdn_ar1        — Zumbach `dn` + AR(1) s05 (the two new mechs)

  Depth-3 stress test (Branch F said depth ≥3 interferes; verify with patches):
    triple_zumdn_ar1_b3   — Zumbach `dn` + AR(1) s05 + B3 k=3

  Replication / sanity:
    pair_AB_reref         — Branch F pair_AB (asymdrag + B3) on neurips branch
    zumdn_solo_n30        — Zumbach `dn` solo at n=30 (Branch F-style replication)

Total: 8 cells × 30 seeds = 240 cfg.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_SPX = REPO / "experiments" / "069_gamma_damping_30seed" / "config_T05_g10_seed0.yaml"
OUT = REPO / "experiments" / "090_patch_composition_30seed"
OUT.mkdir(parents=True, exist_ok=True)


def apply_asym(cfg, alpha=0.6):
    cfg["simulator"]["asym_drag_alpha"] = alpha


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
    # ── Patch × existing best singles ──────────────────────────────────
    ("pair_zumdn_b3",       30, [(apply_zumbach,     {"lam": 0.95, "strength": 1.0, "mode": "downside"}),
                                  (apply_b3,          {"k": 3, "tau": 1.0})]),
    ("pair_zumdn_asym",     30, [(apply_zumbach,     {"lam": 0.95, "strength": 1.0, "mode": "downside"}),
                                  (apply_asym,        {"alpha": 0.6})]),
    ("pair_ar1_b3",         30, [(apply_ar1_whiten,  {"lam": 0.9, "strength": 0.5}),
                                  (apply_b3,          {"k": 3, "tau": 1.0})]),
    ("pair_ar1_asym",       30, [(apply_ar1_whiten,  {"lam": 0.9, "strength": 0.5}),
                                  (apply_asym,        {"alpha": 0.6})]),
    # ── Two-patches composition ────────────────────────────────────────
    ("pair_zumdn_ar1",      30, [(apply_zumbach,     {"lam": 0.95, "strength": 1.0, "mode": "downside"}),
                                  (apply_ar1_whiten,  {"lam": 0.9, "strength": 0.5})]),
    # ── Depth-3 stress test ────────────────────────────────────────────
    ("triple_zumdn_ar1_b3", 30, [(apply_zumbach,     {"lam": 0.95, "strength": 1.0, "mode": "downside"}),
                                  (apply_ar1_whiten,  {"lam": 0.9, "strength": 0.5}),
                                  (apply_b3,          {"k": 3, "tau": 1.0})]),
    # ── Replication / sanity ───────────────────────────────────────────
    ("pair_AB_reref",       30, [(apply_asym,        {"alpha": 0.6}),
                                  (apply_b3,          {"k": 3, "tau": 1.0})]),
    ("zumdn_solo_n30",      30, [(apply_zumbach,     {"lam": 0.95, "strength": 1.0, "mode": "downside"})]),
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
            (OUT / f"config_{tag}_seed{s}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1
    n_cells = len(CELLS)
    print(f"wrote {n} configs across {n_cells} cells to {OUT}")


if __name__ == "__main__":
    main()
