---
document: Paper F concept note — recording design + floor-relative simulator validation
authored: 2026-09-08
status: CONCEPT NOTE ONLY — not a topic card, not activated, no route/card authorization
  implied or created; recorded so the discussion is not lost and so the re-audit
  conditions are explicit
provenance: PI discussion 2026-09-08 (Paper E direction review → "does it guide better
  simulators?" → "merge the two parts into one paper?"). Recorded by the session agent
  same day.
hostile_t0_assessment: ~0.10–0.14 — BELOW the 0.15 activation floor; no card may be
  created from this note under research/discovery/protocol.yaml without a fresh
  activation-gate audit
---

# Paper F (working name): Recording Design for Market Simulators — floor-relative validation

## 1. Context and the two decisions recorded here

Paper E (matching-fiber non-identifiability theorems + preregistered attribution cube) is
the frozen-candidate GAMMA-led paper; its preregistration is complete and its campaign is
compute-gated on D0. The 2026-09-08 discussion surfaced the natural follow-up: E's theory
says the ONLY floor-moving repair is information-side (change what is recorded, not what
learns). Two decisions:

**Decision 1 — do NOT merge into Paper E.** E's frozen prereg forbids superiority claims
outright (contract C3: "No confirmatory test compares through-M vs raw for superiority;
the estimand is path-dependence attribution"). Merging a "better simulator" claim would
void the panel-verified prereg, force a re-panel, and delay D0 — for a result that can be
had three months later by sequencing. The two-paper arc:

- **Paper E (now)**: boundary and map — where the blindness is, how large, what is safe,
  how to read the exposure table. Theory + attribution campaign.
- **Paper F (after E's campaign)**: repair and validation — recording design lowers the
  floor; a simulator trained on the richer recording measurably approaches the NEW floor;
  no improvement leaks into provably-blind directions.

E's outputs are F's inputs: floor formulas (objective function), attribution results
(motivating evidence), engine/corpus/cube machinery (reused wholesale).

**Decision 2 (PENDING PI CHOICE, not yet made) — Paper E title.** The PI judged the title
clause "with a Preregistered Attribution Design" to be process language, not science
(preregistration is governance, belongs in abstract/methods/Appendix C; in a title it also
advertises "no results yet"). Options on the table, none applied:

| Option | Title | Note |
|---|---|---|
| A (recommended by session) | The Aggregate Tape Is Not Sufficient: Matching-Fiber Non-Identifiability in Market Clearing | drop the third clause entirely |
| B | The Aggregate Tape Is Not Sufficient: Consumer Floors and Deployment Exposed Sets in Market Clearing | replace process language with the positive objects |
| C | What Can a Market Simulator Learn from the Aggregate Tape? | question form (intro-writer fallback) |

A title change pre-freeze is a lawful one-line manuscript edit (D1_16 scope); it must be
PI-chosen and then applied with an abstract first-sentence alignment.

## 2. The scientific content of Paper F

### 2.1 What "better" means (the definitional move)

"Better" is DEFINED as *distance to the computable information floor of the recording
contract* — not stylized-facts fit (fit ≠ counterfactual validity; killed repeatedly in
this program's audits), not in-sample metrics, and not real-market comparison (protocol-
sealed: no market-data access; verification_liquidity holdout until 2026-10-17 UTC). This
definition is engine-checkable, falsifiable, and requires no external truth beyond the
recording itself, because the floor is a theorem (S3 exact-arithmetic/enumeration
machine-checkable), not an engine opinion.

### 2.2 The validation battery (V1–V4)

| Layer | Validates | Design | Why it is clean |
|---|---|---|---|
| V1 floor attainment | simulator error hugs its own floor | consumers × recording contracts × lineages; RMSE vs precomputed floor | floor is a theorem; no external ground truth needed |
| V2 recording A/B | richer recording R2 actually beats R1 | SAME architecture, SAME seeds, paired training on R1 vs R2 corpora; theory predicts improvement ONLY on directions R2 newly records | improvement on un-recorded directions = information-leak alarm (lookahead audit fires) |
| V3 deployment generalization | improvement transports to deployment changes | evaluate on exposed-set deployment maps (swap→ru, truncation windows); **provably-blind maps (Exp=∅) are the placebo arm — a true improvement MUST show zero difference there** | the improvement claim carries a built-in negative control |
| V4 axis transport | local vs general improvement | reuse E's cube axes (population-2N, tick-2Δ, kernel-swap) | E's machinery reused directly |

**The placebo arm is the distinctive methodological piece.** No parent template has a
point-null slot for improvement claims (E's own KT-M2 expressibility table row R5): the
provably-blind deployment maps give "our simulator is better" something no simulator-
validation paper has — an internal control group.

### 2.3 What F reuses vs builds

- REUSES from E: lab-asset engine + conformance suite; E-1 F_exec corpus projector; the
  eight-cell cube and its axes; seed/namespace discipline; the floor theorems and exposed-
  set tables; the paired-bootstrap/SESOI statistical contract patterns.
- BUILDS new: the fine-recording corpus arm (F_exec+orders / F_full generators — note the
  E prereg REJECTED F_full for E's own purposes (D1_01: fibers collapse), which is exactly
  why it is the repair arm for F); the recording-schema design space (which fields to add
  per consumer class); V2/V3 analyzers. CPU-first; GPU only if a campaign is later
  authorized.

## 3. Honest hostile-T0 assessment (why no card now)

Estimate ~0.10–0.14, BELOW the 0.15 activation floor. Main deductions:

1. **Self-grading circularity**: "your engine, your floor, your grade." Mitigations: floor
   is an engine-independent theorem (machine-checked); engine is the frozen A-2
   conformance-tested artifact; improvement is relative to a mathematical bound, not
   engine self-report. A hostile reviewer can still say real-market validity is unproven —
   and that line stays sealed (deliberate nonclaim).
2. **Positive-claim shape**: "X% closer to floor" reads as engineering unless V3 + placebo
   arm carry it; without them it is just another simulator paper.
3. Re-audit triggers (any may lift the estimate above floor): (a) E's campaign complete —
   attribution results become motivating evidence and the cube infrastructure is proven;
   (b) V2 fine-recording generator built and floor-drop demonstrated on one consumer class
   (theorem-level, CPU, no GPU); (c) an external recording-schema anchor appears (e.g., a
   public venue documenting its exact recorded fields, giving a non-self-graded arm).

## 4. Standing constraints (unchanged by this note)

No GPU before D0 freeze; no confirmatory execution; no market-data access or purchase;
verification_liquidity sealed until 2026-10-17 UTC; Paper D terminal; no topic-card
creation without the full activation gate; K=16 immutable; prereg v2 remains the freeze
candidate. This note creates no authorization, no compute claim, and no precedence — it
is a record of a direction and its re-audit conditions.

## 5. Sequencing

1. Now → D0: freeze-date PI decision (A/B1/B2 per
   `ecomd_reexploration_d0_calendar_proposal_2026-09-08.md`); build items 8–10 (analyzer
   contract, cleanup scripts, reflexive impl); regression battery green.
2. D0 → campaign end: E executes exactly as preregistered. F does not exist operationally.
3. Post-campaign: E outcome writing (D2); re-audit F against §3 triggers; only then a
   topic-card decision.
