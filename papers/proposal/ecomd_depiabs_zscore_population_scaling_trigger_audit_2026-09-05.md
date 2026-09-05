# EcoMD DEpiABS z-score population-scaling trigger audit

**Date:** 2026-09-05  
**Archetype:** `simulator_method`  
**Decision:** `not_trigger`  
**Candidate harvesting:** not authorized  
**Outcome access, implementation, EcoMD execution, SSH, and GPU work:** not authorized

## 1. Executive decision

DEpiABS is a current, accepted differentiable-agent-simulator paper and therefore a relevant test
of whether a new small-to-large population-scaling method can reopen EcoMD's closed population
transfer route. It does not. Its proposed scaler is a target-conditioned affine transformation of
one output series, not a population transfer operator.

Writing the simulated series as `x` and the calibration series as `y`, the published construction
reduces exactly to

\[
\widehat x
=\sigma_y\left(\frac{x-\mu_x}{\sigma_x}
-\min_t\frac{x_t-\mu_x}{\sigma_x}\right)+\min_t y_t.
\]

Consequently the final output has the target standard deviation and minimum, but its mean is
`min(y) - sigma_y min(z_x)`, which equals `mu_y` only when the two series have the same standardized
minimum. The target mean cancels from the final expression. The paper's statement that the final
transformation directly matches both location and scale while also aligning the minimum is therefore
false in general.

The transform is also invariant to every positive affine change of the simulator output:
`T_y(a x+b)=T_y(x)` for `a>0`. It therefore cannot distinguish simulators with arbitrarily different
levels or amplitudes when their standardized shapes agree. Those are precisely the quantities a
population-size scaling claim must explain rather than erase.

The reported forecasting experiment uses a 500-agent simulation against regional data, while the
scalability test measures runtime versus simulated population size. The paper does not report a
matched small-population versus large-population path-law test, a population-indexed parameter map,
or intervention-response preservation. Its encounter equations are pairwise and contain no stated
population normalization that would make fixed parameters projectively consistent as population
changes.

The result is a useful negative trigger but not a new ICLR topic. Correcting a two-line affine
identity is too small; expanding it into a generic simulator-audit paper collides with the already
closed audit route; and a genuine learned population-transfer method collides with mesoscopic-SDE,
mean-field, graph-size-generalization and neural-renormalization parents while EcoMD's latent
particle count remains non-native. No new route node is warranted.

## 2. Question, rivals, and cheapest discriminator

The market-native object would have to be the law of a declared aggregate market response at a
larger economic population, not the visual similarity of a rescaled output curve.

- **H1 -- projective population transfer:** a small-system law and an explicit population-indexed
  dynamics map determine the large-system law, including fluctuations and intervention responses.
- **H0 -- target-conditioned curve calibration:** empirical target moments set the output's units
  after simulation; this can improve a forecast metric without establishing any small-to-large
  mechanism.

**Cheapest discriminator.** Expand the proposed transform before running any model. A valid
population-transfer operator must retain information that distinguishes incompatible amplitude and
population laws and must be evaluable without the realized target path. The published map fails
both tests algebraically.

A positive answer would justify cheaper small-system training followed by certified transfer. A
null answer matters because it prevents a target-normalized forecast from being cited as evidence
that latent EcoMD particles represent real market population.

## 3. Three-constraint affine lemma

Assume nonconstant real vectors `x,y` and use the same standard-deviation convention for both. Let

\[
z_x=(x-\mu_x)/\sigma_x,
\quad x'=\sigma_y z_x+\mu_y,
\quad \widehat x=x'-\min(x')+\min(y).
\]

Since `sigma_y>0`, `min(x')=sigma_y min(z_x)+mu_y`, hence

\[
\widehat x=\sigma_y(z_x-\min(z_x))+\min(y).
\]

It follows immediately that

\[
\operatorname{sd}(\widehat x)=\sigma_y,
\qquad \min(\widehat x)=\min(y),
\qquad \operatorname{mean}(\widehat x)=\min(y)-\sigma_y\min(z_x).
\]

