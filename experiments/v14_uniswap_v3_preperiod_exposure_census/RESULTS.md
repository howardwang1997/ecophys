# Uniswap v3 U1R full-population preperiod exposure census result

**Protocol commit:** `ab722229d305220c23ec53d268a91d854a6a4e31`

**Collection:** 2026-08-15 11:22:10--11:31:20 UTC

**Decision:** `FAIL_FULL_PREPERIOD_EXPOSURE_SUPPORT_KEEP_UNISWAP_M2_ONLY`

## Outcome

The run completed the exact 1,000-pool U0 population and passed ten of eleven conjunctive gates. It failed the
frozen swap event-count concentration gate: pool `0x919f...af79` supplied 2,625 of 8,722 swaps, or 30.096%, above
the maximum 25%. The threshold cannot be relaxed after observing the result.

The failure is not a lack-of-support result. In the frozen preperiod:

- 89 pools were swap-active;
- 25 pools were position-action-active;
- 91 pools had either event type: 23 had both, 66 swaps only, two position actions only, and 909 neither;
- there were 8,722 swaps and 353 position actions;
- NPM managed 212/353 position actions, a 60.057% action-count share;
- the largest pool supplied 102/353 position actions, or 28.895%, below the frozen 50% cap.

All count, fee-class and NPM gates passed. Nevertheless, the protocol is conjunctive, so these facts do not
authorize controls, identity expansion or response access.

## Fee-class support

| Packed fee | Pools | Event-active | Swap-active | Position-active | Swaps | Position actions |
|---:|---:|---:|---:|---:|---:|---:|
| `0x44` | 107 | 15 | 15 | 4 | 2,004 | 106 |
| `0x66` | 893 | 76 | 74 | 21 | 6,718 | 247 |

These are event counts in the first two propagation batches, not volume, liquidity, value at risk or a Uniswap-
wide prevalence estimate. The RPC transferred event payloads and indexed participants as part of standard logs,
but the collector decoded no economic amount and retained no raw payload or non-NPM manager address.

## Integrity and independent verification

- 1,000 census rows and 1,000 unique pools reproduce the U0 ledger in exact order;
- all 1,000 root log requests use exact frozen topics and bounds; the only saturated pool required six child
  requests, forming four non-overlapping terminal intervals inside the same window;
- 1,009/1,009 responses succeeded on the first attempt: one chain ID, two block headers and 1,006 log queries;
- 9,075 normalized events and 10,463,695 response bytes stayed below all hard caps;
- duplicate and conflicting normalized-log counts are both zero;
- the 16 U1a pools match the census exactly on swap, mint, burn, collect, total position and NPM counts;
- all summary totals, fee partitions, shares, request counts and artifact hashes were independently recomputed;
- the end header is 12 seconds before treatment; no control or treatment/post-treatment event was opened;
- focused tests, Ruff and strict mypy pass after collection.

## Artifact hashes

| Artifact | SHA-256 |
|---|---|
| Frozen contract | `ff8c48cc40e4f2e79da638019138621591a69cacc4d9da1a5636689d322aa6ee` |
| Exposure census | `677483727bfd7d1537640221bb3b7441f2227e5907a5abfa4b5d67370c5bf72f` |
| HTTP response-hash manifest | `d2e6bd367538f31bdbdfe00059c093a167de5b9715c2c7f412d2ca9ba48c1334` |
| Summary | `3ddff9cd49570a85f3c658533266a05539068624cf9385dd008147237adf0d6c` |

## Disposition

Do not exclude the dominant pool, raise the 25% cap, reweight by an outcome discovered later or open U2 on this
frame. Uniswap remains the validated exact-M2 mechanism case. The concentration pattern may be characterized only
as explicitly post-hoc, pre-treatment description using these already consumed counts; it cannot repair U1R.
Participant adaptation M3/M4 must move to another real system or await a genuinely new, independently frozen
event and control frame.

Compute use was local CPU/network only. Paid data, remote workers, both V100s and the RTX 2060 were unused; GPU
hours were zero.
