# EcoMD HFT-proxy truth-asset trigger audit

**Date:** 2026-09-05  
**Archetype:** `measurement_method`  
**Decision:** `not_trigger`  
**Candidate harvesting:** not authorized  
**Market-data outcome access, implementation, simulation, SSH, and GPU work:** not authorized

## 1. Executive decision

Ibikunle, Moews, Muravyev, and Rzayev provide a useful new *measurement proxy* for daily
liquidity-demanding and liquidity-supplying HFT activity. Their source data are unusually strong:
true HFT counterparty flags in the 2009 Nasdaq sample and a separately labelled Euronext Paris
sample. This is valuable descriptive financial research.

It does **not** reopen an EcoMD research route. The public object is a prediction

\[
\widehat H=g(X),
\]

where `X` is a vector of 24 public stock-day TAQ aggregates. It is not a release of the HFT
counterparty labels. Any simulator already matched or evaluated on the law of `X` receives no new
identifying restriction from `g(X)`. Two latent market worlds can have the same public tape and the
same learned HFT measure while having different true HFT populations, mechanisms, and responses.

There is also a semantic mismatch. The two outcomes are overlapping *executed-volume roles*, not
mutually exclusive persistent trader types. An HFT--HFT trade contributes to both measures. Current
EcoMD types are uniformly sampled persistent latent labels with no participant-level execution
observation map. Calling two labels “HFT supply” and “HFT demand” would impose the desired meaning;
the learned public proxy cannot establish it.

The new paper therefore supplies a useful compatibility statistic and a useful watch item, but it
removes none of the recorded population-unit, participant-truth, action, state, transport, or
independent-replication blockers. All three GPU workers remain idle.

## 2. Exact question and rival explanations

**Market-native object.** For stock `i` on day `t`, let the labelled execution volumes be
`V_HH`, `V_HN`, `V_NH`, and `V_NN`, where the first letter is the liquidity demander and the second
the supplier. The paper defines

\[
H_D=\frac{V_{HH}+V_{HN}}{V_{\mathrm{tot}}},\qquad
H_S=\frac{V_{HH}+V_{NH}}{V_{\mathrm{tot}}}.
\]

The candidate question was whether public predictions of `(H_D,H_S)` provide external semantic
truth for EcoMD latent populations and their intervention responses.

- **H1 — external semantic constraint:** a source-labelled public-feature mapping supplies an
  independent observation of HFT roles, so matching it can identify or validate EcoMD agent types
  and their response to market interventions.
- **H0 — derived compatibility score:** the public prediction is a function of the same aggregate
  tape, so it can measure compatibility with the source mapping but cannot identify hidden trader
  roles, latent population units, or counterfactual responses without target labels and a valid
  observation/transport model.

**Cheapest discriminator.** Ask whether two latent worlds with the same law for all public inputs
`X` can have different true HFT labels or action responses. If yes, every released prediction
`g(X)` has the same law in both worlds and cannot adjudicate them.

A positive result would have supplied the first external role-level bridge for EcoMD. A null result
still matters: it prevents a high-quality predictive proxy from being mistaken for independently
observed mechanism truth.

## 3. What the primary work actually supplies

The v2 paper reports the following contract.

1. **Nasdaq source truth.** The 2009 dataset covers 120 Nasdaq- and NYSE-listed stocks and labels
   both trade counterparties as HFT or non-HFT. It contains 29,880 stock-days before missing-value
   exclusions. The paper trains random forests and extremely randomized trees on 24 same-day TAQ
   price, volume, depth, spread, impact, imbalance, volatility, retail, and institutional-flow
   variables.
2. **Public-scale output.** The fitted mapping is applied to 9,396,251 US stock-days from 2010 to
   2023. The authors state that the resulting stock-day measures will be public. As of this audit,
   neither the arXiv record/PDF nor a title/identifier GitHub search exposed a first-party data,
   model, code, checksum, or licence endpoint. This availability issue is recorded as unresolved,
   not as the scientific killer: even a fully downloadable prediction panel would remain `g(X)`.
3. **Cross-market evidence.** Eurofidai-Bedofih supplies proprietary Euronext buyer/seller HFT
   status, initiator identity, and regulatory Pure/Mixed HFT flags through 2017. The paper trains
   separate 2009 Nasdaq and 2009 Euronext models and compares feature importance. It does **not**
   apply the fitted Nasdaq mapping directly to labelled Euronext outcomes.
4. **Temporal Euronext test.** A model fitted on 2009 Euronext data predicts labelled Euronext HFT
   in 2010 and 2017. Total-variation training `R^2` is reported as 72% for Euronext and 82% for
   Nasdaq. After stock and day fixed effects, the Euronext out-of-sample within-`R^2` values are
   only 0.07%--0.12% for supply and 0.30%--0.34% for demand. This is evidence of coarse predictive
   persistence, but weak evidence for within-stock, within-day-condition discrimination.
