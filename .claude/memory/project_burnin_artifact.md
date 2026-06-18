---
name: burnin-artifact-zeta-ed-2026-06-18
description: "The ζ_ED≈1.5/cube-law tail-transfer validation is a ~20-step burn-in transient artifact; Phase 0 shows the standard hill scoring is burn-in-inclusive project-wide. Pivot to non-equilibrium-transient frontier (exp 123)."
metadata:
  node_type: memory
  type: project
---

# Memory — ζ_ED burn-in artifact (2026-06-18, threatens Paper A tail-transfer claim)

**One line.** The "ζ_ED≈1.5 / cube-law-3" evidence for the tail-transfer derivation
(`papers/paper_a_methods/theory_tail_transfer.md`) is a **~20-step burn-in transient artifact**;
`run_large.py` has no warmup discard, so every rollout's equilibration transient inflates the Hill
estimate with low cross-seed variance (looks like a robust law, isn't). In steady state the
model's ED **and** return tails are **light** (Hill α ≈ 4–12) at every δ.

**Full finding + D1/D2 evidence + options:** `papers/paper_a_methods/burnin_artifact_finding_2026-06-18.md`.
Session detail: `logs/2026-06-18.md`. Branch: `diagnostics/zeta-ed-burnin-artifact`.

**Three root causes (none is the transfer law being wrong — `α_Y=ζ/δ` is a correct identity):**
1. Trajectory `excess_demand` is saved **post**-concave-impact (`price_formation.py:357`→454); the
   theory's ζ_ED is the **pre**-impact (raw) tail. Invert with s=δ=0.5 fixed:
   `|raw|=s·(|post|/s)^(1/δ)`.
2. Heavy tail is burn-in-only — dropping first ≥50 steps makes all tails light
   (`experiments/122_zeta_ed_d1/`, spx seed0 δ-grid).
3. `het_mass_enabled` (GGPS Zipf-size heavy-tail source) is **off in every config** — deliberately
   dropped 2026-06-01 (misfired twice; see `project_neural_sde_tournament.md:148-154`). Model is
   concave-impact-only; it has **no stationary mechanism that can produce ζ_ED≈1.5**.

**Impact on Paper A.** `theory_tail_transfer.md` §validation table (Hill·δ≈1.48–1.60, CV 1–9%, 5
assets) is contaminated. The headline "δ≈0.5 derived not fitted" currently rests on a transient.
Not yet refuted at n=30 (D1 was seed0 only) — R1 (full n=30 + warmup discard) settles it; expect
refutation. Constructive fix = R2 (revive a working heavy-tail source; het_mass v3 = per-step
heavy flow + learnable tail index, per the tournament memory's own prescription).

**Code enabled this:** `scripts/score_transfer_law.py::measure_zeta_mode` upgraded (Hill α-vs-k +
bootstrap CI + |ret| sanity + transfer ratio). Use it for any future tail measurement; **always
report burn-in sensitivity**, never a single-point Hill.

**Do NOT** re-claim ζ_ED≈1.5 / cube-law-reproduced without (a) warmup discard and (b) a stationary
heavy-tail source in the model.

**2026-06-18 Phase 0 (Mac, no GPU) — blast radius = PROJECT-WIDE, not confined to tail-transfer.**
Verdict + evidence: `papers/paper_a_methods/phase0_burnin_blastradius_2026-06-18.md`. The standard
11-fact scoring is **also** burn-in-inclusive: `run_large.py:107` `returns = traj.log_returns_np()[1:]`
(full series, no warmup discard) → `compute_all` → `hill_tail_index`. So EVERY standard Hill in the
project shares the contamination. The **concave-impact "solve" sits in the blast zone**: standard
Hill at N=10⁴ n=30 5-asset = baseline 1.23–1.38 (too-fat) → concave 2.9–3.4 (in-band), but finding
D1 shows dropping warmup pushes the in-band concave Hill (3.42) to 11.5 (too-thin, FAIL). So the
5-asset "solve" (and this `feature/exp113-gabaix-solve` branch) is very likely a burn-in artifact;
steady-state concave is too THIN. **Contaminated:** hill≈1.3 overshoot (exp 109/112), concave solve
(113/114), δ-grid Hill·δ, δ*≈0.5 (where Hill-criterion-based). **Survives:** lemma α=ζ/δ; ceiling
*structure* (only strengthened — removing wrong Hill passes lowers scores); ABIDES daily (close-to-close,
burn-in washed). Magnitude per-cell unmeasured → R1 (GPU re-run 114 + `--save-trajectory` + warmup discard).

**2026-06-19 — exp 123 driven-transient RAN (3-box H20 fleet) → (P) PHYSICS, the positive reframe is
VALIDATED.** Windowed Hill α_ED(t) on spx (control + state_kick mag 3/6/12, n=32) + ndx (control +
kick6, n=30); verdict `experiments/123_driven_transient/verdict_{spx,ndx}.json`:
- **H1 control light**: steady-state [500,3000) α_ED = **4.75** (PASS). Control never dips (flat 4.7–4.9).
- **Shock revives**: every kicked arm **craters to α_ED ≈ 0.5** at the shock (4.75→0.49), *heavier than*
  the t=0 burn-in template (0.66).
- **H3 transient**: recovers to **≈4.7 within ~1k steps** (PASS) — relaxes back, not a permanent flip.
- **H4 = burn-in**: post-shock min (0.5) matches the burn-in template (0.66) (PASS) — same mechanism.
- ⇒ **the t=0-only "startup artifact" reading (A) is RULED OUT**; the heavy tail genuinely recurs under
  driving and relaxes. ndx replicates (4.4→0.58→4.65) = clean **P**.
- **Caveat (spx = P\*)**: the dip **SATURATES** at the floor for mag≥3 (0.51/0.49/0.58, not dose-monotone)
  → owed: a **SUB-THRESHOLD dose sweep (mag<3)** to map the dose-response, AND a **market-realistic shock**
  (news/liquidity) to answer the "is state_kick mechanical?" skeptic. Then the frontier paper is bulletproof.
- **R1 magnitude (warmup-discard, n_steps=8000)**: baseline hill drop0 3.87 → drop50 6.55 (Δ+2.68,
  IN-BAND→TOO-THIN); concave_d050 5.05 → 9.26 (Δ+4.21, already TOO-THIN at drop0 because n=8000 dilutes
  burn-in). **Confirms the concave "solve" is burn-in-held** — too-thin in steady state; the 4000-step
  "in-band solve" was burn-in inflation.

**Reframe decided (positive frontier, not a warning):** *"market fat tails are a non-equilibrium /
driven transient; the stationary model is light-tailed."* **NOW EVIDENCED (P/P*, 2026-06-19).** Earns-or-kills
experiment pre-registered: `experiments/123_driven_transient/DESIGN.md` — shock a steady-state system, test whether the cube-law
tail revives + relaxes with the SAME ζ_ED signature as the t=0 burn-in (H1–H5 + binding gate). If the
revival reproduces the burn-in template ⇒ genuine non-equilibrium physics (publishable, C2+C3); if no
revival at any dose ⇒ t=0 startup artifact ⇒ fall back to diagnose-centered frontier. **R2 (rebuild a
stationary heavy-tail source) is now DEPRIORITIZED** — the transient framing needs no stationary source,
and fitting one would undercut "derived not fitted." See [[paper-a-target-neurips-2027-problem-diagnose-solve-framing]],
[[pareto-ceiling-11-fact-frontier-in-v3-mechanism-family]].
