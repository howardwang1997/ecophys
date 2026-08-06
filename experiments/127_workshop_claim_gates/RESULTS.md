# Experiment 127 — Results and decision record

**Status:** active (analytic controls complete; learned-model execution in progress). This file includes
positive, null, failed, missing, and deviated outcomes.

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

Pending.

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

Pending.

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

Pending: E-A / E-B / E-C.

## Conditional Paper S rescue

Not queued until Paper E is frozen.

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
