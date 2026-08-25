# Structural-complement and prospective-mechanism reselection

**Date:** 2026-08-25
**Stage:** D-3 to D-1, outcome blind
**Decision:** no new topic card; all frozen formulations failed before implementation

## 1. Why this round was different

Earlier searches repeatedly started from a physics method and then looked for a market
application. This round instead took the set complement of the route knowledge graph. It
asked which market-native state, action, or observable had not already been killed by
observation quotients, local-to-global gaps, hard-event semantics, field contracts,
cross-system mismatch, or standard-parent reductions.

The only clean structural complement was **exchange-hosted executable metadata**: dormant
conditional orders, queue-priority tokens, reserve instructions, beneficial-owner conflict
rules, rolling message credits, and rule-migration maps. A separate scan sought announced
2026--2027 mechanisms with two independently varied physical scales. No market outcomes,
simulator run, implementation, dataset download or purchase, external outreach, EcoMD
change, model call, or GPU was used.

The activation rule remained unchanged: the conservative hostile-T0 lower bound must be at
least 15%, the central result must escape an exact prior or mature parent problem, two
independent simulators must implement the same estimand, and a real observation bridge must
be qualified before an outcome-blind decision can authorize work.

## 2. What Nature-level computational evidence actually looks like

Recent adjacent papers make the target evidentiary burden concrete. Successful work does
not rely on a single attractive analogy or on two simulators showing the same plot.

