# Paper A — submission ladder (decided) + the NCS work-list

**Date:** 2026-06-19. **Owner decision** (this is the plan of record). Companion to
`paper_a_dual_track_plan_2026-06-19.md` (which has the per-venue fit analysis).

## Submission ladder (decided by the researcher)

1. **Split into two non-archival NeurIPS workshop papers** (visibility + feedback, burns no novelty):
   - **ML & the Physical Sciences (ML4PS)** ← the non-equilibrium / driven-transient *physics* angle.
   - **Generative AI in Finance** ← the generative *market-simulator / scenario-generation* angle.
   - Keep the two genuinely distinct (different experiments/emphasis) to avoid same-conference dedupe.
2. **Recombine + add experiments → submit the full paper to Nature Computational Science (NCS).**
3. **Fallback → ICLR.**
4. **Fallback → TMLR.**
5. **Fallback → AI4S** *(clarify: if this means the AI-for-Science **workshop**, it is non-archival and
   should sit for visibility, not below TMLR; if an archival AI4S venue, specify which).*

Honest calibration (not a veto — the ladder always lands somewhere archival): workshops high; NCS
**~12–20%** (stretch; must be computational-science-method-centric, NOT a real-market discovery —
Stage 3 refuted that); ICLR ~25–35%; TMLR is the soundness floor. Manage the **journal→conference
cadence**: submit NCS ~1–2 months before the ICLR deadline and set a "redirect-by" date so an open
NCS review doesn't eat the ICLR cycle.

---

## What's still needed to submit to NCS — work-list

Two tiers. **Tier 1** reaches an NCS attempt with **no new data purchase** (framework + measurement
correction + controlled in-sim discovery + the honest real-market boundary). **Tier 2** adds the
order-flow/L2 evidence that could genuinely *lift* the NCS odds — but it is gated on the Tardis buy,
which per the dual-track plan should be **justified by Paper B**, not Paper A alone.

### 跑实验 — Experiments (simulator, GPU)

| id | task | tier | status / effort |
|---|---|---|---|
| E1 | **Stage 2b** market-realistic `price_jump` channel — two-channel robustness | 1 | **DONE → 🔴 NEGATIVE.** "A — ARTIFACT, no revival" (α_ED flat ~4.6; α_ret stays light ~6). The transient is specific to latent-state displacement; price shocks don't trigger it. *Robustness claim fails; report as a mechanistic bound.* |
| E2 | **Stage 2c** news/info-shock channel (3rd channel): retrain 1 seed `info_asym` ON + inference | 1 | OPEN but **LOW-VALUE** — same indirect mechanism as price_jump → likely also negative. Skip unless a positive non-latent channel is needed. |
| E3 | **Seed-count audit**: confirm every headline number at n≥30 seeds (seed-count-lottery clause); re-run any thin cells | 1 | OPEN — mostly done; verify 2b/2c |
| E4 | **τ generalization** (Stage 2d+): fit τ across assets + the price_jump channel (is the relaxation time universal?) | 1 | OPEN — analysis only (no new sim) |
| E5 | **EcoMD order-flow counterfactuals**: log order-flow imbalance in the sim; run the L2-matched shock protocol | 2 | OPEN — needs the order-flow observable in the recorder + GPU runs |

### 处理数据 — Data (acquisition + processing)

| id | task | tier | cost / effort |
|---|---|---|---|
| D1 | Crypto 1m crash windows (5 episodes) + null source — the model-reality-gap evidence | 1 | **done** (free, `data/real/`) |
| D2 | **Equity stationary-tail cross-check** (show the gap isn't crypto-only). Free daily = too coarse for windowed/regime Hill → need **FirstRate minute** ($1.5–2.5k) OR ship a coarse daily regime-level check as a stated limitation | 1 | OPEN — buy-or-limitation decision |
| D3 | **Tardis L2 buy** (BTC+ETH × 6mo, book changes + trades) | 2 | **$4–5k** (justify via Paper B) |
| D4 | L2 ingest + order-book reconstruction + order-flow-imbalance series + crash/calm window extraction | 2 | OPEN — heavy (days of CPU) |
| D5 | Provenance files (source/date/license/hash) for every real dataset (data-discipline clause) | 1–2 | OPEN — quick per dataset |

### 算力 — Compute

| id | task | tier | resource |
|---|---|---|---|
| C1 | Stage 2b/2c inference | 1 | H20 fleet — hours (have it) |
| C2 | **L2 reconstruction** (Tardis ingest) | 2 | CPU-heavy — H20-4 CPU node or a big box; **storage**: 6mo L2 BTC+ETH ≈ tens–hundreds of GB → R2 |
| C3 | EcoMD order-flow counterfactual runs | 2 | H20 GPU — modest |
| C4 | Spine rewrite + figures + analysis | 1 | Mac |

### 写作与打包 — Writing & packaging (NCS-specific)

| id | task | tier |
|---|---|---|
| W1 | **Spine rewrite** to the 7-section computational-science structure (problem → EcoMD framework → measurement correction → controlled discovery → robustness/channels → real-market boundary → handoff) | 1 |
| W2 | **Figures** (4–5): burn-in R1 correction; shock dip-and-recover + sigmoid dose-response; τ; real-market null test; (Tier 2) order-flow transient | 1–2 |
| W3 | **Code/simulator artifact release** — NCS rewards reproducible computational tools: clean EcoMD repo, configs+seeds+README, one-command repro | 1 |
| W4 | **Pre-registration** of the order-flow test (binding pre-reg clause) before looking at the L2 data | 2 |

### Decision gates
- **Tier-1 NCS attempt** (no buy): E1–E4, D2(coarse/free), D5, C1/C4, W1–W3. Effort ~2–4 weeks. Odds ~12–20%.
- **Tier-2 (order-flow-lifted)**: + E5, D3/D4, C2/C3, W4. +6–10 weeks + **$4–5k**. Commit the Tardis buy
  **only when Paper B greenlights it** (it needs L2 regardless); then Paper A's NCS shot is an
  opportunistic by-product, not the buy's justification.
- If NCS rejects at either tier → ICLR → TMLR per the ladder (the work above all transfers).
