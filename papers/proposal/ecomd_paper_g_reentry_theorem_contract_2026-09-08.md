# Paper G re-entry: prospective theorem verification contract

Frozen before the v3 computation. The PI requests new mechanisms or stronger
theorems. This bounded audit preserves the closed M0 record; it does not presume
novelty or start another candidate-harvesting cycle.

## T1: executable imitation bounds reward loss, not recovery time

For M0 states s=(q,b,a), define d(s,s')=|q-q'|+|b-b'|+|a-a'|. Couple two markets
with common customer and refill innovations. Given a legal virtual action, the
real account copies its hedge if feasible and otherwise omits it; it copies each
quote unless the real post-hedge inventory makes that quote infeasible.

Conjectured certificate, to be proved by event cases and exhaustively checked:

`r_virtual - r_real <= 2*(d_before - d_after)`.

Hedge omission costs the virtual account one tick but never increases d: it
either consumes a mismatched depth bit or brings inventories closer while possibly
creating one depth mismatch. A customer fill omitted at a real inventory boundary
brings inventories closer by one and loses at most two ticks. Shared refill cannot
increase depth mismatch. Summation predicts loss <=2*d_initial for any finite tape.

For a known-law optimal virtual policy, implementation under actual feedback uses
conditional sampling of the latent virtual transition after the real observation;
no hidden actual type or future draw is given to the real policy. The sampled
joint law matches the coupling. Thus the proposed consequence is

`|V_T(s)-V_T(s')| <= 2*d(s,s')`, and `span(V_T) <= 2*(Q+2)`.

The bound is uniform in horizon, the customer-law parameters and rho, including
zero. For communicating rho>0 it also bounds the optimal bias span via discounted
limits (apply the same discounted telescoping certificate). SCAL/REGAL already
turn known bias-span bounds into regret bounds. Any resulting rate is a parent
corollary, not a new RL algorithm. At rho=0 do not silently apply communicating-MDP
theorems to the full depth state space.

## T2: a persistent access right differs from one unit of depth

Keep all funded M0 customer actions and Q>=2. Add an observed eligibility state.
While suspended, external hedges are unavailable. At the end of each suspended
round an independent Bernoulli(lambda) restores eligibility. After restoration,
external depth is full each round permanently. This is a specified theoretical
access contract, not a calibrated model of any venue's reinstatement process.

Fix nu=0.8 and theta_b=theta_s=1. In the eligible regime the dealer can restore
q=1 each round by one hedge, then quote 98/102; the first customer trade earns
two ticks and subsequent rounds earn one after hedging, so g_eligible>=1.
During n suspended rounds, inventory conservation bounds customer sells to at
most customer buys plus Q; reward <=4*(seller arrivals)+2Q. At the independent
restoration time this gives expected reward <=0.8*E[n]+2Q.

The full-depth eligible subsystem has bias span <=2Q by T1. The finite-horizon
eligible-versus-suspended optimal-value difference at the same q is therefore at
least `0.2*G_T(lambda)-6Q`, where

`G_T(lambda)=(1-(1-lambda)^T)/lambda`, with `G_T(0)=T`.

This follows by comparing each eligible continuation with g_eligible times its
remaining horizon plus/minus 2Q, then applying the suspended reward bound.
Equivalently, the relative-value access gap grows at least 0.2/lambda-O(Q).
Thus a constant inventory/depth bound cannot extend to an indefinitely reusable
access right. Customer-only information probing still works: this is an economic
continuation-value obstruction, not a proof of information nonidentifiability or
learning regret proportional to 1/lambda.

## Frozen checks and stopping rules

- Exhaustive T1 event certificate over Q=2/4, every ordered state pair, every legal
  virtual action, all four customer types and all four refill innovations.
- Exact M0 DP on 96 fixed law/capacity/rho cells through T=4096. Check every
  adjacent-state inequality at every horizon; adjacency implies all-pairs T1.
- Exact access-gate DP on ten fixed capacity/lambda cells, reporting all four
  horizons. Check T2, the lambda=0 split, and the one-round lambda=1 switch.
- No learner benchmarking, parameter selection, field outcomes or GPU. A proof
  failure stops the affected proposition. Computation checks finite instances;
  only the analytic argument can support the uniform statement.
- Audit bounded stateful market-making imitation, bias-span RL, censored inventory
  and the official native access grammar. Neither an elementary application of a
  parent theorem nor a two-state recovery counterexample alone qualifies Paper G.
