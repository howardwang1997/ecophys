# Paper G shock-response truth preflight

PRIVATE / INTERNAL. Formal:
`papers/proposal/ecomd_paper_g_shock_response_truth_preflight_2026-09-09.md`.
Contract: `research/paper_g/shock_response_truth_preflight_20260909.yaml`.

Decision partial_capability; no contribution blocker removed or candidate
harvest. Exact nonlinear dynamical truth improves the validation toolbox but
does not qualify an innovative topic. Herty et al.2007.05330v1 has moving-shock
generalized sensitivities; Herty--Zhou2412.04251v1 restricts its multiple-shock
construction to no interactions; Bressan1995 Theorem5.1 already includes binary
interactions under its structural and small-total-variation assumptions. Do not
turn one method restriction into a literature-wide gap.

Two classical paper-only controls retained. The exact Burgers ramp
u=a*x/(1+a*t) on [0,sqrt(1+a*t)] has regular derivative x/(1+a*t)^2 plus a
Dirac mass of weight a*t/(2*(1+a*t)). Their mass pairing sums to1/2.
Initial regular L1/L2 variation becomes a measure response at positive time.
Nodal sampling can omit the singular term; true cell-average derivatives
contain weight/h and their weighted L2 norm grows as weight/sqrt(h). Fixed
smooth physical observables supply a distinct well-defined weak target.

The compact 0/2/1/0 family with fronts -1+p and1-p and a shared left edge -10
has mass20. Fronts merge at t=2-2*p into X=t, independent of p. At t=2,p<0,
state L1 and squared L2 differences both equal2*abs(p), yet every fixed smooth
observable has zero first derivative. A local first-moment response equals
p^2 on p<0 and zero on p>=0. At the collision instant, weak derivative zero
is not a strong L1 derivative or an o(abs(p)) state approximation. For fixed
2<t<=4 all sufficiently close members have identical full states. This is
classical entropy/RH algebra, not a new theorem, learned-model observation or
counterexample to the old fixed-additive-current-state-pulse formulation.

Truth boundaries: inviscid versus viscous dynamics; point versus cell versus
weak observations; amplitude variation versus mass-preserving front shift;
collision time and one-sided limits; no independent execution/confirmation or
release contract. Both controls are development assets. Future re-entry still
needs a distinct contribution and qualified same-estimand validation. No new
cycle, forecast, card, outcomes, implementation, GPU or publication authority.

Verified 2026-09-09T09:33:56Z: graph293 /edges274 /locators1266; evidence898;
re-entry112 /qualified0; cycles21 /raw133 /cards0 unchanged. Scoped canonical
validation, source/contract/trigger parity,18 existing tests and git diff --check
passed. Receipt: `logs/private/paper_g_shock_response_20260909_verification.md`.
