# Resolution-certified partially ordered event dynamics — T0 result

**Closed:** 2026-08-23

**Verdict:** **FAIL / RED**

**Failure stage:** mathematical object and E1--E3 nearest-work reduction

**Metadata gate:** not opened

**Compute/data used:** literature and finite symbolic examples only; no market outcome, data acquisition,
benchmark, fit, holdout or GPU

## 1. Decision

Close the selected card. No eligible exit survives:

- E1 is linearizability/language reachability, dynamic partial-order reduction or linear-extension counting once
  state-dependent legality is written correctly;
- E2, once finite fully observed uncertainty semantics are declared, has PAC/robust stochastic-game baselines
  plus a standard indistinguishability lower bound;
- E3 is observational determinism and product reachability; observational confluence is one sufficient proof
  technique, followed by standard counterexample extraction.

The molecular-dynamics transfer also fails as a novelty rescue: set-valued dynamics over arbitrary simultaneous-
impact ordering already exists with existence, dissipation, finite-termination and probabilistic set-
approximation guarantees.

This is a verdict on the frozen formulation, not a theorem that no future restricted order-book problem can be
new. A future card would need a formally different object and a proved result before mentioning markets.

## 2. The frozen mathematical object fails as written

The frozen response set quantifies a static linear extension

\[
\pi\in\mathcal L(P).
\]

That is incomplete alongside the card's requirement of state-dependent enabledness, but it is not automatically
contradictory. A poset only says which unprocessed event blocks are precedence-available; the current state says
which are executable. The stochastic model must choose one of two distinct information structures.

- In an **open-loop** model, (\pi) or an order law is selected before execution and independently of future
  noise. Restrict to orders that complete almost surely, or retain invalid paths with an explicit absorbing
  failure response.
- In a **feedback** model, use an adaptive scheduler only if the ordering mechanism can condition on observed
  history. Let (H_j) be that history and (\mathcal F_j=\sigma(H_j)); then

\[
\gamma_j(\cdot\mid H_j),
\]

  is (\mathcal F_j)-measurable and supported on precedence-available blocks that are admissible almost surely
  under the conditional state law. Full-state feedback is allowed only if full state observation is declared;
  otherwise the policy uses the observable history or belief state.

Using feedback without causal support enlarges exogenous order uncertainty into a controller or adversary. The
frozen formula fails to state this choice, pathwise completion/failure or recorded-return consistency. Turning an
invalid operation into a reject/no-op changes a recorded-history object: a feed event reported as successfully
completed is replaced by a rejection.

Atomic grouping is a separate primitive, not another ordinary poset edge. If a two-message block has
(x\prec y) and an external event is (z), permitting both placements (zxy) and (xyz) forces any flat poset to
permit the false interleaving (xzy). The observation contract must first quotient split messages into a macro-
event or use a hierarchical event/transaction semantics.

After these repairs, a finite observer with state (q) retains path outputs such as fill tapes. The deterministic
graph has vertices ((D,s,q)) and an edge for each currently available, enabled and return-consistent block. Only
vertices with (D=E) are accepting. Legal complete schedules are exactly its root-to-accepting paths; a sink with
(D\ne E) is a non-accepting deadlock. That correction makes the problem coherent, but also exposes the exact
reductions below.

## 3. Toy audit result

The four mandatory queue cases all behaved as required.

| Case | Result | What it establishes |
|---|---|---|
| disjoint partial cancels | both orders legal and identical | ordinary semantic independence/commutation |
| full cancel and execution of the same order | only execute-then-cancel is legal | (mathcal V(P,s)\subsetneq\mathcal L(P)); legality is a sequential-state property |
| better-priced add and atomic aggressive execution | both orders legal but fill different identities and leave different books | any deterministic tie rule suppresses a legal response |
| generative aggressor macro-event split into children | generic child consumptions permit a false third tape; a separate identity-bearing recorded contract instead rejects the inconsistent placement/interleaving | atomic grouping must precede partial-order construction, and generative versus recorded-return semantics must not be mixed |

In the fourth case, (G=M(2)) is explicitly a generative block with no recorded fill return, so its placements
before and after the concurrent add are both counterfactual simulator executions. If a feed instead records the
identity tape ((A,B)), consistency accepts only the macro placement that emits ((A,B)); splitting its rows into
generic children yields a false ((A,C)) tape, while splitting them into identity-targeted children makes that
interleaving deadlock. These are separate observation contracts, not three outcomes of one recorded event.

