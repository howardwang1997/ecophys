# Paper G convex-semigroup theorem scope audit

PRIVATE / INTERNAL. Formal:
`papers/proposal/ecomd_paper_g_semigroup_scope_reentry_audit_2026-09-09.md`.
Contract: `research/paper_g/semigroup_scope_reentry_audit_20260909.yaml`.

Decision not_trigger, no removed contribution blockers or candidate harvest.
New primary arXiv2609.02727v1 (September2) gives conditional approximation for
convex monotone semigroups on bounded horizons; it does not automatically cover
nonlinear conservative physical state maps, supply a learning/sample-cost
guarantee, or establish fixed-model uniform-in-time accuracy. Target convexity
must not be conflated with every Chernoff network or arbitrary ReLU readout in
Definition4.4; the constructed finite-max approximants have that structure.
The existing semigroup diagnostic2605.26324 is an ICML2026 workshop paper, not
main; abstract rechecked. No matched primary contradiction identified.

Retained elementary rigidity: on a convex L1 family or positive-weight grid,
pointwise input-convexity and exact integral conservation force affinity.
A nonnegative Jensen gap with zero integral must vanish. For a triple with
mass defects<=epsilon_M and negative-gap norm<=epsilon_C, full gap norm is
at most2*epsilon_M+2*epsilon_C. If the target gap norm is d, maximum prediction
error on the triple is at least d/2-epsilon_M-epsilon_C.

Smooth positive periodic Burgers inputs c±a*sin(x) have midpoint c. Their
generator Jensen gap is -a^2*sin(x)*cos(x), independent of viscosity; short-time
gap L1=2*a^2*t+O(t^2). Thus the state map is neither convex nor concave even
before shocks. Linear heat/advection provide zero-gap controls. This is simple
PDE/convexity algebra, not a new theorem or trained-model observation.

State/value control: pointwise max of identity and swap sends (1,0) to(1,1),
valid for payoff optimization but not a density update. A fixed Markov kernel
acts on payoffs and its transpose on densities; a payoff-dependent policy has
no single payoff-independent linear adjoint. Native-state semantics matter.
Repository-style mean correction can break input convexity while preserving
mass and nonlinearity; an explicit positive unit-simplex example is retained.
The source function project_pde_output was read, not executed. No claim that
Paper D models impose input convexity or fail this diagnostic.

Next re-entry requires a distinct contribution after fixing evolved object,
mixtures, invariant weights, regularity, horizon and learning/access cost.
No new cycle, forecast, card, scientific implementation, outcomes, GPU or release.

Verified 2026-09-09T09:47:33Z: graph293 /edges274 /locators1270; evidence899;
re-entry113 /qualified0; cycles21 /raw133 /cards0 unchanged. Scoped canonical
validation, source/contract/trigger parity, local-source hash,18 existing tests
and git diff --check passed. Receipt: `logs/private/paper_g_semigroup_scope_20260909_verification.md`.
