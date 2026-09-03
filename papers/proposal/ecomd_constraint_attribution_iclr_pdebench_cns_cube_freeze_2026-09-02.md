# ICLR PDEBench compressible-NS enforcement-cube freeze

Registered on 2026-09-02 before the fixed public HDF5 download completed and before any value or
model metric from that file was read. This document specializes the already frozen Advection
training-by-inference cube to the independently selected PDEBench periodic 1D compressible
Navier--Stokes benchmark. It adds no trained model and cannot change the parent factorial.

## Scientific question

Does the apparent benefit attributed to an output coordinate instead arise from whether density
conservation is imposed during training, during recursive inference, or both? The cube crosses:

1. output coordinate: absolute (`A`) versus residual (`R`);
2. density-conserving projection during training: absent (`0`) versus present (`1`); and
3. the same projection during recursive inference: absent (`0`) versus present (`1`).

The five parent cells are the frozen factorial records: `A00=free`, `R00=free_res`,
`A01=projection`, `A11=hard_abs`, and `R11=hard`. After the exact 150-record core passes its
frozen analyzer, derive exactly three additional cells per seed with zero optimization:

- `R01=projection_res`: load `free_res` and project density after every recursive step;
- `A10=hard_abs_unprojected`: load `hard_abs` but evaluate its learned raw absolute map without
  the density projector;
- `R10=hard_res_unprojected`: load `hard` but evaluate its learned raw residual map without the
  density projector.

For the unprojected hard cells, the identical parameter tensors are loaded into the compatible
unconstrained forward map. All four parent architectures have equal parameter counts, so this
operation removes only the deterministic output transformation. No optimizer, gradient update,
or checkpoint repair is permitted.

## Frozen estimands

At every already frozen evaluation case and horizon, let `Dte = Ate - Rte`, where `t` is the
training-projection indicator and `e` is the inference-projection indicator. Lower RMSE is better.
Compute per seed:

- bundled interaction `I_bundle = D00 - D11`;
- training effects `T0 = D00 - D10` and `T1 = D01 - D11`;
- inference effects `E0 = D00 - D01` and `E1 = D10 - D11`;
- three-way interaction `J = T0 - T1 = E0 - E1`;
- symmetric credits `phi_train = (T0 + T1)/2` and `phi_infer = (E0 + E1)/2`, which must satisfy
  `phi_train + phi_infer = I_bundle` to numerical tolerance.

The primary cell remains OOD resolution 512, horizon 16, and the primary metric remains density
conserving RMSE. The 12 case-by-horizon tests use the parent protocol's paired bootstrap,
sign-flip, SESOI, and Holm rules. The cube is explanatory: it does not replace the independently
frozen parent factorial estimand.

## Integrity and activation

Formal seeds remain 5000--5029. The core must contain exactly 150 valid records and 120 trained
checkpoints; the derived file must contain exactly 90 records. After the core worker exits and its
analyzer passes, create a canonical checkpoint lock binding the complete core JSONL, its analysis,
and every parent checkpoint's run ID, path, bytes, SHA-256, payload schema, and completed epoch.
Every derived record must bind that lock and its exact parent provenance.

No formal metric may be read before exact derived coverage and worker exit. Missing or corrupted
parents terminate the affected experiment; they do not authorize retraining, seed substitution,
grid changes, or schema amendments. Result interpretation may be positive, null, or adverse, but
the registered estimands and gates may not be changed in response.
