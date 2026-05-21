# Paper A — Next Steps (2026-05-21)

**Author**: Claude (reviewer-2 stance)
**Branch**: `feature/paper-a-neurips-2027`
**Supersedes**: framing decision in `~/.claude/plans/089-099-humming-jellyfish.md` §2.3
**Companion**: `papers/proposal/paper_a_neurips_2027_state.md` (living state)

## 1. Framing decision (user-confirmed 2026-05-21)

Paper A 的 **headline claim 必须是正向的 constructive contribution**。
负向发现（Pareto frontier within hand-crafted v3 Markov family）从 **conclusion 位置降为
motivation 位置**：

> "We discover an empirical Pareto frontier in hand-crafted Markov mechanism families
> (§4). We then introduce architectural extensions (non-Markov memory kernels,
> scheduled-sampling depth-3 training, explicit regime-attractor dynamics, and
> revisited learned interaction potentials) that **break** the frontier on 5 assets
> at n=30 (§5–6). The simulator further admits gradient-based posterior inference at
> ~100× ABIDES+SBI wall-clock (§7)."

**问题陈述 → 诊断 → 提出方法 → 验证 works → 实用性论据**——这条 arc 是 Paper A 的 single
narrative line. 任何对它的修改必须保持这条 arc 完整.

---

## 2. Track 总览

| Track | 内容 | Priority | Risk | Time |
|---|---|---|---|---|
| **A** | Memory kernels (memk via 099b n=30) breaks Markov ceiling | in-flight | low | 0 ($) — tomorrow decision |
| **B-β** | Scheduled-sampling for depth-3 rollout stability | **primary parallel** | low | 1-1.5 wk |
| **B-α** | Hopfield regime attractors (replace GRU regime) | **primary parallel** | med | 2-3 wk |
| **B-γ** | Adversarial per-fact discriminator training | secondary | high (GAN stability) | 3-4 wk |
| **B-MACEv2** | MACE-lite v2 with explicit failure-aware fixes | secondary, **failure-aware** | high | 2-3 wk |
| **C** | Multi-objective Pareto-optimal selection | **fallback only**, not lightly accepted | low | 2-3 wk |
| **D** | ABIDES+SBI calibration shootout | independent parallel | low | 1-2 wk |

User instruction 2026-05-21:
- B-α + B-β 并行 (primary)
- MACE-lite v2 可以尝试，**but 必须记住 2026-04-22 失败档案**
- B-γ adversarial 可以做
- C 是退路，不轻易接受

---

## 3. Track A — Memory kernels (Markov-breaking)

**Status**: H20 overnight 099b_memk_refinement_n30 (270 cfg) 在过夜队列。

**Claim if successful**: "Non-Markov memory kernels lift the frontier from 5.5 → ≥6.0
mean on 5 assets at n=30, evidence that the ceiling is in part a Markov-constraint
not an irreducible information-theoretic bound."

**Decision gate (post-099b, ~明天上午)**:
- IF best `memk` cell n=30 mean ≥ 5.5 AND 95% CI lower ≥ 5.2 → **Track A confirmed**, write §5.1
- IF best < 5.5 → memk falls into existing frontier; demote to supporting evidence
- IF best ≥ 6.0 → strong signal, consider memk × Hopfield composition (B-δ extension)

**Time cost**: $0 (已在 H20 跑). Result tomorrow morning.

**Linked to**: `.claude/memory/feedback_seed_count_lottery.md` — n=30 is the minimum;
n<20 cell numbers (e.g., 099 n=5 best 5.80) **不可引用**.

---

## 4. Track B-β — Scheduled-sampling depth-3 (FAST PRIMARY)

### 4.1 Motivation

Branch F depth-3 finding: mean 4.94 → 5.18 → **4.79 → 4.62** with depth. `scaling_v1.md`
§6.2 + TrajCast NMI 2025 suggest this is **rollout drift** (autoregressive drift
during long rollouts), not a fundamental mechanism-class limit.

**Hypothesis**: scheduled-sampling-style perturbation regularization during BPTT chunks
prevents drift, pushing the compositional ceiling from depth-2 to depth-3 or higher.

### 4.2 Design

- **Training-time only**: every chunk during forward rollout, randomly replace
  fraction `p(t)` of the chunk's noise samples with samples from a perturbation
  distribution (Gaussian widen + small bias). `p(t)` starts at 0, ramps to 0.2 by
  chunk 32.
