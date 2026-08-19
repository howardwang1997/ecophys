# Experiment 139 — CUDA compute calibration for the free-data feasibility phase

**Frozen:** 2026-08-19, before the scaling cells are run  
**Status:** engineering/compute evidence only; no market-fit or method claim  
**Resources:** 2 × V100 32 GB and 1 × RTX 2060 8 GB; no H20

## Question

What state-complete EcoMD workload fits on the current heterogeneous CUDA fleet, and what wall-time/HBM
budget should be used for later pre-registered experiments? This benchmark reuses the already audited exp128
mechanics probe, including arbitrary-chunk parity, checkpoint resume, train/inference jump parity, live finite
gradients and a finite long rollout.

This is deliberately not WP2 training: no new invariant-measure estimator exists yet, and running the old
objective longer would create compute expenditure without evidence for the main claim. No scientific result
will be inferred from runtime or random-weight trajectories.

## Frozen matrix

- Both V100 nodes independently run `N = {500, 2,000, 5,000, 10,000}` with two fixed seeds per size.
- The RTX 2060 portability pool runs `N = {500, 2,000}` with the same two-seed rule.
- Each cell uses 32 parity steps, 1,024 long-rollout steps, `dt=0.005`, float32 and the exp128 state-complete
  stochastic-pair configuration.
- Heterogeneous GPU types are never combined in one training job. Results are grouped by device.

The two V100 matrices are intentionally duplicated: this measures node-to-node runtime variance and catches
environment drift. The 2060 is a portability scout, not a performance comparator.

## Gates

1. every exp128 mechanics check passes in every cell;
2. no cell raises an OOM or non-finite result;
3. peak reserved HBM stays below 95% of reported device memory;
4. both V100 nodes complete the entire matrix; the 2060 completes its smaller declared matrix;
5. source commit, Python/platform, Torch/CUDA, device name, arguments, wall time and HBM are retained.

A failure changes the supported production size or requires a numerical diagnosis. Thresholds and sizes are
not changed in this version. Passing calibrates compute only and cannot upgrade NCS gate G0, G2, G3 or G4.
