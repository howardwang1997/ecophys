# Aave V3 cross-deployment Configurator-program directory v1

**Frozen date:** 2026-08-17

**Stage:** B0, zero-account cross-deployment program inventory. This protocol must be committed and pushed before
the first new-chain RPC call.

## Question

Does a fixed, free-data universe of canonical Aave V3 deployments contain enough complete Configurator-level
program transactions to support a later executable-policy compiler with deployment-held-out validation and test
sets?

B0 does not test participant response, predictive performance or causal effects. A pass authorizes only the design
of a historical ABI/source/receipt/state compiler protocol. It does not authorize B1 execution, accounts, outcomes,
G1 or model training.

## Development disclosure and immutable parents

Ethereum treatment metadata were already opened in A1a and the subsequent bundle replay. Ethereum is therefore
development-only and contributes zero rows to every B0 support threshold. Its immutable 77-bundle summary is
reused without a new Ethereum RPC call.

The B0 manifest pins the A1a directory/summary and the development replay manifest/summary by SHA-256. The official
Aave address book is fixed at commit `70e2f303fe93616784148d6827df6644e5dda4db`; ten deployment files are pinned by
git blob and SHA-256 and are re-read from the git object tree at execution.

## Frozen deployment split

The split was chosen before opening any new Configurator event count.

| Role | Deployments | Use |
|---|---|---|
| Development | Ethereum | Previously exposed mechanism development; never support or confirmation |
| Train | Arbitrum, Avalanche, Optimism, Polygon | Mature heterogeneous discovery/training deployments |
| Validation | Base, Gnosis | Fixed model/protocol-selection deployments |
| Untouched test | BNB, Linea, Scroll | Deployment-held-out final evaluation set |

The primary universe is limited to the named canonical V3 main pools with a pinned official address file, a free
no-auth PublicNode endpoint and a separate public chain endpoint for cutoff-header replication. Alternate Ethereum
pools, whitelabel pools, testnets and all other current deployments are outside v1. They cannot be added after B0
support is seen; an extension requires a new protocol and cannot repair this gate.

## Exact time window

For each new deployment the inclusive window begins at block zero. The end is the largest block whose timestamp is
at most `2026-08-15T00:00:00Z` (`1786752000`). Both frozen endpoints independently binary-search block headers.
The selected block and its successor must exactly agree in number, hash and timestamp; the selected timestamp must
be at or before the cutoff and the successor strictly after it.

This rule fixes a common calendar cutoff without inspecting event counts. It assumes nondecreasing block timestamps;
the adjacent boundary pair is checked explicitly.

## Complete program inclusion rule

For every new deployment:

1. Scan every PoolAddressesProvider log from genesis through the replicated cutoff.
2. Decode the complete pinned provider event surface and derive every Configurator address created or set for the
   `POOL_CONFIGURATOR` identifier. The current official address must be present.
3. Scan all topics at every derived Configurator address over the same complete window.
4. Define one program by `(chain_id, transaction_hash)` if the transaction has at least one Configurator-surface
   log.
5. Include initialization, upgrade-only, emergency, steward and governance transactions. Apply no filter on event
   type, parameter direction, LT, scalar purity, log count or expected usefulness.
6. Preserve full normalized topics/data and the within-transaction log path. Provider logs are contextual and do
   not create a program unless that transaction also emits a Configurator-surface log.

The proxy-history rule incorporates the A1a corrigendum: initial proxy creation and its first provider
implementation transition may have zero or one matching `Upgraded` event. Every later provider implementation
transition must match exactly one Configurator `Upgraded` event by transaction and new implementation.

## Frozen support contract

Every named non-development deployment must contribute at least ten programs. In addition:

| Split | Programs | Unique topics | Multi-log programs | Deployments with an upgrade | Span | Quarters |
|---|---:|---:|---:|---:|---:|---:|
| Train | 120 | 12 | 30 | 2 | 730 days | 8 |
| Validation | 40 | 8 | 10 | 1 | 365 days | 4 |
| Test | 60 | 8 | 15 | 1 | 365 days | 4 |

The total non-development count must be at least 220. All conditions are conjunctive. No threshold may be changed,
no deployment may be reassigned and no chain may be added after rows are observed. These are feasibility minima,
not statistical-power claims; B1 will need a separate attrition and sample-size gate after exact compilation.

## Completeness and integrity

Log roots are inclusive, disjoint 250,000-block intervals. A response with at least 10,000 logs is discarded and
bisected. A bounded RPC error on a multi-block interval is also bisected; a single-block failure terminates the
run. After a range failure, the deterministic half-span bound is reused for the remaining streams of that
deployment; every failed logical request remains in the response ledger. There are two internal transport retries
and no endpoint substitution. Normalized identities must be unique,
all program block headers must match log hashes, every provider topic must be known, and the source-corrected
Configurator upgrade history must pass on every deployment.

Eighteen conjunctive gates cover immutable parents/source, deployment and split identity, replicated chain/cutoff
headers, provider and Configurator directory completeness, strict normalization, duplicate/conflict absence,
upgrade history, exact program grouping, all support thresholds, resource caps and the zero-account boundary.

## Access boundary

B0 may open official source, chain IDs, block headers, provider logs, Configurator logs, event topics/data and the
transaction hashes already carried by those logs. `eth_getBlockByNumber(..., false)` incidentally transfers other
transaction hashes in the raw block response; they are discarded immediately with the raw body and never enter a
normalized artifact.

B0 may not request transaction objects, receipts, calldata, traces, historical contract state, bytecode,
governance payloads, account state, participant actions, liquidations, prices/oracle values or realized responses.
Raw RPC bodies are hashed then discarded. Paid data, external workers and GPUs are forbidden.

## Decision

A full pass yields
`PASS_CROSS_DEPLOYMENT_PROGRAM_DIRECTORY_AUTHORIZE_B1_COMPILER_PROTOCOL_DESIGN_ONLY`. Any completed gate failure
yields `FAIL_CROSS_DEPLOYMENT_PROGRAM_DIRECTORY_KEEP_B1_ACCOUNTS_RESPONSES_G1_GPU_LOCKED`. A transport,
single-block, decoding or resource-cap exception writes a failure artifact and also keeps every downstream gate
locked. The v1 endpoints or thresholds are not repaired in place after observation.

## Resource budget

The hard caps are 50,000 HTTP attempts, 512 MiB of response bodies, 250,000 normalized logs and 50,000 programs,
at two requests per second globally. Based on chain heights rather than event counts, the expected run is roughly
1.5--4 hours on one CPU/network worker; provider range errors can lengthen it but remain within the cap. Durable
artifacts are expected below 100 MiB.

No GPU is useful. The Mac can run the audit, or one V100 host may supply only its CPU/network if a longer unattended
run is preferable. Both V100 GPUs and the RTX 2060 remain idle; H20 is excluded.

## Primary provenance

- Aave official address registry: https://github.com/aave-dao/aave-address-book
- PublicNode endpoint directory and terms: https://publicnode.com/
- Base RPC: https://docs.base.org/base-chain/api-reference/rpc-overview
- Optimism RPC: https://docs.optimism.io/app-developers/reference/rpc-providers
- Avalanche C-Chain RPC: https://docs.avax.network/docs/primary-network
- BNB RPC: https://docs.bnbchain.org/bnb-smart-chain/developers/json_rpc/json-rpc-endpoint/
- Gnosis RPC: https://docs.gnosischain.com/about/networks/
- Polygon RPC: https://docs.polygon.technology/pos/reference/rpc-endpoints
- Scroll RPC: https://docs.scroll.io/en/developers
- Linea documentation: https://docs.linea.build/
