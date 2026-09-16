# Paper G boundary-response / energy assembly — 2026-09-10

PRIVATE / INTERNAL. `public_evidence_eligible: false`.

- Decision:not_trigger; goal active/unachieved. Closed numerical-teacher
  route unchanged and no recorded blocker removed.
- Formal: `papers/proposal/ecomd_paper_g_energy_assembly_scope_2026-09-10.md`.
  Contract: `research/paper_g/energy_assembly_scope_20260910.yaml`.
  Manifest: `research/paper_g/energy_assembly_source_manifest_20260910.json`.
- NOEM2506.18427v1 explicitly acknowledges nonconvex energy minimization,
  differentiates its trial-field energy and reuses one model across many
  same-geometry elements. Fixed geometry does not mean one element instance.
- NOEM VOR, NCS6:417–429, read in selected author-uploaded text on ResearchGate
  (Lu Lu,Apr29,2026). The published main text already reports OOD negative
  Hessians/convergence risk, referring to Supplementary Section4; supplement
  not read. Its error theorem assumes an energy minimizer and retains a gap
  to an enlarged linear trial space; it is not a Newton convergence guarantee.
- Convex Neural Energy Elements2608.02036v1 directly covers energy export,
  condensed square-root regression, nullspace and assembly. It includes a
  competitive polynomial baseline and separates boundary-only versus full-
  field costs. Nonlinear example is convex reaction-diffusion; finite Newton
  refinements have no proved global convexity. Implementation-development
  footnote/failed variants excluded from scientific support. No failure
  magnitudes or source-reported speedups adopted as Paper G findings.
- Standard paper-only diffusion trial q=xU+eps sin(omega U) sin(pi x) keeps
  boundary traces exact and has uniformly small spatial L2/H1 errors and
  energy excess, yet E_q_second=1+pi^2 eps^2 omega^2 cos(2omega U)/2 can be
  negative. Omega changes the representation, not physical stability.
  Any global minimizer under load f still lies within pi eps/sqrt(2) of f:
  curvature/solver behavior and global approximation error are different.
- Standard linear-lift null for K>=0,K_ii>0: S_hat=[I;R]^T K[I;R]
  =S+(R-R*)^T K_ii(R-R*)>=S. A boundary-linear field lift retains convexity
  without directly learning energy. Null modes require reproduction; forcing
  needs affine terms. Geometry dependence can be nonlinear at fixed U-linearity.
- No matched geometry, boundary parameterization, training target or full-cost
  comparison qualified. Stop generic Hessian/value-derivative mismatch,
  convex energy export,nullspace regularization and square-root regression.
- Next source-only Parish2307.05434: official abstract/bibliography located;
  exact version and fulltext not audited. Distinguish state-dependent secant,
  consistent force derivative and energy Hessian before importing SPSD claims.
  Classical Jacobian/integrability alone is not a new topic or re-entry trigger.
- Two works/three selected versions, two arXiv HTML caches plus VOR web-only
  passages. No PDF,source code,notebooks,raw outcomes,model,experiment,GPU,
  outreach or publication. Graph293/274/1413,evidence980,triggers135/qualified0;
  search21cycles/133raw/0cards unchanged. Verification receipt:
  `logs/private/paper_g_energy_assembly_20260910_verification.md`.
