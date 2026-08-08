# Experiment 127 — Results and decision record

**Status:** complete; frozen tier **E-B**. This file includes positive, null, failed, missing, and
deviated outcomes.

## Integrity and provenance

- Analytic generation and analysis ran in the clean detached worktree at
  `2734ee9351293bd72c1afe73bd5af2ef7c0a1e7e`.
- Frozen parameter SHA-256: `a79399356aea22b100bc20029389a58584869813761960bf386452e1fde16e1a`.
- Generation-manifest SHA-256:
  `40a2d20da66003b6ac8c0161c0708c37cd019f407558f4f031bb6ed5ba23f439`.
- Analytic-results SHA-256:
  `7dc0f7db254da01e666ffa8616b1a1b9f1d2bd44b3beb1fae38caa0f26e202ce`.
- Archived records: `ANALYTIC_GENERATION_MANIFEST.json` and `ANALYTIC_RESULTS.json`. The seven raw
  `(1000, 8000)` `float64` arrays remain outside git; their individual hashes are frozen in the
  generation manifest.
- V100 execution uses compatibility commit `22a6e41628d7cca7688ecdf5513e5a5bb014e462` with
  PyTorch `2.3.1+cu121`, CUDA runtime 12.1, and an `sm_70`-capable wheel.
- All 160 calibration trajectories were retrieved and hash-verified before gate fitting. The gate was
  frozen at `2026-08-07T16:42:36.931108+00:00` with zero held-out trajectories; the first held-out
  trajectory was written at `2026-08-07T16:49:13+00:00`.
- Raw controller gate/result SHA-256 values are
  `8c3ac123c999dc1bffee03b7bc31083312ffc13f60294879ff7aaa693e02f074` and
  `2c3d3c5e266b7327482867146edccf3799cd681d88ce1c334e9fd6622aae1b8e`.
  The committed review copies replace only the absolute repository prefix in provenance paths; their
  SHA-256 values are `6ec6a372348efa49fc23cbc7d8152682a86cff55e49d32b9f79061d7da5a4b57`
  and `0af68915b481b7fbc75f8285b9189b0e85065a19d42a65dcf737ba9033ddc8e1`.

## V100 probes

The exact `N=10000`, FP32, `chunk_steps=24`, ten-iteration training probe passed on both 32 GiB
V100s. The two nodes produced the same checkpoint SHA-256
`f9b84705f013f14b9125ec80509b6bb194aee2b51c8f604183c3fd1ea0d7b8bc`.

| node | training time | peak allocated | peak reserved | result |
|---|---:|---:|---:|---|
| `v100_a` | 480.323 s | 14.141 GiB | 15.031 GiB | pass |
| `v100_b` | 478.675 s | 14.141 GiB | 15.031 GiB | pass |

The identical-seed, 8000-return inference probe also passed. It took 388.309 s on `v100_a` and
383.879 s on `v100_b`, with 3.419 GiB allocated and 3.814 GiB reserved. Both nodes produced the same
trajectory SHA-256 `b8d7ac6f733a0db33c3a07c954ce11cb05df33217d1a04a21dee6cbcc28d7a4d`;
all inference fields other than wall time were identical. `V100_PROBE_RESULTS.json` freezes the full
probe metadata. Production retraining began as two resumable systemd services after this pass.

## E1 learned-model held-out scoring

All seven primary checkpoints produced a calibration W-star. Six of seven passed the held-out
three-block transfer rule; the gold concave checkpoint failed transfer and remains in the denominator
and effect estimate. The equal-weight mean of checkpoint median paired Hill differences was `+6.1192`
with primary hierarchical-bootstrap 95% interval `[+5.4287, +6.9879]`. Every primary checkpoint had a
positive median difference. This passes the frozen direction/effect test but not the seven-of-seven
transfer requirement for E-A.

The pre-held-out common-seed bootstrap gave `[+5.4437, +7.0558]`. The market-balanced effect was
`+6.3720`; leave-one-market-out effects ranged from `[+5.8417, +6.6672]` and were all positive. The
Hill-fraction grid was also consistent: crossed-bootstrap intervals were `[+7.8180, +9.9631]` at
2.5%, `[+5.4270, +7.0038]` at 5%, and `[+3.0414, +4.2420]` at 10%. These secondary analyses support
robust direction but cannot upgrade the binding tier. `LEARNED_ROBUSTNESS.json` has SHA-256
`155a663a2eae4dc28a9c6115e0a101a063cf405d95cd98d58cc7e62324bc5e7e`.

## E2 analytic controls

Completed all seven frozen conditions: 1000 trajectories per condition, 8000 returns per trajectory,
partitioned into 31 independent 16-calibration/16-held-out pseudo-checkpoints.

The primary specificity gate passed. On the pooled stationary controls, the energy gate flagged
`1/62 = 1.61%`; its Wilson 95% interval was `[0.29%, 8.59%]`, below the pre-registered 15% upper-bound
criterion. Frozen-W transfer passed on 188/217 (86.6%) analytic pseudo-checkpoints.

