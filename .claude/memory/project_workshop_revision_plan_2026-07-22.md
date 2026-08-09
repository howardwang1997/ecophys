---
name: project_workshop_revision_plan_2026-07-22
description: Frozen execution plan for retargeting and revising the two 2026 workshop papers, including P0/P1 experiments, compute, data, and claim gates
metadata:
  type: project
---

The executable source of truth is `papers/proposal/workshop_revision_plan_2026-07-22.md`.

## Paper split

- STODY (4 pages): driven stochastic dynamics only — shock-channel contrast, finite relaxation,
  saturating dip-amplitude law, and the trained-Lévy steady-tail experiment. Do not headline
  warm-up methodology, real-crash stationarity, or `tau(dose)`.
- Sim2Science (5 pages): stationarity-aware evaluation only — fixed-length warm-up audit,
  calibration/held-out stationarity gate, scoring/ranking sensitivity, `sv_d3_both` transfer, and
  GARCH-t initialization controls. No shock atlas, dose law, OFI, or real-crash figure.
- Ask both organizers about related submissions. If the final papers share a core result/figure or
  related submissions are disallowed, submit only the stronger paper.

## P0 experiment order

1. W0 raw-ED/provenance gate: preserve original training configs, use eval-only raw-ED logging,
   require `ed_is_raw==1`, prove logging is return-bitwise-invariant, and make no-shock reports use
   `shock_step=null` plus the full `[500,T)` steady interval. The current baseline is post-impact and
   the current no-shock scorer arbitrarily truncates at 3000, so every W1 arm including baseline must
   be rescored.
2. W1 score all 12 trained Lévy checkpoints (alpha 1.9/1.7/1.5/1.3 x 3 seeds; 32 rollouts each).
   Treat checkpoint seed, not rollout, as the training-method statistical unit.
3. W2 audit recovery estimators on existing control/kick6 trajectories. Report finite recovery and
   estimator sensitivity; do not attempt to rescue a dose-dependent tau law.
4. W3 run fixed-length stationarity-aware scoring on 5 concave checkpoints plus SPX/BTC baseline
   checkpoints, 32 rollouts each, calibration/held-out split.
5. W4 run preselected `sv_d3_both` seeds 0/1/2 plus independent CPU GARCH-t long-burn and cold-start
   controls. The neural-SDE leg is an architecture variant, not an independent codebase.

W5 (`sigma_price=0`, fixed-SNR, and price-component logging across N) is conditional: run only if a
causal self-averaging sentence is still needed. Otherwise omit the mechanism claim. Paid L2 data is
explicitly outside the workshop critical path.

## Resource decision

- Normal path: reserve one continuous 12h window on 8x96GB H20, including at least 6h for scoring,
  integrity checks, retries, and packaging. Estimated active compute is 35–50 GPU-hours. This is the
  fastest schedule, not a hardware requirement.
- Missing-checkpoint path: reserve 18h for retraining plus evaluation.
- Fewer H20s are scientifically equivalent when total rollouts and an explicit seed manifest are held
  fixed: book about 48h on 1xH20, 24–30h on 2xH20, or 14–18h on 4xH20 for the normal P0 path.
- Current custom-autograd P0 training is measured at 14.19 GiB allocated / 14.85 GiB reserved, so
  A100 40/80GB and V100 32GB have sufficient HBM for both inference and retraining. V100 16GB is too
  close to the measured peak for production retraining. Benchmark a full T=8000 rollout and a
  10-iteration train probe before budgeting non-H20 wall time; verify sm_70 support before V100 use.
- Do not mix GPU generations inside one torchrun job. Run separate single-GPU workers and record GPU,
  CUDA, and PyTorch in the manifest. Cross-architecture trajectories need statistical-tolerance, not
  bitwise, equivalence; W0's logging A/B must stay on one identical hardware/software stack.
- `run_large` derives seeds from rank, so changing NPROC changes the seed set unless the 32 seeds are
  explicitly manifested or the original rank seed blocks are queued serially.
- W5, if authorized by the schedule gate, gets a separate 8xH20 6h window.
- CPU analysis: Mac/H20-4, 8–16 cores, 16–32GB RAM; GPFS/H20 scratch allocation at least 200GB.
- No new paid market data is required. Daily yfinance snapshots are needed only if checkpoints must
  be retrained, and must match the original snapshot/hash.

Internal experiment/text freeze is 2026-08-24; target internal submission is 2026-08-27 ahead of the
2026-08-29 AoE deadlines.
