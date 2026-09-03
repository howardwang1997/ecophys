# ICLR external-validity freeze: PDEBench 1D Advection with FNO

Date frozen: 2026-08-31 NZST, before downloading or inspecting the selected solution tensor and
before any model outcome on this benchmark exists.

Target: ICLR 2027. This is a separate, prospectively frozen external-validity evidence block for
the constraint-attribution paper. It neither amends nor rescues the frozen synthetic confirmation,
and its results will not be pooled with those systems.

## Selection and audit chronology

The benchmark was selected before any PDEBench solution values were accessed, using four
predeclared scientific criteria: a public benchmark with a stable DOI, a documented periodic PDE
with a linear invariant, an official neural-operator baseline, and native resolution transfer.
The selected system is PDEBench 1D linear advection at `beta=0.4` with an FNO backbone.

During the subsequent repository audit, an over-broad search accidentally rendered several
historical synthetic-pilot OOD numeric fields. No held-out confirmation value and no PDEBench
outcome was accessed. The incident is recorded in
`experiments/constraint_attribution_iclr/deployment/pilot_ood_accidental_exposure_20260831.yaml`.
Those pilot values are forbidden inputs to every choice below. The candidate is deliberately not
changed after the exposure.

## Public data contract

- Dataset: PDEBench, DOI `10.18419/DARUS-2986`, DaRUS released version 8.
- File: `1D_Advection_Sols_beta0.4.hdf5`, data-file ID `255674`.
- Download URL: `https://darus.uni-stuttgart.de/api/access/datafile/255674`.
- Released size: `8,232,966,952` bytes.
- Released MD5: `d595bbfd2c659df995a93cd40d6ea568`.
- License: CC BY 4.0. Dataset attribution and the PDEBench paper are mandatory in the paper.
- Expected scalar tensor schema: `[trajectory, time, x] = [10000, 201, 1024]`, float32, with
  `x-coordinate` and `t-coordinate` arrays.
- Generator metadata used only to interpret the benchmark: periodic domain `[0,1)`, saved time
  step `0.01`, final time `2`, spatial resolution `1024`, and advection coefficient `beta=0.4`.

The file is admissible only if its byte count and MD5 match, its schema and coordinates match, all
values are finite, and the maximum absolute drift of the float64-computed spatial mean from the
first frame is at most `1e-5` over all 10,000 trajectories and 201 frames at each evaluation
spatial stride `{1,2,4}`. The scan is a physical
data-integrity gate, not a model outcome. Failure stops this benchmark; the tolerance, file, and
beta may not be changed after seeing the failure. A successful scan writes an immutable data lock
containing SHA-256, MD5, observed schema, coordinate checks, and invariant-gate statistics.

Only the CC-BY dataset and factual configuration metadata are reused. The experiment uses an
independent implementation of the MIT-licensed FNO architecture; no PDEBench generator or training
code with a more restrictive header is copied or distributed.

## Frozen partitions and inferential units

Trajectory indices are fixed before access:

- public benchmark test / external confirmation: `[0, 256)`;
- training pool: `[1000, 9000)`;
- outcome-excluded preflight only: `[9000, 9256)`;
- all remaining trajectories: unused.

Formal paired seeds are exactly `{2000, ..., 2029}`. For each seed, 2,048 training trajectories are
sampled without replacement from the training pool using a stable namespaced hash seed. All arms
for that seed share the exact subset, temporal windows, minibatch order, initialization tensor, and
test trajectories. Seed `1999` is reserved for a one-epoch CUDA preflight and is never analyzed.
Samples are not inferential units; all sample/time/space reductions occur inside a seed first.

## Operator task and OOD cases

The model receives the preceding 10 saved frames and predicts the next frame. Data are temporally
subsampled by 5, so adjacent model frames are separated by `0.05` physical time units. Training is
at spatial stride 4 (256 points). Autoregressive evaluation starts from the first 10 subsampled
ground-truth frames and uses horizons `{1, 4, 16, 31}`.

- `id_r256`: the training resolution, all frozen horizons;
- `ood_r512`: spatial stride 2, evaluated without retraining;
- `ood_r1024`: native resolution, evaluated without retraining.

