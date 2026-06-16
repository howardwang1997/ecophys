# Paper A — full results compilation + writing plan + gap analysis (2026-06-13)

**Why this doc exists.** The three prior Paper-A docs are all stale and mutually inconsistent:
`outline.md` (2026-04-25, ICAIF / v2.1 / "7-8/11 calibrated tool"), `draft_sections.md`
(same era), and `proposal/paper_a_neurips_2027_state.md` (2026-05-21, captures the §4 *diagnose*
but predates the entire *solve* arc). **None reflects the spine the 2026-06 experiments actually
established.** This doc is the current source of truth: every claim mapped to the experiments that
support it, with what's verified vs. owed.

Venue (settled): **NeurIPS / ICML** (methods + physics). *Not* Nature Physics — that is Paper B.
Honest acceptance estimate, executed cleanly: **~25–35%**.

Numbers tagged `[v]` were re-scored on Mac this session (2026-06-13); `[doc]` are from the
committed record (state doc / attribution_matrix.md / memory) and should be re-scored at write-time.

---

## 0. The honest spine (3 pillars — this is the paper)

> **Problem → diagnose → solve**, on a single clean axis:
>
> **P1 (diagnose).** Across three modeling paradigms there is a per-fact Pareto frontier:
> **tail-shape XOR volatility-dynamics**. Physics-sims (EcoMD) reproduce dynamics (clustering,
> leverage, long-memory) but structurally *overshoot* tails; deep-generative (WGAN/TrajCast/
> diffusion) reproduce tails but *kill* clustering (acf²≈0.1); agent-based (ABIDES) reproduce
> neither. **No paradigm clears the joint.**
>
> **P2 (mechanism / why).** The tail overshoot is **dynamical, not distributional** — Gaussian
> noise + zero jumps still gives Hill≈1.30 (exp 109). So no noise/objective/mixture knob fixes
> it; it is emergent from the excess-demand dynamics. The full set of failed "solve" tracks are
> the negative controls that make this paradigm-level, not a capacity artifact.
>
> **P3 (solve + theory).** A square-root-law-inspired **concave price impact** `β·sign(ED)·|ED|^δ`
> is the only cell we found that lands **both** Hill✓ and acf²✓. Pooled across 5 assets it pulls
> Hill in-band 7%→81% (+73pp), worst collateral −6pp. **And it is derived, not fitted:** a
> tail-transfer lemma gives `α = ζ_ED/δ`, so the crossing to the empirical inverse-cubic (α=3) sits
> at `δ* = ζ_ED/3`; with the Gabaix half-cubic demand tail ζ_ED≈3/2 this is **δ*=1/2** (TLB √-law).
> Verified in-silico: `Hill·δ ≈ ζ_ED ≈ 1.5` constant across the δ-grid (CV 1–9%) for all 5 assets,
> and ndx's δ*=0.53 is *explained* by its heavier demand tail ζ_ED=1.60 (not a universality
> failure). Full derivation: **`theory_tail_transfer.md`** (`scripts/score_transfer_law.py`).

---

## 1. Experiment corpus map (≈120 experiments → 6 clusters)

### Cluster A — Architecture exploration & negative architectural results  (→ §4.1 "we tried hard")
| exp | what it tested | result | status |
|---|---|---|---|
| 003–017 | ecomd v0→v2 lineage, MACE-lite, Ilinski gauge, v2.1 | MACE-lite **0–4/11** (canonical failure); gauge/body-order hurt | [doc] |
| 018 force_probe, 019 acf_shape | force-magnitude / ACF-shape diagnosis | \|F\|/σ "Goldilocks" table; SE(3) drowns dynamics | [doc] Fig1/Fig2 exist |
| 037–048 | arch tiers: memory, kernels, features, jumps, multitimescale, ISAB, MEGNet, dyngraph | each ingredient ablated; most theory-suggested ones hurt | [doc] |
| 045–054 | MEGNet / dyngraph / `4.2` family + pairs/triples | `p_4_2__2_1` family; depth-2 sweet spot | [doc] |

