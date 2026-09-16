# Paper G: square-root lower bound with legal inventory and actual feedback

PRIVATE / INTERNAL. `public_evidence_eligible: false`.

**Result.** In the existing access model with Q=2 and lambda=0, every admissible
learner has, on one of two customer laws,

\[
\max\{R_T^-,R_T^+\}\ \ge\ \frac{\sqrt T}{288}-1.                 \tag{1}
\]

Regret is against the same known-law finite-horizon optimal dynamic controller.
All customer recovery trades remain legal. Together with the preceding
[modewise upper bound](ecomd_paper_g_access_modewise_bound_2026-09-11.md), this
matches the horizon exponent, up to logarithms, for the Q=2 suspended subclass
and for the worst case over external restoration rates at Q=2. It does not give
an exact minimax value, optimal logarithms, a capacity law or a lower bound at
every positive restoration rate. The construction uses standard two-point
information theory; independent Paper G novelty remains unqualified.

## 1. Two admissible worlds

Use the [existing market grammar](ecomd_paper_g_experiment_plan_2026-09-08.md)
with funded inventory q in {0,1,2}, initial q=1, fixed mark100 and nonbinding
prefunded cash. Access starts suspended and lambda=0, so hedging is unavailable
throughout. Customer side is iid with buy probability nu=1/2. Set both unknown
willingness probabilities to the same p. A wide bid98 or ask102 earns two ticks
when accepted, with probability p conditional on the corresponding request side.
A narrow bid99 or ask101 always executes on that side and earns one tick.
Quotes may be off, but buying at q=2 and selling at q=0 remain illegal.

The learner sees request side after quoting, fills/nonfills, its reward and
inventory. It does not see private willingness independently of the receipt.
For horizon T>=1 set

\[
\epsilon=\frac1{40\sqrt T},\qquad p_-=\frac25-\epsilon,
\qquad p_+=\frac25+\epsilon.                                   \tag{2}
\]

The learner may know the symmetric model, nu, lambda and the two candidate
values, but not which world holds. Thus the argument also applies to learners
with less prior information. The alternatives depend on T, as usual for a
minimax lower bound over a fixed parameter class; this is not a statement about
the asymptotic regret of one fixed separated customer law.

## 2. Exact Bellman certificates

Set h(0)=h(2)=0 and h(1)=x. Conditional on either request side at q=1, the
expected reward plus bias increment from narrow, wide or off quoting is,
respectively,

\[
1-x,\qquad p(2-x),\qquad0.                                    \tag{3}
\]

At a boundary, only one request side can trade; the corresponding unconditional
quantities are (1+x)/2, p(2+x)/2 and0. These expressions account for inventory
changes and for the side arriving with probability1/2. Mixed bid/ask choices at
q=1 average their two conditional expressions.

The following gains and biases satisfy the average-reward optimality equation
at all three states and all legal actions:

| World | g | x | Maximizing quotes |
|---|---|---|---|
| p_- | 2/3 | 1/3 | Narrow on every feasible side |
| p_+ | 3p_+/(1+2p_+) | (4p_+-1)/(1+2p_+) | Wide on both sides at q=1; narrow on the feasible side at either boundary |

For p_-, narrow dominates wide at q=1 because p_-<=2/5, and at a boundary
because 7p_-/6<=2/3. For p_+ in[2/5,17/40], wide exceeds narrow at q=1 by

\[
d_+=\frac{5p_+-2}{1+2p_+}
    =\frac{5\epsilon}{1+2p_+}.                               \tag{4}
\]

At a boundary, narrow exceeds wide by

\[
\frac{p_+(5/2-4p_+)}{1+2p_+}
 \ge\frac{32}{185}>\frac16;                                 \tag{5}
\]

off quoting is worse as well. Both biases have 0<=h<=x<1.

For either world define the nonnegative Bellman gap
Delta_p(q,a)=g_p+h_p(q)-E_p[r_t+h_p(q_{t+1})|q,a].
Telescoping for an arbitrary adaptive randomized learner yields

\[
\mathbb E_p\sum_{t=1}^T r_t
 =Tg_p+x_p-\mathbb E_p h_p(q_{T+1})
   -\mathbb E_p\sum_{t=1}^T\Delta_p(q_t,a_t).                 \tag{6}
\]

Following a maximizing stationary rule has zero gaps and earns at least Tg_p
from q=1, since h_p(q_{T+1})<=x_p. The finite-horizon dynamic optimum is at
least as good. Therefore its regret, without changing comparator, satisfies

\[
R_T^p\ge\mathbb E_p\sum_t\Delta_p(q_t,a_t)-1.                 \tag{7}
\]

## 3. Information exposure and boundary avoidance

Let Z_t be half the number of legal wide quotes posted at time t: Z_t is
0,1/2 or1. It is the conditional probability that this round's request meets a
wide quote. Define N=sum_t Z_t, so 0<=N<=T.

In the minus world every wide quote at the center loses 5epsilon/3 per
corresponding request opportunity. The boundary wide-quote loss per opportunity
is 4/3-7p_-/3, which is larger. Off quotes cannot reduce the gap. Consequently

\[
R_T^-\ge\frac{5\epsilon}{3}\mathbb E_-N-1.                  \tag{8}
\]

