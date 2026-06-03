"""Exp 115 — mechanism COMPOSITION: concave √-impact (tails) + stochastic-vol/leverage (dynamics).

Paper A's "beat-SOTA + it's-a-method" double lever. 113/114 established concave impact fixes the
fat-tail OVERSHOOT (hill→≈3) but leaves the DISJOINT dynamics-asymmetry floors untouched (leverage
~7–10%, zumbach ~7%, dfa ~47%). The 108 scout showed the SV head (sv_d3_both) HELPS exactly those
(DFA 33→45%, leverage 33→50%). The two mechanisms attack non-overlapping facts → compose them.

Two wins if it lands:
  (1) net > 5.96 (prior SOTA) ⇒ a real ceiling-break claim, not just a per-fact tail fix.
  (2) two independent mechanisms, each theory-motivated (TLB √-impact + return→vol leverage),
      each lifting its own fact set ⇒ "differentiable mechanistic calibration" is a METHOD, not a
      one-off. (Concave δ→0.5 is recovered against TLB; SV is the pragmatic 2nd. The clean
      theory-recovery 2nd mechanism = exp 117 leverage, stretch.)

Both mechanisms are orthogonal flags in price_formation_kwargs → compose at the config level (no new
code). SV settings = the scout's sv_d3_both (sv_d=3, gain=0.5, leverage=True, price_enabled=True,
state_dep=False, v_clip=3.0). Concave = the 114 champion (δ=0.5 fixed, TLB √-law).

Cells (5 × 30 = 150, SPX, N=10K fp32, MMD long-rollout every=4):
  baseline             control
  concave              tails only (δ=0.5)                       reuse-equivalent of 114 spx d050
  sv_both              dynamics only (sv_d3_both)               isolates the SV leg
  concave_sv_both      THE COMPOSITION (hero)                   tails + dynamics together
  concave_sv_nolev     ablation: composition w/ SV leverage OFF attributes the leverage channel

Gate G1: concave_sv_both net > 5.96 (Welch+Bonferroni vs baseline AND vs SOTA) AND lifts ≥1 of
{leverage, zumbach, dfa} WITHOUT losing the tail (hill stays in [2,4], acf2 in band). SPX first;
the winner goes to 5-asset n=30 confirmation (no best-of-N).
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_PATH = REPO / "experiments" / "108_neural_sde_scout" / "config_baseline_mmd_seed0.yaml"
OUT = REPO / "experiments" / "115_composition"
OUT.mkdir(parents=True, exist_ok=True)

N_SEEDS = 30
REG_EVERY = 4

CONCAVE = {"impact_concave_enabled": True, "impact_delta_init": 0.50,
           "impact_delta_learnable": False}
SV_BOTH = {"sv_price_enabled": True, "sv_d": 3, "sv_gain_init": 0.5, "sv_leverage": True,
           "sv_state_dep": False, "sv_v_clip": 3.0}
SV_NOLEV = {**SV_BOTH, "sv_leverage": False}

CELLS: dict[str, dict] = {
    "baseline":          {},
    "concave":           {**CONCAVE},
    "sv_both":           {**SV_BOTH},
    "concave_sv_both":   {**CONCAVE, **SV_BOTH},
    "concave_sv_nolev":  {**CONCAVE, **SV_NOLEV},
}


def main() -> None:
    base = yaml.safe_load(BASE_PATH.read_text())
    assert base["training"].get("target_dataset", "spx") == "spx", "115 SPX-first"
    n = 0
    for tag, pf_over in CELLS.items():
        for seed in range(N_SEEDS):
            cfg = copy.deepcopy(base)
            cfg["training"]["seed"] = seed
            cfg["training"]["rollout_reg_every"] = REG_EVERY
            cfg["simulator"]["price_formation_kwargs"].update(pf_over)
            (OUT / f"config_{tag}_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1
    print(f"wrote {n} configs ({len(CELLS)} cells × {N_SEEDS}) to {OUT}")
    print(f"  N={base['simulator']['n_agents']} {base['training']['mixed_precision']} "
          f"reg_every={REG_EVERY}  cells:", ", ".join(CELLS))


if __name__ == "__main__":
    main()
