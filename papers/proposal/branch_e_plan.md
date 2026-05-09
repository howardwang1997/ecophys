# Branch E — A-round Combo + B-round New Mechanisms

**Date**: 2026-05-07
**Context**: Branch D (077-081) gave first 9/11 runs and validated all three v4 mechanisms individually. This plan covers the follow-up work to either push Paper A to ICML 2027 main conference or, if v4 saturates, introduce B-round mechanisms.
**Target**: ICML 2027 main (Jan 15 – Feb 1, 2027 deadline; ~8 months lead time).

---

## 1. State after Branch D

### Established facts (30 seeds per cell)

| Cell | mean n/11 | max | notes |
|---|---:|---:|---|
| 069 T05_g10 (v3 baseline) | 4.77 | 7 | 2000+ seeds total in history; never hit 8 |
| 077 levy_a19 | 4.93 | **9** | First 9/11 ever |
| 078 asymdrag_a06 | **5.10** | **9** ×3 | Current best cell; leverage pass 77% |
| 079 memk_l095_s10 | 4.63 | 8 | zumbach pass 13% vs v3's 3% |
| 080 GARCH | 4.73 | 6 | Critical: leverage/zumbach/gain_loss = 0% |
| 081 BTC v3 baseline | 4.57 | 8 | Cross-asset does not degrade |

### Four 9/11 winners all fail on the same 2-3 facts

| fail fact | winners failing | model value vs band | diagnosis |
|---|---:|---|---|
| autocorr_returns | 3/4 | +0.29 – +0.33 (band [-0.1, 0.2]) | AR(1) drift untouched by v4 |
| hill_tail_index | 3/4 | +1.15 – +1.84 (band [2, 4]) | Just below lower bound |
| zumbach_asymmetry | 2/4 | -0.01 – -0.04 (band [0.001, 0.5]) | Sign flip; a06 kills zumbach |
| aggregational_gaussianity | 2/4 | 408, 491 (band [10, 200]) | Likely AR(1)-induced |

---

## 2. A-round — Combining existing mechanisms

Goal: determine whether v4 mechanisms are additive, complementary, or conflicting.
This is the decisive experiment for Paper A §4.3.

### 082 — V4 mechanism leave-one-out + dose-response (180 cfgs, ~2.6h H20)

**Revised 2026-05-09** after plan review uncovered that the original 4-cell
plan (a) didn't include a clean ablation around a single flagship cell,
and (b) didn't combine ALL four mechanisms (Lévy + asym + memk + adiabatic
inner_steps) — yet that 4-mechanism combination is the only configuration
that can *plausibly* break the 2-3 facts the 9/11 winners all fail.

| cell | levy_α | asym_α | memk (λ, scale) | inner | answers |
|---|---:|---:|---|---:|---|
| `combo_full` | 1.9 | 0.4 | (0.95, 1.0) | 3 | flagship: full additive? |
| `combo_no_levy` | — | 0.4 | (0.95, 1.0) | 3 | does Lévy add? |
| `combo_no_inner` | 1.9 | 0.4 | (0.95, 1.0) | 1 | does adiabatic add? |
| `combo_no_memk` | 1.9 | 0.4 | — | 3 | does memk add? |
| `combo_asym05` | 1.9 | 0.5 | (0.95, 1.0) | 3 | asym dose-response |
| `combo_levy17` | 1.7 | 0.4 | (0.95, 1.0) | 3 | Lévy dose-response |

**Design rationale**:
- Leave-one-out structure quantifies each mechanism's marginal contribution
  vs the flagship — the standard ablation table reviewers expect.
- a04 (not a06) chosen because a06 had std=2.12 driven by conditional_kurtosis
  blowups in 4/30 seeds; a04 should be the sweet spot.
- inner_3 (not inner_5) — Branch C's inner_5 underperformed inner_1 standalone,
  suggesting adiabatic helps only when paired with other mechanisms.
- Lévy α=1.9 (not 1.7) — Branch D's 077 `levy_a19` had the highest cell mean
  (4.93). α=1.7 added as dose-response to test whether heavier tails help when
  AR(1) is broken by adiabatic.

