# Exploratory amendment: classical warm-up comparator

**Timestamp:** 2026-08-07 NZST, after the primary analytic results were inspected but before any
learned calibration or held-out rollout was available.

**Status:** exploratory only. This amendment cannot change the pre-registered E-A/E-B/E-C tier,
specificity gate, learned estimand, or stopping rule.

The literature audit identified a missing classical simulation-output comparator: MSER-5. The frozen
primary comparison already contains no discard, fixed discards, and ADF/KPSS. MSER-5 is added only to
show how a standard mean-oriented initialization-bias heuristic behaves when the downstream score is a
distributional tail functional.

The implementation is fixed before its output is inspected:

1. For each analytic pseudo-checkpoint, use only its 16 calibration trajectories.
2. Form the across-trajectory mean absolute-return series at every time point. This is independent of
   the Hill target used for scoring.
3. Average that series into non-overlapping batches of five observations.
4. Choose the smallest deletion index minimizing the marginal-standard-error statistic
   `sum((z - mean(z))^2) / n_remaining^2`, with deletion restricted to at most half the 8,000-return
   horizon (`W <= 4000`).
5. Transfer the selected `W` without refitting to the 16 held-out trajectories and compute the same
   fixed-length 4,000-return Hill score.
6. Report every selected deletion, stationary unnecessary-discard rate, cold-start selection rate,
   and absolute Hill error relative to the matched stationary no-discard reference.

Any favorable or unfavorable result remains labeled post hoc. MSER-5 targets steady-state means and is
not expected to be a universal distributional convergence test; that mismatch is part of the diagnostic
comparison, not evidence that the classical method is defective.
