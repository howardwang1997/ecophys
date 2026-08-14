# V14 cross-domain and cross-region event scout

**Date:** 2026-08-14

**State:** metadata and schema audit only; no candidate target endpoint was queried for a research outcome panel.

## 1. Decision

Australia is not a scientific requirement. AEMO FTA was considered because it has a public rule clock, not because
the paper is about Australia. Its affected-participant panel is private, so it should remain a partner-conditional
option rather than the default flagship event.

The domain-independent object is a prospective Lucas test: fit and select models before a real mechanism changes,
seal their probabilistic response forecasts, then test whether they predict mechanical, persistent-participant and
population responses without post-event refitting. Cross-region and cross-domain confirmation would strengthen the
claim, provided the same capability ordering and forecast protocol have substantive rather than merely verbal
meaning in every system.

The current scouting priority is:

1. audit Great Britain's GC0166 transition as the nearest free, public, unit-level prospective electricity event;
2. maintain the frozen event-selection rule for the next qualifying on-chain market mechanism change; and
3. retain AEMO FTA only if an authorised participant partnership becomes available on acceptable terms.

The first GC0166 metadata audit is complete at `5/10` contract clauses passed. The on-chain first-event rule is now
frozen, but its candidate registry is empty. No event is yet admitted and `G1 NOT PASSED` remains the correct state.
The audit and executable contracts are
`papers/proposal/v14_gc0166_g1_metadata_audit_2026-08-14.md` and
`data/manifests/gc0166_prospective_event_contract_v1.yaml`, plus
`data/manifests/onchain_prospective_event_selection_v1.yaml`.

## 2. Domain-independent admission contract

A region or field is eligible only if it supplies all of the following before outcomes are examined:

1. a versioned rule and an activation or unit-adoption clock that can be frozen prospectively;
2. persistent participant or unit identifiers, with declared entry, exit and identity-change handling;
3. timestamped actions available before their outcomes, including null, rejected and failed actions;
4. outcomes and a defensible state/confound panel at the same statistical unit;
5. a legal, reproducible observation route with versioned schemas and retention; and
6. a response vector for which the same M0--M4 model-capability ladder is meaningful.

Public prices or aggregate traffic alone do not pass. A policy document without affected-agent actions does not
pass. A software upgrade whose only observable effect is deterministic execution latency may be useful systems
engineering, but it does not automatically test adaptive economic behaviour.

## 3. Current candidate ranking

| Priority | System and region | Prospective clock | Observable actions/outcomes | Status and principal risk |
|---|---|---|---|---|
| A | NESO GC0166, Great Britain electricity Balancing Mechanism | operational implementation required by 2026-11-05; controlled rollout already live | Elexon exposes BMU identities, MDO/MDB, physical/dynamic parameters, bid-offers, acceptances and settlement/cashflow reports through public APIs | `PRIORITY_G1_AUDIT`, not admitted; early-pilot contamination, eligibility completeness and the non-public parts of dispatch decision logic must be resolved |
| B | next qualifying CoW or Uniswap economic-mechanism change, permissionless networks | exact on-chain execution is available only after a proposal is final | solver/pool/wallet actions, code, governance and settlement are largely public | `FROZEN_EMPTY_REGISTRY`; post-cutoff origin, 28-day lead, identities, failures and ten other clauses are mandatory; no event selected |
| C | Solana Alpenglow, global validator network | official page says Q3 2026, but no frozen activation instant was established | validator, stake, vote, block and latency records are publicly reconstructable | `WATCHLIST_CLOCK_UNFROZEN`; may measure engineering/validator adaptation rather than the same economic object |
| D | Ethereum Hegotá, global validator/application ecosystem | official roadmap says H2 2026 while proposals remain under discussion | protocol code and on-chain actions are public | `WATCHLIST_CLOCK_UNFROZEN`; treatment is multi-component and could defeat causal interpretation |
| E | AEMO FTA Release 2, Australia retail electricity | official 2026-11-01 clock | schemas are public, but affected SSP adoption, actions and interval settlement are participant-facing | `PARTNER_CONDITIONAL`; exact clock but no public confirmation panel |

