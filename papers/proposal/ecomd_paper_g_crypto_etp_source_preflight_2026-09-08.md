---
document: Paper G crypto-ETP delivery-route source preflight
date: 2026-09-08
visibility: private/internal research selection and infrastructure record
record_type: bounded_followup_to_cycle19_not_a_new_search_cycle
preflight_decision: failed_current_public_source_contract
parent_program: paper_g_crypto_etp_delivery_execution_transfer
outcome_accessed: false
candidate_harvest_authorized: false
simulator_runs: 0
gpu_hours: 0
forecast_status: no F3 subject or forecast
---

# Crypto-ETP delivery: public-source feasibility resolved

## Decision

The cycle19 question was whether in-kind redemption reduces outside execution and financing
pressure or transfers that activity from the fund to authorized participants (APs). **Stop the
current public-source mechanism-identification formulation.** The reviewed basket, filing,
public-trade and custody-observation interfaces do not identify the joined transaction,
participant and financing history needed to distinguish those explanations.

This is stronger than merely failing to find a convenient download: an explicit example below
has the same public observations but different AP execution. It is also narrower than a claim
that all public-data ETF research is impossible. A descriptive policy-date study, a price-only
policy effect, or a study with lawfully released participant records would have different
contracts. None is substituted for the question that was retained in cycle19.

This follow-up is a paper-only infrastructure preflight. It resolves an already-recorded
formulation; the preflight itself is not a new research topic or machine card. Eight primary
documents were inspected, with no target data API requests, account access, blockchain queries,
holdings download, data purchase, outreach or experimental execution. Source scouting began
after the 09:32:07 UTC clock checkpoint. This record is exploratory, not a prospective freeze.
No F3 review or probability is backfilled.

## Native estimand and the missing contract

Let j be a redemption opportunity whose requested quantity q, eligibility and participant set
are recorded **before** delivery-mode assignment. D chooses between two fully specified legal
cash and in-kind procedures. The contrast concerns the same pre-assignment demand, with the
fund, eligible APs and relevant executing intermediaries included in a predeclared participant
boundary. Responses would be:

- signed net execution crossing that participant boundary over a specified horizon; and
- actual outside financing usage and financing costs over that horizon.

The bounded preflight family uses one-hour and 24-hour wall-clock windows after assignment,
plus the complete settlement lifecycle for reconciliation. These are candidate measurement
windows, not experimental endpoints or a sample-size authorization. Delayed/rejected orders
remain in the lifecycle. Conditioning on realized redemption volume after the policy choice
would change the estimand and could select on a treatment consequence.

Importantly, individual bitcoin units need not be labelled as having "caused" a particular
trade. The required observation is participant-labelled execution under a defensible assignment
and interference design. Asset fungibility does not excuse missing participant identity, and
possession of labelled transactions would not by itself establish causal assignment.

## What the primary source contracts actually supply

| Source | Available documentation or fields | Missing connection for this estimand |
|---|---|---|
| DTCC ETF Portfolio Data Service [P1] | Basket constituents, quantities and create/redeem eligibility; daily and supplemental portfolio files | A portfolio description is not an actual redemption instruction. Commodity-backed product coverage is qualified by the issuer; cash representation can stand in for components not exchanged in kind. No AP execution or financing ledger is promised. |
| NSCC ETF Processing [P2] | Describes a separate Instruction File and Instruction Detail File containing actual creation/redemption details, delivered within member services | This is a distinct service and entitlement from the portfolio data product. An AP/member agreement and relevant access are needed; no public joined export is established. Crypto underlying-leg coverage cannot be inferred from generic ETF processing. |
| SEC Form N-CEN [P3] | E.2 contains AP identity and reporting-period purchase/redemption amounts; E.3 contains fund-level cash/in-kind summary statistics | It is an annual registered-investment-company form, not a transaction-time delivery/hedge ledger. Even where applicable, these fields do not join each delivery to an AP execution history. |
| iShares digital-assets disclosure [P4] | States that the relevant iShares Trusts are not investment companies registered under the 1940 Act | N-CEN coverage from registered bond funds cannot be transplanted to IBIT by calling both products ETFs. This is a scope finding, not a statement that IBIT has no public reporting. |
| Coinbase Prime List Portfolio Fills [P5] | Portfolio/order identifiers, product, side, quantity, price, time, venue and fee fields in the documented response | This is a portfolio-specific account interface. It does not grant access to the fund or AP accounts, include every external venue, or automatically join fills to redemption instructions and financing. |
| Coinbase Prime request authentication [P6] | Requests use access key, passphrase, signature and timestamp, with portfolio/entity identifiers | Public documentation does not make third-party account records public. No credentials were sought or used. |
| Coinbase Prime Instant Transfers [P7] | Documents internal-ledger transfers using counterparty identifiers without onchain settlement for supported same-type portfolios | Public chain observation need not reveal these ownership movements. The documentation explicitly excludes Vault transfers and cross-type Trading/Custody transfers; no assertion is made that a specific IBIT redemption used this feature. |
| Coinbase Exchange public trades [P8] | Time, trade ID, price, size and maker-order side | The documented response has no AP/customer identity. Its `side` is the maker side, not a label identifying fund or AP selling. It cannot be joined to a Prime portfolio without additional authenticated crosswalks. |

