---
name: Paper A target — NeurIPS 2027 main, falsification-tool framing
description: Paper A reframed 2026-05-13 from ICAIF 2026 (calibrated tool for Paper B) to NeurIPS 2027 (differentiable simulator as falsification tool); 12-month plan
type: project
---

**Target**: NeurIPS 2027 main, deadline ~2027-05. Plan-agent reviewer-2 stress test gives ~18-25% acceptance with this framing (vs ~8-12% with the original "mechanism attribution + VaR" framing).

**Two reframes the user accepted on 2026-05-13** (lift acceptance estimate by ~10pp):

1. **Headline downstream → calibration-speed shootout vs ABIDES+SBI** (~80 gradient iters vs ~10⁴ rollouts ≈ 100× speedup). The differentiability claim becomes load-bearing. VaR demoted to secondary chapter.

2. **Whole-paper reframe → "differentiable simulator as a falsification tool"**. The depth-2 ceiling and Zumbach floor (see `project_arch_floors.md`) are reframed as *findings about the sufficiency of standard ABM mechanism classes*, not bugs in our architecture. Mechanism-fact attribution matrix is the evidence; AR(1) + Zumbach patch attempts are systematic falsification experiments.

**Main claim**: ECoMD is a differentiable MD-style market simulator; gradient-based search across 10 mechanisms × 5 assets × 50 seeds × 11 facts shows (1) a depth-2 compositional ceiling, (2) two architectural floors (autocorr, Zumbach) that no patch lifts without breaking other facts, (3) ~100× faster calibration than ABIDES+SBI at matched coverage. We argue this falsifies the implicit claim that the 11 Cont 2001 facts are jointly producible by Markovian latent-state agents under standard microstructure assumptions.

**Three contributions** (in submission order): methodological (first differentiable particle-based market simulator), empirical falsification (depth-2 ceiling + two floors), practical capability (calibration speed + VaR backtest).

**Why:** Branch F (088) ruled out "find a hero cell" — best mean 5.18/11, no SOTA. Original Paper A outline at `papers/paper_a_methods/outline.md` targeted ICAIF 2026 with a "calibrated tool for Paper B physics" framing — that frame doesn't survive the 5.18/11 result. Reframing to falsification-tool turns the negative empirical result into the *point* of the paper.

**How to apply:** Any Paper A discussion now defaults to NeurIPS 2027 timeline + falsification-tool framing. Plan: `~/.claude/plans/curried-cuddling-cloud.md` (M1-M6, 8 weeks each, → 2027-05). When proposing new experiments, ask "does this strengthen the falsification claim or the calibration-speed claim?" If neither, defer.

**Supersedes**: `papers/paper_a_methods/outline.md` ICAIF 2026 framing (kept for history). Plan v3 (`memory/project_overview.md`) Paper A timeline still aligns — both target ICML/NeurIPS in 2027.
