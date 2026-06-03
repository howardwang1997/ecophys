---
name: EcoPhys project overview
description: Research program "EcoPhys / EcoMD" — differentiable physics-inspired simulator for financial markets. Three contribution pillars (C1 methods / C2 physics / C3 applications). As of plan v3 + Path C (2026-04-24 evening), Paper B targets Nature Physics flagship with 15–22% joint probability, supported by $8-12k high-frequency data commitment (Tardis L2 6mo + FirstRate minute 3y + LOBSTER 3y); Paper A + companion PRL + QF are guaranteed retreat papers. Total timeline 58 weeks to M6. Full plan at papers/proposal/plan_v3.md mirror at ~/.claude/plans/4-h20-claude-ai-playful-bubble.md.
type: project
originSessionId: c6748c05-53ac-462d-9535-154e95f91d9f
---

# EcoPhys — Project Overview

## Research goal
Build **EcoMD**: a differentiable, equivariant, learned-potential molecular-dynamics-style simulator for financial markets. Agents = particles in latent feature space; dynamics = Langevin; interaction potentials learned end-to-end from high-frequency order flow / return data.

## Three contribution pillars
- **C1 (methods)**: a differentiable MD-style market simulator with learned equivariant interaction potentials (MACE-lite GNN), end-to-end pathwise BPTT. ⚠️ **NOT "first differentiable / first Langevin"** — lit check 2026-06-03 ([[reference_differentiable_priorart]]) found Bouchaud-Cont 1998 (Langevin markets) + Dyer/Quera-Bofarull 2023–25 (differentiable financial ABMs) occupy the broad claim. Demoted to a SECONDARY contribution; Paper A LEADS with the finding (concave-impact tail solve), not the artifact. Targets NeurIPS/ICML main.
- **C2 (physics)**: non-equilibrium thermodynamics of markets — extract entropy production rate σ(t), effective temperature T_eff(t) from trained simulator, test cross-market universality via critical scaling + Jarzynski identity. **Paper B → Nature Physics flagship**; retreat to PRL.
- **C3 (applications)**: crash early warning + optimal execution under regime shift. Targets QF/JEDC/ICAIF.

## Publication strategy (plan v3 + Path C, 2026-04-24 evening — supersedes v3 early draft)
**Flagship-with-retreat + high-frequency data commitment (Path C)**. User reviewed daily-only data feasibility for Nature Physics physics claims and explicitly chose to commit $8-12k to high-freq data (Tardis L2 6mo + FirstRate minute 3y + LOBSTER 3y) because daily-only would leave the three main NP reviewer attacks (Jarzynski work protocol undefined at daily, TUR non-stationary over 30y, T_eff novelty weak vs Mantegna-Stanley 1995) unanswered. With Path C, joint NP probability moves from 10–15% → 15–22%. Total timeline 52w → 58w. Accepted three pre-registration/rigor clauses.
- **Paper A** (methods): NeurIPS/ICML main. **arXiv preprint at Wk 28 (M3)** stakes priority regardless of flagship outcome. Timeline shifted +2 weeks from v3 early draft to accommodate high-freq data ingestion.
- **Paper B** (physics) → **Nature Physics**. Primary: A1 (T_eff critical scaling on ≥3 timescales: daily + minute + L2) + B2 (Jarzynski with FOMC/earnings intraday protocol). Secondary: A2 (hyperscaling). Wk 54 submission.
- **Paper B.5 / Companion PRL**: B3 (TUR saturation on L2 event-level data) as standalone.
- **Paper C** (finance, applications): QF/JEDC. LOB subscription (originally Tier C) now merged into Tier B — Paper C data needs fully covered by Paper B's purchase.
- **Retreat papers** (if flagship fails): 2 PRL + 1 QF. $8-12k high-freq data is not wasted in retreat — feeds Paper C + PRL retreat + Paper A microstructure appendix.

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