The positive capability is concrete: relevant fields exist in private processing and account
systems. That does **not** remove the current public-source blocker. Conversely, public
eligibility and basket data remain useful reference data. Their usefulness is not evidence that
they expose the required transaction lifecycle.

## Analytic stop: the same public record permits different AP execution

Consider a deliberately simplified accounting system with an AP A, an unrelated dealer C outside
the declared participant boundary, and buyer B.
Before redemption, A holds no underlying, C holds q units, and B holds sufficient cash. The
fund transfers q units to A in a declared in-kind redemption, identically in both histories.
The public fund balances and share cancellation are consequently identical.

Next the public tape records one sale of q units to B at the same price, time and maker-side
classification in both histories:

| Hidden history | Seller behind the same anonymous print | Final A holdings | Final C holdings | A's outside sale |
|---|---|---:|---:|---:|
| H_A | A sells the newly received inventory | 0 | q | q |
| H_C | C sells its pre-existing inventory; A retains the redemption delivery | q | 0 | 0 |

B receives q in both histories. Both conserve assets and cash. If ownership is recorded within
the same custodial ledger, aggregate custody balances can also agree. The fund's delivery may
have an identical publicly visible transfer in both histories; that does not identify the
subsequent anonymous seller. Internal ledger movements are a documented capability [P7], while
the public trade schema omits account identity [P8]. This example is compatible with those
observation limits; it is not a reconstruction of a particular issuer's settlement practice.

Write Z for the full history and O(Z) for the reviewed public view. The example gives
O(H_A)=O(H_C), but Y_A(H_A)=q and Y_A(H_C)=0. Therefore no function of this public view alone
recovers even that AP's realized net sale for both histories. Repeating anonymous prints,
acquiring a longer daily-flow series, or fitting a more elaborate simulator does not supply
the missing ownership label. A probabilistic model could fill it in only by adding assumptions
whose validity would need independent evidence.

This is elementary observation-loss reasoning, already belonging to the repository's closed
observation-quotient parent. It is retained as a source-contract counterexample, **not proposed
as a novel impossibility theorem**. It does not prove nonidentification under every imaginable
public source or under additional externally justified restrictions.

There is a second, separate obstacle: even if every realized fill became observable, optional
delivery choice may depend on inventory, financing and expected trading costs. Observability of
Y does not identify E[Y(kind)-Y(cash)]. The source audit establishes no assigned mode, valid
instrument, complete pre-state or independently replicated policy environment. The prior
cycle19 directed-cash/in-kind flow-equivalence check also remains valid.

## Minimum reusable truth asset, if one becomes available

This table specifies capability requirements; it is not permission to build or acquire them.

| Requirement | Required content | Current verdict |
|---|---|---|
| Supported estimand family | Same-request route-assignment effects on participant-boundary flow and actual financing, with fixed windows and full lifecycle reconciliation | Defined on paper; no eligible empirical unit is established. |
| Assignment and interference | Pre-choice requests/eligibility, assigned and realized mode, known selection law or justified instrument; shared APs, executing desks, custodians and asset exposures mapped across concurrent requests | Missing. Multiple funds sharing APs are not independent treatment replications. |
| Complete event lifecycle | Immutable issuer, request, AP and order IDs; received/accepted/rejected/cancelled/amended/partially settled/settled states; timestamps, intended and actual cash/asset legs, costs and late events | Basket descriptions and public prints do not supply this. Private schemas are partial leads. |
| Initial and replay state | Pre-inventory, cash, financing usage/terms, hedge positions and unfilled orders; role/beneficial-owner mapping and cross-venue coverage; exact event ordering, deduplication and custody/cash reconciliation | Missing. No replay implementation is authorized. |
| Rights, ethics and release | Written authority for commercial account records and each join; derived-data release conditions; privacy protection for identifiable account users; no assumption that a public endpoint or blockchain label grants reuse rights | No such grant or released asset established. No outreach occurred. |
| Immutable artifact identity | Dataset/schema version, extraction/preprocessing hashes, source snapshots, code/config/container digests and a dated release | No dataset or build exists. Invented hashes would provide no evidence. |
| Untouched confirmation | Separate issuer/participant-period source held out before any outcomes and a prospective freeze; the already exposed IBIT 2025 annual-aggregate source is excluded | No qualifying partition named. A calendar date alone does not guarantee clean data. |
| Independent replication | Independently governed issuer/participant source, genuinely distinct assignment episodes and matching state/action/outcome definitions | Not supplied by two funds or two software runs sharing the same AP/provider process. |
| Cost, precision and stops | Rights/acquisition quote, legal independent-unit count, effect/variance assumptions and a power calculation conditional on a valid assignment design | Cannot estimate a credible run budget or sample size before these gates. Stop before purchase or outcomes. |