Current CoW CIP-85 and the July 2026 Uniswap v4 fee activation cannot be promoted after observing their public
rollout. They are historical/development events. BYOS, future fee expansions and future solver-reward changes are
useful monitoring streams, but only a proposal whose rule, execution time and observation contract are frozen before
its outcome can become confirmation.

## 4. Why GC0166 moves ahead of FTA

NESO states that GC0166 introduces Maximum Delivery Offer and Maximum Delivery Bid parameters for limited-duration
assets and requires operational implementation by 2026-11-05. Five units across four lead parties were already in
the controlled rollout when NESO published its June update. Those early units must be excluded from confirmation or
used as development only.

Elexon's Insights Solution currently documents public, no-key endpoints for:

- MDO and MDB submissions by BM Unit;
- bid-offer data and bid-offer acceptances;
- physical and other dynamic parameters;
- indicative BMU cashflows and BMU-level settlement reports; and
- current BMU, fuel-type and lead-party reference data.

The BMRS open-data licence is worldwide, royalty-free and permits copying, adaptation and redistribution with
attribution, so ordinary BMRS observables do not have FTA's main access problem. CRA-I015 officially carries action
codes, BMU/Lead Party identifiers and effective dates, and Elexon gives non-Parties a Service Desk request route; a
complete historical extract, licence and any fee remain to be confirmed. The detailed audit additionally verifies
public validation, defaulting, post-gate resubmission and declared-energy constraints, and Elexon's intended
superseded-record retrieval. Those clauses define an exact public mechanism boundary without pretending that
NESO's optimiser and operator discretion are open source.

The audit also invalidates a naive staggered-adoption interpretation. All active BMUs are subject to MDO/MDB;
initial `+9999/-9999` values and BMU-specific copy-forward or zero defaults can generate public values without a new
participant action. A row or value change is not automatically adoption or behavioral plasticity. Confirmation is
conditional on a public provenance field or companion log separating authenticated submissions from generated
defaults, rejections, late and missing messages. If that cannot be obtained, GC0166 becomes a mechanism/state
development case rather than V14's behavioral confirmation event.

## 5. On-chain confirmation pipeline

Permissionless digital markets are attractive because mechanism code, governance, actions, failures and outcomes
can often be observed without a data-access partner. They also create serious selection risk because proposals occur
frequently and outcomes are immediately public.

The selection rule is now committed in machine-checkable form with an effective cutoff of 2026-08-14 07:00 UTC.
The first post-cutoff, independently governed proposal that changes solver or liquidity-provider economic payoffs;
has a final executable specification and activation block at least four weeks after its final package; preserves
complete action, identity, null/failure and outcome panels; has acceptable licence/retention; supports the common
model ladder; and passes a pre-event precision simulation becomes the event. Twelve clauses are mandatory.

Each final package must be audited within 72 hours and is ordered by its official timestamp, not local discovery.
The registry is empty. If the first qualifying proposal is inconvenient, fails operationally or produces a null
result, it cannot be silently replaced. Exact rules and tests are documented in
`papers/proposal/v14_onchain_event_selection_freeze_2026-08-14.md`.

The current watchlist contains:

- the next CoW solver-competition or reward-rule change after CIP-85;
- a future Uniswap fee-controller activation or parameter change not already executed;
- Solana Alpenglow after an exact mainnet activation clock and estimand are final; and
- Ethereum Hegotá only if one separable economic mechanism and an exact activation clock emerge.

Protocol teams can clarify schemas and activation semantics, but access need not depend on a private collaboration.
All model and scoring snapshots should be published independently before the activation block.

## 6. Recommended paper architecture

The stronger NCS story is not “an Australian market simulator predicts Australia.” It is:

