# V14 on-chain prospective event-selection freeze

**Prepared:** 2026-08-14

**Effective cutoff:** 2026-08-14 07:00:00 UTC

**State:** `FROZEN_NO_EVENT_SELECTED`

**Access lock:** no candidate outcome row, realized effect comparison, paid dataset, remote worker, V100 or RTX2060
was used or queued.

## 1. Decision

V14 needs a second intervention governed independently of GC0166. Frequent public protocol proposals make it easy
to wait for an attractive result and then call that event “prospective.” The repository now carries a deterministic
selection contract and validator before any future event is chosen:

- `data/manifests/onchain_prospective_event_selection_v1.yaml`;
- `ecomd/research/prospective_event_selection.py`; and
- `tests/test_prospective_event_selection.py`.

The eligible universe is deliberately narrow: the next qualifying economic-mechanism proposal originating after
the cutoff in either CoW Protocol or Uniswap. The registry is empty at freeze and no event is admitted. Proposals,
drafts and rollouts first public before the cutoff remain historical development material even if they are edited,
renumbered, split, voted or implemented later.

This freeze removes one degree of freedom; it does not pass V14 G1. The future event must still satisfy every
action, identity, null/failure, outcome, licence, lead-time, precision and common-response requirement.

## 2. Objective selection algorithm

For every post-cutoff proposal reaching a final package:

1. register its official first-publication timestamp, platform proposal ID, immutable specification/code evidence,
   final-package timestamp and activation block or UTC time;
2. complete the metadata-only eligibility audit within 72 hours, ordered by the official final-package timestamp
   rather than the researcher's discovery time;
3. require all twelve frozen criteria, including a minimum of 28 full days between the final package and
   activation;
4. select the earliest qualifying final package; and
5. break an exact timestamp tie with SHA-256 of
   `lower(platform_id + ':' + official_proposal_id)`.

The 72-hour service level prevents a researcher from delaying an inconvenient candidate while approving a later
one. An earlier final package that is still pending blocks selection of a later candidate. Missing that service
level is a reportable protocol deviation, not an exclusion reason.

The selection validator derives the winner from the append-only registry and rejects a manifest that names another
candidate. It also rejects pre-cutoff proposals, target-outcome access, candidate-effect comparison, unsafe source
hosts, inconsistent lead-time flags, late audits and selection after activation.

## 3. Qualification criteria

Every criterion is mandatory:

1. **post-freeze origin:** the proposal itself first appears after the cutoff; a revived old draft cannot qualify;
2. **economic treatment:** the rule changes participant payoffs, allocation, eligibility or competition, not only
   UI, security, deployment, speed, treasury transfer or software maintenance;
3. **binding specification:** final parameters, executable code/calldata, authority and activation clock are fixed;
4. **lead time:** at least 28 days remain for a sealed forecast and independent review;
5. **observable actions:** the relevant eligible actions are timestamped before outcomes;
6. **identity history:** persistent IDs, entry, exit, transfer and alias limits are declared without imputation;
7. **null/failure capture:** the eligible-opportunity denominator and rejected, filtered, failed or explicitly
   scoped null actions are observable;
8. **observable outcomes:** execution, allocation, reliability and a declared cost/surplus/contribution response are
   available at the same unit;
9. **licence and retention:** reproducible collection, retention and derived publication are permitted;
10. **common response ladder:** exact mechanics, frozen policy, persistent adaptation and population reallocation
    are separately meaningful and scoreable;
11. **independent governance:** the authority, participants and observation system are independent of GC0166; and
12. **pre-event precision:** historical development data and event metadata support the declared precision without
    opening candidate outcomes.

The null/failure clause is intentionally strict. A public blockchain records successful execution well, but it may
not reveal private intentions or dropped transactions. Uniswap qualifies only if the estimand and denominator can
be defined without pretending that invisible intentions were observed. CoW qualifies only if solver submissions,
filtered solutions, identities and retention are complete enough for the frozen estimand.

## 4. Monitoring without outcome leakage

Inspect both official governance registries once per UTC day. Before activation, the monitor may record only:

- proposal IDs, first-publication time, governance stage and immutable version hashes;
- binding parameters, code/calldata, authority and activation clock;
- action, identity, failure and outcome schemas without target response rows;
- licence, retention, revision rules and expected pre-event sample size; and
- precision diagnostics computed from historical development data.

Do not inspect or compare realized post-change prices, volume, surplus, participation, concentration, execution or
reliability to decide admission or replacement. Governance vote totals needed to establish binding approval are
mechanism metadata; participant-market responses after activation are outcomes. The evidence bundle must preserve
that distinction.

The official governance processes are living documents. Their current forum pages establish public discussion and
binding-vote routes, but each candidate audit must hash the process and executable version actually in force. A
forum label such as “active” or “temperature check” is not itself a binding specification.

## 5. No-replacement and failure semantics

The first qualifying event remains the primary registered event if:

- its observed effect is zero, negative or contrary to the model;
- the preferred model loses;
- data quality is worse than expected;
- participation is sparse; or
- the mechanism is delayed or cancelled after selection.

These are scientific results or protocol failures. They cannot be erased by selecting the next proposal. A later
event may be added only as a separately labelled secondary event while the first remains in the headline record.
If a selected event loses a field that was promised at admission, the loss is reported and the relevant claim is
narrowed or stopped.

## 6. Implication for GC0166 and the paper

The contract creates a credible route to independent replication, but the replication gate remains unresolved
until an actual event passes. It prevents a future on-chain success from being promoted after the fact and makes a
null or failed first attempt publishable evidence about the limits of the prospective protocol.

The most coherent NCS design remains one institutional power-market event plus one permissionless digital-market
event, with a common question about model-capability ordering rather than equal physical effects. If GC0166 cannot
separate participant submissions from system defaults, it becomes a mechanism/state development case; the on-chain
selection contract does not repair that behavioral-identification problem.

For NMI, this event protocol is validation infrastructure, not the method contribution. NMI still requires a new
learning/calibration principle that improves blind intervention forecasts across systems.

## 7. Data and compute state

Current work is metadata-only and runs on Mac CPU. Daily proposal scanning and contract validation require
negligible storage and no GPU. After an event is selected but before activation, limited historical development
shards may be used for a frozen precision simulation under a separate provenance manifest.

The two V100 32 GB workers and RTX2060 remain idle and unqueued. They become relevant only after the complete event
contract passes and the historical model ladder is admitted. No H20 is assumed.

## 8. Reproduction

```bash
conda run -n ecophys python -m ecomd.research.prospective_event_selection \
  data/manifests/onchain_prospective_event_selection_v1.yaml
conda run -n ecophys pytest -q tests/test_prospective_event_selection.py
conda run -n ecophys mypy --strict ecomd/research/prospective_event_selection.py
conda run -n ecophys ruff check \
  ecomd/research/prospective_event_selection.py tests/test_prospective_event_selection.py
```

## 9. Official metadata sources

- [CoW DAO governance process](https://forum.cow.fi/t/cow-dao-governance-process/27)
- [CoW DAO proposal registry](https://forum.cow.fi/c/cow-improvement-proposals-cip/6)
- [CoW Protocol mechanism code](https://github.com/cowprotocol/services)
- [Uniswap community governance process](https://gov.uniswap.org/t/community-governance-process-update-jan-2023/19976)
- [Uniswap governance registry](https://gov.uniswap.org/c/governance-meta/8)
- [Uniswap v4 core code](https://github.com/Uniswap/v4-core)
