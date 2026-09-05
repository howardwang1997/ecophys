---
name: project_ecomd_zumbach_orientation_audit_2026-09-05
description: Exact orientation-bias closure for the canonical EcoMD Zumbach metric and the failed ICLR re-entry
type: project
---

# EcoMD Zumbach-orientation audit — 2026-09-05

## Lasting decision

The canonical `ecomd.eval.stylized_facts.zumbach_asymmetry` and differentiable
`training.losses.zumbach_asymmetry_diff` are not valid time-reversal antisymmetric statistics. They
hold one coarse volatility window in the past and compare it with fine volatility at two unequal
ordinary lag distances. For any reversible stationary squared-return process whose positive
autocovariance decreases with lag, the implemented population statistic is non-positive and is
strictly negative under ordinary volatility memory.

Consequently, historical negative-score floors, positive-band pass rates, Zumbach-targeted mechanism
comparisons and the Zumbach component of the eleven-fact Pareto frontier are quarantined pending a
separate null-calibrated rescore. The result does not show that EcoMD passes a corrected Zumbach
test; it makes the old statistic non-evidentiary.

The standard role-swapped covariance definition, VARMA arrow-of-time inference and finite-sample
forward/reverse path-KL estimation directly occupy the obvious correction and generalization. The
candidate `zumbach_orientation_safe_path_evaluation` is therefore failed-closed as an ICLR method.
No implementation, outcome access, simulator, SSH or GPU work is authorized.

Full derivation and source audit:
`papers/proposal/ecomd_zumbach_orientation_reentry_audit_2026-09-05.md`.

