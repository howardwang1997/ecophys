# Paper G: portfolio-level strategy review after 31 consecutive zero-card cycles

PRIVATE / INTERNAL — retrospective portfolio review. Not a search cycle, not a
topic, not scientific evidence. 2026-09-16. No new raw questions, primary
literature, forecasts or machine cards are created here.

## Question this review answers

The 2026-09-13 portfolio audit diagnosed Cycles 32–37 and issued a next-search
contract (named alternatives, decisive result, contribution conditional on
perfect data, equal-budget baselines, cheapest applicable truth check). Ten
further cycles (38–47) ran under that contract plus two procedural patches
(Cycle 46: mandatory occupancy check against the full route list; Cycle 47:
asset-first generation with file-level asset verification). The yield stayed at
zero. This review asks which layer is actually binding, using per-program data
from all 31 Paper G cycles, and recommends an allocation.

## Method and accounting

Eight extraction agents (orchestrated workflow, 8/8 completed, 0 errors) read
all 31 cycle memos (Cycle 17 under `ecomd_paper_g_screening_2026-09-08.md`,
Cycles 18–47 under their `ecomd_paper_g_topic_cycle*` memos) and classified
every named program by archetype, outcome, single binding gate, nearest-miss
status, and the memo's own "what would have saved it" item. Aggregation script
and journal are session artifacts; no new literature was opened.

Cross-check against `search_cycle_ledger.yaml`: official raw-question count for
Cycles 17–47 is 107; extraction produced 109 program records. The two
overcounts (Cycle 23: 5 vs 4; Cycle 28: 2 vs 1) are closed follow-up fixtures
counted as separate programs. Spot checks of Cycles 31, 44, 46, 47 against the
ledger and this session's own records match. Limitation: each program carries
one primary gate, so secondary kills (venue appears as a secondary kill inside
several Cycle 46–47 F1 closures) are undercounted in the tables below.

## Aggregate picture

Binding gate by era (share of programs):

| Gate | Market era 17–31 (n=57) | Cross-domain 32–37 (n=26) | Cross-domain 38–47 (n=26) |
|---|---:|---:|---:|
| occupancy_parent | 60% | 54% | 38% |
| none_unresolved (deferred/parked) | 14% | 23% | 23% |
| analytic_non_identifiability | 9% | 15% | 19% |
| data_access | 5% | 0% | 12% |
| truth_contract / design_power / duplicate / other | 12% | 12% | 8% |

Binding gate by archetype (all cycles):

| Archetype | n | Dominant gates |
|---|---:|---|
| theory | 19 | occupancy 17/19, duplicate 1, venue 1 — zero deferred |
| measurement | 41 | occupancy 18, non-identifiability 10, deferred 9 |
| empirical | 39 | occupancy 20, deferred 6, non-identifiability 4 |
| simulator | 8 | deferred 5, occupancy 3 — highest F1-survival rate |

Keyword triage of the 109 "what would have saved it" items: contribution versus
a named capable baseline 51 mentions; assignment/design or dataset/asset access
26 each; independent instrument/truth asset 16; unclassified 22.

Two readings:

1. **The procedural patches work and do not change the yield.** The occupancy
   share fell from 54% to 38% after the F0 occupancy check, and Cycle 47's
   asset-first rule produced zero asset-existence deaths — but the deaths moved
   one gate deeper (non-identifiability and data_access rose), and the number
   of programs surviving to "deferred" did not move (23% flat). The funnel is
   calibrated; the supply region is not responding.
2. **The theory lane is not an escape.** Nineteen theory programs, seventeen
   killed instantly by existing theorems or parent problems, zero deferred.
   Cross-domain theory is even more densely occupied than measurement.

## Near-miss inventory and triage

21 of 109 programs were flagged nearest-miss (deferred past F1, or all hard
gates passed). Triage of their memo-named missing items:

- **Market era (9: G04, G18-08, G19-01, G19-03, G20-03, G21-6, G22-05, G29-01,
  g31).** All nine subsequently resolved to failed_closed at source, rights,
  assignment or contribution gates (linked resolution memos in the ledger
  notes). None is live.
- **Cross-domain 32–37 (6: g32–g37).** All six adjudicated parked by the
  2026-09-13 audit; each blocker is an external-world fact (paired stress
  contracts, acquisition joins, blind family limits, lineage/growth joins,
  particle manifests, few-label cost separation).
