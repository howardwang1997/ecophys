# EcoMD Discovery Loop topic cycle 8: cross-engine discrepancy audit

**Date:** 2026-08-26
**Scope:** simulated markets, market physics, and financial physics
**Stage:** D-2 discrepancy-first semantics and theorem audit
**Literature cutoff:** 2026-08-26
**Outcome access:** none
**Decision:** passed-and-closed audit; zero topic cards and zero execution authorizations

## 1. Search question

Cycle 8 reversed the usual workflow. Instead of proposing another market-physics analogy and
then finding simulators that can express it, the cycle asked whether a qualitative disagreement
between two independent, state-complete market simulators could expose a missing physical
mechanism. A qualifying object had to satisfy all of the following:

1. the two engines implement one frozen state, action, clock, randomness, policy-information,
   and observation contract;
2. the discrepancy survives exact matching-kernel conformance and cannot be assigned to a bug,
   unspecified tie, output sampling phase, or random-number-stream shift;
3. the discrepancy implies a market-specific response theorem rather than ordinary simulator
   docking, operator splitting, causal abstraction, or model-form uncertainty; and
4. a prospective real-market or controlled-market bridge can decide which response is correct.

No formulation passed. ABIDES, PAMS, and Bourse are useful independent software lineages, but
their native schedulers do not implement one estimand. ABIDES processes timestamped messages and
permits message-by-message reaction after latency and computation delay. PAMS uses tick-time,
randomizes normal-agent order lists, preserves order within a list, executes after every order,
and may insert high-frequency agents after each list. Bourse asks agents to act before a fixed
step, shuffles the individual queued instructions, processes them, and only then advances the
agents again. Agreement on a manually injected exogenous order tape would be matching-engine
conformance; disagreement under native adaptive agents would compare different information
filtrations and mechanisms.

## 2. The cross-engine discrepancy trilemma

Let engine `i` have full state space \(X_i\), intervention/action space \(U_i\), Markov kernel
\(K_i^u\), observation map \(O_i\), and policy filtration \(\mathcal F^i_t\). Suppose there are
state and action maps \(\phi:X_1\to X_2\) and \(\alpha:U_1\to U_2\) such that

\[
\phi_\#K_1^u(x,\cdot)=K_2^{\alpha(u)}(\phi(x),\cdot),
\qquad O_2\!\circ\!\phi=O_1,
\]

and the policies see corresponding histories. The two engines then have the same observable path
law under every compiled intervention. In the deterministic, exogenous-tape case this follows by
induction over events. In the stochastic case it is the familiar kernel-intertwining or
probabilistic-bisimulation condition. A measured discrepancy means that at least one claimed map
or implementation is not conformant; the discrepancy alone does not identify a new law.

This leaves three possibilities:

1. **Same complete kernel:** a difference is a conformance failure, unspecified semantic choice,
   numerical error, or invalid randomness coupling.
2. **One generator, different numerical propagation:** a fixed-policy event engine and a
   finite-step split or batch engine differ by established operator-splitting error.
3. **Different policy information or market rules:** a continuous reactive engine and a batch
   engine are different mechanisms. Their difference can be economically meaningful, but it is
   not an implementation discrepancy and continuous-versus-batch market design is direct prior
   art.

An observable-level match does not create a fourth case. Two engines can reproduce the same L2
statistics while disagreeing under interventions because their hidden states or abstractions
differ. That is the already closed observation-quotient and interventional-simulator-fidelity
problem.

## 3. Native engine contracts

### 3.1 ABIDES

The pinned ABIDES kernel maintains a single priority queue ordered by message-delivery time.
Messages incorporate sender computation delay and communication latency. Agents may react to a
wakeup, execution, or other message before later messages arrive. This is a nanosecond-domain,
message-driven information structure. The public repository does not document a bit-complete
mid-trajectory checkpoint containing every agent, pending message, scheduler coordinate, and RNG
state.

### 3.2 PAMS

PAMS 0.2.2 is explicitly tick-time. Its `SequentialRunner` samples the normal-agent order, then
samples the returned order lists; it preserves the order inside each list, matches after every
order, and uses another shared-runner random draw to decide whether high-frequency agents may act
after a normal list. Consequently, changing whether one agent returns an empty list can change
later random-number consumption and the number of high-frequency opportunities. It is not a
native physical-time or isolated-RNG counterpart to ABIDES.

### 3.3 Bourse

