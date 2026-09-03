# PDEBench v2 deployment amendment (2026-09-01)

## Scope

This is a deployment-test-only amendment to the frozen PDEBench v2 confirmation.
It does not change the benchmark bytes, conservative restriction, model, mechanisms,
training grid, evaluation grid, seeds, stopping rule, selector, or analysis plan.

## Trigger

The first external-host test run against snapshot
`6392bb2a7b217e06e9d79ffde55afd57612d2cc9c815f130ccc6eeccc0078970`
passed 18 of 19 tests.  The sole failure occurred before any CUDA model run because
`test_frozen_config_has_thirty_new_seeds_and_primary_case` still loaded the obsolete
v1 filename `pdebench_advection_fno.yaml`.  That file is neither a runtime dependency
of v2 nor included in the v2 snapshot.

## Correction

The test now loads `pdebench_advection_fno_v2.yaml`, the same frozen config already
validated by the adjacent v2-specific test.  No assertion changed.

- Previous test SHA-256:
  `216e97bc6fcd1cd29edc01bd41d3a97e536fcc364d3a83768c6d00f33ea793f2`
- Corrected test SHA-256:
  `18042f3d14be158c502c03f41ba0dbff726ace6feb0a325b29ed9405080aafb5`
- Frozen v2 config SHA-256 (unchanged):
  `6bdea758e343cbe0b3676663e36cfc082f66b1719fb670800a276d88aee7231e`
- Frozen v2 protocol SHA-256 (unchanged):
  `01d300410364b07e779c2c2462cdd60f720a24a86622675f4df0f7c604724307`

## Gate

The corrected local suite must pass 19/19 tests and Ruff before packaging.  The
external host must verify the replacement archive and every included file, then pass
the same 19/19 tests.  The old archive remains preserved as the rejected deployment
candidate.  No preflight or formal CUDA run may use it.

The execution authority is the user's explicit confirmation on 2026-09-01 to proceed
with v2.  This amendment repairs an executable test reference only and does not expand
that scientific authority.
