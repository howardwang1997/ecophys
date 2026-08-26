# EcoMD Discovery Loop topic cycle 9: asset portfolio and probability-gate audit

**Date:** 2026-08-26
**Scope:** simulated markets, market physics, and financial physics
**Stage:** D-3/D-2 asset-triggered screening and governance audit
**Literature cutoff:** 2026-08-26
**Outcome access:** none; only official rules, schemas, source descriptions, and primary papers
**Decision:** passed-and-closed cycle; eight formulations screened, zero topic cards, one prospective bridge forecast retained

## 1. Why this cycle was different

Cycle 9 did not begin from another physics analogy. It began from newly available or scheduled
truth assets and asked which market-simulator question each asset could actually adjudicate. In
parallel, it audited the Discovery Loop's fixed requirement that an `active` route have a
conservative hostile-T0 lower bound of at least 15%.

The audit separates three propositions that had previously been conflated:

1. a claim is scientifically false or occupied;
2. a proposed next action is not worth its cost; and
3. a route is not yet strong enough for expensive D0/D1 activation.

Only the third proposition is encoded by the 15% floor. A direct prior, counterexample,
non-identification proof, unlawful asset, or impossible same-estimand contract can terminalize a
formulation. A probability estimate below 15% cannot do so by itself. Cheap paper, source, schema,
or theorem work should instead be selected by its expected decision value.

## 2. Audit of the 15% lower-bound rule

### 2.1 What the probability means

`hostile T0` is now defined as the probability that one frozen formulation survives every named
T0 gate and becomes *eligible* for an outcome-blind active decision. It is not the probability of
an attractive plot, a positive result, acceptance by NMI/NCS, or eventual scientific truth. Venue
probability remains a separate estimate conditional on T0 survival.

The interval is an elicited epistemic forecast. The lower endpoint is deliberately conservative,
but it is not a frequentist confidence bound and currently has no empirical coverage guarantee.
Calling it a bound without this qualification would overstate its statistical meaning.

### 2.2 What the recent history says

The eight bounded topic cycles before this one screened 48 formulations. Forty-seven were in
machine-readable result tables and the shared-capital trilemma was the forty-eighth. Among the 47
tabulated intervals:

- median lower endpoint: 1%;
- largest lower endpoint: 6%;
- median point estimate: 4%;
- largest point estimate: 12%;
- lower endpoints at or above 15%: 0;
- upper endpoints at or above 15%: 5.

These are post-audit judgments, not preregistered forecasts, so they cannot calibrate the floor.
They do show that a 15% lower-endpoint rule is extremely selective in the present search regime.
Crucially, every one of the 48 formulations also failed an independent hard gate. Lowering the
floor would therefore not have activated a scientifically qualified route.

### 2.3 Decision-theoretic result

A fixed probability cutoff is not a general rule for whether information is worth buying. Let
`B` be the value if T0 is survived, `S` the reusable salvage value if it fails, `C` the cost of the
next action, and `p_L` the conservative probability. When `B > S`, a simple robust net-value check
is

\[
S + p_L(B-S) - C > 0,
\]

or equivalently \(p_L > (C-S)/(B-S)\). The threshold changes with cost and salvage. For an
information-gathering action, the relevant quantity is expected value of sample information:
whether the action is expected to change a downstream decision enough to justify its cost. Classic
value-of-information theory makes exactly this dependence on payoffs, diagnosticity, priors, and
study cost explicit.

The governance consequence is:

- retain 15% as a **provisional, uncalibrated full-activation heuristic** for costly D0/D1 work;
- use no probability floor for D-3 framing or D-2 paper/source search;
- authorize bounded D-1 or DX work only when its named uncertainty has positive robust information
  value and no hard gate has already failed;
- never use probability alone to set `failed_closed`; and
- review, calibrate, replace, or make the floor action-specific only after at least 20 genuinely
  prospective forecasts resolve under one stable target definition.

