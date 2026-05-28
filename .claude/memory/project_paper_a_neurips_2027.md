---
name: paper-a-target-neurips-2027-problem-diagnose-solve-framing
description: "Paper A NeurIPS 2027 framing pivoted 2026-05-21 from \"falsification tool\" (headline negative) to \"problem→diagnose→solve\" (headline positive). Track A memk + Track B-β scheduled-sampling + Track B-α Hopfield are primary parallel; B-γ adversarial + B-MACEv2 secondary; C multi-obj fallback."
metadata: 
  node_type: memory
  type: project
  originSessionId: d8f75917-cbc6-43cc-814b-11508430a13a
---

**Target**: NeurIPS 2027 main, deadline ~2027-05. Plan-agent reviewer-2 stress test estimates: 18-25% under old "falsification tool" framing; **30-40% target** under new "problem→diagnose→solve" framing (2026-05-21 pivot, conditional on ≥2 of Track A/B-β/B-α succeeding at 5-asset mean ≥6.0). M3 (arXiv) shifts Wk 28 → Wk 32.

## 2026-05-21 framing pivot — headline POSITIVE

User instruction: "我不希望 Paper A 的主要 claim 是一个负向的 claim。我希望在提出了一个负面问题之后，我们还应该设计方法去解决这个问题。"

**Old headline (deprecated)**: "Differentiable simulator as falsification tool" — too negative; reviewer-2 reads as "we did ablation and found a limit, so what?"

**New headline**: "We discover an empirical Pareto frontier in hand-crafted Markov mechanism families (§4 motivation), then introduce architectural extensions that break it (§5-6), and demonstrate gradient-based calibration at ~100× ABIDES+SBI wall-clock (§7 utility)."

Five constructive solution tracks (paper §5-6 candidates):
- **Track A** — Memory kernels (memk). **FAILED at n=30, demoted 2026-05-26** (best 5.00/11; see below)
- **Track B-β** — Scheduled-sampling depth-3 (1-1.5 wk, lowest risk; borrows TrajCast NMI 2025 trick)
- **Track B-α** — Hopfield regime attractors (Ramsauer 2020) replacing GRU regime (2-3 wk, highest claim value)
- **Track B-γ** — Adversarial per-fact discriminator (3-4 wk, GAN stability risk)
- **Track B-MACEv2** — MACE-lite v2 with explicit failure-aware fixes (canonical failure case; pre-flight gated; see [[project_mace_lite_failure]])
- **Track C** — Multi-objective Pareto (fallback only, 5/5 B-track failures required to demote)
- **Track D** — ABIDES+SBI calibration shootout (independent parallel, §7 utility)

User confirmed (2026-05-21): B-β + B-α 并行 primary; B-γ adversarial 可以做; B-MACEv2 可以做但要记住 prior failure; C 是退路, 不轻易接受.

## 2026-05-22 — B-β and B-α both implemented + pilots queued

