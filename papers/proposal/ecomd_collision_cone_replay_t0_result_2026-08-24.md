# Collision-cone exact counterfactual replay — T0 result

**Date:** 2026-08-24

**Frozen config:** `configs/empirical_physics/ecomd_collision_cone_replay_t0_v1.yaml`

**Resource boundary:** zero implementation, benchmark runs, market outcomes, paid data, EcoMD execution and GPU

## Formal decision

**FAIL/RED at G0 exact reduction; stop the route.** Hanai et al. (2019) already introduce
*exact-differential simulation* for repeated discrete-event simulations: retain the baseline events, states and
anti-messages; accept event addition, deletion or state update; recursively replay only the altered events and
their causal influences through rollback; and obtain the same result as complete re-execution. The mechanism is
application-independent and was evaluated on both PHOLD and a microscopic Tokyo traffic simulation.

That prior work directly absorbs the frozen T1 headline. Once the missing soundness conditions are added, the
proposed proof is also a specialization of established from-scratch consistency for self-adjusting computation.
This triggers the frozen `generic_from_scratch_consistency_specialization` stop rule even though Hanai et al. do
not state the exact proposed $O((k+|D|)\operatorname{polylog}M)$ notation.

The residual pieces do not rescue the route. Work proportional to the changed execution trace has a generic
trace-distance theory; the proposed $O(k/(1-\rho))$ expectation follows immediately from a conditional
subcritical offspring assumption; and an $\Omega(|D|)$ bound is merely the cost of inspecting or emitting
$|D|$ declared differences. A market, collision or EcoMD implementation would therefore be an application of
the occupied generic method, not an NCS/NMI-grade scientific result.

The first-failure rule stops the 40-work audit, the external-system gate and all implementation. This document
records the decisive reduction and the formal guardrails discovered before closure; it is not a completed
40-source novelty matrix.

## Direct reduction to exact-differential simulation

| Frozen object | Hanai et al. (2019) object | Reduction |
|---|---|---|
| Stored baseline trajectory | All baseline future events, anti-messages and state data retained in timestamp order | Same reusable execution history |
| Local rule/event intervention | What-if `ADD`, `DELETE` and `UPDATE_STATE` queries at an LP and virtual time | Covers inserted/deleted events and local state/rule effects |
| Dynamically affected collision cone $D$ | Altered events and recursive influences detected through optimistic-PDES causality recovery | Same causal disagreement region, without collision-specific semantics |
| Selective replay | Roll back affected LPs, cancel obsolete events with anti-messages, insert new events and recursively reprocess influences | Same operational mechanism |
| From-scratch exactness | Referentially transparent event handler; repeat result identical to full execution of the same scenario | Absorbs T1 |
| Coupled stochastic execution | Same handler input must give the same output; the paper explicitly permits common seeded randomness | Event-keyed randomness is a stronger implementation discipline, not a new replay theorem |
| Output-sensitive motivation | $T(E_{\rm exdiff})=t_{\rm exdiff}|E_{\rm exdiff}|$ and reprocessing rate $|E_{\rm exdiff}|/|E_{\rm all}|$ | Already makes work depend on replayed influence rather than all events |
| Market/MD transfer | Transparent middleware supports arbitrary event handlers and multiple DES applications | Collision language does not make the theorem irreducible |

The journal article's abstract and Sections 3--4 explicitly state the same-result, altered-portion guarantee,
recursive rollback propagation, referential-transparency condition and three what-if operations:

