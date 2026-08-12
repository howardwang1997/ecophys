---
name: Tier 4.2 dynamic graph breakthrough (2026-04-29)
description: First reproducible break of the 11-fact orthogonal-basin ceiling — gate-without-u at 6.10/11 mean across 10 seeds, top 9/11.
type: project
originSessionId: 8e49c8c5-5aca-4713-a84c-51220094fb28
---
After 094 runs across 031–036 plateaued at baseline mean 3.20/11 (no
single tier in the 6-tier arch-extensions sprint of 037–044 broke this),
**Tier 4.2 `dyngraph_no_u`** (learned soft edge gate on the SPS
random-pair pool, gate input = (s_i, s_j, |Δs|), no u) hit:

- **mean 6.10/11** across 10 seeds in 047
- **top 9/11** (single seed) — historic high
- LayerNorm on pair MLP input is load-bearing for inference stability;
  gate without LN NaNs in the 4000-step inference rollout.

**Why:** The breakthrough is a state-conditioned topology — different
agent pairs contribute to V with different weights at different steps.
Fixed-uniform random sampling can't satisfy facts that need different
mixing topologies (autocorr=0 vs zumbach>0 vs hill).

**Counter-finding:** MEGNet-style global state u **HURTS** the gate.
Gate alone 6.10 → gate + u 4.60. u alone 3.00. Best hypothesis: u and
gate both try to inject regime-conditioning into V, and they
destructively compete for representational capacity.

Why: The orthogonal-basin ceiling we'd been hitting was a topology
ceiling, not a hyperparameter or expressivity one. Validated the
hypothesis from PLAN_2026-04-29_tier_4_2_dynamic_graph.md.

How to apply: For any new architecture work, the baseline is now
`abl_no_chunk128 + edge_gating_enabled=True + edge_gating_input_u=False
+ pair_input_layernorm=True`. Don't add u to the gate. If 049 (40-seed
repro) confirms, this becomes the standard configuration for Paper A
results section. See `papers/proposal/PLAN_2026-04-29_post_breakthrough.md`
for the decision tree on tomorrow's results.
