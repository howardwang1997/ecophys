# Paper G shared-parameter capacity bound — 2026-09-11

PRIVATE / INTERNAL. `public_evidence_eligible: false`.

Latest September11 [constructive resolution](project_paper_g_grid_planner_resolution_2026-09-11.md)
replaces the exact optimistic oracle by a nu grid and discounted LPs. With
M=ceil(sqrtT), polynomial computation preserves the asymptotic bound; the log
and finite constants differ as explicitly recorded. Practical speed and novelty
remain unqualified. Stop this refinement as an independent Paper G proposal.

Later September11 [parent collision](project_paper_g_structured_parent_collision_2026-09-11.md)
proves exact four-type Exo-MDP and known-reward linear-mixture representations.
Selected Wan v4 and Chae fulltext rule out broad latent/shared-parameter novelty;
exact continuing capacity-additive collision and efficient local planner remain
unresolved. Earlier abstract-only reading below describes the predecessor session.

- Same fixed-mark, prefunded, unit-action inventory model, Q>=2, q_initial=1,
  iid unknown (nu,p_b,p_s), one independent external restoration. Every request
  side is observed after acting; wide-quote fill/nonfill supplies willingness.
- Derived expected regret O(sqrt(T log T)+Q log T), against the original
  known-law finite-horizon optimal dynamic controller, uniformly in lambda and
  without a known positive lower bound on either customer side probability.
  This sharpens the previous generic SCAL specialization's Q dependence.
- Key certificate: every candidate model has a bias with adjacent differences
  at most2. A shared three-parameter optimistic planner therefore pays local
  model error without the global capacity factor. Share observed streams across
  inventory/modes; freeze confidence intervals at count-doubling epochs.
- Exact bound: min{3T,4Q+2Q K_T+(24+16sqrt2)sqrt(LT)+13T eta}, where
  eta=(T+1)^(-2), L=log(6T/eta), K_T=5+3floor(log2T). Martingale expectations
  remain unconditional; no confidence-event conditioning or hidden observations.
- The planner is an existence oracle over a compact constrained set. Efficient
  implementation, optimal Q dependence and independent novelty are unproved.
  Q2/lambda0 lower witness retains its limited scope. No endogenous-protection
  extension or Q-uniform lower bound follows.
- One primary AISTATS2025 structured-RL abstract/metadata read; no full theorem
  mapping or claim of improvement over that paper is verified. Exact prior
  collision and efficient planning are the next decisive checks.
- Decision:not_trigger; one reusable standard paper-only diagnostic. No new
  candidate cycle, forecast, scientific implementation or outcome access. The
  structural refinement is within the retained original model, not permission
  for more untriggered protection variants. Publication-level goal remains unmet.
- Formal: `papers/proposal/ecomd_paper_g_capacity_additive_bound_2026-09-11.md`.
  Contract: `research/paper_g/capacity_additive_bound_20260911.yaml`.
