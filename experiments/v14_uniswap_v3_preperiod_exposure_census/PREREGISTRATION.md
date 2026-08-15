# Uniswap v3 U1R full-population preperiod exposure census

**Frozen:** 2026-08-15 11:17:00 UTC

**Role:** historical development route reset after a negative pilot

**Response lock:** no treatment-block or post-treatment pool event, outcome, control behavior or identity history
may be queried

## Question

Does the exact 1,000-pool U0 propagation prefix contain a sufficiently broad pre-treatment event-active subset to
justify a new control and identity design?

U1a found only three swap-active and one position-active pool among 16 hash-selected pools. This census is not a
top-up of that failed sample. It applies one uniform query to every U0 pool, including the 16 already consumed
pools, and changes the estimand to the complete disclosed U0 prefix. Its thresholds were chosen after seeing U1a,
so a pass is development evidence rather than pristine confirmation.

## Frozen population and window

Use every row of the committed U0 treatment ledger in ledger order, with no replacement or behavioral selection:
1,000 unique pools, including 107 packed-fee `0x44` and 893 `0x66` rows. The canonical population projection has
SHA-256 `bdfad0b57a8873bbb3ff95c28598d4b3869a019284163ca269c0d9f0adafbcd9`. This is the exact first two
propagation batches, not all Uniswap v3 pools and not a representative sample of them.

Read only blocks 24,548,777 through 24,599,176 inclusive, the same 50,400-block interval used by U1a. Fetch both
boundary headers and require the final timestamp to be strictly before the first pool-treatment block 24,599,177.

## Query and retention rules

For each pool, issue one Blockscout JSON-RPC `eth_getLogs` request with topic-0 OR over `Swap`, `Mint`, `Burn` and
pool `Collect`. Address-array batching is prohibited because the deployed endpoint rejected the official JSON-RPC
array shape during a preflight on already consumed U0 mechanism data; topic-0 OR succeeded on that same data. A
response of exactly 1,000 logs is treated as saturated and its inclusive block interval is recursively bisected.
Only leaves below 1,000 are accepted; a saturated single block fails the run.

An adapter-only empty-result probe also confirmed acceptance of the full frozen block range. The first probe had
a disclosed lower-bound hexadecimal transcription error (64 extra earlier blocks); it returned zero events and
was immediately repeated with the exact frozen bounds, also returning zero. Neither probe addressed a pool or
opened market behavior.

The RPC response necessarily transfers event data plus indexed pool participants. The collector does not decode
amount, price, tick, liquidity or token-amount fields and discards raw responses. It decodes the indexed manager
for position actions only long enough to count the official NonfungiblePositionManager share and the number of
distinct managers. Non-NPM addresses are not retained. Per-pool output contains event counts, activity flags,
NPM counts/shares, a distinct-manager count and an irreversible normalized-event hash.

No transaction envelope, calldata, transaction sender, token ID, transfer history, control behavior or
treatment/post-treatment pool event may be opened.

## Frozen gates

All gates are conjunctive:

1. exactly the 1,000 U0 pools and exact pre-treatment interval;
2. all terminal log partitions below 1,000, with zero duplicate or conflicting normalized logs;
3. at least 50 swap-active pools, at least 20 position-active pools and at least 200 position-action logs;
4. in each packed-fee class, at least five swap-active and two position-active pools;
5. aggregate NPM share at least 0.50 by position-action count;
6. the largest pool contributes no more than 0.25 of swaps and no more than 0.50 of position actions.

These thresholds are support and concentration checks, not effect-size hypotheses. They were informed by the U1a
failure and cannot be represented as preregistered confirmation. A pass unlocks only a separately committed,
outcome-blind control-source protocol and a separate identity design. It does not unlock U2 or establish a causal
effect. A failure keeps Uniswap as an exact-M2 mechanism case and moves M3/M4 elsewhere; thresholds, window and
population cannot be repaired on this frame.

## Resource ceiling

- expected unsaturated path: 1,003 successful responses, about 8.4 minutes at two requests per second;
- hard ceiling: 5,000 HTTP attempts, 512 MiB response bytes and 1,000,000 normalized events;
- compute: local CPU/network only, expected below one CPU core-hour;
- paid data: zero;
- GPU: zero; both V100s and the RTX 2060 remain idle;
- H20: excluded.
