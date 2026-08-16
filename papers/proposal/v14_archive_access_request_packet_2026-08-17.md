# V14 archive-access request packet

**Date:** 2026-08-17

**Status:** send-ready draft; no message has been sent and no purchase is authorized.

## 1. Short request

**Subject:** Research access request: reproducible historical EVM logs across nine networks

We are evaluating data infrastructure for an academic study of how market participants respond to executable
protocol-policy changes. Before accessing any target event, we need to qualify a reproducible historical archive
route for Arbitrum, Avalanche C-Chain, Optimism, Polygon PoS, Base, Gnosis Chain, BNB Smart Chain, Linea and Scroll
through 2026-08-15 00:00 UTC.

The first-stage requirement is complete historical logs for arbitrary addresses/topics from each deployment's
genesis through that cutoff, plus canonical headers and deterministic pagination/range behavior. An RPC route may
use `eth_getLogs`; a filtered backfill or bulk export is acceptable only with explicit completeness, ordering,
checkpoint and content-hash semantics. The existing RPC budget is at most 50,000 HTTP attempts, 512 MiB of
responses, 250,000 normalized logs and 50,000 program transactions. A bulk route requires a separately frozen
job/byte/time budget before access. Qualification uses only chain/header calls and zero-address empty-log probes;
it does not query the study protocol.

Please confirm the product/region/credential class, supported chains and methods, historical retention, maximum
range/pagination behavior, rate/response limits, evaluation access, support path and terms for retaining hashes,
normalized derived rows and publication artifacts. We also welcome a separate quote or collaboration route for
later transaction receipts, call/instruction traces, historical bytecode/state and block-parameter calls, but
those data will not be opened during first-stage qualification.

Negative or partial answers are useful. We will not choose a resource based on observed target-event counts.

## 2. Required written response matrix

The custodian/provider should complete one row per chain and product region.

| Field | Required answer |
|---|---|
| Chain and chain ID | Exact network/product identifier |
| Historical headers | Earliest retained block; hash-stable block-number access |
| `eth_getLogs` | Earliest retained block; arbitrary address/topic support |
| Backfill/export | Filter semantics, start/end range, ordering, completeness, checkpoint/retry and checksums |
| Range behavior | Maximum inclusive span, result cap, pagination/continuation and error codes |
| Quota | Requests/s, requests/day, bytes/results and concurrency |
| Reproducibility | Retention/SLA and behavior under reorg or historical repair |
| Authentication | Credential class, IP/region constraints and rotation process |
| Evaluation | Duration and quota of target-free trial access |
| Derived-data rights | Permission to retain request/response hashes, normalized rows and aggregate artifacts |
| Publication/review | Permission to publish derived benchmark statistics and support confidential reviewer audit |
| Support | Named ticket/escalation route for truncation or historical inconsistency |

An aggregate “EVM compatible” or “archive supported” answer is insufficient; capability must be explicit for all
nine named chains.

## 3. Optional later-stage matrix

These capabilities are not needed for the first qualification and do not authorize their use.

| Capability | Required semantics |
|---|---|
| Transactions and receipts | Canonical historical transaction, receipt status and ordered logs |
| Call traces | Complete nested frames, success/revert status, logs and declared timeout/truncation behavior |
| Instruction traces | Ordered opcodes with storage/memory/stack availability and completeness limits |
| State differences | Pre/post account and storage changes with block-hash anchoring |
| Historical code | `eth_getCode` or equivalent at exact historical block hashes |
| Historical calls/storage | Block-parameter `eth_call`/storage access or independently verifiable proofs |
| Batch/export | Deterministic bulk route, checksums, immutable manifest and rerun terms |

## 4. Target-free qualification to be frozen after a resource is named

No credential is used until a versioned protocol pins:

- provider, product, region, endpoint family and credential class;
- all nine expected chain IDs;
- exact cutoff blocks derived only from timestamps and replicated headers;
- zero-address log probes at block 0, a deployment-era fixed block and the cutoff era;
- fixed spans of 1, the documented small range, the required production range and any pagination boundary;
- for a bulk route, one empty-filter backfill with fixed range, checkpoint and delivery-count expectations;
- byte, attempt, latency, empty-result, continuation and error ledgers;
- two predeclared egresses when permitted by the product contract;
- terminal handling for throttle, truncation, inconsistent headers or nonempty zero-address results; and
- written licence/retention evidence by content hash, stored separately from credentials.

The qualification cannot include an Aave address, event topic, account, outcome or market response. A pass permits
only a separately committed B0 protocol; it does not permit same-step target access.

## 5. Internal evaluation rubric

Candidates are ranked before target access in this order:

1. complete nine-chain B0 capability within the frozen request/byte caps;
2. reproducible retention, explicit error behavior and scientific auditability;
3. derived-data/publication rights;
4. independent header and later trace/state verification options;
5. ability to extend to the optional B1/B2 methods;
6. total cost and expected wall time.

Failure on any of the first three criteria is terminal. A cheaper partial-chain service is not combined into an
outcome-conditioned endpoint mosaic unless a new multi-resource design is frozen before any target row.

## 6. Suitable recipients

- multi-chain archive/RPC providers;
- historical stream/backfill and content-hashed bulk-export providers;
- university blockchain systems, measurement or security laboratories with reproducible archive access;
- Aave/protocol analytics and data-infrastructure teams;
- institutional data platforms already licensed for cross-chain historical access; and
- research collaborators able to provide a content-hashed export under publication-compatible terms.

The collaboration is not geographically restricted. B0 needs public chain history, not proprietary trader data or
participant identities.

## 7. Internal boundary

No email, form submission, credential use, trial activation, purchase or data transfer has occurred. Sending this
packet or accepting commercial terms requires an explicit recipient/resource choice. Secrets remain outside Git;
written terms and non-secret qualification manifests are versioned.
