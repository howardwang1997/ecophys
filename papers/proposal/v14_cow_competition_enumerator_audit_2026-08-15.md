# CoW solver-competition enumerator audit — 15 August 2026

## Decision

The public Order Book API has lookup routes by auction ID and transaction hash plus a latest-record route, but no
route that lists all historical solver competitions. Arithmetic auction-ID sampling is nevertheless repairable
without looking at competition outcomes: the deployed service accepts HEAD on the lookup route and returns the
same 200/404 existence classification while transferring no JSON body.

The next admissible route is therefore a two-commit protocol:

1. freeze a contiguous candidate-ID frame and enumerate it with status-only HEAD;
2. commit the exact HTTP-200 ID list before issuing any GET for those bodies.

## Official-code finding

The official service code shows why the earlier 33/100 result is not a retention estimate. Both the autopilot
auction cutter and the quote service call the same PostgreSQL `nextval` function. Fast-path quote calculation
allocates a new auction ID, and the autopilot also allocates an ID before skipping an empty auction. Only auctions
with valid competition data enter `competition_auctions`, which backs the public solver-competition lookup.
Consequently, 404s can be structural holes in a shared sequence; they are not evidence that a competition record
was deleted.

Audited source state:

- deployed API version: `v2.374.3@b2de49bf955eca9976b5b9465d8be173b545db6f`;
- deployed tag commit: `b2de49bf955eca9976b5b9465d8be173b545db6f`;
- audited main commit: `20b3a62f222ad278502fb7e85cae4938e7f26f65`;
- deployed and main OpenAPI SHA-256: `264d4d906c64329664e90b093b1e597ca1dbdeb76b1564c624f53b36538e3e3b`.

HEAD is allowed by the deployed CORS response but is not declared as a separate OpenAPI operation. It was tested
only on one previously consumed 200 ID and one previously consumed 404 ID. All headers, especially body length,
are forbidden in the new enumeration ledger.

## Frozen feasibility frame

The new frame contains 384 contiguous IDs from `13,373,706` down to `13,373,323`, derived from the previously
committed anchor. It does not overlap the prior initial or expansion sample. The prior 33% hit rate is used only
to choose 384 candidates so that 100 eligible rows are likely; it is not used to select IDs or assert prevalence.

The pass gate requires an exact status-only ledger, no body/header retention, only terminal 200/404 statuses and
at least 100 eligible IDs. Any failure blocks payload access. Even a pass validates enumeration only; temporal
representativeness and mechanism replay require separate protocols.

## Sources

- CoW Protocol Order Book OpenAPI: https://raw.githubusercontent.com/cowprotocol/services/v2.374.3/crates/orderbook/openapi.yml
- CoW Protocol services: https://github.com/cowprotocol/services/tree/v2.374.3
- Solver-competition route: https://github.com/cowprotocol/services/blob/v2.374.3/crates/orderbook/src/api/get_solver_competition_v2.rs
- Shared auction sequence: https://github.com/cowprotocol/services/blob/v2.374.3/crates/database/src/auction.rs
- Fast-path quote ID allocation: https://github.com/cowprotocol/services/blob/v2.374.3/crates/shared/src/order_quoting.rs
- Autopilot empty-auction skip: https://github.com/cowprotocol/services/blob/v2.374.3/crates/autopilot/src/run_loop.rs

## Executed disposition

The committed HEAD frame returned 93 HTTP 200 and 291 HTTP 404 statuses. Every integrity condition passed: exact
order, one attempt per ID, no transport error, zero body bytes and no retained response field beyond status. The
predeclared minimum was 100 eligible records, so the decision is `FAIL_MINIMUM_ELIGIBLE_COUNT_NO_GET`.

No resolved GET manifest was generated. The 93 IDs cannot be promoted, topped up or combined with a post-hoc
extension. HEAD remains a valid technical enumerator, but this particular scientific frame failed its sample-size
contract. Result: `experiments/v14_cow_competition_head_enumeration/RESULTS.md`.
