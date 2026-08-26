# EcoMD Discovery Loop topic cycle 3: capability-first on-chain market screen

**Date:** 2026-08-25
**Scope:** simulated markets, market physics, and financial physics
**Stage:** D-3/D-2 source-, theorem-, and truth-contract screening
**Literature cutoff:** 2026-08-25
**Outcome access:** none; no market outcome, simulator output, sealed split, paid asset, or sandbox result was opened
**Decision:** zero machine topic cards, zero D-1 candidates, and zero execution authorizations

## 1. Decision

The third bounded cycle did not begin from another analogy. It first searched for a new
scientific capability: an open market mechanism whose executable state is public, whose
implementation is versionable and replayable, and whose intervention can be represented in
two independent engines. The search focused on on-chain central-limit-order books because
they expose owner-labelled orders, balances, matching code, and deterministic settlement
more completely than anonymous exchange feeds.

The strongest near miss was **shared-capital global orders**. Manifest lets one deposited
token balance back displayed orders in many markets and removes an order when the balance can
no longer support it. Mangrove lets one wallet or strategy advertise the same funds across
markets and either retract sibling offers or pay a bounty when an offer fails. This is a real,
nonlocal conserved-resource coupling: one fill can change another market's executable
liquidity without changing its previously displayed quantity.

That object nevertheless fails the Nature-grade gate. With fixed offers and a fixed arrival
stream, it is exactly sequential online resource allocation or a loss network. With arbitrary
Mangrove offer code, the response can encode an arbitrary state-dependent policy; complete
code and state make exact execution the oracle, while incomplete dependencies make the
response unidentifiable. Manifest and Mangrove also implement materially different failure,
cleanup, funding, execution, and scheduling semantics. Finally, duplicated-then-cancelled
liquidity across venues is already directly documented in market data.

Seven related capabilities also failed: bonded promises, deferred-settlement backlog,
lazy-expiry maintenance debt, regenerative reverse orders, tickless priority inversion,
global-account lock contention, and executable order programs. Their conservative hostile-T0
lower bounds were 1--5%; the largest upper bound was 17%. This cycle therefore creates no
`candidate`, `parked`, `active`, topic card, or disposable sandbox. It authorizes no
implementation, simulation, outcome access, chain query, data download or purchase, external
outreach, EcoMD edit, or GPU work.

## 2. Frozen capability-first contract

Every worksheet used the same five-part discovery object

\[
(X,\operatorname{do}(A),Y,H_1\!:\!H_0,T),
\]

but capability had to precede the physics claim:

1. `X` had to be native, owner-labelled, versioned state sufficient for deterministic replay;
2. `do(A)` had to be an admissible protocol action, not a latent-agent edit;
3. `Y` had to be invariant to order splitting, token decimals, event grouping, and labels;
4. the mechanism had to survive a finite killer and an exact parent-problem reduction;
5. `T` had to name two independent implementations of the same estimand and a prospective
   external check; and
6. an implementation became eligible only if the hostile-T0 lower bound was at least 15%.

The frozen source family was Manifest at commit
`bad2e6bb16ebb35349a373083933bb2f9fcd6354`, Mangrove Core at
`6fa9a5716753e577f127d1b1511304add0b386eb`, OpenBook v2 at
`f3e17421e675b083b584867594bf3cf4f675d156`, and Phoenix at
`5a34f7f901fd9e04057198d4fc7b7286f78b53f2`. Source inspection was read-only. A shared label
such as “order book,” “global order,” or “crankless” was not accepted as semantic equivalence.

## 3. Results matrix

