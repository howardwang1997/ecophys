# Compound III all-candidate mechanics preflight v1

**Frozen date:** 2026-08-16

**Decision authority:** the first pushed commit containing this document,
`data/manifests/compound_v3_candidate_mechanics_preflight_v1.yaml` and
`ecomd/research/compound_candidate_mechanics.py`.

## Question

D0 found 14 log-level candidates. This preflight asks whether at least one survives exact transaction/receipt,
complete provider-returned call trace, T-1/T configuration, proxy state, governance-neighborhood and finality
checks. It audits all 14 before filtering, in the already frozen event-class priority followed by ascending block
and transaction hash. It opens no account or market response.

The pass condition is intentionally narrow. It creates a mechanics-conforming historical development candidate
set and permits writing a D1 exposure-count/cost protocol. It does not select a headline event, certify exposure,
validate controls or authorize a participant panel.

## Frozen parents and candidate order

The D0 summary and normalized inventory, exposure design and chain summary are pinned by SHA-256. The 14 rows and
their ordering are re-derived from those artifacts at runtime. Candidate replacement is forbidden.

Two borrow-collateral-factor changes appear first, followed by twelve supply-cap changes. The contamination
neighbor set is also derived from D0. Because every candidate is post-Merge and Ethereum has at most one execution
block per 12-second slot, any other relevant block within 24 hours must be within 7,200 execution blocks. Only
blocks 20,721,442 and 21,237,796 require additional headers; one candidate already has another relevant transaction
in its own block.

## Exact network plan

The no-retry path is 188 successful operations: 187 JSON-RPC calls plus one Beacon REST call.

Initial/finality operations:

1. PublicNode `eth_chainId` and `eth_getBlockByNumber("finalized", false)`;
2. PublicNode Beacon `/eth/v1/beacon/light_client/finality_update`;
3. an explicit PublicNode execution header at the Beacon response's finalized execution height; and
4. two Blockscout contamination-neighbor headers.

For each candidate, in frozen priority order:

1. Blockscout transaction, receipt and block header;
2. PublicNode block header and `debug_traceTransaction` with Geth `callTracer`;
3. Blockscout ERC-1967 implementation and admin slots at T-1 and T;
4. Blockscout code at the old and new implementation addresses; and
5. Blockscout `getAssetInfoByAddress(asset)` at T-1 and T.

The exact method vector is 1 chain ID, 32 headers, 14 transactions, 14 receipts, 14 traces, 56 storage reads, 28
code reads and 28 calls. Provider counts are 156 Blockscout, 31 PublicNode execution and one PublicNode Beacon.
The collector checks the full ordered label/provider/method/parameter plan, including response-derived historical
implementation addresses, rather than accepting matching totals alone. No endpoint or candidate may be
substituted after execution.

## Receipt, proxy and getter conformance

Every transaction/receipt must match the D0 hash, block and index and have status one. Every Configurator or frozen-
proxy log in the receipt must reproduce the complete decoded D0 relevant-log row—including indexed addresses and
values—with no missing, changed or extra row. Every receipt log must also agree with its receipt's block,
transaction and index identity, and duplicate log indexes are forbidden.
Block number, hash and timestamp must agree between Blockscout and PublicNode.

At T-1 and T, the target proxy must have a nonzero unchanged admin, different implementation addresses and a T
implementation equal to D0's `CometDeployed`/`Upgraded` address. Both implementation codes must be nonempty; only
their hashes are retained.

`getAssetInfoByAddress` is decoded as exactly eight static ABI words with strict uint/address widths. The asset
must already resolve at T-1. Exactly one field may change—borrow CF, liquidate CF or supply cap according to the
event—and its T-1/T values must equal D0's old/new values. All other asset fields must be identical.

## Complete-call and payload-isolation rule

The `callTracer` root must reproduce the transaction sender, target, value and complete input. Every call node is
normalized with its path, call type, addresses, selector, full input and output hash; raw trace envelopes and
outputs are discarded.

One successful `CALL` of each exact form is required:

- the corresponding Configurator setter with target proxy, asset and new value;
- `Configurator.deploy(targetProxy)`;
- proxy-admin `deployAndUpgradeTo` or `deployUpgradeToAndCall` with the frozen Configurator and target proxy; and
- target-proxy `upgradeTo` or `upgradeToAndCall` with the D0 implementation.

The deploy and target-proxy upgrade must both be strict descendants of that same exact proxy-admin invocation,
and both must identify the proxy admin as their caller. This is call-topology evidence, not a claim that the
historical deployed bytecode has yet been matched to verified source.

The permitted stateful call cone is the union of ancestors and descendants of those four exact calls. Successful
CALL/CALLCODE/DELEGATECALL/CREATE/CREATE2 nodes outside it fail that candidate. STATICCALL nodes and failed internal
calls do not count as state changes. This allows source-conforming factory/proxy internals while rejecting sibling
governance actions in the same payload. Code hashes are retained, but historical deployed-source conformance is a
later hard gate rather than assumed here.

## Finality and contamination

Every candidate must precede both the execution endpoint's `finalized` header and the Beacon light-client
finality update. The Beacon finalized execution block hash must match an explicit PublicNode execution header.
Candidate headers must agree across both execution providers.

This is stronger than the prior 64-block convention but not self-verifying consensus: the collector does not
locally verify the Beacon update's BLS signature or Merkle branches. The artifact must say provider-reported
finality, not cryptographic light-client verification.

A candidate fails its contamination check if another D0 Configurator or frozen-proxy log lies within 86,400
seconds, excluding its own mechanism transaction. The two neighbor timestamps are read explicitly; a same-block
other transaction fails with zero time difference.

## Gates and decision

All twelve global gates are conjunctive. Transport, receipts, cross-provider headers and trace roots must cover all
14 candidates. Candidate-specific mechanics/getter/contamination failures are retained, not used to truncate the
audit. At least one candidate must pass every candidate check.

A pass is `PASS_CANDIDATE_MECHANICS_AUTHORIZE_D1_EXPOSURE_PROTOCOL_DESIGN_ONLY`. It authorizes only a separately
frozen D1 exposure-count and cost protocol design. A failure is
`FAIL_CANDIDATE_MECHANICS_KEEP_ACCOUNT_AND_RESPONSE_ROWS_LOCKED`.

## Resources and access boundary

The global caps are one request per second, 600 HTTP attempts, 256 MiB of responses, 200,000 normalized trace
nodes, 64 MiB of trace inputs and 100,000 receipt logs. The expected lower bound is about 3.2 minutes plus trace
latency; budget up to 15 minutes. Durable output is three bounded JSON artifacts.

Permitted data are public governance transaction/receipt/payload/call-trace rows, fixed configuration getters,
proxy slots, bytecode hashes and finality metadata. Forbidden are account state, participant actions or traces,
liquidations, prices/oracles and realized responses. No paid data, remote worker or GPU is used. Both V100s and the
RTX 2060 remain idle.

Primary specifications:

- [Ethereum Execution API finalized tag](https://ethereum.github.io/execution-apis/api/methods/eth_getBlockByNumber/)
- [Ethereum Beacon Node APIs](https://github.com/ethereum/beacon-APIs)
- [PublicNode Ethereum endpoints](https://ethereum.publicnode.com/)
- [Blockscout ETH RPC methods](https://docs.blockscout.com/devs/apis/rpc/eth-rpc)