Bourse 0.4.0 first calls the agents' update, then takes every queued new, cancel, and modify
instruction, shuffles the individual instructions with the simulation RNG, processes them one at
a time with successive integer timestamps, and jumps the clock to the next fixed step. Agents do
not react within that shuffled instruction block. Its JSON persistence covers the order book, not
the complete agent, queued-action, scheduler, and RNG state.

The three lineages are independent enough to falsify portability claims. They are not three
replications of a single endogenous path law. Replacing their runners with one common compiler
would produce researcher-authored wrappers, not independent native confirmation.

## 4. Screened descendants

| Route | Proposed object | Decisive failure | Hostile T0 lower / point / upper |
|---|---|---|---:|
| Exact-kernel cross-engine docking | Compile one state/action/event tape into two matching engines and treat any path difference as scientific evidence | With the same complete transition semantics the engines must agree; a difference is conformance or an underspecified rule, and verified matching/docking are established | 0 / 2 / 5% |
| Hard-boundary batch shadow generator | Use the discrepancy between event-driven and batched LOB dynamics as a boundary-localized market commutator | For a frozen generator it is Lie--Trotter or randomized-splitting error; observable and invariant-measure commutator theory is established, including jump processes | 2 / 6 / 13% |
| Adaptive scheduler information-filtration response | Attribute persistent continuous-versus-step differences to a new collective market timescale | Agents receive different histories and reaction opportunities, so the engines implement different mechanisms; asynchronous financial ABMs and frequent batch auctions directly occupy the broad effect | 3 / 8 / 17% |
| Disagreement-guided market intervention | Select the intervention maximizing distance between two simulators and use the disagreement as an uncertainty certificate | Simulator disagreement supplies neither truth nor calibrated coverage without external outcomes; model discrepancy, docking, causal abstraction, and interventional consistency are established | 1 / 4 / 10% |
| Action-packet and RNG-namespace discrepancy | Compare PAMS list atomicity, Bourse instruction shuffling, and ABIDES same-time messages under a matched seed | The first component is the closed partial-order/atomic-grouping problem; the second is common-random-number coupling, and a shared seed is not a common potential outcome | 1 / 3 / 7% |

No conservative lower bound reaches the 15% activation floor. The exact-kernel and action-packet
forms duplicate existing graph nodes and are not registered again. The other three are recorded as
failed-closed descendants of this cycle.

## 5. Killer constructions

### 5.1 Exact complete semantics cannot disagree

Start both engines at mapped states and feed the same next action and random mark. If the commuting
kernel condition holds, the next-state laws map exactly. Repeating the argument gives identical
finite-dimensional path laws. A distinguishing trace is therefore proof that the claimed compiler,
kernel, randomness map, or implementation differs. It is valuable debugging evidence, not by
itself a market-dynamics discovery.

### 5.2 A two-instruction matching-boundary commutator

Begin with a resting ask at 101. In one interval submit a new ask at 100 and a unit market buy. If
the new ask arrives first, the buy executes at 100; if the market buy arrives first, it executes at
101 and the new ask subsequently rests at 100. The instruction multiset and pre-state are the same,
while price and terminal book differ. ABIDES requires an arrival order; Bourse samples a permutation;
PAMS samples order-list order and preserves the sequence inside a list. This is not a common target
with three implementations. It is the standard hard-event ordering counterexample already captured
by the partial-order route.

### 5.3 Frozen-policy splitting is generic

For a continuous-time generator \(L=A+B\), exact propagation over \(h\) is
\(e^{h(A+B)}\). A first-order batched composition is \(e^{hA}e^{hB}\), whose local defect is
proportional to

\[
\frac{h^2}{2}[A,B]+O(h^3).
\]

The matching boundary can concentrate or amplify the commutator because adding, cancelling, and
clearing do not commute. It does not change the mathematical parent. Strong and weak jump-process
error, local observable error, long-run information loss, and invariant-measure bias already have
general analyses.

### 5.4 Reactive policies change the filtration

Let a market maker replenish immediately after its first fill. In a message-driven engine, the fill
can be delivered before the next incoming market order and the replenishment can trade. In a
pre-step action engine, both taker actions were chosen before the maker observes the first fill; the
replenishment cannot occur inside the batch. Holding the policy source text fixed does not hold its
input history fixed. Calling the output difference a numerical error hides a real change in the
information and action mechanism.

### 5.5 Agreement is not external validity

