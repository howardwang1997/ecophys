# Paper G: true-memory source and observability preflight

Private/internal; 2026-09-09. Formal result:
`papers/proposal/ecomd_paper_g_true_memory_preflight_2026-09-09.md`.
Structured contract: `research/paper_g/true_memory_preflight_20260909.yaml`.

- Partial source capability, zero removed blockers. No candidate, new cycle,
  forecast, card or execution. Physical-history response and v3 state-closure
  routes remain failed_closed; the neural-PDE domain is not globally closed.
- MemNO ICLR2025 directly covers benefits of PDE memory with low-resolution/noisy
  observation. Its stated inference task starts from an observed initial field
  and feeds back generated predictions; internal recurrence is not new sensing.
  Its interpolation/downsampling differs from sharp spectral filtering.
- HS-FNO uses a supplied delay-PDE history segment; exact shift-append is not a
  cure for next-slice prediction error or insufficient history sampling.
- Flux-form2026 uses filtered histories and a closure energy-injection correlation
  guideline, with an oscillatory-correlation caveat and local grid search. Do not
  call it a universal minimal-history or observability theorem.
- Pan–Duraisamy SIADS2018 section5 already gives finite-memory rank tests and
  distinguishes reconstructing the desired closure from all hidden coordinates.
  Target-specific observability is not a fresh Paper G contribution.
- Exact A: for fixed trained parameters, generated history measurable from O
  leaves sigma(O) unchanged and cannot reduce unrestricted Bayes risk below
  E trace Cov(Y|O). Recurrence can still improve approximation, retention and
  optimization; independent randomization can represent conditional uncertainty.
- Exact B: an observed quadrature of an advection-diffusion Fourier mode has
  eliminated kernel -omega^2 exp(-gamma*t), with decay1/gamma, yet two exact
  observations predict via x_next=2r*cos(theta)*x-r^2*x_previous. At theta pi/2
  the inversion is well conditioned even as1/gamma grows. Complete-pair Fourier
  projection commutes with the same PDE and gives a Markov retained field.
  These observation maps differ; no representation-invariant physical effect
  or refutation of the flux paper's actual injection diagnostic is claimed.
- Exact C: at theta pi the hidden quadrature is unobservable from any sampled
  x history, but same-grid future x is predictable; the quarter-period target
  is not. Standard Gaussian conditioning gives a target-dependent positive
  Bayes-risk control under finite noisy observations. No new filtering theorem.
- Exact D: future pairs(R,R) and(R,-R) have identical lead marginals but temporal
  covariance+1/-1 and sum variance4/0. Sum-of-lead scores does not alone identify
  a non-Markov joint path. Brolly2026 equation10 has this per-lead scoring scope;
  its MSE and marginal claims remain intact. A new joint-score label is occupied.
- The LPSDA fork named by MemNO documents fixed time spacing and viscosity/
  initial-mode controls and has an MIT repository license. Only README/license
  metadata qualified. No immutable implementation, replay, dependency rights,
  accuracy, untouched partition or second independent solver qualified. A fork
  is not an independent lineage merely through a new URL.
- Canonical evidence now explicitly scopes Brolly to lead-wise conditional
  marginals; maintenance history exists only in a separate private audit.
- Next source intake must remove a named blocker with an immutable truth/control
  contract or substantive result beyond MemNO, closure/filtering observability
  and correctly specified scoring. No repeat true-memory or memory-plus-noise
  candidate harvesting. The persistent ICML-main/NMI/NCS goal remains active.
- Verified2026-09-09T06:51:23Z: graph292 /274 /1194; evidence847;
  triggers104 /qualified0; cycles20 /raw132 /cards0 unchanged. Canonical scoped
  checks,18 existing tests and `git diff --check` passed. Receipt:
  `logs/private/paper_g_true_memory_preflight_20260909_verification.md`.
