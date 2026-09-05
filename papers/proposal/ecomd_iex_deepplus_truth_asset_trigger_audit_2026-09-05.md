# EcoMD IEX DEEP+ truth-asset trigger audit

**Date:** 2026-09-05  
**Stage:** bounded D-3 re-entry-trigger audit; no candidate harvest  
**Archetype:** `measurement_method` / `empirical_intervention` boundary  
**Decision:** one `partial_capability`, one `not_trigger`, zero removed project blockers  
**Raw outcomes, data download, implementation, simulator, SSH and GPU access:** none

## Decision first

[IEX DEEP+](https://www.iex.io/products/equities/market-data-connectivity) is the
strongest newly identified public order-level US-equity truth asset in this search. It reports
OrderID, symbol, side, message timestamp, price and size for every *displayed* resting IEX order,
with amendments, cancellations and executions. IEX added DEEP+ to its free T+1 HIST product and
publishes binary PCAPs captured when the feed is disseminated. One DEEP+ tape can therefore provide
an exact nested pair: its order-level displayed state and the price-level aggregate obtained by
summing those orders.

That capability is useful, but neither obvious paper survives:

1. **L2-to-L3 microstate recovery or state-sufficiency.** Classical strong lumpability already
   states the exact Markov condition. Two direct 2026 works now occupy the market-specific exits:
   Bafarassat gives sharp queue-ahead and execution identified sets under market-by-price data,
   while Xiong defines projection fibres, task sufficiency and residual event-path information for
   L3 order books. LOB-Bench and *Painting the Market* additionally occupy generative evaluation
   and explicit L2/L3 model comparison. A paired IEX benchmark would be useful engineering, not an
   irreducible ICLR method.
2. **Rule 612 as prospective field validation.** The adopted rule assigns a $0.005 tick when a
   stock's three-month time-weighted average quoted spread is at most $0.015, but the SEC has now
   delayed compliance until the first business day of November 2027 and directed a further review
   of both the tick and access-fee rules. The reform remains bundled with a market-wide access-fee
   change, supplies one policy lineage, and IEX-only displayed L3 omits cross-venue adaptation and
   private participant state. It cannot support an ICLR 2027 experiment or remove the existing
   prospective-validity blockers.

The DEEP+ launch and later real-time fee are not a rescue. Access was optional; the official filing
reports usage categories but no subscriber identities, adoption path or untreated subscriber
cohort. Older SuperMontage and Shanghai subscription studies directly occupy the transparency-shock
question. The rolling twelve-month HIST window also means that a durable launch-era archive would
have needed to be pinned prospectively.

The correct decision is to retain IEX DEEP+ as a high-quality watch-listed measurement asset, close
the microstate-lifting formulation as a duplicate/direct collision, and leave Rule 612 on a 2027+
watch condition. No topic card, experiment plan or worker launch is scientifically authorized.

## 1. Scope and outcome-blindness

This is a blocker-specific trigger audit under the saturated-family rule. It is not Cycle 17 and
does not harvest a new portfolio. It tests whether DEEP+ or the updated Rule 612 schedule removes a
named blocker from:

- `l2_order_identity_lumpability_taxonomy`;
- `observation_quotient_response`;
- `interventional_lob_fidelity_benchmark`;
- `task_conditioned_market_simulator_adequacy`;
- `sec_halfpenny_abides`; or
- `prospective_counterfactual_market_simulator_validity`.

Only official product pages, specifications, SEC filings and primary-work abstracts were examined.
No PCAP was downloaded, no row or market outcome was opened, and no EcoMD or remote-compute action
was taken.

## 2. Frozen market-native question

**Object.** The identities, sizes, ages and ordering of displayed resting orders within an IEX
price level, together with their price-level aggregate.

**Rival explanations.** Under H1, the aggregate displayed book and its history are sufficient for a
declared future task, so order identity and queue composition add no task-relevant information.
Under H2, distinct order-level states inside one aggregate fibre have different cancellation,
execution, fill or price-response laws.

**Discriminating result.** For a predeclared task and horizon, compare the true conditional law
given the order-level filtration with the law given the projected price-level filtration. A valid
positive result requires out-of-sample information that remains after identical clocks, symbols,
history length and model capacity are controlled. A null requires an equivalence or upper bound,
not failure to reject with an underpowered predictor.

**Value of either sign.** A positive result quantifies which tasks cannot be validated from L2; a
null result can certify a narrower task-specific aggregation. Neither sign, however, is novel by
itself. The contribution must survive the exact-parent and direct-collision tests below.

## 3. What DEEP+ actually identifies

### 3.1 Exact displayed-book capability

The 2024 SEC product filing states that DEEP+ disseminates order-by-order information for all
displayed resting orders and updates an order upon amendment, cancellation and execution. The
corresponding HIST filing places the same substantive data in the historical product and records a
December 9, 2024 launch. IEX's current resources list DEEP+ specification v1.02 and sample PCAPs.
The historical page says the binary feed output is captured at dissemination and named by transport
and feed-specification versions.

For the displayed order book, define

\[
  Z_t(p,s)=\sum_{i:\,P_i(t)=p,\,S_i=s} Q_i(t),
\]

where an active DEEP+ OrderID indexes each displayed order. This gives a deterministic same-tape
projection from order-by-order state to price-level depth. It avoids the clock, universe and vendor
alignment errors that arise when separately purchased L2 and L3 products are paired.

The current HIST product is free on T+1 under specific terms, not an open-license dedication. The
terms require attribution, preserve IEX's proprietary rights and disclaim completeness and fitness.
The product page exposes only the most recent twelve months. A reproducible study therefore needs a
dated immutable file manifest, hashes, retained specifications and a release-rights review before
the source window rolls away.

### 3.2 It is not complete L3 market state

IEX explicitly excludes non-displayed orders and the non-displayed portions of reserve orders from
both DEEP and DEEP+. Last-sale messages can include executions against non-displayed interest, but
that does not reveal the hidden pre-execution queue. Routed executions are omitted. OrderID is an
order-lifecycle key, not a participant owner, inventory, intent or policy label. The feed also does
not contain other venues' books, routes or latencies.

Consequently, two full states can agree on every displayed DEEP+ message while differing in hidden
and reserve interest, off-venue inventory and adaptive routing policies. They may then produce
different responses to the same new order or rule. DEEP+ is exact truth for the *displayed IEX
projection*, not an oracle for the complete Markov state or for field counterfactuals.

## 4. Exact reduction and direct collision

### 4.1 Markov aggregation is strong lumpability

Let a continuous-time microstate chain have generator `q`, and let `pi` map order-level states to
price-level states. The projected state is Markov for every initial law only if, for every pair
`x,x'` in the same fibre and every aggregate cell `B`,

\[
  \sum_{y\in B} q(x,y)=\sum_{y\in B} q(x',y).
\]

This is the classical strong-lumpability rate-to-cell criterion already recorded in
`l2_order_identity_lumpability_taxonomy`. FIFO age, targeted cancellation and owner-dependent
policies give immediate counterexamples. Measuring the size of an empirical violation can be
useful, but does not create a new aggregation theorem.

### 4.2 Sharp execution bounds are now a direct collision

[Bafarassat (2026)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7299999)
starts from the exact missing-order-identity problem. It derives a sharp interval recursion for
unfilled queue-ahead volume under market-by-price observations and propagates it to fill, value,
policy-dominance and regret bounds, then checks the bounds by masking Nasdaq order identities. An
IEX implementation of the same queue filter would be replication, not a distinct ICLR thesis.

[Xiong (2026)](https://papers.ssrn.com/sol3/Delivery.cfm/7082878.pdf?abstractid=7082878&mirid=1&type=2)
uses the same L3-to-depth mapping and explicitly defines projection fibres, task sufficiency, fibre
variation, residual event-path information and queue-ahead fragility. This directly occupies the
obvious theorem/measurement language for “what L2 loses.” Both works are recent preprints rather
than settled final authority, but their exact subject overlap makes a novelty claim unsafe.

### 4.3 Generative lifting is also insufficient

A learned posterior over order-level paths conditional on aggregate history is a missing-state or
coarsened-observation model. Paired IEX tapes can score samples against displayed truth, but:

- the posterior is task- and assumption-dependent rather than a unique inverse of the projection;
- reproducing one hidden displayed realization is not necessary for every aggregate-level task;
- displayed DEEP+ still omits the actual hidden market state; and
- cross-venue generalization is not supplied by a single IEX engine.

LOB-Bench already provides conditional and unconditional distributional evaluation of generative
message-by-order models. [*Painting the Market*](https://arxiv.org/abs/2509.05107) explicitly
compares Level-2 and Level-3 inputs within that benchmark. A new architecture, diffusion imputer or
multiresolution consistency loss without a new identification or sample-complexity result would be
an incremental model paper in a crowded neighborhood.

## 5. DEEP+ launch and fee as an information intervention

There are two dated events: DEEP+ became available on December 9, 2024, initially free; real-time
access changed to $3,500 per month on October 1, 2025. The fee filing reports that approximately 88%
of then-current subscribers used the feed for non-display purposes. This confirms that the feed was
economically relevant to algorithmic users, but it does not identify exposure.

The key missing variables are the subscriber count, subscriber identities, connection/use dates,
actual cancellations after the fee, and a non-subscriber cohort subject to the same market state.
Subscription is optional and chosen for business reasons. A before/after IEX comparison therefore
mixes selection, secular market changes and any simultaneous IEX changes; other exchanges are not
same-estimand controls because they have different rulebooks, order populations and information
products.

The broad transparency question is also mature. Chung and Chuwonganant study market quality around
Nasdaq SuperMontage's increase in displayed depth, and He et al. use Shanghai software subscriptions
to estimate a nonlinear liquidity response to transparency. The IEX event lacks the latter paper's
subscriber-dose variable. A generic difference-in-differences or neural causal estimator would not
repair missing treatment exposure or create an ICLR contribution.

**Gate:** DEEP+ is a truth asset, but its launch/fee is not a qualified assigned intervention.

## 6. Rule 612 branch

The 2024 final rule is unusually explicit: for NMS stocks priced at least $1, a three-month TWAQS
at or below $0.015 assigns a $0.005 tick; otherwise the tick is $0.01. Assignment is recomputed
semiannually for a six-month operative period. In principle this creates a prospective threshold
design and a market-native action that a simulator could implement.

Four hard failures remain:

1. On June 11, 2026, the SEC extended temporary relief for Rules 600(b)(89)(i)(F), 610(c) and 612
   until the first business day of November 2027. The Chairman also directed staff to review Rules
   610(c) and 612, including whether their tick and access-fee parameters should change. The action
   and assignment are therefore not currently frozen.
2. The tick and access-fee-cap changes are deliberately linked. They alter quoting, routing and
   maker-taker economics together, so the field response cannot be attributed to tick size alone.
3. The deterministic TWAQS threshold is not randomization. A regression-discontinuity claim would
   need a frozen running-variable construction, continuity and no-manipulation arguments, bandwidth
   and density diagnostics, and a treatment that is not simultaneously bundled.
4. DEEP+ observes displayed orders on IEX only. The reform is national; response includes routing
   and liquidity migration across exchanges. One policy event, even across many securities, is one
   intervention family rather than independent replication.

The asset therefore improves the earlier `sec_halfpenny_abides` record only on one measurement
dimension. It does not remove that route's implementation, unbundling, simulator-bridge or
replication blockers, and its timing is incompatible with an ICLR 2027 empirical submission.

## 7. Trigger decisions

| Capability claim | Truth/data | Identification | Novelty | Replication | Decision |
|---|---:|---:|---:|---:|---|
| Paired displayed L3/L2 truth reopens microstate lifting | pass | fail for complete state | fail: exact/direct parents | fail: one engine | `partial_capability`; zero blockers removed |
| Rule 612 plus IEX L3 reopens prospective simulator validity | partial | fail: delayed, reviewed, bundled | existing tick and validation parents | fail: one rule family | `not_trigger` |

No graph node is added. The microstate question maps to existing closed aggregation,
observation-quotient and LOB-fidelity nodes; Rule 612 maps to the existing half-penny and
prospective-validity nodes. Creating renamed descendants would violate the saturation rule.

## 8. Exact re-entry conditions

Re-audit the paired-resolution route only if all of the following appear together:

- an immutable lawful archive with a frozen displayed-order projection and durable release rights;
- a second independently governed order-level matching-engine lineage under the same task estimand;
- a theorem, estimator or calibrated abstention result not expressible as lumpability, projection
  fibres/task sufficiency, sharp queue partial identification, generic latent-state inference or
  existing LOB benchmarks; and
- an independently defined response truth or assigned action, rather than reconstruction accuracy
  alone.

Re-audit Rule 612 only after the final rule, compliance date, assignments and common simulator
action adapters are frozen *before* outcome access, and only with complete cross-venue prestate,
several independently governed intervention families and an untouched confirmation partition.

## 9. Compute and data disposition

- `root@100.113.230.38` (A800 40 GB): untouched.
- `root@100.80.236.112` (V100 32 GB): untouched.
- `root@100.123.220.57` (V100 32 GB): untouched.
- IEX HIST PCAPs: not downloaded.
- EcoMD code/configuration: unchanged.
- Topic card and experiment plan: not created.

This is a scientific stop, not a resource limitation. More GPU seeds cannot resolve a direct prior
collision, an omitted state, an unfrozen policy or a missing independent intervention family.
