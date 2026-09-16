# Paper G modewise access-learning bound — 2026-09-11

PRIVATE / INTERNAL. `public_evidence_eligible: false`.

Later September11 quantitative successor:
[shared-parameter bound](project_paper_g_capacity_additive_bound_2026-09-11.md)
derives O(sqrt(T log T)+Q log T) under the same model with an exact optimistic
planning oracle. This improves the capacity dependence of the SCAL specialization
below. Efficient planning and independent novelty remain unqualified.

Scope follow-up, September 11: [MMP recovery audit](project_paper_g_mmp_recovery_scope_2026-09-11.md)
identifies a documented endogenous protection lifecycle. The exogenous theorem
does not automatically cover its policy-dependent mode occupation. No harder
learning rate or qualified new route follows from this boundary.

Later September11 successor: `project_paper_g_inventory_quote_lower_bound_2026-09-11.md`
proves an all-policy Omega(sqrtT) lower witness at Q2,lambda0, matching this
upper bound's horizon exponent up to logarithms for that subclass and worst case
over lambda at Q2. Exact logarithms, capacity dependence and per-positive-lambda
lower bounds remain unproved; the upper-bound-only statements below are historical.

- Proved derived upper bound for the original exogenous one-way access model:
  expected finite-horizon regret is Otilde(Q sqrt((Q+1)T))+4Q, uniformly in
  lambda in[0,1]. Previous T^(2/3) bound remains valid but is superseded in rate.
- Freeze S/E as separate communicating inventory MDPs; each has bias span2Q,
  S=Q+1,A<=27,Gamma<=3. Full dynamic oracle <= expected sum of mode gains+4Q
  by Bellman telescoping over at most two segments.
- Run fresh SCAL per mode, initialize E at current actual inventory. Statistics
  restart is not a market reset. F_actual contains all required feedback.
  SCAL Thm12 anytime bound handles random segment lengths; failure tail converts
  to expected regret. No implementation or numerical verification performed.
- Learner need not know lambda, but switch must remain external and independent
  of customer innovations/actions. Unknown action-dependent channel theorem is
  distinct; repeated access loss, binding cash and price risk are not covered.
- Decision:not_trigger. Standard SCAL/bias/telescoping corollary, not independent
  algorithm novelty or matching minimax theorem. Stop generic exogenous-wait
  penalty claims. Full Paper G objective remains unachieved.
- Formal: `papers/proposal/ecomd_paper_g_access_modewise_bound_2026-09-11.md`.
  Contract: `research/paper_g/access_modewise_bound_20260911.yaml`.
- SCAL primary PDF page7 (index6) visually checked; no code, model or outcomes.
