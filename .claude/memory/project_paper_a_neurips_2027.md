---
name: Paper A target — NeurIPS 2027, problem-diagnose-solve framing
description: Paper A NeurIPS 2027 framing pivoted 2026-05-21 from "falsification tool" (headline negative) to "problem→diagnose→solve" (headline positive). Track A memk + Track B-β scheduled-sampling + Track B-α Hopfield are primary parallel; B-γ adversarial + B-MACEv2 secondary; C multi-obj fallback.
type: project
---

**Target**: NeurIPS 2027 main, deadline ~2027-05. Plan-agent reviewer-2 stress test estimates: 18-25% under old "falsification tool" framing; **30-40% target** under new "problem→diagnose→solve" framing (2026-05-21 pivot, conditional on ≥2 of Track A/B-β/B-α succeeding at 5-asset mean ≥6.0). M3 (arXiv) shifts Wk 28 → Wk 32.

## 2026-05-21 framing pivot — headline POSITIVE

User instruction: "我不希望 Paper A 的主要 claim 是一个负向的 claim。我希望在提出了一个负面问题之后，我们还应该设计方法去解决这个问题。"

**Old headline (deprecated)**: "Differentiable simulator as falsification tool" — too negative; reviewer-2 reads as "we did ablation and found a limit, so what?"

**New headline**: "We discover an empirical Pareto frontier in hand-crafted Markov mechanism families (§4 motivation), then introduce architectural extensions that break it (§5-6), and demonstrate gradient-based calibration at ~100× ABIDES+SBI wall-clock (§7 utility)."

Five constructive solution tracks (paper §5-6 candidates):
- **Track A** — Memory kernels (memk n=30 via 099b, decision tomorrow 2026-05-22)
- **Track B-β** — Scheduled-sampling depth-3 (1-1.5 wk, lowest risk; borrows TrajCast NMI 2025 trick)
- **Track B-α** — Hopfield regime attractors (Ramsauer 2020) replacing GRU regime (2-3 wk, highest claim value)
- **Track B-γ** — Adversarial per-fact discriminator (3-4 wk, GAN stability risk)
- **Track B-MACEv2** — MACE-lite v2 with explicit failure-aware fixes (canonical failure case; pre-flight gated; see [[project_mace_lite_failure]])
- **Track C** — Multi-objective Pareto (fallback only, 5/5 B-track failures required to demote)
- **Track D** — ABIDES+SBI calibration shootout (independent parallel, §7 utility)

User confirmed (2026-05-21): B-β + B-α 并行 primary; B-γ adversarial 可以做; B-MACEv2 可以做但要记住 prior failure; C 是退路, 不轻易接受.

## Current SOTA cell (2026-05-20, supersedes pair_AB 5.18)

`xa_gold_zumdn = 5.96 ± 1.54 (n=26, 5/26 ≥8/11)` from 092_5asset_replication_30seed.
Cross-replicated: 089 SPX 5.12 (n=48), 090 SPX 5.31 (n=29), 089b EURUSD 5.36 (n=28).

## Main claim (post-pivot)

ECoMD is a differentiable MD-style market simulator with mechanism-decomposable dynamics. (1) Systematic ablation reveals an empirical Pareto frontier in hand-crafted Markov mechanism families, with no cell exceeding 5.5/11 stylized facts on 5 assets at n=30. (2) Four architectural extensions — non-Markov memory kernels, scheduled-sampling depth-3 training, Hopfield regime-attractor dynamics, and (with failure-aware safeguards) learned MACE-lite v2 potentials — are individually evaluated; the winning combination lifts the frontier to ≥6.5 on ≥3 assets. (3) Gradient-based posterior inference calibrates ECoMD ~100× faster than ABIDES+SBI at matched coverage.

## Why the pivot

Negative-headline papers face ~15% NeurIPS acceptance ceiling regardless of evidence strength (reviewer-2 default: "you found a limit, you didn't solve it"). The 089-099 data alone supports a problem-diagnosis arc but not a solution arc — so Wk 17-22 dev is allocated to building the solution arc before submission.

## Critical reminders

- **MACE-lite v1 is the canonical failure case** (2026-04-22, 0-4/11 across 8 ablations). Any new learned-potential work must respect this. See [[project_mace_lite_failure]].
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
