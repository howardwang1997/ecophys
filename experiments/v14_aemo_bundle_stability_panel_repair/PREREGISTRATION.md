# AEMO stability-panel pre-parse repair

**State:** frozen and unexecuted. All ten ZIPs remain content-blind: panel v1 failed before the archive loop, with
zero ZIP opens and zero CSV rows observed.

**Scientific role:** plumbing repair only. This protocol cannot change the dates, objects, table contracts,
set-valued relation, thresholds, all-days decision or claim boundary frozen by panel v1.

## 1. Preserved failure

Panel v1 commit `1f44811e75a455f161532fbfdd3bde2092508bf5` completed eight exact source downloads and ten
R2 materializations. Its analyzer then raised `KeyError: 'resource_contract'` at
`parse_conformance_archives:693`, before entering the archive loop. The immutable decision is
`FAIL_PANEL_IMPLEMENTATION_PRE_PARSE`; failure artifact SHA-256 is
`0b1d4fa9229997f8be220eda0c9e4bb6319191c13981d658fb222493b8c756f1`.

The failure supplies no scientific result. Panel v1 is not edited or rerun.

## 2. Only permitted repair

The derived day manifest must expose the resource cap already frozen in v1:

```text
resource_contract.maximum_total_data_rows = 4,000,000
```

Permitted implementation work is exactly:

1. add that key/value to the derived day manifest;
2. add an integration preflight that invokes the parser entry point on synthetic inputs and proves the manifest
   passes the formerly failing lookup;
3. add an R2-only materializer and a repair analyzer.

No other parser, relation or scientific-gate change is allowed.

## 3. Zero-source-request provenance

No AEMO URL may be requested. The repair manifest freezes all ten R2 keys, byte counts and SHA-256 values from the
v1 receipt chain. It also freezes exact hashes for the original manifest, download receipt, retention receipt and
pre-parse failure artifact.

Execution order is:

1. commit and push this repair before content access;
2. verify the four original provenance artifacts exactly;
3. HEAD every frozen R2 object, require exact content length and SHA-256 metadata, then materialize it locally;
4. hash all local bytes and record `aemo_source_request_count=0`, `zip_opened=false`, `csv_rows_opened=false`;
5. only after 10/10 verification, run the four original days sequentially through the unchanged 25 gates;
6. preserve any implementation or scientific failure with no rerun.

The exact staged input remains 71,350,764 compressed bytes.

## 4. Unchanged scientific decision

The selected dates remain 23/30 June and 14/28 July 2026. Every day must independently pass all original E1b
schema, time, key, join and one-or-exact-`{GEN, LOAD}` gates. One failed date fails the panel; there is no pooled
exception. Realized dispatch cannot select an ex-ante leg.

Even a pass validates only within-version modern observation-bridge stability. It does not validate historical
version portability, raw/rejected actions, dispatch replay, causality, prediction or EcoMD.

## 5. Resources

This is sequential local CPU work with zero new source bytes, zero paid data, zero remote workers and zero GPU-hours.
V100 and RTX 2060 resources remain idle. The original per-day 4,000,000-row and 1.11 GB uncompressed caps remain
unchanged.
