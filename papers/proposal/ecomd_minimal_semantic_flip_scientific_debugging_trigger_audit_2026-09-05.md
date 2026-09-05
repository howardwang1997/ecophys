# EcoMD minimal-semantic-flip scientific-debugging trigger audit

**Date:** 2026-09-05  
**Stage:** post-closure theorem and primary-work re-entry screen  
**Archetype:** `simulator_method`, with a `measurement_method` repair tested  
**Decision:** `not_trigger`  
**Candidate harvesting:** not authorized  
**Outcome access, implementation, simulation, SSH, and GPU status:** none

## 1. Decision first

The proposed escape was to use EcoMD's differentiability to find the smallest simulator assumption,
parameter, or rule change that reverses a declared scientific conclusion. This would be useful as an
internal audit tool. It is not currently a defensible ICLR topic.

There are two independent failures. First, “smallest semantic change” is not an intrinsic object.
A smooth reparameterization can reverse which of two conclusion-flipping models is closer, and a
behavior-preserving refinement of the edit grammar can change a one-edit cause into an arbitrary
number of edits. Second, after a cost and edit language are declared, the continuous problem is an
ordinary counterfactual/falsification optimization and the discrete problem is delta debugging,
validity-preserving input reduction, or satisfiability-based nearest-counterfactual search.
Differentiable simulation has already been used explicitly to predict and repair failure modes.

Information-geometric and set-valued repairs were also tested. A path-law divergence is coordinate
invariant only after choosing an observation map and a state--action visitation measure; it assigns
zero distance to off-support semantic changes and cannot distinguish hidden implementations with the
same observed law. A full-latent divergence instead changes under latent-state refinement. Reporting
all inclusion-minimal edits avoids a scalar metric but inherits the chosen grammar and is directly in
the delta-debugging/model-checking family.

The recent fragmented-market replication remains a valuable hard negative, but it supplies neither
a complete semantic language nor gold minimal causes. EcoMD cannot manufacture those labels. No
recorded blocker is removed and all three accelerator workers remain idle.

## 2. Frozen question contract

Let `K0` be a baseline market-simulator kernel and let

\[
q(K)=\mathbb E_K[Y\mid do(a_1)]-\mathbb E_K[Y\mid do(a_0)]
\]

be a declared scientific contrast, such as the welfare effect of fragmentation. Let
`C(K0)` be the simulator variants admitted by a semantic-edit language and let `c(K0,K)` be their
cost. The proposed explanation is

\[
K^*\in\arg\min_{K\in\mathcal C(K_0)}c(K_0,K)
\quad\text{subject to}\quad
\operatorname{sign}q(K)\ne\operatorname{sign}q(K_0).
\]

**Rival explanations.** Under H1, market event structure plus differentiability yields a new,
representation-invariant scientific-debugging primitive. Under H0, gradients only accelerate a
counterfactual or falsification search after the analyst has supplied the admissible edits and their
cost; the returned “cause” is therefore conditional on those choices and belongs to established
optimization, formal-methods, or software-debugging parents.

**Cheapest discriminator.** Require the identity and ordering of minimal causes to survive (i) a
smooth one-to-one change of continuous coordinates and (ii) behavior-preserving split/merge of edit
atoms. If this fails before any simulator run, an optimization benchmark cannot rescue the scientific
interpretation. A positive result would justify looking for a market-specific estimator theorem. A
null result is valuable because it prevents a visually compelling adversarial parameter trace from
being called an intrinsic mechanism explanation.

## 3. Exact coordinate counterexample

### Proposition 1: Euclidean nearest flips are not invariant to smooth reparameterization

Consider a one-dimensional simulator family with baseline `theta0=0` and a smooth contrast

\[
q(\theta)=(\theta+1/2)(\theta-1).
\]

Then `q(0)<0`, while both `theta_-=-1` and `theta_+=2` give positive contrasts. In the original
coordinate,

\[
|\theta_- - \theta_0|=1<2=|\theta_+-\theta_0|,
\]

so the negative-direction model is the nearer flip. Now use the smooth strictly increasing bijection

\[
\phi=g(\theta)=-\exp(-k\theta),\qquad k>\log 2.
\]

The three simulator kernels and their contrast values are unchanged. Nevertheless,

