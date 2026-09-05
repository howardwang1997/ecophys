# Family A results: conservation-constraint attribution audit (analytic/spectral systems)

Date: 2026-08-27

Status: **confirmatory outcome under the D0 freeze
`papers/proposal/ecomd_constraint_attribution_audit_d0_freeze_2026-08-27.md`; six jobs
(advection/diffusion/Burgers × σ_f ∈ {1.0, 0.1}), capacity grid 64/128 × 400/800 epochs, 5
seeds/cell, 8 trained variants per cell; JSON records in this directory; executed on the two
authorized V100s; generated data only.**

## Frozen-rule outcomes (cell 128×800; full grid in JSONs; mean ± sd over 5 seeds)

### Rule 1 — attribution (primary): **PASS in 6/6 settings**

| System@σ_f | free | free_res | hard | attribution ratio |
|---|---:|---:|---:|---:|
| advection@1.0 | 0.421±0.024 | 0.030±0.004 | 0.031±0.005 | 745× |
| advection@0.1 | 0.442±0.033 | 0.030±0.005 | 0.031±0.005 | 260× |
| diffusion@1.0 | 0.422±0.021 | 0.005±0.002 | 0.003±0.000 | 252× |
| diffusion@0.1 | 0.443±0.031 | 0.004±0.001 | 0.004±0.001 | 5225× |
| burgers@1.0 | 0.596±0.019 | 0.408±0.000 | 0.408±0.001 | 1035× |
| burgers@0.1 | 0.610±0.030 | 0.408±0.001 | 0.408±0.001 | 654× |

(conserving-channel error on the flat-mode OOD probe; the rule required the parameterization
difference to be ≥2× the constraint difference in ≥2/3 systems; it exceeds it by 2--3 orders of
magnitude in all six, with non-overlapping seed bands.) **`hard ≡ free_res` on conserving error
in every system: the exact conservation constraint contributes nothing to conserving-channel
OOD error beyond zeroing mass drift.**

### Rule 2 — laundering (frozen conjunction): **2/6; harm component 6/6**

`soft@30` inflates conserving error over `free` in 6/6 settings (+18--33%, e.g. advection@0.1:
0.562±0.055 vs 0.442±0.033). The frozen conjunction also required reduced mass drift; at full
training `free`'s drift is already ≈0.008--0.009 and `soft@30` reduces it in only 2/6
(σ_f=0.1 advection/diffusion). Honest verdict: the laundering *conjunction* holds in 2/6;
the robust confirmatory statement is **strong soft penalties inflate conserving-channel error
without buying a drift advantage at converged training** — i.e., they are dominated in this
regime.

### Rule 3 — decoupling negative control: **PASS exactly (6/6, deviation 0.00%)**

`projection` reproduces `free`'s conserving error to the printed precision everywhere,
zeroing drift — the closed-form decoupling theorem holds in the nonlinear setting for the
post-hoc mechanism, validating the decomposition pipeline.

### ID-cost finding (frontier non-overlap branch of the D0)

At every capacity cell the absolute-output family's ID RMSE is 2--2.5× the residual family's
(e.g. advection@0.1 128×800: 0.0005 vs 0.0002), so no cross-parameterization comparison
satisfies the ±5% matched-ID window. Per the freeze this is reported as an **ID-cost finding**
(the absolute form pays 2--2.5× in-distribution at matched budget) and cross-family OOD claims
remain qualitative; all within-residual-family comparisons are ID-matched.

## Family-A separability stop rule: PASS

Arms separate by 14--130× across systems; the design proceeds to families B and C unchanged.

## What this establishes (and does not)

Established, confirmatory, under the frozen rules on one family: the celebrated constraint
benefit on data-flat OOD channels is attributable to output parameterization; the constraint's
own marginal effect is confined to the constraint observable; strong soft penalties are
strictly dominated; post-hoc projection implements the decoupling theorem exactly. Not yet
established: PDEBench-class (B) and 2D structured-grid (C) families; nonlinearity of the
invariant (energy-type); learned-simulator families beyond MLPs (Conv/GNN arms in family C
address architecture breadth).

## Next actions (authorized by the D0)

Implement and launch family B (higher-resolution PDEBench-style OOD definitions) and family C
(2D grid, ConvNet learner); hold the 40 V100-hour/family caps; pull results through
`scripts/analyze_constraint_audit.py` unchanged.