Thus mean, standard deviation and minimum are matched simultaneously if and only if

\[
\frac{\min(x)-\mu_x}{\sigma_x}
=\frac{\min(y)-\mu_y}{\sigma_y}.
\]

This compatibility condition does not hold generically. It is the familiar fact that an affine
map has only two degrees of freedom: matching standard deviation and minimum consumes both, so an
independent mean constraint cannot also be imposed without a shape restriction.

## 4. Affine-erasure lemma

For `x_2=a x+b` with `a>0`, `z_{x_2}=z_x`; therefore

\[
T_y(x_2)=T_y(x).
\]

This is not merely harmless unit invariance. In a claimed population scaler, `a` can encode the
entire change in event count or response amplitude between two simulated population laws. The
transformation makes the following worlds observationally identical after scaling:

1. one small simulator whose epidemic or market count is proportional to population;
2. another whose count is independent of population;
3. a third with the wrong population multiplier by an arbitrary positive factor.

If their standardized temporal shapes agree, the reported scaled series agree exactly. Hence a
successful post-transform forecast cannot identify the population exponent, conservation law,
finite-size noise, or interaction normalization.

## 5. Why this is not population transfer

A defensible stochastic small-to-large claim requires a family of laws `P_N`, a declared map between
population states, and a metric or estimand under which transfer is proved or tested. At minimum it
must specify:

1. what one population unit means and how weighted splitting or merging acts;
2. how interaction, noise and initial-state parameters depend on population;
3. whether aggregation and dynamics commute under the chosen projection;
4. which marginal, temporal, tail and intervention-response objects are preserved; and
5. how performance is evaluated on a target scale whose outcomes were not used to define the map.

DEpiABS instead maps one realized simulated output directly to empirical calibration statistics.
Its final expression contains no target population size and no large-population transition law. It
cannot map agent microstates, pair correlations, stochastic variance, rare events or counterfactual
policies. It is an output calibration layer.

The distinction is especially sharp in the stated encounter dynamics. The encounter matrix is
pairwise with probability `m`, and expected exposures aggregate over infectious agents. No
population-indexed law for `m`, facility capacity, density or agent weights is given in the scaling
section. Holding these quantities fixed while changing `P` need not preserve per-agent interaction
intensity. A post-hoc affine curve transform cannot repair the resulting state-law change.

## 6. Evidence and evaluation contract

The paper describes `y_mu` and `y_sigma` as statistics of real data for calibration and says that it
follows the baseline's processing, calibration and forecasting procedure. The available experiment
description does not state the exact index set from which every scaling statistic is computed.
This audit therefore does **not** allege evaluation leakage as an observed fact.

It does establish a mandatory contract: all target-derived location, scale and minimum statistics
must be fitted only on a frozen calibration interval and carried unchanged into the forecast
interval. Computing any of them from the evaluated future path would leak outcomes directly into
the prediction. Even with a clean split, however, the method remains calibration rather than
population transfer.

The published evidence does not close that scientific gap:

- the forecast table is based on a 500-agent simulation followed by target normalization;
- five repeated runs quantify forecast variation but do not compare matched `P_N` laws;
- the scalability section reports runtime growth and notes that larger populations can improve
  accuracy; and
- no held-out population size, distributional distance, intervention response, or micro-to-macro
  commuting test is reported.

## 7. Collision and residual-novelty audit

The strongest repair is not an open EcoMD method niche.

1. **Finite-size stochastic closure.** Nabeel et al. learn mesoscopic drift and multiplicative
   diffusion for finite interacting populations and study deviations from mean-field scaling.
2. **Learned small-to-large coarse graining.** Neural renormalization already trains a shared map on
   small lattices and evaluates large-system critical fluctuations and finite-size scaling.
3. **Mean-field population representations.** Current work learns population-law features and gives
   finite-population transfer guarantees under explicit coverage assumptions; major-agent, common-
   noise and robust-mismatch variants already occupy the obvious extensions.
