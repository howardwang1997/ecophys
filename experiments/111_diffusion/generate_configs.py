"""Exp 111 — A3 conditional diffusion entrant (Bracket-1 solve + Bracket-2 generative leg).

Deep-generative paradigm: a conditional autoregressive DDPM
(ecomd/baselines/score_diffusion.py) trained on real SPX returns. Mac smoke showed
the OPPOSITE failure mode from EcoMD — finite tails (hill≈5, no α<2 overshoot) and
DFA in-band, but UNDERshoots vol-clustering (acf²/agg too Gaussian). That contrast
is the three-paradigm Pareto-ceiling story.

Runs via scripts/run_baseline_fit_eval.py (NOT torchrun) — fit once on real returns,
sample n_rollouts series, score with compute_all. One config = one seed.

Cells (2 × 30 seeds = 60 cfg, SPX daily):
  diffusion_cond   conditional=True   (context window → shot at dynamics facts)
  diffusion_marg   conditional=False  (pure marginal ablation: aces tails, kills dynamics)
"""

from __future__ import annotations

from pathlib import Path

import yaml

OUT = Path(__file__).resolve().parent
N_SEEDS = 30

# model_kwargs per cell (conditional flag is the ablation axis)
CELLS = {
    "diffusion_cond": {"context": 64, "hidden": 128, "n_diffusion_steps": 50, "conditional": True},
    "diffusion_marg": {"context": 64, "hidden": 128, "n_diffusion_steps": 50, "conditional": False},
}
FIT_KWARGS = {"n_epochs": 300, "batch_size": 256, "lr": 3e-4}


def main() -> None:
    n = 0
    for tag, mk in CELLS.items():
        for seed in range(N_SEEDS):
            cfg = {
                "baseline": {
                    "model": "score_diffusion",
                    "asset": "spx",
                    "period": "daily",
                    "n_rollouts": 4,
                    "n_steps_per_rollout": 4000,
                    "fit_kwargs": dict(FIT_KWARGS),
                    "model_kwargs": dict(mk),
                },
                "simulator": {},
                "training": {"seed": seed},
            }
            (OUT / f"config_{tag}_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1
    print(f"wrote {n} configs ({len(CELLS)} cells × {N_SEEDS} seeds) to {OUT}")
    print("  model=score_diffusion asset=spx/daily  cells:", ", ".join(CELLS))


if __name__ == "__main__":
    main()
