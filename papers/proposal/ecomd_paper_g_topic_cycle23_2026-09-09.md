# Paper G Cycle 23: swing pricing, cost incidence and liquidity provision

**PRIVATE / INTERNAL — exploratory research selection; excluded from public
paper and release evidence.** Literature cutoff: September 9, 2026. No
prospective forecast, target outcome access or scientific execution.

Four compact F0/F1 questions terminate at direct primary-work collisions.
There is no F2 survivor or machine card. The useful result is a precise
separation of cost recovery, quoted-price variation, conditional redemption
payments and endogenous liquidity provision. The calculations below are
elementary diagnostics and substitutions into existing formulas, not new
theorems, equilibrium counterexamples or observed market effects.

The question record is
`research/paper_g/cycle23_question_screen_20260909.yaml`; canonical dispositions
are in the route graph and search-cycle ledger. Source scouting and question
formulation were interleaved. This record is exploratory, not preregistered.

## Eligibility and bounded scope

The graph, evidence registry and cycle/re-entry ledgers were checked before
screening. Open-end fund share pricing is a new native parent in this recorded
portfolio; ETF authorized-participant delivery and previously closed generic
latent-state claims are not reopened. Marketron was an intake duplicate of the
September 4 `marketron_gauge_reduction_screen_20260904` audit and was stopped;
it contributes no new question, source record or trigger here.

This is a four-question compact cycle: two theory, one measurement and one
empirical program, all from a native pricing/withdrawal rule. There is no
verified same-state disagreement between primary models. The twelve-program
sampling targets are not invoked. Five fund-specific primary works and one
foundational abstract were inspected, with at most three anchors per F1
question. This is not six complete paper audits or a fifteen-work neighborhood.

## Question decisions

| ID / archetype | Native fork and cheapest discriminating result | Value of either answer | F1 decision |
| --- | --- | --- | --- |
| G23-01 / theory | For predetermined gross share subscriptions/redemptions at one common transaction NAV, can all execution cost be recovered for stayers despite a benefit to opposite-side traders? Compute post-settlement assets per remaining share under the exact same cost and price rule. | A positive result specifies an implementable cost-neutrality condition; a negative result identifies missing charges or a policy constraint. | Deduplicated: net-share cost accounting and opposite-side benefits are already explicit in Roncalli; SEC discusses the distribution. Diagnostic A resolves the apparent contradiction. |
| G23-02 / measurement | Does extra volatility of the published swung NAV represent extra variation in the underlying portfolio value, or variation in the applied pricing factor? Decompose the returns and compare admissible price/factor paths. | Distinguishing the terms validates a risk estimand; failure specifies the extra pricing record needed. | Deduplicated: BIS explicitly separates accounting and portfolio effects. Diagnostic B is a measurement guardrail, not a new recovery method. |
| G23-03 / theory | With the portfolio, liquidation technology and outflow fixed, must swing pricing raise the payment-based liquidity provision index, or can charging liquidation costs lower it? Compare the two contract payments on one feasible state. | Either sign establishes the conditional contract comparison and prevents confusion with the endogenous portfolio effect. | Deduplicated: Ma–Xiao–Zeng directly characterize both contracts. Diagnostic C is an existing-formula substitution. |
| G23-04 / empirical | Does a specified swing-pricing rule reduce stress withdrawals through first-mover incentives, or can selection/common stress account for the association? Require a comparable rule assignment and investor/flow history. | A positive effect supports the rule's incremental role; a null bounds that benefit in the defined population. | Deduplicated: Jin et al. directly study this broad question. BIS's country-availability contrast is not the same treatment and conditioning set. No causal replication or data qualification was attempted. |

Each formulation closes for the broad contribution proposed here. This does
not close every fund-liquidity question or establish that no narrower new
result exists. No surviving program needs a full truth-asset contract now.

## Diagnostic A: net cost recovery and opposite-side benefit can coexist

Let the initial fund contain \(N\) shares with gross value \(p\) per share.
Fix share quantities \(S\) subscribed and \(R\) redeemed, signed net issuance
\(n=S-R\), realized execution cost \(C\geq0\), and common transaction price
\(p+\delta>0\). Require \(N+n>0\). With no other cash flows,

\[
A'=Np+n(p+\delta)-C,\qquad
p_{after}=p+\frac{n\delta-C}{N+n}.
\]

Thus stayers retain gross value exactly when \(n\delta=C\). If execution
cost itself depends on the induced payment/liquidation, this is an implicit
consistency condition, not a solved policy. A net outflow \(q=R-S>0\)
requires a discount \(C/q\). Redeemers contribute \(RC/q\), subscribers
benefit by \(SC/q\), and the difference retained is exactly \(C\).

For \(N=100,p=100,R=20,S=10,C=20\):

| Declared illustrative rule | Transaction NAV | Net cost retained | Stayer NAV after settlement |
| --- | ---: | ---: | ---: |
| Discount \(C/R\) | 99 | 10 | \(899/9\approx99.8889\) |
| Discount \(C/(R-S)\) | 98 | 20 | 100 |

