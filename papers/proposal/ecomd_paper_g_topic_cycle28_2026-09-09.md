# Paper G topic cycle 28 — Shared debt-service constraints and equilibrium computation

**PRIVATE / INTERNAL — exploratory selection record; not public or confirmatory evidence.**

2026-09-09; literature cutoff 2026-09-09. One theory/mechanism question,
one F1 screen, one F2 collision/contract audit, no F3 or machine card.
Final disposition: **closed as an independent Paper G contribution**.
The exact results below are retained as paper-only analytic fixtures.

## Question and staged decision

**G28-01:** Does replacing separate bond-issuance limits with one shared
debt-service constraint preserve rational-valued Arctic-auction equilibria,
or does coupling change their exact representation and approximation?

The native object is a seller's jointly feasible issuance of differentiated
bonds, expressed in fixed forward-converted repayment units. The rival
predictions are rationality inherited from separable supply and failure of
that inheritance under joint issuance constraints. A positive inheritance
result would extend an exact-output contract; a negative result would
identify what needs a different representation or approximation certificate.

No matching Arctic/sovereign-restructuring route was found in the route
registry. This does not reopen treasury buybacks, carbon delivery, generic
network pooling, price-only electricity settlement or other closed parents.
One question was formulated; the other indexed auction, prediction-market
and combinatorial-market leads remained intake. This is not a twelve-question
sampling cycle.

F1 used the Arctic-cost paper, the older production-equilibrium paper and
the original restructuring proposal. It found an exact two-good example
and a genuine institutional reason for a shared constraint. F2 was warranted
because the older production result uses a different economy, so it cannot
simply be asserted to prove the restricted Arctic example. F2 expanded to
six primary works, completed the analytic contract and checked a constructive
approximation twin. No claim of a prospective freeze or full paper audit
is made; reading and algebra were interleaved.

## Six-work collision map

