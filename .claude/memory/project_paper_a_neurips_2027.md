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
`mf_all_mse_longroll` ≤ `baseline_v3` (Bonferroni p<0.05) → objective-coverage falsified → Path B,
**first move = exp 104 MMD with long rollout** (085's Wasserstein negative is a suspect
rollout-length artifact — chunk_steps=24 ~7 returns; MMD/W are implemented but unwired,
need `target_returns` threaded in), then heterogeneous-node MoE.** ABIDES ceiling probe (exp 105) runs in parallel and sets the
Paper A narrative (≤4/11 → paradigm-SOTA = *upgrade*; ≥9/11 → Path C). Full ladder:
`papers/proposal/plan_v3_addendum_2026-05-28.md`. Discipline per [[feedback_no_downgrade]],
[[project_surrogate_rolloutlen_trap]], [[feedback_h20_day_budget]].

### 2026-05-29 — Path A FALSIFIED; ABIDES weak; Path B0 (MMD, exp 104) launched

**Path A (exp 107) failed its pre-registered gate.** Welch+Bonferroni vs the new
N=2000 baseline_v3: `mf_all_mse_longroll` 4.27±2.11 (n=26) vs 4.14±1.70 (n=22),
Δ=+0.13, **p=0.81**; `longroll_moments` Δ=−0.09, p=0.86. Surrogates were LIVE this
time (pre-flight verified) → a fair, clean null. **Hand-built per-fact surrogates
do NOT break the ceiling — objective-coverage falsified.** Escalate (no downgrade).

**Two findings:** (1) the N=2000+bf16 budget regime is **unstable** — baseline_v3
went 2/30→8/30 rejected (agg-gaussianity blowup), mean 4.64→4.14. Since
`_compute_rollout_reg_loss` is truncated BPTT (peak mem = one chunk), N=2000 was a
throughput choice not a memory need → Path B runs at **N=10K, fp32**
([[project_chunk_oom_constraint]]). (2) **ABIDES (exp 105) = 2–3/11** on all 5
RMSC03 variants — vanilla agent-based SOTA misses fat tails/clustering/asymmetry.
⇒ "paradigm-SOTA" framing (≤4/11 = *upgrade*) is on the table, **pending a
timescale-fair re-run** (ABIDES ran intraday 60s/390-bar but scored on daily bands;
volume_vol_corr=1.0 is an extraction artifact → mark N/A).

**Path B0 built (exp 104 — MMD long-rollout, next H20 run):** wired `target_returns`
into the rollout-reg path only — losses.py now SKIPS the distribution-distance term
when target_returns is None (instead of raising), so MMD fires only on the 512-return
rollout, never the ~7-return main loop. **w_mmd calibration (key catch):** raw MMD
~0.012 vs structural ~1.16, so w_mmd=1 is negligible (an invalid test, surrogate-trap
déjà-vu) → cell is a SWEEP `w_mmd∈{20,50,100}`. 150 cfg, N=10K fp32, steps=512 every=2.
Launcher `scripts/h20_104_mmd_2026-05-29.sh --probe` gates on a single-config
timing+stability check. **Pre-registered: if NO mmd_w* beats hybrid_nomm_longroll
(Bonferroni p<0.05/3) AND none exceeds baseline_v3 → distribution-matching falsified
across a 5× weight range → Path B2 (heterogeneous-node MoE).** Winner → exp 106
5-asset (no best-of-N). See [[project_surrogate_rolloutlen_trap]].

### 2026-06-01 — Path B falsified (broad tournament); the DIAGNOSE is the paper

The beyond-framework tournament ([[project_neural_sde_tournament]], exp 109/108/110/111,
verified on Mac) **closes the "solve" arc with no winner**: Path B0 MMD, Path B2 MoE
(mixture-of-Gaussians), the SV head, and A3 diffusion **all fail to break ~5.1-5.2**. The
decisive new fact: the **fat-tail overshoot is DYNAMICAL, not distributional** — Gaussian noise
+ zero jumps (109 `normal_j00`) still gives hill=1.30 (deep α<2). So no objective/noise/mixture
knob fixes it; it's emergent from the excess-demand dynamics.

