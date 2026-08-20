# Liquity Agentic Queue D0: Resumable Transport Recovery v3

**Operational status:** superseded by v4 after the first v3 attempt preserved four chunks but again exhausted
OnFinality's documented public response-unit bucket. The scientific contract and this audit history remain
binding; see `liquity_agentic_queue_d0_weighted_rate_limit_amendment_2026-08-20.md`.

**Parent transport freeze:** `liquity_agentic_queue_d0_v2.yaml`, SHA-256
`221145272f3549e8a773e314fa788a6986ebc8b5fd291b5879e8f3377e66d7be`

**Recovery freeze:** `liquity_agentic_queue_d0_v3.yaml`, SHA-256
`958797c8126d6168cc2e59c711a4e480e10b8c78e6b6c92db4f0c59252aba4e8`

**Amendment time:** 2026-08-20 05:30:35 UTC

**Outcome access before amendment:** no support-gate breakdown, numerical rate, debt, collateral, redemption
value or price, queue rank, adjustment direction or size, liquidation outcome, market outcome, causal estimate,
EcoMD output, or GPU result

## Why v2 did not complete

The v2 formal run reproduced the three qualification shards exactly at 0, 50, and 38 allowed events. Blockscout
then completed all 331 fixed 10,000-block chunks with 24,291 allowed events. OnFinality independently reached
these exact cumulative checkpoints:

| Completed chunk | Blockscout | OnFinality |
|---:|---:|---:|
| 25 | 2,507 | 2,507 |
| 50 | 3,939 | 3,939 |
| 75 | 6,110 | 6,110 |
| 100 | 8,126 | 8,126 |

Before the next printed checkpoint at chunk 125, OnFinality returned HTTP 429 after all seven frozen retries:
`Too Many Requests, Please apply an OnFinality API key or contact us to receive a higher rate limit`. The
runner exited with code 1 and wrote no result manifest. It had not attached relevant timestamps or called the
support summarizer. This is a public-transport capacity failure, not a failed sample gate or a test of the
research hypothesis.

The v2 runner queried each of three TroveManager addresses separately because Blockscout rejects address arrays.
That compatibility decomposition was unnecessarily imposed on OnFinality, which accepts the standard address
array. The failed run also had no persistent progress record, so a retry would have repeated all successful
queries.

## Frozen recovery

Version 3 changes only two operational properties of the OnFinality replication pass:

1. Query all three frozen TroveManager addresses in one address-array filter for every unchanged 10,000-block
   chunk.
2. After every completed chunk, atomically save a tamper-evident external checkpoint. A later clean run resumes
   from the longest verified contiguous prefix.

The checkpoint contains only the already allowed block number and canonical identity fields: block hash,
transaction hash, log index, contract address, and event topic. It never stores raw RPC responses or event data
words. Its identity binds the exact v3 config hash, Git SHA, provider, block interval, chunk span, address set,
topic set, and address-grouping rule. Every chunk and the entire checkpoint have canonical SHA-256 digests.
Loading rejects non-contiguous chunks, out-of-range blocks, unknown addresses or topics, duplicate identities,
non-canonical fields, a changed Git/config identity, or any digest mismatch. The checkpoint must reside outside
the Git worktree so every formal attempt still starts from a clean repository.

The Blockscout formal scan remains one-address-per-query. Before freezing v3, the previously disclosed chunk 110
was used only as a transport capability test. Blockscout's three single-address filters and OnFinality's one
three-address filter both returned 42 events with exact canonical identity digest
`c42e2b7e7c46a590a08097d5fcded8bf4e7156ef3dff75d07db0748644b6649d`. No new support metric was opened.

## Scientific and protocol invariance

The v3 runner loads the exact v2 parent and recursively validates v2 against the original outcome-blind v1.
It rejects v3 unless all official sources, chain anchors, contracts, branches, event signatures, operation codes,
support windows, pass thresholds, forbidden fields, stop rules, and resource limits equal the parent. It also
requires every existing transport field to remain equal, including:

- Blockscout, OnFinality, and dRPC role assignments;
- 0.25-second minimum pacing;
- seven rate-limit retries and the original backoff schedule;
- 10,000-block maximum span;
- all three qualification shards;
- the exact full-identity replication requirement.

The only new fields require combined replica-address filters, checkpoint schema 1, and an atomic checkpoint after
every chunk. Ten focused tests, Ruff, and strict mypy pass. Tests cover parent/scientific tampering, inherited
transport tampering, address grouping, exact-prefix resumption, and checkpoint tampering.

## Decision consequence

Version 3 does not pass D0. It authorizes a resumable clean rerun using an external checkpoint. A 429 or other
transport error preserves completed sanitized chunks but produces no scientific decision. Exact full-interval
identity mismatch is still a hard transport stop. Only complete equality permits the original v1 support gates
to be evaluated once. Neither the checkpoint nor transport recovery authorizes D1, queue outcomes, EcoMD, or GPU
work.
