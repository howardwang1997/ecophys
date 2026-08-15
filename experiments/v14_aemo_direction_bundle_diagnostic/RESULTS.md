# AEMO direction-bundle post-hoc diagnostic result

**Status:** `POST_HOC_DEVELOPMENT_DIAGNOSTIC_NO_GATE_DECISION`

**Analyzer commit:** `b6572efc96b816268bb959e033a9127930970c7f`

**Artifact SHA-256:** `d8b4bb0ffe6ede3fadf00cdac68c6851568fab132b6e2c94162c8bb4317cfaa2`

This diagnostic was motivated by, and executed after observing, the frozen E1a failure. It cannot override
`FAIL_MODERN_ROW_CONFORMANCE_SMOKE` and is not confirmation evidence.

## Exact reconciliation

The diagnostic independently reproduced all 592,560 tracker records and the exact 43,200 ambiguous records in
the frozen E1a summary. There were zero invalid tracker references and zero unmatched records.

Candidate cardinality and direction sets were:

| Structure | Tracker records |
|---|---:|
| one candidate | 549,360 |
| two candidates | 43,200 |
| one `GEN` row | 341,616 |
| one `LOAD` row | 106,368 |
| one `BIDIRECTIONAL` row | 101,376 |
| two-row `{GEN, LOAD}` set | 43,200 |

Every ambiguous record had exactly two candidate rows, exactly the directions `{GEN, LOAD}`, and no repeated
direction. The 43,200 records covered 60 DUIDs and split by bid type as follows:

| Bid type | Ambiguous records |
|---|---:|
| `ENERGY` | 17,280 |
| `LOWERREG` | 12,960 |
| `RAISEREG` | 12,960 |

Every ambiguous record matched exactly one effective identity, and all 43,200 identities had
`DISPATCHTYPE=BIDIRECTIONAL`. `DISPATCHSUBTYPE` was empty and is not used to support the interpretation.

## Why signed dispatch is not a repair

Every ambiguous record matched physical dispatch, but the realized `TOTALCLEARED` signs varied:

| Bid type | Negative | Zero | Positive |
|---|---:|---:|---:|
| `ENERGY` | 3,109 | 12,325 | 1,846 |
| `LOWERREG` | 2,718 | 8,648 | 1,594 |
| `RAISEREG` | 2,718 | 8,648 | 1,594 |

The large zero group alone prevents a complete sign selector. More importantly, `TOTALCLEARED` is the realized
dispatch outcome. Using it to choose an ex-ante bid direction would leak outcomes into actions even when nonzero.

## Development interpretation

The exact pattern supports a set-valued observation bridge: a `DISPATCHOFFERTRK` record identifies an applied
offer version, and for BDU energy/regulation services that version legitimately contains both direction-specific
period rows. The correct object is a bundle, not one arbitrarily selected row. Single-row `BIDIRECTIONAL` records
remain distinct and are consistent with direction-independent services.

This is a clean development finding, but it is still an observation-schema result—not a market phenomenon,
mechanism replay, causal effect or EcoMD result. Confirmation requires a fresh date selected without inspecting
its rows. E1a remains failed, and no multi-day acquisition or GPU training is unlocked by this diagnostic.

The fresh-day E1b contract should require every tracker relation to be either one candidate or exactly one
`{GEN, LOAD}` pair; every two-row pair must have unique directions, an effective `BIDIRECTIONAL` identity and bid
type in `{ENERGY, LOWERREG, RAISEREG}`. It must never use realized dispatch to choose an offer leg.
