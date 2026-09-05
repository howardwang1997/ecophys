# EcoMD counterfactual-coupling re-entry audit

**Date:** 2026-09-04

**Mode:** outcome-blind theorem, artifact and release audit; this is not a discovery cycle

**Decision:** **NO QUALIFIED TRIGGER.** Deterministic event logs add an exact replay container but
not a common stochastic hard-event gradient system. Counterfactual-coupling ambiguity is real, but
the generic theorem, partial-identification and transport-gradient territory is directly occupied.
No candidate harvesting, implementation, simulator run, SSH session or GPU job is authorized.

## 1. Exact question tested

Does the combination of newly released deterministic event-graph worlds and coupling-aware world
models create a representation-invariant ICLR question for EcoMD: can a fixed-noise differentiable
market response be certified from observational or interventional path laws without observing the
same-unit counterfactual?

The rival explanations were:

- **H1 -- structural gradient:** once all intervention-indexed path distributions are correct, the
  simulator's fixed-noise pathwise gradient is a scientific response of the represented market;
- **H0 -- coupling gauge:** the path distributions determine population responses but not how
  stochastic worlds are paired, so sample-level counterfactuals and fixed-noise gradients can change
  under an observationally and interventionally invisible recoupling.

A positive result would have justified a coupling-invariant gradient certificate or abstention rule.
A null result still matters because it states exactly which EcoMD gradients may be used for
optimization but not interpreted as identified individual market mechanisms.

## 2. Deterministic Event-Graph Substrates do not supply the missing testbed

