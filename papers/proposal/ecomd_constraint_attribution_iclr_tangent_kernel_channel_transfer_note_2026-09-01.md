# Tangent-kernel channel-transfer theory note

Recorded 2026-09-01 NZST before completion or analysis of the fresh-seed Advection factorial,
before activation of the gradient-coupling diagnostic, and before Burgers data admission or any
Burgers model run. This note changes no frozen experimental factor, record, endpoint, hypothesis,
threshold, or analyzer.

For a stacked minibatch prediction `h_theta`, error `e`, parameter Jacobian `J`, and blockwise
orthogonal invariant projectors `Pbar` and `Qbar`, define the finite-width empirical tangent kernel
`K = J J^T`. With half-squared channel losses,

`g_Q = J^T Qbar e` and `g_P = J^T Pbar e`.

Starting from identical parameters, a free gradient step and a hard gradient step differ by
`-eta g_P`. Under the predictor linearization at those parameters, their conserving-output
difference is therefore exactly

`-eta Qbar K Pbar e`.

Moreover,

`<g_Q, g_P> = (Qbar e)^T K (Pbar e)`.

Consequently, `Qbar K Pbar = 0` if and only if the violating-channel gradient has no first-order
effect on conserving predictions for every violating residual. This is a local functional-space
form of the previously stated channel-separable training null. The measured gradient dot product
is one residual-weighted bilinear slice of this off-diagonal block; the exact matched Adam step is
retained because the formal optimizer is Adam and the finite network is nonlinear.

A 2026-09-01 primary-source search found extensive generic NTK analysis and NTK analyses of PINN
loss imbalance, but no exact conservation-channel attribution claim sufficient to justify a
priority statement. The manuscript therefore cites the original NTK work and presents this as a
specific identity used by the audit, not as the first use of tangent kernels in physics learning.

The identities were independently checked on three random finite-dimensional Jacobian/projector
instances. Maximum absolute discrepancies were between `2.2e-16` and `1.5e-15` for the output
identity and between `0` and `2.5e-14` for the gradient-bilinear identity.
