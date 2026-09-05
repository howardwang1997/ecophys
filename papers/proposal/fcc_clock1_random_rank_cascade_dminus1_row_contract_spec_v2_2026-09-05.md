# FCC clock-1 randomized rank cascade — Auction 108 row-contract diagnostic v2

**Frozen:** 2026-09-05, before emitting any unmatched-row quantity summary

**Parent:** `fcc_clock1_random_rank_cascade_dminus1_row_contract_spec_2026-09-05.md`, SHA-256
`71a2eec3bf1e06ea3c1814745dd6b5a9f8623cc16aa182bf119780889630ebf7`

## Narrow repair

The v1 diagnostic closed all row accounting, found zero impossible transitions among matched rows,
and localized all 8,113 missing joins to `round1_simple`. It emitted no quantity breakdown for that
class. Because the Auction 108 Technical Guide says a bidder may submit only quantity 1 in Round 1,
the frozen class is still too coarse to distinguish an unexplained missing outcome from a public-file
placeholder convention.

V2 changes no join, class, transition check, or decision threshold. It may additionally emit the four
global cells `(round1_simple, quantity in {0,1}, matched/unmatched)`, suppressing any cell below 10.
No other new field, partition, identifier, outcome, or statistic is authorized. If any unmatched Round 1
row has quantity 1, the public-file discrepancy remains an action-changing replay blocker unless an
official source supplies a different exact row semantics. Quantity 0 would still require an official
source establishing a state-redundant placeholder; the empirical partition alone cannot pass the gate.
