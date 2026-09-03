# ICLR PDEBench factorial attribution freeze

Frozen: 2026-09-01 NZST, after the completed PDEBench v2 block was analyzed and before any model
run with factorial seed 2999 or 3000--3029. This is a prospectively specified follow-up, not a
claim that the question was registered before the first external result.

## Why this experiment exists

The completed v2 block compared `free -> free_res -> hard`, so its numerical credit allocation is
path-specific: output coordinates change first and hard enforcement is added second. It did not
train the missing absolute-output/hard-enforcement cell. The new experiment asks whether output
parameterization and exact conservation interact. A material interaction is a scientific finding:
credit depends on the reference path. Practical equivalence of the interaction is also falsifiable:
it validates an additive decomposition at the inherited scale. An unresolved interval remains
unresolved and cannot be rewritten as either conclusion.

This design was fixed with knowledge of the immutable completed v2 artifacts:

- records SHA-256 `09e69b4e50bd39c152bef0e22e07d86a8b513f31ed119d887ed3077fb72d2fc3`;
- analysis SHA-256 `e1619126f46eb081ace19000d44771559029c49f22f0057812183fc7e2efb41a`.

No v2 seed, record, or checkpoint is reused in the factorial inference.

## Frozen 2 x 2 intervention

Let the output-coordinate factor be absolute (`A`) or residual (`R`), and let the enforcement
factor be unconstrained (`0`) or exact hard mass conservation (`1`). Four equally parameterized
FNOs are trained per seed:

| Cell | Mechanism ID | Prediction map |
|---|---|---|
| `A0` | `free` | `f_theta(x)` |
| `R0` | `free_res` | `u_t + f_theta(x)` |
| `A1` | `hard_abs` | `f_theta(x) + mean(u_t) - mean(f_theta(x))` |
| `R1` | `hard` | `u_t + f_theta(x) - mean(f_theta(x))` |

The mass projection is differentiable and belongs inside training for both hard cells. A fifth
record, `projection`, is derived without optimization by applying the same projection to the
`free` model at every rollout step. It is a secondary training-versus-inference control and not a
factorial cell. `soft30` is not rerun because it is not a level of the binary enforcement factor;
its completed v2 result remains report-only.

## Data, pairing, model, and budget

Everything except the new factor cell, mechanism allowlist, stage/output identity, and fresh seeds
is inherited unchanged from the admitted PDEBench 1D Advection `beta=0.4` v2 block:

- exact public file SHA-256
  `d973ff2bb3c2a5edf42957ff029b78672451532ebd6bf475848ff23cfd3ee3b6` and data-lock SHA-256
  `78705fc8f0c342bc5f937756fce93ab60c660acbb24d15a5ea90a620f7890687`;
- training pool `[1000,9000)`, 2,048 trajectories per seed, and external trajectories `[0,256)`;
- history 10, temporal stride 5, conservative factor-4 training restriction, width 20, 12 modes,
  four FNO blocks, padding 2, and projection width 128;
- Adam at `1e-3`, weight decay `1e-4`, batch 50, 200 epochs, StepLR(100, 0.5), float32 without AMP,
  one deterministic 31-window cycle, and no validation selection or early stopping;
- evaluation at `id_r256`, `ood_r512`, and `ood_r1024`, horizons `{1,4,16,31}`, with
  `ood_r512` horizon 16 primary.

Formal seeds are exactly `{3000,...,3029}`. Seed 2999 is excluded CUDA preflight only. Within a
seed, every trained cell shares the trajectory subset, windows, minibatch order, and identical
initial parameter tensors. The formal file must contain exactly 150 records: 30 seeds times four
trained cells plus the derived projection. Hardware runtime, energy, and disk are monitored but do
not stop or resize the block.

## Frozen estimands

For primary conserving RMSE `Y` (lower is better), define positive quantities as improvements:

- residual-coordinate credit when free: `P0 = Y_A0 - Y_R0`;
- residual-coordinate credit when hard: `P1 = Y_A1 - Y_R1`;
- hard-enforcement credit in absolute coordinates: `E_A = Y_A0 - Y_A1`;
- hard-enforcement credit in residual coordinates: `E_R = Y_R0 - Y_R1`;
- interaction/path dependence:
  `I = P0 - P1 = E_A - E_R = Y_A0 - Y_R0 - Y_A1 + Y_R1`;
- path-averaged two-factor Shapley credits:
  `phi_P = (P0 + P1)/2` and `phi_E = (E_A + E_R)/2`.

The exact efficiency identity `phi_P + phi_E = Y_A0 - Y_R1` must hold numerically. The Shapley
credits are estimands for intervention attribution, not feature-explanation scores.

Seeds are the inferential units. Percentile paired-bootstrap intervals resample whole seed vectors
with 50,000 draws. Fixed RNG namespaces are part of the analyzer. The inherited practical scale is
`delta = 0.10 * mean(Y_R0)` in the primary cell.

Primary interaction classification is exactly:

1. `material_nonadditivity` if the 95% interval is wholly above `+delta` or below `-delta`;
2. `statistical_nonadditivity_below_or_crossing_sesoi` if the 95% interval excludes zero but rule 1
   does not pass;
3. `practical_additivity` if the 90% interval lies wholly inside `[-delta,+delta]`;
4. `unresolved` otherwise.

Rules are mutually exclusive in the order above. Report means and 95% intervals for all four
simple credits and both Shapley credits regardless of sign. The projection-versus-`hard_abs`
contrast, total RMSE, drift metrics, and the other 11 case/horizon cells are secondary. For the 12
cell-wise interaction sign-flip tests, report Holm-adjusted p-values; they cannot override the
primary classification.

## Integrity and outcome-blind execution

Before formal execution: focused tests must pass; a one-epoch seed-2999 CUDA preflight must create
five finite records; the executable snapshot and per-file SHA-256 manifest must verify on the
authorized V100; and preflight artifacts must be excluded from formal analysis.

Formal analysis is allowed once only after all of these pass:

1. exact 150-record coverage, unique run IDs, exact seed/mechanism pairs, and finite numeric fields;
2. exact bindings to this protocol, the coordinate amendment, data lock, snapshot provenance, and
   identical paired training-subset hashes;
3. equal parameter counts and identical initialization digest across the four trained cells within
   each seed;
4. horizon-one `free`/`projection` conserving-RMSE identity at every resolution;
5. `hard_abs`, `hard`, and `projection` maximum absolute invariant drift at most `1e-4` for every
   seed/case/horizon;
6. Shapley efficiency identity absolute error at most `1e-12` in the final float64 analysis.

Partial model metrics may not be printed, read, copied, or used to stop, tune, retry, add a seed, or
change a threshold. Progress inspection is limited to process health, line counts, run IDs,
provenance, finiteness, hashes, GPU state, and exceptions. A hardware interruption may resume only
the identical run ID/checkpoint. Any scientific failure is preserved and disclosed rather than
repaired from its outcome.
