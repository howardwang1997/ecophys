# Frozen A-3 truth-asset capability-build plan: prospective controlled-market response asset

Date: 2026-08-26 (Session 16)

Status: **paper-only infrastructure preflight; no topic status, no route status, no authorization**

This document freezes the design contract required by
`research/discovery/protocol.yaml` (`topic_search_funnel.capability_build_policy.required_contract_parts`)
for the reusable truth-asset preflight retained by
`ecomd_discovery_bottleneck_truth_asset_preflight_2026-08-26.md`. Per the machine policy:
this plan cannot authorize candidate harvesting, participant work, outreach, implementation,
outcome access, sandbox use, or compute. Re-entry into a topic cycle still requires a separately
qualified append-only entry in `research/discovery/reentry_trigger_ledger.yaml`.

## 0. Stage boundary

Everything in this plan is **A-3 paper-only design**. The stage ladder from the preflight is
unchanged: A-2 (implement/modify a platform, conformance runs, synthetic pilots), A-1 (site
contact, recruitment quotes, ethics filing, registration), and A0 (outcomes, participant markets,
simulator fitting, confirmation opening) all remain unauthorized.

## Part 1 — Named blocker and blocked estimand family

**Recorded blockers.** The terminal failure families `causal_field_contract_missing`,
`two_system_contract_missing`, and `cross_system_estimand_mismatch` closed, among others:

- `prospective_counterfactual_market_simulator_validity` (Cycle 16): no prospectively sealed
  real rule intervention with complete state, lawful reuse, and a deterministic common simulator
  action existed.
- `cross_simulator_disagreement_intervention_certificate` (Cycle 8): no two engines shared one
  complete checkpoint, clock, action, policy-information, and semantic-randomness contract with an
  external adjudicator.
- `interventional_lob_fidelity_benchmark`: no assigned interventional response truth distinct
  from passive path fitting.

Every audit since Cycle 5 terminated on the same absence: a lawful, prospectively assigned
response with replay-complete state. Idea generation is not the constraint
(84 raw programs, 187 primary sources, 59 killer toys, zero cards in Cycles 10–16).

**What the asset would adjudicate.** One bounded estimand family: the conditional path response
of an interacting laboratory market population to an externally assigned exchange-rule change —
prespecified session-level path statistics (mid-price response over fixed horizons, spread and
depth distributions, realized impact of aggressive orders, cancel/replace rates, volume and
volatility) contrasted across randomized rule arms. The unoccupied scientific use, per the Cycle
16 gap audit: prospectively test whether a frozen simulator fitted on passive paths predicts a
held-out assigned response of independently generated human markets
([Dyer et al. 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/26b8e3dc3a21fcd660d80c63b767f324-Abstract-Conference.html)
occupy simulator-to-simulator interventional consistency, not human-market response).

**Explicit non-goals.** No field-transfer claim (a laboratory assignment identifies treatment
effects in its controlled population only); no latent-intention, parent-order, or unsubmitted-
demand estimands (blocked by Cycles 5–6 and not repairable by any laboratory instrument); no
"which institution is better" claim (occupied).

## Part 2 — Supported estimand family (frozen)

Primary estimand: for rule arms `a ∈ {control, treatment}`, the arm-conditional law of the
session path summary vector

```
Y(session) = (impact-response slope over horizons h ∈ {1s, 10s, 60s},
              time-weighted spread, mean resting depth within k ticks,
              cancel/replace intensity, volume-volatility covariance)
```

estimated over independent sessions, with the contrast `E[Y | treatment] − E[Y | control]` and
its session-clustered uncertainty. Secondary estimands: quantiles and tails of the same
statistics; per-horizon impulse-response paths. All statistics are computed from the released
event tape by a frozen analysis script; no questionnaire, belief, or post-session self-report
measure is part of the truth asset (those may exist for the host experiment's own purposes but
are not the asset).

Frozen exclusions: any estimand requiring unobservable private state (intentions, valuations
beyond induced values), any cross-session interference assumption beyond the pool-cohort
stratification below, and any claim about venues outside the two laboratory sites.

