# AEMO modern bundle-bridge stability panel — repaired result

**Decision:** `PASS_MODERN_BUNDLE_STABILITY_PANEL`

**Repair protocol commit:** `59540001a5ce9ee6a340ea346e5755609c4bdd77`

**Preserved v1 decision:** `FAIL_PANEL_IMPLEMENTATION_PRE_PARSE`

## Provenance

The repair changed only the missing derived-day row-cap field. It made zero AEMO source requests and changed no
date, object, schema, relation, threshold or claim boundary. All ten exact v1 objects were verified and materialized
from R2 before content access; staged input remained 71,350,764 compressed bytes.

Artifact SHA-256 values are:

- R2-only materialization receipt:
  `1fb6c8ff64aed55bd1f39f9db4adfe4c1cd0d86aa6ace220aed8c7db5bd51582`;
- aggregate/day-level summary:
  `d939fffd8bc7673eb0aac78e06ae2abf38b1ea27e81cba67d03c355bec77ec88`.

## Per-day decisions

Every date independently passed all 25 frozen gates.

| Market date | Tracker rows | Exact `{GEN, LOAD}` pairs | Pair rate | Relation violations |
|---|---:|---:|---:|---:|
| 2026-06-23 | 595,584 | 43,488 | 7.3017% | 0 |
| 2026-06-30 | 596,880 | 44,928 | 7.5271% | 0 |
| 2026-07-14 | 594,720 | 44,928 | 7.5545% | 0 |
| 2026-07-28 | 595,008 | 45,216 | 7.5992% | 0 |

For each day, exact acquisition/R2 materialization, CRC, five schemas, timestamps, primary keys, market windows,
bid parentage, tracker-to-offer, tracker-to-physical-dispatch and dispatch-to-effective-identity gates passed.
Identity overlap was zero. Every multi-row relation was one unique `{GEN, LOAD}` pair for exactly one effective
`BIDIRECTIONAL` identity and an allowed `ENERGY`, `LOWERREG` or `RAISEREG` bid type. Realized dispatch selected no
leg.

## Aggregate

- days passing: 4/4;
- tracker records: 2,382,192;
- singleton relations: 2,203,632;
- exact two-leg bundles: 178,560 (`7.4956%`);
- target rows: 5,697,359;
- total MMSDM rows: 5,975,309;
- contracted timestamps parsed: 18,255,035;
- pair bid types: `ENERGY` 73,152, `LOWERREG` 52,704, `RAISEREG` 52,704;
- total frozen relation violations: 0.

## Interpretation

Together with the June development diagnosis and untouched 7 July E1b confirmation, the exact set-valued relation
is supported on six Tuesdays across two monthly identity snapshots. This is strong evidence that the modern public
observation bridge is temporally stable within these table versions. It also confirms that forcing a unique
direction row is the wrong representation for bidirectional energy/regulation offers.

The result does **not** establish historical table-version portability, raw participant submissions or rejected
actions, dispatch optimization replay, causal adaptation, prediction or EcoMD. It is a necessary data-model result,
not the flagship scientific claim. The next admissible work is a separately frozen historical-version bridge audit
and continued prospective action/identity provenance work; GPU model training remains locked.

Resources used: local CPU, existing R2, zero new source bytes in the repair, zero paid data, zero remote workers and
zero GPU-hours.
