# Morpho Public Allocator pressure displacement — D0 support freeze

## Binding decision before event counts

The source-bound T0 passed from clean commit `4a480108e`, but it established only accounting identities. This D0
asks a narrower question before any amount, rate, utilization or outcome is decoded:

> Is there enough source-exact, independently witnessed Ethereum and Base transaction support to justify exact
> reconstruction of atomic Public Allocator routing followed by a target-matched Morpho borrow?

This contract was frozen after inspecting official source, deployment registries, finalized dataset metadata and
four exact cutoff headers. No Public Allocator event count, transaction identity, amount or market outcome was
queried before the freeze.

## Fixed systems and interval

Only the two oldest mature deployments are eligible. Adding another chain after seeing support is forbidden.

| Chain | Public Allocator | Morpho | Start block | Frozen finalized end |
|---|---|---|---:|---:|
| Ethereum | `0xfd32fA2ca22c76dD6E550706Ad913FC6CE91c75D` | `0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb` | 19,375,099 | 25,795,523 |
| Base | `0xA090dD1a701408Df1d4d0B85b716c87565f90467` | `0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb` | 13,979,545 | 50,214,705 |

The official Morpho SDK commit is `eb27628b88300665405e0bd0bde395b834cae969`. Its address registry fixes the
addresses and deployment blocks above. The cutoff block hashes were obtained from the finalized SQD datasets and
matched independently before event retrieval:

- Ethereum block 25,795,523: `0x95f88569b407a1c3619efdbc7f99e7e59589a57c92488ed87bb3d6d2a53d6926`,
  timestamp `2026-08-20T09:45:59Z`; matched dRPC, Blockscout and OnFinality headers.
- Base block 50,214,705: `0x7b2f535e8b08fdef902f1260dfc66e33ffc28506b7c8a1dafa0ba2a4b69f156d`,
  timestamp `2026-08-20T09:39:17Z`; matched the Base public RPC and Tenderly headers.

## Exact identity definition

The only retained log fields are block number/hash/timestamp, transaction hash/index, log index, emitting address
and topics. RPC responses necessarily contain non-indexed `data`, but the D0 implementation must never decode,
persist, hash into a scientific feature or summarize that field.

One Public Allocator call group is constructed in receipt log order:

1. one or more `PublicWithdrawal(address,address,bytes32,uint256)` logs from the exact Public Allocator;
2. one terminal `PublicReallocateTo(address,address,bytes32,uint256)` from the same contract, with the same indexed
   sender and vault; and
3. a later `Borrow(bytes32,address,address,address,uint256,uint256)` from the exact Morpho contract in the same
   transaction, whose indexed market id equals the terminal target market id.

Each terminal consumes the preceding unconsumed, sender/vault-matched withdrawals. Any orphan, ambiguous or
out-of-order Public Allocator sequence is unclassified and makes the required classification rate fail. A
transaction with at least one target-matched group is an **atomic routing--borrow identity candidate**. It is not
yet called a genuine JIT event: D0 does not decode routed or borrowed amounts, verify `0 < r <= x`, or verify the
target market's IRM. Those are binding D1 filters.

A directed donor--target edge is the ordered pair of the donor market id from `PublicWithdrawal` and target market
id from the matched terminal. Counts are over unique transactions, vaults, UTC dates and directed edges; repeated
logs within a transaction never create pseudoreplicates.

## Transport and omission audit

The complete Public Allocator identity stream is read independently from:

- finalized SQD Portal (`ethereum-mainnet` and `base-mainnet`); and
- a full-range JSON-RPC `eth_getLogs` scan (Ethereum Blockscout; Base Tenderly), with deterministic splitting.

Before the full interval, three fixed 10,000-block qualification shards per chain must reproduce the frozen end
header and identical RPC-versus-SQD identity sets. The full audit then requires:

1. no full-RPC-only event absent from SQD;
2. at most ten SQD-only events and at most a `0.1%` SQD-only fraction per chain;
3. every SQD-only event verified exactly in a receipt from the separately fixed receipt RPC;
4. every transaction used for classification fetched as a receipt with exact block hash, transaction hash,
   emitting addresses, topic arrays and log ordering; and
5. the 20 densest Public Allocator blocks per chain, or all if fewer, explicitly reported with zero unresolved
   identity mismatch.

This asymmetric rule accounts for a previously observed isolated Blockscout omission without permitting an
unbounded one-source sample. Any RPC-only log is evidence that SQD omitted a canonical event and is a hard stop.
Any unresolved discrepancy, wrong cutoff header, duplicate identity, receipt mismatch or exhausted resource
budget stops before support metrics are interpreted.

## Frozen support gates

All gates are conjunctive:

| Gate | Threshold |
|---|---:|
| chains passing transport and support | exactly Ethereum and Base |
| target-matched unique candidate transactions | at least 500 pooled |
| target-matched candidate transactions | at least 100 on each chain |
| active first-to-last span | at least 90 days on each chain |
| distinct active UTC dates | at least 30 on each chain |
| distinct vaults in matched groups | at least 3 on each chain |
| distinct donor--target edges | at least 4 on each chain and 12 pooled |
| Public Allocator sequence classification rate | exactly 100% |
| candidate receipt verification rate | exactly 100% |
| unresolved transport/identity discrepancies | zero |

The 500-candidate D0 floor is deliberately higher than the later 300-event analysis floor. D1 must still retain
at least 300 events after decoding exact amounts, checking `0 < r <= x`, binding market parameters to the official
AdaptiveCurveIRM and applying all reconstruction checks. D0 success cannot substitute for that attrition gate.

## Forbidden before D0 passes

- supplied, withdrawn or borrowed amounts and shares;
- flow-cap values, balances, utilization and interest rates;
- borrower, supplier or liquidator behavior beyond event-class identity;
- prices, yield, liquidation, loss, bad debt or incident labels;
- the Resolv event window or any outcome-based sample choice;
- EcoMD, learned models, hyperparameter selection, GPU jobs or paid data.

The result artifact retains aggregate counts, timing support, transport statistics and canonical identity digests,
not raw transaction hashes, addresses or market ids. A failure closes this route without adding chains, changing
cutoffs or relaxing thresholds.

## Data and compute

All data are free public source code, finalized indexed log identities and public JSON-RPC receipts. D0 is bounded
at 25 CPU core-hours, 50 GB transferred and 1 GB retained derived data. GPU hours and paid-data spend are zero.
The Mac is sufficient; the two V100 workers and RTX 2060 remain idle because they cannot improve an identity gate.

## D0 pass does and does not authorize

A full pass authorizes a separately frozen D1 exact-replay design. D1 may then decode the amounts and state needed
to test feasibility and must retain 300 amount-compatible AdaptiveCurveIRM events. It still may not inspect future
participant response or market outcomes until reconstruction and chronological split gates pass.

A D0 pass does not establish signal displacement in the field, delayed controller memory, causality, novelty,
NMI fit or NCS fit. The paper route remains AMBER until the observed consequence exceeds the contemporaneous
accounting identity and survives a sealed cross-chain test.
