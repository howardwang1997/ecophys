# Paper G: unknown recovery channels, exact-check contract

This contract freezes the v4 checks before implementation or numerical outcome
access. The analytic candidate formula and primary-parent collision were derived
before this freeze; this is not a prospective novelty forecast, untouched
confirmation, qualified re-entry trigger, or new harvesting cycle. The PI-directed
decision authorizes only a small reusable exact-theory benchmark.

## Model and comparator

Initially the observed access state is suspended. Each suspended round permits
exactly one of two channels, A or B. In unknown world theta=A/B, the named channel
restores access with probability p+=lambda*(1+alpha), the other with p-=lambda*(1-alpha).
Lambda and alpha are known, 0<=alpha<1, lambda>=0, p+<1. The state change occurs at
the end of the round; all draws are conditionally independent. Restoration is
absorbing. Suspended rounds earn zero incremental reward; each subsequent eligible
round earns known Delta>=0. There are no switching costs, resets, parallel attempts,
counterfactual channel outcomes or informative external signals. The comparator
knows theta but has exactly the same initial state, actions and transition timing.

This is a reduced restoration-search model. It is not the previous inventory
simulator, a calibrated venue protocol, or a theorem about an inventory-dependent
credit constraint. A separate customer process may be appended only when both its
feasible optimum and its observations are independent of the channel/world and it
shares no constrained resource; it then adds no mechanism and cancels from regret.

## Candidate exact theorem

Set u=1-p+ and v=1-p-. Under the equal prior, a failure-only prefix with counts a,b
has survival probability (u^a*v^b+v^a*u^b)/2. Among prefixes of length n, balancing
the counts minimizes this expression. Alternation realizes every minimum at once:

- S(2m)=(u*v)^m;
- S(2m+1)=(u+v)*(u*v)^m/2.

The predicted exact minimax regret at horizon T is

`Delta * sum_{n=0}^{T-1} (S(n)-u^n)`.

An equal random initial channel followed by alternation after failures equalizes
the two world risks and attains the equal-prior lower bound. Every adaptive policy
has only one nonterminal observation branch, so deterministic policy enumeration
on that branch covers all deterministic policies; random policies are mixtures.

For fixed lambda>0 the regret has a finite limit

`Delta * ((2-lambda)/(2*lambda-lambda^2*(1-alpha^2)) - 1/(lambda*(1+alpha)))`.

For lambda=c/T and fixed c>0, alpha>0, the predicted normalized limit is

`Delta * ((1-exp(-c))/c - (1-exp(-c*(1+alpha)))/(c*(1+alpha))) > 0`.

The latter is a sequence of different environments. It does not establish linear
regret in a fixed environment. At lambda=0 both policies remain suspended and regret
is zero; at alpha=0 the two worlds are identical and regret is also zero.

## Independent finite checks

1. Enumerate every failure-branch action sequence of length T-1 for all T=1..12
   under three rational laws. Accumulate reward from first-success probabilities
   with exact fractions, and compare the optimal equal-prior value to the formula.
2. Solve the two-world minimax linear program over mixtures of those sequences for
   T=1..10, under the same three laws. Check the LP result and both world risks of
   the symmetrized alternating policy against the formula.
3. Compute the Bayesian reward DP over failure counts independently for 18 cells
   through T=256. Its posterior updates must condition on actual failures only.
4. Report the frozen 72 closed-form scaling cells, including fixed environments
   and lambda=c/T. These are deterministic formula evaluations, not learning runs.

The proof, not these finite checks, supports the all-policy minimax claim. No
Monte Carlo, GPU work, field data, parameter search or Paper E/F dependency.

## Parent collision and scientific stop

Rosenberg, Cohen, Mansour and Kaplan (ICML 2020), supplement Appendix C, already
use an initial state, absorbing goal, and one unknown action with greater success
probability. Set B*=1/p+ and epsilon=1-p-/p+=2*alpha/(1+alpha); the transition and
feedback kernels match. Their proof uses small epsilon and repeated episodes;
our finite-horizon single episode is a truncated-cost variant, so their reported
K-episode bound must not be quoted as this exact formula. For alpha<1/15 and
B*>=2 the parameters also fall inside their stated lower-bound construction range.

The identity reward=Delta*(T-min(tau,T)) preserves all policies, observations and
regret under conversion to truncated waiting cost. No inventory, price, ownership,
funding or strategic residual remains. This exact reduction already blocks a
standalone novelty claim for this formulation. The independent checks preserve a
useful benchmark, not an escalation case. Gittins (1979), Section 10, is an earlier
first-success search parent, but its independent-arm index theorem is not applied
to this correlated two-world prior.

Primary sources checked before computation:

- https://proceedings.mlr.press/v119/rosenberg20a.html
- https://proceedings.mlr.press/v119/rosenberg20a/rosenberg20a-supp.pdf (Appendix C)
- https://academic.oup.com/jrsssb/article/41/2/148/7027626 (Gittins, 1979)