- **Architectural change**: NONE — purely a training trick. Doesn't risk repeating
  MACE-lite architectural mistakes.
- **Hyperparameters**: perturbation σ_pert ∈ {0.5, 1.0, 1.5}×σ_base, ramp schedule
  ∈ {linear, cosine}, max p ∈ {0.1, 0.2, 0.3} — 18 cells × 30 seeds = 540 cfg
- **Loss**: unchanged; we test whether existing moment-matching loss + scheduled
  sampling alone breaks ceiling

### 4.3 Sub-tasks

1. **B-β.1 — Implementation** (Mac, 2-3h): add `scheduled_sampling.py` to
   `ecomd/training/`, expose via `EcoMDTrainConfig.scheduled_sampling` field.
   ~150 LoC.
2. **B-β.2 — Mac smoke** (Mac, 1h): SPX × N=200 × 5 seeds × 2 sched configs.
   Verify training stability + that fact-count doesn't regress below v3 baseline 4.82.
3. **B-β.3 — H20 depth-3 sweep** (~5h H20 wall): 18 cells × 30 seeds. Includes the
   3 best v3 depth-2 cells (zumdn, pair_zumdn_b3, pair_AB) all at depth-3 with scheduled
   sampling on.
4. **B-β.4 — H20 5-asset replication** (~12h H20 wall): best depth-3 cell × 5 assets × 30 seeds.

### 4.4 Decision gates

- B-β.2 smoke regression ≥ -0.5 vs baseline → STOP, mark hypothesis falsified
- B-β.3 best cell mean < 5.0 → drop B-β, write up as negative finding in §5.4
- B-β.3 best cell mean ≥ 5.5 → proceed to B-β.4
- B-β.4 5-asset mean ≥ 6.0 on ≥ 3 assets → §5.2 paper claim solid

### 4.5 Linked

- `papers/proposal/scaling_v1.md` §6.2 — original idea
- TrajCast (Thiemann et al. NMI 2025) — citation borrow
- Existing `ecomd/training/train_distributed.py` — integration point

---

## 5. Track B-α — Hopfield regime attractors (HIGHER-CLAIM PRIMARY)

### 5.1 Motivation

`improvement_paths.md` C4 + Ramsauer et al. 2020 (modern Hopfield).

Current `ecomd/models/regime_latent.py` (206 LoC) is a **black-box GRU**. Hypothesis:
the ceiling is partly driven by **mechanism interference within a single implicit
regime**——agents in different market regimes need different forces, but a single
mechanism mix applied uniformly creates conflicting gradients.

**Modern Hopfield** lets regime states be **attractors of an energy landscape**:
- Explicit, interpretable regime separation
- Different mechanism weighting per regime via attention to stored prototypes
- Regime transitions become saddle-point crossings (Paper B hook!)

### 5.2 Design

```
At each timestep t:
  s_t  → query q_t = MLP_q(s_t, p_t, σ_t)
  Stored regime prototypes Z = [z_1, ..., z_K] ∈ R^{K×d}   # learned, K=4 or 8
  Attention α = softmax(q_t @ Z^T / sqrt(d) · β)            # β=8 (sharp Hopfield)
  Regime mix m_t = Σ_k α_k · θ_mech^{(k)}                    # K mechanism mixes
  Force F_t = Σ_mech m_t[mech] · F_mech(s_t)
```

Key: **K mechanism mixes**, one per regime prototype. Hopfield's sharp attention (β
large) lets each regime use a near-pure mechanism subset.

### 5.3 Sub-tasks

1. **B-α.1 — Hopfield module** (Mac, 3-5 day): `ecomd/models/hopfield_regime.py`
   (~300 LoC). Replace `regime_latent.py` GRU as `regime_kind="hopfield"` option in
   `EcoMDConfig`. Add unit tests for attention shape, gradient flow, prototype
   identifiability.
2. **B-α.2 — Mac smoke** (Mac, 2h): SPX × N=200 × 5 seeds × K∈{4,8}. Verify
   prototype z_k differentiation (cosine similarity matrix shouldn't collapse to
   identity) + training stability.
