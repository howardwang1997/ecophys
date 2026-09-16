# Paper G: tail value consistency versus tangent consistency

PRIVATE / INTERNAL. September11 Session25. Decision:not_trigger.

- Smooth valid tail quantile log Q_theta(t)=2l+sin(theta(1+l)^2)/(1+l)
  -sin(theta), l=log t, |theta|<=1/4. Its l derivative is at least1/2.
  Uniformly Q_theta(t)/(exp(-sin(theta))*t^2)->1: true gamma=2 is constant.
- With iid common uniforms, T=L_(k+1), A=mean top-k exponential excesses,
  sup_theta|H(theta)-2A|<=2/(1+T). For intermediate k, Hill is uniformly
  consistent in probability and L1, including uniform expectation convergence.
- At theta0, parameter tangent logQ equals l, so H'(0)=A, E H'=1,
  Var H'=1/k and H'->1 in L2 although gamma'=0. Finite-n domination holds;
  ranks never change. This is derivative/limit noncommutation, not a wrong
  finite-batch gradient or failure of value consistency.
- Sufficient iid control: tangent=b(theta)+gamma'(theta)l+r_theta(l), bounded
  gamma', epsilon(M)=sup_theta,l>=M |r|->0. Then uniform sample-gradient
  error <=C|A-1|+2epsilon(T), hence convergence in probability. Expectation
  convergence requires additional uniform integrability; no dependent rate.
- Drees existing selected T0–T3/Theorem2.2 text revisited, no new source or
  theorem contradiction. Statistical functional derivative is a different limit.
- Three standard analytic controls. The quantile family is designed for a
  theorem assumption check; no independently motivated native model or new
  estimator established. Stop scalar tail constructions; no route blocker removed.

Formal: `papers/proposal/ecomd_paper_g_tail_tangent_limit_scope_2026-09-11.md`.
Contract: `research/paper_g/tail_tangent_limit_scope_20260911.yaml`.
Manifest: `research/paper_g/tail_tangent_source_manifest_20260911.json`.

Verified by2026-09-11T04:41:26Z: graph293/274/1576,evidence1040,
triggers168/qualified0,cycles21/raw133/cards0. Scoped verifier,18existing tests
and whitespace passed, terminal exit0. Predecessor/core registry hashes intact.
These validate records, not proof novelty or an independent scientific review.
