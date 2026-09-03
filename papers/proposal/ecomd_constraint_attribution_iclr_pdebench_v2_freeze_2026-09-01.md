# ICLR PDEBench external-validity v2 freeze: conservative restriction

Frozen: 2026-09-01 NZST (`2026-08-31T17:06:50Z`), after explicit PI approval and before any
PDEBench model run or model outcome.

## Status and relationship to v1

PDEBench v1 is terminally stopped at its prospective data-admission gate. Direct point decimation
preserved neither the 512-point nor 256-point discrete spatial mean, so v1 produced no data lock,
model run, or model record. Its failure artifact remains immutable.

The PI explicitly authorized v2. V2 changes exactly one scientific operation: spatial restriction
from the native 1024-point grid to 512 or 256 points uses non-overlapping block averages instead of
taking every second or fourth point. Every other data, split, seed, architecture, arm, training,
metric, horizon, analysis, and compute choice remains as frozen in v1. V1 records, if any were ever
created, would be excluded; the expected count is and must remain zero.

## Public data and schema

- PDEBench 1D Advection, `beta=0.4`, DOI `10.18419/DARUS-2986`, released DaRUS version 8.
- File ID `255674`, `1D_Advection_Sols_beta0.4.hdf5`, 8,232,966,952 bytes.
- Released/observed MD5 `d595bbfd2c659df995a93cd40d6ea568`.
- Observed SHA-256 `d973ff2bb3c2a5edf42957ff029b78672451532ebd6bf475848ff23cfd3ee3b6`.
- CC BY 4.0; dataset and PDEBench paper attribution are mandatory.
- Tensor `[10000,201,1024]`, float32. The exact cell-centered x and one-unused-trailing-t schema is
  governed by the outcome-blind 2026-09-01 coordinate amendment.

The linear invariant is the spatial mean (equivalently mass on a uniform periodic grid).

## Conservative restriction and admission gates

For factor `q` in `{1,2,4}`, partition each native field into consecutive periodic-grid blocks of
size `q` and replace each block by its float64-computed average cast to float32. Factor 1 is the
identity. The coarse coordinate is the float64 mean of the corresponding native cell centers cast
to float32. No interpolation, filtering, learned preprocessing, or outcome-dependent transform is
allowed.

The exact downloaded file is admissible only if all of the following pass:

1. bytes, MD5, SHA-256, tensor schema, coordinate schema, and global finiteness match;
2. at factors `{1,2,4}`, maximum absolute target-mean drift from the first frame is at most `1e-5`;
3. at factors `{2,4}`, maximum absolute difference between the restricted mean and the native mean
   for the same trajectory/frame is at most `1e-6`.

The factor-2/4 identities are algebraic implementation gates. Failure stops v2; thresholds or
precision cannot be changed. A pass creates a new immutable v2 data lock containing both protocol
hashes, exact data hashes, schema report, and all gate statistics.

## Frozen splits and paired seeds

- external confirmation trajectories: indices `[0,256)`;
- training pool: `[1000,9000)`;
- excluded preflight pool: `[9000,9256)`;
- remaining trajectories: unused.

Formal seeds are exactly `{2000,...,2029}`. Each seed samples 2,048 unique training trajectories
from the pool using the frozen stable namespace. All arms for a seed share the subset, 31-window
cycle, minibatch order, initialization tensor, and evaluation data. Seed 1999 is CUDA preflight
only and excluded from every analysis.

## Task, model, arms, and training

Inputs are 10 preceding frames; the next frame is predicted. Temporal stride is 5 (`0.05` physical
time). Training uses factor-4 block averages (256 points). Evaluation without retraining uses:

- `id_r256`: factor 4;
- `ood_r512`: factor 2;
- `ood_r1024`: factor 1.

Autoregressive horizons are `{1,4,16,31}`. The primary external case remains `ood_r512`, horizon
16. All other case/horizon combinations are mandatory secondary results.

The original implementation uses a PDEBench-shaped 1D FNO: history 10 plus coordinate, width 20,
12 Fourier modes, four spectral-plus-pointwise blocks, padding 2, GELU, and projection width 128.
Trained arms have identical parameters: `free`, `free_res`, `hard`, and `soft30`; `projection` is
derived from `free` without optimization. Hard residual output removes the delta mean exactly;
soft30 adds `30 * mean-drift^2` to absolute-output MSE.

Training remains float32 without AMP: Adam, learning rate `1e-3`, weight decay `1e-4`, batch 50,
200 epochs, StepLR at epoch 100 with gamma 0.5, and one deterministic legal window per selected
trajectory per epoch. Every trained arm sees 409,600 examples. No validation selection, early
stopping, hyperparameter search, or outcome-driven retry is allowed.

## Metrics and frozen adjudication

Within each seed/case/horizon record total RMSE, conserving RMSE after removing the error mean,
mean/max absolute predicted-mass drift from initial mass, and target-mass drift. The horizon-one
`free`/`projection` conserving-RMSE identity must pass relative `1e-5`, absolute `1e-8` at every
resolution.

The primary paired analysis over 30 seeds is unchanged:

1. `hard - free_res` equivalence: 90% paired-bootstrap CI within a SESOI of 10% of mean
   `free_res` conserving RMSE;
2. `free - free_res`: 95% paired-bootstrap CI excluding zero for a nonzero parameterization effect;
3. attribution additionally requires the absolute mean parameterization effect to be at least
   twice the absolute hard-enforcement effect;
4. `soft30` and `projection` remain secondary controls and cannot rescue primary failure.

Bootstrap uses 50,000 draws; secondary parameterization sign tests receive Holm correction across
all resolution/horizon cells. Samples are reduced inside seed; seeds are the inferential units.
The block remains external validity only and is never pooled with the synthetic confirmation.

## Execution and outcome-blindness

- Required before formal work: 14 focused tests, an end-to-end synthetic block-average smoke, v2
  data lock, immutable per-file snapshot hashes, and an excluded seed-1999 CUDA preflight.
- Formal output is append-only with exactly 150 records: 30 seeds times four trained arms plus the
  derived projection. Only identical run-ID checkpoint resume is permitted.
- Do not read partial model metrics. Analyze once only after coverage, hashes, provenance,
  finiteness, pairing, target-invariant, and projection gates pass.
- Do not interrupt or colocate with the active synthetic V100 confirmation. Prefer the authorized
  RTX 2060S if reachable and preflight-safe; otherwise wait for a V100 to become naturally idle.
- Runtime, GPU hours, disk, and energy are monitoring quantities, not scientific stopping rules.

