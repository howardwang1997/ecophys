# EcoMD stochastic hard-projection measure audit (2026-09-05)

Status: `failed_closed`; trigger `not_trigger`; no outcome, implementation, SSH or GPU.

The candidate asked whether per-step hard conservation in a stochastic market surrogate silently
changes its generator and invariant measure, and whether a Jacobian/Fixman correction could be a new
ICLR method. The exact general issue is real: for a nonlinear equality constraint `c(x)=0`, the
small-residual-noise conditional density relative to surface volume contains
`det(JJ^T)^(-1/2)`, and a state-dependent tangent projector carries geometric drift.

It is not a new route. Lelièvre--Rousset--Stoltz (2012) cover constrained Langevin sampling and
measure-correct numerics; Hartmann--Neureither--Sharma (2026) directly cover affine constraints in
nonreversible degenerate-noise SDEs and conditional invariant measures; Xu et al. (2026) directly
state the ML hard-projection/co-area bias and provide a corrected sampler.

The repository's relevant market projection is in `scripts/run_constraint_iclr_market.py`, not the
EcoMD core. It enforces `sum cash delta + fee delta = 0` and `sum inventory delta = 0` by blockwise
mean removal. Hence `c(x)=Ax-b`, `J=A` and the orthogonal projector are constant: the co-area factor
cancels and curvature drift is zero. Positivity is an inequality/reflected-process problem already
closed; using `xy=k` moves to the already closed CFMM-curvature route.

Reusable gate: compute the native constraint Jacobian before proposing stochastic projection
geometry. An affine constraint cannot demonstrate a nontrivial Fixman correction. Re-entry needs a
native nonlinear equality, declared reference measure, a theorem beyond the direct parents, and
two-system truth. Diagnostic ICLR survival was 0.5--2%, not a prospective forecast.
