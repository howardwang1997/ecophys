# ICLR pilot expansion decision (ID-only)

Date: 2026-08-30, after both initial pilot workers completed and before any pilot OOD value was
inspected or analyzed.

Inputs: active pilot records only. The runtime-only aborted B partial was excluded. Provisional
selector output:
`experiments/constraint_attribution_iclr/pilot/pilot_lock_thin_20260830.json`, SHA-256
`9ad88f746bc0fd8bb03d81720747cd7beafd588201ff394af54600e654054cb2`.

The selector code accesses pilot ID RMSE and compute proxy only. All ten systems completed their
scheduled seeds and cells with finite metrics and valid provenance.

## Frozen expansion decision

`free_res`--`hard` passed simultaneous 5% ID and 5% compute overlap in all ten systems. The primary
`free`--`free_res` comparison passed in C-ad2d (relative ID gap 0.0021) and M2-FIFO (0.0142), so
those systems are locked without expansion.

The following systems enter the predeclared expansion because `free`--`free_res` did not overlap:

| system | thinned relative ID gap |
|---|---:|
| A-advection | 1.6470 |
| A-diffusion | 1.8791 |
| A-Burgers | 1.0617 |
| B-advection | 0.7317 |
| B-diffusion | 1.5644 |
| B-Burgers | 0.6975 |
| H-near | 1.6109 |
| H-strong | 1.4916 |

A/H resume the full original hidden/epoch/learning-rate grids. B resumes every omitted cell from
the full `{8,16,32}` by `{100,200,400}` grid. Existing append-only run IDs are skipped, so only
missing cells train. Seeds and arms remain 100--102 and the frozen four arms. C, M2, and all
confirmation jobs remain untouched.

After expansion, run the ID-only selector exactly once. If overlap is still absent, lock the
fixed-compute non-overlap branch. No further capacity search, tolerance change, or outcome-driven
adaptation is permitted.

