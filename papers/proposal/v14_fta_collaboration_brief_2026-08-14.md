# V14 FTA prospective-data collaboration brief

**Date:** 2026-08-14

**Status:** partner discovery only; no organisation has been contacted or confirmed.

## 1. Decision

The FTA confirmation study needs an authorised prospective research partnership around a real Secondary Settlement
Point (SSP) rollout. It cannot be supplied by a generic market-data vendor. The minimum viable partnership is:

1. one FRMP, retailer or energy-service/aggregation business that will actually offer and operate an SSP-based
   service after 2026-11-01; and
2. the NMISP plus Metering Data Provider/Metering Coordinator chain that creates the SSP and supplies its standing,
   interval-meter and settlement records.

AEMO should be asked to facilitate partner discovery, confirm the event clock and schemas, and clarify whether any
de-identified output will become public. AEMO is not assumed to hold the retailer's invitation, consent, product
offer or control-action history. A DNSP/PNSP is a useful optional partner for outages and network context, but it
cannot replace the operating FRMP and metering chain.

For an NCS/NMI-scale claim, one portfolio is a development/feasibility cohort, not sufficient independent
confirmation. The intended design needs at least two independently governed rollout cohorts or a second sealed
market transition.

## 2. Collaboration topology

| Party | Indispensable contribution | Why that party alone is insufficient |
|---|---|---|
| SSP-operating FRMP, retailer or aggregator | eligible population; invitation, consent and adoption times; product/rule version; dispatch or control actions; commercial operating context | may not hold authoritative SSP lifecycle, validation flags or final metering/settlement data |
| NMISP | SSP allocation, PCP--SSP relationship, creation/activation/abolition and participant-role history | usually does not own the customer offer, behavioural intervention or full outcome interpretation |
| MDP and MC | interval observations, substitutions/estimations, missingness and quality flags, settlement delivery | meter outcomes without invitation, action and non-adopter records do not identify behavioural adaptation |
| AEMO NEM Reform / ITWG | official clock and schema interpretation; identification of genuine industry-test/go-live participants; possible sharing facilitation and independent process validation | industry testing does not run prospective settlements, and public documentation is not a participant-level outcome panel |
| DNSP/PNSP, optional | outages, local constraints, PCP context and cross-participant validation | network context does not reveal the service offer, adoption or control action |
| Academic/ethics host, optional | ethics review, secure environment and governance credibility | cannot create the missing operational records |

The preferred contract is therefore with an already integrated operational team rather than five unrelated
organisations. A retailer/aggregator that can bring its nominated NMISP, MDP and MC into one data agreement is the
lowest-friction principal partner.

## 3. Minimum data contribution

The agreement must cover the complete eligible cohort, not a hand-picked list of successful SSPs, and must include
non-adopters, failed requests and exits. Required fields are:

- a stable research pseudonym for the premises, SSP, controllable asset and participating organisation, with raw
  NMI, address and direct customer identifiers retained by the partner;
- eligibility, invitation, consent, enrolment, SSP request, creation, activation, suspension and abolition times;
- PCP--SSP linkage, participant roles and every effective-dated role change;
- exact tariff, product, mechanism and software/rule version presented to each unit;
- actions or control signals available to the participant before the corresponding outcome is realised, including
  null, rejected and failed actions;
- five-minute interval meter and settlement outcomes, with validation, substitution, estimation, late-arrival and
  missingness flags;
- declared rollout assignment or invitation policy, so adopters can be compared with eligible non-adopters or a
  staggered rollout rather than an unmatched before/after sample; and
- outages, asset availability and other pre-declared confounders needed to distinguish behaviour from mechanical
  availability.

No hard sample-size gate should be invented before a clustered pre-event power simulation. For partner scouting,
the useful target is the complete portfolio with hundreds and preferably thousands of eligible assets, plus a
credible control or staggered-adoption group. A cohort of only a few successful sites can validate plumbing but
cannot support the headline adaptation claim.

## 4. Acceptable operating models

### A. Pseudonymised research export

The partner sends immutable, versioned extracts to a controlled research store. This has the lowest analysis burden
but may be unacceptable for customer-level meter data.

### B. Secure enclave or code-to-data

Raw records remain inside the partner's environment; containerised, hashed analysis code runs there and only
disclosure-controlled aggregates leave. This is scientifically acceptable if row counts, schema hashes, failures
and audit logs can be retained for peer review.

### C. Joint prospective field study

The partner declares the eligible population and rollout rule before go-live, optionally randomises or staggers
invitations, and releases outcomes only after the forecast artefact is sealed. This is the strongest design and the
recommended collaboration form. It changes the study from retrospective access negotiation into a real Lucas test.

## 5. Scientific and legal terms that cannot be traded away

1. The forecast artefact, model set, estimands, exclusions and scoring code are timestamped before target outcomes
   are opened.
2. The full eligible cohort, null actions, failures and attrition are retained. The partner cannot select only good
   cases after observing results.
3. The research team may publish negative or null findings. The partner may review privacy, security and factual
   descriptions, but has no result-based publication veto.
4. The agreement permits peer-review audit material: schemas, row counts, provenance, transformation hashes and
   disclosure-controlled derived statistics. Raw NMI/address/customer records are neither requested for publication
   nor released.