**This makes the diagnose strong enough to BE the paper, honestly.** Reframe: Paper A's central
contribution is a **per-fact Pareto frontier across three modeling paradigms** where tail-shape
and volatility-dynamics are mutually exclusive — physics-sim (EcoMD) reproduces dynamics
(clustering acf2~0.25, long-memory, leverage) but structurally overshoots tails (hill<1.5);
deep-generative (diffusion) reproduces tails (hill~3 in-band) but kills dynamics (acf2~0.09,
agg too Gaussian); agent-based (ABIDES) reproduces neither (2-3/11). Both hill AND agg-gaussianity
**flip the sign of their error** between the physics and generative paradigms — a clean figure.
The §5-6 "solve" tracks (memk/B-β/B-α/MMD/MoE/SV/diffusion) become **negative controls
establishing the frontier is paradigm-level, not a capacity artifact.** Owed for the figure:
**ABIDES timescale-fair re-run** (multi-sim-day→daily). One untested mechanistic lever noted but
likely Pareto-blocked: a tail-clamp in the price-formation map (would probably kill acf2).
**Pending user decision: commit to diagnose-centered framing vs. keep hunting a solve.**

### 2026-06-03→06 — concave √-impact SOLVE landed (113/114); weekend sprint driver built

**The solve arc reopened and landed at the per-fact level.** Exp 113 (SPX n=30): concave price
impact `β·sign(ED)·|ED|^δ` thins the dynamical tail overshoot INTO band while preserving
clustering — `concave_d050` net 5.60 vs baseline 4.23 (p=0.0014, d=0.90), hill 13→80% in-band,
no ≥20pp collateral; hill(δ) linear (r²=0.98), crossing hill=3 at **δ*≈0.509 = the TLB
square-root law**, and learnable-δ self-calibrates to ≈0.5.

**Exp 114 (5-asset confirmation) verdict — scored 2026-06-06, both halves reported honestly:**
- Pre-registered strict per-asset gate (Welch+Bonferroni α_eff=0.002): **2/5** (spx ✓ btc ✓;
  ndx 0.0065 / gold 0.051 / eurusd 0.062 ns). Power artifact: n=30 at α_eff=0.002 only powered
  for d≥1.0; observed d=0.50–1.07, direction 5/5, pooled Stouffer p≈1e-8.
- **Physics gate 5/5**: every asset hill 1.2–1.5 → 2.9–3.25, acf² in band, worst collateral −6pp.
- δ* 2-point fits are noise (bootstrap CI [−0.2,1.4] on ndx/eurusd); spx 5-point fit
  δ*=0.508 [0.463,0.540]. Exp 118 (δ∈{0.40,0.60} × 4 assets) closes this.
- **User decision: honest reporting, NO seed top-up, no gate-shopping.** Paper wording:
  "band-recovery universal (5/5), δ*≈0.5 crossing, strict per-asset gate 2/5 (power-limited)".

**Weekend window (2026-06-06→08, single unattended 36–48h, EVAL_H=8 reserve):**
`scripts/h20_sprint_driver.sh` orchestrates the whole fleet one-command (see
[[project_h20_fleet_scheduling]]): H20-1 = 115 composition (concave+SV, G1: beat SOTA 5.96) →
auto-scored G1 → champion (exp 119, winner × 4 assets n=30, **baselines+SPX reused** — 113/114/115
verified identical recipe: 108 baseline_mmd base + reg_every=4) or δ-grid fallback; H20-2 = 116
criticality FSS (Paper B fork GO/NO-GO) + δ-grid eurusd; H20-3 = δ-grid ndx→btc; H20-4 = ABIDES
timescale-fair re-run. G1 verdict + champion result land in the window — update this memory after.

`xa_gold_zumdn = 5.96 ± 1.54 (n=26, 5/26 ≥8/11)` from 092_5asset_replication_30seed.
Cross-replicated: 089 SPX 5.12 (n=48), 090 SPX 5.31 (n=29), 089b EURUSD 5.36 (n=28).

### 2026-06-09 — weekend verdict + Paper A week sprint (honest spine FINAL)

