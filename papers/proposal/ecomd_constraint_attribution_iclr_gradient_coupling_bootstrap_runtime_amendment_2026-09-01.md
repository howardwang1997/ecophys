# Gradient-coupling Spearman bootstrap runtime amendment

Registered 2026-09-01T09:21:49Z, while the Advection factorial worker was still running with fewer
than 150 records, before any factorial metric or factorial analysis was inspected, and before any
formal gradient-coupling diagnostic record existed.

## Scope and defect

The frozen scientific protocol requires a 50,000-draw paired seed bootstrap interval for
Spearman's correlation between the local one-step interaction `D_I` and final rollout interaction
`I_seed`. The first analyzer implementation computed the full-sample ranks once and resampled
those fixed ranks. A nonparametric bootstrap sample contains repeated observations, so Spearman's
statistic must instead re-rank `D_I` and `I_seed` inside every paired resample. Resampling fixed
full-sample ranks is generally not the same statistic.

This amendment changes only that implementation detail. Every resample still draws 30 seed pairs
with replacement, uses the same deterministic RNG seed, recomputes the two average-tie rank
vectors, and evaluates their Pearson correlation. Degenerate constant-rank draws remain excluded;
fewer than 99% valid draws still fails closed. The point estimate, 50,000 draw count, percentile
95% interval, positive-support rule, seeds, data, optimizer, local estimand, final estimand, and all
factorial settings are unchanged.

## Immutable lineage

- scientific protocol SHA-256:
  `e99e6925cbb744ec4ac129e2a05b54fde27a862556963dc40b2954bfed8def78`;
- scientific decision SHA-256:
  `ba758bf50a4deb383a6ab6d1dbc093dcd00b432bfd862c5c5438f2911e88a634`;
- superseded analyzer SHA-256:
  `226ddfcf119f3f4468b8dc78f452d4990f45cdcc626cc4eef73627272ca21fa4`;
- preserved superseded snapshot SHA-256:
  `3d989bd9ac41b0d58a4e11f2d792e51d8e5881bae1131584b452cff46adaed9b`;
- corrected analyzer SHA-256:
  `3ce291bd38eaf51266b68ed5419b1fb453dc0ae36261e43e5526b9863f696d28`;
- regression-test source SHA-256:
  `a992ec0da1a5062f51b7b4f60337c2905934ac643c3d96ff0970e0e29a0c910e`.

The new regression test independently reconstructs every paired bootstrap draw, re-ranks within
that draw, and checks the emitted percentile interval. The complete PDEBench-focused test file
passes 35/35; Ruff passes the corrected analyzer and test file. A 50,000-draw runtime smoke on 30
synthetic pairs completed in 1.315 seconds. These synthetic values are software-test inputs, not
experimental outcomes.

## Activation and interpretation

Only a new versioned executable snapshot and machine decision may activate this correction. The
old snapshot is retained as superseded and must not be deployed. Activation remains conditional on
the Advection factorial reaching exactly 150 records and its training worker exiting. The
corrected diagnostic cannot modify a model run or be used to inspect partial factorial metrics.
The original frozen interpretation remains binding: only a positive Spearman interval wholly
above zero supports the local mechanism; a null, negative, degenerate, or zero-crossing result is
not mechanism support and cannot be reframed as robustness.
