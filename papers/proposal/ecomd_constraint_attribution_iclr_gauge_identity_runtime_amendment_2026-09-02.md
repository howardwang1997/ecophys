# Gauge identity numerical-runtime amendment (2026-09-02)

Registered at `2026-09-02T04:37:09Z` after the original gauge-feedback runner
had written 10 of 60 records and then stopped with
`step-one gauge identity exceeded tolerance`. No metric from any partial record
was read. The 10-record file is frozen at SHA-256
`f55983ec19d258e5db3d04478cc629ba531ff5c677d831075cea9209dc6fa7ab`
and must be moved intact to an excluded directory before a fresh run.

## Numerical issue

The scientific intervention requires the first raw and projected states to
differ only along the uniform invariant direction. In exact arithmetic,
`project_mass` guarantees this by construction. The implementation evaluates a
float32 reduction over as many as 1024 cells, adds and subtracts the resulting
means from a possibly large raw prediction, and then subtracts the two stored
float32 states to audit their difference. A fixed `1e-6` absolute check can
therefore reject representational roundoff even when its non-invariant component
is negligible for the scientific estimand.

This amendment does not remove the original absolute tolerance. It replaces the
absolute-only audit with two simultaneous gates, frozen before the failing
residual or any feedback metric is inspected:

1. **IEEE-754 gate.** For each case, define `scale` as the maximum absolute
   magnitude encountered among the previous, raw, projected, and raw-minus-
   projected first states. Both identity residuals must be no larger than

   `1e-6 + 2048 * float32_epsilon * max(1, scale)`.

   The multiplier 2048 covers a worst-case 1024-term reduction plus the
   projection and audit arithmetic; it is fixed by the maximum grid size, not
   an observed result.
2. **Scientific-contamination gate.** The larger identity residual divided by
   the projected-history conserving RMSE must be no larger than `0.001`. This
   bounds representational leakage to 0.1% of the baseline, or 1% of the frozen
   10% practical feedback threshold. Passing the IEEE gate alone is
   insufficient.

The runner records `step_one_identity_scale_max_abs` so the analyzer can
recompute both gates independently. No feedback value, target, checkpoint,
trajectory, grid, seed, coordinate, case, estimator, bootstrap, 0.10 practical
threshold, or classification changes. The amendment also applies the already
authorized parent-analysis field correction to the gauge analyzer entry point:
the frozen cube binds `core_input_sha256` and `derived_input_sha256`.

## Fresh provenance run

- Preserve the original 10-record file unchanged under `excluded/` with its
  SHA-256 sidecar; never analyze or merge it.
- Use a new Hydra overlay, output JSONL, analysis JSON, amendment hash, decision
  hash, and therefore new canonical run IDs.
- Recompute all 60 zero-optimization records. Do not reuse the 10 partial
  records because their source manifests and metric schema predate this
  amendment.
- Reveal results only after exactly 60 records share one source manifest, both
  numerical gates pass for every case, all original parent hashes pass, and the
  analyzer exits successfully.
- If either numerical gate fails, terminate the direct gauge diagnostic and
  retain the paper's weaker timing-based mechanism statement. Do not relax a
  gate again or convert failure into a positive result.

