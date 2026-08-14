# AEMO semantic-crosswalk held-out validation

**Status:** the crosswalk, exact validation months, exact URLs and stop rules are frozen before any validation HEAD
request, archive byte or data row is opened.

## Why this is a new protocol

The v1 header audit failed. Its two months, 2021-03 and 2025-01, are now schema-discovery data and cannot be reused
as evidence that a repaired mapping generalizes. This protocol preserves that failure and tests an explicit
field-level mapping on two previously unopened months.

The held-out month rule is mechanical: add six calendar months to each discovery month. Within each resulting
month, reserve the first Gregorian Tuesday for a possible later row test. This produces 2021-09-07 and 2025-07-01.
There is no holiday adjustment, availability replacement or outcome-based resampling.

## Claim and gate

This experiment can establish only that five logical AEMO roles have a stable, declared header-level semantic
projection across a legacy and current held-out month. It cannot establish row-level value equivalence, identity
continuity, mechanism replay, causal effects or policy prediction.

The header gate requires all ten exact archives to:

1. return HTTP 200 to an exact HEAD request and expose a positive content length;
2. match that length on download and pass SHA-256, single-CSV-member and ZIP CRC checks; and
3. match the declared internal package/table plus every source field used by the canonical crosswalk.

Any failed object fails the protocol. The object, month or field mapping cannot be replaced. Header version numbers
are recorded but are not treated as semantic proof; compatibility is determined by the frozen package, table and
source-field projection.

## Access and compute boundary

The unresolved manifest must be committed before HEAD metadata resolution. The resolved manifest must be committed
before archive downloads. Generated held-out headers and the failure/pass summary must be committed before any row
count, date filter, transform or join. Discovery archives cannot count as validation.

All work is CPU-only with CUDA hidden. Raw archives remain outside Git. GC0166 rows, controlled-rollout rows,
post-cutoff governance outcomes, Experiment 156 and all prospective-event responses remain sealed.
