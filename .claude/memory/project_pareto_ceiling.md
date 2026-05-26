---
name: Pareto ceiling — 11-fact frontier in v3 mechanism family
description: 089-099 evidence (3000+ runs, 5 assets, 23 pair combinations) shows no single mechanism nor any depth-2 composition reaches mean ≥ 5.5/11; new SOTA Gold zumdn 5.96. Central Paper A §4 claim.
type: project
---

**The 089-099 3-day batch (~3000 cfg) settled the central Paper A question**:
*can the v3 ECoMD mechanism family produce a "hero" cell that satisfies all 11
Cont 2001 facts?* Answer: **no**, and the failure pattern is Pareto-bounded, not
random.

### What the evidence says (n≥26 each, post-rescore 5-asset)

1. **Best single-mechanism cell**: `xa_gold_zumdn = 5.96 ± 1.54 (n=26, max=8, 5/26 ≥8)`.
   Replicated across batches: 089 SPX zumdn 5.12 (n=48), 090 SPX zumdn 5.31 (n=29),
   092 Gold zumdn 5.96, 089b EURUSD zumdn 5.36 (n=28, 4/28 ≥8).
2. **Best pair-composition cell**: `pair_asym_ms = 5.33` (096 all-pairs at n=27).
   23 pair combinations tested at n=30 each; **none reaches 5.5**.
3. **Depth-3 only one stable cell**: `triple_zumdn_b3_memk = 5.00 max=9` (090d n=30).
   Other depth-3 triples 4.04-4.77. Depth-2 sweet spot confirmed.
4. **N-agents ceiling**: 097 N=500/1000/5000 mean 4.08/3.87/4.65. Ceiling is NOT
   a finite-N artefact (rebuts the obvious reviewer-2 attack).
5. **ECoMD vs baselines** — ⚠️ **the n=5 claim below was REFUTED at n=30 (2026-05-26)**:
   - Traditional (093): GARCH best SPX 4.60, GBM flat 2.80, AR1-SV unstable (11/15 rej).
   - ~~Modern surrogates (095, n=5 preliminary): TrajCast 4.00-5.00, WGAN 4.00-4.20, max ≤ 6.~~
   - ~~ECoMD beats every baseline on every asset by ≥ 1.4 mean.~~ **DO NOT USE in paper.**
   - **095b n=30 (2026-05-26), common-10-fact head-to-head** (`--exclude volume_volatility_corr`,
     baselines are returns-only): `trajcast_spx`=5.24 and `wgan_ndx`=5.12 **beat every
     weekend-batch ECoMD cell** (best ECoMD `x5_zum_downside`=4.89; `baseline_v3`=4.14). The win
     is **SPX/NDX-specific** — `trajcast_gold`=4.16, `trajcast_eurusd`=3.00 still lose to ECoMD.
     Baselines are also ~2× more seed-stable (std ≈0.6–0.9 vs 1.3–1.7). Trajcast/WGAN are return
     generators fit on the target asset, so beating ECoMD on *return* facts is unsurprising — but
     a NeurIPS referee will run exactly this head-to-head, so "ECoMD reproduces stylized facts
     well" is **not defensible as stated**. Full artifact + caveats:
     `experiments/095b_baselines_n30/baseline_vs_ecomd_10fact.md`. See [[project_paper_a_neurips_2027]].

### The Pareto structure

089 attribution matrix (16 cells × 11 facts × Δ-vs-baseline) shows:
- **Per-fact biggest mover is a DIFFERENT mechanism for each of 11 facts** (Figure 1b).
  Specialist mechanisms, no generalist.
- **Every cell that lifts a "floor" breaks ≥1 other fact ≥20pp**, with one exception:
  `zumbach_dn_s10` lifts `zumbach_asymmetry` 6%→29% with no individual breakage ≥−13pp.
- This is the strongest single-paper falsification of "v3 ABM mechanisms can match all 11
  Cont 2001 facts simultaneously" — see [[project_arch_floors]] for the floor-by-floor
  breakdown.

### What's NOT in the evidence yet (gates for §4 final)

- ✅ **099b memk at n=30** (landed 2026-05-26): best `memk_s025_lam090`=5.00/11 — **no hidden
  operating point; Track A failed/demoted** (see [[project_paper_a_neurips_2027]]).
- ✅ **095b TrajCast/WGAN at n=30** (landed 2026-05-26): **refutes** the old "ECoMD beats every
  baseline" claim — baselines win on SPX/NDX (see point 5 above).
- ✅ **098c zumdn fine-grid n=30** (landed 2026-05-26): best 5.07/11 — saturated, no lift over cluster.
- **098b zumdn dose-response at n=30**: confirm/kill noisy 098 top `zumdn_s075_lam095=6.67 at n=3`.
- **VaR backtest on 094 holdout** (Mac analysis, blocked on ECoMD unconditional sampler
  limitation — Future Work in paper).
- **ABIDES+SBI calibration shootout** (Paper A headline, blocked on H20 install).

### How to apply

- Cite as the central Paper A §4 claim. Use the phrase "Pareto-bounded" not "architectural
  ceiling" (latter was the 2026-05-13 wording, superseded after 089 landed).
- Figure 1 source: `papers/paper_a_methods/figures/fig1_attribution.py`.
- SOTA cell to cite throughout: `xa_gold_zumdn 5.96 (Gold, zumbach-downside)`. NOT
  `pair_AB 5.18` (2026-05-13 Branch F number, superseded).
- Acceptance estimate after 089-099 5-asset evidence: 22-28% (plan-agent stress test
  baseline 18-25%; cross-asset replication + N-scaling + clean baseline gap +1pp each).
  Further +3-5pp gated on ABIDES+SBI calibration leg (Track D, next week).

### Sources

- `experiments/089_attribution_50seed/attribution_matrix.{md,json}` — Figure 1 source
- `experiments/089b_cross_asset_attribution_30seed/attribution_matrix.{md,json}` — per-asset
- `experiments/092_5asset_replication_30seed/scoreboard.md` — 5-asset confirmation
- `experiments/096_all_pairs_30seed/scoreboard.md` — 23-pair ceiling evidence
- `experiments/097_n_agents_scaling_30seed/scoreboard.md` — N-scaling rebuttal
- `papers/proposal/paper_a_neurips_2027_state.md` §2 — living state doc
