# Liquity Agentic Queue D0: Weight-Aware Public-Rate-Limit Recovery v4

**Parent recovery freeze:** `liquity_agentic_queue_d0_v3.yaml`, SHA-256
`958797c8126d6168cc2e59c711a4e480e10b8c78e6b6c92db4f0c59252aba4e8`

**Weight-aware freeze:** `liquity_agentic_queue_d0_v4.yaml`, SHA-256
`e0652a56245310ced9dd2f838cca9775ffe0ce3b3f9caa1b00ed44f9ca533996`

**Amendment time:** 2026-08-20 06:01:35 UTC

**Outcome access before amendment:** no support-gate breakdown, numerical protocol outcome, queue state, market
outcome, causal estimate, EcoMD output, or GPU result

## What v3 established and why it stopped

The clean v3 run again reproduced qualification counts 0/50/38 and Blockscout's complete 24,291-event formal
surface. It then wrote four valid external replica checkpoints containing 129 canonical identities. The combined
OnFinality request for chunk 5 failed with HTTP 429 after the inherited seven retries. No result manifest was
written, and the timestamp attachment and support summarizer had not run.

A Blockscout transport diagnostic found 105 allowed events in chunk 5: 45 WETH, 50 wstETH, and 10 rETH. This
initially suggested that the combined response might be too heavy for the public endpoint's token bucket. A
post-cooldown repeat falsified the strong form of that interpretation: the same combined request returned all 105
events without splitting and matched Blockscout exactly, with identity digest
`355a754eaba659c30933a75d171d11e749c7a406b58240e917d3919b9b4e31e6`. The supported conclusion is narrower:
the public bucket lacked enough response units at the v3 retry times; the combined query itself is serviceable
when sufficient capacity is available.

## Official capacity constraint

OnFinality's [Public Rate Limits](https://documentation.onfinality.io/support/public-rate-limits), retrieved
2026-08-20, lists Ethereum at 10 response units per minute with a burst of 10. The same documentation states that
limits apply to response units rather than merely request counts and may change without warning. OnFinality's
[Response Units](https://documentation.onfinality.io/support/response-units) page explains that intensive
Ethereum methods can have higher weights. Consequently, the v1-v3 0.25-second replica pacing was inconsistent
with the documented public service even though exponential retries sometimes hid the mismatch.

## Frozen v4 recovery

Version 4 retains v3's combined address filter and per-chunk tamper-evident checkpoint, then adds a replica-only
capacity policy:

- minimum 6.1 seconds between OnFinality requests, just slower than the documented 10-per-minute rate;
- two rate-limit retries under the same frozen backoff parameters;
- after exhausted 429 or `-32029`, split the query by address first;
- if a single-address response still cannot be served, bisect its block range;
- cap the adaptive recursion at 32 levels and fail rather than omit data.

Every split is a disjoint partition of the same frozen address/topic/block product. The formal Blockscout query,
10,000-block outer chunks, event set, exact-identity comparison, and support thresholds do not change. The
checkpoint still commits only a whole outer chunk after every subquery succeeds, so a partial adaptive traversal
cannot masquerade as completed coverage.

The four v3 chunks are not migrated because the checkpoint deliberately binds the v3 config and Git SHA. Version
4 starts a new external checkpoint; this sacrifices four transport chunks to preserve provenance.

## Invariance and tests

The runner recursively validates v4 against v3, v2, and the original outcome-blind v1. It rejects changes to any
official source, chain anchor, contract, branch, event signature, operation code, support window, sample gate,
forbidden field, stop rule, resource limit, provider role, qualification shard, or existing transport setting.
Only the replica pacing, retry count, exhausted-limit splitting rule/order, and maximum split depth are added.

Thirteen focused tests, Ruff, and strict mypy pass. The new tests require address splitting before range
splitting, exact recursive range coverage, inherited-field invariance, checkpoint resumption, and tamper
rejection.

## Decision consequence

Version 4 authorizes another clean, resumable transport attempt. A persistent one-block/one-address 429, exhausted
split depth, identity mismatch, or any original support failure remains a hard stop. Transport recovery does not
authorize D1, numerical queue reconstruction, EcoMD, or GPU work.
