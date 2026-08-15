# AEMO modern bundle-bridge stability panel

**State:** frozen, unexecuted and row-locked. At freeze time, none of the eight newly selected ZIPs had been
requested or opened and no selected market row had been read.

**Scientific role:** within-version, multi-day stability test of the E1b set-valued observation bridge. This is not
a cross-version test, causal study, dispatch replay, forecast or EcoMD result.

## 1. Why another gate is needed

E1b prospectively confirmed the one-or-exact-`{GEN, LOAD}` relation on one untouched July day. One fresh day is
enough to reject a purely development-day artifact, but not enough to claim temporal stability. This panel tests
the already frozen rule on four further ordinary days without changing its direction, identity or bid-type domain.

The relation may not be fitted again. E1a remains the immutable failure of the old unique-row representation;
E1b summary SHA-256 is `dc36b2fe31cc5c230def8f808a7efef1fa320f80ab30e61f1999d367dd9e466b`.

## 2. Mechanical selection

The metadata-only common directory window on 15 August 2026 was 16 June through 14 August. Control the weekday
by considering Tuesdays only. Exclude the previously accessed development and confirmation dates, 16 June and
7 July. Retain only months with a complete, previously retained monthly identity snapshot and at least two
untouched Tuesdays. Within each eligible month choose the earliest and latest remaining Tuesday.

This produces exactly:

- 23 and 30 June 2026;
- 14 and 28 July 2026.

The August identity archive directory returned HTTP 404 at freeze, so August is excluded. The protocol must not
reuse July identity data as if it were a complete August snapshot. No replacement date is allowed.

The two listing hashes are:

- `BIDMOVE_COMPLETE`: `37885534285a2039fc8bfea5f1b3592204358467c6d363557c713d8d5980c97f`;
- `NEXT_DAY_DISPATCH`: `a527bbbdebff3a54993b4aaed019cee96f9a9233019ba00bbb06302ff524ed4e`.

## 3. New source objects

| Market date | Bidmove bytes | Dispatch bytes |
|---|---:|---:|
| 2026-06-23 | 9,226,981 | 8,558,160 |
| 2026-06-30 | 9,180,603 | 8,538,407 |
| 2026-07-14 | 9,189,813 | 8,577,698 |
| 2026-07-28 | 9,135,889 | 8,186,385 |

The eight literal filenames, URLs and R2 keys are frozen in
`data/manifests/aemo_bundle_stability_panel_v1.yaml`. New acquisition totals exactly 70,593,936 compressed bytes.

The June and July `DUDETAILSUMMARY` objects are not requested from AEMO again. Their previously verified R2 bytes
are materialized using frozen hashes:

- June: 378,528 bytes,
  `f6af1ba508eb473bb95ee0dae0964b9e00d29aa6f8bf549a60f75d597f48c3ae`;
- July: 378,300 bytes,
  `c87e888dbae6e65fba3b07aba89c04c1f3e3a17f38e811cfe0b1ee6833139b1e`.

Total staged compressed input is 71,350,764 bytes.

## 4. Acquisition and retention order

1. Commit and push this protocol before requesting any newly selected URL.
2. From that clean commit, issue exactly one non-redirecting GET per new object, without retry, substitution or
   date replacement. Require HTTP 200, exact bytes and SHA-256 while treating the response as opaque.
3. Upload and verify every new object under its frozen R2 key. Refuse a mismatched pre-existing object.
4. Verify the two prior identity objects at their original R2 keys using exact size and SHA-256 metadata, then
   materialize them locally from R2. A new AEMO source GET for either identity is forbidden.
5. Only after all ten materializations pass may any ZIP be opened or CSV row parsed.
6. Analyze days sequentially. Preserve any failure; do not rerun, replace or relax a gate.

Raw archives and rows are excluded from Git. Only credential-free receipts and aggregate summaries are retained.

## 5. Per-day frozen decision

Each day independently reuses the 25 E1b gates. All exact source/R2/CRC/header/time/key and supporting-join checks
must pass. Every tracker must map to either:

- one row with direction `BIDIRECTIONAL`, `GEN` or `LOAD`; or
- exactly one `GEN` plus one `LOAD`, with no repeated direction, one effective `BIDIRECTIONAL` identity and bid
  type `ENERGY`, `LOWERREG` or `RAISEREG`.

Each day must contain at least one pair. Realized dispatch may never select a bid leg. All relation violation counts
must be zero.

Panel `PASS_MODERN_BUNDLE_STABILITY_PANEL` requires all four days to pass. There is no tolerated failed day,
pooled-rate exception or post-hoc exclusion. Counts and pair rates are descriptive; they are not required to be
equal across days.

## 6. Claim and resource boundary

A pass supports within-version temporal stability of the modern public observation bridge across six Tuesdays in
total when E1a/E1b dates are included. It does not support historical table-version portability, raw participant
action provenance, rejected actions, NEMDE replay, causality, prediction or model fidelity. A separate historical
version protocol remains necessary.

This is a free sequential CPU experiment. New download is 70.6 MB; staged compressed input is 71.4 MB. The maximum
admitted input is 4,000,000 rows and about 1.11 GB uncompressed per day, never loaded for all days simultaneously.
Expected local runtime is several minutes. Required paid data, remote workers and GPU-hours are zero; V100 and RTX
2060 resources remain idle.
