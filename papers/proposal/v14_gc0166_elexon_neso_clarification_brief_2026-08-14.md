# V14 GC0166 Elexon/NESO clarification brief

**Prepared:** 2026-08-14

**State:** `SEND_READY_UNSENT`

**Authority boundary:** this document prepares two narrowly scoped research enquiries. No message, form submission,
account creation or data request has been sent. External contact requires the user's approval.

## 1. Decision and purpose

The remaining GC0166 blocker is no longer a vague search for electricity-market data. Official Elexon documents
show that the `CRA-I015` flow contains BM Unit and Lead Party identifiers, action codes and effective-from/to dates.
Elexon also directs non-BSC organisations seeking specific BSC data to the BSC Service Desk. This creates a concrete
request route for identity history; it does not prove that a complete historical extract is public, free, retained
for the required period or licensed for research redistribution.

The public MDO/MDB schemas expose the parameter value, BMU, settlement interval, publication time and serial number.
The GC0166 rules separately define participant submissions, initial values, `C` copy-forward, `Z` zero-fill and EDL
rejection acknowledgements. The official public material reviewed does not expose a field that joins a published
row to one of those origins. Until that distinction is auditable, a row cannot be interpreted as participant
behaviour.

The requests below seek only the minimum metadata and provenance needed to decide whether GC0166 can be a
prospective behavioural event. They do not request proprietary optimiser logic, personal data or a commercial
market feed.

## 2. Routing

1. **Elexon BSC Service Desk / Insights support:** request the historical registration flow, access terms and the
   exact public MDO/MDB publication semantics. Elexon's official data-flows page explicitly gives this route to
   non-BSC organisations.
2. **NESO GC0166 / Balancing Mechanism implementation team:** request authoritative submission/default/rejection
   semantics and the controlled-rollout roster when Elexon cannot answer or does not hold the source logs.

Identity history may require only an ordinary Elexon service request, not a research collaboration. NESO/Elexon
cooperation or disclosure-controlled analysis is more likely to be needed for EDL rejection and default-origin
provenance. No generic paid-data vendor can reconstruct a source flag that the operational systems never publish.

## 3. Send-ready Elexon request

**Suggested subject:** Academic research request: historical CRA-I015 and MDO/MDB provenance for GC0166

> Hello Elexon Service Desk,
>
> I am conducting non-commercial academic research on prospective forecasting of participant responses to the
> GC0166/P499 Balancing Mechanism change. Before collecting any event outcomes, I am auditing whether the required
> identity and submission provenance can be observed reproducibly.
>
> The live NETA Interface Definition and Design Document Part 2 describes CRA-I015 records with action codes, BM
> Unit and Lead Party identifiers, and effective-from/effective-to dates. Could a non-BSC researcher obtain a
> historical CRA-I015 backfill from at least 1 January 2024 plus a continuing delivery through 31 December 2027,
> including adds, changes and deletes? If another flow is required to recover Lead Party transfers, closures or
> related identity changes, please identify it as well.
>
> Could you also clarify the following for the MDO and MDB datasets introduced under P499?
>
> 1. Does each published MDO/MDB record identify whether it originated from an authenticated participant
>    submission, the initial `9999.000/-9999.000` value, a `C` copy-forward or a `Z` zero-fill default?
> 2. Are rejected EDL messages, error reasons, late submissions and expected-but-missing submissions retained in a
>    public or disclosure-controlled dataset?
> 3. Do `publishTime` and `serialNumber` provide a complete, retained history of every received and superseded
>    MDO/MDB record, and what are the retention/backfill guarantees?
> 4. Were initial system-generated MDO/MDB values published for all active BMUs before 14 August 2026?
> 5. What licence, attribution, retention, account, delivery and cost terms would apply to the requested CRA and
>    provenance material?
>
> A public release is preferred. If row-level rejection data cannot be released, a code-to-data environment or a
> disclosure-controlled extract containing non-personal provenance flags and reason-code categories would be
> sufficient. We do not need participant contact details, proprietary NESO optimiser logic or personal data.
>
> I would be grateful if you could confirm the authoritative field dictionary and direct me to the correct request
> form or team. The study will report a negative feasibility decision if these distinctions cannot be audited.
>
> Kind regards,
> [Researcher name and institutional details]

## 4. Send-ready NESO request

**Suggested subject:** GC0166 research clarification: participant submissions, defaults, EDL failures and pilot scope