| Worksheet | Native capability | Hostile T0 lower/point/upper | Terminal result |
|---|---|---:|---|
| Shared-capital global-order exclusion | one balance supports offers in several markets | 5/10/17% | fixed policy is online packing/loss-network allocation; programmable policy is arbitrary |
| Bonded executable-liquidity promises | unbacked offers prepay cleanup or failure compensation | 3/7/12% | performance-bond mechanism with hidden success policy; no common bond semantics |
| Deferred-settlement event-heap backpressure | fills create bounded maker-state work consumed by a crank | 2/5/10% | finite-buffer workload queue; Phoenix and Manifest remove rather than reproduce the state |
| Lazy-expiry matching maintenance debt | expired records consume bounded matching or cleanup work | 1/4/8% | lazy deletion under engine-specific budgets; no common response law |
| Regenerative reverse-order lattice | a fill flips or reposts a dual order using proceeds | 3/7/13% | grid-trading/birth-death strategy whose behavior is determined by external order flow |
| Tickless priority inversion | arbitrarily small price improvement jumps time priority | 1/4/8% | sub-penny queue-jumping and coordinate precision, not a new collective phase |
| Global-account lock contention | shared writable balance serializes otherwise separate markets | 2/6/12% | generic runtime scheduling; losing/nonincluded demand is not in the public ledger |
| Programmable-offer liquidity oracle | an order is an executable contract rather than locked stock | 1/4/9% | complete program is the oracle; incomplete external state is nonidentified |

No row passed all of exact novelty, same-estimand engines, public opportunity state,
prospective confirmation, and the 15% lower-bound gate.

## 4. Shared-capital global-order exclusion

- **State `X`:** token balances `b_r`, owner-labelled offers `e`, their requested resource
  amounts `a_{er}`, prices, priority, expiry, and the protocol's cleanup state.
- **Intervention `do(A)`:** place the same resource-backed offer on one additional market,
  or change only the allowed reuse degree while holding total owned capital fixed.
- **Response `Y`:** displayed-to-executable depth, the market receiving the next fill,
  cross-market removal, slippage, and cleanup work.
- **`H1`:** conservation creates a market-native nonlocal exclusion law that predicts
  cross-market liquidity failure beyond ordinary depth and order flow.
- **`H0`:** requests arrive sequentially and consume limited capacity; this is online
  packing/loss-network allocation, followed by arbitrary maker policy when replenishment is
  admitted.
- **Truth `T`:** Manifest exposes the global deposit and order state on Solana; Mangrove
  exposes offers and contracts on EVM, but the two systems do not share one execution grammar.

For one resource of balance `B` and fixed offers of sizes `a_e`, an arrival sequence
`e_1,e_2,...` succeeds exactly while the cumulative accepted consumption is at most `B`.
The decision to accept, skip, or remove an offer is therefore a sequential knapsack or
resource-allocation policy. With several resources it becomes online packing; with stochastic
arrivals and holding times it lies in the loss-network family. Price-time priority changes
the request order, not the parent problem.

Two finite killers fix the claim's scope. First, let `B=1` and display one unit in markets A
and B. An A-then-B arrival allocates the unit to A; B-then-A allocates it to B. Conservation
alone determines no venue-independent response. Second, compare locked local orders with a
shared global balance while preserving both displayed books. The first fill affects the
other market only in the shared system, which identifies the protocol feature but supplies
no scaling law beyond the known capacity constraint.

Manifest's own whitepaper defines the mechanism, warns that unfillable orders can remain,
and specifies prepaid removal. Mangrove documents amplified orders that reuse one wallet's
funds across markets and contract logic that either retracts a sibling or lets it fail with
a bounty. Degryse et al. already show that duplicated orders and swift cancellation make
consolidated displayed liquidity differ from realizable liquidity in fragmented markets.
Collateral-reuse models already cover the broader leverage and volatility channel.

**Close at 5/10/17%.** Reopen only with a theorem forced by a protocol invariant that fails
for general online packing/loss networks, remains meaningful under order and token-unit
refinement, and is implemented with the same action/failure semantics in two independent
engines. A field claim additionally needs complete failed-attempt exposure and a frozen
prospective intervention; successful on-chain transactions alone are insufficient.

## 5. Bonded executable-liquidity promises

- **State `X`:** displayed promise, executable backing, offer program, gas estimate,
  provision/bounty, cleanup prepayment, and taker cost.
- **Intervention `do(A)`:** change only the bond or prepaid cleanup amount.
- **Response `Y`:** failure frequency, taker loss, stale-book residence, and cleanup effort.
- **`H1`:** bonding yields a universal reliability--capital-efficiency frontier for
  executable liquidity.
- **`H0`:** it is a performance bond priced against gas, while success remains an arbitrary
  maker-program outcome.
- **Truth `T`:** Mangrove pays a bounty when a smart offer fails; Manifest prepays removal of
  unbacked global orders. The triggering event and payment recipient are not the same.

