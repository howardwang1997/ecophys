# EcoMD unpaired interaction-energy trigger audit — 2026-09-05

## Durable decision

- Stage: bounded D-3 re-entry-trigger audit; no candidate harvest.
- Decision: `not_trigger`; zero removed blockers; no topic card, implementation, simulation, SSH or
  GPU authorization.
- Formal result:
  `papers/proposal/ecomd_unpaired_interaction_energy_trigger_audit_2026-09-05.md`.

## Lasting findings

- ICLR 2026 iJKOnet corrected a paired-data leak in an intended unpaired snapshot benchmark and
  reports that iJKOnet and JKOnet* do not accurately recover tested interaction energies. Its theorem
  is restricted to potential energy. Paper v3 and the official MIT code at
  `873bc0a331f79e2ab1b2d539d29ebb9df0ce444a` predate the August EcoMD closures.
- Replacing the all-pairs mini-batch V-statistic by an off-diagonal U-statistic removes only an
  `O(1/B)` diagonal bias. This is a classical estimator correction, not interaction-law
  identifiability.
- Exact gauge: for any transient density path with fixed mean `m`, adding
  `delta W(z)=c||z||^2/2` and `delta V(x)=-c||x||^2/2+c m^T x` leaves
  `grad V + grad W*rho_t` unchanged at every time. Non-equilibrium alone therefore does not separate
  external confinement from pair interaction even inside the gradient-flow class.
- Lang--Lu already characterize the identifiable mean-field interaction space and its ill-posed
  inverse operator. Density inversion, WSINDy and sparse partial inversion already recover
  interaction kernels from aggregate or discrete particle observations and supply numerical,
  finite-particle, noise or Wasserstein-stability guarantees. JKOnet* and iJKOnet occupy the inverse-
  JKO formulation.
- EntangledSBM learns a target-conditioned control bias relative to known base dynamics; static
  endpoints do not identify the uncontrolled physical force.
- EcoMD agents are latent, coupled and representation-dependent. One market tape is not a sequence
  of independent synchronized populations, and no current asset supplies complete repeated state,
  controlled excitation, untouched response truth and independent replication.

## Re-entry condition

Require both (i) a genuinely new finite-sample quotient-aware theorem/estimator for joint external,
interaction and diffusion recovery with sharp behavior near coercivity loss, beyond inverse JKO,
weak-form/RKHS and partial-inversion parents, and (ii) a legal market population or assigned-control
asset with complete pre-state, untouched same-estimand truth and independent replication.
