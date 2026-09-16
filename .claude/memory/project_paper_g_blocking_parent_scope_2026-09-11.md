# Paper G blocking-bandit parent scope — 2026-09-11

PRIVATE / INTERNAL. `public_evidence_eligible: false`.

Later September11 [recovery/bias audit](project_paper_g_recovery_span_scope_2026-09-11.md)
derives a conditional return-time bound but isolates the missing outside-normal
bias advantage K. Fast reset alone does not bound span; an explicit large-span
parent has zero learning regret. Native recovery and contribution remain unqualified.

- NeurIPS2019 Blocking Bandits already treats policy-dependent availability;
  ICML2021 CBBSD already permits correlated reward and stochastic blocking.
- Exact stripped specialization: F~Bernoulli(p), X=bF, D=1+LF; only the selected
  arm is blocked. This is an existing-parent instance, not a reduction of the
  complete market inventory/group/reset contract.
- ICML2021 Theorem7 bounds rho-regret, rho=alpha*beta/(1+alpha*beta).
  R1=(1-rho)V*+Rrho prevents silently claiming an exact dynamic-oracle rate.
  NeurIPS2019 greedy-comparator loss likewise omits scheduling suboptimality.
- Direct quote-as-arm mapping does not cover unselected group members being
  frozen. Larger encodings remain unproved. Per-selected-arm reward shifts also
  need not preserve the original objective when selection counts differ.
- Finite-state representation alone does not kill all possible structural
  learning novelty. Need a concrete quantitative improvement over the parent,
  common legal comparator and accessible native truth; none qualified here.
- Decision:not_trigger on existing MMP route; stop bare-cooldown bibliography.
  No candidate, new cycle, scientific implementation, account or outcome access.
- Two primary PDFs, four visually checked pages; full supplementary proofs
  unread. Formal: `papers/proposal/ecomd_paper_g_blocking_parent_scope_2026-09-11.md`.
  Contract: `research/paper_g/blocking_parent_scope_20260911.yaml`.
