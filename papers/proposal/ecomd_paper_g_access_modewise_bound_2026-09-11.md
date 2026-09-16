# Paper G: a restoration-uniform square-root learning upper bound

PRIVATE / INTERNAL. `public_evidence_eligible: false`.

**Result:** the existing one-way exogenous-access model admits an actual-feedback
learner with expected finite-horizon regret

\[
\widetilde O\!\left(Q\sqrt{(Q+1)T}\right)+4Q,
\]

uniformly in the restoration probability \(\lambda\in[0,1]\). For fixed inventory
capacity this improves the previous \(T^{2/3}\) upper bound to square-root order,
up to logarithms. It is a corollary of the repository's imitation certificate,
Bellman telescoping and published SCAL theory, **not an independent new RL
algorithm or a matching minimax theorem**. Decision: `not_trigger` for independent
Paper G novelty. No algorithm was implemented or run in this audit.

## 1. Exact contract and comparator

Retain the [September 8 access model](ecomd_paper_g_reentry_theory_result_2026-09-08.md)
and its fixed-mark, funded inventory and actual-feedback grammar. Capacity
\(Q\ge2\) is finite, \(q_1=1\), and cash remains nonbinding over the declared
horizon by the existing prefunding contract. Customers are iid; their unknown
law has buy probability \(0<\nu<1\) and arbitrary binary willingness
probabilities in \([0,1]\). Thus the earlier compact two-sided class is included.

At the start of a round, mode \(m_t\) is observed. In suspended mode S, hedging
is unavailable but legal customer quotes remain available. At the end of each
suspended round, access is restored with probability \(\lambda\), independently
of actions and customer innovations. Eligible mode E is absorbing, with both
unit hedge sides full at every subsequent round start. Restoration itself does
not reset inventory or change that round's reward. At most one S-to-E switch
occurs. Marked-wealth reward is in \([-1,2]\); the terminal excess reward is zero.

The comparator \(V_T^*(q_1,S;\mu,\lambda)\) is the original known-law,
finite-horizon optimal dynamic controller. It obeys the same timing, legal
actions and feedback and is not given future customer draws. Expected regret is
\(V_T^*-\mathbb E\sum_{t=1}^T r_t\). We do not replace this comparator by a
fixed quote, a fixed inventory target or an average-gain comparator.

## 2. Two auxiliary stationary MDPs

For analysis and algorithm selection, freeze the access mode at S forever or E
forever. Each resulting MDP has state \(q\in\{0,\ldots,Q\}\), at most
\(A=27\) legal actions per state, and at most \(\Gamma=3\) possible successor
inventories for a fixed action: the deterministic hedge is followed by a
customer increment in \(\{-1,0,1\}\). In S there are fewer actions. These
auxiliary MDPs are not extra physical runs or resets.

Both are communicating. A dealer can post only bid 99 until a seller moves
inventory up, or only ask 101 until a buyer moves it down. These trades always
execute on the appropriate side, irrespective of willingness, and their waits
have finite means because \(0<\nu<1\). Repeating moves connects every pair of
inventories; no external hedge is needed for this argument.

