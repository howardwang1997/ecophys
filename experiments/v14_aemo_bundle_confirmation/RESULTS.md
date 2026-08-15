# AEMO fresh-day set-valued offer-bridge confirmation — result

**Decision:** `PASS_FRESH_SET_VALUED_OFFER_BRIDGE_CONFIRMATION`

**Protocol commit:** `9ee922f91ca1b4be4257e8555b49d13f27272c1a`

**Sample:** 7 July 2026, selected mechanically and frozen before ZIP or row access.

## Integrity and retention

Each of the three frozen AEMO objects was requested exactly once. All returned HTTP 200 with the exact frozen byte
count. The 18,244,129 bytes were uploaded to the frozen R2 prefix and all remote sizes and SHA-256 metadata were
verified before any ZIP was opened.

| Object | Bytes | SHA-256 |
|---|---:|---|
| `BIDMOVE_COMPLETE` | 9,224,570 | `18f3b5fd8485c86dad4ebcd56546305ad9d9461e6c4910acec1ecfdaae6a04d2` |
| `NEXT_DAY_DISPATCH` | 8,641,259 | `b7a2ba62396ffcb07b61c73af10aeb705ab54196581bfbb4dcf82e44f392e214` |
| July `DUDETAILSUMMARY` | 378,300 | `c87e888dbae6e65fba3b07aba89c04c1f3e3a17f38e811cfe0b1ee6833139b1e` |

All three CRC, parse and exact-byte checks passed. Artifact hashes are:

- download receipt: `e5d38651f1cd77385bb791e89a7584dc685d938ab090c4596865f9a939e71899`;
- R2 retention receipt: `a1f0cb438733b03c07547d83a70633e55a693642ef9f7ce2dcb688a13fa15f87`;
- summary: `dc36b2fe31cc5c230def8f808a7efef1fa320f80ab30e61f1999d367dd9e466b`.

## Frozen-gate result

All 25 preregistered gates passed. The five required table headers were exact and nonempty. There were 1,422,918
target rows and 1,506,415 total MMSDM data rows. All declared primary keys were unique; all 4,559,065 contracted
timestamps parsed; every bid date and every interval matched the frozen market-day window.

Supporting joins were exact:

- 639,648/639,648 period bids matched a daily-bid parent;
- 594,720/594,720 tracker rows matched a physical dispatch row;
- 163,008/163,008 physical dispatch rows matched exactly one effective identity row;
- effective-identity overlap count was zero.

## Prospective relation result

All 594,720 tracker records had a valid offer reference and a valid frozen relation:

| Candidate relation | Count |
|---|---:|
| one candidate | 549,792 |
| exact two-candidate `{GEN, LOAD}` bundle | 44,928 |

Singleton directions were `GEN` (337,824), `LOAD` (108,288) and `BIDIRECTIONAL` (103,680). Every one of the
44,928 pairs had exactly one `GEN` and one `LOAD`, no repeated direction, exactly one effective `BIDIRECTIONAL`
identity and an allowed bid type: `ENERGY` 18,432, `LOWERREG` 13,248 or `RAISEREG` 13,248. The pairs involved 64
unique DUIDs. Every frozen violation count was zero.

Realized dispatch was not used to select either bid leg.

## Interpretation and next gate

The exact development-day pattern reproduced on an untouched cross-month day. This confirms that a modern
`DISPATCHOFFERTRK` record should be represented as a set-valued applied-offer version for BDU energy/regulation,
not forced into a unique direction row.

This is a narrow data-model result. It does not validate raw submissions, rejected actions, historical table
versions, dispatch optimization replay, causal adaptation, prediction or EcoMD. E1a remains an immutable failure
of the old unique-direction contract; E1b validates its prospectively specified replacement.

The only newly unlocked action is to freeze a limited multi-day, version-aware development-panel protocol that
tests stability of this observation bridge. Experiment 156, prospective target outcomes and all GPU/model work
remain locked.

Compute used: local CPU only; zero GPU-hours, zero paid data and no remote worker.
