# Paper G topic exploration — Cycle 22, September 9, 2026

Private/internal topic-selection result. Exploratory, assembled during primary
source reading; not a preregistration, experiment, public claim or F3 audit.

Later resolution: the initially deferred information-rent candidate was
closed at its bounded F2 qualification stop. See the
[analytic resolution](ecomd_paper_g_information_rent_resolution_2026-09-09.md).
The initial screening decision and portfolio counts below remain history.

**Decision:** six raw questions, six quick screens and one F2 screen leave
**one deferred measurement question and zero machine cards**:
`paper_g_information_rent_execution_measurement`. Its working title is
**When Does Order-Flow Covariation Measure Information Rents in a Limit-Order
Market?** No equilibrium counterexample, new measurement theorem or empirical
explanation of active-management fees has been established.

This question has a cheaper next discriminator than another observational
event study: compute both the proposed statistic and actual expected profits
inside one fully specified finite trading equilibrium. It can fail before any
data acquisition or simulator work. The current evidence justifies that bounded
paper-only check, not a claim that this is already a publishable Paper G.

## 1. Portfolio and route boundaries

The sample contains one theory, three measurement and two empirical programs.
These are sampling choices, not advancement quotas. Four questions originate
in native trading/delivery rules; two concern an imported measurement argument
under market-specific observation semantics. **Zero verified same-state primary
model disagreements** are claimed: continuous dealer models, finite order-book
models and different auction formats cannot be counted as contradictory
predictions merely because their headlines differ.

| ID / archetype | Native object and rival explanations | Discriminator and positive/null value | Disposition |
|---|---|---|---|
| G22-01 / empirical | Random termination of opening/closing calls: it deters strategic late distortions versus merely reallocating order timing. | Compare the actual ending-rule intervention and price formation; either result informs the design's value. | Deduplicated for this broad efficiency/manipulation claim by Lin, Michayluk and Zou [S1]. |
| G22-02 / theory | Random-close ascending auctions with leaked bids: random termination limits the informed follower's advantage versus preserving it. | Equilibrium allocation and payments under the same leakage/order rules; either result constrains anti-front-running design. | Deduplicated by Hafner and Stewart's revised analysis [S2]. Candle-auction field/lab efficiency and collusion are also directly studied [S3]. |
| G22-03 / empirical | Corn futures redelivery: recipients' resale weakens the nearby spread versus common carry/storage conditions explaining the association. | A redelivery-specific price response with assignment/common conditions separated; either result informs delivery frictions. | Deduplicated for the broad redelivery/spread pitch by Fernandes, Kunda and Robe [S4]. Their causal interpretation is not independently validated here. |
| G22-04 / measurement | Certificate turnover from deliveries and net registered stock: the excess measures exact redelivery versus gross issuance/cancellation producing the same excess. | Two legal lifecycle allocations with equal proposed observables; uniqueness would validate a sufficient statistic, nonuniqueness specifies missing fields. | Quick-closed for exact recovery from net stocks and totals alone; retain the lifecycle counterexample. |
| G22-05 / measurement | Signed executions and quote changes as a measure of designated informed-cohort profits: a bound survives finite market/limit-order choice versus order role/timing breaking it. | Same-equilibrium cash/payoff accounting versus the statistic, retaining all load-bearing assumptions; a positive boundary or a certified counterexample both clarify measurement validity. | F2-deferred. Exact residual novelty and a qualifying equilibrium witness are unresolved. |
| G22-06 / measurement | Binary-market updating against a calibrated public-state model: a slope below one certifies underreaction versus different information sets explaining it. | An exactly calibrated efficient-price counterexample; a valid certificate would identify underreaction, failure prevents a false mechanism attribution. | Quick-closed for the calibration-plus-slope certificate alone. No general closure of prediction-market efficiency research. |