These are different rules. The SEC's historical distributional example is
not a mandate to use our first denominator. Roncalli's ideal net-cost formula
and its opposite-side benefit are explicit prior art. A subscriber benefit
alone therefore does not establish incomplete recovery. [SEC 2016, printed
p.160](https://www.sec.gov/files/rules/final/2016/33-10234.pdf);
[Roncalli 2021, §§3.3.2–3.3.3](https://arxiv.org/pdf/2110.01302).

For \(n=0,C>0\), no common price change can recover this stipulated cost;
that conditional identity does not imply positive cost when actual flows
net completely. Amount-denominated orders, cost uncertainty, caps and
endogenous quantities require a different contract and are not resolved here.

## Diagnostic B: observed price variation is not the underlying-value target

Define \(P_t=V_t(1+s_t)>0\), where \(V_t\) is the unswung per-share value
under the realized policy and \(s_t\) is the signed swing factor. Then

\[
r^P_t=r^V_t+\Delta\log(1+s_t),\qquad
\operatorname{Var}(r^P)=\operatorname{Var}(r^V)+
\operatorname{Var}(\Delta\ell)+2\operatorname{Cov}(r^V,\Delta\ell).
\]

The covariance prevents an unconditional sign claim. Take observed
\(P=(100,99,100)\), negative net flows at every date, and a declared toy
factor limit of 2% in magnitude:

* Path A: \(s=(-.01,-.01,-.01)\), \(V=P/.99\).
* Path B: \(V=(100/.99,100/.99,100/.99)\),
  \(s=(-.01,-.0199,-.01)\).

Both generate the same published price and flow direction, but only A has
nonzero underlying returns. This is a factorization example with different
unobserved value/cost paths, not two equilibria, a same-full-state market
counterexample, or an assertion about a current legal cap. Known exact factors
would recover \(V\) algebraically. They would not by themselves recover the
counterfactual portfolio under a different policy.

The distinction is already developed in [Lewrick and Schanz, BIS Working
Paper 664, §2.2, equation (2)](https://www.bis.org/publ/work664.pdf).
Our log-return notation is an elementary restatement, not their price-level
formula quoted as a new statistic.

## Diagnostic C: a conditional payment comparison is not an equilibrium gain

Use cash \(x=1/5\), illiquid holdings \(y=4/5\), valuation
\(\beta(R)=1\), liquidation discount \(\phi=1/5\), and outflow
\(\lambda=1/2\). The common direct-liquidation benchmark is
\(x+(1-\phi)y\beta=21/25\). Outflow exceeds the cash threshold \(1/5\)
but lies below the unswung solvency threshold \(21/25\).

Substitution into the published contract formulas gives

\[
LPI_f=\frac{1}{21/25}-1=\frac4{21},\qquad
LPI_s=\frac1{1-(1-1/2)/5}-1=\frac19,
\]
\[
LPI_s-LPI_f=-\frac5{63}.
\]

Payments per redeeming share are respectively 1 and \(14/15\).
The formulas are from [Ma, Xiao and Zeng, equations (1.4), (5.1), and the
proof of Proposition 2](https://academic.oup.com/rfs/advance-article/doi/10.1093/rfs/hhaf105/8343552).
The paper also studies endogenous portfolio choice. Our feasible conditional
point certifies neither optimal portfolios nor the selected outflow equilibrium;
it cannot contradict an ex-ante gain or measure welfare or real-market risk.

Crucially, their swung contract incorporates liquidation costs into the
post-cost NAV, with costs shared across agents. It is not Diagnostic A's
requirement to preserve stayers' pre-cost NAV. These two uses of “swing
pricing” must not be silently treated as the same treatment. A smaller
conditional payment can coexist with different run incentives and a different
optimal portfolio; no universal sign follows for the total policy effect.

## Empirical collision and remaining truth requirements

[Jin, Kacperczyk, Kahraman and Suntheim, RFS 35(1), 2022,
1–50](https://academic.oup.com/rfs/article/35/1/1/6162183) directly analyze
alternative pricing, stress withdrawals and first-mover incentives using
UK corporate-bond fund investor transactions. That occupies G23-04's broad
pitch. The BIS country-availability comparison has different assignment,
fund composition and conditioning. Different findings cannot be promoted
into a same-native-state disagreement. This cycle audits neither paper's
complete causal identification and does not independently reproduce its
published estimates.

Any substantively new empirical formulation would first need the actual
rule/factor history, gross and net orders with cancellation/cutoff state,
asset execution and cost records, investor assignment and interference,
rights, untouched confirmation and independent replication. This list is a
boundary on interpretation, not an authorized data search or a new candidate.

## Decision and next update

Counts: 4 raw / 4 F1 / 0 F2 / 0 F3 / 0 cards; all four broad pitches
deduplicated. Three reusable paper-only diagnostics; zero simulator runs,
outcome assets or prospective forecasts. Primary documents are literature
context, not independent confirmation data. The Diamond–Dybvig foundational
abstract was read only for context and supports no additional novelty claim.

Do not spend the next turn extending these four formulations with extra
frictions, a new venue or a simulator name. Reconsider a closed formulation
only after a specific primary result or lawful truth/control asset removes its
recorded blocker and the applicable trigger is validated. Otherwise, the next
eligible search should begin with a new native assignment or a genuinely
matched primary-model fork, and perform the cheapest decisive check first.
No promising active Paper G candidate is established in this cycle.
