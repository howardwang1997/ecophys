---
name: Paper G energy target and local entropy preflight
description: Physical constraint targets must distinguish full/resolved state, samples/conditional means and global/local entropy; direct parents prevent novelty escalation.
type: project
---

**PRIVATE / INTERNAL — discovery infrastructure, not public research evidence.**

Decision: partial capability, zero removed blockers, no candidate harvest or new
cycle. Linked to `theory_exploration_equation_audit_v3`, which remains closed.
Paper D supplies the affine-constraint PDE scope; its evidence labels remain.

Durable controls:

- Periodic viscous Burgers with initial u=a*sin(x)+b*sin(2x), a!=0, nu>0:
  a_dot=ab/2-nu*a and b_dot=-a^2/2-4nu*b at time zero in the full PDE.
  With E=norm(u)^2/2 and norm^2=(1/pi) integral u^2,
  E_P_dot=a^2*(b/2-nu) and E_dot=-nu*(a^2+4b^2).
  b=+/-B with B>2nu matches resolved state and SGS energy but reverses resolved
  transfer while total energy decays. This is instantaneous, not a truncated rollout.
- The van Gastelen/Edeling/Sanderse model already permits backscatter and uses
  signed linear SGS compression. The unsigned-energy twin is not a collision
  under its actual transform T and must not be presented as refuting the method.
- If norm(Y)=r(O), m=E[Y|O], then r^2=norm(m)^2+trace Cov(Y|O).
  A radius-r deterministic prediction adds at least(r-norm(m))^2 Bayes squared
  risk. Isotropic scattering has mean risk r^2 versus constrained prediction
  risk2r^2. An independent correct sample also has risk2r^2; distributional
  prediction is a different task. Zero conditional variance, affine constraints
  and a convex norm upper bound provide explicit nulls.
- Stationary periodic Burgers square wave(+1 left,-1 right) is weakly conserving
  with constant global entropy integrals. For eta=u^2/2,q=u^3/3, local residual
  is(2/3)delta_pi-(2/3)delta_0. A seam-localized positive test rejects the expansion
  jump. Standard entropy conditions and wPINNs already supply the remedy.

Sources: ECNN arXiv2301.13770v5 (selected sections2.5–3.2), stochastic neural
collision Physics of Fluids38,057123 (2026-05-20; sectionsII.C–D), wPINNs
section2 and local-residual construction; ENO AISTATS2025 abstract only.
ECNCM_1D README/directory metadata supplies Julia source and manifest pointers.
Repository license label, replay, independent solver and untouched confirmation
are not fully qualified. No source implementation, outcomes, notebook outputs,
checkpoint, simulation, scientific code, GPU, outreach or publication.

Formal: `papers/proposal/ecomd_paper_g_energy_entropy_preflight_2026-09-09.md`.
Structured: `research/paper_g/energy_entropy_preflight_20260909.yaml`.
Trigger: `paper_g_energy_entropy_target_contract_20260909`.
Verification: `logs/private/paper_g_energy_entropy_preflight_20260909_verification.md`.

Canonical graph292 /edges274 /locators1210; evidence859; triggers106 /qualified0;
cycles20 /raw132 /cards0 unchanged. No new forecast or F3 audit.

Next requires a source-specific result or newly qualified asset leaving a
same-state, same-information residual beyond competent energy closure,
stochastic prediction and local entropy baselines. Wrong-target constraints
and elementary identities cannot be promoted into a new scientific method.