3. **B-α.3 — H20 5-asset n=30** (~14h H20 wall): K=4 vs K=8 vs no-Hopfield baseline
   × 5 assets × 30 seeds. Cells:
   - `hopf_K4_baseline_mech`
   - `hopf_K4_zumdn_mech`
   - `hopf_K4_full_v3_mech`
   - `hopf_K8_full_v3_mech`
   - `hopf_K4_memk_mech` (if Track A confirms memk)
   - Total ~6 cells × 5 assets × 30 seeds = 900 cfg
4. **B-α.4 — Attribution analysis**: for the winning cell, plot per-regime
   prototype features + per-regime mechanism α_k. **This is paper Figure 2.**

### 5.4 Decision gates

- B-α.2 prototypes collapse (mean cosine sim > 0.9 across K) → re-design attention,
  +1 wk; if still collapses → STOP, demote to §5.4 future work
- B-α.3 best cell mean < 5.5 → still useful as architectural ablation, but not
  ceiling-breaker; write up as §5.3 supporting evidence
- B-α.3 best cell mean ≥ 6.5 on ≥ 3 assets → **§6 paper headline**

### 5.5 Linked

- `improvement_paths.md` C4
- Ramsauer et al. 2020 "Hopfield Networks is All You Need"
- `ecomd/models/regime_latent.py` — existing GRU module to replace

---

## 6. Track B-γ — Adversarial per-fact discriminator (SECONDARY)

### 6.1 Motivation

Current loss = moment matching on (acf_sq, leverage_sum, hill_alpha). **Goodhart-
vulnerable**: model can match a single moment via a constant-variance regime instead
of real clustering (this exact failure was already observed in v1 ablation, see
`scaling_v1.md` §5).

**Adversarial training**: per-fact discriminator gives gradient on **distributional
indistinguishability**, not just moments. Each of 11 stylized facts gets its own
small CNN/MLP discriminator, agents adversarially optimize joint pass-rate.

### 6.2 Design

```
For each of 11 facts f:
  D_f(window) → real / fake             # small CNN, ~50K params each
  Total D params: ~550K
  
Training:
  Inner: D_f update on (real_window, sim_window) for each f
  Outer: ECoMD update on Σ_f BCE(D_f(sim), 1) + λ · moment_match
  
  λ → 0 schedule (warmup with moments, transition to pure adversarial)
```

### 6.3 Risks (well-documented)

- GAN mode collapse → agents find a single distribution that fools all 11 D's at
  steady state, breaks burst-and-decay (same failure mode as MACE-lite per-node
  readout!)
- D_f overfitting → sim_window distinguishable from any real_window
- Hyperparam sensitivity (lr_D / lr_G ratio, λ schedule)

### 6.4 Mitigation

- Spectral normalization on all D_f
- Gradient penalty (WGAN-GP style) on each D_f
- Keep moment-match loss as auxiliary throughout (λ never reaches 0; floor at 0.1)
- Verify burst-and-decay preserved by checking acf(r²) **shape** not just lag-1 value
  (carries forward the `scaling_v1.md` §5 lesson)

### 6.5 Sub-tasks (3-4 wk total)

1. **B-γ.1** Multi-D module (Mac, 1 wk): `ecomd/training/adversarial_loss.py`
2. **B-γ.2** Mac smoke (1 wk): SPX × N=200 × verify stability
3. **B-γ.3** H20 5-asset n=30 (1 wk H20 wall): best config × 5 assets × 30 seeds
4. **B-γ.4** Analysis + §5.5 paper section

### 6.6 Decision gates

- B-γ.2 mode collapse detected (acf(r²) lag-10 deviates from real by > 50%) → drop
- B-γ.3 mean < hand-crafted SOTA 5.96 → "adversarial doesn't help", §5.5 future work
- B-γ.3 mean > B-α / B-β winner → escalate to §6 headline

---

## 7. Track B-MACEv2 — Failure-aware retry (SECONDARY)

**⚠️ CANONICAL FAILURE CASE**: MACE-lite v1 (2026-04-22) failed at **0-4/11 across
8 ablations** with two architectural causes:
1. Force magnitude 60-190× too small (per-node readout smooths contributions)
2. k-NN biased sparsity (loses long-range pair signal, kills burst-and-decay)

**This Track B-MACEv2 is allowed ONLY with explicit safeguards against these
failure modes** (per user instruction "可以尝试，但要记住前面的负面结果").

### 7.1 Required failure-aware design (NON-NEGOTIABLE)

