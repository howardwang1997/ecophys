# EcoMD Discovery Loop topic cycle 16: prospective simulator validity

**Date:** 2026-08-26
**Literature cutoff:** 2026-08-26
**Mode:** outcome-blind, paper/source-only topic search
**Decision:** one frozen F3 formulation failed; zero machine cards
**Authorization:** no simulator run, outcome access, dataset action, implementation, outreach,
sandbox, purchase, EcoMD edit, or compute

## 1. Decision

Cycle 16 returned from venue-by-venue rule hunting to the central simulated-market question:
can a simulator score measured before a real rule change predict which simulator will forecast that
change correctly? The strongest formulation was frozen before the full hostile audit in
`ecomd_cycle16_prospective_simulator_validity_f3_freeze_2026-08-26.md`.

The narrow empirical gap is genuine. I found no primary work that predeclares a simulator
interventional-fidelity score and then tests whether it predicts full path-law error across multiple
unseen, independently governed real market-rule changes. That absence is not enough to make the
current formulation sound. It failed four independent gates:

1. **No-free-lunch off-support adaptation.** Two real data-generating processes can agree on every
   pre-change observation and every simulator-native intervention in the score, yet respond
   oppositely after a new real rule because participant adaptation outside the observed regime is
   unconstrained. A simulator score cannot certify field transfer without a structural bridge.
2. **Only two field interventions are not a population.** Errors from many models, securities and
   horizons remain clustered within the same two rule changes. Treating those rows as independent
   would be pseudoreplication and cannot establish a general score--validity relation.
3. **No common action language.** Data-driven LOB generators can match message distributions but
   normally do not expose a structurally faithful rule intervention. Structural ABMs expose rule
   knobs, but their adaptive agent populations are not identified from the pre-change book. A
   custom adapter can encode the desired answer unless it is fixed and independently validated.
4. **The available prospective field assets do not close one joint contract.** The TSE controller
   changes several market-design dimensions and relies on paid FLEX history; CME SR3 tick changes
   are collinear with contract maturity and omitted implied-book state; the US tick reform is a
   bundled market-structure change without a post-period. Trading pauses are endogenous and already
   have direct empirical literatures.

The claim therefore failed for scientific, statistical, and data-contract reasons. Its frozen
10-percent point forecast resolves false with Brier score `0.0100`. Together with Cycle 12, the mean
Brier score is `0.0122` over only two resolved full-T0 forecasts, both negative. This is far too
small and one-sided a sample to recalibrate the provisional 15-percent active-status brake.

## 2. Funnel accounting

| Stage | Limit | Used | Result |
|---|---:|---:|---|
| F0 raw question programs | 12 | 12 | Complete portfolio recorded |
| F1 quick screens | 6 | 6 | Three closed and three advanced |
| F2 collision/contract screens | 3 | 3 | One closed, two advanced |
| F3 full hostile audits | 2 | 1 | Frozen formulation closed |
| Machine cards | 1 | 0 | No authorization |

Six programs were portfolio-pruned, three failed quick screens, two failed collision screens, and
one failed the full hostile audit. No program was closed by a probability label.

## 3. F0 portfolio: twelve question programs