- **Cross-domain 38–45 (6: g38, g40, g41, g42, g43, g45).** Missing items
  split into (i) independent reference truth that is in principle computable
  by us (equilibrium reference for g38; reference mixing for g42; DFT/molecular
  reference for g40/g41) but producing it is the research execution itself,
  gated behind activation, and (ii) external data or instrument items (g43
  matched single-input probes; g45 matched public kinetic data with
  within-parent variation) that no search can conjure.

Verdict: **no near-miss has a paper-only conversion path.** Every missing item
is either an external data/instrument fact, an execution-gated demonstration,
or circular (the demonstration is the paper). Fourteen parked questions stay
parked with named blockers; this review does not close or reopen any of them.

## Diagnosis

Three stacked filters explain 31 zero-card cycles: (1) about half of all
generated questions are already answered by someone (occupancy); (2) of the
rest, roughly a third are unidentifiable from the public observation map
(analytic killer toys); (3) every survivor then lacks exactly one of two
things — an independent truth contract, or an increment over a named capable
baseline at equal budget — and those missing items are facts about the world,
not findable ideas. The searched region is "public archived measurement assets
+ solo computation + ICLR/ICML-method contribution". Thirty-one cycles bound
the density of card-qualifying questions in that region at roughly zero:
107 raw programs, 21 near-misses, 0 closable contribution contracts. This is a
statement about this search basis, not about scientific ML opportunities in
general.

## Recommendation

1. **Do not allocate an unconditional Cycle 48.** Two procedure patches in a
   row shifted the death gate without moving the deferred share; the expected
   yield of another harvest under the same basis is empirically near zero and
   the marginal record cost is not.
2. **Conditional resumption paths, in order of substance:**
   - A PI-authorized bounded exploration sandbox for one simulator-archetype
     near-miss (g38 or g42), whose missing "reference truth" is computable.
     This is the only path that converts a parked blocker into screening
     evidence with our own resources. It is currently blocked: the sandbox
     launcher requires the GitHub check to be made required, force pushes
     disabled, and an enforcing launcher reviewed before any execution
     authorization.
   - External data events processed through the existing re-entry ledger
     (176 audits, 0 qualified): SLATE loan-lifecycle publication (2028–29),
     new public deposits carrying the named missing fields, or a
     collaboration offering instrument access (load-resolved ATP counting,
     isogenic paired editing, matched kinetic panels).
3. **If the PI directs that harvesting continue anyway,** the one basis not
   yet tried is truth-construction: start from a documented evaluation flaw
   (several of our own killer toys — significance-label non-identifiability,
   efficiency-mixture confounds, common-mode specification artifacts — are
   such flaws) and construct the repaired benchmark/protocol as the
   contribution. Its two named kill risks are already on record: occupancy by
   the specification-curve/selective-inference parents (Simonsohn 2020 is in
   our own registry) and the benchmark-racing venue shape that closed the
   Cycle 46 lab-pipelining program. Low prior; PI's call, not a
   recommendation.
4. **Redirect:** Paper G effort moves to the live paper tracks (Paper D
   ICLR-2027 P0: abstract by 2026-09-18; the reexploration D0 freeze pinned
   2026-09-19). Paper G search stays paused, not failed: parked questions,
   closures, the route graph and the re-entry machinery are all unchanged.

No closure is broadened, no parked question is terminated, no new gate is
added, and nothing here authorizes implementation, data access, sandbox
execution, outreach or compute.

## Provenance

- Cycle memos: `papers/proposal/ecomd_paper_g_screening_2026-09-08.md` and the
  30 `ecomd_paper_g_topic_cycle18..47` memos.
- Official counts and dispositions: `research/discovery/search_cycle_ledger.yaml`
  (107 raw questions, Cycles 17–47; Paper G 107 formulations / 31 cycles / 0
  cards; validator green 2026-09-15, 1390 evidence records).
- Prior audit: `papers/proposal/ecomd_paper_g_search_portfolio_audit_2026-09-13.md`
  (Cycles 32–37; next-search contract).
- Failure taxonomy: `research/discovery/failure_families.yaml`.
- Extraction workflow journal: session subagents
  `wf_5ae23682-b0f/journal.jsonl` (8 agents, 521k tokens, 0 errors).
