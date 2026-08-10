# Experiment 140 — independent active-set Newton reference gate

**Frozen:** 2026-08-10, after the complete exp139 result and an explicitly disclosed development-only Newton
prototype, but before any formal seed is generated, any formal candidate implementation is committed or any
formal result is inspected

**Status:** generated numerical reference repair only; exp138 and exp139 remain FAIL and G3 remains open

**Cost boundary:** generated event streams only; CPU-only on the two existing V100 hosts with CUDA hidden; no
real dataset, purchase, H20 or compute expansion

## Question and claim boundary

Can a separately specified analytic-Hessian active-set Newton polish solve the convex direct-Hawkes reference
problem to a first-order condition substantially stricter than exp139's failed reference gate, from two fixed
starts and on fresh generated streams, while preserving the exact algebraic identity with the intercept-only
combined likelihood?

A PASS closes only the direct-reference numerical sub-blocker exposed by exp139. Together with exp139's passed
real training-prefix convergence gate, it permits the repaired baseline to enter a future protocol on genuinely
unseen dates or markets. It does not relabel exp138 or exp139, confirm their exposed real likelihood pattern,
fit an EcoMD latent, pass G0/G3, unlock paid L2 or support a market-physics claim.

## Information inspected before freezing

The full exp139 result is known. Exp139 formally failed 8/9 gates because two of 16 direct-Hawkes references
stopped at projected residuals `1.6248e-8` and `2.0216e-8`, above the separately frozen `1e-8` reference
threshold. All 32 equivalent combined starts reached `<=1e-7` and matched the direct objectives within
`1.7875e-14` nats/event. All 120 real selected targets and all 240 real starts reached `<=1e-5`; no real
held-out metric was evaluated.

A temporary, untracked development prototype reconstructed only exp139's eight already exposed generated
streams and initialized from their archived direct-reference endpoints. One analytic-Hessian Newton step drove
all 16 projected residuals to at most `4.3877e-15`; absolute objective changes were at most `1.3323e-15`.
Hessian condition numbers were `6.82--7.68`. No seed descended from the formal root below has been generated,
and no real data were loaded. The entire exp139 generated set is now development evidence and cannot enter any
exp140 hard gate.

## Frozen generated process and split

Generate 16 new two-mark stationary exponential-Hawkes streams from root seed `140202608` using
`numpy.random.SeedSequence(root).spawn(16)` and one `uint64` state per replicate. Use the same scientifically
relevant process family as the failed reference:

- immigrants begin at `-1000` and events are retained on `[0,30000]`;
- decay `beta=1.3`;
- immigrant rates `(0.35,0.25)`;
- branching matrix `[[0.22,0.08],[0.06,0.18]]`;
- chronological 10/50/40 split, with optimization and every metric restricted to the middle 50% training
  interval.

The event simulator, trace/compensator construction and training boundaries remain those validated in exp138/
exp139. Root seeds `139202608`, `139202609` and `139202610`, their descendants and all archived exp139 streams
are forbidden. No real LOBSTER archive may be opened by the formal runner.

## Convex objective, derivatives and bounds

For one target mark, let `Z=[1,F]` be the event design after the same train-only trace scaling and let
`c=(duration, integrated_F)`. In direct physical coordinates `x=(mu,alpha)`, minimize

`f(x) = [-sum_i log(Z_i x) + c^T x] / n`

under `mu>=1e-12` and `alpha>=0`. Use the analytic derivatives

`g(x) = [-Z^T(1/(Zx)) + c] / n`,

`H(x) = [Z^T diag(1/(Zx)^2) Z] / n`.

The lower-bound projected gradient uses exp139's sign convention with active tolerance `1e-12`: an interior
coordinate retains `g_i`; a coordinate at its lower bound retains `min(g_i,0)`. Report its infinity norm, raw
gradient norm, maximum complementarity product, active count, Hessian condition number and minimum eigenvalue.

At fixed preregistered interior points, central finite differences with step `1e-6` must match the analytic
gradient within `5e-7`; central differences of the analytic gradient with step `1e-6` must match the Hessian
within `5e-7`. The Hessian symmetry error must be `<=1e-14`. Fixed hand-computable lower-bound projected cases
must match within `1e-15`.

## Frozen starts and hybrid solver

Each target uses two deterministic starts in the scaled direct coordinates:

1. **rate-zero:** `mu = n_target/duration`, every excitation coefficient zero;
2. **positive:** `mu = 0.5*n_target/duration`, every scaled excitation coefficient `0.05`.

Each start first receives one L-BFGS-B warm stage with `maxiter=1000`, `ftol=1e-15`, `gtol=1e-9`, `maxls=100`
and `maxcor=20`. SciPy's success flag is diagnostic only. The endpoint then receives at most eight active-set
Newton iterations:

