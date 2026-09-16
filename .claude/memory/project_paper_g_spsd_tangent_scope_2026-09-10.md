# Paper G SPSD/tangent scope — 2026-09-10

PRIVATE / INTERNAL. `public_evidence_eligible: false`.

- Decision: not_trigger. No recorded blocker removed; overall goal unachieved.
  The user resumed work; do not infer completion or execution authority from
  historical goal-service status. No new cycle, candidate, forecast or card.
- Formal: `papers/proposal/ecomd_paper_g_spsd_tangent_scope_2026-09-10.md`.
  Contract: `research/paper_g/spsd_tangent_scope_20260910.yaml`.
  Manifest: `research/paper_g/spsd_tangent_source_manifest_20260910.json`.
- Parish2307.05434v3 dated Oct23,2023: boundary force is a common-basis
  state-dependent L L^T coefficient times displacement, plus preload.
  Static/path-independent scope is explicit. Constant versus nonlinear
  coefficient cases must be separated; full derivative includes DK[u] terms.
- Source Section6.1 uses nonlinear CG with tangent preconditioning and
  differing matrix constructions, not simply Newton with linear CG.
  Source Section7 already names solver interaction versus ill-posedness.
  No matched opposing primary prediction established.
- Publisher confirms Computational Mechanics74:1357–1381, May6,2024,
  DOI10.1007/s00466-024-02481-5. Preview/notes/metadata only; VOR Section5
  not read. Do not automatically extend the v3 wording audit to the VOR.
- Standard exact control: l(u)=ReLU(2-u); frozen coefficient1+l²>=1.
  G(u)=(1+l²)u=15/8 has roots(5-sqrt5)/4,3/2,(5+sqrt5)/4.
  G'(3/2)=-1/4. Embed diagonal interface factors l/sqrt2 in the source's
  normalized four-degree outer matrix with load5/8 on each degree:
  eliminating endpoints gives two independent G=15/8 equations, hence nine
  equilibria. Constructed factor map only; no fit, physical truth or actual
  trained-model failure. Constant exact condensation retains uniqueness.
- Second standard control: K=diag(1,(1+x)²),F=K(x,y) on x>-1 is SPD but
  curlF=2(1+x)y; loop work on unit square is3/2 and reverses orientation.
  No potential; not physical friction/hysteresis. Constant-factor null has
  symmetric derivative/zero loop work. No new theorem claimed.
- Next bounded source-only lead: Xu/Huang/Darve2004.00265v1, Apr1,2020,
  exact constitutive update/hypotheses. Abstract/history only so far.
  Stop if it only repeats coefficient/tangent calculus; no generic harvest.
- Two source/version records, five graph locators, two controls, one audit.
  Graph293/274/1418; evidence982; triggers136/qualified0;
  search21cycles/133raw/0cards unchanged. No Paper D outcomes used.
- Web text only; an embedded Appendix A code excerpt was visible, but no
  external source file was accessed or executed. No local cache/PDF, raw
  outcomes, model, scientific implementation, simulation, GPU, outreach or
  publication. Optional HTML fetch failure has no scientific meaning.
- Verification receipt:
  `logs/private/paper_g_spsd_tangent_20260910_verification.md`.
