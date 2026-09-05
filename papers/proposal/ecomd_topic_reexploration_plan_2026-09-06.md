# EcoMD topic re-exploration plan (2026-09-06)

Machine decision: `research/discovery/decisions/pi_topic_reexploration_directive_20260906.yaml`
(PI directive: pause A-1, reopen market-simulation/EcoMD topic exploration under scientific
soundness, novelty, data and compute feasibility, with a clear plan).

Status: **screening** (protocol status; literature/source/schema/theorem work only; no outcome
access, no GPU, no execution, no route-level decision).

---

## 1. Why this re-exploration is not cycle 17 of the saturated funnel

The 16 closed cycles plus the 2026-09-04/05 trigger-audit rounds (99 audits, zero qualified)
share one search basis: **discover or validate a market law, which requires an intervention
truth asset** (legally randomized assigned intervention + fully replayable state + independent
same-estimand replication). That asset does not exist in field data, robot populations are
circular for population-response claims, and every generic-method repair was occupied by an
exact parent. Under that basis the funnel is saturated — re-running it would only re-derive
known closures.

The reopened search uses a **changed basis**: the object of study is the **market simulator
itself**, and claims are methodology claims whose ground truth is available **by construction**
(synthetic DGPs, frozen factorials, surgery on locked checkpoints), with at most a
stylized-fact bridge to public data. This is the frame that produced Paper D — the project's
only top-venue-terminal result — and it has never been run over EcoMD's market-native
structure. Concretely, what did not exist at closure time and exists now:

1. **A proven audit apparatus** (prospective freezing, paired-seed factorial cubes, SESOI-graded
   ordered classification, zero-training checkpoint surgery, gauge non-identifiability analysis,
   artifact/verifier machinery) — Paper D, terminal 2026-09-03.
2. **An exact dual-arm matching engine** with arm-invariant tape grammar, replay validator and
   conformance suite (lab-asset-v3, A-2 exit satisfied 2026-09-05) — usable as an experimental
   instrument without any human subject.
3. **A negative-knowledge map** (222 failed routes, 99 audits) that converts most of the
   collision work from search to lookup.

What remains true and is NOT reopened: no claim about real-market response to real
interventions without A-1/A-0 truth; no universal cross-domain claims; no reopening of
failed_closed families.

## 2. Death patterns every candidate must clear (from the 99-audit ledger)

| # | Veto family | One-line statement |
|---|---|---|
| V1 | Exact-parent occupation | A generic-method literature already owns the contribution |
| V2 | Truth-asset absence | The estimand needs assignable-intervention market truth |
| V3 | Circularity | Robot populations instantiate the conclusion by construction |
| V4 | Invariance/gauge twin | Observationally equivalent generative stories both fit |
| V5 | Bundled/contaminated | No clean counterfactual or holdout in the data |
| V6 | Data legality | Needed microstructure truth is restricted or MNAR |
| V7 | Compute envelope | Exceeds 2x V100 32 GB or requires H20/LLM-scale resources |

## 3. Candidate families and pre-screen verdicts

### Family ALPHA (audit-first) — plug-and-play attribution of forcing/clearing layers in market simulators

- **Question.** In autoregressive market simulators, does training through an exact
  mechanism layer (cash/inventory accounting conservation, matching/clearing projection,
  price-tick projection) make that layer constitutive of the learned dynamics — and does the
  bundled "constrained is better" comparison conceal opposite-signed training and deployment
  path credits, as it did for conservation layers in PDE surrogates?
- **Market-native structure that PDEs lack** (the anti-"domain transfer" defense): (i) integer
  units and discrete ticks (lattice projections, not linear subspaces); (ii) combinatorial
  matching rather than rank-one projection; (iii) evaluation against stylized facts rather than
  trajectory error; (iv) reflexive deployment — downstream users (execution/policy simulators)
  adapt to the simulator's outputs.
- **Known veto risks to clear at D-2:** Duruisseaux et al. 2024 and Paper D itself (must be
  cited as the parent whose boundary we extend, not rediscovered); GradABM / Dyer et al. 2023
  differentiable market ABMs (feasibility, not attribution); Gen-DFL / Diff2SP
  decision-focused lane (training-for-decisions, different estimand); the hard-matching
  gradient lane (Lee–Yu–Yang, Parmas–Sugiyama, Potto, StochasticAD/ADEV, EventFBP) — our claim
  is empirical identification/attribution, not gradient estimation through discontinuities;
  simulator-internal mechanism decomposition (Chen 2026; Hashimoto–Izumi 2025).
- **Data.** Synthetic DGPs (existing `ecomd/eval/synthetic_dgps.py`) with known ground truth;
  optional stylized-fact bridge via existing ingests (`lobster_ingest`, `binance_ingest`,
  `yfinance`) — public/free tiers only, no purchase.
- **Compute.** EcoMD-scale models, 30-seed paired factorials — the Paper D precedent (FNO /
  U-Net, 450+270 records) fits 2x V100 comfortably.
- **Preliminary hostile-T0 forecast (un-calibrated heuristic, pre-D-1):** 0.15–0.25.
- **Pre-screen verdict: advance to D-3.**

### Family GAMMA (theory-first) — matching-fiber gauge non-identifiability of matched/cleared training

- **Question.** Let a clearing/matching operator M map intended order flow z to an executable
  tape T = M(z; state). If the training loss observes z only through M(z), the learned raw map
  is identified only modulo the fiber {z' : M(z') = T}. For uniform-price clearing with
  quantities this fiber is a transportation polytope — exponentially large, input-dependent,
  combinatorially structured — a strict generalization of Paper D's rank-one (affine,
  one-dimensional) projection gauge. Theorems to attempt: (1) fiber structure and dimension
  under FIFO vs random-unit priority kernels; (2) surgery-instability: model edits that stay
  inside the fiber (exactly loss-equivalent) can change autoregressive rollout dynamics after
  the gauge is exposed in feedback; (3) what SGD's inductive bias selects within the fiber and
  whether the selection is measurable.