> Historical realism is not intervention fidelity; a prospectively sealed model-selection protocol identifies
> which adaptive world models survive real mechanism changes across computational economies.

A plausible confirmation pair is one power-system institution and one permissionless digital market. The common
claim concerns the ranking and value of model capabilities under intervention, not equality of physical units,
welfare measures or numerical effect sizes.

For NMI, geographic breadth does not compensate for a weak method. The paper would still need a new learning or
calibration principle with theory/identifiability evidence, and the real events would validate that method. For NCS,
the prospective real-world confirmation and transparent computational protocol carry more of the headline, but two
independently governed transitions are still required.

## 7. Data, compute and collaboration consequence

- GC0166 metadata/schema audit: completed on Mac CPU with 5/10 gates passed, no purchase and no collaboration.
  Remaining G1 work is official schema/provenance clarification; storage and row budgets must be measured only
  after a non-target sampling contract is frozen.
- Later GB historical development: CPU/Parquet workload first; GPU use only for admitted learned models after G1/G2.
- On-chain events: the frozen metadata monitor is Mac-CPU-only and negligible in size. Public archive/RPC or
  indexed data may later require more storage and CPU, but no number is authorised until an event passes and a
  limited development sample is measured.
- AEMO FTA: continue only through the collaboration contract in
  `papers/proposal/v14_fta_collaboration_brief_2026-08-14.md`.
- NESO/Elexon or protocol-team conversations are valuable for interpretation and schema validation, but are not
  assumed to grant private target data.

The two V100 nodes and RTX2060 remain idle. No H20 is assumed.

## 8. Immediate gates

1. Resolve the five open GC0166 gates: deliver the defined effective-dated population/identity history, establish
   public submission/default/error provenance, freeze the response and admit independent replication.
2. Freeze the GC0166 response vector, fixed horizons, pilot exclusions, negative controls and precision design before
   retrieving target rows.
3. Maintain the frozen on-chain event-selection registry daily; inspect metadata only and audit final packages
   within 72 hours.
4. Admit neither GC0166 nor any protocol event until its complete event contract passes G1.

## 9. Primary evidence

- [NESO GC0166 implementation update](https://www.neso.energy/news/gc0166-goes-live-enabling-smarter-use-limited-duration-assets)
- [Elexon Insights API documentation](https://bmrs.elexon.co.uk/api-documentation/)
- [Elexon MDO/MDB, bid, acceptance and settlement endpoint index](https://bmrs.elexon.co.uk/api-documentation/endpoint/balancing/acceptances)
- [Elexon BM Unit reference endpoint](https://bmrs.elexon.co.uk/api-documentation/endpoint/reference/bmunits/all)
- [Elexon effective-dated CRA-I015 interface](https://bscdocs.elexon.co.uk/interface-definition-documents/neta-interface-definition-and-design-document-part-2-interfaces-to-other-service-providers)
- [Elexon non-BSC data-request route](https://www.elexon.co.uk/bsc/data/key-data-reports/data-flows-available-from-bsc-systems/)
- [Elexon BMRS open-data licence](https://www.elexon.co.uk/bsc/data/balancing-mechanism-reporting-agent/copyright-licence-bmrs-data/)
- [CoW CIP-85](https://forum.cow.fi/t/cip-85-performance-and-consistency-rewards/3377)
- [Uniswap v4 protocol-fee proposal](https://gov.uniswap.org/t/temp-check-activate-v4-protocol-fees/26162)
- [Solana Alpenglow roadmap](https://solana.com/upgrades/alpenglow)
- [Ethereum 2026 roadmap](https://ethereum.org/roadmap/)
- [AEMO FTA implementation page](https://www.aemo.com.au/initiatives/major-programs/nem-reform-program/nem-reform-program-initiatives/flexible-trading-arrangements)

Local audit: `papers/proposal/v14_gc0166_g1_metadata_audit_2026-08-14.md`.
