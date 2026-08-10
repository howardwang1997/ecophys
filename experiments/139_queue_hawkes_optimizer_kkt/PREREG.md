# Experiment 139 — queue--Hawkes optimizer and projected-KKT repair

**Frozen:** 2026-08-10, after the exp138 failure/KKT audit but before any candidate optimizer implementation,
candidate optimization, generated-control simulation or candidate result

**Status:** numerical baseline repair only; exp138 remains FAIL and G3 remains open

**Cost boundary:** generated controls plus the burn/training prefix of the five already tracked free LOBSTER
streams; CPU only on the two 16-core V100 hosts; CUDA hidden; no purchase, no H20 and no compute expansion

## Question and claim boundary

Can the unchanged additive loglinear-queue plus full multiscale-Hawkes likelihood be fitted to a correct
bound-constrained first-order condition under the exp138 feature scaling, and can two scientifically nested
starts reach materially equivalent training optima without using the already inspected real test partition?

A PASS repairs the numerical baseline implementation and permits it to enter a later protocol on genuinely
unseen data. It does not change exp138's frozen FAIL, confirm exp138's aligned-queue likelihood pattern, fit an
EcoMD latent, pass G3, unlock paid L2 or support a market-physics claim.

## Information inspected before freezing

The complete exp138 result is already known. It failed because 19/20 combined real symbol/policy/model cells
reported optimizer failure and the archived diagnostic used the raw gradient infinity norm. Before this freeze,
a read-only audit reconstructed only the exp138 **training** objectives at the archived fitted parameters. It
did not run a candidate optimizer, alter parameters or compute any new held-out likelihood.

For a lower-bounded excitation coefficient at zero, a positive minimization gradient satisfies the KKT sign
condition and must not contribute to the projected gradient. Replacing the raw diagnostic by the mathematically
appropriate projected residual reduced the 20 archived cell maxima from `0.245--0.644` to
`1.318e-4--1.092e-2`. This proves that the raw statistic exaggerated the residual, but every cell still exceeds
`1e-5`; exp138 therefore remains a genuine convergence failure under either diagnostic.

No candidate-repair output, new generated seed or candidate objective value has been inspected. Thresholds
below are frozen now and cannot change after a smoke or formal fit.

## Unchanged statistical model

For mark `k`, exp139 retains exactly the exp138 normalized-time intensity

`lambda_k(t) = exp(theta_k^T q_i) + sum_{j,r} alpha[k,j,r] h[j,r](t)`,

with `alpha >= 0`, six external marks, fixed `beta=(0.1,1,10)`, train-standardized queue/clock features and the
analytic event log intensity plus interval compensator. It retains both `nextafter` and `capped_uniform`, the
same vendor order/sign map, the 10% burn plus next 50% training rows, and the same aligned versus one-third
circularly shifted queue-state designs.

No likelihood term, regularizer, feature, trace scale, mark, timestamp rule, split boundary or start may change.
No real held-out likelihood, residual, branching comparison or aligned-versus-shifted test statistic is
computed in exp139.

## Projected KKT diagnostic

The objective is negative log likelihood divided by the number of training intervals. Let `g` be its analytic
gradient in the scaled coordinates used by the optimizer: seven standardized queue coefficients followed by
18 trace-scaled excitation coefficients.

- Queue coefficients are unbounded, so their projected gradient equals `g_i`.
- For excitation `alpha_i > 1e-10`, the projected gradient equals `g_i`.
- For `alpha_i <= 1e-10`, it equals `min(g_i, 0)`: a positive gradient at the lower bound is KKT-feasible.
- The projected-KKT residual is the infinity norm of this vector.

Report raw and projected norms, active-bound count, the maximum absolute complementarity product
`|alpha_i g_i|`, objective, iterations, function evaluations and termination message for every target/start/
stage. Unit tests use hand-computable boundary cases and central finite differences away from bounds.

## Frozen legacy comparator and repaired optimizer

For each target mark and queue design, reconstruct the two exp138 starts:

1. the fitted queue-reactive baseline with zero excitation;
2. the fitted full-Hawkes excitation with a constant log-baseline.

Each start first runs the exact exp138 legacy L-BFGS-B settings: `maxiter=300`, `ftol=1e-10`, `gtol=1e-6`,
`maxls=40`, default memory. The lower training objective is the legacy comparator; this is recomputed rather
than read from the exp138 artifact.

The repair then continues **each** legacy endpoint through at most six deterministic L-BFGS-B refinement
stages. Each stage uses `maxiter=500`, `ftol=1e-15`, `gtol=1e-8`, `maxls=80`, `maxcor=20` and the same bounds.
After every stage, recompute the objective, analytic gradient and projected KKT independently of SciPy's
success flag. Stop a start early only when its projected residual is at most `1e-7`. No random restart, solver
search, coefficient clipping beyond the declared bound or adaptive tolerance is allowed.

For reporting, retain every endpoint. Select the lowest-objective endpoint among those with projected residual
at most `1e-5`; if none qualifies, retain the finite lowest-objective endpoint and fail the relevant gate. A
SciPy `success=True` without the frozen projected residual is not sufficient.

## Frozen generated equivalence controls