> Hello GC0166 implementation team,
>
> I am preparing a non-commercial, prospectively registered study of model forecasts around the 5 November 2026
> GC0166 operational deadline. I have not opened the target outcome data. The design requires a strict separation
> between participant actions and system-generated states.
>
> Could you please confirm:
>
> 1. whether the MDO/MDB values sent to Elexon carry an origin flag for participant submission, initial value, `C`
>    copy-forward or `Z` zero-fill, even if that flag is not currently published;
> 2. whether expected submissions, accepted submissions, rejected EDL messages, rejection categories, late messages
>    and missing messages are retained in an auditable log;
> 3. the complete list of controlled-rollout BMUs and their first-live or first-authenticated-submission dates;
> 4. whether system-generated initial values were created or published for every active BMU before 14 August 2026;
> 5. the versioned rule or data source assigning each BMU its `C` or `Z` default; and
> 6. whether a non-commercial researcher could validate aggregate counts or run approved code against these fields
>    if row-level operational logs cannot be released.
>
> We are not requesting optimiser source code, commercially sensitive bid strategy, participant contact details or
> personal data. If submission provenance cannot be made auditable, the project will treat GC0166 only as a
> mechanism/state case study and will not claim participant behavioural adaptation.
>
> Kind regards,
> [Researcher name and institutional details]

## 5. Minimum field dictionary

### Identity and eligibility

| Field | Minimum semantics | Why required |
|---|---|---|
| `action_code` | add/change, delete or no-change for the delivered record | reconstruct the registry without survivorship bias |
| `bm_unit_id` and `ngc_bm_unit_id` | stable IDs plus documented aliases | join Elexon and NESO records |
| `bm_unit_name` and `bm_unit_type` | effective-dated attributes | unit classification and schema checks |
| `lead_party_id` | effective-dated responsible party identifier | persistent-participant and clustering analysis |
| `effective_from`, `effective_to` | inclusive/exclusive convention stated | entry, exit and transfer timing |
| capacity and production/consumption fields | units and revision semantics stated | pre-event controls and eligibility checks |
| delivery/version timestamp | extraction and snapshot identity | reproduce the registry as known at forecast time |

### Submission and failure provenance

| Field | Minimum semantics | Why required |
|---|---|---|
| BMU and settlement interval | same keys as public MDO/MDB | deterministic join |
| event/serial/publish timestamps | ordering and replacement semantics | revision reconstruction |
| `origin_kind` | participant, initial, `C`, `Z`, or other system action | prevent defaults being labelled behaviour |
| expected-submission indicator/deadline | which unit-periods had an opportunity/obligation | construct the null-action denominator |
| accepted/rejected/late/missing status | exhaustive mutually exclusive definitions | avoid conditioning on successful messages |
| rejection category | stable documented code or coarser approved class | failure response and data-quality audit |
| supersedes/superseded-by key | links all versions | preserve corrections rather than latest-only rows |

### Pilot and retention

- complete controlled-rollout BMU IDs and first-live/first-authenticated-submission timestamps;
- date on which initial records were generated or first made public for every non-pilot BMU;
- historical start date, deletion policy, correction policy and completeness guarantees; and
- licence, attribution, redistribution, delivery, account and any fee conditions.

## 6. Acceptable access modes

Preference order:

1. versioned public release under the BSC/BMRS open-data licence;
2. standard non-Party extract under explicit research and derived-output terms;
3. disclosure-controlled row-level access with approved exports;
4. code-to-data execution returning preregistered aggregate counts and model scores.

Modes 3 or 4 can establish feasibility only if the full analysis is independently reproducible or audited. An
informal verbal assurance, a hand-selected pilot list or aggregate total without a declared denominator does not
pass G1.

## 7. Response-to-gate map

| Answer | Contract consequence |
|---|---|
| complete CRA-I015 history, licence and retention supplied | identity-history gate may pass after a zero-row integrity audit |
| current active list only | identity-history gate remains unresolved |
| auditable origin plus accepted/rejected/late/missing denominator | null/failure gate may pass after schema tests |
| public value rows without provenance | GC0166 is restricted to a mechanism/state study |
| complete pilot roster and initial-publication clock | confirmation exclusions can be frozen |
| every BMU was exposed before the freeze with no independent onboarding clock | untouched cohort may be exhausted; do not relabel it |
| fees or restrictive terms | compare against the preregistered value-of-information gate; do not purchase automatically |

No answer changes the current state by itself. Evidence must be versioned in the event contract, tested, and
reviewed before any target endpoint is opened.

## 8. Official basis

- [Elexon NETA IDD Part 2, live V55.0](https://bscdocs.elexon.co.uk/interface-definition-documents/neta-interface-definition-and-design-document-part-2-interfaces-to-other-service-providers)
- [Elexon data flows and the non-BSC Service Desk route](https://www.elexon.co.uk/bsc/data/key-data-reports/data-flows-available-from-bsc-systems/)
- [Elexon active BM Unit route](https://www.elexon.co.uk/bsc/operational/balancing-mechanism-units/)
- [Elexon P499](https://www.elexon.co.uk/bsc/mod-proposal/p499/)
- [Elexon MDO/MDB API documentation](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/MDB/stream)
- [Elexon API guidance on data-as-received and superseded retrieval](https://bmrs.elexon.co.uk/api-documentation/guidance)

**Contact log:** none; both drafts remain unsent.
