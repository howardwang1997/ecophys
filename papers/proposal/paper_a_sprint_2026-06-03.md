# Paper A — 10-Day Result Sprint (2026-06-03 → 2026-06-13)

**Hard goal:** produce the experimental results that lift Paper A from "borderline findings paper"
to **NeurIPS/ICML-main shape**, within the 10-day large-scale H20 window.

**The four levers (from the 2026-06-03 strategy pass):**
1. **Cross-asset universality** of the concave √-impact solve (exp 114, running).
2. **Beat net SOTA (5.96)** via mechanism **composition** (concave + SV) — exp 115.
3. **The "method" claim** = ≥2 mechanisms recovered/composed (concave δ→0.5 already; SV as the
   pragmatic 2nd; leverage-recovery as the clean stretch demonstrator) — exp 115 (+117 stretch).
4. **Failure-mode frontier figure** (three-paradigm Pareto) — ABIDES fair re-run (CPU, free).
   Plus **mechanistic depth**: the criticality probe (exp 116) — why tails overshoot (also the Paper B fork).

Discipline (binding): champion confirmed at **5-asset n=30 (no best-of-N)**, Welch+Bonferroni vs
baseline AND vs SOTA; smoke up to 3 fail-rounds autonomously; **H20 not accessible from Claude**
(hand off launch commands); dated logs + memory each session.

---

## Compute budget — compute is NOT the binding constraint

8×H20, ~62 min/config/card, 8 cards = 8 configs/wave. 10 days ≈ 1900 card-hours ≈ ~1500 configs
at realistic utilization. Planned GPU work ≈ **~5 GPU-days**, leaving ~5 days of slack for
dev→smoke→score→iterate loops and fail-loops. **The binding constraint is dev throughput + the
sequential "see results before designing the next" dependency** — so experiments are front-loaded
and built launch-ready NOW to minimize idle H20.

| exp | what | configs | GPU time |
|---|---|---:|---:|
| 114 (running) | 5-asset universality of concave δ=0.5 | 390 | ~50h (2.1d) |
| 115 composition | baseline / concave / SV / **concave+SV** / ablation, SPX n=30 | 150 | ~19h (0.8d) |
| 116 criticality | κ-sweep + finite-size scaling, **pure inference** | ~80 | ~3h |
| 117 leverage (stretch) | learnable leverage coupling, recover empirical leverage | 150 | ~19h (0.8d) |
| champion confirm | winner + baseline × 5 assets n=30 | ~150 | ~19h (0.8d) |
| ABIDES (CPU) | timescale-fair re-run for the frontier figure | — | 0 GPU |

---

## Day-by-day

**Day 1 (today, 06-03)** — 114 running.
- DEV: build **115 composition** + **116 criticality** generators/launchers/scorers; smoke on Mac. ✅ this session
- CPU: kick off ABIDES timescale-fix + re-run (no GPU; parallel to everything).

**Day 2 (06-04)** — 114 finishes (~50h from launch). 
- Score 114 → **universality verdict** (≥4/5 assets + δ*≈0.5?). Pull, `score_concave_confirm.py`.
- Launch **116 criticality** (cheap inference, ~3h) → tail-scaling / critical-point read.
- DEV: build the **champion 5-asset confirmation** template (ready for whatever wins 115).

**Day 3 (06-05)** — launch **115 composition** (SPX, ~0.8d GPU).
- DEV (stretch): start **117 leverage mechanism** — make a return→vol asymmetric coupling learnable
  (tests + smoke). Timebox dev to 1 day; if it doesn't smoke clean → drop, SV is the 2nd mechanism.

**Day 4 (06-06)** — 115 returns. Score.
- **Gate G1 (composition):** does **concave+SV beat net 5.96** AND lift leverage/zumbach/dfa WITHOUT
  losing the tail? Per-fact Welch+Bonferroni vs baseline AND vs the 5.96 SOTA number.
- If 117 smoked clean: launch **117 leverage-recovery** (n=30).

**Day 5 (06-07)** — fail-loop / iterate.
- If 115 underperformed: adjust SV gain / composition (pre-registered A→B→C ladder), relaunch.
- Score 117 if it ran → "2nd mechanism recovered at theory value" demonstrator.

**Day 6 (06-08)** — identify the **champion** (best composition cell).
- Launch **champion 5-asset n=30 confirmation** (~0.8d GPU). NO best-of-N — this is THE gate.

**Day 7 (06-09)** — champion confirmation returns.
- Score: per-fact gate, all 11 facts, vs baseline AND vs SOTA, Welch+Bonferroni, 5 assets.
- CPU: ABIDES results in → assemble the **three-paradigm frontier figure**.

**Day 8 (06-10)** — buffer / re-run any seed-underflow (n<30 effective on heavy-tail seeds).
- Lock the **results table** (the paper's Table 1).

**Day 9 (06-11)** — analysis consolidation.
- Finalize all scorers/figures; write the **results-section skeleton** (claims → section refs).

**Day 10 (06-12→13)** — final buffer. Memory + log. Any last confirmation re-run.

---

## Gates & honest fallback ladder (no downgrade — escalate, don't soften)

- **114 fails universality** (<4/5) → Paper A retreats to "SPX solve + the diagnose"; still a paper,
  lower tier. Report the boundary honestly (which asset/timescale broke).
- **G1: composition doesn't beat SOTA** → claim stays "per-fact tail solve + method + universality",
  NOT "+SOTA". Still NeurIPS-plausible on method+universality; don't claim the ceiling break.
- **117 leverage doesn't build in time** → drop; SV is the pragmatic 2nd mechanism; the method claim
  is slightly weaker (composition not theory-recovery) but holds.
- **Criticality probe finds no critical point** → fine for Paper A (it's depth, not load-bearing);
  it does down-weight the Paper B phase-transition fork — recorded, not hidden.

## The hard Day-10 deliverable (the Paper A results section)

1. **114 universality verdict** (pass, or honest boundary).
2. **115 composition** scored — best achievable net + per-fact gate vs baseline AND SOTA.
3. **Champion confirmed at 5-asset n=30** (the no-best-of-N claim).
4. **Three-paradigm frontier figure** (ABIDES).

Items 1–4 are the spine. 116 (depth) + 117 (clean method demonstrator) are high-value adds, not
blockers. If only 1–4 land, Paper A has: a universal theory-derived mechanism, a (possible) SOTA,
a method framing, and a failure-mode map — a defensible NeurIPS/ICML-main submission.

**Honest ceiling if the sprint fully lands:** ~50–60% NeurIPS-main (up from ~30–40%), ~85%+ a
respectable venue.
