# ICLR shallow-water training-by-inference enforcement cube freeze

Frozen 2026-09-02 NZST before any shallow-water HDF5 value, preflight metric, checkpoint, or
formal metric was accessed. This protocol is subordinate to, and cannot weaken, the public-data,
model, split, metric, and inference contract in
`ecomd_constraint_attribution_iclr_pdebench_swe_freeze_2026-09-02.md`.

## Scientific estimand

For output coordinate `c in {A,R}`, training enforcement `t in {0,1}`, and inference enforcement
`e in {0,1}`, construct all eight cells `Y[c,t,e]` on identical seeds, training subsets,
initializations, checkpoints, evaluation trajectories, resolutions, and horizons. The five core
records provide `A00`, `R00`, `A01`, `A11`, and `R11`. After the complete core file passes its
frozen analyzer, obtain exactly three missing records per seed with zero optimization:

- `R01`: apply the mass projector to the `free_res` checkpoint;
- `A10`: load the `hard_abs` checkpoint but evaluate through the compatible unprojected absolute
  forward map;
- `R10`: load the `hard` checkpoint but evaluate through the compatible unprojected residual
  forward map.

The state dictionaries are architecture-identical across mechanisms; only the registered forward
map changes. Every parent checkpoint must first be locked by path, bytes, SHA-256, run ID, schema,
and completed epoch count. The derived file contains exactly 90 records and every derived record
has `optimization_runs=0`, `examples_seen=0`, and `training_runtime_seconds=0`.

## Frozen analysis

For `D[t,e]=Y[A,t,e]-Y[R,t,e]`, report `D00`, `D01`, `D10`, `D11`,
`I_bundle=D00-D11`, `T0=D00-D10`, `T1=D01-D11`, `E0=D00-D01`,
`E1=D10-D11`, `J=T0-T1=E0-E1`, `phi_train=(T0+T1)/2`, and
`phi_infer=(E0+E1)/2`. Require both exact path and efficiency identities within `1e-12`.

The primary metric is conserving RMSE at native OOD-128/horizon-16, with all two-resolution by
four-horizon cells retained. Use the parent protocol's paired bootstrap, sign-flip, Holm, SESOI,
and ordered four-way classification. Apply the same cell construction descriptively to total RMSE,
mass drift, negative-depth fraction, and negative-depth deficit so a gain in conservation cannot
hide a loss of physical admissibility.

For every lower-is-better metric, also report the eight direct enforcement effects
`train_A_e0`, `train_R_e0`, `train_A_e1`, `train_R_e1`, `infer_A_t0`, `infer_R_t0`,
`infer_A_t1`, and `infer_R_t1`, using the sign convention unprojected/free-training minus
projected/hard-training. Report their coordinate-averaged training and inference effects and the
fully marginalized main effects. These are ordinary paired factorial effects, whereas `T0`, `T1`,
`E0`, `E1`, and `J` above are interactions of the output-coordinate contrast.

The prespecified conservation--positivity test uses native OOD-128 at the longest registered
horizon, 31. It averages the inference-projection effect over absolute and residual coordinates
while holding training enforcement off:

`psi_infer_free = 0.5 * [(Y[A,0,0]-Y[A,0,1]) + (Y[R,0,0]-Y[R,0,1])]`.

Compute this paired-seed contrast separately for maximum absolute invariant drift, mean negative
depth deficit, negative-depth fraction, and conserving RMSE, with a 95% paired-bootstrap interval.
Mean negative-depth deficit is the primary positivity outcome; negative-depth fraction is
secondary. Classify a resolved conservation--positivity trade-off only when the invariant-drift
interval lies strictly above zero and the negative-deficit interval lies strictly below zero.
Classify synergy when both lie strictly above zero. If the conservation gain is resolved but the
positivity interval contains zero, label the positivity effect unresolved. This gate was added
before data admission or any shallow-water outcome access and requires no additional training.

No derived metric may be read before exact 90-record coverage, unique run IDs, source provenance,
checkpoint binding, projection identities, file hash, and worker exit. No retraining, clamping,
seed replacement, or result-driven stopping is permitted.