| Failure mode 2026-04-22 | Required mitigation in v2 |
|---|---|
| Per-node readout smooths force | `F = -∇U` via autograd readout (NOT per-edge MLP readout). Confirmed in `improvement_paths.md` C3. |
| k-NN biased sparsity | Hybrid graph: k-NN edges UNION SPS random pairs. Or pure SPS with attention weights (not pure k-NN). |
| Body-order 3/4 smoothing | Default body_order=2. Test 3/4 only if smoke shows comparable force magnitude. |
| Force magnitude 60-190× shortfall | **Mac smoke pre-flight**: measure `||F_v2||` vs `||F_v3_baseline||`. If ratio < 0.5×, STOP — do not commit H20. |

### 7.2 Sub-tasks

1. **B-MACEv2.1 — Pre-flight design review** (Mac, 1 day): write `mace_lite_v2.py`
   in `ecomd/models/` (separate file, NOT overwriting v1's `mace_lite.py` which stays
   as failure record). Implement F = -∇U autograd readout. Add `tests/test_mace_lite_v2.py`
   with explicit force-magnitude assertion against v3 baseline.
2. **B-MACEv2.2 — Mac smoke + GATING TEST** (Mac, 2 day): N=200 × SPX × 5 seeds.
   **Gate**: force magnitude ratio ≥ 0.5× v3 baseline; mean ≥ 4.5 (i.e., doesn't
   regress below v0 floor). If either fails → STOP, document in §5.5 negative
   findings, do not run H20.
3. **B-MACEv2.3 — H20 5-asset n=30** (only if 7.1 + 7.2 pass): ~12h H20 wall.
4. **B-MACEv2.4 — Comparison with B-α / B-β / B-γ results**.

### 7.3 Decision gates

- B-MACEv2.2 force ratio < 0.5× → **HARD STOP**, this is the 2026-04-22 failure
  signature
- B-MACEv2.2 mean < 4.5 → STOP, document as second failure
- B-MACEv2.3 mean < B-α winner → not a headline contributor, optional §5.5
  supporting evidence

### 7.4 Linked

- `papers/proposal/improvement_paths.md` C3 — failure-aware fix proposal
- `papers/proposal/scaling_v1.md` §2 — "Why this beats MACE-lite k-NN" comparison
  table (must inform v2 design)
- `logs/2026-04-25.md` 关键发现 #1, #3 — explicit failure record
- `ecomd/models/mace_lite.py` — v1 module, **keep as failure case**, do not modify

---

## 8. Track C — Multi-objective Pareto-optimal selection (FALLBACK ONLY)

**触发条件 — 必须全部满足才 demote**:
1. Track A (memk) **fails** (n=30 best < 5.5)
2. Track B-β (scheduled-sampling) fails (depth-3 5-asset mean < 5.5)
3. Track B-α (Hopfield) fails (K∈{4,8} 5-asset mean < 5.5)
4. Track B-γ (adversarial) fails OR not yet completed by Wk 24
5. Track B-MACEv2 fails the pre-flight OR H20 mean < B-α winner

只有 **5/5 都满足** 才考虑 Track C. Even 4/5 不构成 demote (e.g., 仍有一条 B-track 在跑就不 demote).

**Why not lightly accepted**: Track C 把 Paper A 从 "method paper that solves a
problem" 退化为 "framework paper that reorganizes a problem". NeurIPS 接受率 ~15%,
显著低于 constructive Track B. Reviewer-2 自然攻击点："multi-objective Pareto 老结果换皮".

If triggered, Track C 还会被设计成 hybrid: 用 trained B-α/B-β/B-γ/B-MACEv2 的局部
improvement (即便每个单独不破 ceiling) 作为 multi-objective frontier 的 anchor
points——这样 paper 至少展示了 "we explored 4 architectural extensions and built a
principled framework for navigating their trade-offs".

---

## 9. Track D — Calibration-speed shootout (INDEPENDENT PARALLEL)

ABIDES+SBI install + 091 leg 是**独立于 A/B/C** 的并行路径, 因为它不在 Pareto frontier
故事线里, 而是 Paper A §7 utility claim 的 standalone evidence.

### 9.1 Sub-tasks

1. **D.1**: `conda create -n abides python=3.10 && pip install abides-markets sbi`
   (Mac, ~1h) — **carry-over from 089-099 plan, NOT done yet**
2. **D.2**: ABIDES+SBI calibration leg on H20, 30 runs × 5 assets = 150 cfg, ~5h wall
3. **D.3**: 写 `figures/fig3_calibration_wallclock.py`, 与现有 ECoMD leg (091) 配对

