# Performative dispatch T0 novelty/identifiability freeze — 2026-08-19

## Purpose

This gate asks whether a public rolling electricity-market forecast can support a new and identifiable
closed-loop mechanism claim. It runs before downloading any AEMO market row, computing any response statistic or
implementing a learned model.

The candidate causal chain is

```text
U_t, X_t -> F_t -> B_t -> C_t -> Y_t
   |          \      \      \
   +----------> B_t -> C_t -> Y_t
```

where `X_t` is observed physical/news state, `U_t` is private or unrecorded common information, `F_t` is the
published forecast/revision, `B_t` is participant bidding/rebidding, `C_t` is the clearing active set and `Y_t`
contains dispatch, price, flow and reliability outcomes. The desired estimands are effects of `do(F_t)` or
forecast availability on `B_t` and decision value, not associations between forecast error and later price.

## Frozen first attack: observational non-identifiability

T0 must begin with two binary SCMs:

- Model A: `U ~ Bernoulli(1/2)`, `F=U`, `B=F`, `C=B`, `Y=B`;
- Model B: `U ~ Bernoulli(1/2)`, `F=U`, `B=U`, `C=B`, `Y=B`.

They generate exactly the same observed joint law for `(F,B,C,Y)`. Under `do(F=1)`, however, Model A changes
`B,C,Y`, while Model B does not. Therefore complete observational logs and correct temporal ordering do not by
themselves identify forecast performativity when forecast and response share hidden information. Any proposed
estimator must either reject total-effect language, add a defensible intervention/instrument or prove
identification under explicit weaker assumptions.

No neural network, simulator or larger sample may fill this causal gap.

## Required prior-art clusters

The claim matrix must include, at minimum:

1. performative prediction, performative stability and distribution maps;
2. proper/incentive-compatible scoring for forecasts that affect outcomes, including recent conditional-forecast
   impossibility and divergence results;
3. causal policy learning and strategic-agent response;
4. rolling/non-binding pre-dispatch price and quantity discovery;
5. strategic bidding/rebidding and forecast use in Australian and New Zealand electricity markets;
6. parametric market clearing, LMP active-set sensitivity, extreme prices and topology/congestion recovery;
7. natural experiments, outages, publication thresholds or rule changes capable of shifting forecast exposure
   without directly changing dispatch incentives or physical state.

Backward and forward citation neighbors through August 2026 are required. Reviews may route the search but do
not establish novelty.

## Allowed exits

At least one exit must pass. A verbal combination of existing components does not count.

### E0 — identification theorem

A theorem identifies a forecast-induced response or decision-value estimand under assumptions strictly weaker
or structurally different from the nearest performative-forecast result. It must state positivity, hidden-state,
interference and time-order conditions and include the frozen counterexample as a failure case.

### E1 — estimator with a real instrument

A public, repeatable intervention or instrument changes forecast exposure/content but has a defensible exclusion
from bids/outcomes except through the forecast. Metadata must indicate at least five eligible independent events
or one rule discontinuity with enough support on both sides. Publication timing alone is not an instrument when
the same news causes both forecast and bids.

### E2 — constraint-mediated law

The clearing active set yields a falsifiable spatial/temporal response identity not already implied by standard
parametric programming, LMP sensitivity or congestion-price decomposition. “Prices change when constraints bind”
and “the solution is piecewise affine” are explicitly ineligible.

### E3 — benchmark/resource contribution

Public logs support a unique closed-loop benchmark with observable forecast, agent action, institutional state
and outcome, plus a task that cannot be reduced to ordinary price forecasting. This exit can justify a data or
specialist systems paper, but cannot alone authorize an NCS claim.

## PASS and stop rules

T0 PASS requires all of the following:

- at least one of E0--E2 passes; E3 alone is insufficient for the high-impact route;
- a one-sentence claim survives a nearest-five-method non-equivalence table;
- the estimand is identifiable or explicitly partial under a written SCM;
- a free-data path contains every required field with timestamps and version semantics;
- a fresh chronological split and independent transfer market can be reserved before any outcome is inspected;
- the result would change a forecast-evaluation, dispatch-policy or agent-response decision if confirmed.

Immediate FAIL occurs if the only contribution is an AEMO application of an existing performative score, an
ordinary predictive model, an association between forecast revisions and rebids, or an active-set explanation
already implied by power-market theory.

On FAIL: archive the matrix, do not download AEMO rows, do not implement the conditional synthetic study, and do
not queue CPU/GPU. On PASS: commit the T0 result, then separately freeze D0 source qualification before network
acquisition.

## Data and compute lock

T0 may read papers, official rules, schema pages and metadata-only outage/rule listings. It may not read or store
prices, bids, dispatch quantities, constraint outcomes or event-window statistics. Budget is less than 20 CPU
core-hours and no GPU. V100, RTX2060, paid data, EcoMD training and H20 are forbidden.

## Initial anchors

- [Perdomo et al., *Performative Prediction*, ICML 2020](https://proceedings.mlr.press/v119/perdomo20a.html)
- [Oesterheld et al., *Incentivizing honest performative predictions*, UAI 2023](https://proceedings.mlr.press/v216/oesterheld23a.html)
- [Boeken et al., *Conditional Forecasts and Proper Scoring Rules*, NeurIPS 2025](https://arxiv.org/abs/2510.21335)
- [Guerci et al., *Price and quantity discovery without commitment*, 2023](https://doi.org/10.1016/j.ijindorg.2023.102987)
- [Clements et al., *Strategic bidding and rebidding in electricity markets*, 2017](https://doi.org/10.1016/j.eneco.2016.12.011)
- [Nesti et al., *Large Fluctuations in Locational Marginal Prices*, 2020](https://arxiv.org/abs/2002.11680)
- [Kekatos, Giannakis and Baldick, *Grid Topology Identification using Electricity Prices*, 2013](https://arxiv.org/abs/1312.0516)
- [AEMO dispatch reports](https://aemo.com.au/energy-systems/electricity/national-electricity-market-nem/data-nem/market-management-system-mms-data/dispatch)
- [AEMO constraint FAQ](https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/system-operations/congestion-information-resource/constraint-faq)
