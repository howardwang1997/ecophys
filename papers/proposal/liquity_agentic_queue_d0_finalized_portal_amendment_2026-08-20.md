# Liquity V2 D0: Finalized SQD Portal Transport Amendment

**Frozen:** 2026-08-20 06:54:43 UTC

**Config:** `configs/empirical_physics/liquity_agentic_queue_d0_v5.yaml`

**Config SHA-256:** `22046333a9d1f16a75eaf2acb91c0f25272c2e344a5b7d7b1229ea31dba30edb`

**Parent:** v4 SHA-256 `e0652a56245310ced9dd2f838cca9775ffe0ce3b3f9caa1b00ed44f9ca533996`

**Scope:** replace only the overloaded public JSON-RPC log replica with a finalized SQD Portal identity stream.
All event definitions, branches, dates, support thresholds, forbidden fields, stop rules, and resource limits remain
exactly equal to v1 through the recursively audited v2--v4 chain.

## Why v4 was stopped

The clean v4 run again reproduced the three frozen qualification counts `0/50/38` and Blockscout's 24,291
allowed-event total. Its external OnFinality checkpoint contained the first four 10,000-block chunks and 129
sanitized identities. Chunk 5 continued to return HTTP 429 after the frozen 6.1-second pacing, two retries,
address-first partitioning, and subsequent block-range bisection; subranges near ten blocks were still rejected.
Continuing that tree would have created an unbounded number of public-endpoint requests, so the run was stopped to
respect the preregistered 12-core-hour/free-resource envelope.

The runner had not attached relevant timestamps, called the support summarizer, written a result manifest, or
decoded any forbidden numerical field. This is a failed transport attempt, not a support-gate or scientific
result. The v4 checkpoint is retained externally but cannot be migrated into a different config/Git identity.

## Free-source selection

The replacement remains a second independent public index, not an Ethereum JSON-RPC alias:

- dataset: `https://portal.sqd.dev/datasets/ethereum-mainnet`;
- API: finalized EVM Portal stream documented by SQD;
- metadata at screening: dataset `ethereum-mainnet`, `start_block=0`, `real_time=true`;
- frozen block 25,792,512 was below the advertised finalized head;
- the Portal returned the exact frozen end hash `0x608302fd...44106d` and timestamp `1787182931`.

The protocol semantics were audited against `@subsquid/portal-client` 0.4.0, npm shasum
`410f563cb33776c480e36ff2146a238fe2d63663`. The official client patches every EVM selection with block number,
hash, and parent hash; consumes newline-delimited blocks; resumes at the last returned block plus one; and binds
the next request to the last returned block hash. The local Python client implements and validates those same
cursor rules against the finalized endpoint.

Alternatives were not used: the current Google Blockchain Analytics query would process about 0.87 TiB and could
be billable depending on billing-account free-tier use; the Liquity subgraph lacks canonical event-log identities;
BlastAPI is deprecated; and 1RPC did not serve the frozen historical block through its advertised public endpoint.
The v1 contract permits zero paid-data dollars, so a possibly billable BigQuery run was not authorized.

## Outcome-blind qualification

Before v5 was frozen, only already allowed log identities were compared. No event payload value or support-gate
breakdown was opened.

| Interval | Blocks | Events | Canonical identity SHA-256 | Equal to Blockscout |
|---|---:|---:|---|---|
| Known dRPC omission | 23,573,043--23,583,042 | 42 | `c42e2b7...6649d` | yes |
| Frozen qualification 0 | 22,483,043--22,493,042 | 0 | `4f53cda1...b945` | yes |
| Frozen qualification 1 | 24,130,000--24,139,999 | 50 | `5b11b4fc...d179` | yes |
| Frozen qualification 2 | 25,780,000--25,789,999 | 38 | `65572283...970c` | yes |
| Previously blocked chunk 5 | 22,523,043--22,533,042 | 105 | `355a754e...31e6` | yes |

The exact five-interval screen used 50 Portal requests, zero retries, and 275,792 NDJSON bytes. A separate earlier
screen encountered one explicit HTTP 529 overload response; v5 therefore permits four bounded retries with
exponential backoff. Retry exhaustion remains a hard transport failure and can never be interpreted as an empty
event interval.

## Frozen v5 execution

The formal run must start from a clean commit and a new external checkpoint bound to the v5 config hash, Git SHA,
Portal dataset and stream endpoint, frozen range, filters, timeout, and retry settings.

1. Verify pinned Liquity repositories, source-file hashes, event signatures, branch addresses, and v1--v5
   recursive invariance.
2. Verify Blockscout and dRPC chain IDs; verify their frozen end header and all six historical deployments.
3. Verify Portal metadata, finalized coverage, and the exact frozen end header.
4. Reproduce all three frozen qualification identity sets across Blockscout and the Portal.
5. Acquire Blockscout's full decoded support surface using the original three independent address filters.
6. Acquire only sanitized identity fields from the finalized Portal in the same 10,000-block outer chunks. After
   every completed chunk, atomically checkpoint the canonical identities outside Git.
7. Require exact equality of the complete identity multisets. Only then attach canonical timestamps and evaluate
   the original support thresholds once.

No raw RPC or Portal response is persisted. The replica stores only block number/hash, transaction hash, log
index, contract address, and topic 0. Portal pages observed in the five 10,000-block screens ranged from 7 to 13;
the full 331-chunk pass is therefore network-bound but remains CPU-only, free, below 0.25 GB derived storage, and
within the frozen 12-core-hour ceiling. V100 and RTX GPUs remain idle.

## Decision rule

- Any source, deployment, metadata, finality, cursor, retry, checkpoint, or full-identity mismatch stops the route.
- Any original support threshold failure stops the route before D1 and numerical outcomes.
- A pass authorizes only a separately committed D1 preregistration. It does not establish an NMI/NCS claim and
  does not authorize queue reconstruction, EcoMD, market-price analysis, or GPU work by itself.
