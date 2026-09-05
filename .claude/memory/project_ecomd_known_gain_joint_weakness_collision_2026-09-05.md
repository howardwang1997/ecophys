# EcoMD known-gain joint-weakness collision (2026-09-05)

- The remaining proposed extension was a joint local phase diagram for three vanishing signals:
  gain-conditioned covariance excitation `xi_n`, reciprocal spectral gaps, and innovation
  non-Gaussianity `beta_n`.
- The covariance-only face is the prior exact result: KL to zero is
  `n*(a^2*xi_n^2+a^4)`. The `xi_n=0` face is already the near-Gaussian ICA/SVAR problem, where
  contamination at or below `n^-1/2` loses mixing identification beyond transpose products.
- A tempting combined law `n*a^2*(xi_n^2+beta_n^2)+n*a^4` is not a theorem. It needs a specified
  source family, score orthogonality and nuisance projection; least-favourable innovation families
  can make channels non-additive.
- Sokol--Maathuis--Falkeborg (EJS 2014) own the near-Gaussian ICA threshold; Hoesch (QE 2024) owns
  locally robust weak-nonGaussian SVAR inference; Junare (2026) owns bootstrap diagnostics at the
  Gaussian-shock boundary; Guay--Stevanovic (2026) own spectral-gap and local-to-weak SVAR limits.
  Stationary Lyapunov higher-cumulant parents are also direct collisions.
- Decision: `not_trigger`; no candidate, machine card, implementation, outcome access, SSH or GPU.
  Re-entry requires a genuinely non-additive joint local experiment with nuisance-efficient uniform
  inference beyond weak ICA/SVAR, Lyapunov cumulants, graphical regression and weak GMM, plus two
  same-estimand controlled truth systems.
