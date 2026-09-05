# FCC clock-1 randomized rank cascade — support-only prefilter v2

**Frozen:** 2026-09-05, before re-reading Auction 108 or Auction 110 data rows

**Parent freeze:** `fcc_clock1_random_rank_cascade_dminus1_freeze_2026-08-24.md`

**Superseded support specification:**
`fcc_clock1_random_rank_cascade_dminus1_support_spec_2026-09-04.md`, SHA-256
`eeeda81b539c6efa02d6ab2ccc0f4d36e6b2d6c56edbb2243d24e7b3402c419c`

**Failed v1 implementation:** `scripts/fcc_clock1_support_audit.py`, pre-repair SHA-256
`94c3b59c351d9f624e96b208bdd776b719a9b1ffdcd0049878502768b307bee4`

## 1. Why v1 stopped

The v1 program produced a valid aggregate result for Auction 113: 53 structurally coupled tie
blocks with an `N` flag, above the provisional floor of 30. It emitted no Auction 108 or Auction 110
support statistic. Both archives failed the frozen switch-integrity check because their two public
rows for one switch instruction do not share the same `selection_number`; the aggregate diagnostics
were respectively 710/355 and 118/59 malformed/missing-price instruction records.

No identifier, bid value, market, round, price point, rank or effect was emitted. The repair below
uses only the already-inspected official file-format definition and is not selected from a support
outcome.

## 2. Correct switch atom from the official schema

The official Auction 108 and 110 file formats state that a switch bid has two public rows:

- the `from`-product row has non-null `switch_to_category` and the operative price point;
- the `to`-product row has non-null `switch_from_category`, while its reported price point is always
  1 regardless of the `from` product's price point.

The v2 atom therefore keeps only the `from`-product row. It constructs the instruction's touched
product set from `(market, category)` and `(market, switch_to_category)`. The display-oriented
`to`-product row is counted and discarded. It is never joined by selection number and never becomes
a second instruction. A switch row with neither or both orientation fields populated fails closed.

Simple bids and Auction 113 instructions are unchanged. All input hashes, field whitelists, tie
blocks, coupling conditions, threshold, aggregate-only output restrictions and interpretation
boundaries from v1 remain frozen. The v2 output may additionally report only the integer number of
discarded switch `to` rows.

## 3. Decision rule

Auction 108 and 113 remain the two clock-1 systems. Let (U_a) retain the v1 meaning: an upper bound
on tie blocks containing an `N`-flagged instruction with a same-FRN or same-product neighbor. If
either (U_{108}<30) or (U_{113}<30), close for insufficient replicated support. Values at or above
30 pass only this support prefilter; all remaining D−1 gates stay closed.
