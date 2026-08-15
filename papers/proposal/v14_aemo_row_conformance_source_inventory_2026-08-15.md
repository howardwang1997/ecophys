# V14 AEMO row-conformance source inventory — 15 August 2026

## Decision

A free, CPU-only modern row-conformance smoke can start after its protocol is committed and pushed. It needs three
official AEMO objects totalling 18,085,971 compressed bytes. It does not need a full monthly bundle, commercial
data, V100/RTX 2060 compute or a target-event row.

This closes source *design*, not row conformance. At the time of this inventory, none of the selected ZIPs or rows
had been accessed.

## 1. Existing-data inventory

The earlier ten-object AEMO development audit recorded 1,177,771,842 compressed bytes and 31,878,556,073
uncompressed bytes. Those full ZIPs were ignored, ephemeral experiment files. They are absent from the current
worktrees and no verified R2 object manifest exists for them. The retained summaries and hashes support the
published audit result, but cannot stand in for the missing input bytes in a new row analysis.

Accordingly:

- do not reconstruct or claim reuse of those archives;
- do not rerun their consumed held-out sample;
- retain the earlier failure and metadata results unchanged; and
- require raw-object R2 verification before any newly selected ZIP is opened.

## 2. Official source mapping

AEMO's public table/file map and trigger documentation give the small daily alternative:

| Report family | Required tables | Role in the smoke | Limitation |
|---|---|---|---|
| [`BID_MOVE_COMPLETE`](https://www.nemweb.com.au/Reports/CURRENT/Bidmove_Complete/) | `BIDDAYOFFER_D`, `BIDPEROFFER_D` | daily and period derived bid summaries | not raw submissions or rejected bids |
| [`NEXT_DAY_DISPATCH`](https://www.nemweb.com.au/Reports/CURRENT/Next_Day_Dispatch/) | `DISPATCHOFFERTRK`, `DISPATCHLOAD` | applied bid reference and physical dispatch | dispatch output, not an open NEMDE engine |
| [monthly individual-table archive](https://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM/2026/MMSDM_2026_06/MMSDM_Historical_Data_SQLLoader/DATA/) | `DUDETAILSUMMARY` | effective-dated DUID identity | identity support only |

The official [`DISPATCHOFFERTRK` schema](https://visualisations.aemo.com.au/aemo/nemweb/mmsdatamodelreport/electricity/mms%20data%20model%20report_files/MMS_129.htm)
defines the offer applied for each DUID, bid type and dispatch interval through `BIDSETTLEMENTDATE` and
`BIDOFFERDATE`. Its key omits direction. Therefore direction is a measured multiplicity limitation, not a field the
pipeline may impute. The [MMS data-model table/file map](https://markets-portal-help.docs.public.aemo.com.au/Content/EMMSenergyFCAS/DataModel.htm)
and [table triggers](https://tech-specs.docs.public.aemo.com.au/Content/TSP_TechnicalSpecificationPortal/EMMSDMTableTriggers.htm)
are the semantic authorities.

## 3. Frozen exact sample

Directory metadata were intersected without opening a ZIP. The earliest complete shared seven-day daily-report
window was 13--19 June 2026; its first Tuesday, 16 June, was selected mechanically. The three exact objects are
listed in `data/manifests/aemo_row_conformance_v1.yaml`:

- bid move complete: 9,095,887 bytes;
- next-day dispatch: 8,611,556 bytes; and
- June DUID identity snapshot: 378,528 bytes.

The experiment window is AEMO market time from `2026-06-16 04:05` through `2026-06-17 04:00`. It is a modern,
non-event development sample. It cannot establish historical schema equivalence or any intervention effect.

## 4. Data, compute and retention budget

- Network: exactly 18.1 MB if all three one-shot downloads return the frozen sizes.
- Local storage: at most about 1.11 GB uncompressed under hard caps; expected working use is much smaller.
- R2: three immutable raw objects plus SHA-256 metadata and small receipts.
- CPU: ZIP CRC, streaming CSV parsing, hashing and joins; expected minutes on the Mac.
- GPU: none. V100 and RTX 2060 machines remain unallocated.
- Paid data: none.

If the smoke passes, the next decision is whether the derived public reports support a multi-day replay-like
development panel. That requires a separate sampling/power protocol. A one-day parser pass is not permission to
train EcoMD or claim mechanism prediction.