**Success criteria** (must satisfy ALL):
- (a) `combo_full` mean n/11 ≥ 5.5 (improves on `asymdrag_a06`'s 5.10)
- (b) `combo_full` ≥ 4/30 seeds at ≥8/11 (matches a06's stability)
- (c) `combo_full` max n/11 ≥ 10 (new project record)

Stretch: combo_full mean ≥ 6.0 AND ≥1 seed at 11/11.

### 083 — Asym-drag fine grid (90 cfgs, ~2.5h H20)

Cell: `asymdrag_a04`, `asymdrag_a05`, `asymdrag_a07` × 30 seeds

**Goal**: dose-response curve for §4.3 ablation. Find sweet spot between a06 (high mean, high std) and a03 (low mean, stable).

**Priority**: medium. Skip if H20 time constrained — partially subsumed by
082's `combo_asym05` cell.

### 075 leftover — adiabatic inner_3 / inner_10 / inner_20 (90 cfgs, ~1.3h H20)

**Existing**: inner_1 mean=4.60 ac_pass=20%; inner_5 mean=4.07 ac_pass=43%.
**Already-generated configs cover**: inner_3, inner_10, inner_20 × 30 seeds = 90.

**Hypothesis**: ac_pass is monotonically increasing in inner_steps. If inner_10 or inner_20 pushes ac_pass > 60%, we have proof that adiabatic separation decouples the AR(1) artifact.

**Priority**: high. This is the only lever that has shown movement on autocorr.

### 081 leftover — BTC v4combo + baseline regen (60 cfgs, ~0.9h H20)

**Critical fix**: existing 081 configs had TWO bugs:
- `levy_alpha: 1.7` (wrong field name) instead of `noise_dist: levy` + `noise_levy_alpha: 1.7`
- `target_dataset: btc` + `target_period: 2017-2026_daily` — neither matches the trainer's recognised keys (`btcusdt` + `2024Q1_1m`), so `load_real_returns` silently fell back to SPX.

**Result**: every prior 081 result was SPX masquerading as BTC. The cross-asset story needs to be redone with the corrected configs. Both `btc_baseline` (30 cfg) and `btc_v4combo` (30 cfg) regenerated.

**Goal**: real cross-asset validation. §4.4 of Paper A.

**Priority**: high. Without this, no cross-asset story.

### 073 Hawkes/jump ablation (48 cfgs, ~1.2h H20)

**Goal**: mechanism attribution for §4.2 of Paper A. Identify which of the 5 baseline passes are Hawkes-contributed and which are jump-contributed.

**Priority**: low-medium. Paper A can proceed without but the ablation table is strengthened by having it.

### A-round resource summary (revised)

| batch | total cfgs | effective (SKIP_DONE) | H20 hours | priority |
|---|---:|---:|---:|---|
| 082 combo (6 cells) | 180 | 180 | 2.6 | **MUST** |
| 075 leftover | 150 | 90 | 1.3 | **MUST** |
| 081 BTC regen | 60 | 60 | 0.9 | **MUST** |
| 083 asym fine | 90 | 90 | 1.3 | optional |
| 073 Hawkes | 48 | 48 | 0.7 | optional |
| **minimum batch** | **390** | **330** | **~4.8h** | |
| **full batch** | **528** | **468** | **~6.8h** | fits in overnight |

---

## 3. B-round — New mechanisms (contingency)

B-round is activated only if A-round saturates (combo mean ≤ 5.1). Listed in descending ROI; not all four need to run.

### B1 — Microstructure noise / bid-ask bounce (fixes autocorr)

**Physical motivation**:
- Real SPX has AR(1) coefficient ≈ 0, but microstructure bid-ask bounce induces a small *negative* lag-1 autocorrelation (≈ -0.05 to -0.20) that masks the small positive autocorr of the underlying signal.
- ECoMD v3 has no order-book microstructure, so the AR(0.9) drift emerges as a structural artifact of the Langevin dynamics.

**Implementation**:
- Post-integrator moving-average noise: ε_t_effective = ε_t_primary - ρ_micro · ε_{t-1}_primary
- `ρ_micro` ∈ [0.0, 0.5] as new integrator config field
- Local change only, no BPTT impact, ~50 lines of code.

**Expected effect**:
- autocorr_returns mean pulled from +0.38 toward 0.10
- Minimal impact on other facts (sign-anti-correlated noise is invisible to |r|-based facts)

**Cost**: ~0.5 days code + 30-cfg test batch.

**Paper A value**: **Highest**. If it works, this becomes the signature mechanism — directly corresponds to a documented real-world market structure.

### B2 — Continuous KL / sliced-Wasserstein loss (fixes all facts marginally)

**Motivation**:
- Current training loss is moment-matching (mean/std/lag-k autocorr of returns).
- The 11 stylized facts are non-linear, strongly non-Gaussian functionals — moment matching is a poor surrogate.
- A continuous distribution distance (sliced-Wasserstein-2 or KL via KDE) would directly optimize what we're evaluating.

**Implementation**:
- Replace `losses.py:moment_matching_loss` with SW2 or KL.
- Add `loss_family: {moments, sw2, kl}` flag to config.
- ~150 lines, 1.5 days.

**Expected effect**:
- Uniform ~5-15% lift across all facts
- Max may or may not break 10/11
- "Tide rises all boats" improvement

**Paper A value**: High but needs careful framing. Reviewer will ask "is this not a trivial baseline improvement?" — must be paired with ablation showing v4 mechanisms remain necessary under new loss.

### B3 — Regime-switching enhancement (fixes aggregational_gaussianity)

**Motivation**:
- GARCH baseline passes aggregational_gaussianity 90% but v4 winners pass ≤ 27% with outliers mean=300+.
- Diagnosis: ECoMD never has a "quiet regime" — all seeds stay in persistent high-vol.
- GARCH gets quiet periods automatically via low σ²_t states.

**Implementation**:
- Convert existing soft regime GRU to hard discrete switching via Gumbel-softmax.
- Force regime to select among K ∈ {3, 5} discrete states with learned transition matrix.
- ~200 lines in `ecomd.py` main loop.

**Cost**: 2 days code + 60-cfg sweep.

**Paper A value**: Medium. Fixes one fact, but that fact is consistently failing in v4 winners.

### B4 — Power-law force tail in ExternalPotential (fixes hill_tail intrinsically)

**Motivation**:
- Lévy noise alone does NOT fix hill_tail — Branch D showed only 1/30 seeds in
  077 levy_a19 actually pass the [2, 4] band (cell mean=1.29). Hill estimator
  on a finite series is dominated by AR(1) drift contamination.
- Even after AR(1) is broken (via inner_steps adiabatic), the noise distribution
  alone may not give a robust hill in [2, 4] — we need a force shape that
  generates fat tails *intrinsically* via the dynamics, not through noise.
- Power-law external potential V_ext(s) ∝ |s|^α / α with α ∈ [1.2, 1.8] gives
  ∇V ∝ sign(s)·|s|^(α-1) — a soft, fat-tail-friendly force. This produces
  return distributions with naturally-heavy tails because the restoring force
  weakens (relative to linear) far from origin.

**Implementation**:
- Add `power_alpha: float | None` to `EcoMDConfig`; when set, modify
  `ExternalPotential.forward` to use `|s|^α / α` instead of the existing
  quadratic.
- File: `ecomd/models/potentials.py:ExternalPotential`
- ~150 lines, 1.5 days.

**Activation criterion**: A-round complete AND combo_full hill_tail pass < 30%
AND B1 (or AR(1) fix) is in place. Otherwise hill remains AR(1)-dominated and
this mechanism cannot show its effect.

**Paper A value**: High if needed. Direct hit on a stylized fact that all
existing baselines (GARCH excepted) fail.

### B-round decision tree (post-082)

```
082 combo result
    │
    ├── case 1 (~30% prob): mean ≥ 6.0, max ≥ 10
    │   → A-round succeeds. No B-round.
    │   → Invest time in cross-asset expansion (ETH, QQQ) + Paper A writing.
    │
    ├── case 2 (~45% prob): mean 5.3–5.9, max 9–10
    │   → Run B1 (microstructure) + 083 fine grid.
    │   → If B1 pushes ac_pass 20% → 60%+ → ship Paper A.
    │   → If B1 insufficient → run B2 (KL loss).
    │
    └── case 3 (~25% prob): combo mean ≤ 5.1 (saturation)
        → A-round confirmed saturated. B-round mandatory.
        → Priority: B1 (highest physics motivation, cheapest).
        → Insufficient → B1 + B2 joint.
        → Path to main-conference: 1–2 weeks.
```

---

## 4. Timeline to ICML 2027 submission

| week | work | output |
|---|---|---|
| Week of May 4 (this week) | Branch D post-analysis; A-round overnight | 082/075/081 results; Paper A §4.3 raw data |
| Week of May 11 | §3 Methods + §4.1 Baselines + §4.2 V3 ceiling draft | ~1/3 paper |
| Week of May 11 (parallel) | If case 2/3: implement B1, run 30 seeds | B1 results |
| Week of May 18 | §4.3 V4 mechanisms + §4.4 Cross-asset + §4.5 Combo | Full paper draft |
| Week of May 25 | §5 Discussion + §1 Intro + abstract + all figures | Submission-ready v1 |
| Week of Jun 1 | Internal review + revision | Revised draft |
| Jun–Dec 2026 | Dataset expansion (ETH, QQQ, crash OOS), polish | Final paper |
| Jan 2027 | ICML 2027 main submission | — |

Lead time: ~8 months. Comfortable margin.

---

## 5. Key open questions

1. **Are v4 mechanisms additive?** (082 answers)
2. **Is adiabatic the unique AR(1) fix?** (075 leftover + 082 combo_inner3 jointly answer)
3. **Does BTC behave like SPX?** (081 v4combo answers)
4. **What does a 10/11 or 11/11 seed look like?** (082 gives first chance)
5. **Can we break the AR(1) drift without breaking leverage/zumbach?** (B1 answers if A-round saturates)

---

## 6. What must not happen

- No retreat to "honest ceiling" / workshop paper route. User has explicitly rejected this.
- No unbounded experimentation: each experiment above has a specific hypothesis and success criterion.
- No mechanism added without a physical motivation document-able in one paragraph.
- No H20 launch without dry-run + estimated wallclock + SKIP_DONE=1.

---

## 7. What to do tonight (revised 2026-05-09)

✅ Completed during plan review:

1. ✅ Generated 082 combo configs — 6 cells (combo_full + 3 leave-one-out + 2
   dose-response) × 30 seeds = 180 cfg via
   `experiments/082_v4_combo_30seed/generate_configs.py`.
2. ✅ Fixed 081 schema bugs and regenerated:
   - `noise_dist: levy` + `noise_levy_alpha` (was `levy_alpha:` + `noise_dist: t`)
   - `target_dataset: btcusdt` + `target_period: 2024Q1_1m` (was `btc` +
     `2017-2026_daily`, which silently fell back to SPX)
   - Deleted prior 30 baseline + 30 v4combo SPX-masquerading-as-BTC results.
3. ✅ Added numerical-stability filter to `scripts/score_phase.py`: rejects
   seeds with conditional_kurtosis>100, aggregational_gaussianity>1000, or
   any fact NaN/inf. Reports rejection count separately. Validated on 078
   (24/90 rejected, all from `asymdrag_a09` over-strong cell).
4. ✅ Wrote `scripts/h20_branch_e_combo.sh` with pre-launch checks (schema
   verify, disk free, no orphan torchrun, GPU presence) and per-phase
   scoreboard auto-emit.
5. ✅ Smoke-tested combo_full on Mac (n_agents=256, n_steps=200): finite
   returns, std=0.0129, no NaN. All 4 mechanisms compose without blowup.
6. ✅ Re-ran V4 unit tests (27 tests pass).

⏳ Next:

7. Push branch to GitHub.
8. SSH H20, pull, run `bash scripts/h20_branch_e_combo.sh --dry-run` for
   sanity check, then `DAEMON=1 bash scripts/h20_branch_e_combo.sh`.
9. B-round implementation **waits until 082 results are in**. Do not pre-
   implement B1-B4 — wastes time on mechanisms we may not need.

---

## 8. Decision log

| date | decision | rationale |
|---|---|---|
| 2026-05-06 | Reject honest-ceiling fallback; pursue v4 mechanisms | User directive; results support physics hypothesis |
| 2026-05-07 | Commit to 082 combo as Paper A's decisive experiment | 9/11 winners all fail the same 2-3 facts → combo is necessary |
| 2026-05-07 | Defer B-round implementation until 082 results | Avoid wasted code if A-round succeeds |
| 2026-05-07 | Target ICML 2027 main, not NeurIPS 2026 | Timeline; substance over deadline |
| 2026-05-09 | Restructure 082 as 6-cell leave-one-out + dose-response | Original 4-cell plan didn't include any all-4-mechanism flagship; ablation needed |
| 2026-05-09 | Fix 081 BTC bugs: Lévy schema + dataset key | Prior 30 baseline runs had silently used SPX (trainer fallback path); cross-asset story was fake |
| 2026-05-09 | Add numerical stability filter to scorer | Composing 4 mechanisms may amplify variance; need to drop blow-ups before counting |
| 2026-05-09 | Add B4 (power-law force tail) to B-round roster | Lévy alone doesn't fix hill_tail (verified: 1/30 pass in 077 levy_a19) — need a force-shape mechanism |