Equal displayed depth and equal bond can attach to one contract that always sources tokens
and another that deliberately fails. Conversely, two identical offer programs can have
opposite cleanup outcomes under different gas prices or taker account sets. Thus bond and
book state do not determine executable liquidity. A bond large enough to reimburse gas
protects a taker from one cost; it does not force price, depth, or reliability dynamics.

**Close at 3/7/12%.** Reopen only with one common bond semantics, a restricted strategy class
that yields a nontrivial tight frontier rather than assuming a failure law, two conformant
implementations, and complete attempts rather than successful fills alone.

## 6. Deferred-settlement event-heap backpressure

OpenBook v2 separates matching from some maker-account updates. Its pinned source fixes an
event heap of 600 records, asserts on insertion into a full heap, processes at most eight
events per `consume_events` instruction, and processes only a bounded number of maker fill
accounts inline. This creates a genuine workload state.

- **State `X`:** full event heap, owner accounts, book, matching sequence, crank arrivals,
  compute budget, and remaining-account set.
- **Intervention `do(A)`:** change only crank service or inline maker-account coverage.
- **Response `Y`:** backlog, transaction reversion, settlement delay, and executable volume.
- **`H1`:** settlement debt creates a new liquidity-jamming transition.
- **`H0`:** it is a finite-buffer queue whose arrival and service rates are chosen by flow
  and crank policy.
- **Truth `T`:** Phoenix and Manifest are crankless/atomic comparators, not second native
  implementations of the OpenBook workload.

The full heap plus future arrival/service processes is an ordinary bounded workload queue.
Equal heap length can contain owners supplied in the next transaction or owners that remain
unavailable, producing different service; heap length alone is not Markov. Adding the event
records, account set, and crank policy closes the queue but removes the claimed new physics.
Phoenix's atomic settlement and Manifest's packed market state eliminate the same deferred
state rather than reproduce it.

**Close at 2/5/10%.** Reopen only with a market-specific theorem not implied by finite-buffer
queueing, a second implementation of the same deferred maker-settlement grammar, and a lawful
record of attempted transactions that failed when the heap was full.

## 7. Lazy-expiry matching maintenance debt

The three Solana engines expose different expiry semantics. OpenBook walks invalid orders but
drops at most five during matching. Phoenix removes an expired top order and decrements the
incoming order's `match_limit`. Manifest skips expired orders when quoting and removes them
during executable matching. These are useful conformance fixtures, but not one estimand.

Two books can contain the same count and total quantity of expired orders while placing them
at the best price or deep in the tree; only the former consumes immediate matching work.
Two engines can begin from the same ordered records yet return different fills because one
charges expiry removal to the match limit and another uses a separate cleanup cap. Full
record position and implementation semantics explain the response as bounded lazy deletion.

**Close at 1/4/8%.** Reopen only if two engines share identical expiration, priority,
compute, and budget semantics and a new bound survives record splitting and tree layout. A
denial-of-service or conformance result should be submitted as systems/security work, not
renamed market physics.

## 8. Regenerative reverse-order lattice

Manifest reverse orders flip a filled buy into a sell, or a sell into a buy, using the
proceeds and a configured spread. A series is explicitly designed to reproduce discretized
concentrated liquidity. Mangrove Kandel places a geometric grid and reposts a dual offer after
a fill.

- **State `X`:** the grid, inventory, active side at each point, spread/step size, priority,
  and external taker flow.
- **Intervention `do(A)`:** enable automatic flip/repost while holding the initial grid and
  capital fixed.
- **Response `Y`:** inventory occupation, cycle current, boundary residence, realized
  spread, and recovery after one-sided flow.
- **`H1`:** interacting regenerative orders have a new stationary phase or transport law.
- **`H0`:** under fixed taker flow they are grid-trading birth--death processes; under
  adaptive flow the kernel is strategy-dependent.
- **Truth `T`:** Manifest and Kandel are independent implementations, but their proceeds,
  partial-fill, provision, grid, and repost semantics differ.

Alternating buy/sell flow can make one order cycle forever, while one-sided flow sends the
same rule to a boundary. Hence regeneration alone implies neither stationarity nor a current.
Assuming a stationary exogenous flow makes the desired invariant measure a standard Markov
chain calculation; allowing strategic flow removes universality. Both protocols already
describe the AMM/grid interpretation.

