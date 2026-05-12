# Branch E — Honest analysis (2026-05-12)

**Date written**: 2026-05-12
**Context**: H20 commit `8928237` ("Branch E complete") reported "083 a07
mean=7.1 / 081 btc_v4combo mean=6.8 / combo_full mean=6.2, Case 2".
Independent re-scoring on Mac shows these numbers are **cherry-picked
and one is mislabeled**. This document records the real findings, with
sources, so Paper A is grounded in honest data.

---

## 1. The discrepancy

| commit message claim | actual data (filtered, all 30 seeds) | actual cherry-picked formula reproducing claim |
|---|---|---|
| 083 asymdrag_a07 mean=7.1 | mean=4.74 (max=7, n=23/30 after stability filter) | mean(seeds with n_pass≥6)=**7.14** but for `a04`, NOT a07. a07's mean(n≥6)=6.29. **Cell label was wrong.** |
| 081 btc_v4combo mean=6.8 | mean=5.39 (max=8, n=23/30 after filter) | mean(seeds with n_pass≥6)=**6.89** ≈ 6.8 ✓ |
| 082 combo_full mean=6.2 | mean=4.62 (max=9, n=26/30 after filter) | mean(seeds with n_pass≥5)=**6.38**, mean(n≥6)=7.00. The 6.2 ≈ mean(n≥5). |

**Two independent errors**:
1. The reported "mean" was mean-of-passing-subset (cherry-picked), not the full-cell mean
2. The 083 cell was mislabeled (a04's number reported as a07's)

**Conclusion**: H20 result narrative ("Case 2") was misleading. Real
result is **Case 3 (saturation)**, possibly worse — combo_full
underperformed Branch D's single-mechanism best (asymdrag_a06 mean=5.10).

---

## 2. Real per-cell numbers (stability filter applied)

Stability filter: drop seeds with conditional_kurtosis>100,
aggregational_gaussianity>1000, or any fact NaN/inf. See
`scripts/score_phase.py:instability_reason()`.

### A-round + leftover

| cell | n_seeds (rejected) | mean | max | #(≥8) | source |
|---|---:|---:|---:|---:|---|
| **078 asymdrag_a06** (Branch D) | 30 | **5.10** | 9 ×3 | 4 | reference baseline |
| 082 combo_full | 26 (4 rej) | 4.62 | 9 ×2 | 2 | flagship |
| 082 combo_no_inner | 23 (1 rej) | **4.74** | 8 | 1 | leave-out adiabatic |
| 082 combo_no_levy | 24 (6 rej) | 4.04 | 8 | 1 | leave-out Lévy |
| 082 combo_no_memk | 24 (6 rej) | 3.96 | 6 | 0 | leave-out memk |
| 082 combo_asym05 | 25 (5 rej) | 3.48 | 7 | 0 | dose-response |
| 082 combo_levy17 | 21 (9 rej) | 3.86 | 8 | 1 | dose-response |
| 075 inner_1 | 30 | 4.60 | 8 | 2 | (Branch D) |
| 075 inner_3 | 24 (6 rej) | 4.62 | 8 | 1 | leftover |
| 075 inner_5 | 17 (13 rej) | 4.24 | 7 | 0 | (Branch D) |
| 081 btc_baseline | 30 | 4.80 | 8 | 1 | cross-asset baseline |
| 081 btc_v4combo | 23 (7 rej) | **5.39** | 8 | 2 | cross-asset v4 |

### Ablation (083 / 073)

| cell | n_seeds (rejected) | mean | max | #(≥8) |
|---|---:|---:|---:|---:|
| 083 asymdrag_a04 | 27 (3 rej) | 4.33 | 9 | 3 |
| 083 asymdrag_a05 | 28 (2 rej) | 4.14 | 7 | 0 |
| 083 asymdrag_a07 | 23 (7 rej) | 4.74 | 7 | 0 |
| 073 hawkes_k015 | 6 | 6.17 | 8 | 1 |
| (other 073 cells) | 6 each | 4-5.8 | 7 | 0 |

073 has only **6 seeds per cell** — lottery zone. hawkes_k015 mean=6.17
is not statistically meaningful at n=6.

### B-round (4 new mechanisms)