For either frozen mode, the existing clipped-imitation argument gives
\(|V_h(q)-V_h(q')|\le2|q-q'|\). It also holds for discounted values: after
coupling customer innovations, an omitted virtual hedge costs the virtual
account one tick, while an omitted customer execution has spread at most two
and reduces inventory distance. The pathwise reward deficit is bounded by
twice the decrease in that distance. Discounted telescoping preserves the
bound. This is the earlier certificate restricted to either frozen mode;
known-law conditional sampling supplies the admissibility argument when virtual
customer outcomes are hidden. It gives no private outcomes to the learner.

In a finite communicating MDP, take a vanishing-discount subsequence of the
normalized optimal values. Their bounded span supplies a limit satisfying the
average-reward optimality equation. Consequently each mode has a constant
optimal gain \(g_m\) and an optimal bias \(h_m\), which can be normalized so that

\[
0\le h_m(q)\le c:=2Q,\qquad
g_m+h_m(q)=\max_{a\in A_m(q)}
 \{r_m(q,a)+P_mh_m(q,a)\}.                 \tag{1}
\]

The large bias difference between access modes is never assumed bounded.
Only the two separately normalized inventory biases enter (1).

## 3. Connecting to the full dynamic oracle

Let \(N_S+N_E=T\) be the actual numbers of suspended and eligible rounds and
define \(G=g_SN_S+g_EN_E\). The distribution of these counts is independent of
the dealer's policy, so the oracle and learner have the same expected G.

Condition on the exogenous restoration time. It fixes at most two contiguous
mode segments without changing the iid customer law. Even if an analysis oracle
is told this restoration time in advance, every nonanticipating customer-policy
action satisfies the Bellman inequality from (1). On a segment of length n,
conditional telescoping gives

\[
\mathbb E\sum_{t\text{ in segment}}r_t
 \le ng_m+\mathbb E[h_m(q_{\rm start})-h_m(q_{\rm end})]
 \le ng_m+c.                             \tag{2}
\]

The random inventory at the segment boundary causes no problem because (1)
holds at every inventory and the same bound c applies. Summing the two segments
and averaging over restoration gives

\[
V_T^*\le\mathbb E G+2c=\mathbb E G+4Q.    \tag{3}
\]

Empty segments contribute nothing. This also covers no restoration, restoration
at the final round, and restoration after the first round. Revealing restoration
time was an upper-bound device only; neither the learner nor the original oracle
receives future customer innovations or a physical reset.

## 4. An admissible learner and the random segment lengths

Run one fresh SCAL instance on q while suspended. If access becomes eligible,
start a second fresh SCAL instance from the **current physical inventory** and
continue there. Restarting learner statistics changes neither inventory nor
cash. The learner may discard the suspended observations; sharing the customer
law across modes is not required for this upper bound. Both instances use only
chosen actions, realized rewards and next inventories, all contained in F_actual.
They use the legal action sets and the known bound c. They do not require hidden
willingness, unchosen-action rewards, a simulator or external recovery probes.

Apply SCAL to the shifted reward \(r+1\in[0,3]\). This adds n to both the
segment return and its gain baseline, leaving regret and bias span unchanged.
[Fruit et al., ICML 2018](https://proceedings.mlr.press/v80/fruit18a/fruit18a.pdf),
Theorem 12, supplies an anytime bound for weakly communicating finite MDPs with
known optimal-bias-span bound:

\[
B(n,\zeta)=C\max\{3,c\}
 \sqrt{\Gamma SA\,n\log(n/\zeta)},\qquad n\ge1, \tag{4}
\]

with probability at least \(1-\zeta\), for all n; C denotes the universal
constant in the published order bound. Use \(B(0,\zeta)=0\) and
\(S=Q+1\). Source reading verified Section 2, Figure 1, Section 6 and the
anytime quantifier in Theorem 12, visually on PDF page 7. Its supplementary
proof was not independently re-proved in this audit.

The suspended trajectory is a prefix of the S-MDP learner. Conditional on the
exogenous restoration time its law is unchanged. After restoration, conditional
on the whole preceding history, the E learner starts at some legal q and receives
fresh iid customer innovations. SCAL's guarantee applies from every such q;
fresh learner randomization can be independent. Giving each instance failure
probability \(\zeta=\eta/2\) and taking a union bound therefore gives

\[
G-\sum_{t=1}^T r_t
 \le B(N_S,\eta/2)+B(N_E,\eta/2)
 \le C\max\{3,2Q\}\sqrt{2\Gamma SA\,T\log(2T/\eta)}             \tag{5}
\]

with probability at least \(1-\eta\). The last step uses
\(\sqrt{N_S}+\sqrt{N_E}\le\sqrt{2T}\). No independence between reward and
next inventory within a customer execution is needed. The relevant independence
is that of the external switch and future customer innovations.

## 5. Expected finite-horizon result

On the failure event, \(G-\sum r_t\le3T\), since both gains and rewards lie
in \([-1,2]\). Combining (3) and (5), with
\(\eta=(T+1)^{-2}\), proves

\[
\boxed{\quad
R_T\le4Q+C\max\{3,2Q\}
 \sqrt{2\Gamma(Q+1)A\,T\log\!\big(2T(T+1)^2\big)}
 +\frac{3T}{(T+1)^2},\quad A\le27,\ \Gamma\le3.
\quad}                                                       \tag{6}
\]

This is an expected-regret theorem for the original dynamic comparator; (5)
alone is a high-probability statement about a random gain baseline and should
not be relabelled as a high-probability theorem for the original comparator.
For fixed Q, (6) is uniform square-root order up to logarithms in T. No optimal
dependence on Q or matching lower rate is established. The trivial \(R_T\le3T\)
may be taken when (6) is looser.

The learner never uses lambda, so the same guarantee also permits an unknown
but exogenous restoration probability under the same independent one-way
clock. It applies even to \(\lambda=c_0/T\) families. This does not contradict
the reduced unknown-channel lower bound: there the dealer's choice changes
restoration and the count baseline is no longer policy independent.

## 6. Hostile scope checks and scientific disposition

| Check | Resolution |
|---|---|
| Compare with the full finite-horizon oracle | Equation (3) bounds every legal dynamic policy; no restricted-comparator substitution |
| Random, unannounced restoration | Exogenous conditioning and the anytime guarantee cover both segment lengths |
| No restoration or a switch after the last action | One active segment suffices; the bound remains valid |
| Inventory at a boundary | Legal-action SCAL and the bias bound hold for every q; no inventory reset |
| Hidden willingness | Realized reward and next q suffice for the imported algorithm |
| Slow customer recovery | It affects diameter; the proved bias bound and imported rate do not require an inverse arrival probability |
| Action-dependent or inventory-triggered restoration | Outside proof: segment law and/or policy-independent gain baseline need not survive |
| Repeated suspensions, joint cash scarcity, price risk | Outside the stated one-switch, nonbinding-cash, fixed-mark contract |

This resolves the previously open existence of a restoration-uniform
square-root upper bound in the exogenous one-switch model. The earlier
explore-then-plan bound stays correct; it is no longer the strongest retained
upper bound. The large access continuation-value gap stays correct too.

Scientific novelty remains unqualified: bounded-bias learning plus one external
switch is a standard parent construction. Do not sell the corollary as a new
SCAL algorithm, a sharp minimax law or a field finding. Stop generic exogenous
waiting-time learning-penalty pitches. A future contribution needs an exact
residual beyond this reduction, such as a lawful action-coupled mechanism with
the same comparator and feedback and a nonstandard matching learning boundary.
No such mechanism is established or authorized for execution here.
