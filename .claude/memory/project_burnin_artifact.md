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
