# Plan v13 — Prospective mechanism changes in real algorithmic-agent markets

**Frozen:** 2026-08-13

**Branch:** `prospective-agent-market-mechanism-scout-v13`

**Base:** `main@4705e3f7a`

**Initial state:** `METADATA_AND_IDENTIFICATION_AUDIT`; no auction outcome, bid value, market record, generated
sample, remote worker or GPU is authorized before the gates in Sections 6--8 are closed in order

## 1. Why V13 exists

V11--V12 produced correct inverse-problem mathematics but no NMI method or NCS scientific mechanism. The deeper
failure is the research object: passive stationary aggregate distributions leave hidden dynamics underidentified,
and simulator-internal transients cannot establish market physics.

V13 changes the object while keeping the venue ambition fixed. It studies real repeated markets in which
algorithmic agents take event-time actions under an executable rule and the rule changes at a publicly specified
time. The intended evidence is prospective, identity-aware and mechanism-grounded rather than an ex-post search
over stylized facts.

The leading scout is Ethereum's possible transition from relay-mediated MEV-Boost auctions to enshrined
proposer--builder separation under EIP-7732. A future CoW Protocol solver-rule change is only a candidate
independent replication. Neither system is admitted at freeze: the protocol clock, common observables, identity
continuity, coverage and replication cells may remain empty.

This document is a topic-selection protocol, not yet a replacement for `plan_v4_ncs.md`. Plan v4 remains the
archival plan of record until V13 passes its scientific-admission gates. Historical EcoMD and workshop artifacts
remain separate and cannot be promoted as evidence for V13.

## 2. Scientific question and signed hypotheses

The question is:

> When an algorithmic market removes or changes an intermediary mechanism, which rents disappear mechanically,
> which strategic advantages persist through agent adaptation, and can allocative efficiency improve without
> proportional deconcentration?

For the MEV-Boost/ePBS scout, the frozen hypotheses are directional but conditional on observability:

- **H1 latency attenuation:** among persistent operational builder identities and comparable auction
  opportunities, the conditional association between action arrival time and winning weakens after relay
  intermediation is removed or materially altered.
- **H2 information persistence:** an independently observable exclusive-order-flow or information-advantage proxy
  retains a positive conditional association with winning and surplus after the change. If no defensible
  pre-specified proxy exists, H2 is retired rather than estimated from an inferred latent label.
- **H3 efficiency--concentration decoupling:** an improvement in a preregistered efficiency measure need not imply
  a proportional fall in builder/solver concentration, entry barriers or persistent-identity market share.

These hypotheses are not facts, universal laws or claims that public keys identify firms. A null, reversal or
partial result is publishable only if the design is prospectively sealed and the observability contract is met.

## 3. Multiscale mechanism-to-population object

For system `s`, regime `r`, event `t` and operational identity `i`, let

\[
 a_{ist}\sim\pi_{is}^{(r)}(\cdot\mid x_{st},h_{ist}),
 \qquad
 y_{st}=\Phi_s\!\left(M_s^{(r)},\mathcal A_{st},x_{st}\right),
\]

where `M` is the versioned executable allocation/payment rule, `A` is the observed admissible action set, `x` is
the public opportunity state and `pi` is an identity-conditioned behavioral policy. Population weights and the
active identity set form a third layer.

For a regime contrast, the analysis must separate:

1. **mechanical rule effect:** replay the same admissible action set under two exact mechanisms;
2. **within-identity response:** change in the observable policy of identities present on both sides;
3. **between-identity reweighting:** changing opportunity or market-share weights among persistent identities;
4. **entry/exit composition:** identities entering, leaving or changing observable aliases.

Any aggregate decomposition is order-dependent unless a path or Shapley convention is frozen. That convention is
descriptive accounting, not method novelty. A learned event-layer policy may enter only after exact-mechanism and
fixed-strategy baselines; it never replaces the rule engine.

“Learning” is not identified merely because actions change. The primary estimand is observable strategy response.
A learning claim additionally requires repeated within-identity adaptation that rejects a frozen hidden-strategy
and changing-opportunity oracle.

## 4. Intended contributions and non-claims

### Conditional NCS contribution

- A prospectively registered mechanism-transition study with exact rule replay, persistent operational identities,
  full coverage diagnostics and untouched confirmation.
- A replicated finding about the separation of latency, information and concentration channels across at least
  two independently governed algorithmic-agent markets.
- A multiscale empirical bridge from executable micro rules through within-agent response to population
  composition, with uncertainty and missingness propagated at every layer.

### Conditional NMI contribution

NMI is opened only if fragmented/censored auction panels require a genuinely non-equivalent estimator or theorem,
such as a partial-identification result with informative sharp bounds under known relay/API selection or a method
that transports exact-mechanism counterfactuals across a changing observation interface. Ordinary event studies,
panel fixed effects, Oaxaca/Kitagawa/Shapley decompositions, survival models, structural auction estimation or
sequence models are mandatory baselines, not novelty.

