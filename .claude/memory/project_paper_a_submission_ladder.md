---
name: paper-a-submission-ladder-ncs
description: "Researcher-decided Paper A submission ladder (2 non-archival NeurIPS workshops → NCS → ICLR → TMLR → AI4S) and the bucketed work-list (experiments/data/compute/writing) still needed to reach an NCS submission."
metadata:
  node_type: memory
  type: project
---

# Paper A — submission ladder (DECIDED) + the NCS work-list (2026-06-19)

**Decided by the researcher (plan of record).** Full detail + the per-venue fit analysis:
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
