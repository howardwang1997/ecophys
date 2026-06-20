# exp 124 — order-flow non-equilibrium transient (the NCS experiment plan, Route A)

**Date:** 2026-06-20. **Purpose:** the concrete, pre-registerable experiment plan that would make
Paper A → **Nature Computational Science** viable. Strategy context:
`papers/proposal/paper_a_ncs_viability_routes_2026-06-19.md`; bucketed work-list:
`paper_a_ncs_worklist_2026-06-19.md`.

## 0. NCS thesis (what a positive result would claim)
Real return tails are stationary (exp 123 Stage 3, refuted the return-tail transient). The
non-equilibrium driving, if present in real markets, lives in **order flow**. EcoMD predicts a
specific signature; we test whether real crash order-flow shows it, distinguishing genuine
non-equilibrium driving from stationary tails. *Positive ⇒ a real-market discovery enabled by the
differentiable simulator ⇒ NCS-credible. Negative ⇒ order flow is also stationary ⇒ folds into the
honest NeurIPS/TMLR paper.*

## 1. The simulator's prediction (already in hand — exp 123 OFI)
With OFI logging (commit e19d868b5), the sim already makes a sharp prediction (`ofi_transient_spx.json`):
a **coordinated-liquidation shock drives an order-flow transient** — lag-1 OFI memory $0.02\!\to\!0.99$
at the shock, $|ρ|$ and saturation burst, all **relaxing** — while an exogenous price gap is inert and
the return *tail* barely moves. So the sim predicts: **real crash order-flow shows a coherence/memory
burst-and-relax that the return tail does not.** Phases 1–2 sharpen this into a pre-registered test.

---

## Phase 1 — sharpen the prediction (sim; runnable NOW, no data buy; GPU)
*No-regret: also strengthens the NeurIPS/TMLR paper and freezes the real-data prediction.*

- **E-S1 — OFI dose-response.** Re-run the spx `kick` dose sweep {0.05…12} WITH OFI logged; measure
  the OFI-memory/|ρ|/saturation peak vs dose. *Predicts how the OFI signature scales with crash
  severity.* (~1 GPU window; reuse ckpt.)
- **E-S2 — cross-asset OFI.** control + kick6 (OFI) on the other 4 assets (ndx, gold, btc, eurusd).
  *Predicts the OFI signature generalizes.* (~1 GPU window.)
- **E-S3 — time-asymmetry / entropy-production proxy.** Define an irreversibility statistic on the
  discretized $(\Delta p_t, \text{OFI}_t)$ process (KL between forward and time-reversed 2-step
  transition distributions — a standard entropy-production estimator); show it bursts-and-relaxes at
  the shock. *Makes the non-equilibrium claim quantitative.* (analysis on Phase-1 trajectories.)
  **⚠ Paper-B carve-out:** lead Paper A with OFI memory/coherence (computational); entropy-production
  is SUPPORTING here — the full thermodynamic-law treatment (TUR/Jarzynski) stays in Paper B.
- **E-S4 — relaxation timescale $\tau_{\text{OFI}}$.** Exp-fit the OFI-memory recovery; compare to the
  tail's $\tau\!\approx\!240$. *Predicts the real-data recovery time.* (analysis.)

Phase-1 deliverable: a frozen, quantitative prediction (which observable, what shape, what
dose-scaling, what timescale) — the pre-registration target for Phase 2.

---

## Phase 2 — the decisive real-data test (gated on Tardis L2 buy; CPU-heavy)

### Data (E-R1)
Tardis.dev L2 (BTC+ETH, 6 mo, book changes + trades), the 6-mo window chosen to **span ≥2 real stress
episodes + matched calm controls** (confirm coverage before buying). Reconstruct the order book →
**OFI** (Cont–Kukanov–Stoikov: signed best-level depth changes per bin) + the same derived observables.
Provenance file; crash/calm windows frozen before analysis.

### Observables (precise; match the sim)
| observable | real (L2) | transient predicts |
|---|---|---|
| OFI memory (lag-1 autocorr of signed OFI) | from reconstructed OFI | $\Delta\text{mem}\gg 0$ at crash (the headline) |
| OFI tail (Hill of \|OFI\| increments) | | $\Delta\alpha_{\text{OFI}} < 0$ (heavier) |
| OFI saturation (frac \|normalized OFI\|>θ) | | $\Delta\text{sat} > 0$ |
| time-asymmetry / EP proxy (E-S3 statistic) | | burst $>0$ (supporting) |

### Test (E-R2) — pre-registered, mirrors `null_test_crash_tails.py`
For each observable, statistic $\Delta = \text{obs(crash 2d)} - \text{obs(pre 5d)}$, vs a null
distribution from a long calm window (sliding window-pairs). Per-episode z + p; pooled across episodes.
**Generalize `null_test_crash_tails.py` from returns→OFI.**

### Framework validation (E-R3 / Phase 3)
Calibrate EcoMD to the real OFI statistics; show it **predicts** the real OFI transient (shape /
dose-scaling / $\tau$) — the differentiable-simulator-enabled counterfactual that is the NCS hook.

---

## Decision gates (BINDING, pre-register before touching real data)
- **G-main (POSITIVE).** ≥1 of {OFI memory burst, OFI tail heavier, EP burst} passes the null test
  (significant in the predicted direction AND recovers) on **≥2** real crash episodes, where the
  *return* tail did not → real-market non-equilibrium discovery → **NCS-credible**.
- **G-null (NEGATIVE).** No observable passes on any episode → order flow is also stationary → fold
  into the honest NeurIPS/TMLR paper ("even order flow shows no transient"); **NCS dies**, but the
  result strengthens the stationarity story + serves Paper B. *(Report straight; no gate-shopping.)*
- **G-partial.** Signature present but weak / 1 episode → mechanism study; do not claim NCS discovery.

## Compute / cost / timeline
- **Phase 1:** GPU (existing fleet), ~2 windows + analysis; **no buy**; ~1 week.
- **Phase 2:** Tardis **$4–5k**; L2 reconstruction CPU-heavy (days; H20-4 CPU node, storage tens–hundreds
  GB → R2); analysis; **6–10 weeks**.
- Commit the Tardis buy **only when Paper B greenlights it** (Paper B needs L2 regardless); then Paper
  A's NCS shot is an opportunistic add-on. Phase 1 is worth running now regardless.

## Honest probability
P(real OFI transient exists) ≈ 30–45%; P(NCS-grade + accepted + carved cleanly from Paper B | signal)
≈ 30% → **joint ≈ 10–18%**. Phase 1 is no-regret (sharpens the prediction, strengthens NeurIPS/TMLR);
Phase 2 is the real bet. Calibrated home remains TMLR if NCS does not land.

## Pre-registration note
Before Phase 2, freeze + arXiv a PREREG (`PREREG_2026-XX.md`): the chosen observable(s), crash/calm
windows, null construction, thresholds, and the binding gates above — per the project's pre-reg clause.
