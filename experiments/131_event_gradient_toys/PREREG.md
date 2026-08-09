# Experiment 131 — discrete-event invariant-gradient baseline audit

**Frozen:** 2026-08-10, before any result from this experiment  
**Status:** baseline/harness audit; no candidate estimator and no novelty claim  
**Cost boundary:** Mac CPU only, synthetic draws only, no purchased data

## Questions

1. Can the harness recover exact stationary gradients for a discrete two-state Markov chain?
2. Can it recover the jump-rate contribution to the stationary second moment of a compound-Poisson AR/OU
   discretization?
3. Does carrying a persistent state while resetting the event score remain biased under slow mixing?
4. Does the corrected stochastic forward law consume exactly the same random stream with and without
   autograd graph construction?

This experiment audits known likelihood-ratio and finite-difference controls. It does not introduce the
mixing-aware candidate required by G0.

## Frozen systems

### E1a — two-state chain

- State `X_t in {0,1}`.
- `P(0->1)=alpha`, `P(1->0)=beta`.
- Mixing sums `g=alpha+beta in {0.80, 0.20, 0.04}` with stationary occupancy fixed at `pi_1=0.4`, so
  `alpha=0.4g`, `beta=0.6g`.
- Objective `E_pi[X] = alpha/(alpha+beta)`.
- Target derivative holds beta fixed:
  `d E_pi[X] / d alpha = beta/(alpha+beta)^2`.

### E1b — compound-Poisson AR(1)

- `X_(t+1) = a X_t + sigma epsilon_t + J_t`.
- `K_t ~ Poisson(lambda)`, `J_t | K_t ~ Normal(0, K_t jump_scale^2)`.
- `a in {0.20, 0.80, 0.97}`, `sigma=0.20`, `lambda=1.5`, `jump_scale=0.35`.
- Objective `E_pi[X^2]` with exact derivative
  `d E_pi[X^2] / d lambda = jump_scale^2/(1-a^2)`.

Both systems use short horizon 24 and long burn/path 2,048. Monte Carlo uses 64 independent batches of 512
replicates (`32,768` paths per cell). All random seeds are spawned from one frozen root seed.

## Frozen estimators and controls

- fresh-short likelihood ratio from a fixed initial state;
- persistent state after a 2,048-step burn, with score/tangent reset at the short-window boundary;
- full-long likelihood ratio from the fixed initial state;
- stationary-initialization oracle for the two-state chain;
- central finite difference with coupled/common randomness;
- analytic stationary/generator truth;
- deliberately naive jump pathwise result, which is zero/unavailable for the Poisson rate and must fail.

Likelihood-ratio estimates use the exact transition/event score. Centering may use the known finite-horizon
expectation because this is a variance-reduction control, not the proposed method. Simulator cost counts every
transition in both finite-difference arms.

## Metrics

For each estimator and mixing regime record:

- relative bias against analytic truth;
- RMSE across the 64 batch means;
- empirical coverage of per-batch 90% normal intervals;
- sign accuracy of batch means;
- simulator transitions and wall time.

The artifact also records forward-law parity: identical terminal RNG state and exact CPU trajectories for
`create_graph=True/False` under fixed seed.

## Hard interpretation rules

- Harness sanity passes only if analytic formulas agree with an independent numerical check and the
  stationary-oracle two-state estimator has absolute relative bias below 10% or 90% interval coverage at least
  85% in every regime.
- Jump-rate feasibility passes if at least one established non-oracle estimator has absolute relative bias below
  10% or interval coverage at least 85% in medium and slow regimes.
- The naive jump pathwise estimator must be labelled invalid even if a noisy sample happens to be close to zero.
- Persistent-detached state is not promoted to an invariant-gradient estimator. Its bias is reported without
  changing the rule after inspection.
- No G0 upgrade is allowed: passing this experiment validates the problem and controls only. Failure blocks any
  EcoMD event-gradient claim until the harness is repaired.

