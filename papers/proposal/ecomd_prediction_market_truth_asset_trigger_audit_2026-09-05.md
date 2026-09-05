# EcoMD prediction-market truth-asset trigger audit

**Date:** 2026-09-05  
**Stage:** bounded D-3 re-entry-trigger audit; no candidate harvest  
**Archetype:** `measurement_method` / `empirical_intervention` boundary  
**Decision:** two `partial_capability` records, zero removed project blockers, no qualified trigger  
**Raw outcome, implementation, simulator, SSH and GPU access:** none

## Decision first

Two genuinely useful public assets appeared after the earlier EcoMD route closures:

1. [Polymarket-v1 Database](https://arxiv.org/abs/2606.04217) provides a very large
   on-chain settlement tape with ground-truth aggressor side, per-fill fees, maker and taker
   wallets, and Conditional Tokens Framework lifecycle events.
2. [OpenMarket](https://arxiv.org/abs/2607.26245) provides a frozen millisecond-level corpus
   joining Binance BTC/USDT events to Polymarket BTC 15-minute top-of-book events, with both
   source and collector timestamps.

They improve measurement, but neither separately nor jointly reopens prospective
counterfactual validation of EcoMD. Polymarket-v1 deliberately omits the off-chain order book;
OpenMarket records top-of-book state rather than the per-order add/modify/cancel/fill/nonfill
lifecycle. A settlement fill tape plus top-of-book changes cannot reconstruct queue priority,
resting depth, cancelled intent, unfilled actions, participant inventory, or the adaptive policies
that determine response to a new order or rule. The fee reform is platform-selected and bundles
taker fees with maker rebates; the source paper has already analyzed its outcomes and reports
pre-trend and inference limitations. Binance price moves are observed events, not assigned
interventions, and OpenMarket's single collector leaves a constant cross-venue clock-offset
ambiguity.

A second repository-derived idea also fails. EcoMD does not repeatedly optimize a finite fixed
bank of random tapes: its generator advances across iterations and checkpoint logic restores the
post-forward state only to prevent recomputation from rewinding it. If a fixed bank were introduced,
the objective would be ordinary sample-average approximation; held-out-seed generalization and
common-random-number variance reduction are mature. The proposed hard-event/pathwise-gradient
variant is already represented by three closed route-graph nodes.

The correct action is therefore to retain both datasets as watch-listed measurement assets, record
the exact missing contracts, and keep candidate harvest and all three GPU workers closed.

## 1. Governing scope

This is a trigger audit under the saturated-family re-entry rule, not Cycle 17 and not a topic-card
decision. It asks whether a newly available truth/control asset or theorem removes a named blocker
from the closed routes:

- `prospective_counterfactual_market_simulator_validity`;
- `interventional_lob_fidelity_benchmark`;
- `observation_quotient_response`; and
- the stochastic-gradient semantic subroutes.

The audit used public paper, repository, dataset-card and official-documentation metadata only. It
did not download either dataset, inspect raw market rows, calculate an outcome, run EcoMD, edit the
simulator, or connect to a worker.

## 2. Fixed-noise-tape hypothesis: exact repository and parent reduction

### 2.1 Frozen question

**Object.** Generalization of a differentiable stochastic market simulator from training noise
realizations to unseen random environments.

**Rival explanations.** Under H1, EcoMD repeatedly optimizes a small fixed noise-tape bank and can
overfit event topology in a way requiring a new stochastic-simulator learning method. Under H2,
the code consumes a continuing random stream; any finite-tape version is standard empirical-risk or
sample-average optimization, while matched tapes are ordinary common random numbers.

**Discriminating result.** H1 requires both a repeated finite tape bank in the current training path
and a population-risk failure not reducible to sample-average approximation or ordinary
environment generalization. Either a code-level absence or the exact reduction closes the idea.

### 2.2 What the code actually does

In `ecomd/training/train.py`, one `torch.Generator` is created and seeded before the training loop.
The same object is passed to initialization and each rollout, but it is not reset at an iteration
boundary. Consequently, its state advances as random draws are consumed.

The distributed path makes the semantics more explicit. `ecomd/training/train_distributed.py`
creates one generator per rank, seeds rank `r` with a distinct rank-local seed, and consumes that
generator through successive rollouts. With truncated-BPTT checkpointing, the code snapshots the
post-forward generator state and restores it after backward. This prevents checkpoint
recomputation from rewinding the next iteration's stream; it does not replay a fixed training tape.
Exact checkpoint resume restores the recorded runtime stream state.

Thus the premise is false for the current implementation. A finite training run of a deterministic
pseudorandom stream is not the same object as repeatedly optimizing a finite enumerated bank whose
members recur and can be indexed by the model.

### 2.3 Exact reduction if fixed tapes were added

For independent tapes `xi_1,...,xi_N`, a fixed-bank simulator objective is

\[
  \widehat L_N(\theta)=\frac1N\sum_{i=1}^N \ell(\theta;\xi_i),
  \qquad
  L(\theta)=\mathbb E_{\xi}\,\ell(\theta;\xi).
\]

This is sample-average approximation or empirical risk minimization. Training-tape versus
held-out-tape error is its ordinary generalization gap. Sample-path optimization dates at least to
[Guerkan, Oezge and Robinson (1994)](https://pure.iiasa.ac.at/4141), and formal sample-average
approximation theory is mature; see
[Kleywegt, Shapiro and Homem-de-Mello (2002)](https://epubs.siam.org/doi/10.1137/S1052623499363220).
Reusing the same tape across two parameter settings is a coupling that can reduce the variance of
their difference, namely common random numbers; it does not identify a new physical response.
[Pearce, Poloczek and Branke (2022)](https://doi.org/10.1287/opre.2021.2208) explicitly optimize
such reuse. Generalization from a fixed set of randomized environments to unseen ones is already a
standard ML evaluation object; [Cobbe et al. (ICML 2019)](https://proceedings.mlr.press/v97/cobbe19a.html)
is a direct example.

The apparent escape through event-topology memorization is also closed. It maps directly to
`coupling_invariant_differentiable_market_counterfactual`,
`noise_frame_optimized_ecomd_gradients`, and
`stochastic_simulator_gradient_semantic_conformance`: a fixed-noise derivative is not an identified
market counterfactual, hard-event gradients need an explicit event semantics, and forward-equivalent
randomness parameterizations need not share sample derivatives. No new route node or trigger entry
is warranted.

## 3. Polymarket-v1: strong trade truth, insufficient intervention truth

### 3.1 Capability that is genuinely new

The paper reports 1.2016 billion nominal `OrderFilled` records over 2022-11-21--2026-04-28,
approximately 1.30 million markets, and complete first-generation contract coverage. The public
[dataset card](https://huggingface.co/datasets/TimeSeventeen/Polymarket-v1) exposes:

- the on-chain maker and taker, execution price and volume, transaction identity, block time, and
  ground-truth aggressor direction;
- `fee_usdc`, plus maker/taker base-fee metadata in the cleaned trade layer;
- standard-binary and negative-risk market mappings; and
- preparations, splits, merges, resolutions, and redemptions in the CTF layer.

This is a material measurement capability. It can validate aggressor-side classification and
settlement-level accounting in a way that inferred equity trade signs cannot. The source paper
already uses it to show that conventional tick-rule and bulk-volume classifiers are close to random
in aggregate and distort downstream microstructure quantities.

The public repository is not yet an ideal immutable paper artifact. Its main branch was still being
changed after the paper, including additions of v2 CTF events and a current `0.1.5` README revision.
An experiment could pin an exact Hugging Face commit, but a future paper would first need to declare
which files are part of the v1 paper-bound release rather than cite moving `main`.

### 3.2 Exact state nonidentification

The dataset card states that none of its layers contains order-book snapshots, quote updates,
cancellations, or off-chain resting-order depth. This is not a cosmetic missing covariate. Let `O`
denote the complete observed settlement and CTF tape. Construct two latent off-chain states:

- `S_A` contains a deep queue behind the observed best quote and many cancelled orders; and
- `S_B` contains a thin queue plus a replenishment policy chosen to produce exactly the same
  realized fills and CTF events when no test action is applied.

Both states map to the same `O`. Under an additional market order, latency change, priority rule, or
fee rule, `S_A` can absorb the dose with negligible price movement while `S_B` can jump by an
arbitrarily larger amount. Therefore

\[
  P(O\mid S_A)=P(O\mid S_B)
  \quad\text{does not imply}\quad
  P(Y(a)\mid S_A)=P(Y(a)\mid S_B).
\]

No learned inverse model can recover a unique counterfactual response from these observations
without an independently justified state restriction. Wallet addresses also do not reveal complete
actor inventory, cross-venue routing, intent, or policy state.

### 3.3 Why the fee reform does not repair the contract

The 2026 fee change is a real institutional event, and official Polymarket documentation records
staggered activations. The same documentation also makes the treatment composite: taker fees fund
daily maker rebates. For example, the official changelog describes both changes together and notes
that some expansions apply only to newly created markets. The current fee documentation is a live
description, not a versioned per-market historical assignment tape.

The source paper estimates a staggered two-way-fixed-effects design and has already analyzed the
available outcome family. It explicitly reports nontrivial pre-trends for VPIN and Amihud,
platform-wide growth and v1-to-v2 migration as competing changes, heterogeneous-treatment concerns,
and implausibly large t-statistics likely caused by underestimated clustered uncertainty. Its
wash-trading result has a more defensible pre-trend, but one usable reduced-form outcome does not
turn the tape into a full simulator-response oracle.

Three distinctions are decisive:

1. `fee_usdc` makes realized exposure measurable; it does not randomize fee assignment.
2. A category/date rollout bundled with maker rebates does not isolate a single market action
   kernel, especially when traders and wallets can move across categories.
3. A trade-tape treatment effect is a narrower empirical-finance estimand. It is not the same as
   validating EcoMD's path response from a fixed complete pre-state.

The method/claim neighborhood is also occupied. The Polymarket-v1 paper itself contains the fee
event study. Maker-taker fee and rebate experiments are mature, and the existing registry already
contains a 2026 public-log, hash-frozen fee-change causal study with an explicit channel audit.
Merely replacing its estimator by a neural causal model, or adding EcoMD as a synthetic comparator,
would not create an ICLR contribution.

### 3.4 Gate result

| Gate | Result |
|---|---|
| Licensed large-scale transaction truth | Pass |
| Ground-truth aggressor and realized fee measurement | Pass |
| Immutable paper-bound release | Partial: an exact revision can be pinned, but `main` is moving and mixes later CTF material |
| Single assigned action kernel | Fail: platform-selected stagger and fee/rebate bundle |
| Complete intervention pre-state | Fail: no off-chain order lifecycle, queue or nonfills |
| Identification for the simulator path-law estimand | Fail: key pre-trends, migration and interference remain |
| Untouched confirmation family | Fail: the source paper already evaluates the fee outcomes |
| Independent same-estimand truth system | Fail |

**Decision:** `partial_capability`, `removed_blockers: []`, no candidate harvest.

## 4. OpenMarket: frozen synchronization asset, not an assigned response oracle

### 4.1 Capability that is genuinely new

OpenMarket's `v0.5.2` tag resolves to commit
`6e6cc240f32ab9fd2f8fa602bd0aba823b24bfee`. Its recommended
`v0.4.3-unified` split contains 727,098,247 deduplicated rows over 202 archival snapshots,
2,936,031 explicit lead-lag pairs, and event data on 54 Polymarket days and 57 Binance days between
2026-02-12 and 2026-05-15. The release is Apache-2.0 and the source is explicitly archived.

The schema is useful and unusually explicit. Binance trades and top quotes include source and
collector times. Polymarket ticks include event type, mid, best bid, best ask, and top-level size.
The release distinguishes the source-clock lag from the collector-clock ordering and retains
pairing-quality metadata.

### 4.2 Clock and action limits

The paper bounds relative clock drift to at most 6 ms over the archive but leaves an unresolved
single-vantage constant offset of roughly plus or minus 99 ms. It correctly labels the 16 ms median
as an apparent source-clock result. A collector-clock event study reports a median 347 ms quote
response after large Binance moves, which establishes ordering on that collector but not assignment.

The cross-venue causal claim needed for EcoMD is stronger. A large Binance move can share news with
Polymarket, be anticipated by both venues, or arise jointly with arbitrage routing. Conditioning on
the observed move does not implement `do(Binance move)`. Network delay and the choice to observe
only events reaching one collector are part of the observation mechanism.

Moreover, `polymarket_ticks_ms` is a top-of-book table. It does not export per-order queue identity,
add/modify/cancel messages, nonfills, hidden depth, or participant inventory. The paper itself says
`lag_pairs_ms` is an event-alignment table, not an order-book reconstruction. Hence the same
latent-state witness from Section 3.2 applies.

### 4.3 Method collision

A proposed method that jointly estimates unknown event-stream shifts and excitation is not new.
[Trouleau et al. (ICML 2019)](https://proceedings.mlr.press/v97/trouleau19a.html) explicitly learn
Hawkes causal structure under unknown synchronization shifts. OpenMarket itself already contributes
source-versus-ingest timing diagnostics and a clock-offset-free collector-time response analysis.

A residual ICLR method would therefore need more than robust standard errors or a learned lag
model. It must produce a market-native estimand that remains informative under the full allowed
clock-offset set and partial state, with a theorem or sharp abstention boundary not reducible to
synchronization-noise point processes. The present data do not supply the exogenous action or full
state needed to make that residual non-vacuous.

### 4.4 Gate result

| Gate | Result |
|---|---|
| Frozen, licensed, reproducible public corpus | Pass |
| Dual source/collector timestamps and explicit pairing metadata | Pass |
| Absolute sub-100-ms cross-venue order | Fail: constant offset remains unidentified |
| Assigned or defensibly exogenous driver | Fail: Binance moves are observational |
| Complete market pre-state and action lifecycle | Fail: top-of-book only |
| Unoccupied clock-robust method | Fail for the obvious formulation |
| Independent platform confirmation | Fail: one collector and one prediction-market platform |

**Decision:** `partial_capability`, `removed_blockers: []`, no candidate harvest.

## 5. Why combining the two datasets is still insufficient

The assets are complementary but not algebraically complete:

\[
  \text{on-chain settled fills and CTF lifecycle}
  + \text{one-collector top-of-book updates}
  \neq \text{complete off-chain market state}.
\]

Their union still omits cancelled and unfilled orders, queue-ahead state, full depth, order ownership
for the resting book, private routing, cross-venue inventory, and adaptive strategy state. Any of
these can be varied while preserving both observed tapes and reversing the response to a new
action. The two releases also observe the same platform, and OpenMarket covers only a narrow BTC
15-minute slice across a period overlapping the v1/v2 transition. They are not independently
governed same-estimand replications.

The combination can support useful descriptive checks: align realized fills and fees to top quotes,
measure aggressor-label error, or bound collector-time response. Those are measurement assets and
possible finance/data-release contributions. Today they have neither an irreducible ML theorem nor
an untouched independent test that raises them to an EcoMD ICLR topic.

## 6. Exact re-entry conditions

### 6.1 Polymarket fee/intervention branch

Re-audit only when one frozen package supplies all of the following:

1. an immutable paper-bound file manifest and revision;
2. per-market historical fee and rebate assignment, exact effective timestamps, rates, eligibility,
   and policy-version provenance;
3. an off-chain per-order add/modify/cancel/fill/nonfill tape with reconstructible pre-action book
   and queue state;
4. a defensible assignment and interference unit that handles wallet/category migration;
5. an entire untouched future rule family or platform held out before outcomes; and
6. a deterministic common-action adapter plus an independently governed same-estimand system.

### 6.2 OpenMarket response branch

Re-audit only after:

1. a second independently clocked collector, PTP-grade venue-clock evidence, or an estimand proved
   invariant over the complete offset set;
2. full L3 event lifecycle and replay pre-state rather than top-of-book summaries;
3. a randomized, scheduled, or otherwise defensibly exogenous driver with frozen support; and
4. an independent prediction-market venue or collection lineage reserved for confirmation.

Without these changes, an observational conditional forecast may still be valid, but it must not be
called a market intervention or simulator counterfactual.

## 7. Machine decision

No topic card was created and no route was activated. The current machine decision authorizes only
the already active constraint-attribution continuation; it does not authorize this exploration to
download data, implement an adapter, run EcoMD, inspect raw outcomes, SSH to a worker, or use GPU.

The A800 at `100.113.230.38` and both V100 workers at `100.80.236.112` and
`100.123.220.57` therefore receive zero work from this audit.
