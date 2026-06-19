# Paper A → NCS: what would make it viable — current status + concrete routes

**Date:** 2026-06-19. Companion to `paper_a_ncs_worklist_2026-06-19.md` (the bucketed work-list) and
`paper_a_dual_track_plan_2026-06-19.md` (venue fit). This doc answers one question: **given the two
negatives, what concrete work would flip NCS from a ~8–15% long shot into a credible submission?**

---

## 1. Current status (recorded)

**What we have (exp 123, all on `feature/exp113-gabaix-solve`):**
- ✅ **Burn-in measurement correction** (solid). Warmup-inclusive rollout scoring misreads an
  equilibration transient as a stationary fat tail; the prior cube-law "solve" was burn-in inflation
  (R1: hill 3.9→6.6 under warmup discard). *This is the load-bearing, defensible contribution.*
- ✅ **In-sim driven transient** under `state_kick`: steady state light (α≈4.7) → shock → heavy
  (α→0.5) → relaxes (τ≈240 deep / ≈20 burn-in), 5/5 assets, sigmoid dose-response. **But:**
- 🔴 **Stage 2b NEGATIVE** — the market-realistic `price_jump` channel does **not** reproduce it
  (α_ED flat ~4.6; α_ret stays light ~6). The transient is **specific to displacing agent latent
  states** = the burn-in mechanism, not a market-shock response.
- 🔴 **Stage 3 NEGATIVE (formal, 5 crashes + null test)** — real return tails are **stationary
  cube-law** in calm and crash (pooled Δα z=+1.03). The transient is **absent in real markets**.

**Why NCS is a long shot now:** NCS desk-screens for a **novel computational method enabling a
positive, broadly-significant discovery**. Our package is a **self-correction + two negatives** on a
**not-first-of-kind** tool (differentiable market sims: Bouchaud-Cont 1998, Dyer 2023–25), with **no
real-world payoff**. That reads as a specialized-methods caveat → high desk-reject risk. **TMLR / PRE
/ NeurIPS-D&B are better-calibrated** for the current package.

**The bar to clear:** add a **positive, real-world-connected, framework-enabled finding** (or a
genuinely novel methodological advance), not another characterization of the (sim-specific) transient.

---

## 2. Route A — order-flow / L2 non-equilibrium transient  (PRIMARY route to NCS)

**Thesis (pre-registered).** Returns are stationary, but microstructure non-equilibrium lives in
**order flow**. At crashes, a windowed measure on **order-flow imbalance (OFI)** shows a transient
dip-and-recover that returns lack; and EcoMD reproduces the OFI signature under driving — including,
possibly, under `price_jump` (which failed on returns but may drive OFI). This is the positive,
real-world, framework-validated discovery NCS needs.

**Why plausible.** Returns are an aggregate that washes out the driving; OFI / queue / depth retain
the arrival–cancellation imbalance where the non-equilibrium physically sits. It's also *consistent*
with our negatives: stationary returns + a transient in the finer order-flow variable is a coherent,
non-trivial story.

### Concrete plan
**Statistic (pre-register 1–2; lead with the non-thermodynamic one to stay distinct from Paper B):**
1. **OFI tail index** — windowed Hill on signed order-flow-imbalance increments *(primary — direct
   analogue of the return test, but on order flow).*
2. **Order-flow memory** — decay/Hurst of signed OFI autocorrelation; crash → transient change.
3. *(secondary/support)* entropy-production rate or TUR slack of the (mid-price, OFI) process — **these
   are Paper B's tools**; use only as corroboration, do not headline (overlap risk, §A-risk below).

**Data.** Tardis L2 (BTC+ETH, 6mo book changes + trades) — **choose the 6mo to span ≥1 real stress
episode + calm controls** (confirm Tardis coverage of the target window *before* buying). Alt:
LOBSTER equity (L10) for the 2010 flash crash (canonical, but pricier). Freeze crash/calm windows +
the statistic + null + threshold **before** analysis (arXiv pre-reg, binding clause).

**Experiments.**
- *Sim:* add **OFI logging** to the EcoMD recorder; run the driven-transient protocol (state_kick
  **and** price_jump) → does the sim's transient appear in OFI? *Key sub-question:* does `price_jump`
  drive an OFI transient even though it failed on returns? If yes, it **also rescues the two-channel
  robustness** (Stage 2b).
- *Real:* compute the OFI statistic on real L2 crash vs calm windows; run the **same null-distribution
  test** that returns failed (`null_test_crash_tails.py` generalized to OFI).
- *Cross:* show calibrated EcoMD **predicts** the real OFI signature → the framework-enabled
  counterfactual (the NCS "computation reveals X about the system" hook).

**Compute.** L2 reconstruction = **CPU-heavy** (book reconstruction is the bottleneck — days of CPU on
the H20-4 CPU node / a big box); storage tens–hundreds GB → R2. EcoMD OFI runs = GPU (modest).
Analysis = Mac/CPU.

**Decision gates (binding, pre-registered):**
- G1: pre-register OFI statistic + windows + null + threshold (arXiv).
- G2: **real OFI shows a transient that passes the null test.** If OFI is *also* stationary → Route A
  dies; fold the result into the honest paper ("even order flow shows no transient" — *strengthens*
  the stationary-universality story, serves Paper B, but **kills NCS**).