## Key timeline (v3 + Path C, 58 weeks)
- ✓ Phase 0 (Wk 1–4): infra + literature → M0
- ✓ Phase 1 (Wk 5–10): stylized facts + baselines → M1
- ✓ **M2 GATE PASSED 2026-04-24**: EcoMD v0.8 (shared MLP PairwisePotential, Student-t noise, β_fixed, persistent state, warmup detach) → **7/11 SPX daily**. v0.6 is Pareto-alternative with stronger vol clustering (6/11 but acf(r²)=+0.306 vs v0.8's +0.079).
- v1 MACE-lite (Phase 2 attempt at N=10K scaling) **failed at 0-4/11** across 8 architecture variants: SE(3)-equivariant inductive biases are domain-mismatched for markets, force magnitude 60-190× too small, per-node readout smooths dynamics. Captured as negative result for Paper A.
- ✓ **EcoMD v2.1 (2026-04-25)**: market-microstructure-derived equivariant GNN (permutation-within-type × persistent type-coupling matrix T_θ). Mac N=200 sweep reached 9/11 with strong Hawkes + ACF-shape loss, but **H20 N=10K does NOT replicate Mac results**: production config (κ=2.0+ws=0.3) DIVERGED (loss 3.9→3208, hill→32K), and conservative retryA (κ=1.0+ws=0+clip=10+lr=5e-4) plateaued at **4/11** (vs v1.0 Hawkes baseline 7/11). v2.1 retired as Paper A ablation negative result.
- ✓ **EcoMD v3 (2026-04-26)**: post-v2.1 architectural exploration. Six features added: P1 multi-asset shared θ training (joint SPX+BTC+ETH); P2 multi-scale Hawkes (long-memory channel); P3 regime GRU slow latent; P4 two-population per-type γ/T; P5 T_eff(t) emergence head; P6 entropy production logger. Plus loss expansion: autocorr_r penalty + hill_max relu clip + zumbach hinge. **Best so far: C4 = 8/11** (multi-asset + twopop γ/T + autocorr_r/hill_max loss) — first 8/11 result on H20 N=10K with **single θ trained on 3 markets simultaneously**. 3 stragglers: autocorr_returns +0.27 (target ≤0.20), volume_volatility_corr −0.38 (sign reverse), zumbach_asymmetry −0.067 (sign reverse). Weekend batch (54 configs) attacking these 3 facts to push C4 → 9-10/11.
- Phase 1.5 (Wk 17–20): **high-freq data procurement + ingest** (parallel with v1 training) → **M1.5 NEW**
- Phase 2 (Wk 11–18): EcoMD v0 → v0.5 → v0.6 → v0.8 reaches **7/11** on SPX daily → M2 ✓ (+2 weeks)
- Phase 3 (Wk 19–28): **Paper A drafting (v0.6/v0.8 Pareto frontier)** + cross-asset BTC/ETH replication + T_eff initial probing → M3 + **Paper A arXiv (Wk 28)**
- Phase 3.5 (Wk 29–34): A1 pilot on **3 markets × 3 timescales** + 7 sanity checks → **M3.5 hard gate (Wk 34)**
- Phase 4 (Wk 35–42): A1 full 8-market × multi-scale + A2 + B2 (FOMC protocol) + B3 (L2 TUR) → M4 (+6)
- Phase 5 (Wk 43–48): "one-line physics" formalization → **M5 hard gate (Wk 48)**
- Phase 6 (Wk 49–54): Paper B drafting + submission → M6 (+6)
- Phase 7 (Wk 55–58): review response / immediate retreat to PRL if desk reject

## Core design commitments (fixed across v1/v2/v3)
- **C2 early-core**: architecture already reserves explicit Langevin form with conservative/dissipative force separation, F-v-s triplet logging for fluctuation-theorem analysis.
- **Main architecture options as of 2026-04-26 (post overnight v3 batch)**:
  1. v0.x `PairwisePotential` = MLP(concat(s_i, s_j, |Δs|)) summed over all N² pairs. Capped at N ≤ 10³. v0.8 (β_fixed) hit 7/11 on Mac.
  2. v0.9 `StochasticPairwisePotential` = same kernel but unbiased random k-pair subsampling. Scales to N=10⁴+.
  3. v1.0 = v0.6 + Hawkes self-excitation. **H20 single-asset 7/11**.
  4. v2.1 `EcoMDv2Potential` = persistent type embedding + K×K T_θ coupling. Mac 9/11; H20 N=10K plateaued at 4/11 (Mac→H20 doesn't transfer). Retired.
  5. **v3 (current best) = v0.9 + Hawkes + persistent K=4 type embedding + per-type γ/T scaling + multi-asset joint training + expanded loss (autocorr_r + hill_max). Trained jointly on SPX+BTC+ETH** → **8/11 on H20 N=10K** (config C4). 3 remaining stragglers: autocorr_returns, volume_volatility_corr, zumbach_asymmetry.
- v1 MACE-lite (SE(3)-equivariant GNN with body-order 4 tensor products) attempted but **failed at 0-4/11** across all 8 ablation variants — captured as Paper A negative result demonstrating SE(3) inductive biases don't transfer to markets.
- **Honest MD-analogy critique**: single traders not observable → agent defined in latent space; non-stationarity → time-varying potential + regime; utility ≠ energy minimum → conservative/dissipative split.
- **Pluggable price formation** (v3 added): `ExcessDemandPrice` (default, designated-position) + `ReadoutPrice` (ablation). Designated-position mechanism gives stylized fact #10 (volume/vol correlation) **when β is fixed** — learnable β breaks #10 by injecting state-dependent amplification. v0.6 (β_learn) vs v0.8 (β_fixed) are two Pareto points.

## Hardware (v3)
**8×H20 NVLink, single node, long-term access** (upgraded from 4×H20 in v2). Enables:
- Single tensor-parallel EcoMD at N=5×10⁵ (vs N=10⁵ without NVLink)
- Shared-θ joint training across 8 markets simultaneously (required for universality claim)
- Jarzynski at 10⁴ trajectory × 8 market = 8×10⁴ trajectories in ~2 weeks

## Data budget (Path C, 2026-04-24 evening)
$50k approved. **Committed up-front $8-12k**:
- Tardis.dev crypto L2 × 6 months × {BTC, ETH} (~$4-5.5k) — B3 TUR + cross-asset universality
- FirstRate / AlgoSeek US equity minute × 3 years × 20 symbols (~$1.5-2.5k) — A1 intraday-equity scale
- LOBSTER research subscription × 2-3 years × 20-50 symbols (~$3-4.5k) — B3 + Paper C execution

Remaining reserve $38-42k for Phase 4/5 contingencies. Purchases stage at Wk 16-18 once v1 converges on SPX daily. Full details: `ecomd/data/buy_order_v2_{en,zh}.md`.

## Key literature
1. Tóth, Lux & Sornette, PRL 120, 138301 (2018) — Boltzmann equation from HFT. Closest prior work.
2. Chopra et al., arXiv:2207.09714 — differentiable ABM methodology template.
3. Batatia et al. (MACE, NeurIPS 2022) — equivariant GNN architecture template.
4. Cont (2001), Quant Finance 1 — canonical 11 stylized facts.
5. Maskawa, J. (Entropy 2025, 27(4), 435, doi: 10.3390/e27040435) — "Empirical Study on Fluctuation Theorem for Volatility Cascade Processes in Stock Markets"; we extend by embedding IFT as in-simulator measurement target.
6. Barato & Seifert, PRL 114, 158101 (2015) — TUR original; Horowitz-Gingrich 2020 review — B3 claim basis.
7. Koyuk & Seifert, PRL 125, 260604 (2020) — generalized TUR for non-stationary; required for B3.

## Critical risks (plan v3 §7)
- Identifiability of learned potentials (structured priors + agent-type regularization)
- Long BPTT gradient instability (checkpointing, persistent state v0.5)
- Non-stationarity breaking T_eff (time-varying potential + regime detection)
- **v3-specific**: Gate 2 (M3.5) fails with ~50% probability → automatic retreat to Paper A arXiv priority plus 2-PRL split; this is built into the plan, not a disaster
