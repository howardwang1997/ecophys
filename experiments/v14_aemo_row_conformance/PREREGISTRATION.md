# AEMO modern daily row-conformance smoke

**State:** frozen, unexecuted and row-locked. At freeze time, none of the three selected ZIPs was downloaded or
opened, no CSV row was read, and no result file existed.

**Scientific role:** development-only E1a data-plane smoke. It tests whether one modern public-report day can be
parsed and joined according to official table semantics. It is not mechanism replay, causal evidence, a model
result or evidence that historical report regimes are equivalent.

## 1. Why this experiment is admissible

The preceding exact-64-KiB protocol passed 10/10 source-header and transfer gates with zero complete objects and
zero data rows. It established delivery-channel/package/table/version metadata, but not timestamp parsing, primary
keys, effective-dated identities or applied-offer/dispatch joins. The large monthly `BIDPEROFFER` object is not an
acceptable conformance input. AEMO's current daily derived reports cover the required modern tables in about
18.1 MB compressed.

Previously downloaded full monthly development archives are no longer present locally and have no verified R2
receipt. Their earlier aggregate results remain valid, but those absent bytes are not treated as reusable data.
This protocol adds a hard retention-before-parse gate so the same provenance gap cannot recur.

## 2. Outcome-blind selection

Using directory metadata only, intersect complete daily `BIDMOVE_COMPLETE` and `NEXT_DAY_DISPATCH` dates. Take the
earliest seven-day shared window, 13--19 June 2026, then its first Tuesday: 16 June 2026. This is a non-event,
non-causal development date. Availability, file names and byte sizes were inspected; ZIP members and market rows
were not. No replacement is allowed after freeze.

The exact inputs are:

| Role | Frozen object | Bytes |
|---|---|---:|
| daily derived bid summaries | `PUBLIC_BIDMOVE_COMPLETE_20260616_0000000522858228.zip` | 9,095,887 |
| next-day applied-offer and dispatch outputs | `PUBLIC_NEXT_DAY_DISPATCH_20260616_0000000522854663.zip` | 8,611,556 |
| effective-dated DUID identity | `PUBLIC_ARCHIVE#DUDETAILSUMMARY#FILE01#202606010000.zip` | 378,528 |

Total compressed input is exactly 18,085,971 bytes. The literal URLs, object limits and R2 keys are frozen in
`data/manifests/aemo_row_conformance_v1.yaml`.

## 3. Immutable acquisition and retention order

1. Commit and push this protocol before executing any selected URL.
2. Run from that clean commit. Issue exactly one non-redirecting GET per object, with no retry or substitution.
3. Treat each response as opaque bytes. Require HTTP 200 and the exact frozen byte count; record SHA-256. Do not
   open the ZIP or CSV.
4. Upload those exact bytes to the frozen `r2://ecophys/raw/aemo/v14_row_conformance/market_date=2026-06-16/`
   keys. Refuse to overwrite an existing object unless its content length and SHA-256 metadata already match.
5. Verify every remote content length and SHA-256 metadata value and write a credential-free retention receipt.
6. Only after all three remote objects pass may the analysis process open a ZIP or parse a CSV row.

A download, retention or parse failure is preserved. It is not rerun, replaced or repaired under this protocol.
Raw ZIPs and rows are not committed to Git.

## 4. Frozen table and time contracts

The required logical tables are `BIDDAYOFFER_D` v3, `BIDPEROFFER_D` v4, `DISPATCH.OFFERTRK` v1,
`DISPATCH.UNIT_SOLUTION` v6 and `PARTICIPANT_REGISTRATION.DUDETAILSUMMARY` v7. Every required information header
must be present and every table nonempty.

AEMO timestamps retain published market-time semantics; no UTC conversion is invented. The market day covers
04:05 on 16 June through 04:00 on 17 June 2026, inclusive. All contracted timestamps must parse, bid settlement
dates must equal 16 June, and interval rows must fall inside the frozen market-day window. Every declared primary
key must be unique.

## 5. Frozen joins and decision thresholds

The analysis tests four bridges:

1. period bids to daily bids on settlement date, DUID, bid type and direction: match rate `1.000`;
2. `DISPATCHOFFERTRK` to the exact period offer on interval, DUID, bid type, bid settlement date and offer date:
   non-null reference rate at least `0.990` and match rate at least `0.995`;
3. applied offers to physical `RUNNO=1`, `INTERVENTION=0` dispatch on interval and DUID: match rate at least
   `0.995`; and
4. physical dispatch to `DUDETAILSUMMARY` on DUID and `START_DATE <= interval < END_DATE`: match rate at least
   `0.995`, with zero overlapping effective rows.

`DISPATCHOFFERTRK` has no direction field. The analysis retains every period-bid match and reports multiplicity;
the ambiguous rate must not exceed `0.050`. It must not silently choose a direction.

Overall pass requires every download, R2, CRC, header, nonempty-table, resource, timestamp, primary-key and join
gate to pass. At most 4,000,000 total MMSDM data rows and 1,107,296,256 uncompressed bytes are admitted.

## 6. Claim boundary and resources

A pass validates one modern public-report parser/time/key/join pipeline. It does not validate raw participant
submission history, rejected actions, historical pre/post-5MS equivalence, NEMDE optimization replay, causality,
policy fidelity or model prediction. `BIDMOVE_COMPLETE` contains public derived summaries, not an audit log of every
participant action.

This is a local CPU experiment: less than 20 MB download, no paid data, no GPU and no remote worker. V100 and RTX
2060 capacity stays idle. A later historical panel or model job remains behind a separate gate.
