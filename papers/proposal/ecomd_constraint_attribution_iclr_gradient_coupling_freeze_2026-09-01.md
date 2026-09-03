# Gradient-coupling mechanism audit freeze

Frozen 2026-09-01 NZST while the fresh-seed PDEBench Advection factorial worker was still
running and before any seed-3000--3029 metric was inspected or its one-shot analyzer was run.
The audit is motivated by the already observed parent block and by the channel-separable training
null, not by the still-hidden factorial interaction. It is a mechanism diagnostic, not an extra
benchmark, a replacement primary outcome, or a route for rescuing an unfavorable factorial result.

## Scientific question

For a linear invariant, a free squared-error loss decomposes exactly into conserving and
invariant-violating terms, `L = L_Q + L_P`. Hard projection deletes the gradient of `L_P` but
cannot directly change the conserving prediction at fixed parameters. With shared parameters,
however, the two gradients can interact during optimization. Under a plain gradient-descent step
of size `eta`,

`L_Q(theta - eta*(g_Q + g_P)) - L_Q(theta - eta*g_Q)
 = -eta*<g_Q,g_P> + O(eta^2)`.

Thus negative gradient alignment predicts an immediate conserving-channel benefit from removing
the violating loss, while positive alignment predicts the opposite. Absolute and residual output
coordinates can change `g_P`, so their difference is a concrete local mechanism for the frozen
factorial interaction.

## Frozen diagnostic

Run the audit for every formal seed of each admitted public factorial block:

- Advection beta=0.4: seeds 3000--3029;
- Burgers nu=0.01: seeds 4000--4029, if and only if its already frozen public-data gate passes.

For each seed and each coordinate system `A` (absolute) and `R` (residual):

1. Reconstruct the exact formal training-trajectory subset, epoch-zero window offsets,
   epoch-zero minibatch permutation, and first minibatch of 50 examples.
2. Reconstruct the exact FNO initialization used by all four factorial cells.
3. Compute `L_Q` as the mean squared centered error and `L_P` as the mean squared spatial-mean
   error. Require `L_Q + L_P` to equal the full MSE within `1e-6` relative error.
4. Record the full-parameter gradient norms, inner product, and cosine for `g_Q` and `g_P`.
5. From identical initialized tensors, execute exactly one Adam step with the frozen optimizer
   settings for (a) free full-MSE training and (b) hard-projected training. Evaluate both
   post-step conserving losses on the same first minibatch.

Define the positive one-step enforcement credit

`D_s = L_Q(theta_free^+) - L_Q(theta_hard^+)`, for `s` in `{A,R}`,

and its coordinate interaction `D_I = D_A - D_R`. Positive `D_s` means that removing the
violating-channel gradient gives lower same-batch conserving loss after the exact first Adam step.
This is deliberately a local diagnostic; it is not forecast RMSE and may not predict 200-epoch
rollout behavior.

## Frozen link to the formal factorial

The diagnostic output may be summarized immediately because it contains no held-out rollout
metric. It may be joined to a public factorial result only after that block independently reaches
150/150 records and passes its one-shot analyzer.

For each seed, define the final primary-cell interaction

`I_seed = (Y_A0 - Y_A1) - (Y_R0 - Y_R1)`

using OOD-512 horizon-16 conserving RMSE. The primary mechanistic association is Spearman's
correlation between `D_I` and `I_seed`; its 95% interval uses 50,000 paired seed-bootstrap draws.
Also report the means and 95% paired-bootstrap intervals of `D_A`, `D_R`, and `D_I`, plus the
gradient cosines, regardless of sign. No multiplicity-adjusted or alternative correlation may
replace the frozen primary association.

Interpretation is fixed:

- a positive correlation whose 95% interval excludes zero supports the claim that early
  coordinate-dependent optimizer coupling predicts part of the final interaction;
- otherwise the local gradient audit does not explain the final interaction, even if its mean
  sign happens to agree;
- a null, negative, or unresolved association must be reported and cannot be reframed as evidence
  of robustness;
- neither outcome identifies a unique long-run mechanism, because Adam state and nonlinear
  training can alter coupling after the first minibatch.

Advection and Burgers are analyzed separately. Their seeds are inference units, and no trajectory,
grid point, or gradient coordinate is treated as an independent replicate.

## Integrity and stopping rules

- The diagnostic must bind the exact data lock, scientific protocol, source snapshot, training
  configuration, dataset hash, initialization hash, training-index hash, first-minibatch row hash,
  and output-coordinate label.
- Each admitted benchmark must contain exactly 60 unique records (30 seeds times two coordinates).
- Absolute and residual records within a seed must have identical initialized tensor hashes,
  selected trajectories, window offsets, and minibatch order.
- All losses, norms, inner products, cosines, and one-step values must be finite. A zero gradient
  norm fails closed rather than assigning an arbitrary cosine.
- The audit cannot change a model run, seed, optimizer, grid, endpoint, threshold, or factorial
  decision. It cannot inspect partial factorial metrics or trigger result-driven stopping/tuning.
- Any implementation error is fixed only through a recorded runtime amendment before diagnostic
  outputs are analyzed; existing artifacts are preserved.