Market protocol evidence supports the last distinction without opening outcomes. A state-dependent Hawkes study
records that LOBSTER can represent one market order matching (n) resting orders as (n) equal-timestamp rows
and aggregates them back into one event
([Morariu-Patrichi and Pakkanen](https://doi.org/10.1080/14697688.2021.1983199)). CME's
`MatchEventIndicator` and Eurex's `CompletionIndicator` provide official macro-event boundaries. Conversely,
Nasdaq/NYSE packet or symbol sequence fields show that equal timestamps do not automatically imply unknown
order.

These cases are valuable semantic tests, but none is a theorem-level exit.

## 4. E1 — FAIL/RED

### 4.1 Exact reduction

On the complete interval-history subclass, encode each event as
(e=(\mathrm{op},\mathrm{arg},\mathrm{ret})), take (P) to be operation real-time order and use the price--time book
update as the sequential ADT specification. A step is admissible only when the specification's emitted return
equals the recorded return. A legal complete schedule then exists exactly when the history is linearizable in
the sense of [Herlihy and Wing](https://doi.org/10.1145/78969.78972). Queue/priority-queue linearizability has
already been reduced to state reachability and receives data-structure-specific algorithms and complexity
boundaries.

For a finite observer, the extremal problem is min/max reachability on the augmented graph ((D,s,q)), with the
payoff evaluated only at accepting vertices (D=E). For cardinality, any poset has an injective price--time
embedding: add one unit order per element at the same price; the accepting FIFO identity tape is exactly the
selected linear extension. Thus distinct-output counting is (\#P)-hard even on this arbitrary-poset, add-only,
injective subclass. This does not claim membership in (\#P) for the general collision-prone distinct-output
problem or hardness restricted to interval orders.

### 4.2 Nearest exact work

- [Lee and Mathur, PLDI 2026](https://doi.org/10.1145/3808315) already give fixed-parameter linearizability
  monitoring for queues and priority queues in the number of processes (k), including
  (O(k2^{2k}n^2)) for FIFO queues and (O(k2^k n\log n)) for priority queues.
- [Amarilli et al.](https://doi.org/10.1016/j.tcs.2019.05.013) already interpret all linear extensions as possible
  worlds, compute order-aware accumulation-result sets, ask possible/certain-answer questions and give NP/coNP
  hardness plus bounded-width/operator tractability.
- Current trace/POR work supplies #P hardness, FPRAS/almost-uniform sampling and separate DPOR-space hardness/
  unbiased-estimation results
  ([POPL 2026](https://doi.org/10.1145/3776723),
  [PLDI 2026](https://doi.org/10.1145/3808291)).
- Context-sensitive and stateful DPOR already make dependence a reached-state property.

No formal semantic-conflict parameter distinct from process count, frontier state, context-sensitive dependence,
partial alternatives or standard graph width was defined. No new algorithm and matching lower bound was proved.
E1 therefore triggers its own kill rule.

## 5. E2 — FAIL/RED

Under a finite fully observed Markov model and an explicitly specified matching uncertainty-game semantics, the
scheduler can select an available event, the learned kernel can supply the stochastic transition, and extremal
responses can be encoded as robust value problems. This reduction requires specifying who selects a kernel and
when: a joint confidence region can be non-rectangular, while an ordinary interval/rectangular robust MDP may
strictly overapproximate it. PAC statistical model checking is therefore a close baseline for unknown transition
probabilities together with MDP/game nondeterminism
([Ashok, Křetínský and Weininger](https://doi.org/10.1007/978-3-030-25540-4_29)); interval concurrent stochastic
games now combine strategic choices and epistemic transition uncertainty directly
([He and Parker, 2026](https://arxiv.org/abs/2601.12003)).

The elementary lower bound is also unfavorable. If two admissible systems induce the same observed-data law but
have responses (\theta_0,\theta_1), any set with (1-\alpha) coverage under both must contain both values with
probability at least (1-2\alpha). Its diameter is therefore at least
(|\theta_1-\theta_0|) on that event, regardless of sample size. More generally, let an unvisited-transition event
(U) have probability (q) under both models and suppose their conditional observed-data laws agree on (U).
Marginal (1-\alpha) coverage implies

\[
\Pr\!\left(U\cap\{\theta_0,\theta_1\in C(X)\}\right)\ge q-2\alpha,
\qquad
\Pr\!\left(\theta_0,\theta_1\in C(X)\mid U\right)\ge 1-\frac{2\alpha}{q}.
\]

This derives a conditional statement from marginal coverage and conditional observational equivalence; it does
not assume conditional coverage, and it is non-vacuous only for (q>2\alpha).

This yields a strict estimand fork:

- cover every legal-order response, and the target is a reachable-response union or, under explicitly matched
  uncertainty semantics, a robust set;
- cover the actually realized response, and a true scheduler/order law or equivalent identifying information is
  required.

The first has close robust-verification baselines, but exact calibrated-set equivalence still depends on the
uncertainty and coverage semantics; without those declarations the frozen target is underspecified. The second
violates the frozen rule against relying on the unknown true order law. The two-point calculation only prevents
shrinkage below the separation of an observationally indistinguishable pair; it is a standard
partial-identification bound, not a new rate theorem or a claim of high-probability coverage of the entire
identified range. E2 fails.

## 6. E3 — FAIL/RED

Let (g) be the declared decision. Create two copies of the finite legal-schedule graph. Decision invariance fails
exactly when their product reaches accepting states (z,z') with (D=D'=E) and (g(z)\ne g(z')). A positive
certificate is a relational invariant; a negative certificate is the pair of accepting paths. This is
observational determinism/product reachability. Confluence modulo the declared observation is one sufficient
proof technique, not an equivalent characterization; property-preserving POR supplies a standard reduction.

State-dependent enabledness does invalidate a *naive* local-swap proof, but does not create a new certificate. A
four-event FIFO interval-order example has legal schedules

\[
AXBY,\qquad ABXY,\qquad BAYX,
\]

where (A,B) add (a,b) and (X,Y) successfully execute heads (a,b). The first two form one legal-swap
component and fill (a) first; the third is isolated and fills (b) first. Any adjacent-swap route through the
full linear-extension graph crosses a disabled execution. Detecting the other component is precisely global
completion/reachability or linearizability checking.

Both complete schedules contain every block, so ordinary shortest-path length is vacuous. A useful optimized
witness needs a declared cost, such as the number of causal blocks or order reversals that distinguish the
decisions. Greedy single-block deletion yields at most a deletion-order-dependent 1-minimal witness because
enabledness makes the property non-monotone; true inclusion-minimality needs exhaustive checking or a proved
monotonicity condition. Related minimum-counterexample variants are known to be hard, but no hardness reduction
is claimed for an undeclared cost on this instance. No nonstandard complexity or statistical guarantee remains.
E3 triggers its renamed-model-checking kill rule.

## 7. Molecular-dynamics transfer — direct collision

[Halm and Posa (2024)](https://doi.org/10.1177/02783649241236860) start from almost the same scientific problem:
simulators cannot reliably predict the ordering of nearly simultaneous impacts and heuristically select one.
They instead construct a set-valued rigid-body model covering arbitrary relative impact ordering, prove solution
existence, dissipation and finite termination, and give an LCP-based randomized approximation of the complete
post-impact velocity set with probabilistic guarantees.

It does not solve a price--time book, but it occupies the transferable MD headline at the exact abstraction level.
“Apply the same principle to markets” could be a useful application, not a Nature-level method contribution.

## 8. Gate table

| Gate | Result | Reason |
|---|---|---|
| 40-plus primary-work matrix | PASS as an audit | 55 non-duplicated entries across all eight buckets |
| mathematical object | FAIL as frozen; repairable | static (pi) misses stochastic/state-dependent scheduling; flat poset cannot express atomic grouping |
| toy semantics | PASS as falsification | all four mandatory cases derived; they expose the intended failure modes |
| E1 | **FAIL/RED** | linearizability/reachability, DPOR, #LE and possible-world result sets |
| E2 | **FAIL/RED** | frozen semantics underspecified; natural finite variants have close PAC/robust-game baselines and only a standard pairwise non-identification bound |
| E3 | **FAIL/RED** | observational determinism/product reachability/confluence/counterexamples |
| dual-resolution metadata | **SKIPPED** | forbidden after mathematical exits fail |
| T0 | **FAIL/RED** | no eligible exit survives exact nearest-work reduction |

## 9. Scope and resource accounting

The stop rule was obeyed:

- no market price, return, queue response, event-window statistic or treatment effect was read;
- no dataset was purchased, downloaded or opened;
- no synthetic benchmark, EcoMD implementation, fit or training was performed;
- the exposed exp138 test split remained unopened as confirmation;
- GPU hours: 0; paid-data spend: 0; benchmark runs: 0.

The conditional metadata audit was not performed. Protocol documents were consulted only as prior-art/semantic
evidence needed to interpret atomicity and authoritative sequence; no source was qualified for a future benchmark.

## 10. What remains useful and what happens next

Preserve the queue cases, atomic-group lemma and enabledness-filtered connectivity counterexample as regression
tests for any future event-driven matching shell. The current repository limitation also remains real:
`strictify_timestamps` preserves row order and makes it strict, while the synthetic order identity contract lacks
persistent lifecycle, matching-engine and price--time-priority support. Those are engineering limitations, not a
publishable residual.

The selected card's planning survival and complete-package probabilities become zero because the card is closed.
Do not automatically promote hard-event gradients or combine this route with the previously failed observation-
quotient/coarse-graining cards. Return to problem selection with a new standalone scientific object; the next
screen should prefer an externally randomized or otherwise genuinely identified repeated protocol over another
conjunction of market semantics and existing concurrency theory.

Supporting artifacts:

- `papers/proposal/ecomd_partial_order_event_t0_prior_art_matrix_2026-08-23.md`;
- `papers/proposal/ecomd_partial_order_event_t0_math_scratch_2026-08-22.md`;
- `papers/proposal/ecomd_partial_order_event_t0_freeze_2026-08-22.md`.
