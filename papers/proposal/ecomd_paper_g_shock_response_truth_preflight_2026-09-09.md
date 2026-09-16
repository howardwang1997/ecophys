# Paper G: entropy-solution response truth preflight

PRIVATE / INTERNAL. Paper-only development record, 2026-09-09. Not public
research evidence, a prospectively frozen experiment, or a new topic cycle.

**Decision: partial_capability; no contribution blocker removed and no re-entry.**
Exact nonlinear dynamical controls are available for moving and merging Burgers
shocks. They sharpen the target of a future response test. Generalized shock
sensitivity and interaction calculus already have direct parents; the retained
algebra is a diagnostic asset, not a new theorem or learning method.

## 1. Existing blocker and primary collision

The repository connection is conservative neural-PDE prediction and physical
response. This preflight links the closed history-response and numerical-teacher
formulations. Their recorded blockers include
`generic_sensitivity_and_history_nuisance_remedies_have_direct_prior` and
`supplied_reference_certificate_is_elementary_error_propagation`. An exact
nonlinear entropy solution can improve validation capability without removing
either contribution blocker. No historical PDEBench reference error or trained
model defect is inferred.

Selected primary reading:

- [Herty et al., Algorithmic differentiation of hyperbolic flow problems,
  arXiv:2007.05330v1](https://arxiv.org/html/2007.05330v1), selected section 2
  examples and generalized-tangent definitions, with introductory method scope.
  The paper already treats a regular variation whose later moving shock needs
  both a regular sensitivity and a shock-position sensitivity. Example 2.3
  supplies the ramp family used below. No implementation or experiment was
  reproduced.
- [Herty and Zhou, A numerical method for solving the generalized tangent
  vector of hyperbolic systems,
  arXiv:2412.04251v1](https://arxiv.org/html/2412.04251v1), selected introduction,
  preliminaries, interface-condition discussion and multiple-shock scope.
  Their multiple-discontinuity construction explicitly assumes no interactions.
  That restriction is specific to this construction.
- [Bressan, A locally contractive metric for systems of conservation laws,
  1995](https://www.numdam.org/item/ASNSP_1995_4_22_1_109_0.pdf), section 5 scope
  and Theorem 5.1 statement. The theorem includes binary shock interactions,
  generalized-tangent evolution and interaction conditions, under sufficiently
  small total variation and the stated structural hypotheses. Full proof and
  applicability of all its assumptions to the finite-amplitude control below
  were not verified. This is not the separate Bressan--Marson variational-calculus
  paper, which was encountered as a reference only.

The current comparison establishes a direct classical parent, not a comprehensive
novelty audit of neural shock methods. Spatial derivatives, derivatives of a
fixed discretized executable, viscous-PDE derivatives and inviscid weak parameter
responses are different objects. Differentiability of one does not contradict
nondifferentiability of another.

## 2. Control A: nonlinear ramp and its moving-boundary term

Work on the real line with the entropy solution of

\[
u_t+(u^2/2)_x=0,\qquad u(0,x;a)=ax\,\mathbf1_{[0,1]}(x),\quad a>0.
\]

Write \(q=1+at\) and \(r=\sqrt q\). The exact solution is

\[
u(t,x;a)=\frac{ax}{q}\mathbf1_{[0,r]}(x).
\]

The smooth part satisfies the PDE. At the right shock the left state is
\(a/r\), the right state is zero, and Rankine--Hugoniot gives
\(r_t=a/(2r)\), as required. The jump is entropy admissible. Each trajectory
conserves mass \(a/2\); varying \(a\) does not keep mass fixed across trajectories.

Differentiating the regular part and the moving boundary independently gives
the following finite-measure derivative:

\[
\partial_a u=
\frac{x}{q^2}\mathbf1_{[0,r]}(x)\,dx
+\frac{at}{2q}\delta_r.
\]

Consequently, for a fixed \(\phi\in C_c^1(\mathbb R)\),

\[
\partial_a\!\int\phi u\,dx=
\int_0^r\phi(x)\frac{x}{q^2}\,dx
+\frac{at}{2q}\phi(r).
\]

Taking \(\phi=1\) on the full support verifies the derivative of conserved mass:
\(1/(2q)+at/(2q)=1/2\). The shock contribution is zero at \(t=0\) and positive
for \(a,t>0\). This is an exact positive/null pair. For a bounded future control,
\(a\in[1/2,3/2]\), \(t\in[0,4]\) confines support to \([0,\sqrt7]\).

A pure jump of height \(d\ne0\) translated by \(\epsilon\eta\), \(\eta\ne0\),
has state difference \(|d|\,|\epsilon\eta|^{1/p}\) in \(L^p\), \(1\le p<\infty\).
Its difference quotient diverges in \(L^p\) for \(p>1\). In \(L^1\) its norm
stays nonzero and it has no function-valued limit: the weak limit is a point
mass. The initial ramp variation is regular in \(L^1\) and \(L^2\), but at
positive time this moving-boundary obstruction appears.

### Observation contract

For fixed nodes away from front crossings, differentiating sampled values sees
only the regular term. At a front crossing the nodal map jumps. Thus a sequence
of consistent nodal quadratures can converge to the observable while their
ordinary parameter derivatives converge to only its regular contribution.
Observation refinement and differentiation need not commute.

For a **true cell average** \(y_j=h^{-1}\int_{C_j}u\,dx\), with the shock strictly
inside a cell, its derivative includes the shock weight \(w=at/(2q)\) divided
by \(h\) in that cell. The weighted discrete \(L^2\) norm of this component is
\(|w|/\sqrt h\). A growing derivative norm can therefore be part of the exact
target. At a cell boundary the average vector can have distinct one-sided
derivatives. Pairing with a fixed smooth spatial test function and the correct
cell weights instead recovers the weak observable response.

Point restriction, arithmetic averages of stored point samples, and integrals
over physical cells must retain different labels. A test function chosen after
seeing the shock, a co-moving observation, or a positive-viscosity target would
change the contract. These controls make no claim about the observation
semantics or errors of any historical repository data file.

## 3. Control B: compact mass-preserving shock merger

Use the same entropy PDE, \(p\in(-1/4,1/4)\), and

\[
u_0^p(x)=
\begin{cases}
0,&x<-10,\\
2,&-10<x<-1+p,\\
1,&-1+p<x<1-p,\\
0,&x>1-p.
\end{cases}
\]

Endpoint conventions do not affect the state as an integrable function.
The initial mass is \(2(9+p)+(2-2p)=20\) for every \(p\). The shared left
rarefaction has \(u=(x+10)/t\) on \([-10,-10+2t]\), preceded by zero and
followed by the plateau of height two. Before collision the descending fronts are

\[
X_1=-1+p+\tfrac32t,\qquad X_2=1-p+\tfrac12t.
\]

Their entropy-admissible speeds give collision time
\(t_c(p)=2-2p\) and collision position \(t_c(p)\). The merged \(2\to0\) shock
has speed one and position \(X=t\), independent of \(p\). On \(0<t\le4\),
the rarefaction stays strictly to the left of the shocks; it reaches the merged
front only at \(t=10\). These pieces define the entire solution for the frozen
time range, not merely an isolated front sketch.

At the nominal collision time \(t=2\), the state equals the baseline exactly
for \(p\ge0\). For \(p<0\), its difference from the baseline is minus one on
\([2+p,2]\), plus one on \([2,2-p]\), and zero elsewhere. Hence

\[
\|u^p(2)-u^0(2)\|_1=2|p|,\qquad
\|u^p(2)-u^0(2)\|_2^2=2|p| \quad(p<0),
\]

and both are zero for \(p\ge0\). The mass difference is always zero.
For \(b=-p>0\) and any fixed smooth test function,

\[
\int\phi(u^p-u^0)\,dx
=\int_0^b[\phi(2+s)-\phi(2-s)]\,ds,
\qquad
\left|\int\phi(u^p-u^0)\,dx\right|
\le\operatorname{Lip}(\phi)b^2.
\]

The weak observable's first derivative at \(p=0,t=2\) is therefore zero from
both sides. With a fixed compactly supported \(\phi\) equal to \(x\) on the
relevant interval, the response is exactly \(p^2\) for \(p<0\), zero for
\(p\ge0\). A nonzero finite response and a zero first derivative coexist.
The state map has no \(L^1\) first derivative there: the left difference
quotient has norm two and converges weakly to zero, while the right quotient
is identically zero. A zero weak derivative is **not** an \(o(|p|)\) strong
state approximation or a regular generalized tangent through this change in
shock count.

For fixed \(2<t\le4\) and \(|p|<\min(1/4,(t-2)/2)\), all members have
merged and the entire states agree. Before collision their weak parameter
derivatives are \(\delta_{X_1}-\delta_{X_2}\); after collision this relative
position direction is erased. This is classical entropy evolution and
Rankine--Hugoniot algebra. It is a useful merger null, not new rephasing,
universal information loss, or a refutation of the older interaction theory.

Here the intervention redistributes initial front positions while preserving
mass. It is not the fixed additive current-state \(L^2\) pulse in cycle 29.
The previous contribution decision cannot be reversed by silently substituting
this intervention.

## 4. Bounded truth-asset contract

| Contract item | Present capability and boundary |
|---|---|
| Estimands | Exact inviscid state, prescribed strong finite-difference norms, fixed smooth-observable parameter responses, and their stated one-sided limits in the two scalar families. |
| Assignment/interference | Deterministic initial amplitude or mass-preserving front-position changes. Each trajectory is a separate mathematical unit. PDE, physical coordinates, entropy condition and clock are fixed; shared rarefaction interactions are explicitly bounded in time. |
| Lifecycle/replay | Family ID, parameter, domain, initial profile, time, viscosity flag, front/fan formulas, collision ordering and observation operator must all be retained. Exact formulas specify mathematical replay; executable conformance, code/config/container hashes and immutable release IDs do not yet exist. |
| Rights/ethics/release | Primary-paper reading and internal independently worked algebra only; no participants, third-party code reuse or raw data access. A reusable code/data release and its dependency rights have not been qualified. |
| Confirmation | Both controls are already development assets. Future whole-family confirmation must be independently chosen and sealed before outcome access; neither these formulas nor a new parameter draw is independent confirmation. |
| Replication | No executed independent lineage or independently governed same-estimand asset. Classical theory and our scalar hand calculation are not two independent empirical replications. |
| Precision/cost | Symbolic identities give zero mathematical approximation error under their assumptions. Floating-point, quadrature and numerical derivative errors remain unqualified. Zero scientific compute used; training, numerical validation and independent replication have no current budget or authorization. |

Stop if the target switches between inviscid and viscous dynamics, point and
cell observations, front shifts and additive pulses, or physical and adaptive
test coordinates without a new contract. Stop any claim that drops the shock
mass, equates weak first-order null with no finite effect, or calls two
calculations from the same classical family independent confirmation.

## 5. Decision and next discriminating requirement

Retain two analytic control bundles and an explicit observation/derivative
contract. Register the direct generalized-shock/interaction parent on the
existing history-response route and append one `partial_capability` re-entry
audit. All route statuses remain unchanged; no raw question, new cycle, full
hostile audit, forecast or machine card is created.

A future re-entry needs a specific contribution beyond existing sensitivity
and interaction methods, attached to a fixed response target and a qualified
validation asset. Neither a moving-shock example nor the no-interaction scope
of one method supplies that contribution. Current-model prevalence and useful
transfer beyond these exact scalar controls remain unresolved.

No implementation, simulation, outcome access, GPU work, outreach, participant
work, purchase or publication is authorized by this preflight. The broader
Paper G search remains open; no venue probability is assigned.