## Part 3 — Assignment and interference

- **Unit of assignment:** one independent market session (one limit-order book, one participant
  cohort of 8–12 induced-value traders, one fixed duration or termination rule).
- **Interference cluster:** the session. Participants interact only within their session; no
  participant appears in two sessions of the same wave; SUTVA holds at session level by
  construction.
- **Assignment mechanism:** between-session randomized assignment, stratified by (participant
  pool cohort, calendar block). No within-session rule switching in the primary design (carryover
  would corrupt path-law estimation). Assignment key generated by a pinned offline procedure,
  sealed at generation, released only with the raw tape.
- **Support requirement:** an arm is admissible only if the outcome-blind precision calculation
  (Part 8) supports it; if power is insufficient for the primary contrast, the design collapses
  to two arms regardless of scientific preference.
- **Timing:** rule active for the entire session from the first matching tick; pre-period is the
  instruction and practice phase under the same rule (no within-wave rule change).

## Part 4 — Event lifecycle and replay prestate (schema-freeze requirements)

The released tape must contain, per event, building on the schema seeds audited in
`truth_asset_domidt_cda_repository` (modern oTree 6 tables) and
`truth_asset_leeps_hft_repository` (OUCH-style tokens and replacement ancestry):

1. immutable identifiers: `request_id`, `order_id`, replacement/parent chain IDs, `execution_id`,
   `rejection_id`, pseudonymous `actor_id`, `session_id`, `role`;
2. full lifecycle: client decision timestamp, server receipt timestamp, matching timestamp;
   price, original/executed/residual quantity; maker/taker flags; **reason-coded rejections**
   (price limit, crossed, cancelled-too-late, malformed), not free-text messages;
3. pre/post state: best bid/ask before and after each accepted action, plus a full-book state
   hash per accepted action;
4. replay prestate: initial cash and inventory endowments, induced-value parameter draws,
   information release schedule, initial book, rule configuration, scheduler and platform RNG
   state, and the assignment key;
5. deterministic replay check: an independent re-execution of the released tape under the
   released configuration must reproduce every state hash exactly; the replay fixture is part of
   the release and its failure voids the asset.

The exact schema is frozen as a versioned artifact at A-2 exit, before any human session.

## Part 5 — Rights, ethics, and release

- Ethics approval at each site before any recruitment (A-1 gate).
- Consent must explicitly cover: open publication of the pseudonymized full event tape,
  derived-data construction, redistribution, and reuse; withdrawal must be honored by full
  session exclusion (a withdrawn session leaves the discovery partition entirely and is reported
  as attrition, not deleted selectively).
- Software: the hardened platform fork and analysis scripts under a permissive licence with
  pinned container image, dependency lock, config hashes, and seed derivation published.
- De-identification: pseudonymous actor IDs with a published mapping-retention policy; no
  free-text participant input is part of the tape.
- Release: one dated raw release per site after Part 6 unsealing, under a data-use licence no
  more restrictive than CC-BY-4.0 for the event tape.

## Part 6 — Untouched confirmation partition

- **Discovery site:** the first site's full wave (all sessions, both arms, whole source).
- **Confirmation site:** an independently governed team running the identical frozen package
  (same schema, same conformance fixtures, same rule arms) on a separate participant pool.
- **Sealing:** the confirmation-site raw tape remains inaccessible to everyone — including this
  project — until the simulator(s) and analysis plans are frozen and time-stamped on the
  discovery partition alone. Registered-report-style time-stamping; no preview, no interim
  aggregate, no shape peeking.
- Confirmation unsealing is an explicit user-authorized machine decision recorded in the
  discovery decision history, not an automatic step.

## Part 7 — Independent replication

- Two sites with separate governance (institutions, ethics boards, participant pools, operators).
- Equivalence contract: both sites run the same frozen package and pass the same deterministic
  replay and schema-conformance fixtures before their first human session; fixture results are
  published per site.
