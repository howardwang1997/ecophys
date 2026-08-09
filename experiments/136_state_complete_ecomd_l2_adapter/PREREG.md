# Experiment 136 — state-complete EcoMD-to-L2 adapter

**Frozen:** 2026-08-10, before adapter implementation or results  
**Status:** G3 plumbing and synthetic recovery only  
**Cost boundary:** Mac CPU, `N=64`, generated messages only, no purchased data, no V100/H20

## Question

Can a state-complete EcoMD rollout drive a checkpointable aggregate-L2 emitter with exact monolithic/chunked
parity, an explicit no-lookahead clock, and a buy/sell sign convention fixed outside the fitted likelihood? When
messages are generated from the model's `latent_flow_alignment`, can that driver beat an observed-flow-only
baseline on a strict future split?

Passing is deliberately narrow. The emission law is used to generate its own synthetic messages, the EcoMD
weights are fixed random weights, and no real market is involved. This test can validate interfaces and reject
broken alignment; it cannot show that EcoMD explains real order flow.

## Frozen EcoMD source

- One fixed random parameter draw with seed `136000`; no fitting or checkpoint selection.
- `N=64`, `d_state=8`, hidden width 16, `dt=0.005`, state-complete regime/agent/global memories,
  stochastic sparse pair interactions and sampled jumps.
- Positive price-readout constants `kappa=0.5`, `beta=0.02`; heterogeneous mass flow disabled;
  raw pre-impact excess demand logged.
- 8 rollout seeds spawned from root seed `136_202_608`.
- 3,000 transitions per rollout; first 500 are discarded before message emission.
- CPU uses one PyTorch thread. Non-finite simulator output is a hard failure, not clipped or retried.

For every seed, compare a monolithic rollout to fixed chunks `(137, 499, 61, 803, 1500)`. Alignment, raw excess
demand, log returns and final state/RNG must be bit-exact. Existing exp128 parity is not substituted for this
adapter-specific check.

## Frozen adapter semantics

One post-burn-in transition emits one LOBSTER-shaped aggregate message. Transition `t -> t+1` produces
`latent_flow_alignment[t]` and then an observation timestamp `(t+1)*dt`; no future state is read. The adapter
state contains current displayed book, next absolute simulator step, next order ID and NumPy RNG state.

The sign anchor is structural and non-learned:

- positive latent alignment means `sum_i delta_position_i > 0`;
- because `kappa>0`, this must have the same sign as raw excess demand;
- positive signed displayed flow means bid addition or ask removal, i.e. buy pressure;
- the emission slope is constrained by configuration to `beta_emit=+2.0` and may not flip during fitting.

Thus `z -> -z, beta -> -beta` is not an allowed relabeling of the adapter. A flipped-driver score keeps the same
positive beta and must lose likelihood. This fixes a model-to-schema convention; it is not evidence that the
convention matches real data.

The remaining event marks use the exp134 aggregate-L5 defaults. The emitter processes events in absolute order
so splitting a stream cannot change RNG assignment. Compare one-shot emission with chunks `(211, 17, 503,
769, 1000)`, including a serialized checkpoint after 731 emitted events.

## Frozen recovery and baselines

The first 60% of the 2,500 emitted events is training and the final 40% held out. Fits use visible messages only;
the observation-only feature is the previous visible signed flow. All models have an intercept:

- `latent`: `2 * latent_flow_alignment_t`;
- `observation_only`: `2 * q_previous_visible`;
- `combined`: both features;
- `permuted`: latent alignment independently permuted within train and test blocks.

Report fitted coefficients and held-out nats per visible event. Parameter recovery is a plumbing check under
correct specification, not a scientific model claim.

## Frozen hard gates

1. All eight EcoMD paths are finite; monolithic and chunked alignment, raw excess demand, returns, terminal
   state and RNG are bit-exact.
2. For every nonzero-alignment step, `sign(latent_flow_alignment) == sign(raw_excess_demand)`; `beta_emit` is
   positive and immutable.
3. One-shot, chunked and checkpoint-resumed adapter outputs are bit-exact for every message field, snapshot and
   terminal adapter state. Order IDs are contiguous, timestamps equal the declared absolute-step clock, all
   queues stay positive and message reconstruction is bit-exact.
4. Across eight streams, median relative error of the latent slope is at most 20%, and at least 7/8 fitted
   slopes are positive.
5. Median held-out latent-minus-observation-only gain is at least 0.01 nats/visible event. The combined model
   adds at most 0.005 over latent and its median absolute observed-lag coefficient is at most 0.15.
6. Under the permuted control, median absolute latent slope is at most 0.20 and median absolute held-out gain
   over the intercept-only null is at most 0.003 nats/visible event.
7. Scoring the same positive frozen emission slope on the anchored driver beats the sign-flipped driver by at
   least 0.02 median held-out nats/visible event.
8. Every optimizer converges and every reported value is finite.

Any failed gate remains visible. Thresholds may not be changed in this version.

## Interpretation boundary

A PASS completes the minimal state-complete adapter plumbing. G3 still requires price/order-level semantics,
an observation-only point-process or queue-reactive baseline, latency/censoring stress and a protocol using
training data not generated by the fitted emission family. Paid L2 remains locked.
