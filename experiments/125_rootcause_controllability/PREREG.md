# exp 125 — PRE-REGISTRATION (BINDING)

**Status:** BINDING. Frozen **before the H20 runs**. Per the project pre-registration clause
(`feedback_preregistration.md`) and the no-downgrade rule (`feedback_no_downgrade.md`): **all arms are
reported regardless of outcome; no arm/observable/threshold may change after the runs**; any deviation
goes in a Deviations section and is reported both ways. The honest-framing guardrail for the user's
"report more positive results" request: **each prediction below is pre-committed to a positive-content
statement for *either* outcome** — we never need a negative to be the headline, and we never hide one.

**Date frozen:** 2026-06-29. **Design:** `DESIGN.md`. **Reframe:** `papers/proposal/paper_a_rootcause_and_reframe_2026-06-29.md`.

---

## H-A (rigor). No hypothesis test — estimation only.
Report mean + 95% CI (bootstrap over ≥30 seeds) for every headline number. **Pre-committed framing:**
the signature is reported *with error bars* either way; if a CI crosses a "strong" threshold we say so.

## H-B (controllability atlas). Mechanism-robustness.
- **Prediction B1:** `temperature_spike` and `liquidity_drop` (the two *non-mechanical* drivers) each
  **revive** the heavy-tail-and-relax + OFI-memory burst (α_ED dip ≥ 2 below control; |ρ| spike and
  OFI-memory burst beyond the control band), on ≥3 of the 4 assets, at sufficient dose/dur.
- **Prediction B2:** `price_jump` stays **inert** (replicates exp 123 Stage 2b).
- **Decision / pre-committed framing (positive either way):**
  - If B1 holds → **"the driven transient is mechanism-robust"**: ≥2 distinct, market-meaningful,
    non-mechanical drivers produce it; the state_kick is not special. (Strong positive; headline.)
  - If B1 fails (temp/liq inert like price_jump) → **"the transient is specifically a coordination /
    coherence phenomenon, not generic agitation or liquidity loss"** — a *sharper mechanism result*
    (only coherent displacement drives it). (Still positive; reframes the mechanism, does not headline
    a "failure".)
  - Report the full channel × observable atlas table regardless.

## H-C (relaxation law). Functional form of τ(dose).
- **Prediction C1:** τ_ED(dose) is **monotone increasing** and well-fit (R² ≥ 0.9) by at least one
  pre-specified form: power-law τ ∝ (m − m_c)^{−z}, logarithmic, or saturating. The sigmoid
  dose-response sharpens with n = 20 (onset 0.1–0.2σ).
- **Pre-committed framing:** report the **best-fit form + parameters with CIs**; if power-law with
  m_c > 0 fits best, report it as critical-slowing-down-like *without* claiming a true critical point
  (criticality was ruled sharp-N_c-negative in exp 116/120 — say so). Either way the law is the result.

## H-D (root cause — the new core). Why the steady tail is light.
- **H-D1a/b (Route A — heavy micro-noise).** *Prediction:* heavier bath noise **fattens the
  steady-state tail** — α_ED decreases monotonically as df↓ (Student-t) and as α_levy↓ — and a
  **trained** Lévy model (D1b) reaches a heavy stationary tail, **at a measurable volatility-clustering
  cost** (ACF²(r²) drops as the tail fattens).
  - *Decision / pre-committed framing (positive either way):*
    - If heavy noise installs a stationary heavy tail with a clustering cost → **"we identify the exact
      missing ingredient (a stationary heavy source) and quantify the tails-XOR-dynamics Pareto cost"**
      (confirms §3 Route A; the central positive mechanism result).
    - If heavy noise does **not** produce a heavy stationary aggregate tail → **"even an
      infinite-variance bath self-averages away — the light tail is an even stronger structural
      property than CLT alone predicts"** (still positive; strengthens the fundamental claim).
- **H-D2 (CLT self-averaging).** *Prediction:* at **fixed trained dynamics**, the steady-state α_ED
  **increases (lighter) with N** (a clear positive trend over N ∈ {1e2…3e4}).
  - *Decision / framing:* a rising α_ED(N) is the **direct interventional signature of self-averaging**
    — the mechanistic proof for §2 P2 (headline mechanism figure). If α_ED(N) is **flat**, the light
    tail is *not* from aggregation and we revise toward the single-agent Boltzmann tail (P1) as the
    cause — reported as a refinement, not a failure. (Either outcome localizes the cause.)
- **H-D3 (coupling).** *Prediction:* steady α_ED heavies only near a coupling threshold. Exploratory;
  no gate. Report if run.

## H-E (transferable pitfall). *Prediction:* the neural-SDE baseline shows the **same** warm-up Hill
inflation (no-discard heavier than discard-50). *Framing:* positive → "the warm-up audit is a
transferable evaluation protocol, validated on 2 generator families"; if the 2nd generator does *not*
show it → "the pitfall is specific to off-equilibrium-initialized rollouts" (a precise scope, still a
usable protocol statement).

---

## Estimators (frozen)
- **Steady-state α_ED:** windowed Hill (k_frac=0.1) on excess demand, **warm-up [0,500) discarded**,
  averaged over the steady window [500,3000) (pre-shock for shocked arms).
- **Post-shock min α_ED / τ_ED:** as exp 123 (`score_transfer_law.py`, `fit_relaxation_tau.py`).
- **OFI memory / |ρ| / saturation:** as exp 124 Phase 1 (`analyze_sim_ofi_transient.py`, `fit_ofi_tau.py`).
- **11 facts:** `compute_all` (warm-up-discarded returns), as the Pareto-ceiling scoring.
- **Dip-window excess kurtosis:** floor-free heaviness, `analyze_transient_extras.py`.
- **CIs:** non-parametric bootstrap over seeds (≥30 for G-A, ≥20 elsewhere); report 95%.

## Multiple comparisons / no gate-shopping
G-D2 (α_ED vs N) is the **single primary mechanism test**. G-D1 is the primary Route-A test. All other
arms are characterization, reported in full. No observable is promoted post-hoc. Every asset × arm ×
observable is tabulated regardless of significance.
