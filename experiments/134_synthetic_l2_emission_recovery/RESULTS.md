# Experiment 134 results — synthetic L2 emission and recovery

**Run date:** 2026-08-10  
**Implementation commit:** `79b7126cd`  
**Artifact:** `SYNTHETIC_L2_RESULTS.json`  
**Decision:** minimal correctly specified synthetic bridge PASS; G3 remains open

## Frozen result

The formal CPU run generated 72 independent streams and 2,160,000 total events across three latent mixing
regimes and three conditional flow slopes. All ten preregistered gates passed in about 2.4 seconds.

- Every L5 after-event snapshot was reconstructed bit-exactly from the initial book and emitted message fields.
- Every hidden execution left displayed depth unchanged; the minimum queue over all streams was 95,418 units.
- All Bernoulli, truncated-level and Poisson fits converged and all reported values were finite.

Conditional flow recovery remained accurate despite latent serial correlation:

| `rho` | true `beta` | median fitted `beta` | median relative error | held-out gain, nats/event |
|---:|---:|---:|---:|---:|
| 0.00 | 0.50 | 0.5007 | 1.46% | 0.0937 |
| 0.80 | 0.50 | 0.5004 | 2.12% | 0.0920 |
| 0.98 | 0.50 | 0.4918 | 2.09% | 0.0961 |
| 0.00 | 1.00 | 1.0057 | 0.97% | 0.2292 |
| 0.80 | 1.00 | 1.0041 | 1.70% | 0.2315 |
| 0.98 | 1.00 | 1.0123 | 1.32% | 0.2230 |

All nonzero cells recovered the correct sign in 8/8 streams. In the three `beta=0` cells, median absolute slope
error was between 0.0031 and 0.0061 and held-out gains were effectively zero.

The median absolute errors for hidden/add/removal probabilities were 0.0014--0.0034; the level-decay error was
0.0038. Median relative error for the size slope `gamma` was 1.08%, and its held-out gain over `gamma=0` was
0.108 nats/event.

## Negative and gauge controls

Permuting the latent driver separately inside train and held-out blocks reduced every nonzero cell's median
absolute fitted slope to at most 0.0076 and its held-out gain to numerical noise. This rules out recovery from
event marginals alone in this correctly specified fixture.

Replacing `z` by `-z` produced exactly the negative fitted slope and exactly the same held-out likelihood in all
72 streams. This is not a nuisance numerical detail: an unanchored latent coordinate has a sign gauge, and L2
messages alone cannot determine its orientation. Any EcoMD adapter must impose and test an external buy/sell
orientation rather than interpreting an arbitrary latent sign post hoc.

## What passed—and what did not

This PASS validates a minimal aggregate-depth schema, exact queue bookkeeping, conditional maximum-likelihood
recovery and two controls under the same model used to generate the data. It does not validate:

- EcoMD's current latent variable as a driver of order flow;
- individual order IDs, price-time priority, queue depletion, inside-spread placement or price moves;
- model misspecification, latency, censoring, aggregation or posterior calibration;
- superiority to Hawkes/queue-reactive, observation-only or empirical-resampling baselines;
- any real LOBSTER/Tardis market claim.

Therefore G3 is not passed and paid data remain locked. The next free steps are the formal
`ofi -> latent_flow_alignment` migration, an EcoMD adapter with a fixed sign anchor, and a preregistered
misspecification/observation-only stress test.

