# EcoMD integrator and calibration trigger audit — lasting decisions

- Formal result:
  `papers/proposal/ecomd_integrator_calibration_trigger_audit_2026-09-05.md`.
- This was a bounded D-3 trigger audit, not a new discovery cycle. It inspected no stored outcome,
  ran no simulator or notebook, made no SSH connection and used no GPU.
- Four proposed triggers were adjudicated: fixed multi-timescale Langevin scheduling,
  probabilistically verified attainable sets, finite-rollout statistic losses, and score-based
  effective Langevin current inference. Decisions are three `not_trigger` and one
  `partial_capability`; no named blocker was removed and candidate harvesting remains forbidden.

## Lasting mathematical findings

1. If exact coordinate/subset kernels all preserve `pi`, any fixed state-independent composition
   preserves `pi`. EcoMD's fast/slow mask is a fixed systematic scan. Its Euler implementation can
   have standard splitting/discretization bias, while a state-dependent clock defines a different
   time-changed process; neither is a new invariant-law mechanism.
2. Fixed-network probabilistic verifiers do not preserve the required quantifier order
   `sup_theta E_noise[path statistic]`. Treating parameters as random inputs gives a mixture;
   treating them as adversarial inputs gives `sup_(theta,noise)` and usually a vacuous bound.
3. For rollout statistic `Z` and target `s`,
   `E||Z-s||^2 = ||EZ-s||^2 + tr Cov(Z)`. An independent two-rollout cross product removes the
   variance term but is only an unbiased mean-functional loss, not a proper score for the full path
   law. Kernel-score/U-statistic calibration and 2026 proper trajectory scoring directly occupy the
   general method.
4. Giorgini's 2026 PRE construction learns constant mean diffusion and mean antisymmetric
   circulation from a stationary score plus short-lag correlations. The conditional-score follow-up
   fits state-dependent mobility from lagged pairs, but in general identifies only projected
   generator action or an observable-dependent equivalence class. It uses transition information,
   not stationary samples alone, and supplies no external market actuator. It therefore does not
   reopen `solenoidal_excitation_gap_v12`.

## Repository interpretation quarantine

- `DissipationPotential` uses `lambda ||s_n-s_(n-1)||^2`; its force is multiplied by `dt` again in
  the Euler update, so its cumulative physical-friction effect vanishes under refinement unless an
  inverse-step scaling and consistent discretization are introduced.
- `entropy_production_per_step` labels `F_diss dot v / T` as positive entropy generation. A
  conventional system friction force has nonpositive force power, medium entropy uses the opposite
  sign, and total stochastic entropy needs a path-probability/system-entropy term. Because EcoMD's
  force is lagged, even the proxy has no fixed sign. Old physical entropy-production claims remain
  quarantined.
- State/history-dependent `T/gamma` and stochastic-volatility noise are not a Gibbs sampler without
  a declared stochastic convention and noise-induced drift. EcoMD is explicitly nonequilibrium, so
  no unique correction is physically privileged until a target path law is frozen.
- The current `isolate_state=True` force helper correctly takes a partial derivative with context
  held fixed; the legacy option takes a total derivative through shared history. This is QA, not a
  method contribution.
- A frozen-context gradient is not generally a conservative force after the context is closed around
  the state. For `F_i=-V_{s_i}(s,C(s))`, the curl contains
  `-sum_a(V_{s_i c_a} C_{a,s_j}-V_{s_j c_a} C_{a,s_i})` and is generically nonzero; if context uses
  history, `s` is not a closed Markov state. Context evolution must be accounted for as
  feedback/controller work. Continuous non-Markovian feedback thermodynamics is direct prior art,
  so this is an interpretation quarantine rather than a paper route.
- Uniform block averaging commutes with the repository's global mean-removal projector; a generic
  projection-resolution commutator does not create a child paper and risks duplicating Paper D.
- The overdamped transition has the exact scale gauge
  `(V, Psi, gamma, T) -> (cV, cPsi, c gamma, cT)` when all force-generating terms are scaled. The
  latent and price paths are unchanged for the same random tape, so absolute learned energy,
  friction and temperature have no separate physical meaning without an external normalization.
  Current M0 freezes `gamma` and `T`; several historical architecture configs learned them, so their
  numerical values are not physical estimates.

## Re-entry and compute boundary

Re-entry needs one of the four exact objects listed in the formal result: a native endogenous-clock
theorem, a quantifier-correct recurrent expectation certificate, an irreducible proper dependent-path
score, or stationary-sample/control-dependent current identification with two-system truth and an
untouched market response. A topic card and new current machine decision are still required before
implementation, outcome access, SSH or GPU work on the A800 or either V100.
