# Compound III all-candidate mechanics preflight v2

**Frozen date:** 2026-08-16

**Decision authority:** the first pushed commit containing this document,
`data/manifests/compound_v3_candidate_mechanics_preflight_v2.yaml` and the v2 implementation in
`ecomd/research/compound_candidate_mechanics.py`.

## Why a second version exists

V1 was executed once at protocol commit `2ee8a87442b6e5a912354362bddcef572876eb59`. PublicNode returned JSON-RPC
`-32601` for all three permitted `debug_traceTransaction` attempts on the first candidate, before any successful
trace or mechanics result. The immutable result at commit `2681d224fc08ce75cecfd58a4c4e7a4ef0d4a2e2` classifies that outcome as
an infrastructure failure and forbids repairing or rerunning v1.

V2 is a narrow transport repair. It changes exactly three things:

1. replace PublicNode `debug_traceTransaction` with Blockscout's documented transaction raw-trace REST endpoint;
2. retain a bounded hash ledger for every HTTP attempt and write it on collection failure; and
3. classify a successful `SELFDESTRUCT` outside the required mechanism cone as stateful.

The v1 manifest and result are hash-pinned parents. V2 loads the full v1 scientific base and overlays only the
transport, failure-artifact, source, request-count, decision-label and limitation sections. All 14 candidates,
their order and values, the receipt/getter/proxy/finality/contamination rules, all twelve gates and the access
boundary are unchanged. No raw-trace request for a frozen candidate may be made before the v2 protocol commit is
pushed, and no provider may be substituted afterward.

## Trace source and provenance

The frozen endpoint is
`GET https://eth.blockscout.com/api/v2/transactions/{transaction_hash}/raw-trace`. Blockscout documents the
response as an unpaginated Parity-style array containing `action`, `subtraces`, `traceAddress`, `type`, optional
`error` and optional `result`. The public documentation, backend and OpenAPI evidence are pinned in the v2
manifest:

- [transaction raw-trace API](https://docs.blockscout.com/api-reference/get-transaction-raw-trace);
- [request limits](https://docs.blockscout.com/devs/apis/requests-and-limits);
- [node tracing requirements](https://docs.blockscout.com/setup/requirements/node-tracing-json-rpc-requirements);
- Blockscout backend commit `40349b01f1d50e73a6d2bb7517f98351b4ff0e0a`; and
- Blockscout Swagger commit `bfc604de6484caa5566962d6ef22c23168c69de6`.

The pinned backend shows that the controller requests raw traces through Blockscout's configured execution node
and may trigger on-demand fetching. Therefore a returned trace is provider evidence, not an independently replayed
EVM proof, and trace availability remains an infrastructure dependency. The per-instance endpoint is documented
but marked for future deprecation. V2 runs at one request per second, below the documented unauthenticated default,
and permits no endpoint substitution if availability changes.

## Complete flat-trace rule

The response must be a nonempty list within the global node and input-byte caps. Every `traceAddress` must be a
unique list of nonnegative integers; exactly one empty root is required. Every nonroot node must have its explicit
parent. For each parent, direct child indexes must be exactly `0..subtraces-1`. Missing parents, duplicate paths,
gaps, extra children or inconsistent `subtraces` abort collection and produce an infrastructure-failure artifact,
not a partial scientific decision.

Accepted source action types are `call`, `create` and `selfdestruct`; accepted call types are `call`, `callcode`,
`delegatecall` and `staticcall`. Addresses, quantities and hex payloads are decoded strictly. Node success is its
own absence of an error conjuncted with every ancestor's success. The root must be a successful `CALL` and reproduce
the transaction sender, target, value and full input.

The four exact successful `CALL` requirements and proxy-admin descendant topology are unchanged from v1. Successful
CALL/CALLCODE/DELEGATECALL/CREATE and SELFDESTRUCT nodes outside the union of ancestors and descendants of those
calls fail isolation. The API schema does not expose a reliable CREATE/CREATE2 distinction, so both are
conservatively represented as stateful CREATE. STATICCALL and failed nodes remain non-state-changing for this gate.

## Exact network plan

The no-retry plan remains 188 successful operations, now split into 173 JSON-RPC calls, 14 Blockscout raw-trace
REST calls and one Beacon REST call. Provider counts are 156 Blockscout RPC, 14 Blockscout raw trace, 17 PublicNode
execution and one PublicNode Beacon. The RPC method counts are:

- one `eth_chainId`;
- 32 `eth_getBlockByNumber`;
- 14 each of `eth_getTransactionByHash` and `eth_getTransactionReceipt`;
- 56 `eth_getStorageAt`;
- 28 `eth_getCode`; and
- 28 `eth_call`.

The initial six operations and all per-candidate operations retain v1 order. Each candidate's raw trace follows its
Blockscout and PublicNode header checks and precedes slots, code and getters. The collector compares every ordered
operation type, provider, label, method/parameters or exact REST path against the frozen plan. Retries are permitted
only within the existing cap and are all retained.

## Mutually exclusive durable evidence

On full completion, v2 writes summary, full candidate evidence and an HTTP hash ledger containing every successful
logical operation plus every HTTP attempt. Raw response bodies are never retained.

On any caught collection exception, v2 writes only `failure.json`. It records the protocol/manifest identity,
bounded exception class and message, all successful logical-operation hashes, every attempted request's outcome and
response hashes, byte and attempt totals, the frozen access boundary and
`INFRASTRUCTURE_FAILURE_NO_CANDIDATE_MECHANICS_RESULT`. The message is capped at 2,000 characters. A failure artifact
is explicitly not a scientific pass/fail and authorizes no next stage. Success outputs must be absent on failure;
the failure output must be absent on success.

## Gates, access and resources

All v1 scientific gates remain conjunctive. A full collection may pass only if all 14 candidates have complete
receipts, two-provider headers and traces, all mechanics/getter/proxy/contamination checks are evaluated, finality
sources agree, the exact request plan and global caps hold, and at least one candidate fully conforms. The pass and
fail labels are unchanged; a pass authorizes only separately freezing D1 exposure-count/cost design.

The access boundary remains public governance transactions, receipts, payloads, call traces, fixed getters, proxy
slots, bytecode hashes and finality metadata. Account state, participant actions/traces, liquidations,
prices/oracles and realized responses remain locked. No paid data, external worker or GPU is used. Both V100s and
the RTX 2060 remain idle. With the one-request-per-second global throttle, the lower-bound runtime is about 3.2
minutes plus provider and trace latency; budget 15 minutes.
