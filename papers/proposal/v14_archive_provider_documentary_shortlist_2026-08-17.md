# V14 archive-provider documentary shortlist

**Date:** 2026-08-17

**Decision:** approach QuickNode's historical Streams/custom-data route first and Alchemy's enterprise/custom
archive route second. No product currently passes the access gate, and no account, trial or purchase is authorized.

## 1. Screening rule

This is a documentation-only screen conducted before any new endpoint or target row. A candidate is not qualified
because its website says “archive.” It must still provide written range/retention/licence terms and pass a frozen
zero-address test on the exact product, region and credential class.

The nine frozen networks are Arbitrum, Avalanche, Optimism, Polygon, Base, Gnosis, BNB, Linea and Scroll. The
scientific deployment/split/support contract is unchanged.

## 2. Candidate ordering

### 1. QuickNode historical Streams or custom archive export — first contact

Documentary strengths:

- QuickNode's official [node-type table](https://www.quicknode.com/docs/platform/supported-chains-node-types)
  lists mainnet archive availability with no pruning for every one of the nine networks.
- Its [data-source matrix](https://www.quicknode.com/docs/functions/data-sources) lists blocks, transactions, logs,
  receipts and `debug_trace` data for all nine. `trace_block` is not universal, which reinforces the need to pin
  one trace family rather than assume interchangeable outputs.
- [Streams backfilling](https://www.quicknode.com/docs/streams/backfilling) exposes historical EVM logs, receipts
  and debug traces, while the [Streams FAQ](https://www.quicknode.com/docs/streams/faq) states sequential,
  finality-ordered, exactly-once delivery.

Core RPC is **not** an acceptable B0 route under the frozen cap. QuickNode documents a paid-plan
[`eth_getLogs` limit of 10,000 blocks](https://www.quicknode.com/docs/data/eth_getLogs). The immutable B0 v1 header
ledger brackets the Arbitrum cutoff above block 494,618,480. Even with only the Provider and one Configurator
surface, genesis-to-cutoff scanning needs at least

\[
2\left\lceil\frac{494{,}618{,}481}{10{,}000}\right\rceil=98{,}924
\]

log calls, before headers, retries, upgrades or the other eight networks. This exceeds the frozen 50,000-attempt
cap. A generic paid RPC key therefore fails on paper and should not be trialed.

The request to QuickNode must specifically ask whether Streams or a content-hashed custom export can:

1. backfill filtered logs from genesis through the cutoff on all nine chains;
2. prove completeness/order and define retry/checkpoint semantics;
3. fit a separately frozen job/byte/time budget rather than the infeasible per-10k RPC scan;
4. retain and publish normalized derived rows and audit hashes; and
5. later expose version-pinned debug traces and historical state under compatible terms.

Open issues: historical start guarantees for Streams, filter semantics, job limits, price, export format,
cross-region reproducibility and derived-publication rights are not established by public documentation.

### 2. Alchemy enterprise/custom archive — second contact

Documentary strengths:

- Alchemy's official [Chain API list](https://www.alchemy.com/docs/reference/node-supported-chains) includes all
  nine networks.
- Its [`eth_getLogs` reference](https://www.alchemy.com/docs/node/stable/stable-api-endpoints/eth-get-logs)
  explicitly publishes plan- and chain-specific range limits and a 150-MiB response cap.
- Its [pricing page](https://www.alchemy.com/pricing) lists archival access and makes increased log ranges and
  premium debug/trace APIs plan-dependent rather than silently universal.

The free plan's ten-block log range is infeasible. Pay-as-you-go is unlimited for Arbitrum/Base/Optimism, but is
2,000 blocks on Polygon, 10,000 on BNB and normally 10,000 on other chains. The aggregate cap cannot be assumed to
pass, especially after Configurator upgrades add address surfaces. Enterprise advertises increased ranges but does
not publicly establish the exact nine-chain contract or publication terms.

Ask Alchemy for a written custom range/pagination matrix, projected CU cost, trace/state coverage and derived-data
rights. Do not activate a free or pay-as-you-go key merely because all chain names appear in the support list.

### 3. GetBlock shared/dedicated archive — conditional backup

GetBlock documents [archive mode](https://docs.getblock.io/getting-started/endpoint-setup/enabling-archive-mode)
for several popular shared networks and says dedicated archive nodes can be deployed for supported chains. Public
documentation does not establish shared archive coverage, log ranges, traces or retention for the complete frozen
nine-chain set. A nine-chain dedicated deployment is likely operationally and financially heavier, but no price
assumption is made before a quote.

Keep it as a backup only if a single written response covers every chain and the derived-data terms.

### 4. dRPC — deprioritized without a written exception

dRPC states that many networks have archive nodes but explicitly warns that an
[Archive label may not mean history from block 0](https://drpc.org/docs/howitworks/archive-nodes). The frozen free
qualification also observed BNB throttling on both eligible egresses. This does not prove that a paid contract
fails, but it removes dRPC from first-contact priority unless support supplies exact genesis/range/retention and
publication guarantees.

## 3. Current decision matrix

| Candidate | Nine-chain names documented | Bulk route documented | Ordinary RPC fits B0 cap | Trace/state promise | Current decision |
|---|---:|---:|---:|---:|---|
| QuickNode Streams/custom | Yes | Yes | No | Promising, unqualified | First written request |
| Alchemy enterprise/custom | Yes | Custom/plan-dependent | Not established | Plan-dependent | Second written request |
| GetBlock dedicated | Supported-chain dependent | Not established | Not established | Archive-dependent | Backup quote only |
| dRPC paid | Dashboard/support dependent | Not established | Free route failed | Archive label nuanced | Deprioritize |

“Promising” is not a pass. Retention, exact historical start, completeness, quotas, licence and a target-free run
remain unresolved for every row.

## 4. Recommended next action

Send the provider-neutral packet first to QuickNode with “Streams/custom historical export, not standard Core RPC”
highlighted. Send the same matrix to Alchemy enterprise/data support in parallel only after the recipient action is
authorized. Responses should be archived by content hash, stripped of secrets, and compared before any trial.

If neither can meet the contract, seek an institutional archive collaborator or redesign the resource layer before
target access. Do not relax the nine deployments, support thresholds or untouched test split to fit a provider.
