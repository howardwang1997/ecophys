# AEMO fresh-day set-valued offer-bridge confirmation (E1b)

**State:** frozen, unexecuted and row-locked. At freeze time, no selected ZIP had been downloaded or opened, no
CSV row had been read, and no result artifact existed.

**Scientific role:** cross-month confirmation of a relation rule learned post hoc on the 16 June 2026 development
day. This is observation-bridge validation only. It is not a causal result, market-mechanism replay, policy model,
forecast or EcoMD result.

## 1. Development result and prospective correction

The immutable E1a row-conformance smoke failed one of nineteen gates: 43,200 of 592,560 tracker records had two
direction candidates (`7.2904%`, above the frozen `5%` maximum). That result remains `FAIL`; its threshold is not
changed. A post-hoc diagnostic then found that every ambiguous record was exactly one unique `{GEN, LOAD}` pair,
belonged to one effective `BIDIRECTIONAL` DUID identity, and had bid type `ENERGY`, `LOWERREG` or `RAISEREG`.

This protocol prospectively tests the corrected representation: an applied-offer tracker maps to either one
direction-specific period row or the complete two-leg `{GEN, LOAD}` bundle. Realized `DISPATCHLOAD` values may be
used only to confirm dispatch-row existence and effective identity; their sign may never choose an ex-ante leg.

Development evidence is locked by these artifact hashes:

- E1a summary: `fc422654de5c64a91e71b8dcceb22612f406092cdf6a36900859072041a6668b`;
- post-hoc diagnostic: `d8b4bb0ffe6ede3fadf00cdac68c6851568fab132b6e2c94162c8bb4317cfaa2`.

## 2. Fresh outcome-blind selection

Without opening a ZIP or reading a market row, select the first Tuesday of the first complete calendar month after
the June development month. This mechanically selects 7 July 2026 and a fresh July identity snapshot. It is a
non-event, non-causal confirmation date. No replacement is allowed.

The exact directory pages used for selection were retained only as metadata hashes:

- `BIDMOVE_COMPLETE` listing:
  `37885534285a2039fc8bfea5f1b3592204358467c6d363557c713d8d5980c97f`;
- `NEXT_DAY_DISPATCH` listing:
  `a527bbbdebff3a54993b4aaed019cee96f9a9233019ba00bbb06302ff524ed4e`;
- July `DUDETAILSUMMARY` listing:
  `79beb058dde1c30616036b21fcd5efa875e93f2f961a0d7f7496b2ae063b5721`.

| Role | Frozen object | Bytes |
|---|---|---:|
| daily derived bid summaries | `PUBLIC_BIDMOVE_COMPLETE_20260707_0000000526370718.zip` | 9,224,570 |
| applied-offer and dispatch outputs | `PUBLIC_NEXT_DAY_DISPATCH_20260707_0000000526367103.zip` | 8,641,259 |
| effective-dated DUID identity | `PUBLIC_ARCHIVE#DUDETAILSUMMARY#FILE01#202607010000.zip` | 378,300 |

Total compressed input is exactly 18,244,129 bytes. Literal URLs, table versions, limits and R2 keys are frozen in
`data/manifests/aemo_bundle_confirmation_v1.yaml`.

## 3. Immutable acquisition and retention order

1. Commit and push this protocol before requesting any selected object.
2. Execute from that clean commit. Issue exactly one non-redirecting GET per frozen object, without retry,
   substitution or date replacement.
3. Treat each response as opaque bytes. Require HTTP 200 and the exact byte count, then record SHA-256. Do not open
   a ZIP or CSV.
4. Upload the exact bytes to
   `r2://ecophys/raw/aemo/v14_bundle_confirmation/market_date=2026-07-07/`. Refuse to overwrite a remote mismatch.
5. Verify remote content length and SHA-256 metadata for all three objects and write a credential-free receipt.
6. Only after all R2 gates pass may the analysis process open ZIPs and parse CSV rows.

Any acquisition, retention or parsing failure is preserved. This protocol is not rerun or repaired. Raw archives
and rows are excluded from Git.

## 4. Frozen schemas, time and base joins

Required tables are `BIDDAYOFFER_D` v3, `BIDPEROFFER_D` v4, `DISPATCH.OFFERTRK` v1,
`DISPATCH.UNIT_SOLUTION` v6 and `PARTICIPANT_REGISTRATION.DUDETAILSUMMARY` v7. Every required header must be
present, every table nonempty, every contracted timestamp parse, and every declared primary key be unique.

AEMO timestamps retain published market-time semantics. Bid settlement dates must equal 7 July 2026. Intervals
must lie in the inclusive market-day window from 04:05 on 7 July through 04:00 on 8 July. Required supporting
joins are 100%: period-to-day bid parentage, tracker-to-physical dispatch, and physical dispatch to exactly one
effective identity row. Identity intervals must not overlap.

## 5. Frozen set-valued relation and decision

Each valid tracker key is matched to period bids by interval, DUID, bid type, bid settlement date and offer date.
All tracker references and relations must have 100% coverage. Candidate cardinality must be one or two:

- a singleton direction must be one of `BIDIRECTIONAL`, `GEN` or `LOAD`;
- a pair must contain exactly one `GEN` and one `LOAD`, with no duplicate direction;
- every pair must have exactly one effective `BIDIRECTIONAL` identity;
- pair bid type must be `ENERGY`, `LOWERREG` or `RAISEREG`;
- at least one pair must occur, so the central correction is actually tested.

Overall `PASS_FRESH_SET_VALUED_OFFER_BRIDGE_CONFIRMATION` requires all 25 download, R2, archive, schema, resource,
time, key, base-join and relation gates to pass. Otherwise the decision is `FAIL`. No threshold, type domain or
sample may be changed after content access.

## 6. Claim and resource boundary

A pass confirms this modern set-valued applied-offer relation on one fresh cross-month day. It does not establish
raw participant submissions or rejected actions, historical table-version equivalence, NEMDE optimization replay,
causal adaptation, model prediction or policy fidelity. It would unlock only a separately frozen limited
multi-day development-panel design.

This is a free CPU experiment: 18.24 MB compressed, at most about 1.11 GB uncompressed and at most 4,000,000 MMSDM
data rows. Required GPU-hours are zero. Both V100 workers and the RTX 2060 remain idle; no paid data, storage
purchase or remote worker is required.