### Cluster B — The Pareto ceiling in hand-crafted Markov mechanisms  (→ §4 diagnose CORE)
| exp | what | result | status |
|---|---|---|---|
| 069–087 | single-mechanism 30-seed sweeps (gamma, levy, asym-drag, memk, power-law, microstructure, wasserstein…) | no single mech > ~5.2; each lifts one floor, breaks another | [doc] |
| 088 pairs_and_confirmation (460) | depth-2 pair sweep, BTC fact-trading | pair_AB 5.18 (superseded) | [doc] |
| **089 attribution (796, n=50)** | 16-cell per-fact attribution | **specialist matrix = Fig 1**; `zumbach_dn_s10` best single 5.12; both floors liftable but Pareto-bounded | **[v]** matrix regenerated |
| 089b cross-asset (480) | per-asset attribution | pattern reproduces 5 assets | [doc] |
| **092 5-asset (600)** | cross-asset replication | **best = `xa_gold_zumdn` 5.96 (n=26)**; no cell >5.5 except gold zumdn; spx 5.24 / eurusd 5.36 / ndx 5.18 / btc 5.10 | **[v]** |
| 096 all-pairs (690) | 23 pair combos | no pair >5.5 → Pareto-impossibility | [doc] |
| 097 n_agents scaling (90) | rebut "ceiling is N-dependent" | ceiling N-independent | [doc] |
| 098/098b/c/d zumdn refinement | SOTA dose-response surface | confirms zumdn ridge ~5.9 | [doc] |

**§4 verdict [v]:** ceiling ≈5.1–5.2 across 4 mechanism families × ≥26 seeds; SOTA-net **5.96**
(gold zumdn). Every floor-lift breaks ≥1 fact by ≥20pp → **Pareto-bounded, not absolute.**

### Cluster C — Negative controls (frontier is paradigm-level, not capacity/objective)  (→ §4.3 + §5)
| exp | track | result | status |
|---|---|---|---|
| 099b memk (270) | Track A memory kernels | best 5.00, n.s. vs baseline | [doc] |
| 100 B-β (930) | scheduled-sampling depth-3 | best 5.10, n.s. | [doc] |
| 101 B-α (750) | Hopfield regime attractors | best 5.10, n.s. | [doc] |
| 102/103 (740) | per-fact surrogate loss / expanded loss | 0/14, 0/12 beat baseline — but 102 was an **invalid test** (surrogates dead at 7-return rollout) | [doc] |
| 107 (90) | surrogates LIVE @ rollout-reg 512 | Δ=+0.13, **p=0.81** → objective-coverage **falsified** (clean null) | [doc] |
| 104 mmd_longroll | MMD distribution-matching | (0 results on disk — check launch) | ⚠ empty |
| 108 neural_sde_scout (61) | baseline_mmd base | — | [doc] |
| **109 tail_attack (135)** | noise × jumps grid | **`normal_j00` (Gaussian, 0 jumps) still Hill≈1.30, mean 5.20** → tail overshoot is **DYNAMICAL not distributional** (the key §4.2 fact) | **[v]** |
| 110 moe_tournament (300) | mixture-of-Gaussians heads | best `moe_k4_tamed` 4.83, no break | **[v]** |
| 111 diffusion (60) | conditional diffusion | scored via distributional path (not 11-fact net); Hill✓ acf²✗ | [doc]; ⚠ score_summary finds no net-eval |