**Close at 3/7/13%.** Reopen only with a native interaction theorem not reducible to grid
trading, birth--death chains, or a discretized AMM, plus an exact cross-engine mapping and a
prospective path-law test frozen before chain outcomes.

## 9. Tickless priority inversion

Manifest explicitly notes that tickless pricing lets the most recent order obtain priority
through a negligible price improvement. The proposed response was queue displacement and
near-mid liquidity under progressively finer price units.

The result is not invariant. Changing token decimals, wrapper rounding, minimum notional, or
economic price precision changes how many nominal improvements fit inside the same spread.
Once price improvement and time priority are specified, the next allocation is ordinary
lexicographic matching. Sub-penny queue-jumping and its market-quality effects are already a
direct microstructure topic.

**Close at 1/4/8%.** Reopen only with a token/numeraire-invariant observable and a theorem
beyond sub-penny priority, plus two independent tickless engines and a clean precision
assignment. Do not infer a phase transition from a coordinate-dependent count of price steps.

## 10. Global-account lock contention and liquidity

Manifest global orders require shared writable account state. Solana can execute unrelated
transactions in parallel but serializes conflicting writes; Manifest itself lists global
lock contention and transaction landing as an open engineering question.

- **State `X`:** complete submitted transaction set, writable-account graph, priority fees,
  scheduler, leader, and program compute.
- **Intervention `do(A)`:** route otherwise identical orders through a shared global account.
- **Response `Y`:** landing probability, latency, failures, and subsequent book state.
- **`H1`:** capital sharing produces a measurable market-wide congestion externality.
- **`H0`:** this is generic transaction scheduling and account-lock contention.
- **Truth `T`:** confirmed chain history omits the complete set of dropped, replaced, and
  privately forwarded attempts needed for the denominator.

Identical confirmed transactions can arise from a quiet submission window or from heavy
competition in which most attempts never land. The on-chain outcome therefore does not
identify contention exposure. A local validator can impose a workload but would test a
chosen scheduler, not a field law. Mangrove's EVM execution does not provide an independent
copy of Solana account-lock semantics.

**Close at 2/6/12%.** Reopen only with complete public or randomized submission exposure,
two scheduler implementations for the same lock graph, and a theorem that is not generic
parallel scheduling or queueing.

## 11. Programmable-offer liquidity oracle

Mangrove offers can point to arbitrary contracts that source liquidity just in time, apply a
last look, repost, or fail. This creates a rich simulator substrate but a sharp scientific
dichotomy.

If bytecode, called contracts, balances, oracle inputs, block context, and ordering are all
known, the chain's deterministic execution is the exact response oracle. A learned EcoMD
surrogate can be useful for speed but is not a new discovery target. If any dependency,
private transaction, or external state is missing, two worlds can show the same order and
book while one fulfills and the other fails. Further, unrestricted offer programs can encode
arbitrary finite-state dynamics, so no universal liquidity law follows from programmability.

**Close at 1/4/9%.** Reopen only after restricting the program class by a market-native
invariant that yields a theorem beyond program reachability, conformance, or surrogate
execution, and after obtaining a second runtime with the same contract and complete state.

## 12. Primary and official source manifest

The screen used the following primary or official records. They cover implementations,
direct market mechanisms, parent mathematics, empirical identification, and negative
neighborhoods; inclusion does not assert that every item is an exact reduction.

