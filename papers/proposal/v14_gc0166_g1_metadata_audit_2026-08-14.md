# V14 GC0166 G1 metadata audit

**Date:** 2026-08-14

**Decision:** `STARTED_METADATA_ONLY`; `G1 NOT PASSED`

**Access lock:** no target or pilot API row, paid dataset, remote worker, V100 or RTX2060 was used or queued.

## 1. Executive result

GC0166 remains worth a bounded feasibility effort because it has a future compliance deadline, public rule text,
public BMU-level action and acceptance schemas, and an open-data licence. The audit improved its contract from a
lead to a partially specified experiment, but it did not admit the event. Five of ten G1 clauses pass and five are
unresolved.

The central risk is now sharper than generic “data access.” Public rules distinguish participant submissions,
automatic copy-forward or zero defaults, initial values, and rejected EDL messages. The documented BMRS rows expose
values, publication times and serial numbers, but the public sources reviewed so far do not prove that a researcher
can distinguish those provenance states. A final MDO/MDB row is therefore not automatically a behavioral action.
If public records cannot identify authenticated submissions and missing/rejected/default-generated messages,
GC0166 cannot support V14's behavioral-plasticity claim and should be downgraded to a mechanism/state case study.

## 2. What was inspected

The audit used official NESO and Elexon rule pages, the GC0166 Final Modification Report, Data Validation,
Consistency and Defaulting Rules, EDL Message Specification, MDO/MDB Best Practice Guidance, BSC Modification P499,
the Elexon API guidance and endpoint schemas, BSCP15 and the BMRS licence. The source inventory and evidence-page
references are versioned in `data/manifests/gc0166_prospective_event_contract_v1.yaml`.

A reproducible local probe fetched only allowlisted documentation URLs. It stores response status, byte count,
SHA-256 and missing-marker names, never page content. NESO and `www.elexon.co.uk` returned HTTP 403 bot-protection
responses. BMRS documentation paths returned a common 926-byte JavaScript shell, so their endpoint fields are not
present in raw HTML. This is a reproducibility constraint on automated documentation capture, not a failed event
gate by itself. The content-free record is
`data/manifests/gc0166_documentation_probe_2026-08-14.yaml`.

No live MDO, MDB, BMU, bid, acceptance or settlement data endpoint was queried. Example-shaped rows visible in
official documentation were treated as schema evidence only.

## 3. Rule semantics that change the experiment

1. GC0166 applies the new parameters to all BM Units active in the Balancing Mechanism. A unit that can deliver the
   full accepted volume may use a default value; a constrained unit must declare its limitation. Presence of an
   MDO/MDB row is therefore not a limited-duration label or an adoption outcome.
2. Initial MDO and MDB values are `9999.000` and `-9999.000` MWh. For missing or partial day-ahead data, each BMU is
   assigned either copy-forward (`C`) or zero-fill (`Z`) defaulting. A value change or repeated row may be generated
   by the system rather than chosen by the participant.
3. MDO/MDB submissions use EDL. NESO validates syntax, rights, unit identity, value bounds and time ordering. Valid
   messages receive an acknowledgement; invalid messages receive a private error acknowledgement and reason code.
   The audit did not find a public BMRS rejection stream.
4. After gate closure, MDO/MDB may be resubmitted only after specified events such as unavoidable faults, a BOA,
   depletion of reserved ancillary-service energy, or a relevant PN change. Those public constraints are exactly
   replayable.
5. NESO's optimiser uses declared MDO/MDB to cap cumulative energy in proposed instructions, but optimiser choice,
   emergency intervention and operator discretion are not an exact public engine. They must be modeled as observed
   stochastic outcomes, not silently replaced with an EcoMD simulator.
6. Elexon states that dataset endpoints publish data as received and support superseded-data retrieval and archive
   backfill. `publishTime` and `serialNumber` therefore pass the intended revision-protocol gate; empirical
   completeness remains a G2 data-quality test.

## 4. G1 gate ledger

| Gate | State | Evidence-based decision |
|---|---|---|
| clock | pass | NESO requires operational implementation by 2026-11-05; the five-unit controlled rollout is already live and is development-only |
| licence | pass | the BMRS licence permits academic use, copying, adaptation and redistribution with attribution |
| action schema | pass | MDO/MDB have BMU, settlement, envelope, publication-time and serial fields; acceptances and reference schemas exist |
| revision history | pass | Elexon documents dataset endpoints as received, with superseded retrieval and backfill; completeness moves to G2 |
| mechanism boundary | pass, scoped | validation/defaulting/resubmission/energy caps are exact; optimiser selection and discretion are explicitly outside exact replay |
| eligible population | unresolved | “all active BMUs” is a rule definition, but no frozen effective-dated active population plus limited-duration/control classification has been established |
| identity history | unresolved | the public reference endpoint is current-only; BSCP15 proves effective-dated CRA records exist but not that a complete historical public extract is available |
| null/failure capture | unresolved | EDL rejection and default rules exist, but public provenance for submitted/defaulted/rejected/late/missing messages is unproved |
| response freeze | unresolved | a defensible response depends on the preceding provenance fields and a pre-event precision calculation |
| independent replication | unresolved | no second independently governed future event has passed its own contract |

`5 pass + 5 unresolved` is not G1. No model training, prospective collector or result endpoint is authorized.

## 5. Conditional experiment design

