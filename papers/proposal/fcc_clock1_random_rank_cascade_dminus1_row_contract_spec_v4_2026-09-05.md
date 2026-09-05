# FCC clock-1 randomized rank cascade — Auction 108 row-contract diagnostic v4

**Frozen:** 2026-09-05, before reading unmatched-row bid or start-of-round prices

**Parent:** `fcc_clock1_random_rank_cascade_dminus1_row_contract_spec_v3_2026-09-05.md`

## Correction of a failed diagnostic

V3 incorrectly operationalized “lowest possible price” as price point 0. The already inspected official
file-format definition states that every Round 1 price point is 1 because the only permitted bid price is
the minimum opening price. V3 consequently returned 8,113 nonzero price points and cannot discriminate
the missing-bid explanation; this is a specification error, not evidence against it.

V4 may read `price` and `start_of_round_price` only for the already isolated 8,113 unmatched Round 1
quantity-0 rows. It may emit only the aggregate counts with `price == start_of_round_price` and
`price != start_of_round_price`; no value or additional partition may be emitted. Combined with the
official Bids-file definition—a system-created missing bid is simple, quantity 0, at the lowest possible
price—equality for every row identifies the absent-result records as system-created zero-demand
placeholders. Any inequality leaves the row contract unresolved. All other v1/v2 restrictions and the
ban on effects, simulation, fitting, and GPU use remain in force.
