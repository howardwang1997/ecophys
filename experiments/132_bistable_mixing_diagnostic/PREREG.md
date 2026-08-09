# Experiment 132 — fail-visible diagnostic in a bistable Langevin system

**Frozen:** 2026-08-10, before any result from this experiment  
**Status:** diagnostic feasibility audit; no candidate estimator and no novelty claim  
**Cost boundary:** Mac CPU only, synthetic draws only, no purchased data

## Question

Can a simple, explicitly fail-visible diagnostic reject an apparently stable gradient when independent chain
groups remain trapped in opposite wells? This tests a necessary behavior for the G0 candidate; it is not itself
a new gradient method.

## Frozen system and truth

Use overdamped Langevin Euler--Maruyama dynamics in

`U_theta(x) = x^4/4 - x^2/2 - theta x`,

so

`x_(t+1) = x_t + dt(-x_t^3 + x_t + theta) + sqrt(2 T dt) epsilon_t`.

- `theta=0.05`, `dt=0.005`;
- temperatures `T in {0.50, 0.15, 0.04}` for easy, medium and hard mixing;
- 64 batches, each containing 64 chains initialized equally at `x=-1` and `x=+1`;
- 4,096 steps, first 1,024 discarded, sample stride 8;
- smooth observable `f(x)=tanh(3x)` and mode indicator `1{x>0}`.

The reference stationary density is evaluated independently on a fixed dense grid over `[-4,4]`:

`pi_theta(x) proportional to exp(-U_theta(x)/T)`,

with exact sensitivity identity

`d E_pi[f] / d theta = Cov_pi(f(x), x) / T`.

Grid boundary mass must be below `1e-10`; otherwise the run hard fails.

## Frozen gradient controls

- fresh 24-step pathwise derivative from `x_0=0`;
- persistent-detached 24-step derivative after a 2,048-step burn, with tangent reset to zero;
- full 4,096-step tangent derivative averaged over post-burn samples;
- stationary quadrature truth.

The tangent recursion is the exact derivative of the Euler update. No result from this experiment may be called
an unbiased invariant-gradient estimator.

## Frozen diagnostic

For every batch, compute:

1. absolute difference in post-burn right-well occupancy between chains initialized left and right;
2. absolute occupancy difference between the first and second halves of the retained window;
3. total number of sign changes across the 64 chains;
4. a conservative lag-1 binary-mode effective-sample-size approximation, with constant chains assigned zero.

Return `resolved` only when all hold:

- initialization-group occupancy difference `<=0.10`;
- retained-half occupancy difference `<=0.10`;
- at least 64 total sign changes;
- approximate mode ESS `>=128`.

Gradient accuracy is defined before inspection as correct sign and absolute relative error `<=25%`.

## Hard gates

- Hard regime false-safe rate (`resolved` but inaccurate) must be below 5%.
- Easy regime resolved rate must be at least 80%; otherwise the diagnostic is too conservative to be useful.
- Among resolved easy batches, median absolute relative error must be at most 25%.
- If persistent-detached estimates look low variance while their chain groups remain separated, the result is a
  failure of that estimator and a success only for the diagnostic if it rejects them.
- Medium/hard resolved rates and gradient errors are descriptive; thresholds cannot be revised after viewing.
- Passing supports only the feasibility of fail-visible rejection. G0 remains AMBER until a candidate estimator
  also improves the frozen accuracy--cost frontier.

