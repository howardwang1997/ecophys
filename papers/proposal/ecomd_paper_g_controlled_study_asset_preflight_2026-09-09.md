# Paper G: controlled-study truth-asset preflight

**PRIVATE / INTERNAL — exploratory discovery record; not public research evidence.**

Date:2026-09-09. Session began17:32 NZST. Source reading and algebra were
interleaved; no prospective freeze, new forecast or experimental result is claimed.
Machine-readable companion:
`research/paper_g/controlled_study_preflight_20260909.yaml`.

The audit finds a documented open forecasting-experiment package and a distinct
randomized investor study whose public release uses pseudo data. These are useful
capabilities with different targets. They do not yet remove the existing
same-intervention, independent-confirmation or contribution blockers. Verdict:
**partial_capability; candidate_harvest_authorized:false; no new cycle/card**.
Cycle28 Arctic-auction closure and the subsequent NAV non-trigger remain intact.

## Sources and capability scope

| Source | Verified capability | Limit of this inspection |
|---|---|---|
| [Hanaki et al., Experimental Economics26,1185–1213 (2023)](https://pure.uva.nl/ws/files/167530653/s10683-023-09815-9.pdf) | Forecasting task, price feedback, rewards and admissible submissions are documented in§2.1–2.2. | Selected design passages; no outcome reanalysis or complete paper audit. Broad elicitation-format effects are already the paper's subject. |
| [Official package metadata](https://www.oar-rao.bank-banque-canada.ca/record/1188) | Version1,2023-10-26, DOI10.21942/uva.24441913.v1; raw data, experimental software and analysis code listed under CC-BY4.0. | File contents, runtime, complete event schema and independent confirmation not inspected. This is the same study, not another replication. |
| [Schnorpfeil, Weber and Hackethal, Inflation and Trading, JFE173,104166 (2025)](https://doi.org/10.1016/j.jfineco.2025.104166) | Primary indexed design text describes randomized information supplied to bank customers, linked to actual trading in the original study. | Full publisher body not opened; no original customer records accessed. |
| [Release v1,2025-08-13](https://data.mendeley.com/datasets/2t83b26ngm/1) | Metadata specifies a random300-person survey subsample, noise added to continuous responses and an aligned bank-data subset; CC-BY4.0. | Confidential originals are not released. The complete release transformation is not qualified here. |
| [Release v2,2025-08-19](https://data.mendeley.com/datasets/2t83b26ngm/2) | Explicitly labels the package pseudo datasets and code; CC-BY4.0. | Do not silently transfer v1's detailed transformation recipe to v2. Two versions are one release lineage. |

The randomized bank-customer contrast can support an individual treatment effect
under its applicable assignment, observation and interference assumptions. Such
an estimand does not require a complete order book or two simulators. It also does
not, by itself, identify endogenous aggregate price feedback. Forecast submission
to a prescribed pricing mechanism and information provision to actual investors
are different actions, populations and responses; these studies cannot simply be
pooled into one simulator-validation truth contract.

## Retained check A: reward equivalence is narrower than action equivalence

Use the source's price and return definitions. Let the previous price be p>0,
next price be P, submitted price forecast be q and decimal return forecast be u.
For corresponding forecasts q=p(1+u), and realized return r=(P-p)/p,

\[
 F_P=\frac{q-P}{p}=u-r=F_R,
 \qquad R(F)=1300\max\{1-625F^2,0\}.
\]

Thus the common reward agrees exactly at corresponding forecasts for a shared
realization. The current four-arm design does not merely switch between absolute
and relative monetary errors. This does not assert equivalent incentives to every
earlier forecasting experiment.

The published submission bounds are q∈[0,1000] and u∈[-1,3]. Mapping the latter
into price units gives [0,4p]. Consequently:

\[
 A_P=A_R^{\mathrm{price}}\iff p=250,
 \qquad A_P\cap A_R^{\mathrm{price}}=[0,\min(1000,4p)].
\]

At the documented initial p=50, q=300 is admissible in price units but requires
u=5, outside the return domain. Conversely, at p=400 the return-domain endpoint
maps to q=1600, above the price-domain cap. These are analytic inputs, not observed
choices. The paper additionally caps realized prices at1000 in the return-task
arms. Hence no global equality of the full transition systems is inferred.

These bounds are disclosed design rules. We do not estimate how often they matter,
attribute the paper's reported effect to them, or claim to refute its empirical
conclusions. The reusable asset is an elementary check of transformed rewards,
admissible actions and resulting state transitions; it is not a new theorem.

## Retained check B: what added noise does and does not imply for an ITT

This is a generic conditional-mean identity, not an assertion about the exact
construction of either released file version. Suppose Z is randomized treatment,
Y=Y(Z), and the released outcome is Y*=Y+η. Let S=1 denote inclusion in a random
subsample independent of treatment and potential outcomes. With consistency,
the stated randomization and no unmodelled interference, define
τ_S=E[Y(1)-Y(0)|S=1]. Then

\[
 E[Y^*|Z=1,S=1]-E[Y^*|Z=0,S=1]
 =\tau_S+E[\eta|Z=1,S=1]-E[\eta|Z=0,S=1].
\]

Equal conditional noise means preserve the population mean contrast; zero noise
is unnecessary. Unknown differential noise means leave an unidentified bias.
Even mean preservation does not certify standard errors, nonlinear effects,
covariances or mediation. The phrase random noise does not establish all needed
conditions or a differential-privacy mechanism. Nor does this additive example
describe every bank-data field or prove that the release is unusable.

The preflight therefore asks for the transformation relevant to the intended
estimand, rather than treating every pseudo-data release as either original truth
or scientifically worthless. This is standard expectation algebra, with no new
estimator, empirical effect or inference guarantee claimed.

## Separate intake: post-trade compression

[Veraart and Zhang, Post-trade netting and contagion](https://eprints.lse.ac.uk/129549/1/Preprint_Final.pdf)
already studies when compression can worsen contagion, conditions preventing harm,
clearing fixed points and delayed payments. Selected introduction and definitions
were inspected; the complete proofs were not audited. A generic compression-harm
question therefore does not acquire novelty merely by selecting another venue.

The [Bank of England consultation of2025-12-11](https://www.bankofengland.co.uk/paper/2025/cp/exempting-post-trade-risk-reduction-transactions-from-the-clearing-obligation)
uses non-price-forming for a post-trade procedure without price negotiation.
That does not promise zero effects on future equilibrium prices or defaults.
This is a historical consultation, not a statement of current operative law.
No same-state, same-action contradiction with the theoretical paper was verified.
This lead remains unformulated intake; no new network/clearing candidate is opened.

## Requirements fixed at closeout; no asset or execution authorized

| Contract field | Required before the corresponding use |
|---|---|
| Supported estimand | Forecast-task effects within the exact feedback game, or bank-customer information ITT, separately. No automatic market-wide or cross-study transfer. |
| Assignment/interference | Recover actual assignment unit, timing, treatment content and exposure. Forecasting participants interact within markets; do not analyze them as independent markets. Specify bank-customer spillovers for the selected target. |
| Event lifecycle | For forecasting: allowed submissions, revisions, timeouts, feedback/shock state, observation history and payments. For investor ITT: assignment, delivery, survey observation, account inclusion and the outcome window. Full trading lifecycle is required only for an extension that depends on it. |
| Replay/release state | Pin source version, preprocessing and any perturbation/subsampling map. Qualify fields sufficient for the claimed replay or estimand; files labelled raw need inspection. |
| Rights/ethics/release | Package CC-BY metadata is documented; third-party components and participant reuse conditions remain to be checked for the intended use. No rights to confidential originals or new recruitment inferred. |
| Untouched confirmation | No such partition is qualified. A new prospective manifest or independent source must be fixed before target access; unread rows of a published archive are not automatically independent confirmation. |
| Independent replication | Reusing code is not an independent execution team. The two reviewed studies do not implement one intervention; neither multiple release versions nor paper+dataset counts as replication. |
| Cost | This session: no data acquisition, monetary spend, scientific execution or GPU. Future acquisition/runtime cost unknown; no estimate is promoted to authorization. |
| Stop/update | No repeated scan for more format studies. Review only a versioned source/control contract that removes a named blocker, or a substantive theorem. A bounded follow-up may inspect at most two directly relevant contract sources and must stop if no blocker changes. Implementation, outcomes and participants still require their applicable decision. |

Both positive and negative qualification have value: a usable documented release
can lower the cost of a future discriminating test; a mismatch prevents testing a
different treatment while claiming the intended one. Neither is itself a novel
Paper G question. No candidate harvesting, new cycle, full-T0 forecast or machine
card is justified by this audit. Structured records retain the two checks without
reopening the terminal parent routes.

Seven external evidence records are retained: six source bodies opened and one
primary article inspected through substantive indexed design text. No raw outcome
asset, experimental software or analysis code was downloaded or executed. Published
source statements are literature context, not independent confirmation. Verification
and access details belong in the separate private receipt.