- G3: EcoMD reproduces the OFI signature (framework validation).
- G4: the finding is framed **distinctly from Paper B** (OFI tail/memory + computational methodology,
  NOT the thermodynamic laws).

**Cost / timeline.** $4–5k (Tardis) + **6–10 weeks**. Compute on the existing fleet.

**Honest probability.** P(real OFI transient exists) ≈ **30–45%** (genuinely unknown — microstructure
is where non-eq lives, but stationarity keeps winning). P(NCS-grade + accepted + distinct-from-B |
signal) ≈ 30%. **Joint ≈ 10–18%** → roughly *doubles* the current NCS odds to ~**15–20%**, *if* the
signal is there. Clean fallback: a second honest negative that serves Paper B and strengthens Paper A.

**⚠️ Route-A risk — Paper-B cannibalization.** Real-market order-flow non-equilibrium **is Paper B's
core** (Nature Physics: entropy production / TUR on L2). Route A only works for Paper A→NCS if you can
carve a **distinct computational-methodology + OFI-tail-discovery** contribution that does **not**
deplete Paper B's thermodynamics. If you can't cleanly separate them, the higher-EV move is: **put all
order-flow in Paper B (Nat Phys), keep Paper A at NeurIPS/TMLR.** Decide this *before* spending the 6–10 weeks.

---

## 3. Route B — EcoMD as a differentiable controlled-experiment platform  (SECONDARY, cheaper)

**Thesis.** The contribution is the **methodology**: a differentiable simulator that enables
**gradient-based mechanism attribution + counterfactual interventions + measurement-hygiene** at
scale — impossible in real markets or non-differentiable ABMs (ABIDES). The burn-in correction is
*one* validated use-case among several.

### Concrete plan
- Demonstrate the platform on **≥3 distinct controlled experiments**: (1) burn-in measurement
  correction; (2) **gradient mechanism-attribution** (∂stylized-fact/∂interaction — which couplings
  produce which fact); (3) counterfactual shock-response / parameter intervention; (4)
  calibration-by-differentiation.
- **Prior-art delineation** vs Dyer/Quera-Bofarull (differentiable ABMs already exist) — the novelty
  hook must be something they did **not**: the equivariant MD architecture, the scale, the
  gradient-*attribution* capability, or the measurement-hygiene methodology. *This is the make-or-break:
  if the hook reads as incremental, NCS desk-rejects.*
- Release the platform as a **reproducible artifact** (NCS rewards this).

**Cost / timeline.** No new data buy; **~3–5 weeks** (mostly analysis + writing).
**Probability.** ~**10–15%**, entirely gated on the method-novelty hook surviving prior-art scrutiny.

---

## 4. Routes C / D (weaker / better-fit elsewhere — for completeness)

- **C — a positive in-sim discovery that generalizes.** Find a sim phenomenon that *is* robust and
  matches real markets. But the Pareto-ceiling work shows the sim plateaus; unlikely to yield a fresh
  positive finding fast. *Low priority.*
- **D — field-wide measurement-correction audit.** Show many *published* market-sim / generative-TS
  models share the warmup-scoring artifact; propose + validate a corrected protocol + tool. Strong
  version could matter, but it's **TMLR / NeurIPS-D&B** identity more than NCS. *Good Plan-B paper, not
  an NCS route.*

---

## 5. Decision framework

| if you want… | do | NCS odds | cost |
|---|---|---|---|
| highest-EV publication | workshops → **ICLR/NeurIPS-D&B → TMLR**, skip NCS | n/a | low |
| a real NCS shot, data available | **Route A** (order-flow), pre-registered, *after* resolving the Paper-B carve-out | ~15–20% | $4–5k + 6–10wk |
| a cheap NCS lob | **Route B** (platform), strong prior-art delineation | ~10–15% | ~3–5wk |
| NCS but can't separate from Paper B | **don't** — route order-flow to Paper B, Paper A → NeurIPS/TMLR | — | — |

**Recommended:** pursue **Route A only if the Tardis buy happens for Paper B anyway** (it needs L2
regardless) — then Paper A's NCS shot is an opportunistic by-product, the OFI logging + pre-reg are
cheap to add, and the worst case is a publishable negative. Do **not** buy Tardis to chase Paper
A→NCS in isolation. In parallel, ship the workshops + draft the NeurIPS/TMLR version now (Route B's
"platform" framing strengthens that draft regardless of the NCS decision).

## 6. Honest bottom line
NCS is viable **only with a positive finding added** — realistically the **order-flow transient
(Route A)**, which roughly doubles the odds to ~15–20% but is gated on (a) the Tardis buy, (b) the
signal actually existing (~30–45%), and (c) a clean carve-out from Paper B. Absent that, NCS stays a
~8–15% desk-reject-prone lob and **TMLR is the calibrated home**. The good news: every route's work
(OFI logging, the platform framing, the measurement correction) **also strengthens the NeurIPS/TMLR
paper and/or Paper B** — so none of it is wasted if NCS doesn't land.
