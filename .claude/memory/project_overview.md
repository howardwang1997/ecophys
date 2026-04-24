---
name: EcoPhys project overview
description: Research program "EcoPhys / EcoMD" — differentiable physics-inspired simulator for financial markets. Three contribution pillars (C1 methods / C2 physics / C3 applications). As of plan v3 (2026-04-24), Paper B targets Nature Physics flagship (10–15% joint probability); Paper A + companion PRL are guaranteed outputs as retreat path. Full plan at papers/proposal/plan_v3.md and mirror at ~/.claude/plans/4-h20-claude-ai-playful-bubble.md.
type: project
originSessionId: c6748c05-53ac-462d-9535-154e95f91d9f
---

# EcoPhys — Project Overview

## Research goal
Build **EcoMD**: a differentiable, equivariant, learned-potential molecular-dynamics-style simulator for financial markets. Agents = particles in latent feature space; dynamics = Langevin; interaction potentials learned end-to-end from high-frequency order flow / return data.

## Three contribution pillars
- **C1 (methods)**: first differentiable MD-style market simulator with learned interaction potentials (MACE-lite equivariant GNN) at ~10⁵–5×10⁵ agent scale on 8×H20 NVLink. Targets NeurIPS/ICML main.
- **C2 (physics)**: non-equilibrium thermodynamics of markets — extract entropy production rate σ(t), effective temperature T_eff(t) from trained simulator, test cross-market universality via critical scaling + Jarzynski identity. **Paper B → Nature Physics flagship**; retreat to PRL.
- **C3 (applications)**: crash early warning + optimal execution under regime shift. Targets QF/JEDC/ICAIF.

## Publication strategy (plan v3, 2026-04-24 — supersedes v2)
**Flagship-with-retreat**. Reason: 8×H20 NVLink unlocks cross-market joint training + full Jarzynski statistics, raising joint Nature Physics probability from 5–12% (v2) to 10–15% (v3). User explicitly willing to delay submission 4–6 weeks to shoot for Nature Physics. Accepted three pre-registration/rigor clauses to make NP referee attacks impossible.
- **Paper A** (methods): NeurIPS/ICML main. **arXiv preprint at Wk 26 (M3)** stakes priority regardless of flagship outcome.
- **Paper B** (physics) → **Nature Physics**. Primary: A1 (T_eff critical scaling) + B2 (Jarzynski self-consistency). Secondary: A2 (hyperscaling). Wk 48 submission.
- **Paper B.5 / Companion PRL**: B3 (TUR saturation) as standalone.
- **Paper C** (finance, applications): QF/JEDC.
- **Retreat papers** (if flagship fails): split into 2 PRL + 1 QF.

## Four pre-registered "one-line laws" (Paper B)
- **A1**: T_eff(t) ∝ (t_c − t)^(−ν), ν universal within ±0.05 across 8 markets.
- **A2**: Hyperscaling ν(2−η) = γ on ≥6/8 markets (supporting claim only).
- **B2**: ⟨e^(−βW)⟩ = e^(−βΔF) with ΔF from learned U_θ, agreement within 15% on ≥5/8 markets.
- **B3**: Var(J)·⟨Σ⟩ ≈ 2k_B T_eff (TUR saturation) on ≥5 markets — independent PRL track.

## Hard pre-registration clauses (2026-04-24, accepted)
Three binding rigor conditions documented in `feedback_preregistration.md`:
1. Surrogate data (IID + GARCH) can falsify main claim
2. Any of 7 sanity checks failing → paper downgrades from Nature Physics
3. Wk 26 arXiv preprint locks crash event list + measurement protocols before experiments

## Key timeline (v3)
- ✓ Phase 0 (Wk 1–4): infra + literature → M0
- ✓ Phase 1 (Wk 5–10): stylized facts + baselines → M1
- Phase 2 (Wk 11–16): EcoMD v0 → v0.5 → v0.6 → v1 reaches ≥7/11 → M2
- Phase 3 (Wk 17–26): MACE-lite + tensor-parallel multi-market on NVLink → M3 (≥9/11) + **Paper A arXiv**
- Phase 3.5 (Wk 27–30): A1 pilot on 3 markets + 7 sanity checks → **M3.5 hard gate**
- Phase 4 (Wk 31–36): A1 full 8-market + A2 + B2 + B3 experiments → M4
- Phase 5 (Wk 37–42): "one-line physics" formalization → **M5 hard gate**
- Phase 6 (Wk 43–48): Paper B drafting + submission → M6
- Phase 7 (Wk 49–52): review response / immediate retreat to PRL if desk reject

## Core design commitments (fixed across v1/v2/v3)
- **C2 early-core**: architecture already reserves explicit Langevin form with conservative/dissipative force separation, F-v-s triplet logging for fluctuation-theorem analysis.
- **Equivariant via feature-space locality, not physical space**: agents interact via k-NN graph in trader feature space.
- **Honest MD-analogy critique**: single traders not observable → agent defined in latent space; non-stationarity → time-varying potential + regime; utility ≠ energy minimum → conservative/dissipative split.
- **Pluggable price formation** (v3 added): `ExcessDemandPrice` (default, designated-position) + `ReadoutPrice` (ablation). Designated-position mechanism gives stylized fact #10 (volume/vol correlation) for free, which is Paper A's differentiation target.

## Hardware (v3)
**8×H20 NVLink, single node, long-term access** (upgraded from 4×H20 in v2). Enables:
- Single tensor-parallel EcoMD at N=5×10⁵ (vs N=10⁵ without NVLink)
- Shared-θ joint training across 8 markets simultaneously (required for universality claim)
- Jarzynski at 10⁴ trajectory × 8 market = 8×10⁴ trajectories in ~2 weeks

## Data budget
$50k (unchanged). Spent on international indices + Tardis crypto L2 + CBOE EOD options. Cross-market data is the core enabler for Nature Physics universality claim.

## Key literature
1. Tóth, Lux & Sornette, PRL 120, 138301 (2018) — Boltzmann equation from HFT. Closest prior work.
2. Chopra et al., arXiv:2207.09714 — differentiable ABM methodology template.
3. Batatia et al. (MACE, NeurIPS 2022) — equivariant GNN architecture template.
4. Cont (2001), Quant Finance 1 — canonical 11 stylized facts.
5. Doshi et al. (Entropy 2025) — empirical fluctuation theorem on vol; we extend.
6. Barato & Seifert, PRL 114, 158101 (2015) — TUR original; Horowitz-Gingrich 2020 review — B3 claim basis.
7. Koyuk & Seifert, PRL 125, 260604 (2020) — generalized TUR for non-stationary; required for B3.

## Critical risks (plan v3 §7)
- Identifiability of learned potentials (structured priors + agent-type regularization)
- Long BPTT gradient instability (checkpointing, persistent state v0.5)
- Non-stationarity breaking T_eff (time-varying potential + regime detection)
- **v3-specific**: Gate 2 (M3.5) fails with ~50% probability → automatic retreat to Paper A arXiv priority plus 2-PRL split; this is built into the plan, not a disaster
