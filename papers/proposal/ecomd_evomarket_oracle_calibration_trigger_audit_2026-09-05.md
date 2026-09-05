# EcoMD EvoMarket oracle-calibration and mechanism-attribution trigger audit

**Date:** 2026-09-05  
**Archetypes:** `simulator_method`, `measurement_method`  
**Decision:** `not_trigger`  
**Candidate harvesting:** not authorized  
**Outcome access, implementation, EcoMD execution, SSH, and GPU work:** not authorized

## 1. Executive decision

Three recent and directly relevant sources were screened because they appear to cover the most
plausible remaining EcoMD exits around calibration and mechanism attribution:

1. [EvoMarket](https://arxiv.org/abs/2604.18046) performs Oracle-guided in-run LOB
   self-calibration and presents event-study-style interventions;
2. [PosEDO](https://arxiv.org/abs/2601.19481) performs online regime-aware black-box simulator
   parameter calibration and was revised on 2026-09-01;
3. [Chen (2026)](https://arxiv.org/abs/2606.23158) directly decomposes selection,
   price formation, behavioral bias, and consensus topology in an evolutionary market ABM.

None is a qualified re-entry trigger. EvoMarket supplies an especially useful counterexample: its
calibrator reads the next historical target snapshot and inserts corrective orders into the same
book whose intervention response is later plotted. In the simplest local representation, the
recorded intervention response is a mixture of the autonomous simulator response and the Oracle
target response. Perfect tracking eliminates the autonomous response completely. Because the
post-intervention target perturbation is specified by an analyst-chosen Gaussian variance law, it
cannot identify a market counterfactual.

This is a scientifically important validity failure, but the underlying attenuation identity is
elementary feedback algebra. The obvious repair--restrict calibration to directions orthogonal to
the intervention response--reduces to known input-rank/persistent-excitation conditions in the
linear case and to the already recorded off-support twin in the unrestricted nonlinear case.
Without independent assigned response truth, it cannot establish which response was preserved.

PosEDO makes a differentiable EcoMD online-calibration paper less novel, not more: it already owns
observation-driven regime detection and posterior-assisted parameter adaptation on two financial
or economic simulators. Its planted regimes and evaluation truth are simulator-generated, so it
does not validate a mechanism change in a real market. Chen, together with the prior
[Hashimoto--Izumi component-factorization study](https://arxiv.org/abs/2507.09863), directly
occupies controlled simulator-internal mechanism decomposition. A factorial or gradient-based
EcoMD version would be an incremental diagnostic and would inherit the repository's quarantined
stylized-fact evidence and missing external response truth.

No new route node, machine card, experiment plan, or compute authorization is warranted.

## 2. Frozen question contract

### 2.1 Oracle-guided self-calibration

**Market-native object.** The law of a recorded LOB response to one declared executable order or
rule intervention when a feedback calibrator also submits state-changing orders.

**Rival explanations.** Under H1, online correction reduces factual tracking error while preserving
the simulator's autonomous intervention response. Under H0, the correction controller absorbs,
attenuates, or replaces that response, so the plotted effect depends on controller gain and Oracle
construction rather than on the market model alone.

**Cheapest discriminator.** Derive the response as a function of the controller and target before
running either simulator. A positive invariance result would justify a bounded benchmark. A null
result is valuable because it prevents target tracking from being reported as counterfactual
fidelity.

### 2.2 Online regime calibration

**Market-native object.** A change in the equivalence class of market mechanisms that generates an
incoming observation law, not merely a change in a fitted parameter vector.

**Rival explanations.** Under H1, a posterior shift identifies a mechanism-regime change. Under H0,
it detects only a change in observational compatibility; observationally equivalent parameter
changes are invisible and nuisance or omitted-state changes can imitate a mechanism change.

**Cheapest discriminator.** Test injectivity of the parameter-to-observation law before treating a
change-point score as mechanism attribution. Both results matter: an identifiable quotient could
support calibration, while non-identification closes the scientific interpretation.

### 2.3 Mechanism decomposition

**Market-native object.** A transportable response of an external market observable to one lawful
mechanism change, conditional on the complete prestate and other mechanisms.

**Rival explanations.** Under H1, simulator-internal ablations reveal separable market mechanisms.
Under H0, they reveal only sensitivity of one programmed simulator and chosen proxy; changing the
implementation, proxy, or interaction terms can reverse the ranking.

**Cheapest discriminator.** First check direct-work collision and external same-action truth. A
factorial sweep is not warranted if the broad decomposition is occupied and no field response is
observable.

## 3. What EvoMarket actually conditions on

EvoMarket defines a level-1-to-level-L aggregate LOB snapshot and, at checkpoint `t_k`, queries an
Oracle for the reference snapshot at the future recording time `t_{k+1}`. It computes the gap,
greedily synthesizes corrective orders, submits them to the exchange, advances the kernel, and
records the next snapshot. The paper explicitly states that snapshot tracking is small by
construction.

Under an intervention with total volume `V`, the historical target is replaced by

\[
 \widetilde L_{k+1}=L^\star_{k+1}+\epsilon_k,
 \qquad
 \epsilon_k\sim\mathcal N(0,\sigma^2(V)I),
 \qquad
 \sigma^2(V)=\sigma_0^2+\alpha V
\]

as one example. The event-study demonstration injects a step jump and then performs ten calibrated
runs using noisy post-event targets. The source therefore exposes the key ambiguity rather than
resolving it: neither `sigma_0`, `alpha`, nor the Gaussian direction law is a measured
counterfactual market response.

The v1 arXiv source archive was also checked. It contains the main TeX file, bibliography, and
figures, but no code or supplementary artifact despite the main text referring to supplementary
diagnostics. This limits executable verification, but it is not the decisive blocker: source code
would not turn an analyst-chosen target law into counterfactual truth.

## 4. Exact feedback-attenuation identity

Let `z(a)` be the next observable snapshot produced by the uncorrected simulator under intervention
`a`, let `r(a)` be the Oracle target, and consider the local additive correction

\[
 c(a)=K\{r(a)-z(a)\},
 \qquad y(a)=z(a)+Gc(a),
\]

where `G` maps a corrective order into the recorded snapshot and `K` is the controller. For a
baseline `a_0`, direct substitution gives

\[
 \boxed{
 y(a)-y(a_0)
  =(I-GK)\{z(a)-z(a_0)\}
   +GK\{r(a)-r(a_0)\}.}
\]

This identity needs no stochastic or asymptotic approximation. It yields four immediate
consequences.

1. **Perfect tracking replaces the simulator response.** If `GK=I`, then
   `y(a)-y(a_0)=r(a)-r(a_0)`; the autonomous response `z(a)-z(a_0)` disappears.
2. **A factual target attenuates interventions.** If the same historical reference is used for both
   regimes, then the recorded response is `(I-GK)` times the simulator response and is zero under
   perfect tracking.
3. **A perturbed Oracle programs the residual.** If the target difference is an analyst-selected
   noise or shock law, its mean and covariance enter the recorded effect through `GK`. Repeated
   runs estimate sensitivity to that selected law, not a missing real-market potential outcome.
4. **Arbitrary response construction is possible.** Whenever `GK` is invertible on the recorded
   subspace, a desired response `d` can be obtained by choosing

   \[
    r(a)-r(a_0)=(GK)^{-1}\{d-(I-GK)[z(a)-z(a_0)]\}.
   \]

Thus low factual tracking error and valid interventional response are logically distinct. This is
not an allegation about every possible EvoMarket implementation; it is an explicit admissible
local case sufficient to refute a generic preservation claim. Nonlinear corrections replace the
matrices by local Jacobians and retain the same first-order obstruction.

## 5. Why the obvious ICLR repair is not open

One might train a correction operator whose image avoids an intervention-response subspace. For a
finite linear system, however, learning that subspace requires a full-rank input design or the
corresponding persistent-excitation condition. If the probes do not span it, response operators
that agree on every calibration probe can disagree on an unprobed intervention. If they do span
it, the recovery is standard linear system identification plus independent validation.

For an unrestricted nonlinear simulator and a finite calibration family, two mechanisms can agree
on all calibrated trajectories and differ arbitrarily off that support. A learned projector,
penalty, adversary, or controller-gain sweep cannot select the real continuation without another
assumption or response source. Reusing the same simulator to synthesize and validate interventions
is the inverse-crime form of the problem. Anytime-valid confidence intervals can certify a declared
simulator-native intervention distribution, but do not convert it into field validity.

Consequently, the following proposed papers are killed:

| Proposed direction | Hard reason | Decision |
|---|---|---|
| Intervention-orthogonal EcoMD calibration | Linear core is persistent excitation; nonlinear core has an off-support twin; no independent response truth | Kill |
| Controller-gain causal certificate | Gain decomposition is the boxed algebra; it measures controller dependence, not the correct market response | Kill |
| Learn the Oracle noise law from factual LOBs | One realized regime does not identify the alternative-regime target law | Kill |
| Benchmark EcoMD against EvoMarket interventions | The actions, hidden state, and Oracle-conditioned outcomes are not a frozen common estimand | Kill |

## 6. L2 correction does not complete the market state

EvoMarket's correction objective minimizes the number of orders needed to transform one aggregate
snapshot into another. The paper itself notes that the constraint can be infeasible because
snapshots discard queue-level details and therefore relaxes the objective over chosen L2 features.

Two full books can have the same displayed price and aggregate depth while differing in order IDs,
owner, queue age, reserve interest, and scheduled cancellations. Corrective orders can place both
books in the same aggregate L2 fibre while their next cancellation, fill, and strategic-response
laws differ. Exact Markov preservation would require equal transition rates from every hidden
microstate in one fibre to every other aggregate fibre--the classical strong-lumpability
condition already recorded in `l2_order_identity_lumpability_taxonomy`.

Counting order messages is also not an economic perturbation norm unless maximum size, ownership,
capital, cancellations, and order-splitting semantics are frozen. One large order and several
economically equivalent children receive different costs. A Wasserstein or learned edit metric can
change the representation, but cannot recover discarded identity or establish future-law
equivalence. This closes an L2 minimal-order-distance paper as either an inverse problem under
hidden state or an application of existing projection/lumpability machinery.

## 7. The complexity comparison changes the task

EvoMarket counts its method as `O(1)` in full simulator runs, while external calibration uses `N`
full runs and may face a `(1/epsilon)^d` covering number. These costs do not concern the same
estimand:

- external calibration searches for a parameterized generator whose autonomous output matches a
  target;
- in-run correction queries future target states and injects additional orders into the generated
  trajectory.

The latter may be computationally useful as controlled replay, but it pays for checkpoint-wise
Oracle access and state feedback rather than solving the former inference problem. The covering
number of a `d`-dimensional region is not, without a declared adversarial function class and
accuracy criterion, a general lower bound on every black-box calibration algorithm. Conversely,
one-run counting suppresses dependence on checkpoints, assets, depth, corrective messages, and
target acquisition. Therefore the reported comparison does not establish a generic complexity
separation from parameter calibration.

## 8. PosEDO closes the online-calibration novelty exit

PosEDO formulates online calibration as an observation-driven dynamic optimization problem, learns
an observation-conditioned posterior over simulator parameters, uses posterior shifts for regime
detection, and uses posterior samples to reinitialize evolutionary search. Its tests plant parameter
changes in the Brock--Hommes and PGPS simulators, then evaluate against those simulator-generated
change points and replay trajectories. This is a legitimate algorithmic benchmark, but not an
independent market-mechanism truth source.

The identification floor is immediate. If two parameter values satisfy

\[
 P_\theta(X_{1:T})=P_{\theta'}(X_{1:T}),\qquad \theta\ne\theta',
\]

then no detector using `X` can distinguish a planted change `theta -> theta'` from no change. The
identifiable object is at most the observational equivalence class `[theta]`, not the parameter
name or economic mechanism. Conversely, omitted exogenous state can change the observation law
without the programmed mechanism changing. PosEDO does not claim to solve this general
identification problem, and no identifiability analysis was found in the paper.

Accordingly, replacing its evolutionary search by differentiable EcoMD gradients, adding a neural
posterior, or using online change points is not a new ICLR principle. A quotient-aware calibration
method would still need a nontrivial recovery or abstention guarantee and external response truth;
those blockers are unchanged.

## 9. Mechanism decomposition is directly occupied

Chen varies four programmed mechanisms one at a time in an evolutionary ABM and uses paired seeds,
sign tests, and bootstrap intervals to associate them with strategy entropy/cycling, a five-fact
realism score, and a genomic fragility proxy. Hashimoto and Izumi had already incrementally added
behavioral components and used optimal transport to attribute power-law similarity, including
joint effects.

This is almost exactly the broad historical EcoMD mechanism-attribution narrative. Chen also states
the appropriate limits: one simulator, synthetic or semi-historical scenarios, single-factor
sweeps, a structurally unreachable stylized fact, proxy rather than systemic fragility or ESS, and
several weak or null effects. A full factorial can reveal interactions inside EcoMD, and automatic
differentiation can estimate local sensitivities more cheaply, but neither establishes that the
same intervention causes the same response in a market or another simulator.

The current repository has an additional evidentiary problem: the former Pareto ceiling and
mechanism story used a Zumbach component now quarantined by the orientation audit. Re-running the
same ablation family with a repaired score would be evaluator maintenance, not an unoccupied
scientific contribution. Therefore mechanism decomposition, gradient attribution, factorial
interaction maps, and selection-versus-realism studies are all killed as present ICLR topics.

## 10. Decision matrix

| Candidate | New capability supplied | Fatal weakest link | Decision |
|---|---|---|---|
| Oracle-safe counterfactual calibration | No; future-target feedback is exposed | Intervention response is controller/Oracle dependent | `not_trigger` |
| L2 minimal corrective-flow geometry | Aggregate edit construction | Hidden-state fibre and action-unit non-invariance | `not_trigger` |
| Differentiable online regime calibration | PosEDO supplies direct algorithmic parent | Simulator-planted truth and parameter non-identification | `not_trigger` |
| EcoMD mechanism separability | Direct 2025/2026 market-ABM parents | One-programmed-model sensitivity, no external same-action truth | `not_trigger` |
| Multi-asset correlation emergence | Configurable coupling exists | EvoMarket explicitly does not match an empirical correlation target | `not_trigger` |

No candidate survives the weakest-link screen. There is no machine card and no reason to consume
the A800 or either V100.

## 11. Re-entry condition

Re-audit only when one method simultaneously provides:

1. a theorem or estimator with nontrivial finite-sample upper and separating lower bounds beyond
   the feedback identity, persistent excitation, ordinary system identification, and off-support
   non-identification;
2. online calibration that preserves a declared intervention response without querying its future
   outcome or programming its target law;
3. complete state and executable action semantics, rather than only an aggregate L2 fibre;
4. exact-response validation on two independent non-EcoMD truth systems; and
5. an untouched, lawfully usable market confirmation family with the same prestate, action, clock,
   and response estimand.

Another Oracle noise schedule, controller ablation, differentiable optimizer, posterior head,
factorial EcoMD sweep, stylized-fact table, cross-asset heatmap, or L2 edit metric is not a trigger.

## 12. Governance result

- `decision: not_trigger`
- `removed_blockers: []`
- `candidate_harvest_authorized: false`
- `outcome_accessed: false`
- no graph node because the formulation is an exact descendant of existing failed-closed routes
- no implementation, simulator execution, SSH, or GPU use
- discovery validator: 630 evidence records, 85 re-entry trigger audits, zero qualified
- route graph unchanged: 251 nodes, 270 edges, 964 evidence/artifact locators
- all 78 focused discovery and route-graph tests passed