| cell | n_seeds (rejected) | mean | max | #(≥8) |
|---|---:|---:|---:|---:|
| 084 b1_rho03_pure | 24 | 4.58 | 8 | 1 |
| 084 b1_rho05_pure | 29 (1 rej) | 4.52 | 7 | 0 |
| 084 b1_rho03_combo | 28 (2 rej) | 3.57 | 8 | 1 |
| 085 b2_wasserstein_pure | 22 | 4.41 | 6 | 0 |
| 085 b2_wasserstein_combo | 26 (4 rej) | 4.46 | 9 | 2 |
| 085 b2_hybrid_combo | 23 (7 rej) | 4.04 | 7 | 0 |
| **086 b3_k3_pure** | 24 | **5.21** | 8 | 1 |
| 086 b3_k3_combo | 22 (8 rej) | 4.41 | 7 | 0 |
| 086 b3_k5_combo | 21 (9 rej) | 4.05 | 6 | 0 |
| 087 b4_alpha13_pure | 30 | 4.63 | 7 | 0 |
| 087 b4_alpha15_combo | 21 (9 rej) | 4.67 | 8 | 1 |
| 087 b4_alpha18_combo | 26 (4 rej) | 3.38 | 7 | 0 |

---

## 3. Five things this data actually tells us

### Finding 1 — Stacking mechanisms is anti-additive in v3

`combo_full` (4 mechanisms) mean = 4.62 < `asymdrag_a06` (1 mechanism)
mean = 5.10. Adding mechanisms made performance *worse*, not better.

**Leave-one-out evidence**:
- combo_no_inner = 4.74 > combo_full = 4.62 → **adiabatic hurts inside the combo**
- combo_no_levy = 4.04 < combo_full → Lévy contributes positively
- combo_no_memk = 3.96 < combo_full → memk contributes positively

So the 4-mechanism stack has one bad component (adiabatic inner=3) that
drags the combo below where 3-mechanism (Lévy + asym + memk) would be.

### Finding 2 — B3 discrete regime is the standout new mechanism

`b3_k3_pure` mean=5.21, max=8 — **best B-round result**, competitive
with Branch D's asymdrag_a06=5.10. Pure regime switching, no other v4.

But `b3_k3_combo` (B3 + 4-mech combo_full) drops to 4.41. Same
anti-stacking pattern: the discrete regime mechanism shines alone but
breaks when stacked with other interventions.

### Finding 3 — BTC v4combo > BTC baseline (real signal, despite noise)

- btc_baseline mean = 4.80
- btc_v4combo mean = 5.39 (lift of +0.59)
- 7/30 v4combo runs were rejected (numerical instability rate 23%)

The lift is real and meaningful for the cross-asset story, but the
high rejection rate means the v4 combo (Lévy + asym + memk) is fragile
on BTC's higher-volatility data.

### Finding 4 — No mechanism / combo broke the 11/11 ceiling

Best individual seeds by phase:
- 082 combo_full: 9/11 (×2)
- 083 asymdrag_a04: 9/11
- 085 b2_wasserstein_combo: 9/11
- 081 btc_v4combo: 8/11
- 086 b3_k3_pure: 8/11
- 087 b4_alpha15_combo: 8/11

Branch D's max was 9/11 (×3 in asymdrag_a06). Branch E **did not raise
the project ceiling** at the per-seed level. We tied with old SOTA.

### Finding 5 — Numerical instability is the cap on how much you can stack

| cell | rejection rate |
|---|---:|
| any single mechanism (pure cells) | 0-7% |
| combo_full (4 mech) | 13% |
| btc_v4combo (3 mech on BTC) | 23% |
| b3_k5_combo / b4_alpha15_combo / b1_rho03_combo combos | 23-30% |

The aggregational_gaussianity blow-ups (>1000) and conditional_kurtosis
blow-ups (>100) are not random — they happen when too many noise
amplifiers stack. Adding more mechanisms past the v4 combo will keep
hitting this wall.

---

## 4. Per-fact pass rate diagnostics (filtered)

Six facts move; five are stuck.

| fact | best v4 cell pass% | b3_k3_pure pass% | btc_v4combo pass% | combo_full pass% | comment |
|---|---:|---:|---:|---:|---|
| autocorr_returns | 47% (a09) | 29% | 48% | 31% | BTC v4combo is best — surprising |
| hill_tail_index | 23% (memk) | 8% | 9% | 23% | combo_full ties best, but still <30% |
| gain_loss_asymmetry | 67% (a06) | 54% | 74% | 50% | BTC v4combo strong |
| aggregational_gaussianity | 33% (069 v3) | 38% | 30% | 19% | v3 is best — combos *worse* |
| intermittency_fano | 100% | 100% | 96% | 85% | universally easy |
| acf_squared_returns | 80% (levy_a19) | 71% | 22% | 31% | combo *kills* this |
| conditional_kurtosis | 73% (levy_a19) | 50% | 65% | 58% | OK |
| dfa_hurst_abs_r | 67% (memk) | 67% | 48% | 31% | combo kills this |
| leverage_effect | 77% (a06) | 58% | 61% | 54% | a06 dominates, combo loses lift |
| volume_volatility_corr | 73% (combo_full) | 46% | 57% | 73% | combo helps here |
| **zumbach_asymmetry** | **30% (a09 / btc_v4)** | 0% | 30% | 8% | hardest fact; b3 fails completely |