4. **Graph-size generalization and pooling.** Size-generalizing graph networks, adaptive pooling and
   degree scalers occupy a learned aggregation-only contribution.
5. **Generic simulator audit.** Metamorphic and scaling tests without a new theorem or estimator fall
   under the already closed `generic_simulator_audit_v4a` route.

A note pointing out the DEpiABS moment inconsistency would be correct but not an ICLR contribution.
A benchmark that merely catches it would also be generic QA. A publishable residual would require a
new projective stochastic operator or certificate with a separating guarantee and validation on
independent systems, not another normalization layer.

## 8. Gate matrix

| Gate | Result |
|---|---|
| Final mean, standard deviation and minimum all match | Fail except under equal standardized minima |
| Target mean affects final output | Fail; it cancels algebraically |
| Simulator scale information is retained | Fail; positive affine changes are erased |
| Map is target-outcome independent | Fail as a general transfer object; it uses target calibration statistics |
| Population-indexed dynamics are specified | Fail |
| Matched small/large path-law validation exists | Fail |
| Temporal dependence, tails and intervention response are controlled | Fail |
| EcoMD particle count is a market-native population unit | Fail from the existing route audit |
| Method is beyond mesoscopic, mean-field, graph and RG parents | Fail |
| New theorem/estimator beyond generic simulator QA | Fail |
| Independent same-estimand truth systems exist | Fail |

## 9. Preserved reusable asset

Preserve the **target-free population-transfer audit**:

1. symbolically eliminate all post-processing nuisance parameters;
2. test which simulator transformations leave the reported output unchanged;
3. require a population-indexed stochastic kernel, not a target-fitted output map;
4. freeze calibration statistics and evaluate on untouched scales and time intervals;
5. test a commuting diagram under subsampling, aggregation and weighted unit splitting; and
6. compare full path laws and intervention responses, not only normalized means or forecast error.

The affine-erasure witness is a cheap first test for any future EcoMD or ABM scaling proposal. It is
a guardrail, not a paper topic.

## 10. Exact re-entry conditions

Re-audit population transfer only after all of the following exist:

1. a market-observable economic population unit and weighting rule invariant to admissible identity
   splitting and aggregation;
2. an explicit population-indexed transition or generator map that is target-outcome independent;
3. a theorem or estimator for path-law or intervention-response transfer with finite-sample upper
   bounds and a matching or separating lower bound, irreducible to mean-field closure, graph
   pooling, stable normalization or learned renormalization;
4. matched full-system truth at several populations on two independently maintained dynamic
   systems, plus an untouched confirmation scale and interval; and
5. a frozen comparison against mesoscopic SDE, mean-field, graph-size and neural-RG parents.

Another z-score, min-max map, learned affine head, visual curve match, runtime sweep, target-moment
fit, or EcoMD latent-`N` sweep is not a trigger.

## 11. Primary sources

1. Gao, Li and An, *DEpiABS: Differentiable Epidemic Agent-Based Simulator*, AAMAS 2026,
   https://arxiv.org/abs/2602.12102 and
   https://www.ifaamas.org/Proceedings/aamas2026/forms/contents.htm
2. Nabeel et al., *Data-driven discovery of stochastic dynamical equations of collective motion*,
   Physical Biology 20, 056003 (2023), https://arxiv.org/abs/2304.10071
3. *Neural Renormalization Group Flow for Percolation*, 2026,
   https://arxiv.org/abs/2608.26764
4. Makkar et al., *Towards Scaling Reinforcement Learning to Massive Populations: Learning
   Mean-Field Representations*, 2026, https://arxiv.org/abs/2609.02928

## 12. Compute decision

This audit is `not_trigger`; `candidate_harvest_authorized=false`. Do not implement the DEpiABS
scaler, download epidemic outcomes, run population sweeps, modify EcoMD, SSH to a worker, or schedule
the A800/V100 pool under this route. The current constraint-attribution machine decision is
unrelated and grants no authority here.
