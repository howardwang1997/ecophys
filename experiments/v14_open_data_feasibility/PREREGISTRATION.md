# V14 open-data feasibility preregistration

**Status:** sampling rules frozen before any historical CoW competition or AEMO market row is opened.

**Scientific role:** development-only feasibility. Nothing in this experiment is prospective confirmation, an
Experiment 156 result, or evidence that the proposed market-world model predicts a real rule change.

## Purpose

This preflight asks three narrower questions:

1. Does the paired proper-score procedure control false positives and detect declared effects without time or
   identity leakage?
2. Can a frozen sample of public CoW solver competitions be retrieved, parsed and audited without replacing missing
   or failed observations?
3. Can two predeclared AEMO wholesale days spanning legacy and current archive naming be reduced to a typed,
   effective-dated action--identity--dispatch panel?

The binding machine-readable contract is
`data/manifests/open_data_development_sample_v1.yaml`. Its parent is commit
`997b750394fa173228acad9840f5c5348e014f98`.

## Outcome-blind execution order

1. Commit the unresolved contract and its validator before any historical source row is queried.
2. Run the generated-data calibration. Generated outcomes do not alter source sampling.
3. Query CoW's `latest` endpoint once, retain only `auctionId`, derive both ID lists from the frozen arithmetic
   rule, and commit the resolved manifest. No sampled competition may be queried before that commit.
4. Query exactly the 100 initial IDs. HTTP failures and unavailable IDs are observations and cannot be replaced.
5. Download only the five named AEMO table archives for the two frozen months. Audit ZIP integrity and headers,
   then commit a table-specific header/key contract before joining or replaying rows.
6. Scale to 1,000 CoW IDs, seven AEMO days, learned nuisance models or any GPU only after the corresponding initial
   gates pass.

## Frozen samples

The CoW initial sample contains 100 IDs at offsets `100000 + 1000*i`, `i=0,...,99`, below a single subsequently
resolved mainnet anchor. The 1,000-ID expansion uses offsets `100000 + 100*i`, making the initial sample an exact
subset. The selected auction must precede the prospective cutoff in block time; failure of that condition fails the
contract rather than triggering replacement.

The AEMO market dates are 2021-03-02 and 2025-01-07: the first Gregorian Tuesday of each declared month, with no
holiday adjustment or replacement. They were chosen from calendar and archive naming metadata, not from prices,
bids, dispatch or event outcomes.

## Stop conditions

- Stop on an invalid or dirty contract, an unresolved ownership hash, a selected post-cutoff auction, an unrecorded
  HTTP failure, target-event access, or any attempt to replace an inconvenient observation.
- A CoW HTTP-200 coverage below 80% is a retention failure, not permission to resample.
- An AEMO empty date, corrupt archive or unresolvable schema is reported as a failed feasibility gate.
- Production NEMDE is not open; any `nempy` comparison remains an approximate replay and is labelled accordingly.

Raw public files remain outside Git with URLs, retrieval clocks and SHA-256 hashes. Git stores contracts, request
ledgers' hashes, compact summaries, code and tests. GC0166 MDO/MDB rows and future governance-event responses remain
sealed throughout.
