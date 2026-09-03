# D0 freeze: conservation-constraint attribution audit (F3 v2)

Date: 2026-08-27 (frozen before any audit outcome; toy probe outcome is prior knowledge and is
recorded as such)

Protocol stage: **D0 outcome-blind freeze** for the F3-v2 subject
(`experiments/toy_h2_laundering/RESULTS.md`), under the PI's blanket authorization (all public
data; servers 100.105.21.7 / 100.80.236.112 / 100.123.220.57). Hash-of-record: this file plus
`scripts/audit_family_analytic.py` at the launching commit.

## Frozen estimand

For each system family, arm, and data-flatness level, at **matched in-distribution RMSE
(tolerance ±5%) and matched compute budget** (same optimizer, batch count, hidden width and
training length cell), the out-of-distribution one-step error decomposed into:

- `conserving_err` = ‖(I − P_1)(f(u) − A(u))‖ (channel that the constraint cannot remove);
- `mass_drift` = |P_1(f(u) − A(u))| (constraint-violating channel; target invariant drift = 0),

evaluated on three frozen OOD probes: extrapolation along the data-flat conserving mode
(2.5σ_typ), along a data-rich mode (2.5σ_typ), and a mass-shifted input.

## Frozen arms (6)

`free` (absolute output), `free_res` (residual, no constraint), `soft` (absolute + λ·mass
residual²), `soft_res` (residual + penalty), `hard` (residual + tangent projection — exact
conservation), `projection` (post-hoc uniform correction of `free`). λ grid frozen at {3, 30}.

## Frozen families

- **A (analytic/spectral, launches first):** periodic-grid n=64 one-step maps — advection
  (u_t = −c u_x, c=1, exact spectral), diffusion (u_t = ν u_xx, ν=0.02, exact spectral),
  viscous Burgers (u_t = −u u_x + ν u_xx, ν=0.01, pseudo-spectral RK4 substeps, dt=0.1).
  Invariant: mean(u) (exactly conserved by all three generators). Data: Fourier-mode covariance
  control — flat band k=1 at σ_f ∈ {1.0, 0.1}; rich band |k|≈8 at σ=1.0; k=0 at σ=1.0; others
  0.5. Truth is analytic-by-construction (no external dataset).
- **B (PDEBench-class surrogates):** same generator class at higher dimension/resolution with
  the PDEBench-style OOD definitions (unseen amplitude/resolution); launches after A passes its
  separability check.
- **C (2D structured-grid learned simulator, MeshGraphNets-class role):** 2D advection–diffusion
  on a 32×32 periodic grid with a ConvNet/U-Net learner; launches last.

## Frozen budget and design cells

Per family: 6 arms × capacity cells {hidden 64, 128} × {epochs 400, 800} × 5 seeds × 2
flatness levels. Budget cap: 40 V100-hours per family; hard stop at the cap. Every run writes
one JSON record (config, git SHA, seeds, per-case metrics) to the server, pulled to
`experiments/constraint_attribution_audit/` in this repository.

## Frozen decision rules

1. **Attribution claim** (primary): at matched ID error, |ΔOOD conserving_err(free vs free_res)|
   versus |ΔOOD(free_res vs hard)|; parameterization-dominance is confirmed if the first
   difference is at least twice the second in ≥2 of 3 systems of a family, with non-overlapping
   seed mean±sd.
2. **Laundering claim** (secondary): soft(λ) conserving_err > free conserving_err at matched ID
   with mass_drift(soft) < mass_drift(free), replicated across seeds; λ-sensitivity recorded.
3. **Negative control**: projection ≡ free on conserving_err within 1% (decoupling check);
   violation invalidates the decomposition pipeline for that family.
4. **Matched-ID rule**: comparisons only inside the ±5% ID window; non-overlapping arms are
   reported as ID-cost findings, never extrapolated.

## Frozen stop rules

- If family A shows no arm separability (all arms' conserving_err within ±2 sd on every OOD
  probe), halt before families B/C and investigate the design.
- Any result contradicting the toy's attribution pattern triggers freeze-and-review of this
  document, not silent continuation.
- Exploratory branches (new systems, new arms, λ values) are recorded as exploratory and never
  merged into the confirmatory tables.

## Authorized actions (this freeze)

Run family A on the authorized pool (public/generated data only); families B/C launch only
after A's separability check passes. No other routes, datasets, or model classes are touched.
