# EcoMD scale, tail and laboratory-truth re-entry audit

**Date:** 2026-09-04

**Mode:** outcome-blind theorem, primary-work, route-duplicate and public-schema audit under the
search-family saturation rule

**Decision:** **NO QUALIFIED TRIGGER. Five narrow formulations are closed or remain only partial
capabilities. Cycle 17, a topic card, an experiment plan, EcoMD implementation, SSH and GPU work are
not authorized.**

## 1. Why this audit was allowed

The simulated-market search family is saturated, so this was not another broad topic cycle. It
tested whether five concrete objects remove a written blocker in an existing route:

1. a random-batch correction uniform in EcoMD's slow-memory limit;
2. fluctuation-aware transfer from small to large latent particle populations;
3. differentiable calibration of an extreme-tail functional rather than ordinary moments;
4. a multi-laboratory assigned-intervention benchmark for market simulators; and
5. a certificate that a requested stylized-fact vector is outside a simulator's attainable set.

The cheapest checks were used first: route-graph duplicate, exact reduction, closest primary-work
collision and public schema. No simulator or data outcome was required.

## 2. Random batching plus slow memory does not yet define a new method

### 2.1 Frozen question

Let $X_t$ denote EcoMD particle state and $H_t$ its Hawkes, recurrent or other slow state. Does an
instantaneously unbiased random-pair force estimator create a long-run error that existing Random
Batch Method (RBM) analysis and corrections cannot control when the memory relaxation rate tends to
zero?

- **H1:** correlated force noise is stored by $H_t$, producing a distinct rare-event or
  invariant-law bias that needs a new correction uniform in the memory time scale.
- **H0:** after augmenting the state to $Z_t=(X_t,H_t)$, this is an ordinary Markov RBM whose error
  constant deteriorates as the augmented spectral gap closes.
- **Discriminating result:** a correction and non-vacuous invariant-law or rare-event bound uniform
  in the slow-memory limit, false for existing RBM corrections and validated against full
  interactions on two independent systems.

### 2.2 Exact reduction

For any finite-dimensional update

\[
X_{t+1}=G(X_t,H_t,\widehat F_t,\epsilon_t),\qquad
H_{t+1}=R(H_t,\phi(X_t),\eta_t),
\]

the pair $Z_t=(X_t,H_t)$ is Markov once its random inputs are included. Conditional unbiasedness of
the batch force remains $E[\widehat F_t\mid Z_t]=F(Z_t)$. A long memory can make contraction or
mixing constants arbitrarily poor, but that is not a new non-Markovian object. In a stable linear
reduction, the stationary covariance is obtained from the ordinary augmented Lyapunov equation;
near loss of stability, any extra batch covariance is amplified by the same closing spectral gap.

