# Collision-cone exact counterfactual replay — T0 freeze

**Frozen:** 2026-08-24

**Status:** **CLOSED FAIL/RED at G0 on 2026-08-24.** This file preserves the preregistration; the binding result
is `papers/proposal/ecomd_collision_cone_replay_t0_result_2026-08-24.md`.

**Primary venue:** *Nature Computational Science*

**Selection:** `papers/proposal/ecomd_post_random_clock_problem_selection_2026-08-24.md`

**Forbidden before T0 PASS:** EcoMD implementation, benchmark code, GPU use, market outcomes, paid data and
full-scale simulation.

## Frozen question

Can a local rule intervention in a deterministic-replayable event-driven simulator be evaluated exactly by
replaying only its dynamically affected collision cone, with work controlled by the cone rather than the full
baseline trajectory, and with a non-circular subcritical certificate for the expected cone size?

This is not a claim that local event queues or common random numbers are new. The candidate survives only if it
adds an exact, output-sensitive counterfactual-replay result that is not already implied by rollback, lazy
cancellation, dynamic slicing, self-adjusting computation, rule-based counterfactual resimulation or standard
event-driven molecular-dynamics invalidation.

## Mathematical object

For initial state $s_0$, rule set $R$ and exogenous random field $\omega$, let

\[
\mathcal T_R(s_0,\omega)=((t_i,q_i,e_i,s_i^-,s_i^+))_{i=1}^{M}
\]

be the unique finite-horizon trajectory. Event order is the total order of event time $t_i$, declared priority
$q_i$ and immutable semantic event key $e_i$. Randomness is addressed by semantic keys in $\omega$; consuming a
different number of draws from a sequential pseudo-random stream does not qualify as shared randomness.

Every executed event declares the state locations it read and wrote, the event-calendar entries it created,
cancelled or changed, and the local eligibility certificate used to exclude an earlier event. The dynamic
dependency relation contains at least:

1. last-writer-to-read dependencies;
2. event creation, cancellation and rescheduling dependencies;
3. dependencies of the minimum-event and no-earlier-event certificates; and
4. dependencies created when a changed time, priority or event key reverses event order.

A local intervention $R\to R'$ supplies an indexable seed set $A_0$ of changed rule instances and potential new
instances. Its affected cone $D$ is the least fixed point under those dependencies, including events newly
created only in the counterfactual execution. A candidate algorithm may reuse a baseline event or trace segment
only with a certificate that its reads, enabledness, schedule position and exclusion of new earlier events remain
unchanged.

The output is a persistent delta representation of the counterfactual trajectory plus the terminal-state delta.
Materializing all $M$ unchanged events is outside the output-sensitive claim and necessarily costs $\Omega(M)$.

## Eligible theorem stack

The route needs all three results, not merely an implementation.

### T1 — from-scratch exactness

Under explicit sufficient conditions, applying the persistent delta to the baseline trace must equal a full run
of $\mathcal T_{R'}(s_0,\omega)$ event by event and state by state. The proof must cover inserted and deleted
events, changed event times, changed tie order, recoupling and the absence of an unrecorded earlier event.

### T2 — output-sensitive work

After a one-time trace-index construction whose cost and storage are reported, one intervention must cost

\[
O((k+|D|)\operatorname{polylog} M)
\]

or a strictly stronger bound, without scanning the full trace or all simulator objects. If a rule-level,
pre-intervention-certifiable multitype offspring envelope $B$ has $\rho(B)<1$, the theorem may additionally use

\[
\mathbb E|D|\leq \mathbf 1^\top(I-B)^{-1}a_0.
\]

A fitted or realized post-hoc branching ratio does not qualify, and restating the Galton--Watson total-progeny
identity is not a contribution.

### T3 — matching limitation

In a declared oracle or cell-probe model, any exact algorithm must inspect at least $\Omega(|D|)$ changed events
or changed state locations. The lower bound must state what persistent baseline index and output representation
the algorithm receives.

## Frozen G0 reduction buckets

Audit at least 40 unique primary works across:

- parallel/distributed discrete-event simulation, rollback and cancellation;
- incremental simulation, dynamic program slicing and trace repair;
- self-adjusting and incremental computation with from-scratch consistency;
- common-random-number, coupled and rule-based counterfactual simulation;
- event-driven hard-particle simulation and collision invalidation; and
- output-sensitive dynamic algorithms, disagreement propagation and subcritical influence clusters.

For every work record its formal object, exact guarantee, preprocessing model, per-change complexity, support for
new events and whether it absorbs T1, T2 or T3.

## Frozen toys

1. **FIFO/price-time queue:** a cancellation rule changes one resting order and later fills; the replay must
   detect both removed and newly exposed matches.
2. **Three hard particles:** changing the first restitution outcome shifts a later collision time and reverses
   the next-event order.
3. **Inserted earlier event:** the counterfactual enables an event absent from the factual trace before the next
   reused event; a read/write graph without absence certificates must fail.
4. **Recoupling:** factual and counterfactual local states diverge and later become identical; propagation must
   stop without changing the remaining persistent suffix.
5. **Global hazard control:** a local state change alters a global intensity or normalization; the cone becomes
   global and the algorithm must abstain rather than claim locality.

## D-minus-1 implementation contract

Before code, identify two independently maintained non-EcoMD systems:

- one order-level, strict price--time-priority market simulator; and
- one event-driven hard-particle simulator.

Each must permit deterministic replay and publication of a derived benchmark. Stable event identities, complete
state transitions, event-calendar mutations, event-keyed randomness, snapshots and dependency metadata must
already exist or be obtainable by a bounded instrumentation layer. EcoMD can only be a third stress test after
both external systems qualify.

## Immediate STOP rules

Close FAIL/RED on the first established condition:

- a primary work already supplies exact affected-cone replay and the same output-sensitive guarantee;
- T1 is a direct specialization of established from-scratch consistency with no collision-specific theorem;
- discovering or validating $D$ requires $\Omega(M)$ work per intervention;
- potential newly enabled events cannot be found without a global scan;
- stable event identities or keyed randomness cannot survive the intervention;
- the subcritical condition is observable only after generating the counterfactual cone;
- the statement is unchanged after replacing collisions by arbitrary event callbacks;
- either external-system contract fails; or
- the contribution is merely an engineering speedup or a first-market application.

## Decision rule and priors

PASS requires T1--T3, no exact G0 reduction, all five toys on paper, two external-system contracts and a concise
reviewer statement that does not use “first in markets”, “MD-inspired” or “powered by EcoMD”. Only then may a
small CPU implementation begin.

Planning prior: 4--8% for T0 survival and 1--2.5% for a complete NCS-grade package. These are not acceptance
probabilities.
