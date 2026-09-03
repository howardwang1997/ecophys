# D-1 hostile audit: conservation constraints vs OOD generalization (paper-only)

Date: 2026-08-27

Status: **hostile falsification audit for
`ecomd_question_contract_constraint_inductive_bias_2026-08-27.md` against the D-2 manifest
`ecomd_constraint_inductive_bias_d2_manifest_2026-08-27.md`. Paper-only: derivations on paper,
no compute, no datasets, no implementation. The F3 subject and full-T0 forecast below are frozen
before any experimental outcome exists.**

## Killer test 1 — analytic-toy starvation test for H2 (does H2 have a regime at all?)

**Derivation.** Take a chain of `n` cells with relaxation dynamics
`u_i' = k(u_{i-1} - 2u_i + u_{i+1})` (mass `C = Σu_i` conserved). A learned one-step map
`f_θ` has error `ε(u)`. Decompose `ε = ε_⊥ + ε_∥` into the non-conserving direction `1`
(uniform) and the `n-1`-dimensional conserving tangent space.

- *Post-hoc projection* (mechanism 3): `ε_⊥` is removed, `ε_∥` is untouched. No laundering by
  construction; only a bias term. H2 requires the constraint to act *during training*.
- *Soft penalty* (mechanism 2): gradient of `λ(C(f_θ(u)) − C(u))²` can be satisfied by moving
  mass along any conserving direction. When the training distribution has low variance along a
  conserving direction `v` (data under-constrains that channel), the data loss is flat in `v`,
  and the penalty pushes the violation into `ε_∥` along `v`: **spurious transport with
  signature ‖ε_∥‖ growing as the ID marginal on `v` flattens**. In the linear-quadratic case
  the transfer rate is computable in closed form (penalty gradient projected onto the
  flat channel scales as `1/σ_v²`).
- *Existence boundary (falsifiable)*: at `n = 2` the conserving tangent is one-dimensional and
  the effect collapses to bias transfer; H2's laundering requires `n ≥ 3` plus one
  data-underconstrained conserving direction. This is a **boundary prediction**: H2 signature
  should switch on only above the data-flatness threshold, which the toy can demonstrate
  analytically.

**Verdict: PASS.** H2 has an analytically demonstrable regime with a computable onset
condition; the 2-cell boundary gives a built-in negative control. Risk retained: real
(non-toy) networks may realize the constraint through channels the quadratic analysis
underestimates — that ambiguity cuts both ways and is exactly what the audit measures.

## Killer test 2 — matched-ID control feasibility (does matching consume the effect?)

**Attack.** "Matched in-distribution error at matched budget" may be infeasible: hard-constraint
architectures have reduced capacity and may never reach the ID error of unconstrained models at
any equal budget; or matching requires capacity tuning that confounds the comparison.

**Defense (protocol-level).**
1. Replace point-matching with **frontier matching**: for each mechanism level, train a family
   sweeping capacity and training length; extract the ID-error/budget Pareto frontier; compare
   OOD decomposition across mechanisms **on the overlapping ID-error window**, with a
   pre-registered tolerance band (ID error within ±5%).