[Rovai (2026)](https://arxiv.org/abs/2605.15967) defines a state as a typed RDF ABox plus an
append-only insert/retract log, forks at a chosen tick, and applies one of five typed interventions.
This is a genuine exact-replay capability under a closed-event contract. The paper is CC BY 4.0.

It does not satisfy the pending hard-event contract:

1. after an intervention, physical-domain deltas are emitted by an **external deterministic
   simulator**; the substrate does not define a stochastic event kernel, exposed propensity,
   shared-noise coupling or gradient target;
2. the central ancestor-duality result assumes closed events, exogeneity of non-ancestors and no
   emergent interactions; the reported counterfactual procedure needs a heuristic precisely when
   new interactions arise;
3. the intervention language (`Assert`, `Retract`, location and awareness edits) is not the same
   action/state/response grammar as DoTime or a legal market order; and
4. although the paper says JSONL artifacts are bundled with a released repository, neither the
   arXiv record/source nor a search of the author's public repositories exposed a paper repository
   at the audit cutoff. This is an availability finding, not proof that no repository exists.

The source therefore adds another semantically distinct exact world. It does not provide the second
independently maintained, licensed fixture implementing the **same** hard-event intervention and
gradient semantics. The existing testbed trigger remains only a partial capability.

## 3. A coupling-gauge witness for fixed-noise gradients

Let (U\sim\operatorname{Unif}[0,1)), let (a\in\mathbb{R}) be a continuous intervention, and
consider two simulator implementations

\[
X_a=a+U,
\qquad
\widetilde X_a=a+((U-ca)\bmod 1).
\]

For every fixed (a), both simulators have exactly the same intervention law,

\[
X_a\overset{d}{=}\widetilde X_a\sim\operatorname{Unif}[a,a+1),
\]

and therefore the same population mean and correct population derivative,

\[
\frac{d}{da}\mathbb E[X_a]
=\frac{d}{da}\mathbb E[\widetilde X_a]=1.
\]

Yet, away from the moving wrap boundary, their fixed-noise pathwise derivatives are

\[
\partial_a X_a=1,
\qquad
\partial_a\widetilde X_a=1-c.
\]

Choosing (c>1) reverses the apparent sample gradient, and varying (c) makes it arbitrary, while
preserving **every** intervention-indexed marginal distribution. The moving boundary supplies the
term missed by an invalid interchange of derivative and expectation. The same construction can be
inserted after a discrete market event or scheduler branch.

This separates three objects that must not be conflated:

- the derivative of an expected intervention response, which is a functional of the interventional
  laws when those laws are available and regular enough;
- an individual or same-noise counterfactual, which requires a cross-world coupling; and
- a straight-through or naive pathwise derivative across a hard boundary, which can omit a boundary
  or likelihood term and need not estimate the first object.

Thus H1 is false without an independently justified coupling and boundary calculus. This is a useful
EcoMD interpretation gate, but it is not a new ICLR theorem by itself.

## 4. Why the generic method claim is occupied

- [Bongers et al.](https://arxiv.org/abs/1611.06221) already distinguish observational,
  interventional and counterfactual equivalence and give examples where interventional equivalence
  does not imply counterfactual equivalence.
- [Nasr-Esfahany and Kiciman](https://arxiv.org/abs/2301.09031) prove non-identifiability of learned
  SCM counterfactuals for general multidimensional exogenous mechanisms, give identifiable monotone
  cases and estimate worst-case counterfactual error.
- [Jankowiak and Obermeyer](https://proceedings.mlr.press/v80/jankowiak18a.html) identify pathwise
  gradient estimators with solutions of a transport equation, including non-unique multivariate
  velocity fields and optimal-transport variance choices.
- [Ribeiro, Santhirasekaram and Glocker](https://proceedings.neurips.cc/paper_files/paper/2025/hash/d938b739ac250e22729cc26e6176f65e-Abstract-Conference.html)
  directly address counterfactual identifiability with dynamic optimal transport and freeze the
  monotone/rank-preserving conditions that select a unique map.
- [WorldKernel](https://arxiv.org/abs/2606.10934) now directly packages the same rung-3 warning as
  counterfactual-coupling bounds and an arena scored for interval honesty. The paper expressly says
  its contribution is **not** a new identifiability result and describes its SDP as a second-moment
  instance of existing counterfactual partial-identification machinery. Its MIT-licensed v0.2.0
  repository already implements counterfactual bounds, sequential potential outcomes and the arena.

Consequently, the obvious paper variants are all reductions:

- “same rollout laws, different fixed-noise counterfactuals” is counterfactual non-identifiability;
- “choose a canonical coupling” is a monotonicity or optimal-transport assumption;
- “optimize the pathwise coupling” is transport-based gradient variance reduction;
- “report a range instead of a point” is counterfactual partial identification and proper interval
  scoring; and
- “apply this to EcoMD” supplies an instance, not an irreducible method, unless market-native
  observables make a non-vacuous bound possible.

## 5. Artifact and truth-asset rechecks

- QuantReplay still points to commit `a58c7c6d5436601d447129a7a81e662ba102cd9c` from 2026-08-12;
  no later tagged checkpoint was found. Its generator RNG, future scheduling, phase and external
  strategy state therefore remain outside the persisted branch state.
- `intrepidkarthi/orderbook` has 26 commits after tagged v0.26.0, but no new tag. The changes concern
  matching/WAL fixes, admission controls, documentation, tests and a seeded web-console sharing
  feature; they do not add a complete simulator population, policy filtration, RNG, scheduler,
  latency and venue-calendar checkpoint. The prior trigger condition is unmet.
- A narrow search of OSF, Dataverse and openICPSR surfaced a published laboratory auction package,
  not a newly registered lawful market-action tape with frozen full lifecycle, a future untouched
  release and an independently governed same-estimand confirmation source. No dataset files or
  outcomes were opened.

## 6. Trigger verdict

| Proposed trigger | Decision | Genuine update | Fatal issue |
|---|---|---|---|
| Event-graph substrate as second testbed | `not_trigger` for re-entry | Exact typed log forks and replay are real. | External deterministic dynamics; no common stochastic hard-event gradient or market action; public complete paper fixture not located. |
| Coupling-invariant EcoMD gradient | `not_trigger` | The moving-wrap witness cleanly separates marginal response, individual counterfactual and naive pathwise gradient. | Core equivalence, non-identification, transport and partial-ID results are direct prior art; market intervention marginals are absent. |
| WorldKernel market extension | `not_trigger` | Public bounds/arena make counterfactual honesty an executable generic benchmark. | The generic contribution is already made; an EcoMD row is application-only and internal coupling is not field truth. |
| Updated engine checkpoint | `not_trigger` | `orderbook` improved after v0.26.0. | No new tagged complete-market checkpoint or independent scientific lineage. |

One append-only coupling audit is recorded. It removes zero blockers and leaves
`candidate_harvest_authorized: false`. The event-graph source does not materially change the prior
partial testbed capability, so that entry is not superseded merely to count another exact world.

## 7. Exact re-entry condition

Re-open only if a written object supplies **all** of the following:

1. a market-observable, non-vacuous population-response or counterfactual bound under partial state;
2. invariance to admissible exogenous-noise recouplings and event-log refinements, or an independently
   justified coupling whose assumption is explicitly testable;
3. a theorem or estimator not reducible to SCM counterfactual equivalence, response-type/moment
   partial identification, dynamic optimal transport, pathwise transport equations, likelihood or
   boundary corrections; and
4. the same assigned action, complete state/filtration and outcome target in two independent
   executable systems plus an untouched real or laboratory confirmation family.

Until that object exists, a coupling layer, event-log adapter, interval score or additional EcoMD
seed has zero decision value. All three workers remain at zero allocation for this route.
