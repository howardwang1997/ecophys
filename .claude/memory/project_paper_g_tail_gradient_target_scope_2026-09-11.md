# Paper G: tail-gradient target scope

PRIVATE / INTERNAL. September 11 Session 24. Decision: `not_trigger`.

- Fixed-k Hill is 2-Lipschitz in log samples across rank boundaries. No ties
  at the target parameter plus integrable local log-path Lipschitz bounds permit
  dominated pathwise differentiation of its finite-batch expectation, including
  dependent samples. Rank nonsmoothness alone does not imply a biased gradient.
- Exact iid Pareto common-uniform coupling gives H=gamma S/k, S~Gamma(k,1).
  Its gradient has mean gamma' and variance gamma'^2/k. Reciprocal exponent
  gradients have the familiar inverse-Gamma moment restrictions and k/(k-1)
  bias factor. These classical facts do not calibrate general dependent tails.
- Survival (1-w)x^-2+w x^-1, 0<w<1, has constant true gamma=1 but strictly
  positive finite-Hill gradient for every no-tie batch. Inverse-CDF ranks never
  cross; dominated differentiation is valid. The mismatch is the derivative
  of finite-threshold bias, not an automatic-differentiation error.
- For w<1/2, crossover x_c=(1-w)/w has exceedance probability
  p_c=2w^2/(1-w); P(Hill threshold>x_c)<=n p_c/(k+1).
  This is threshold coverage, not an all-method identification lower bound.
- Drees preprint68 (submitted2002-08-14), selected Section2 T0–T3/Theorem2.2
  text: dependent statistical tail-functional asymptotics do not automatically
  give uniform simulator-parameter gradient calibration. No full-proof review.
  ParetoGAN official abstract revisited only as an existing generation parent.
- Four standard analytic controls, no independently original theorem/method.
  Existing tail route remains closed; no candidate harvest or experiment authority.
  Stop scalar mixture/soft-sort variants absent a nonstandard uniform result.

Formal: `papers/proposal/ecomd_paper_g_tail_gradient_target_scope_2026-09-11.md`.
Contract: `research/paper_g/tail_gradient_target_scope_20260911.yaml`.
Manifest: `research/paper_g/tail_gradient_source_manifest_20260911.json`.

Verified by2026-09-11T01:37:36Z: graph293/274/1573, evidence1040,
triggers167/qualified0, cycles21/raw133/cards0. Scoped verifier,18 existing
tests and whitespace passed with terminal exit0. Protocol/search/forecast and
predecessor hashes unchanged. Checks validate records, not novelty or proof.
Access-only details are confined to the private manifest and verification receipt.

Successor: [tail-tangent limit scope](project_paper_g_tail_tangent_limit_scope_2026-09-11.md)
settles the stronger asymptotic question: even parameter-uniform Hill consistency
does not imply gradient consistency. A separate tangent remainder condition is
sufficient in the iid quantile setting. No dependent-rate method or topic follows.
