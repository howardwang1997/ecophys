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

**2026-06-19 Stage-1.5 + Stage-2a (overnight, 8-card .14):**
- **spx dose-response MAPPED (full, mag 0.05–12) — a clean SIGMOID:** post-shock α_ED =
  4.24/3.01/1.88/1.45/1.08/0.77/0.58/0.51/0.49/0.58. **Light below mag≈0.1 (4.24 = no revival), onset
  ~0.1–0.2, graded ramp to mag 2, saturated floor ~0.5 for mag≥3.** Monotone 9/10 (only the mag6→12
  floor step 0.49→0.58 is seed-noise). H2 graded-dose-response SATISFIED; script still prints P\* only
  for that floor-noise non-monotonicity.
- **Multi-asset generalization: 5/5 assets show the driven-transient revival (all P):** spx, ndx(0.58),
  gold(0.54), btcusdt(0.57), **eurusd**. eurusd needed a bigger kick — A at mag3 (4.16) but P at mag6/12
  (2.91→**1.68**); its burn-in template is also lighter (1.04). ⇒ **asset-dependent threshold tied to
  intrinsic volatility**: equities/gold/crypto onset ~0.1–0.2, low-vol FX (eurusd) ~6–12. A feature, not
  a bug. The earlier "eurusd=A" is RESOLVED (sub-threshold, confirmed by the mag12 revival).
- Verdicts `verdict_{spx,gold,eurusd,btcusdt,ndx}.json`; claim+roadmap `papers/paper_a_methods/claim_and_roadmap_2026-06-19.md`.

**Reframe decided (positive frontier, not a warning):** *"market fat tails are a non-equilibrium /
driven transient; the stationary model is light-tailed."* **NOW EVIDENCED (P, 4/5 assets, 2026-06-19);
graded dose-response + relaxation floor.** Earns-or-kills experiment: `experiments/123_driven_transient/DESIGN.md`.
**Owed before bulletproof:** spx onset micro-sweep + eurusd threshold (running); a market-realistic shock
channel (price-jump/liquidity, Stage 2b, vs the "state_kick is mechanical" skeptic); **REAL-DATA crash
validation (Stage 3 — decides NeurIPS vs Nature-Physics)**. — shock a steady-state system, test whether the cube-law
tail revives + relaxes with the SAME ζ_ED signature as the t=0 burn-in (H1–H5 + binding gate). If the
revival reproduces the burn-in template ⇒ genuine non-equilibrium physics (publishable, C2+C3); if no
revival at any dose ⇒ t=0 startup artifact ⇒ fall back to diagnose-centered frontier. **R2 (rebuild a
stationary heavy-tail source) is now DEPRIORITIZED** — the transient framing needs no stationary source,
and fitting one would undercut "derived not fitted." See [[paper-a-target-neurips-2027-problem-diagnose-solve-framing]],
[[pareto-ceiling-11-fact-frontier-in-v3-mechanism-family]].

**2026-06-19 PM — "push to NCS" attempt → Stage 3 real-data pilot REFUTES the market-discovery claim
(decisive). Paper A scope = NeurIPS sim-physics + model–reality gap, NOT Nat-CS/Physics.**
- **🔴 Stage 2b (market-realistic channel) — NEGATIVE (validated).** `price_jump` (exogenous price gap
  folded into the realized return) finished on .56 (5 doses, 300 rollouts). Verdict **"A — ARTIFACT,
  no revival"**: post-shock min α_ED flat ~4.5–4.6 (vs state_kick 4.7→0.5). NOT an invalid test —
  checked α_ret too (price_jump perturbs the return): α_ret pre≈7.7→min 6.0 at mag12, a weak nudge
  that STAYS LIGHT (~100× weaker than state_kick). ⇒ **the transient is specific to displacing agent
  LATENT states** (state_kick = the burn-in mechanism); exogenous price shocks don't trigger it. So
  the driven transient is a **model latent-equilibration phenomenon, not a market-shock response.**
  Compounds Stage 3 (absent in real markets) ⇒ NOT a robust market-physics discovery. **What survives:
  the burn-in MEASUREMENT CORRECTION** + the mechanistic localization. NCS positive-discovery framing
  further weakened (→ ~8–15%); leans TMLR/PRE/measurement-methods. Stage 2c news channel now low-value
  (same indirect mechanism, likely also negative).
