# FCC clock-1 randomized rank cascade — frozen support-only prefilter

**Frozen:** 2026-09-04, before any FCC bid or result row was parsed

**Parent:** `fcc_clock1_random_rank_cascade_dminus1_freeze_2026-08-24.md`

**Status effect:** none. This specification permits only the already-authorized D−1 aggregate
support prefilter. It does not authorize an effect estimate, simulator, EcoMD work, model fitting,
outcome analysis or compute.

## 1. Question and stop rule

The prefilter asks only whether two completed clock-1 auctions contain enough tie blocks that could
possibly be sensitive to bid processing order. Auction 108 and Auction 113 are the two exact
clock-1 systems. Auction 110 is a mechanism comparator because it uses generic multi-unit products
and switch bids rather than one frequency-specific licence per category.

For each auction, report an upper bound (U_a) on potentially binding tie blocks. If either
(U_{108}<30) or (U_{113}<30), close the candidate for insufficient replicated support. The
threshold is the provisional hard minimum frozen by the parent D−1 document; it is not a power
claim. Passing this prefilter removes no other D−1 blocker.

## 2. Immutable official inputs

| Auction | File | SHA-256 |
|---|---|---|
| 108 | `https://auctiondata.fcc.gov/public/projects/auction108/static_files/bids.zip/download` | `c750f8609d99231a1434411cfc6207eb66610d2ea26247f618deaa7c57a13629` |
| 108 | `https://auctiondata.fcc.gov/public/projects/auction108/static_files/results.zip/download` | `bc8cbfce8c312f1609603ca358570127c7eaf699c7b604d77c81c1aa4af17fc7` |
| 110 | `https://auctiondata.fcc.gov/public/projects/auction110/static_files/clock_bids.zip/download` | `fe49b2e880b15915f9b6c3f416298e11914d569cce60bc432ec9485d58efc20e` |
| 110 | `https://auctiondata.fcc.gov/public/projects/auction110/static_files/clock_results.zip/download` | `464def4a790913dd8755c34c842de41f12b3f7a7d1c2ce11f4bec1d1914a5f46` |
| 113 | `https://auctiondata.fcc.gov/public/projects/auction113/static_files/bids.zip/download` | `927ed6306b5637b8aa30251acbdb75521248a7ebbcfcbb45bd367cb586e1047a` |
| 113 | `https://auctiondata.fcc.gov/public/projects/auction113/static_files/all_bid_results.zip/download` | `00835d7ec07cab57bb21352763f486e70f85271e9e8e90cd17269409cd42f330` |

The official PRS file-format PDFs were inspected before this freeze. They define one bid record per
round and bid combination, a bid-specific pseudorandom `selection_number`, and product-level result
flags. The raw archives remain disposable temporary inputs; only hashes, schema and aggregate
outputs may enter the repository.

## 3. Whitelist and instruction reconstruction

The program may read only these columns:

- bids: `auction_id`, `round`, `frn`, `market`, `category` or `channel_block`, `bid_type`,
  `price_point`, `selection_number`, `switch_from_category`, and `switch_to_category`;
- results: `auction_id`, `round`, `frn`, `market`, `category` or `channel_block`, and
  `fully_processed_flag` or `fully_applied_flag`.

Names, prices, quantities, processed demand, aggregate demand, detail strings, payments and final
winnings are forbidden. Identifiers needed for joins exist only in memory and must never be emitted.

An instruction is keyed internally by auction, round, FRN and selection number. For Auctions 108
and 110, the two public rows representing one switch instruction are collapsed. Its processing
price point is taken from the `from` leg, identified by non-null `switch_to_category`; its touched
product set contains both legs. If the expected leg is absent, the program fails closed. Auction 113
has no switch fields and each unique key is one instruction.

A tie block is the exact tuple `(auction_id, round, Decimal(price_point))` and contains unique
instructions, not duplicated switch legs.

## 4. Structural upper bound

Two instructions within a tie block can interact only if they share at least one state constraint:

1. the same FRN, because processed activity is checked against bidder eligibility; or
2. the same market-product key, because a reduction is checked against product supply/demand.

A tie block contributes to (U_a) only if at least one instruction with a public `N` result flag
has another instruction in the block sharing its FRN or one of its touched products. This is a
necessary but not sufficient condition for order sensitivity: a replay may show that the two
operators still commute or that the rejected instruction stays rejected under every permutation.
Therefore (U_a) is deliberately an upper bound and cannot be used as an effect count.

## 5. Permitted aggregate output

For each auction the output may contain only source hashes, schema version, the frozen threshold,
Boolean integrity/pass flags, and integer counts of:

- bid and result rows;
- reconstructed instructions and unmatched touched products;
- all tie blocks, multi-instruction tie blocks and structurally coupled tie blocks;
- instructions with any `N` flag; and
- structurally coupled tie blocks in (U_a).

No bidder, FRN, market, product, round, price point, selection number, rank, outcome contrast,
regression coefficient or cascade statistic may be printed or persisted.

## 6. Interpretation boundary

If the support prefilter passes, the route remains a candidate. It must still establish
exchangeability, deterministic zero-discrepancy first-stage replay, cross-auction mechanism
compatibility, a twenty-primary-work novelty audit and source-level faithful-simulator feasibility.
No current result can authorize EcoMD integration or GPU work.
