# Experiment 138 — SQD nine-chain zero-target qualification

**Frozen:** 2026-08-19, before any SQD event/log/transaction row is requested  
**Status:** free source feasibility only; not an Aave result and not an NCS claim  
**Resources:** public SQD Portal, three existing nodes, CPU/network only, no purchase

## Question and contamination boundary

Can the public SQD Portal reproducibly supply finalized block headers across the nine EVM chains required by
the candidate mechanism backend? This version requests only metadata, finalized heads and block headers. The
request builder has no event collection arguments. It must not contain an Aave address, event topic, log,
transaction, trace or state-diff filter.

No protocol outcome, contract activity or target row may be inspected before this protocol and code are
committed. A pass is source qualification `Q0a`; it does not unlock the Aave extraction or support an economic
claim. Target extraction remains locked until a second frozen audit validates non-target join fixtures,
cross-provider hashes, data-use terms and an immutable snapshot procedure.

## Frozen universe and sampling

Use the nine dataset slugs in `config.yaml`: Arbitrum, Avalanche, Optimism, Polygon, Base, Gnosis, BNB Chain,
Linea and Scroll. For each dataset, capture `/metadata` and `/finalized-head` once. From the returned immutable
bounds select inclusive six-block windows at 10%, 50% and 90% of history, plus 2,048 blocks before the
finalized head. Duplicate windows caused by a very short chain are de-duplicated.

Each window is requested twice from `/finalized-stream`, using `includeAllBlocks=true` and only block number,
hash, parent hash and timestamp fields. Network shards are assigned by dataset index modulo the declared shard
count; shard assignment changes neither the selected blocks nor any threshold.

## Frozen gates

Every network must satisfy all of the following:

1. metadata and finalized-head calls succeed within four attempts;
2. every requested block is returned exactly once and in increasing order;
3. hashes are well formed and unique, adjacent parent hashes link exactly, and timestamps do not decrease;
4. the two repeats have identical canonical block content;
5. returned records contain no event collections;
6. at most 10% of HTTP requests require a retry and median successful-request latency is at most 10 seconds.

Any missing network is an overall failure. Raw response hashes, selected heights, latency and retry counts are
retained. Thresholds cannot be changed in this experiment version.

## Interpretation and next decision

- **PASS:** proceed to a separately frozen `Q0b` audit using non-Aave join fixtures and an independent block
  provider, then decide whether to extract a small immutable training-only Aave shard.
- **FAIL:** diagnose coverage/API integrity or replace the source. Do not relax gates after seeing failures.

This experiment deliberately does not exercise transaction/log joins, estimate market mechanisms or use a
GPU. Its value is preventing an expensive downstream analysis from being built on an unqualified data path.