| ID | Native object and rival explanations | Discriminating result | Lane / archetype | Disposition |
|---|---|---|---|---|
| P1 `prospective_counterfactual_market_simulator_validity` | **H1:** conditional on pre-change fit, synthetic interventional fidelity predicts path-law forecast error after unseen real rule changes. **H0:** it measures only consistency with the simulator that supplied its interventions. | Predeclare the score and forecast errors, then reveal several independent rule changes. Both a positive result and a calibrated failure would change simulator use. | new truth or control capability / simulator method | F3 failed |
| P2 `task_conditioned_market_simulator_adequacy` | **H1:** an intervention-specific adequacy envelope is more informative than global realism. **H0:** this is established task-oriented validation and model criticism. | Require a market-hard-semantic theorem or coverage result absent from the parent methods. | unresolved model disagreement / simulator method | F2 parent close |
| P3 `disagreement_guided_market_intervention_design` | **H1:** cross-engine disagreement chooses maximally informative interventions. **H0:** disagreement is neither truth nor calibrated uncertainty. | Supply analytic truth or a real assigned intervention that resolves the disagreement. | unresolved model disagreement / simulator method | portfolio-pruned: Cycle 8 duplicate |
| P4 `field_calibrated_simulator_ensemble_abstention` | **H1:** agreement across simulators certifies when to abstain. **H0:** correlated structural error allows unanimous failure. | Prove calibrated coverage against independent field interventions. | new truth or control capability / simulator method | portfolio-pruned: Cycle 8 duplicate |
| P5 `market_simulator_heterogeneity_value_frontier` | **H1:** richer agent heterogeneity improves intervention forecasts. **H0:** latent population detail is nonidentified and only increases flexibility. | Same-cost nested models must improve sealed rule-change prediction, not in-sample fit. | unresolved model disagreement / simulator method | F1 identification close |
| P6 `strategy_ranking_preservation_under_rules` | **H1:** a valid simulator preserves strategy rankings across rules. **H0:** ranking is payoff-, opponent-, and state-specific. | Require live counterfactual truth and a fixed strategy population. | new truth or control capability / simulator method | F1 truth close |
| P7 `multiscale_semigroup_consistency` | **H1:** consistent coarse and fine transition operators certify a simulator. **H0:** internal semigroup consistency does not imply field truth. | Construct equal semigroup fit with opposite unseen intervention response. | cross-domain theorem with market-specific obstruction / simulator method | F1 parent close |
| P8 `event_representation_invariant_validation` | **H1:** validation survives legal timestamp and batching representations. **H0:** quotienting discards priority and enabledness that determine response. | Require identical native actions and outcomes under each representation. | cross-domain theorem with market-specific obstruction / measurement method | portfolio-pruned: observation/partial-order closure |
| P9 `circuit_breaker_stored_order_release_response` | **H1:** releasing accumulated auction orders produces a measurable relaxation law. **H0:** the trigger is endogenous and the response is ordinary auction price discovery. | Identify the same pre-trigger state under an assigned pause rule. | market-native action or constraint / empirical intervention | F2 direct-prior and assignment close |
| P10 `pause_duration_as_liquidity_relaxation_clock` | **H1:** pause duration is a controlled relaxation time. **H0:** duration and reopening state are selected by volatility and auction imbalance. | Randomize duration conditional on complete stored-order state. | market-native action or constraint / empirical intervention | portfolio-pruned: pause route duplicate |
| P11 `forced_book_purge_as_market_reset` | **H1:** a purge isolates replenishment kinetics. **H0:** purge eligibility and latent replacement flow select the response. | Require an assigned purge and complete cancelled/restored order state. | market-native action or constraint / theory-mechanism | portfolio-pruned: reset/data-contract failure |
| P12 `adaptive_price_band_controller_criticality` | **H1:** an adaptive band controller creates a new boundary response. **H0:** it is a state-dependent controller already represented in the graph. | Prove a result false for finite-state feedback control and ordinary auction intervention. | market-native action or constraint / theory-mechanism | portfolio-pruned: graph duplicate |

## 4. F1 and F2 reductions

### 4.1 Task-conditioned adequacy is useful but not a new parent problem

Task-specific validation is the correct way to avoid a meaningless global realism score. However,
optimal model discrimination, computer-model discrepancy, posterior predictive criticism,
task-oriented ABM surrogates, and interventionally consistent surrogates already provide the parent
language. A market contribution needs a new guarantee caused by matching, priority, inventory, or
another hard market semantic. Merely combining those methods into a LOB benchmark is not an
irreducible result.

### 4.2 Stored-order release is not a clean field quench

Volatility interruptions can preserve a trigger order and route later orders into an auction, so
their order-release semantics are genuinely market-native. But activation is selected by the same
price path and order flow whose response is measured. The trigger threshold can be undisclosed,
and the full latent intent or counterfactual no-pause book is unavailable. Direct studies already
measure trading pauses, order-book conditions, magnet effects, and volatility-auction price
discovery. Without an assigned pause conditional on the same complete pre-state, this is not a new
causal relaxation experiment.

## 5. Full F3 audit

### 5.1 Frozen target

For simulator `m`, field rule change `r`, and horizon `h`, let `E_{m,r,h}` be a proper path-law
forecast loss. Let `S_{m,r}` be a score computed before field outcomes from observational fit and a
fixed suite of simulator-native interventions. The frozen claim asked whether `S` predicts `E`
after conditioning on observational fit, across at least two independently governed future rules,
and beats an observation-only ranking.

### 5.2 Off-support twin