**Weekend sprint (115/116/118/119) landed; the ambitious legs FAILED — spine collapsed to its
honest core:**
- **G1 (composition beats SOTA 5.96) = FAIL** (115); **champion (119) pooled 4.90 < 5.96, and SV
  does NOT compose → the "≥2 composable mechanisms = method" leg BROKE.** No SOTA-break. Do NOT
  re-chase it (failed twice — burning the week on it is where quality dies).
- **116 criticality FSS = Paper B fork NO-GO** (smooth crossover, no critical point — see
  [[project_neural_sde_tournament]] 2026-06-09).
- **118 δ-grid = strongest result**: δ\*≈0.51±0.01 universal across spx/gold/eurusd/ndx (btc "0/60"
  was an H20-clone bug — btc parquet IS present locally).
- **HONEST SPINE (final): diagnose (3-paradigm ceiling) + concave-impact solve + δ\*≈0.5
  universality.** Solid NeurIPS methods+physics, ~18-25%. It will NOT become a SOTA-break paper.

**Week plan LAUNCHED** (runbook `papers/proposal/launch_paperA_week_2026-06-09.md`, pre-reg
`papers/proposal/prereg_2026-06-09_power_topup_and_delta_grid.md` — frozen before results):
1. **δ-grid ext** δ∈{0.35,0.55}×5 + btc (118 gen now takes `--deltas`, +spx) → ≥6 δ pts/asset.
2. **n=30→60 power top-up** on ndx/gold/eurusd (114 gen now takes `--assets/--cells/--seed-start/-end`)
   — pre-registered, **reverses the prior "no seed top-up" decision** (user 2026-06-09) to lift the
   strict per-asset gate from 2/5.
3. **exp 117 leverage** 2nd-mechanism sweep (`experiments/117_leverage/`, NEW): concave_d050 +
   {asym_drag_alpha, zumbach_feedback downside} — mechanisms ALREADY in `integrator.py` (no new
   physics). GREEN-lit + reframed: **concave_d050 already passes `leverage_effect` (-0.98, n=30)**,
   so 117 = confirm/strengthen per-seed pass-rate, not from-scratch. Timeboxed (drop if no clean win).
4. **ABIDES timescale-fair daily re-run** — `scripts/h20_abides_baseline.sh` fixed: threads
   `--drop-facts`, `MODE=daily` → `results_*_daily/` + auto-drops volume_volatility_corr.

**Two rigor findings (Mac, cached data, 2026-06-09):**
- **Surrogate-kill (`scripts/score_surrogate_kill.py`): concave solve SURVIVES** — net 7/11 >
  GARCH-t 5/11, structural (zumbach/leverage/dfa) 2/3 > GARCH 0/3. **CRITICAL caveat: the hill+acf²
  2-fact gate IS GARCH-t-FAKEABLE** (GARCH-t hill 2.38✓ acf² 0.19✓) → the paper must lead with the
  JOINT 11-fact + structural facts a null can't fake, NOT the 2-fact gate.
- **3-paradigm frontier (`scripts/assemble_frontier.py` → `fig_frontier_3paradigm.png`, draft):**
  **EcoMD-concave is the ONLY cell passing hill✓ AND acf²✓ (net 7/11)**; all neural baselines
  (WGAN/TrajCast/diffusion) pass hill but FAIL acf² (~0.1, no clustering); ABIDES 2/11. The clean
  "tails XOR dynamics" figure. TODO finalize: swap the real 5.96 SOTA cell into SOURCES + ABIDES
  `_daily` once the re-run lands.

### 2026-06-12 — week-sprint results landed: δ* universality DOWNGRADED; top-up did NOT rescue gate

Pulled the 06-10/11/12 H20 dumps (822 files, dumps only — no H20-side log). All week-sprint cells
now complete: **118 δ-grid at full 0.35–0.60 lever arm (30 seeds/cell); 114 power top-up landed**
(eurusd/gold baseline+d050 → 60 seeds, ndx_concave_d050 → 40). Re-scored on Mac with the canonical
scorers. **Two pre-registered claims moved against us — report honestly, do NOT gate-shop:**