- Two code branches of one researcher-built lineage do not qualify (recorded in the preflight);
  the confirmation site must adopt the frozen artifact, not a re-implementation of it.
- A site pair qualifies only if assignment, tape schema, and analysis grammar are byte-identical
  in the frozen artifacts; any drift voids the replication label for the drifted fields.

## Part 8 — Cost, power, operational failure modes, and stop rules

**Paper-only cost skeleton** (no quotes sought; that is A-1): platform hardening and conformance
engineering (largest item; weeks of engineering), participant payments (8–12 paid participants ×
20–40 sessions/site at standard per-participant show-up plus performance payments), operator
time per session, ethics filing, and confirmation-site coordination. Ranges, not quotes, are
frozen now; the plan stops if the A-1 quotes exceed the ceiling set by the user at that stage.

**Outcome-blind precision rule:** session counts per arm are fixed before any outcome from the
pilot-free variance floor — using published laboratory market session variability from the
occupied institution comparisons (e.g., [Aldrich and López Vargas 2019](https://doi.org/10.1007/s10683-019-09605-2);
[Guler et al. 2025](https://doi.org/10.1016/j.euroecorev.2025.105148)) for noise calibration
only, never for effect directions. Any design whose primary contrast cannot reach a
preregistered minimal detectable effect at the affordable session count stops.

**Operational failure modes with pre-declared handling:** thin/empty book in a session
(announced minimum activity per session with make-whole payments; excluded only by the frozen
rule, never post hoc), attrition (whole-session exclusion + report), platform incident during a
session (session voided by frozen rule; incident log published), instruction non-comprehension
(frozen comprehension check; failure excludes the session), and data-corruption (state-hash
mismatch voids the session).

**Exact stop conditions** (each terminal for the asset build, recorded in the decision history):

1. platform conformance or deterministic replay fails after two engineering iterations at A-2;
2. ethics or lawful-release contract fails at any site;
3. precision calculation requires a session budget above the user-frozen ceiling;
4. no independently governed confirmation site commits in writing by the A-1 deadline;
5. treatment selection (below) ends with zero non-occupied candidate treatments.

## Treatment selection: deferred, procedure frozen

The treatment is **not** selected here. Selection happens in a separate bounded outcome-blind
prior audit with these frozen disqualifiers:

- direct prior collision: a human-subject same-estimand comparison already exists — currently
  disqualifying families: continuous vs frequent batch
  ([Aldrich and López Vargas 2019](https://doi.org/10.1007/s10683-019-09605-2)), double auction
  vs call market vs tâtonnement ([Guler et al. 2025](https://doi.org/10.1016/j.euroecorev.2025.105148));
- assignment impossibility in a CDA grammar, or a treatment that changes the event schema
  between arms (the tape grammar must be arm-invariant);
- no discriminating simulator fork: at least two serious simulator families must predict opposite
  signs or order-one different magnitudes for the primary contrast.

Candidate families entering that audit (each still subject to its own collision search):
equal-price queue-priority rule (FIFO vs pro-rata vs randomized tie-break), cancellation/replace
cost schedule, resting-depth visibility (displayed vs hidden own-side depth), minimum resting
time, and order-size unitization. Several have adjacent field or theory literatures (e.g.,
priority rules in futures design, quote-life speed bumps); adjacency is not collision, but a
same-estimand human-subject prior is.

## Decision

This plan is retained as the frozen A-3 contract for the controlled-market response asset. It
creates no topic card, no route status, no forecast, no sandbox, and no re-entry authorization.
`candidate_harvest_authorized` remains `false` in every trigger-ledger entry. The next legal
actions, each requiring explicit user authorization, are: (a) the bounded outcome-blind
treatment-selection audit (still A-3, paper-only), or (b) A-2 platform qualification. A topic
cycle remains closed until a qualified trigger exists.

No participant experiment, outreach, implementation, simulator execution, outcome access, data
purchase, EcoMD change, sandbox, CPU experiment, or GPU work is authorized by this document.
