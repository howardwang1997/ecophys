# Experiment 138 — external continuous-time queue/Hawkes baseline gate

**Formal result:** **FAIL (8/9 hard gates passed)**

**Frozen protocol:** `e4fa739b` on 2026-08-10, before implementation, synthetic simulation, queue-feature
construction or target likelihood inspection

**Formal implementation:** `09ded22691196f1786f83fa712c7db9d2cbbc0f6`

**Protocol hash:** `c47577f0afa698e5fd9fd9f3dd7db8e281f6c839a0977c2139dc073b9f9e5b01`

## Decision

The external timestamp/sign parser, exact continuous-time likelihood, generated Hawkes control, causal split,
model nesting, shifted-queue control and tie-policy sensitivity all passed their frozen gates. The experiment
nevertheless fails because the real-data combined queue--Hawkes optimizer did not meet the frozen convergence
criterion. Nineteen of the twenty combined model cells reported optimizer failure: all 10 aligned cells and
9/10 shifted cells. Their final reported infinity-norm gradients were `0.245--0.644`, far above the allowed
`1e-5` fallback.

The positive aligned-versus-shifted likelihood pattern is therefore a diagnostic signal, not confirmatory
evidence. Exp138 cannot be relabeled PASS by increasing the iteration cap or relaxing the gradient threshold.
Any optimizer repair is a new experiment and cannot turn the already inspected test split into an independent
confirmation set.

## Hard gates

| Frozen gate | Result | Evidence |
|---|---:|---|
| Manifest and provenance exact | PASS | Five canonical archives, ReadMe and all hashes matched; 2,641,557 rows |
| Timestamps and external marks exact | PASS | Raw time nondecreasing; two policies strictly increasing; every type-1--5 row mapped once |
| Split and no-lookahead exact | PASS | 10/50/40 row split; event `i` used book row `i-1`; train-only scaling |
| Generated Hawkes recovery | PASS | 8/8 finite converged controls; all frozen recovery and residual thresholds passed |
| Real fits finite and converged | **FAIL** | All values finite, but 19/20 combined cells failed convergence and exceeded `1e-5` |
| Training nesting | PASS | All frozen train-likelihood nesting comparisons held within tolerance |
| Aligned queue control | PASS | Cross-symbol median aligned-minus-shifted was positive under both tie policies |
| Tie-policy robustness | PASS | Median combined-minus-Hawkes sign agreed; difference was below 0.002 nats/event |
| Complete unfavorable reporting | PASS | All symbols, models, radii, residuals and negative results remain in the artifact |

All nine gates were required, so the formal experiment is FAIL.

## Data and timestamp audit

The five nonduplicated free LOBSTER sample streams contain one day per equity and one hour for SPY. They are
external market messages, but they are not independent days, exchanges or a confirmatory market panel.

| Symbol | Depth/window | Events | Equal-time increments | Largest tie group |
|---|---|---:|---:|---:|
| AAPL | L10, full day | 400,391 | 16,062 (4.012%) | 43 |
| AMZN | L10, full day | 269,748 | 8,483 (3.145%) | 31 |
| GOOG | L10, full day | 147,916 | 8,537 (5.772%) | 35 |
| MSFT | L10, full day | 668,765 | 57,203 (8.554%) | 97 |
| SPY | L50, one hour | 1,154,737 | 123,250 (10.673%) | 121 |

Every stream had zero negative raw-time increments. The smallest positive raw interval ranged from
`1.67e-7` to `3.03e-7` seconds. `nextafter` and `capped_uniform` preserved row order, crossed no next distinct
timestamp and produced strictly positive intervals. The vendor ReadMe externally anchors buy/sell limit sides
and the opposite aggressor side for executions; it does not anchor an EcoMD latent coordinate.

## Generated control

Eight stationary two-mark Hawkes controls contained at least 24,608 retained events each, and all eight fits
converged.

| Diagnostic | Formal result | Frozen requirement |
|---|---:|---:|
| Immigrant-rate median relative error | 2.66%, 1.66% | each <=15% |
| Branching-entry median relative error | 2.06%--7.35% | each nonzero entry <=25% |
| Hawkes-minus-Poisson held-out gain | 0.04492 nats/event | >=0.005 |
| Rescaling mean, median | 1.0084 | 0.90--1.10 |
| Rescaling KS, median | 0.01074 | <=0.05 |
| Absolute rescaling lag-1, median | 0.00723 | <=0.05 |

