# Aave V3 B0 target-row-free transport canary v1

**Status:** frozen before any post-v1 RPC request. A PASS authorizes only design of a versioned B0 collector; it
does not authorize a B0 scientific rerun, B1, account/outcome access or GPU work.

## Motivation and immutable parent

The sealed B0 v1 run at commit `707956291...` completed Arbitrum chain/cutoff headers but received HTTP 403 for
every Provider `eth_getLogs` request, including block 0. Its immutable archive commit is `da29a8e0...`. No log row
or support count was observed. The failure could reflect endpoint method policy, archive policy or egress, so target
data cannot be used to choose a repair.

This canary pins the v1 manifest, result, failure and request ledger by SHA-256. It inherits without modification
the deployment universe, split, cutoff, program inclusion rule, support thresholds, scientific hard caps and all
downstream access locks.

## Zero-target query contract

For each of the nine non-development deployments, each host tests the same two v1 endpoints in the same order:
PublicNode `primary`, then the official/public `replica`. The only methods are `eth_chainId` and `eth_getLogs`.
Every log filter uses address `0x0000000000000000000000000000000000000000` and begins at genesis:

1. `[0, 0]` must return an empty list.
2. `[0, 249999]` must return an empty list, or a JSON-RPC range error may trigger deterministic left-prefix
   bisection until an empty range succeeds.

An HTTP/transport error is retried once and then fails without range bisection. A nonempty list is a contamination
failure; rows are discarded immediately and only the count and response-body hash remain. Raw response bodies are
never written. No Aave Provider/Configurator address, target topic, transaction, receipt, state or outcome is
queried.

## Frozen host and selection rule

All four host IDs must report: `v100_a`, `v100_b`, `rtx2060`, `local_mac`, in that priority order. IDs map to SSH
targets only through the gitignored local machine inventory. CUDA is hidden and no GPU library is imported.

A host passes only if at least one endpoint passes for every deployment. After all four artifacts are present, the
aggregator selects the first passing host by the frozen order. Within that one host, it selects `primary` before
`replica` independently for each deployment. Partial-host mosaics, early stopping, target-result conditioning and
replacement hosts are forbidden.

## Integrity and resource caps

Each host artifact records the exact protocol commit, manifest/source SHA-256, runtime identity, every logical
request, canonical request hash, every HTTP attempt, HTTP status, response hash/size, normalized error/count and
resource totals. The aggregator recomputes request hashes, query-address confinement, attempt/byte accounting,
endpoint identities, host coverage and frozen selection.

Per host: at most 500 HTTP attempts, 32 MiB of responses, two requests per second, two attempts per logical call
and a 30-second timeout. Expected duration is under ten minutes in parallel, under 1 MiB of durable artifacts and
zero GPU-hours. Only existing free endpoints and existing CPU hosts may be used.

## Decision

`PASS_TARGET_ROW_FREE_TRANSPORT_CANARY_AUTHORIZE_B0_V2_PROTOCOL_DESIGN_ONLY` requires all four valid artifacts and
one single host covering all nine deployments. Otherwise the decision is
`FAIL_TARGET_ROW_FREE_TRANSPORT_CANARY_KEEP_B0_V2_B1_G1_GPU_LOCKED`. Neither decision estimates Aave program
support.
