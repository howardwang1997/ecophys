---
name: EcoMD recurrent-depth accuracy-control trigger audit
description: RecurrSim exposes a useful compute dial but no per-instance accuracy controller; exact wrong-fixed-point counterexamples and direct early-exit, LTT, conformal-operator, and step-doubling parents make the obvious repair incremental, while the official supplement is not a clean depth-intervention fixture.
type: project
---

# EcoMD recurrent-depth accuracy-control trigger audit

- RecurrSim (ICLR 2026) trains a weight-tied simulator at random recurrent depths and reports
  favorable average accuracy-cost curves. It supplies no theorem making error monotone in depth, no
  mapping from a requested tolerance to per-instance depth, and no calibrated error or abstention
  output. A compute dial is not accuracy control.
- Exact counterexample: for `T(z)=rho*z+(1-rho)*c`, `0<rho<1`, identity decoder, target `y!=c`, and
  `z0=y`, the update residual tends to zero while truth error increases monotonically to `|c-y|`.
  Convergence to a learned fixed point therefore cannot certify physical truth.
- Mean improvement is also insufficient: two examples can have depth losses `(0,2)` and `(4,0)`,
  making mean loss fall from 2 to 1 while one example worsens. Any output-only stopping rule admits
  two observationally identical worlds with different truths, so a uniform label-free certificate
  is impossible without calibration or a truth-equivalent physical residual.
- The positive repair is directly occupied. Fast yet Safe applies CRC/UCB/LTT to arbitrary bounded
  early-exit losses; Learn-then-Test selects finite policy families without monotonicity; Conformal
  Thinking chooses the lowest-cost valid signal-threshold rule; adaptive CRC/LTT cover difficulty
  conditioning and adaptive configuration testing. Put `(K,H,score,threshold)` in the policy and
  use a max-over-horizon bounded path loss: selection validity and path simultaneity follow without
  new simulator mathematics.
- Hybrid Neural World Models already uses semigroup step-doubling to rank surrogate errors and gate
  exact-solver fallback, including a reported below-chance far-OOD collision regime. Millard et al.
  and the post-closure Stent--Boulle paper cover function-space/neural-operator conformal bands;
  variationally correct operators cover physics-linked a posteriori residual bounds when equations
  are available. ICLR 2026 implicit-model theory occupies the broad recurrent-depth expressivity
  explanation.
- Official RecurrSim supplement SHA256 `73450aae...` is not a clean fixture: training executes
  `max(K,B)` rather than sampled `K` below the TBPTT floor; evaluation draws fresh latent state;
  `state_dict().copy()` aliases best-checkpoint tensors; the main sweep reuses `valid_traj`; and the
  trajectory loss remains marked for repair. These are source-level provenance findings, not an
  empirical refutation.
- EcoMD-as-truth would test only surrogate fidelity to EcoMD, not real-market counterfactual
  validity; available markets lack paired same-prestate trajectory truth, coupled stochastic tapes,
  and untouched independent replication.
- Decision: `not_trigger`, zero blockers removed, no candidate harvesting, implementation, outcome
  access, simulation, SSH, or GPU. Re-entry requires a prospectively frozen hard-event/dependent-
  rollout theorem with an observable, sharp truth-error certificate and matching lower bound that
  is not representable as generic LTT/CRC policy selection, or a lawful repeated market truth asset.