A new append-only forecast ledger starts with one prospective Rule 605 bridge gate. Historical
probabilities remain explicitly unscored rather than being backfilled as if they were forecasts.
The Rule 605 entry is a component-gate forecast and does not count toward the twenty comparable
full-T0 resolutions required before reviewing the activation floor.

## 3. Eight asset-triggered formulations

| Formulation | Native asset and proposed scientific object | Decisive hard failure | Hostile T0 lower / point / upper | Decision |
|---|---|---|---:|---|
| Expanded Rule 605 execution-tail truth bridge | First amended monthly execution-quality reports; predict order-type/size-conditioned execution speed, effective spread, and price-improvement cells from a simulator | Monthly reporter aggregates mix customer composition, routing, internalization, and venue response; the rule itself warns that the reports alone are not a reliable best-execution basis, and proprietary order-level work finds economically important information omitted by Rule 605 | 6 / 13 / 24% | current same-estimand formulation closed; future reports retained as a watch asset |
| Laboratory information-filtration relaxation | Randomized Black-Box versus Open-Book feedback in controlled CDAs; relaxation time and overshoot toward competitive equilibrium | The source papers already study convergence and information feedback, all source outcomes are published, and the nominally independent experiment changes the learning task and market grammar rather than replicating one intervention | 5 / 10 / 18% | closed |
| Treasury central-clearing network quench | December 2026 cash and June 2027 repo mandates; bilateral-to-CCP network rewiring, netting, margin liquidity, and stress propagation | Systemwide anticipated compliance is not an orthogonal assignment; public data do not expose the bilateral exposure, margin, membership, and rejected-funding state; central-clearing liquidity, netting, concentration, and network-risk effects are mature direct priors | 3 / 8 / 16% | closed |
| Uniswap-v4 fee-family relaxation | Onchain family-based protocol-fee activation and dynamic-fee hooks; LP migration and nonlinear feedback | Protocol fee, trader-facing dynamic fee, hook logic, routing, and adoption are different treatments; optimal dynamic fees and a pre-specified causal study of Uniswap protocol-fee changes directly occupy the broad theoretical and empirical claims | 2 / 6 / 13% | closed |
| Solana 60M-to-100M compute-capacity quench | SIMD-0286 single block-CU limit change; finite-capacity inclusion, latency, and priority-fee response | The change was live before formulation, landed blocks omit dropped/private/replaced demand, writable-account bottlenecks remain, and block-capacity/congestion fee markets are direct prior | 3 / 7 / 15% | closed |
| HyperCore cancel-first intra-block shield | Protocol sorting of cancels ahead of GTC/IOC submissions; stale-fill and liquidity-withdrawal response | With a frozen action packet this is deterministic partial-order/batch semantics; with adaptive users the rule changes submitted actions. Both branches duplicate the closed hard-event and scheduler-information routes | 1 / 4 / 10% | deduplicated; no new graph node |
| HIP-2 regenerative liquidity wave | Three-second consensus-hosted geometric-grid replenishment; inventory and refill-front dynamics | The exact rule is a reverse/grid strategy whose stationarity and propagation are fixed by external taker flow; it is an instance of the already closed regenerative reverse-order lattice | 1 / 4 / 10% | deduplicated; no new graph node |
| OMIE 96-gate temporal refinement | September 2026 move to 96 continuous intraday gates; temporal-resolution response of prices and balancing | Systemwide bundled time discretization, private bid state, no untreated mechanism, and direct quarter-hour/aggregation precedents duplicate the closed SDAC resolution-quench family | 2 / 5 / 11% | deduplicated; no new graph node |

No formulation is eligible for a card or experiment. Five nonduplicate formulations are recorded
as failed-closed descendants; three exact descendants are referenced to existing nodes rather than
inflating the graph.

## 4. Killer constructions

### 4.1 Rule 605 aggregate-equivalence twin

