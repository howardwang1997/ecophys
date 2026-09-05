# EcoMD metaorder, waveform-composition, and decision-compatibility trigger audit

**Date:** 2026-09-05  
**Scope:** three post-closure primary-work screens  
**Archetypes:** `measurement_method`, `simulator_method`, `simulator_method`  
**Decisions:** three `not_trigger`  
**Candidate harvesting:** not authorized  
**Outcome access, implementation, simulation, SSH, and GPU work:** not authorized

## 1. Why these sources were screened

Three very recent works appear to address recurrent EcoMD bottlenecks:

1. [Goliath and Gebbie (2026)](https://arxiv.org/abs/2608.30999) reconstruct synthetic
   metaorders from anonymous public trades and explicitly distinguish compatibility from
   identification;
2. [Zerihun and Lee (2026)](https://arxiv.org/abs/2609.03358) replace timestep marching by a
   whole-trajectory fixed point assembled from learned subsystem operators;
3. [Hashimoto et al. (2026)](https://arxiv.org/abs/2608.20842) replace global scenario realism by
   a hedger- and task-conditioned compatibility discrepancy.

At headline level these suggest, respectively, a route around missing parent-order labels, a new
computational form for differentiable EcoMD, and a task-native validation or training objective.
The relevant question is stricter: does any source remove a recorded blocker and leave an
irreducible ICLR-level theorem or method? The answer is no for all three.

## 2. Screen A: anonymous metaorder reconstruction

### 2.1 Exact question

The market-native object is the latent partition of public child trades into trader-specific parent
metaorders. The rival explanations concern the same anonymous tape and the same reconstructed
partition:

- **H1 -- aggregate constraints identify the partition:** matching square-root impact, execution
  shape, decay and the Lillo--Mike--Farmer relation recovers economically meaningful parent orders;
- **H0 -- target-conditioned compatibility:** many incompatible partitions of the same tape can
  match selected aggregate targets, and choosing a reconstruction against one target imports that
  target into the answer.

The cheapest discriminating observation is whether parameters selected without the LMF relation
recover it on an independent target. A positive answer would provide genuine out-of-target
evidence for latent order splitting. A null answer still matters because it prevents a synthetic
label from being treated as observed trader identity.

### 2.2 What the new study establishes

Goliath and Gebbie use JSE Level-1 trade and quote data for 239 stocks over 2023--2025, assign every
trade to one of (N) synthetic traders using homogeneous or power-law participation weights, and
group same-sign runs within each synthetic trader. They grid-search (N) and the participation
exponent. Configurations selected on aggregate impact stylized facts reproduce several intended
targets but yield a poor LMF relation. Configurations selected to minimize LMF discrepancy recover
that relation by construction. The authors correctly conclude that this is compatibility within
the reconstruction class, not independent identification or validation.

This is a scientifically useful negative result, and is more careful than treating the synthetic
labels as ground truth. It does not remove the missing-parent-label blocker. The underlying BMLL
rows are also not redistributed, so the exact empirical panel is not a new open truth asset for the
project.

The immediate parents already delimit the problem. [Maitrier, Loeper, and Bouchaud
(2025)](https://arxiv.org/abs/2503.18199) introduce the public-tape synthetic-metaorder
construction and validate it through aggregate impact shapes. [Naviglio et al.
(2025)](https://arxiv.org/abs/2501.17096) show why public-data metaorder impact estimates depend on
model, aggregation, intervention and horizon choices. The new paper sharpens rather than removes
that ambiguity.

### 2.3 Data-processing and non-identification floor

Let (X) be the public trade tape, (Z) the unobserved true parent partition, (U) independent
algorithmic randomness, and

\[
 \widetilde Z=A_\eta(X,U)
\]

the synthetic reconstruction selected by hyperparameter (eta). Conditional on (X), the
algorithmic label contains no information about (Z):

\[
 I(Z;\widetilde Z\mid X)=0,
 \qquad I(Z;\widetilde Z)\le I(Z;X).
\]

More directly, if two latent worlds have the same law for (X) and different parent partitions or
parent-level target (T(Z)), then every statistic of ((X,U)), including a cross-fitted synthetic
partition, has the same observable law in both worlds. Randomization cannot identify which world
generated the tape.

Holding out stocks, days or calibration targets can honestly measure predictive transfer of the
algorithm. It cannot turn a latent partition into truth. Set-valued or Bayesian reconstructions can
state assumptions and uncertainty, but return to partial identification, latent record linkage and
model criticism. The generic theorem is the data-processing principle, not a new EcoMD method.

### 2.4 Decision

`not_trigger`. The source supplies a reusable warning against target-selected validation, not a
truth asset or irreducible reconstruction theorem. Parent-order identity, beneficial-owner units,
complete attempts, and an untouched trader-labelled replication remain absent.

## 3. Screen B: whole-trajectory self-consistency

### 3.1 Exact question

The object is the physical trajectory produced by mutually coupled learned subsystem operators.
The rival explanations are:

- **H1 -- composability is separately controllable:** local operator accuracy plus a measured
  coupling Jacobian is enough to train and certify a cheap global fixed-point simulator;
- **H0 -- self-consistent model error:** the learned operators can agree to numerical precision
  while their common trajectory remains physically wrong, with coupling coverage and resolvent
  conditioning amplifying errors invisible to isolated MSE.

A discriminating result would bind true coupled-trajectory or path-observable error using quantities
available before the exact coupled solve, under a declared distribution shift and coupling family.
Both signs matter: a positive result would make modular learned simulation operational; a null
result separates solver convergence from physical accuracy.

### 3.2 What Time Without Timesteps owns

Time Without Timesteps (TWT) learns a full-trajectory operator for each subsystem and assembles the
coupled system through

\[
 X=F(X).
\]

It uses Picard or Jacobian-free Newton--Krylov solves and a GMRES implicit adjoint. In the reported
small smooth systems, coupled trajectories represented over 1,500 timesteps are solved in roughly
4--10 Newton iterations, and implicit differentiation uses memory independent of solver depth. The
paper also cleanly reports that isolated accuracy and composability can move in opposite directions.

The negative boundary is equally explicit:

- a self-consistency residual near (10^{-12}) can coexist with substantial physical error;
- the exact-operator waveform-relaxation solve is the relevant formulation floor;
- a random-direction Jacobian penalty controls a Frobenius-like average rather than the dominant
  spectral direction and worsens composition;
- coupling-induced training-distribution coverage is the dominant practical failure;
- scale, wall-clock speed, PDEs, chaos, discontinuities, event-driven systems, windowing,
  preconditioning and spectral-radius training are not established.

Thus TWT itself owns the waveform-neural-operator formulation, the spectral composability
diagnostic, the JFNK solve and the implicit gradient. Reimplementing it in EcoMD would be an
application.

### 3.3 Exact linear error relation

The certification obstruction is visible even in a linear subsystem. Let the true operator be
(S_\star(u)=Au+b), let the learned operator be (S(u)=(A+E)u+b), and couple through (u=WX).
When both fixed points exist,

\[
 X_\star=AWX_\star+b,
 \qquad
 \widehat X=(A+E)W\widehat X+b,
\]

so

\[
 \widehat X-X_\star
 =\bigl[I-(A+E)W\bigr]^{-1}EWX_\star.
\]

Small isolated error (E) does not control the coupled error without both relevant-direction
coverage and a bound on the resolvent. Spectral radius controls asymptotic Picard convergence under
the appropriate local assumptions; it does not by itself control nonnormal transient amplification,
the conditioning of (I-J_F), or distance to the true operator. Newton additionally needs the
ordinary local smoothness and initialization conditions; nonsingularity at a solution is not a
global convergence certificate.

### 3.4 Direct-parent collision

The obvious repairs are already occupied:

- classical waveform relaxation is the exact numerical parent;
- [LegONet](https://arxiv.org/abs/2603.07882),
  [CompNO](https://arxiv.org/abs/2601.07384), and
  [compositional generation for coupled PDEs](https://arxiv.org/abs/2510.20141) already learn and
  recombine subsystem or mechanism operators;
- learner-induced input collection is a fixed-point analogue of on-policy dataset aggregation;
  [DAgger](https://arxiv.org/abs/1011.0686) is the generic covariate-shift parent;
- [Zou, Lie, and Marzouk (2026)](https://arxiv.org/abs/2603.20467) already train SDE surrogates
  against information-theoretic error bounds for path-space observables;
- [Pervez and Locatello (2026)](https://arxiv.org/abs/2605.08856) identify nonnormal,
  noncommuting Jacobians as a source of transient rollout amplification, give a propagator bound,
  and train with JVP-based commutativity and normality regularizers.

An equilibrium data-aggregation loop could be useful engineering, but without a new oracle model,
sample-complexity separation or lower bound it is DAgger over coupling waveforms. Direct
spectral-radius, pseudospectral or nonnormal regularization is no longer an unoccupied method claim.

### 3.5 EcoMD boundary and decision

EcoMD adds stochastic hard events, changing agent state and discontinuous execution semantics—the
very regimes TWT does not cover. An EcoMD-generated trajectory can test surrogate fidelity to
EcoMD, but cannot certify EcoMD against an external market. Historical data do not provide the
same-prestate, same-action alternative trajectory needed for a coupled counterfactual error label.

`not_trigger`. TWT is an important new computational capability, but it supplies neither an
inference-observable true-error certificate nor a market truth asset and therefore does not satisfy
the recurrent-depth route's re-entry condition.

## 4. Screen C: task-conditioned scenario compatibility

### 4.1 Exact question

The object is the risk landscape induced by a scenario generator over a declared class of hedging
strategies. Rival explanations are:

- **H1 -- stylized-fact realism is sufficient:** generators close on conventional return metrics
  are interchangeable for downstream hedging;
- **H0 -- loss-class compatibility governs transfer:** generators with similar realism can rank
  differently because hedger architecture, payoff, risk functional and frictions select different
  path features.

Hashimoto et al. define

\[
 \Gamma(P,Q;\mathcal H)
 =\sup_{h\in\mathcal H}|\rho_P(h)-\rho_Q(h)|
\]

and bound true excess risk by synthetic-distribution learning error plus (2\Gamma). For expected
loss, (Gamma) is exactly an integral probability metric over the hedger-induced loss class. They
also construct distributions that match a finite-dimensional realism feature class while differing
on a hedging loss. Their Nikkei experiment shows generator rankings changing with option,
transaction cost and hedger class.

This correctly rejects a global realism scalar. The excess-risk inequality is the standard
telescoping/domain-adaptation argument, and the finite-feature counterexample is a standard linear
separation. Most importantly, the paper states that compatibility is difficult to observe and uses
indirect proxies; it does not estimate or certify (Gamma) for an unknown deployment law.

### 4.2 Why the obvious method is occupied

With independent real paths (omega_i\sim P) and synthetic paths
(widetilde\omega_j\sim Q), the natural estimator is the empirical loss-class IPM

\[
 \widehat\Gamma
 =\sup_{h\in\mathcal H}
 \left|
  \frac1n\sum_i C(\omega_i,h)
  -\frac1m\sum_j C(\widetilde\omega_j,h)
 \right|.
\]

Uniform convergence, sample splitting and complexity control are standard empirical-process or GAN
ingredients. Optimizing (Q) against this objective is task-induced adversarial distribution
matching; optimizing the resulting downstream decision is decision-focused generative learning.
The direct parents are unusually close:

- [Gen-DFL, ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/5c25c15b5b2fd386ab188a918e54c7d5-Abstract-Conference.html)
  jointly trains a conditional generator and risk-sensitive downstream optimizer and gives a
  proxy-distribution/Wasserstein regret bound;
- [Diff2SP](https://arxiv.org/abs/2606.05649) trains a diffusion scenario generator with an
  optimization loss in addition to statistical losses;
- [decision-focused scenario generation and selection](https://arxiv.org/abs/2607.05830) applies
  the same principle across VAE, GAN and diffusion generators with differentiable scenario
  selection;
- [Robust Hedging GANs](https://arxiv.org/abs/2307.02310),
  [Adversarial Deep Hedging](https://arxiv.org/abs/2307.13217), and
  [distributional adversarial training for deep hedging](https://arxiv.org/abs/2508.14757)
  already couple market generators, hedgers and distributional robustness.

Consequently, “train EcoMD for downstream hedging rather than stylized facts” is a direct domain
composition, not a new learning principle.

### 4.3 The interactive-market obstruction

The paper assumes a fixed exogenous path law (P), independent of the hedger. This is appropriate
for a price-taking historical-path evaluation. EcoMD's scientific purpose is stronger: actions can
change order flow, liquidity and prices. The relevant object would instead be

\[
 \Gamma_{\mathrm{int}}(P,Q;\mathcal H)
 =\sup_{h\in\mathcal H}
   |\rho_{P_h}(h)-\rho_{Q_h}(h)|,
\]

where (P_h) and (Q_h) are policy-induced market laws. A passive tape generally does not reveal
(C(\omega,h)) for an action (h) that would have changed (omega). Thus the easy empirical IPM
is valid only under price-taking/no-impact assumptions; the interactive quantity needs repeated
assigned actions, support or a defensible causal model. This is exactly the closed
policy-aware/prospective-simulator-validity blocker, not a newly removed one.

### 4.4 Decision

`not_trigger`. The source gives strong motivation and an honest negative evaluation principle, but
the price-taking estimator and generator-training variants have direct ICLR/optimization/hedging
parents. The interactive EcoMD version remains counterfactually unidentified and has no independent
same-action truth system.

## 5. Joint verdict

| screen | useful new information | fatal gate | decision |
|---|---|---|---|
| anonymous metaorders | target-independent calibration fails to recover LMF; compatibility is not identification | synthetic labels are a randomized function of the anonymous tape; no parent truth | `not_trigger` |
| whole-trajectory composition | sequential depth and implicit memory improve; accuracy and composability separate | learned fixed-point residual is not physical error; all obvious composition/coverage/stability repairs have direct parents | `not_trigger` |
| decision compatibility | global realism can disagree with downstream ranking | price-taking method is occupied; interactive loss requires unavailable counterfactual response | `not_trigger` |

No source removes a recorded hard blocker. No topic card or machine card is created. The current
constraint-attribution decision cannot authorize work on any of these routes, so the A800 and both
V100 workers remain closed for this exploration.

## 6. Exact re-entry conditions

Candidate harvesting remains forbidden unless one of the following is first recorded as a
qualified trigger:

1. **Metaorder branch:** an authoritative parent/child linkage or a theorem returning sharp latent
   functionals from anonymous tapes under testable restrictions, with a matching impossibility
   boundary and an untouched trader-labelled replication. More stylized-fact targets or cross-fit
   partitions are not sufficient.
2. **Waveform branch:** a prospectively frozen theorem connecting an inference-observable
   composability statistic to true trajectory or path-observable error under dependent stochastic
   hard events, with a matching lower bound beyond waveform relaxation, DAgger, goal-oriented SDE
   learning and nonnormal-rollout control. A larger TWT benchmark or EcoMD backend is not sufficient.
3. **Compatibility branch:** either a learning/certification result not representable as an
   empirical loss-class IPM, Gen-DFL, decision-focused scenario generation or distributional robust
   hedging, or a lawful interactive-market panel exposing repeated same-prestate actions and
   untouched policy-induced response truth. Passive price paths alone are not sufficient.

## 7. Operational disposition

- No historical or simulated outcome was opened.
- No external repository or model was executed.
- No EcoMD implementation or data pipeline was run.
- No SSH connection was made.
- The A800 at `100.113.230.38` and the V100 workers at `100.80.236.112` and `100.123.220.57`
  remain idle for these routes.
