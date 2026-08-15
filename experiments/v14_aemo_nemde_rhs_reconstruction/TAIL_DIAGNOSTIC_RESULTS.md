# Post-hoc NEMDE RHS tail diagnostic result

**Status:** descriptive only; original decision remains
`PARTIAL_INPUT_SIDE_DYNAMIC_RHS_RECONSTRUCTION`

**Diagnostic commit:** `94204d8c3d1b875389bc4568eda0835509f7ee9a`

**Artifact SHA-256:** `5c51257ed48c54b4b2164c83729332dd1288438444c1e35fd14dc7022fe80348`

## Bottom line

The failed p95 gate is not random floating-point noise and is not explained by one mechanism. Three structured
failure modes appear:

1. **RPN group-boundary implementation defects.** All four unevaluated equations terminate at Nempy
   `_rpn_stack` line 555, which reads `equation[i + 1]` for a group term without checking that a next term exists.
   The same source block also references `group.pop` without calling it. These are concrete software defects, not
   missing production RHS.
2. **A small catastrophic group-expression family.** The nine largest pre-5MS errors are all
   `Q_NIL_STRGTH_*` constraints with normalized error `0.9880--0.9968`; each has the same 83 expanded group terms
   and 17 generic references, with no unresolved lookup or flagged SCADA entry. The largest post-change error,
   `Q>YLTX_DS` at `0.500001`, is also group-structured and has neither unresolved nor flagged SCADA input.
3. **A broader input-resolution/SCADA tail.** Equations referencing multiple SCADA entries exceed the original
   `1e-3` boundary in 52.8% pre-5MS and 49.4% post-change, versus 17.2% and 9.52% overall. Equations with an input
   not found in the pinned resolver's maps exceed it in 36.7% and 26.3%. The source evaluator sums multiple SCADA
   rows and does not enforce the available EMS quality flags. This is an association, not yet proof of the correct
   AEMO selection rule.

One ad-hoc patch cannot fairly test all three. The repair experiment should be factorial: pinned baseline,
RPN-group repair only, specification-grounded input/SCADA resolution only and combined repair. Development may use
the consumed cases; evaluation must use fresh mechanically selected intervals.

## Fixed threshold counts

| Normalized error above | Pre-5MS (n=772) | Post-5MS/WDR (n=882) |
|---:|---:|---:|
| `1e-8` | 294 (38.08%) | 232 (26.30%) |
| `1e-6` | 291 (37.69%) | 227 (25.74%) |
| `1e-4` | 238 (30.83%) | 144 (16.33%) |
| `1e-3` | 133 (17.23%) | 84 (9.52%) |
| `1e-2` | 14 (1.81%) | 3 (0.34%) |
| `0.1` | 9 (1.17%) | 1 (0.11%) |

The tail is therefore a structured minority, not merely four exceptions. Median-only reporting would still hide
84--133 equations beyond the original operational tolerance.

## Exception localization

| Case | Constraint | Direct / expanded terms | Group terms | Generic refs | Terminal |
|---|---|---:|---:|---:|---|
| pre | `Q_NIL_STRGTH_MEWF` | 90 / 437 | 189 | 30 | `_rpn_stack:555` |
| pre | `S_NIL_STRENGTH_1` | 396 / 1,710 | 686 | 17 | `_rpn_stack:555` |
| post | `DSNAP_T_ROCOF_3` | 15 / 15 | 8 | 0 | `_rpn_stack:555` |
| post | `N^^N_NIL_3` | 37 / 37 | 5 | 0 | `_rpn_stack:555` |

All have zero unresolved input terms. This directly falsifies the idea that those four exceptions can be repaired
only by sourcing more state.

## Descriptive enrichment

| Feature | Pre tail / feature n | Pre rate | Post tail / feature n | Post rate |
|---|---:|---:|---:|---:|
| unresolved resolver input | 77 / 210 | 36.67% | 44 / 167 | 26.35% |
| multiple SCADA entries | 47 / 89 | 52.81% | 41 / 83 | 49.40% |
| `EMS_Good=False` SCADA | 54 / 177 | 30.51% | 39 / 226 | 17.26% |
| `EMS_Replaced=True` SCADA | 54 / 177 | 30.51% | 39 / 226 | 17.26% |
| generic-equation reference | 66 / 295 | 22.37% | 41 / 290 | 14.14% |
| group terms | 22 / 204 | 10.78% | 14 / 237 | 5.91% |

These slices overlap and are not causal estimates. In particular, group equations have a lower aggregate tail rate
yet contain nearly all catastrophic errors and every exception. A repair must measure both coverage and the full
error distribution rather than optimizing one slice.

## Repair hypothesis and required controls

The next development implementation may contain two independently switchable changes:

- **RPN arm:** bounds-safe group lookup, an actually executed first-member removal and regression tests built from
  sanitized group shapes; no production output enters evaluation.
- **Input arm:** implement SCADA/entered/default resolution only after checking the official Constraint
  Implementation Guidelines; explicitly record which quality/fallback rule chose each input.

Fresh evaluation must include four paired arms (`baseline`, `RPN`, `input`, `combined`) on identical intervals.
Primary metrics remain equation coverage, exact dual-sentinel invariance, normalized median/p95/max and named
exception counts. The fresh threshold must be frozen before any new RHS values are opened; the old partial result
is never overwritten.

## Claim boundary and resources

This diagnostic identifies plausible software/input mechanisms. It validates no repair and changes no scientific
decision. It made zero AEMO/R2 requests, reused 2 MiB already materialized locally, used no solver, GPU or paid
data and retained no individual RHS/SCADA value.

## Subsequent development disposition

The later identifier-tree RPN candidate recovered the four exceptions but caused 57/63 strict error regressions
and raised normalized p95 to `0.500736/0.315787`. It is rejected without fresh validation. The descriptive 2-by-2
repair suggestion is therefore superseded: neither the nested-group encoding nor the SCADA-selection rule is
fully determined by the audited public sources. Result:
`experiments/v14_aemo_nemde_rpn_repair_development/RESULTS.md`.
