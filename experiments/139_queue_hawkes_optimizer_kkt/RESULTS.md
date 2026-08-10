# Experiment 139 — queue--Hawkes optimizer and projected-KKT repair

**Formal result:** **FAIL (8/9 hard gates passed)**

**Frozen protocol:** `338e0165` plus finite-difference clarification `732e1e7b`, both before candidate
implementation, candidate optimization or generated-control simulation

**Formal implementation:** `e6a7eaafb61f272c8e6711947e1a7da9f427cc03`

**Protocol hash:** `870a3360fbc3c64ba4bc54bc98bbda5fe4ddf88305349881fc8110f8c2c4475f`

## Decision

The projected-KKT repair succeeds on its real-data numerical target: all 120 selected target fits and both
starts meet the frozen `1e-5` selection criterion, every selected objective improves on the recomputed legacy
comparator, and the two starts reach materially identical training objectives. The experiment nevertheless
fails because two of the 16 independently parameterized direct-Hawkes reference fits in the generated controls
stop just above their stricter `1e-8` reference threshold, at `1.625e-8` and `2.022e-8`.

All 32 corresponding combined-model starts meet `1e-7`, and their maximum objective discrepancy from the
direct reference is only `1.79e-14` nats/event. This strongly localizes the failure to the direct-reference
optimizer at a deliberately strict numerical tolerance; it does not permit the frozen gate to be relabeled
PASS. Exp138 remains FAIL, and its already inspected real test likelihoods remain exploratory.

## Hard gates

| Frozen gate | Result | Evidence |
|---|---:|---|
| Chronology and provenance exact | PASS | Both clean shards used the frozen commits, hashes, constants, ownership and one-thread environment |
| No real-test access | PASS | Only 1,584,932 burn/training-prefix rows were materialized; no real test/held-out value was loaded or scored |
| Gradient and KKT correct | PASS | Finite-difference maximum error `3.19e-11`; hand-bound error exactly `0` on both nodes |
| Generated equivalence | **FAIL** | 14/16 direct references met `1e-8`; two reached only `1.625e-8` and `2.022e-8` |
| Real selected convergence | PASS | 120/120 selected fits met projected KKT and complementarity `<=1e-5` |
| No objective regression | PASS | All 120 selected objectives improved on the exact legacy rerun |
| Start robustness | PASS | Both starts qualified in 120/120 targets; maximum objective gap `6.52e-9` |
| Cross-node determinism | PASS | Complete shared-anchor hashes were identical on the two nodes |
| Complete unfavorable reporting | PASS | Every real/generated target, start, stage, endpoint and resource record is retained |

All nine gates were required, so the formal experiment is FAIL.

## Generated equivalence control

Eight new two-mark Hawkes streams used the frozen root seed `139202608`; none reused exp138's generated seeds.
The direct nonnegative Hawkes model and the intercept-only combined model are algebraically the same intensity
family under `mu = exp(theta_0)`.

| Diagnostic | Formal result | Frozen requirement |
|---|---:|---:|
| Direct-reference fits at selection KKT | 14/16 | 16/16 at `<=1e-8` |
| Failed direct reference, replicate 1 / target 0 | `1.6248e-8` | `<=1e-8` |
| Failed direct reference, replicate 5 / target 0 | `2.0216e-8` | `<=1e-8` |
| Combined starts at stop KKT | 32/32 | 32/32 at `<=1e-7` |
| Maximum combined projected KKT | `9.8646e-8` | `<=1e-7` |
| Maximum absolute objective difference | `1.7875e-14` nats/event | `<=1e-7` |
| Maximum physical-parameter absolute difference | `1.3143e-7` | descriptive only |

Both failed direct references consumed all six refinement stages. For each, the combined Hawkes-initialized
endpoint reproduces the direct-reference physical parameters to floating-point precision, while the independent
queue start reaches the same objective and parameters within about `1.15e-8`. Thus the equivalence identity and
combined implementation are not contradicted; the formal failure is the reference solver's stricter residual.

