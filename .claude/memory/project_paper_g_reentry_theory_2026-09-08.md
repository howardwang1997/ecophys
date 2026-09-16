---
name: Paper G executable imitation and persistent-access theorem follow-up
description: Stronger value and learning bounds plus an access-gate counterexample; partial capability, paper novelty unqualified.
type: project
---

# Paper G restart — 2026-09-08

September11 successor: `project_paper_g_access_modewise_bound_2026-09-11.md`
derives a restoration-uniform square-root expected-regret upper bound for the
one-way exogenous access model, using SCAL separately in each mode and the full
finite-horizon dynamic comparator. The T^(2/3) result below remains correct;
its formerly open sharper upper-rate question is resolved. This is a standard
parent corollary, with no new implementation or independent novelty qualification.

PI requested “重启，探索新机制或更强理论命题”. A separate bounded theorem
decision authorized deterministic CPU checks. This is a follow-up to the closed
M0 formulation, not a new candidate-harvesting cycle or an outcome-blind trigger.

Formal result: `papers/proposal/ecomd_paper_g_reentry_theory_result_2026-09-08.md`.
Receipt: `research/paper_g/theorem_reentry_v3_receipt.yaml`. Current disposition:
**partial capability / theorem assets obtained, independent-paper novelty unqualified**.
The original M0 route remains failed_closed; its graph now links this follow-up.

- Executable imitation: copy the virtual hedge if feasible, clip only quotes that
  exceed actual inventory. Under common innovations, r_virtual-r_actual <=2*(D-D'),
  where D is inventory L1 distance plus the two depth-bit mismatches. Therefore
  |V_T(s)-V_T(s')|<=2D and span(V_T)<=2(Q+2), uniform in T, customer law and rho.
  This compares states under one law/rho, not values across different rho regimes.
  Known-law admissibility uses conditional virtual-state sampling under actual
  feedback; it does not reveal hidden actual types to an unknown-law learner.
- SCAL's bias-span bound gives a uniform-in-rho learning upper bound on communicating
  M0 classes as an existing-theory corollary. Do not apply it blindly to rho=0's
  entire depth state space or claim a new generic RL algorithm.
- New boundary: observed hedge-venue access is suspended, restored at end of round
  with probability lambda, then remains eligible with full depth every round.
  All customer recovery actions remain legal. For nu=.8 and both willingness
  probabilities 1, eligible-minus-suspended value >=.2*G_T(lambda)-6Q, with
  G_T=(1-(1-lambda)^T)/lambda and G_T(0)=T. This is a persistent access right,
  not a consumed unit of liquidity. CME's official account controls support the
  native distinction; the geometric restoration law is an uncalibrated toy.
- Completed checks: 101,376 exhaustive event cases, 96 M0 exact-DP cells and ten
  gate cells. At T4096, lambda=.001, gaps are 508.903/589.346 ticks for Q2/8;
  original same-model state-span bounds are 8/20. The quantities are oracle
  continuation-value gaps, never learner regret or real-market profit.
- Later analytic corollary (not in the v3 grid): M0 law error gives value error
  <=T*(6*TV(mu,mu_hat)+4*abs(rho-rho_hat)) and deployed optimal-policy loss <=twice
  that bound, via optimal continuation values and Bellman telescoping.
- Later learning theorem (not benchmarked): if lambda is known and exogenous,
  only customer law is unknown, and nu in [delta,1-delta], completing n customer
  probe cycles then planning gives expected regret <=15*(1+1/delta)*n+
  6*sqrt(3)*T/sqrt(n). Thus an O(T^(2/3)) upper bound is uniform in lambda for
  fixed delta, despite divergent global access-value span. This does not give
  matching minimax rates or exclude lambda dependence in a sharper sqrt(T) regime.
- Strong parents: Abernethy–Kale 2013 bounded stateful switching, Xue–Du–Xu AAAI25,
  SCAL ICML18, Asadi ICML18 Lipschitz model error, Agrawal–Jia OR22, and Jiang–Jiang–
  Shen AISTATS26 censored network inventory. The latter's primary abstract is
  verified but proof-level overlap remains unaudited. No independent novelty claim.
- Runtime 21.367 s on one v100ts CPU process; GPU zero, 19 scientific tests pass
  in .59 s, strict mypy passes eight modules. Fifteen source and three result hashes
  verified. Bundle SHA 67c6142f540c498750899989f7633eb09e284a7b476864208d4fceb4f785c8bc.
  All outputs at `experiments/paper_g/theorem_reentry_20260908_v3/`.

Next decisive question: a matching learning boundary under the same legal access
process, or a specified unknown, action-dependent restoration rule. Need a genuine
indistinguishability/lower-bound pair and an upper bound; large access losses,
renamed finite MDPs, or neural benchmarks alone are insufficient. No F3 forecast,
new route card, E/F dependency, field outcomes or confirmation. The separate
receipt transparently records development outcome access instead of backfilling
the canonical outcome-free trigger ledger.

Later same-day continuation resolved the reduced unknown A/B restoration search:
exact finite-horizon minimax regret, attained by random-start alternation, but a
direct first-success-search/SSP parent collision closes that independent novelty
pitch. See `project_paper_g_recovery_search_2026-09-08.md`. The v3 theorems here
are unchanged; the coupled inventory-dependent credit mechanism remains unqualified.