Both Track B-β and B-α landed on `feature/paper-a-neurips-2027` in two
commits: `72d75bf2` (B-β) and `e0e4ec48` (B-α). Track B-α scope was reduced
from spec-estimated 3-5 days (480 LoC) to ~210 LoC by skipping the literal
"per-prototype mechanism mix" force-pipeline refactor — instead K mechanism
mixes emerge implicitly from K learned prototype embeddings + the existing
RegimeReadHead non-linear pipeline. Minor expressivity reduction (sharp β
recovers the spec's behavior exactly; soft β approximates a mixture). Worth
keeping in mind if B-α pilot shows surprisingly flat results.

**Implementation locations** (verify before recommending future edits):
- B-β: `ecomd/training/scheduled_sampling.py`, plumbed through
  `ecomd/physics/integrator.py` (noise_scale_mult on step),
  `ecomd/models/ecomd.py` (5 EcoMDConfig fields + step + rollout_chunk),
  `ecomd/models/bptt_step_function.py` (custom Function fwd + bwd),
  `ecomd/training/train_distributed.py` (ScheduledSamplingState per run)
- B-α: `ecomd/models/hopfield_regime.py` (drop-in replacement for
  `RegimeGRU`), `ecomd/models/ecomd.py` (regime_kind branching, default
  "auto" preserves legacy bit-exact)

**Weekend H20 queue** (`scripts/h20_weekend_2026-05-22.sh`):
6 phases × 2560 cfg ≈ 47h wall-clock on 8-card H20 (96h calendar budget,
~49h buffer):
1. 099B memk n=30 (Track A decision gate)
2. 098C zumdn fine-grid (§4 figure surface)
3. 095B WGAN+TrajCast n=30 (§4 baselines)
4. 098D Asset×Mode 2×3 (§3 098B-regression diagnosis;
   {SPX, joint_5} × {none, abs, downside})
5. B-β pilot (6 max_prob × 5 sigma_mult + baseline, 930 cfg)
6. B-α pilot (3 K × 4 β × 2 update_every + baseline, 750 cfg)

**Determinism fix landed 2026-05-22 Session 2**:
`ecomd/models/potentials.py:_sample_edges` now uses `self._step_generator`
(set by `EcoMDSimulator.step` at the top of each inner-step loop) for
`torch.rand`. Backward-compat default `None` → global RNG. Verified:
340/340 tests pass; `torch.set_num_threads(1)` + the fix gives bit-exact
identical loss across two sequential in-process `train_distributed`
calls (max diff 0.00e+00). Residual multi-threaded CPU drift is BLAS
reduction-order non-determinism (not in our code) — mitigated by
`torch.set_num_threads(1)` in Mac smoke scripts when bit-exact A/B is
needed. H20 unaffected (per-cfg torchrun isolation). `ecomd_v2.py:135`
has the same pattern but V2 is non-primary; deferred. Filed in
`logs/2026-05-22.md` Session 2.

## 2026-05-26 — weekend-batch results landed (Mac re-score, canonical scorers)

The 2560-cfg weekend batch (commits `50561de5`+`e9bf2ed6`) is in. Re-scored locally — **the
"solve" arc has no winner yet, and a baseline-parity risk opened**:

- **Track A memk — FAILED, demoted.** Best `memk_s025_lam090`=5.00/11 (n=28), barely above
  `baseline_v3`=4.64 (z=0.97, n.s.). No hidden operating point.
- **Track B-β scheduled-sampling — "not broken" but not better.** Best `bb_p010_s250`=5.10/11,
  top of a 31-cell noise distribution (no monotone trend in p or σ). z=1.22 vs baseline, n.s.
- **Track B-α Hopfield — flat ridge.** Best by mean `ha_K06_b016_u08`=5.10/11; z=1.30, n.s.
- **⚠️ NONE of A/B-β/B-α beats `baseline_v3` at p<0.05** even *before* multiple-comparison
  correction; all winners are best-of-6…31 cells (winner's curse). After Bonferroni, all n.s.
  This means the §4-final acceptance condition ("≥2 of A/B-β/B-α at 5-asset mean ≥6.0") is
  **currently UNMET** — the 30-40% estimate is at risk until a real lift appears.
- **The "first-ever 11/11" (`ha_K04_b016_u08_seed13`) is a seed-lottery artifact**, not a
  ceiling break: that cell's mean is 4.97±1.71 (n=30), seed 13 is the only seed ≥8 (3.6σ),
  winning by passing the two architectural-floor facts (`hill_tail_index`, `zumbach_asymmetry`)
  ~2/30 siblings pass. **Report the cell mean, never seed 13.** Per [[feedback_seed_count_lottery]].
- **⚠️ Baseline-parity kill-shot risk.** On the common 10 facts, TrajCast/WGAN baselines beat
  every weekend ECoMD cell on SPX/NDX (see [[project_pareto_ceiling]] point 5). Tooling fixed
  (`score_summary.py`/`score_phase.py` `--exclude`); the defensible Paper A claims are the
  mechanism-independent ceiling + capabilities baselines lack (volume channel, mechanistic
  knobs), NOT raw fact-count superiority.

**Implication for framing:** the *diagnose* half is strong (ceiling reconfirmed 5.1–5.2 across 4
mechanism families × 30 seeds); the *solve* half (§5-6) has produced no significant lift. If no
B-track delivers, fall back to the diagnose-centered framing with B-β/B-α/memk as
**negative controls** establishing mechanism-independence (deferred decision, 2026-05-26).

### 2026-05-26 Session 2 — root cause + Batch 1 (exp 102/103) launched

**Root cause of the ceiling is the OBJECTIVE, not the architecture.** The loss
(`ecomd/training/losses.py`) optimised only 3 moments (acf_sq/leverage/hill ≈ facts #6/#9/#2);
**8 of 11 facts never entered the gradient**. All four failed tracks added *capacity* to a
3-moment loss. Confirmed: all weekend configs were `loss_family: moments, distance_mode: l1`; the
dormant `compute_loss` distributional families were never swept except Wasserstein (exp `085`),
which **lost to baseline** (4.46 vs 4.64). So matching the whole return marginal is a spent lever
— **explicit per-fact surrogates** are the move. Also corrected: `baseline_v3` ALREADY stacks
global_state + edge_gating + twopop + SPS + t-noise, so those are NOT untested levers (real
untested config-only levers: isab pairwise, inner_steps>1, agent_memory).

**Built + pushed** (`b6ccf73f`, `e8d30cc2`): `ecomd/training/fact_surrogates.py` (differentiable
#3/#4/#5/#8 + surrogate-kill tests ρ>0.6); `multi_fact_terms` wired into both loss paths;
`train_distributed` routed through `compute_loss` (fast-path = legacy bit-exact) so mse/huber
distance + multi-fact terms take effect. **Batch 1 (2-day, review 2026-05-28 AM)**: exp
`102_multifact_loss_n30` (420 cfg, Thread 1 primary) + `103_arch_expanded_loss_n30` (390 cfg,
arch × expanded loss), SPX screen, launcher `scripts/h20_batch1_2026-05-26.sh` (~22h). MMD (104)
+ learned-diffusion (3c) deferred to Batch 2; Track D (105) = ABIDES-install handback. 5-28 review
promotes SPX winners → 5-asset confirm (exp 106) under the significance gate (Δ>0 vs baseline,
Bonferroni p<0.05, **not best-of-N**). See [[project_pareto_ceiling]], [[feedback_seed_count_lottery]].

### 2026-05-28 — Batch 1 reviewed: exp 102 was an INVALID test (not a refutation)

5-28 gate: **0/14 (102) and 0/12 (103) cells beat `baseline_v3` at Bonferroni p<0.05** — no
exp-106 promotion. But the 102 "negative" does **not** refute objective-coverage; it never
tested it. Root cause (`scripts/diagnose_surrogate_coverage.py`): training rollout feeds only
~7 returns (`chunk_steps=24`, `warmup_steps=16`, `train_distributed.py:490-493`), but the
surrogate length guards need more — `soft_fano` n≥50, `dfa_hurst_surrogate` n≥~200,
`agg_gaussianity` n≥400 for the correct (k1−kL) signal (`fact_surrogates.py:81-82,111-113,147-149`).
So **`mf_fano`/`mf_dfa` were bit-identical to baseline (zero gradient, 30/30 seeds)** and `mf_agg`
optimised a degraded k1-only signal (explains it hurting to 4.33). Only `gain_loss_skew` was live,
and where surrogates were active they moved the target fact toward band **with zero collateral**
— a weak *positive* signal. 103: ISAB dead (2.2–3.1); `inner_steps>1`/`agent_memory` blow up
`aggregational_gaussianity` on ~40–50% of seeds (real instability); `agentmem_inner4` 5.41 is
survivorship (13/30 rejected). **Objective-coverage = untested, not falsified.**

**Path A (exp 107, launched 2026-05-28):** config-only fix — enable rollout-reg
(`_compute_rollout_reg_loss`, 057) at `rollout_reg_steps=512` so all 4 surrogates are live while
peak memory stays one chunk (respects [[project_chunk_oom_constraint]]); N 10K→2000 + bf16.
Verified on Mac N=500: all 4 `grad_fn=LIVE`, gradient reaches params. Deconfounded 3-cell ladder:
`baseline_v3` → `longroll_moments` → `mf_all_mse_longroll`. **Pre-registered failure: if
`mf_all_mse_longroll` ≤ `baseline_v3` (Bonferroni p<0.05) → objective-coverage falsified → Path B
(heterogeneous-node MoE first).** ABIDES ceiling probe (exp 105) runs in parallel and sets the
Paper A narrative (≤4/11 → paradigm-SOTA = *upgrade*; ≥9/11 → Path C). Full ladder:
`papers/proposal/plan_v3_addendum_2026-05-28.md`. Discipline per [[feedback_no_downgrade]],
[[project_surrogate_rolloutlen_trap]], [[feedback_h20_day_budget]].

## Current SOTA cell (2026-05-20, supersedes pair_AB 5.18)

`xa_gold_zumdn = 5.96 ± 1.54 (n=26, 5/26 ≥8/11)` from 092_5asset_replication_30seed.
Cross-replicated: 089 SPX 5.12 (n=48), 090 SPX 5.31 (n=29), 089b EURUSD 5.36 (n=28).

## Main claim (post-pivot)

ECoMD is a differentiable MD-style market simulator with mechanism-decomposable dynamics. (1) Systematic ablation reveals an empirical Pareto frontier in hand-crafted Markov mechanism families, with no cell exceeding 5.5/11 stylized facts on 5 assets at n=30. (2) Four architectural extensions — non-Markov memory kernels, scheduled-sampling depth-3 training, Hopfield regime-attractor dynamics, and (with failure-aware safeguards) learned MACE-lite v2 potentials — are individually evaluated; the winning combination lifts the frontier to ≥6.5 on ≥3 assets. (3) Gradient-based posterior inference calibrates ECoMD ~100× faster than ABIDES+SBI at matched coverage.

## Why the pivot

Negative-headline papers face ~15% NeurIPS acceptance ceiling regardless of evidence strength (reviewer-2 default: "you found a limit, you didn't solve it"). The 089-099 data alone supports a problem-diagnosis arc but not a solution arc — so Wk 17-22 dev is allocated to building the solution arc before submission.

## Critical reminders

- **MACE-lite v1 is the canonical failure case** (2026-04-22, 0-4/11 across 8 ablations). Any new learned-potential work must respect this. See [[project_mace_lite_failure]].
- **Baseline-parity kill-shot (2026-05-26)**: on the common 10 facts, TrajCast/WGAN beat every weekend ECoMD cell on SPX/NDX. Never write "ECoMD reproduces stylized facts better than baselines" without the asset-specific caveat + the volume-channel capability argument. See [[project_pareto_ceiling]].
- **Report cell means, never lottery seeds** — the `ha_K04_b016_u08_seed13` 11/11 is a 3.6σ artifact. Per [[feedback_seed_count_lottery]].
- **n<20 seed counts forbidden in paper** per [[feedback_seed_count_lottery]] (4 confirmed hits).
- **Goodhart on single-moment loss** — `scaling_v1.md` §5; all Track B losses must use shape constraints not just lag-1 values.
- **5-asset n=30 replication discipline** — every paper claim requires this minimum.

## How to apply

Any Paper A discussion defaults to:
1. NeurIPS 2027 timeline (M3 arXiv Wk 32, submission Wk 60)
2. Problem→diagnose→solve arc (ceiling is motivation, not conclusion)
3. Track A/B-β/B-α primary parallel; Track B-γ + B-MACEv2 secondary; Track C fallback only
4. New experiments: ask "does this strengthen Track A or one of the Track B candidates or Track D?" If neither, defer.

Current plan doc: `papers/proposal/paper_a_next_steps_2026-05-21.md`.

## Supersedes

- 2026-05-13 "falsification tool" headline (kept in §2.2 historical state doc for record)
- `papers/paper_a_methods/outline.md` ICAIF 2026 framing (kept for history)

## Related

- [[project_pareto_ceiling]] — §4 motivation
- [[project_arch_floors]] — Pareto reframe of floors
- [[project_mace_lite_failure]] — Track B-MACEv2 failure-aware constraint
- [[project_branch_f_088]] — superseded SOTA
- [[feedback_seed_count_lottery]] — n=30 minimum discipline