### Fixed non-claims

- Public keys, relay labels and solver names are operational identities, not guaranteed firms, humans or common
  economic owners.
- Missing bids are not losing bids, and one relay's feed is not the global auction without a coverage proof.
- A protocol fork is not random treatment. Causal language requires a declared estimand, interference model,
  opportunity controls and falsification tests.
- Better winning bids do not by themselves establish welfare, decentralization or social efficiency.
- Blockchain observability does not make private order flow observable.
- EcoMD may later serve as a controlled ablation environment, but it is neither the mechanism ground truth nor
  the real-system confirmation.

## 5. Work packages

| Work package | Required work | Output | Stop condition |
|---|---|---|---|
| WP0 chronology | Verify official mechanism specification, governance status, activation rule, schema versioning and rollback/fork contingencies. | Immutable protocol-clock manifest. | No finalized material transition or no sealable date. |
| WP1 observation contract | Enumerate received/submitted/winning actions, timestamps, payments, opportunity state, missingness, relay/API coverage and licences before values. | Versioned field-level data contract and synthetic schema fixtures. | Pre/post actions cannot be mapped to a common estimand. |
| WP2 identity contract | Define time-indexed public-key/solver aliases, ambiguity sets, split/merge rules and minimum persistence. | Identity graph with uncertainty, never a firm ontology. | H1 cannot be tested under any defensible identity coarsening. |
| WP3 prior-art attack | Compare the exact hypotheses with MEV-Boost latency/private-flow/concentration studies, ePBS theory, auction-transition designs and algorithmic-market adaptation work. | Claim-by-source matrix and human-audit packet. | The joint claim is a direct restatement or only a dataset update. |
| WP4 estimand and negative controls | Freeze event time, units, exposure, interference, exact replay, opportunity matching, placebo forks, fake cutoffs, coverage shifts and fixed hidden-strategy oracle. | Estimand card plus generated power/identification preflight. | Signed channels are not identifiable under declared missingness. |
| WP5 development replay | Use only a named historical development period to validate parsers, mechanism replay and baselines. | Reproducible development report; no headline claims. | Rule replay or coverage calibration fails. |
| WP6 prospective confirmation | Hash and embargo a future transition window; run once after completeness checks, including all preregistered nulls. | Untouched primary confirmation. | The transition changes definition or the sealed panel is incomplete. |
| WP7 independent replication | Repeat the same channel-level claim in a separately governed system with its own exact rule and agent identities. | Cross-system replication report. | No second system is sealed before primary outcomes. |
| WP8 multiscale model | Fit exact-rule plus identity-policy plus population model only after simpler oracles; test transfer and counterfactual calibration. | Model, ablations and uncertainty decomposition. | Learned layer does not beat fixed-strategy/mechanism baselines out of time. |

## 6. Sequential admission gates

### G0 — protocol finality

- Identify a first-party specification, governance state and executable activation condition.
- Record whether ePBS remains draft, scheduled, activated, delayed, superseded or split across clients.
- **Kill:** no prospective causal transition if the mechanism or activation is not stable enough to freeze.

### G1 — common-observable support

- Define a common pre/post action, outcome and opportunity space without using outcome values.
- Prove which bid streams are complete, duplicated or selectively reported; distinguish received, delivered and
  winning traces.
- **Kill:** no H1/H3 if a coverage-sensitive statistic cannot be bounded; no H2 without a direct proxy contract.

### G2 — identity and selection

- Freeze alias evidence and report every result over at least three defensible coarsenings: raw key, public label
  and ambiguity-set bounds.
- Model relay/API selection and post-transition visibility changes explicitly.
- **Kill:** no adaptation claim if key rotation, mergers or missingness can reproduce the effect.

### G3 — novelty

- Audit exact neighboring results on latency games, private order flow, builder concentration, strategic bidding,
  ePBS design and natural experiments in solver rewards.
- **Kill:** retire NCS if only a new date or larger sample remains; retire NMI if the method is a standard
  composition.

### G4 — identification and prospective seal

- Predefine the event window, untouched units, exclusion rules, estimators, signed hypotheses, multiple-testing
  family and negative controls.
- Demonstrate identification and power on generated data using metadata-supported missingness and effect scales,
  not favorable arbitrary sweeps.
- **Kill:** no outcome access if type-I error, power or fixed-strategy falsification gates fail.

### G5 — independent replication

- Seal a second independently governed algorithmic-agent market and common mechanism channel before viewing the
  first transition's confirmation outcome.
- **Kill:** one Ethereum fork alone cannot support the intended NCS general claim.

## 7. Data requirements

