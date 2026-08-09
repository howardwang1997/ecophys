# Experiment 135 results — latent-flow misspecification stress

**Run date:** 2026-08-10  
**Preregistration commit:** `795308eb5`  
**Implementation commit:** `eca713fac`  
**Artifact:** `MISSPECIFICATION_RESULTS.json`  
**Decision:** all frozen gates PASS; G3 remains open

## Frozen result

The clean-tree CPU run generated 144 independent streams and 4,320,000 signed-flow events across six truth
families and three latent mixing regimes. All 864 logistic fits converged, every value was finite, and all seven
gate groups passed in 8.3 seconds.

The evaluator selected the correct source when the truth was single-source:

| Truth | `rho` | recovered coefficient | correct model minus wrong single-source, nats/event |
|---|---:|---:|---:|
| current latent (`beta=0.8`) | 0.00 | 0.8070 | 0.1814 |
| current latent (`beta=0.8`) | 0.80 | 0.7949 | 0.1462 |
| current latent (`beta=0.8`) | 0.98 | 0.7959 | 0.1322 |
| observed lag (`alpha=0.8`) | 0.00 | 0.7985 | 0.2409 |
| observed lag (`alpha=0.8`) | 0.80 | 0.7979 | 0.2383 |
| observed lag (`alpha=0.8`) | 0.98 | 0.8072 | 0.2418 |

Adding the wrong source to either single-source truth changed held-out likelihood by at most about `1e-4`
nats/event in median. Under observation-only truth, the combined model's median latent coefficient stayed
between `-0.0015` and `0.0058`, far below the frozen `0.08` limit.

Under combined truth, the two fitted coefficients were `(0.611, 0.605)`, `(0.607, 0.608)` and
`(0.600, 0.605)` for `rho=0.00, 0.80, 0.98`, against truth `(0.6, 0.6)`. The combined model beat the better
single-source model by `0.106`, `0.073` and `0.057` nats/event, respectively.

## Misspecification and identifiability findings

The lagged-latent oracle beat the incorrectly aligned current-latent model by `0.1818` nats/event at `rho=0`
and `0.0719` at `rho=0.8`. At `rho=0.98`, the gap collapsed to `0.00844`, as anticipated in the
preregistration. This is a substantive warning: highly persistent latent paths can make adjacent temporal
alignments predictively similar, so held-out likelihood alone cannot establish causal timing.

For the even nonlinear truth, the quadratic oracle beat the linear latent model by `0.1342`, `0.1326` and
`0.1269` nats/event. The fitted linear slopes were only `0.0014`, `0.0083` and `0.0197`, while the quadratic
coefficient recovered as `0.5994`, `0.5981` and `0.6053` against truth `0.6`.

Under the complete null, the median largest positive held-out gain among all five non-null models was only
`2.12e-5`, `2.44e-5` and `1.21e-5` nats/event across the three `rho` values. No flexible model manufactured a
material signal.

## What passed—and what did not

This PASS shows that the fixed evaluator can distinguish several simple synthetic latent and observation-only
stories, detect wrong lag/nonlinearity when the features are identifiable, and keep null gains negligible. It
also records a predeclared failure of temporal identification in the nearly collinear `rho=0.98` lag case.

It does not validate:

- `latent_flow_alignment` as a driver of EcoMD-emitted messages;
- any external buy/sell sign anchor or causal temporal alignment for EcoMD;
- queue dynamics, price moves, censoring, latency or aggregation under these misspecified truths;
- superiority to Hawkes, queue-reactive or empirical-resampling baselines;
- any real-market or paid-L2 claim.

Therefore G3 remains open and paid data remain locked. The next zero-cost observation-bridge experiment is a
state-complete EcoMD adapter with a frozen sign anchor and temporal alignment. If the adapter cannot beat the
observation-only baseline on synthetic holdout, the model-to-L2 route stops.
