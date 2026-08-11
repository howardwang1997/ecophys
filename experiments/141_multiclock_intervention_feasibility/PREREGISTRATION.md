# Experiment 141 — multi-clock intervention feasibility preregistration

**Status:** frozen before implementation and before any formal seed is generated.

**Purpose:** determine whether the proposed event/behavior/institution clock separation is identifiable in a
controlled setting and executable on the three current non-H20 workers. A PASS is not real-market evidence.

## Frozen inputs

The sole scientific configuration is
`configs/market_world/intervention_feasibility_v1.yaml`. Formal generated data use no market files.

- Development magnitudes: `0.5, 1.0, 1.5`; 16 seeds beginning at 100.
- Held-out magnitudes: `0.75, 2.0`; 30 seeds beginning at 10,000.
- Truth families: no adaptation, single-rate adaptation, two-rate misspecification and an unmodeled short
  confounding shock.
- Event clock: 256 events per behavioral epoch.
- Intervention: tick size changes from one to two integer price units after 16 pre epochs. Existing off-grid
  resting orders are cancelled deterministically. The normalized magnitude controls the slow behavioral target;
  it does not rewrite the matching algorithm.
- Each path has 16 pre and 24 post epochs.

## Models

1. `frozen`: pre-intervention behavior never updates.
2. `instant`: behavior jumps immediately to the fitted intervention target.
3. `multiclock`: one fitted bounded relaxation rate updates behavior once per epoch.

All models use the same exact exchange kernel and paired random seeds. Development observations fit parameters;
no held-out epoch contributes to fitting, threshold selection or model selection. The single-rate candidate is
deliberately misspecified for the two-rate truth.

## Primary estimand

For each seed and held-out magnitude, form the post-intervention effect vector relative to a paired no-intervention
path. Its primary components are market-order fraction and cancellation fraction in early, middle and late post
windows. Spread, top depth, volume and fee revenue are secondary diagnostics.

The primary error is the equally weighted standardized RMSE of the effect vector, with development-period standard
deviations frozen before held-out merging. Improvement is `1 - RMSE_multiclock / RMSE_baseline`.

## Hard gates

1. Every event path has zero price--time, tick, crossed-book, nonpositive-depth, cash-conservation or
   inventory-conservation violation.
2. For single-rate truth, multiclock improves on frozen by at least 25%, and the seed-bootstrap 95% lower bound is
   above 10%. It must also improve on instant by at least 10% descriptively.
3. For two-rate truth, multiclock improves on frozen by at least 10%, with bootstrap lower bound above zero.
4. Under no adaptation, multiclock may not degrade RMSE by more than 5% relative to frozen.
5. A residual detector frozen at absolute `z > 3` detects at least 90% of confounded paths while false-positive
   rate on single-rate paths is at most 10%. Confounded paths do not enter the positive model comparison.
6. All three machine shards have exact Git/config/protocol ownership and reproduce the shared CPU anchor hash.
7. All three CUDA probes have finite losses and gradients, exact same-device split/resume continuation, and peak
   reserved memory below 70% of physical memory. Final-loss relative spread across devices is at most `1e-3`.

Gates 1--6 define F1/F2. Gate 7 defines F3. Overall PASS requires all seven. Failure is preserved; any repair gets a
new experiment number and fresh seeds.

## Sharding and independence

Each machine receives every truth/magnitude arm but only evaluation seed indices matching one residue modulo three.
A shared anchor is repeated on all machines and excluded from inference. Development fitting and formal merging run
once from a clean committed implementation. Shards may not read one another.

## Stop boundary

A PASS authorizes only R0 intervention selection and, after a separate preregistration, a small real-data pilot. It
does not authorize paid bulk data, a positive EcoMD claim, an NMI/NCS manuscript claim or a large GPU sweep.
