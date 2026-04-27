# Loss Redesign Ablation — Scoreboard

**Date**: 2026-04-27 (partial run on H20)
**Note**: All configs were fixed to chunk24_K0 due to BPTT OOM (see Phase 6 report).
Phase 1 training partially completed (24/45); no eval was run before batch was killed.
Phases 2/4/5 not started.

## Baseline references (for §5 paper table)

- GARCH(1,1)-t fitted (per-asset, deterministic): see `experiments/002_garch_baseline/results/three_way_comparison.md`. Approximately **5-7/11** under strict bands.
- LM99 ABM (asset-agnostic): **5/11** under strict bands.
- Shi 2024 Neural Hawkes: TODO if Phase C implementation lands.

## Phase 6 HBM Profile

See `experiments/028_hbm_profile/report.md`. Result: **BPTT checkpointing failed**
for EcoMD (nested `autograd.grad` prevents memory savings). Only chunk24_K0 at
N=10K fits single H20 (79.6 GB / 98 GB).

## Phase 1 — Training partial (24/45)

All completed configs converge to same loss (expected — chunk24 fix collapsed
the ch/bal/dm axes). Only lf (loss family) and te (tail estimator) axes carry
meaningful variation; those configs did not finish training.

| Group | Configs | Trained | Eval'd | Notes |
|---|---|---|---|---|
| bal (fixed/invvar × 3) | 6 | 6/6 | 0/6 | identical to baseline after chunk24 fix |
| ch (chunk24/64/128 × 3) | 9 | 9/9 | 0/9 | all collapsed to chunk24 after fix |
| dm (huber/l1/mse × 3) | 9 | 9/9 | 0/9 | identical to baseline after chunk24 fix |
| lf (l1_legacy/mse/huber × 3) | 12 | 0/12 | — | killed mid-training |
| te (softhill/quantile/kurtosis × 3) | 9 | 0/9 | — | not started |

Training time: ~110s per config (200 iters, N=10K, single H20).
Peak HBM: 79.6 GB per config.

## Phases 2, 4, 5 — Not started

- Phase 2 (45 configs): 3 winners × 3 architectures × 5 seeds
- Phase 4 (10 configs): N=20K/50K × 5 seeds — **blocked by OOM at N>10K**
- Phase 5 (9 configs): multi-asset universality — immediately runnable

