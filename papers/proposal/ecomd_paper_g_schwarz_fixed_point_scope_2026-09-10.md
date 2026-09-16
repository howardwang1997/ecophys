# Paper G: local assembly, stopping and physical truth

PRIVATE / INTERNAL. `public_evidence_eligible: false`.
Started 2026-09-09T17:26:49Z (2026-09-10 05:26 Pacific/Auckland).
Previous goal turn: progress. The full Paper G objective remains unachieved.

**Decision: not a qualified re-entry trigger.** The local-flux lead resolves
into established local-to-global assembly and a directly occupied distinction
between iterator convergence and physical residual. No candidate is created.
This bounded source/theorem-scope preflight attaches to the existing closed
`paper_g_numerical_teacher_continuum_ranking` route. Neither its elementary
certificate nor direct-supervision-parent blocker is removed.

The repository connection is the original neural-PDE conservation/generalization
question and its downstream use of learned physical predictions. This audit
adds no Paper D empirical evidence, no renamed training/deployment contribution
and no market claim. It does not activate another search cycle.

## Primary scope, with the necessary qualifications

[NEST, Secchi/Balint/Maurizi2605.12343v1](https://arxiv.org/html/2605.12343v1),
Sections 3–4.2, 7 and Appendices B–D: nonlinear compressible neo-Hookean static
equilibrium, prescribed displacement on the full boundary, FEniCS references.
Overlapping patch solvers exchange displacement traces through additive
Jacobi-style Schwarz sweeps and partition-of-unity assembly. The stopping
quantity is relative iterate change; the gradient is subsequently predicted
by a separate non-iterative pass. These define separate output roles.

The paper already compares one-shot tiling with iterative coupling. It also
states that iteration count grows with resolution, total runtime is not
established as linear, and the GPU-versus-one-CPU-core comparison is not
hardware normalized. Generic coupling, multilevel acceleration or exposing
these qualifications is not an unoccupied contribution. Section 7 promises
code/data upon acceptance; this reading does not establish a currently
released, licensed reproduction or independent continuum truth asset.

[Wu et al.2602.06842v2](https://arxiv.org/html/2602.06842v2), Sections 2–4
and selected experimental/conclusion scope: the published formulation already
distinguishes small full-cycle updates from nonzero physical residuals and
compares training objectives and update strategies. Its physics-aware Anderson
acceleration minimizes residuals of a known **linear discrete system** over
an affine combination of candidate iterates. This is a direct parent for
generic false-convergence diagnostics and residual-guided acceleration.

Use v2, dated June 2, 2026; v1 was consulted initially but is not the selected
current evidence version. The v2 abstract record states acceptance in IEEE
Computing in Science & Engineering. Preserve the SPD restriction on the
energy line-search formula and the source's qualification of near-resonant
Helmholtz residuals. Numerical results were read, not independently reproduced.
Small observed updates do not prove an exact non-solution fixed point.

The papers use different physical equations, information and update rules.
Their headlines do not constitute opposite predictions for a matched native
state, intervention and response. Valid model-family limitations may inform
scope; no internal implementation or retrieval history is scientific evidence.

## Control 1: a fixed point of the surrogate is a different target

Let the exact local-assembly map `T` have a physical fixed point `u*` and be
contractive with factor `q<1` on a specified invariant domain in a specified
norm. Suppose the learned assembled map satisfies
`sup_u ||T_hat(u)-T(u)|| <= eta` there. Then, for any point `u` in that domain,

\[
\|u-u^*\|\leq
\frac{\|\widehat T(u)-u\|+\eta}{1-q}.
\]

This follows by adding and subtracting `T(u)` and applying contraction.
If a learned fixed point exists in the domain, its error is at most
`eta/(1-q)`. The assumptions alone do **not** establish convergence of the
learned iteration. An empirical patch MSE is not a uniform assembled-map
error bound; an exact-map contraction is not a learned-map contraction.
Neither assumption is verified for nonlinear NEST by this audit.

For `T(u)=Q u+c` and `T_hat(u)=Q u+c+b`, the fixed-point displacement is
`(I-Q)^(-1)b` whenever the inverse exists. Its direction and amplification
depend on the full iteration map. A matched local error norm or a count of
patches alone does not determine the assembled error.

For a damped sweep `u_next=(1-alpha)u+alpha T_hat(u)`, `alpha>0`, the fixed
points are unchanged while the observed increment is scaled by `alpha`.
The bound uses `||u_next-u||/alpha`, not the increment alone. This is a
paper-only classical perturbation/control identity, not a new certificate,
an observed NEST error or a proposed damping experiment.

## Control 2: whole-cycle cancellation is not individual-step inactivity

Take the invertible scalar system `A=1`, right-hand side `f`, and residual
`r=f-u`. One classical step produces `u_s=u+r/2`, with residual `r_s=r/2`.
Let a linear correction map be `N(r_s)=-r_s`. The full cycle gives

\[
u_{next}=u_s+N(r_s)=u,
\]

for every `u`, including `u!=f`. Both substeps can be nonzero. This is an
exact false fixed point from a deliberately chosen correction map; linearity
and `N(0)=0` alone do not exclude it. No such learned correction is asserted
for the cited models, and it is not proposed as a useful solver.

Conversely, for a single update `delta=B r` with nonsingular `B`, exact zero
increment implies zero residual. Small increments can still accompany a
large residual when the inverse is poorly conditioned. Thus exact fixed
points, near-stagnation, cancellation and slow convergence must be separated
before proposing a mechanism. This is standard linear algebra.

## Control 3: residual acceleration has an information and span contract

For linear `A`, candidates `g_i` and weights summing to one,

\[
f-A\!\left(\sum_i\alpha_i g_i\right)
=\sum_i\alpha_i(f-A g_i).
\]

Residual minimization over these weights therefore finds the best point in
their affine hull in the chosen residual norm. If `A` is invertible, zero
residual is attainable exactly when its solution belongs to that hull.
An uninformative candidate history does not become informative merely by
changing the minimized norm; the cancellation example can supply such a
history. No universal convergence theorem is inferred from the published
successful comparisons.

For a nonlinear physical residual `F`, in general
`F(sum_i alpha_i g_i) != sum_i alpha_i F(g_i)`. A nonlinear extension must
evaluate the actual residual and establish its own local/global convergence
conditions. This does not supply a novel nonlinear method. Also, solving a
discrete system accurately is distinct from bounding continuum error;
residual norm, conditioning, lifting and discretization remain in the truth
contract. These are standard controls, not new scientific findings.

## Stop rule and next evidence that could matter

Stop generic learned-Schwarz coupling, damping, fixed-point/physical-residual
diagnosis, affine-history acceleration and elementary contraction certificates
as candidate generators. Another neural architecture or PDE name cannot
remove these direct-parent and standard-reduction barriers.

Two more specific **routing leads only** were located:

- [NOEM, Nature Computational Science2026](https://doi.org/10.1038/s43588-026-00974-2):
  publisher search text exposes the abstract, publication metadata and
  code/data availability statement. The full methods, supplement and source
  were not audited. No rights or independent truth asset is qualified.
- [Convex Neural Energy Elements2608.02036v1](https://arxiv.org/abs/2608.02036v1):
  official abstract claims a distinction between geometry-parameterized field
  predictors and convex boundary-energy elements. This is an author claim,
  not a verified failure of NOEM, matched primary disagreement or Paper G result.

Before any candidate harvesting, inspect that pair's exact boundary degrees
of freedom, PDE/geometry family, training target, energy construction,
nullspace, nonlinear/linear regime, assembled Hessian, reference truth and
compute budget. Check first whether the distinction reduces to classical
energy approximation, strong convexity or static condensation. Both works
predate the current closure; neither is a new-publication trigger. A qualified
re-entry ledger entry must identify a removed blocker before any new cycle.

All records remain private/internal. No implementation, source execution,
raw outcome access, numerical/symbolic experiment, simulation, GPU use,
outreach or publication occurred. Record-validation tests establish
consistency, not the requested scientific novelty or venue suitability.
