# Paper G cycle 30 — numerical teachers and continuum ranking

PRIVATE / INTERNAL. Formal result:
`papers/proposal/ecomd_paper_g_topic_cycle30_2026-09-09.md`.
Structured record: `research/paper_g/cycle30_question_screen_20260909.yaml`.

One new repository-linked neural-PDE measurement question, one F1/F2 screen,
zero cards. Current generic ranking-diagnostic plus correction formulation is
`failed_closed`; actual trained-model prevalence remains unresolved.

The distinction to preserve is generation mesh versus observation/model grid.
Paper D reads and restricts a fixed source dataset; no numerical-source bias
or explanation of its effects follows from this cycle.

Valid periodic upwind has multiplier 1-lambda+lambda*exp(-i*k*h), squared modulus
1-4lambda(1-lambda)sin²(k*h/2), and leading numerical diffusion
c*h*(1-lambda)/2. Exact and teacher predictors reverse squared-loss rankings.
Constant modes, lambda=1 exact shifts and consistent refinement are nulls.
These are stipulated predictors, not neural training outcomes.

For v=u+delta, D_v-D_u=-2<a-b,delta>. A certified epsilon reference bound
gives rank robustness when |D_v|>2||a-b||epsilon. Identical references can share
bias: a=1,b=-1,v1=v2=0,u=+/-epsilon yields opposite D_u. Inconclusive intervals
are not reversals. Fresh unbiased noisy truth gives the usual paired squared-loss
estimator; remaining oracle bias persists when averaging more samples.

Seven primary works retained, six selected full texts plus CROP abstract.
Model-grid invariance work does not directly settle source-label accuracy.
Exact manufactured and stochastic physical supervision have direct parents.
The present algebra and generic remedy do not supply an independent contribution.

Cycles 29 and 30 exhaust two no-card screens in this neural-PDE measurement
parent. Require a qualified recorded trigger before a third relabelled cycle.
A new same-state primary disagreement, actual truth asset removing a blocker,
or theorem defeating the reduction is needed. Paper-only source preflight may
continue on a named blocker; benchmark wish lists are not qualified assets.

No F3, forecast, machine card, outcomes, scientific implementation or compute.
No re-entry audit was created in this cycle. Keep existing route statuses and
Paper D evidence roles unchanged apart from adding the terminal G30 node.

Verified2026-09-09T07:50:07Z: graph293 /edges274 /locators1220; evidence866;
search ledger21 /raw133 /cards0; triggers106 /qualified0. Scoped validation,
18 existing tests and diff whitespace checks passed. Protocol, forecast and
re-entry registry bytes unchanged. Private receipt:
`logs/private/paper_g_cycle30_20260909_verification.md`.
