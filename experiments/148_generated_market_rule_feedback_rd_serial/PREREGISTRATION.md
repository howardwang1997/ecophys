# Experiment 148 — serial repair of generated annual market-rule-feedback RD preflight

**Frozen:** 2026-08-13

**Branch:** `endogenous-market-rule-feedback-v5`

**Parent experiment:** Experiment 147, closed `IMPLEMENTATION_OR_SPEC_FAILURE`

**Scientific role:** execution-backend repair only; no new DGP, estimator, gate or market evidence

## 1. Reason for a new experiment

Experiment 147's sole formal attempt failed inside `ProcessPoolExecutor.__init__` because the managed sandbox
denied `os.sysconf("SC_SEM_NSEMS_MAX")`. The exception occurred before worker construction, task dispatch,
generated-panel creation or `rdrobust` fitting. No output exists. The immutable evidence is
`experiments/147_generated_market_rule_feedback_rd/FORMAL_ATTEMPT_FAILURE.md`.

Experiment 147 cannot be rerun under its one-attempt contract. Experiment 148 repairs only orchestration: execute
the same frozen tasks serially in the controller process, without a process pool, thread pool, multiprocessing,
subprocess worker, semaphore or task queue.

## 2. Inherited scientific contract

Experiment 148 reads Experiment 147's configuration at
`experiments/147_generated_market_rule_feedback_rd/config.yaml`, SHA256
`fd594d5d4a8ff6e3eb548f726465adc6ff705b372f475e5b3df35c2a54f1b0fc`. It also freezes Experiment 147's
preregistration at SHA256 `3119a9a16774acedf061f28ec58aab61802fffaf8f0a8d1a2862508645d4cb68` and its generated-data
research module at SHA256 `dc9b2f0e6a45e1a91919c78dafd9a6b7ae7b736e7c7d2ee0727d61b7188dfa6d`.
The Experiment 147 runner's pure task, summary and diagnostic helpers are reused at SHA256
`dfdbded9bebd87f2068a9dc9dee22cca8dc51ee0d97dc272b719f065d87e2bec`; its failed process-pool entry point is
never called. The failure record is fixed at SHA256
`da90698d772240746a4dd2ac99f3511bb6bb6d2bf447125075df6fcf2241158f`.

The following are inherited byte-for-byte or semantically without change:

- seed `14720260813`, SHA256 stream labels and replicate indices;
- 300 replicates per cell, six years and 240 candidates per year;
- all standard, rounded, curved, regression-to-mean, MCAR, clustered, reinforcing, corrective and mixed-exposure
  DGP parameters;
- all 22 scenario/cutoff/noise cells: ten gated null, six gated `sigma=0.10` effect and six descriptive
  `sigma=0.20` effect cells;
- official `rdrobust==2.0.0`, local-linear `p=1`, bias correction `q=2`, triangular kernel, `mserd`, HC3/CR3,
  year covariates, mass-point adjustment and robust bias-corrected inference;
- the fixed-bandwidth known-curvature oracle and its six null/cutoff cells;
- all false-positive, coverage, Wilson, power, sign, median-bias, fit-failure, oracle and diagnostic thresholds;
- sorting, attrition, coarse-support, shared-RTS-28 and statutory tick-first-stage guards; and
- all interpretation, real-data locks and stop rules in Experiment 147's preregistration.

The exact expected work is 6,600 primary `rdrobust` fit tasks, 1,800 oracle constructions, 300 sorting diagnostics,
300 differential-attrition diagnostics, 300 coarse-support diagnostics and the frozen deterministic rule cases.
Task ordering is the Experiment 147 runner's cell order followed by replicate order `0..299`. Because every random
stream is label-derived, serial scheduling must not change a generated draw.

## 3. Sole permitted implementation change

The Experiment 148 runner must reuse the immutable Experiment 147 data generator, estimator adapter, `_fit_task`,
`_cell_summary` and `_diagnostics` helpers. It replaces only this operation:

```text
ProcessPoolExecutor(...).map(_fit_task, task_list)
```

with the equivalent serial operation:

```text
[_fit_task(task) for task in task_list]
```

It must not instantiate `ProcessPoolExecutor`, any other executor, multiprocessing, a thread pool, a subprocess
worker or a semaphore. A focused test must statically inspect the Experiment 148 runner for these forbidden
symbols and dynamically show that task execution occurs in the controller PID.

One controller process and one numerical thread are the complete execution pool. Experiment 147's scientific
configuration remains immutable; `execution_config.yaml` overrides only the tighter execution-resource audit.

## 4. Failure and result mapping

The result decision vocabulary is unchanged:

- all applicable statistical and diagnostic gates pass: `GENERATED_RD_PREFLIGHT_PASS`;
- any applicable statistical or diagnostic gate fails: `GENERATED_RD_PREFLIGHT_FAIL`;
- estimator/API/hash/version/resource/orchestration failure, including zero successful fits in any gated cell:
  `IMPLEMENTATION_OR_SPEC_FAILURE`.

No partial scientific pass exists. Descriptive `sigma=0.20` cells cannot affect the overall decision. Fit-failure
denominators, successful-fit denominators, Wilson intervals and cell-by-cell non-pooling rules remain exactly as
specified in Experiment 147.

## 5. Chronology

1. Commit and push this preregistration, README and execution configuration before an Experiment 148 runner,
   focused test, freeze or output exists.
2. Implement only the serial orchestration layer; do not edit any frozen Experiment 147 file.
3. Run deterministic focused tests only, then commit and push the implementation.
4. Commit and push `FREEZE.yaml` with both preregistration and implementation commits, exact parent/repair hashes,
   dependency versions and preformal checks.
5. From a clean checkout, make exactly one formal attempt and write
   `artifacts/raw/preflight.json` only after all cells finish. Refuse overwrite and partial checkpoints.
6. Any scientific change requires a new experiment. Any second execution repair requires Experiment 149; do not
   rerun Experiment 148.

## 6. Resource and data boundary

- Generated constants only; no market, FITRS instrument, price, paid, R2, user or sealed data.
- Mac CPU only: one controller process, one numerical thread, at most 12 CPU core-hours, 8 GB RAM and 90 minutes.
- Network prohibited by the same Python audit-hook contract; CUDA and ROCm hidden before numerical imports.
- V100-A, V100-B and RTX2060 are neither contacted nor queued; GPU-hours are zero.
- A PASS authorizes only preparation of the still-blocked real-data/licence preregistration. It does not unlock an
  instrument value or raise an NMI/NCS claim by itself.
