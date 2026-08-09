---
name: paper-a-submission-ladder-ncs
description: "Researcher-decided Paper A submission ladder (2 non-archival NeurIPS workshops → NCS → ICLR → TMLR → AI4S) and the bucketed work-list (experiments/data/compute/writing) still needed to reach an NCS submission."
metadata:
  node_type: memory
  type: project
---

# Paper A — submission ladder (DECIDED) + the NCS work-list (2026-06-19)

> **NCS route audit (2026-08-09; supersedes the Route-A cross-validation claim below).** STODY is
> cancelled and only the narrow Sim2Science audit remains from the workshop ladder. Exp127 shows
> post-gate EcoMD fidelity at roughly 1--2/11 and exposed state/horizon and jump-law mismatches, so the
> old NCS draft cannot be submitted by merely filling its L2 result section. More importantly, EcoMD's
> model `ofi` is `sum(dpos)/sum(abs(dpos))`, whereas exp124 defines real OFI from L2 quote-depth changes
> and trades; there is no validated observation map between them. A positive real-L2 result therefore
> cannot currently be called confirmation of an EcoMD prediction. Initialization/latent-state
> calibration and steady-state sensitivity also have substantial prior art, so neither "initialization
> matters" nor generic differentiability is an NCS-level novelty claim. A credible NCS route now needs
> one coherent advance: a genuinely new invariant-measure/long-horizon calibration method validated
> beyond EcoMD, plus a real-data application whose observable is explicitly bridged and whose held-out
> outcome depends on that method. **The user approved this direction on 2026-08-09; the authoritative
> execution plan is `papers/proposal/plan_v4_ncs.md`.** It starts from 2×V100 32 GB, permits gated
> expansion to more non-H20 compute, and treats current data as only the first acquisition tier.

> **SUPERSEDED IN PART (2026-07-22):** the public accepted-workshop audit after the July 11 NeurIPS
> notification found neither ML4PS nor Generative AI in Finance for 2026. Do not use those target names.
> Current candidates are STODY (driven stochastic dynamics) and Sim2Science (simulator
> misspecification/stationarity audit), both with an August 29 AoE deadline. See
> [[project_workshop_audit_2026-07-22]]. The later archival ladder below is retained as historical
> planning, not re-endorsed by this venue correction.

**Historical June decision (superseded by Plan v4 for the NCS route).** Full detail + the per-venue fit analysis:
`papers/proposal/paper_a_ncs_worklist_2026-06-19.md` and `papers/proposal/paper_a_dual_track_plan_2026-06-19.md`.

**Ladder:**
1. Split into **2 non-archival NeurIPS workshop** papers — **ML4PS** (non-equilibrium physics angle) +
   **GenAI in Finance** (generative market-simulator / scenario-generation angle). Keep genuinely
   distinct (same-conference dedupe risk). Both confirmed non-archival (GenAI-in-Finance 2025 CFP
   explicitly so; ML4PS historically so).
2. **Recombine + add experiments → Nature Computational Science (NCS).**
3. Fallback **ICLR** → 4. **TMLR** (soundness floor) → 5. **AI4S** (clarify: if the AI-for-Science
   *workshop* it's non-archival, shouldn't sit below TMLR).

**Honest calibration (not a veto):** workshops high; **NCS ~12–20%** (must be computational-science-
method-centric, NOT a real-market discovery — Stage 3 refuted that, see [[burnin-artifact-zeta-ed-2026-06-18]]);
ICLR ~25–35%; TMLR likely. Manage the **journal→conference cadence**: submit NCS ~1–2 mo before the
ICLR deadline + set a redirect-by date so an open NCS review doesn't eat the ICLR cycle.

**NCS work-list (two tiers; Tier 1 = no new data buy, Tier 2 = order-flow-lifted via Tardis):**
- **跑实验 Experiments:** E1 Stage 2b price_jump (*running on .56*); E2 Stage 2c news/info channel
  (retrain 1 seed info_asym ON + inference); E3 n≥30 seed audit; E4 τ generalization (analysis);
  **E5 (Tier 2)** EcoMD order-flow counterfactuals (needs order-flow observable in the recorder).
- **处理数据 Data:** D1 crypto 1m crashes (done, free); D2 equity stationary-tail cross-check
  (FirstRate minute $1.5–2.5k OR coarse-daily-as-limitation); **D3 (Tier 2) Tardis L2 buy $4–5k**;
  D4 L2 ingest+book reconstruction+order-flow-imbalance; D5 provenance files.
