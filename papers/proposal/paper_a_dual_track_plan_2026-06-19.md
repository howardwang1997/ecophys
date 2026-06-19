# Paper A — dual-track venue plan: NeurIPS/ICML (primary) + Nature Computational Science (stretch)

**Date:** 2026-06-19 (post Stage-3). **Supersedes** the venue sections of
`paper_a_b_ncs_strategy_2026-06-19.md`. Evidence: `experiments/123_driven_transient/`,
`papers/paper_a_methods/{claim_and_roadmap,stage3_realdata_pilot,burnin_artifact_finding}_*.md`.

---

## 0. What changed — the fork

Exp 123 established, **in the EcoMD simulator**, a clean driven-transient: the steady state is
light-tailed (Hill α≈4.7); a shock (state_kick or the market-realistic price_jump) revives a heavy
cube-law-and-beyond tail (α→0.5) that relaxes on a finite timescale (τ≈240 deep / ≈20 burn-in),
across 5/5 assets with a sigmoid dose-response. This is real and well-characterized.

The **Stage 3 real-data test refuted the naive extrapolation** to real markets: across 5 crypto
crashes (COVID-2020, China-2021, Celsius-2022, Luna, FTX) + a formal null-distribution test
(Δα = α(crash 2d) − α(pre 5d), vol-standardized, vs n=170 calm window-pairs), the **pooled Δα z =
+1.03** — real return tails are **stationary cube-law** in calm *and* crash (Gabaix–Plerou–Stanley),
the opposite of "crashes drive a heavier tail." The EcoMD transient is a property of the *simulator*
(het_mass off → no stationary heavy-tail source), not of real-market *returns*.

⇒ The venue strategy bifurcates: **Track A** (NeurIPS, on the simulator + the model–reality gap, ready
now) and **Track B** (NCS, only via a *different real-market observable* than returns).

---

## Track A — NeurIPS / ICML / ICLR  (PRIMARY; evidence in hand; recommended)

### A.1 Claim (scope-controlled, fully supported)
> We introduce **EcoMD**, a calibrated differentiable particle simulator for market dynamics, and use
> it for controlled non-equilibrium experiments. In EcoMD the **steady state is light-tailed**, while
> **heavy tails emerge only transiently** under non-equilibrium driving (initialization or exogenous
> shock) and relax on a finite timescale. Warmup-inclusive rollout scoring **misreads this transient
> as a stationary law** (the prior cube-law "solve" was a burn-in artifact). Controlled shocks across
> two channels (latent kick, market-realistic price gap) revive the same relaxation template; the
> effect generalizes across 5 assets with a sigmoid dose-response. **Unlike real markets** — whose
> return tail we show is stationary cube-law in calm and crash — this localizes a **missing stationary
> heavy-tail mechanism** in this class of differentiable market simulators.

### A.2 Allowed strong claims
- EcoMD is a calibrated differentiable particle simulator for controlled non-equilibrium market experiments.
- In MD-style differentiable market simulation, warmup-inclusive rollout scoring confounds transient and stationary tails (measurement correction).
- Controlled shocks (two channels) revive the heavy-tail relaxation template seen at initialization; 5-asset, dose-response, finite τ.
- The simulator's transient heavy tail does **not** match real markets' stationary cube-law tail — a falsifiable, tested model–reality gap.

### A.3 Forbidden claims (would over-reach the evidence)
- "Real market fat tails are driven transients" (Stage 3 refutes).
- "Universal critical scaling" / "market thermodynamics established" (Paper B territory; not shown).
- C1 "first differentiable market sim" (false — Bouchaud-Cont 1998, Dyer 2023; lead with the finding).

### A.4 Structure (7 sections)
1. **Problem** — fat-tail/vol dynamics measured passively; real markets can't be experimentally shocked.
2. **Framework** — EcoMD: differentiable particle simulator; raw pre-impact ED logging; shock schedules; windowed non-equilibrium diagnostics; warmup hygiene; gradient calibration.
3. **Measurement correction** — warmup-inclusive scoring confounds transient vs stationary; the prior concave "solve" was burn-in inflation (R1: hill 3.9→6.6 under warmup discard).
4. **Controlled discovery** — steady state light; shock revives heavy tail; relaxes (τ); 5/5 assets; sigmoid dose-response (onset 0.1–0.2, floor ~0.5); asset-dependent threshold ∝ intrinsic vol.
5. **Robustness / channels** — state_kick (latent) **and** price_jump (market-realistic gap) give the same dip-and-recover (Stage 2b); τ characterization.
6. **The real-market boundary (honest)** — 5 crash episodes + null test: real return tails stationary cube-law ⇒ the transient is a simulator property; the gap pinpoints a missing stationary mechanism.
7. **Handoff** — EcoMD as the calibrated substrate for Paper B's real-market thermodynamic program.

### A.5 Evidence map
| section | experiment / artifact |
|---|---|
| 3 | `burnin_artifact_finding_2026-06-18.md`, R1 `r1_warmup_report.json` |
| 4 | exp 123 Stage 1/1.5/2a verdicts; `claim_and_roadmap`; τ `tau_report_spx.json` |
| 5 | Stage 2b `verdict_spx_jump.json` (running on .56); `_apply_shock` price_jump |
| 6 | `stage3_realdata_pilot_2026-06-19.md`; `null_test_crash_tails.py`; `data/real/` |

