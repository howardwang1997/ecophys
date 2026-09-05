# EcoMD DEpiABS z-score population-scaling trigger audit (2026-09-05)

## Durable decision

`not_trigger`; no candidate harvesting, outcome access, implementation, SSH or GPU work is
authorized. DEpiABS is a relevant AAMAS 2026 differentiable-ABM paper, but its z-score scaler is a
target-conditioned output calibration, not a small-to-large population operator. It removes no
blocker from `fluctuation_aware_population_size_transfer` or
`tail_index_cardinality_pooling_for_particle_simulators`; no new route node was created.

## Exact algebraic result

For simulated series `x`, target series `y`, and standardized `z_x`, the published two-stage map
reduces to `hat x = sigma_y (z_x - min(z_x)) + min(y)`. Thus `sd(hat x)=sd(y)` and
`min(hat x)=min(y)`, but `mean(hat x)=min(y)-sigma_y min(z_x)`. It matches the target mean iff the
standardized minima of `x` and `y` agree. The target mean cancels completely.

For every `a>0,b`, `z_(a x+b)=z_x`, hence `T_y(a x+b)=T_y(x)`. The scaler erases simulator level
and amplitude, so it cannot identify a population exponent, interaction normalization, finite-size
noise or response law. Its output contains no target population size or population-indexed
transition kernel.

## Evidence boundary and re-entry

The paper reports forecasting from a 500-agent simulation and a runtime-versus-population test, not
a matched small/large path-law or intervention-response test. It describes target moments as
calibration statistics; the exact time indices are not specified in the available experiment text,
so leakage is a risk requiring a frozen split, not an allegation made by this audit. A clean split
would still leave the operation as calibration.

The reusable guardrail is the target-free population-transfer audit: eliminate nuisance parameters,
test affine-erasure symmetries, require a market-native weighted population unit and an explicit
population-indexed stochastic kernel, then validate a commuting aggregation diagram and full path
laws on untouched scales. Re-enter only for a new theorem/estimator beyond mesoscopic SDE,
mean-field, graph pooling and neural renormalization, with two independent dynamic truth systems.

Formal result:
`papers/proposal/ecomd_depiabs_zscore_population_scaling_trigger_audit_2026-09-05.md`.