Let all pre-change histories lie in regime `R0`. Construct real kernels `K+` and `K-` that are
identical on `R0` and on every finite synthetic intervention used by `S`. After the real rule
activates a previously unreachable state `z`, define the participant adaptation kernels to send
the book toward recovery under `K+` and depletion under `K-`. Every pre-change datum and every
simulator score is equal, while the future path laws can be arbitrarily separated. Hence no generic
field-validity implication follows from simulator interventional consistency alone.

This does not say prospective validation is impossible. It says that the structural bridge and its
domain must be part of the claim; they cannot be inferred from a benchmark score.

### 5.3 Independent-unit gate

With two rule changes, the independent treatment-level sample size is two, even if each change has
many securities, models, seeds and horizons. Those observations estimate within-change noise; they
do not create more policy environments. A cross-validation or mixed-effects model cannot repair an
unidentified between-intervention relation. The frozen `at least two` requirement is therefore
insufficient for a general predictive-validity claim. Any descendant must set the number of
independent intervention families by an outcome-blind precision or power calculation; a plausible
planning floor is six, not a guarantee of sufficiency.

### 5.4 Action-language gate

The same rule must be expressed without researcher discretion in every simulator and in the field.
For example, changing tick size inside a learned message generator is not defined unless the model
contains a structural price-grid action; adding an even-grid wrapper to one engine while modifying
matching or agent actions in another changes the estimand. Equal labels do not establish equal
interventions. Adapters require deterministic conformance fixtures and must be frozen before the
field intervention is chosen.

### 5.5 Prospective asset matrix

| Asset | Strength | Decisive unresolved contract |
|---|---|---|
| TSE 2027 adaptive tick controller | Official prospective mechanism and transition map | Bundled controller dimensions, endogenous denominator, paid historical FLEX data, no independent same-controller replication |
| CME SR3 recurring tick transition | Repeated official transition by contract maturity; MBO available commercially | Exact collinearity with maturity/roll, pro-rata and implied-liquidity semantics, implied orders absent from MBO, rights and common simulator action unfrozen |
| US Regulation NMS tick reform | Official future market-wide rule | Tick, access-fee, odd-lot and routing environment bundled; no post-period yet; public complete L3 unavailable |
| Eurex-style volatility interruptions | Native pause/auction action and official semantics | Endogenous trigger, partly undisclosed thresholds, no no-pause potential outcome, direct pause/auction empirical prior |

No pair simultaneously provides independent assignment, a common rule action, complete pre-state,
lawful outcomes, and enough independent rule families. The correct decision is to stop before data
purchase, adapters, simulation, or outcome access.

## 6. Primary and official evidence manifest

| Work/source | What it establishes | Limit for this route |
|---|---|---|
| Nagy et al., LOB-Bench, ICML 2025 | Conditional distribution, response, impact and discriminator tests for generated LOB data | Historical realism, not prospective rule validity |
| Dyer et al., NeurIPS 2024 | High-probability interventional consistency of an ABM surrogate with its source simulator | Source-simulator fidelity is not real-system validity |
| Fabiani et al., Nature Communications 2024 | Task-oriented ABM surrogate construction and validation | Occupies the broad task-conditioned surrogate framing |
| Ward et al., NeurIPS 2022 | Posterior predictive model criticism under simulator mismatch | Criticism detects mismatch but does not identify an unseen intervention response |
| Kennedy and O'Hagan, JRSS B 2001 | Calibration with explicit computer-model discrepancy | Generic calibration/discrepancy parent |
| Atkinson and Fedorov, Biometrika 1975 | Designs observations to discriminate rival models | Generic model-discrimination parent |
| Fraedrich and Goldberg, EJOR 2000 | Predictive-simulation validation framework | Broad predictive-validation parent |
| Windrum, Fagiolo and Moneta, JASSS 2007 | Empirical validation strategy for agent-based models | Broad ABM validation parent |
| Belfrage et al., JASSS 2024 | Credibility and validation requirements for ABMs | Supports hard evidence contracts, not the frozen forecast claim |
| Poledna et al., EER 2023 | Out-of-sample forecasting with a macro ABM | Forecasting evidence, not market-rule counterfactual validation |
| CDC PRISM validation study, 2021 | Distinguishes face, internal, cross, external and predictive validation; predictive validation was omitted for lack of long-run intervention outcomes | Supports the missing-field-truth warning, not a prospective-validation result |
| Noble, Rosenbaum and Souilmi, 2026 | Latency- and race-aware interactive LOB simulation aimed at the reality gap | Does not validate unseen exchange-rule effects |
| Werner et al., Management Science 2023 | Tick-size theory paired with empirical evidence | Direct rule-specific theory/evidence; not a generic simulator-validity relation |
| Chung et al., JFE 2020 | Empirical evidence from the US Tick Size Pilot | Historical tick intervention is no longer sealed for topic selection |
| Hautsch and Horvath, JFE 2018 | Trading pauses, order-book conditions and price discovery | Occupies the broad pause-response empirical claim |
| Castro, Agudelo and Preciado, IREF 2020 | Volatility auctions and market quality | Occupies broad auction-release validation |
| CME SR3 rulebook | Official recurring tick-size schedule and matching context | Maturity and implied-book confounds remain |
| JPX/TSE tick controller and FLEX pages | Official prospective controller and historical-data availability | Bundled intervention and paid-data contract remain |
| SEC Regulation NMS final rule | Official future tick/access-fee/odd-lot reforms | Bundled treatment and absent post-period |
| Eurex volatility-interruption specification | Trigger-order and auction semantics | Assignment and counterfactual state absent |