### 9.2 Decision gate

D.3 must show ECoMD ≥ 50× faster than ABIDES+SBI at equal fact-coverage. 如果 < 50×
→ 重写 §7 from "100× faster" → "matched coverage at fraction of compute" (仍 publishable,
弱化 headline).

---

## 10. Concrete timeline

| Wk | Date | Track A | Track B-β | Track B-α | Track B-γ | Track B-MACEv2 | Track D |
|---|---|---|---|---|---|---|---|
| 17 | 05-21 (今天) | 099b running | doc | doc | doc | doc | doc |
| 17 | 05-22 (明天) | **DECISION** | B-β.1 impl | B-α.1 impl start | — | — | D.1 install |
| 17-18 | 05-23 → 05-29 | (writeup) | B-β.2 smoke + B-β.3 H20 | B-α.1 cont. | — | — | D.2 H20 launch |
| 18-19 | 05-30 → 06-05 | (writeup) | B-β.4 5-asset | B-α.2 smoke + B-α.3 H20 | B-γ.1 multi-D impl | B-MACEv2.1 pre-flight | D.3 figure |
| 19-20 | 06-06 → 06-12 | (writeup) | results integration | B-α.3 results | B-γ.2 smoke | B-MACEv2.2 smoke + GATE | — |
| 20-21 | 06-13 → 06-19 | — | — | B-α.4 attribution + §5 draft | B-γ.3 H20 (if smoke passed) | B-MACEv2.3 H20 (if gate passed) | — |
| 21-22 | 06-20 → 06-26 | — | — | — | B-γ.4 §5.5 | B-MACEv2.4 compare | — |
| 22-24 | 06-27 → 07-10 | **Track convergence**: pick best 2-3 winners → §5/§6 paper sections |
| 24-28 | 07-11 → 08-08 | §7 + §8 + figures + abstract |
| 28-32 | 08-09 → 09-05 | arXiv submission ready (M3) |
| 60 | NeurIPS 2027 deadline | — |

**M3 (Paper A arXiv) shifts from Wk 28 → Wk 32** (4 周延期) 换 problem-diagnosis-
solution arc 完整性. NeurIPS 2027 deadline 仍有 28 周 buffer.

---

## 11. 上一计划 (089-099-humming-jellyfish.md) carry-over 状态

### 11.1 Done ✅

- 5-asset rescore (089b/091/092/093/095 with EURUSD/NDX) — commit `84e5c871`
- 089b per-asset attribution matrix — commit `84e5c871`
- Figure 1 v1 draft (`papers/paper_a_methods/figures/fig1_attribution.{py,pdf,png}`) — commit `84e5c871`
- Pareto ceiling cross-asset confirmation (no EURUSD/NDX cell ≥ 5.5) — commit `84e5c871`
- `scripts/reconcile_r2_to_supabase.py` — commit `3775eaf8`
- 098c zumdn fine-grid (180 cfg) added to overnight queue — commit `adeb5c4d`
- 098b/098c/099b/095b configs generated and pushed
- `papers/proposal/paper_a_neurips_2027_state.md` 2026-05-20 TL;DR updated
- 5 memory updates (project_pareto_ceiling/arch_floors/paper_a/branch_f/seed_count_lottery)
- Doshi 2025 → Maskawa 2025 citation correction — commit `26da65f3`
- `references/notes/maskawa_2025_fluctuation_theorem.md` + publication-sociology analysis

### 11.2 Not done — H20 batches not launched yet ⏳

**User action required** (today/tonight):

```bash
ssh h20 && cd ecophys
git fetch && git checkout feature/paper-a-neurips-2027 && git pull

# Day-shift (~3h): 098b zumdn dose-response n=30 (240 cfg)
DAEMON=1 bash scripts/h20_098b_dayshift.sh

# Overnight (~12-13h): 098c → 095b → 099b sequencing
DAEMON=1 bash scripts/h20_overnight_2026-05-20.sh
```

**Verification (after launch + completion)**:
- `experiments/098b_zumdn_dayshift_n30/scoreboard.md` with 8 cells × n≥27
- `experiments/099b_memk_refinement_n30/scoreboard.md` with n=30 → **Track A decision gate**
- `experiments/095b_baselines_n30/scoreboard.md` with n=30 → C3b strength upgrade
- `experiments/098c_zumdn_fine_grid_n30/scoreboard.md` with n=30