1. Garg, Lock and Vazirani, *Efficiently Restructuring Sovereign Debt via
   Arctic Auctions with Convex Costs*, arXiv v3, 22 August 2026. Section2
   and Theorem1 assume separable stepwise costs and per-good caps; the
   rationality result does not cover our shared-cap feasible set.
   [Primary text](https://arxiv.org/html/2606.09631v3).
2. Garg and Vazirani, *On Computability of Equilibria in Markets with
   Production*, arXiv2013, Section2.1. Nonseparable production can already
   yield only irrational equilibria. Its exchange endowments, production
   inputs and profit ownership differ from our fixed-budget fixture.
   [Primary paper](https://arxiv.org/pdf/1308.5272).
3. Willems, *An Auction-Based Sovereign Debt Restructuring Mechanism*,
   March2021 author proposal, paragraphs26,36 and49. The worked example
   combines local-currency and dollar bonds within a fixed year's repayment
   total using forward rates. This motivates coupling; it is not evidence
   of a deployed rule or of our numerical costs and bids.
   [Primary proposal](https://www.imfconnect.org/content/dam/imf/Spring-Annual%20Meetings/SM21/openevents/An%20Auction-Based%20Sovereign%20Debt%20Restructuring%20Mechanism.pdf).
4. Baldwin, Klemperer and Lock, *Implementing Walrasian Equilibrium: The
   Languages of Product-Mix Auctions*, July2024, Sections5.2,5.4 and6.
   Seller supply preferences and joint quantity choices already belong
   to the PMA framework; adding a shared limit is not itself a new design.
   [Primary paper](https://www.nuffield.ox.ac.uk/economics/Papers/2024/2024-W06_PMAlanguages.pdf).
5. Vazirani, *Arctic Auctions, Linear Fisher Markets, and Rational Convex
   Programs*, arXiv v1, November2025, Sections2 and6. This supplies the
   convex-program and constant-cost context, without proving rationality
   for the coupled set below.
   [Primary text](https://arxiv.org/html/2511.21637v1).
6. Kelly, *Charging and rate control for elastic traffic*, European
   Transactions on Telecommunications8,33–37(1997), author-hosted version.
   Weighted logarithmic allocation, capacity multipliers and price
   decomposition supply the optimization parent. Our affine-cost
   specialization is derived below, not attributed as an identical theorem.
   Selected substantive primary text was inspected through indexing.
   [Primary manuscript](https://www.statslab.cam.ac.uk/~frank/elastic.pdf).

These sources do not establish a disagreement over the same complete model.
No exact prior location for the numerical fixture is claimed. The novelty
decision rests on its explicit elementary reduction and limited consequence,
not on assuming that a broader-class counterexample settles every subclass.

## Analytic truth contract

There are two divisible goods and two price-taking buyers. Budgets are
one each. Value vectors are (10,0) and (0,10). Buyer i maximizes
1+u_i dot x_i-p dot x_i subject to x_i>=0 and p dot x_i<=1.
Prices are strictly positive in a fixed numeraire; unspent money retains
unit value. The seller maximizes p dot y-c dot y over its declared set,
where c=(1,2). Budgets do not receive seller profits or other feedback.
Markets clear exactly: aggregate buyer quantities equal y.

The comparison changes only the supply set:

- Separate caps: 0<=y1<=1/2 and 0<=y2<=1/2.
- Shared cap: y1,y2>=0 and y1+y2<=1.

These are different permissible issuance rules, not two solvers of the
same rule. Forward conversion is fixed; there is no endogenous exchange
rate, default probability, strategic bid change or welfare claim. The
shared-cap equilibrium also solves the fixed-total variant y1+y2=1,
which is closer to the original proposal's example. A ceiling and an
equality remain different out-of-equilibrium feasible sets.

The response is existence/uniqueness and arithmetic representation of
equilibrium, followed by budget-feasible approximate buyer optimality
with exact issuance, clearing and seller optimality. This is analytic
truth for a constructed economy. No observed bids, participant assignment,
field outcomes, simulator lineage or implementation are required or claimed
for these narrow results. Those assets would be required for field claims.

## A. A complete rational-input/irrational-equilibrium example

Under separate caps, p=(2,2) and y=(1/2,1/2) form an equilibrium.
Each buyer spends one on her valued good. The seller fills the first cap
and is indifferent over feasible quantities of the second good, whose price
equals its unit cost. This is a rational reference outcome.

Under the shared cap, any equilibrium must fill the cap and sell both goods.
To see the first claim, if both net prices were nonpositive, p1<=1,p2<=2,
so budget-exhausting demand would total at least3/2, exceeding capacity.
Hence the seller has a positive net price and wants to use all capacity.
If a good had zero sales, its buyer would require its price to be at least10;
the other good could attract all seller capacity only at a similarly high
net price, but a unit-budget buyer cannot then absorb one unit. Thus a
corner cannot clear.

Positive sales of both goods require equal net prices:

\[
p_1=1+\lambda,\qquad p_2=2+\lambda,\qquad\lambda>0.
\]

Neither price can reach its buyer's value threshold. If p2>=10 then
p1>=9, so aggregate demand is at most1/9+1/10<1. Consequently both buyers
spend their full budgets, and clearing is exactly

\[
H(\lambda):=\frac1{1+\lambda}+\frac1{2+\lambda}=1,
\qquad \lambda^2+\lambda-1=0.
\]

The only positive root is lambda*=(sqrt(5)-1)/2. Therefore the equilibrium is

\[
(p_1,p_2)=\left(\frac{1+\sqrt5}{2},\frac{3+\sqrt5}{2}\right),\quad
(y_1,y_2)=\left(\frac{\sqrt5-1}{2},\frac{3-\sqrt5}{2}\right).
\]

All primitive inputs are integers or rationals; all four equilibrium
coordinates are irrational. Buyer optimality, spending, seller optimality
and clearing have been checked, and the preceding argument excludes a
different rational equilibrium. Shared rational polyhedral constraints
therefore do not inherit the separable model's rational-output property.
The corresponding fixed-total case has the same result; nonpositive net
prices would again generate excessive demand.

Coupling alone is not sufficient for irrationality: with c=(1,1) and all
other shared-cap primitives fixed, p=(2,2), y=(1/2,1/2) is rational.
The example refutes neither the original separable-cost theorem nor a
claim that every coupled economy is irrational. An algebraic expression is
also an exact finite representation; only rational-coordinate output fails.

## B. Rational approximate equilibrium with an explicit certificate

For the shared-cap example, H is strictly decreasing,
H(1/2)=16/15>1 and H(1)=5/6<1. Bisection with rational arithmetic gives
an interval [l,u] containing lambda*, with l>=1/2 and width delta=u-l.
This is a paper construction; no bisection or solver was executed.

Choose prices p=(1+l,2+l), put H=H(l), and allocate

\[
x_{11}=\frac1{p_1H},\qquad x_{22}=\frac1{p_2H},\qquad
x_{12}=x_{21}=0.
\]

These quantities are rational and sum to one. Each buyer pays1/H<=1;
remaining money is retained. Both seller net prices equal l>0, so the
seller is exactly optimal and market clearing and the fixed-total repayment
constraint hold exactly. Only buyer optimality is approximate.

Each buyer's forgone utility, compared with her true demand at these same
prices, is

\[
R_i=\left(\frac{10}{p_i}-1\right)\left(1-\frac1H\right).
\]

On [1/2,1], |H'|<=4/9+4/25=136/225. Therefore
H(l)-1<=(136/225)delta and

\[
0\le R_i\le\frac{2312}{675}\,\delta<4\delta,
\qquad |p_i-p_i^*|\le\delta.
\]

After k rational bisection steps delta=2^(-k-1). Thus arbitrary additive
buyer-regret accuracy is obtained with O(log(1/epsilon)) steps for this
fixed fixture, with O(k)-bit intermediates. This is a direct approximation
certificate, not a complexity theorem for unrestricted Arctic auctions.
It prevents conflating irrational exact coordinates with intractability.

## Parent reduction and terminal decision

In the budget-binding regime of this fixture, its allocation is exactly
the unique optimizer of

\[
\max_{y_1,y_2>0,\ y_1+y_2\le1}
\log y_1+\log y_2-y_1-2y_2.
\]

Strict concavity and its KKT equations recover 1/y_j=c_j+lambda and the
same scalar root. This is weighted logarithmic resource allocation with
affine charges. The displayed program is an allocation potential, **not**
the original buyers' utility or a new social-welfare interpretation.

F2 therefore closes the proposed independent Paper G contribution. We
obtained a correct boundary example and a useful approximation certificate,
but no irreducible market-specific algorithm, lower bound or measurement
result. General nonseparable equilibrium irrationality, flexible seller
preferences and convex resource allocation are established parents. No
costly audit or scientific implementation is justified by this fixture.

Counts: **1 raw / 1 F1 / 1 F2 / 0 F3 / 0 cards**; six retained works and
two analytic diagnostics. No survivor, new forecast or re-entry trigger.
Retain the exact example and rational approximate-equilibrium certificate.
Re-entry requires a substantive result or qualified native control/contract
asset that removes the independent-contribution blocker; a new bond label,
cost vector or generic irrationality example is insufficient.

No outcomes, solver, scientific implementation, simulation, GPU work,
account connection, purchase, outreach, participants, EcoMD integration,
publication, commit or push. Metadata validation is separate from the
paper-only mathematical derivations.