5. **Event checks.** The learned measures move in theoretically expected directions around a
   Nasdaq data-feed upgrade, an Amex speed bump, and latency-arbitrage opportunities. These are
   useful construct-validity checks. They observe `g(X)` after the event, not post-event true HFT
   labels under a replay-complete assigned state.

## 4. Three decisive identification results

### 4.1 Deterministic-proxy no-increment lemma

Let `Z` denote latent participant identities and strategies, `X` the public input vector, and
`g` the fixed learned HFT predictor. Suppose two market models `P_0` and `P_1` satisfy

\[
P_0(X)=P_1(X)
\]

but disagree on a latent functional `T(Z)` or its response. Then

\[
P_0\bigl(X,g(X)\bigr)=P_1\bigl(X,g(X)\bigr).
\]

The proof is immediate: `(X,g(X))` is a measurable pushforward of `X`. Therefore every divergence,
moment loss, classifier score, or posterior based only on `(X,g(X))` assigns the same evidence to
the two worlds. If the public procedure also uses independent algorithmic randomness `U`, then

\[
I\!\left(Z;A(X,U)\mid X\right)=0.
\]

Consequences for EcoMD are exact:

- adding the predicted HFT panel to a loss that already matches the full `X` law cannot reduce the
  observational equivalence class;
- matching only selected summaries of `X` can make `g(X)` an additional *derived moment*, but not
  participant truth;
- holding out stocks or dates estimates predictive transfer of `g`, not semantic recovery of `Z`.

This is the same data-processing floor already recorded for synthetic metaorders. It is not a new
ICLR theorem.

### 4.2 Target-transport twin

Let `eta_s(x)=E_s[H\mid X=x]` be the source relation learned from Nasdaq labels. Consider two target
worlds with the same public marginal `P_t(X)` but conditionals

\[
E_{t,0}[H\mid X=x]=\eta_s(x),\qquad
E_{t,1}[H\mid X=x]=1-\eta_s(x).
\]

Unlabelled target features and the released source predictor have identical observable laws in both
worlds, but their label errors and latent interpretations are opposite. More realistic twins can
hold the marginal HFT share fixed while swapping conditional roles in an intervention-relevant
region. Thus similarity of marginal inputs or feature-importance rankings cannot certify the
conditional relation required for transport.

The Euronext exercise is useful evidence against arbitrary drift, but it does not remove this
logical boundary for the US mapping: it trains a separate Euronext predictor, changes unavailable
features, uses a different regulatory label rule, and does not release target-labelled error under
the proposed EcoMD actions. Classical domain-adaptation impossibility results already occupy the
general theorem.

### 4.3 Activity roles are not a persistent-type simplex

Because `V_HH` enters both numerators,

\[
H_D+H_S=\frac{2V_{HH}+V_{HN}+V_{NH}}{V_{\mathrm{tot}}}.
\]

The two values are neither disjoint shares nor counts of stable economic agents. The same HFT firm
can demand liquidity in one execution and supply it in another. A daily stock-level pair cannot
determine:

- how many HFT firms participated;
- which firm generated which orders, cancellations, and fills;
- inventories, information, latency, or policy state;
- a persistent interaction graph or force between participant types; or
- how the same participants would act under a rule change.

This is not a weakness in the paper's stated measurement target. It is a category error only if the
measures are repurposed as labels for EcoMD's persistent latent particles.

## 5. Repository-semantic audit

Current EcoMD cannot consume this asset as ground truth without changing the scientific object.

- `ecomd/models/ecomd_v2.py::TypeEmbedding` samples fixed labels uniformly from `0..K-1`; the
  “fundamentalist/chartist/noise/market-maker analogue” names are modelling interpretations, not
  observed identities.
- `ecomd/models/price_formation.py::ExcessDemandPrice` maps latent signed positions to aggregate
  price and volume. It does not emit labelled counterparties or exact price-time-priority fills.
- `ecomd/observation/continuous_time.py` represents aggressive-buy and aggressive-sell event marks,
  but not participant identity, HFT regulatory status, maker inventory, or a role-persistent
  observation map.

Replacing two random latent labels by `HFT_D` and `HFT_S` would therefore encode the conclusion in
the model. It would also incorrectly turn overlapping execution roles into mutually exclusive
agent classes.

## 6. Method and novelty collision

Three adjacent method families close the obvious repairs.