### 11.3 Not done — Mac-side deferred items 🔴

| Item | Status | Priority |
|---|---|---|
| ABIDES install (`conda create -n abides`) | env doesn't exist | **HIGH** — Track D.1 blocker |
| ABIDES smoke (`scripts/abides_calibration_smoke.py`) | not started | HIGH — Track D.1 |
| VaR backtest full run (top-3 cells × 2 seeds × 6 ECoMD) | smoke timed out, ECoMD sampler unconditional limitation documented as Future Work | Low |
| §3 + §4 LaTeX draft (`papers/paper_a_methods/section_*.tex`) | files don't exist | Med — needed by Wk 30 |
| 095 local pilot n=10 (Mac CPU/MPS) | not started | Low — H20 095b supersedes |
| filter-repo cleanup of 6861 re-tracked .pt files | `.git` is 3.5GB | Low — maintenance window |
| Maskawa 2025 PDF download to `references/pdfs/` | not done | Low — citation works without |
| Supabase reconcile row-count verification (3986 → ~6100 expected) | bg job started, not verified | Med — quick check tomorrow |

### 11.4 Tomorrow morning checklist (after H20 batches finish)

1. `git fetch && git pull` (lands H20 commits)
2. Rescore the 4 new experiments:
   ```bash
   for dir in 098b_zumdn_dayshift_n30 098c_zumdn_fine_grid_n30 099b_memk_refinement_n30 095b_baselines_n30; do
     conda run -n ecophys python scripts/score_phase.py experiments/$dir
     conda run -n ecophys python scripts/score_summary.py experiments/$dir
   done
   ```
3. **Track A decision gate**: inspect 099b scoreboard for best memk cell mean + 95% CI lower
4. `conda run -n ecophys python scripts/reconcile_r2_to_supabase.py --bucket ecophys --prefix checkpoints/`
5. Update Figure 1 if 098c or 099b changes per-fact biggest-mover bar
6. Update `paper_a_neurips_2027_state.md` §2 with new SOTA cell
7. Today's log: `logs/2026-05-21.md` Session 1 = framing decision + Track plan; Session 2 = (tonight) overnight launches; tomorrow Session 3 = results

---

## 12. Files to create / modify

### 12.1 Today (Mac, 已完成 or being done)

- ✅ `papers/proposal/paper_a_next_steps_2026-05-21.md` (this doc)
- 📝 `papers/proposal/paper_a_neurips_2027_state.md` — update with problem-diagnosis-solution arc, supersede "falsification tool" framing
- 📝 `logs/2026-05-21.md` Session 1
- 📝 `.claude/memory/project_paper_a_neurips_2027.md` — update headline framing
- 📝 `.claude/memory/project_mace_lite_failure.md` (new) — explicit failure record so future-me doesn't repeat
- 📝 `.claude/memory/MEMORY.md` — index update

### 12.2 Wk 17-18

- 📝 `ecomd/training/scheduled_sampling.py` (B-β.1, ~150 LoC)
- 📝 `tests/test_scheduled_sampling.py`
- 📝 `ecomd/models/hopfield_regime.py` (B-α.1, ~300 LoC)
- 📝 `tests/test_hopfield_regime.py`
- 📝 `experiments/100_scheduled_sampling_smoke/` (B-β.2 Mac smoke)
- 📝 `experiments/101_hopfield_smoke/` (B-α.2 Mac smoke)
- 📝 `scripts/abides_calibration_smoke.py` (D.1 Mac smoke)

### 12.3 Wk 18-19

- 📝 `experiments/102_scheduled_sampling_depth3_n30/` (B-β.3 H20)
- 📝 `experiments/103_scheduled_sampling_5asset_n30/` (B-β.4 H20)
- 📝 `experiments/104_hopfield_5asset_n30/` (B-α.3 H20)
- 📝 `ecomd/training/adversarial_loss.py` (B-γ.1)
- 📝 `ecomd/models/mace_lite_v2.py` (B-MACEv2.1, separate from v1 — v1 stays as failure record)
- 📝 `tests/test_mace_lite_v2.py` with explicit force-magnitude assertion

### 12.4 Wk 20+

