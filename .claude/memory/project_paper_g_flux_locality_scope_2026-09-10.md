# Paper G flux/locality scope audit — 2026-09-10

Successor: September 11 local-sampling resolution proves the source Eq11
initialization is identifiable from a5x5 exact subgrid within its declared
input. It separately proves linearized current-state observability and a
conditional fixed-time local nonlinear inverse. Numerical conditioning,
global/mixed-time nonlinear identification and model performance remain open.
See `project_paper_g_local_sampling_resolution_2026-09-11.md`; historical
source/proof scope below is retained unchanged.

PRIVATE / INTERNAL. `public_evidence_eligible: false`.

- Decision: not_trigger. Paper G remains active and unachieved. Closed
  numerical-teacher route stays closed; neither recorded blocker removed.
- Formal: `papers/proposal/ecomd_paper_g_flux_locality_scope_2026-09-10.md`.
  Contract: `research/paper_g/flux_locality_scope_20260910.yaml`.
  Manifest: `research/paper_g/flux_locality_source_manifest_20260910.json`.
- McGreivy/Hakim2303.16110v2 already discusses global correction versus local
  restrictions and propagation. Preserve hyperbolic, timestep, boundary-flux
  and noninvariant-term qualifications; generic trade-off is not new.
- Ye/Li/Yan2504.09807v1 defines zero exterior input derivative but targets
  compressible viscous flow with thermal conduction. Exact arbitrary-field
  response and approximate prediction on restricted initial states differ.
  Boundary extension/domain reuse already has a direct parent.
- Standard paper-only control: any zero-sum periodic update admits a cumulative
  flux representation. A local divergence stencil does not restrict flux
  input dependence; audit D J_F, including global normalization/pressure.
- Standard heat-kernel control: exterior amplitude A gives uncertainty radius
  A erfc(R/sqrt(4 nu t)) for the unrestricted exterior class. Local generators
  have nonlocal finite-time response; a tiny tail is not practical failure.
- Source-native linearized transverse shear around uniform rest has
  nu=2/(rho0 Re) with Eq7 exactly as written. Opposite zero-mean remote bumps
  match local state, mass, momentum and total energy but differ in first-order
  future shear. This is a small-perturbation continuum control, outside the
  cited finite-mode initialization family, not a reproduced model result.
- Finite trigonometric polynomials are determined on an open interval.
  Restricted local observations can encode global state; finite-grid rank and
  conditioning are not established, and later states need separate analysis.
- No new theorem, same-condition primary disagreement, practical effect size,
  independent truth or confirmation qualified. Stop generic flux rewrites,
  local/global correction variants and heat-tail certificates as topics.
- Next source-only lead: NEST2605.12343v1, official abstract only. Local learned
  solid-mechanics patches are globally coupled through Schwarz iteration.
  Inspect actual interface variables, coupling/convergence and reference
  truth before any new question. Predates closure, not a publication trigger;
  classical domain decomposition alone removes no blocker.
- Two new selected article HTML readings, one reused Huang scope and one
  abstract-only lead. No source code, raw outcomes, model payload, scientific
  implementation, simulation, GPU, outreach or public release.
- Graph293/274/1402, evidence975, triggers133/qualified0;
  search21cycles/133raw/0cards unchanged. Verification receipt:
  `logs/private/paper_g_flux_locality_20260910_verification.md`.