- **δ\*≈0.5 is NOT universal** (`scripts/score_delta_grid.py`, authoritative). Per-asset OLS
  hill(δ) + bootstrap-over-seeds δ\* CI: spx 0.508 [0.463,0.540] ✓, **ndx 0.531 [0.514,0.555] ✗**,
  gold 0.513 [0.495,0.534] ✓, eurusd 0.521 [0.499,0.555] ✓, btc 0.508 [0.486,0.530] ✓ → **4/5
  cover 0.5; ndx deviates** (CI excludes 0.5 by 0.014 — marginal but a clean pre-reg exclusion).
  The 2-point fits (ndx 0.589 / eurusd 0.658) WERE largely noise: **eurusd corrected to 0.521
  (covers 0.5), but ndx's is a real ~3% deviation.** ⇒ the 2026-06-09 "δ\*≈0.51 universal across 4
  assets" line is **superseded** — honest headline is now "4/5 consistent, ndx small significant
  deviation." (Caveat for referee: hill(δ) line r²=0.22–0.31 — large per-seed scatter; slope
  strongly negative + δ\* CI tight from 150–180 pts, but the linear fit approximates a possibly
  curved hill(δ). Open: test true inverse-cubic form — may pull ndx back toward 0.5.)
- **The n=30→60 power top-up did NOT lift the strict gate** (`score_concave_confirm.py`). Even at
  n=60, JOINT hill+acf² Bonferroni gate still **2/5** (spx p=0.0014 d=0.90, btc p=0.0002 d=1.07;
  gold p=0.051 d=0.53, eurusd p=0.062 d=0.50, ndx p=0.0065 d=0.75 all ns). **gold/eurusd are
  genuinely marginal (medium effect d≈0.5 + noisy discrete net-fact metric), not underpowered** —
  more seeds won't rescue them. ⇒ frame the solve via the **pooled mechanism + frontier**, not
  per-asset 5/5: pooled hill_tail in-band **7%→81% (+73pp)**, worst collateral −6pp (gate PASS);
  concave is the only hill✓+acf²✓ cell ([[project_neural_sde_tournament]] frontier).
- **Tooling bug to fix:** `score_concave_confirm.py:139` prints "...√-law crossing is UNIVERSAL" —
  **hardcoded**, reads the stale 2-point δ\* column, now contradicts `score_delta_grid.py`. Fix
  before exporting any figure/table from it. Log: `logs/2026-06-12.md`.

**Net effect on the honest spine:** still diagnose + concave solve + δ\*, but pillar 3 is now
"δ\*≈0.5 holds 4/5, ndx deviates" (not universal), and the solve is pooled-effect/frontier framed
(not per-asset 5/5). Slightly weaker than the 06-09 framing; ~18-25% NeurIPS unchanged in spirit.

### 2026-06-13 — TAIL-TRANSFER DERIVATION added + verified (δ≈0.5 is now DERIVED, not fitted)

The δ≈0.5 result gained a clean derivation — the paper's theory backbone. **Tail-transfer lemma:**
if excess demand has tail index ζ_ED and impact is Δp=β·sign(ED)·|ED|^δ, then the return tail index
**α = ζ_ED/δ** (exact change-of-variables on regularly-varying tails). So the crossing to the
empirical inverse-cubic (α=3, Gabaix 2003) is at **δ* = ζ_ED/3**; with the Gabaix half-cubic demand
tail ζ_ED≈3/2 → **δ*=1/2 (TLB √-law)**. δ≈0.5 is the exponent reconciling a half-cubic demand tail
with an inverse-cubic return tail — NOT a fit.

**Verified in-silico on the existing δ-grid** (`scripts/score_transfer_law.py`, no retraining):
the law's parameter-free prediction `Hill·δ = ζ_ED = const` HOLDS — Hill·δ ≈ **1.48/1.60/1.51/
1.55/1.49** (spx/ndx/gold/eurusd/btc), CV 1–9% across the grid, all ≈ the Gabaix 1.5. Two payoffs:
(1) the old "low r²=0.22–0.31" worry was just per-seed scatter — the per-δ *means* are a clean 1/δ
curve; (2) **ndx's δ*=0.53 deviation is now EXPLAINED** by its heavier demand tail ζ_ED=1.60, i.e.
δ*=ζ/3 applied per-asset — the honest headline flips from "4/5 universal, ndx mysteriously deviates"
to "δ*=ζ_ED/3 holds for all 5; δ*=0.5 ⟺ ζ_ED=3/2." **Unifies with exp 109** (dynamical-not-
distributional): dynamics generate the heavy ED tail (ζ); concave impact transfers ζ→α via δ. One
causal chain. Derivation written paper-ready: `papers/paper_a_methods/theory_tail_transfer.md`.