## Real training-prefix numerical repair

The real component contains five external symbols, two timestamp-tie policies, aligned/shifted queue designs
and six marks: 20 cells and 120 target fits. It recomputes the exp138 legacy fit and then refines both the queue
and Hawkes endpoints without changing the likelihood, features, fixed decay rates, bounds, split or starts.

| Diagnostic | Formal result | Frozen requirement |
|---|---:|---:|
| Selected targets qualified | 120/120 | 120/120 |
| Both starts qualified | 120/120 | at least 114/120 |
| All individual starts qualified | 240/240 | implied by the row above |
| Starts reaching stricter `1e-7` stop | 169/240 | descriptive only |
| Maximum selected projected KKT | `8.9118e-7` | `<=1e-5` |
| Median selected projected KKT | `7.8122e-8` | descriptive only |
| Maximum selected complementarity | `7.6208e-9` | `<=1e-5` |
| Maximum / median start objective gap | `6.5250e-9` / `5.7725e-14` | `<=1e-5` / `<=1e-6` |
| Minimum / median legacy improvement | `7.0915e-9` / `9.1548e-7` | no regression beyond `1e-10` |

The selected endpoint came from the queue start in 71 targets and the Hawkes start in 49. Seventy-two of 240
starts exhausted all six refinement stages, but all still met the `1e-5` selection threshold. The largest raw
selected gradient was `0.6485` while the largest projected residual was `8.91e-7`; up to ten excitation
coefficients were active at their lower bound. This confirms why raw gradients are invalid convergence
diagnostics for these bound-constrained fits.

No real test or held-out likelihood was computed. The loader materialized full message/book fields only through
the 60% boundary: 1,584,932 of 2,641,557 source rows. A bounded timestamp-only sentinel was used solely to finish
boundary tie groups. The exp138 40% test partition was not revisited.

## Compute and reproducibility

- Shard 0: GOOG, SPY and generated replicates 0/2/4/6; 1,412.49 worker seconds and 23 min 36.855 s systemd CPU.
- Shard 1: AAPL, AMZN, MSFT and generated replicates 1/3/5/7; 819.84 worker seconds and 13 min 44.048 s systemd CPU.
- Both transient services deactivated successfully. They used one CPU process and one BLAS thread on each V100
  host with `CUDA_VISIBLE_DEVICES=-1`; both GPUs remained unused.
- Both clean clones used Python 3.11.15, NumPy 2.4.6, pandas 3.0.5 and SciPy 1.17.1 at exact commit `e6a7eaaf`.
- Peak RSS was about 745 MiB on shard 0 and 498 MiB on shard 1; merged worker time was 2,232.33 seconds.
- Shard 0 SHA-256: `2fe252db3ef0533b06c08cfcfd3a6e9aa5b75d190148f2421a7d27e784e28276`.
- Shard 1 SHA-256: `4e4879d823c5672dd5ca0428efee3058996c14c751d7e679e6362844dd9aed35`.
- Merged SHA-256: `21818f9d9798b0c213239efa19160ac9bf46be1759cb98643367d221a8b08984`.
- A second merge to a temporary path was byte-identical to the archived merged artifact.

## Claim boundary and next gate

Exp139 is a training-only numerical-method experiment. It establishes that the projected-KKT implementation
is correct and that the unchanged combined real fits can reach defensible training endpoints under the frozen
budget. It does not confirm queue-state predictive value, validate EcoMD against external messages, pass G3,
unlock paid L2 or support a market-physics claim.

A formal numerical PASS now requires a separately preregistered solver-family check with fresh generated seeds;
the two failed reference endpoints and all current generated seeds are development evidence. More importantly,
external empirical confirmation requires genuinely unseen dates or markets, a frozen EcoMD-to-message map and
individual-order or explicitly limited aggregate semantics. Optimizer work must not displace the unresolved G0
method-novelty audit or be presented as the NCS contribution.
