# Experiment 152 — exact multi-stationary drift identity and obstruction suite

**Frozen:** 2026-08-13  
**Branch:** `multi-stationary-drift-tomography-audit-v11`  
**Parent plan commit:** `df75a5c0166bbb7e933bdb0692a536cd8680c983`  
**Scientific role:** deterministic algebra and counterexamples only; cannot pass novelty, admit a paper candidate or
unlock generated/real data or GPU work

## 1. Questions

Experiment 152 checks six exact implications of the V11 population identity before any estimator is built:

1. Does the sign and diffusion convention recover a one-dimensional Ornstein--Uhlenbeck drift?
2. Do spanning stationary-score shifts recover the rotational component of a nonreversible two-dimensional drift?
3. Can rank-deficient score shifts leave two distinct common drifts exactly observationally equivalent?
4. Can a quantitatively nonzero intervention leave the stationary density, and hence all score excitation, unchanged?
5. Does incorrectly imposing common diffusion produce deterministic drift bias even with exact densities?
6. Is score-difference rank coordinate invariant while raw singular-value conditioning and an uncorrected vector
   transformation of Itô drift are not?

Every fixture is analytic and fixed below. There are no random samples, integration paths, optimizers, fitted
scores or parameter sweeps.

## 2. Shared convention

For

\[
dX_t=\{b(X_t)+u_m(X_t)\}\,dt+\sqrt{2\kappa_m}\,dW_t,
\]

the stationary density satisfies

\[
0=-\nabla\!\cdot\{(b+u_m)\rho_m\}+\kappa_m\Delta\rho_m.
\]

When a common `kappa` is valid, define

\[
s_m=\nabla\log\rho_m,\qquad
g_m=\kappa(\nabla\!\cdot s_m+\lVert s_m\rVert^2)
-\nabla\!\cdot u_m-u_m^\top s_m.
\]

The checked identity is `b^T(s_m-s_0)=g_m-g_0`. Float64 absolute tolerance is `1e-12`.

## 3. Frozen fixtures and expected values

### W1 — one-dimensional sign check

Set `kappa=0.5`, `b(x)=-2x`, `u_0=0`, `u_1=1`. The two invariant laws are Gaussian with variance `0.25` and
means `0` and `0.5`. Thus `s_1-s_0=2`, `g_1-g_0=-4x`, and inversion must recover `-2x` at
`x in {-1,0,1}`. Expected maximum identity and reconstruction errors: `<=1e-12`.

### W2 — nonreversible OU recovery

Set `kappa=1`,

\[
B=\begin{bmatrix}1&-2\\2&1\end{bmatrix},\qquad b(x)=-Bx.
\]

The common invariant covariance is `I`. Choose invariant means `mu_0=0`, `mu_1=e_1`, `mu_2=e_2`, which fixes
the known constant interventions `c_m=B mu_m`. The score-difference matrix is exactly `S=I`, so it must recover
the full drift, including its antisymmetric rotational component, at the three points in `config.yaml`. Expected
rank: `2`; expected minimum singular value: `1`; maximum reconstruction error: `<=1e-12`.

### W3 — exact rank-deficient alias on the two-torus

On `T^2`, set `kappa=1`,

\[
\rho_m(x)\propto \exp(a_m\cos x_1),\qquad
u_m=(-a_m\sin x_1,0),\qquad a_m\in\{0,1,2\}.
\]

Both common drifts `b^(0)=(0,0)` and `b^(1)=(0,1)` leave every `rho_m` stationary under the same known
interventions. At `x_1=pi/2`, the score-difference matrix has rank `1`, while the two drift fields are separated by
Euclidean norm `1`. Expected maximum analytic stationary-PDE residual for both drifts and all environments:
`<=1e-12`.

### W4 — stationary-density-invisible intervention

For `rho=N(0,I)`, `b(x)=-x`, and

\[
u(x)=3Jx,\qquad J=\begin{bmatrix}0&-1\\1&0\end{bmatrix},
\]

`div u+u^T grad log rho=0`. Baseline and intervened densities are identical even though
`||u(1,2)||=sqrt(45)`. Expected score-difference rank: `0`; weighted-divergence residual: `<=1e-12`.

### W5 — diffusion misspecification

In one dimension let `b(x)=-x`, `u_0=0`, `u_1=1`, but use true diffusion coefficients `kappa_0=1` and
`kappa_1=2`. The invariant laws are `N(0,1)` and `N(1,2)`. Correct environment-specific diffusion terms recover
`b` at `x in {0,1,2}`. Incorrectly using `kappa=1` for both yields

\[
\widehat b_{wrong}(x)=\frac{1-3x^2}{2(x+1)},
\]

and values `(0.5,-0.5,-11/6)`. Expected correct maximum error: `<=1e-12`; expected wrong maximum absolute error:
`0.5` within tolerance.

### W6 — coordinate covariance and non-invariant raw conditioning

For `S_x=I`, the affine unit change `y=Lx`, `L=diag(10,1)`, gives
`S_y=S_x L^{-1}=diag(0.1,1)`. Both ranks equal `2`, but the raw minimum singular value changes from `1` to `0.1`
and the condition number from `1` to `10`.

For the nonlinear diffeomorphism `phi(x)=(x_1+x_1^3,x_2)`, at `x=(1,0)` the Jacobian is `diag(4,1)` and
`Delta phi=(6,0)`. With `kappa=1`, transformed Itô drift is

\[
b_y=J_\phi b_x+\Delta\phi,
\]

not the vector-only expression `J_phi b_x`. Expected correction norm: `6`. Score differences must obey
`delta s_y=J_phi^{-T} delta s_x` and retain rank `2`.

## 4. Frozen decision rule

| Condition | Decision | Interpretation |
|---|---|---|
| W1--W6 all match | `IDENTITY_AND_OBSTRUCTIONS_CONFIRMED` | The elementary identity works under its assumptions, and the exact scope/stability obstructions are real. |
| Any fixture fails | `IMPLEMENTATION_OR_SPEC_FAILURE` | Diagnose formula or implementation; do not reinterpret a mismatch as scientific evidence. |

There is no scientific `PASS` state. Even a complete match sets `candidate_admission=false`, `novelty_pass=false`
and `compute_unlock=false`. V11 survives only if the separate equation-level audit finds a nonstandard stable
estimator or theorem; Experiment 152 cannot establish that.

## 5. Implementation and immutable-run contract

- The implementation is written only after this preregistration is committed and pushed.
- Planned runner: `experiments/152_multi_stationary_drift_tomography/run_exact_audit.py`.
- Planned reusable module: `ecomd/research/stationary_drift_tomography.py`.
- Planned focused tests: `tests/test_stationary_drift_tomography.py`.
- Planned raw output: `experiments/152_multi_stationary_drift_tomography/artifacts/raw/exact_audit.json`.
- A later `FREEZE.yaml` must pin the implementation commit and SHA-256 of config, runner, module and focused test.
- The formal runner must refuse a dirty checkout, a non-descendant implementation SHA and artifact overwrite.
- The formal suite runs once. Any repair requires a new experiment number; Experiment 152 is never overwritten.

## 6. Resource and data boundary

- Inputs: constants and analytic fields in `config.yaml` only.
- Data: no generated sample, market, human, vendor, R2, sealed-period or historical outcome file.
- Network: forbidden during the formal run.
- Compute: Mac CPU, one process, expected under one second; zero GPU-hours.
- V100-A, V100-B and RTX2060 are not contacted or queued.

