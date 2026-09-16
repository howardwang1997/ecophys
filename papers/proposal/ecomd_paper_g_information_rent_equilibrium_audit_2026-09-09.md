# Paper G information-rent measurement — equilibrium follow-up

September 9, 2026. **Private/internal, exploratory F2 follow-up to Cycle22.**
No new search cycle, empirical result, F3 audit, forecast or machine card.

Later status: the [final bounded resolution](ecomd_paper_g_information_rent_resolution_2026-09-09.md)
closes the parent candidate. The decision and next-check allowance below are
the historical state after the first equilibrium follow-up.

**Decision:** retain the parent question as F2-deferred, with weaker support
for the proposed counterexample route. A solved parameter point of the
Kaniel–Liu equilibrium characterization gives informed profits below both
explicitly defined covariation statistics. An elementary argument excludes
the centered-limit-price uniform-value family as a counterexample for the
posterior-mark statistic. This is a useful analytic baseline, not an
irreducible new measurement theorem or a refutation of Kadan–Manela.

## 1. Primary-model boundary

[Kaniel and Liu (2006)](https://doi.org/10.1086/503651), Section II and the
Appendix A equilibrium characterization, allow informed market/limit-order
choice, competitive conditional-mean quotes and time priority. There are
three dates, continuous values/prices and one incoming unit order per date.
Uninformed direction and patience are exogenous. Information survives the
first date with probability p. Their existence/optimality argument maintains
a continuous quote-updating rule. The primary paper text was inspected through
its [full-text reproduction](https://www.researchgate.net/publication/24103582_What_Orders_do_Informed_Traders_Use).
This is the published paper, not a new independent primary work.

[Kadan and Manela v2](https://arxiv.org/html/2605.11180v2), Sections 2,
3.1 and 4.2.10–11, already connect profits and covariation under declared
assumptions and give a discrete linear-impact upper bound. Their empirical
statistic uses signed trades in time bins. The calculations below do not
establish correspondence with that empirical observation pipeline or its
economic magnitude. A Bayesian public mark is not automatically an observed
quote midpoint, and an event partition is not a minute partition.

## 2. Exact specialization and observation contract

The following are our calculations from the published equilibrium equations.
Use a centered payoff v uniform on [-1,1]; adding 2 to every value and price
gives a positive-price asset without changing any result. Set

\[
\mu=\frac13,\qquad \ell=\frac14,\qquad p=\frac67.
\]

Here mu is the uninformed arrival probability and ell their patient fraction.
All positions are unit-sized; short sales are allowed; fees and discounting
are zero. Profits mean cash plus terminal-valued inventory less initial
endowments, aggregated over all informed arrivals, before any signal cost.

Freeze the observation horizon at the first public revelation of v. Pending
orders expire then; any subsequent liquidity completion is at the known value
and outside the measured flow. This explicit terminal completion preserves
the primary model's information-profit payoffs. We do not claim to measure
covariation after disclosure or under a different order-expiry convention.
Each arrival and each disclosure is a separate event; this partition is fixed
throughout. Both price definitions below use this same economic horizon.

Let S_k be the aggressor-signed executed quantity: +1 for a market buy,
-1 for a market sell and 0 for a nonexecution event. A resting limit buyer
filled by a market sell therefore receives inventory +1 while S_k=-1.
The statistic is C=E sum_k Delta P_k S_k, with P_0=0 in centered units.

- **M:** the public conditional mean of v after the current event. It includes
  order submissions, no-order observations and disclosure. It is a theoretical
  public mark, not a quoted midpoint or a field-observed fundamental.
- **T:** the last transaction price, carried forward through nontrade events.
  Every execution before disclosure uses the primary model's competitive quote.

We verify a solution of the published equilibrium characterization, including
on-path best responses, quote Bayes equations and patient participation.
We rely on its continuous quote-updater existence argument for off-path limit
price deviations; no independent extensive-form reconstruction is claimed.
This is a finite-date, continuous-price model, not a finite-tick order-book
simulator.

## 3. Equilibrium verification

The initial ask/bid are a=3/7 and -a. Both limit prices are zero; a limit
buy has precedence over the dealer's subsequent zero bid, and the sell side
is the reflection. The informed cutoff is c=1/2:

\[
q=\frac{\mu p}{2}=\frac17,\qquad
c=\frac{a-qb}{1-q}=\frac12,\qquad b=0.
\]

For v>0 the two relevant payoffs are v-3/7 and v/7. A limit buy is optimal
for 0<v<1/2 and a market buy for v>1/2; selling gives a nonpositive payoff.
The negative-value case is symmetric. Indifference points have probability
zero. The initial pricing and limit-price equations reduce to

\[
-\frac{3}{16}\frac37+
  \int_{1/2}^{1}(v-3/7)\frac{dv}{2}=0,
\qquad
\int_0^{1/2}v\frac{dv}{2}+
 \frac14\int_{-1}^{0}v\frac{dv}{2}=0.
\]

Both are exact. A patient uninformed buyer's expected completion cost is
1/7, below the immediate ask 3/7; the seller's condition is symmetric.

The first-order probabilities are Pr(MB)=Pr(MS)=7/24 and
Pr(LB)=Pr(LS)=5/24. Conditional densities following a buy are

\[
f(v\mid MB)=\frac3{14}+\frac87\mathbf1_{(1/2,1)}(v),\qquad
f(v\mid LB)=\frac1{10}+\frac85\mathbf1_{(0,1/2)}(v),
\]

on [-1,1], with means m_MB=3/7 and m_LB=1/5. Sell histories reflect these.
If information remains private, the next ask x and bid y obey

\[
m_h-x+4E[(v-x)_+\mid h]=0,\qquad
m_h-y-4E[(y-v)_+\mid h]=0.
\]

They are

\[
(x,y)_{MB}=(A,0),\quad
A=\frac{45-\sqrt{353}}{38},\quad 19A^2-45A+22=0,
\]
\[
(x,y)_{LB}=(B,0),\quad B=\frac6{17},\quad17B^2-23B+6=0.
\]

The selected roots satisfy A in (1/2,1) and B in (0,1/2); the other roots
are outside their integration regions. The second informed arrival buys for
v>x, sells for v<y and abstains otherwise. No profitable limit execution
opportunity remains before disclosure. These are optimal one-unit choices.
The Bayes equations make the dealer's expected profit zero on the trades
actually allocated to it; the resting order has priority on its own side.

## 4. Cash, inventory and covariation in the same equilibrium

The first informed arrival contributes, unconditionally over arrival type,

\[
\Omega_{1,MO}=\frac3{28},\qquad
\Omega_{1,LO}=\frac1{84},\qquad \Omega_1=\frac5{42}.
\]

These follow by integrating (v-3/7) over (1/2,1) and v/7 over (0,1/2),
including the reflected sell side and the informed arrival probability 2/3.
For the second opportunity conditional on history h and survival, the
informed profit is x_h/6. Therefore

\[
\Omega_2=\frac A{12}+\frac5{238},\qquad
\boxed{\Omega=\frac A{12}+\frac{50}{357}\simeq0.1975378333.}
\]

The independently grouped balance sheets are

| Cohort | Expected trading profit |
|---|---:|
| First informed, market orders | 3/28 |
| First informed, limit orders | 1/84 |
| First uninformed, impatient | -3/28 |
| First uninformed, patient | -1/84 |
| Second informed, including survival probability | A/12+5/238 |
| Second uninformed, including survival probability | -(A/12+5/238) |
| Dealer, aggregate | 0 |

The rows sum to zero. These are cohort totals, not a table of bilateral
counterparties. In particular, the first patient cohort's fills are selected
by subsequent trading; its inventory innovations cannot be substituted for
exogenous direction draws. Gross informed profit equals aggregate uninformed
loss here, with no unexplained dealer rent or omitted inventory payoff.

For M, the first contribution to C is 1/4. At the second opportunity,
competitive execution implies

\[
E[(\Delta M)S\mid h]
=E[(v-m_h)S\mid h]
=\Omega_{2\mid h}+G_h,
\]
\[
G_h=\frac23\{(x_h-m_h)\Pr(v>x_h\mid h)
 +(m_h-y_h)\Pr(v<y_h\mid h)\}\geq0.
\]

This is a conditional-expectation identity, not a new measurement method.
Direct substitution gives

\[
G_{MB}=\frac{106-125A}{147},\qquad G_{LB}=\frac{56}{1275},
\]
\[
\boxed{C_M=\Omega+\frac{11}{84}
  +\frac12G_{MB}+\frac5{14}G_{LB}
  \simeq0.4114461610>\Omega.}
\]

After an initial market order M_1=T_1. After a limit buy, M_1=1/5 but
T_1=0, and E[S_2|LB]=2/15. Reflection gives the same additional product on
the sell side. Hence, under the identical horizon and event partition,

\[
\boxed{C_T=C_M+\frac1{105}\simeq0.4209699706>\Omega.}
\]

This does not validate arbitrary quote midpoints, calendar bins, after-news
completion sequences or unidentified cohort profits in observed markets.
It gives a same-equilibrium baseline for two fully declared price processes.

## 5. Exclusion of the centered-limit uniform family

The point above is not the only exclusion. Keep v uniform on [-1,1],
mu, ell, p in (0,1), and the published equilibrium class, and impose a limit
buy price equal to the prior mean: b=0. The limit-price equation gives
ell=c^2. Write q=mu p/2. The remaining equations imply

\[
a=c(1-q)=\frac{(1-\mu)(1+c)}{2(1+\mu c)}.
\]

Since 0<q<mu/2,

\[
1-c>\mu(1+2c^2)-\mu^2c^2>\mu,
\qquad q<(1-c)/2.
\]

The first-event covariation minus all first-arrival informed profit is

\[
C_{M,1}-\Omega_1
=(1-\mu)c\{(1-c)-q(1-c/2)\}>0.
\]

The second-event contribution minus second-arrival profit is nonnegative by
the preceding G_h identity, replacing 2/3 by 1-mu: competitive asks/bids bracket the conditional
mean. Disclosure changes M with S=0. Consequently **C_M>Omega throughout
this feasible family**. Rescaling the price level or payoff range does not
change the sign.

This elementary exclusion uses the established equilibrium characterization
and ordinary conditional expectations. It is not a new universal market law.
Only the centered-limit uniform family is excluded as a counterexample for
M; the transaction-price calculation above is certified at the explicit
parameter point, not throughout this family. We do not infer validity for
all value distributions, all limit prices or all finite markets.

## 6. Consequence for topic selection

Close the narrow counterexample formulation
`paper_g_information_rent_zero_center_limit_counterexample`. The broader
`paper_g_information_rent_execution_measurement` remains F2-deferred, with
no qualifying violation and no established residual novelty. The earlier
abstract weighting and separated-event examples remain diagnostics; this
follow-up does not retrospectively turn them into equilibrium evidence.

At most one further bounded paper-only check is justified: derive the sign
of C-Omega in the remaining Kaniel–Liu class, starting with noncentered limit
prices, while retaining the same cohorts, horizon and two observation
definitions. Every parameter choice must satisfy equilibrium and participation,
and the off-path assumptions must remain explicit. Do not start a broad
model search, field study or a new topic cycle merely to find a violation.
If that check supplies only the existing conditional-expectation decomposition
or known informed order choice, close the current candidate for lack of an
irreducible measurement result. A violation would still need a smallest
economic failure condition and novelty review before escalation.

No new source work is counted: one deeper-access evidence record is linked
to the existing Kaniel–Liu parent. Cycle22's original counts and dispositions
remain historical, with this follow-up linked. No new re-entry trigger,
forecast, outcome access, implementation, simulation, GPU, purchase, outreach,
participant action or EcoMD integration is authorized.
