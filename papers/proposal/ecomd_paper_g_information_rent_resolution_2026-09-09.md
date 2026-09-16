# Paper G information-rent measurement — bounded analytic resolution

September 9, 2026. **Private/internal; exploratory F2 resolution of Cycle22.**
This consumes the one remaining paper-only follow-up recorded in the
[preceding audit](ecomd_paper_g_information_rent_equilibrium_audit_2026-09-09.md).

**Decision: close the current Paper G candidate at its bounded novelty gate.**
The uniform-value public-mark exclusion extends from b=0 to every feasible
b>=0 in the selected equilibrium characterization. Explicit positive- and
negative-b parameter points also retain the transaction-price upper bound.
What survives is an analytic baseline and conditional-expectation accounting;
no irreducible measurement contribution was qualified. This decision is not
a proof that every limit-order market obeys the bound. General negative-b
and arbitrary-distribution signs, and the general transaction-price sign,
remain unresolved.

## 1. Unchanged economic and observation contract

The parent is [Kaniel and Liu (2006)](https://doi.org/10.1086/503651),
Section II and its Appendix A characterization, read through the
[primary-paper reproduction](https://www.researchgate.net/publication/24103582_What_Orders_do_Informed_Traders_Use).
Its maintained continuous quote-updater and exogenous uninformed direction,
patience and arrivals are retained. We use its equilibrium equations and
participation condition, not an independent extensive-form off-path proof.

As in the preceding audit, prices/values are continuous and orders have unit
size. Initial endowments are removed from cash-plus-terminal-inventory profit;
short sales are permitted and fees/discounting are zero. Information survival
probability is p. Measurement ends at the first public revelation, pending
orders expire, and later known-value liquidity completion is excluded.
Arrivals and disclosure remain separate events. M is the public conditional
mean after the current event; T is last transaction carried through nontrades.
Neither M nor this partition is asserted to reproduce a field estimator.

[Kadan and Manela v2](https://arxiv.org/html/2605.11180v2), Sections 2 and
4.2.10, provide the existing covariation/profit relation and discrete
linear-impact upper-bound parent. Our account does not refute their theorem
or quantify any bias in their empirical estimates. The two existing papers
were revisited; no independent primary work or fresh confirmation data was
added.

## 2. General sign decomposition inside the selected model

Center the symmetric prior at zero, with density g supported on [-1,1]. Write
mu for the uninformed arrival probability, ell for its patient fraction,
a for the first ask, b for the resting limit-buy price, c for the informed
market/limit cutoff and r=max(0,b). The sell side reflects the buy side.
The equilibrium ordering is -a<b<a<c<1, with a>r, and

\[
q=\frac{\mu p}{2},\quad 0<q<\mu/2,\qquad
a=c-q(c-b).
\]

Informed buys are market orders for v>c, limit orders for r<v<c, and,
when b>0, there is a no-order region |v|<b. Retain that region in the
history distribution. Define

\[
D_1=2(1-\mu)\left[a\int_c^1g(v)dv
  -q\int_r^c(v-b)g(v)dv\right].
\]

This is the first-event public-mark covariation minus **all** first-arrival
informed profit, including later fills of its resting orders. It is not the
full-horizon gap.

For each first history h in {MB,MS,LB,LS,NO}, let w_h be its probability,
m_h its posterior mean, x_h/y_h its next competitive ask/bid, and
u_h=Pr(v>x_h|h), d_h=Pr(v<y_h|h). Let

\[
G_h=(1-\mu)\{(x_h-m_h)u_h+(m_h-y_h)d_h\}\geq0.
\]

The inequality follows from x_h>=m_h>=y_h. Expected uninformed direction is
zero conditional on history, and the price at an execution is its public
conditional expected value. Applying conditional expectation, including
no-order histories and both informed arrival cohorts, gives

\[
\boxed{C_M-\Omega=D_1+p\sum_h w_hG_h.}
\]

For T, first market and no-order histories have the same initial mark as M;
after a limit order the carried transaction remains zero. With
G_h^T=(1-mu){(x_h-t_h)u_h+(t_h-y_h)d_h}, where t_h is that carried price,

\[
C_T-\Omega=D_1+p\sum_h w_hG_h^T,
\]
\[
\boxed{C_T-C_M=2pw_{LB}m_{LB}(1-\mu)(u_{LB}-d_{LB}).}
\]

The last identity has no automatic sign. A positive posterior mean alone
does not sign net subsequent aggressive trading. At a limit-buy history,
y_LB=b and G_LB^T=(1-mu)(x_LB u_LB-b d_LB). Thus:

- For b<=0, G_LB^T>=0, because x_LB>=m_LB>0. All other reflected or
  no-order continuation gaps are also nonnegative. Therefore C_T-Omega>=D_1.
- For b>0, discarding the nonnegative ask contribution gives a useful lower
  bound. Only an initial uninformed limit buyer can coexist with v<b, so
  w_LB d_LB=(mu ell/2)F(b), with F the prior CDF. Consequently

\[
\boxed{C_T-\Omega\geq D_1-p\mu\ell(1-\mu)bF(b),\qquad b>0.}
\]

These are direct accounting and conditioning consequences. They are not
unconditional assertions that every residual is positive, nor a new
observable estimator of latent cohort profits.

## 3. Uniform prior: the public-mark bound holds for all feasible b>=0

Take g=1/2 on [-1,1], b>=0. Put e=1-c, d=c-b. The initial Bayes and
limit-price equations imply

\[
2\mu(1-\ell)a=(1-\mu)e(e+2qd),\qquad
\ell=\frac{d^2}{(1+b)^2+2\mu b/(1-\mu)}.
\]

The first gap is

\[
D_1=(1-\mu)\{ae-qd^2/2\}.
\]

Here is an elementary sign proof that uses those equilibrium constraints.
It does not choose a limit price independently of a feasible equilibrium.

If c<=1/2, then a>c/2, d<=c and q<1/2. Hence

\[
\frac{D_1}{1-\mu}
>\frac c2(1-c)-\frac{c^2}{4}
=\frac{c(2-3c)}4>0.
\]

For c>=1/2, the expression for ell gives

\[
1-\ell\geq\frac{e(1+c)}{(1+b)^2}.
\]

Substitution into the initial pricing equation, followed by 2q<mu, yields

\[
\mu K<e,\qquad K=\frac{2a(1+c)}{(1+b)^2}-d.
\]

To bound K, set a_0=(c+b)/2<a. At a=a_0,

\[
4a_0K_0-d^2
=\frac{2(c+b)^2(1+c)}{(1+b)^2}-3c^2+2bc+b^2.
\]

At b=0 this is c^2(2c-1)>=0. Its derivative with respect to b is

\[
\frac{4(c+b)(1+c)(1-c)}{(1+b)^3}+2(c+b)>0.
\]

Therefore K_0>0 and 4a_0K_0>=d^2. Increasing a increases K and 4aK,
so K>0 and 4aK>=d^2. Finally,

\[
\frac{qd^2}{2}<\frac{ed^2}{4K}\leq ea.
\]

Thus D_1>0 in both cases and the nonnegative continuation terms imply
**C_M>Omega for every feasible nonnegative b in this uniform-prior class.**
This extends the earlier b=0 exclusion. It does not sign the general
transaction-price correction and does not cover all negative b or other g.

## 4. Explicit noncentered checks without a parameter search

Fix mu=1/3 and c=1/2. For a prescribed b, define

\[
Q=1+3b+b^2,\quad
H=\begin{cases}(c-b)^2,&b\geq0,\\c^2-2bc,&b<0,\end{cases}
\]
\[
\ell=H/Q,\qquad a=\frac3{4(2-\ell)},\qquad
q=\frac{c-a}{c-b},\qquad p=6q.
\]

These are algebraic substitutions into the equilibrium equations, not a
numerical equilibrium sweep. Two admissible points are:

| b | ell | a | p |
|---|---|---|---|
| 1/50 | 576/2651 | 7953/18904 | 37475/37808 |
| -1/10 | 35/71 | 213/428 | 5/214 |

Both have mu,ell,p in (0,1), -a<b<a<c and the required cutoff relation.
Their first pricing and limit-price equations hold exactly. The patient
buyer's expected completion cost is qQ, respectively about 0.17518 and
0.002765, below the corresponding asks 0.42070 and 0.49766. The first
informed market/limit/no-order choices maximize the stated payoffs. The
published continuous quote-updater characterization supplies the maintained
off-path basis; no new extensive-form certificate is asserted.

For the uniform prior, F(b)=(1+b)/2. Substitution into the bounds above gives:

| b | D_1, also a lower bound for C_M-Omega | Certified lower bound for C_T-Omega |
|---|---:|---:|
| 1/50 | 0.1275476090 | 0.1270594533 |
| -1/10 | 0.1654335410 | 0.1654335410 |

These are positive lower bounds, **not the full gaps or empirical estimates**.
No continuation root, random draw, solver or outcome dataset is needed for
these exclusions. The rational specifications and displayed inequalities,
rather than rounded decimals, support the conclusion.

## 5. Terminal decision and preserved uncertainty

The current candidate `paper_g_information_rent_execution_measurement` is
**failed_closed at the predeclared bounded F2 qualification stop**. The
analytic work removed an accessible counterexample family and produced
reusable accounting checks. It did not qualify a new measurement method,
an independently novel failure boundary, or an observation bridge. The
remaining identities depend on the maintained economic model and latent
cohort definitions; renaming these corrections is not enough to advance.

This closure does not assert that the full Kaniel–Liu class, all negative
limit prices, arbitrary priors, quoted midpoints, calendar partitions or all
finite markets have been settled. Those universal sign questions remain
unproved here. There is no fee-puzzle resolution, empirical bias finding or
counterexample to the published Kadan–Manela theorem. The earlier abstract
weighting/timing examples remain non-equilibrium diagnostics.

Do not spend another same-formulation follow-up changing parameter values,
clocks or labels. Reconsider only after a substantive new result removes the
recorded blocker—for example a complete equilibrium violation with a
market-specific, irreducible measurement consequence, or a new theorem that
does more than the retained accounting decomposition. Such a trigger must
be recorded and validated under the discovery protocol before harvesting.

Cycle22 retains its original six questions and initial dispositions as
history, with this later resolution linked. No new cycle, primary work,
killer-test count, F3 audit, probability forecast, trigger, card or experiment
is added. No outcome access, implementation, simulation, GPU, purchase,
outreach, participant work or EcoMD integration is authorized.
