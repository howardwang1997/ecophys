# AEMO NEMDE daily-archive tail inventory v1

**Frozen:** 2026-08-15 06:14:35 UTC

**Parent:** `c208f199da24338b9a61dae6cdd1c8967108cab1`

**Manifest:** `data/manifests/aemo_nemde_tail_inventory_v1.yaml`

## Question

Can the official date-partitioned NEMDE audit ZIPs expose a complete central directory and one bounded,
range-addressable dispatch-interval member without downloading a full day?

This is a metadata-only development gate after the monthly `BIDPEROFFER` prefix failed. It does not inspect XML,
validate fields, replay the solver, identify a participant decision or estimate an intervention effect.

## Source finding and boundary

AEMO says that its daily production NEMDE format files contain input, output and price-setting sections and that
there is one file for each of 288 five-minute dispatch intervals. The historical archive exposes those files as
day-level `NemSpdOutputs_YYYYMMDD_loaded.zip` objects. This is distinct from access to the NEMDE executable or the
paid NEMDE Queue.

The current AEMO copyright-permissions page grants general use of publicly available AEMO material with accurate
attribution. The archived DVD notice says personal/non-commercial use only. This protocol does not resolve that
conflict: raw redistribution remains prohibited inside EcoPhys until AEMO supplies written clarification.

## Frozen selection

Reuse the first daily NEMDE archive in each already consumed development month:

| Regime | Date | Declared archive bytes |
|---|---|---:|
| pre-5MS | 2021-01-01 | 116,002,085 |
| post-5MS/WDR | 2021-12-01 | 132,455,595 |

Each object receives exactly one suffix request, `Range: bytes=-1048576`. No retry, extension, replacement or
full-file fallback is permitted. The exact 2 MiB total must be hash-verified in R2 before parsing ZIP metadata.
No XML member may be opened in this protocol.

## Gates

Both tails must contain a valid single-disk, non-ZIP64 end record and the complete central directory. Member names
must cover every interval ID `001..288` for the declared date. Members must be unencrypted and use only stored or
deflate compression. The lexicographically first interval-144 member is the deterministic candidate for a later
protocol, and a conservative local-header-plus-member range bound must not exceed 2 MiB.

`PASS_NEMDE_TAIL_INVENTORY` unlocks only a separately frozen two-member XML conformance audit. A fail prohibits
range extension and sends source design back to review. GPU-hours, paid data, remote workers and target-event rows
are all zero. Experiment 156 and every causal, replay and model claim remain locked.
