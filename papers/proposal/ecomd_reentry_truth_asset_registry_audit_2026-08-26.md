# Registered market-experiment truth-asset audit

Date: 2026-08-26
Decision: **not a re-entry trigger; do not open Discovery Cycle 17**

## Question

Do current public trial and preregistration registries expose a prospective market experiment that
can adjudicate the closed EcoMD simulator-response routes? A qualifying source must freeze all of
the following before outcomes are opened:

1. a randomized or otherwise assigned market action;
2. a complete order-event lifecycle and replayable pre-state;
3. an outcome and interference map for the same estimand;
4. lawful raw-data and program reuse plus a dated future release;
5. a whole-source confirmation partition not touched during topic formation; and
6. an independently governed same-estimand replication.

This is an outcome-blind metadata and protocol audit. No trial result, raw outcome file, current OSF
project, simulator, market data, or participant record was opened.

## Bounded source screen

### AEA RCT Registry

The [official data documentation](https://docs.socialscienceregistry.org/data) states that the live
CSV contains all public trial metadata, refreshes approximately every ten minutes, and is archived
as monthly Dataverse snapshots. The frozen 2026-03 snapshot is [CC BY 4.0 and citable by
DOI](https://doi.org/10.7910/DVN/5XM7IG).

The live CSV retrieved on 2026-08-26 contained 12,635 registrations. Its SHA-256 was
`03a35c12b9f4a022bf1a19b7d8e783f530bb2c551dd3ca5b6c13ff0b662a62fd`. There were
8,887 records marked `in_development` or `on_going`. An outcome-free search across title,
abstract, intervention, design and design-detail fields for asset-market, financial-market,
stock-market, order-book, trading-platform, trading-rule, double-auction and limit-order terms
returned 76 broad hits. Five closest interacting-market protocols were read in full at the protocol
level:

| Registration | Useful capability | Decisive failure |
|---|---|---|
| AEARCTR-0013691, *The Value of Investor Data* | Individual randomization, 450 subjects, private information, limit/market orders and positions on an in-house trading platform | Scheduled to end in 2024; no public analysis plan, program, data URL, event schema, release commitment or independent replication |
| AEARCTR-0014188, *Teams in Asset Markets* | 28 continuous-double-auction markets, individual-versus-team intervention and full trading rounds | Analysis plan private; no public data/program contract; scheduled to end in 2025; treatment is behavioral rather than a field market-rule action |
| AEARCTR-0017219, *Price Informativeness* | Session assignment and 3,200 planned pairwise trading decisions | Pairwise threshold-price game, not an order book; no public data/program; scheduled to end before this audit |
| AEARCTR-0017639, *Networked Markets* | Exogenous information network and 16 market groups | Reuses one earlier laboratory design; no public event schema/data/program; scheduled to end before this audit |
| AEARCTR-0019139, *Social Comparison and Retail Trading* | Data collection remained scheduled through 2026-12-31 | Independent portfolio-allocation survey with no interacting market or event tape |

The registry therefore reveals potentially useful behavioral experiments, but none freezes the
truth contract needed for a market-dynamics or simulator-response claim. Registry status is also
not a reliable future-seal flag: several `in_development` or `on_going` records have end dates years
before this audit.

### OSF Registrations

The public OSF API was searched by the bounded title filters `asset market`, `market`, `trading`,
`asset`, `exchange`, `order book`, `double auction`, and `prediction market`. Only immutable
registration content was inspected; mutable source projects and outcomes were excluded.

| Registration | Useful capability | Decisive failure |
|---|---|---|
| [`xagjc`](https://osf.io/xagjc/), *Second-order beliefs and asset prices* | Registered before data existed; randomized laboratory market; planned beliefs, bids, asks, prices and quantities | At least five small sessions; collection began in March 2026; no full lifecycle schema, dated raw release, untouched partition, or second implementation |
| [`3by86`](https://osf.io/3by86/), *A protocol for achieving pricing efficiency* | Registered before data; twelve planned 24-person continuous-double-auction sessions; hashed z-Tree programs | Collection scheduled for June--November 2025; registered object has no raw data; no same-estimand independent replication or future release contract |
| [`8g3jw`](https://osf.io/8g3jw/), *Prediction Market Study -- new wave* | Immutable CC0 registration with a hashed replication protocol | Public record exposes neither an assigned market rule nor complete pre-state/order lifecycle; it is not a same-state field counterfactual |

The node licence on a registration is not itself a promise that future raw human-subject or market
data will be released under that licence. Likewise, the presence of bids and asks in a plan does not
establish immutable order IDs, replacement ancestry, partial fills, residual quantity, aggressor and
passive roles, or replay-complete state.

## Why this does not reopen the saturated family

One narrow claim is satisfied: immutable pre-data registrations of randomized interacting asset
markets exist. Four necessary claims fail:

- no reviewed registration freezes a complete event-lifecycle and pre-state schema;
- no reviewed registration commits to a lawful, dated raw release with an untouched confirmation
  source;
- no pair supplies independently governed, same-estimand action and observation semantics; and
- laboratory information/team/belief treatments do not create the real same-state exchange-rule
  counterfactual missing from Cycle 16.

These are hard contract failures, not a low probability score. The provisional 15% active-status
brake is not used in this decision.

## Decision and exact re-review condition

`registered_market_experiment_truth_asset_screen_20260826` is recorded as `not_trigger`, with
`candidate_harvest_authorized: false`. Discovery Cycle 17 remains unopened.

Re-review is allowed only after an immutable pre-data protocol commits to all of: a file-level raw
event schema, assignment key, replay-complete pre-state, lawful licence, dated release, whole-source
confirmation partition, and an independently governed replication using the same action, clock,
state, observation and outcome grammar. A new registration, another lab treatment, or a promise to
share data later is insufficient.

No outcome access, data acquisition, participant experiment, simulator run, implementation,
purchase, outreach, EcoMD change, sandbox, CPU experiment, or GPU use is authorized.
