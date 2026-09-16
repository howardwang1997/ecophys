# Paper G: response-error bounds and trajectory-law contracts

PRIVATE / INTERNAL — public_evidence_eligible=false.
Session started 2026-09-10 03:55 Pacific/Auckland. Previous turn: progress.
Source/theorem preflight only; no new candidate, search cycle or experiment.

Repository connection: the earlier [conservation/generalization D-3 contract](ecomd_question_contract_constraint_inductive_bias_2026-08-27.md)
asks whether enforcing an invariant removes dynamical error or redirects it
into other channels. This audit supplies attribution controls for that
question and the existing EcoMD force/bath analogy. It imports no Paper D
outcomes, historical publication forecasts or experiment authorization.

## Decision

The proposed generic extension from force accuracy to certified dynamical
observables has direct parents, including an explicit underdamped example in
the existing goal-oriented learning paper. An integrator-aware extension also
has a direct parent. Stop those method-only formulations. This does not close
the deeper question about the causal effect of a specified learned force
component on a specified physical response.

Disposition: `not_trigger`; no recorded blocker removed. The preceding dual-
head asset still lacks a qualified pure-component intervention, independent
physical response truth and untouched confirmation. Conditional mathematical
bounds below do not fill those gaps. The attachment to the closed
`slow_memory_random_batch_invariant_correction` route is a reusable control
cross-reference, with no scope or execution authority change.

## Three primary contracts

