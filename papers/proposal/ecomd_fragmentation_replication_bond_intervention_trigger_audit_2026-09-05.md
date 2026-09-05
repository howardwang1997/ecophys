# EcoMD fragmentation-replication and bond-intervention trigger audit

**Date:** 2026-09-05

**Mode:** outcome-blind primary-work, source-contract, exact-reduction, and theorem audit. This is
not a new discovery cycle and does not authorize candidate harvesting.

**Decision:** **NO QUALIFIED TRIGGER.** The fragmented-market replication is a strong public
counterexample to treating one documented agent-based model as one determinate scientific object,
but it is neither a second same-kernel truth system nor an unoccupied ICLR method. The bond RfQ
paper uses real observations and an explicit causal graph, but does not execute or validate a price
or outreach intervention, and its data are proprietary. No outcome access, implementation, EcoMD
change, SSH session, or GPU job is authorized.

## 1. Source-integrity correction

The initial batch scan attached *Causal Interventions in Bond Multi-Dealer-to-Client Platforms* to
arXiv identifier `2606.18147`. That identifier actually belongs to an unrelated wearable-health
question-answering paper. The correct preprint is
[arXiv:2506.18147](https://arxiv.org/abs/2506.18147), and the peer-reviewed primary source is the
[2026 PLOS One article](https://doi.org/10.1371/journal.pone.0341369). All claims below use the
corrected source. The mistaken identifier is not retained as evidence.

This correction matters scientifically: title--identifier joins from a bulk search result are not
primary evidence until the title, authors, abstract, and document agree.

## 2. Frozen capability claims

This audit asks whether two new sources remove a recorded blocker for an EcoMD-related ICLR paper:

1. Does an independent replication of a fragmented-market ABM supply a second same-estimand
   simulator lineage and a new discrepancy target?
2. Can the sign of a simulator conclusion be certified over every implementation compatible with
   an incomplete model description, rather than over a hand-picked implementation ensemble?
3. Does the bond MD2C study supply real intervention truth for price or client-outreach actions, or
   a public sequential RfQ problem on which EcoMD can be evaluated?

The related closed routes are
`discovery_loop_topic_cycle_8_cross_engine_discrepancy_20260826`,
`cross_simulator_disagreement_intervention_certificate`,
`task_conditioned_market_simulator_adequacy`,
`intermarket_trade_through_exclusion`, and
`prospective_counterfactual_market_simulator_validity`.

## 3. Fragmentation replication: a genuine disagreement, not independent truth

[Ratliff-Crain et al.](https://arxiv.org/abs/2604.20067) attempt an independent replication of
Wah and Wellman's 2016 fragmented-market latency-arbitrage model. This is a substantive result, not
a superficial code rerun:

- the paper tests a separately interpreted `BestGuess` implementation, a later author-lineage
  `MarketSim` codebase, and a hybrid implementation;
- it rejects quantitative alignment in every nonzero-latency setting even for its closest hybrid;
- changing only the zero-intelligence traders' greedy rule changes qualitative conclusions about
  fragmentation, execution time, and welfare; and
- it identifies an apparent order-routing bug and supplies a detailed ODD protocol.

The paper therefore provides exactly the kind of hostile example that an EcoMD simulator paper
must survive. It does **not**, however, provide a second truth system for the original conclusion.
The disputed greedy rule changes which feed the trader observes and how aggressively it prices.
Consequently the implementations have different policy information and transition kernels. Their
different responses are scientifically informative about specification sensitivity, but they are
not two independent realizations of one frozen state--action--clock--policy estimand.

The public Apache-2.0
[replication fork](https://github.com/eratlif1/market-sim-WW-replication/tree/97e876eb5279e9b303cf74355a2bd08c9ab0a7b9)
adds WW configurations and processing scripts to `MarketSim`; its Java market logic remains from
the original author lineage. The paper does not link a pinned release of the separately written
`BestGuess` implementation or the original WW run-level outcomes and random states. Thus the
source is an excellent documented hard negative, but not a two-lineage, fully executable gold
fixture.

Porting the same treatment into EcoMD would not repair this. Unless EcoMD implements the identical
trader information, action timing, matching, randomness, and response definition, it is another
mechanism. If those semantics are forced to be identical, remaining differences are conformance or
numerical errors, which is the existing Cycle 8 trilemma.

## 4. The narrow residual: conclusion invariance over incomplete specifications

A more defensible question than “which implementation is right?” is:

> Given a partial simulator specification \(S\), is the sign of a declared intervention contrast
> \(q(K)\) invariant over every legal completion \(K\in\mathcal C(S)\)?

For the fragmentation example, a query could be the sign of

\[
q(K)=\mathbb E_K[\text{surplus}\mid do(\text{two venues})]
     -\mathbb E_K[\text{surplus}\mid do(\text{one venue})].
\]

This formulation exposes a decisive coverage boundary.

### Proposition: finite implementation samples cannot certify universal specification robustness

Let an auditor execute a strict subset \(A\subsetneq\mathcal C(S)\) and observe
\(q(K)>0\) for every \(K\in A\). Without a sound coverage relation between \(A\) and
\(\mathcal C(S)\), construct two admissible worlds:

\[
\mathcal C_0=A,
\qquad
\mathcal C_1=A\cup\{K^-\},\quad q(K^-)<0.
\]

Every executed trace and statistic is identical in the two worlds, while the universal statement
is true only in \(\mathcal C_0\). Therefore no procedure using only the sampled implementations can
certify sign invariance over the undocumented completion set.

The result is elementary but fatal to the cheap proposal. A sound certificate needs either:

1. a machine-readable grammar whose denotation is exactly \(\mathcal C(S)\), followed by exhaustive
   enumeration; or
2. a proved outer approximation on which extrema of \(q\) can be bounded soundly.

The first branch meets direct parents. Complete Rashomon-set enumeration already computes all
models satisfying a declared fit/class constraint for restricted nonlinear model classes
([Xin et al., NeurIPS 2022](https://proceedings.neurips.cc/paper_files/paper/2022/hash/5afaa8b4dd18eb1eed055d2d821b58ae-Abstract-Conference.html)).
Robust verification and policy synthesis for explicitly parameterized uncertain MDPs already give
scenario/PCTL guarantees
([Rickard et al., L4DC 2024](https://proceedings.mlr.press/v242/rickard24a.html)). The second branch
is a probabilistic-program/model-checking problem and requires a new sound relaxation plus a
matching hardness or incompleteness boundary.

Natural-language or ODD-to-grammar compilation does not evade the problem. If the compiler omits
one legal reading, the certificate is unsound; if humans enumerate readings, the output is a
conditional multiverse analysis. The current source supplies no labelled corpus of complete legal
readings against which compiler recall could be measured. EcoMD by itself cannot manufacture that
truth.

Hence the fragmentation paper supplies a **partial capability**: a public, market-native hard
negative and an audit target. It does not yet supply an irreducible method, complete benchmark, or
field-valid conclusion.

## 5. Bond MD2C paper: causal notation without intervention validation

[Marín Martínez et al.](https://doi.org/10.1371/journal.pone.0341369) provide a useful explicit
graph for partially observed dealer-to-client RfQs. The paper distinguishes the historical
conditional hit probability from a spread intervention and derives adjustment sets under its
declared graph. Its empirical section uses 102,437 BBVA RfQs, including 5,738 hits, and compares a
generative model, logistic regression, and LightGBM. The generative and LightGBM ROC-AUC values are
0.742 and 0.743, respectively, while the generative model enforces spread monotonicity.

Those are predictive results. The empirical evaluation does not randomize spreads, dealer calls,
or axes; it does not report calibration against potential outcomes; and it does not evaluate the
multi-RfQ extension. The paper itself states that an RCT/A-B test is required when an effect cannot
be identified and says detailed commercial-action records are limited even internally. Its data
availability statement says the BBVA transaction and licensed market data cannot be shared, even
in de-identified form.

### Equal-history witness

Let \(U\sim\operatorname{Bernoulli}(1/2)\) be latent client intent, \(A\) an aggressive-quote
indicator, and \(Y\) a hit. Suppose the historical policy has \(A=U\). Compare

\[
M_1:Y=A,
\qquad
M_0:Y=U.
\]

Both worlds generate the same complete historical law \(A=Y=U\). Under intervention,
\(M_1\) has a unit average effect of \(A\) and \(M_0\) has zero effect. Predictive AUC,
calibration on historical quotes, and monotonic architecture cannot distinguish them. The paper's
back-door equality is valid conditional on its causal graph; the observational sample does not
independently establish that the asserted adjustment set blocks every latent policy-selection
path.

The proposed multi-RfQ extension is economically real but not a residual EcoMD method on current
evidence. Once its sequential assignment and state are supplied, it is a dynamic treatment,
offline-policy-evaluation, partially observed control, or stochastic market-making problem. Without
them, a simulator produces only source-model counterfactuals. Recent action-conditioned forecasting,
adversarial causal tuning, interventional surrogate, and stochastic-control parents already remove
novelty from simply joining a causal graph to an EcoMD controller.

## 6. Decision table

| Lead | Useful new fact | Decisive missing contract | Decision |
|---|---|---|---|
| Fragmented-market ABM replication | Independent authors document quantitative failure and qualitative sign sensitivity | Same kernel, complete two-lineage executable fixture, exhaustive specification set, external truth | `partial_capability` |
| Specification-invariance certificate | Market-native query and a clear universal target | Sound completion grammar/outer bound and theorem beyond Rashomon enumeration and robust model checking | no candidate |
| Bond MD2C causal model | Real RfQs, explicit graph, partial-observability and monotonicity constraints | Assigned intervention, propensity, complete pre-state, public rights, potential-outcome validation, independent institution | `not_trigger` |

No recorded hard blocker is removed. Candidate harvesting remains false.

## 7. Exact re-review conditions

Re-audit the specification route only when one package supplies:

1. a formal partial stochastic-simulator language with a sound, declared completion semantics;
2. a computable lower and upper bound for a path/intervention query with finite-simulation coverage,
   plus a matching hardness or incompleteness result;
3. two independently written, fully pinned systems and hard negatives where the legal completion
   set or gold extrema are known; and
4. a result caused by event-driven market semantics and false for existing Rashomon, multiverse,
   uncertain-MDP, model-checking, and simulator-discrepancy parents.

Re-audit the bond route only after a lawful source jointly exposes pre-action assignment and
propensity, complete RfQ/inventory/client state, interference and timing, every attempted action and
outcome, derived-output rights, an untouched confirmation institution or period, and an
independently governed same-action replication. A predictive holdout, an assumed DAG, a private
access-request possibility, or an EcoMD-generated intervention is not sufficient.

Until then, do not contact BBVA for data, reconstruct the proprietary sample, implement an RfQ
simulator, reproduce the fragmentation grid, or schedule the A800/V100 workers.