The closed CfD, latent-order provenance, participant-identity, race-susceptibility
and random-match-clock routes remain closed. G22-01/02 are cheap direct-prior
stops, not permission to reconstruct hidden random match events or harvest
children of that closed replay program. G22-05 asks about a scalar measurement
inside a truth-defined economic model; it does not claim to identify individual
private-information labels from anonymous field trades. No re-entry trigger is
claimed. The deferred recall and intraday-margin leads are unchanged.

## 2. Two quick exclusions with reusable content

### Net stock is not gross certificate lifecycle

Let `B` be outstanding registered certificates, `N` new registrations, `K`
cancellations and `D` deliveries on a correctly aligned lifecycle window.
The stock identity is `Delta B=N-K`. A delivery changes ownership without
necessarily changing `B`; registration, delivery and cancellation are distinct
operations [S4–S5]. Take initial stock 110, all previously delivered, and the
same observed `D=11, Delta B=0`:

- A: register and first-deliver 11 new certificates; cancel 11 old certificates.
  There are zero redeliveries.
- B: neither register nor cancel; redeliver 11 old certificates. There are
  11 redeliveries.

Both histories end with 110 certificates. This is a stock-flow observation
counterexample, not a historical event reconstruction. It does not say that
the prior paper's explicitly labelled proxy is useless or that all public
reports omit gross flows. Extra issuance/cancellation and first-delivery
lineage could change the observation contract. Under the additional matching
assumption that all and only newly registered certificates first-deliver in this window,
`D-Delta B=redeliveries+K`. Without that matching assumption, even this correction
is insufficient. The generic arithmetic does not constitute a new method paper.

### Calibration does not complete the market's information set

Let `S` be equally likely ±1 and terminal payoff `V|S` be Bernoulli with mean
`0.5+0.3S`. An external state-only benchmark has `q0=0.5` and receives `S` at
time 1, so `q1=0.5+0.3S`. The market already knows `S` at time 0:
`p0=p1=0.5+0.3S`. Every displayed forecast is calibrated for its own information
set, and market prices are conditional-expectation martingales. Yet the
population slope of `Delta p` on `Delta q` is zero.

The benchmark omits information already present in the market price; it is
not the conditional probability given *all* public market information.
Calibration and sharpness have established methodological distinctions [S14].
The recent prediction-market paper [S13] additionally examines subsequent drift,
alternative benchmarks and executable-style costs. Our example does not
replicate or refute those additional results; it closes only the shortcut
specified in G22-06. No new forecasting theorem or market finding is claimed.

## 3. F2: information rents and execution semantics

