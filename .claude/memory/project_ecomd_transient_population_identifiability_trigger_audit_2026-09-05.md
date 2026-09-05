# EcoMD transient-population identifiability trigger audit — lasting decisions

- Formal result:
  `papers/proposal/ecomd_transient_population_identifiability_trigger_audit_2026-09-05.md`.
- The trigger is `partial_capability`, not qualified. It removes zero project blockers, authorizes no
  candidate harvest and gives no implementation, outcome, SSH or GPU permission.
- Guan et al. (AISTATS 2026) prove joint identifiability of a time-homogeneous gradient drift and
  constant scalar diffusivity from exact temporal population marginals iff the population is seen
  outside equilibrium. Their equilibrium rescaling is the continuous-time counterpart of EcoMD's
  energy--friction--temperature gauge.
- The result does not cover EcoMD's endogenous feedback, nonconservative current, memory,
  state-dependent noise or jumps. Its data are independent full-state population samples at
  synchronized times, not one aggregate market trajectory or a cross-section of coupled latent
  agents.
- Exact counterexample: for radial transient densities, adding `u(x)=Omega x` with skew `Omega`
  preserves every temporal marginal because `div(p_t u)=0`, while changing rotational current.
  Nonstationarity alone therefore does not identify general drift.
- For known diffusion, uniqueness requires temporal score-ratio gradients
  `grad log(p_t/p_t0)` to span the tangent space. This is the time-indexed counterpart of the closed
  V11/V12 density-ratio operator. Unknown scalar diffusion needs an augmented score/Laplacian frame;
  state-dependent diffusion leaves a larger field ambiguity.
- APPEX already occupies linear non-gradient temporal-marginal identification and a general
  additive-noise inference algorithm; nn-APPEX occupies nonlinear gradient-flow joint inference.
- Re-entry requires both a nonconservative finite-sample stability theorem/estimator beyond those
  parents and a legal repeated-population market asset or assigned actuator with untouched response
  truth and independent replication.
