# Aave V3 Ethereum LT event directory v1 result

**Protocol commit:** `ceb83d1fdd638836cfd8c563d7741f59d33174c6`

**Execution:** 2026-08-16 05:29:34--05:32:36 UTC

**Frozen decision:** `FAIL_AAVE_LT_EVENT_DIRECTORY_KEEP_ACCOUNTS_RESPONSES_AND_G1_LOCKED`

## Integrity and transport

The first detached-worktree preflight inherited the repository's sparse checkout and omitted two committed parent
artifact directories. Two tests failed only because those files were absent; no chain request or output existed.
The exact committed parent paths were materialized without changing tracked content. Their hashes reproduced the
manifest, the worktree remained clean at the pushed protocol SHA, all 26 bounded tests then passed, and the four
output paths were still absent.

The sealed collector was executed exactly once. It completed the unsaturated request plan:

- 344 successful one-attempt requests over a 181.476-second response span;
- six chain/header calls, 312 root log calls, five fixed-end state calls and 21 code calls;
- 2,948,736 response bytes;
- 3,119 normalized logs, zero duplicate or conflicting identities, and zero unknown provider events; and
- zero saturated roots or child queries.

Blockscout and PublicNode reproduced chain ID 1 and the same start/end headers. The end block was 25,760,572 with
the frozen hash `0xd2bb...a4ca4`. Blockscout's fixed-end provider getters, implementation slots and all 21 code
objects conformed; all code was nonempty. This remains header replication plus single-provider historical state,
not local consensus or state-proof verification.

Raw RPC bodies were discarded after hashing. No transaction, receipt, calldata, trace, historical reserve call,
account, participant action, liquidation, price value or realized response was opened.

## Event directory result

The directory contains 40 provider logs, 3,069 Configurator logs and ten Pool upgrade logs. There are 137
`CollateralConfigurationChanged` rows. Successive emitted configurations yield:

- 18 strict positive LT decreases;
- four rows that also keep emitted LTV and liquidation bonus unchanged; and
- zero rows satisfying the full preregistered transaction-isolation rule.

The four mechanism-shaped rows occur in only two transactions:

1. block 19,526,281, transaction `0xa1d1...9868`: BAL LT `6200 -> 5900` and UNI LT `7700 -> 7400`, while the
   transaction emits 13 Configurator logs; and
2. block 25,037,701, transaction `0xe239...478f`: the same asset is toggled `7500 -> 1 -> 7500 -> 1 -> 7500`
   within one transaction containing 16 Configurator logs. The two apparent decreases are temporary in-transaction
   legs, not a persistent block-boundary treatment.

Fourteen of the other LT decreases also change emitted LTV. Only five of all 137 configuration rows occur in a
transaction with exactly one Configurator log, and none is an emitted LT-only decrease. Therefore the frozen
minimum of three provisional rows, two assets and three transactions fails at zero; this conclusion does not
depend on historical account or response data.

## Frozen proxy-history gate and source corrigendum

The frozen `complete_proxy_upgrade_crosswalk` gate also fails: Pool has 11 provider transitions versus ten
`Upgraded` logs, and PoolConfigurator has seven versus six. In both cases, the sole unmatched transition is the
initial proxy creation. Every later transition matches an upgrade by transaction and implementation; each
old-to-new chain is continuous and ends at the address-book/fixed-slot implementation.

This is a preregistration mistake, not evidence of a broken on-chain history. At the same pinned Aave source commit,
`InitializableUpgradeabilityProxy.sol` (Git blob `4b43fa6...`, SHA-256 `496cde2...`) initializes with
`_setImplementation(_logic)` rather than `_upgradeTo(_logic)`, so it emits no initial `Upgraded` event. The frozen
v1 gate incorrectly required one. The result is not rewritten or rerun: v1 retains two failed gates. An offline
source-corrected diagnostic passes both component histories but cannot change the frozen decision.

Crucially, the independent zero-support failure remains after this source correction. A v2 history-only repair
would therefore consume requests without reopening the strict Ethereum LT route and is not authorized.

## Independent verification

The standalone verifier imports no collector code. It rejects duplicate YAML/JSON keys; pins every artifact and
parent hash; reconstructs all 344 request bodies and hashes in exact order; checks request/byte/method accounting;
rebuilds all 3,119 identities, event counts, 137 candidate vectors, both frozen proxy histories, the code-role
inventory, all sixteen gates and the final decision. It also reproduces the source-corrected initial-deployment
diagnostic while leaving the v1 gates unchanged.

Artifact SHA-256 values are:

- frozen manifest: `860cd0338414508d3a447cd522114cc3dbaa3193624863c9326091e0f1fa2763`;
- summary: `ff3e120920b766957353c59c02341c42990a18818a751d62da6e1a6798a3c1bb`;
- normalized event directory: `1d1d73b5f5ba51c60841a411edf563317f143e9599e3eac958643895c90648ec`;
  and
- RPC hash ledger: `71055ad80b66bc36138fedb63ff0fc742d12a0f72e0341320e2b4a1060e151b1`.

Raw-response parsing cannot be replayed because raw bodies were never retained. The verifier establishes internal
artifact, request-plan and derived-decision consistency, not independent chain observation.

## Scientific consequence

The strict Ethereum scalar-LT route is retired before accounts. It would be post-hoc to relax “one Configurator
log” after observing that all four mechanism-shaped rows are bundled. No A1b historical state/payload audit,
account census, action/response panel, G1 admission or GPU training is authorized for this route.

Two new directions remain scientifically legitimate only under new protocols:

1. apply the unchanged strict directory rule to precommitted additional Aave deployments, preserving a fresh
   confirmation pool; or
2. pose a different vector-policy-shock problem in which bundled multi-asset transitions are the treatment.

The second is not a rescue of this event study. It needs a new estimand, exact joint transition operator,
governance-endogeneity model and controls for every simultaneous state change. For an NCS-scale story it may be
more general, but it is also materially higher risk. Neither direction may reuse the two exposed Ethereum bundles
as untouched confirmation evidence.

The run used free public data and local CPU/network only. Paid data, external-worker time and GPU-hours were zero;
both V100s and the RTX 2060 remained idle, and no H20 was assumed.
