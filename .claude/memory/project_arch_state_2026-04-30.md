---
name: EcoMD architectural state 2026-04-30
description: Current best architecture (4.2 + 2.1) and its real performance after 35-seed CI — supersedes the stale "9/11 breakthrough" claim
type: project
---

**Current best EcoMD architecture (as of 2026-04-30):**

`p_4_2__2_1` = full Tier 4.2 dyngraph + Tier 2.1 jumps:
- `edge_gating_enabled=True, edge_gating_input_u=True, gate_init_p=0.7`
- `global_state_enabled=True, global_state_d=16, global_state_into_pair=True`
- `pair_input_layernorm=True` (REQUIRED for inference stability)
- `jump_lambda=0.5, jump_scale=0.01`
- baseline: chunk_steps=24, hidden=96, N=10K, init_state_scale=0.1

**Real performance** (35-seed CI, 048 seeds 0-4 + 052 seeds 5-34):
- mean **5.40/11**, 95% CI [4.86, 5.97], median 5
- max **10/11** at seed 21 (current project record, ~3% lottery)
- ≥7/11 hit rate: 23%
- ≥9/11 hit rate: 6%
- distribution is wide (std 1.75); architecture produces high-variance outcomes

**Compared to predecessor architectures:**
- baseline (Sprint 2 path, no Tier 4.x): mean 3.20/11 — `p_4_2__2_1` is ~2x improvement
- `t42_dyngraph_no_u` (gate alone, 30 seeds): mean **5.40/11** — same mean, lower ceiling (8 vs 10)
- adding u + jumps to gate widens the upper tail but does NOT improve the mean

**Why:** gate alone vs gate+u+jumps trade-off. The composition increases lottery ceiling without lifting the average. Likely a deeper basin issue (orthogonal-basin ceiling at ~5/11 mean).

**Why this matters for papers:**
- Cannot claim "improvement over no_u variant" in mean — must use peak/ceiling argument
- Needs auxiliary regularization (stop-grad rollout, multi-position loss, longer chunk via bf16) to lift mean
- 5-seed numbers are unreliable lottery — never report n<20 in papers

**How to apply:**
- When user asks "what's our best", quote 5.40/11 (35-seed) with the 10/11 ceiling
- Don't repeat the 7.20 number from 048 alone — that was 5-seed lottery
- For paper claims, default to mean+CI; cite ceiling as "best observed" only
- For new arch experiments, target mean improvement, not ceiling
