# OASIS simultaneous-window random-priority network response — D−1 result

**Date:** 2026-08-24

**Frozen protocol:** `papers/proposal/oasis_ssw_random_priority_network_response_dminus1_freeze_2026-08-24.md`

**Verdict:** **FAIL/RED at the public-realization contract; close before records, support counting or replay**

**Resource boundary:** official rules, schemas, access terms and primary literature only; zero TSR outcome records,
paid data, parsers, simulators, EcoMD runs, model calls or GPU use

## Formal decision

The underlying mechanism is real. MISO and SPP both place otherwise tied customers in a random order and then
expand that customer order into round-robin transmission-service-request positions that are evaluated sequentially
against available flowgate capacity. BPA provides a closely related backup rule.

The frozen D−1 nevertheless fails at its first empirical identification gate. The public standard OASIS machine
contract documents request identifiers, customer and service fields, requested and granted capacity, POR/POD,
status and second-resolution queue/update times, but it does not document a stable export field for the realized
customer lottery or the resulting TSR evaluation position. Some implementation and training material displays a
`Lottery Order` concept in an authenticated interface; that is not a documented NAESB template, historical export
or research-reuse contract. OATI expressly prohibits automated navigation or scraping of its user interface.

The state gate fails independently. Current AFC, flowgate summaries and request-evaluation reports exist, but no
public schema inspected here atomically joins each lottery window and request to the complete immediately preceding
and succeeding AFC/ASTFC vector, limiting-flowgate impacts, topology/outage inputs and calculation version. A
request's final status and granted MW do not constitute the network post-state.

These are conjunctive gates. Their failure stops the audit before querying any transaction record, counting
support, inspecting outcomes or implementing replay. A regulation requiring OASIS audit records does not establish
that an internal lottery variable or per-evaluation network snapshot is part of the exported audit record.

## Frozen gate matrix

| Gate | MISO | SPP | BPA backup | Decision |
|---|---|---|---|---|
| Random-order rule and deterministic precedence | **PASS:** five-minute window; priority, duration and pre-confirmation precede random position | **PASS:** random customer order followed by round-robin TSR positions | **PASS:** duration, pre-confirmation and bid price precede a customer lottery | Rule gate passes |
| Realized lottery/evaluation position | **FAIL:** no documented standard export distinguishes it from ordinary `TIME_QUEUED` | **FAIL:** no documented `Lottery Order`, customer-pick or round field in a public machine export | **FAIL:** the rule exposes the concept, not a stable public export | **Automatic stop at R2** |
| Exact event-linked pre-state | **FAIL:** horizon/current AFC reports are not immutable, AREF-linked pre-evaluation snapshots | **FAIL:** Request Evaluation reports do not establish a complete visitor-accessible historical snapshot contract | **FAIL:** initialization and pending-ATC reports do not establish the required event join | **S0 fails independently** |
| Exact event-linked post-state | **FAIL:** request status/granted MW is not the post-AFC vector | **FAIL:** no atomic AREF-to-next-state contract | **FAIL:** no atomic AREF-to-next-state contract | **S0 fails independently** |
| Programmatic access and research reuse | **FAIL for a ready pipeline:** credentials/certificate and supported templates are required; no bulk research licence was found | **FAIL for a ready pipeline:** query-only visitor access still requires a certificate; no open reuse licence was found | **FAIL for a ready pipeline:** authenticated OATI access and customer requirements apply | **A0 fails** |
| Binding support | Not queried | Not queried | Not queried | Not authorized after R2/S0 |
| Multi-request, multi-constraint non-triviality | Not queried | Not queried | Not queried | Not authorized after R2/S0 |
| Outcome-blind replay | Not implemented | Not implemented | Not implemented | Not authorized after R2/S0 |
| Independent replication | Different operator/network, but the same OATI webTrans product family and essentially the same allocation workflow | Same | Same family | Cross-network replication only; not software- or mechanism-independent |

Qualified primary operators: **0/2 required**. The backup does not repair the same realization and state failures.

## What the public field contract does and does not establish