Construct two brokers with the same monthly counts, mean effective spread, price-improvement bins,
and execution-time bins. Broker A internalizes every order immediately and deliberately delays a
small balancing subset. Broker B routes every order and receives a mixture of fast and slow venue
fills. The public report vectors are identical, while a fee, tick, or routing intervention can have
opposite effects. The aggregate report is valuable external measurement, but it is not the same
action--state--observation loop as an order-level simulator.

### 4.2 Information-treatment grammar twin

Give two laboratory markets the same full-book display. In one, private values are stationary and
subjects repeat; in the other, values or participant composition change between rounds. Identical
information displays can yield different relaxation. Conversely, an adaptive learner can reproduce
the same price path under different feedback screens. A relaxation statistic does not isolate the
information filtration without one common assignment and learning grammar.

### 4.3 Clearing netting twin

Two networks have the same gross Treasury notional. In the first, offsetting bilateral positions
net strongly at a CCP; in the second, positions point in the same direction and do not. The mandate
therefore produces different balance-sheet relief. Holding the netted exposure fixed while changing
CCP margins or default-fund obligations reverses liquidity pressure again. Gross volume or network
degree cannot identify the response.

### 4.4 Fee-channel twin

Reduce the LP take-rate through a protocol fee while holding the trader-facing swap fee fixed, then
compare it with a dynamic hook that raises the trader-facing fee while leaving LP take-rate shares
unchanged. Both are called a fee increase but act through different kernels. A family label cannot
be treated as a scalar physical field.

### 4.5 Hidden congestion twin

Use the same sequence of landed Solana blocks under a 100M-CU cap. One world has no excluded
transactions; the other has a large private and dropped queue that happens not to alter the landed
set. Inclusion data are identical while the capacity relaxation counterfactual differs by order
one. A common-random replay of landed transactions cannot restore the missing opportunity set.

## 5. What remains scientifically useful

The expanded Rule 605 reports are the strongest reusable asset from this cycle because they are
prospective, standardized, free, and repeated across many reporting entities. They may falsify
execution-quality claims and expose transport failures. They cannot currently certify a
same-estimand market-simulator response because order-level receipt, routing policy, counterfactual
order composition, and venue state are not jointly public.

The forecast ledger therefore asks a narrow future question: whether the amended reports plus
publicly documented routing/receipt inputs ever close that bridge for at least 20 independent
reporters. A positive resolution would authorize a new child-card audit, not activate the current
failed formulation. No report download or outcome inspection is authorized now.

The controlled-market archive is useful for mechanism teaching, falsifier development, and model
criticism. It cannot be a prospective confirmation source because the treatments and findings are
already published. Treasury clearing and Solana capacity remain valuable real events for finance or
systems studies, but their public state is insufficient for the proposed Nature-scale causal market
physics. Uniswap v4 is an excellent programmable testbed, yet broad fee-response novelty is already
occupied and hook heterogeneity destroys a one-dimensional dose.

## 6. Decision

**Passed-and-closed asset portfolio audit; zero new cards and zero execution authorizations.** The
cycle generated several scientifically intelligible questions, but none survives the combined
novelty, identifiability, same-estimand, prospective-confirmation, and two-system contracts. The
largest lower endpoint is 6%, but probability is not the terminal reason for any closure.

The 15% lower-bound rule remains in force only for `active` status and is now explicitly provisional.
It is reasonable as a conservative brake on expensive simulation, data, participant, and compute
work; it is not reasonable as a universal topic-truth criterion or as a barrier to cheap falsifying
information. The next bounded search may use paper/source/schema work below 15% if a written robust
value-of-information case is positive. No threshold should be lowered merely to manufacture a
survivor.

No sandbox, simulator execution, market-data outcome access, download, purchase, external outreach,
EcoMD implementation, or GPU use is authorized by this cycle.

## 7. Primary-work and official-source manifest

### Decision and forecast governance

