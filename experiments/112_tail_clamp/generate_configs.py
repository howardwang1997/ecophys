"""Exp 112 — tail-clamp probe (the ONE untested mechanistic lever).

Context (2026-06-01, verified): the broad weekend tournament closed the "solve"
arc with no winner. The decisive finding (exp 109): the fat-tail OVERSHOOT
(hill<2, infinite-variance) is DYNAMICAL not distributional — Gaussian noise +
zero jumps still gives hill=1.30. No noise/mixture/objective knob fixes it.

This experiment tests the single remaining mechanistic lever before committing to
the diagnose-centered Paper A: a soft, differentiable saturating clamp on the
realized per-step log-return (price_formation.py, tail_clamp_c/tail_clamp_mode):
    r_clamped = scale · tanh(r / scale)
- "rel": scale = c · running_volatility → caps moves at ±c running-sigmas. This
  is the version with a REAL CHANCE to enter hill∈[2,4] while preserving acf2,
  because it bounds the UNCONDITIONAL tail in vol-relative units (clustering is a
  vol-persistence property, not an absolute-magnitude one).
- "abs": scale = c absolute → the Pareto-blocked reference (should kill acf2).

PRE-REGISTERED GATE (binds the Paper-A framing decision):
  A clamp cell is a genuine SOLVE iff, vs `baseline` (n=20, Welch + Bonferroni):
    (1) hill_tail_index enters [2,4] (mean in-band), AND
    (2) acf_squared_returns stays in band (clustering NOT killed, no >20pp drop).
  i.e. it must BREAK the tail⊥dynamics Pareto coupling. If NO cell does both →
  the coupling is confirmed mechanistically → commit to the 3-paradigm diagnose
  (clamp cells become the final negative control). No best-of-N; winner (if any)
  → 5-asset n=30 the following weekend.

Built on the 108 baseline_mmd sim cfg (N=10K fp32, hybrid+MMD long-rollout,
custom-fn BPTT), rollout_reg_every=4 (matches the weekend budget).

Cells (5 × 20 seeds = 100 cfg, SPX, ~5-6h slot):
  baseline       no clamp (c=0)                  -> control
  tclamp_rel_c8  rel clamp at 8 running-sigmas   -> gentlest; least collateral
  tclamp_rel_c5  rel clamp at 5 running-sigmas   -> the primary bet
  tclamp_rel_c3  rel clamp at 3 running-sigmas   -> aggressive; max tail-pull
  tclamp_abs     abs clamp (Pareto-blocked ref)  -> predicted to kill clustering
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_PATH = REPO / "experiments" / "108_neural_sde_scout" / "config_baseline_mmd_seed0.yaml"
OUT = REPO / "experiments" / "112_tail_clamp"
OUT.mkdir(parents=True, exist_ok=True)

N_SEEDS = 20
REG_EVERY = 4

# cell -> (tail_clamp_c, tail_clamp_mode); c<=0 = OFF (bit-exact baseline)
CELLS: dict[str, tuple[float, str]] = {
    "baseline":      (0.0, "rel"),
    "tclamp_rel_c8": (8.0, "rel"),
    "tclamp_rel_c5": (5.0, "rel"),
    "tclamp_rel_c3": (3.0, "rel"),
    "tclamp_abs":    (0.04, "abs"),  # ~8× sigma_price(0.005); fixed absolute cap
}


def main() -> None:
    base = yaml.safe_load(BASE_PATH.read_text())
    assert base["training"].get("target_dataset", "spx") == "spx", "112 is SPX-only"

    n = 0
    for tag, (c, mode) in CELLS.items():
        for seed in range(N_SEEDS):
            cfg = copy.deepcopy(base)
            cfg["training"]["seed"] = seed
            cfg["training"]["rollout_reg_every"] = REG_EVERY
            pfk = cfg["simulator"]["price_formation_kwargs"]
            pfk["tail_clamp_c"] = c
            pfk["tail_clamp_mode"] = mode
            (OUT / f"config_{tag}_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1

    print(f"wrote {n} configs ({len(CELLS)} cells × {N_SEEDS} seeds) to {OUT}")
    print(f"  N={base['simulator']['n_agents']} {base['training']['mixed_precision']} "
          f"reg_every={REG_EVERY}  cells:", ", ".join(CELLS))


if __name__ == "__main__":
    main()
