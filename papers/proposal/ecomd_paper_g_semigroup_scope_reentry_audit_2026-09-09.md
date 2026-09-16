# Paper G: convex-semigroup theorem scope audit

PRIVATE / INTERNAL. Paper-only development audit, 2026-09-09.
Not a new topic cycle, prospectively frozen experiment or public research result.

**Decision: not_trigger; no recorded contribution blocker removed.** A recent
semigroup approximation theorem is a relevant direct parent, but its target
class does not automatically contain nonlinear conservative state evolution.
The distinction can be decided by elementary algebra before implementation.
The calculations below are scope controls, not claimed novel theorems.

## 1. Source, target and repository connection

The new primary work is Blessing, Schmocker and Sgarabottolo,
[Neural operators approximate strongly continuous convex monotone semigroups,
arXiv:2609.02727v1](https://arxiv.org/html/2609.02727v1), dated September 2, 2026.
Reading covered definitions, selected assumptions, Theorems 3.6 and 4.12,
the finite-max construction and the opening PDE example. The target is convex
and monotone in its input function. Approximation on bounded time horizons
requires stability and regularity conditions. The quantitative envelope result
also depends on action-space covering complexity. It is not a finite-data
learning guarantee or a uniform-in-time guarantee for one fixed trained model.

The general Chernoff network class is not automatically input-convex. Nor does
Definition 4.4 make every arbitrary ReLU readout convex. The finite-max readout
constructed in the approximation proof does have that structure. Distinguish
the target assumptions, a theorem's constructed approximant, and an entire
architecture class; the rigidity calculation does not condemn all networks
in the paper.

The already registered [Semigroup Consistency as a Diagnostic for Learned
Physics Simulators](https://arxiv.org/abs/2605.26324) was rechecked at abstract
scope only. It is an ICML 2026 workshop paper, not an ICML main paper. A temporal
composition diagnostic and a conditional approximation theorem are different
claims and do not constitute opposing predictions on a matched experiment.

The repository connection is the existing conservative neural-PDE work and its
output mean correction in `scripts/constraint_iclr_common.py`, function
`project_pde_output`. Selected source lines were read, without importing or
executing the module. The correction fixes the mean; it does not assert that
the complete input-to-state map is convex. Nothing here establishes a failure
of a repository trained model or changes Paper D evidence roles.

The re-entry audit links `theory_exploration_equation_audit_v3` and
`ncs_invariant_calibration_v4`. Their recorded method and coupling-theorem
blockers remain. Broad positivity, realizability and memory-embedding searches
were intake only; no additional raw question or fifteen-work review was opened.

## 2. Control A: conservation and input convexity

Let \(C\subset L^1(\Omega)\) be convex and \(F:C\to L^1(\Omega)\).
Assume pointwise order convexity,

\[
F(\lambda f+(1-\lambda)g)
\le \lambda F(f)+(1-\lambda)F(g),\qquad 0\le\lambda\le1,
\]

and integral conservation \(\int F(f)=\int f\) for all \(f\in C\).
The Jensen gap

\[
D_F(f,g;\lambda)=\lambda F(f)+(1-\lambda)F(g)
-F(\lambda f+(1-\lambda)g)
\]

is nonnegative and has integral zero. It vanishes almost everywhere.
Thus \(F\) preserves every convex combination: it is affine on \(C\).
If \(C\) is a vector space and \(F(0)=0\), it is linear. Monotonicity is
not needed for this implication. The same argument works on a discrete grid
with strictly positive cell weights, and on a convex fixed-mass family.
It does not apply to a signed invariant functional that fails to be strictly
positive on nonzero nonnegative outputs.

### Approximate form and approximation boundary

For one triple \(f,g,m=\lambda f+(1-\lambda)g\), suppose each integral defect
\(|e(z)|=|\int F(z)-\int z|\) is at most \(\epsilon_M\), and
\(\|(D_F)_-\|_1\le\epsilon_C\). Then

\[
\int D_F=\lambda e(f)+(1-\lambda)e(g)-e(m),\qquad
\|D_F\|_1=\int D_F+2\|(D_F)_-\|_1
\le2\epsilon_M+2\epsilon_C.
\]

These are errors on the same three inputs under the same physical weights,
not averages over unrelated training samples. For an exact conserving target
\(S\), write \(d=\|D_S(f,g;\lambda)\|_1\). If a candidate \(F\) approximates
all three target outputs within \(E\) in \(L^1\), the triangle inequality gives

\[
E\ge d/2-\epsilon_M-\epsilon_C.
\]

In particular, exact conservation and exact pointwise convexity imply
\(E\ge d/2\). This elementary bound is not a statistical generalization result,
a sharp minimax claim, or evidence that any actual network obeys its hypotheses.

### Nonlinear physical control before any shock

Take smooth \(2\pi\)-periodic data on the real line for viscous or inviscid Burgers,

\[
u_t=\nu u_{xx}-u u_x,\qquad \nu\ge0,
\quad f=c+a\sin x,\quad g=c-a\sin x,\quad c>a>0.
\]

Use a sufficiently short classical-solution interval (before shock formation
when \(\nu=0\)). All three initial states \(f,g,(f+g)/2=c\) have the same
mass per period. At time zero their generator Jensen gap is exactly

\[
\tfrac12 A(f)+\tfrac12 A(g)-A(c)=-a^2\sin x\cos x.
\]

The linear viscosity terms and constant advection contributions cancel.
Consequently,

\[
D_{S_t}(f,g;1/2)=-a^2t\sin x\cos x+O(t^2),\qquad
\|D_{S_t}\|_1=2a^2t+O(t^2)
\]

over one period. The gap has both signs for sufficiently small positive time,
so this state semigroup is neither pointwise convex nor concave. This failure
of the target-class hypothesis already occurs for smooth positive data; it is
independent of the previous moving-shock derivative issue. An exactly conserving
and input-convex approximant has three-input maximum error at least
\(a^2t-Ct^2\) for some finite \(C\) on a sufficiently short interval, with
\(a,c,\nu\) fixed. No bound uniform over viscosity or long times is asserted.
Linear advection and heat evolution have gap zero and provide the null.

This argument does not claim that the cited theorem was stated on a periodic
finite-volume grid. Periodic smooth functions are a bounded smooth subfamily
on the real line; a hypothetical convex Burgers state operator would restrict
to a convex map on that family, where mass over one period is defined.
No claim in the primary theorem says that this Burgers state map belongs to
its target class.

## 3. Control B: state, value and projection semantics

For two equally weighted cells, let \(I\) be identity and \(P\) swap the cells. Both are linear,
positive, constant-preserving and sum-preserving. Their pointwise envelope is

\[
B(z)=\max(Iz,Pz)=(\max(z_1,z_2),\max(z_1,z_2)).
\]

It is convex, monotone and constant-preserving. For \(z=(1,0)\), its output
sum is two rather than one. This is entirely legitimate if \(z\) is a payoff
and the maximization selects actions separately at each starting state.
It is not a conservative density update. The toy illustrates one-step
forward/backward semantics, not every continuous-time assumption of the
primary theorem.

For a fixed Markov kernel \(K\), payoff propagation is \(z\mapsto Kz\),
whereas forward density propagation is \(\rho\mapsto K^T\rho\). The latter
preserves total probability because \(K\mathbf1=\mathbf1\). In a nonlinear
Bellman envelope the selected policy can depend on the payoff: it does not
define one payoff-independent linear adjoint density operator. Fixing that
policy supplies a forward kernel, while changing the policy changes the target.
An HJB value function, a spatially integrated potential and a physical density
must therefore keep different labels. A nonlinear coordinate change also
changes the convex mixtures and invariant functional in the rigidity test.

The repository-style mean correction has the algebraic form

\[
\Pi_zG(z)=G(z)+[\overline z-\overline{G(z)}]\mathbf1.
\]

It preserves the input mean but can remove input convexity. On the nonnegative
unit simplex take \(G(z)=(z_1^2,0)\). Then

\[
\Pi_zG(z)=((1+z_1^2)/2,(1-z_1^2)/2).
\]

This is nonlinear, nonnegative and sum-preserving; its second component is
concave. Thus mean correction alone does not force an affine model. The same
distinction prevents interpreting convex energy functions, convex losses,
convex optimization or monotonicity alone as order convexity of every output
coordinate with respect to the initial field.

## 4. Decision and next condition

The new theorem provides a direct semigroup-approximation parent, but no
same-target result that removes the closed routes' contribution blockers.
The exact and approximate Jensen-gap controls, smooth Burgers nonlinearity
control, linear null and state/value/projection examples are retained as two
paper-only diagnostic bundles. They are elementary consequences of known
convexity, conservation and PDE algebra, without a novelty claim.

Re-entry requires a distinct contribution after fixing the evolved object,
input mixtures, invariant weights, regularity, horizon and learning/access
cost. Neither citing the recent theorem, enforcing a generic semigroup loss,
nor adding mean projection meets that condition. A representation change must
carry the original physical target and validation contract through the map.

One theorem/counterexample audit is appended to the re-entry ledger. No new
raw question, cycle, F3, forecast, machine card, implementation, simulation,
outcome access, GPU work or public release is authorized. The broader Paper G
objective remains open; no venue probability is assigned.
