# EcoMD known-gain reciprocity-cancellation follow-up (2026-09-05)

- The prior pure-circulation result is exact but does not imply that unequal gains always reveal
  orientation. With `K=I`, `Phi=diag(p1,p2)+a[[0,1],[-1,0]]`, the off-diagonal precision signal is
  `a c`, where `c=(g1-g2)+g1*g2*(p1-p2)`.
- Opposite signs `a` and `-a` have exact Gaussian sign KL
  `2*a^2*c^2 / ((1-p1*g1)*(1-p2*g2)+a^2*g1*g2)^2`. They are exactly equivalent when
  `p1-p2=1/g1-1/g2`, even if `g1 != g2`. The full-law ambiguity also holds for spherical
  innovations, so financial heavy tails alone are not an identification assumption.
- Conversely, common gain is not universally blind: for `g1=g2=s`, the signal is
  `s^2*(p1-p2)`. It vanishes only on reciprocal-isotropic pairs. The true object is joint
  gain--reciprocity geometry.
- Across two-channel environments, write `d_t=1/g1t-1/g2t` and `w_t=g1t*g2t`. The score numerator
  is `c_t=w_t(delta-d_t)`. Varying `d_t` prevents one unknown reciprocal contrast `delta` from
  cancelling every environment; its worst-case raw excitation is the weighted variance of `d_t`.
  This is a restricted exact result, not a general optimal-design theorem.
- The corrected weak boundary uses `xi_n^2=mean(c_t^2)`: KL to zero is of order
  `n*(a^2*xi_n^2+a^4)`, giving `1/(sqrt(n)*xi_n)` versus `n^-1/4`. Any gain-only condition number can
  falsely certify a singular design.
- In general, with `Phi=P+Q`, `P` symmetric and `Q` skew, the orientation derivative at `Q=0` is
  `[D,U]+D[P,U]D`. Under common gain it becomes `s^2[P,U]`; reciprocal eigenvalue gaps can reveal
  circulation and repeated eigenspaces are singular. With unknown nuisance, the correct target is a
  nuisance-projected stacked information operator, which remains undeveloped.
- Direct parents now include continuous/discrete Lyapunov identification, UAI 2026 sign
  identifiability, UAI/ICML 2026 interventional SDE recovery, NeurIPS 2025 near-optimal cyclic
  experiment design, and higher-cumulant estimators. The standalone inverse-gain-design ICLR pitch is
  killed; the theorem is retained as `partial_capability` and a false-positive design guard.
- Re-entry requires joint arbitrary-support identification with unknown `K`, matching minimax and
  uniform inference through simultaneous weak gain/reciprocity/non-Gaussianity, irreducibility from
  the direct parents, and two same-estimand controlled truth systems. No candidate, implementation,
  outcome access, SSH or GPU work is authorized.