1. mark a coordinate active when it is within `1e-12` of its lower bound and has positive gradient;
2. solve `H_FF p_F=-g_F` with `numpy.linalg.solve`, with `p_A=0`;
3. if a free coordinate at its bound has `p_i<0`, add it to the active set and resolve until the direction is
   feasible at every bound;
4. require a finite strict-descent direction; no ridge, pseudo-inverse, quasi-Newton or random fallback is
   permitted;
5. take the largest bound-feasible step at most one, clipping only floating-point boundary undershoot, and
   apply Armijo backtracking with constant `1e-4` and factor `0.5` for at most 60 trials;
6. stop early only when the independently recomputed projected residual is `<=1e-11`.

A singular solve, non-descent direction, failed line search, nonfinite value or nonpositive event intensity is
reported and fails that endpoint. Select the lowest-objective endpoint with projected residual and
complementarity both `<=1e-10`; if neither qualifies, retain the finite lower-objective endpoint and fail.
Every warm and Newton endpoint is retained.

## Algebraic parameterization check

For every selected direct solution, construct the intercept-only combined coordinates exactly as
`theta_0=log(mu)` with the same scaled excitation coefficients. Re-evaluate both objectives and gradients from
their independent implementations on the same training interval. Require:

- absolute objective difference `<=1e-12` nats/event;
- `|g_theta - mu*g_mu|<=1e-12` and excitation-gradient difference `<=1e-12`;
- physical parameters recovered by the inverse transform agree within `1e-14`.

This is an implementation identity check, not a second optimizer or empirical model comparison. Projected
gradient norms in `mu` and `theta` coordinates are not required to be equal because raw first-order residuals
are parameterization-scaled.

## Frozen hard gates

1. **Chronology/provenance:** exact preregistration and implementation commits, clean formal clones, frozen
   constants, seed ownership, thread settings and dependency versions.
2. **Isolation:** exactly 16 fresh formal streams; no exp139 seed/record and no real archive, feature or metric
   is loaded.
3. **Derivative/KKT correctness:** all gradient, Hessian, symmetry and hand-bound self-check thresholds pass;
   all recomputed quantities are finite.
4. **Newton convergence:** all 32 targets from both starts, 64 endpoints total, have projected residual and
   complementarity `<=1e-10` after polish.
5. **Monotone repair:** no polished endpoint exceeds its own warm endpoint by more than `1e-13` nats/event;
   every accepted Newton step satisfies the frozen Armijo condition.
6. **Start robustness:** all 32 dual-qualified target pairs have objective gap `<=1e-11` nats/event; the median
   gap is `<=1e-12`.
7. **Algebraic equivalence:** every direct/combined objective, gradient-chain-rule and inverse-parameter check
   meets the frozen tolerances above.
8. **Cross-node determinism:** a shared generated anchor from root seed `140202609`, with burn start `-500` and
   end time `5000`, is byte-identical after excluding only environment and runtime metadata.
9. **Complete unfavorable reporting:** all streams, targets, starts, warm endpoints, Newton iterations,
   termination reasons, line-search trials, residuals, eigen/condition diagnostics and resources are present;
   missing or post-hoc excluded records fail.

All nine gates are required. Thresholds cannot change after smoke or formal execution. A failed formal stream
cannot be replaced by another seed.

## Execution and merge

- A separate smoke root `140202610` uses two shorter `[0,3000]` streams after implementation; smoke evidence
  may find code defects but cannot alter formal settings or thresholds.
- Formal shard 0 owns even replicates and shard 1 odd replicates. Each uses one CPU process, one BLAS thread and
  `CUDA_VISIBLE_DEVICES=-1` on the existing V100 hosts; the GPUs must remain unused.
- Each shard runs the shared anchor. The merger rejects wrong seed ownership, protocol/SHA mismatch, dirty
  trees, nonhidden CUDA, missing records or unequal anchors.
- Expected total is below two CPU core-hours and 4 GiB RAM per shard. Runtime and peak RSS are reported.

## Interpretation and stopping rule

A PASS records an independently validated convex reference solver and closes exp139's narrow numerical
reference blocker without changing either prior decision. The next observation experiment must use genuinely
unseen dates or markets and a frozen EcoMD-to-message map.

A FAIL is retained as a numerical failure. Do not relax `1e-10` around the observed residual or recycle a
failed formal seed. A third optimizer chase is justified only by a diagnosed mathematical defect; otherwise
drop this reference route and keep G3 closed. In all outcomes, G0 novelty remains the higher-priority NCS gate.
