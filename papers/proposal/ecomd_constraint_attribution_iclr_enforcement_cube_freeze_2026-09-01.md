# ICLR training-by-inference enforcement cube freeze

Frozen 2026-09-01 NZST while the fresh Advection factorial had 87/150 append-only records, before
its complete-result analysis, before any gradient-coupling record, and before Burgers data
admission or any Burgers model run. No partial formal metric was accessed. This is an outcome-blind
construct correction: multi-step projection changes subsequent inputs, so the bundled hard-versus-
free rollout contrast cannot by itself be called a training-only effect.

## Scientific question

For each absolute (`A`) or residual (`R`) output coordinate, separate whether the projector is used
during training from whether it is used at every autoregressive inference step. Let
`Y[c,t,e]` be conserving RMSE, where `t=0/1` denotes free/projected training and `e=0/1` denotes
unprojected/per-step-projected inference.

The already frozen four trained arms supply the diagonal endpoints:

- `free = Y[A,0,0]` and `free_res = Y[R,0,0]`;
- `hard_abs = Y[A,1,1]` and `hard = Y[R,1,1]`.

The existing absolute post-hoc projection supplies `Y[A,0,1]`. Without any new optimization, load
the exact completed checkpoints and derive the three missing evaluations:

- `projection_res = Y[R,0,1]`, the free-residual checkpoint with per-step projection;
- `hard_abs_unprojected = Y[A,1,0]`, the hard-absolute checkpoint evaluated through the compatible
  absolute/free forward map;
- `hard_res_unprojected = Y[R,1,0]`, the hard-residual checkpoint evaluated through the compatible
  residual/free forward map.

The FNO parameter tensors are identical in shape across forward maps. A derived evaluation must
load the parent checkpoint strictly, perform zero optimizer steps, and preserve the parent's seed,
training-index digest, initialization digest, and checkpoint SHA-256. These raw hard-trained
rollouts are diagnostic interventions, not recommended deployments.

## Frozen estimands

At every resolution-by-horizon cell define the coordinate contrast

`D[t,e] = Y[A,t,e] - Y[R,t,e]`.

The original bundled coordinate-by-enforcement interaction is

`I_bundle = D[0,0] - D[1,1]`.

Complete the enforcement sub-factorial on this coordinate contrast:

- `T0 = D[0,0] - D[1,0]`: training-enforcement credit under free inference;
- `T1 = D[0,1] - D[1,1]`: training-enforcement credit under projected inference;
- `E0 = D[0,0] - D[0,1]`: inference-projection credit after free training;
- `E1 = D[1,0] - D[1,1]`: inference-projection credit after hard training;
- `J = T0 - T1 = E0 - E1 = D[0,0] - D[1,0] - D[0,1] + D[1,1]`;
- `phi_train = (T0 + T1)/2` and `phi_infer = (E0 + E1)/2`.

The exact efficiency gate is

`phi_train + phi_infer = I_bundle`.

Here `J` is the coordinate-by-training-by-inference interaction. If it is practically material,
the training and inference credits depend on which is applied first, so report their path-averaged
Shapley values rather than selecting a favorable path. This decomposition refines rather than
replaces the already frozen bundled factorial result.

## Primary and inference

Use the same prospectively fixed OOD-512, horizon-16 cell, seeds, inference unit, 50,000 paired
bootstrap draws, confidence levels, and SESOI
`delta = 0.10 * mean(Y[R,0,0])` as the parent factorial. Classify `J` by the same ordered rules:
material nonadditivity, statistical nonadditivity below/crossing the SESOI, practical additivity,
or unresolved. Apply the existing 100,000-draw paired sign-flip procedure and Holm correction to
the 12 mandatory cube cells. This new classification cannot override or rescue the original
`I_bundle` classification.

The local gradient audit changes the training update but contains no rollout projector
intervention. Its scientifically matched primary association is therefore amended, before any
diagnostic record, to the seed-wise `T1` at OOD-512/horizon-16: the coordinate interaction of
training through the hard layer when both endpoints use projected inference. The originally frozen
association with `I_bundle` remains a labeled secondary result. Only a 95% paired-bootstrap
Spearman interval wholly above zero supports the proposed local training mechanism; a null or
reverse result cannot be reframed as robustness.

## Coverage and integrity gates

Run this audit separately for the fresh Advection block and, if admitted, the Burgers block. Each
30-seed PDE requires exactly 90 new derived records (three per seed) in a separate append-only
JSONL. For distributed Burgers execution, each preassigned 15-seed worker emits exactly 45 derived
records and the existing no-migration seed partition remains unchanged.

Before analysis require:

1. the parent core factorial has exactly 150 valid records and its frozen analyzer has passed;
2. all 120 trained checkpoints exist and match their parent record paths and SHA-256 values;
3. all 90 derived run IDs and seed/mechanism pairs are unique and complete;
4. every derived record reports zero optimization runs and the exact parent provenance bindings;
5. at horizon one, projected and unprojected evaluations of the same checkpoint have equal
   conserving RMSE within the inherited numerical identity tolerance;
6. hard/projection invariant drift passes the inherited threshold wherever inference projection
   is active;
7. all metrics are finite, source manifests are identical within a block, and every algebraic
   decomposition and Shapley efficiency identity passes at `1e-12`.

No derived or core partial metric may be inspected. Do not change a seed, checkpoint, data split,
grid, horizon, threshold, or interpretation from a result. A failure of a raw hard-trained rollout
is reported as failure of this cube audit; it cannot trigger retraining or clipping.
