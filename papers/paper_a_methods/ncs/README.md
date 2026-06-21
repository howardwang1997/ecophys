# Paper A → Nature Computational Science — long-form draft

`main.md` — the recombined, long-form Paper A targeting **NCS** (markdown working draft). It subsumes
the two workshop papers (`../workshops/{genai_finance,ml4ps}/`) and adds the order-flow program:

- §3 measurement correction (= the GenAI-Finance "evaluation pitfall", reframed as computational hygiene)
- §4–§5 controlled discovery + mechanism (= the ML4PS "driven transient" + the OFI signature)
- §6 the real-market boundary (returns stationary, exp 123 Stage 3)
- **§7 the order-flow test** — §7.1 the sim prediction (Phase 1, complete); **§7.2 the real-data test
  is BLANK**, pending the Tardis L2 buy. Setup/gates frozen in
  `../../../experiments/124_order_flow_transient/PREREG_phase2.md`.

## Status
- Complete except **§7.2** (the load-bearing real-market result) — which decides the central claim and
  the venue. Written conditionally against the pre-registered gates (G-main positive → NCS market
  discovery; G-null → retreat to the simulator-physics + measurement-correction paper, still self-contained).
- **NCS is a stretch (~10–18% joint)**; gated on the Tardis buy (justify via Paper B) + a positive §7.2.
  If §7.2 is null or the buy doesn't happen, the workshops + a NeurIPS/TMLR version (this draft minus
  §7.2) are the fallback. See `papers/proposal/paper_a_{dual_track_plan,ncs_viability_routes}_2026-06-19.md`.

## TODO
- [ ] Fill §7.2 (Table 2 + Figure 4 + outcome) after Tardis L2 reconstruction + the pre-registered test.
- [ ] Convert to the NCS LaTeX template once §7.2 lands; tighten to length; de-anonymize.
- [ ] Reconcile authorship/figures with the workshop versions (shared `references.bib`).