Construct two independent engines that both omit hidden reserve orders. They can agree on every
compiled displayed-book intervention and still disagree with a real venue whose reserve refreshes
after depletion. Conversely, one engine can be closer to the real system while disagreeing with the
other. Without an external assigned intervention and complete relevant state, model agreement and
disagreement have no calibrated truth interpretation.

### 5.6 A seed is not a stochastic coupling

Suppose one arm emits no order while the other emits one order. In PAMS, this changes whether an
order list enters later sampling and may change the number of high-frequency Bernoulli draws. In
Bourse, it changes the length and permutation of the transaction vector. The same numeric seed now
assigns different later random variates to different semantic events. Matched seeds are not common
potential outcomes unless randomness is explicitly namespaced by event and the coupling is frozen.
Adding such a namespace would change these native runners.

## 6. Prior-art reductions

- Alignment or docking of independent simulation implementations has explicitly distinguished
  identity, distributional, and relational agreement since Axtell et al.; conceptual replication
  is a verification method rather than a new dynamical law.
- Lie--Trotter, Strang, commutator, jump-process strong/weak error, invariant-measure error, and
  path-space relative-entropy error cover the fixed-policy event-versus-batch residual.
- Synchronous versus asynchronous updating has long been known to change qualitative many-agent
  dynamics. Financial-market work directly derives return effects from asynchronous belief
  updating, and event-driven matching-engine models already argue that reactive asynchronous
  interaction changes stylized facts and model identification.
- When batching is visible to agents, it is a market-design intervention. Frequent batch auctions
  explicitly replace serial continuous processing with discrete batches and analyze the economic
  response.
- If the target is choosing between imperfect simulators, computer-model discrepancy and
  interventionally consistent causal abstractions already supply the generic statistical framing.
  LOB-Bench supplies a direct market-output comparison benchmark but cannot turn simulator
  agreement into prospective discovery.

## 7. Real and controlled truth bridge

Authoritative exchange feeds provide the realized message sequence or matching-event boundary for
the deployed mechanism. They do not provide the counterfactual path under a different scheduler for
the same endogenous submissions. Replaying one fixed event tape can test a matching subkernel, but
it suppresses strategic reaction and reduces to conformance.

A continuous-to-batch venue change is also not a clean compiler check: traders change placement,
latency investment, cancellation, and information use in response to the rule. A valid empirical
study would therefore estimate a market-design treatment, for which direct theory already exists,
not isolate a simulator's numerical propagation error. No prospective, orthogonally assigned,
full-state field or laboratory bridge with two native simulator implementations was qualified in
this audit.

## 8. Reusable decision rules

1. Before comparing outputs, freeze a commuting diagram for complete state, action, clock,
   randomness, policy information, and observation. A shared class name such as `CDA` is not a
   same-estimand contract.
2. Split cross-engine differences into conformance error, numerical propagation error,
   information/mechanism difference, and external model discrepancy. Do not average them into one
   simulator uncertainty score.
3. A fixed exogenous tape can validate matching semantics but cannot validate adaptive market
   response.
4. Event batching under a fixed generator must be compared with standard commutator and
   invariant-measure error baselines before any market-specific claim.
5. A shared numeric seed is not a common-randomness intervention. Random marks must be bound to
   semantic events, and that binding must itself be native or declared researcher-authored.
6. Agreement between simulators is not validation; disagreement is not falsification. Both require
   an external truth contract.
7. A market-visible scheduler change is a mechanism-design treatment, not a numerical-method
   experiment.

## 9. Decision

**Passed-and-closed discrepancy-first audit; zero cards.** The strongest residual is the adaptive
scheduler information-filtration response, with a 3--17% hostile-T0 interval and an 8% point
estimate. Its effect is real in the sense that reactive continuous and pre-step batch agents can
generate different paths. It fails as a new topic because the engines do not implement one
estimand, asynchronous market dynamics and frequent batch design are direct priors, and no
prospective assignment decides a new theorem-level claim.

Reopen only if two independent native engines expose bit-complete branch state, isolated semantic
randomness, one physical clock, one action and information contract, and a discrepancy that remains
after matching conformance and all known splitting corrections. The residual must force a theorem
outside probabilistic bisimulation, operator splitting, partial-order semantics, market-design
comparative statics, and model discrepancy, and an external prospective intervention must adjudicate
it. A new hostile review must put the conservative T0 lower bound at or above 15%.

No sandbox, simulator run, market-data action, data purchase, external outreach, EcoMD edit, GPU, or
other experiment is authorized by this cycle.

