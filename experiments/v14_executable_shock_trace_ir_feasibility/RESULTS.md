# Executable Shock Trace IR feasibility v1 result

**Decision:** `PASS_ESTIR_SOFTWARE_FEASIBILITY_AUTHORIZE_COMPILER_FIXTURES_ONLY`

## Sealed execution and integrity

- Protocol commit: `b7b123e4ed970f1f15bad5d46a8aef04679be640`, pushed and remotely verified.
- Manifest SHA-256: `045cbbc682705204ea1e02522bbe30e59b00a09ff8645e33fbb48242495090e8`.
- Source SHA-256: `eca01f7301a61b6eae217da52a2b573f76281833c00d2daa74c9c4bdac73bf85`.
- Summary SHA-256: `2f9ed635eb7693d0e4108df5172e12662eb6f43d570b7e176b67b845f4c9dfa5`.
- Case-ledger SHA-256: `66611df2bfe7f6e668633019a538c17f6bbad99de739346cd20d08fc5922d814`.

The clean detached preflight passed eight focused tests, format/Ruff, strict mypy, manifest validation and all
parent hashes/decisions. The formal run took 3.06 seconds and wrote 3,628 bytes. An independent full reconstruction
took 2.83 seconds and matched the complete artifact, including every count, witness, gate and ledger hash.

## Exhaustive generated result

| Quantity | Result |
|---|---:|
| Instructions | 24 |
| Initial states | 125 |
| Ordered pair/state cases | 72,000 |
| Duplicate-ID schema rejections | 3,000 |
| Successful forward executions | 55,830 |
| Guard-rejected forward executions | 13,170 |
| Certified-independent cases | 38,250 |
| Determinism violations | 0 |
| Independent acceptance violations | 0 |
| Independent terminal-state violations | 0 |
| Independent canonical-hash violations | 0 |
| Sparse-support violations | 0 |

All ten conjunctive gates pass. The five malformed-input checks—unknown opcode, unknown field, boolean-as-integer,
duplicate instruction ID and missing coordinate—also reject as frozen.

## Named witnesses

- The independent `set(b)`/`add(a)` pair has the same terminal state in either order and the same canonical hash;
  both forms canonicalize to `a_add_a, z_set_b`.
- The dependent `set(a,1)`/`add(a,1)` pair produces `a=2` forward and `a=1` reversed. Each dependency-preserving
  canonical form retains its original order.
- From liquidation threshold 8,000, the Aave-like `8000 -> 1 -> 8000` program and an empty program both have an
  empty terminal delta, but their trace hashes differ and the transient value 1 is retained.
- In the generic inventory fixture, setting cap to 20 before copying cap to inventory yields inventory 20; reversing
  the dependent order yields inventory 12.

## Interpretation

The result supports three implementation choices:

1. exact mechanism instructions should remain ordered unless read/write independence is certified;
2. a dependency partial order is a safe canonical representation for this limited primitive subset; and
3. the compiler must retain path information as well as the terminal sparse vector.

These are standard program-semantics obligations, not a new theorem. Exhausting a small integer grid is not a proof
of full EVM correctness. V1 omits rollback, nested/external calls, emitted events, dynamic storage keys, aliasing,
reentrancy, gas and source-to-bytecode conformance.

No network, market/chain row, account/outcome datum, paid data, remote worker or GPU was used. The PASS authorizes
only compiler fixture/specification extension. B0 v2, empirical B1, accounts, outcomes, G1 and GPU training remain
locked behind the separate archive-data and scientific-support gates.
