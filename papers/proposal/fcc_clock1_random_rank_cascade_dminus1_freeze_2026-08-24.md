# FCC clock-1 randomized rank cascade — D−1 freeze

**Frozen:** 2026-08-24

**State:** candidate only; not active, not an experiment authorization

**Parent selection:** `ecomd_post_aprime_reselection_gminus1_result_2026-08-24.md`

## Scientific question

FCC clock-1 auctions process bids to change demand across all bidders and licences in ascending price-point order.
When multiple bids have the same price point, the official rule assigns their processing order through a
bid-specific pseudorandom number. Because every applied bid updates bidder holdings and aggregate demand and causes
queued bids to be reconsidered, a random microscopic ordering can in principle change which bids apply and then
propagate into prices, activity and later eligibility.

The candidate asks whether this documented random ordering produces a reproducible **rank-response cascade** and
whether a mechanism-faithful simulator, frozen on one auction, predicts the cascade distribution in later auctions.
This is the market analogue of collision-order damage spreading; the analogy is not itself a novelty claim.

## Frozen estimands

Let (g=(r,p)) denote one round-by-price-point tie set and let (R_{ig}) be bidder (i)'s rank induced by the
published `selection_number`. Let (A_{ig}) record whether the bid was fully applied. D−1 may only determine whether
there is support for a randomization design. It may not estimate effects.

If D−1 passes, the next freeze must define:

1. a within-tie-set randomized first-stage estimand for rank on (A_{ig}), respecting sampling without replacement;
2. a prespecified exposure mapping for interference through licences and bidder activity;
3. a finite-horizon response kernel over aggregate demand, posted price, processed activity and next-round
   eligibility; and
4. an explicit abstention region for private valuation, intent and welfare, none of which is identified by rank.

No independent-Bernoulli approximation to ranks is allowed. Tie sets are the randomization blocks.

## D−1 pass conditions

All conditions are conjunctive:

1. **Binding support.** At least two official auctions each contain enough same-round, same-price-point tie sets in
   which alternative processing orders could change an applied/not-applied decision. The sample floor must be set
   by a blinded power calculation; 30 binding tie sets per auction is a provisional hard minimum, not a power claim.
2. **Randomization semantics.** Official documentation or an auditable diagnostic must support exchangeability of
   the bid-specific pseudorandom ordering within declared blocks. The absence of a public PRNG or seed must be
   resolved by a fail-closed balance/randomness protocol, not assumed away.
3. **First-stage replay.** Public fields must deterministically reconstruct whether a submitted bid was applied,
   including no-excess-supply, activity/eligibility and unfulfilled-queue logic, to a frozen zero-discrepancy rule or
   a justified tolerance.
4. **Replication contract.** Auction 108, 110 and 113 schemas and mechanisms must be mapped before choosing
   development and held-out auctions. A mechanism change cannot be called a replication without an explicit bridge.
5. **Novelty.** At least 20 primary works must be audited across spectrum auctions, randomized tie-breaking,
   randomization inference under interference, queue-order sensitivity and auction simulation. A direct use of FCC
   `selection_number` for the same propagation estimand closes the card.
6. **Simulator feasibility.** SATS and ML-CCA may provide valuation and clock-auction components, but neither may be
   called an FCC clock-1 replay engine. A separate source-level feasibility audit must show that exact bid processing
   can be implemented and tested before any simulator run.

## Resource boundary

D−1 may inspect official rules, schemas, licences, source trees and blinded support summaries. A support program may
read only fields needed to construct tie blocks and report aggregate counts; it must not emit bidder-, licence- or
round-level outcomes. No effect estimate, graph propagation statistic, welfare measure, private-value inference,
model fitting, simulator implementation, EcoMD run, model API call, paid data or GPU is allowed.

Search-engine snippets and project-page summary metadata seen during selection are not an analysis dataset. The
official bid and result files remain unopened by this project.

## Automatic stop

Close the route if any pass condition fails. In particular, close it if pseudorandom ranks cannot be defended as
exchangeable, binding ties are too sparse, the first-stage processor cannot be replayed, or the surviving method is
ordinary randomization inference plus a standard auction simulator with no new scientific propagation result.

Passing D−1 would authorize only a separate T0 theorem/novelty and estimand freeze. It would not activate a Nature
paper or authorize outcome analysis.