This validates the simulator, trace, compensator, likelihood and gradient plumbing for a correctly specified
low-dimensional Hawkes process. It does not validate the market specification.

## External held-out diagnostics

All values below are held-out nats per event. `Aligned-shifted` compares the same combined model with only the
four queue-state features displaced. `Combined-Hawkes` compares aligned queue--Hawkes with full multiscale
Hawkes.

| Symbol | Aligned-shifted, nextafter | Aligned-shifted, capped | Combined-Hawkes, nextafter | Combined-Hawkes, capped |
|---|---:|---:|---:|---:|
| AAPL | +0.003731 | +0.003913 | +0.003868 | +0.003841 |
| AMZN | +0.002773 | +0.002709 | +0.001098 | +0.001161 |
| GOOG | +0.010376 | +0.010845 | +0.004889 | +0.004989 |
| MSFT | +0.000507 | +0.000463 | +0.000006 | +0.000013 |
| SPY | +0.008221 | +0.011970 | **-0.027097** | **-0.029428** |
| **Cross-symbol median** | **+0.003731** | **+0.003913** | **+0.001098** | **+0.001161** |

The aligned-minus-shifted sign is positive for all five symbols under both policies. The combined-minus-Hawkes
median has the same positive sign under both policies, and the median difference is `6.27e-5` nats/event.
However, SPY favors full Hawkes by about `0.027--0.029` nats/event, and the combined fits are not converged.

Other unfavorable diagnostics are also retained. The queue-reactive model by itself loses to Poisson on AMZN
(`-0.0189`) and SPY (`-0.7032`) while full Hawkes beats Poisson on every stream (`+2.318` to `+4.107`). Under
the primary policy, full-Hawkes held-out rescaling KS statistics remain `0.164--0.355`, means are
`0.997--1.083`, and lag-1 correlations range from `-0.047` to `+0.172`. The history model is therefore far
better in likelihood than Poisson but is not a calibrated generative description of these samples.

## Optimizer failure

The Poisson, queue-reactive, diagonal-Hawkes and full-Hawkes cells all reported success. For the combined
models, the frozen per-mark L-BFGS-B cap was 300 iterations. The aligned model failed in 10/10 symbol-policy
cells and the shifted model failed in 9/10; only `AAPL/nextafter/shifted` reported success. Multiple marks in
most failed cells reached the iteration limit. Finiteness and training nesting passed, so this is not a parser
or arithmetic crash, but the remaining gradients are too large to regard the fitted optima as established.

A legitimate repair should be developed using generated controls and training-only/free development streams,
with projected-gradient/KKT diagnostics and an optimizer comparison frozen before evaluation. The exp138 test
likelihoods must remain archival diagnostics. Independent real confirmation requires unseen days or markets.

## Compute and reproducibility

- Shard 0: GOOG, SPY and generated replicates 0/2/4/6; one CPU process on V100-A; about 9.0 CPU min.
- Shard 1: AAPL, AMZN, MSFT and generated replicates 1/3/5/7; one CPU process on V100-B; about 7.2 CPU min.
- Both formal clones were clean at `09ded226`; Python 3.11.15, NumPy 2.4.6, pandas 3.0.5 and SciPy 1.17.1.
- `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`, `CUDA_VISIBLE_DEVICES=-1`; both V100s stayed unused.
- Merged worker time: 964.02 seconds.
- Shard 0 SHA-256: `3c28a6801deb8df1b22d2e8f3b8005ecda0db9056674e393109c160667172f5e`.
- Shard 1 SHA-256: `624ffd915920dda314f43ffc30d0d379bf9bbf14198da32e6940bb43da443c6d`.
- Merged SHA-256: `0e25df8c6fa30992cf0ec69c55db787c09e3a34958aa1fe196d4eb85b02fecf2`.
- A second merge to a temporary path was byte-identical to the archived merged artifact.

## Claim boundary and next gate

Exp138 is an external baseline/evaluator preflight. It contains no EcoMD latent, fits no EcoMD checkpoint and
does not establish market physics, model-to-real causality or G3. Because the frozen experiment failed, paid
L2 remains locked. The immediate zero-cost follow-up is a separately preregistered optimizer/KKT repair using
only generated and development/training data. A future G3 claim still needs a frozen EcoMD-to-message map,
independent days/markets, individual-order or explicitly limited aggregate semantics, and an observation-only
comparison on a genuinely unseen test set.
