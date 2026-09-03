# ICLR B/C pilot learning-rate correction

Date: 2026-08-30, discovered during a runtime-only ETA audit. No pilot OOD value had been opened,
and confirmation seeds 1000--1029 had not been run.

Parents:

- `ecomd_constraint_attribution_iclr_extension_freeze_2026-08-30.md`
- `ecomd_constraint_attribution_iclr_pilot_timing_amendment_2026-08-30.md`
- `ecomd_constraint_attribution_iclr_compute_authority_amendment_2026-08-30.md`

## Implementation discrepancy

The timing amendment freezes B/C learning rates `{0.0003, 0.001}`. The deployed thinned manifest
specified capacities and epochs but accidentally omitted `lr_grid`, so Hydra inherited
`pde_pilot.yaml` values `{0.001, 0.003}`. This is a configuration error, not an outcome finding.
It was identified from resolved configuration and record metadata only.

## Outcome-blind correction

1. Preserve every existing JSONL record append-only. Do not delete or rewrite the accidental
   `lr=0.003` records.
2. B expansion commands already use the frozen `{0.0003,0.001}` pair and therefore fill the
   required B cells while skipping existing `lr=0.001` run IDs.
3. Append the missing C-ad2d `lr=0.0003` cells for channels `{8,16}`, epochs `{100,200}`, arms
   `{free,free_res,hard,soft30}`, and pilot seeds 100--102. Supplying both frozen learning rates is
   permitted because append-only run-ID checks skip the completed `lr=0.001` cells.
4. The final ID-only selector admits only learning rates `{0.0003,0.001}` for families B and C and
   reports excluded-record counts in the lock. The accidental `lr=0.003` records cannot trigger an
   expansion, select a confirmation cell, or enter confirmation analysis.
5. Discard the provisional thin-grid lock after the corrected records are complete. Rerun the
   selector exactly once on the corrected eligible grid. If C then lacks overlap, apply the
   already frozen omitted-cell expansion rule before the final lock; otherwise do not expand C.

The PI explicitly authorized the C correction on `root@100.123.220.57`. It was queued behind the
existing V100b expansion lock as PID 171506. OOD remains blind throughout this correction.
