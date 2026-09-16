# Paper G inventory quote lower bound — 2026-09-11

PRIVATE / INTERNAL. `public_evidence_eligible: false`.

- Paper-only all-policy lower witness in the existing Q2,lambda0 suspended
  subclass: nu=.5, theta_b=theta_s=p±=.4±1/(40sqrtT), q0=1.
  max expected finite-horizon dynamic-oracle regret >=sqrtT/288-1.
- Exact Bellman biases: minus g2/3,x1/3; plus g3p/(1+2p),x(4p-1)/(1+2p).
  N=sum of conditional wide-request exposure. Minus regret controls N;
  plus-world inventory occupancy and boundary opportunity costs prevent avoidance.
  Full actual-feedback transcript KL=E_minus N*kl(pminus,pplus)<=1/96.
- No illegal reset, removed customer probe, hidden-side restriction or fixed-policy
  comparator. All adaptive randomized legal quote policies are covered.
- Combined with prior SCAL upper: matching square-root horizon exponent up to
  logs at Q2 for lambda0 and worst case over lambda. Not every positive lambda,
  Q-scaling, exact logarithms/constants or one fixed separated customer law.
- Decision:not_trigger. Standard Bellman-gap/two-point method; the lower witness
  already exists without restoration and proves no extra slow-access penalty.
  Independent Paper G novelty remains unqualified; no numerical execution.
- Formal: `papers/proposal/ecomd_paper_g_inventory_quote_lower_bound_2026-09-11.md`.
  Contract: `research/paper_g/inventory_quote_lower_bound_20260911.yaml`.
- Standard theory reference: Bandit Algorithms, selected Lemma15.1 proof and
  Eq14.12. PDF indices206/201 visually checked; no whole-book reading claimed.