- **Why it may be alive.** The ledger's metaorder-reconstruction audits establish
  tape-to-parent non-identification at the *inference* level (occupied); cycle 7 establishes
  that conserved charges do not fix market transition laws (consistent, different claim — that
  is about market dynamics, this is about what training through M identifies in the model). The
  *training-identification* statement for matching-constrained market simulators has no parent
  we have recorded.
- **Known veto risks to clear at D-2:** transportation-polytope fiber theory (classical math);
  OT layers and differentiation through OT in ML (Cuturi; Blondel et al.); econometric partial
  identification of matching markets (Choo–Siow lineage); set-identification literature; any
  2024–2026 work on gauge freedoms in constrained simulator training.
- **Data / compute.** Theorem work plus synthetic signatures; lab-asset-v3's engine is an exact
  M with a frozen dual-arm grammar — the natural instrument. Compute trivial at screening;
  small at D-1.
- **Preliminary hostile-T0 forecast:** 0.20–0.30 (higher than ALPHA because the claim is
  sharper and the parent risk is narrower, lower venue breadth).
- **Pre-screen verdict: advance to D-3.** ALPHA and GAMMA are complementary (GAMMA is the
  theory core of ALPHA's phenomenon); whether they merge into one paper is a D-3 output.

### Family BETA (secondary, non-primary) — lab-asset-v3 replay-contract artifact

- A reusable replay-contract standard (arm-invariant tape schema + replay validator +
  conformance suite + dual-arm fixtures) for the community. Viable only as a Datasets &
  Benchmarks / artifact track after a science paper needs the instrument, not as the primary
  topic under this directive. Cycle 8 (cross-engine discrepancy) and the KineticSim audit both
  warn that engine-pair equivalence work without a strict theorem is engineering. **Verdict:
  parked pending ALPHA/GAMMA.**

### Pre-killed families (not re-litigated; ledger citations)

| Family | Killed by |
|---|---|
| Market-law discovery from field data | Program-level closure; V2/V6 across all 99 audits |
| Stylized-fact metric invariance audit | FinEvo audit 2026-09-05: generic audit closed, corrections too small |
| Performativity of market simulators | Prior route `performative_dispatch_t0` (2026-08-19); generic performativity occupied |
| Market-physics (FT/energy/Langevin) claims | Plan v3/v4 closure; requires market truth assets |
| Cross-engine law equivalence | Cycle 8 + KineticSim audit; ABIDES–PAMS native clock/RNG contract failure on record |
| LLM-agent market evaluation | FinEvo/RetEvoAct-family occupation recorded in ledger; compute-marginal on V100 — re-screen only if ALPHA survives and shares its instrument |

## 4. Data and compute plan (screening honesty)

- **Screening (D-3/D-2):** paper-only. Zero GPU, zero data access, zero purchase. Literature
  and theorem work.
- **D-1 hostile falsification:** still paper-only (killer-test design, contract checks);
  simulator-lineage contract verification may run CPU-only smoke checks only if explicitly
  recorded as engineering qualification, not evidence.
- **Two independent simulator lineages (activation requirement):** (1) EcoMD v2
  (neural, differentiable, MD-style); (2) lab-asset-v3 engine (event-driven, exact matching,
  dual-arm). A third public lineage (e.g., ABIDES) may be added only after its native
  clock/RNG contract passes — the prior ABIDES–PAMS failure is the recorded warning.
- **D1 execution budget (only after D0 freeze + explicit authorization):** Paper-D-scale —
  paired 30-seed factorials, checkpoint surgery records, ≤ 2 weeks wall-clock on 2x V100.
  Ops prerequisite: V100 disks at 98%/96% must be cleaned before any D1 launch.
- **No dataset purchases.** Public/free tiers only (existing ingest pipes). Crash-event
  reserves stay untouched (data discipline).

## 5. Gate sequence and cycle budget (protocol-compliant)

| Step | Content | Limit / gate |
|---|---|---|
| D-3 (next session) | Question framing for ALPHA and GAMMA: native object, intervention, observable, invariances, nonclaims; merge/split decision | 2 families in, ≤ 2 out |
| D-2 | Searched primary-work manifests (≥ 15 works each), route-graph failure reuse, unresolved-collision lists; explicit adjudication against V1–V7 | A direct unresolved collision kills the family |
| D-1 | Hostile falsification: ≥ 2 killer tests per family, simulator contracts, real bridge qualification, calibrated hostile-T0 forecasts to the forecast ledger | Hostile T0 lower bound ≥ 0.15 to proceed |
| D0 | Outcome-blind freeze (estimand, stop rules, budget, authorized actions) — **only if** the full activation gate passes; requires explicit PI authorization | No card, no GPU before this line |
| Stop | If both families die at D-2/D-1 → close the reframe, record, re-consult PI with evidence | No forced continuation |

## 6. What this plan does not change

- A-1 is paused, not failed; its frozen assets (thesis v2, C2 fork, C4-v2 precision contract,
  lab-asset-v3, ethics draft) remain intact and reopenable by a new PI decision.
- verification_liquidity holdout sealed until 2026-10-17 UTC.
- Paper D is terminal; ICLR 2027 submission execution continues on its own track (P0).
- All failed_closed families stay closed; provenance is append-only.
