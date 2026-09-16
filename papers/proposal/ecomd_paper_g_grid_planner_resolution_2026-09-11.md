# Paper G: polynomial approximate planning and closure of this proposal

PRIVATE / INTERNAL. `public_evidence_eligible: false`. Paper-only derivation.
Decision:`not_trigger`. Retain a reusable theoretical asset; stop this
access-learning refinement as an independent Paper G proposal.

## 1. Result and scope

Under the unchanged model and actual feedback of the
[capacity-additive bound](ecomd_paper_g_capacity_additive_bound_2026-09-11.md),
the exact optimistic planning oracle can be replaced by a finite grid of
ordinary discounted-MDP linear programs. No model simulation or scientific
implementation is used to establish this statement.

Let T>=1,Q>=2, eta=(T+1)^(-2),
L_star=ceil(log2(6T(T+1)^2)), K_T=5+3 floor(log2 T), and let M>=1 be an integer.
The learner defined below has expected regret against the original known-law
finite-horizon optimal dynamic controller bounded by

\[
R_T\le\min\{3T,\;4Q+2QK_T+(24+16\sqrt2)\sqrt{L_\star T}
              +13T\eta+30T/M\}.                         \tag{1}
\]

It solves at most (M+1)K_T discounted linear programs, each with Q+1 value
variables and at most27(Q+1) Bellman inequalities. With M=ceil(sqrt T), this
retains O(sqrt(T log T)+Q log T), using O(sqrt T log T) LP solves. All LP
coefficients are rational with bit length O(log(M(Q+1))). Thus computation is
polynomial in explicit inventory-state count Q, interaction length T and input
bit size. This does not mean polynomial in log T or log Q alone, strongly
polynomial complexity, constant work per interaction, or practical speed.

Equation(1) uses L_star rather than the predecessor's natural logarithm.
It preserves the order, not that record's exact constants. Taking M=100T
instead makes the additional discretization/discount term at most0.3, at the
cost of O(T log T) LP solves.

## 2. Willingness monotonicity and side-mixture sensitivity

For any frozen mode and candidate customer law, retain the certified scalar
average gain g and bias h with |h(q+1)-h(q)|<=2. Given a fixed legal hedge,
let qbar be post-hedge inventory. The contribution of a wide quote is

\[
p_b[2+h(qbar-1)-h(qbar)]\quad\hbox{or}\quad
p_s[2+h(qbar+1)-h(qbar)].
\]

Each bracket lies in[0,4]. Increasing p_b or p_s while fixing nu therefore
weakly increases r+Ph for every action when tested against the old model's h.
In particular the old Bellman-maximizing stationary policy satisfies
r_new+P_new h-h>=g_old. Summing and dividing by time, its new average return
is at least g_old. Consequently the optimal scalar gain is coordinatewise
nondecreasing in p_b,p_s. This argument also covers candidate nu endpoints.

The prior local-prediction inequality likewise gives, with p_b,p_s fixed,