## 10. Primary-work and official-semantics manifest

1. Axtell et al., *Aligning Simulation Models: A Case Study and Results*: https://doi.org/10.1007/BF01299065
2. Wilensky and Rand, *Making Models Match: Replicating an Agent-Based Model*: https://www.jasss.org/10/4/2.html
3. Chanda and Miller, *Replicating Agent-Based Models: Revisiting March's Exploration--Exploitation Study*: https://doi.org/10.1177/1476127018815295
4. Trotter, *On the Product of Semi-Groups of Operators*: https://doi.org/10.1090/S0002-9939-1959-0108732-6
5. Strang, *On the Construction and Comparison of Difference Schemes*: https://doi.org/10.1137/0705041
6. Engblom, *Strong Convergence for Split-Step Methods in Stochastic Jump Kinetics*: https://doi.org/10.1137/141000841
7. Hellander, Lawson and Drawert, *Local Error Estimates for Adaptive Simulation of the Reaction-Diffusion Master Equation via Operator Splitting*: https://doi.org/10.1016/j.jcp.2014.02.004
8. Abdulle, Vilmart and Zygalakis, *Long Time Accuracy of Lie--Trotter Splitting Methods for Langevin Dynamics*: https://doi.org/10.1137/140962644
9. Gourgoulias, Katsoulakis and Rey-Bellet, *Information Metrics for Long-Time Errors in Splitting Schemes for Stochastic Dynamics and Parallel Kinetic Monte Carlo*: https://doi.org/10.1137/15M1047271
10. Anderson, Ganguly and Kurtz, *Error Analysis of Tau-Leap Simulation Methods*: https://arxiv.org/abs/0909.4790
11. Huberman and Glance, *Evolutionary Games and Computer Simulations*: https://doi.org/10.1073/pnas.90.16.7716
12. Schönfisch and de Roos, *Synchronous and Asynchronous Updating in Cellular Automata*: https://doi.org/10.1016/S0303-2647(99)00025-8
13. Diks and van der Weide, *Herding, A-Synchronous Updating and Heterogeneity in Memory in a CBS*: https://doi.org/10.1016/j.jedc.2003.12.004
14. Jericevich, Chang and Gebbie, *Simulation and Estimation of an Agent-Based Market-Model with a Matching Engine*: https://arxiv.org/abs/2108.07806
15. Jericevich, Chang and Gebbie, *Simulation and Estimation of a Point-Process Market-Model with a Matching Engine*: https://arxiv.org/abs/2105.02211
16. Budish, Cramton and Shim, *The High-Frequency Trading Arms Race: Frequent Batch Auctions as a Market Design Response*: https://doi.org/10.1093/qje/qjv027
17. Byrd, Hybinette and Balch, *ABIDES: Towards High-Fidelity Market Simulation for AI Research*: https://arxiv.org/abs/1904.12066
18. Hirano, Takata and Izumi, *PAMS: Platform for Artificial Market Simulations*: https://arxiv.org/abs/2309.10729
19. ABIDES pinned kernel and repository: https://github.com/jpmorganchase/abides-jpmc-public/tree/f9cbe51342b7dedd9587e4e069040d68a5c6477f
20. PAMS 0.2.2 pinned sequential runner: https://github.com/masanorihirano/pams/blob/28cbb86192a019ddff00f9192d27e1ba87d381a8/pams/runners/sequential.py
21. Bourse 0.4.0 pinned fixed-step environment: https://github.com/zombie-einstein/bourse/blob/17285fde5a5293b55fed9236c7f35a859160a5f5/crates/step_sim/src/env.rs
22. Kennedy and O'Hagan, *Bayesian Calibration of Computer Models*: https://doi.org/10.1111/1467-9868.00294
23. Dyer et al., *Interventionally Consistent Surrogates for Complex Simulation Models*: https://proceedings.neurips.cc/paper_files/paper/2024/hash/26b8e3dc3a21fcd660d80c63b767f324-Abstract-Conference.html
24. Nagy et al., *LOB-Bench: Benchmarking Generative AI for Finance*: https://arxiv.org/abs/2502.09172
25. Garg et al., *Efficiently Verifying the Correctness of Marketplaces*: https://arxiv.org/abs/2412.08624
26. *Sequential and Parallel Market Clearing in Agent-Based Simulations*:
    https://doi.org/10.1016/j.jocs.2026.102793
