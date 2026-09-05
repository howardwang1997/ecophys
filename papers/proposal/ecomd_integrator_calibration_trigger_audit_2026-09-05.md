# EcoMD integrator and calibration trigger audit

**Date:** 2026-09-05  
**Stage:** bounded D-3 re-entry-trigger audit; no new discovery cycle  
**Archetypes screened:** `simulator_method`, `measurement_method`  
**Decision:** three `not_trigger`, one `partial_capability`, zero qualified triggers  
**Outcome, implementation, SSH and GPU access:** none

## Decision first

None of the four strongest repository-derived formulations justifies an ICLR topic or an experiment.

1. EcoMD's fixed fast/slow update mask is an instance of coordinate/subset Langevin splitting.
   Fixed compositions of exact kernels sharing one invariant law preserve that law; scan order can
   alter mixing and Euler bias, but both are established subjects.
2. Current probabilistic neural-network verifiers bound outputs of a fixed finite network under a
   random-input law. They do not preserve the quantifier order needed for a global certificate of
   `sup_theta E_noise[statistic]` for a recurrent stochastic simulator.
3. Per-rollout squared error on a random statistic contains an exact variance-collapse term, and an
   independent two-rollout cross product removes it. The correction is a linear-kernel U-statistic,
   while kernel-score calibration and proper probabilistic trajectory scoring already occupy the
   general method.
4. The 2026 score-based effective-Langevin papers are a genuine new capability but not a re-entry
   trigger. They add short- or finite-lag transition information, identify only mean mobility or a
   projected-generator equivalence class in general, and provide neither the stationary-sample-only
   estimator nor the externally anchored market actuator required by the closed solenoidal route.

The code audit also found one material interpretation defect: the current quadratic
`DissipationPotential` vanishes as physical friction under time-step refinement, while the entropy
module labels `F_diss dot v / T` as positive entropy generation even though medium entropy from a
friction force has the opposite force-power sign and total stochastic entropy requires a path-law
definition. This quarantines the old thermodynamic interpretation; it is not a paper contribution.

No machine card, experiment plan or compute authorization is created. The A800 and both V100s stay
idle for these formulations.

## 1. Scope and stopping rule

This audit tests four proposed exogenous triggers against existing terminal routes. It is not a
synonym-generating topic cycle. Each screen stops after an exact reduction or a minimal primary-work
collision. Repository and source semantics were inspected, but no model, evaluator, notebook,
dataset, stored outcome or remote host was executed or opened.

The relevant existing terminal routes are:

- `adaptive_scheduler_information_filtration_response` and `generic_simulator_audit_v4a`;
- `stylized_fact_attainable_set_certificate`;
- `tail_functional_differentiable_simulator_calibration`; and
- `multi_stationary_drift_tomography_v11`, `solenoidal_excitation_gap_v12` and
  `observation_quotient_response`.

No new route-graph nodes are added because every formulation below reduces exactly to one of those
registered nodes. The four proposed triggers are recorded append-only in the trigger ledger.

## 2. Fixed multi-timescale Langevin schedule

### Question contract

**Market-native object.** The stationary and transient law of fixed slow and fast agent populations
under EcoMD's physical update clock.

**Rivals.** Under H1, heterogeneous update frequency creates a distinct stationary market mechanism.
Under H2, a fixed state-independent scan changes computational mixing and discretization error but
does not create a new exact invariant law; only an endogenous clock can change the scientific
process, and then its market semantics must be observed independently.

**Cheapest discriminating result.** Let `K_i` be the exact transition kernel updating coordinate or
agent subset `i`, with `pi K_i = pi`. Then for any fixed scan `i_1,...,i_m`,

\[
  \pi K_{i_1}\cdots K_{i_m}=\pi.
\]

A counterexample with exact common-target kernels would support H1. The identity supports H2 and is
valuable as a null because it prevents ordinary scan order from being misread as a new equilibrium
mechanism.

### Repository semantics

The model builds a fixed `update_mask`: fast identities update every step, while every
`timescale_slow_freq` step updates everybody. All agents still enter the force calculation. The
integrator first computes a full Euler-Maruyama proposal and then restores masked coordinates to
their old values. Consequently:

- it is a deterministic systematic subset scan, not a learned market event clock;
- an exact coordinate kernel would preserve a common target under composition;
- the implemented Euler proposal can have ordinary step-size and splitting bias; and
- making the scan depend on state would define a different time-changed process and would require a
  stationary-measure correction if a target law were claimed.

