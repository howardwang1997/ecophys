# CoW competition HEAD enumeration preregistration

**Frozen:** 2026-08-15 08:22 UTC

**Status:** `FROZEN_BEFORE_HEAD_ENUMERATION`

**Role:** development-only exact-mechanism data feasibility; no confirmation claim

## Question

Can persisted mainnet solver competitions be enumerated without reading scores, rankings, winners, transactions,
orders, prices or any response body?

The previous arithmetic sample returned 33 HTTP 200 and 67 HTTP 404 responses. That result must not be described
as 33% retention. CoW's audited code uses one PostgreSQL auction-ID sequence for regular auctions, skips empty
auctions after allocating an ID, and also allocates IDs to fast-path quote competitions. Therefore the integer
space is a shared candidate sequence, not a dense solver-competition table.

## Frozen method

Use the previously committed anchor `13,583,706`. Enumerate exactly 384 contiguous IDs
`anchor - 210000 - i`, for `i=0,...,383`, in descending order. The resulting range is
`13,373,706` through `13,373,323`, with SHA-256
`ea4ad29d44185999c18d89338147a9394324d664c7c3280637266798787bbf35`. It is strictly below and disjoint from
the old 1,000-ID expansion frame.

For each ID, issue `HEAD` to the official `/api/v2/solver_competition/{auction_id}` route at no more than one
request per second. Retain only the requested ID, status code, request order, attempt statuses, transport errors
and the assertion that zero body bytes were read. Discard all response headers, including `Content-Length`.

- HTTP 200: eligible persisted solver-competition record.
- HTTP 404: shared sequence slot without an exposed competition record; do not infer why.
- Any other final status or transport failure: enumeration failure; do not replace the ID.

The two method controls (`13481706 -> 200`, `13483706 -> 404`) were already consumed in the previous development
sample. No fresh candidate ID was accessed while testing HEAD behavior.

## Gates

The enumeration passes only if all 384 entries appear in exact order, every request outcome is retained, every
request is HEAD, no response field or header is retained, zero response-body bytes are read, every final status is
200 or 404, and at least 100 IDs return 200. The 100-row threshold is a feasibility/sample-size gate, not a
population-retention claim.

A pass permits materializing an exact eligible-ID list. That resolved manifest must be committed and pushed
before any new competition body is opened with GET. A failure forbids GET, resampling and replacement.

## Claim boundary and resources

This experiment establishes only an outcome-blind public enumeration path for a local contiguous development
frame. It does not establish representativeness over time, complete historical retention, exact score replay,
counterfactual validity or behavioral adaptation. It uses public metadata, CPU/network minutes, no paid data and
zero GPU-hours.
