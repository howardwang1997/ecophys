# ICLR public multi-field conservation replication freeze

Frozen 2026-09-01 NZST after the PDEBench Burgers data block failed its coordinate contract,
while the fresh Advection factorial was incomplete, before any Advection metric was accessed, and
before downloading or inspecting any value from the selected replacement dataset.

## Why this task

The independent public replication is PDEBench's periodic one-dimensional compressible
Navier--Stokes dataset with `eta=zeta=0.01`. It is a nonlinear three-field system (density,
pressure, and velocity), unlike the scalar linear Advection task. Periodic finite-volume density
updates conserve the spatial integral of density, which is a linear invariant. This task therefore
tests whether coordinate/enforcement attribution extends beyond scalar translation dynamics.

The replacement is not a retry of the failed Burgers block. The Burgers file, failure record, and
terminal exclusion remain unchanged.

## Frozen public-data contract

Use only
`1D_CFD_Rand_Eta0.01_Zeta0.01_periodic_Train.hdf5` from Hugging Face dataset
`pdebench/1D-Compressible-Navier-Stokes` at commit
`aebb84fc14f674881696a9c72c814bd8b7083fd1`:

- exact bytes: `12,410,888,600`;
- exact SHA-256: `86a2b8cf81f40191dbc40a7c2a9b268784979f2c1c269b59daa23c83885ebe8f`;
- required fields: `density`, `pressure`, `Vx`, `x-coordinate`, and `t-coordinate`;
- each physical field: float32 with shape `[10000,101,1024]`;
- `x-coordinate`: 1024 uniform cell centers, first `-0.9990234375`, period `2.0`;
- `t-coordinate`: 101 uniform values from `0.0` through `1.0` at spacing `0.01`;
- attributes: `eta=0.01` and `zeta=0.01`.

These expectations follow the official fixed generator source, whose commit and per-file hashes
are stored in `cns_eta0p01_source_20260901.json`. Before model code is activated, stream all three
fields to require finite values and verify density conservation over every trajectory/time. The
maximum absolute density-mean drift from the first time is at most `2e-5`. For spatial factors
`{1,2,4}`, block-average restriction must preserve the density mean within `1e-6`.

Any bytes, hash, key, shape, dtype, coordinate, attribute, finiteness, density-drift, or restriction
identity failure terminates this dataset block. It cannot trigger a schema amendment, viscosity
change, alternate file, or model run.

## Frozen model and factorial

Use a three-field 1D FNO. Each input is ten consecutive states with the three channels flattened
at each spatial point plus the spatial coordinate. The network predicts three output channels.
Use four equal-parameter trained arms:

- `free`: absolute output, no density projection;
- `free_res`: residual output for all fields, no density projection;
- `hard_abs`: absolute output with the density channel projected to the preceding density mean;
- `hard`: residual output for all fields with the density residual centered exactly.

No channel normalization is used. Training minimizes the unweighted physical-space mean squared
error over all three fields. This choice is fixed before data-value access. The invariant projector
acts only on density. Report density conserving RMSE as the primary attribution metric and full
three-field RMSE plus per-field RMSE and density drift as secondary metrics.

Use FNO history 10, modes 12, width 20, padding 2, projection width 128, 200 epochs, Adam learning
rate 0.001, weight decay 0.0001, StepLR at epoch 100 by 0.5, batch size 50, and checkpoints every
25 epochs. For each seed sample 2,048 training trajectories without replacement from indices
1000--8999. Hold out trajectories 0--255 for evaluation. Train at temporal stride 2 and spatial
block-average factor 4. Evaluate factors `{4,2,1}` as ID-256/OOD-512/OOD-1024 at horizons
`{1,4,16,31}`; OOD-512/horizon-16 is primary.

The formal seeds are exactly 5000--5029; seed 4999 is an excluded one-epoch implementation
preflight. Do not tune from either output. Each formal seed yields the four trained records plus
the zero-training absolute post-hoc density projection, for exactly 150 core records.

## Frozen enforcement cube and inference

After the core factorial passes its complete-record analyzer, derive the residual post-hoc
projection and the two compatible unprojected hard-checkpoint evaluations exactly as in the
Advection enforcement-cube protocol. They require zero optimization and produce exactly 90
additional records. Apply the same `D[t,e]`, `T0`, `T1`, `E0`, `E1`, `J`, and path-averaged Shapley
decomposition to density conserving RMSE.

Use 50,000 paired bootstrap draws, the seed as inference unit, 95% nonzero and 90% equivalence
intervals, 100,000 paired sign flips with Holm correction over the 12 cells, and SESOI
`0.10 * mean(Y[R,0,0])`. The same ordered four-way classification applies. Null, reverse,
non-finite, or practically negligible effects cannot be relabeled as robustness evidence.

No formal metric may be read before exact coverage and worker exit. A failed checkpoint or raw
hard-trained rollout is a failed block, not permission to retrain, clip, change a seed, or select a
different viscosity.