An asset must satisfy the conjunction, not merely expose one currently hidden field. A fill
schema, a paid PCF subscription or an individually accessible brokerage account would not alone
qualify. No F3 subject is proposed, so there is no full-T0 forecast or probability threshold to
apply. The zero-purchase, zero-GPU source review is complete; no empirical compute estimate is
presented as if additional GPU hours could repair identification.

## Disposition and re-entry boundary

- Resolve the existing program `paper_g_crypto_etp_delivery_execution_transfer` as
  `failed_closed` **under the reviewed public-source mechanism-identification formulation**.
- Record a `not_trigger` capability audit with no removed blockers and
  `candidate_harvest_authorized: false`. This is not cycle20; cycle19's original six-question,
  one-deferred counts remain historical, with a follow-up pointer added.
- Re-entry requires a real, lawfully reusable joined transaction/account asset and credible
  assignment/replication, or a distinct externally justified identification result. A newer
  provider page, annual mode statistic, wallet heuristic or additional simulator seeds is
  insufficient.
- Do not reopen generic observation-loss theory or silently replace the original mechanism with
  a price-only before/after event study. The separate cycle18 margin lead and Paper D's separately
  authorized revision work are unaffected.

## Primary-source manifest

All eight documents below were inspected on September 8, 2026. Only documentation, blank forms
and issuer legal-scope text were used. Example JSON values are documentation fixtures, not
queried market observations. Prior cycle19 sources are reused by reference rather than counted
as newly read papers.

1. **P1 — [DTCC ETF Portfolio Data Service](https://www.dtcc.com/data-services/corporate-actions-and-reference-data/etf-portfolio-data).** Product scope, offering and commodity-coverage qualifications; neither actual files nor samples obtained.
2. **P2 — [DTCC/NSCC ETF Processing](https://www.dtcc.com/clearing-and-settlement-services/equities-trade-capture/etf).** Member access and the separate actual creation/redemption instruction lifecycle; crypto asset-specific completeness remains unverified.
3. **P3 — [SEC Form N-CEN](https://www.sec.gov/files/formn-cen.pdf).** Blank form, General Instruction A and Items E.2–E.3; no fund filing outcomes opened.
4. **P4 — [iShares digital-assets disclosure](https://www.ishares.com/us/products/digital-assets).** Targeted 1940 Act scope language for the Trusts; the product-family page is not an empirical dataset or a stable historical protocol version.
5. **P5 — [Coinbase Prime List Portfolio Fills](https://docs.cdp.coinbase.com/api-reference/prime-api/rest-api/orders/list-portfolio-fills).** Response schema and portfolio-scoped request; no API call executed.
6. **P6 — [Coinbase Prime REST API Requests](https://docs.cdp.coinbase.com/prime/rest-api/requests).** Authentication headers and entity/portfolio scope; no credentials accessed.
7. **P7 — [Coinbase Prime Instant Transfers](https://help.coinbase.com/en/prime/trading-and-funding/transfer-funds-between-prime-accounts-through-instant-transfers).** Internal-ledger capability and portfolio/Vault exceptions; not evidence of use in a specified historical ETP transaction.
8. **P8 — [Coinbase Exchange Get product trades](https://docs.cdp.coinbase.com/api-reference/exchange-api/rest-api/products/get-product-trades).** Public response fields and maker-side meaning; no live or historical trades requested.

The source-contract matrix and analytic twin are reusable infrastructure. They do not establish
novelty, a real-market effect, a new active thesis or permission for experimental execution.