\[
|g(-1)-g(0)|=e^k-1
\quad\text{and}\quad
|g(2)-g(0)|=1-e^{-2k},
\]

so the positive-direction model is now nearer. Any gradient direction, robustness radius, or ranked
cause derived from a fixed Euclidean norm can therefore be changed without changing the simulator
family or scientific claim.

This is not repaired by standardizing each coordinate: the reference distribution, range, and
covariance are then additional analyst choices, and nonlinear reparameterizations still change the
ranking. A Riemannian metric transforms covariantly, but selecting that metric is precisely the
missing scientific cost contract.

### Proposition 2: edit-count minimality is not invariant to semantic atomization

Suppose one legal macro edit `E` changes a greedy trader's information and pricing rule and flips the
conclusion. In an equivalent language, replace `E` by a sequence of `m` mandatory micro-edits
`e1,...,em` whose joint denotation is exactly `E`; leave a competing one-atom edit `F` unchanged.
Both languages denote the same completed simulator kernels, yet Hamming or graph-edit cost changes
`cost(E)` from one to `m` and can reverse the minimal cause for arbitrary `m`.

Quotienting edits by behavioral equivalence would help only after equivalence is defined over the
complete state, action, clock, randomness, information, and observation contract. For general
stochastic programs, establishing that quotient is at least the simulator-conformance/bisimulation
problem already recorded in Cycle 8. The incomplete ODD or prose specification that motivated this
route does not provide it.

## 4. Why the natural repairs do not create a residual

### 4.1 Path-law or information-geometric cost

One may replace parameter distance by a divergence between path laws. This removes ordinary
coordinate dependence but not the scientific choice. A divergence over observed paths requires a
reference policy, intervention distribution, horizon, stopping rule, and observation map. A rule
that differs only in states never reached under that reference has zero observed divergence even if
the target intervention reaches those states and reverses `q`. If the divergence is computed on full
latent paths, behavior-preserving state splitting or hidden-label refinement can change it while all
market observables remain fixed.

Thus a path-law radius is a valid *declared robustness analysis*, not a canonical semantic distance.
Optimizing an expectation under a KL, Wasserstein, Fisher--Rao, or transition-kernel ball then meets
distributionally robust optimization, robust MDP, rare-event, and adversarial-falsification parents.

### 4.2 Inclusion-minimal or Pareto explanations

Returning every inclusion-minimal flip avoids pretending that different rule types share one unit.
It does not remove the atomization problem: minimal sets are defined relative to a grammar. Once a
valid generator or formal formula supplies the grammar, delta debugging, generator-trace reduction,
SAT/SMT nearest-counterfactual search, and complete model-class enumeration are direct parents.

### 4.3 Causal or economic intervention cost

A real action cost would be the strongest repair, but simulator-specification edits such as a
different feed, queue tie, random-number binding, observation clock, or agent taxonomy are not
actions available to one market actor. They have no common economic unit. Calling them causal
interventions does not establish their legality, cost, or real response. ACIF also shows that an
intervention-indexed discriminator needs newly executed interventional data to adjudicate models;
simulator disagreement alone is not truth.

## 5. Direct collision map

