# FCC historical-auction outcome-access incident

**Recorded:** 2026-09-05 NZST

**Affected route:** `fcc_clock1_random_rank_cascade`

**Disposition:** Auctions 102 and 105 are conservatively tainted for any claim of untouched
development or confirmation in this project. No effect was estimated, no report archive was saved,
and no simulator, SSH session, or GPU job was started.

## Incident

During a D−1 schema-header check, four FCC public-report HTML endpoints were requested:

- `https://auctiondata.fcc.gov/public/projects/auction102/reports/bids`
- `https://auctiondata.fcc.gov/public/projects/auction102/reports/results`
- `https://auctiondata.fcc.gov/public/projects/auction105/reports/bids`
- `https://auctiondata.fcc.gov/public/projects/auction105/reports/results`

The report pages embed default data rows rather than returning schema-only metadata. Tool output
visibly exposed actual Auction 102 bid rows and Auction 105 result rows; because all four requests
were issued, this record conservatively treats both auctions and both report families as accessed.
The exact access time was not separately captured; it occurred before 01:00 NZST on 2026-09-05.

This invalidates the sentence in the 2026-08-24 freeze that the official bid and result files had
remained unopened. That sentence was a contemporaneous boundary statement, not a permanent fact.

## Scope and non-scope

- The access revealed outcome-bearing rows. It was not limited to column names or schema text.
- No rank effect, propagation statistic, welfare quantity, treatment contrast, model score, or
  subgroup result was computed.
- No complete Auction 102 or 105 data archive was downloaded or intentionally persisted in the
  repository.
- This incident made no report-page request for Auctions 103 or 107. Their status is not inferred
  from this statement and remains subject to the project-wide provenance ledger.
- The pre-specified aggregate support and row-contract diagnostics for Auctions 108, 110, and 113
  are separate D−1 operations. They do not restore Auctions 102 or 105 as untouched sources.

## Containment

Outcome-page browsing stopped immediately. Subsequent source checks were restricted to FCC rules,
public-reporting schema PDFs, scholarly primary works, and the patent record. Auctions 102 and 105
must not be named as untouched confirmation, used to choose an estimand, or used to tune a simulator.
Any future lawful use must explicitly label them post-access exploratory sources and freeze a new
question using a genuinely untouched source before outcome access.

The FCC route is closed independently on scientific identification and novelty grounds. Therefore
no attempt is made to replace the contaminated auctions, and this incident authorizes no further
data access or experiment.
