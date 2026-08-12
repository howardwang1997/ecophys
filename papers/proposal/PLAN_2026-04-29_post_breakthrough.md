# PLAN — Post-breakthrough 2026-04-29

**Status**: Tier 4.2 dynamic graph (gate without u) hit **mean 6.10/11
with top 9/11** across 10 seeds — **first reproducible break of the
orthogonal-basin ceiling** since 031–036's hyperparameter sweeps capped
at 3.20. Tier 1.3 features-all (LN-fixed) at 4.90/11 second-best.

This plan supersedes `PLAN_2026-04-28_arch_extensions.md` (which framed
the 6-tier batch as exploratory). With one tier confirmed as a
breakthrough, focus shifts to: (a) confirming reproducibility, (b) finding
constructive composition, (c) understanding the mechanism.

## Key results table (yesterday + today)

| Tier / cell | mean / 11 | top | seeds | notes |
|---|:-:|:-:|:-:|---|
| **t42_dyngraph_no_u** | **6.10** | **9/11** | 10 | ⭐ gate alone, no MEGNet u |
| t13_features_all (LN) | 4.90 | 7/11 | 10 | features + dist/inner_prod normalised |
| t42_dyngraph (with u) | 4.60 | 8/11 | 10 | u HURTS the gate |
| p_1_1__1_3 (memory + features) | 4.60 | 6/11 | 5 | |
| p_1_2__1_3 (het kernels + features) | 5.33 | 7/11 | 3/5 | partial eval |
| 1.1 memory alone | 3.20 | 6/11 | 10 | at par with baseline |
| t41_megnet (u into pair+ext) | 3.00 | 4/11 | 10 | u alone is mildly worse than baseline |
| baseline (no tier) | 3.20 | 6/11 | 10 | from `036/abl_no_chunk128` |

## What we learned about the mechanism

**Dynamic graph (gate) is the only mechanism that breaks the ceiling.**
Other tiers (memory, het kernels, jumps, multi-timescale, ISAB
attention, MEGNet-style u) all stay below or at baseline. The gate's
distinctive feature is that it lets each random pair carry a
**state-conditioned weight** — different (s_i, s_j) pairs contribute
differently. This is exactly the **"different facts need different
topologies"** mechanism we hypothesised:

- `autocorr_returns ≈ 0` needs many independent paths
- `zumbach_asymmetry > 0` needs asymmetric edges
- `hill_tail_index` needs cascade-prone connectivity

A fixed sampling distribution can't satisfy all three; a learnable
gate can route compute differently per pair per step.

**u (MEGNet global state) is a red herring**:
- u alone (3.00) ≈ baseline 3.20
- u + gate (4.60) < gate alone (6.10) — destructive composition
- Tentative explanation: u tries to inject regime info into the V
  surface; gate already does this through pair-level routing. Two
  competing channels don't reinforce — they compete for representational
  capacity.

**LayerNorm was load-bearing**: training-time NaN is not the same as
inference-time NaN. State drifts over 4000 steps, MLPs trained at
state ~ 0.1 fail at state ~ 1+. LN is the correct fix; the 1/√d, 1/d
feature normalisation we did first was insufficient.

## Tonight's batch (105 configs, already pushed)

```
experiments/048_arch_dyngraph_pairs        15  retry partial-eval cells
experiments/049_arch_4_2_no_u_repro        30  seeds 10-39 → 40-seed total
experiments/050_arch_4_2_no_u_pairs        40  gate × {1.1, 1.2, 1.3, 2.1} × 10
experiments/051_arch_4_2_no_u_triples      20  gate + 1.3 + {1.1, 1.2, 2.1}; gate + 1.1 + 2.1
```

Launcher: `scripts/h20_overnight_2026-04-29.sh` on `feature/megnet-global-state`.

## Decision tree (tomorrow morning)

### Branch A — 6.10 reproduces (049 mean ≥ 5.5, CI-low ≥ 5.0)

**Promote 4.2_no_u as the new baseline architecture.** Update
`abl_no_chunk128` to include `edge_gating_enabled=True` for all
subsequent experiments. Next sprint focus: per-fact analysis →
identify the 2 facts the gate misses → architectural target for
those specifically.

### Branch B — 6.10 was lottery (049 mean drops to 4.0–5.0)