1. **Data processing and target-conditioned compatibility.** The repository's prior anonymous-
   metaorder audit already proves that a randomized or learned function of an anonymous tape cannot
   create hidden trader information. The HFT predictor is the deterministic special case.
2. **Domain adaptation.** Ben-David et al. prove that source labels plus unlabelled target samples
   do not guarantee target success without substantive cross-domain restrictions. Similar public
   features or predictors are not a new solution to conditional shift.
3. **Observation-aware SBI.** OASIS already embeds a declared observation process into simulation-
   based inference and proves concentration on the MMD-identified set. Its latent consistency still
   requires a correct observation model and identifiability. Here the intervention-dependent proxy
   error kernel is unknown because target labels are absent.

“Calibrate EcoMD through the public HFT predictor” would therefore be an application of an unknown
observation model, not a new method. “Prove that the proxy adds no information after its inputs” is
correct but too elementary and already duplicated. “Use a domain-invariant network” does not remove
the no-target-label boundary.

## 7. Gate matrix

| Gate | Result | Reason |
|---|---|---|
| New authoritative participant truth exists in the source study | Partial | Two proprietary labelled datasets exist, but neither is an open project asset |
| Public object is true HFT labels | Fail | It is a learned stock-day prediction panel |
| Independent information beyond public inputs | Fail | Exact pushforward/data-processing lemma |
| Same native unit as EcoMD persistent types | Fail | Overlapping execution-volume roles versus random persistent particles |
| Direct Nasdaq-to-Euronext model transport | Fail | Separate models are trained; feature importance is compared |
| Label accuracy under proposed interventions | Fail | Event checks observe proxy responses, not labelled target error |
| Complete assigned state/action/response contract | Fail | No participant state, replay prestate, assignment, or same-state counterfactual |
| Irreducible ML method | Fail | Generic domain adaptation, observation-aware SBI, and prior data-processing result |
| Two independent truth systems and untouched confirmation | Fail | Both label systems are inaccessible and no EcoMD action is shared |

No hard gate is removed. The availability of the promised prediction panel, if later confirmed,
would improve feasibility for descriptive replication but would not change this decision.

## 8. Legitimate retained use

The learned measures may be used in future as:

- a descriptive stock-day covariate;
- a compatibility diagnostic for simulated public aggregates not already included in a score;
- a source of hypotheses about separate aggressive and passive HFT activity; or
- a benchmark for reproducing the paper's *predictive measurement* task if the model, labels and
  licence become available.

They must be called predicted HFT activity, not observed agent types, external mechanism truth, or
an independent validation target after matching the predictor inputs.

## 9. Exact re-entry conditions

Re-audit only if a new asset or theorem supplies all relevant missing pieces:

1. participant- or trade-resolved authoritative HFT labels with lawful reuse, stable identifiers,
   and complete order/cancel/fill lifecycle state;
2. a frozen observation kernel connecting those labels to an event-emitting EcoMD model, explicitly
   separating persistent participant status from per-trade maker/taker role;
3. target-labelled error under at least one legal, state-complete intervention, with an untouched
   independently governed market or time block;
4. a non-vacuous response-identification or sharp partial-identification theorem robust to a
   declared class of conditional shifts and false for existing domain-adaptation and observation-
   aware SBI parents; and
5. a prospective full-T0 freeze before any full neighborhood review or target outcome access.

A public prediction CSV, more dates, an ExtraTrees reimplementation, proxy cross-validation, or an
EcoMD GPU fit is not a re-entry trigger.

## 10. Decision and compute

**Decision:** `not_trigger`; `removed_blockers: []`; `candidate_harvest_authorized: false`.

No data download, model training, simulation, EcoMD integration, SSH, or GPU job follows. The A800
and both V100 workers remain idle for topic discovery.

## 11. Primary sources

1. Ibikunle, Moews, Muravyev, and Rzayev,
   [*Data-Driven Measures of High-Frequency Trading*](https://arxiv.org/abs/2608.00858), v2,
   2026.
2. Brogaard, Hendershott, and Riordan,
   [*High-Frequency Trading and Price Discovery*](https://doi.org/10.1093/rfs/hhu032),
   *Review of Financial Studies* 27 (2014), 2267--2306.
3. Ben-David, Lu, Luu, and Pál,
   [*Impossibility Theorems for Domain Adaptation*](https://proceedings.mlr.press/v9/david10a.html),
   AISTATS 2010.
4. Farahi, Zhou, and Vashistha,
   [*OASIS: Observation-Aware Simulation-Based Inference via Distributional
   Matching*](https://arxiv.org/abs/2606.22572), 2026.
5. Prior in-repository formal result:
   `papers/proposal/ecomd_metaorder_waveform_compatibility_trigger_audit_2026-09-05.md`.
