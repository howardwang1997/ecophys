# ICLR compute-authority amendment: evidence-limited rather than hour-limited

Date: 2026-08-30, after the PI explicitly directed that necessary experiments not be constrained
by the 25-hour limit, before any pilot ID/OOD analysis and before any confirmation run.

Parents:

- `ecomd_constraint_attribution_iclr_extension_freeze_2026-08-30.md`
- `ecomd_constraint_attribution_iclr_pilot_timing_amendment_2026-08-30.md`

## Budget authority

The former 25 V100-hour pilot and 120 V100-hour confirmation values are monitoring estimates, not
hard scientific stop conditions. GPU-hours, wall-clock, disk, failures, and energy proxies remain
recorded. Runs stop for safety, invalid provenance, failed implementation gates, exhausted
scientific value, or explicit PI direction—not merely because an hour counter is reached.

The already authorized B/C `{8,16}` by `{100,200}` pilot remains the first stage because it retains
the frozen minimum grid and avoids low-value cells. This is not a terminal budget reduction.

## ID-only expansion rule

The pilot selector continues to read only ID RMSE and compute proxy. If either primary comparison
(`free`--`free_res` or `free_res`--`hard`) lacks simultaneous 5% ID and 5% compute overlap on the
thinned B/C grid, run every omitted cell from the original grid using the same pilot seeds and arms:

- channels 32 at epochs 100 and 200;
- epochs 400 at channels 8, 16, and 32;
- both frozen learning rates.

Then rerun the selector once. OOD values remain unread until the lock is written. If the expanded
grid still lacks overlap, use the frozen fixed-compute branch; never widen the tolerance.
The omitted-cell job list is frozen in `configs/constraint_iclr/pilot_manifest_bc_expand.yaml`.

Apply the same rule to A/H/M2: if either primary comparison lacks simultaneous overlap, resume the
full original family grid and let append-only run IDs skip completed cells. A/H restore hidden 256,
epochs 800, and learning rate 0.01; M2 restores hidden 256 and learning rate 0.01. The frozen job
list is `configs/constraint_iclr/pilot_manifest_ahm_expand.yaml`; invoke only selected entries via
the launcher's repeatable `--job` option. Expansion decisions are made per system from ID and
compute only; an overlapping system is not expanded for symmetry.

## Confirmation strength

Before any confirmation seed is run, expand the confirmation partition from 20 to 30 paired seeds:
`{1000,...,1029}`. All 30 are now the inferential set; 20 is not an interim analysis. The paired
bootstrap, equivalence SESOI, Holm families, and all other decision rules are unchanged. A claim
requires all 30 scheduled seeds or a documented non-outcome-related hardware failure; there is no
outcome-driven early stopping.

This amendment changes compute authority and sample size only. It does not authorize new systems,
arms, metrics, OOD cases, tolerances, or claims.
