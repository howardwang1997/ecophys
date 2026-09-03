# PDEBench v8 coordinate-schema amendment

Recorded: 2026-09-01 NZST (`2026-08-31T15:34:35Z`).

This outcome-blind amendment corrects only the coordinate representation expected by the frozen
PDEBench external-validity protocol. It was written after the released byte count and MD5 passed
but before any value from the solution tensor was read, before the invariant scan, and before any
model run or outcome.

## Trigger

The original validator expected `x-coordinate[0] == 0` and a time-coordinate length equal to the
201 tensor frames. The exact released v8 file (data-file ID 255674, released MD5
`d595bbfd2c659df995a93cd40d6ea568`) instead has:

- solution-tensor metadata: shape `[10000, 201, 1024]`, dtype float32;
- `x-coordinate`: 1024 uniform cell centers from `0.00048828125` through `0.99951171875`, spacing
  `0.0009765625`, with cell-centered period exactly 1;
- `t-coordinate`: 202 uniform entries from 0 through approximately 2.01, spacing approximately
  0.01. The first 201 entries, through approximately 2.00, correspond to the 201 tensor frames;
  the final 2.01 coordinate has no tensor frame.

Only HDF5 keys, shapes, dtypes, coordinate arrays, byte count, and hashes were accessed to diagnose
the trigger. The scanner raised at the coordinate-start check before its first tensor slice.

## Corrected fail-closed contract

The validator must require exactly the representation above. It uses the first 201 time
coordinates and requires the single unused trailing coordinate to be 2.01 within `1e-6`. The
cell-centered spatial grid must have start `1/2048`, spacing `1/1024`, and period 1 within `1e-6`.
Any other coordinate length, extra-coordinate count, endpoint, spacing, byte count, MD5, tensor
shape/dtype, nonfinite value, or mean-drift failure still stops the benchmark.

This amendment changes no solution value, physical domain, PDE, file, beta, invariant threshold,
split, seed, architecture, arm, training budget, metric, horizon, analysis rule, or compute policy.
The original stop rule remains binding after this exact schema correction. Both the base protocol
hash and this amendment hash must be present in the data lock, every formal record, and the frozen
analyzer.

