# Compound III chain-metadata v2 result

**Execution date:** 2026-08-16

**Protocol commit:** `d1019df44df4acbc944e6aae408595de69478e09`

**Decision:** `PASS_CHAIN_METADATA_AUTHORIZE_EXPOSURE_PROTOCOL_DESIGN_ONLY`

## Frozen-gate result

All 12 conjunctive gates passed. The clean detached run completed 62/62 successful requests, all on their first
attempt, in 36.18 seconds between the first and last recorded response. It transferred 418,232 response bytes.
The exact method vector was:

- 24 `eth_call`;
- one `eth_chainId`;
- three `eth_getBlockByNumber`;
- 18 `eth_getCode`; and
- 16 `eth_getStorageAt`.

The provider head was block 25,760,636 at `2026-08-15T13:06:35Z`. The explicit snapshot was block 25,760,572 at
`2026-08-15T12:53:47Z`, exactly 64 blocks behind. This is a provider-observed confirmation-depth snapshot, not
Ethereum consensus finality.

## Deployment findings

All six source-pinned Comet proxies had nonempty code and matched their expected base token, governor and pause
guardian. Their `numAssets()` values, in manifest order, were 13, 10, 16, 4, 17 and 7 (total 67).

The six proxies shared one proxy-code hash but resolved to six distinct current implementation addresses and six
distinct implementation-code hashes. All six proxy admin slots resolved to the same address,
`0x1ec63b5883c3481134fd50d5daebc83ecd2e8779`; the shared Configurator used that same admin. This strengthens the
shared-authority/spillover warning: the six markets are not automatically six independent controls.

At fixed block 17,000,000 (`2023-04-07T23:58:11Z`), mainnet USDC and WETH both had the same immutable proxy code
as at the current snapshot and nonempty historical implementation code. Their historical implementation addresses
differed from current, establishing bounded archive readability across an upgrade—not the timing or cause of any
specific migration.

## Independent verification

An independent read-only verifier reproduced:

- the manifest and committed source-result hashes;
- the collection commit, request indexes, labels, method counts and one-attempt status;
- the 64-block gap and timestamp ordering;
- all six manifest/getter tuples and bounded asset counts;
- historical/current proxy-code equality for the two frozen archive markets;
- the exact gate set and 12/12 pass decision; and
- every retained request/response/result hash format and both artifact hashes.

Artifacts:

- `artifacts_v2/summary.json`: 11,486 bytes, SHA-256
  `14f5b044d8c51e4323419b901a7f037c84c4af45083464e0daaefc561256c944`;
- `artifacts_v2/rpc_response_hashes.json`: 40,368 bytes, SHA-256
  `68f7b21b10e770f0b4695231e0c142a3843d095351ac8a43068726f1a56a54c5`.

## Scientific consequence

This pass establishes source-to-deployment conformance and bounded archive capability for the permitted metadata.
It does not establish an exposure denominator, a valid untreated/control population, event completeness,
participant identity, provider-independent finality, data-retention rights or a causal response.

The only newly authorized action is to write a separately frozen pre-event exposure/control protocol. `G1` is
still not passed. Account mappings, balances, participant actions, transactions, receipts, logs, liquidations,
prices, realized responses and all model/GPU work remain locked until that protocol is reviewed and committed.
