# Liquity V2 Agentic Priority Queue D0 v5 Result

**Decision:** **FAIL — close the preregistered Liquity NMI route before support-gate evaluation**

**Failure stage:** exact full log-identity replication

**Formal commit:** `971b985d738da78735d3addffe93a30bbdb7c7d7`

**Frozen config SHA-256:** `22046333a9d1f16a75eaf2acb91c0f25272c2e344a5b7d7b1229ea31dba30edb`

**Failure manifest:** `results/empirical_physics/liquity_agentic_queue_d0_v5_failure.json`

**Manifest canonical payload SHA-256:** `2767a17f204694959d254e1f7a17755a2609bf7507cae3eb6b85d794a9eecf73`

## Result in one sentence

Blockscout returned 24,291 allowed identities and the finalized SQD Portal returned 24,292; the sole SQD-only
identity is independently present in dRPC and OnFinality logs and receipts, establishing a real Blockscout
omission, but the frozen two-source equality gate nevertheless failed and cannot be repaired post hoc.

## Gates completed before failure

The clean v5 run completed the pinned-source audit, event-signature audit, frozen end-block checks, historical
deployment-bytecode checks, and Portal metadata/finality checks. All three frozen qualification shards matched
exactly across Blockscout and SQD:

| Qualification | Event count | Canonical identity SHA-256 | Exact equality |
|---:|---:|---|---|
| 0 | 0 | `4f53cda1...b945` | yes |
| 1 | 50 | `5b11b4fc...d179` | yes |
| 2 | 38 | `65572283...970c` | yes |

SQD also reproduced every previously disclosed OnFinality prefix: 2,507, 3,939, 6,110, and 8,126 cumulative
events at chunks 25, 50, 75, and 100. It completed all 331 frozen chunks and stored 24,292 sanitized identities in
an external checkpoint with payload SHA-256 `4c639da2...c0eaf`. No raw provider response was retained.

## Exact failure

The runner compared canonical tuples

```text
(block_hash, transaction_hash, log_index, contract_address, topic0)
```

and stopped with:

```text
formal=24291, replica=24292, formal_only=0, replica_only=1
```

The single replica-only identity is:

| Field | Value |
|---|---|
| Block | 25,401,761 |
| Block hash | `0x3919ae979122597b3441992de0200ed93b2379856ec3f62b383e9e7bdce4ef18` |
| Transaction | `0x1b0d7de54db2f5b838f6a1a8c169bb18bc9c6fda6fbfefc33cb9f67b5897f109` |
| Log index | 1,756 |
| Contract | `0xa2895d6a3bf110561dfe4b71ca539d84e1928b22` (wstETH TroveManager) |
| Topic 0 | `0xecf6daab6f1facdfdd8dfe32b525744d8a7a940824dd52e2b53c24028ee5faa0` (`BatchUpdated`) |

The discrepancy first appears in chunk 292. A fresh repeat of all chunks 276--300 returned the same
Blockscout/SQD difference. A one-block, one-address, one-topic `eth_getLogs` query then returned zero from
Blockscout and one exact match from each of dRPC and OnFinality. The transaction receipt returned the same exact
identity from dRPC and OnFinality, while Blockscout's receipt omitted it. Together with the finalized SQD record,
three independent witnesses establish that the log is canonical and that Blockscout is incomplete at this point.

This diagnosis explains the failure; it does not erase it. The frozen contract required exact equality between
the declared formal and replica sources. Re-running until Blockscout changes, deleting the extra canonical event,
or replacing the formal source after observing the mismatch would all violate the stop rule.

## What was not learned

The run exited inside `_assert_exact_replication`, before relevant timestamps were attached and before
`summarize_agentic_queue_support` was called. Therefore:

- none of the original sample-support metrics is available;
- no rate, debt, collateral, redemption value/price, queue rank, or adjustment direction was decoded;
- no causal, predictive, market-price, liquidation, or policy result was computed;
- there is no evidence for or against the proposed human-versus-autonomous rank-externality claim;
- EcoMD and all GPUs remained unused.

The observed 24,291/24,292 totals are transport diagnostics, not scientific sample support.

## Consequence for the research program

The preregistered Liquity route is closed before D1. There will be no threshold relaxation, v6 transport swap on
the same observed interval, queue reconstruction, outcome decoding, EcoMD rescue, or GPU experiment. The result
should be retained because it reveals a general engineering requirement for future event-log studies: qualification
must include adversarial high-log-index blocks and receipt-level triangulation, and no single explorer-backed
JSON-RPC should be treated as canonical merely because it passes small random shards.

A future Liquity study would have to be a genuinely new preregistration with an untouched prospective interval
and a canonical acquisition design defined before observing that interval. It cannot be presented as completion
or continuation of this failed D0. The next active NMI/NCS candidate should return to question selection rather
than spend compute on the closed route.
