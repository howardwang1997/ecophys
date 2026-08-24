# OASIS random-priority network response — D−1 freeze

**Frozen:** 2026-08-24

**State:** candidate only; no effect estimation or simulator authorization

**Systems:** MISO and SPP, with BPA as a backup

## Question

Within a five-minute Simultaneous Submission Window, same-priority transmission-service requests can receive a
random customer order and then consume available transfer capability sequentially. D−1 asks only whether two
independent operators expose enough legally reusable and linkable information to identify and replay binding,
multi-constraint lottery events without examining their downstream effects.

The possible later scientific question is whether an exogenous local priority perturbation propagates through a
network of coupled flowgates and whether a frozen state-dependent response operator predicts held-out events across
operators. “Request order matters” and scalar first-come-first-served allocation are forbidden novelty claims.

## Admissible event

All conditions are required:

1. one documented five-minute simultaneous-submission window;
2. the same service/reservation priority and the same posted-tariff/no-discount price tier;
3. an auditable realized lottery position, not ordinary submission time or queue position;
4. at least three eligible requests;
5. at least two coupled limiting constraints or flowgates; and
6. an alternative admissible order can change a third party's allocation or another constraint's terminal state.

Events with differentiated bid prices, administrator discretion, missing requests or only one scalar capacity are
excluded.

## Required public field contract

For both MISO and SPP, one stable schema and key map must connect:

- window identifier and processing timestamp;
- transmission-service-request identifier;
- customer or auditable anonymized customer key;
- service type, reservation priority and price/discount tier;
- realized lottery position and the official randomization rule/version;
- requested and awarded MW, POR/POD and path;
- pre-window AFC/ATC or sufficient flowgate state for exact replay;
- limiting constraints and counteroffer logic; and
- accepted, counteroffered or refused status plus the linkable post-window capacity state.

Public-display regulation is not accepted as proof that current observer exports contain this complete join. Reuse
terms, retention period, timestamps, revisions and vendor versions must be recorded.

## Pass conditions

All gates are conjunctive:

1. **Rule gate:** official MISO and SPP documents unambiguously establish random order for the frozen equal-tier
   subset and identify every deterministic precedence rule applied before it.
2. **Realization gate:** public exports distinguish realized lottery position from request submission time and
   ordinary queue position.
3. **State gate:** the exact pre-window and post-window constrained state can be linked to every request without
   imputation from future information.
4. **Support gate:** each operator has at least 50 binding admissible lotteries and the combined sample has at least
   200; these are provisional hard floors and must be superseded by a blinded power calculation.
5. **Non-triviality gate:** each operator has enough three-request, two-constraint events for a powered third-party
   response estimand; two requests sharing one scalar capacity do not count.
6. **Replay gate:** an outcome-blind processor reproduces request status and capacity updates under a frozen
   zero-discrepancy rule or a pre-justified tolerance.
7. **Replication gate:** MISO and SPP both pass. Shared OATI/webTrans infrastructure, versions and common failure
   modes are explicitly audited; operator replication is not described as software independence.
8. **Novelty gate:** at least 20 primary works are mapped across OASIS transmission allocation, network connection
   queues, randomized priority, interference and state-dependent response. A direct prior for the same
   cross-flowgate randomized estimand closes the candidate.
9. **Method gate:** the proposed next-stage result must exceed sequential knapsack, standard randomization
   inference and a generic queue-order response curve.

## Outcome-blind resource boundary

D−1 may inspect official rules, schemas, reuse terms, source/version metadata and fields strictly required to test
event existence, joins, replay completeness and aggregate support. Any parser must emit only aggregate gate counts,
missingness and replay-discrepancy diagnostics. It may not emit operator-event, customer, path, award, price or
response estimates.

Paid acquisition, effect estimation, outcome plots, counterfactual policy claims, private-value inference,
simulator implementation, EcoMD, model API calls and GPU use are forbidden. If the public observer contract itself
cannot be established without purchasing data, D−1 stops and asks for a new authorization rather than buying it.

## Automatic stop

Stop on any missing realization, pre-state or post-state join; insufficient support in either operator; only
single-constraint allocation; no operator replication; an unresolved shared-vendor failure; or reduction of the
surviving claim to ordinary queue order, sequential capacity allocation or existing interconnection path-dependence
work.

Passing D−1 creates no active Nature route. It authorizes only a separately frozen T0 estimand, theorem and
prospective held-out prediction contract.
