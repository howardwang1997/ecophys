# Compound III supply-cap activation preflight v1 result

**Protocol commit:** `1dfdecf47d60b3f78a1076d2a09ed60f7ad5fc7f`

**Manifest SHA-256:** `aac34fd0b8bb1d3e1f63b12fb0230f10039a0d2d7019bf8ea461d433cb5b3037`

**Failure artifact SHA-256:** `225266d3fb1e394f0714ceed60000ca42c84476ac8bd1641b4eacb8da30c40c8`

**Decision:** `INFRASTRUCTURE_FAILURE_NO_SUPPLY_CAP_ACTIVATION_RESULT`

## Outcome

The sealed v1 collector was launched once from a clean detached worktree at the exact remote protocol commit. It
stopped at the first candidate's first historical PublicNode code operation. All three permitted attempts to call
`eth_getCode` for the old implementation at block `16,133,170` returned HTTP 403. The endpoint was not changed and
v1 was not rerun.

This is an infrastructure capability failure, not a source-conformance, cap-activation or causal-estimand result.
No candidate can be called saturated, slack, conforming or nonconforming from v1.

## Durable evidence

Before the failure, nine logical operations succeeded on one attempt each:

- Blockscout and PublicNode both returned their chain-ID responses; and
- all seven fixed Blockscout smart-contract metadata GET requests returned HTTP 200.

The source responses were parsed in memory before the next operation, but v1's failure schema intentionally keeps
only response hashes, sizes and attempt outcomes. It does not persist the normalized source-conformance records.
Consequently, HTTP 200 for the seven source records is not evidence that the seven verified-source gates passed.

The failure ledger contains 12 HTTP attempts: nine successes followed by three identical HTTP 403 failures. It
accounts for 1,370,203 response bytes over 14.878 seconds. The three forbidden responses are 152 bytes each and
share response-body SHA-256 `a6d3b310fda9ecc7095ed950ab34fb484e2edc41db7579af4e5490bff95a442a`.
The failure artifact contains the exact collection commit, manifest and parent identities, all nine successful
request/response hashes, every attempt, the bounded exception and the frozen access boundary. It contains no raw
response or source body.

A standalone offline verifier that did not import the collector rejected duplicate JSON keys and reconstructed
the manifest/failure hashes, exact nine-operation prefix, JSON-RPC IDs and request hashes, seven REST paths/hashes,
the failed historical-code request, response-byte accounting, attempt order, mutually exclusive outputs and
access locks. It passed.

## Access and resource accounting

No historical implementation code result, configuration getter, aggregate `totalsCollateral`, account, action,
log/trace, price/oracle, liquidation, post-event state or realized-response row was opened. No paid data, external
worker or GPU was used. Both V100s and the RTX 2060 remained idle.

## Interpretation and next action

The failed operation was a cross-provider reproduction layer, not the scientific quantity itself. D0b already
retains Blockscout historical implementation-code hashes, while D1a still needs a documented source for historical
configuration and aggregate state. Any repair must be a new hash-pinned protocol that preserves the four
candidates, source semantics, six lookbacks, exact-saturation rule, zero-account boundary and non-movable
decisions. It must use official provider documentation rather than an ad hoc candidate probe, persist normalized
source evidence on partial failure if scientifically useful, and be pushed before any further candidate request.

V1 must never be rerun or edited. Account/action/response acquisition, D1b, G1 and every GPU job remain locked.
