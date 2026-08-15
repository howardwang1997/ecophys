# Compound III supply-cap activation and estimand preflight v1

**Frozen date:** 2026-08-16

**Decision authority:** the first pushed commit containing this document,
`data/manifests/compound_v3_supply_cap_activation_preflight_v1.yaml`,
`ecomd/research/compound_supply_cap_activation.py` and its tests.

## Question and scope

Compound D0b v2 passed its mechanics audit but retained only four supply-cap increases. A supply-cap increase does
not change an existing account's balance, collateral factor or liquidation threshold. Therefore an existing
nonzero position is not a treated unit, and the people who would have supplied but were blocked are not enumerable
before the event. D0b consequently authorizes this zero-account D1a design, not an account census.

D1a asks one narrow physical question: immediately before each governance event, did the source-defined aggregate
collateral supply exactly equal the contemporaneous old cap? It also checks six fixed event-preceding snapshots to
describe cap utilization without selecting a threshold or time window from the result. It does not query a
post-event aggregate total, account, action, price, liquidation or response.

## Frozen candidates and parent evidence

All and only the four fully conforming D0b v2 rows are included, in parent order:

1. `supply_cap_16133171_5c9dacfa`, mainnet USDC market, WETH cap increase at block 16,133,171;
2. `supply_cap_16520572_f626c068`, mainnet USDC market, COMP cap increase at block 16,520,572;
3. `supply_cap_16549206_b96f2c61`, mainnet WETH market, cbETH cap increase at block 16,549,206; and
4. `supply_cap_16668519_f803c13b`, the same mainnet WETH/cbETH market pair at block 16,668,519.

The manifest hash-pins the D0b v2 protocol, result, summary, full candidate evidence and HTTP ledger, plus the
earlier official-source metadata result. Runtime derivation must reproduce the exact four IDs, strict cap
increases and seven unique old/new implementation addresses and bytecode hashes. There is no replacement,
ranking or filtering based on D1a responses.

## Source-defined mechanism

At official Compound Comet source commit `f766f51583c23acc33b2a7824654ef2029a96804`, collateral supply loads
`totalsCollateral[asset]`, increments `totalSupplyAsset`, and reverts with `SupplyCapExceeded` when the resulting
total exceeds `assetInfo.supplyCap`. `TotalsCollateral` contains two `uint128` fields and the public mapping getter
selector is `0x59e017bd`; the second reserved field must be zero.

For each of the seven historical implementation addresses, D1a retrieves the documented Blockscout verified-
contract record before any state call. A conforming record must be fully verified Solidity with unchanged
bytecode, an accepted Comet contract name, exact `totalsCollateral(address)` and `getAssetInfoByAddress(address)`
ABI shapes, all six normalized enforcement/storage markers, and deployed-bytecode SHA-256 equal to D0b's
historical `eth_getCode` hash. The bounded artifact retains compiler/ABI/file inventory hashes and semantic
booleans, never source bodies. This is verified-source matching, not a local reproducible Solidity build.

## Frozen historical states

For each event block `T`, the six fixed offsets are `1`, `300`, `1,800`, `7,200`, `21,600` and `50,400` blocks.
They are approximately immediate, one hour, six hours, one day, three days and seven days before the event, but
the artifact records the actual header timestamp and elapsed seconds. Block offsets were chosen before response
access. Discrete observations do not establish uninterrupted saturation between snapshots.

At every snapshot, both Blockscout and PublicNode return:

- `getAssetInfoByAddress(asset)`, including the cap that was actually active at that historical block; and
- `totalsCollateral(asset)`, including aggregate `totalSupplyAsset` and the zero reserved field.

Both provider records must agree exactly, and total supply may not exceed its contemporaneous cap. PublicNode also
reproduces D0b's old/new implementation bytecode hashes, the T−1 asset getter and the T configuration getter. Only
historical block headers, configuration state and aggregate collateral state are opened.

## Confirmatory rule and diagnostics

The confirmatory strong-activation predicate is exact integer equality at `T−1`:

\[
\mathrm{totalSupplyAsset}_{T-1}=\mathrm{supplyCap}_{T-1}.
\]

Under the matched source semantics, this means any positive collateral supply at that state would exceed the old
cap. It still does not reveal an attempted supplier or counterfactual order.

Utilization at 90%, 95% and 99%, headroom, and exact saturation at the other five snapshots are descriptive only.
They cannot replace exact T−1 equality, authorize a pass, or be tuned after collection. A slack cap may still
block a deposit larger than its headroom, but the relevant depositor and order-size distribution are unobserved in
this audit; treating near-cap state as causal exposure would therefore be post-hoc and unidentified.

## Decisions

All ten integrity gates are conjunctive. They cover parents/selection, two mainnet identities, seven source
matches, cross-provider runtime/configuration/aggregate reproduction, complete candidate evaluation, exact request
order, resource caps and the access boundary.

- If every integrity gate passes and at least one candidate is exactly saturated at T−1, return
  `PASS_EXACT_CAP_ACTIVATION_AUTHORIZE_MARKET_LEVEL_D1B_DESIGN_ONLY`. This permits only a separately frozen design
  for a market-level collateral-entry/flow estimand and controls. It does not permit account rows or response
  acquisition.
- If integrity passes but no event is exactly saturated, return
  `FAIL_NO_EXACT_T_MINUS_ONE_SATURATION_RETIRE_COMPOUND_M3_CAUSAL_ROUTE`. Compound remains useful as public
  mechanism evidence, not this project's causal M3 path.
- If a source/state/integrity gate fails, return
  `FAIL_SOURCE_OR_STATE_CONFORMANCE_KEEP_ALL_D1_ROWS_LOCKED`.
- A transport or schema exception produces only
  `INFRASTRUCTURE_FAILURE_NO_SUPPLY_CAP_ACTIVATION_RESULT`, never a scientific decision.

For every possible outcome, the participant-level disposition is fixed as
`RETIRE_ACCOUNT_LEVEL_M3_FOR_SUPPLY_CAP_EVENTS_UNOBSERVABLE_TREATED_COHORT`. The only potential continuation is a
market-level design.

## Exact request and resource contract

The no-retry vector has 141 successful operations:

- 134 JSON-RPC calls: two `eth_chainId`, eight `eth_getCode`, 24 `eth_getBlockByNumber` and 100 `eth_call`;
- seven Blockscout smart-contract REST calls, one per unique historical implementation;
- provider counts of 49 Blockscout RPC, seven Blockscout source REST and 85 PublicNode execution calls.

Every ordered provider, label, method/parameters or REST path is reproduced at runtime. One global request per
second, two retries, 512 total attempts, 128 MiB response, 2,048 source-file and 64 MiB source-text caps apply.
Every HTTP attempt and successful logical response is hash-ledgered; raw bodies are not retained. Success writes
three artifacts, while a caught failure writes only a bounded `failure.json`.

This is a free public-data CPU/network experiment. The throttle gives a lower bound of about 2.4 minutes plus
source payload and provider latency; budget 15 minutes. No V100, RTX 2060, external worker, paid data or new storage
capacity is needed, and all GPU queues remain idle.
