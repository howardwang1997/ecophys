---
name: ecomd-partial-order-event-t0-2026-08-23
description: "Partial-order hard-event T0 closed FAIL/RED: corrected semantics collide with linearizability/reachability, robust stochastic games and observational determinism; no metadata, data, implementation or GPU."
metadata:
  node_type: memory
  type: project
---

# EcoMD partially ordered hard-event T0 — lasting closure

The AMBER/T0-only card selected on 2026-08-22 is **FAIL/RED as of 2026-08-23**. Do not implement, inspect
market outcomes, acquire data, train EcoMD or use GPUs for this route. The conditional dual-resolution metadata
gate was not opened.

The frozen formula over static linear extensions was semantically incomplete. A poset controls precedence
availability, state controls enabledness, and atomic grouping prevents external interleaving. Under stochastic
updates one must declare either an open-loop order selected independently of future noise or, only when causally
supported, a non-anticipating feedback scheduler over observed history. Invalid paths require an almost-sure
completion restriction or an explicit failure outcome. A flat poset also cannot permit both placements of a
two-event block while excluding an insertion between its members.

After repair, the finite deterministic system is a configuration graph on completed down-sets, queue states and
an observer state for path-dependent outputs. Only (D=E) vertices accept; incomplete sinks are deadlocks, not
responses. On complete interval histories, an event includes its recorded return and is admissible only when the
sequential specification emits that return. The exits
reduce as follows:

- E1: legal history existence is linearizability against a sequential queue/priority-queue specification;
  extrema are reachability; distinct-output counting is #P-hard on an arbitrary-poset, add-only injective
  subclass; state-local conflicts are DPOR. PLDI 2026 already gives process-parameter FPT queue/priority-queue
  monitors.
- E2: under a declared finite fully observed Markov and matching uncertainty-game semantics, scheduler/kernel
  extrema have robust-value baselines. Joint confidence regions need not be rectangular, so an interval robust
  MDP may overapproximate. CAV 2019 PAC model checking and TACAS 2026 robust concurrent stochastic games are
  nearest work. A two-point indistinguishability bound prevents shrinkage below the separation of an
  observationally indistinguishable pair without order-law or identifying metadata; it does not cover the whole
  identified range with high probability.
- E3: all schedules giving one decision is observational determinism/product reachability; counterexample pairs
  are standard model checking. Observation-level confluence is sufficient rather than equivalent, and witness
  minimization needs an explicit cost; greedy event deletion gives at most a 1-minimal result without
  monotonicity.

The 55-source eight-bucket matrix passed its coverage audit but found exact collisions. Amarilli et al. already
compute possible/certain order-aware accumulation answers across partial-order possible worlds. Halm and Posa
already return a probabilistically approximated set over arbitrary simultaneous-impact ordering in rigid-body
dynamics, blocking the broad MD-transfer headline.

The four queue toys remain useful regression tests: disjoint commutation; cancel/execute enabledness; add versus
aggressive execution changing fill identity; and atomic grouping of split fills. An interval-order example also
shows enabledness-filtered legal schedules can be disconnected under adjacent legal swaps, so a local
commutator certificate is incomplete and must return to global reachability.

Full result: `papers/proposal/ecomd_partial_order_event_t0_result_2026-08-23.md`. Matrix:
`papers/proposal/ecomd_partial_order_event_t0_prior_art_matrix_2026-08-23.md`. Scratch:
`papers/proposal/ecomd_partial_order_event_t0_math_scratch_2026-08-22.md`.

No reserve card is automatically promoted. Return to fresh problem selection; do not rescue this route by
combining it with hard-event gradients or the previously closed observation-quotient/coarse-graining cards.