- **OFI logging + sim-side OFI transient (2026-06-20, Route-A prerequisite).** Added per-step order-flow
  imbalance ρ∈[-1,1] to the recorder (commit e19d868b5). Fresh spx control/kick6/jump6 (n=30, OFI logged)
  → `ofi_transient_spx.json`: **kick6 drives a strong OFI transient on all 4 measures** (|ρ|, std,
  **lag-1 memory 0.018→0.995→−0.03**, saturation — burst-then-relax); **jump6 = control bit-for-bit (NO
  OFI transient).** ⇒ **OFI does NOT rescue price_jump** (inert on tail AND order flow); two-channel
  robustness definitively dead. **Reframe:** a crash = *coordinated agent liquidation* (=state_kick),
  not a price gap (=price_jump) → state_kick is the better crash analogue, and its OFI coherence/memory
  burst-and-relax is a **concrete falsifiable prediction for real crash order-flow** (Route-A L2 test,
  distinct from the stationary return tail). OFI substrate validated (sensitive). Work-list E5
  recorder-half DONE.
- **Stage 2d (τ):** burn-in template τ≈20 steps (matches the known ~20-step burn-in); deep/saturated
  shocks τ≈240 (driven transient relaxes ~10× slower than cold-start; τ grows with dose). Quantifies
  "~1k steps". `scripts/fit_relaxation_tau.py`, `tau_report_spx.json`.
- **🔴 Stage 3 (NCS Gate 2) — ROBUST NEGATIVE.** Free 1m Binance crypto, Luna(2022-05)+FTX(2022-11)+
  calm control. Regime-level Hill: Luna BTC pre α=2.54→crash α=**3.97** (tail LIGHTER, Δ+1.43); ETH
  +1.76; FTX ≈flat (Δ−0.16/−0.23), inside calm null 2.63±0.17. **Vol-standardized** (removes
  high-vol→lighter-Hill confound): Luna still lightens 3.42→4.47; FTX flat → NOT a vol artifact. **Real
  fat tails are ~STATIONARY cube-law (calm AND crash) = Gabaix-Plerou-Stanley universality.** The
  EcoMD driven-transient is a property of the SIMULATOR (het_mass off → no stationary heavy-tail
  source), NOT of real markets. **BROADENED + FORMALLY TESTED (user: "broaden before deciding"):**
  5 crypto crashes (COVID-2020/China-2021/Celsius-2022/Luna/FTX) + a null-distribution test (Δα =
  α(crash 2d)−α(pre 5d), vol-std, null slid over a 3mo calm stretch n=170). **Pooled z=+1.03**
  (slightly LIGHTER, opposite the prediction); only 1/5 (China-ban) significant-heavier (within the
  5-test FPR), 2/5 significant-LIGHTER (Luna/Celsius). Underpowered caveat removed → negative robust.
  `scripts/{fetch_crash_windows,analyze_crash_tails,null_test_crash_tails}.py`,
  `papers/paper_a_methods/stage3_realdata_pilot_2026-06-19.md`, `data/real/`.
- **Venue call (reviewer-2):** NCS Gate 2 fails → do NOT sell Paper A as a real-market discovery. The
  honest, strong paper is **NeurIPS/ICML simulator-physics + measurement correction + the model–reality
  gap** ("in EcoMD heavy tails are a driven transient & the steady state is light-tailed, UNLIKE real
  markets whose cube tail is stationary — localizing a missing stationary mechanism in this sim class").
  This is the original "close-strong NeurIPS" path. Real-market NCS would need a DIFFERENT observable
  (order-flow/L2 — Tardis, not yet bought); future direction, not this pilot.
- **Infra note:** `git pull --rebase origin HEAD` against the partial-clone remote triggers a
  full-branch rebase onto an old commit (promisor trap) — it broke the local tree once; `git rebase
  --abort` restored it. ALWAYS push/pull with the explicit branch name, never the literal `HEAD`.
