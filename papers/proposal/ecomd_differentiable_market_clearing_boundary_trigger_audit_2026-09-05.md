# EcoMD differentiable market-clearing boundary trigger audit

**Date:** 2026-09-05  
**Stage:** post-closure re-entry trigger screen  
**Archetype:** `measurement_method`, with `simulator_method` and discrete-optimization rescues tested  
**Decision:** `not_trigger`  
**Candidate harvesting:** not authorized  
**Outcome access, implementation, simulation, SSH, and GPU status:** none

## 1. Decision first

[Mungo, Scholl, and Quera-Bofarull (2026)](https://arxiv.org/abs/2609.02646), submitted
after the repository's differentiable-market closures, is a useful and unusually transparent stress
case. It differentiates a convex DC optimal-power-flow clear and then optimizes a mixed
continuous/discrete data-center siting objective. Its gradients are accurate inside fixed clearing
regimes, while the reported plans switch site support too late.

That juxtaposition does **not** establish a new EcoMD topic. The paper contains two mathematically
different boundaries:

1. an **inner clearing active-set boundary**, where a transmission limit or generator offer segment
   changes status and the LMP solution map may be nonsmooth; and
2. an **outer site-support boundary**, where an exact fixed charge changes the preferred subset of
   active sites.

The paper's systematic planning error is explicitly traced to the second boundary: its smooth
site-count surrogate prefers to shrink a site rather than pay the exact charge and then develops a
bistable barrier. It is not evidence that the implicit gradient through DC-OPF failed. Conflating the
two would produce a false mechanism claim.

After separating them, the apparent residuals reduce to established active-set sensitivity,
perturbed/proximal differentiation, combinatorial backward surrogates, mixed-integer search, and
generic gradient-plus-optimization benchmarking. The source is therefore a reusable negative-control
fixture, not a qualified re-entry trigger. No experiment plan or compute authorization is created.

## 2. Frozen question contract

### Market-native object

The object is the exact planning decision induced by repeated market clearing: allocation of a fixed
load across candidate buses, cleared nodal prices, and the discrete set of built sites.

### Rival explanations

- **H1 -- inner-gradient failure.** Optimization fails near the best plan because implicit
  derivatives of cleared prices become inaccurate or undefined when congestion or offer active sets
  change.
- **H0 -- outer-objective mismatch.** Market gradients correctly optimize the continuous energy
  term, but the chosen smooth/straight-through representation is not the exact fixed-charge
  objective and therefore moves the support breakpoint.

### Discriminating result

Hold the market-clear oracle fixed and separately intervene on (i) the inner derivative rule and
(ii) the outer support rule. If exact support enumeration or a discrete step removes the lag while
changing the clearing derivative does not, H0 wins. If decision error tracks clearing KKT margins
after exact support control, H1 remains viable.

A positive H1 result would expose a failure mode of differentiable optimization layers. A null H1
result is equally valuable because it prevents support-relaxation error from being misreported as
market-gradient error. The new paper already supplies decisive evidence for H0 on its two instances.

## 3. What the new paper actually establishes

For allocation `q`, operating state `s`, and cleared LMP vector `lambda_s(q)`, its exact physical
objective is

\[
  J(q;\kappa)=\frac{1}{|\mathcal S|}\sum_s q^\top\lambda_s(q)
  +\kappa\lVert q\rVert_0.
\]

The inner clear uses strictly convex piecewise-quadratic generation costs, balance equations,
generator bounds, and line limits. DiffOpt.jl over Ipopt supplies the reverse pass. The experiment
allocates 50 MW across six candidate buses and 36 operating states in one 12-node Erdos--Renyi
instance and one 12-node GeoDe instance.

The discrete count is not differentiated exactly. The allocation is parameterized by a softmax and
the count is replaced by

\[
  K_\tau(w)=\sum_i [1-\exp(-w_i/\tau)].
\]

The forward count temperature is 0.02, while a straight-through backward temperature is annealed
from 2.0 to 0.2. Five near-uniform Adam initializations are run for 450 iterations. Loads below 1 MW
are then discarded, the remaining allocation is renormalized and refined, all states are re-cleared,
and the lowest exact post-commit objective is reported. The numerical reference enumerates all 63
nonempty supports and solves each conditional continuous problem numerically.

The largest reported positive objective gaps are 2.3% and 8.5% of the corresponding one-site energy
spread. Appendix C directly evaluates the terminal smooth objective along a path between the best
one- and two-site allocations. The surrogate collapse occurs at normalized fixed costs about 0.049
and 0.13, whereas the exact support breakpoints are about 0.032 and 0.090. The trained paths follow
the surrogate curve. Near collapse, its two-site and one-site states are separated by a barrier, and
late annealing explains the residual tail. This is an attribution to the supplied outer objective,
not an inference from coincident gradients.

The gradient study is careful but narrower. There are 972 directional checks per topology family,
and stable checks require the stencil center and endpoints to share an active-set signature. The
paper also locates 18 active-set transitions per family and performs one-sided checks rather than
asserting a derivative at the boundary. At requested distance `1e-3`, a narrow GeoDe offer regime
has maximum relative discrepancy 0.334, and unresolved sides are excluded rather than counted as
successes. Those are honest numerical limitations. They do not explain the measured support lag.

## 4. Exact two-boundary decomposition

Write the continuous cleared-energy term as

\[
  E(q)=|\mathcal S|^{-1}\sum_s q^\top\lambda_s(q).
\]

Let `A(q)` denote the collection of binding line limits and active offer intervals. On a
nondegenerate region where `A(q)` is fixed, the KKT system gives a locally differentiable `E`.
Crossing an inner boundary can change its Jacobian or make the point derivative set-valued. This is
the ordinary parametric-programming issue tested by the one-sided finite differences.

Now impose a physical commitment floor `delta` and let `S` be a fixed site support. Define

\[
  V_S=\min\{E(q):\sum_iq_i=D,\ q_i\geq\delta\ (i\in S),\ q_i=0\ (i\notin S)\}.
\]

The exact outer problem is

\[
  \min_{\varnothing\ne S}\;V_S+\kappa |S|.
\]

On the relative interior of any fixed-support stratum, `kappa |S|` is constant, so every continuous
derivative of the exact fixed-charge term is zero. A switch from support `S` to `T` is instead
determined by the global value comparison

\[
  V_S+\kappa|S|=V_T+\kappa|T|.
\]

Consequently, even a perfect inner gradient cannot reveal the value of an unvisited support. A
method must inject nonlocal information through enumeration, branching, a discrete neighborhood,
random perturbation, or a relaxation. Once a relaxation is chosen, its temperature and off-support
extension define a different optimization problem. The observed lag is exactly this difference.

This argument is a useful killer lemma but not a new optimization theorem: local derivatives cannot
solve an exact fixed-charge comparison because the charge is constant on each stratum. It is the
standard reason mixed-integer search or an explicitly declared surrogate is necessary.

## 5. The proposed trajectory-conditioned audit is insufficient

One tempting paper would compare random-point gradient accuracy with gradient accuracy on the
states visited by an optimizer, stratified by KKT margin or distance to an active-set boundary.
That measurement is sensible QA. It does not survive the ICLR irreducibility gate here.

First, it targets the wrong cause of the headline error in the new paper. Second, the paper already
performs one-sided boundary checks, and generic end-to-end optimization convergence is an explicit
part of [Mosaic](https://arxiv.org/abs/2606.27895), alongside finite-difference accuracy,
conditioning, cost, and compatibility. Third, a measure-zero nondifferentiability set can certainly
be visited or approached by an optimizer, so random-point accuracy alone is not a decision theorem;
but merely changing the test distribution from random inputs to training trajectories is an
evaluation refinement, not a new learning method.

A publishable residual would require more than a boundary heat map. It would need a decision-risk
certificate that connects observable active-set margins, solver tolerances and update sizes to exact
downstream regret, plus a matching lower bound outside its assumptions. No such result was derived
in this screen.

## 6. Direct collision map

| Primary work | Occupied object | Consequence for the proposed escape |
|---|---|---|
| [OptNet](https://proceedings.mlr.press/v70/amos17a.html) and differentiable convex layers | KKT/implicit differentiation of convex programs | Differentiating the continuous clear is established infrastructure. |
| [PEAR](https://arxiv.org/abs/2605.01361) | Active-set tangent-space characterization of regret gradients under local stability, with decision-regret evaluation | A local active-set geometry or decision-gradient interpretation is directly occupied. |
| [dQP](https://arxiv.org/abs/2410.06324) | Solver-agnostic QP differentiation from the recovered active set, with active-set refinement and benchmarks | Reconstructing and checking active sets is not a new method. |
| [LPGD](https://proceedings.mlr.press/v235/paulus24a.html) | Re-running a solver on perturbed inputs to replace degenerate optimization-layer derivatives; unifies several predecessors | “Use an extra branch/perturbed solve near a bad boundary” is a direct special case unless a new guarantee remains. |
| [Perturbed optimizers](https://proceedings.neurips.cc/paper/2020/hash/6bb56208f672af0dd65451f869fedfd9-Abstract.html) and [Identity with Projection](https://arxiv.org/abs/2205.15213) | Differentiable replacements for zero or undefined discrete-solver derivatives | A new straight-through temperature or projected backward rule is occupied and representation-dependent. |
| [Differentiable Feasibility Pump](https://arxiv.org/abs/2411.03535) | Gradient interpretation of relaxation-plus-rounding and a differentiable rounding/feasibility loss for MILPs | Relax, round, commit, and refine is not an empty algorithmic category. |
| [Gradient plus primitive directions](https://arxiv.org/abs/2407.14416) | Alternating continuous gradient steps with exact discrete-neighborhood searches, with convergence results | Separating continuous placement from discrete support search is already an explicit method family. |
| [Mosaic](https://arxiv.org/abs/2606.27895) | Common forward/VJP/finite-difference/cost/conditioning/optimization benchmark across 14 solvers | A market-clearing-only gradient benchmark is a domain addition, not an irreducible benchmark contribution. |

The repository's prior
[straight-through trigger audit](ecomd_reentry_trigger_scan_round2_2026-09-04.md) adds a stronger
representation gate. Two smooth backward extensions can agree on every reachable discrete forward
state yet return arbitrary, even opposite, surrogate gradients. The new paper's distinct forward and
backward temperatures are a declared heuristic choice, not a gradient of the exact fixed-charge
objective. Exact forward evaluation therefore cannot canonize that backward rule.

## 7. EcoMD transfer test

The source does not reopen the closed `conservative_differentiable_transaction_integrator` route.
Exact price-time-priority allocation still changes discontinuously at ties, and conservation still
does not identify an allocation or price. Replacing a hard market event by a soft backward pass
inherits the off-state-extension nonuniqueness above.

It also does not reopen the `coupling_invariant_differentiable_market_counterfactual` route. A
gradient of a synthetic DC-OPF planning objective is neither an identified real-market intervention
response nor a coupling-invariant individual counterfactual. The paper evaluates two synthetic
network instances and does not provide an assigned market outcome or an independent same-estimand
truth system.

Finally, an attribution cube that crosses inner derivative, outer support surrogate, and
post-commit refinement would be scientifically clean but not a separate ICLR contribution. It would
repeat the causal-attribution logic already used by Paper D and diagnose a mechanism the source's
Appendix C has already isolated. More networks and seeds could improve the source's evidence; they
would not create a new EcoMD method.

## 8. Gate decision

| Gate | Result |
|---|---|
| Genuine post-closure primary source | Pass: arXiv v1 submitted 2026-09-02 |
| Same native object and rival explanations | Pass after separating inner active set from outer support |
| Headline error attributable to inner gradient | Fail: direct path evaluation attributes it to the outer surrogate |
| Exact support choice recoverable from local exact gradient | Fail: the fixed charge is constant on each support stratum |
| Boundary-conditioned benchmark irreducible | Fail: one-sided checks, active-set methods, decision regret and Mosaic-style optimization audits are established |
| Hybrid perturb/branch/discrete rescue irreducible | Fail: LPGD, perturbed optimizers, feasibility-pump and primitive-direction parents |
| EcoMD preserves the same truth contract | Fail: different hard-event semantics and no external market counterfactual |
| Two independent same-estimand truth systems | Fail |
| Recorded blocker removed | Fail |

**Decision:** `not_trigger`, `removed_blockers: []`, and
`candidate_harvest_authorized: false`. This screen concerns already closed formulations, so it does
not create a new route-graph node.

Re-entry requires a theorem or algorithm that simultaneously:

1. keeps the inner clearing active set and outer discrete support mathematically separate;
2. gives an observable, decision-conditioned regret or abstention certificate across active-set
   changes, with a matching lower bound outside its assumptions;
3. cannot be represented as classical critical-region sensitivity, LPGD/perturbed solving,
   projected/straight-through differentiation, feasibility-pump logic, or mixed-integer discrete
   search;
4. is validated against exact decision truth on at least two independent optimization-system
   lineages and hard negative regimes; and
5. preserves a market-native action and outcome contract before any EcoMD application.

A code release, more synthetic networks, another gradient heat map, or adding EcoMD as one backend
is not such a trigger. Until the stated condition is met, the A800 and both V100 workers remain idle
for this route.
