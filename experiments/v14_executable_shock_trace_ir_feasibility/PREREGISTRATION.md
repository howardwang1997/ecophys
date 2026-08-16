# Executable Shock Trace IR feasibility v1

**Status:** frozen before implementation and execution.

## Question

Can a minimal exact-integer IR represent ordered policy updates, safely canonicalize only instructions certified
independent by derived read/write sets, and distinguish terminally identical programs with different transient
paths?

This is a development-only software feasibility test. It is not an EVM compiler, empirical Aave validation,
theorem-novelty claim or permission to open B0/B1/G1.

## Inputs and parents

The only parent evidence is the immutable Ethereum development bundle result and the target-free transport-repair
failure. Parent paths and SHA-256 values are fixed in the JSON manifest. Evaluation inputs are generated from the
manifest's exact coordinate/value/instruction grid; no existing event directory or outcome row is read by the
runner.

## Semantics

State coordinates contain exact Python integers, excluding booleans. Four strict opcodes are admitted: `set`,
`add`, `copy` with integer offset, and `require_equal`. The implementation derives each opcode's read/write sets.
Every program has unique instruction IDs and an explicit state schema.

Execution is ordered and fail-closed. The result includes the terminal sparse delta and a normalized per-step
trace. The dependency graph retains original order for every read/write or write/write conflict. A deterministic
topological sort may reorder only certified-independent instructions, using instruction ID as the tie-breaker.

## Evaluation and witnesses

- Exhaust all ordered pairs from the fixed 24-instruction library over all 125 states on coordinates `a,b,c`.
- Require repeated execution equality and terminal support containment for every successfully executed case.
- For every certified-independent pair that succeeds in both orders, require identical terminal state.
- Require canonical program/hash equality for a fixed independent-swap pair.
- Require a fixed dependent `set`/`add` pair to have a nonzero terminal commutator and retain its original order.
- Require an Aave-like `8000 -> 1 -> 8000` liquidation-threshold round trip to collide terminally with a no-op
  program while retaining a different trace signature.
- Require a generic inventory/cap dependent-order fixture to reproduce different terminal results.
- Feed malformed schemas, duplicate IDs, booleans, missing coordinates and unknown opcodes to the validator and
  require rejection.

Only aggregate counts, exact named witnesses and a canonical ledger hash are durable.

## Decision and locks

All ten manifest gates must pass for
`PASS_ESTIR_SOFTWARE_FEASIBILITY_AUTHORIZE_COMPILER_FIXTURES_ONLY`. Otherwise the result is
`FAIL_ESTIR_UNDERSPECIFIED_KEEP_EMPIRICAL_COMPILER_AND_GPU_LOCKED`.

Neither decision authorizes archive access, B0 v2, B1 empirical receipts/traces/state, account/outcome rows, G1 or
GPU work. No result may be described as a new theorem; read/write commutation and terminal-collision facts are
standard semantics used as implementation obligations.

## Resource cap

One Mac CPU core, no network, at most 100,000 generated cases, at most 60 seconds and at most 1 MiB output. No paid
data, remote worker, V100, RTX GPU or H20 is used.
