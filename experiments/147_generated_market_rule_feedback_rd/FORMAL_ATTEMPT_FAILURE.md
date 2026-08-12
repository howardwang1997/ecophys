# Experiment 147 formal-attempt failure

**Attempted:** 2026-08-13 06:02 NZST

**Checkout:** `2d14357fbaac1480d897e1ec09fc0ef3d2765897`

**Classification:** `IMPLEMENTATION_OR_SPEC_FAILURE`

## What happened

The single authorized formal command passed its external preflight: the local and remote branch SHA matched, the
checkout was clean, the output did not exist, all seven frozen file hashes matched and the four frozen package
versions matched. The runner then failed while constructing `ProcessPoolExecutor`, before a worker existed or a
Monte Carlo task was submitted:

```text
ProcessPoolExecutor.__init__
  -> concurrent.futures.process._check_system_limits
  -> os.sysconf("SC_SEM_NSEMS_MAX")
PermissionError: [Errno 1] Operation not permitted
```

The managed execution sandbox denied the semaphore-limit query. The traceback reached the `with
ProcessPoolExecutor(...)` constructor before `executor.map(_fit_task, ...)`; therefore zero generated panels and
zero `rdrobust` fits ran. `artifacts/raw/preflight.json` was not created.

## Scientific interpretation

This failure contains no evidence about RD false-positive control, coverage, power, bias, market feedback, EcoMD,
NMI or NCS. It cannot be relabeled as `GENERATED_RD_PREFLIGHT_FAIL`, because none of the statistical cells ran.
Experiment 147 remains immutable and ends as `IMPLEMENTATION_OR_SPEC_FAILURE`.

The only permitted repair is a separately preregistered Experiment 148 that changes the execution backend while
reusing Experiment 147's exact scientific configuration, stream labels, DGPs, estimator options, thresholds and
failure mappings. Running Experiment 147 again, including outside the sandbox, is forbidden by its one-run
contract.

## Resource audit

- formal attempts: 1
- Monte Carlo tasks submitted: 0
- generated panels: 0
- `rdrobust` fits: 0
- output artifacts: 0
- market/FITRS/price/paid/sealed files opened: 0
- network calls made by the runner: 0
- remote workers contacted or queued: 0
- GPU-hours: 0.0
