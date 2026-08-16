# Aave B0 transport-repair official-source audit

**Date:** 2026-08-17
**Scope:** documentation only; no post-canary-v1 RPC or target row was opened.
**Decision:** freeze a narrow target-row-free repair canary before any new request.

## What the failed canary established

Transport-canary v1 used four independent egresses and no Aave address. Its pattern was nearly identical across
hosts. Polygon and Base replicas passed a single genesis block but rejected a 250,000-block empty range with HTTP
400 and 413. BNB PublicNode returned 403 and the official dataseed returned JSON-RPC `-32005 limit exceeded` even
for block 0. This rules out a Mac-only repair and leaves error classification plus BNB history access as the exact
transport blockers.

## Official findings

1. BNB Chain explicitly states that `eth_getLogs` is disabled on its listed mainnet public endpoints and directs
   log users to third-party providers. Its provider list includes dRPC. Source:
   https://docs.bnbchain.org/bnb-smart-chain/developers/json_rpc/json-rpc-endpoint/
2. BNB's official archive-node guide says an Erigon archive sync takes about three days and 4.3 TB; its stated
   minimum is 64 GB RAM and 5 TB SSD/NVMe. The current no-expansion plan declares no 5 TB archive-storage
   allocation, so self-hosting is outside this experiment. Source:
   https://docs.bnbchain.org/bnb-smart-chain/developers/node_operators/archive_node/
3. Base's official `eth_getLogs` documentation warns that large ranges may be rejected and recommends ranges below
   2,000 blocks. The observed HTTP 413 after a passing single block is therefore consistent with a range limit,
   not evidence of missing genesis history. Source:
   https://docs.base.org/base-chain/api-reference/ethereum-json-rpc-api/eth_getLogs
4. dRPC's BNB documentation exposes `https://bsc.drpc.org`, lists `eth_getLogs` for BSC and documents event-log
   retrieval. BNB Chain independently lists dRPC as a provider. These documents justify a canary candidate; they do
   not prove free genesis retention, which must be tested before selection. Sources:
   https://drpc.org/docs/bsc-api and https://drpc.org/docs/bsc-api/eventlogs
5. SubQuery describes a free BNB archive RPC but now states that its RPC service has retired in favor of OnFinality.
   Because the current no-auth endpoint and retention contract are unclear, it is not a v2 candidate. Source:
   https://subquery.network/rpc/list/56

## Frozen repair choice

- Reuse only the two v1 hosts with the highest target-free coverage: `rtx2060` then `local_mac`. Their immutable v1
  artifacts each cover the same six deployments. The V100 hosts cover only five and cannot become eligible from
  the three repair probes, so repeating them would add no decision information.
- Inherit the six already-validated routes and range hints from canary v1.
- Reprobe only Polygon replica and Base replica. After their single-block empty result passes, persistent HTTP 400
  or 413 on a multiblock range is treated as range-dependent and triggers left-prefix bisection. HTTP 401/403,
  429, 5xx and transport failures remain terminal.
- Add exactly one BNB candidate, `https://bsc.drpc.org`, after the two v1 endpoints failed. It must pass chain ID,
  zero-address block 0 and a bisected zero-address genesis prefix. No alternative is substituted after observation.
- Both eligible hosts must finish. The first host in frozen order passing all three repairs supplies a complete
  nine-deployment transport plan. PASS authorizes B0 v2 protocol design only.

## Data and compute consequence

The repair uses no Aave address/topic and retains no target row. It needs at most two CPU hosts, 100 attempts and
8 MiB per host, and should finish within five minutes in parallel. No purchase, archive-node deployment, data
download, GPU or H20 is authorized. A failure closes the current free-RPC B0 route pending a genuinely new archive
resource decision; it cannot be repaired by removing BNB or changing the scientific support contract.
