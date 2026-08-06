# Experiment 127 — pre-held-out Hill-fraction sensitivity amendment

**Declared:** 2026-08-07 07:12 NZST and implemented in commit `33975c7c6` at 07:19 NZST, while both
V100 training services were active. Read-only audits at declaration and immediately after commit found
zero calibration or held-out trajectory files on either node.

The binding primary Hill estimator remains `k_frac=0.05`. Because Hill estimates can depend materially
on the tail fraction, the learned audit will also report `k_frac={0.025, 0.05, 0.10}` on the same
held-out trajectories, fixed 4,000-return windows, and calibration-frozen W-star values.

For each fraction, use the equal-weight mean of scorable E1 checkpoint median paired differences. Its
secondary 95% interval uses the common-seed crossed bootstrap declared in
`PREHELDOUT_ROBUSTNESS_AMENDMENT_2026-08-07.md`, with 2,000 replicates and seeds `127903`, `127904`,
and `127905` in ascending fraction order. Market-balanced leave-one-out values are also reported.

Only the 5% result can enter the frozen primary tier. The sensitivity grid cannot upgrade a null
primary result. A point-effect sign change or an interval that disagrees with the primary direction
must be disclosed and blocks tail-fraction-robust wording.