- [Machine-guided path sampling](https://doi.org/10.1038/s43588-023-00428-z) combines a
  new closed-loop computational method, transition-path theory, interpretable mechanism
  extraction, four qualitatively different molecular systems, and large efficiency gains.
- [TrajCast](https://doi.org/10.1038/s42256-026-01227-7) tests a new equivariant trajectory
  operator across molecules, crystals and liquids, including out-of-distribution physical
  regimes, scaling and explicit failure boundaries.
- [Synthetic Lagrangian turbulence](https://doi.org/10.1038/s42256-024-00810-0) validates
  multiscale and high-order statistics, extreme events, and known small-scale failure
  against DNS and experiment rather than reporting only a familiar heavy tail.
- [pySTED](https://doi.org/10.1038/s42256-024-00903-w) validates the simulator component by
  component and deploys the same learned action--observation loop on a real microscope.
- A [chemical digital twin](https://doi.org/10.1038/s43588-025-00857-y) closes both the
  forward and inverse loop against measured spectra and treats degeneracy as a stopping
  condition.
- [Parallel symbolic enumeration](https://doi.org/10.1038/s43588-025-00904-8) compensates
  for the lack of a field intervention with hundreds of truth-defined problems, strong
  baselines, independent seeds, and a recovery--runtime Pareto improvement.

The implied evidence chain is therefore: an irreducible object, theorem, or algorithm;
gold-standard truth for the same estimand; cross-system and out-of-distribution tests;
explicit error control and hard negatives; and, for a sim-to-real claim, the same
action--state--observation loop in the real system. The present candidates fail before this
chain begins.

## 3. Exchange-hosted state: the three strongest formulations

### 3.1 Conditional-order closure

Let the complete exchange state be `x = (B, p, C, F)`: active L3 book, trigger reference,
dormant conditional-order ledger, and fired set. Given an external message, repeatedly
match, select the next eligible order under venue priority, and apply its action until no
guard is true. The proposed observable was the closure size, volume, final price, or the
commutator obtained by exchanging two triggering messages.

This does not create a new dynamics class. If guards and actions are monotone and
firing-order independent, the closure is a least fixed point on a finite lattice. If OCO,
cancel, stop, or peg actions make it non-monotone, termination, confluence and observable
determinism are the classical event-condition-action rule problem
([Aiken, Hellerstein and Widom, 1995](https://doi.org/10.1145/202106.202107)). Fixed venue
priority makes it a deterministic finite-state transducer. Random trigger populations
return branching or threshold cascades, while stop-driven market cascades are already a
direct market result ([Osler, 2005](https://doi.org/10.1016/j.jimonfin.2004.12.002)).

Two killer twins are decisive:

1. identical public L3 state and external sell order, but one world contains a dormant sell
   stop and the other does not; the final price differs by several ticks, proving that the
   armed ledger, not a public closure law, carries the response;
2. simultaneous buy- and sell-stop eligibility, where buy-first and sell-first produce
   opposite terminal prices; the result is venue snapshot and priority semantics, not a
   cross-market invariant.

No pair among ABIDES, PAMS and Bourse natively implements the same stop/OCO/peg ledger and
eligibility semantics. Ordinary L2/MBO does not archive every participant's outstanding
armed condition. **Hostile T0: 2--5%; lower bound 2%. Failed-close.**

### 3.2 Queue-priority holonomy

Let `X` contain order IDs, timestamps and ordered queues, and let `pi(X)` retain only
aggregate L2 depth. A cancel--re-add loop can satisfy

\[
\pi(T_\gamma x)=\pi(x)
\]

while changing which order is first and therefore who receives the next fill. This looks
like a geometric phase only because the proposed loop discards the priority coordinate.

The exact two-order witness starts from `[A, B]`. Cancel and re-add `A` gives `[B, A]`;
cancel and re-add `B` gives `[A, B]`. Both aggregate paths are `2 -> 1 -> 2`, but the next
unit market order fills different owners. Hence:

- on L2, the effect is non-lumpability of the observation quotient;
- on complete MBO state, the path is not closed;
- if the complete state truly returns to `x`, a Markov matching engine gives identical
  future response and the proposed holonomy is zero;
- stochastic action loops reduce to noncommuting Markov kernels and the established
  stochastic-pump/geometric-phase theory.

Queue position already has explicit economic value
([Moallemi and Yuan](https://doi.org/10.2139/ssrn.2996221)), and
[CME MBO](https://www.cmegroup.com/articles/faqs/market-by-order-mbo.html) publishes the
OrderID/PriorityID coordinate that resolves the apparent loop. Natural cancel--re-add paths
are also endogenous, not controlled cycles. **Hostile T0: 3--7%; lower bound 3%.
Failed-close.**

### 3.3 Iceberg regeneration depinning

The proposed interface consumed displayed liquidity while an exchange-hosted iceberg
revealed reserve volume. With displayed peak `v_i`, hidden residual `h_i`, and refresh rule
`rho_i`, one might seek a pinned--moving threshold in the ratio of consumption and
refresh rates.

The public-state twin is fatal: two books can display the same one unit at the best ask,
while only one has hidden reserve `M`; the same market order crosses the first book and
stays pinned in the second. If refresh is instantaneous, the crossing rule is merely the
cumulative displayed-plus-hidden capacity threshold. If refresh is finite, the model is a
latent-to-revealed reaction/queue system. The latter is directly occupied by
[Dall'Amico et al.](https://doi.org/10.1088/1742-5468/aaf10e), including a calibrated
liquidity-instability threshold. Venue-specific refresh priority gives a second rule twin
rather than a universal interface law. No two project simulators expose identical native
reserve semantics, and real MBO does not reveal the pre-refresh residual.
**Hostile T0: 1--3%; lower bound 1%. Failed-close.**

Three lower-ranked structural sketches also stopped before route instantiation:
self-trade-prevention topology reduced to constrained matching with unavailable beneficial
ownership; cyclic tick-grid memory reduced to non-bijective quantization hysteresis; and
rolling message credits reduced to token-bucket queueing with private account state.

## 4. Prospective two-scale and complete-state mechanisms

The second branch searched announced or recurring mechanisms for an outcome-blind,
orthogonal assignment. None supplied it.

| Frozen formulation | Hostile T0 lower / point / upper | Earliest decisive failure |
|---|---:|---|
| AEMO Project EnergyConnect capacity × market operator | 6 / 11 / 18% | Readiness dates are not treatment dates; the 800 MW release is test-contingent, dispatch and settlement are not factorial, and official NEMDE/SRA state is incomplete. |
| Nasdaq--NYSE Arca 23/5 boundary operator | 7 / 10 / 13% | Both venues change on the same date, overnight bands are bundled, routing is endogenous, and proprietary displayed feeds omit router/hidden/CAT state. |
| SEM FASS--DASSA commitment × recourse | 4 / 6 / 9% | Day-ahead, secondary and real-time products launch together; real-time activation is shortage-triggered and complete bids/network state are not public. |
| Solana SIMD-0553 × SIMD-0123 fee/reward controls | 3 / 6 / 11% | Both proposals lack a frozen activation; the first gate bundles fee changes, there is no 2×2 assignment, and nonincluded demand is absent. |
| Ethereum BPO3 capacity × controller gain | 2 / 5 / 9% | Activation and parameters are blank; pseudo-test values scale target, maximum and gain together, reproducing the known normalized-controller alias. |
| Included failed/reverted transaction pressure | 2 / 5 / 10% | An included execution failure is not a rejected intent, and a cross-program minimum displacement to success is not a canonical quantity. |

The final row was a separate complete-state check. [EIP-658](https://eips.ethereum.org/EIPS/eip-658)
status zero omits invalid, replaced, dropped and private transactions; Solana `meta.err`
omits preflight rejects, TPU drops and unlanded bundles. Different routers can encode the
same economic swap with different slippage predicates, while custom errors, out-of-gas,
deadlines and storage guards have no shared one-dimensional distance to success. Direct
work already studies failed-transaction and MEV collisions
([Flash Boys 2.0](https://arxiv.org/abs/1904.05234),
[First-Spammed, First-Served](https://arxiv.org/abs/2506.01462), and
[Why Does My Transaction Fail?](https://arxiv.org/abs/2504.18055)). At most this supports a
narrow predictive diagnostic after admission-point logging; it does not identify a causal
market pressure.

## 5. Decision and reusable boundary

This round produces **zero admissible cards**. The highest lower bound is 7%, and the only
upper bound above 15% belongs to a design whose assignment is explicitly test-contingent.
Upper-bound optimism cannot substitute for the protocol's conservative lower-bound gate.

Reusable results are retained:

- a nonzero loop that closes only after deleting priority is an observation-quotient
  witness, not market holonomy;
- a full-state deterministic loop must return the same response, so any residual identifies
  omitted state, stochastic forcing, or a non-closed action path;
- hosted conditional cascades must escape fixed-point/ECA/confluence and direct stop-cascade
  theory before simulation;
- an announced readiness date is not an intervention if the actual state transition depends
  on tests, demand, scarcity, routing, or administrator discretion;
- an included failed transaction is selected execution evidence, not the population of
  attempted market actions.

No simulator, implementation, data purchase, outcome access, external outreach, EcoMD
modification, or GPU is authorized for these formulations. A future child must begin with
a different market-native contradiction and independently clear every Discovery-Loop gate.
