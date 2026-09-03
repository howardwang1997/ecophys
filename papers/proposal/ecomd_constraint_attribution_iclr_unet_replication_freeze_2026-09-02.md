# ICLR second-architecture replication freeze

Frozen before any U-Net training record exists on 2026-09-02.

## Question

Does the coordinate-by-training-by-inference path dependence found with FNO persist in a fully
convolutional U-Net on the same public PDEBench Advection task? This is an architecture replication,
not a hyperparameter search or an attempt to rescue an unfavorable result.

## Fixed design

- Public data, byte/hash lock, train/test split, conservative restriction, history, temporal stride,
  training resolution, OOD resolutions, rollout horizons, optimizer, epochs, learning rate, batch
  size, and four training arms are identical to the frozen FNO factorial.
- The only scientific change is the model body: a two-level 1D U-Net with base channels 20,
  kernel size 5, GroupNorm, SiLU, average-pooling downsampling, transposed-convolution upsampling,
  skip connections, and a one-channel head. Spatial coordinates are concatenated to the ten input
  history channels. No capacity or optimizer alternative will be tried.
- Fresh paired seeds are exactly 7000--7029. Within each seed, all four arms share the sampled
  trajectories, minibatch order, windows, and initialized tensor. Seed 6999 is an excluded
  execution-only preflight and can never enter analysis.
- Core output is exactly 150 records: four trained arms plus the zero-training projection control
  for every seed. After a complete one-shot core analysis, 120 checkpoints are hash-locked and the
  same three zero-training inference toggles produce exactly 90 cube records.
- V100-A receives seeds 7000--7014 and V100-B seeds 7015--7029. Every arm for a seed stays on one
  host. No third GPU, seed reassignment, early analysis, or result-driven stop is allowed.

## Frozen estimands and admission rule

The primary cell remains OOD-512 at horizon 16. The estimand is the same three-way interaction
`J`, with the same paired bootstrap, 10% SESOI, ordered classification, 12 mandatory
resolution--horizon cells, and Holm correction as the FNO cube.

The replication may strengthen the main claim only if the primary cell is materially non-additive
and at least 6 of 12 mandatory cells are material. A resolved architecture boundary may be reported
only when the frozen classifications themselves establish it; a null or mixed result cannot be
renamed robustness. All other complete outcomes remain auditable appendix evidence. The grid,
threshold, seeds, architecture, and stopping rule cannot change after activation.

## Runtime and integrity

The excluded seed-6999 probe must pass CUDA execution, finite loss, shape, exact arm initialization
parity, hard-arm mass conservation, and checkpoint resume. Formal metrics remain unread until both
workers exit and exact 75+75 record coverage is verified. Runtime failures may be resumed only from
their own fixed checkpoints. There is no wall-clock limit.
