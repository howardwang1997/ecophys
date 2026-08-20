# Morpho Public Allocator pressure displacement — D0 qualification result

**Decision:** PASS to the single frozen full D0 support audit.

**Formal run commit:** `15faa402770b036d4d52ca8284bb1f049bee4836`

**Config SHA-256:** `bc6fc21cfd6b782280ace89d4d854b603dd19370bdad3c6d4803c72557333c60`

**Canonical payload SHA-256:** `d59b0184cc2a3e616abbbd158d47dc6952643dd9fecd31567e37811728b3edfe`

**Result-file SHA-256:** `f7db923c7e01a96c968510743151bdb6ba8fe6b67e37dd1ce62d1779495c2dba`

All six frozen 10,000-block qualification shards reproduced exactly between the finalized SQD Portal stream and
the independently fixed full-scan RPC. Ethereum and Base cutoff headers also matched SQD, full-scan RPC and the
separate receipt RPC. The canonical payload digest was reproduced independently after the run.

## Frozen-shard result

| Chain | Shard | Public Allocator identity events | SQD/RPC exact full-topic match |
|---|---:|---:|---|
| Ethereum | deployment | 0 | pass |
| Ethereum | midpoint | 335 | pass |
| Ethereum | cutoff | 231 | pass |
| Base | deployment | 0 | pass |
| Base | midpoint | 220 | pass |
| Base | cutoff | 2 | pass |

The nonempty midpoint and cutoff shards show that the transport is exercising actual `PublicWithdrawal` and
`PublicReallocateTo` identities rather than agreeing only on empty intervals. These event counts are not atomic
routing--borrow candidate counts: qualification did not retrieve transaction receipts or inspect Morpho Borrow
events.

Ethereum used 29 SQD requests and three `eth_getLogs` requests; Base used 53 SQD requests, including two
transparent Portal overload retries, and three `eth_getLogs` requests. Neither RPC required range or topic
splitting, rate-limit retries or server-error retries. Total wall time was 111.05 seconds on one local process.

## Source and data audit

- exact source commits and all pinned SDK, Public Allocator and Morpho Blue file hashes passed;
- all three event topics recomputed from the source signatures;
- only the six frozen shards and cutoff headers were requested;
- only block/log identity fields and full topics were retained;
- RPC log `data` was neither decoded nor retained;
- no receipt, transaction input, amount, balance, cap, utilization, interest rate, price, liquidation, incident
  label or outcome was read;
- no paid data, EcoMD, GPU or remote compute worker was used.

The first orchestrator call returned no console payload even though the artifact completed on disk. A subsequent
identical diagnostic invocation encountered the runner's existing-artifact guard and terminated before source
audit or network access. Thus the six shards were queried once; no provider, range, threshold or scientific field
was changed.

## What this authorizes

Commit and push this immutable qualification artifact, then run the full D0 exactly once from a new clean
upstream-matched SHA. The full run may retrieve complete Public Allocator identity streams and receipts solely to
classify same-transaction target-matched Borrow identities and apply the frozen support gates.

Qualification does not establish 500 candidate transactions, genuine `0 < r <= x` JIT support, AdaptiveCurveIRM
binding, delayed response, causality, novelty, NMI fit or NCS fit. Amounts and outcomes remain forbidden. Any full
D0 failure stops the route without adding chains or changing the transport policy.
