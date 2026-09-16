# Paper G Cycle 25: redemption jurisdiction and Treasury buyback capacity

**PRIVATE / INTERNAL — exploratory selection, not public or confirmatory
evidence.** Literature cutoff: September 9, 2026.

Two compact F1 screens produce no survivor. Multi-country stablecoin
redemption routing and Treasury buyback inventory relief both have direct
primary predecessors. The retained calculations distinguish redemption
requests from cash paid, and an operation ceiling from realized purchases.
They are elementary diagnostics, not independent scientific discoveries.

Structured record: `research/paper_g/cycle25_question_screen_20260909.yaml`.
Reading and formulation were interleaved; this is not preregistration.

## Eligibility and questions

Registry/ledger searches found no exact prior node for these two formulations.
The stablecoin question concerns coissuer redemption eligibility and lawful
resale, not Cycle11's peg-restoration/controller question. The Treasury question
concerns the stated buyback ceiling, not central-clearing networks. Closed
generic identification, public crypto-ETP lifecycle, CfD and simulator parents
remain closed. No hidden-account inference or threshold event-study candidate
was harvested. This is a two-program cycle, not a twelve-program quota exercise.

| ID | Object and competing explanations | Discriminator and value under either answer | Decision |
| --- | --- | --- | --- |
| G25-01, theory | A fungible coissued coin with region-specific direct redemption. Initial regional ownership bounds local requests, versus eligible buyers importing claims through resale. | Hold eligibility fixed and trace a fully funded lawful resale and redemption request. Insulation would support an ownership-based bound; failure identifies the missing funding and transfer state. | F1 closed: the broad routing mechanism is direct prior art; the cash-flow calculation adds no irreducible theorem. |
| G25-02, empirical intervention | An increase in a Treasury buyback operation ceiling. A binding ceiling releases dealer inventory, versus a slack ceiling with unchanged purchases and possible expectation/selection effects. | Check whether changing the cap changes accepted quantity under a fixed offer schedule, before proposing a causal comparison. A first stage would justify further design work; a null prevents equating policy capacity with executed demand. | F1 closed: broad inventory-relief novelty is already covered; the announcement alone does not establish a purchase-dose change. |

These are our screening hypotheses, not a verified disagreement between two
matched primary models. No F2 contract or full hostile audit was opened.

## A. Eligible resale, requests and cash settlement

