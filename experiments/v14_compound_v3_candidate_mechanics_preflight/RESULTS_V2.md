# Compound III all-candidate mechanics preflight v2 result

**Execution date:** 2026-08-16

**Protocol commit:** `c7f770a938abe9f0e8452c9bda84bb8ed69f2e5e`

**Manifest SHA-256:** `47ef0fab151a532e0fdc4fce2689d67179ccf8b5d1ba22276f7c3d5e8ffe3738`

**Decision:** `PASS_CANDIDATE_MECHANICS_AUTHORIZE_D1_EXPOSURE_PROTOCOL_DESIGN_ONLY`

## Outcome

The sealed v2 command was run once from a clean detached worktree after the protocol commit was pushed and its
remote ref confirmed. All 14 frozen D0 candidates completed the receipt, two-provider header, complete flat-trace,
proxy slot/code, T-1/T getter, contamination and provider-finality audit. All 12 global gates passed. Four
candidates pass every candidate-specific check:

| Candidate | UTC block time | Market | Asset address | Frozen change |
|---|---:|---|---|---:|
| `supply_cap_16133171_5c9dacfa` | 2022-12-07 13:37:59 | mainnet USDC | `0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2` | `75000000000000000000000 -> 150000000000000000000000` |
| `supply_cap_16520572_f626c068` | 2023-01-30 15:35:35 | mainnet USDC | `0xc00e94cb662c3520282e6f5717214004a7f26888` | `600000000000000000000000 -> 900000000000000000000000` |
| `supply_cap_16549206_b96f2c61` | 2023-02-03 15:39:23 | mainnet WETH | `0xbe9895146f7af43049ca1c1ae358b0541ea49704` | `7100000000000000000000 -> 20000000000000000000000` |
| `supply_cap_16668519_f803c13b` | 2023-02-20 08:17:47 | mainnet WETH | `0xbe9895146f7af43049ca1c1ae358b0541ea49704` | `20000000000000000000000 -> 30000000000000000000000` |

These are mechanics-conforming historical development candidates, not causal events or four independent
replications. The last two are repeated changes to the same market/asset only about 17 days apart. All four are
supply-cap expansions concentrated in December 2022--February 2023. This dependence and narrow intervention class
must be explicit in D1/control design and precludes a universality claim.

## Deterministic filters on the other ten

Every candidate passed transaction/receipt identity, exact D0 relevant-log reproduction, cross-provider header
identity, root-envelope match, all four exact required mechanism calls and proxy-admin topology, implementation/
admin/code conformance, exact T-1/T getter change and both finality-height checks.

Eight candidates fail only or partly because a successful stateful sibling lies outside the frozen mechanism call
cone. They contain 65 such nodes in total: 39 CALL and 26 DELEGATECALL. Counts by candidate are 15, 1, 3, 11, 5,
17, 12 and 1. This is a conservative payload-isolation failure under the preregistered rule; it does not assert
that every zero-value CALL changed durable storage.

Three candidates fail the 24-hour governance-neighborhood rule:

- `supply_cap_20720177_ee0c1da4`: another frozen relevant block is 15,360 seconds away;
- `supply_cap_20878779_ca4bfe09`: another relevant transaction is in the same block, a zero-second gap; and
- `supply_cap_21237694_13cb76a1`: another frozen relevant block is 1,236 seconds away and this row also fails call-
  cone isolation.

Thus eight isolation failures plus three contamination failures, with one overlapping row, account exactly for
the ten non-survivors. No candidate was dropped early or replaced.

## Transport and resource result

The exact ordered plan completed all 188 logical operations: 173 JSON-RPC, 14 Blockscout raw-trace REST and one
Beacon REST. Provider counts were 156 Blockscout RPC, 14 Blockscout raw trace, 17 PublicNode execution and one
PublicNode Beacon. The request labels, methods/parameters or exact REST paths matched the frozen order.

There were 191 HTTP attempts. Three first attempts returned HTTP 500 and then succeeded on the next attempt: one
`admin_pre` storage read, one raw trace and one `implementation_pre` storage read. The attempt ledger
retains all three failures and all 188 successful responses by hashes; no raw body is retained. The ledger spans
240.472 seconds between first and last recorded responses and accounts for 3,711,152 response bytes.

The normalized evidence contains 599 trace nodes, 532,327 trace-input bytes and 129 receipt logs, far below the
frozen 200,000-node, 64-MiB-input, 100,000-log, 256-MiB-response and 600-attempt caps. The finalized execution tag,
Beacon finalized execution header and explicit execution-header replica all agree at block 25,762,219 and hash
`0x6d13bfc0deedc9137eaf0e0079897b0ae2268a8baaee7ab39bfc52e9ab1aac91`. This remains provider-reported finality;
no local BLS or Merkle verification was performed.

## Independent offline verification

A verifier that did not import the collector re-read the v1/v2 manifests, every pinned parent and all three result
artifacts. It rejected duplicate JSON keys; rebuilt the 188-operation plan and every canonical request hash;
reconciled 191 indexed attempts to 188 logical successes and byte totals; re-derived all receipt/D0 matches,
flat-trace parent/child topology, exact calls and call cones, getters, proxy state, contamination, finality and every
candidate check; and reproduced the same four survivors and 12/12 global gates. The copied artifacts reproduce the
source-worktree hashes:

- `summary.json`: `83e32d0e07ac395d02a9d8a8e385633545a605f62d778f60071e424e32923474`;
- `candidates.json`: `553055dae591daab0ef662b02d7e32a98d726fd154a5f43d34575ca3f31160d5`;
- `http_evidence.json`: `814e66afe43f06cc19b99426f9b7408ccbc423f65e051fcd63de7cbaf5844b87`.

`failure.json` is absent, as required on success.

## Access boundary and consequence

Only the authorized public governance transactions, receipts, call traces, fixed historical getters, proxy slots,
implementation code hashes and finality metadata were opened. No account state, participant action/trace,
liquidation, price/oracle or realized-response row was opened. No paid data, external worker or GPU was used; both
V100s and the RTX 2060 remained idle.

The pass authorizes writing and reviewing a separately frozen D1 exposure-count/cost protocol over the four
survivors. It does not authorize account collection, control selection from outcomes, response construction, a
causal claim, G1, model training or GPU work. D1 must handle repeated-event overlap, exact pre-event denominator
reconciliation, historical implementation/source conformance, provider terms, cost caps and outcome-blind control
support before any participant row is opened.

There is also a sharper estimand blocker: all four survivors are supply-cap increases. Unlike a borrow-collateral-
factor change, a cap increase does not mechanically change an existing account's balance, collateral factor or
liquidation threshold. The prior generic “any nonzero position” population is therefore not a directly treated
cohort for these events, while thwarted would-be suppliers are not identifiable from pre-event on-chain state.
D1 must begin with a zero-account-row activation/estimand gate using preregistered aggregate cap-utilization evidence
and must not silently reuse the generic at-risk denominator. If the old cap was not binding, or if no defensible
market-level entrant/flow estimand and control can be frozen, the Compound M3 causal route should stop even though
this mechanics preflight passed.