Sensitivity was limited and heterogeneous rather than universal:

| condition | detections | rate (Wilson 95%) | median resolved W |
|---|---:|---:|---:|
| GARCH-t cold-low | 2/31 | 6.45% [1.79%, 20.72%] | 0 |
| GARCH-t cold-high | 19/31 | 61.29% [43.82%, 76.27%] | 500 |
| AR(1)-SV cold-low | 4/31 | 12.90% [5.13%, 28.85%] | 0 |
| AR(1)-SV cold-high | 3/31 | 9.68% [3.35%, 24.90%] | 0 |

Pooled cold-start detection was `28/124 = 22.58%` (Wilson 95% `[16.11%, 30.70%]`). Therefore the
energy method is a conservative contamination gate, not a high-power universal transient detector.
The fixed-500 and fixed-1000 rows mechanically count every case as a discard/detection, so their 100%
"detection" rates are not evidence of sensitivity.

## E3 within-EcoMD architecture variant

Two variants were scorable and both had positive median Hill differences (`+5.2130`, `+5.4759`).
Variant 0 failed held-out gate transfer, variant 1 passed, and variant 2 produced no calibration
W-star within the frozen horizon. Because the frozen E3 rule requires all three to be scorable before
counting a two-of-three sign replication, `e3_same_positive_sign_2_of_3` is false. This blocks broad
within-family transfer wording.

## E4 method baselines

The classical ADF/KPSS rule is not a viable replacement: its pooled stationary false-positive rate
was 50.0% (Wilson 95% `[37.92%, 62.08%]`) and it was unresolved on 30/31 long-burn GARCH-t
pseudo-checkpoints. The energy gate's pooled median cold-condition Hill error was 0.0507, versus
0.0594 for fixed-500 and 0.0533 for fixed-1000, but its pooled mean error was worse (0.0966 versus
0.0910 and 0.0846). Both summaries will be reported; the median-only advantage is insufficient by
itself for a broad methods claim.

A literature audit after the primary analytic result was frozen identified MSER-5 as a missing
classical warm-up comparator. The method and reporting rule were declared in
`EXPLORATORY_AMENDMENT_2026-08-07.md` before its output was inspected; this analysis is post-primary
and cannot change the registered Paper E tier. MSER-5 selected a nonzero discard in 16/62 (25.81%)
stationary pseudo-checkpoints and 76/124 (61.29%) cold-start pseudo-checkpoints. Its pooled cold-start
Hill absolute error was 0.0491 by median and 0.0847 by mean. Thus it was more sensitive than the
energy gate but paid a substantially higher stationary unnecessary-discard rate; the energy gate does
not have uniformly lower tail-score error. The full 217-row record is frozen in
`EXPLORATORY_MSER5_RESULTS.json` (SHA-256
`4940621cb88518438d2e4340a4f8af29257bd310deb39e5a4aa21eec0c74c566`).

## Paper E tier decision

**E-B: simulator-specific case study/protocol audit.** E1's positive held-out effect, analytic
specificity, common-seed robustness, market leave-one-out checks, and Hill-fraction sensitivity pass.
E-A is blocked by one of seven primary held-out transfer failures, one unresolved E3 gate, one E3
transfer failure, and mixed rather than uniformly superior baseline performance. E-C is not triggered:
the primary effect does not vanish, fixed-length scoring is maintained for all seven E1 checkpoints,
and no target leakage or post-hoc threshold change occurred.

## Conditional Paper S rescue

Paper E is now frozen at E-B. Paper S/STODY remains unqueued until the Sim2Science manuscript and
artifact are frozen; no rescue experiment may alter the Paper E claim or thresholds.

## Deviations, failures, and missing artifacts

- H20 is inaccessible; original exp108/113/114 checkpoints could not be recovered from the current R2
  checkpoint archive. Per the frozen plan, exp127 retrains all required learned checkpoints and treats
  them as new artifacts.
- The first remote probe invocation failed before iteration 0 because PyTorch 2.3 does not expose
  `torch.amp.custom_fwd/custom_bwd`. Commit `22a6e41628d7cca7688ecdf5513e5a5bb014e462`
  introduced a version-compatible AMP decorator shim. Targeted tests passed before the probes were
  rerun with unchanged scientific configurations and seeds. The failed invocation remains in the
  append-only remote logs.
- The repository-wide local test command was terminated by the host resource limit (exit 137) after
  roughly 65 tests and before completion; no assertion failure had appeared. This is not recorded as
  a full-suite pass. The changed-scope test suite, Ruff, and strict mypy checks passed.
- Two Mac-side controller processes exited during remote execution: the first encountered a collected
  transient systemd unit after training, and the second misclassified an SSH transport outage as an
  unknown terminal unit. Remote systemd workers continued and their status/artifact hashes were
  preserved. Commits `46125b44c` and `6d21459e7` harden supervision; neither changes the frozen
  scientific worker or execution SHA.