The primary external case is `ood_r512` at horizon 16. The other resolution/horizon combinations
are secondary and all are reported. No parameter-beta OOD file is added after outcomes.

## Backbone, arms, and fixed training budget

The original 1D FNO implementation follows the published baseline shape: coordinate concatenation,
width 20, 12 Fourier modes, four spectral-plus-pointwise blocks, padding 2, GELU, and a 128-unit
projection layer. The input history is 10 frames. All trained arms have identical parameters:

- `free`: absolute output;
- `free_res`: last input frame plus an unconstrained learned delta;
- `hard`: last input frame plus a learned delta whose spatial mean is removed exactly;
- `soft30`: absolute output with `30 * mean-drift^2` added to MSE;
- `projection`: derived at evaluation from the trained `free` model, with no optimization.

Training is float32 without AMP: Adam, learning rate `1e-3`, weight decay `1e-4`, batch size 50,
200 epochs, and StepLR at epoch 100 with gamma 0.5. Each epoch presents exactly one deterministic
next-frame window from every selected trajectory; offsets cycle through all 31 legal windows.
Thus every trained arm sees 409,600 examples. There is no early stopping, validation selection, or
hyperparameter grid. The reduction from the official 500-epoch default and the 2,048-trajectory
subsample are fixed computational adaptations made before data access. Checkpoints are mechanical
recovery artifacts and may resume only the identical run ID.

## Metrics and frozen analysis

For error `e = prediction - target`, the conserving error removes its spatial mean. Per seed and
case/horizon, record total RMSE, conserving RMSE, mean and maximum absolute drift of predicted mass
from the initial mass, and target-data mass drift. The primary outcome is conserving RMSE on
`ood_r512`, horizon 16.

The exact horizon-one identity gate is checked at every resolution: `free` and its derived
`projection` must have equal conserving error within relative `1e-5` and absolute `1e-8`.

Across the 30 paired seeds:

1. `hard - free_res` practical equivalence uses a 90% paired-bootstrap CI and a SESOI equal to 10%
   of mean `free_res` conserving RMSE.
2. The parameterization effect `free - free_res` uses a 95% paired-bootstrap CI.
3. External attribution requires rule 1 and an absolute mean parameterization effect at least twice
   the absolute mean `hard - free_res` effect. Direction is reported rather than assumed.
4. `soft30` and `projection` are secondary controls and cannot rescue failed primary rules.

Bootstrap uses 50,000 draws and RNG seed `20260831`. Every resolution/horizon is displayed;
secondary sign tests receive Holm correction as one external family. The external block may
support architecture/dataset transfer only. It cannot establish universality, a nonlinear
invariant claim, or repair any failed/incomplete synthetic system.

## Execution gates and compute isolation

- Focused unit tests, synthetic-HDF5 smoke, dataset lock, source/config snapshot hashes, and one
  excluded seed-1999 CUDA preflight must pass before formal launch.
- Formal results are append-only, skip only already completed canonical run IDs, and remain
  outcome-blind until all 150 expected records (30 seeds times four trained arms plus projection)
  pass coverage, provenance, hash, finiteness, and algebraic gates.
- The existing V100 confirmation workers are never interrupted or colocated with this benchmark.
  Use the RTX 2060S only if it becomes reachable and passes memory/timing preflight; otherwise queue
  on the first V100 after its frozen main worker finishes.
- GPU hours and wall time are monitoring quantities, not result-driven stopping rules. A hardware
  failure permits identical resume; seed replacement, setting changes, partial analysis, and
  outcome-driven stopping are forbidden.

## Primary sources

- PDEBench repository and dataset instructions: `https://github.com/pdebench/PDEBench`
- PDEBench benchmark paper: `https://papers.nips.cc/paper/2022/hash/0a9747136d411fb83f0cf81820d44afb-Abstract-Datasets_and_Benchmarks.html`
- Released dataset record: `https://doi.org/10.18419/DARUS-2986`
- Frozen official advection configuration:
  `https://github.com/pdebench/PDEBench/blob/main/pdebench/data_gen/data_gen_NLE/AdvectionEq/config/multi/beta4e-1.yaml`
