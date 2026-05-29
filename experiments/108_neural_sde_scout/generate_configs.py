"""Exp 108 — neural-SDE stochastic-vol SCOUT (Slot 1, 5-6h H20).

The tournament's hero entrant (learned multi-timescale stochastic volatility,
ecomd/models/stoch_vol.py) gets its first GPU-scale test here. We validate at
SPX n=12 whether the SV head lifts the volatility-structure floors (fat tails #2,
agg-gaussianity #4, Fano #5, DFA #8) that the ~5.1 paradigm ceiling is made of.

Base = the 104 hybrid+MMD cell (mmd_w50): the now-wired distribution objective is
the right partner for an expressive vol process. N=10K fp32 (NOT 107's unstable
N=2000+bf16). rollout_reg_every=8 trims the scout to ~5h (the weekend uses every=4).

Cells (5 × 12 seeds = 60 cfg), deconfounded for mechanism attribution:
  baseline_mmd   no SV (= 104 hybrid+MMD)                    -> anchor
  sv_d1          SV price, K=1 timescale, leverage on        -> ablates multi-scale
  sv_d3          SV price, K=3 timescales, leverage on       -> the hero
  sv_d3_nolev    SV price, K=3, leverage OFF                 -> ablates leverage (#9/#11)
  sv_d3_both     SV price + integrator placement, K=3, lev on -> + Langevin-level (Paper B)

Attribution: (sv_d3 - sv_d1) = multi-timescale effect (DFA #8 / agg-gauss #4);
(sv_d3 - sv_d3_nolev) = leverage coupling; (sv_d3_both - sv_d3) = integrator placement.

PRE-REGISTERED SCOUT GATE (binds the weekend tournament): a cell advances iff at
n=12 it lifts >=1 hard floor (#2/#4/#5/#8) WITHOUT >=20pp collateral on an in-band
fact, AND mean n/11 >= baseline_mmd. Non-clearing cells are dropped (documented).
See papers/proposal/plan_v3_addendum_2026-05-28.md and the plan file.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_PATH = REPO / "experiments" / "104_mmd_longroll_n30" / "config_mmd_w50_longroll_seed0.yaml"
OUT = REPO / "experiments" / "108_neural_sde_scout"
OUT.mkdir(parents=True, exist_ok=True)

N_SEEDS = 12
REG_EVERY = 8  # scout trim (~5h); weekend uses 4

# SV price-head kwargs merged into price_formation_kwargs. Base (off) = {}.
def sv_kw(d: int, leverage: bool) -> dict:
    return {
        "sv_price_enabled": True,
        "sv_d": d,
        "sv_leverage": leverage,
        "sv_state_dep": False,
        "sv_v_clip": 3.0,
        "sv_gain_init": 0.5,
    }

# cell -> (price_formation sv kwargs, sv_integrator_enabled)
CELLS: dict[str, tuple[dict, bool]] = {
    "baseline_mmd": ({}, False),
    "sv_d1":        (sv_kw(1, True), False),
    "sv_d3":        (sv_kw(3, True), False),
    "sv_d3_nolev":  (sv_kw(3, False), False),
    "sv_d3_both":   (sv_kw(3, True), True),
}


def main() -> None:
    base = yaml.safe_load(BASE_PATH.read_text())
    assert base["training"].get("target_dataset", "spx") == "spx", "108 is SPX-only scout"

    n = 0
    for tag, (sv_over, integ) in CELLS.items():
        for seed in range(N_SEEDS):
            cfg = copy.deepcopy(base)
            cfg["training"]["seed"] = seed
            cfg["training"]["rollout_reg_every"] = REG_EVERY
            # merge SV kwargs into price_formation_kwargs
            pfk = dict(cfg["simulator"].get("price_formation_kwargs", {}))
            pfk.update(sv_over)
            cfg["simulator"]["price_formation_kwargs"] = pfk
            cfg["simulator"]["sv_integrator_enabled"] = integ
            (OUT / f"config_{tag}_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1

    print(f"wrote {n} configs ({len(CELLS)} cells × {N_SEEDS} seeds) to {OUT}")
    print(f"  base={BASE_PATH.name}  reg_every={REG_EVERY}  N={base['simulator']['n_agents']} "
          f"{base['training']['mixed_precision']}")
    print("  cells:", ", ".join(CELLS))


if __name__ == "__main__":
    main()