For the plus world let C=sum_t 1{q_t=1}. Let B count boundary rounds on which
the feasible-side quote is wide or off, rather than narrow. Boundary-narrow
rounds number T-C-B, and each moves to q=1 with probability1/2. Hence

\[
\frac12\mathbb E_+(T-C-B)
 \le\mathbb E_+\sum_t1\{q_{t+1}=1\}
 \le\mathbb E_+C+1,
\quad
\mathbb E_+C\ge\frac{T-\mathbb E_+B-2}{3}.                  \tag{9}
\]

This deliberately loose endpoint allowance suffices. It prevents a learner
from avoiding the center at no cost. Center non-wide opportunities cost at
least d_+ each, while each boundary bad round costs at least1/6 by (5).
Writing N_C=sum_t 1{q_t=1}Z_t<=N, the cumulative gaps obey

\[
\begin{aligned}
\mathbb E_+\sum_t\Delta_+(q_t,a_t)
&\ge d_+\mathbb E_+(C-N_C)+\tfrac16\mathbb E_+B\\
&\ge d_+\big(T/3-\mathbb E_+N-2/3\big)
    +(\tfrac16-d_+/3)\mathbb E_+B\\
&\ge d_+\big(T/3-\mathbb E_+N-2/3\big).                     \tag{10}
\end{aligned}
\]

The final coefficient is nonnegative: epsilon<=1/40 makes d_+<=5/72.
This accounts for every legal off, narrow, wide or asymmetric quote policy;
it does not assume a learner follows either stationary rule in the table.

## 4. Adaptive change of measure

Let P_- and P_+ be the laws of the full actual-feedback transcript, including
actions. Given a common history and chosen legal action, the request-side law
is identical. Narrow and off receipts are p-independent. If the request meets
a wide quote, its fill/nonfill is Bernoulli(p). Reward, cash and next inventory
are known functions of that receipt and carry no additional independent signal.
The policy kernels cancel in the likelihood ratio, including for randomized
adaptive policies. The chain rule therefore gives

\[
\operatorname{KL}(P_-\Vert P_+)
 =\mathbb E_-N\;\operatorname{kl}(p_-,p_+).                  \tag{11}
\]

This uses the standard divergence-decomposition argument, applied to the
specified state-dependent legal receipts rather than asserting that inventory
states are iid bandit arms. See Lattimore and Szepesvari,
[Bandit Algorithms](https://tor-lattimore.com/downloads/book/book.pdf),
Lemma15.1 and its proof. Equation14.12 supplies Pinsker's inequality.

Using log u<=u-1 for Bernoulli probabilities gives
kl(p,q)<=(p-q)^2/[q(1-q)]. Since p_+ in[2/5,17/40], its denominator is at
least6/25. Thus

\[
\operatorname{KL}(P_-\Vert P_+)
 \le\frac{50}{3}\epsilon^2T=\frac1{96},
\qquad
\operatorname{TV}(P_-,P_+)\le\sqrt{1/192}<1/12.              \tag{12}
\]

For the same transcript statistic N in[0,T], integration of its tail
probabilities yields

\[
|\mathbb E_+N-\mathbb E_-N|\le T\operatorname{TV}(P_-,P_+)<T/12. \tag{13}
\]

## 5. Lower bound and its exact quantifiers

If E_-N>=T/12, (8) immediately gives R_T^->=sqrt(T)/288-1.
Otherwise (13) gives E_+N<T/6. Equations(7) and(10), for T>=8, imply

\[
R_T^+\ge d_+(T/6-2/3)-1
 \ge\frac{100\epsilon}{37}\frac{T}{12}-1
 =\frac5{888}\sqrt T-1
 \ge\frac{\sqrt T}{288}-1.                                  \tag{14}
\]

For T<8 the claimed right side is negative and nonnegative expected regret
suffices. This proves (1) for all adaptive randomized feasible learners.

The lower bound holds within Q=2, lambda=0, nu=1/2. For a fixed compact
two-sided customer-law class containing nu=1/2, the worst-case expected regret
at Q=2 therefore lies between Omega(sqrt T) and O(sqrt(T log T)) using the
preceding SCAL corollary. The same horizon bracket holds for the worst case
over lambda in[0,1], because its upper bound is uniform and this subclass is
included. This is matching polynomial order, **not an exact logarithmic or
constant-order minimax solution**. No lower bound for each fixed lambda>0,
Q>2, or a fixed separated p is supplied.

The lower bound is already present with no restoration. It cannot establish
an extra learning penalty caused by a slow restoration clock. Full-reveal
feedback is a different problem and is not covered by (11). Realized recovery
trades, private randomization and the lawful customer probe have not been
removed; they are included in the all-policy argument.

## 6. Disposition

The repository now has an explicit legal-market lower witness and an upper
bound matching its horizon exponent. This is a reusable benchmark boundary,
but the proof is a classical Bellman-gap and two-point information argument.
The cited book does not print this inventory construction; its method supplies
the generic parent. No independent algorithm or theorem novelty, empirical
result, new experiment, qualified candidate or publication readiness is claimed.

Record `not_trigger`; preserve M0's existing closure. Do not continue generic
exogenous-clock learning-penalty pitches or merely enlarge the same benchmark.
A future contribution must specify a lawful coupling and a response or learning
boundary surviving the known control and information-theory reductions.