The obvious numerical repair is also occupied. [Xu, Zhao and
Zhou](https://arxiv.org/abs/2411.01762) estimate batch-force variance and correct artificial
Langevin heating consistently with fluctuation--dissipation. Momentum correction, multi-species RBM,
Lévy-driven RBM and random reshuffling are adjacent established variants. Random batching has also
already been transferred to neural attention in [Random Batch
Attention](https://arxiv.org/abs/2511.06044). The repository's earlier trigger audit already records
the original method, long-time invariant behavior and phase-transition effects.

The stronger colored-noise escape is occupied as well. [Random Reshuffling
SGLD](https://arxiv.org/abs/2501.16055) proves lower Wasserstein bias from changing the temporal
batch policy. [Stochastic-gradient thermostats](https://proceedings.neurips.cc/paper_files/paper/2014/hash/b610047c85e73cb7ec04fd36ec503f93-Abstract.html)
introduce auxiliary variables for unknown batch noise, and the [covariance-controlled adaptive
Langevin thermostat](https://proceedings.neurips.cc/paper/2015/hash/6f4922f45568161a8cdf4ad2299f6d23-Abstract.html)
explicitly estimates and dissipates parameter-dependent noise covariance. Fitting the random-batch
error spectrum and adding an auxiliary thermostat would compose these parents with a generalized
Langevin representation; it is not a new principle.

### 2.3 Verdict

**`not_trigger`.** “RBM + GRU/Hawkes” is a state augmentation, not a new algorithm. A proof whose
constant diverges as memory becomes slow would merely re-express poor mixing. Re-entry requires an
actual correction and theorem uniform in that singular limit and irreducible to force-variance,
momentum, reshuffling, adaptive-thermostat, control-variate or standard augmented-state RBM methods.

## 3. Finite-size fluctuation transfer fails the native-control gate

### 3.1 Frozen question

Can a learned mesoscopic SDE or renormalization map trained at small particle count predict EcoMD
aggregate fluctuations and intervention responses at large $N$?

- **H1:** drift and diffusion obey a learnable projective scaling law, so small-$N$ experiments
  identify the large-$N$ response.
- **H0:** $N$ is an analyst-selected latent resolution; changing it changes density, interaction
  normalization, type counts or the observation map rather than one market-native control.
- **Discriminating result:** a representation-invariant response law under matched economic state,
  plus a finite-size error theorem and a hard case that generic graph or neural-operator transfer
  does not cover.

### 3.2 Direct collisions and representation failure

[Nabeel et al.](https://arxiv.org/abs/2304.10071) already learn finite-population mesoscopic drift
and multiplicative noise for stochastic pairwise collective motion, explicitly study population-
size dependence and show deviations from mean-field predictions. [Neural Renormalization Group Flow
for Percolation](https://arxiv.org/abs/2608.26764) trains a recursively shared rule on small lattices,
extrapolates to substantially larger systems and recovers finite-size scaling and critical
fluctuations. Existing graphon, graph neural dynamics and mean-field inference work occupies the
remaining generic scale-transfer neighborhood.

More importantly, real market data do not observe EcoMD's latent particle count. Replacing one
latent agent by two identical half-weight agents can preserve every aggregate path while changing
$N$, pair counts and an apparent finite-size exponent. Unless the proposed quantity is invariant
to that legal refinement, it measures simulator resolution rather than market physics. Neither a
mesoscopic SDE module nor a neural renormalization module repairs this identification failure.

### 3.3 Verdict

**`not_trigger`.** The computational problem is real, but both main method components have direct
parents and EcoMD lacks a market-native population-size control. Re-entry requires an observable
economic unit and refinement-invariant law, or a generic theorem false for existing mesoscopic,
graphon and learned-renormalization methods. No such object is currently present.

## 4. A differentiable Hill loss does not solve tail learning

### 4.1 Frozen question

Can differentiating an extreme-value tail estimator through EcoMD correct the historical failure to
match return tails?

- **H1:** an estimator aligned with the tail index supplies the missing gradient signal.
- **H0:** the apparent novelty is only automatic differentiation through a locally fixed top-$k$
  set; the hard problem is rare-event support, threshold choice, dependence and model capacity.
- **Discriminating result:** a consistent or calibrated stochastic gradient for a tail functional
  through event-support changes, with a bias--variance--cost theorem and improvement over EVT,
  weighted-score, CVaR and kernel-score baselines.

### 4.2 Local derivative and hard boundary

For positive samples and a fixed order with no ties, the Hill statistic

\[
\widehat \xi_k=\frac1k\sum_{i=1}^{k}\log X_{(i)}-\log X_{(k+1)}
\]

is an ordinary smooth composition. Autodiff adds no estimator beyond differentiating the selected
samples. At a rank or threshold crossing it is non-smooth; with finite trajectories, parameters may
also change whether a rare event occurs at all. A pathwise derivative conditioned on the observed
top-$k$ set does not correct missing support, threshold-selection bias or long-range dependence.

The generic neighborhood is already strong:

- [Pareto GAN](https://proceedings.mlr.press/v139/huster21a.html) uses EVT-aware architecture and
  metric choices for heavy-tailed generation;
- [tail-calibrated training](https://arxiv.org/abs/2506.13687) studies weighted scores and a tail-
  miscalibration regularizer, including the center--tail tradeoff;
- [CVaR-GPA](https://arxiv.org/abs/2608.11544) derives empirical-measure subgradients and a
  Wasserstein flow for extreme-event fine-tuning; and
- [kernel-score calibration](https://proceedings.mlr.press/v258/su25a.html) already calibrates an
  inexact differentiable stochastic simulator from output data with frequentist uncertainty and a
  stochastic-volatility example.

EcoMD's own historical Hill number is additionally burn-in contaminated. Optimizing it now would
target a known defective evaluation lineage unless a new estimator, support and holdout contract
were frozen first.

### 4.3 Verdict

**`not_trigger`.** A soft sort, top-$k$ derivative or CVaR penalty is an implementation choice in an
occupied field. Re-entry requires a tail-gradient estimator with new correctness or lower-bound
theory at support changes and dependent paths, not merely another differentiable loss.

## 5. Laboratory-market portfolios improve truth assets but not EcoMD validity

### 5.1 Halim dark-trading archive

[Halim et al.](https://doi.org/10.1093/ej/ueaf007) study lit-only versus lit-plus-dark trading under
low versus high information concentration. The [CC-BY-4.0 replication
archive](https://zenodo.org/records/14671457) contains raw order, transaction and lifecycle tables,
programs, instructions, analysis code and ethics material for sixteen sessions. A metadata- and
schema-only inspection found a materially better event contract than most laboratory assets.

It still fails the joint gate:

1. the paper and package do not establish randomized assignment of market sessions to the four
   treatment cells;
2. all reported treatment effects are already public and no untouched whole-source confirmation
   partition exists;
3. no independent group supplies the same midpoint, quantity-only dark-pool mechanism with the same
   event grammar; and
4. a lit/dark exchange rule is not an input native to the existing continuous latent-force EcoMD
   transition.

No outcome row was opened.

### 5.2 Huber multi-site replication is an old route duplicate

The strongest apparent new asset was [Huber et
al.](https://www2.uibk.ac.at/downloads/c4041030/wpaper/2024-12.pdf): 166 markets, several sites,
preregistration and within-session random assignment between paired treatments. This is meaningful
experimental infrastructure, but it was already audited and terminalized as route
`kls_self_control_independent_replication_near_pair` on 2026-08-25. The original and replication
market implementations differ in best-offer and marketable-order semantics; the focal treatments
are pre-market excitement or self-control manipulations, not exchange-rule actions; the OSF outcome
asset had no public reuse licence in the prior audit; and the published replication cannot serve as
a sealed future confirmation source.

Rediscovering its sample size does not reopen the route. It also provides only two behavioral
intervention families rather than Cycle 16's required portfolio of independent, common-action
policy environments.

### 5.3 Verdict

Halim is **`partial_capability`** as a replayable laboratory source, but not a qualified trigger.
The Huber lead is a **route duplicate**, so it receives no new candidate status. A multi-lab paper
would still compare incompatible treatment semantics and would not validate EcoMD's response to one
common legal action.

## 6. Stylized-fact reachability is a useful diagnostic, not yet a paper

### 6.1 Frozen question

Before expensive training, can one certify that a target vector of market summaries is unattainable
by a differentiable simulator family?

Let

\[
\mu(\theta)=E_\theta[S(X)],\qquad \mathcal M=\{\mu(\theta):\theta\in\Theta\}.
\]

A vector $v$ satisfying

\[
v^\top s_\star > \sup_{\theta\in\Theta}v^\top\mu(\theta)
\]

is a valid separating certificate that $s_\star$ lies outside the closed convex hull of
$\mathcal M$. This gives a clean training-before-compute diagnostic in idealized settings.

### 6.2 Why the certificate is insufficient

The certificate cannot distinguish a target in
$\operatorname{conv}(\mathcal M)\setminus\mathcal M$, which is exactly possible for a nonconvex
neural simulator family. Gradient optimization only lower-bounds the unknown support function and
therefore cannot certify its supremum. A local Jacobian or Fisher matrix describes the tangent
space near one parameter value, not global attainability. Adding interval verification would return
to generic neural reachability and become intractable for a long stochastic simulator.

[Robust Neural Posterior Estimation](https://proceedings.neurips.cc/paper_files/paper/2022/hash/db0eac6747e3631eb91095cd76065611-Abstract-Conference.html)
already treats simulator misspecification and model criticism. The newer [preconditioned robust
NPE](https://arxiv.org/abs/2602.18004) directly targets incompatible observed summaries and extreme
prior-predictive simulations. Kernel two-sample model criticism, overidentifying-moment tests and
simulation-based calibration are further direct parents. The linear separation identity is useful
but elementary; it does not establish a new global certificate.

### 6.3 Verdict

**`not_trigger`.** Preserve the support-function inequality as an outcome-blind diagnostic, but do
not call a locally optimized witness an impossibility certificate. Re-entry requires a computable
global certificate with finite-simulation coverage for a declared nonconvex stochastic-simulator
class, plus a matching hardness or incompleteness boundary and validation on two systems.

## 7. Trigger decisions

| Audited object | Decision | Genuine update | Fatal weakest link |
|---|---|---|---|
| Slow-memory random-batch correction | `not_trigger` | Artificial-heating correction and neural RBM applications are now explicitly in the parent set. | Memory is Markov after state augmentation; no correction or theorem uniform in the slow limit. |
| Fluctuation-aware population-size transfer | `not_trigger` | Mesoscopic SDE discovery and learned RG small-to-large transfer are direct parents. | EcoMD particle count is not a market-native, refinement-invariant control. |
| Differentiable tail-functional calibration | `not_trigger` | Current EVT, tail-score, CVaR-flow and kernel-score methods cover the obvious construction. | Top-(k) autodiff does not solve rare-event support, dependence or threshold changes. |
| Halim laboratory dark-market asset | `partial_capability` | Licensed order-level lifecycle and programs exist. | No documented treatment assignment, untouched confirmation, same-mechanism replication or EcoMD action map. |
| Huber multi-site replication | route duplicate | Large randomized multi-site asset was correctly recognized. | Already closed; behavioral action semantics, licence, implementation mismatch and contamination remain. |
| Stylized-fact attainable-set certificate | `not_trigger` | A convex support-function witness is a reusable pretraining diagnostic. | It cannot certify nonconvex reachability, and simulator misspecification/model criticism is occupied. |

No row removes a recorded blocker. `candidate_harvest_authorized` remains false.

## 8. Compute decision

There is no scientifically identified experiment to run. The current machine decision authorizes
only unrelated Paper D work. Therefore this audit made:

- zero SSH connections to `100.113.230.38`, `100.80.236.112` or `100.123.220.57`;
- zero EcoMD code or configuration changes;
- zero simulator or model executions;
- zero empirical outcome reads; and
- zero A800 or V100 GPU allocations.

Writing a three-server plan before a topic passes would create activity without information. More
seeds cannot repair a missing theorem, native control or intervention truth asset.

## 9. Exact re-entry conditions

Review this family again only if one concrete object exists in writing before candidate harvesting:

1. **RBM:** a new estimator and bound uniform in a declared slow-memory limit, irreducible to
   augmented-state mixing, variance correction, momentum, reshuffling, adaptive thermostats and
   control variates;
2. **scale:** an economically observable population unit plus a response invariant to splitting,
   density, clock and observation-map refinements, or a new generic finite-size theorem false for
   mesoscopic SDE, graphon and neural-RG parents;
3. **tail:** a calibrated tail-gradient estimator through rare-event support changes with dependent-
   path bias, variance and cost theory;
4. **truth asset:** one assigned legal market action, complete replay state and lifecycle, reuse
   rights, untouched confirmation and independently governed same-semantics replication; or
5. **reachability:** a global finite-simulation certificate for a nonconvex stochastic simulator,
   with coverage and a matching hardness boundary.

A qualifying object would permit a bounded D-minus-3 child screen only. It would still not authorize
implementation or GPU work without a topic card and a new current machine decision.
