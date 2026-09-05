---
name: pareto-ceiling-11-fact-frontier-in-v3-mechanism-family
description: "089-099 evidence (3000+ runs, 5 assets, 23 pair combinations) shows no single mechanism nor any depth-2 composition reaches mean ≥ 5.5/11; new SOTA Gold zumdn 5.96. Central Paper A §4 claim."
metadata: 
  node_type: memory
  type: project
originSessionId: 32d573d8-fe44-4e40-9577-f55d59632fcb
---

> **2026-09-05 Zumbach-metric quarantine.** The canonical `zumbach_asymmetry` implementation is not
> zero under the time-reversal null: unequal lag geometry makes any reversible process with
> decaying volatility autocovariance score negative. Therefore all exact 11-fact means, SOTA labels,
> Zumbach pass rates and Pareto statements whose witness or cost uses that component are historical
> only pending a separately authorized role-swapped, null-calibrated rescore. The remaining valid
> metrics may still exhibit trade-offs, but they do not establish the eleven-fact claim as written.
> See [[project_ecomd_zumbach_orientation_audit_2026-09-05]].

> **2026-05-28 update:** exp 102/103 (Batch 1) did NOT break the ceiling (0 cells past the
> Bonferroni gate), but exp 102 was an **invalid test** — 3 of 4 multi-fact surrogates were
> dead/degraded at the ~7-return training rollout (see [[surrogate-rollout-length-trap]]). The
> ceiling at ~5.1 still stands as the best *fairly-tested* number; the first fair test of the
> objective-coverage escape is exp 107 (rollout-reg steps=512), running 2026-05-28. Do not cite
> 102 as evidence the ceiling is unbreakable.
>
> **2026-05-29 update:** exp 107 (the fair test) **FALSIFIED** objective-coverage —
> `mf_all_mse_longroll` Δ=+0.13 vs baseline, p=0.81 (surrogates verified live). Hand-built
> per-fact surrogates do NOT break the ceiling; ~5.1 holds. Next escape = exp 104 MMD
> (Path B0, [[project_paper_a_neurips_2027]]). **ABIDES (exp 105) scores only 2–3/11** on all
> 5 RMSC03 variants — vanilla agent-based SOTA also can't reach 11/11, so the ceiling may be
> **paradigm-level, not ECoMD-specific** (a Paper A *upgrade* to "paradigm-SOTA"), but this is
> PENDING a timescale-fair re-run (ABIDES scored intraday-on-daily-bands; volume_vol_corr=1.0
> is an extraction artifact). Don't put the ABIDES comparison in the paper until re-run fairly.
>
> **2026-06-16 update — timescale-fair re-run DONE, ABIDES comparison now paper-usable.** Daily
> mode (each sim-day -> 1 close-to-close return -> 250-pt daily series/cell, 250 seeds x 5 cells,
> scored on the same 10 daily facts dropping volume_volatility_corr): **best cell = morevalue
> 4/10** (others 2/2/3/3). Passes only autocorr/cond_kurt/dfa; **fails every clustering+fat-tail
> fact** (acf2~0, Fano~1, agg~0), and its tails are too THIN (hill 5-7) -- opposite of EcoMD's
> too-fat overshoot. Confirms the ceiling is **paradigm-level**. Section-7 SBI-cost leg also done:
> T_sim~844s => 1k/5k/10k sims = 235/1173/2345 CPU-h. See [[neural-sde-tournament-beyond-framework]].

> **2026-06-18 caveat — the `hill_tail_index` fact is burn-in-contaminated PROJECT-WIDE.** Standard
> scoring computes Hill on a warmup-inclusive per-step series (`run_large.py:107`
> `traj.log_returns_np()[1:]`, no discard). So the "fat-tail overshoot hill≈1.3" and the concave
> in-band "solve" (113/114, hill 1.3→3.0–3.4) are very likely burn-in artifacts — dropping ≥50 warmup
> steps pushes the in-band concave Hill (3.42)→11.5 (too-thin, FAIL). **What this does NOT change: the
> ceiling STRUCTURE is robust / strengthened** — removing wrongly-credited Hill passes only LOWERS
> cell scores, so "no cell reaches 11/11, Pareto-bounded" holds more firmly, not less. But the specific
> SOTA number (gold zumdn 5.96) and any cell leaning on a Hill pass would shed ~1 fact under warmup
> discard (needs R1 to quantify). ABIDES daily (close-to-close) is unaffected. Full:
> [[burnin-artifact-zeta-ed-2026-06-18]], `papers/paper_a_methods/phase0_burnin_blastradius_2026-06-18.md`.

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
