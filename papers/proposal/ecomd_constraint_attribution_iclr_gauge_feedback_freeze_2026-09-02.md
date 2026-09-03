# ICLR direct gauge-feedback intervention freeze

Frozen 2026-09-02 NZST after the complete Advection factorial and enforcement cube had been
analyzed, and after the frozen gradient-coupling diagnostic failed to predict the final
training interaction, but before any record from this new intervention existed. This is a
targeted prospective mechanism follow-up, not an outcome-blind redefinition of the already known
cube result. No partial shallow-water model metric had been accessed at this freeze.

## Scientific question

The completed cube establishes a projection-gauge ambiguity and shows one-step equality followed
by multi-step divergence when a projector is removed from a hard-trained autoregressive model.
That timing is consistent with, but does not directly intervene on, the proposed feedback link:
an invariant-channel error in the predicted state changes the next input and may then alter the
network's conserving output channel.

For each locked `hard_abs` or `hard` checkpoint, evaluate its compatible raw forward map
`F_c` (`free` for absolute coordinates and `free_res` for residual coordinates) from the same
ground-truth history `s_0`. Let `x_0` be the last frame and define

`z_1 = F_c(s_0)` and `p_1 = Pi_x0(z_1)`.

Construct two histories by dropping the oldest frame and appending either `z_1` or `p_1`. They are
identical except for the invariant-direction difference `z_1 - p_1`. With the same weights and no
optimization, compute the second raw predictions

`z_2_raw = F_c(s_raw)` and `z_2_proj = F_c(s_proj)`

and the directly intervened feedback response

`Delta_Q = Q(z_2_raw - z_2_proj)`.

This design changes only the gauge component of the immediately preceding input. A non-negligible
`Delta_Q` is therefore direct evidence that the learned transition transfers an invariant-channel
input perturbation into admissible dynamics. It does not establish that this one transition
quantitatively explains every later rollout difference.

## Frozen estimands and decision rule

For every seed, coordinate, and resolution, pool the fixed 256 confirmation trajectories and all
grid cells. Define

- `feedback_rmse` as the RMS norm of `Delta_Q`;
- `projected_branch_conserving_rmse` as the conserving RMSE of `z_2_proj` against the true second
  target; and
- `feedback_ratio = feedback_rmse / projected_branch_conserving_rmse`.

The primary cell is the already established OOD-512 resolution. For seed `s`, average the absolute
and residual `feedback_ratio` values, preserving the seed as the inference unit. Use 50,000 paired
bootstrap draws and a two-sided 95% interval. The prespecified practical threshold is 0.10:

1. **material gauge feedback** if the 95% interval lies wholly above 0.10;
2. **practically negligible gauge feedback** if the 90% interval lies wholly within `[0, 0.10]`;
3. **unresolved** otherwise.

Because an RMS is nonnegative by construction, no claim is based on merely excluding zero.
Coordinate-specific and ID-256/OOD-1024 estimates are mandatory secondary results and cannot
override the primary classification. Apply paired bootstrap intervals to each and Holm-adjusted
paired sign-flip tests only to the absolute-minus-residual coordinate contrast, not to the
nonnegative RMS itself.

As a labeled secondary diagnostic, compute the paired-seed Spearman association between the
primary feedback ratio and the existing coordinate-averaged horizon-16 harm from removing the
projector from the same hard checkpoints. A 95% bootstrap interval wholly above zero supports
magnitude prediction; a zero-crossing or negative interval is reported as unsupported and cannot
be reframed as robustness.

## Frozen coverage and integrity

Use seeds 3000--3029, both hard-trained coordinates, the existing confirmation trajectories
0--255, history 10, and conservative ID-256/OOD-512/OOD-1024 restrictions. The experiment performs
zero optimizer steps and emits exactly 60 records (30 seeds by two coordinates) into a new
append-only JSONL. Every record must bind the existing core JSONL and analysis, cube JSONL and
analysis, 120-checkpoint lock, parent run ID, checkpoint SHA-256, initialization digest,
training-index digest, data lock, source manifest, and current Git provenance.

Before analysis require:

1. exact 60-record coverage with unique run IDs and seed/coordinate pairs;
2. byte- and SHA-identical parent checkpoints and exact compatible raw forward maps;
3. zero training runtime, optimization runs, examples seen, and proxy count;
4. `Q(z_1-p_1)` and the spatial non-constancy of `z_1-p_1` below `1e-6`;
5. strictly positive finite baseline denominators and finite reported metrics; and
6. one identical source manifest across all records.

Do not inspect a partial record metric, substitute a checkpoint, change the threshold or primary
resolution, add a clamp, perturb another channel, or retrain after seeing the result. To avoid
resource interference, activation on the Advection host must wait until its formal shallow-water
worker has exited. An unfavorable result rejects the material feedback claim; it is not converted
into a generic robustness contribution.
