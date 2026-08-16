# Execution-evidence adapter contract

**Date:** 2026-08-17

**Status:** design boundary only; implementation waits for a B0 pass and a frozen B1 source sample.

## 1. Purpose

The adapter converts version-pinned external execution evidence into ESTIR-like normalized policy-shock records.
It does not execute the EVM, infer missing calls or writes, or treat emitted configuration events as authoritative
state. Its purpose is to make every empirical compiler claim traceable to a bytecode/fork identity, transaction,
receipt, ordered execution path and authoritative pre/post value.

## 2. Authority hierarchy

1. chain ID, block number/hash, transaction index/hash and finalized status;
2. fork-pinned execution semantics and official reference fixtures;
3. raw transaction and canonical receipt;
4. historical runtime bytecode/code hash for every executed address and implementation route;
5. instruction/call trace plus state-difference evidence;
6. independently queried T-1/T protocol getters or storage values;
7. verified source/ABI as a decoding and interpretation aid, never as a replacement for executed bytecode; and
8. normalized ESTIR record plus a complete uncertainty/coverage mask.

A lower item cannot silently repair disagreement in a higher item. Any unresolved conflict fails the program.

## 3. Minimum normalized objects

### Evidence envelope

- schema version and adapter version;
- chain/fork identity and block/transaction coordinates;
- provider/client/version and retrieval timestamp;
- immutable raw-evidence hashes and licence/retention metadata;
- bytecode, source and ABI identities; and
- explicit completeness, unsupported-feature and disagreement fields.

### Ordered frame record

- unique frame ID, parent ID, depth and sibling order;
- call/create/self-destruct kind, caller, context address and executed code hash;
- input/output/value hashes, success/revert/error status and gas metadata when available;
- ordered child-frame IDs;
- storage reads/writes attributed to the frame;
- emitted-log identities and order; and
- committed-versus-rolled-back effect status.

### State-effect record

- fully qualified coordinate: chain, protocol/version, contract, storage/getter route, asset/account and field;
- exact integer T-1 and T value with source block hashes;
- ordered intermediate values when observed;
- terminal sparse delta;
- frame/write provenance; and
- coverage/uncertainty status. Unknown is a first-class value and never means zero.

### Program record

- ordered root frames and complete included call cone;
- receipt-log reconciliation;
- terminal operator and path signature;
- program-level uncertainty mask; and
- deterministic content hash over normalized evidence.

## 4. Conformance gates

All gates are conjunctive for an admitted program:

1. strict schema rejects unknown fields, ambiguous integer encodings and missing identities;
2. two allowed header sources agree on chain/block identity;
3. transaction and receipt identity/order/status are canonical;
4. frame tree has one root, valid parents, exact sibling order and no cycles/orphans;
5. executed code hashes and proxy/implementation routes are pinned at the event block;
6. reverted frames and descendants cannot contribute committed terminal writes or receipt logs;
7. normalized committed logs reproduce the canonical receipt exactly;
8. terminal effects reproduce every admitted T-1/T getter or storage change with no unexplained nonzero write;
9. two independent trace/state-evidence paths agree on the response-relevant call cone and effects, or the
   disagreement is explicitly fatal;
10. official/reference execution fixtures cover every admitted semantic feature for the pinned fork;
11. normalization is deterministic and invariant to irrelevant provider JSON ordering; and
12. unsupported opcodes, storage aliasing, missing state, incomplete traces or source/bytecode mismatches fail
   closed rather than being mapped to a no-op.

Passing these gates establishes evidence conformance for the sampled programs, not causal identification or
predictive value.

## 5. Provider/client adapters

The normalized contract is provider-neutral. A provider-specific parser may consume Geth-style call/prestate
traces, raw instruction traces or equivalent reference-client output, but every adapter must declare which fields
are directly observed, reconstructed or unavailable. `callTracer` alone is insufficient for storage effects;
receipt logs alone are insufficient for reverted/intermediate paths; verified source alone is insufficient for
executed semantics.

The first implementation must be restricted to the exact clients/providers present in the frozen B1 sample. New
formats, chains or forks require versioned adapters and fresh conformance fixtures; permissive fallback parsing is
forbidden.

## 6. Data and compute requirements

- **Before B0 pass:** no implementation or execution; only this schema contract.
- **B1 pilot:** transactions, receipts, historical bytecode/source, raw/call traces, state differences and T-1/T
  getters for a mechanically sampled outcome-blind subset. CPU, network and storage dominate; GPU use is zero.
- **B1 breadth:** shard by deployment/program, retain immutable raw hashes and normalized records, and run
  independent reconstruction. V100/RTX hosts may supply CPU workers with CUDA hidden.
- **B2 and later:** account/state expansion is separately budgeted and remains locked until B1 conformance passes.

The adapter cannot unlock account outcomes, model training or a venue claim by itself.