1. Manifest source, pinned commit: https://github.com/Bonasa-Tech/manifest/tree/bad2e6bb16ebb35349a373083933bb2f9fcd6354
2. Manifest, *The Orderbook Manifesto*: https://www.manifest.trade/assets/The_Orderbook_Manifesto.pdf
3. Manifest global-order matching source: https://github.com/Bonasa-Tech/manifest/blob/bad2e6bb16ebb35349a373083933bb2f9fcd6354/programs/manifest/src/state/market.rs
4. Manifest global-balance source: https://github.com/Bonasa-Tech/manifest/blob/bad2e6bb16ebb35349a373083933bb2f9fcd6354/programs/manifest/src/state/global.rs
5. Mangrove Core, pinned commit: https://github.com/mangrovedao/mangrove-core/tree/6fa9a5716753e577f127d1b1511304add0b386eb
6. Mangrove protocol introduction: https://docs.mangrove.exchange/dev/protocol/introduction
7. Mangrove amplified-order contract: https://docs.mangrove.exchange/dapp-guide/trade/how-to-make-an-order/amplified-order
8. Mangrove amplified-liquidity implementation guide: https://docs.mangrove.exchange/dev/strat-lib/guides/creating-a-direct-contract
9. Mangrove offer provisions and bounties: https://docs.mangrove.exchange/mangrove-core/technical-references/taking-and-making-offers/reactive-offer/offer-provision
10. Mangrove Kandel regeneration semantics: https://draft.docs.mangrove.exchange/general/kandel/how-does-kandel-work/step-by-step-visual-explanation
11. OpenBook v2 source, pinned commit: https://github.com/openbook-dex/openbook-v2/tree/f3e17421e675b083b584867594bf3cf4f675d156
12. OpenBook event heap: https://github.com/openbook-dex/openbook-v2/blob/f3e17421e675b083b584867594bf3cf4f675d156/programs/openbook-v2/src/state/orderbook/heap.rs
13. OpenBook event consumption: https://github.com/openbook-dex/openbook-v2/blob/f3e17421e675b083b584867594bf3cf4f675d156/programs/openbook-v2/src/instructions/consume_events.rs
14. OpenBook matching and expiry cleanup: https://github.com/openbook-dex/openbook-v2/blob/f3e17421e675b083b584867594bf3cf4f675d156/programs/openbook-v2/src/state/orderbook/book.rs
15. Phoenix source, pinned commit: https://github.com/Ellipsis-Labs/phoenix-v1/tree/5a34f7f901fd9e04057198d4fc7b7286f78b53f2
16. Phoenix FIFO matching and expiry source: https://github.com/Ellipsis-Labs/phoenix-v1/blob/5a34f7f901fd9e04057198d4fc7b7286f78b53f2/src/state/markets/fifo.rs
17. Degryse et al., *Duplicated Orders, Swift Cancellations, and Fast Market Making in Fragmented Markets*: https://doi.org/10.1287/mnsc.2023.01789
18. Kelly, *Loss Networks*: https://www.statslab.cam.ac.uk/~frank/PAPERS/loss.html
19. Jiang and Zhang, *Online Resource Allocation with Stochastic Resource Consumption*: https://arxiv.org/abs/2012.07933
20. Brumm et al., *Re-use of collateral: leverage, volatility, and welfare*: https://doi.org/10.1016/j.red.2022.03.003
21. Buti et al., *Sub-Penny and Queue-Jumping*: https://doi.org/10.2139/ssrn.2350424
22. Lin, *The Effect of DLT Settlement Latency on Market Liquidity*: https://www.world-exchanges.org/storage/app/media/Cally%20Billimore/Crypto%20Settlement%20Latency_WFE.pdf
23. Solana official account-concurrency guidance: https://solana.com/developers/courses/program-optimization/program-architecture
24. Budish, Cramton and Shim, *The High-Frequency Trading Arms Race*: https://doi.org/10.1093/qje/qjv027

## 13. What this cycle changes

The cycle adds a capability-first fork to the Discovery Loop:

1. **Resource-program dichotomy.** Freeze offer policy and reduce shared capital to online
   allocation; unfreeze arbitrary program logic and demand a restricted invariant before
   discussing universality.
2. **Execution denominator gate.** A confirmed public ledger can reconstruct successful
   state transitions but usually not all submitted, dropped, private, or replaced attempts.
   It cannot identify landing or failure probabilities without that denominator.
3. **Same-estimand means same debt semantics.** A crank queue, atomic settlement, synchronous
   removal, bounty-bearing failure, and prepaid cleanup are different mechanisms, not four
   replications of “on-chain order books.”
4. **Capability can be reusable without being a topic.** Manifest, Mangrove, OpenBook, and
   Phoenix are valuable exact conformance and counterexample fixtures. Their availability
   does not make a generic queue, packing, grid, scheduling, or program-analysis result new.

The next search should not enumerate more on-chain order types. It should start only when a
new input supplies either (a) a theorem forced by a native conservation/priority rule that
provably escapes online allocation and program semantics, or (b) a prospective asset with
complete assignment, opportunity exposure, two same-estimand engines, and a sealed holdout.
Until then, the scientifically correct output remains zero cards.