5. Ethics/privacy review, retention, deletion, breach response and cross-border access are agreed before transfer.
6. Commercial product development and scientific model evaluation are separated; partner analysts do not tune the
   frozen forecast after viewing target-period outcomes.
7. Authorship follows substantive scientific contribution. Providing access alone earns acknowledgement and a data
   statement, not automatic authorship.

If a prospective partner refuses complete-cohort access, failed-action retention, negative-result publication or
pre-outcome sealing, the FTA event is unsuitable for the flagship claim.

## 6. Who to approach

### First route: AEMO NEM Reform and the Industry Testing Working Group

Ask `NEMReform@aemo.com.au` for a short technical discussion and introductions to organisations that have actually
committed to Release 2 industry testing or production SSP operation. The request should also ask whether AEMO plans
any de-identified SSP creation, active-interval or settlement publication. Industry testing is useful for schema
conformance and partner discovery, but AEMO's test strategy says it will not run prospective settlement testing;
therefore test data cannot be presented as the post-rule behavioural outcome.

### Second route: an operating retailer/aggregator plus its data chain

The highest-priority principal is an organisation that can provide both a real SSP product cohort and its nominated
NMISP/MDP/MC contacts. Public FTA consultation participation establishes a relevant contact pool, not production
commitment. Retail/energy-service organisations in that pool include AGL, Alinta Energy, EnergyAustralia, Enel X,
Origin Energy, and Red Energy/Lumo Energy. Approach no more than three initially, selected after AEMO clarifies which
ones are testing or planning a rollout.

### Third route: NMISP and metering implementation partners

The same consultation record identifies metering and implementation stakeholders including Bluecurrent,
IntelliHUB, Landis+Gyr and PLUS ES. The public AEMO MDP register provides a broader technical contact pool. ENM
Solutions publicly describes itself as an accredited NMISP and offers SSP creation services, but the AEMO
accreditation page reviewed on 2026-08-14 did not expose a dedicated downloadable NMISP roster. Its status and any
other NMISP claim must be confirmed directly with AEMO before scientific reliance.

### Optional network partners

Ausgrid, AusNet, CitiPower/Powercor, Energy Queensland, Evoenergy, Jemena, SA Power Networks, TasNetworks and United
Energy participated in the consultation and are candidates for network context. They should be approached only
after an operating-product partner is identified, unless one can introduce the full FRMP/NMISP/MDP chain.

None of these names is a confirmed collaborator or confirmed Release 2 SSP operator. Consultation participation is
evidence of technical interest only.

## 7. Concrete first ask

The first communication should not ask vaguely for “data”. It should request:

1. confirmation of a planned SSP use case, expected rollout window and approximate eligible-cohort scale;
2. the organisations holding offer/invitation, SSP lifecycle, control-action, meter-quality and settlement records;
3. willingness to preserve the whole eligible cohort and support a pre-outcome model/analysis seal;
4. the acceptable access model: pseudonymised export, secure enclave or code-to-data;
5. permission to publish negative results and disclosure-controlled aggregate findings; and
6. one schema call followed by a metadata-only field inventory, with no target outcome rows opened.

Prepare a two-page scientific brief, a one-page field dictionary and a draft governance schedule before outreach.
Do not promise commercial recommendations, customer-level predictions or favourable results.

## 8. Go/no-go rule

FTA remains `WATCHLIST_ONLY` until one principal partner confirms the field inventory, complete-cohort coverage,
prospective seal and publication terms in writing. It becomes a flagship confirmation event only after a clustered
power/design audit and an independent replication path are also locked. Otherwise, use the public FTA schemas for
method development and find a different intervention with observable participant actions.

## 9. Evidence base

- [AEMO FTA implementation page](https://www.aemo.com.au/initiatives/major-programs/nem-reform-program/nem-reform-program-initiatives/flexible-trading-arrangements): scope, voluntary participation, NMISP role and 2026-11-01 Release 2 clock.
- [AEMO Release 2 Industry Test Strategy](https://www.aemo.com.au/-/media/files/initiatives/flexible-trading-arrangements/2026/aemo-november-2026-release-fta-release-2-industry-test-strategy-final.pdf?rev=b2c3405491f0438f83e8486bd3e460d4&sc_lang=en): test scope, cross-participant testing, schedule and exclusion of prospective settlement testing.
- [AEMO MDM reports](https://tech-specs.docs.public.aemo.com.au/Content/TSP_MSATS_Oct2026/MDM_Reports.htm): participant delivery and RM29/RM53 field contracts.
- [AEMO data-sharing process](https://di-help.docs.public.aemo.com.au/Content/Data_Sharing/2_-Requesting_data_sharing.htm): affected-party agreement and production sharing requirements.
- [AEMO 2025 FTA consultation](https://www.aemo.com.au/consultations/current-and-closed-consultations/2025-flexible-trading-arrangements): public stakeholder submissions used only to construct the contact pool.
- [AEMO accreditation and registration](https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/market-operations/retail-and-metering/accreditation-and-registration): qualification documents and public provider registers reviewed at the audit date.
- [AEMO Industry Testing Working Group](https://www.aemo.com.au/consultations/industry-forums-and-working-groups/list-of-industry-forums-and-working-groups/nem2025-industry-testing-working-group): official testing-engagement route.
- [ENM Solutions NMISP page](https://www.enmsolutions.com.au/nmi-service-provider): non-AEMO self-description that requires official accreditation confirmation.
