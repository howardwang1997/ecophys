# Experiment 129 results — analytic AR(1) invariant gradients

**Run date:** 2026-08-09  
**Artifact:** `AR1_RESULTS.json`  
**Decision:** need for a slow-mixing estimator is supported; G0 remains AMBER

## Main result

The controlled slow-mixing regime (`a=0.97`) exposes exactly the failure relevant to EcoMD:

| Estimator | Relative bias | RMSE of Monte Carlo mean | Mean simulator steps |
|---|---:|---:|---:|
| fresh short BPTT | -56.1% | 28.03 | 24 |
| persistent state, detached tangent | -27.5% | 13.82 | 2,072 |
| full long pathwise | +3.8% | 2.73 | 2,072 |
| exact stationary-init oracle | -3.6% | 2.51 | 25 |
| finite difference + common random numbers | -3.0% | 2.45 | 4,144 |
| known Rhee--Glynn linear telescoping | +14.3% | 11.15 | 629 average |

The control estimates' residual deviations are within roughly one standard error of zero in the slow regime.
The important falsification is that merely carrying a stationary-looking state and detaching it does not recover
the derivative of the invariant measure: at horizon 24, it removes about half of the fresh-start bias but leaves
a large `-27.5%` error.

## Other regimes

At `a=0.2` and `a=0.8`, Monte Carlo variability is large relative to the small exact derivative at the frozen
2,000 replicates. Confidence intervals, rather than raw relative-bias rankings, include the analytic truth for
most correctness controls. These regimes do not justify declaring a winner.

The randomized telescoping baseline is close to unbiased in the fast regime at very low mean cost, but its
variance grows sharply as mixing slows (`replicate SD 383.1` at `a=0.97`). This is a known bias--variance--cost
tradeoff, not evidence of a new method.

## Consequences for the research plan

1. Persistent state is a simulator-semantics repair, not a sufficient invariant-gradient estimator.
2. A valid candidate must address the derivative of the stationary initial distribution or supply an equivalent
   Poisson/coupling/generator correction.
3. Slow mixing is the decisive benchmark; fast AR(1) results alone would be uninformative.
4. Any candidate must beat full-long, finite-difference CRN and Rhee--Glynn on an accuracy--cost frontier, not
   only show lower apparent bias in one run.

G0 is not passed: no candidate estimator was introduced here, and established methods remain strong controls.