**Owed to close end-to-end (P0):** measure ζ_ED DIRECTLY (Hill on the |ED| series) — currently
inferred via the law. Prediction: ζ_ED≈1.50 (ndx≈1.60). Realizations store only aggregated facts →
needs a short rollout with ED logging (Mac N≤500 or 1 H20 cell). If confirmed, ED-tail→transfer→
return-tail is measured end-to-end. **Paper structure decision (2026-06-13): user wants to SPLIT —
framework/systems paper (ICAIF/tools, repositioned off the refuted "first differentiable" onto
mechanism-decomposability + attribution + calibration) + this findings paper. I advised against
(value is in the method↔finding loop; each half weaker alone) but it's reasonable if driven by
land-grab / guaranteed-pub / disjoint-audience.** Full current state: `results_compilation_2026-06-13.md`.

### 2026-06-18 — TAIL-TRANSFER VALIDATION REFUTED (burn-in artifact); pivot to non-equilibrium-transient frontier

**The 06-13 "δ≈0.5 is DERIVED" headline is down.** The owed P0 (direct ζ_ED measurement) ran on H20
and **refuted** the validation: the ζ_ED≈1.5 / cube-law-3 is a **~20-step burn-in transient**, not a
stationary property (`run_large.py` has no warmup discard). Steady-state ED + return tails are **light**
(Hill α≈4–12). The lemma α=ζ/δ survives (correct identity); its empirical support does not. Full:
[[burnin-artifact-zeta-ed-2026-06-18]] + `papers/paper_a_methods/burnin_artifact_finding_2026-06-18.md`.

**Phase 0 (Mac, 2026-06-18) — blast radius is PROJECT-WIDE, not just tail-transfer.** Standard 11-fact
scoring is also burn-in-inclusive (`run_large.py:107` `traj.log_returns_np()[1:]`, no discard). The
concave "solve" (113/114) is in the blast zone: standard Hill baseline 1.3→concave 3.0–3.4 in-band, but
D1 shows dropping warmup pushes in-band concave Hill (3.42)→11.5 (too-thin, FAIL). So **the 06-09→06-12
honest spine's pillar 2 (concave solve) and pillar 3 (δ*≈0.5) are both contaminated.** Survives: lemma;
ceiling *structure* (only strengthened); ABIDES daily. Verdict doc:
`papers/paper_a_methods/phase0_burnin_blastradius_2026-06-18.md`.

**New framing decision (user 2026-06-18): NOT a methods-warning paper — a positive frontier method+results
paper.** Thesis: *"market fat tails are a non-equilibrium / driven transient; the stationary model is
light-tailed; α=ζ/δ decomposes the transient tail."* Aligns C1 (diff MD) + C2 (non-eq tail genesis) + C3
(crash = the driving), fits Paper B's Nature-Physics non-equilibrium thread better than the stationary
framing. **EARNS-OR-KILLS experiment (pre-registered):** `experiments/123_driven_transient/DESIGN.md` —
shock a steady-state system, test whether the cube-law tail revives + relaxes with the SAME ζ_ED signature
as the t=0 burn-in (H1 control-light, H2 shock-revives, H3 transient, H4 same-as-burn-in, H5 transfer-law;
binding gate). Pass H1∧H2∧H3∧H4 → physics story EARNED; H2 fails → t=0 startup artifact → diagnose-centered
fallback. Stage-1 ≈31h/8-card (spx, news shock, 3 doses + control, n=30). **R2 (rebuild stationary heavy-tail
source) DEPRIORITIZED** — transient framing needs none, and fitting one undercuts "derived not fitted."
Next GPU: Stage-0 plumbing (raw pre-impact ED log + `step()` shock hook + `--windows` estimator) → Stage-1.

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
