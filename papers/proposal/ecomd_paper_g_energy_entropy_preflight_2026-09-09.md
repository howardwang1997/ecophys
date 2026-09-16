# Paper G: energy target and entropy-admissibility preflight

**PRIVATE / INTERNAL — discovery infrastructure, not public research evidence.**

Session began 2026-09-09T07:14:16Z. Structured record:
`research/paper_g/energy_entropy_preflight_20260909.yaml`.

**Decision: partial source capability, zero removed blockers; no new candidate.**
The useful result is a precise separation of full-state energy, resolved energy,
energy of a conditional mean, and a local entropy inequality. The elementary
controls below and their established remedies do not provide an independent
learning contribution. No trained-model defect or invalid implementation is
used as scientific evidence.

## Repository connection and scope

Paper D studies affine mass constraints in Advection and shallow water. Its
scope and analytic propositions were read; no raw outcomes or checkpoints were
accessed. Moving to nonlinear energy requires a new target contract. The closed
`theory_exploration_equation_audit_v3` already records state-closure reduction to
predictive-state methods and the inability of calibration to recover omitted
state. This preflight checks whether physically defined energy/state sources
remove those blockers. It does not reopen that formulation, create another
topic cycle, or extend market-specific closures to the whole PDE domain.

## Primary sources and their actual claims

