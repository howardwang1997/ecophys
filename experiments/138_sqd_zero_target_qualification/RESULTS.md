# Experiment 138 results — SQD nine-chain zero-target qualification

**Run date:** 2026-08-19
**Frozen source commit:** `9357600d1`
**Decision:** Q0a PASS; event/target extraction remains locked

## Result

The three-node run covered all nine declared SQD datasets. It made 90 public API requests: metadata and a
finalized head for each network, plus two repeats of four six-block header windows per network. All 36 windows
returned exactly the requested heights, valid unique hashes, exact adjacent parent links, nondecreasing
timestamps and no event collections. Repeat content was identical in all 36 cases.

Across the 72 stream calls, the median latency was 0.424 seconds, the empirical p95 was 0.777 seconds and 2/72
(2.78%) required a retry. All three shard gates passed:

| Worker | Networks | Requests | Retry fraction | Median latency |
|---|---|---:|---:|---:|
| V100-A CPU | Arbitrum, Polygon, BNB | 30 | 0% | 0.475 s |
| V100-B CPU | Avalanche, Base, Linea | 30 | 6.67% | 0.396 s |
| RTX2060 CPU | Optimism, Gnosis, Scroll | 30 | 0% | 0.326 s |

## Decision boundary

This is a data-path result, not evidence for a DeFi mechanism or a market model. The code requested no logs,
transactions, traces, state diffs, Aave addresses or event topics. Therefore it neither contaminates the future
target analysis nor validates transaction/log joins.

Before any Aave extraction, Q0b must be frozen and pass on non-Aave fixtures: transaction/log joins,
independent-provider block hashes, gap/duplicate handling, immutable shard export and explicit data-use terms.
Only then may a small training-only target shard be considered. Test outcomes remain unopened.
