# Aave rate-step response spectroscopy — T0 result

**Decision:** PASS to a separately frozen pre-period activity screen.

**Formal run commit:** `15e01b577`

**Preliminary manifest SHA-256:** `fd696f66addf9c8509ff08222a8c48a0648c2242461e8b85917e2ba9c393c947`
(superseded before acceptance because it failed JSON read-back stability; final rerun pending)

This pass establishes intervention metadata and a free acquisition route. It is not evidence of a behavioral
response, scaling collapse, friction distribution, causal effect, or model validity.

## What passed

The pinned official governance cache maps each selected proposal to one executed Ethereum payload and one exact
`PayloadExecuted` event. The pinned official proposal repository maps each cached AIP to executable source and a
before/after diff. For DAI, USDC and USDT, all six selected events have `variableRateSlope1` as the only
configured change.

| Proposal | Payload | Executed UTC | Block | Slope1 change |
|---:|---:|---|---:|---:|
| 3 | 44 | 2024-01-15 14:00:23 | 19,012,737 | +100 bp |
| 94 | 117 | 2024-05-06 07:46:23 | 19,809,641 | −300 bp |
| 130 | 144 | 2024-07-25 06:54:11 | 20,381,902 | −250 bp |
| 159 | 167 | 2024-09-10 20:20:59 | 20,722,559 | −100 bp |
| 247 | 244 | 2025-02-11 19:09:59 | 21,825,278 | −200 bp |
| 271 | 259 | 2025-03-19 15:23:47 | 22,081,787 | −200 bp |

The final machine-readable result will be regenerated from the canonicalization-fix commit before D1A is
frozen.

The rendered diff can show three non-independent changes without invalidating the singleton configuration
claim:

- `interestRateStrategy` changes when a legacy deployment installs a strategy instance;
- `baseStableBorrowRate` follows the pinned identity
  `variableRateSlope1 + baseStableRateOffset`, while the payload keeps the offset unchanged;
- `maxVariableBorrowRate` changes algebraically when slope 1 changes.

The panel therefore contains 15 primary rate-decrease asset-event units and three reverse-sign units. It clears
the inherited metadata-stage minimum of 15 without adding bundled proposal 69 or 216.

## Free-data result

The public Ethereum RPC returned chain ID 1 and deterministic event topics for `Borrow`, `Repay`, and
`ReserveDataUpdated`. No market log was requested.

The separate bulk-data route failed availability verification. Zenodo's record API returned HTTP/API 404 with
“The persistent identifier is not registered,” and an exact-title search returned zero records for the claimed
DOI `10.5281/zenodo.17898640`. No bulk file was downloaded. The direct-chain route is the current free source;
the preprint's claimed 50-million-row dataset must not be described as available or acquired.

## Blinding and compute audit

- no `Borrow`, `Repay` or `ReserveDataUpdated` market log was queried;
- no position balance, utilization, realized rate, amount, price or post-event value was queried;
- raw market responses were not persisted;
- no paid data, GPU or EcoMD run was used.

## What T0 does not solve

The next activity pass would still leave the main threats intact: governance anticipation, endogenous policy,
intervening risk-steward updates, repeated-asset dependence, feedback through utilization and construction of a
valid at-risk population. Generic aggregate elasticity remains an ineligible claim because Aave's own Risk
Oracle already implements it.

## Authorized next action

Freeze and commit a 28-day pre-execution activity screen before requesting logs. It may retain only weekly
`Borrow`/`Repay` event counts and unique debt-user counts for DAI, USDC and USDT. It must stop before post-event
data unless at least 15 of the 18 singleton asset-event units meet the frozen activity rule. Passing that screen
still does not authorize a behavioral analysis; intervention-ledger and identification gates must follow.