This distinction is already central to [Random Coordinate Langevin Monte
Carlo](https://proceedings.mlr.press/v134/ding21a.html), [scan-order theory for Gibbs
sampling](https://arxiv.org/abs/1606.03432), and [state-dependent time changes of Markov
processes](https://arxiv.org/abs/2501.15155). EcoMD adds neither a theorem false for those parents nor
an independently observed market clock.

**Decision:** `not_trigger`. Retain fixed-scan versus endogenous-clock semantics as QA only.

## 3. Probabilistically verified attainable sets

### Question contract

**Market-native object.** Whether a target vector of market path summaries is globally attainable
by any parameter in a declared EcoMD class, rather than merely missed by a local optimizer.

**Rivals.** H1 says recent probabilistic neural verification makes the old global certificate
computable. H2 says those methods answer a fixed-network random-input question, whereas EcoMD needs
a nested parameter supremum, stochastic expectation and recurrent path functional.

**Cheapest discriminating result.** For direction `u`, the needed support value is

\[
 h(u)=\sup_{\theta\in\Theta}\mathbb E_{\xi}
       [u^\top S(F_\theta(\xi))].
\]

A sound computable upper bound on this exact object would remove a recorded blocker. A bound on a
different quantifier order would be a useful negative result because it prevents a formal-looking
but invalid nonattainability claim.

### Quantifier audit

[Kofnov et al.](https://proceedings.mlr.press/v267/kofnov25a.html) give convergent CDF bounds for the
output of a **fixed** feedforward or convolutional network under a random-input distribution.
[Boetius et al.](https://proceedings.mlr.press/v267/boetius25a.html) give sound branch-and-bound
probability bounds, with a conditional completeness result, for the same fixed-network class.

Neither result supplies `h(u)` above. Treating `(theta, xi)` as one bounded verifier input produces a
worst-case support bound of the form

\[
 \sup_{\theta,\xi} u^\top S(F_\theta(\xi)),
\]

which is sound but discards the expectation and is generally far too loose. Assigning a probability
law to `theta` instead computes a mixture average, not a supremum over parameters. A nested verifier
might be constructed in principle, but the cited algorithms provide no tractable recurrent-horizon
bound, dependent-noise expectation certificate, finite-simulation coverage or matching hardness
boundary for this object. Unrolling EcoMD also makes dimension grow with agents times horizon.

**Decision:** `not_trigger`. The new verification results strengthen adjacent tools but remove none
of `stylized_fact_attainable_set_certificate`'s named blockers.

## 4. Finite-rollout statistic loss and variance collapse

### Question contract

**Market-native object.** Calibration of the population mean of a random long-rollout market
statistic, without artificially suppressing the simulator's path-to-path variability.

**Rivals.** H1 says per-rollout mean squared error estimates squared error of the population mean.
H2 says it additionally penalizes rollout variance and therefore selects an incorrectly
under-dispersed simulator.

**Cheapest discriminating result.** Let `Z_theta` be a vector of rollout statistics and `s` the
target. Then

\[
 \mathbb E\|Z_\theta-s\|^2
 =\|\mathbb E Z_\theta-s\|^2+\operatorname{tr}\operatorname{Cov}(Z_\theta).
\]

For conditionally independent rollouts `Z_theta` and `Z'_theta`,

\[
 \mathbb E[(Z_\theta-s)^\top(Z'_\theta-s)]
 =\|\mathbb E Z_\theta-s\|^2.
\]

Thus H2 is exact. The cross product is an unbiased loss for a **mean functional**. It can be negative
for a finite pair and is not a strictly proper score for the complete path law. Likewise, an L1
per-rollout target selects a median of the statistic distribution rather than its mean.

### Novelty audit

The correction is the U-statistic structure of a linear-kernel MMD. [Su and
Klabjan](https://proceedings.mlr.press/v258/su25a.html) already calibrate differentiable inexact
stochastic simulators by kernel-score minimization and derive U-statistic gradients and uncertainty
under misspecification. More directly, [Brolly 2026](https://arxiv.org/abs/2603.28671) proves
variance suppression from deterministic trajectory losses for chaotic closures and replaces them
with strictly proper probabilistic trajectory scores, with a stochastic fluid-closure experiment.

An EcoMD demonstration would therefore be a domain instance of two direct parents. The identity is
important for repairing future calibration objectives, but it does not supply an ICLR contribution.

**Decision:** `not_trigger`. Do not advertise the independent-replicate correction as a new loss.

## 5. Score-based effective Langevin dynamics

### Question contract

**Market-native object.** The probability current or drift of a resolved stationary market state,
and its response to an externally defined market action.

**Rivals.** H1 says a learned stationary score plus observed correlations now identifies the missing
solenoidal drift and reopens the closed route. H2 says the method introduces transition information,
identifies only selected observable sectors in general, and still cannot infer an unseen
intervention response from a passive state projection.

**Cheapest discriminating result.** The trigger would have to recover the original current object
from the original stationary-sample contract, or supply a feasible market actuator with a
control-dependent identification theorem. A positive result would remove a named route blocker. A
null result still maps the new papers correctly and prevents an overlooked direct parent from being
presented as EcoMD novelty.

### What the 2026 papers actually establish

[Giorgini, *Physical Review E* 2026](https://doi.org/10.1103/6qpv-lqmt) writes a stationary diffusion
drift using the steady-state score and a mobility whose symmetric part controls diffusion and whose
antisymmetric part carries circulation. In the implemented closure, mobility is constant and its
mean components are inferred from the right derivative of the short-lag coordinate correlation:

\[
 \langle D\rangle=-\dot C^{S}(0^+),\qquad
 \langle R\rangle=-\dot C^{A}(0^+).
\]

The paper explicitly states that this constant closure does not reconstruct state-dependent
probability currents, general finite-lag correlations, higher-order multitime observables or
pathwise recovery. Its input is a stationary **time series**, not independent stationary samples.

The follow-up [Conditional Score-Based Modeling of Effective Langevin
Dynamics](https://arxiv.org/abs/2604.23952) uses conditional transition scores and stationary lagged
pairs to fit state-dependent mobility against chosen observables and lags. This is a material method
advance. It also gives the decisive negative result for re-entry: in general the constraints do not
identify a unique pointwise mobility. They identify its projected generator action on a selected
Koopman-evolved observable sector, or an observable-dependent equivalence class. The paper further
lists non-Markovian projected dynamics, high-dimensional score estimation and missing external
parameter/forcing/control dependence as limitations.

### Comparison with the closed route

`solenoidal_excitation_gap_v12` asks what can be identified from several stationary densities and
records a divergence-free ambiguity plus an unstable fold boundary. Adding short- and finite-lag
transition pairs changes the observation operator; it does not solve the stationary-density-only
inverse problem. Accepting any mobility in an observable equivalence class also does not identify an
externally anchored response, as the registered observation-quotient counterexample shows.

The obvious method extension—conditional-score state-dependent mobility—is now itself direct prior
art. The remaining external-control extension is named future work in that paper but has no market
actuator, assignment, sufficient pre-state, response truth or independent replication here.

**Decision:** `partial_capability`, with zero removed blockers and
`candidate_harvest_authorized: false`. This is the closest item in the audit, but it is not a
qualified trigger.

## 6. Additional repository semantics that do not form topics

### 6.1 Partial versus total derivative of a contextual potential

If a context is itself computed from state, autodiff through `V(s,C(s))` returns

\[
 \frac{dV}{ds}=\partial_sV+J_C(s)^\top\partial_CV.
\]

A physical force declared at fixed market context is only `-partial_s V`. The current helper clones
the force-state node when `isolate_state=True`, correctly holding shared-history context fixed; the
legacy option reproduces the total derivative. This is an elementary computational-graph semantic
guard, not a research method.

There is a second, more important distinction. Once the context is closed around the state, the
effective force `F_i(s)=-partial_{s_i}V(s,C(s))` need not itself be conservative. Its curl is

\[
 \partial_jF_i-\partial_iF_j
 =-\sum_a\left[V_{s_i c_a}\partial_jC_a
                -V_{s_j c_a}\partial_iC_a\right],
\]

which is generically nonzero. If `C` depends on history, the instantaneous state `s` is not even a
closed Markov state. The conditional potential remains a valid parameterization at frozen context,
but its changing context supplies feedback/controller work that cannot be folded into a conservative
system energy. [Munakata and Rosinberg](https://doi.org/10.1103/PhysRevLett.112.180601) already derive
the required modification of time reversal and trajectory entropy for continuous non-Markovian
feedback. This further quarantines an autonomous conservative-system interpretation; it does not
leave an unoccupied method claim.

### 6.2 State-dependent temperature, friction and multiplicative noise

Regime heads and the per-agent mixture router make `T/gamma` state- or history-dependent, while the
stochastic-volatility hook further multiplies the noise. If the model claimed a fixed Gibbs target,
a state-dependent diffusion would require the appropriate divergence/noise-induced drift and a
declared stochastic convention. The current update supplies neither. EcoMD also includes memory,
jumps, feedback and time-varying temperature, however, so no unique Gibbs target has been declared;
one cannot call a particular correction physically correct without first freezing the intended
nonequilibrium path law. The general issue is standard multiplicative-noise and Langevin theory.

### 6.3 Dissipation scaling and entropy sign

The repository defines

\[
 \Psi_h(s_n,s_{n-1})=\lambda\|s_n-s_{n-1}\|^2,
 \qquad F^{\rm diss}_n=-2\lambda(s_n-s_{n-1}),
\]

then multiplies this force by `h/gamma` in the next Euler update. For a smooth path the per-step
effect is `O(h^2)`. For an overdamped stochastic path the force is `O_p(sqrt(h))`, but over a fixed
horizon and constant coefficients its cumulative contribution is proportional to
`h sum_n (s_n-s_{n-1}) = h(s_T-s_0)`, and still vanishes. A discrete Rayleigh potential for velocity
must instead include inverse-step scaling, with the exact factor depending on the chosen variational
discretization.

The entropy module computes `F_diss dot v / T` and documents it as positive generation. For a
conventional friction force acting on the system, `F_diss dot v` is nonpositive and the medium-heat
sign is the negative of that power. Here the force is also lagged, so its dot product with the new
velocity need not have either sign. Total stochastic entropy production additionally contains the
system/path-probability contribution. [VONNs](https://doi.org/10.1016/j.jmps.2022.104856) and
[standard stochastic thermodynamics](https://doi.org/10.1088/0034-4885/75/12/126001) already occupy
the structural method space.

Therefore every old claim that this variable measures physical market entropy production is
quarantined unless the dynamics, discretization, sign convention and path measure are rederived. A
code fix would be necessary QA but would not be a new paper.

### 6.4 Projection versus resolution

Requiring a fine-grid constraint projector and a coarse restriction to commute is useful:
`R P_h = P_H R`. For the repository's uniform block-average restriction and global mean-removal
projector, the identity already holds because restriction preserves the mean. The general idea is
compatible discretization/conservative operator learning and would also overlap the active
constraint-attribution manuscript. No irreducible child remains.

### 6.5 Energy--friction--temperature gauge

Ignoring only fixed parameters that are deliberately held outside the model, the overdamped update
has an exact positive scale symmetry. If every force-generating potential, including the
dissipation coefficient when enabled, is scaled by `c>0`, then

\[
  (V,\Psi,\gamma,T)\mapsto(cV,c\Psi,c\gamma,cT)
\]

leaves both `h(F_cons+F_diss)/gamma` and `2Th/gamma` unchanged. With the same random tape it
therefore leaves the latent path and every downstream price output unchanged. Additive constants in
`V` are another exact gauge. The transition law can identify drift and diffusion, but it cannot
assign an absolute energy, friction or temperature unit without an external normalization.

EcoMD's class defaults and several early architecture configs allow both `gamma` and `temperature`
to learn while the potential scale is also learned; the current M0 reference freezes them. Learned
historical values must not be interpreted as separately measured market friction or temperature.
Quotienting or fixing this elementary units gauge is necessary calibration hygiene, but a generic
gauge-aware training claim would reduce to standard identifiability and energy-unit normalization.
It does not create a new trigger.

## 7. Gate summary

| Formulation | Scientific result | Novel residual | Truth / market bridge | Decision |
|---|---|---|---|---|
| Fixed multi-timescale scan | Exact invariant-law null; scan can change mixing/bias | None beyond coordinate/split/time-change parents | No observed endogenous clock | `not_trigger` |
| Verified attainable set | Fixed-network output bounds are real | Quantifier-preserving recurrent expectation certificate absent | No finite-simulation coverage | `not_trigger` |
| Two-rollout statistic loss | Exact variance decomposition and unbiased mean correction | Kernel/U-statistic and proper-score parents own it | No market-native new estimand | `not_trigger` |
| Score effective Langevin | Useful constant and conditional-score constructions | Direct papers own the method; pointwise current remains nonidentified | No actuator or external response truth | `partial_capability` |
| Dissipation / entropy semantics | Material interpretation defect | Mature variational and stochastic-thermodynamic theory | Old physical claim is invalid, not newly supported | QA only |
| Endogenous contextual potential | Frozen-context gradient has generically nonzero closed-loop curl | Feedback Langevin thermodynamics is mature | Controller/action truth is absent | QA only |
| `V`--`gamma`--`T` scale gauge | Exact path-law nonidentifiability | Elementary units/parameter gauge | No external energy or friction anchor | QA only |

Post-evidence diagnostic ICLR survival for the four paper formulations is below 3% each. This is not
a prospective forecast or a closure threshold; the exact reductions, quantifier mismatch and direct
primary collisions are the closure evidence.

## 8. Exact re-entry boundary

Re-audit this neighborhood only if at least one concrete object exists:

1. an independently observed endogenous market clock with a theorem false for coordinate Langevin,
   systematic scan and time-changed Markov parents;
2. a sound computable upper certificate for `sup_theta E_noise` of a dependent recurrent path
   statistic, including horizon complexity, finite-simulation coverage and a matching impossibility
   boundary;
3. a strictly proper dependent-path score for a market-native functional with an estimator or
   theorem not reducible to kernel/energy scores and U-statistics; or
4. a stationary-sample-only current estimator or feasible externally anchored market actuator on
   the original solenoidal-drift estimand, with control-dependent identification beyond projected
   generator equivalence, two independent truth systems and an untouched market response contract.

Any future survivor still needs a topic card and a new current machine decision before EcoMD
implementation, outcome access, SSH or GPU use.
