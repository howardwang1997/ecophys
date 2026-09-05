# EcoMD RetailAgent and dormant-reporter trigger audit

**Date:** 2026-09-05  
**Archetypes:** `simulator_method`, `measurement_method`  
**Decisions:** two `not_trigger`  
**Candidate harvesting:** not authorized  
**Outcome access, implementation, simulation, EcoMD execution, SSH, and GPU work:** not authorized

## 1. Executive decision

Two very recent primary works create plausible headlines for an EcoMD/ICLR project:

1. [RetailAgent](https://arxiv.org/abs/2608.28399) finds stable adverse timing in
   self-conditioned multimodal LLM long/flat decisions on historical intraday paths and suggests
   studying how another participant might respond to the predictable policy.
2. [Brewster and Cluzel](https://arxiv.org/abs/2609.00725) find that small panels mixing
   high-response "promiscuous" and selective low-average-response "dormant" nodes classify
   shocks in noisy Boolean-network dynamics much better than sensitivity-ranked panels.

Neither source is a qualified re-entry trigger.

RetailAgent's primary statistic is a fixed-path covariance between a shadow position and the next
historical return. Its complementary schedule changes the sign by algebra, not by an executable
best-response experiment. A fixed historical path gives no sign bound for the same policy after
its orders change prices, other agents respond, and the policy consequently observes a different
history. The current paper states this scope correctly and leaves execution, impact, latency,
capacity, counterparties, and feedback to future work.

There is also a treatment-dependent selection issue in the memory comparison. The paper computes
timing only on stock-days containing both actions. Its table reports 1,194 of 1,500 eligible paths
for `w=0` but only 1,054 for `w=1`. Since timing is exactly zero on a constant path, zero-extending
the reported conditional means changes the contrast from `-11.3` basis points to only `-2.08`
basis points per attempted stock-day. This does not refute the authors' explicitly conditional,
descriptive result, but it prevents interpreting that contrast as a population causal effect of
memory. Principal stratification already supplies the generic correction language.

An EcoMD interactive extension would also collide directly with existing endogenous LLM asset
markets, order-book LLM market simulators, performative prediction, multi-agent policy evaluation,
and the repository's closed agent-market and prospective-simulator-validity routes. A long/flat
state is not yet an order grammar.

The dormant-reporter result is scientifically credible inside its declared simulated ensemble,
including a useful held-out-initial-condition leakage check. It does not, however, supply a market
measurement contract. "Dormant" is defined only after observing a node under all labelled shocks,
at a chosen noise level and objective; panels are optimized separately for every network and fixed
shock set. The strongest practical rule consumes condition-specific pilot means and spreads for
every candidate. In a market, LOB levels are normally already observed and are not stable physical
sensors under recentering or grid refinement; trader identities are latent and split-dependent;
and stable venue feeds would require an actual cost, rights, and labelled repeated-shock contract.
Programmed EcoMD shocks would provide only source-simulator truth.

Sparse sensor placement for classification and robust submodular observation selection already
occupy the generic algorithmic core. No new route node, machine card, experiment plan, or compute
authorization is warranted.

## 2. Frozen question contracts

### 2.1 Fixed-path adverse timing versus interactive exploitability

**Market-native object.** The executable, self-financing value or best-response regret of a frozen
stochastic LLM order policy when its own orders and legal counterparties affect the LOB transition
law.

**Rival explanations.** Under H1, negative exposure-matched timing on a passive historical path
reveals a stable policy defect that remains exploitable after transaction costs and strategic price
feedback. Under H0, the statistic is only a covariance on one no-impact path; an order adapter,
impact law, latency, policy observability, and counterparty response can erase or reverse it.

**Cheapest discriminator.** Before simulation, ask whether the fixed-path statistic yields any
nonzero lower or upper bound on executable value over a declared class of endogenous response
kernels. If not, require one frozen order policy and filtration, a common self-financing adapter,
multiple independent engines, and an external response source before making a market claim. A
positive bound could support a new certificate; a null result prevents passive-path evaluation
from being called exploitability.

### 2.2 Dormant market reporters

**Market-native object.** The smallest physically costed set of stable observables that identifies
one of several named exogenous market interventions under uncontrolled pre-state variation.

**Rival explanations.** Under H1, low-average-response but intervention-selective channels preserve
pre-state information and improve robust shock classification beyond high-sensitivity channels.
Under H0, the category is defined using labelled response outcomes, changes with the shock
ensemble and representation, and reduces to supervised feature or sensor selection.

**Cheapest discriminator.** Freeze the physical reporters, their acquisition costs, shock labels,
assignment and lifecycle before reading response outcomes; select on discovery intervention
families and test on entirely held-out interventions and an independently governed market. Both
answers matter: a positive result could establish a market measurement method, while a null result
would prevent a Boolean-network ensemble effect from becoming simulated market physics.

## 3. What RetailAgent measures

For stock-day `(i,d)`, binary long/flat position `p_t`, return `r_t`, and mean exposure
`pbar`, RetailAgent defines

\[
 A=\sum_{t=1}^T (p_t-\bar p)r_t
   =\sum_t p_t r_t-\bar p\sum_t r_t.
\]

This is `T` times the within-path empirical covariance under the corresponding normalization. It
is a useful descriptive statistic: it removes the passive component due only to average long
exposure. Shuffling the saved actions while preserving exposure largely attenuates the observed
negative value, so the intact action-return alignment is real in the archived sample.

The source also states the necessary scope limits. Prices are fixed historical paths and outcomes
are research-return labels. Matched human traces, executable returns, costs, borrowing, latency,
market impact, capacity, counterparties, and endogenous feedback are explicitly separate future
requirements. The audit therefore does not dispute the paper's scoped fixed-path claim.

### 3.1 The complementary schedule is a sign identity

For `q_t=1-p_t`, its exposure is `1-pbar`, hence

\[
 A(q,r)=\sum_t\{(1-p_t)-(1-\bar p)\}r_t=-A(p,r).
\]

This diagnostic cannot by itself establish predictability or exploitability. It uses the future
return label, does not show that a counterparty can predict the action before trading, and does not
specify size, order type, execution price, latency, borrowing, inventory, or cost. Further,
`p_t+q_t=1`; `q` is a complementary holding schedule, not automatically a zero-sum best response.

### 3.2 Exact full-attempt re-expression of the memory contrast

Let `S_c=1` when condition `c` produces a valid path containing both actions. The archived scorer
reports

\[
 \mu_c=\mathbb E[A_c\mid S_c=1].
\]

Since `A_c=0` whenever the path is constant, the zero-extended mean over every attempted stock-day
is exactly

\[
 \widetilde\mu_c=\Pr(S_c=1)\mu_c.
\]

The paper's narrative provenance table gives

| condition | attempted | both-action paths | selection rate | reported conditional timing | zero-extended timing |
|---|---:|---:|---:|---:|---:|
| `w=0` | 1,500 | 1,194 | 0.7960 | -62.8 bp | -49.9888 bp |
| `w=1` | 1,500 | 1,054 | 0.7027 | -74.1 bp | -52.0676 bp |

Thus the conditional contrast is `-11.3` bp whereas the full-attempt zero-extended contrast is
`-2.0788` bp. Memory also lowers the chance of entering the both-action sample by 9.33 percentage
points. The two quantities answer different questions. In particular,

\[
 \mathbb E[A_1\mid S_1=1]-\mathbb E[A_0\mid S_0=1]
\]

compares different post-condition populations. A causal effect among always-switching paths would
condition on the latent joint stratum `(S_0,S_1)=(1,1)`, which is not identified from the two
marginal experiments without further assumptions. This is the standard principal-stratification
problem, not a new EcoMD method. The authors already call cross-frame magnitudes descriptive, so
this is a reporting boundary rather than evidence of misconduct or a refutation of the negative
sign within each selected group.

### 3.3 Fixed-path timing has no deployment sign bound

Let a nonconstant open-loop shadow position `p` receive passive-path returns `r^0` and score `A^0`.
For any `lambda>0`, two endogenous response maps compatible with the same passive path can set,
when that policy is deployed,

\[
 r_t^{+}(p)=r_t^0+\lambda(p_t-\bar p),\qquad
 r_t^{-}(p)=r_t^0-\lambda(p_t-\bar p).
\]

Both leave the no-policy historical path unchanged. Yet

\[
 A^{\pm}=A^0\pm\lambda\sum_t(p_t-\bar p)^2.
\]

For every nonconstant action trace, choosing `lambda` can make the deployment score have either
sign and arbitrary magnitude. A one-step terminal response gives the same counterexample without
any recursion through later observations. Adding market restrictions can exclude these particular
maps, but then those restrictions--impact, information, latency, inventory, and strategic response--
become the identifying content. The passive path alone supplies none of them.

This is the market instance of the performative/off-support problem: once a deployed decision
changes the data-generating distribution, past no-deployment outcomes do not identify the new
distribution. Running only EcoMD chooses one response map rather than identifying the field map.

## 4. Direct collisions around interactive LLM markets

The suggested interactive extension is already a populated engineering and experimental area.

- [Lopez-Lira](https://arxiv.org/abs/2504.10789) implements heterogeneous LLM traders in a
  persistent order book with market and limit orders, partial fills, dividends, information sets,
  endowments, and endogenous interaction.
- [Henning et al.](https://arxiv.org/abs/2502.15800) place homogeneous and mixed-model LLM agents
  in an endogenous experimental asset market and explicitly test their behavior against human
  market evidence.
- [StockSim](https://arxiv.org/abs/2507.09255) exposes order-level and candle-level modes with
  latency, slippage, LOB microstructure, heterogeneous roles, and multi-agent coordination.
- [Performative Prediction](https://proceedings.mlr.press/v119/perdomo20a.html) already formalizes
  the general fact that deployment changes the target distribution.

EcoMD could host another interactive experiment, but "insert RetailAgent and train an exploiter"
would be a composition of these parents. It would still lack a public observation-to-order adapter,
a common filtration across engines, and external counterfactual truth. Adversarial policy search or
best-response training would estimate exploitability in the chosen game; it would not establish
that the same response occurs in a market.

The only potentially useful near-term action is a selection-aware reanalysis of RetailAgent's
released trajectories, if complete artifacts become available. That could improve reporting, but
the identity above and principal-stratification parent are far below an ICLR central contribution.

## 5. What the dormant-reporter paper establishes

Brewster and Cluzel use synchronous Boolean threshold networks with 5,000 nodes. For each network,
ten shock classes select 50 target nodes and redraw every outgoing target weight to `-1` or `+1`.
The control plus ten shocks are simulated from noisy copies of one base initial state. A random
forest predicts the class using snapshots of a selected node panel.

For node `j` and shock `q`, the paper defines

\[
 \Delta_{j,q}=\left\langle\left|\sigma_j^{(q)}-\sigma_j^{(0)}\right|\right\rangle,
 \qquad S_j=\langle\Delta_{j,q}\rangle_q.
\]

After estimating a pooled response cutoff `theta`, the response breadth is

\[
 n_j=\#\{q:\Delta_{j,q}\geq\theta\}.
\]

Nodes with `n_j=0` are unresponsive, `1<=n_j<=5` are dormant, and `n_j>=6` are
promiscuous. Thus dormant status is not an observable topology label or a condition-blind property.
It is a supervised summary relative to this shock set, control, noise level, response threshold,
and inference objective. The authors explicitly state that the labels are not immutable node
properties.

Panels are optimized separately for every network realization and fixed shock set. The main
snapshot split allows states from one initial-condition trajectory on both sides; importantly, the
authors rerun a whole-initial-condition holdout and the principal algorithm ordering changes little.
That leakage is therefore not used as a kill reason here. The transfer problem is different: the
study does not select one panel before seeing a new network or classify previously unseen shock
families.

The practical spring rule greedily raises the low tail of pairwise Mahalanobis separation. It needs
the per-condition mean and spread for every candidate--about 100 pilot replicate readouts per node
in the source's estimate. Greedy information gain performs similarly but needs joint patterns. Both
are legitimate train-rich/deploy-sparse methods; neither gives a market its missing labelled pilot
interventions for free.

## 6. Why the market mapping fails

### 6.1 No native reporter unit and cost

Four obvious mappings fail different gates.

| proposed reporter | problem |
|---|---|
| LOB price level | Public feeds commonly expose all chosen levels; recentering, tick changes, or splitting a level changes the node list and dormant label without necessarily changing the information set |
| EcoMD agent | Agent identity is simulated, exchangeable, and sensitive to behavior-preserving split/merge; the internal state is not a market-observable sensor |
| engineered feature | This is ordinary supervised feature selection, not physical reporter placement |
| venue/feed | Potentially a stable physical sensor, but requires a declared fee/latency/rights budget and synchronized labelled intervention lifecycle not currently available |

A representation-invariant claim could be made only after the reporter is tied to a physical feed
or other stable measurement endpoint with an actual cost. Selecting eight convenient LOB features
because eight nodes worked in the Boolean ensemble is not such a contract.

### 6.2 No useful repeated market shock-label contract

- Scheduled FOMC, CPI, or payroll announcements have known types before the response and differ in
  sign, surprise, content, and concurrent state. Classifying which calendar event occurred is
  trivial; treating every event of one type as the same intervention is false without a dose and
  conditioning contract.
- Unscheduled outages, halts, attacks, and failures are rare, selected, heterogeneous, and usually
  lack the complete losing/failed event lifecycle and repeated pre-state support.
- Programmed EcoMD rewiring, agent removal, or liquidity shocks can create unlimited labels, but
  then the selected reporters are optimized and validated against the same source simulator.

Consequently no current mapping supplies labelled assignment, stable treatment semantics,
independent repeated trials, a confirmation family, and a nontrivial decision use.

## 7. Generic method collision

[Sparse Sensor Placement Optimization for Classification](https://doi.org/10.1137/15M1036713)
already learns a small set of physical coordinates from labelled high-dimensional training data and
then classifies from the sparse deployment measurements. [Robust Submodular Observation
Selection](https://www.jmlr.org/papers/v9/krause08b.html) already treats max-min observation
selection across alternative objectives, robust experimental design, event/outbreak detection,
feature deletion, non-unit costs, and approximation guarantees.

In the diagonal shared-covariance case, pairwise squared Mahalanobis separation on a selected panel
is additive over reporters:

\[
 D_{q q'}(R)=\sum_{j\in R}
 \frac{(\mu_{qj}-\mu_{q'j})^2}{\sigma_j^2}.
\]

Maximizing the minimum across class pairs is therefore a robust selection problem over modular,
hence submodular, objectives. Correlated covariance and a lower quantile can make the exact spring
objective non-submodular, but simply running greedy search does not create a guarantee, and the new
paper already owns that heuristic. A potentially re-auditable mathematical residue would need a
finite-sample upper bound and separating lower bound or approximation theorem for correlated,
quantile pairwise discrimination that is false for the robust-submodular parent. It would still
need stable market reporters and external shock truth before becoming an EcoMD project.

## 8. Decision matrix

| proposed direction | new ingredient | fatal weakest link | decision |
|---|---|---|---|
| Put RetailAgent into EcoMD and measure profit | endogenous price feedback | result is chosen-simulator value; long/flat-to-order semantics and field response are absent | `not_trigger` |
| Train an EcoMD counterparty to exploit LLM timing | adversarial best response | generic multi-agent exploitability plus direct LLM-market simulators; no transport to a real market | `not_trigger` |
| Selection-aware timing metric | zero-extension/principal strata | useful reporting correction, but exact algebra plus established post-treatment stratification | `not_trigger` |
| Select dormant LOB levels | sparse interpretable panel | levels are not a native costly sensor set and shock labels/trials are missing | `not_trigger` |
| Select dormant EcoMD agents | simulator internal access | arbitrary agent unit and source-simulator truth | `not_trigger` |
| Spring-rule EcoMD benchmark | low-tail discriminability | direct application of the new paper and established sensor-selection parents | `not_trigger` |
| Correlated quantile-panel theorem | possible narrow mathematical gap | no theorem yet, unclear novelty after robust selection literature, and no market bridge | re-audit condition only |

No candidate survives the weakest-link screen.

## 9. Exact re-entry conditions

### 9.1 Interactive LLM-policy route

Re-audit only if one package supplies all of the following:

1. a frozen stochastic policy filtration and an executable, self-financing order grammar with
   size, price, cancellation, latency, inventory, borrowing, and costs;
2. a pre-action exploitability or deployment-value certificate with nontrivial finite-sample upper
   and separating lower bounds beyond passive covariance, performative prediction, ordinary OPE,
   and generic best-response learning;
3. common action semantics and complete state on at least two independent non-EcoMD engines;
4. an untouched external same-estimand response family or a deliberately simulator-native claim
   that does not imply field validity;
5. evaluation on all attempted trajectories, with policy-dependent selection either avoided or
   handled by a frozen principal-stratum/bounding analysis.

Another prompt sweep, memory window, complementary schedule, EcoMD-only opponent, profit table, or
stylized-fact plot is not a trigger.

### 9.2 Dormant-reporter route

Re-audit only if one package supplies all of the following:

1. stable physical market reporters and nonzero acquisition/latency costs that survive admissible
   grid, clock, and identity refinements;
2. named exogenous interventions with assignment, dose, complete lifecycle, pre-state, repeated
   support, rights, and an untouched independent confirmation family;
3. discovery-only reporter selection followed by whole-intervention and whole-market holdout;
4. a theorem or estimator beyond sparse classification, information gain, robust submodular
   observation selection, and the source paper's spring heuristic;
5. a positive and null interpretation that remains meaningful without EcoMD-generated labels.

Another simulated shock taxonomy, top-`k` LOB feature selector, agent-state probe, or classifier
accuracy comparison is not a trigger.

## 10. Operational decision

The two new sources remove no recorded route blocker. Therefore:

- do not create a route node or machine card;
- do not download model weights or datasets;
- do not implement a RetailAgent adapter, exploiter, reporter selector, or EcoMD shock suite;
- do not connect to the A800 or either V100 worker;
- continue the search only from a new external truth/control asset or the narrowly stated
  correlated-panel theorem trigger.

