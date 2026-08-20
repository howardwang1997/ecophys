# Morpho Public Allocator D0 — deterministic transport amendment v2

## Decision

The v1 scientific contract remains binding. This amendment changes acquisition scheduling only: the same two
chains, addresses, event topics, finalized block intervals, RPCs, receipt rules, classification, support
thresholds, stop rules and data prohibitions are retained byte-for-byte through the parent-config hash
`bc6fc21cfd6b782280ace89d4d854b603dd19370bdad3c6d4803c72557333c60`.

The first v1 full invocation from clean pushed commit `05c74b71b2a4e5be3fd2d91e6dcd1f8ec6804fc0` was stopped after
approximately eleven minutes. It wrote no result artifact and exposed no console or support count. Process
inspection showed a live network-bound Python process. The stop was technical rather than scientific.

## Why the serial execution is not retained

The passing v1 qualification required 29 Portal requests for three Ethereum 10,000-block shards and 53 requests
for the corresponding Base shards. Per-shard Portal pages were 6/7/14 on Ethereum and 5/23/21 on Base. Linear
extrapolation to the frozen full intervals gives roughly 5,800 Ethereum and 59,000 Base Portal pages at the
three-shard mean. Even an intentionally optimistic extrapolation from the sparsest qualification shard gives
about 22,000 pages pooled. At the observed 111.05 seconds for 82 Portal requests plus the fixed RPC checks, the
serial Portal stage is plausibly 8--24 hours before any sequential receipt verification.

This behavior follows the [documented Portal stream contract](https://docs.sqd.dev/en/portal/evm/quickstart): a
response may terminate at an SQD worker-range boundary before `toBlock`, after which a client must resume from
the next block. Finalized, bounded, disjoint block ranges can therefore be queried independently and their
canonical identity sets unioned without changing the requested population.

## Frozen v2 execution

The technical configuration is
`configs/empirical_physics/morpho_public_allocator_pressure_d0_transport_v2.yaml`.
Its frozen SHA-256 is `b549efa43be88d9ce9385224f61158767b042df824fef447f959b600c66634a4`.

1. Qualification splits each already-observed 10,000-block shard into eight disjoint 1,250-block pieces and uses
   at most eight Portal workers. It must reproduce all six v1 event counts and canonical identity digests exactly,
   as well as the original exact Portal/RPC equality.
2. A formal chain run partitions its unchanged inclusive interval into deterministic 100,000-block shards. At
   most eight Portal workers operate concurrently. Each substream independently reaches its fixed end; the
   combined list is sorted canonically and any duplicate identity is fatal.
3. Full-RPC scanning is unchanged. Receipt classification uses at most four workers, each paced at no more than
   two requests per second. Every receipt still undergoes the same exact transaction/block/status/log checks;
   results are reduced in canonical transaction-hash order.
4. Ethereum and Base produce independent aggregate-only chain artifacts from the same clean pushed SHA. Both
   jobs must be launched before either result is read. A local merge verifies artifact hashes, common source and
   config provenance, a common batch id derived from Git/config/qualification, the fixed worker assignment, the
   exact required-chain set, and then evaluates the original v1 gates once.
5. Progress output may report only stage, elapsed time and completed/total technical shards or receipts. It must
   not expose event, candidate, vault, edge or outcome counts before a formal chain artifact is complete.

The two V100 hosts are CPU/network workers only: Ethereum is assigned to V100-A and Base to V100-B, with
`CUDA_VISIBLE_DEVICES` empty. Each runner refuses to start unless `ECOPHYS_D0_WORKER_ID` matches that assignment
and CUDA is explicitly hidden. The GPU devices themselves remain unused. The RTX 2060 is reserve-only and is not
part of the frozen formal run.

## Invariants and failure rules

- No amount, balance, cap, utilization, rate, price, liquidation, incident label or later market outcome is
  decoded or requested.
- No raw response, transaction hash, address, market id or event identity is retained in a chain or merged
  artifact. Identity-bearing objects exist only in process memory until their aggregate digest is computed.
- No support threshold may be changed after either chain starts. A missing/failed chain cannot be replaced by a
  third chain.
- A qualification digest mismatch invalidates v2 before the full run.
- A chain transport failure remains a D0 failure. Concurrency is not permission to discard a failed shard or use
  whichever provider returns more rows.
- A merged D0 failure closes the route before D1, protocol values, outcomes, EcoMD, GPU computation or paid data.

## What a pass would mean

A v2 D0 pass would establish only that the frozen two-chain population contains enough exact atomic
routing--Borrow identity candidates to justify a separately frozen amount/state replay. It would not establish
genuine `0 < r <= x` JIT routing, AdaptiveCurveIRM exposure, delayed controller memory, causality, novelty, NMI
fit or NCS fit. The accounting story remains too simple to carry a paper without the later field result and an
independent-system transfer.
