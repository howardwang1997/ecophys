# Compound III supply-cap activation preflight v2 result

**Execution date:** 2026-08-16

**Protocol commit:** `a9af33e9c1e519a1b670f5700bf627655ff053fa`

**Manifest SHA-256:** `aca9d2af723a9644066a85f8ce0c98893a97463402574cdb04feb771944163f9`

**Decision:** `FAIL_NO_EXACT_T_MINUS_ONE_SATURATION_RETIRE_COMPOUND_M3_CAUSAL_ROUTE`

## Outcome

The sealed v2 collector was run once from a clean detached worktree after the complete protocol commit was pushed
and the remote ref was verified. All 105 frozen operations completed on their first HTTP attempt. Every one of the
ten integrity gates passed, all four candidates were evaluated, and all seven historical implementations passed
the frozen verified-source, deployed-bytecode, ABI and source-marker checks.

None of the four candidates had exact integer equality between `totalSupplyAsset` and the contemporaneous
`supplyCap` at T−1. Under the preregistered rule, this is a complete negative activation result, not an
infrastructure or conformance failure. It retires the Compound supply-cap route for the confirmatory M3 causal
study and does not authorize D1b, account/action/response acquisition, G1 or model training.

| Candidate | Market / asset | T−1 total | Old cap | T−1 headroom | T−1 utilization | Exact |
|---|---|---:|---:|---:|---:|---|
| `supply_cap_16133171_5c9dacfa` | USDC / WETH | 74,895.044596316890233867 | 75,000 | 104.955403683109766133 | 99.860059% | no |
| `supply_cap_16520572_f626c068` | USDC / COMP | 441,184.077769799756107341 | 600,000 | 158,815.922230200243892659 | 73.530680% | no |
| `supply_cap_16549206_b96f2c61` | WETH / cbETH | 7,099.973170408659338541 | 7,100 | 0.026829591340661459 | 99.999622% | no |
| `supply_cap_16668519_f803c13b` | WETH / cbETH | 19,999.989799797353682986 | 20,000 | 0.010200202646317014 | 99.999949% | no |

The human-readable quantities use 18 decimals for these four ERC-20 assets. All decisions were made on the raw
integers retained in the artifact, not rounded values.

## Diagnostic signal is not a changed decision

Three candidates were close to the cap in at least one frozen lookback. The first WETH row came within
0.254506752915736246 WETH at offset 21,600; the first cbETH row came within 0.000099161340661459 cbETH at offset
50,400; and the second cbETH row was within 0.010200202646317014 cbETH at T−1. The COMP event was materially slack
at T−1. None of the 24 snapshots was exactly saturated.

This is scientifically relevant descriptive evidence but cannot be promoted into the frozen confirmatory result.
The source mechanism rejects a deposit when the post-deposit total would exceed the cap, so a positive residual
headroom does not prove that the constraint was behaviorally irrelevant: orders larger than the remaining
headroom could still have been blocked. Those attempted orders and would-be suppliers are absent from this
zero-account audit. Changing the rule after seeing the near-boundary values would be post-hoc threshold selection.

The proper interpretation is therefore narrow: **the strong, observable exact-saturation instrument failed**.
It is not evidence that supply caps never constrained behavior, nor is it a license to rescue M3 with a movable
near-cap cutoff. Any future boundary-layer or endogenous-governance study must be a new hypothesis with a new
protocol and must not reuse these four events as an untouched confirmatory set.

## Source, state and transport evidence

Both providers returned Ethereum chain ID `0x1`. For every candidate and each fixed offset 1, 300, 1,800, 7,200,
21,600 and 50,400, Blockscout and PublicNode returned identical block number, hash and timestamp. Blockscout then
returned the contemporaneous `getAssetInfoByAddress` and `totalsCollateral` values. All 24 totals had a zero
reserved word and lay at or below their contemporaneous cap; every T−1 asset record reproduced its D0b parent.

The exact request vector was 98 JSON-RPC calls plus seven Blockscout verified-source GETs. Method counts were two
`eth_chainId`, 48 `eth_getBlockByNumber` and 48 `eth_call`; provider counts were 73 Blockscout RPC, seven
Blockscout source and 25 PublicNode execution operations. There were 105 attempts for 105 successes, 1,961,938
response bytes and no retry. The response ledger spans 107.202 seconds from its first to last recorded response.

Blockscout remained the sole historical state provider. Cross-provider header equality anchors the queried block,
but it is not independent state replication and no Ethereum state proof was verified locally. This evidence was
adequate for the frozen free-data feasibility kill gate, not for a standalone final-paper state-validity claim.

## Independent offline verification

`verify_v2_artifacts.py` does not import the collector. It rejects duplicate YAML/JSON keys; checks the v1 failure
and every D0b/source parent hash; re-derives the four survivors; verifies normalized source inventories and their
hashes; rebuilds all 105 ordered requests and canonical request hashes; reconciles the 105 attempt records and byte
total; verifies all 24 two-provider header identities and state/utilization calculations; and reproduces the four
candidate decisions, ten integrity gates and final decision.

The copied artifact hashes are:

- `summary.json`: `e5f4ef20a3561d75cd8b13007fcd2b0e23e518c13aa20f7d0cd1fd4b1f5caa66`;
- `candidates.json`: `e452a2fcd00a238f5d44fb9b9c04eab294979fd93b3f6be2490f5845f26e5707`;
- `http_evidence.json`: `cf62cf400b243e9883e4d97d69d47b12339f2da2ee312a1437351a6cb03069ad`.

`failure.json` is absent, as required on success. Raw HTTP bodies were intentionally never retained, so an offline
verifier can prove request, hash-ledger, normalized-evidence and decision consistency but cannot independently
replay raw-response-to-normalized-source/state parsing. That retention boundary is explicit rather than hidden.

## Access, resources and route disposition

No account state, participant action or trace, price/oracle, liquidation, post-event aggregate state or realized
response was opened. Paid data, external workers and GPU use were zero; both V100s and the RTX 2060 remained idle.

The account-level M3 estimand was already structurally retired because would-be blocked suppliers have no
pre-event enumerable denominator. This complete D1a result now also retires the preregistered market-level D1b
route: `authorized_next_stage` is null. Compound remains useful as mechanics and exploratory real-system evidence,
but these four events cannot support the planned confirmatory participant-adaptation claim.

The next authorized step is source selection and zero-row identification design for a genuinely different M3/M4
route, not more Compound account collection and not GPU training. Aave or another domain may be audited under a
fresh protocol. Separately, the near-boundary values motivate an exploratory cross-protocol question about hard
constraint boundary layers and endogenous rule adjustment, but that question needs new events, controls and a
held-out confirmation set before it can affect the NCS main story.
