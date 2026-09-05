# FCC clock-1 randomized rank cascade — Auction 108 row-contract diagnostic

**Frozen:** 2026-09-05, before reading `quantity`, `previous_round_processed_demand`, or any
unmatched Auction 108 row

**State:** D−1 schema-integrity diagnostic only; no effect estimation or experiment authorization

**Parent:** `fcc_clock1_random_rank_cascade_dminus1_freeze_2026-08-24.md`

## 1. Pre-observed discrepancy

The support-only v2 program used only its frozen whitelist and established the following aggregate
set relation for the official Auction 108 archives:

- 665,637 bid-product keys;
- 657,524 result-product keys;
- every result key is a bid-product key; and
- 8,113 bid-product keys have no result row.

The official public-reporting schema says that the Results file contains a record for a product when
the bidder had prior processed demand and/or submitted a bid. The discrepancy therefore cannot be
silently treated as harmless. It may reflect a documented display convention, a mistaken bid atom,
or missing public replay state.

## 2. Rival explanations

- **R1 — report convention:** the unmatched records are a mechanically recognizable class that has
  no independent state transition (for example, a display-only leg) and the public files still close
  the state transition exactly.
- **R2 — parser/key error:** the unmatched records arise from an incorrect interpretation of a
  public row or join key and disappear under the official schema.
- **R3 — replay-state loss:** some action-changing instructions lack the public outcome/state needed
  for deterministic replay. This fails the D−1 first-stage replay gate.

The diagnostic is designed to separate these explanations, not to rescue the candidate.

## 3. Newly authorized fields and transformations

The program may read the already authorized join fields plus only these Auction 108 bid fields:

- `bid_type`, `quantity`, `previous_round_processed_demand`;
- `switch_from_category`, `switch_to_category`; and
- `round` only through the Boolean bucket `round == 1`.

It may additionally read `processed_demand` from the Results file. It must not read or emit names,
prices, exact rounds, markets, products, selection numbers, free-text processing details, bidder
status outcomes, or any downstream response.

Each public bid row is classified before joining as one of:

- `round1_simple`;
- `simple_maintain` (`previous=1, quantity=1`);
- `simple_reduce` (`previous=1, quantity=0`);
- `simple_increase` (`previous=0, quantity=1`);
- `simple_noop_zero` (`previous=0, quantity=0`);
- `switch_from`; or
- `switch_to`.

Blank or invalid states fail closed. The result join remains exactly
`(round, frn, market, category)`. The program reports only global integer counts by the seven frozen
classes and match status. For matched rows it may also report counts by
`(class, fully_processed_flag, processed_demand)`; no cell with fewer than 10 records may be emitted.
It also reports result-only keys, duplicate keys, invalid rows, and accounting equalities. No row or
identifier may be retained in output.

## 4. Decision rule

R1 or R2 passes this diagnostic only if all 8,113 missing joins are exhausted by a single
schema-supported, state-redundant class and the remaining matched transition table has no impossible
state transition. A merely convenient empirical pattern is insufficient: the corresponding reporting
rule must be located in an official source.

If any unmatched record is an action-changing simple instruction or `switch_from`, if accounting does
not close, or if no official source explains the exhausted class, classify the discrepancy as R3 and
fail the deterministic replay gate. Passing this diagnostic removes only the row-contract blocker; it
does not validate the processor, identify a causal estimand, establish novelty, or authorize a
simulator, EcoMD integration, model fitting, outcome analysis, or GPU work.
