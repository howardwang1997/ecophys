# Paper G: experimental observation and constraint truth

PRIVATE / INTERNAL. Session35,2026-09-09. Decision:partial_capability;
zero removed blockers,no candidate or cycle. Goal remains active.

- Renn-Palmer-Gharib SciData2026 supplies planar cylinder-wake velocity sequences;
  the source explicitly recognizes 3D effects. No planar divergence-free truth
  follows. CaltechDATA g2z1f-nex65 v2,created2025-11-06,has public files and
  CC-BY4 data rights verified by official API,separate from article terms.
- AIVT arXiv2407.15727v2 selected methods describe joint volumetric positions,
  three velocity components and calibrated particle temperatures. Gradients
  and dissipation are inferred fields,not simultaneous direct derivative truth.
  Dryad154294 v4/resource359200,2025-04-16,CC0-1.0,documents txyz/uvwT arrays.
  Both asset metadata were pinned;no HDF5,MAT or notebook files were accessed.
- Exact unforced periodic Navier-Stokes control:U=a(t)*(sinx*cosz,0,-cosx*sinz),
  a=A*exp(-2nu*t),p=a^2*(cos2x+cos2z)/4. Full divergence is zero,but the z0
  planar restriction is (a*sinx,0),whose planar divergence is a*cosx. Planar
  orthogonal Helmholtz projection removes this entire gradient. Single-plane
  stereo still measures Uz=0,not its missing normal derivative. Planar shear
  provides the null. This is standard observation/projection noncommutation.
- Generic error identity:||P(v+e)-v||^2-||e||^2=||Qv||^2-||Qe||^2,Q=I-P.
  No zero-mean or independence assumption needed. Nearby planes resolve the
  declared mode with sinc(h) bias and sigma^2/(2h^2) independent-noise variance;
  no universal finite-spacing derivative or new measurement theorem follows.
- Shimano-Shiratori-Nagano Meccanica2024 is direct prior for planar inference
  with out-of-plane transport. Its one-component target differs from the
  two-component projection control,but the broad mismatch/remedy is occupied.
- Preserve point values,derivative truth,complete state and intervention truth
  as separate capabilities. Whole-source confirmation,calibrated covariance,
  independent same-target replication and a distinct contribution remain open.
  Do not present old releases as new post-closure acquisitions or infer a failure
  of Paper D from this different observed object.

Formal:`papers/proposal/ecomd_paper_g_observation_constraint_truth_preflight_2026-09-09.md`.
Contract:`research/paper_g/observation_constraint_truth_preflight_20260909.yaml`.

Completed after local midnight on2026-09-10;see both dated logs.
Verified 2026-09-09T12:06:29Z: graph293 /edges274 /locators1303;evidence917;
re-entry119 /qualified0;cycles21 /raw133 /cards0 unchanged. Scoped canonical
validation,source/contract/trigger parity,two metadata hashes and version/rights
parity,18 existing tests and git diff --check passed. Search,protocol and forecast
bytes unchanged. Receipt:`logs/private/paper_g_observation_truth_20260909_verification.md`.
