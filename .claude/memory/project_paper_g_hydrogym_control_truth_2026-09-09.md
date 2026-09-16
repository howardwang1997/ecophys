# Paper G HydroGym controlled-flow truth preflight

PRIVATE / INTERNAL. Development infrastructure, not public research evidence.

The September9 preflight pins seven HydroGym source/license texts at commit
4ab9854dea3d84e38a59c25e0f5835a00cf8225f. Selected primary reading covers the
June30 expanded preprint, August19 Nature publisher-indexed passages and the
L4DC2025 parent abstract/metadata. These are one platform lineage. The selected
KolmogorovFlow inherits JAXFlowEnvBase without HF integration; do not transfer
the separate JAXFlowEnv constructor behavior to this class.

Decision: partial_capability, zero removed contribution blockers, no candidate
harvest, new search cycle, machine card, implementation, outcomes or compute.
History-response and numerical-teacher routes remain failed_closed; this does
not close the whole fluid-control domain. Multiple backends do not qualify
independent same-PDE control truth, and a numerical wing is not physical field
confirmation. The exact archived paper-code identity is still unqualified.

Reusable continuum controls on periodic zero-mean shear u=(sum c_k sin(ky),0):

- Held momentum forcing b_k+a_k gives c_k(tau)=r_k*c_k(0)+g_k*(b_k+a_k),
  r_k=exp(-nu*k^2*tau),g_k=(1-r_k)/(nu*k^2). Its action gain g_k differs from
  an initial velocity reset gain r_k, even with matched integrated impulse.
- E=sum(c_k^2)/4, P=sum((b_k+a_k)*c_k)/2,D=nu*sum(k^2*c_k^2)/2 and E'=P-D.
  Fixed action norm can inject, extract or instantaneously supply zero fluid
  power as the initial shear changes. This is classical accounting, not a new
  theorem or a claim about electrical actuator cost or published policy failure.

The shear subfamily has zero nonlinear advection. It cannot validate chaotic
gradients. Source policy observations average trajectory speed samples; endpoint
spectral state and that observation must stay distinct. Equal instantaneous
speed under a sign flip does not establish identical legal observation histories.
Source/config/physical time, replay lifecycle, independent nonlinear truth,
untouched whole-source confirmation and equal-access baseline remain required.

Formal result: papers/proposal/ecomd_paper_g_hydrogym_control_truth_preflight_2026-09-09.md.
Contract: research/paper_g/hydrogym_control_truth_preflight_20260909.yaml.
Manifest: research/paper_g/hydrogym_source_manifest_20260909.json.
Next update must supply a distinct matched contribution or primary disagreement;
platform access alone does not reopen the saturated parent.

Verified 2026-09-09T10:07:38Z: graph293 /edges274 /locators1277; evidence903;
re-entry114 /qualified0; cycles21 /raw133 /cards0 unchanged. Canonical scoped
validation, source/contract/trigger parity, seven pinned source hashes,18 existing
tests and git diff --check passed. Receipt: `logs/private/paper_g_hydrogym_20260909_verification.md`.
