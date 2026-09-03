# ICLR PDEBench Burgers factorial replication freeze

Frozen: 2026-09-01 NZST, before downloading or inspecting model-ready file ID 281363 and before
any seed 3999 or 4000--4029 model run. The choice is independent of the still-running advection
factorial outcomes.

## Scientific role and fixed system

This is a nonlinear public-benchmark replication of the fully crossed intervention attribution
design. The system is periodic PDEBench 1D viscous Burgers at exactly `nu=0.01`. This viscosity was
selected because it matches the separately frozen synthetic Burgers setting while providing a
nonlinear transport-diffusion problem; it may not be switched after data admission or model
outcomes. The conserved linear invariant is the uniform-grid spatial mean (mass).

The official DaRUS version-8 API metadata observed before download fixes:

- file ID 281363, `1D_Burgers_Sols_Nu0.01.hdf5`, 8,232,968,312 bytes;
- MD5 `e6d9a4f62baf9a29121a816b919e2770`;
- DOI `10.18419/DARUS-2986`, CC BY 4.0.

The SHA-256 is unknown until the exact bytes are downloaded and must be recorded in a new immutable
data lock. The source metadata artifact is
`experiments/constraint_attribution_iclr/pdebench/burgers_nu0p01_source_20260901.json`.

## Terminal data-admission gate

The exact byte count, MD5, global SHA-256, finiteness, and separately frozen coordinate schema must
pass. At native resolution and conservative non-overlapping block-average factors 2 and 4:

1. maximum target-mean drift from each trajectory's first frame is at most `1e-5`;
2. maximum restricted-versus-native mean difference is at most `1e-6`.

Block means are computed in float64 and cast to float32. Failure is terminal for this file and
viscosity: do not loosen thresholds, switch viscosity, select trajectories, or replace the public
file. No model may run without a passing immutable data lock.

## Frozen experiment

The data split, FNO, training budget, factor cells, and analysis are intentionally identical to the
advection factorial block unless the Burgers schema makes a field inapplicable:

- external trajectories `[0,256)`, training pool `[1000,9000)`, and excluded preflight pool
  `[9000,9256)`;
- 2,048 unique trajectories per seed; history 10; temporal stride 5; factor-4 conservative
  restriction for 256-point training;
- width 20, 12 Fourier modes, four spectral-plus-pointwise blocks, padding 2, GELU, projection
  width 128;
- Adam `1e-3`, weight decay `1e-4`, batch 50, 200 epochs, StepLR(100, 0.5), float32 without AMP,
  deterministic 31-window cycle, no validation selection, early stopping, or tuning;
- zero-shot evaluation at 256, 512, and 1024 points and horizons `{1,4,16,31}`; OOD 512 at horizon
  16 is primary;
- exact trained cells `free`, `free_res`, `hard_abs`, and `hard`, plus derived `projection`.

Formal seeds are exactly `{4000,...,4029}` and excluded CUDA preflight seed is 3999. The formal file
must contain exactly 150 records. Within seed, all four cells share trajectories, windows,
minibatch order, and initial parameter tensors. No advection checkpoint or seed is reused.

## Frozen analysis and interpretation

Use the same conserving-RMSE estimands and signs as the advection factorial protocol:

`I = Y_A0 - Y_R0 - Y_A1 + Y_R1`,
`phi_P = ((Y_A0-Y_R0)+(Y_A1-Y_R1))/2`, and
`phi_E = ((Y_A0-Y_A1)+(Y_R0-Y_R1))/2`.

Use 50,000 paired seed-bootstrap draws, the primary SESOI
`delta = 0.10 * mean(Y_R0)`, and the same ordered four-way classification:
`material_nonadditivity`, `statistical_nonadditivity_below_or_crossing_sesoi`,
`practical_additivity`, or `unresolved`. Apply Holm adjustment to the 12 secondary interaction
sign-flip tests. Hard/projection drift must remain at most `1e-4`, the horizon-one projection
identity must pass, and Shapley efficiency error must be at most `1e-12`.

Analyze Burgers separately from advection and the synthetic systems. Agreement may support
cross-PDE replication; disagreement is scientific heterogeneity and must not trigger tuning or
selective omission. Partial metrics may not be inspected, and the one-shot analyzer runs only
after exact coverage and all integrity gates pass.