\[
|g(\nu,p_b,p_s)-g(\nu',p_b,p_s)|\le6|\nu-\nu'|.       \tag{2}
\]

For completeness, test the second model's Bellman operator on the first
model's bias: its residual lies between g-6|nu-nu'| and g+6|nu-nu'| at every
state. A maximizing stationary policy proves the lower gain bound; the
Bellman upper inequality proves the upper bound for every policy by telescoping.
This does not assume that the same policy remains optimal across laws.

Thus an average-gain maximizer over a rectangular confidence set can take
p_b,p_s at their respective upper endpoints. Only nu requires a grid search.
We do not assert that g is monotone in nu or that its maximum is at a nu endpoint.

## 3. Rational confidence sets and discounted LPs

Use the same three actual streams and count-doubling/mode-change epochs as
before. For a stream with n>=1 observations, form its clipped interval of
radius sqrt(L_star/(2n)) around the empirical mean. For n=0 use[0,1]. Since
L_star>=ln(6T/eta), all intervals cover simultaneously with probability>=1-eta.

At an epoch start, round the lower endpoint down and the upper endpoint up
to multiples of1/M, retaining clipping to[0,1]. The resulting width is at
most the original width plus2/M. This rounding preserves coverage. It is
computable with rational/integer comparisons because L_star, counts and M
are integers; comparisons against the square-root radius can be squared after
checking signs. The integer L_star itself is obtained from binary integer
length/comparison, avoiding an exact transcendental endpoint oracle.

For each grid point nu_i in the rounded nu interval, take
theta_i=(nu_i,upper_p_b,upper_p_s). There are at most M+1 candidates. Set

\[
\kappa=\frac{1}{M(Q+1)},\qquad\gamma=1-\kappa.
\]

For each candidate, solve the ordinary discounted Bellman LP

\[
\min_v\sum_{q=0}^Qv(q),\qquad
v(q)\ge r_i(q,a)+\gamma\sum_{q'}P_i(q'\mid q,a)v(q')
\quad\forall q,a\in A_m(q).                         \tag{3}
\]

Its unique optimum is V_gamma: Bellman supersolutions dominate the fixed
point by monotonicity and contraction, while V_gamma itself is feasible.
The objective has positive weight on every state, giving uniqueness.
Recover a greedy action in each state from its Bellman equality. Negative
raw rewards cause no difficulty in this LP.

Define c_i=V_gamma,i(0), h_i=V_gamma,i-c_i and g_gamma,i=kappa c_i. Select a
candidate maximizing g_gamma,i and use its discounted-greedy stationary policy
until the ordinary epoch ending. Keep the actual inventory and all observation
counts. The original objective and comparator are not changed to discounted
reward; discounting is only a planning approximation.

The rational LP formulation and general bit-size polynomial solution methods
are classical; see Section1–2 of [Ye's author manuscript](https://stanford.edu/~yyye/SimplexMDP3.pdf),
revised November30 2010, especially PDF pages3 and6. Only these formulation/
complexity portions were inspected. Its fixed-discount strongly polynomial
theorem is not invoked: our gamma depends on Q,M. No particular floating-point
solver's accuracy, speed or policy tie-breaking has been validated.

## 4. Approximation accounting

The existing discounted imitation certificate gives |h_i(q+1)-h_i(q)|<=2,
h_i(0)=0, and |h_i(q)|<=2Q. The discounted Bellman identity is

\[
g_{\gamma,i}+h_i(q)=\max_a\{r_i(q,a)+\gamma P_i h_i(q,a)\}.
\]

For the selected greedy action, replacing gamma P_i h_i by P_i h_i has
absolute error at most

\[
\epsilon_b=2Q\kappa\le2/M.
\]

Bellman upper bounds for every policy and lower bounds for the discounted
greedy policy show |g_i-g_gamma,i|<=epsilon_b. This uses bounded-bias
telescoping, not a communicating-time or side-frequency lower bound.

On the confidence event, willingness monotonicity and the nu grid give
g_true<=max_grid g_i+6/M. Maximizing g_gamma,i then gives

\[
g_{true}-g_{\gamma,selected}\le6/M+\epsilon_b.
\]

The selected action's additional discounted Bellman residual contributes at
most another epsilon_b. The rounded confidence widths add at most
(6+4nu+4(1-nu))2/M=20/M to the one-round model-error bound. The total extra
one-round term is therefore at most

\[
6/M+2\epsilon_b+20/M\le30/M.                       \tag{4}
\]

On confidence failure, true gain and g_gamma lie in[-1,2], and the local model
error is at most10. Thus the previous13-per-round failure accounting still
applies, with the nonnegative approximation term retained. The selected h_i
is predictable within each epoch, so unconditional martingale expectations
remain zero. Its telescoping contribution is at most2Q per epoch. The same
observed-stream width sum applies with L_star and the original count bound K_T.

Adding30T/M to that accounting and the unchanged finite-dynamic-oracle
bridge4Q proves(1). No willingness observations, physical resets, lower bound
on nu or knowledge of external restoration probability were introduced.

## 5. Scientific allocation

This resolves the specific polynomial-computability question left by the
[parent collision audit](ecomd_paper_g_structured_parent_collision_2026-09-11.md).
The construction is a finite parameter grid, a standard discounted LP and
the already retained imitation certificate. It supplies a concrete constructive
corollary, but does not establish an independently novel general RL mechanism.

Stop spending topic-discovery effort on this fixed exogenous access-learning
refinement as an independent Paper G proposal. Retain the upper/lower witnesses,
exact Exo-MDP mapping, monotonicity and constructive bound for later reuse.
This allocation judgment is not a theorem that every refinement is unpublishable,
nor a claim that a complete literature search found an identical theorem.

Reopen only for a qualified same-contract primary disagreement, a new truth/
control asset, or a nonstandard result removing the recorded contribution
blocker. Better grid constants, an alternative LP solver or another access
variant do not themselves qualify. The broad ICML/NMI/NCS objective remains
unmet, and no implementation, outcome access or GPU work is authorized.
