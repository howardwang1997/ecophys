# Aave V3 bundle-structure feasibility v1 results

**Run date:** 2026-08-16

**Protocol commit:** `d5636dd751b7654a24e8fae9fc39b72c6cc4a76b`

**Decision:** `COMPLETE_DEVELOPMENT_BUNDLE_STRUCTURE_AUTHORIZE_VECTOR_COMPILER_PROTOCOL_DESIGN_ONLY`

## Scope and evidential status

This was a deterministic, local-CPU replay of the immutable A1a normalized event directory. It made no network
call and opened no transaction, receipt, calldata, trace, historical state, account, action, liquidation, price or
realized-response row. Paid data, external workers and GPU use were zero.

This result is **development-only**. Aggregate bundle counts and some shapes were inspected before the protocol
freeze while diagnosing A1a. The replay makes those definitions and counts reproducible; it is neither blind nor
confirmatory evidence and has no post-observation support threshold.

## Integrity result

All seven gates passed. An independent verifier that does not import the analysis module reproduced the parent
hashes and decision, all 3,119 unique log identities, the exact 77 transaction records, every sparse net vector,
the round-trip flag, all aggregate counts and the access boundary.

| Object | SHA-256 |
|---|---|
| Frozen manifest | `e8cf60b2577bdf9e46f68f15c0c7e21931a3d705357420a907b75d74838a65e0` |
| Derived summary | `922312a9c75a64cfe66a1ef828140df938929e4bc6fbac9200a3a1f6fa9d9db9` |
| Parent normalized directory | `1d1d73b5f5ba51c60841a411edf563317f143e9599e3eac958643895c90648ec` |

The derived summary is 288,390 bytes. Reproduction is:

```bash
conda run -n ecophys python \
  experiments/v14_aave_v3_bundle_structure_feasibility/verify_artifact.py
```

## Structural findings

| Quantity | Result |
|---|---:|
| Transaction bundles containing a decoded collateral-configuration event | 77 |
| Bundles with at least one known-predecessor net change | 27 |
| Bundles with a known net LT decrease | 5 |
| Pure emitted-LT net-vector bundles | 0 |
| Bundles containing an intermediate leave-and-return round trip | 1 |
| First-observed asset occurrences with unknown emitted predecessor | 54 |
| Distinct Configurator topic identities in the parent | 28 |
| Bundles containing no opaque Configurator topic | 13 |
| Maximum Configurator logs in one bundle | 83 |
| Maximum known net-vector dimension | 20 |

The net-vector dimension distribution is highly uneven: 50 bundles have zero *known* net dimensions, 11 have one,
five have two, and the remainder reach 20. The zero-dimensional count must not be read as 50 no-change programs:
54 asset occurrences lack an earlier emitted configuration, so their predecessor is deliberately unknown. Only
three zero-dimensional bundles have known predecessors for every affected asset.

The sole detected round trip is transaction
`0xe2391ea418e16d70196ca3d77dfc836cca1096eebf65e423d52ad867b416478f` at block 25,037,701. Its decoded asset LT
follows `7500 -> 1 -> 7500 -> 1 -> 7500`, returning to the known predecessor. Its terminal net vector is therefore
zero even though its execution path is not. This demonstrates why a compiler must retain both the execution trace
and the terminal sparse operator.

## Interpretation

The parent contains genuine program-level structural breadth, but the current directory is not an executable
policy benchmark. Only one of 28 Configurator topic identities is semantically decoded here; receipt/call paths,
historical implementations and authoritative T-1/T state remain unopened. Consequently:

- the result supports designing an ABI/source/state/receipt compiler protocol;
- it does not establish that 77 usable policy programs will survive exact compilation;
- it does not identify causal effects of individual coordinates inside a bundle;
- it does not authorize accounts, participant outcomes, G1 or model training; and
- the zero pure-LT count reinforces retirement of the Ethereum scalar-LT route rather than relaxing isolation.

The next admissible action is to freeze B0 before opening another deployment: name the deployment universe,
historical source/address authorities, exact program inclusion rule, support requirement and untouched
train/validation/test separation. B1 execution begins only if that protocol passes its zero-account breadth gate.
