# Paper G continuation — tokenized NAV measurement capability audit

**PRIVATE / INTERNAL — exploratory source and analytic audit; not public or
confirmatory evidence.** Literature cutoff: 2026-09-09.

The Arctic shared-service formulation remains closed at Cycle28 F2. Its
proofs are retained; adding bond types, parameters or simulation does not
remove its contribution blocker. Paper G discovery continues.

This session audits a proposed measurement capability before any candidate
harvesting. It is **not Cycle29**, an F3 review or an activated topic. The
observation-identification family is already saturated. The tested trigger
does not remove a recorded blocker; no new candidate is authorized.

## Source-led capability claim

Could a recently encountered tokenized-fixed-income screening criterion,
together with issuer documentation, identify whether a published series
contains market information and thereby reopen the measurement family?

Three primary sources were retained and selected source bodies inspected:

1. Alkhamov and Kriuk, *Price-Discovery Admissibility in Tokenized Fixed
   Income*, arXiv2606.13822v1, 11 June2026, especially Section3.2. Its screen
   uses a lag-one correlation threshold of0.10 and a dispersion limit. The
   authors explicitly acknowledge false admissions and false rejections
   and do not claim that passing proves efficient pricing.
   [Primary text](https://arxiv.org/html/2606.13822v1).
2. Ondo's OUSG overview, current documentation read2026-09-09, “How It
   Works.” It describes subscriptions/redemptions using NAV and an onchain
   oracle updated from the fund's business-day NAV. This establishes the
   documented origin of that oracle, not an independently negotiated
   secondary-market execution price or a historical deployment pin.
   [Issuer documentation](https://docs.ondo.finance/qualified-access-products/ousg/overview).
3. Franklin OnChain U.S. Government Money Fund's2026 filed prospectus/SAI,
   accession000165558926000970, “Pricing Shares.” It describes amortized-cost
   valuation, next-NAV order pricing and a separate market-value comparison.
   Accounting and market-valued quantities therefore have different roles.
   [Issuer filing](https://www.sec.gov/Archives/edgar/data/1786958/000165558926000970/c485bpos.htm).

The paper's realized product classification, fitted parameters and returns
were not reanalyzed or used to select a numerical target. No raw outcome
asset was accessed. Current issuer documentation does not verify every
historical observation used in the paper. No product is reclassified here.

## Three targets that must be distinguished

| Target | Required meaning | What is insufficient |
|---|---|---|
| Inherited information | A published value responds to information already in the underlying benchmark or portfolio | Low or high autocorrelation of the residual alone |
| Incremental token-market information | Negotiated token prices add information beyond the benchmark and the complete publication process | A NAV oracle, transfer record or benchmark correlation alone |
| Slow-basis model suitability | The chosen observation frequency resolves the persistence being estimated | Treating a convenient dynamic-model screen as a universal information test |

Administrative publication can transmit genuine underlying-market
information. “Administrative” and “informative” are not complementary
statistical hypotheses without a narrower target. In particular, a
publication can contain inherited information without any independent
token-market price formation.

## Diagnostic A — fast informative adjustment can fail a daily gate

This is a constructed observation model, not a fitted token economy or a
complete equilibrium theorem. Let r(t) be the contemporaneously known,
maturity-matched benchmark yield, and suppose a negotiated token quote has
yield y(t)=r(t)+b(t). The economic basis is b(t)=a*S(t), where a>0 and S
is a stationary symmetric two-state process switching sign at rate lambda.
The basis is independent of the benchmark. A benchmark innovation therefore
enters y immediately with coefficient one.

For an observation separation Delta, let N be the number of sign switches.
Since N is Poisson(lambda*Delta),

\[
\operatorname{Corr}(b(t),b(t+\Delta))
=E[(-1)^N]=e^{-2\lambda\Delta},
\quad
\operatorname{Var}(b(t+\Delta)-b(t))
=2a^2(1-e^{-2\lambda\Delta}).
\]

Take time in days and lambda=log(20)/2. Daily correlation is1/20=0.05;
one-minute correlation is20^(-1/1440)>0.99. The very same process crosses
the0.10 screen solely through the observation separation. Amplitude a
can be arbitrarily small, so high dispersion is not needed for this result.

This need not require a frictionless same-claim arbitrage. For a claim with
remaining maturity tau<=tau_max, the corresponding quote-price ratio to
the reference is exp(-tau*b). Choosing a small enough that
exp(a*tau_max)-1<=c places the entire fixture inside a declared proportional
conversion/trading-cost band c>0. This is a feasibility check, not a claim
that a particular issuer has these costs or that the process is an
equilibrium of an otherwise unspecified economy.

Thus daily persistence is not a necessary condition for inherited market
information over this wider observation class. The example is outside a
class that *assumes* a multi-week basis half-life. It does not refute a
screen restricted to fitting slow dynamics, identify actual token-market
information leadership, or establish a new financial-physics law.

## Diagnostic B — persistence cannot identify the source of innovation

Let a purely administrative publisher report y_t=r_t+b_t, where

\[
b_t=0.9b_{t-1}+\eta_t.
\]

Initialize in its stationary distribution. Innovations eta_t are centered,
independent, bounded and have variance0.19*a^2. Then Var(b_t)=a^2,
Corr(b_t,b_{t-1})=0.9 and SD(b_t-b_{t-1})=sqrt(0.2)*a. Against any fixed
positive comparison dispersion, choose a small enough to pass a limit of
three times that dispersion. A comparison population of identical such
publishers also passes, since its median dispersion equals each member's.

There is no negotiated token price in this construction. The publisher
can inherit information through r_t while its residual dynamics arise
from its own reporting rule. Conversely, assigning the same innovation
law to a token-specific economic state produces exactly the same observable
law of (r_t,y_t). Observing these series alone cannot label the innovation's
origin; source information or independently anchored additional observables
must restrict the model class.

The source paper already allows smoothed accounting series to pass. This
diagnostic therefore does **not** discover an unacknowledged sufficiency
claim or contradict its explicit caveat. It prevents promoting a weak
screen into an incremental-information certificate. No statement is made
about the actual AR coefficient or reporting process of OUSG or FOBXX.

## Trigger verdict and surviving useful work

Decision: **not_trigger**; candidate_harvest_authorized=false. The two
diagnostics are elementary sampling and observational-equivalence results.
They reinforce the recorded need for an externally anchored observation
contract and leave the independent-contribution blocker intact. There is
no new uniform estimator, identified mechanism or nontrivial bound here.

Issuer documentation provides useful origin labels for specified published
quantities. It does not alone supply matched historical raw measurements,
independent negotiated prices, information assignment or a validation
population. These limitations apply to the reviewed capability; they do
not establish that such records do not exist elsewhere.

The reusable output is a source-origin schema and two analytic controls:
one rejects an unrestricted daily-persistence necessity claim; the other
requires abstention on innovation origin without source restrictions.

## Paper-only truth-asset preflight

The requirements below are fixed for evaluating a future asset, with
availability explicitly unqualified. This plan grants no collection,
implementation, participant, outreach or outcome-access authority.

- **Estimand family:** classify documented value origins and, only if the
  additional truth exists, measure incremental information in negotiated
  token quotes/executions conditional on a fixed benchmark and publication
  operator. Exclude profitability, welfare and general causal price discovery.
- **Assignment/interference:** descriptive origin labels need source truth,
  not randomization. A causal information-response extension needs a named
  independently assigned information change, participant exposure, release
  timing and cross-venue interference. None is qualified in these sources.
- **Lifecycle/replay:** require immutable event IDs; asset/share class;
  NAV valuation time, publication time and chain inclusion time; oracle
  version; price origin; quoted/executed size; submitted, cancelled, filled
  and unfilled states where executions are studied; subscription/redemption
  request, acceptance, rejection and settlement; fees, distributions,
  rebase/share conversion and benchmark tenor/clock. A Transfer event is
  not an execution-price label. Replay only the declared observation
  operator; do not claim a full adaptive-market counterfactual.
- **Rights/ethics/release:** require a versioned schema, lawful archive and
  explicit research/derived-release rights. Do not infer rights to investor
  identity, private holdings or account joins from public documentation.
  No identities are collected in this audit; no participant work is planned.
- **Untouched confirmation:** before outcome access, bind whole-source or
  prospective-time partitions to immutable manifests and fix calibration,
  false-rejection, abstention and precision targets. No such archive,
  partition, release date or sample size is qualified today. Existing paper
  results cannot serve as untouched confirmation.
- **Independent replication:** require an independently governed issuer or
  venue implementing the same measurement and lifecycle definitions. OUSG
  and FOBXX document different valuation conventions; they are useful
  documentary controls, not an established common-estimand replication pair.
- **Cost/stop:** follow-up is limited to reviewing a newly supplied primary
  source or an exact analytic claim, with monetary cost0 and GPU budget0.
  Stop before harvesting or collecting if origin labels, clocks, rights,
  confirmation or the intended assignment remain unqualified. Do not scan
  more wrappers merely to repeat the same audit. Any actual asset requires
  a new append-only re-entry decision before topic generation.

## Intake and accounting

The queue-bounds paper and Rule605 report lead were checked against earlier
records and not reopened. Their prior audits already record the relevant
capabilities and blockers. Other auction and fixed-income search hits
remained unformulated intake. Hasbrouck's1995 abstract was background intake,
not a new audited theorem or retained measurement source.

This session adds one re-entry audit, not a search cycle or terminal route.
Cycle count remains19, raw questions131 and cards0. Route status is
unchanged. No forecast, machine decision, sandbox, solver, simulation,
GPU work, account connection, purchase, outreach, publication, commit or
push was performed. Mathematical derivations are paper-only.