| Primary work | Occupied object | Consequence |
|---|---|---|
| [Dawson and Fan, CoRL 2023](https://proceedings.mlr.press/v229/dawson23a.html) | Approximate-Bayesian failure-mode sampling and automatic design repair using differentiable simulation, with gradient-free comparisons | The broad “differentiate a simulator to find and repair failures” contribution is directly occupied. |
| [VERIFAI](https://arxiv.org/abs/1902.04245) | Formal-model-guided simulation, temporal-logic falsification, parameter synthesis, counterexample analysis, debugging and dataset augmentation | Searching simulator inputs/parameters for claim violations is established even without differentiability. |
| [MACE](https://proceedings.mlr.press/v108/karimi20a.html) | Provably nearest counterfactuals through repeated satisfiability queries, agnostic to model, data type and declared distance | Once a semantic grammar and cost are formal, exact nearest flips are not a new problem statement. |
| [Zeller and Hildebrandt 2002](https://doi.org/10.1109/32.988498) | Delta debugging that minimizes failure-inducing inputs and isolates passing/failing differences | Discrete minimal conclusion-flipping subsets reduce to a mature debugging primitive. |
| [GReduce](https://arxiv.org/abs/2402.04623) | Validity-preserving delta debugging by reducing generator traces across structured benchmarks | Requiring edits to remain valid under a semantic generator is already an explicit repair. |
| [Dominguez-Olmedo et al., ICML 2023](https://proceedings.mlr.press/v202/dominguez-olmedo23a.html) | Causally grounded counterfactuals on SCM-induced Riemannian manifolds | A geometry-aware counterfactual is available, but its metric and conformal factors remain modeling choices rather than intrinsic facts. |
| [Antonova et al., CoRL 2022](https://proceedings.mlr.press/v205/antonova23a.html) | Global search that combines differentiable-simulation gradients with semi-local Bayesian-optimization leaps on rugged landscapes | A hybrid gradient/global optimizer is a baseline, not a market-specific novelty claim. |

The repository adds three closer collisions. The Cycle 8 trilemma already separates conformance
failure, numerical propagation error, and true mechanism differences. The action-counterfactual
audit records ACIF and the need for external assigned response truth. The fragmentation-replication
audit shows that sampled implementations cannot certify all legal completions without a sound
grammar or outer bound. Minimal-flip search does not invalidate any of those reductions.

## 6. EcoMD and benchmark contract

EcoMD's differentiability covers parameters of its chosen aggregate Langevin-style dynamics. It
does not expose a machine-readable language of legal simulator semantics, an exact individual-order
price-time-priority kernel, or an externally justified cost between changes to information,
matching, clocks, randomness and agent definitions. Gradients can therefore find local sensitivity
inside one chosen relaxation; they cannot decide which simulator edit is semantically smallest or
which response is true in a market.

The fragmented-market replication supplies one excellent qualitative flip, but its compared greedy
rules change information and action kernels, its public fork is not a complete independent
two-lineage fixture, and the complete set of legal interpretations is unknown. It cannot label a
minimal-edit benchmark. Synthetic mutation operators written for EcoMD would label themselves and
measure recovery of researcher-planted causes, which is valid software QA but circular evidence for
a general scientific-debugging claim.

No GPU has positive decision value here. The decisive failures are algebraic and problem-definitional;
faster optimization would only solve a noncanonical objective.

## 7. Gate decision

| Gate | Result |
|---|---|
| Clear market contrast and two rival explanations | Pass conditionally |
| Minimal cause invariant to smooth coordinate changes | Fail by Proposition 1 |
| Minimal cause invariant to behavior-preserving edit refinement | Fail by Proposition 2 |
| Coordinate-free repair supplies a canonical market cost | Fail |
| Continuous differentiable-falsification method is unoccupied | Fail: Dawson--Fan, VERIFAI, global differentiable search |
| Discrete/formal minimal-edit method is unoccupied | Fail: MACE, delta debugging, GReduce |
| Public gold semantic-edit benchmark exists | Fail |
| Current EcoMD preserves the required hard-event semantics | Fail |
| External market truth adjudicates the flipped response | Fail |
| A recorded re-entry blocker is removed | Fail |

**Decision:** `not_trigger`, `removed_blockers: []`, and
`candidate_harvest_authorized: false`. This is a useful reusable falsifier, not a new route node.
The hostile full-T0 lower endpoint would be below the provisional 15% activation brake even before
benchmark feasibility, so a full F3 review is not opened.

## 8. Exact re-review condition

Re-audit only after one package jointly supplies:

1. a formal stochastic-market edit language with complete state, action, clock, information,
   randomness and observation semantics, plus a behavior-equivalence quotient fixed before results;
2. a market-native edit cost or set order proved invariant to smooth reparameterization and
   behavior-preserving atom split/merge, with an explicit normative interpretation;
3. a theorem or algorithm that is false for counterfactual search, differentiable failure
   prediction/repair, delta debugging, generator reduction, Rashomon enumeration, robust MDP/model
   checking and ACIF, with a matching lower bound;
4. two independently written, fully pinned systems with known gold minimal causes and hard negative
   cases; and
5. for any real-market claim, a lawful assigned intervention and untouched external response truth
   under the same state/action/clock/outcome grammar.

Another parameter norm, mutation library, gradient heat map, EcoMD-only benchmark, implementation
ensemble, or larger seed sweep is not a trigger. Until the condition is met, do not implement the
search, mutate EcoMD, open simulator outcomes, SSH to any worker, or schedule the A800/V100 GPUs.