Gate is still better than baseline, but not the breakthrough we
thought. Re-run 047 in parallel with different seeds to see if the
047 sample was unusually lucky. Either way, gate stays in the
toolkit — just not the headline result.

### Branch C — A pair or triple goes above 6.10

Composition works. The orthogonal-basin ceiling has TWO breakable
floors, and we found both. Design a quad/quint stack for the next
sprint. Probably worth a paper section on "architectural depth in
differentiable market simulators" since this would be novel.

### Branch D — Nothing in 050/051 beats 6.10

Gate is the unique active ingredient, other tiers don't help and may
hurt (like u did). Document this as a clean **architectural finding
for Paper A** — a single architectural change (edge gating) breaks
the ceiling, no stacking required. This is actually the CLEANEST
narrative for a top-tier paper: one mechanism, one effect, large
margin (3.20 → 6.10 = nearly 2× the gap).

## Per-fact analysis priority

Once `049/results_t42_dyngraph_no_u_seed{?}` lands, run for the top
2-3 seeds (the 9/11 + 7/11 + 7/11 ones from 047):

```bash
conda run -n ecophys python scripts/perfact_analysis.py experiments/047_arch_tier_4_2_dyngraph experiments/049_arch_4_2_no_u_repro
```

Expected: gate covers most facts but consistently misses 2. Those
become the next sprint's targets. Likely candidates given prior data:
- `autocorr_returns` (only 6% pass rate across all 94 yesterday's runs)
- `zumbach_asymmetry` (3% pass rate, hardest fact)

If those are the missing 2, the next sprint is **a focused
intervention on autocorr + zumbach with the gate-as-baseline.**

## Outside today's batch

Things explicitly NOT in tonight's run, queued for next sprint:

1. **Per-edge state with persistence** (Tier 4.3 candidate): edges
   "remember" being active. Heavy implementation, only worth doing if
   tonight's triples plateau.
2. **Discrete top-k routing** (Switch Transformer style): hard
   sparsification rather than soft. Skip unless we want compute savings
   at N=100K.
3. **Loss redesign sprint**: distribution-level loss (W2,
   score-matching) could naturally cover all facts simultaneously.
   Ortho to gate; could compose. Not in this batch.
4. **Inference-time stability**: even with LN, `p_4_2__1_3` (gate +
   features WITH u) NaNs reproducibly. Investigate as standalone task
   if we ever need that combo.

## Paper-A implications (if 6.10 confirmed)

- **§3 Method**: Tier 4.2 is the headline architectural contribution.
  Frame as "learnable edge gating for differentiable market
  simulators". The gate's regime-awareness comes from state-dependent
  per-edge weighting, not global state injection (the latter we tried
  and it hurt).
- **§4 Results**: 11-fact coverage table; bootstrap CI on 40 seeds.
- **§5 Ablation**: gate vs gate+u (interference), gate vs no-gate
  (3.20 → 6.10 step), LayerNorm necessity for inference stability.
- **§6 Discussion**: orthogonal-basin ceiling and how dynamic topology
  resolves it. This is a genuine NeurIPS/ICML angle if it holds up.

## Risks

| Risk | Mitigation |
|---|---|
| 6.10 doesn't reproduce — sample noise | 049 brings sample to 40 seeds; bootstrap CI will be tight enough to settle this |
| Gate is sensitive to k_random / gate_init_p / LN — fragile | Followup ablation: scan k_random ∈ {25, 50, 100}, gate_init_p ∈ {0.5, 0.7, 0.9}, LN on/off. If gate only works at one specific config, that's a generalisation concern. |
| Gate's gain comes from compute (it's effectively learning to focus on a smaller graph) | Not a problem — k_random=50 is fixed. The gate does soft re-weighting of the 50-pair pool, not pruning. Still O(N·k) compute. |
| The "u hurts gate" finding is artefact of our specific u | Try different u architectures (GRU vs SSM vs no-recurrence) in future ablation. Out of scope tonight. |

## Verification log

- 75 tests pass after LN fix (test_arch_extensions, test_dynamic_graph,
  test_global_state, test_potentials).
- Mac smoke: triple gate+1.3+1.1 finite + gradient flows.
- 105 new configs all parse cleanly via `EcoMDConfig + LossWeights`.
- Branches `feature/megnet-global-state` and `feature/arch-extensions`
  both pushed with the LN fix.
