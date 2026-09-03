# ICLR pilot timing amendment: B/C convolution grid

Date: 2026-08-30, after remote CUDA preflight and the first B-advection timing cell, before any
pilot OOD metric was inspected or analyzed.

Parent protocol:
`papers/proposal/ecomd_constraint_attribution_iclr_extension_freeze_2026-08-30.md`.

## Runtime-only observation

On V100b, the first `B:advection`, channels 8, epochs 100 arms took approximately 33 seconds per
trained arm. All values were finite and the CUDA/provenance gates passed. Only record counts,
runtime, finite status, process state, and GPU memory/utilization were read. ID and OOD values were
not read.

Quadratic channel scaling gives an approximately 31 V100-hour projection for one B system under
the initial `{8,16,32}` by `{100,200,400}` grid. That violates the parent protocol's 25 V100-hour
hard cap before the remaining B/C systems, so continuing the initial grid is forbidden.

## Amended B/C grid

Use the parent protocol's predeclared thinning order:

- channels `{8,16}`;
- epochs `{100,200}`;
- learning rates `{0.0003,0.001}`;
- mechanisms and pilot seeds unchanged: `{free,free_res,hard,soft30}` and `{100,101,102}`.

This retains the required minimum of two capacities, two epoch counts, and two learning rates.
A/H/M2 grids are unchanged. The B/C process was terminated by process group after a completed
record boundary; its partial runtime-only file is moved intact to an excluded `runtime_only_aborted`
directory. The thinned run starts a fresh output file and never pools the aborted records.

If runtime-only projection after the first complete thinned B system still puts the total pilot
above 25 V100-hours, stop before the next system. Do not thin again, inspect outcomes, or substitute
confirmation seeds; instead drop the unaffordable family from the ICLR claim.

Executable manifest: `configs/constraint_iclr/pilot_manifest_bc_thin.yaml`.

