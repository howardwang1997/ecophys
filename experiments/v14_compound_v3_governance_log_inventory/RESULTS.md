# Compound III governance-log inventory v1 result

**Protocol commit:** `db26bbe91111b6a71f6a4083231927574dd2b188`

**Execution:** 2026-08-15 16:34:24--16:37:33 UTC

**Decision:** `PASS_GOVERNANCE_LOG_INVENTORY_AUTHORIZE_RECEIPT_PAYLOAD_PREFLIGHT_ONLY`

## Integrity and transport

The first test attempt in the clean detached worktree inherited a sparse-checkout that omitted two committed
parent-artifact directories. Three tests failed only because those files were absent. The fixed parent paths were
materialized without changing tracked content; the worktree remained clean at the exact pushed protocol commit,
all 30 relevant tests then passed, and no network request had yet been made.

The sealed collector completed the unsaturated path exactly:

- 339 successful one-attempt requests: one chain ID, two block headers and 336 log roots;
- 48 queries at each of one Configurator and six market-proxy addresses;
- zero saturated roots or child queries;
- 605,863 response bytes in about 188.9 seconds;
- 886 normalized logs, zero duplicates and zero conflicts; and
- all ten conjunctive gates passed.

PublicNode reproduced the previously frozen end block 25,760,572 and hash
`0xd2bb...a4ca4`; this is cross-provider header replication, not consensus-finality evidence. Raw RPC bodies were
not retained. No receipt, transaction, calldata, trace, account, participant action, liquidation, price or
realized-response row was opened.

## Inventory result

The 886 normalized rows contain 678 Configurator logs and 208 proxy upgrades. Event counts are:

| event class | rows |
|---|---:|
| other Configurator | 292 |
| `CometDeployed` | 202 |
| `UpdateAssetSupplyCap` | 130 |
| `UpdateAssetBorrowCollateralFactor` | 30 |
| `UpdateAssetLiquidateCollateralFactor` | 24 |
| proxy `Upgraded` | 208 |

There are 184 eligible parameter-event rows. Every one had the required same-proxy deployment and matching
upgrade and had `old != new`, but governance bundling is common: 170 had another Configurator log, 167 had more
than one eligible parameter event and 126 shared a transaction with another frozen-market upgrade. These failure
counts overlap. This directly supports the prior warning that a shared admin/Configurator is not an independent
control design.

Fourteen events at fourteen distinct blocks satisfy the conservative log-only atomic rule. Twelve are supply-cap
changes and two are borrow-collateral-factor changes; none is a qualifying liquidation-factor change. Their market
distribution is four mainnet USDC, one USDS, two USDT and seven WETH, with zero WBTC or wstETH-market candidates.

The two highest-priority rows under the already frozen event-class ordering are:

1. block 22,273,296, mainnet USDS, wstETH collateral, borrow factor `0.82 -> 0.80`, transaction
   `0x0080d1f75c7193799b5e1f00028f51239da8da0d0e3192db1f0af5f1edc7bfda`; and
2. block 25,571,051, mainnet WETH, rsETH collateral, borrow factor `0 -> 0.80`, transaction
   `0xfdbdc6fc0f46864658d90fa4d20109cc2436446ef9059b3e2d0a58303224c69b`.

These names are mapped only from the pinned official deployment source. Neither row is yet a valid intervention.
In particular, the second row's zero old borrow factor makes pre-existing-collateral and direct-exposure checks
essential; it must not be promoted merely because its nominal change is larger.

## Independent verification

A separate offline verifier, without importing the collector, reproduced:

- manifest hash, commit, exact request ordering and every request hash;
- all 48 inclusive intervals for each of seven addresses;
- method/provider counts, response-byte sum and absence of retries;
- normalized ordering, unique log identities and event/market counts;
- all 184 candidate check vectors and exactly 14 provisional passes; and
- the highest-priority nonzero-to-nonzero borrow-factor row above.

Artifact SHA-256 values are:

- summary: `e03161118ac4cd7aea56f92f40aabdd49348d3170ce256ff42896291c1470b7f`;
- normalized governance logs: `0435a55b652f5b6a6419f22b296b72184aed25c0073a132c232de55f741fd9e2`;
- RPC response-hash ledger: `85e41d06b3db59b8684ff33c113146dd722c45b7bea7439958ad59f085f5ea5f`; and
- frozen manifest: `f24a69b0ff7b773232629f22240ce43cd0a23d2752dd6ad009944e790325ea9f`.

## Scientific decision and next gate

D0 solves only candidate enumeration. It does not establish payload isolation, existing-collateral conformance,
the operative getter transition, a clean 24-hour neighborhood, consensus finality, exposure completeness,
controls or any response. `G1` remains not passed.

To avoid selecting the most convenient historical event, the next separately frozen preflight should audit all
14 provisional candidates using only receipts, calldata/call paths, pre/post configuration getters, block/finality
evidence and the already collected governance neighborhood. It must preserve a deterministic filtering and
event-priority rule before any account or response data are opened. A failure is retained; no candidate may be
replaced post hoc.

The run used local CPU/network, zero paid data, zero remote workers and zero GPU-hours. Both V100s and the RTX 2060
remain idle. Account/action/response acquisition and model training remain unauthorized.
