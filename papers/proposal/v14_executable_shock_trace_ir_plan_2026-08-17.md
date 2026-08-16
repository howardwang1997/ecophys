# Executable Shock Trace IR — zero-network feasibility plan

**Date:** 2026-08-17

**Status:** protocol design only; implement and execute only after the frozen manifest is committed and pushed.

## 1. Purpose and non-claim

The empirical B0 route is blocked on explicit archive access. The useful no-data task is to test whether the paper's
proposed compiler object has a precise, fail-closed intermediate representation before paying for traces/state.
This experiment builds an **Executable Shock Trace IR (ESTIR)** for exact integer state updates.

This is software/method feasibility, not a novelty claim. Read/write-set commutativity is standard program and
database semantics; a terminal-state collision counterexample is elementary. The value is architectural: it
prevents the future model from treating a governance transaction as an unordered parameter vector or silently
discarding transient execution information.

## 2. Formal object

Let an integer state be `x in Z^K` over named coordinates. A program is an ordered sequence of primitive partial
maps `u_1,...,u_m`, with guards allowed to reject execution. The exact interpreter produces

\[
x_i=u_i(x_{i-1}),\quad x_0=x^-,\qquad
\Delta_P(x^-)=x_m-x^-.
\]

ESTIR retains both the terminal sparse vector `Delta_P` and the ordered trace `(x_0,...,x_m)`. For primitive maps
with derived read/write sets `(R_i,W_i)`, the compiler certifies pairwise independence only if

\[
W_i\cap(R_j\cup W_j)=W_j\cap(R_i\cup W_i)=\varnothing.
\]

Under the implemented primitive semantics this condition is sufficient for swapping the pair without changing
guard acceptance or terminal state. A dependency DAG preserves every conflicting order and a deterministic
topological sort canonicalizes only the remaining independent order.

The standard but important counterexample is two programs with the same `Delta_P` and different traces: from
`x=0`, `set(x,1); set(x,0)` and `set(x,0)` both have zero terminal shock, but only the former crosses the transient
boundary. Therefore terminal vectors alone are insufficient for path-sensitive compilation.

## 3. Frozen instruction subset

V1 supports exactly four integer primitives:

- `set(target, value)`;
- `add(target, value)`;
- `copy(target, source, offset)`;
- `require_equal(source, value)`.

Read/write sets are derived from the opcode; callers cannot assert them. Programs require unique instruction IDs,
declared coordinates and strict schemas. Missing coordinates, duplicate IDs, unknown opcodes/fields, failed guards
and integer-type violations fail closed. Booleans are rejected as integers.

This subset does not claim to model the EVM, dynamic storage, external calls, reentrancy, gas, rollback or emitted
events. Those are later compiler obligations. V1 tests only the semantic skeleton needed to represent exact ordered
updates and uncertainty honestly.

## 4. Generated evaluation

No empirical Aave row is read. The exhaustive core uses coordinates `a,b,c`, initial values `{-2,-1,0,1,2}` and a
fixed primitive library of sets, adds, copies and guards. Every ordered instruction pair is evaluated on every
initial state. Successful cases check determinism and sparse support; certified-independent cases also check
swap/commutator soundness.

Two named fixtures are mandatory:

1. an Aave-like risk-configuration round trip with equal terminal state but a nonzero transient trace; and
2. a generic constrained-inventory program with a dependent reorder that changes the terminal result.

The result stores only counts, exact witnesses and a canonical case-ledger SHA-256. It opens no network, chain,
account, action, price or response data.

## 5. Conjunctive gates

1. manifest and parent hashes validate;
2. strict instruction/program schemas reject malformed or incomplete inputs;
3. repeated exact interpretation is deterministic for every admitted generated case;
4. every certified-independent successful pair has zero terminal commutator;
5. a frozen dependent pair has a nonzero commutator and cannot be reordered across its dependency edge;
6. canonical hashes agree for programs differing only by certified-independent swaps;
7. the terminal-collision witness has equal net vectors and unequal trace signatures;
8. every terminal changed coordinate lies inside the union of primitive write sets;
9. both named fixture families reproduce their frozen expected outcomes; and
10. access/claim boundaries remain zero-network, development-only and GPU-locked.

All gates must pass. A PASS authorizes only extension of compiler fixtures/specification while archive access is
resolved. It does not authorize B0 v2, B1 empirical compilation, participant data, G1, model training or a theorem
claim.

## 6. Resource plan

- Data: generated integer fixtures plus hash-pinned existing result metadata; no target row or download.
- Compute: one Mac CPU core, at most 100,000 generated cases and 60 seconds.
- Durable output: one JSON summary below 1 MiB.
- GPU: zero; V100 and RTX workers remain idle; H20 excluded.
- Cost: zero.

## 7. Interpretation

If the gates fail, the current compiler object is underspecified and should be repaired before data acquisition.
If they pass, ESTIR becomes tested infrastructure for B1 design, but only after B0 and archive access pass their own
gates. The experiment cannot raise the NCS/NMI probability by itself; it reduces implementation risk and exposes
which future claims require full trace semantics rather than a net policy vector.