- Hanai, Suzumura, Liu, Theodoropoulos and Perumalla,
  [*Exact-Differential Simulation: Differential Processing of Large-Scale Discrete Event Simulations*](https://doi.org/10.1145/3301499),
  *ACM TOMACS* 29(3), Article 18 (2019).
- [IBM Research publication record](https://research.ibm.com/publications/exact-differential-simulation-differential-processing-of-large-scale-discrete-event-simulations)
  and the [author-hosted article](https://kalper.net/kp/publication/2019-06-18-tomacs-exact-differential/2019-06-18-TOMACS-Exact-differential.pdf).

Its conference predecessor had already applied the method to a local road intervention:

- Hanai, Suzumura, Theodoropoulos and Perumalla,
  [*Exact-Differential Large-Scale Traffic Simulation*](https://doi.org/10.1145/2769458.2769472),
  SIGSIM-PADS (2015).

## Why T2 and T3 are not an independent escape

Let $Z_d$ be the number of newly affected events at propagation depth $d$. If the proposed theorem assumes

\[
Z_0=k,
\qquad
\mathbb E[Z_{d+1}\mid\mathcal F_d]\leq \rho Z_d,
\qquad 0\leq\rho<1,
\]

then

\[
\mathbb E|D|
\leq \sum_{d\geq0}\mathbb E Z_d
\leq k\sum_{d\geq0}\rho^d
=\frac{k}{1-\rho}.
\]

This is a geometric-series consequence, not a collision theorem. It becomes non-circular only if a uniform
offspring envelope is computable before the intervention from auditable local quantities and remains valid for
newly enabled events, retiming, priority inversions and scheduler dependencies. No such collision-specific
certificate was identified. A fitted branching ratio or the realized cone size cannot certify the claim.

Generic self-adjusting computation already records execution dependencies, rebuilds only affected parts, proves
agreement with a from-scratch run and bounds update time by trace distance. Trace reordering is also explicitly
covered:

- Ley-Wild, Acar and Fluet,
  [*A Cost Semantics for Self-Adjusting Computation*](https://home.ttic.edu/~pl/sa-sml/popl09.pdf), POPL (2009).
- Ley-Wild, Acar and Blelloch,
  [*Non-monotonic Self-Adjusting Computation*](https://doi.org/10.1007/978-3-642-28869-2_24), ESOP (2012).
- Acar, Blume and Donham,
  [*A consistent semantics of self-adjusting computation*](https://doi.org/10.1017/S0956796813000099),
  *Journal of Functional Programming* (2013).

The proposed T3 lower bound is true only after the output model declares $D$ explicitly: any algorithm that must
emit or verify $|D|$ distinct changed records needs $\Omega(|D|)$ record accesses in the usual unit-cost model.
That is an output-size observation. It does not separate collision replay from generic incremental computation,
and it supplies no matching lower bound for the harder task of discovering newly enabled or retimed events.

## First-failure prior-work map

The following primary works were sufficient to establish the reduction before the frozen 40-work minimum. They
are recorded to prevent a future rename of the same route.

| Work | Occupied component | Effect on frozen stack |
|---|---|---|
| Hanai et al. 2019, exact-differential simulation | Exact selective replay of altered DES events and causal effects; same result as full rerun | T1 direct collision; T2 mechanism substantially occupied |
| Hanai et al. 2015, exact-differential traffic simulation | Local real-system change with exact differential propagation | Blocks “first real system/market” rescue |
| Deelman and Szymanski, [breadth-first rollback](https://www.cs.rpi.edu/~szymansk/papers/pads97.pdf) (1997) | Incremental state saving recovers causal event relations and rolls back only affected events | Affected-cone rollback predates the candidate |
| Damani, Wang and Garg, [transitive dependency tracking](https://doi.org/10.1109/PADS.1997.594591) (1997) | Rollback based on transitive event dependencies | Dependency-closure mechanism occupied |
| Hwang, [incremental digital simulation](https://doi.org/10.1016/0167-9260(89)90057-6) (1989) | Resimulate modified or history-deviating portions; time tied to change implications | Output-sensitive simulation premise occupied |
| Lubachevsky, Shwartz and Weiss, [rollback analysis](https://doi.org/10.1145/116890.116912) (1991) | Rollback trees, branching random walks and stability/instability transition | Subcritical propagation is not a fresh analogy |
| Ley-Wild, Acar and Fluet 2009 | From-scratch consistency and change-propagation time bounded by trace distance | Generic T1/T2 theory |
| Laurent, Yang and Fontana, [counterfactual resimulation](https://doi.org/10.24963/ijcai.2018/260) (2018) | Shared stochastic contingencies and selective resimulation of affected rule-based events | Counterfactual/event-rule framing occupied |

## Soundness audit of the proposed baseline cone

A baseline dynamic read/write graph plus a common seed is not sufficient for exact replay. The following finite
counterexamples identify the additional conditions that any future incremental simulator must enforce.

| Case | Counterexample | Required repair |
|---|---|---|
| Sequential RNG | Deleting event $A$ shifts every later pseudo-random draw used by $B,C,\ldots$ | Randomness keyed by stable event identity and semantic draw site |
| Newly generated event | A changed event creates $C$ before a baseline event $B$, but $C$ has no baseline dependency node | Online fixed point over old and newly generated trajectories |
| Insertion into the past | A replayed event schedules a new event earlier than the current frontier | Roll back to the insertion time or reject the intervention |
| Negative enabledness | Removing $A$ enables baseline-disabled $B$, which was never executed or logged | Guard and absence dependencies, including false candidates |
| Latent branch write | A changed guard activates a write absent from the baseline dynamic write set | Complete effect envelope, not baseline writes alone |
| Collision retiming | A local velocity change moves or removes a collision across another event | Collision certificates plus schedule/order dependencies |
| Tie-order change | Equal-time events become reordered after a priority/key change | Stable deterministic total order or declared batch semantics |
| Global scheduler | One priority edit changes the service order of all queued jobs | Sound global-cone abstention; locality cannot be assumed |

Stable identities must be causal names, not global execution counters or mutable child ordinals. The cone must
also include writes, reads, guards, event creation/cancellation, time/priority changes, queue-minimum certificates
and the absence of a newly earlier event. Defining $D$ after comparing two complete executions makes correctness
tautological but forfeits the output-sensitive algorithm.

## Binding closure

Do not implement this route, run a benchmark, inspect market outcomes, fit EcoMD or use GPU. Do not claim novelty
from event-keyed randomness, a persistent trace delta, a collision vocabulary, a market application or the
geometric offspring bound. The external market-simulator and hard-particle-system contract was not reached and
must not be reported as failed.

Reopen only with a fresh preregistration that states a **collision-specific** theorem not implied by
exact-differential simulation or self-adjusting computation. At minimum it must construct a sound online cone
without a counterfactual oracle, cover disabled events and schedule inversions, derive a uniform subcritical
certificate from pre-intervention quantities, prove a separating lower bound, and yield a scientific conclusion
beyond software acceleration. Merely specializing arbitrary DES callbacks to price-time matching or hard
particles does not qualify.
