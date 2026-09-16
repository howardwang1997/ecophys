# Paper G grid-planner resolution — 2026-09-11

PRIVATE / INTERNAL. `public_evidence_eligible: false`.

- Resolved polynomial approximate planning in the unchanged exogenous access
  model. Average gain is nondecreasing in both wide-quote willingness parameters
  and 6-Lipschitz in side probability nu. Take willingness confidence upper
  endpoints and grid nu; this does not assert nu endpoint optimality.
- Rational outward-rounded intervals on mesh1/M; integer
  L_star=ceil(log2(6T(T+1)^2)); gamma=1-1/[M(Q+1)]. At most(M+1)K_T ordinary
  discounted LPs, Q+1 variables and<=27(Q+1) inequalities each. Select by
  (1-gamma)V_gamma(0); discounted local bias bound stays2.
- Retained expected dynamic-oracle regret bound plus30T/M, replacing the
  predecessor natural log by L_star. M=ceil(sqrtT) preserves
  O(sqrt(T log T)+Q log T) with O(sqrtT logT) LP solves. Polynomial in explicit
  Q,T/input bits, not strongly polynomial, constant per step or proven fast.
- All approximation costs explicit: side grid6/M, two bias errors<=4/M,
  outward-rounded widths20/M. No hidden feedback, market reset, side-frequency
  floor or comparator change. No scientific implementation or numerical check.
- One selected author-source LP reference, one PDF/two visual pages; no full
  proof or neighborhood audit. Classical general rational LP complexity used;
  fixed-discount strong-polynomial theorem explicitly not invoked.
- Decision:not_trigger. This is a constructive standard-parent corollary.
  Stop this refinement as an independent Paper G proposal; preserve its theory
  assets. No new source absence claim or theorem that all variants lack novelty.
  Require a qualified primary disagreement/truth asset/nonstandard result before
  renewed work here. Solver changes and grid tuning are insufficient triggers.
- Formal: `papers/proposal/ecomd_paper_g_grid_planner_resolution_2026-09-11.md`.
  Contract: `research/paper_g/grid_planner_resolution_20260911.yaml`.