[Kadan and Manela's August 30, 2026 revision](https://arxiv.org/html/2605.11180v2)
connects informed expected profits to price/order-flow covariation under
competitive intermediation and an orthogonality condition. It also examines
discrete-time bounds, jumps, stochastic liquidity and multi-asset extensions.
Consequently, adding one of those labels is insufficient novelty. The question
here concerns the mapping from a finite execution/quote process to the same
profit object when signal receivers can supply liquidity [S6].

The overlap is substantial: informed limit-order choice is already explicit
in Kaniel and Liu [S7], finite dynamic order-book information acquisition in
Goettler, Parlour and Rajan [S8], stochastic liquidity in Collin-Dufresne and
Fos [S9], restricted market-design equivalence in Back and Baruch [S10], and
informed liquidity provision in Bloomfield, O'Hara and Saar [S11]. Hasbrouck
[S12] already models lagged trade/quote information responses. None of these
seven anchors was read as an exact proof of our proposed measurement bound;
access depth is recorded below. There is no claim that they disagree on an
identical equilibrium or that their existing methods have been superseded.

| Contract | Required interpretation |
|---|---|
| X | Declared finite economic model: terminal value and signals, designated cohorts, endowments, fees, information sets, quote grid, priority, order lifetime and complete cash/inventory state. |
| Legal action | Permit signal receivers to choose market and limit orders within one stated mechanism; compare a restricted order grammar only as a separate equilibrium with its own responses. |
| Y / estimand | Expected cash-plus-terminal-inventory trading profit of the designated informed cohort, with initial endowments subtracted and fees separately accounted for. Calling it incremental information value also requires a specified uninformed baseline. |
| Measurement | `C_pi=E sum_k Delta P_k Delta Y_k`, with the price observable, signing convention, units, partition and terminal horizon fixed. Execution flow, submitted order volume and latent cohort flow are distinct. |
| Rival predictions | A provable profit bound survives the declared finite market class; alternatively a valid equilibrium violates it after all assumptions not intentionally varied are verified. |
| Truth | Exact equilibrium and cash/payoff accounting first. The current diagnostic paths below are not this truth asset. Field validation, actor identities and cohort profits are not available from a named qualified source. |

Gross profit, willingness to pay for a signal, social information value and
asset-management fees are different objects. Any comparison must use the
same object and baseline. A finite-model result would not by itself explain
the real-market magnitude of fees.

### Diagnostic A: state weighting needs its own restriction

For a deliberately abstract extension, set independent symmetric
`X in {-1,1}`, `Z in {-2,2}`, `Y=X+Z`, and `Delta P=lambda*Y`, where
`lambda=1` when `XZ>0` and `lambda=4` when `XZ<0`. Then

\[
E[XZ]=0,\quad E[\lambda XY]=-1/2,\quad
C=E[\lambda Y^2]=13/2,\quad L=E[\lambda YZ]=7.
\]

Thus unconditional orthogonality does not imply impact-weighted orthogonality.
For deterministic impact, or an appropriate conditional orthogonality
restriction with predictable impact, this particular objection disappears.
This is a negative control for a naive generalization. **L is only a defined
noise-slippage functional here**: no fundamental-value law, competitive pricing
or strategic optimality was supplied, so L cannot be declared informed profit.
This is neither a refutation of the published theorem nor a market-equilibrium
counterexample. A conditional covariance calculation alone is not new science.

### Diagnostic B: quotation and execution need not be simultaneous

On an abstract admissible visible tape, let a quote change by one unit at an
order-entry event without a trade, and let one signed unit execute later while
enough depth remains to leave the quote unchanged. A partition separating the
events gives `sum Delta P Delta Y=0`; one joining them gives 1. The fine-path
jump covariation is zero. This is ordinary nonsynchronous-event arithmetic.
Neither tape identifies the trader's information or expected profit. It only
forces a precise price/flow/clock definition before a model comparison; adding
a generic lag kernel would collide with established trade/quote methods [S12].

## 4. The next decisive check and stop conditions

Only G22-05 survives the cheap screens. Its positive/null scientific value is
conditional; its weakest link is an **equilibrium-valid, irreducible measurement
result**, not computing capacity. The next bounded paper-only task is:

1. Fully inspect one tractable primary finite market/limit-order model and
   freeze the exact value, signals, prices, priority, baseline and profit target.
2. Verify strategic optimality, dealer competition and all balance sheets;
   calculate the statistic and the profit target under the same equilibrium.
3. Either prove the bound in that class or produce a certified violation and
   identify the smallest native assumption responsible. Then check whether
   the result is already a consequence of the primary model or a standard
   covariance/lead-lag identity.

Stop if the only result is informed traders using limit orders, ordinary
asynchronous sampling, conditional covariance algebra, a changed estimand, or
an example without equilibrium. Do not use model-generated profitability or a
renamed information signal to reopen the closed Paper G learning routes. A
nontrivial survivor would still need coverage/failure regimes and a separate
observation bridge before an empirical claim; the full fifteen-work audit and
prospective F3 forecast have not been opened.

## 5. Retained primary-source manifest

Fourteen sources support the six-program portfolio, not fourteen full audits.
Eight primary pages/documents were substantively opened; six additional works
were inspected through indexed primary text. Published outcomes are selection
context, not untouched confirmation data. No raw target market dataset was
accessed. Ancillary discovery hits are not counted as completed question
programs or retained evidence.

- **S1** [Lin, Michayluk and Zou, Does Random Auction Ending Curb Stock Price Manipulation?](https://opus.lib.uts.edu.au/handle/10453/175634), 2023. University publication record and abstract opened; estimates not independently audited.
- **S2** [Hafner and Stewart, Front-Running in Ascending Auctions](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3846363), SSRN revision August 26, 2026; indexed author abstract. Exact equilibrium proofs not audited.
- **S3** [Gehrlein, Hafner and Oechssler, The Candle Auction in the Field and the Lab](https://papers.ssrn.com/sol3/Delivery.cfm/5109856.pdf?abstractid=5109856), revised February 18, 2026; indexed author abstract. No laboratory data/reuse contract qualified.
- **S4** [Fernandes, Kunda and Robe, Commodity Futures Deliveries](https://doi.org/10.1002/fut.22585), 2025. Publisher full-text sections on delivery lifecycle, the redelivery proxy and data availability inspected; not a full replication.
- **S5** [CBOT Rulebook Chapter 7](https://www.cmegroup.com/content/dam/cmegroup/rulebook/CBOT/I/7.pdf), retrieved September 9; registration/cancellation procedure text inspected. Current consolidated text includes dated future provisions; it is not a historical-version pin or a joined event asset.
- **S6** [Kadan and Manela, The Value of Information: A Puzzle](https://arxiv.org/html/2605.11180v2), v2 August 30, 2026. Sections 2 and selected 4.2 subsections inspected; no empirical replication.
- **S7** [Kaniel and Liu, So What Orders Do Informed Traders Use?](https://doi.org/10.1086/503651), 2006. JSTOR abstract opened and author-hosted introduction indexed; complete model/proofs not yet audited.
- **S8** [Goettler, Parlour and Rajan, Informed traders and limit order markets](https://doi.org/10.1016/j.jfineco.2008.08.002), 2009. Indexed publisher introduction/model-scope text; no numerical equilibrium or data accessed.
- **S9** [Collin-Dufresne and Fos, Insider Trading, Stochastic Liquidity, and Equilibrium Prices](https://doi.org/10.3982/ECTA10789), 2016. Publisher abstract opened; stochastic liquidity is an existing parent.
- **S10** [Back and Baruch, Working orders in limit order markets and floor exchanges](https://doi.org/10.1111/j.1540-6261.2007.01252.x), 2007. Indexed university abstract; its market-order and pooling assumptions must be retained.
- **S11** [Bloomfield, O'Hara and Saar, The Make or Take Decision](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=336683), September 2003 working paper, published JFE 2005. Indexed author abstract; no claim of accessible fresh laboratory truth.
- **S12** [Hasbrouck, Measuring the Information Content of Stock Trades](https://doi.org/10.1111/j.1540-6261.1991.tb03749.x), 1991. Publisher abstract opened; lagged trade/quote measurement parent.
- **S13** [Angelini and De Angelis, When Do Markets Fully Process Public Information?](https://arxiv.org/html/2606.07811v1), v1 June 5, 2026. Benchmark and subsequent-drift sections inspected; not an audit of every empirical result.
- **S14** [Gneiting, Balabdaoui and Raftery, Probabilistic Forecasts, Calibration and Sharpness](https://doi.org/10.1111/j.1467-9868.2007.00587.x), 2007. Indexed publisher abstract; existing forecast-evaluation parent.

Records: `research/paper_g/cycle22_question_screen_20260909.yaml` and
`research/paper_g/information_rent_source_screen_20260909.yaml`. There is no
outcome, implementation, simulation, GPU, purchase, outreach, participant,
EcoMD-integration or candidate-harvesting authorization. No T0 probability is
backfilled. Verification provenance is kept separately under `logs/private/`.
