# Paper G Schwarz/fixed-point scope — 2026-09-10

PRIVATE / INTERNAL. `public_evidence_eligible: false`.

- Decision: not_trigger; overall Paper G objective active/unachieved. Closed
  numerical-teacher route unchanged; no recorded blocker removed.
- Formal: `papers/proposal/ecomd_paper_g_schwarz_fixed_point_scope_2026-09-10.md`.
  Contract: `research/paper_g/schwarz_fixed_point_scope_20260910.yaml`.
  Manifest: `research/paper_g/schwarz_source_manifest_20260910.json`.
- NEST2605.12343v1: nonlinear full-Dirichlet neo-Hookean static equilibrium.
  Local displacement solvers exchange traces via additive Jacobi Schwarz
  and partition-of-unity assembly. Relative iterate change is the stopping
  measure; a separate gradient network is applied afterward. No uniform
  contraction, continuum truth or current released asset qualified.
- Coupling ablation, iteration-count growth, non-linear-total-runtime and
  GPU/one-CPU-core comparison qualifications are already explicit in NEST.
  Generic coupling or acceleration is not a fresh contribution.
- Wu/van Beek/Dolean/Heinlein2602.06842v2 is the selected current version,
  June2,2026; arXiv metadata states accepted CiSE manuscript. v1 initially
  consulted, not selected evidence. Generic update/physical-residual mismatch,
  training/update comparisons and physics-aware AA already have this parent.
  Keep SPD line-search and near-resonant Helmholtz qualifications.
- Three standard paper-only controls: (1) assembled-map discrepancy eta
  and exact contraction q give error <=(update+eta)/(1-q), without proving
  learned convergence; damping scales updates, not fixed points. (2) Scalar
  half-residual smoother plus negative linear residual correction cancels
  exactly, although both substeps may be nonzero. Not a trained-model result.
  (3) Physical residual combinations equal residuals of affine combinations
  for linear systems; attainable span and true nonlinear residual matter.
- No observed NEST failure or exact false fixed point inferred from small
  measured updates. Linear-system accuracy is not a continuum certificate.
  NEST and DL-HIM have different states, equations and interventions.
- Stop generic learned-Schwarz, damping, false-convergence diagnostics,
  affine-history acceleration and elementary perturbation certificates.
- Next source-only pair: NOEM NCS2026 publisher search abstract/metadata/
  availability text, and Convex Neural Energy Elements2608.02036v1 official
  abstract. Full methods/supplements/source not read. Verify exact boundary
  degrees of freedom, geometry/training family, energy, nullspace, Hessian,
  truth and budget; check classical convexity/static-condensation reduction
  before asserting disagreement. Neither is a new-publication trigger.
- Two selected primary HTML caches; no code, notebooks, raw outcomes,
  models, scientific implementation, simulations, GPU, outreach or release.
  Graph293/274/1407,evidence977,triggers134/qualified0;
  search21cycles/133raw/0cards unchanged. Verification receipt:
  `logs/private/paper_g_schwarz_20260910_verification.md`.
