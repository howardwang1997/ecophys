# Post-A′ market-simulation reselection — G−1 result

**Date:** 2026-08-24

**Machine record:** `configs/empirical_physics/ecomd_post_aprime_reselection_gminus1_v1.yaml`

**Resource boundary:** papers, official protocols and schemas, public source/licence metadata and finite
counterexamples only; no bid/result file, paid data, implementation, model call, EcoMD run or GPU

## Decision

**One new question is selected as a candidate, but no Nature-grade route is active.** The candidate is the causal
propagation of FCC clock-auction pseudorandom tie order. It receives a paper-and-metadata-only D−1 because the
official mechanism and schema expose a genuine randomized micro-ordering, its applied/not-applied first stage and
several later state variables. Its estimated T0 survival is 12%, below the frozen 15% activation floor.

Seventeen other cards close at G−1. Six AI-agent cards collide with 2025--2026 direct work or established economic
theory; six molecular-dynamics cards reduce to mature rare-event, response or multilevel methods or fail by finite
counterexample; five field protocols lack randomization, replay state, treated L2 data, a post period or a second
system. Combining failed cards does not repair those defects.

| Branch | Cards | Best T0 prior | Outcome |
|---|---:|---:|---|
| FCC randomized clock-auction order | 1 | 12% (upper bound 14%) | **CANDIDATE / D−1 only** |
| AI-agent markets | 6 | 5--12% | all **RED** |
| MD and computational physics | 6 | 7% | all **RED** |
| other real protocols | 5 | 4% | all **RED** |

These are decision priors, not probabilities estimated from data. A candidate label authorizes only the frozen
D−1 support, randomization, replay and novelty audit.

## Selected candidate: FCC clock-1 randomized rank cascade

### Why it survives this screen

