# EcoMD stochastic-semantics re-entry audit (2026-09-04)

## Canonical decision

The noise-frame, non-Gaussian-bath and cross-implementation gradient-conformance formulations do
not activate a new EcoMD ICLR topic. Decisions are respectively `not_trigger`, `not_trigger` and
`partial_capability`; all remove zero route blockers and keep `candidate_harvest_authorized: false`.
This was a blocker-specific, outcome-blind audit rather than Discovery Cycle 17. No public package
or simulator was executed, and no SSH, EcoMD edit or GPU work occurred. The formal record is
`papers/proposal/ecomd_stochastic_semantics_reentry_audit_2026-09-04.md`.

## Durable findings

- Diffusion factorization is not a forward-law invariant. The family
  `X_theta=cos(c theta) W_1 + sin(c theta) W_2` has a constant `N(0,t)` law and zero population
  derivative, but at zero its pathwise estimator is `c phi'(W_1) W_2`, whose variance is
  `c^2 t E[phi'(W_1)^2]`. The arbitrary frame can therefore set gradient variance and sample sign
  without changing the model law. This is a claim gate, not novelty: pathwise transport fields,
  common-random-path optimality, learned same-marginal correlations and diffusion gauges occupy the
  generic method.
- For Euler OU with unit-variance innovation excess kurtosis `kappa_epsilon`, stationary excess
  kurtosis is `kappa_epsilon (1-r^2)/(1+r^2)`. With `r=1-lambda h`, EcoMD's Student-t5 bath contributes
  only `6 lambda h + O(h^2)`, which vanishes under refinement. Direct 2023 Langevin-integrator work
  already establishes the higher-moment and Boltzmann distortion from non-Gaussian discrete noise.
- EcoMD's alpha-stable sampler is multiplied by `sqrt(h)` and then clipped. Without clipping its
  stationary scale behaves as `h^(1/2-1/alpha)` and diverges for `alpha<2`; Levy increments require
  `h^(1/alpha)`. With fixed clipping the refinement is finite-variance/Gaussian, and the clipped
  sample is not unit-variance normalized. Prior trained-Levy results are therefore discrete-kernel
  results, not evidence for a resolution-invariant physical bath.
- Public CTMC capability is stronger than the earlier scan. `codeExactDL` is pinned at
  `f191cd435ade065ff4356d8721ac1cac0f992a83`; `stochastix` has Apache-2.0 tag v0.2.0 at
  `2d83fe64ac1bff9d80367338e3b4fc222357fb66`; `stochastix-paper` is Apache-2.0 at
  `cc09f8c77b8009b4987a335e19680b7217ef7450`; and `DifferentiableGillespie` is pinned at
  `a3ee28b3081f42cef7f0d0f85c32d8d4c67ec556` with MIT package metadata but no root licence file.
- The portfolio does not form a matched two-system fixture. `codeExactDL` has no repository
  licence/tag and linearly interpolates cadlag count states for its dimerization loss while using a
  different step/integral convention for ion channels. `stochastix-paper` has loose dependencies;
  `stochastix` does not return a complete PRNG tape; Burger's repository is untagged and lacks a
  root licence file. Their observation clocks, cutoff rules and replay states differ.
- A generic conformance benchmark is occupied. Burger et al. v2 already compare GS-ST,
  score-function and alternative-path gradients against analytic truth under event-count and
  physical-time semantics. StochasticAD and ADEV give unbiased or denotationally sound expected-
  value differentiation for discrete probabilistic programs. Mosaic already benchmarks solver
  forward passes, VJPs, finite-difference accuracy, conditioning, cost and optimization.

## Re-entry condition

Require either (1) a market-observable noise-frame-invariant gradient theorem beyond transport and
coupling parents, (2) a non-Gaussian market mechanism whose tail law survives time-step, clipping
and observation refinement without inserting the answer, or (3) a semantic certificate with a new
power/complexity theorem that analytic CME, unbiased stochastic AD, common-random finite differences
and Mosaic-style checks cannot replace, plus two licensed matched systems and a market-native
bridge. More seeds, benchmark rows or GPU throughput do not qualify.
