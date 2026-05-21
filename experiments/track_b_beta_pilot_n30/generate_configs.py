"""Track B-β scheduled-sampling pilot at n=30 (Paper A "solve" half).

B-β rationale (paper_a_next_steps_2026-05-21.md §4): during BPTT training,
with curriculum probability p(iter) that ramps from 0 to ``ss_max_prob``
over ``ss_warmup_iters`` outer iters, widen each rollout step's stochastic
force by ``ss_sigma_mult`` (>1). A Bengio-style exposure-bias regularizer
adapted to Langevin dynamics — instead of mixing teacher-forced ground-
truth states (TrajCast-style), we widen the noise channel so the network
learns to recover from larger excursions than the standard diffusion.

The hypothesis: if the v3 Pareto ceiling at 5.5-5.6/11 is caused by an
*exposure-bias* failure mode (the model is fit on chunk=24 trajectories
but evaluated on 4000-step rollouts, accumulating compounding errors B-β
should regularize), then aggressive ss should lift the ceiling.

Pilot grid (Paper A explore-then-commit; full sweep is 540 cfg, this pilot
covers the most informative 2D slice at n=30):

    ss_max_prob ∈ {0.10, 0.15, 0.20, 0.25, 0.30, 0.40}    (6 values)
    ss_sigma_mult ∈ {1.25, 1.50, 1.75, 2.00, 2.50}        (5 values)

Other hyperparams fixed for pilot:
    ss_ramp_schedule = "linear"
    ss_warmup_iters = 32  (~ 1/6 of n_iters=200; reaches plateau by iter 32)

Plus baseline_v3 reference (ss off, identical otherwise).

30 cells + 1 baseline = 31 cells × 30 seeds = 930 configs ≈ 19.4h on 8-card H20.

Decision gates (Paper A §5.1 contribution criteria):
- IF best cell n=30 mean ≥ 5.5 AND 95% CI lower ≥ 5.2 → B-β confirmed, fund
  full 540-cfg sweep (vary ss_warmup_iters + ramp schedule next).
- IF best < 5.2 → B-β doesn't move the ceiling; demote to "explored,
  null result" in §5 footnote.
- IF 5.2 ≤ best < 5.5 → suggestive; consider extending grid (lower
  max_prob, longer warmup) before committing to full sweep.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_PATH = REPO / "experiments" / "099b_memk_refinement_n30" / "config_baseline_v3_seed0.yaml"
OUT = REPO / "experiments" / "track_b_beta_pilot_n30"
OUT.mkdir(parents=True, exist_ok=True)


SS_MAX_PROB = [0.10, 0.15, 0.20, 0.25, 0.30, 0.40]
SS_SIGMA_MULT = [1.25, 1.50, 1.75, 2.00, 2.50]
SS_RAMP = "linear"
SS_WARMUP = 32

N_SEEDS = 30


def _apply_bbeta(cfg: dict, max_prob: float, sigma_mult: float) -> None:
    sim = cfg["simulator"]
    sim["scheduled_sampling_enabled"] = True
    sim["ss_max_prob"] = float(max_prob)
    sim["ss_sigma_mult"] = float(sigma_mult)
    sim["ss_ramp_schedule"] = SS_RAMP
    sim["ss_warmup_iters"] = int(SS_WARMUP)


def _cell_tag(max_prob: float, sigma_mult: float) -> str:
    # encode as p015_s175 (max_prob*100, sigma_mult*100) for filename stability
    return f"bb_p{int(round(max_prob*100)):03d}_s{int(round(sigma_mult*100)):03d}"


def main() -> None:
    base = yaml.safe_load(BASE_PATH.read_text())
    n = 0
    for mp in SS_MAX_PROB:
        for sm in SS_SIGMA_MULT:
            tag = _cell_tag(mp, sm)
            for seed in range(N_SEEDS):
                cfg = copy.deepcopy(base)
                _apply_bbeta(cfg, mp, sm)
                cfg["training"]["seed"] = seed
                out_path = OUT / f"config_{tag}_seed{seed}.yaml"
                out_path.write_text(yaml.safe_dump(cfg))
                n += 1
    # baseline reference (ss off — sanity check the chunk's grid)
    for seed in range(N_SEEDS):
        cfg = copy.deepcopy(base)
        # explicit-off so the config records the absence of B-β
        cfg["simulator"]["scheduled_sampling_enabled"] = False
        cfg["training"]["seed"] = seed
        (OUT / f"config_baseline_v3_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
        n += 1

    print(f"wrote {n} configs ({len(SS_MAX_PROB)}×{len(SS_SIGMA_MULT)} = "
          f"{len(SS_MAX_PROB)*len(SS_SIGMA_MULT)} grid + 1 baseline × {N_SEEDS} seeds) to {OUT}")


if __name__ == "__main__":
    main()