### Cluster D — The other two paradigms (frontier comparison points)  (→ §5 baselines + frontier fig)
| exp | paradigm | result | status |
|---|---|---|---|
| 093 (100) | traditional: GARCH-t / GBM / AR1-SV / LM | GARCH-t fakes Hill+acf² (the surrogate-kill caveat) | [doc] |
| 095 / 095b (300) | neural-generative: WGAN-LP, TrajCast-lite | Hill✓ but acf²≈0.1 ✗ (no clustering) | [v] in frontier |
| **105 abides_ceiling (5×250, daily re-run)** | agent-based: ABIDES RMSC03 | **best 4/10** (morevalue; base/morenoise 2, fewnoise/fewvalue 3) on 10 daily facts; passes only autocorr/cond_kurt/dfa; **fails every clustering+tail fact** (acf²≈0, Fano≈1, agg≈0); tails too THIN (Hill 5–7, opposite of EcoMD's too-fat) | **[v] DONE 06-16** |

### Cluster E — The solve (concave √-impact + δ≈0.5)  (→ §6 solve)
| exp | what | result | status |
|---|---|---|---|
| 113 gabaix_solve (180) | concave impact δ∈{.40,.50,.60,.70}, SPX | `concave_d050` 5.60 vs base 4.23 (p=0.0014, d=0.90); Hill 13→80%; δ*≈0.509 = TLB √-law | [doc] |
| **114 concave_confirm (390, n=60)** | 5-asset confirm + power top-up | pooled Hill **7→81% (+73pp)**, collateral −6pp; strict JOINT gate **2/5** (spx,btc; gold/eurusd/ndx ns even at n=60) | **[v]** |
| **118 delta_grid (662)** | δ∈{.35,.40,.55,.60} lever arm | δ\* per asset: spx .508 / **ndx .531✗** / gold .513 / eurusd .521 / btc .508 → **4/5 cover 0.5, ndx deviates**; eurusd's old .658 WAS noise | **[v]** |
| 115 composition (91) | concave+SV beat SOTA 5.96 (G1) | **FAIL** — do not re-chase | [doc] |
| 119 champion_confirm (80) | champion × 4 assets | pooled 4.90 < 5.96; **SV does not compose** | [doc] |
| 116 criticality (131) | FSS criticality (Paper B fork) | **NO-GO** (smooth crossover, no N_c) | [doc] |
| 117 leverage | 2nd mechanism (asym-drag/zumbach) | **empty — 0 results** | ⚠ not run |
| 120 fss_train, 121 heldout_regime | — | empty / pending | ⚠ |

### Cluster F — Utility / downstream  (→ §7)
| exp | what | result | status |
|---|---|---|---|
| 091 calibration (30) | ECoMD wall-clock leg | ~100× ABIDES+SBI claim | [doc] |
| **105 sbi cost (20 timed sims)** | ABIDES+SBI comparand | T_sim≈844s ⇒ SBI 1k/5k/10k sims = **235/1173/2345 CPU-h** vs ECoMD gradient calib ~minutes | **[v] DONE 06-16** |
| 094 var_holdout (96) | clean train/test VaR | no-leakage VaR backtest | [doc] |
| 015 crash_oos / 121 | OOS crash windows | pending | ⚠ |

---

## 2. How to write Paper A (section → evidence)

**Title direction:** drop "calibrated tool for Paper B" framing (that was the ICAIF goal-driven
title). Lead with the frontier. e.g. *"Tails XOR Dynamics: a Three-Paradigm Pareto Frontier in
Market Simulation, and a Square-Root-Impact Mechanism that Crosses It."*

| § | content | load-bearing evidence | draft state |
|---|---|---|---|
| 1 Intro | the joint-reproduction problem; no simulator gets tails AND dynamics | frontier fig | rewrite (old intro is Paper-B-motivated) |
| 2 Related work | ABIDES, GradABM/Dyer, GAN/diffusion sims, MACE templates | — | mostly reusable from draft_sections §2 |
| 3 Method | EcoMD: Langevin + typed pair potential (SPS) + excess-demand price + **concave impact** | §3 of draft_sections + concave term from 113 | reusable; ADD concave-impact subsection |
| **4 Diagnose** | (a) arch negatives → Cluster A; (b) Pareto ceiling in Markov family → Cluster B (**Fig 1 = 089 attribution**); (c) **frontier across 3 paradigms** → `assemble_frontier` table+fig | 089 [v], 092 [v], 095/105, frontier [v] | **new — the spine** |
| 4.2 "why" | tail overshoot dynamical not distributional | **109 [v]** | new, short, high-impact |
| **4.5 Theory** | **tail-transfer law `α=ζ_ED/δ` ⇒ δ*=ζ/3=0.5 (TLB √-law); verified Hill·δ≈1.5 [v]; explains ndx** | **`theory_tail_transfer.md`** | **new — the derivation; converts δ≈0.5 from empirical to derived** |
| 5 Negatives as controls | memk/B-β/B-α/MMD/MoE/SV all fail to get both → paradigm-level | Cluster C [v partial] | new |
| **6 Solve** | concave √-impact: pooled +73pp Hill, frontier-unique Hill✓∧acf²✓, δ≈0.5 (TLB) on 4/5 | **113/114/118 [v]** | **new — the solve** |
| 7 Utility | gradient calibration ~100× ABIDES+SBI; VaR | 091 (half), 094 | needs ABIDES+SBI leg |
| 8 Discussion / limits | 2/5 strict gate; ndx δ\* deviation; GARCH-fakeable 2-fact gate → lead JOINT+structural | — | new, honest |

**Figures (current):** Fig1 attribution (089, exists), Fig_frontier_3paradigm (exists, [v]),
Fig hill(δ) crossing (118 — **needs rendering**), Fig concave before/after per-fact (114 — needs
rendering). Old fig3/4/5 (scoreboard/overfit/phase) are reusable supporting material.

---

## 3. What experiments the paper still needs (derivation-aware, prioritized)

**P0 — closes the theory loop (high value, cheap):**
1. **Measure ζ_ED directly** — the single most valuable missing experiment. The derivation predicts
   the return tail from the excess-demand tail (`α=ζ_ED/δ`); we currently *infer* ζ_ED≈1.5 via
   `Hill·δ`. Dump the per-step `ED_t` series from a rollout and Hill-estimate its tail, per asset.
   **Prediction: ζ_ED≈1.50 (ndx≈1.60), matching the `Hill·δ` column.** If confirmed, δ* is *derived
   AND independently verified* end-to-end — no longer a fit. No retraining; realizations don't store
   ED, so needs a short rollout w/ ED logging (Mac N≤500 smoke per asset, or 1 H20 cell).
   → owed: small patch to the rollout dumper + `score_transfer_law.py --measure-zeta`.
2. ✅ **ABIDES daily fair re-run** (105) — **DONE 2026-06-16** (CPU box, 5 cells × 250 seed-days,
   daily mode on 10 facts). Best 4/10 (morevalue); fails every clustering+tail fact; tails too
   THIN (Hill 5–7). Agent-based now a *solid* third frontier corner: reproduces neither, undershoots
   tails — distinct from EcoMD (overshoots tails) and neural (kills clustering). Results fetched to
   `experiments/105_abides_ceiling/results_rmsc03_*_daily/inference_merged.json`.
3. **Frontier on >1 asset** — neural baselines (WGAN/TrajCast/diffusion) are SPX-only in the frontier
   table. Score them on NDX (+1 more) so "neural passes Hill but fails acf²" is multi-asset, or scope
   the claim to SPX explicitly. (Baselines exist in 095b — may just need re-scoring, not re-running.)

**P1 — strengthens / referee will ask:**
4. ✅ **ABIDES+SBI calibration leg** (091) — **DONE 2026-06-16**. T_sim≈844 s/sim ⇒ SBI 1k/5k/10k
   sims = 235/1173/2345 CPU-h; comparand for §7's gradient-calibration claim (`sbi_cost_report.json`).
   Note the gap is ≫100× at sim-count budgets (sim-bound); state honestly as CPU-core-hours.
5. **Per-step vs series tail check** — confirm the marginal-tail caveat empirically: Hill on per-step
   |Δp| vs on the aggregated return series should give the same exponent. Cheap, defends the lemma's
   transfer-to-series step against a referee. (Same ED-logging rollout as #1.)
6. **111 diffusion / 104 MMD completeness** — 111 has no 11-fact net eval (only distributional);
   104 MMD shows 0 results on disk. Verify both ran; needed for the Cluster-C negative-control claim.

**P2 — nice-to-have / revision-response:**
7. OOS crash validation (015/121) — pending; §7 robustness.
8. ndx ζ_ED targeted check — directly measure ndx's demand tail to confirm the 1.60 that explains
   its δ*=0.53 (subsumed by #1 if #1 is run per-asset).

**Note — what is NOT a missing experiment (already settled, don't re-run):** δ-grid (full 0.35–0.60,
n=30); power top-up (n=60, did not lift the 2/5 gate); composition/SV (G1 dead); criticality (NO-GO).

**Tooling fixes (not experiments, but block clean export):** render hill(δ) crossing fig (118) +
concave before/after fig (114); fix `score_concave_confirm.py:139` hardcoded "UNIVERSAL"; update
`score_delta_grid.py` to fit `α=ζ/δ` (report Hill·δ) instead of the linear form.

---

## 4. What NOT to write (dead / forbidden claims)
- **"Beats SOTA 5.96"** — DEAD. 5.96 is *our own* zumdn cell (092), not a literature method;
  concave doesn't beat it on net-count and shouldn't try (G1/115 + SV/119 failed twice). Frame
  zumdn as the "max-net-count but fails tails" interior point ON the frontier.
- **"δ\*≈0.5 universal"** — downgraded to "4/5 consistent, ndx deviates."
- **"solved on all 5 assets"** — strict JOINT gate is 2/5; frame via pooled + frontier.
- **Any 2-fact (Hill+acf²) gate as the headline** — GARCH-t-fakeable (093); lead with JOINT 11-fact
  + structural facts (zumbach/leverage/dfa) a null can't fake.
- **Nature-Physics / criticality / T_eff** — that's Paper B (116 FSS = NO-GO anyway).

---

## 5. Doc hygiene
- Mark `outline.md`, `draft_sections.md`, `paper_a_neurips_2027_state.md` **SUPERSEDED by this
  file** (keep for history). The reusable prose is draft_sections §2 (related work) and §3 (method).
- This compilation + `MEMORY.md` + `logs/2026-06-12.md` / `logs/2026-06-13.md` are the live state.
