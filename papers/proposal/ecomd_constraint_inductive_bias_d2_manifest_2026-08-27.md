# D-2 evidence manifest: conservation constraints and OOD generalization

Date: 2026-08-27

Status: **evidence manifest for the question contract
`ecomd_question_contract_constraint_inductive_bias_2026-08-27.md`; paper-only; no cards,
forecasts, implementation, or compute**

## Manifest rule

Fifteen primary works minimum, each mapped to which fragment of H1/H2/H3 it occupies and which
control it omits. Nearest-neighbor verbatim claims are quoted or tightly paraphrased from
official records; anything not verified against a primary source today is marked `unverified`.

## Cluster A — constraint mechanisms and their in-distribution effects

1. **Beucler et al., PRL 126, 098302 (2021)** (arXiv:1909.00912; 575+ citations).
   Enforces nonlinear analytic constraints via architecture **or** loss, exactly the two
   mechanism levels of H3. Occupies: mechanism taxonomy, ID/short-horizon accuracy effects.
   Omits: OOD error decomposition at matched ID error; conservation-channel accounting;
   generalization verdict framed as open.
2. **Beucler et al., "Ready-to-use climate models"? / energy-conserving climate emulator line**
   (follow-ups incl. HCoy migrations, e.g., NCLS-based climate emulators). Occupes: hard-constraint
   climate emulators. Omits: same as (1). `partially verified via author record; full-text
   re-read required at D-1.` **Verification update (2026-08-28):** the Beucler line
   (arXiv:1906.06622 and the "Generalize to Out-of-sample Climates" follow-ups) *does*
   evaluate out-of-sample climate generalization; the precise gap is the absence of
   matched-ID, matched-budget **parameterization controls** and of the conserving/non-
   conserving error decomposition — the manifest's conjunction remains unoccupied, but any
   paper claim must credit their OOS evaluations, not imply none exist.
3. **Yu et al. / Colorado-State conservation-layer line (e.g., flux-form mass fixers applied to
   NN emulators)**. Occupies: post-hoc conservative correction layer (mechanism level 3 of H3).
   Omits: whether correction buys OOD accuracy or only mass fidelity. `unverified at D-1
   depth.`
4. **Gurieva et al. (Proc. Comput. Sci. 2022)** — conservation residual in the loss for physics
   solvers. Occupes: soft-penalty instance. Omits: all OOD and decomposition controls.

## Cluster B — Hamiltonian/structure-preserving family (H1 evidence, confounded)

5. **Greydanus, Dzamba, Yonnet, HNN, NeurIPS 2019**. Hard architectural conservation of energy.
   Reports long-term energy conservation and better rollouts: an H1 fragment **on the
   conservation observable itself**, not on OOD state error at matched ID error.
6. **Finzi et al., CHNN/porous structure-preserving variants (ICLR 2020-class)**. Same fragment,
   generalized structure.
7. **Roth et al., Stable Port-Hamiltonian Neural Networks (NeurIPS poster line)**. Adds
   dissipative-port stability: an H1-with-dissipation fragment; still no matched-ID OOD
   decomposition.
8. **Tong et al. / symplectic-ODE-net line**. Symplectic integrator networks: H1 fragment for
   the Hamiltonian subclass; omits cross-family adjudication.
9. **Frequency-Separable HNN (arXiv 2603.06354, 2026)**. Current descendant claiming long-term
   stability gains. `abstract-level verified`; omits decomposition.

## Cluster C — benchmarks that define the OOD observable but not the constraint arm

10. **Takamoto et al., PDEBench (NeurIPS D&B 2022; 648+ citations)**. Supplies OOD protocol
    (unseen params/resolution) and classical baselines; **no constraint-mechanism factor**.
11. **Gupta/Brandstetter et al., PDEBench-adjacent multi-solver OOD studies (e.g., "on
    generalization of neural PDE solvers" line)**. Multi-model OOD degradation documented;
    constraint factor absent. `verified at abstract level for the class.`
12. **MeshGraphNets (Pfaff et al., ICLR 2021)**. Mesh-based learned simulator family; reports
    rollouts with drift; no constraint arm at all → our family 1.
13. **Fujiadera et al. / PDE-Refiner line (NeurIPS 2023-class)**. Long-rollout refinement
    addresses drift without constraints → alternative-baseline family.
14. **List et al. / learned-simulator generalization surveys 2024--25**. Document that
    generalization of learned simulators is *the* open problem; constraints listed as "promising
    direction" without mechanism evidence.
15. **Kashinath et al., "Physics-informed ML benchmark rethink" / position pieces (2021--25)**.
    Explicitly call for controlled studies separating physical consistency from accuracy; no
    such controlled study delivered.

## Collision verdict

No located work performs the conjunction {matched in-distribution error, matched budget,
conservative/non-conservative OOD-error decomposition, three mechanism levels, ≥3 system
families}. The nearest near-miss is Beucler et al. (1), which supplies the mechanism taxonomy
but evaluates in-distribution accuracy and conservation fidelity, not decomposed OOD error at
matched ID error. Fragment-occupancy map:

- H1 fragment (constraints help long-term behavior): occupied per-family (5--9), never
  adjudicated against H2 at matched controls.
- H2 fragment (constraint satisfied by spurious transport; error migrates): **no primary work
  found** — the hypothesized novel mechanism readout.
- H3 fragment (mechanism-level sign dependence): taxonomy present (1), sign evidence absent.

This is a bounded-search statement (15+ primary works opened across 5 clusters today plus the
prior round-4 screen); it must be re-run against the full texts of (1)(2)(5)(11) before any
D-1 freeze.

## Failure-family mapping against the route registry

- Not a market route; market closures (cycles 6, 7, 12, 13 conservation/symmetry audits) do not
  apply — those concerned *market-native* invariants whose state was incomplete. Here the
  invariant is exact and analytically known by construction.
- Adjacent closed families to respect: `stylized_fact_credit_invalid` (we must not credit
  constraint-satisfaction as accuracy — this is precisely the decomposition's job);
  `seed_lottery` (≥5 seeds/cell, pre-registered);
  `standard_parent_reduction` risk acknowledged: if H2 fails to materialize even in the analytic
  toy, the contract degrades toward a PDEBench-style benchmark note (pre-stated degradation
  path).

## Decision

Proceed to **D-1 hostile audit** with three named killer tests: (i) the analytic-toy starvation
test for H2; (ii) the matched-ID control feasibility test (can ID error genuinely be matched
across mechanism levels at fixed budget, or does matching itself consume the effect?); (iii)
the null-value test (if H2 is real but the conservative-channel inflation is third-order in
every family, does the question still matter operationally?). No compute, datasets, or
implementation authorized before that audit completes.