| Source; inspected scope | Relevant prior | Boundary |
|---|---|---|
| [van Gastelen, Edeling and Sanderse](https://arxiv.org/pdf/2301.13770v5), sections 2.5–3.2, equations 29 and 33–42; code pointer | Energy-conserving neural closure augments resolved state with subgrid variables and permits backscatter while bounding total energy. | Its subgrid state is a signed linear compression, not just one unsigned energy scalar. Approximate energy storage is not a claim of complete hidden-state identification. |
| [Roohi, Shoja-sani and Stefanov, Physics of Fluids 2026](https://doi.org/10.1063/5.0328463), sections II.C–D | Conditional stochastic collision modeling with pair momentum/energy constraints; explicitly discusses conditional-mean variance suppression. | No independent endorsement of its fitted kernel, thermodynamic guarantees or optional cell-level stabilization. Only the stated pair-level and prediction-target contract is used here. |
| [wPINNs](https://arxiv.org/pdf/2207.08483), section 2.1 and equations 2.10–2.11 | Weak conservation plus local Kruzhkov entropy residuals, optimized over test functions; source also provides error analysis. | Local entropy testing and entropy-solution approximation are established methods. No theorem for general multidimensional systems is inferred. |
| [Tanaka et al., AISTATS 2025](https://proceedings.mlr.press/v258/tanaka25a.html), primary abstract only | Energy-consistent operator learning for Hamiltonian and dissipative PDEs using a training penalty. | The abstract does not establish a same-observation contradiction with the other sources or a claim about coarse-only energy. |

The [ECNCM_1D repository](https://github.com/tobyvg/ECNCM_1D) is a documented
Julia source lineage for the first work. README and directory metadata were
inspected, including the source, test, manifest and tutorial pointers. The page
displays an MIT label; exact source, license text and dependencies are not
qualified here. No notebook outputs, training data or implementation were read.

## Check A: equal subgrid energy does not determine energy transfer

Use the full unforced periodic viscous Burgers equation
u_t+u*u_x=nu*u_xx on [0,2*pi], nu>0, with the smooth initial field

\[
u(x,0)=a\sin x+b\sin 2x,\qquad a\ne0.
\]

Define ||u||^2=(1/pi) integral u^2 dx and E=||u||^2/2. Let P retain the
first sine mode. Direct projection of the PDE at time zero yields

\[
\dot a=ab/2-\nu a,\qquad
\dot b=-a^2/2-4\nu b,
\]
\[
\dot E_P=a^2(b/2-\nu),\qquad
\dot E=-\nu(a^2+4b^2)<0.
\]

These are exact instantaneous derivatives of the full PDE at the specified
initial state. Higher modes are subsequently generated; no two-mode truncated
rollout or long-time conclusion is asserted.

Choose b=+B and b=-B with B>2*nu. The two legal initial states have the same
resolved field, zero total momentum, subgrid energy B^2/2, full energy and full
energy dissipation rate. Their resolved energy derivatives have opposite signs.
Thus the pair (resolved field, total subgrid energy) does not identify the
transfer direction. Enforcing monotone resolved energy would reject one exact
truth response. Retaining the signed b distinguishes this particular pair;
knowing the complete field supplies the exact PDE response.

This is an elementary closure/state-sufficiency witness. It is consistent with
the cited closure model, which already permits resolved/subgrid exchange and
retains signed compressed coordinates. It is not evidence that the source's
actual compression maps these two fields to the same state. A source-specific
collision would have to use its exact transform T, not just total subgrid energy.

## Check B: the invariant of a realization is not the invariant of its mean

Let O be the supplied information, and suppose ||Y||=r(O) almost surely, with
finite second moment. Write m=E[Y|O] and Sigma=Cov(Y|O). Then

\[
r^2=\|m\|^2+\operatorname{tr}\Sigma,
\quad
\mathbb E[\|Y-z\|^2\mid O]
=\operatorname{tr}\Sigma+\|z-m\|^2.
\]

Consequently a deterministic predictor constrained to ||z||=r has excess Bayes
risk (r-||m||)^2. This follows by taking the closest point on the sphere to m;
if m=0, all points on that sphere are minimizers. For an isotropic elastic
scattering kernel Y=r*S with S uniform on the unit sphere and r>0, m=0. The
conditional-mean predictor has risk r^2, while every radius-r deterministic
prediction has risk 2*r^2. Incoming state and radius are fixed; physical
scattering randomness is the declared uncertainty.

An independently sampled correct realization also has risk 2*r^2 against an
independent true realization. Sampling therefore does not beat the conditional
mean at this squared-loss task. It answers a different, distributional task and
must be assessed using an appropriate proper distributional score and physical
sample constraints. The mean is a valid statistic even though it is not a
possible individual collision outcome.

The controls matter: if Sigma=0, the equality conflict disappears. If the
constraint is the convex upper bound ||z||<=r, the mean is feasible. If AY=c(O)
is affine, A*m=c(O) by conditional expectation. Thus this argument neither
refutes Paper D's affine constraints nor says all dissipation inequalities
conflict with Bayes prediction. It is standard conditional-expectation geometry,
not a new uncertainty method or a learned-model experiment.

## Check C: a global energy bound does not replace local entropy admissibility

For inviscid Burgers on the periodic interval (-pi,pi), take the stationary
square wave u=+1 on (-pi,0) and u=-1 on (0,pi). Since u^2/2=1/2 almost
everywhere, it is an exact distributional weak solution with that initial data.
Its mass is zero and its quadratic energy is constant. Any time-independent
spatial integral of eta(u) is constant, so global entropy nonincrease passes.

For the convex entropy pair eta=u^2/2, q=u^3/3, however,

\[
\partial_t\eta(u)+\partial_x q(u)
=\tfrac23\delta_{\pi}-\tfrac23\delta_0
\]

on the circle. A nonnegative test function supported near the periodic seam
detects a positive residual. Local entropy admissibility fails at the expansion
jump even though the two signed contributions cancel globally. This example
uses periodic boundaries, so no omitted boundary-flux term causes the contrast.

The standard entropy condition removes this weak solution. Neural min-max
entropy residuals and classical entropy-admissible solvers are competent
baselines, not proposed innovations. This is a textbook weak-versus-entropy
distinction, not evidence that an entropy-trained neural method fails it.

## Truth-asset preflight and stop rules

- Supported estimands: instantaneous resolved/full energy transfer under a fixed
  physical PDE and projection; conditional squared risk under a declared physical
  uncertainty kernel; and local weak entropy residual under specified test functions.
  These are separate contracts and must not be pooled into one realism score.
- Assignment and interference: choose full initial conditions before evolution;
  separate physical scattering, observation noise and model sampling. The
  matched-sign Burgers pair is a deterministic diagnostic, not an independent
  empirical replication. No future hidden state is supplied to a coarse predictor.
- Lifecycle and replay state: exact PDE, viscosity, domain, boundary conditions,
  initial fine field, projection/quadrature, signed compression and initialization,
  optional forcing, time integration, solver tolerances, entropy pair/test-function
  support, observation map and RNG state. Metadata alone does not qualify these.
- Rights, ethics and release: no participants or field collection; repository
  license label does not settle source/dependency/data/derived-release rights.
- Untouched confirmation: prospectively separate fine initial-field families,
  uncertainty kernels and PDE regimes; freeze transform fitting, training,
  calibration, selection and evaluation roles before outcomes. Paper D is
  development for a newly formulated question, with its existing labels retained.
- Replication and cost: analytic controls are not two independently executed
  solvers. No independent nonlinear solver or real-system bridge is qualified.
  Current scientific compute is zero; source evolution, auxiliary-state storage,
  training, inference and local entropy integration costs remain unqualified.
- Stop: no escalation for applying a law to the wrong state/statistic, forgetting
  subgrid exchange, or replacing local admissibility with a global bound. A new
  method must leave a residual after competent closure, stochastic-kernel and
  entropy baselines. Incomplete replay, rights or confirmation also stops execution.

## Disposition

Four primary works and one source repository supply partial capability and
direct parents. Three exact controls are retained. No substantive novelty or
omitted-state blocker has been removed; no new question cycle, forecast, F3
audit, machine card, outcome access, scientific implementation or compute follows.

The next admissible update is a source-specific result or truth asset that
distinguishes rival predictions at the same complete state, projection,
information supply and target, after the named competent baselines. Adding
energy or entropy constraints, or showing an underspecified constraint rejects
truth, is not sufficient. No publication probability is assigned.
