# ICLR public 2D shallow-water conservation replication freeze

Frozen 2026-09-02 NZST after the exact PDEBench compressible-Navier--Stokes file
terminally failed its frozen time-coordinate schema gate, while the fresh Advection factorial was
still incomplete, before any fresh Advection metric was accessed, and before downloading or
inspecting any value from this shallow-water file.

## Scientific purpose and falsifiable hypotheses

The independent replication is PDEBench's two-dimensional radial-dam-break shallow-water task.
It changes the equation family, dimension, boundary condition, geometry, and model class relative
to scalar periodic Advection. Finite-volume flux updates conserve total water mass, a linear
invariant, while physically admissible water depth is nonnegative. This permits two distinct tests:

1. whether the output-coordinate, training-enforcement, and inference-enforcement contributions
   remain separately identifiable for nonlinear 2D rollouts; and
2. whether exact enforcement of one linear invariant trades against the nonlinear admissible set,
   measured by negative predicted water depth.

For one prediction step, subtracting a spatially constant mass error leaves the mean-centered
error exactly unchanged. Therefore any inference-projection effect on mean-centered error at
horizons greater than one must arise through autoregressive state feedback, not an instantaneous
metric artifact. The enforcement cube tests that mechanism. A null, reverse, or harmful result is
a boundary of this mechanism, not permission to relabel the experiment as generic robustness.

## Frozen public-data contract

Use only `2D_rdb_NA_NA.h5` in released PDEBench dataset
`doi:10.18419/DARUS-2986`, version 8.0, official DaRUS file ID 133021:

- exact bytes: `6,626,098,972`;
- official MD5: `75d838c47aa410694bdc912ea7f22282`;
- exactly 1,000 top-level groups named `0000` through `0999`;
- `{group}/data`: float32 `[101,128,128,1]` water depth;
- `{group}/grid/x` and `y`: float32 `[128]` cell centers from `-2.48046875`
  through `2.48046875` at spacing `0.0390625`;
- `{group}/grid/t`: float32 `[101]` from `0.0` through `1.0` at spacing `0.01`;
- every group must have identical coordinates and finite, strictly positive depth.

The official metadata, fixed generator commit, and source hashes are stored in
`swe_rdb_source_20260902.json`. Download to a `.part` path. Before HDF5 access, require exact
bytes and official MD5, compute SHA-256, atomically rename the file, and write the SHA-256 into an
immutable data lock. Stream every trajectory and require maximum absolute water-depth mean drift
from its initial time at most `5e-5`. Spatial block-average factors `{1,2}` must preserve the mean
within `1e-6`.

Any byte, MD5, group, key, shape, dtype, coordinate, finiteness, positivity, conservation, or
restriction-identity failure terminates this exact dataset block before model activation. It cannot
trigger a schema amendment, alternate shallow-water file, regenerated data, or result-conditioned
threshold change.

## Frozen model, split, and factorial

Use a single-field FNO2d. Each input contains ten consecutive depth fields plus normalized x/y
coordinates; the output is the next depth field. Padding is retained because the physical boundary
is non-periodic. Use four equal-parameter trained arms:

- `free`: absolute output without mass enforcement;
- `free_res`: residual output without mass enforcement;
- `hard_abs`: absolute output shifted to the preceding state's spatial mean;
- `hard`: residual output with its spatial mean centered exactly.

Training minimizes unweighted physical-space MSE. Do not normalize or clamp water depth. The
absence of clamping is essential: post-hoc mass projection is a constant shift, and clamping would
confound linear conservation with nonlinear positivity enforcement.

Use history 10, modes 8 per axis, width 20, padding 4, projection width 64, 100 epochs, Adam
learning rate 0.001, weight decay 0.0001, StepLR at epoch 50 by 0.5, batch size 8, and checkpoints
every 20 epochs. For each seed, sample 512 training trajectories without replacement from groups
0200--0999. Hold out groups 0000--0127 for evaluation. Train at temporal stride 2 and spatial
2x2 block averaging (64x64). Evaluate ID-64 and native OOD-128 at horizons `{1,4,16,31}`;
OOD-128/horizon-16 is primary.

Formal seeds are exactly 6000--6029. Seed 5999 is an excluded one-epoch implementation/CUDA
preflight and may be used only to verify execution and estimate runtime, never to choose a model,
threshold, seed, horizon, or conclusion. Each formal seed yields four trained records and the
zero-training post-hoc projection of `free`, for exactly 150 core records.

## Frozen outcomes and enforcement cube

The primary attribution outcome is mean-centered (`conserving`) RMSE. Secondary outcomes are total
RMSE, mean/max absolute mass drift, target mass drift, negative-depth fraction, mean negative-depth
deficit, and minimum predicted depth. Primary scientific interpretation requires all three:

- local-dynamics quality from conserving RMSE;
- exact or approximate invariant satisfaction from mass drift; and
- physical admissibility from the positivity outcomes.

After the core factorial passes exact coverage and provenance checks, derive the residual post-hoc
projection and the two compatible unprojected hard-checkpoint evaluations with zero additional
optimization, producing exactly 90 records. Use the same eight cells `Y[c,t,e]`, differences
`D[t,e]=Y[A,t,e]-Y[R,t,e]`, bundled interaction `I_bundle=D[0,0]-D[1,1]`, training effects
`T0=D[0,0]-D[1,0]`, `T1=D[0,1]-D[1,1]`, inference effects `E0=D[0,0]-D[0,1]`,
`E1=D[1,0]-D[1,1]`, interaction `J=T0-T1=E0-E1`, and path-averaged contributions
`phi_train=(T0+T1)/2`, `phi_infer=(E0+E1)/2`.

Use 50,000 paired bootstrap draws, seed as the inference unit, 95% nonzero and 90% equivalence
intervals, 100,000 paired sign flips with Holm correction over the eight case--horizon cells
(two resolutions by four predeclared rollout horizons), and SESOI
`0.10 * mean(Y[R,0,0])`. The primary four-way classification is ordered and unchanged from the
Advection protocol. Apply paired bootstrap summaries to positivity outcomes as secondary mechanism
evidence, without using them to select the primary conclusion.

No formal metric may be read before exact coverage, unique run IDs, successful checkpoints,
complete provenance, record-file hash, and worker exit. Missing or non-finite records fail the
block; they do not authorize retraining with a different hyperparameter, clipping, seed, or file.
