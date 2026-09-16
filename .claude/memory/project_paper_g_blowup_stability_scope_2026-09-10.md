# Paper G: blow-up stability and explicit event truth

PRIVATE / INTERNAL. Session9 started2026-09-10 02:35 NZST. Previous turn progress.
Formal `papers/proposal/ecomd_paper_g_blowup_stability_scope_2026-09-10.md`;
contract `research/paper_g/blowup_stability_scope_20260910.yaml`;
manifest `research/paper_g/blowup_stability_source_manifest_20260910.json`.

- Partial capability, no recorded contribution blocker removed, no harvest.
  Stop generic neural singularity-certificate expansion; original goal active.
- HNW final ARMA250:28(2026), DOI10.1007/s00205-026-02191-7, gives a concrete
  stability theorem for decaying a_t=Delta a+a^2 on R^n. Initial data
  lambda^-1*(ubar+g), ubar=(1+|z|^2/8)^-1, even g, ||g||Ek<=C0*lambda,
  lambda<lambda0. k=2n+10 (12 in1D), with singular L2 plus high derivatives.
  Constants expressed through energy constants, not numerically certified here.
- One-dimensional normalization gives Cu_t=-1+lambda/4. Under the actual full
  bootstrap, lambda is positive and nonincreasing and Cu vanishes at T, hence
  Cu0<=T-t0<=Cu0/(1-lambda0_current/4). Standard consequence, not new theorem.
- Independent elementary truth family: u0=1/(a+b*x^2) on R, a>0,0<b<1/2.
  Constant supersolution1/(a-t) and rational subsolution
  1/[a-(1-2b)t+b*x^2] prove a<=T_infinity<=a/(1-2b), using bounded-class
  local existence, comparison and continuation. Subsolution residual is
  -8*b^2*x^2/[a-(1-2b)t+b*x^2]^3. No computation or unknown constant needed.
  Event is maximal bounded/Linfinity lifetime, not an asserted L2 equivalent.
- Under parabolic scaling, a changes but b stays fixed. Fix a=1 and vary b
  to avoid scale clones; invariant -u0''(0)/u0(0)^2=2b. Full initial field
  remains required. All members one PDE/theorem lineage, not replication.
  ODE predictor T=a already has error<=2*a*b/(1-2b). Narrow intervals do not
  automatically establish a neural advantage. b=1/2 is not a phase boundary.
- For HNW g=0, a=lambda,b=lambda/8: the same explicit event interval holds
  for0<lambda<4 by comparison. This does not extend HNW's profile-stability
  theorem to that full range. No general sharpness or actual event value claimed.
- Dirichlet splice obstruction: prior polynomial has endpoint slopes +/-192/5.
  Its zero extension has derivative jumps and is not H2 across endpoints,
  so cannot meet HNW H12. Smoothing/whole-line evolution changes the benchmark.
- Norm control: g_epsilon=+/-epsilon^4*phi(z/epsilon), phi even compact smooth,
  phi(0)=phi''(0)=0,phi''''(0)=1. Singular weighted L2 norm squared O(epsilon^3)
  vanishes but fourth jet is +/-1; initial lambda drift has opposite signs.
  Twelfth-derivative norm squared scales epsilon^-15, so HNW is not contradicted.
  No different final blow-up class or trained-model failure established.
- Direct method parent: Wang et al.2506.19243v1 already uses hard local jets,
  parity, far-field information and high-precision PINN optimization, and cites
  HNW. TMLR final-text identity not qualified. CGL2407.15812v1 selected setup
  covers removal of evenness with translation/rotation. Fasondini2023 publisher
  abstract only is the reciprocal-variable parent, not a source of our interval.
- Three selected primary full texts, one publisher-search abstract; one author-
  hosted copyrighted PDF privately cached, pages3,6,15 visually checked.
  No code, raw outcomes, solvers, GPUs/SSH, participants, outreach or publication.
- Next: a named matched physical mechanism disagreement or theorem with a
  nonclassical residual contribution before re-entry. Another normalization,
  reciprocal coordinate, interval or derivative penalty is insufficient.
- Verified2026-09-09T15:03:59Z: graph293/274/1357, evidence951,
  reentry126/qualified0; cycles21/raw133/cards0 unchanged. Scoped validator,
  five cache hashes,18 existing tests and git diff --check passed. These are
  record checks, not a novelty assessment or independent source-proof replay.
  Receipt `logs/private/paper_g_blowup_scope_20260910_verification.md`.