- 📝 `experiments/105_adversarial_5asset_n30/` (B-γ.3 H20)
- 📝 `experiments/106_mace_lite_v2_5asset_n30/` (B-MACEv2.3 H20, gated on pre-flight)
- 📝 `papers/paper_a_methods/section_4_pareto_motivation.tex`
- 📝 `papers/paper_a_methods/section_5_extensions.tex`
- 📝 `papers/paper_a_methods/section_6_winning_architecture.tex`
- 📝 `papers/paper_a_methods/section_7_calibration_speed.tex`
- 📝 `papers/paper_a_methods/figures/fig2_winning_attribution.py`
- 📝 `papers/paper_a_methods/figures/fig3_calibration_wallclock.py`

### 12.5 Doc updates needed

- 📝 `papers/paper_a_methods/outline.md` — re-org §4 → motivation, add §5/§6
- 📝 `papers/paper_a_methods/draft_sections.md` — same
- 📝 `papers/paper_a_methods/goals.md` — update primary claim

---

## 13. Acceptance estimate update

| Framing | NeurIPS 2027 estimate | Notes |
|---|---|---|
| Old: "falsification tool" (Pareto ceiling as conclusion) | 18–25% | Pre-2026-05-21 over-claim |
| Current (state doc): "differentiable simulator + falsification + calib-speed" | 22–28% | Post 089–099 5-asset confirm |
| **NEW: problem → diagnose → [Track A + B-β + B-α + maybe B-γ + maybe B-MACEv2] solve → calib-speed utility** | **30–40%** (target) | Conditional on ≥ 2 of (A, B-β, B-α) succeeding at 5-asset mean ≥ 6.0 |
| Fallback to Track C (multi-obj only) | **~22%** | Only if 5/5 Track-B-* fail |

**Target acceptance probability = 30–40%** under successful primary Track B. This is
the Paper A planning target for NeurIPS 2027.

---

## 14. Anti-Maskawa checklist (cross-reference)

Per `references/notes/maskawa_2025_fluctuation_theorem.md`, Paper A must break the
four Maskawa failure modes:

1. **Predictive ≠ descriptive** ✅ — "Hopfield + scheduled-sampling lift frontier
   ≥6.5 on 5 assets" is positive testable prediction with effect-size, not "we
   measured X = Y"
2. **ML community bridge** ✅ — Hopfield (Ramsauer 2020), scheduled-sampling
   (TrajCast NMI 2025), gradient-based calibration vs SBI
3. **Finance community bridge** ⚠ — Paper A is methods-first; finance hook is
   limited to crash EWS + calibration speed. Stronger finance bridge belongs to
   Paper C.
4. **High-status signal** ⚠ — independent researcher, no high-status collaborator;
   compensated by arXiv pre-registration (already planned) + 5-asset n=30
   replication discipline + explicit failure-aware design (MACE-lite v2 case
   demonstrates we don't repeat known errors).

NeurIPS 不要求 (3) 和 (4)（不像 Nature Physics 那样 cross-community signaling
load-bearing），所以 Paper A 主要靠 (1) + (2) 驱动. Paper B 仍然必须四条全击破.

---

## 15. Critical reminders (do not repeat past mistakes)

1. **MACE-lite v1 failure case is canonical** — `improvement_paths.md` C3 +
   `scaling_v1.md` §2 + `logs/2026-04-25.md` 关键发现 #1, #3. Force magnitude 60-190×
   too small + k-NN biased sparsity. Any new learned-potential work (including
   B-MACEv2) MUST address these explicitly with pre-flight gates, not assume they
   are fixable in passing.
2. **n<20 seed counts are forbidden in paper** — `.claude/memory/feedback_seed_count_lottery.md`
   has 4 confirmed hits where n<20 results inflated by ≥30% vs n≥20 truth. Every
   Track B claim must have n≥20 (preferably n=30) per cell before written into paper.
3. **Goodhart on single-moment loss** — `scaling_v1.md` §5 documents that
   `acf_sq_mean` alone can be satisfied by constant-variance regime (not real
   clustering). All Track B losses must use **shape constraints** not just lag-1
   values. Already encoded in B-γ design; also needed for B-β / B-α.
4. **Architectural extensions can't bypass the failure modes documented for prior
   architectures** — keep `mace_lite.py` v1 file as failure record, don't overwrite.
   Hopfield + scheduled-sampling are explicitly chosen as orthogonal to v1 failure
   modes; B-MACEv2 is allowed only with explicit safeguards.