1. Edwards, *Value of Information for Decisions*: https://doi.org/10.1016/0022-2496(69)90015-7
2. Heath et al., *Simulating Study Data to Support Expected Value of Sample Information Calculations*: https://doi.org/10.1177/0272989X211026292
3. Hall et al., *Expected Net Present Value of Sample Information*: https://doi.org/10.1177/0272989X12443010
4. Gneiting and Raftery, *Strictly Proper Scoring Rules, Prediction, and Estimation*: https://doi.org/10.1198/016214506000001437
5. Camerer et al., *Evaluating the Replicability of Social Science Experiments in Nature and Science*: https://doi.org/10.1038/s41562-018-0399-z

### Rule 605 and simulator validation

6. SEC, amended Rule 605 FAQ effective 2026-08-01: https://www.sec.gov/rules-regulations/staff-guidance/trading-markets-frequently-asked-questions/frequently-asked-questions-rule-605-regulation-nms
7. SEC, 2024 Rule 605 adopting release: https://www.sec.gov/files/rules/final/2024/34-99679.pdf
8. Electronic Code of Federal Regulations, Rule 605: https://www.ecfr.gov/current/title-17/chapter-II/part-242/section-242.605
9. Bacidore, Ross and Sofianos, *Quantifying Market Order Execution Quality at the NYSE*: https://doi.org/10.1016/S1386-4181(02)00067-8
10. Battalio et al., *Wholesaler Execution Quality*: https://doi.org/10.1287/mnsc.2023.04156
11. Vyetrenko et al., *Get Real: Realism Metrics for Robust Limit Order Book Market Simulations*: https://arxiv.org/abs/1912.04941
12. Nagy et al., *LOB-Bench*: https://proceedings.mlr.press/v267/nagy25a.html

### Controlled information and convergence

13. Ikica et al., *Competitive Market Behavior: Convergence and Asymmetry in the Experimental Double Auction*: https://doi.org/10.1111/iere.12630
14. Anufriev et al., *The Role of Information in a Continuous Double Auction*: https://doi.org/10.1016/j.jedc.2022.104387
15. Cespa and Vives, *Market Opacity and Fragility*: https://doi.org/10.1257/aer.20231613

### Clearing, fees, capacity, and batching

16. SEC, Treasury clearing implementation and compliance dates: https://www.sec.gov/featured-topics/treasury-clearing-implementation
17. Bowman, Huh and Infante, *Balance-Sheet Netting in U.S. Treasury Markets and Central Clearing*: https://doi.org/10.17016/FEDS.2024.057
18. Loon and Zhong, *The Impact of Central Clearing on Counterparty Risk, Liquidity, and Trading*: https://doi.org/10.1016/j.jfineco.2013.12.001
19. Uniswap, official v4 dynamic-fee semantics: https://developers.uniswap.org/docs/protocols/v4/concepts/dynamic-fees
20. Baggiani, Herdegen and Sánchez-Betancourt, *Optimal Dynamic Fees in Automated Market Makers*: https://arxiv.org/abs/2506.02869
21. Wang, *Causal Effects of Protocol-Fee Changes on Liquidity Provision in Automated Market Makers*: https://arxiv.org/abs/2607.08525
22. Solana SIMD-0286, *Increase Block Limits to 100M CUs*: https://github.com/solana-foundation/solana-improvement-documents/blob/main/proposals/0286-raise-block-limits-to-100M.md
23. Garratt and van Oordt, *Monopoly without a Monopolist*: https://doi.org/10.1093/restud/rdaa076
24. Hyperliquid, official HyperCore order-action ordering: https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/order-book
25. Hyperliquid, official HIP-2 Hyperliquidity semantics: https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-2-hyperliquidity
26. Budish, Cramton and Shim, *The High-Frequency Trading Arms Race*: https://doi.org/10.1093/qje/qjv027
27. OMIE, September 2026 implementation of 96 continuous intraday gates: https://www.omie.es/en/market-regulations/rules-omie
