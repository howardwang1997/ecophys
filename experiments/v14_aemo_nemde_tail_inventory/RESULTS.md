# AEMO NEMDE daily-archive tail inventory v1 — result

**Decision:** `PASS_NEMDE_TAIL_INVENTORY`

The pushed protocol at `0787be5f04f7d66e80c497f85051ce2b742bcc11` was executed once. Both exact 1 MiB
suffix requests returned HTTP 206 with the frozen archive totals. Both byte strings were uploaded to R2 and
size/SHA-256 verified before ZIP metadata was parsed. No XML member was opened.

| Date | Members | Interval set | Interval-144 member | Compressed bytes | Conservative later range bound |
|---|---:|---|---|---:|---:|
| 2021-01-01 | 288 | 001–288 complete | `NEMSPDOutputs_2021010114400.loaded` | 404,030 | 469,595 |
| 2021-12-01 | 288 | 001–288 complete | `NEMSPDOutputs_2021120114400.loaded` | 459,136 | 524,701 |

Both central directories were complete. There were zero encrypted members, unsupported compression methods,
wrong-date members or duplicate interval-144 candidates. Member compression is deflate. The exact local-header
offsets are 57,637,442 and 65,590,506. The inventory hashes are `89912ebb…` and `7c4813d…`.

Artifact SHA-256 values:

- download receipt: `291c63c78862925d3abd7ead396a201fd3a7bdd522ddf1bbb7816e7edb67cb61`
- retention receipt: `8a054aa6817f7de757504b5b8d398a6b5b687053bf32ad04dc61108ded1d830b`
- summary: `9fca06c5e627960499f0e045dbbf77de174ac8a99b3f5fe46d975dfdbb1e1bb8`

## Interpretation

The failed monthly-table prefix route is no longer the cheapest historical path. Official NEMDE daily ZIPs are
structurally date-partitioned and their individual dispatch cases are range-addressable. The pass authorizes a new
protocol that requests exactly one bounded range beginning at each frozen interval-144 local header, retains it,
then validates the local header, deflate stream, CRC and XML section/field contract.

This result does not validate XML semantics, replay, raw participant actions, adaptation, causality or a model.
The solver executable remains unavailable and raw redistribution remains locked pending AEMO clarification. No
GPU, remote worker, paid data or target event was used.