Eight new two-mark stationary exponential-Hawkes streams use root seed `139_202_608`; they are disjoint from
exp138's root seed. The Poisson-cluster protocol remains: immigrants begin at `-1000`, events through `30000`,
retain `[0,30000]`, decay `1.3`, immigrant rates `(0.35,0.25)` and branching matrix
`[[0.22,0.08],[0.06,0.18]]`. Use the same 10/50/40 split, but score **training only**.

Fit the ordinary nonnegative full-Hawkes model and the repaired combined model with an intercept-only queue
design. These are the same intensity family under `mu=exp(theta_0)`, giving an independently parameterized
equivalence anchor. Refine the direct `(mu,alpha)` full-Hawkes reference with the same staged budget until its
bound-aware projected residual is at most `1e-8`. For both combined starts, require finite coefficients,
projected residual at most `1e-7` and absolute training-objective difference from that reference at most `1e-7`
nats/event. Report parameter and objective differences for all eight controls; parameter equality is
descriptive rather than a gate.

Each shard also runs the same small cross-node anchor from root seed `139_202_609`, with end time `5000` and
burn start `-500`. Excluding environment and runtime, its complete result must be byte-identical across nodes.

## Frozen real development prefixes

Use the same five nonduplicate archives and hashes as exp138: AAPL, AMZN, GOOG and MSFT L10 full-day samples,
plus the SPY L50 one-hour sample, totaling 2,641,557 rows in the source archives. For each stream, the formal
loader may materialize message/book rows only through the end of the 60% boundary. A timestamp-only sentinel
may be read beyond that boundary solely to finish a tie group; no held-out event type, direction, size, price,
book state or model score may be loaded.

The formal training intervals are `[floor(0.10*N), floor(0.60*N))`. Queue features for event `i` still come
only from book row `i-1`; normalization uses those training rows. The shifted control circularly shifts the
four state columns only inside the training interval by `floor(train_length/3)` and leaves intercept/clock
columns aligned.

There are 20 real cells: five symbols times two tie policies times aligned/shifted queue. Each contains six
independent target fits, for 120 target optimizations. Exp139 reports training objective and numerical
diagnostics only. Any output field containing a real `test`, `heldout`, validation likelihood or test residual
is a hard failure.

## Frozen hard gates

1. **Chronology/provenance:** exact preregistration commit, implementation SHA, archive/ReadMe hashes, model
   constants, split counts, thread settings and clean formal clones.
2. **No real-test access:** no held-out marks/books/features are loaded or scored; only an optional timestamp
   sentinel may cross the 60% boundary; output contains no real test/held-out metric.
3. **Gradient/KKT correctness:** analytic gradients pass central finite differences at frozen test points;
   projected gradients pass hand-computable lower-bound cases; recomputed objectives/gradients are finite.
4. **Generated equivalence:** all 8 controls and both starts attain projected residual `<=1e-7`, and each
   combined training objective is within `1e-7` nats/event of the equivalent full-Hawkes objective.
5. **Real selected convergence:** all 120 selected target endpoints attain projected residual `<=1e-5` and
   complementarity residual `<=1e-5`; all 20 symbol/policy/design cells therefore converge.
6. **No objective regression:** every selected target objective is no worse than the corresponding recomputed
   legacy comparator by more than `1e-10` nats/training interval.
7. **Start robustness:** both refined starts attain projected residual `<=1e-5` in at least 114/120 targets;
   among dual-qualified targets, no objective gap exceeds `1e-5` and the median gap is at most `1e-6`
   nats/training interval. Counts and every exception are reported.
8. **Cross-node determinism:** the shared generated anchor is byte-identical across the two formal shards after
   excluding only host/environment/runtime metadata.
9. **Complete unfavorable reporting:** every target/start/stage, failed termination, active count, raw/projected
   residual, objective gap and resource measurement is retained; missing cells or post-hoc exclusions fail.

All nine gates are required. The real thresholds are numerical conditions on an already exposed training
prefix, not empirical evidence thresholds.

## Execution and merge

- Formal execution uses two CPU-only shards, one process and one BLAS thread each, with CUDA hidden.
- Shard 0 owns GOOG/SPY and generated replicates 0/2/4/6; shard 1 owns AAPL/AMZN/MSFT and replicates 1/3/5/7.
- Both shards run the shared cross-node anchor. Node identity cannot change seeds, model or numerical settings.
- Formal work requires a clean exact implementation commit descended from this preregistration commit. The
  merger rejects wrong ownership, protocol/SHA/hash mismatches, dirty trees, CUDA visibility or missing cells.
- Expected upper bound is 50 CPU core-hours and 12 GiB RAM per worker. Smoke uses at most 20,000 source rows,
  shorter generated windows and separate artifacts; it may inspect execution/KKT diagnostics but cannot alter
  any formal setting or threshold.

## Interpretation and next gate

A PASS means the combined baseline has a defensible training optimum and correct bound-aware diagnostics. The
positive exp138 real-test pattern remains exploratory because it was already seen before this repair. The next
empirical test must use unseen dates or markets under a new protocol. A FAIL preserves exp138's numerical
blocker; another solver family would require a new preregistration and independent generated validation seeds.
In either case, G3 and paid L2 remain locked until a frozen EcoMD-to-message map and independent real test exist.