### A.6 Remaining work + timeline
1. **Collect Stage 2b** (jump verdict, ~now, on .56) — closes the two-channel robustness. *(in flight)*
2. **Spine rewrite** — replace the stale "7/11 calibrated tool / stationary concave solve" outline with the 7-section structure. *(~1–2 sessions)*
3. **Figures** — (a) burn-in correction R1; (b) shock dip-and-recover + dose-response sigmoid; (c) τ; (d) real-market null test (the honest boundary). *(~1 session)*
4. **Baselines/ablations sufficiency** — confirm the ceiling/baseline story survives the warmup correction (already mostly done; cite `pareto_ceiling`).

### A.7 Honest probability
- Well-executed methods + computational-science + honest-negative paper. NeurIPS/ICML main: **~30–40%**;
  ICLR/TMLR: higher. The measurement-correction + model–reality-gap framing is a genuine, citable
  contribution but not flashy SOTA — set expectations accordingly. **Ready to draft now.**

---

## Track B — Nature Computational Science  (STRETCH; conditional; re-aimed)

### B.1 Why the original NCS thesis is dead
The pre-Stage-3 plan anchored NCS on a real-market **return-tail** driven transient. Stage 3 formally
refuted it (pooled z=+1.03, stationary cube-law). A return-tail NCS claim is **not available**.

### B.2 The pivoted NCS thesis (the only honest route)
The non-equilibrium signature, if it exists in real markets, lives not in the **return** tail
(stationary) but in **order-flow / liquidity** dynamics — where microstructure non-equilibrium
actually sits. Pivoted claim:
> Controlled EcoMD experiments + real L2 data reveal that crashes drive a transient non-equilibrium
> signature in **order-flow imbalance / liquidity depth / entropy production** (dip-and-recover),
> even though the return tail stays stationary — distinguishing genuine non-equilibrium driving from
> stationary heavy tails.

### B.3 Gates (all required; pre-register before looking)
1. **Data:** Tardis L2 buy (BTC+ETH × 6mo, **$4–5k**) — order book changes + trades. (LOBSTER for equity optional.)
2. **Define + pre-register** the order-flow transient statistic (windowed tail/entropy-production/TUR
   slack on order-flow imbalance), the crash windows, the calm null, and the decision threshold —
   *before* analysis, same discipline as Stage 3.
3. **It must pass** the same dip-and-recover + null test that *returns* failed. If order-flow is
   *also* stationary across crashes, Track B dies and the result folds into Track A as "even
   order-flow shows no transient" (still honest, still NeurIPS).

### B.4 The Paper-B overlap caveat (important)
The order-flow / entropy-production / TUR program **is Paper B's core** (Nature Physics: real-market
thermodynamics). Re-aiming Paper A at NCS via order-flow **cannibalizes Paper B.** Two coherent resolutions:
- **(Preferred) Keep Paper A = NeurIPS** (Track A) and route the order-flow non-equilibrium ambition
  into **Paper B (Nature Physics)**. Cleanest division of labor; no self-competition.
- **(Alt) Stretch Paper A → NCS** only if a *quick* order-flow pilot (post-Tardis) shows a clean,
  pre-registered transient that is *distinct in framing* from Paper B's thermodynamics (e.g., Paper A
  = "computational-experiment methodology + the order-flow transient as discovery"; Paper B =
  "the thermodynamic laws"). Requires careful scoping to avoid overlap.

### B.5 Cost / timeline / risk
- Cost: **$4–5k** (Tardis) committed before any Track-B evidence exists.
- Timeline: +6–10 weeks (data ingest + L2 reconstruction + pre-reg + analysis) on top of Track A.
- Risk: order-flow may be stationary too (plausible — stationarity is the empirical norm); then the
  buy yields a *second* honest negative (not wasted — it serves Paper B's measurement program).

### B.6 Honest probability
- P(order-flow shows a clean real transient) ≈ 30–45% (genuinely unknown; microstructure is where
  non-equilibrium lives, but stationarity keeps winning). P(that + NCS-grade + accepted | signal) ≈
  30–40%. **Joint ≈ 10–18%**, gated on a real-money buy. **Do not commit the buy for Paper A alone** —
  commit it for **Paper B**, and let Track B be an *opportunistic* by-product if the pilot is clean.

---

## Sequencing + decision triggers

- **Now:** draft **Track A** (NeurIPS) — it is unconditional and depends on nothing pending except the
  Stage 2b collect (in flight). Ship it.
- **Tardis buy trigger:** commit the $4–5k **when Paper B's program is greenlit** (it needs L2
  regardless), *not* to chase Paper A→NCS in isolation.
- **Track B go/no-go:** after a pre-registered order-flow pilot on the Tardis data — if it shows the
  dip-and-recover that returns lacked **and** can be framed distinctly from Paper B, *then* consider
  stretching Paper A to NCS; else Track A stands and order-flow lives in Paper B.

## Bottom line
**Track A (NeurIPS) is the plan of record — draft it now.** **Track B (NCS) is a conditional stretch**
that (a) requires a different observable than returns, (b) is gated on the Tardis L2 buy justified by
Paper B, and (c) must clear the same pre-registered null test returns failed. Honest joint odds for
the NCS stretch are ~10–18%; the NeurIPS paper is the high-probability, evidence-backed deliverable.
