# Paper G: sampled kernel certificate scope

PRIVATE / INTERNAL. Session6, 2026-09-10 01:50 NZST. Bounded paper-only
follow-up; previous turn classified progress. No candidate harvesting or cycle.

- Formal: `papers/proposal/ecomd_paper_g_ks_kernel_certificate_scope_2026-09-10.md`.
- Contract: `research/paper_g/ks_kernel_certificate_scope_20260910.yaml`.
- Source manifest: `research/paper_g/ks_kernel_source_manifest_20260910.json`.
- Partial capability, no removed route blocker. Stop generic scalar-moment
  certificate expansion; all existing statuses and original goal unchanged.
- Positive result: for fixed radial potential Kdelta, write g=2*pi*r*Kdelta',
  D=1-g. The scalar virial correction is C=E[D(|X-Y|)] for iid density draws.
  This can be bounded and sampled without a density upper bound. The preceding
  concern about unusable density bounds is too strong for this narrow task.
- Kernel scope: Fournier–Jourdain force softening gives D=delta^2/(r^2+delta^2)
  in [0,1]. DeepParticle v2 Equation7 instead multiplies the potential by
  r^2/(r^2+delta^2); its derivative has an extra logarithmic term. A declared
  reference length ell gives range width 3/2+abs(log(delta/ell)). Freeze the
  actual mathematical kernel; no executed-code or later-method identity claim.
- IID pairs from a frozen pointwise generator give the standard Hoeffding
  radius R*sqrt(log(2/alpha)/(2*n)). This is not n^2 independent samples;
  disjoint labels in one interacting cloud are not independent. Empirical
  resampling estimates an empirical-law functional, not continuum truth.
  Independent times with density b/integral(b) can target one weighted integral;
  no uniform-time/adaptive-selection coverage follows.
- Persistence correction: Ldelta,shape+c*B*Cdelta,b>=-a*J0+kappa*B,
  B=log(1+a*T). An upper C bound gives a necessary lower action bound. It
  gives no full velocity-residual upper bound or vector kernel-bias bound.
- Exact control: a smooth radial reference before singularity pushed through
  S=diag(sqrt(1+eta),sqrt(1-eta)), eta(0)=0, preserves initial density,mass,
  center and J(t), but has covariance eigenvalue gap abs(eta)*J. Hence exact
  scalar virial agreement does not identify shape. No trained-model claim or
  claim that its softened pair correction equals the reference.
- Direct parents: DeepParticle2024 already uses neural/particle moments and
  examines regularization; Fournier–Jourdain2015 has symmetrization and force
  regularization; Hoeffding1963 is the concentration parent. Two selected
  full texts, one primary publisher-search abstract; three old refs reused.
- Next re-entry review requires substantive spatial coercivity, exact event
  time/control truth or a matched primary-model disagreement that removes a
  recorded contribution blocker. Another moment or iid interval is insufficient.
- One CC-BY-4.0 preprint PDF privately cached and page4 visually checked;
  no scientific implementation, outcomes, simulations, source code, GPU/SSH,
  outreach, participants, purchase or publication. All analysis development.
- Canonical after registration: graph293/274/1342, evidence942,
  reentry124/qualified0; cycles21/raw133/cards0 unchanged. Goal active.