Auction 113 uses a clock-1 ascending auction. After each round, bids that maintain demand are applied first and
bids that change demand are processed in ascending price-point order across bidders and licences. An applied bid
changes holdings and aggregate demand; rejected bids enter a queue and are reconsidered after later applications.
For bids tied at one price point, the FCC states that processing order is determined by a bid-specific
pseudorandom number. See paragraphs 211--214 of the
[Auction 113 Procedures Notice](https://docs.fcc.gov/public/attachments/DA-25-1075A1.pdf).

The official [Auction 113 public-reporting schema](https://auctiondata.fcc.gov/public/projects/auction113/static_files/auction_113_prs_file_formats_final.pdf/download)
exposes the `selection_number` used for tie-breaking, whether a bid was fully applied, the reason it was not
applied, processed and aggregate demand, posted prices, activity, processed activity and next-round eligibility.
[Auction 108](https://auctiondata.fcc.gov/public/projects/auction108) and
[Auction 110](https://auctiondata.fcc.gov/public/projects/auction110) expose analogous public reporting families.
This is unusually close to a field-randomized collision-order experiment: the microscopic order is documented,
the local transition is observable, and the state can propagate over rounds.

The scientific target is deliberately narrow:

> Does pseudorandom rank within an otherwise tied processing block change bid application and generate a
> reproducible causal response kernel through the unfulfilled queue, aggregate demand, prices, bidder activity and
> eligibility; and can a mechanism-faithful simulator trained on one auction predict that kernel in another?

It is not a claim about bidder intent, private valuation, welfare or optimal FCC policy. Those quantities remain
unidentified.

### Why it is not active

Four hard facts are missing:

1. No blinded count yet establishes enough **binding** tie sets in at least two auctions. Many tied bids can be
   non-binding, in which case order cannot change the first stage.
2. The rules call the number pseudorandom, but this audit found no public PRNG, seed or generation audit. A rank
   design therefore needs fail-closed exchangeability and balance tests rather than an assumption of ideal
   randomization.
3. The public fields have not yet been shown to reproduce the official applied/not-applied processor exactly.
4. [SATS](https://github.com/spectrumauctions/sats) supplies spectrum-auction value models and
   [ML-CCA](https://github.com/marketdesignresearch/ML-CCA) supplies a combinatorial clock-auction implementation,
   but neither is an FCC clock-1 replay engine.

The frozen next step is
`papers/proposal/fcc_clock1_random_rank_cascade_dminus1_freeze_2026-08-24.md`. It requires binding support in two
auctions, defensible randomization blocks, deterministic first-stage replay, a source-level simulator feasibility
contract and at least 20 primary works. Failure of any condition closes the candidate before outcomes or code.

### MD connection and its limit

The useful molecular-dynamics analogy is **damage spreading from randomized collision order**: two otherwise
identical tied-event schedules differ by one local ordering and may separate through a stateful queue. The FCC
randomization makes that perturbation causal rather than hypothetical. The analogy supplies experimental design,
not novelty. Lyapunov exponents, instantons, weighted ensembles, odd response and collision-cone replay may not be
attached unless each independently passes its own theorem gate; all such generic attachments failed below.

## Closed AI-agent cards

### 1. Reasoning-time versus market-staleness law

The proposed law traded a quality gain from additional test-time compute against execution delay in a changing
market. It closes because Cheng et al.'s 2026
[Agents Are Not Algorithms](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6713620) directly manipulates
reasoning intensity and market speed in real-time trading and reports a reasoning dividend and deliberation tax.
[Learning When to Plan](https://arxiv.org/abs/2509.03581) already studies adaptive test-time compute, while
[Magentic Marketplace](https://www.microsoft.com/en-us/research/wp-content/uploads/2025/10/multi-agent-marketplace.pdf)
reports a large response-speed advantage.

There is no distribution-free curve: in a static market with monotonically improving decisions, more compute is
always better; if decision quality is flat and state hazard is positive, it is always worse. ABIDES has native
delay, but an SCML wall-time deadline is not the same economic event-time intervention. T0 survival: 0--2%.

### 2. Reverse market thickness for AI contractors

The proposed mechanism selected the highest self-reported capability, allowing extreme overconfidence errors to
make welfare fall with bidder count. It is the strongest failed AI card, but
[MarketBench 2026](https://arxiv.org/abs/2604.23897) already reports miscalibrated success/cost self-assessment and
selection of overconfident agents; Magentic Marketplace reports welfare degradation when the choice set grows from
3 to 100; and [Hong and Shum 2002](https://doi.org/10.1111/1467-937X.00229) supplies the classic winner's-curse
mechanism.

With truthful reports, adding a bidder cannot hurt the selector; with an unbounded positive report-error tail,
welfare may decrease arbitrarily. The joint ability/error law determines the curve. MarketBench and Magentic do
not expose the same bidder-count intervention or estimand. T0 survival: 5--12%.

### 3. Strategic rationale-disclosure paradox

Forcing public rationales might reveal reservation values and transfer surplus to opponents. This reduces to a
signalling game, and natural-language chain of thought is not a verified internal state. Recent private-information
negotiation work already varies provider identity and strategic patience, while the NeurIPS 2024
[PACT benchmark](https://proceedings.neurips.cc/paper_files/paper/2024/file/984dd3db213db2d1454a163b65b84d08-Paper-Datasets_and_Benchmarks_Track.pdf)
covers competition and manipulation. If rationales are type-independent or ignored, the effect is zero; if they
encode type injectively and opponents exploit them, leakage can be complete. No sign is identified. T0: 2--6%.

### 4. Strategy fossil record and Red-Queen cross-play

Cross-year SCML or Power TAC payoff matrices could reveal non-transitive cycles, but empirical game-theoretic
analysis was already applied to TAC/SCM agents by
[Jordan, Kiekintveld and Wellman 2007](https://strategicreasoning.org/publications/2007/empirical-game-theoretic-analysis-of-the-tac-supply-chain-game/),
and modern population geometry and response diversity directly cover non-transitivity. Any finite historical
matrix can be extended by a new agent that beats all, loses to all or creates an arbitrary cycle, so it cannot
predict an unrestricted future agent. T0: 0--2%.

### 5. Market-automorphism defect as an OOD certificate

Approximate equivariance in MDPs, equivariant RL/MARL and metamorphic testing occupy the method. The graph's prior
gauge-invariant and generic simulator-audit routes already close the local variants. More decisively, a deliberately
non-equivariant policy can be optimal in the target distribution and a perfectly equivariant policy can fail under
a non-symmetric shift. The defect is neither necessary nor sufficient for OOD success. T0: 1--4%.

### 6. Settlement conservation-defect cascade

Invalid quotes, fictitious inventory and unfulfillable contracts are important engineering failures, but 2026
agent-commerce work already supplies runtime verification/repair, overbidding and bankruptcy observations, and
contract execution benchmarks. If the executor rejects every invalid intent, ledger conservation holds with no
cascade; if an adapter interprets the same text arbitrarily, it can produce arbitrary balance paths. Adapter
semantics, not a universal market law, dominates. T0: 1--5%.

## Closed molecular-dynamics and computational-physics cards

### 1. Lineage-complete weighted ensemble for market crashes

Full-state branching could estimate a rare crash without pretending that a visible order-book projection is
Markov. But [Zhang, Jasnow and Zuckerman 2010](https://doi.org/10.1063/1.3306345) already proves weighted-ensemble
unbiasedness for broad Markov and non-Markov dynamics and adaptive bins. Modern neural Feynman--Kac, AMS and
adaptive committor work occupy the algorithmic neighborhood.

A last-step Bernoulli crash is a decisive counterexample to a uniform efficiency theorem: if every trajectory is
identical until the last step and crashes with probability (p), then no pre-terminal score helps and

\[
\frac{\operatorname{Var}(\hat p)}{p^2}=\frac{1-p}{Kp}.
\]

The relative variance cannot be bounded by (C/K) uniformly as (p\to0) without committor information. ABIDES
and BSE also lack a frozen bit-complete branch-state contract. T0: 4%.

### 2. Hybrid jump-process market instanton

The card sought a least-action marked-order path whose action gap predicts how a market rule changes crash hazard.
[Heymann and Vanden-Eijnden 2008](https://doi.org/10.1002/cpa.20238) covers geometric minimum action for
nongradient systems and a Markov-jump example; continuous-time jump-network action gradients and deep gMAM now
cover the computational core.

At finite noise, two exit channels can have

\[
p_1^\epsilon=a e^{-I/\epsilon},\qquad p_2^\epsilon=b e^{-I/\epsilon}.
\]

Equal action leaves arbitrary prefactors to decide the ranking, and prefactors can also reverse nearby actions at
attainable noise. ABIDES and BSE do not natively share one small-noise family. T0: 7%.

### 3. Oscillatory liquidity microrheology

An inventory-neutral multisine probe could estimate a complex liquidity modulus. Market impact propagators,
no-dynamic-arbitrage response constraints, OFI response, Hawkes impact and direct
[linear-response theory in stock markets](https://doi.org/10.1038/s41598-021-02263-6) already occupy the linear
object. Two systems (y=G*u+cu^3) and (\tilde y=G*u-cu^3) have the same infinitesimal spectrum and opposite
nonlinear failure behavior. Without a new transferable nonlinear bound, the spectrum cannot predict stress. T0:
2%.

### 4. Odd and nonreciprocal market mechanics

Odd elasticity and nonreciprocal phase transitions supply the physics vocabulary, but
[Klimek et al. 2023](https://www.nature.com/articles/s42005-023-01379-7) already uses a nonnormal interaction ABM
for financial bubbles, and 2025 work studies self-organized nonnormal financial influence networks. Moreover

\[
J=-I+\omega\begin{pmatrix}0&-1\\1&0\end{pmatrix}
\]

has nonzero antisymmetric response but (\lVert e^{Jt}\rVert_2=e^{-t}), so it never transiently amplifies. The
antisymmetric component also depends on state scaling and metric. T0: 0.5%.

### 5. Conservative differentiable transaction integrator

Exact cash/asset conservation can be imposed, but an exact price-time-priority allocation is discontinuous at
bidding ties. For one object and two buyers,

\[
x_1=\mathbf 1\{b_1>b_2\},\qquad x_2=1-x_1,
\]

so no map is both exact and everywhere differentiable. Smoothing, straight-through estimators and generalized
gradients change the claim and enter established differentiable-auction, GradABM and stock-flow-consistent work.
Conservation alone does not identify prices or allocations. T0: 1%.

### 6. Event-aligned MLMC market simulation

MLMC for continuous-time Markov chains, PDMPs, discontinuous functionals and rare events is established. In a
unit bid queue, one cancellation and one aggressive sell inside the same coarse cell give order-dependent trade and
price outcomes. Near-simultaneous pairs occur with probability (O(h)) and produce an (O(1)) path difference, so

\[
\mathbb E|Y_h-Y_{2h}|^2=O(h),
\]

not the proposed (O(h^2)). Resolving exact order removes the cheap coarse level and returns to the already closed
hard-event semantics. T0: 3%.

## Closed field-protocol cards

### EU SDAC 60-to-15-minute temporal quench

The [ENTSO-E implementation record](https://www.entsoe.eu/network_codes/cacm/implementation/sdac/) and
[European Commission announcement](https://energy.ec.europa.eu/news/eu-electricity-trading-day-ahead-markets-becomes-more-dynamic-2025-10-01_en)
fix the 1 October 2025 system-wide switch. It has no untreated zone, complete bids and EUPHEMIA state are hidden,
and the public aggregate problem maps back to the graph's failed observation/coarse-graining route. Earlier work
already studies 15-minute causal and aggregation effects. T0: 4%.

### ERCOT RTC+B scarcity paths

[ERCOT records the 5 December 2025 go-live](https://www.ercot.com/news/release/12052025-ercot-goes-live), and its
[public API release notes](https://developer.ercot.com/applications/pubapi/relnotes/) expose added SCED, ancillary-
service and storage fields. The intervention is nevertheless system-wide and nonrandom; full bids, network state,
QSE strategy and private telemetry are missing. Public inputs cannot replay the pre-change counterfactual, while
large-deviation and extreme-event market-clearing methods are already mature. T0: 4%.

### Polymarket dynamic tick boundary

The [official WebSocket schema](https://docs.polymarket.com/api-reference/wss/market) includes book, trade, price
and `tick_size_change` events. But a tick change is deterministically triggered near extreme prices, where
information arrival and contract resolution also change. There is no equivalent second real system or exact public
engine. Without an instrument, the event is endogenous and a local event study cannot identify the tick effect.
T0: 3%.

### Binance scheduled tick changes

Official notices specify affected pairs, old/new tick and time, but the
[public data repository](https://github.com/binance/binance-public-data) does not provide continuous reconstructable
L2 for the treated small pairs. Exchange selection and concurrent GTC/ATA or suspension rules further confound the
event, and the raw-data reuse terms require a separate legal audit. The treated-state data gate has already failed.
T0: 1%.

### Future SEC half-penny rule with ABIDES

The [2024 final rule](https://www.sec.gov/files/rules/final/2024/34-101070.pdf) is a potentially valuable future
intervention, but a [2026 proposal](https://www.sec.gov/files/rules/proposed/2026/34-105655.pdf) places implementation
after the present date. There is no post period, public full L2 is absent, and tick, access-fee and odd-lot changes
are bundled. ABIDES does not provide a validated real-state bridge. The card may be watched as a future protocol,
but it is not a present research route. T0: below 1%.

## Why combinations do not rescue the closed cards

- Adding weighted ensemble or an instanton to FCC would contribute a generic estimator without a rare-event
  estimand; it does not solve binding support, randomization or replay.
- Calling the FCC propagation kernel odd response, a Lyapunov exponent or a collision cone would import already
  closed claims. The causal random order is the scientific object.
- Combining AI overconfidence, latency or rationale disclosure with a protocol card changes the bidder population
  and destroys the field randomization contract; it creates a benchmark rather than a field mechanism.
- Combining two nonrandom cutovers does not create randomization, and combining two partially observed systems does
  not identify either hidden state.

The selected card therefore remains deliberately small: official random tie order, an observed bid-processing
first stage, a prespecified interference map, and a cross-auction simulator prediction. Nothing else is bundled.

## Graph decision and next action

The route graph should record one completed reselection node, seventeen failed-closed children and one candidate
child. The previous A′ node points to this selection; the selection aggregates every screened card. No child is
active.

Run only the frozen FCC D−1. It must produce a support/randomization/replay/novelty verdict without emitting or
analysing treatment effects. A RED result closes the candidate and returns to contract-first selection. A GREEN
result authorizes only a separate T0 estimand and theorem audit; it does not authorize simulation, outcomes or
compute.