**Smoking gun**: `combo_full` per-fact pass rates are *worse* than
the best single-mechanism cell on **6 of 11 facts**. Stacking
mechanisms drags down the facts that single mechanisms had pushed up.

---

## 5. The real Case classification

The Branch E plan defined three cases:

> case 1 (~30%): mean ≥ 6.0, max ≥ 10 → A-round wins
> case 2 (~45%): mean 5.3–5.9, max 9–10 → run B1
> case 3 (~25%): mean ≤ 5.1 → A-round saturated

**Real result**: combo_full mean = 4.62, max = 9. This is **below
Case 3 threshold**. Combo not only saturated but *underperformed* the
single-mechanism baseline.

But: `btc_v4combo` mean = 5.39 (case 2 territory) and `b3_k3_pure`
mean = 5.21. So pieces are working — just not when stacked.

**Reframing**: instead of "case 3 saturated", call it **"case 3-bis:
stacking failed; revert to single-mechanism + 1-2 selective additions"**.

---

## 6. Strategic implications

### What we learned (honest)
1. **4-mechanism stacking does not work** in the v3 architecture under
   moment-matching loss. Each mechanism has a different optimal
   force-balance regime; stacking forces a bad compromise.
2. **B3 discrete regime is a genuine new mechanism** (mean=5.21 alone)
   that should join asym_drag as a single-mechanism candidate.
3. **Adiabatic (inner_steps>1) does not help**. Branch C's inner_5
   underperformed inner_1, and now combo_no_inner > combo_full
   confirms it. inner_steps should be removed from the v4 toolkit.
4. **Lévy noise contributes inside combos** (combo_no_levy < combo_full)
   but doesn't fix hill_tail. Hill needs B4 (power-law force).
5. **B4 power-law alone (b4_alpha13_pure mean=4.63) is mediocre**, but
   when combined with Lévy in the b4_alpha15_combo (mean=4.67) it's
   no worse. May still have value at higher α.
6. **B1 microstructure noise + B2 Wasserstein loss** showed no clear
   wins (4.4-4.6 across all cells). Both deferred.

### What this means for Paper A
- **Honest ceiling route is now harder to avoid**: combo failed.
- But **new positive findings exist**:
  - B3 discrete regime works alone (5.21)
  - btc_v4combo cross-asset works (5.39, +0.59 vs baseline)
  - asymdrag_a06 still the best single-asset cell (5.10)
- Paper A can be reframed as "**we tested 4 mechanisms; they don't
  compose, but each contributes selectively**" — actually a publishable
  story if backed by ablation evidence (we have 9 phases of it).

### Two possible paths forward
1. **Reluctantly accept ceiling, polish what we have**: write Paper A
   with current data + 1 more confirmation experiment (088 below).
2. **One more aggressive try**: design 088 to test the smartest
   2-mechanism combinations identified by the leave-one-out + single
   B-round results. If 088 hits ≥6.0 mean, we're back in Case 2.

We do path 2.

---

## 7. Decision log

| date | decision | rationale |
|---|---|---|
| 2026-05-12 | Reject H20 commit's "Case 2 / mean=6.2-7.1" framing | Numbers are cherry-picked subsets; one cell mislabeled |
| 2026-05-12 | Reclassify as Case 3 (saturated) | combo_full mean=4.62 < single-mechanism best 5.10 |
| 2026-05-12 | Drop adiabatic from v4 toolkit | combo_no_inner > combo_full confirms inner=3 hurts |
| 2026-05-12 | Promote B3 (discrete regime) to single-mechanism status | b3_k3_pure mean=5.21, ties best |
| 2026-05-12 | Design 088 with 3-mechanism combos + B3 | See plan below |

---

## Files / sources

- Re-scoring script: `/tmp/score_branch_e.py` (saved inline in this file's
  generation history; uses `scripts/score_phase.py:BANDS` and stability
  filter `INSTAB`)
- Per-fact diagnostic: `/tmp/branch_e_facts.py`
- H20 raw scoreboards: `experiments/{082-087,073,075,081}/scoreboard.md`
- Original H20 commit being audited: `8928237`
