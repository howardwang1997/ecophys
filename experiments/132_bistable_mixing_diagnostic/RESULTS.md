# Experiment 132 results — bistable fail-visible mixing diagnostic

**Run date:** 2026-08-10  
**Artifact:** `BISTABLE_RESULTS.json`  
**Decision:** preregistered diagnostic gate FAIL; thresholds are unchanged; G0 remains AMBER

## Gate outcome

| Frozen gate | Required | Observed | Result |
|---|---:|---:|---|
| grid boundary mass | `<1e-10` | at most `1.1e-46` | PASS |
| hard false-safe rate | `<5%` | `0%` | PASS |
| easy resolved rate | `>=80%` | `78.125%` | **FAIL** |
| easy resolved median relative error | `<=25%` | `11.97%` | PASS |

The overall result is FAIL because the easy-regime resolved rate missed its frozen threshold by 1.875 percentage
points. The threshold is not relaxed after inspection.

## What the diagnostic did detect

| Regime | Resolved rate | False-safe rate | Median group occupancy gap | Median switches |
|---|---:|---:|---:|---:|
| easy, `T=0.50` | 78.125% | 9.375% | 0.0459 | 934 |
| medium, `T=0.15` | 1.5625% | 1.5625% | 0.3665 | 258 |
| hard, `T=0.04` | 0% | 0% | 0.9934 | 3 |

In the hard regime, every batch was rejected while the full-long tangent gradient had `-96.53%` relative bias
and the persistent-detached estimate had `-99.88%` bias. The persistent estimate looked numerically stable only
because opposite-well chains remained trapped; its low variance is not evidence of correctness.

The easy regime shows the other side of the tradeoff. The full-long mean had `-3.73%` bias, but the conjunction
of four diagnostic rules rejected 14 of 64 accurate batches and resolved only 50 of 64 batches. The current rule
is therefore slightly too conservative under the frozen easy-case utility criterion.

## Consequence

The experiment supports the qualitative need for initialization-group and mode-switch diagnostics, but this
particular conjunction is not yet a validated certificate. A successor may be designed only as a new version
with an independent tuning/validation split and a new preregistration; this artifact must remain the failed v1.
No candidate invariant-gradient estimator was tested, so this result cannot advance G0.