2. If a mechanism's frontier does not overlap the others' windows, that ID-cost is itself a
   reported outcome (the constraint's in-distribution price), and cross-mechanism OOD claims
   are restricted to the overlap; non-overlap extrapolation is declared unsupported.
3. Budget matching is measured in optimizer steps × FLOPs (not wall-clock), per the repo's
   equal-budget rule.

Feasibility on 2×V100 for three small-system families (advection/KdV-class PDEBench tasks,
small-mesh MeshGraphNets, diffrax analytic systems): frontier of ~6 capacity points × 3
training lengths × 3 mechanisms × 3 families × 5 seeds ≈ 810 runs of small scale — weeks, not
months. **Verdict: PASS with the frontier protocol as a binding pre-registration commitment.**

## Killer test 3 — null-value operationality (if H2 is third-order everywhere, does it matter?)

- If H2 is negligible in every family and H1 holds uniformly with no mechanism dependence: the
  contract degrades to the pre-stated PDEBench-style benchmark note ("constraints are safe and
  helpful; decomposition method included") — TMLR/D&B ceiling, below the honest target. This
  degradation is real and is the main downside risk.
- If H2 fires only under data-flatness (the toy's onset condition): the result is an
  *actionable prescription* — constraint safety is conditional on training-data coverage of
  conserving channels, with a measurable diagnostic. That is a mechanism finding even with a
  bounded scope.
- Same-estimand check: H1/H2/H3 share one estimand (OOD error decomposition at matched ID
  error) — no estimand drift across arms. Contamination: prior soft-penalty literature reports
  ID accuracy or conservation fidelity, not this decomposition; no outcome contamination of our
  experimental cells. Reusable assets retained under any outcome: the decomposition metric, the
  frontier-matching protocol, the toy with its analytic onset law.

**Verdict: PASS (conditional value survives; unconditional-H1 degradation path pre-priced).**

## Exact-parent / standard-parent reduction check

Is this a disguised known result? Nearest parents: (i) constrained-hypothesis-class
generalization theory (abstract, sign-free — does not predict the decomposition or mechanism
dependence); (ii) Beucler et al. mechanism taxonomy (no OOD/decomposition evaluation);
(iii) PINN bias-variance tradeoff studies (parameter-identification setting, not
learned-simulator OOD). No parent states or tests H2. **Not reduced.**

## F3 subject (frozen before any outcome)

**"At matched in-distribution error and matched compute budget, the mechanism level of an
exact conservation constraint (hard architecture / soft penalty / post-hoc projection)
re-distributes the out-of-distribution error of learned simulators between conserving and
non-conserving channels, with a predicted laundering onset governed by training-data flatness
over conserving directions."** Systems: three families (PDEBench-class PDE surrogates,
MeshGraphNets-class mesh dynamics, diffrax analytic systems); ≥5 seeds/cell; public data or
generated-from-analytic-truth data only; pre-registered decomposition, frontier-matching
tolerance, and decision rules.

## Full-T0 forecast (frozen; uncalibrated reviewer estimate)

Probability the frozen formulation survives all T0 gates (exact-prior: survived today; killer
tests: passed on paper; two independent system lineages: satisfied by design; execution to a
criterion-visible result on solo 2×V100; archival publishability across outcome branches):

- **lower 10% / point 22% / upper 35%** — dominated by: toy-to-real transfer of H2 (~55--65%),
  frontier-overlap adequacy (~80%), solo completion (~70%), sign decisiveness (~70%).

The lower bound is **below the 15% activation brake**. Under the protocol this formulation is
therefore **not eligible for active status today**; D-1 permits recommending the cheapest
bounded information acquisition instead: the analytic toy itself (CPU-days, public/generated
data only), whose H2 onset law would move the dominant uncertainty before any V100 spend. Any
toy execution still requires separate PI authorization (no sandbox is currently authorized).

## Decision

D-1 audit: **passed on paper with a frozen F3 subject and forecast**. The recommended next
action, in cost order: (1) full-text re-read of the four `unverified` manifest entries; (2)
PI-authorized CPU-only analytic toy (H2 onset law + 2-cell negative control); (3) re-estimate
T0 after the toy; (4) only if the lower bound then clears 15%, request outcome-blind
activation of the three-family audit.

## Addendum (same day, post-toy): revision of killer-test 1 and the F3 subject

Two corrections from the executed probe (`experiments/toy_h2_laundering/RESULTS.md`, run under
the PI's blanket data+compute authorization):

1. **The closed-form "laundering onset" claim in killer test 1 was wrong.** In the
   linear-quadratic class the soft penalty operates on the `{1·bᵀ}` subspace of the error
   operator, which is orthogonal to conserving-channel errors: H2 is exactly zero there. H2 is
   a nonlinear-optimization phenomenon only.
2. **The probe refuted H1 by a confound**: the hard arm's OOD advantage equals the residual
   parameterization's advantage (matched-pair `hard` vs `free_res`); constraint level governs
   only the constraint observable. H2 survives narrowly (strong λ × absolute output); the
   decoupling theorem for post-hoc projection was confirmed exactly.

The F3 subject is revised to the child v2 formulation recorded in the probe RESULTS
(attribution of constraint benefits into parameterization vs constraint components; soft-penalty
laundering audit), with a first collision check passing. Revised full-T0: **15% / 30% / 45%**
(lower bound now at the activation brake, conditional on the D0 freeze passing). The
2-cell/n≥3 boundary statement is withdrawn. Original text above is retained as the frozen
pre-probe record.