| Tier | Data | Minimum fields and provenance | Admission condition |
|---|---|---|---|
| T0 current | First-party specifications, governance records, API schemas, licence/retention statements and publication metadata; no outcome values. | URL/version/hash/retrieval time, field definitions, clock semantics and known coverage. | Frozen plan only. |
| T1 free development | Public historical relay bid traces, beacon/execution blocks, relay coverage, builder labels and mechanism versions; or analogous solver data. | Event/slot, receive time, bid/action, operational key, rule version, winning/delivery status, public opportunity state and source-level missingness. | G0--G3 pass and a separate development preregistration. |
| T2 free prospective | Immutable complete pre/post transition mirror with a sealed untouched period. | T1 plus reorg/rollback flags, schema migration, client/relay participation and cross-source checksums. | G4 pass; collection may begin before analysis. |
| T3 independent system | Separately governed repeated auction or allocation market with exact rule change, persistent agent IDs and prospectively sealed repeated actions. | A defensible common latency/information/composition channel, even if field names differ. | G5 contract frozen before primary outcome. |
| T4 optional expansion | Paid/private comprehensive feeds, private-order-flow tags, additional chains/markets and longer panels. | Licence permits research, reproducible derived artifacts and auditable selection process. | Only after free feasibility shows that added data resolve a named bottleneck. |

Current data are a starting tier, not a ceiling. Future acquisition may span vendors, relays, chains, exchanges,
periods and modalities, but no purchase is justified until it changes a failed gate. Crash or exceptional periods
remain held out from tuning.

## 8. Compute requirements and worker policy

| Stage | CPU | GPU | Worker policy |
|---|---:|---:|---|
| T0 metadata/prior art | `<=30` core-hours | `0` | Mac only; do not contact workers. |
| Schema/replay smoke | `<=300` core-hours | `0--10` V100-equivalent hours | Mac first; RTX2060 or V100 nodes may run CPU jobs after preregistration. |
| Generated identification preflight | `500--5,000` core-hours | `0--100` V100-equivalent hours | Two current V100 32 GB nodes for independent seeds only if G0--G3 pass; RTX2060 for smoke. |
| Historical development | `2,000--20,000` core-hours | `50--1,000` V100-equivalent hours | Exact replay and panel baselines are CPU-first; learned policies use isolated canonical V100 jobs. |
| Prospective plus replication | `10,000--150,000` core-hours | `500--10,000` V100-equivalent hours | Capacity may expand to more non-H20 CPU/GPU workers after V100 equivalence benchmarks. |

The current floor is two V100 32 GB workers at `100.80.236.112` and `100.123.220.57`, plus the RTX2060 worker at
`100.105.21.7`. They remain idle at freeze. H20 is excluded from all present and future capacity assumptions.
Independent market/seed arrays are preferred to distributed training. More compute cannot repair missing bids,
mutable mechanisms, identity ambiguity, prior-art equivalence or absent replication.

## 9. First zero-cost execution

Before any values or workers, V13 authorizes only:

1. first-party protocol, schema, licence and chronology verification;
2. equation-level estimand and missingness analysis;
3. direct primary-paper prior-art audit;
4. a search for an independently governed second mechanism transition; and
5. deterministic validators over hand-written schema examples, but only after a separate experiment manifest if
   nontrivial code is needed.

No endpoint may be queried in a way that returns bids, prices, allocations, rewards, transaction outcomes or
market shares during this stage. Field names and static example payloads in documentation are metadata.

## 10. Venue and decision rules

- **NCS primary route:** requires prospective untouched confirmation, exact-mechanism grounding, channel-level
  scientific interpretation, strong fixed-strategy/coverage controls and an independent real-system replication.
- **NMI conditional route:** requires a non-equivalent estimator/theorem for changing-interface, fragmented or
  censored agent-auction panels, plus broad synthetic and cross-system validation.
- **Neither:** if only a conventional event study of one blockchain transition survives, report the design lesson
  internally and do not inflate it into a flagship claim.

Pre-audit flagship probability remains low: approximately `5--12%` for an NCS-worthy prospective program and
`2--6%` for a distinct NMI method. The object is stronger than passive simulator diagnostics, but execution risk
is high because the mechanism date, observability and independent replication are not yet secured.

## 11. Chronology

1. Commit and push this metadata-only plan before additional outcome-bearing endpoint access or formal candidate
   fitting.
2. Close G0--G3 using primary sources and append-only claim ledgers.
3. Close as `V13_NO_TRANSITION`, `V13_NO_COMMON_OBSERVABLE`, `V13_NO_IDENTITY`,
   `V13_NO_SURVIVOR_PRIOR_ART`, `V13_NO_REPLICATION`, `V13_WAIT_PROSPECTIVE` or
   `V13_READY_FOR_PREREGISTRATION`.
4. Only the last two states may define a data collector; only `READY_FOR_PREREGISTRATION` may open a generated
   identification experiment after a second freeze commit.
5. Synchronize the knowledge graph, candidate/failure ledgers, research lineage, durable memory and dated log
   before any integration into `main`.
