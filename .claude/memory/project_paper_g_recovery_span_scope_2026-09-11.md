# Paper G recovery versus bias scope — 2026-09-11

PRIVATE / INTERNAL. `public_evidence_eligible: false`.

Later September11 [ActiveQP source audit](project_paper_g_activeqp_state_scope_2026-09-11.md)
identifies separate class and aggregate restoration in current Phlx rules.
Class-counter clearing does not certify the normal-state assumption used below;
uniform native recovery and the missing bias advantage remain unqualified.

- Conditional recovery lemma: quiescence B, unit inventory move success floor
  p0, monotone post-fill cleanup and Q capacity give H=B+Q(B+1/p0).
  These are unverified native assumptions, not a validated Deribit bound.
- Finite communicating MDP, r in[0,R]: if every state can reach every normal
  z in C within expected H, then min h >=max_C h-RH. To bound full span still
  need K=max_s h-max_C h; span(h)<=RH+K. Defining K does not bound it.
- Exact two-state witness: reset to L costs one step, L tries H with epsilon,
  H stays for reward1. Bias span1/epsilon, but try-at-L/stay-at-H is optimal
  for every epsilon and horizon. Unknown epsilon incurs zero regret.
- Consequently neither fast reset nor large bias alone decides learning
  difficulty. Need a native K certificate or different-optimal-action unknown
  laws, preserving the same comparator, reset permissions and feedback.
- Two standard paper-only diagnostics; no external source or scientific
  execution. Existing MMP route remains failed_closed; audit:not_trigger.
- Formal: `papers/proposal/ecomd_paper_g_recovery_span_scope_2026-09-11.md`.
  Contract: `research/paper_g/recovery_span_scope_20260911.yaml`.