## 7. Forecast and 15-percent-floor assessment

The F3 subject and forecast were recorded at `2026-08-26T06:08:09Z`, before this full audit. The
point forecast was `0.10` with diagnostic interval `[0.04, 0.22]`. The resolution is false because
the frozen requirements for field assets, common action semantics, and a defensible predictive test
failed. The Brier score is

\[
(0.10-0)^2=0.0100.
\]

The only other resolved comparable forecast is Cycle 12 (`p=0.12`, false; Brier `0.0144`). Their
mean Brier is `0.0122`, but two failures provide no information about calibration near the decision
boundary and cannot distinguish a conservative forecaster from an easy all-negative stream. The
predeclared review threshold of twenty comparable resolutions remains appropriate. The 15-percent
lower endpoint remains a provisional cost brake for `active` status, not a scientific gate.

## 8. Reusable result and search consequence

The useful residue is a stricter definition of prospective simulator validity:

- score and adapters frozen before choosing or revealing field interventions;
- common native action semantics with deterministic conformance tests;
- several independently governed intervention families, with sample size set by precision/power;
- proper path-law loss and observation-only/equal-budget baselines;
- an explicit structural transport domain, not an unrestricted validity claim; and
- entire intervention families, not model--security rows, as the replication unit.

This family is now saturated for blind repetition. A third consecutive search cycle may not begin
from another simulator-validity label or another exchange rule unless a new primary model fork, a
new truth/control asset, or a theorem removes one of the recorded blockers. The next cycle should
therefore harvest a genuinely new capability first, rather than substitute a new venue for the same
missing truth contract.

## 9. Source links

- https://proceedings.mlr.press/v267/nagy25a.html
- https://proceedings.neurips.cc/paper_files/paper/2024/hash/26b8e3dc3a21fcd660d80c63b767f324-Abstract-Conference.html
- https://doi.org/10.1038/s41467-024-48024-7
- https://proceedings.neurips.cc/paper_files/paper/2022/hash/db0eac6747e3631eb91095cd76065611-Abstract-Conference.html
- https://doi.org/10.1111/1467-9868.00294
- https://doi.org/10.1093/biomet/62.1.57
- https://doi.org/10.1016/S0377-2217(99)00117-4
- https://www.jasss.org/10/2/8.html
- https://doi.org/10.18564/jasss.5505
- https://doi.org/10.1016/j.euroecorev.2022.104306
- https://www.cdc.gov/pcd/issues/2021/20_0225.htm
- https://arxiv.org/abs/2603.24137
- https://doi.org/10.1287/mnsc.2022.4502
- https://doi.org/10.1016/j.jfineco.2019.11.004
- https://doi.org/10.1016/j.jfineco.2017.12.011
- https://doi.org/10.1016/j.iref.2020.06.024
- https://www.cmegroup.com/rulebook/CME/IV/400/460.pdf
- https://www.jpx.co.jp/english/equities/trading/domestic/07.html
- https://www.jpx.co.jp/english/markets/paid-info-equities/historical/01.html
- https://www.govinfo.gov/content/pkg/FR-2024-10-08/pdf/2024-21867.pdf
- https://www.eurex.com/ex-en/support/emergencies-and-safeguards/volatility-interruption-functionality
