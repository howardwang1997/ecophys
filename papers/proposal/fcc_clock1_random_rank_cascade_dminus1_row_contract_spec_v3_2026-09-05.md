# FCC clock-1 randomized rank cascade — Auction 108 row-contract diagnostic v3

**Frozen:** 2026-09-05, before joining the unmatched Round 1 zero rows to their price-point class

**Parent:** `fcc_clock1_random_rank_cascade_dminus1_row_contract_spec_v2_2026-09-05.md`

## Narrow source-concordance check

V2 found that all 8,113 unmatched rows are `round1_simple` with quantity 0, while all 12,202
Round 1 quantity-1 bids have matched, fully applied demand 1. The official Auction 108 Bids-file
schema defines a system-created “missing bid” as a simple quantity-0 bid at the lowest possible price;
the Auction 108 Technical Guide separately says a bidder may submit only quantity 1 in Round 1 and
that processed Round 1 demand is exactly the set of licenses bid for.

The program may reuse the already support-authorized `price_point` field solely to emit two integers:
the number of unmatched Round 1 quantity-0 rows whose price point is exactly 0 and the number whose
price point is nonzero. It may emit no exact price point, price, selection number, row, identifier, or
further partition.

If every unmatched row has price point 0, the conjunction of the two official rules classifies it as a
system-created zero-demand missing-bid placeholder, and initializing its absent result state to zero is
mechanically unique. Any nonzero record keeps the public row contract unresolved. This check still does
not validate the later-round queue replay or authorize effect estimation, simulation, fitting, or GPU use.