Circle's July 10 whitepaper, D.1, permits eligible EEA holders to request
redemption of supported USDC irrespective of which coissuer issued it; rights
transfer with ownership subject to eligibility. This is issuer documentation,
not our independent opinion on enforceability. [Circle USDC whitepaper](https://www.circle.com/legal/mica-usdc-whitepaper).

The July 13 redemption policy includes EEA scope, verification requirements
and a stress clause allowing processing delays when interissuer reserve
rebalancing is late. A par claim does not specify immediate cash availability.
[Circle redemption policy, sections 1, 4 and 8](https://www.circle.com/legal/mica-redemption-policy).

Define a hypothetical one-batch accounting model, with dollar par value one.
All sellers and buyers are lawful, transactions pass the specified compliance
checks, and eligible buyers purchase for their own account. There is no false
identity, nominee arrangement or prohibited-person transaction. Fix:

- outside tokens offered for sale, X; purchase price p > 0;
- eligible buyers' available dollars K, with no credit or cash recycling;
- locally held tokens already submitted for redemption, L;
- issuer cash available by horizon T, B; additional reserve cash actually
  received by T, R; no other cash inflows, outflows or asset sales.

The maximum **feasible purchase quantity**, if sellers offer X at p, is

\[
q_{\max}=\min(X,K/p).
\]

For a chosen feasible purchase q, buyers can submit L+q in total redemption
requests. If the issuer pays as much as available cash permits, pending par
requests at T are

\[
U(T)=[L+q-B-R]_+,
\quad P(T)=\min(L+q,B+R).
\]

These are cash accounting identities under declared assumptions. For
X=100, p=.99, K=99, L=10 and B=30, the purchase q=100 is feasible. Total
requests are 110, exceeding the initial local holdings of 10. With R=0,
payments are 30 and pending requests 80; with R=80, payments are 110 and
pending requests zero. The ownership/eligibility rule is identical in both
cases. Restricting q through K can reduce routing; ownership eligibility
alone does not imply a bound by initial local token holdings.

The example does not show that a rational buyer would choose q=100 when
payments are delayed. Price formation, anticipation, financing costs and
reserve-transfer feasibility are unspecified. Pending requests are neither
an observed default nor proof of insolvency. Real reserves, redemption
times and cash movements were not accessed or estimated.

Martino, Monnet and Perotti already discuss eligible-buyer resale and the
limitations of reserve mobility. Their September 7 Policy Insight also
distinguishes discretionary recovery from automatic contingent measures.
The issuer's stress clause therefore does not establish a contradiction
with their policy argument. [CEPR Policy Insight 151, sections 4.1–4.2](https://cepr.org/system/files/publication-files/306375-policy_insight_151_stablecoins_without_borders_stablecoin_multi_country_issuance_and_dollar_run_risks_in_europe.pdf).

**Close the proposed independent routing contribution.** A finite-budget
accounting bound is useful for model specification but does not establish
a new equilibrium, welfare result or optimal intervention.

## B. A larger ceiling is not an observed purchase increase

Treasury announced on August 19 that maximum operation sizes for the
10–20 and 20–30 year nominal sectors would rise from $2 billion to at
least $4 billion, effective September 9 through November 4. It cited
strong offers in those sectors. This is an announced capacity change,
not evidence of actual purchases or random sector assignment.
[Treasury announcement](https://home.treasury.gov/news/press-releases/sb0607).

For a deliberately simplified fixed acceptable-offer quantity A and ceiling
M, suppose the buyer accepts up to its limit, so Q(M)=min(M,A). At the
illustrative M=2 to M=4 change, measured in billions,

\[
Q(4)-Q(2)=
\begin{cases}
0,&A\leq2,\\
A-2,&2<A<4,\\
2,&A\geq4.
\end{cases}
\]

For A=1, the ceiling doubles while executed demand is unchanged. This is
not a model of Treasury's full acceptance/pricing discretion, and the
announced new ceiling is **at least** 4. A zero contemporaneous purchase
change also does not rule out effects through future demand expectations.
The calculation only rejects an automatic equality between ceiling and
purchase dose. No announcement-window return, spread, offer or result was
read for the target intervention, and no causal effect was estimated.

Zhou's 2025 paper already directly studies security liquidity and dealer
inventories under Treasury buybacks, including a selection instrument and
an inventory-cost mechanism. Its abstract was sufficient to reject broad
first-study novelty; we did not independently audit its identification or
replicate its estimates. [IMF Working Paper 2025/088](https://www.imf.org/en/publications/wp/issues/2025/05/09/testing-the-liquidity-support-effects-of-the-u-s-566801).

**Close the broad inventory-relief pitch.** A new date alone does not supply
an independent scientific contribution. Neither all buyback research nor a
properly qualified distinct estimand is ruled out.

## Disposition and next decisive update

Counts: **2 raw / 2 F1 / 0 F2 / 0 F3 / 0 cards**. Five retained primary
sources: one policy paper with selected substantive sections, two issuer
documents, one official announcement, and one research abstract. No full
paper audit, outcome asset, prospective forecast or new trigger was created.
Broader indexed stablecoin-arbitrage, insurance and debt-management intake
did not become additional raw questions or evidence records.

Reopening either precise formulation requires an explicit result or lawful
control asset that removes its recorded blocker and the applicable validated
trigger. A larger dataset, another coin, a new policy date or an extra
unmeasured friction is insufficient. Future eligible intake should prioritize
a primary source that supplies a distinct discriminating intervention or
measurement truth; do not extend these closed questions by adding a simulator.
No implementation, outcomes, compute, accounts, outreach or publication is
authorized by this record.
