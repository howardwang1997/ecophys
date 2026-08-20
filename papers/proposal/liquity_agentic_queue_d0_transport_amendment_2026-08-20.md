# Liquity Agentic Queue D0: Transport-Only Amendment v2

**Parent scientific freeze:** `liquity_agentic_queue_d0_v1.yaml`, SHA-256
`b4a45e62cef5c0b0826da5a382a1b4762f130c489340b6f78b3e54d427690c14`

**Amendment time:** 2026-08-20 04:23:09 UTC

**Outcome access before amendment:** no numerical protocol outcome, queue rank, rate direction, debt,
collateral, redemption value, price, liquidation, causal estimate, or support-gate breakdown

## Why an amendment was necessary

The v1 run completed the Blockscout formal scan with 24,291 allowed support events. During dRPC replication,
the two transports matched exactly through chunk 109. On chunk 110 (blocks 23,573,043–23,583,042), Blockscout
returned 42 identities while dRPC returned 15. Repeating the identical dRPC query returned 14. The omission was
one-way: 27 identities present in Blockscout were absent from the first dRPC result. Because disjoint later
chunks cannot restore missing historical identities, the run was interrupted before support summarization.

The discrepancy was localized by branch. Blockscout returned 30 WETH, 12 wstETH, and zero rETH events; dRPC
returned 3/11/0 and then varied on repeat. Thus dRPC is not a valid log-completeness witness for this audit.

## Replacement qualification

The official OnFinality page documents the rate-limited public Ethereum endpoint
`https://eth.api.onfinality.io/public`. Before promotion:

- OnFinality reproduced all 42 chunk-110 canonical identities exactly, with no identities exclusive to either
  endpoint.
- It exactly reproduced all three source-blind qualification shards: 0, 50, and 38 events.
- It returned chain ID 1 and the exact frozen end-block header.
- It does not provide historical state at the frozen end block through the public endpoint, so it cannot replace
  the state witness.

The v2 role split is therefore:

- Blockscout: formal complete event acquisition, block headers, and deployment bytecode;
- OnFinality: independent complete event-identity replication and block headers;
- dRPC: independent frozen-height block header and deployment-bytecode witness only.

No provider is trusted for a capability it failed. Full Blockscout/OnFinality event-identity equality remains
mandatory before any support metric is accepted.

## Scientific invariance

The v2 runner loads v1 and validates its exact digest. It rejects v2 unless these sections are byte-equivalent as
parsed YAML:

- official source commits and file hashes;
- chain, block interval, end hash/timestamp, contracts, branches, and official ARM identities;
- event signatures and operation codes;
- proximity-window definition;
- every pass threshold;
- forbidden data and stop rules;
- CPU/GPU/data resource limits.

The formal Blockscout endpoint, 10,000-block span, pacing, retries, three qualification shards, nonempty-shard
minimum, and full-union replication requirement also remain unchanged. The only substantive transport change is
`replication_rpc: dRPC -> OnFinality`; dRPC becomes `state_witness_rpc`. Tests deliberately alter a scientific
threshold and the state witness and confirm that both changes are rejected.

## Decision consequence

This amendment neither passes nor fails D0. It authorizes one clean v2 rerun. Exact full-union mismatch on
Blockscout versus OnFinality is a transport hard stop. If transport passes, the original v1 sample-support gates
are evaluated once. No further provider replacement may modify any scientific field.
