# exp 124 Phase 2 — PRE-REGISTRATION (real order-flow non-equilibrium test)

**Status:** BINDING. To be frozen + arXiv'd (or OSF) **before any real L2 data is touched** (project
pre-registration clause; see `memory/feedback_preregistration.md`). **Nothing below may change after the
data lands**; any deviation is logged + justified in a Deviations section and the result reported both ways.

**Date drafted:** 2026-06-21. **Depends on:** Phase 1 (sim) frozen prediction — `DESIGN.md`,
`ofi_{transient,entropy}_*.json`, `ofi_tau_report.json`. **Analysis code (pre-committed before data):**
`null_test_crash_tails.py` generalized returns→OFI (a `--observable ofi_memory|ofi_tail|ofi_sat` flag),
plus `analyze_crash_tails.py` helpers.

## 1. Background + the sim prediction being tested
Real return tails are stationary (exp 123 Stage 3: pooled Δα z=+1.03, refuted). The NCS thesis: the
non-equilibrium driving lives in **order flow**, not returns. Phase 1 (sim) makes a sharp, frozen
prediction: a coordinated-liquidation shock drives a **sharp order-flow-MEMORY spike toward perfect
persistence** (lag-1 OFI autocorrelation 0.02→~1.0), with a **monotonic sigmoid dose-response** (onset
~0.1–0.2σ), **generalizing across assets** (vol-dependent threshold), and a **sharp relaxation**
(τ_OFI≈22 steps, ~10× faster than the return-tail τ_ED≈236). The sign-level entropy-production proxy
was **flat** (E-S3) → the predicted signature is **persistence/coherence, not entropy production**.

## 2. Hypotheses (directional, pre-registered)
- **H1 (primary).** At real crash onsets, windowed OFI memory **rises above its pre-crash baseline**
  (Δmem ≫ 0), beyond the calm-null distribution, and **relaxes** (sharp, returns toward baseline).
- **H2 (discriminating).** This occurs **where the return tail is stationary** (the same windows show
  no significant return-tail change), i.e. the signature is order-flow-specific.
- **H3 (secondary, supporting).** OFI tail heavies (Δα_OFI<0) and/or OFI saturation rises (Δsat>0).
- **H0 (null).** OFI memory shows no crash-localized burst beyond the calm null → order flow is also
  stationary.

## 3. Data
- **Source:** Tardis.dev L2 (BTC-USDT + ETH-USDT), 6 months, full book changes + trades. Provenance
  file (source, download date, license, preprocessing hash) per data discipline.
- **Window choice (frozen before purchase):** the 6-mo span is chosen to contain **≥2 stress episodes
  + a long calm stretch** (confirm Tardis coverage before buying).
- **Episode selection (from PRICE ALONE, before any OFI computation):** a *stress episode* = a
  drawdown ≥ **15%** within ≤ **72 h**; onset t0 = the local price maximum immediately preceding it.
  *Calm windows* = max 72-h drawdown < **5%**, ≥ 7 days from any stress episode; the longest calm
  stretch is the **null source**.
- **Binning:** event-level L2 → fixed Δt bins; **Δt = 1 s primary**, Δt = 60 s as a robustness check.
- **Windows (match the sim/returns protocol):** pre = 5 days before t0; crash = 2 days from t0.

## 4. Observables (precise; frozen)
- **OFI** (per bin): Cont–Kukanov–Stoikov order-flow imbalance — signed best-level depth changes +
  signed trade flow, summed within the bin.
- **OFI memory (PRIMARY)** = lag-1 autocorrelation of the signed binned OFI within a sliding window
  (W = 3600 bins, stride = 600 for Δt=1s; scaled for Δt=60s).
- **OFI tail (secondary)** = Hill index of |OFI| increments (k_frac=0.1).
- **OFI saturation (secondary)** = fraction of |normalized OFI| > 0.5.
- **EP proxy: NOT used** as a gate (E-S3 flat in sim; finer estimator = future work / Paper B).

## 5. Statistic + null (mirrors `null_test_crash_tails.py`, returns→OFI)
For each observable: **Δ = obs(crash 2d) − obs(pre 5d)**. **Null distribution:** slide the same
(5d-pre, 2d-event) window-pair across the calm stretch (stride = 12 h) → distribution of Δ under
no-crash. Per-episode **z** and one-sided **p** (P(null ≥ Δ) for memory; P(null ≤ Δ) for the tail);
**pooled** across episodes.

## 6. Decision gates (BINDING)
- **G-main → POSITIVE (NCS-credible).** Primary (OFI memory) Δmem significant in the predicted
  direction (one-sided **p ≤ 0.05** vs the calm null) on **≥ 2 independent crash episodes**, AND H2
  holds (return-tail Δα not significant on those episodes), AND it survives §7 controls.
- **G-null → NEGATIVE.** OFI memory not significant on any episode → order flow is also stationary →
  fold into the honest NeurIPS/TMLR paper ("even order flow shows no transient"); **NCS dies.** Report
  straight (no gate-shopping; see `memory/feedback_no_downgrade.md`).
- **G-partial.** Significant on 1 episode only, or fails a §7 control → mechanism study; **no NCS
  discovery claim.**

## 7. Controls (BINDING — surrogate-kill + sanity-cascade clauses)
1. **Vol-confound.** Recompute OFI memory on **vol-standardized** OFI (÷ local realized OFI scale,
   as in Stage 3 for returns). The burst must survive — else it is a volatility artifact.
2. **Reversibility surrogate.** An IAAFT / AR(1) surrogate matched to the **calm** OFI autocorrelation,
   given a placebo onset, must **not** produce a Δmem burst — else memory bursts are an autocorr artifact.
3. **Placebo onsets.** Random non-crash onsets within the crash episode's own series must not produce
   the burst (this is the null test, applied in-episode).
4. **Returns cross-check (= H2).** The identical windows on returns must be stationary (Δα null), per
   exp 123 — the discriminating condition.
The signature must pass **all four**. Any single failure ⇒ G-partial at best.

## 8. Multiple comparisons
**OFI memory is the sole primary/gating observable** (fixed by Phase 1 — no observable-shopping). Tail
and saturation are reported as supporting, non-gating. The "≥2 episodes" requirement controls the
family-wise rate across episodes. We report all observables × all episodes regardless of outcome.

## 9. What confirms / falsifies
- **Confirms (NCS route alive):** G-main — a sharp, vol-robust, surrogate-surviving OFI-memory burst
  at ≥2 crashes where returns are stationary.
- **Falsifies (NCS route dead):** G-null — order flow stationary too; the EcoMD transient is sim-only
  across both returns and order flow. (Still a clean, publishable boundary for the NeurIPS/TMLR paper.)

## 10. Paper-A / Paper-B carve-out
Paper A (→ NCS) claims the **order-flow MEMORY/coherence transient** + the EcoMD prediction/counterfactual
(computational). Entropy production / TUR / fluctuation-theorem **laws** stay in **Paper B** (Nature
Physics). This PREREG deliberately does **not** gate on EP, keeping the lanes separate.

## 11. Compute / sequencing
Tardis $4–5k (commit only when **Paper B** greenlights the buy — Paper B needs L2 regardless). L2
reconstruction CPU-heavy (days; H20-4 CPU node; storage → R2). Analysis with the pre-committed code.
arXiv this PREREG before reconstruction begins.