- **算力 Compute:** C1 H20 inference (have); **C2 (Tier 2)** L2 reconstruction = CPU-heavy + R2 storage
  (tens–hundreds GB); C3 EcoMD order-flow runs (GPU); C4 Mac writing/figures.
- **写作 Writing:** W1 spine rewrite (7-section comp-sci structure); W2 4–5 figures; W3 code/simulator
  artifact release (NCS rewards reproducible tools); **W4 (Tier 2)** pre-register the order-flow test.

**Gates:** Tier-1 NCS attempt ≈ 2–4 weeks, no buy. Tier-2 adds +6–10 wk + $4–5k — commit the Tardis
buy **only when Paper B greenlights it** (Paper B needs L2 regardless; Paper A's NCS lift is then an
opportunistic by-product, not the buy's justification). See [[target-venue-registry-ecophys]],
[[differentiable-priorart-c1-novelty]], [[user-role]].

**🔴 2026-06-19 update — NCS is a long shot now (~8–15%), Stage 2b also NEGATIVE.** The market-realistic
price_jump channel did NOT reproduce the transient (see [[burnin-artifact-zeta-ed-2026-06-18]]) → two
negatives (Stage 2b + Stage 3) on a not-first-of-kind tool ⇒ NCS desk-screens for a *positive* novel
discovery, which we lack. **What would make NCS viable** (full plan: `papers/proposal/paper_a_ncs_
viability_routes_2026-06-19.md`): **Route A** = a real **order-flow/L2** non-equilibrium transient
(where returns failed) + EcoMD reproducing it → ~15–20% IF the signal exists (~30–45%), gated on the
Tardis buy + a clean carve-out from Paper B (which owns the order-flow thermodynamics). **Route B** =
EcoMD-as-differentiable-controlled-experiment-platform (~10–15%, gated on method-novelty vs Dyer 2023–25).
Recommended: pursue Route A *only if* Tardis is bought for Paper B anyway; otherwise ship NeurIPS/TMLR
and route order-flow to Paper B. **TMLR is the calibrated home.**

**Concrete experiment plan: `experiments/124_order_flow_transient/DESIGN.md` (2026-06-20).** Phase 1
(sim, runnable NOW, no buy, no-regret): E-S1 OFI dose-response, E-S2 cross-asset OFI, E-S3
time-asymmetry/entropy-production proxy, E-S4 τ_OFI → freezes a quantitative prediction. Phase 2
(decisive, gated on Tardis L2 $4–5k): reconstruct real OFI, pre-registered null test (generalize
`null_test_crash_tails.py` returns→OFI) on OFI memory/tail/saturation/EP; G-main = ≥1 observable
bursts-and-relaxes on ≥2 crashes where returns didn't ⇒ NCS-credible; G-null ⇒ folds into honest
paper. Paper-B carve-out: lead with OFI memory/coherence (computational), entropy-production supporting
(full thermo program stays in Paper B). Joint NCS odds ~10–18%.
**Phase 1 DONE 2026-06-21 (.56, ~12h):** E-S1 spx OFI-memory dose-response = clean MONOTONIC SIGMOID
(0.05→0.05 … 1→0.97 … 12→1.00; onset ~0.1–0.2, saturates ~1.0 — cleaner than the tail). E-S2: OFI
transient generalizes — spx/ndx/gold/btc all burst mem→~1.0 (all 4 measures); eurusd weak at kick6
(sub-threshold, consistent w/ its vol-threshold). Sharpened prediction for Phase-2 real L2: crash
order-flow memory bursts toward perfect persistence, sigmoid in severity, vol-dependent threshold,
where returns are stationary. **E-S4:** τ_OFI≈22 steps (4 assets, R²=1.0) vs tail τ_ED≈236 → OFI-memory
burst is a SHARP impulse (~10× faster than the tail). **E-S3 FLAT:** sign-level (Δp,OFI) entropy-
production proxy does NOT burst → the transient is persistence/coherence, NOT sign-level irreversibility
⇒ **lead the NCS real-data test with OFI MEMORY, not entropy production** (tightens Paper-A/Paper-B
split: memory=A, real EP=B). Phase 1 COMPLETE. See `logs/2026-06-21.md`,
`experiments/124_order_flow_transient/DESIGN.md`, `ofi_{transient,entropy}_*.json`, `ofi_tau_report.json`.