The NAESB/OASIS data dictionary exposes fields such as `ASSIGNMENT_REF`, customer code, service class and
increment, NERC curtailment priority, bid and pre-confirmation fields, `CAPACITY_REQUESTED`, `CAPACITY_GRANTED`,
POR/POD/path, `STATUS`, `TIME_QUEUED`, `TIME_STAMP` and `TIME_OF_LAST_UPDATE`. The documented time fields resolve to
seconds. The inspected standard dictionary does not define `SSW_ID`, `LOTTERY_ORDER`, `LOTTERY_POSITION`,
`CUSTOMER_ORDER`, `LOTTERY_ROUND` or an equivalent random-evaluation field.

This absence is stated narrowly: the **current public machine contract inspected here does not establish the
field**. It is not a claim that no internal OATI database or authenticated human page contains it. The distinction
is decisive because the frozen protocol requires a reproducible export, history and key map. Neither a common
window-close queue time nor a later status timestamp is contractually the lottery order, and second-resolution
timestamps cannot safely break ties.

The regulatory requirements are also narrower than the proposed dataset:

- [18 CFR §37.6](https://www.ecfr.gov/current/title-18/chapter-I/subchapter-B/part-37/section-37.6) requires
  request time, queue place, status/result and transmission-capability disclosures, but does not identify a
  customer-lottery permutation or require a per-request full flowgate snapshot.
- [18 CFR §37.7](https://www.ecfr.gov/current/title-18/chapter-I/subchapter-B/part-37/section-37.7) requires
  time-stamped audit data, limited online history and longer retention on request. Retention cannot create an
  undocumented field or an atomic pre/post calculation record.
- The [standard OASIS data dictionary](https://pjmoasis.pjm.com/OASIS/PJM/datadic.htm) documents ordinary queue,
  status and capacity fields but no lottery rank.
- The [OATI access policy](https://www.oasis.oati.com/OATI_OASIS_Access_Policy.pdf) requires supported NAESB
  templates and credentials for programmatic access, prohibits automated UI scraping, rate-limits queries and
  requires advance notice for significant automation.

## Operator evidence

### MISO

The [MISO Tariff Module B](https://docs.misoenergy.org/miso12-legalcontent/Module_B_-_Transmission_Service.pdf)
establishes the five-minute simultaneous window, deterministic precedence and random queue position. The
[MISO ATC Implementation Document](https://www.oasis.oati.com/woa/docs/MISO/MISOdocs/TP-OP-005_Available_Transfer_Capability_Implementation_Document_v30.pdf)
explains that a TSR submission or status change can update AFC used for a later request. This makes the missing
event-linked snapshots material: a current or horizon report is not necessarily the state used immediately before
one lottery evaluation. The [MISO TSR FAQ](https://help.misoenergy.org/knowledgebase/article/KA-01425/en-us)
documents FG/Path Summary and AFC/ASTFC horizon reports, but not the frozen AREF-to-pre/post-state join.

MISO therefore receives `R1=PASS`, `R2=FAIL`, `S0=FAIL` and `A0=FAIL for a ready, reusable bulk pipeline`.

### SPP

[SPP Business Practice 2450](https://www.spp.org/documents/37896/spp%20oatt%20business%20practices_2020_11.pdf)
establishes random customer order, round-robin request positions and a common effective window-close queue time.
The [SPP Transmission Service Reference Manual](https://www.oasis.oati.com/SWPP/SWPPdocs/Transmission_Service_Reference_Manual.pdf)
documents request, status and capacity fields. Official Request Evaluation material documents flowgate/AFC impact
reports, but no inspected source establishes a machine-exported lottery position or an immutable per-position
network-state history. [SPP's OASIS registration page](https://spp.org/digital-certification-registration-for-spp-oasis/)
also shows that even query-only visitor access requires a digital certificate.

SPP therefore receives the same `R1=PASS`, `R2=FAIL`, `S0=FAIL` and `A0=FAIL for a ready, reusable bulk pipeline`.

### BPA backup

The [BPA simultaneous-submission-window practice](https://www.bpa.gov/-/media/Aep/transmission/business-practices/tbp/simultaneous-submission-window-bp.pdf)
gives the clearest verbal expansion: customers are randomly picked, their order persists across rounds, and
requests within a customer follow assignment-reference order. Its [Short-Term ATC Analysis guide](https://www.bpa.gov/-/media/Aep/transmission/customer-training/Short-Term-ATC-Analysis-User-Guide.pdf)
documents pending/committed ATC and evaluation reports. It still does not establish the required public lottery
export or atomic pre/post state join, so it cannot replace either primary operator.

## The randomization unit is not an independent TSR rank

The rule does not uniformly permute all requests. It first permutes customers and then expands that order through
round-robin rounds. Multiple requests from one customer consequently share a treatment component, and TSR ranks
within a window are dependent. Any future design would need exact assignment probabilities and inference at the
window/customer-permutation level. Treating each TSR as an independent random draw, or treating observed rank as
an ordinary continuous instrument, would understate dependence and misstate the estimand.

## Scientific reduction warning

Even under a hypothetical complete private export, the immediate allocation can be written schematically as

\[
c_k=c_{k-1}-a_{\pi_k}x_{\pi_k},\qquad
x_{\pi_k}=\mathbf 1\{a_{\pi_k}\leq c_{k-1}\},
\]

where \(c_k\) is remaining flowgate capacity, \(a_i\) is a request's multi-constraint usage and \(\pi\) is the
customer-round-robin order. This is random-order online multidimensional packing or serial allocation. A third
party can lose feasibility when an earlier request consumes capacity, but that immediate “cascade” is a ledger
and feasible-set contraction; no physical power injection, market price formation, dissipation or stationary
dynamics occurs at reservation evaluation.

No exact academic use of the OASIS SSW lottery was found in this audit, but that narrow application gap does not
establish a Nature-level method. The closest families already include:

- connection-order and hosting-capacity path dependence, including Fernandes Fontinele, Torrez Caballero and
  Costa's 2026 *Connection Order Matters* working paper, Johnston--Liu--Yang's interconnection-queue work,
  Gorman et al. on US grid-connection barriers, Pollitt et al. on connection-queue rules, Mays on generator
  interconnection and PNNL hosting-capacity analysis;
- random-order online packing, including Kesselheim et al.,
  [*Primal Beats Dual on Online Packing LPs in the Random-Order Model*](https://doi.org/10.1137/15M1033708),
  Naori and Raz on multidimensional random-order packing, and Albers--Khan--Ladewig on random-order knapsack/GAP;
  and
- causal inference under interference, including Hudgens--Halloran,
  [Aronow--Samii](https://doi.org/10.1214/16-AOAS1005), Athey--Eckles--Imbens and Basse--Airoldi.

The frozen 20-primary-work novelty gate was intentionally not completed after the public data contract failed.
The partial hostile audit covered 18 directly adjacent works and found no exact OASIS application; it is evidence
of a severe reduction risk, not a literature-complete novelty verdict. Current decision priors are approximately
3% that the frozen public contract could be rescued and, conditional on complete data, 8--10% that a central
result would survive the packing/path-dependence reduction. Their combined survival is about 0.3%; these are
review judgments, not empirical probabilities.

## Binding closure and exact reopen condition

Do not query TSR records, count support, scrape OATI pages, buy data or certificates, register a market entity,
implement a parser or replay engine, estimate effects, run EcoMD, call a model API or use GPU under this route.
Do not infer random order from `TIME_QUEUED`, update timestamps, assignment references or result order.

Reopen only after receiving versioned, field-level written confirmation from **both** MISO and SPP/OATI that:

1. a stable SSW run identifier and each customer's realized lottery order, round and derived TSR evaluation
   position are persisted and available through a supported machine export, with their precise relation to
   ordinary queue time;
2. the export contains the complete eligible customer/request set and either a verifiable randomization log or
   exact assignment-probability rule;
3. each evaluation position joins atomically to its immediately preceding and succeeding AFC/ASTFC vectors,
   limiting flowgates, impact/response factors, topology, outages, counteroffer trace and calculation/software
   version, including interleaved non-SSW updates;
4. historical availability, credentials, cost, rate limits, automated-use terms and publication/reuse rights are
   explicit; and
5. an outcome-blind metadata query can then test at least 50 admissible multi-constraint lotteries per operator
   and 200 combined without exposing effects.

MISO and SPP may then count only as cross-network replications of a shared vendor mechanism. A claim of
implementation-independent replication additionally requires a non-OATI system with a substantively different
allocation implementation. Any reopened T0 must use online packing, exact constrained-permutation inference and
connection-order hosting-capacity models as mandatory baselines and freeze a downstream response that is not the
mechanical AFC decrement itself.

No external schema inquiry was sent during this audit. Sending one would be a new external action requiring
separate user authorization.