- [Zou, Lie and Marzouk, arXiv2603.20467v2](https://arxiv.org/html/2603.20467v2):
  selected Sections2–3 and the Section4 scope statement. Remark3 explicitly
  includes underdamped Langevin with noise acting on momentum. Lemma7 uses
  second moments under both path laws and KL divergence; Proposition11 needs
  a valid reference second-moment upper bound. The gradient has additional
  regularity and stopping-time hypotheses. Section3.4 separates empirical
  approximation from the population loss. Overdamped demonstrations do not
  make the underdamped case an unoccupied theorem. This extends the reading
  scope of the already registered source; it is not a newly discovered paper.
- [Birrell, Katsoulakis and Rey-Bellet, arXiv1906.09282v4](https://arxiv.org/html/1906.09282v4):
  Theorem1, event-probability corollary and AppendixD.3 cover observable-specific
  information bounds and stopped path entropy. The appendix explicitly writes
  a drift change as `sigma beta` and requires a genuine exponential martingale
  and uniqueness in law. An auxiliary process can be included before
  marginalization. These are conditional tools, not automatic estimates from
  a finite force dataset. No final/preprint identity audit is asserted.
- [Kieninger, Ghysbrecht and Keller, arXiv2303.14696v1](https://arxiv.org/html/2303.14696v1):
  Table1, SectionsIV–V and AppendicesA.1–A.2 describe integrator-dependent
  transition supports and likelihood ratios. ABOBA supplies a common support;
  BAOAB generally does not. This concerns the full phase-space trajectory at
  integration-step resolution. No universal statement about position-only or
  coarsely saved paths follows. Only the displayed algorithms and support
  arguments were checked, not implementations or empirical results.

The earlier Dupuis et al.1503.05136 abstract was a locator/parent lead only.
Other search summaries and implementation listings are not theorem evidence.
The existing [Bigi v6 source](https://arxiv.org/html/2412.11569v6), Sections4.4
and4.6, was revisited to fix the relevant response: the velocity-correlation
spectrum, including its low-frequency diffusion interpretation. Published
numerical values are not being used as independent Paper G evidence.

## A finite-horizon kinetic bound, with its required information

Use unit masses and Boltzmann constant, one fixed bath temperature `Tb>0`,
friction `gamma>0`, common initial state, and nonexplosive well-posed dynamics:

    dq = v dt,
    dv = [F_i(q)-gamma v]dt + sqrt(2 gamma Tb)dW,   i=0,1.

Let `r=F_1-F_0` and fix physical horizon `H`. The perturbation `(0,r)` lies in
the noise range, even though position has no direct noise. Under the usual
Girsanov integrability conditions, for the full continuous path laws,

    K_H = KL(P_1 || P_0)
        = E_1 integral_0^H |r(q_t)|^2/(4 gamma Tb) dt.

This is a standard specialization; no gradient assumption on r is needed.
A uniform bound `|r|<=R` is one sufficient finite-horizon martingale condition
and gives `K_H<=H R^2/(4 gamma Tb)`. Unbounded learned forces require their
own verified integrability argument. Different initial laws require their
initial relative entropy as well. A stationary force-error average may replace
the time occupation average only under a justified stationary law, not merely
because both processes start at the same point.

Pinsker's inequality then yields, for a fixed target set A and its first hit
time tau,

    |P_1(tau<=H)-P_0(tau<=H)| <= min(1,sqrt(K_H/2)),
    |E_1[min(tau,H)]-E_0[min(tau,H)]| <= H min(1,sqrt(K_H/2)).

The second line follows because the capped time takes values in [0,H].
These controls avoid an unknown second-moment bound for the uncapped time,
but change the estimand. Two hypothetical time laws concentrated at H+1 and
H+L have identical capped observations and means separated by L-1. That is
an elementary information control, not a kinetic-SDE impossibility theorem.
Recovering an uncapped mean needs separately justified tail information.

Computing K_H still needs reference-force evaluations over the relevant
occupation law, or an independently proved envelope. A training-set RMSE
does not by itself supply either. A population inequality is not a finite-
sample confidence interval. Relative error for rare hitting probabilities
and uniformity as relaxation or bath parameters degenerate remain unproved.
This KL compares two forward models; it is not their time-reversal entropy
production, and is not the preceding session's mean-work diagnostic.

In particular, capped hitting times are controls, not replacements for the
velocity-correlation target. A velocity-product observable is unbounded; the
second-moment route needs corresponding joint fourth-moment control. For a
specified stationary correlation C(t), even the rectangular finite-lag
approximation to its spectrum leaves a tail bounded by
`2*integral_H^infinity |C(t)|dt`, if that integral exists. Neither that decay
envelope nor the correct stationary preparation follows from a finite-horizon
KL bound. No diffusion coefficient or infinite-lag spectrum is certified here.

## A matched continuous/discrete support control

The following hand calculation instantiates established splitting theory;
it is neither a new theorem nor an observed software behavior.

For one-dimensional BAOAB, step size h and force F, eliminate the intermediate
states from the drift/kick/Ornstein-Uhlenbeck steps. Every one-step transition
from fixed (q,v) satisfies

    v' + v - 2(q'-q)/h = (h/2)[F(q')-F(q)].

Take `F_0(q)=-kq`, `F_1(q)=-kq+epsilon*tanh(q)`, with k>0 and epsilon!=0.
The force difference is bounded and both potentials are confining. At fixed
gamma,Tb,H the continuous-time laws satisfy the preceding finite entropy
bound, since the forces are globally Lipschitz and the perturbation bounded.

A transition satisfying both BAOAB constraints must have tanh(q')=tanh(q),
hence q'=q. The BAOAB position update has a nondegenerate Gaussian noise
term for every h>0, so that event has probability zero. The two conditional
one-step phase-space laws are therefore mutually singular. This remains
true for arbitrarily small nonzero epsilon and positive h. It says nothing
about nonconservative-force effects: this scalar control uses two conservative
forces. Nor does it assert singularity after marginalizing or skipping steps.

For ABOBA, put `c=exp(-gamma*h)`, `s^2=Tb*(1-c^2)` and `q_m=q+h*v/2`.
The one-step law instead obeys

    v' = c*v + h*(1+c)*F(q_m)/2 + s*xi,
    q' = q + h*(v+v')/2,                  xi~N(0,1).

The supporting line is independent of F. The Gaussian mean-shift formula
gives the conditional entropy for the same two forces:

    KL(K_1(q,v) || K_0(q,v))
      = h^2*(1+c)^2*r(q_m)^2 / [8*Tb*(1-c^2)].

Its leading small-h term is `h*r(q_m)^2/(4*gamma*Tb)`. Chain-rule sums give
the entropy of the discrete full trajectory when the initial law is common.
This is exact for that discrete kernel, not an exact continuum-response
certificate. Changing the integrator requires accounting for the resulting
discretization error, and is not a novel response-learning principle.

## Bath changes and access boundaries

For the continuous unit-mass process, quadratic covariation is
`[v_i,v_j]_H=2*gamma*Tb*H*delta_ij`. If two constant baths have different
gamma*Tb, their full continuous velocity-path laws are singular. A drift-only
likelihood cannot compare them. If gamma*Tb is unchanged, that particular
obstruction disappears, but the changed friction and its integrability must
still be handled. Finite saved observations require their own transition-law
analysis. This is a standard quadratic-variation control, not a new effect.

The complete prospective contract must freeze force functions, masses, bath,
initial law, boundaries, integrator/splitting, step size, saved state, output
cadence, target set, hitting rule, censoring, random inputs, reference-force
query access and error certification. Model-output documentation alone fixes
only a small part of this contract.

Three public article HTML snapshots were cached privately. No source code,
model/checkpoint, raw trajectory, notebook, archive payload, numerical or
symbolic scientific computation, simulation, GPU/SSH, outreach or publication
was used. Source benchmarks were not independently reproduced. Prior Paper D
results and authorizations remain outside this evidence chain.

## Next decisive update

Do not commission another generic underdamped, KL-loss, path-reweighting or
integrator-support preflight in this family. The tool-level opening is closed
by direct parents. The deeper mechanism fork may re-enter only with a named,
matched primary disagreement or a theorem removing the recorded attribution
blocker, together with the same physical response and valid intervention.

The next useful source check is at the physical-mechanism level: use the
velocity-correlation spectrum and its low-frequency diffusion limit in the
Bigi liquid-water study, and inspect whether an independent primary model
makes a conflicting prediction under the same force, bath, preparation and
conditioning. Different materials,
thermostats, static marginals or capped/uncapped times do not qualify. If no
matched comparison exists, record absence of a qualified trigger and move
away from this method-only branch; do not harvest relabelled candidates.
