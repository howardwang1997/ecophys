# Pre-registration — Paper A week sprint (2026-06-09)

**Repo SHA at pre-registration:** `e30eac182` (feature/exp113-gabaix-solve)
**Author:** A. Hall · **Status:** frozen *before* any new results exist.

This document pre-registers two confirmatory analyses for Paper A's concave √-impact
solve, **before** the corresponding runs are launched, to immunize them against
optional-stopping / gate-shopping critique. The analysis scripts named below are frozen at
the SHA above and will not be edited after results land.

Context: exp 113/114 established the concave-impact solve. The 114 verdict (2026-06-06) was
**physics gate 5/5, strict per-asset statistical gate 2/5** (spx, btc significant; ndx/gold/
eurusd n.s. at the pre-registered Bonferroni α_eff=0.002), with the miss attributed to power
(n=30 at α_eff=0.002 powers only d≳1.0). The δ\* universality fit was noise-limited on 2-point
arms for 4 of 5 assets. The weekend SOTA-break (G1, exp 115) and SV-composition method legs
**failed** and are dropped per the 114 fallback ladder; Paper A's honest spine is now
**diagnose (3-paradigm ceiling) + concave-impact mechanism solve + δ\*≈0.5 universality**.

---

## A. Power top-up: ndx / gold / eurusd, n = 30 → 60

**Hypothesis (unchanged from 114):** for each asset, the concave_d050 (δ=0.5, TLB √-law) cell
moves the tail index into band and beats its own baseline.

**Pre-declared design (frozen now):**
- Assets: **ndx, gold, eurusd only** (the three n.s.-at-n=30 cells). spx and btc are NOT
  topped up (already significant; topping them up would be outcome-dependent selection).
- Cells: `baseline` and `concave_d050`, **seeds 30–59** appended to the existing seeds 0–29
  in `experiments/114_concave_confirm/` (→ n=60 per cell). Identical recipe to 114
  (108 baseline_mmd base, reg_every=4, fixed δ=0.5, n_agents unchanged).
- **Sample size is fixed at n=60. No interim peeking, no further extension** regardless of the
  n=60 p-values. n=60 is the final, only top-up.
- Gate statistic and threshold are **unchanged** from 114's pre-registration
  (`scripts/score_concave_confirm.py`): per asset, `concave_d050` vs that asset's `baseline` —
  **hill ∈ [2,4] AND acf² ∈ [0.15,0.55]**, Welch t (one-sided, concave > baseline on Δnet),
  **Bonferroni m=5, α_eff = 0.002**.
- **Decision rule (frozen):** report BOTH the originally-pre-registered n=30 result and the
  n=60 result. The n=60 per-asset gate is the primary; the paper states the gate as "k/5 assets
  pass at n=60 (α_eff=0.002), 2/5 at the original n=30." No gate is declared retroactively.
- **Power justification:** at d≈0.5–0.6 (the 114 observed effect sizes for the 3 misses),
  n=60 lifts power at α_eff=0.002 from ~0.35 to ~0.70 — enough to detect the effect if real,
  not enough to manufacture one (the physics gate is already 5/5 and pooled Stouffer p≈1e-8,
  so the effect's existence is not in question; this only sharpens per-asset resolution).
- **Honest fallback:** if n=60 still yields <4/5, the paper reports the per-asset gate as
  power-limited and leans on the pooled + physics evidence. We do NOT escalate n further.

## B. δ-grid extension: hill(δ) lever arm → ≥6 points / asset

**Hypothesis:** the √-law crossing δ\* (δ where hill(δ)=3, the empirical inverse-cubic) is
universal across markets at δ\*≈0.5.

**Pre-declared design (frozen now):**
- Add fixed-δ concave cells **δ ∈ {0.35, 0.55}** for **all 5 assets**, n=30, appended into
  `experiments/118_delta_grid/<asset>/` (pools via `scripts/score_delta_grid.py`). For
  **btcusdt** also (re)generate **δ ∈ {0.40, 0.60}** (the 118 btc cells that never ran due to
  an H20-clone bug, not a data gap — btc parquet is present locally).
- Resulting per-asset δ arm: spx {0.35,0.40,0.45,0.50,0.55,0.60,0.70} (7); ndx/gold/eurusd
  {0.35,0.40,0.45,0.50,0.55,0.60} (6); btc {0.35,0.40,0.45,0.50,0.55,0.60} (6).
- **Universality criterion (frozen, already in `score_delta_grid.py`):** per-asset OLS
  hill = icpt + slope·δ over all per-seed points; δ\* = (3−icpt)/slope; bootstrap 95% CI on δ\*
  by resampling seeds within each δ cell. **√-law is UNIVERSAL iff every asset's δ\* 95% CI
  covers 0.5.** Assets with a CI excluding 0.5 are reported honestly as asset-specific
  deviations, not hidden.
- No δ points will be added or dropped after seeing the fit. Seed count fixed at n=30/cell.

---

## Optional-stopping / gate-shopping mitigations (summary)
1. Sample sizes (n=60 top-up; n=30/δ-cell) and δ grids are fixed in this document **before**
   launch.
2. Decision rules and thresholds are the **frozen** scorer scripts at SHA `e30eac182`
   (`score_concave_confirm.py`, `score_delta_grid.py`); they will not be edited post-hoc.
3. Both the original (n=30) and topped-up (n=60) numbers are reported — no silent replacement.
4. Asset selection for the top-up (ndx/gold/eurusd) is the pre-declared set of n=30 misses, not
   chosen after seeing n=60 outcomes.
