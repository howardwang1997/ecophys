# Aave V3 bundle-structure feasibility v1

**Frozen date:** 2026-08-16

**Status:** development-only structural replay; bundle counts and shapes were explored before freeze.

## Question

Can the failed scalar-LT directory be deterministically reorganized into transaction-level sparse policy vectors,
and does the existing Ethereum artifact contain enough structural breadth to justify designing an executable
vector-policy compiler?

This is not a blind support test. The parent contains no participant outcomes, but aggregate bundle counts and
several shapes were inspected while diagnosing A1a. The purpose of this protocol is reproducibility, exact
definitions and route selection. No statistic may be presented as confirmatory evidence.

## Immutable input and access

The only data input is the hash-pinned A1a normalized directory at
`1d1d73b...648ec`, with its summary and manifest parents. The A1a decision remains
`FAIL_AAVE_LT_EVENT_DIRECTORY_KEEP_ACCOUNTS_RESPONSES_AND_G1_LOCKED`.

No network call is allowed. Transactions, receipts, calldata, traces, historical state, accounts, actions,
liquidations, price values and realized responses remain unopened. The run uses local CPU only and writes one
derived JSON summary.

## Exact vectorization

Rows are ordered by block number, transaction index and log index, then grouped by block/transaction identity.
For every asset with `CollateralConfigurationChanged` in a transaction:

1. the predecessor is the last emitted configuration strictly before the transaction;
2. a first-observed asset has unknown predecessor and is never imputed as zero;
3. the post value is the last emitted configuration for that asset in the transaction;
4. the net vector contains every nonzero `post - predecessor` coordinate over LTV, LT and liquidation bonus; and
5. an intermediate path that leaves and returns to the predecessor is a round trip with zero net change.

All other Configurator logs are retained as topic-count identities. They are not assigned invented semantics. A
“pure emitted LT vector” is nonempty and changes no decoded field except LT. It is not called isolated because
opaque Configurator topics and other-contract actions remain unresolved.

## Integrity gates and decision

Seven gates check parent hashes/decision, exact unique log partition, deterministic transaction grouping, unknown-
predecessor handling, net-vector reconstruction, round-trip detection and preservation of the zero-network/zero-
outcome boundary. There is deliberately no support threshold: counts were already explored.

Completion yields
`COMPLETE_DEVELOPMENT_BUNDLE_STRUCTURE_AUTHORIZE_VECTOR_COMPILER_PROTOCOL_DESIGN_ONLY`. It authorizes only a new
protocol design that source-decodes historical ABIs and validates transaction receipts, payloads, calls and
authoritative T−1/T state for every included bundle. It does not authorize accounts, G1 or GPU training.

## Resource budget

Expected runtime is seconds on one Mac CPU core. Input is about 2.1 MiB and durable output should be below a few
MiB. Paid data, external workers and GPU-hours are zero. Both V100s and the RTX 2060 stay idle; H20 is excluded.
