# Open NEMDE replay-engine audit

**Date:** 2026-08-15

**Decision:** `NO_INDEPENDENT_REPLAY_YET_USE_NEMPY_FOR_INPUT_RHS_PREFLIGHT`

## Bottom line

Neither audited open implementation currently supports the paper-level statement that EcoPhys can independently
reproduce production NEMDE from the published applied inputs. Both standard historical-recreation paths read at
least the realized generic-constraint right-hand sides from `NemSpdOutputs`. Their reported price, target or
objective agreement is therefore a useful **solution-assisted engineering baseline**, not yet an input-only
mechanism validation.

Nempy is nevertheless the right primary engine to audit further. Its current codebase is maintained, BSD-licensed,
compatible with modern Python and contains a separate evaluator for recomputing dynamic RHS expressions from
`NemSpdInputs`. The immediate experiment should test that evaluator on the two already consumed production cases,
with all output RHS values replaced by sentinels during computation. It needs no new AEMO request, no paid data and
no GPU.

## Audited implementations

### Nempy

- Repository: [UNSW-CEEM/nempy](https://github.com/UNSW-CEEM/nempy), audited commit
  [`2d3cef0e5545c820067fecddfa2e2fd984ac5583`](https://github.com/UNSW-CEEM/nempy/commit/2d3cef0e5545c820067fecddfa2e2fd984ac5583),
  package version 3.0.3, last commit 22 October 2025, BSD-3-Clause.
- The standard `ConstraintData` path calls `RawInputsLoader.get_constraint_rhs()`. That delegates to
  `XMLCacheManager.get_constraint_rhs()`, which reads `ConstraintSolution/@RHS` from `NemSpdOutputs`, filters the
  chosen intervention solution and passes those values to the optimization model.
- The detailed historical example also requires MMSDM tables for unit details, AGC limits, network definitions,
  loss models and observed comparison prices. It is not an XML-only replay. The current example warns of roughly
  54 GB of downloads for its month-scale setup; that number does not apply to our bounded one-day route.
- Nempy's `RHSCalc` separately parses RHS equations, SCADA values, entered values, initial unit output and MNSP
  availability from `NemSpdInputs`. Its `compute_constraint_rhs()` can therefore be tested as an input-side
  mechanism component. The constructor also loads production RHS for testing, so output-sentinel invariance is
  required before treating computed values as leakage-free.
- The documented evaluator does not implement the historical `BRANCH` operation and the authors report small
  differences for some equations. Coverage and error must be measured, not assumed.
- The time-sequential example omits generic constraints because their RHS would have to be recomputed from the
  evolving simulated state. It also notes that replaying historical bids under a changed state is behaviorally
  inconsistent. This is exactly the mechanical-versus-adaptive decomposition relevant to the main paper.

### akxen/nemde

- Repository: [akxen/nemde](https://github.com/akxen/nemde), audited commit
  [`23afcdf128352f12d3074194a1321a8f810f4407`](https://github.com/akxen/nemde/commit/23afcdf128352f12d3074194a1321a8f810f4407),
  last commit 8 August 2021, Apache-2.0.
- Its README correctly calls the model a reverse-engineered approximation because the production formulation is
  not public.
- `casefile_serializer.get_generic_constraint_rhs()` reads `ConstraintSolution/@RHS` from `NemSpdOutputs` and
  stores it as `P_GC_RHS` in the model. The default validation test then compares its solved objective with the
  production objective and accepts relative error at most `0.001`.
- Here `run_mode="target"` selects the target/physical intervention solution rather than fixing every decision
  variable to production targets. The material leakage is narrower but still decisive: realized production RHS is
  part of the solved model.
- The frozen stack uses Pyomo 5.7.3, MySQL/Docker and 2021-era dependencies. It is useful as a second formulation
  reference, but it is a higher-risk production dependency than current Nempy.

## Claim taxonomy

| Label | Inputs allowed | Scientific use | Current status |
|---|---|---|---|
| production consistency | production output can be read throughout | parser and accounting checks | available |
| solution-assisted replay | applied inputs plus realized RHS/flags from output | upper-bound engineering baseline | both engines |
| input-side RHS reconstruction | applied inputs; output used only after computation for scoring | tests one important mechanical layer | next gate |
| input-only independent replay | no realized output enters formulation or solve | mechanism-fidelity claim | not available |
| counterfactual mechanism replay | changed rules/state solved without realized outcomes | intervention engine | not available |
| behavioral adaptation | participant information predicts changed actions | main economic claim | requires separate data/model |

This taxonomy must appear in every later replay result. In particular, a near-zero price error from a
solution-assisted model cannot be promoted to evidence that the market mechanism or participant behavior has been
learned.

## Selected next gate

Run a two-case, R2-only Nempy RHS reconstructibility preflight:

1. pin the exact Nempy commit and source-file hashes;
2. materialize the two previously retained 1 MiB ranges from R2 and reproduce XML size, CRC and SHA;
3. extract production RHS only as a sealed reference table;
4. replace every output RHS with two different sentinel assignments before constructing `RHSCalc`;
5. compute every input-side dynamic RHS equation under both sentinels;
6. require identical computed values across sentinels, report evaluation coverage and compare to the sealed
   production reference using frozen normalized-error summaries;
7. preserve all failures and unsupported operations rather than dropping them.

A pass unlocks a one-day temporal-schema/alignment protocol and the design of paired solution-assisted versus
input-only solver arms. It does not unlock a replay claim, Experiment 156, learned surrogate or GPU training. A
partial/fail result identifies the exact missing mechanical state that EcoPhys must model or source.

## Data and compute

- **New AEMO bytes:** zero; reuse two immutable R2 objects totaling 2 MiB.
- **New paid data:** zero.
- **Local dependencies:** pinned Nempy source plus `xmltodict==0.12.0`; the RHS preflight does not require `mip` or
  a mathematical solver.
- **Compute:** Mac CPU, expected seconds to minutes, less than 1 GB RAM.
- **GPU:** zero V100/2060 hours. All three workers remain available for later model work only after mechanism gates.

## Consequence for the research story

The replay layer should be split explicitly into two objects:

`published applied case -> mechanical dispatch solution`

and

`information/history + announced mechanism -> participant action distribution`.

The first can be validated against production NEMDE cases. The second is where Lucas-style adaptation and the
larger economic story live. A simulator that conflates them can obtain good in-regime fit by borrowing realized
mechanical state while failing exactly when the rule changes. Measuring that separation is potentially useful for
NCS; merely cloning historical dispatch is not.

## Protocol freeze update

The R2-only two-case gate is frozen at
`experiments/v14_aemo_nemde_rhs_reconstruction/PREREGISTRATION.md`, manifest SHA-256
`b56f40999518a7e2df657ea7480a85f0f855a9d8ee8151b6f7cf4f76c99ab7cd`. It fixes dual sentinels, all-equation
retention, exact engine hashes and per-case coverage/error gates before any production RHS value is reopened for
this experiment. No full-day download or solver install is authorized by the freeze.

## Executed gate update

The gate returned `PARTIAL_INPUT_SIDE_DYNAMIC_RHS_RECONSTRUCTION`. Leakage integrity passed and more than 99.7%
of dynamic equations were scored in both cases, with exact dual-sentinel invariance and median normalized error
below `5e-10`. But the pre-registered p95 ceiling failed in both regimes (`0.00416664` and `0.00194488` versus
`0.001`). This confirms the audit's warning: default production-RHS assistance can hide a sparse but material
mechanical tail. The original gate is not relaxed; only a post-hoc tail-mechanism diagnostic is next.

## Repair-path disposition

The subsequent official-rule and development audits did not unlock input-only replay. An identifier-tree
interpretation of nested `GroupTerm` relations recovered the four evaluation exceptions but worsened normalized
p95 from `0.00416664/0.00194488` to `0.50073642/0.31578724`, with 57/63 strict regressions. It is rejected without
fresh validation. Public sources also did not specify SCADA duplicate/quality/default selection.

The free open-source boundary is now explicit: Nempy remains a useful solution-assisted engineering baseline and
production RHS may be treated as a declared observed state, but it is not a validated input-only counterfactual
engine. Exact NEMDE mechanism replay requires additional authoritative formulation access rather than more
target-conditioned patches. Development result:
`experiments/v14_aemo_nemde_rpn_repair_development/RESULTS.md`.