The statistical unit is a BMU by settlement period, clustered by Operational Day and Lead Party. The five already
operating pilot units, plus every BMU with an MDO/MDB publication before the 2026-08-14 freeze, are development-only.
They cannot confirm the prospective claim.

That exclusion is intentionally conservative. If system-generated initial values were published for the whole
active population before the freeze, it would exhaust the confirmation cohort. The design could then continue only
with a prospectively frozen official onboarding/authenticated-submission roster; it cannot relabel pre-freeze rows
as untouched after seeing their outcomes.

The response vector remains deliberately `not_frozen`. If provenance becomes public, the candidate vector is:

1. authenticated participant MDO/MDB envelope updates conditional on PN, accepted instructions, reserved services
   and public system state;
2. bid-offer and PN adaptation for persistent BMUs;
3. acceptance probability, instruction feasibility under the contemporaneous declared envelope and delivery
   reliability;
4. entry, exit, Lead Party concentration and contribution-share reallocation; and
5. technical onboarding only when an independent onboarding or authenticated first-submission clock exists.

Candidate fixed post-deadline scoring horizons are 1, 7, 28 and 84 days. They are planning values, not a freeze.
The primary score, interval aggregation, default-state treatment and minimum detectable effect must be set after a
non-target schema/precision sample becomes lawful and before any confirmation outcome is opened.

Negative controls are pre-classified long-duration or conventional BMUs under documented default rules and placebo
dates before the compliance deadline but outside the controlled-rollout start. Matching may use pre-event
covariates only. A default MDO/MDB row alone cannot define a control.

## 6. Data required to unlock the experiment

### Required before any target query

1. An effective-dated BMU/Lead Party table with active-from, active-to, transfers, technology, duration/capacity and
   the BMU-specific `C` or `Z` default rule.
2. A public field or companion log that distinguishes participant submissions from initial, copied and zero-filled
   values.
3. Coverage semantics for rejected, failed, late and missing EDL messages, including whether error reason codes can
   be published or audited under code-to-data access.
4. The identities and first-submission dates of every controlled-rollout BMU, or an exclusion rule that can recover
   them without reading confirmation outcomes.
5. A frozen response/scoring contract and a second independently governed prospective event contract.

### Required only after G1

- all revisions of MDO/MDB, PN, bid-offer, acceptance and relevant physical/dynamic records;
- public system-state and confound panels at matching timestamps;
- immutable daily shards, source timestamps, schema versions, retrieval manifests and missing-sequence flags; and
- a limited development sample for row counts, revision multiplicity, storage and pre-event power simulation.

There is no purchase recommendation. The unresolved information is provenance and governance, not a commodity
price feed. An Elexon/NESO clarification or controlled code-to-data agreement may be needed if the public API omits
rejection/default origin; buying generic electricity data would not repair that omission.

## 7. Compute requirement and execution state

| Stage | Data and compute | Authorization |
|---|---|---|
| current G1 metadata audit | Mac CPU; six unit tests plus schema/type/lint checks; latest documentation probe completed in 16.2 seconds | completed; no GPU |
| remaining free G1 work | official documents, OpenAPI definitions and written schema clarification; expected under 20 Mac core-hours and negligible bulk storage | authorized, metadata only |
| post-G1 development sample | CPU parsing, columnar storage and precision simulation; RAM, storage and core-hours measured from a limited non-target shard rather than guessed | locked until contract passes |
| G2 model ladder | RTX2060 for smoke/parity; two V100 32 GB workers for independent domain/model/seed jobs; CPU workers for parsing and bootstrap | locked until G1/G2 admission |
| later scale | additional non-H20 CPU/GPU workers only after profiling identifies compute, rather than event support, as the bottleneck | not authorized |

No H20 is assumed. Starting GPU work now would only accelerate models for an outcome whose behavioral observable is
not yet established.

## 8. Minimum clarification request

Before external contact, prepare but do not send the following questions without user approval:

1. Do public MDO/MDB datasets identify whether each record was a participant submission, initial value, `C`
   copy-forward or `Z` fill?
2. Are rejected EDL messages, reason codes, late messages and missing expected submissions retained in any public or
   disclosure-controlled dataset?
3. Which public extract provides effective-dated BMU and Lead Party registration/transfer history?
4. Can NESO publish the complete controlled-rollout unit list and first-live dates before the confirmation freeze?
5. What retention and completeness guarantees apply to superseded MDO/MDB serials?
6. Were system-generated initial MDO/MDB values published for non-pilot BMUs before 2026-08-14, and if so does that
   leave any genuinely untouched cohort?

If questions 1-3 cannot be answered with auditable data, stop treating GC0166 as V14's behavioral confirmation
event. It may remain a useful exact-defaulting and dispatch-constraint development case.

## 9. Reproduction

```bash
conda run -n ecophys python -m ecomd.research.prospective_event_contract \
  data/manifests/gc0166_prospective_event_contract_v1.yaml --probe-documentation
conda run -n ecophys pytest -q tests/test_prospective_event_contract.py
conda run -n ecophys mypy --strict ecomd/research/prospective_event_contract.py
conda run -n ecophys ruff check \
  ecomd/research/prospective_event_contract.py tests/test_prospective_event_contract.py
```

The validator rejects live `data.elexon.co.uk` URLs, query strings and any contract that claims target, pilot,
external-worker or paid-data access during the metadata-only stage.
