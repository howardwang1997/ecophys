# ICLR 2027 submission plan — scientific contribution first

Date: 2026-09-01 NZST. Target paper deadline: 2026-09-25 AoE.

## P0: replace path-specific rhetoric with an identified scientific question

The paper's central object becomes intervention attribution under interacting design choices, not a
retreat from an unfavorable constraint result. The new 2 x 2 experiment crosses absolute versus
residual output coordinates with free versus exact enforcement. Its primary estimand is the
interaction/path-dependence term. Path-averaged two-factor Shapley credits replace arbitrary
single-path credit whenever the interaction is material.

Prove minimality: the usual three trained cells leave the absolute-hard value free, so the
interaction and both path-averaged credits are algebraically unidentified; a post-hoc projection
cannot substitute for training in the missing cell. This turns the fourth cell from an optional
ablation into the intervention required for identification.

Add a channel-separable training-null proposition: if conserving and violating outputs have
disjoint parameter blocks and a separable optimizer/regularizer, hard and free training must have
identical conserving predictions. The factorial enforcement effects therefore test representation
and optimization coupling, while the interaction tests whether that coupling depends on output
coordinates. State clearly that rejection diagnoses coupling but does not identify its unique
cause.

Connect that global null to a local functional mechanism with the outcome-blind tangent-kernel
identity recorded before formal-result access: the off-diagonal block `Qbar K_theta Pbar` is exactly
the first-order route by which the violating-channel gradient changes conserving predictions, and
the recorded gradient dot product is its residual-weighted bilinear form. This is a specific
conservation-channel use of the established empirical NTK, not a claim to have introduced NTK
analysis. The theory note SHA-256 is
`defe61a6025cd17b36bccf872a95a92c2edc210728d8d4577202b158d539dc5c`.

The manuscript must use the frozen four-way classification without reinterpretation:

- `material_nonadditivity`: headline that parameterization and enforcement do not admit a unique
  sequential credit allocation; report Shapley intervention credits;
- `statistical_nonadditivity_below_or_crossing_sesoi`: report reproducible but practically smaller
  path dependence, with both the zero and SESOI distinctions explicit;
- `practical_additivity`: report a successful equivalence test validating the simpler sequential
  decomposition at the inherited 10% scale;
- `unresolved`: say the experiment does not identify additivity or material interaction. Do not
  turn this into a robustness narrative or a positive result.

Before the factorial result is revealed, freeze a mechanism test of the channel-separable null.
Decompose the first matched training minibatch into conserving and violating losses, measure their
parameter-gradient alignment, and execute the exact paired free/hard first Adam step in both output
coordinates. The primary test is the prospectively fixed seed-wise association between this local
coordinate interaction and the final rollout interaction. A null or reversed association falsifies
the proposed local explanation; it must not be relabeled as robustness. This is positioned against,
and explicitly cites, the established PINN gradient-conflict literature rather than claiming that
gradient alignment itself is new.

## P0: complete and analyze both already-frozen formal blocks

1. Complete C-ad2d under the unchanged synthetic lock; preserve and exclude both Burgers failures.
2. Require exactly 1,830 valid records across eight complete systems before the amended synthetic
   analyzer runs once.
3. Complete the fresh-seed PDEBench factorial block with exactly 150 records and run its frozen
   analyzer once.
4. Archive remote/local SHA-256 receipts before any manuscript number is updated.

## P1: build evidence breadth, not a result-contingent rescue

Independently of the advection interaction sign, attempt admission of one second public PDEBench
system with the same linear mass invariant. The preferred system is periodic 1D Burgers at one
fixed viscosity selected before model outcomes. The data file, conservation drift, coordinate
schema, split, model, seeds, factor grid, primary cell, and analysis must receive a separate
outcome-blind freeze. Failure of the public data-admission gate is itself terminal for that block;
do not switch viscosity from a model result.

This replication is worth including only if it is fully paired and scientifically comparable. A
partial or differently tuned Burgers block belongs in limitations/artifacts, not the main evidence.

## P1: rewrite the paper around the actual estimand

- Add the exact interaction identity and two-path/Shapley attribution derivation.
- Replace the old five-arm framing with a four-cell factorial plus a derived projection control;
  retain `soft30` as report-only evidence from the parent block.
- Lead Results with the fresh factorial primary classification, then show simple and Shapley
  credits, then resolution/horizon heterogeneity.
- Use the eight-system synthetic confirmation only as separately analyzed breadth; never pool it
  with PDEBench or hide the two failed Burgers systems.
- Distinguish exact conservation as a guarantee from conserving-channel predictive effects.

## P1: reviewer-facing claim and novelty audit

The defensible contribution is a controlled attribution methodology for conservation-aware neural
surrogates: exact channel decomposition, a fully crossed intervention design, a diagnostic of path
dependence, and path-averaged credit. Novelty wording must be checked against primary literature on
hard constraints, conservation-law neural operators, neural PDE benchmarking, factorial ablation,
and game-theoretic attribution. Do not claim the first use of Shapley values or the first hard
constraint; claim only the specific intervention-attribution formulation supported by the audit.

The closest contemporaneous public submission found in the 2026-09-01 audit, Physics-Manifold
Flow Matching, already compares a pure network, projection only, projection plus residual geometric
guidance, and fuller adaptive variants on PDEs including Advection and Burgers. Therefore neither a
projection-versus-residual-branch ablation nor those benchmarks are sufficient novelty. The ICLR
case must rest on the identified coordinate-by-training factorial, its non-identification result,
and evidence for or against a prospectively specified coupling mechanism.

## ICLR viability gate: scientific contribution, not fallback rhetoric

The final submission decision is made from the complete frozen evidence, not from whether any one
coefficient has a favorable sign. A main-track ICLR case is strongest if the identified factorial
experiment establishes practically material path dependence, or if the prospective gradient
intervention supplies a reproducible mechanism and the second public PDE establishes external
relevance. A tightly estimated practical-additivity result can still validate the simpler
decomposition in the tested regime, but equivalence alone is not to be advertised as a major
scientific discovery.

The paper is not promoted as ICLR-ready if all three conditions hold: the Advection interaction is
unresolved, the frozen local-mechanism association is non-positive or crosses zero, and the
Burgers block either fails admission or supplies no independently interpretable factorial result.
That state calls for a genuinely new causal or theoretical contribution before submission, not a
rewrite around robustness, better bookkeeping, or a weaker claim. Cross-PDE disagreement is
reportable only through the prespecified per-system estimands; it cannot be converted post hoc into
a new moderator claim.

## P2: submission integrity

- Keep the paper within the ICLR nine-page main-text limit; move full cells and receipts to the
  appendix/supplement.
- Include the required AI-use statement and double-blind artifact links.
- Rebuild with the official ICLR 2027 style, inspect every rendered page, verify embedded fonts,
  and scan for overfull boxes, missing references, and undefined citations.
- Final claims, abstract, title, and conclusion are edited last, after frozen analyses.
