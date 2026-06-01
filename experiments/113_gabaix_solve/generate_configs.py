"""Exp 113 — concave-impact mechanism solve (the best-result swing, refocused).

The tournament closed the solve arc by attacking the loss/noise/paradigm layer, never the
tail-setting mechanism. Two findings reframed the swing (see logs/2026-06-01 S5/S5b):
  (1) our baseline OVERSHOOTS the tail (hill≈1.4 @N=10K, α<2) — synchronization dynamics
      OVER-produce heavy tails. So we must THIN to α≈3, not add heaviness.
  (2) heterogeneous agent masses (the GGPS "size" half) MISFIRED twice (fixed Pareto weights
      → one whale dominates → the time tail tracks the innovation, not the size dist) AND are
      conceptually wrong here (we have excess tail, not a deficit). Dropped.

So 113 is a clean CONCAVE (square-root) PRICE-IMPACT solve (Tóth-Lillo-Bouchaud): replace the
linear β·ED with β·sign(ED)·s·(|ED|/s)^δ, δ∈(0,1). Concavity compresses the synchronized bursts
→ thins the overshoot toward α≈3, and — unlike the tail-clamp — KEEPS clustering (smoke: acf2
0.43→0.36 vs the clamp which killed it) because it reshapes the order-flow DRIVER, not the
realized return. δ is the control: smaller δ = more compression = thinner tail.

The loss already carries soft_hill (w_hill); δ joins sim.parameters() so the learnable cell
calibrates itself. Built on 108 baseline_mmd (N=10K fp32, hybrid+MMD long-rollout, custom-fn BPTT).

Cells (6 × 30 seeds = 180 cfg, SPX, N=10K fp32, MMD long-rollout every=4):
  baseline       impact OFF (linear)              -> control (≈ overshoot, hill≈1.4)
  concave_d040   δ=0.40 fixed                     -> aggressive compression  ┐
  concave_d050   δ=0.50 fixed (sqrt law, TLB)     -> the canonical sqrt-impact├ hill(δ) curve:
  concave_d060   δ=0.60 fixed                     -> mild                     │ where does α
  concave_d070   δ=0.70 fixed                     -> mildest                  ┘ land in [2,4]?
  concave_learn  δ learnable (init 0.6, soft_hill-calibrated) -> does the loss FIND α≈3?

Gate: hill∈[2,4] AND acf2∈[.15,.55] vs baseline (Welch+Bonferroni). SOLVE → 5-asset n=30.
(Heterogeneous-masses code remains in price_formation.py, gated OFF — kept for the record, not
exercised here. impact_scale fixed at the default; can be re-centered from exp 112 Part B.)
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_PATH = REPO / "experiments" / "108_neural_sde_scout" / "config_baseline_mmd_seed0.yaml"
OUT = REPO / "experiments" / "113_gabaix_solve"
OUT.mkdir(parents=True, exist_ok=True)

N_SEEDS = 30
REG_EVERY = 4

# cell -> price_formation_kwargs override
def concave(delta: float, learnable: bool) -> dict:
    return {"impact_concave_enabled": True, "impact_delta_init": delta,
            "impact_delta_learnable": learnable}

CELLS: dict[str, dict] = {
    "baseline":      {},
    "concave_d040":  concave(0.40, False),
    "concave_d050":  concave(0.50, False),
    "concave_d060":  concave(0.60, False),
    "concave_d070":  concave(0.70, False),
    "concave_learn": concave(0.60, True),
}


def main() -> None:
    base = yaml.safe_load(BASE_PATH.read_text())
    assert base["training"].get("target_dataset", "spx") == "spx", "113 is SPX-only"

    n = 0
    for tag, pf_over in CELLS.items():
        for seed in range(N_SEEDS):
            cfg = copy.deepcopy(base)
            cfg["training"]["seed"] = seed
            cfg["training"]["rollout_reg_every"] = REG_EVERY
            cfg["simulator"]["price_formation_kwargs"].update(pf_over)
            (OUT / f"config_{tag}_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1

    print(f"wrote {n} configs ({len(CELLS)} cells × {N_SEEDS} seeds) to {OUT}")
    print(f"  N={base['simulator']['n_agents']} {base['training']['mixed_precision']} "
          f"reg_every={REG_EVERY}  cells:", ", ".join(CELLS))


if __name__ == "__main__":
    main()
