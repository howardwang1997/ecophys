# Paper G: recovery time is only one side of a bias certificate

PRIVATE / INTERNAL. `public_evidence_eligible: false`. Paper-only theorem
preflight for the existing protection/inventory boundary. No new candidate,
scientific implementation or native protocol is activated. Decision: `not_trigger`.

**Result:** under explicit recovery assumptions, a normal inventory state can
be reached in expected time at most B+Q(B+1/p0). That certificate alone does
not bound optimal bias span. A two-state counterexample has one-step reset,
unbounded bias span and zero learning regret. The missing quantitative target
is an upper bound on the value advantage outside the normal-state set.

## 1. Connection and conditional recovery lemma

The [MMP lifecycle audit](ecomd_paper_g_mmp_recovery_scope_2026-09-11.md) and
[blocking-parent audit](ecomd_paper_g_blocking_parent_scope_2026-09-11.md) leave
the full group/inventory/reset representation unproved. This note checks a
possible sufficient certificate; it does not replace that native contract.
It reuses the existing [customer recovery construction](ecomd_paper_g_reentry_theory_result_2026-09-08.md).

Fix a common discrete physical clock, inventory q in {0,...,Q}, and a set C
of normal states z_q, one per inventory. Require all of the following:

1. From any admissible state, a legal quiescence procedure cancels/drains pending
   activity and reaches some z_q within expected time B, uniformly conditional
   on the history when the procedure starts. Initial draining may change q.
2. At z_q, one legal unit quote can move inventory one step toward any prescribed
   target q*. Conditional on every preceding failure, its next-round success
   probability is at least p0>0. Failure leaves that recovery quote usable;
   a success can trigger protection, but no other inventory-changing order remains.
3. After such a success, quiescence costs at most B in conditional expectation,
   restores z at the new inventory, and does not alter that inventory. Waiting
   and this action sequence preserve all funding and risk constraints.

These are assumptions requiring a native truth contract, not verified features
of Deribit. In particular, a documented reset button does not certify bounded
pending-event draining or the existence of a usable recovery quote. B and p0
must be uniform over the contemplated unknown market-law class, in the same
clock as the horizon; neither may be tuned after observing the outcome.

**Conditional lemma.** Every z_q* is reachable by one fixed recovery strategy
with expected hitting time bounded by

\[
H:=B+Q(B+1/p_0).
\]

**Proof.** First quiesce. The target is then at most Q unit moves away. The
conditional probability that any unit move takes more than n attempts is at
most (1-p0)^n, by iterated conditioning; its expected waiting time is at most
1/p0. Follow each successful unit move with quiescence. Assumption 3 prevents
backtracking, so at most Q such stages occur. Conditional expectation and
addition give the bound, without requiring independence between stages. The
strategy uses observable receipts and availability, not the unknown law.

This bounds a controlled hitting time. It is not itself a bound on the regret
of using that strategy repeatedly, nor a certificate for arbitrary ongoing
trading policies. Fixed native bounds B,p0 have not been established here.

## 2. What one-way recovery proves about bias

Suppose, additionally, a finite communicating MDP represents the same contract,
with expected rewards in [0,R], optimal average gain g and a bounded optimal
bias h satisfying the average-reward Bellman equation. This is conditional
algebra, not a proof that the completed protection process satisfies those
assumptions. The repository's [SCAL corollary](ecomd_paper_g_access_modewise_bound_2026-09-11.md)
explains why a genuine bias-span certificate would matter.

For any admissible policy that reaches z from s at an integrable stopping time
tau, the Bellman inequality, telescoped to tau, gives

\[
h(s)\ge h(z)+\mathbb E\sum_{t<\tau}(r_t-g),
\quad\text{hence}\quad h(z)-h(s)\le R\mathbb E\tau.
\]

Bounded h and rewards and integrable tau justify passage from truncated
stopping times. If every z in C is reachable from every s in mean time H,

\[
\min_s h(s)\ge\max_{z\in C}h(z)-RH.
\]

Define the remaining one-sided advantage

\[
K:=\max_s h(s)-\max_{z\in C}h(z)\ge0.
\]

Then, and only with a bound on K as well,

\[
\operatorname{span}(h)\le RH+K.                 \tag{1}
\]

Writing K is not proving it small: without independent control of K, (1) is
only a decomposition. A sufficient stronger alternative is a uniform bound
on controlled travel between every ordered pair of states. One-way reset to
C does not provide that. A proof that C contains a maximum-bias state would
set K=0, but no such dominance proof has been supplied for threshold/window,
pending-order and group states. Normalization may remove valuable timing state.

## 3. Exact counterexample: fast reset, large span, zero learning loss

Consider a parent MDP with states L,H and parameter epsilon in (0,1]. At L,
`try` pays zero and moves to H with probability epsilon, otherwise staying L.
`reset` pays zero and stays L. At H, `stay` pays one and stays H; `reset` pays
zero and moves to L. Rewards precede transition. No other actions exist.

Every state can reach the reference L in at most one step. The MDP is
communicating for each positive epsilon. Its optimal Bellman solution is

\[
g=1,\qquad h(L)=0,\quad h(H)=1/\epsilon.
\]

At L, the `try` right-hand side is epsilon*h(H)=1, exceeding the reset
value zero. At H, `stay` attains 1+h(H), exceeding reset. These verify both
Bellman equations. Thus bias span is 1/epsilon despite the one-step reset.
With C={L}, the missing K is exactly 1/epsilon.

For every horizon T, the policy that tries at L and stays at H is optimal,
independently of epsilon. Delaying an attempt cannot make the first arrival
at H earlier, and resetting from H replaces a maximal future stream of ones
with zeros until another success. Equivalently, finite-horizon induction gives

\[
V_T(H)=T,\qquad
V_T(L)=T-\frac{1-(1-\epsilon)^T}{\epsilon}.
\]

An unknown-epsilon learner can use exactly that policy. Its regret against
the same known-law finite-horizon oracle is zero for every T and epsilon.
Large bias span therefore does not by itself establish a hard learning
instance either. This is a standard parent witness, not a market experiment,
an empirical protection claim or a new publication contribution.

## 4. Decision and next decisive target

No recorded MMP blocker is removed. Native H is unqualified, K is unbounded
by the present argument, and there is no new algorithm, learning lower bound,
independent implementation or accessible participant truth asset.

Future theorem work should target a lawful bound on K, or prove its necessity
using rival unknown laws with different optimal actions under the same feedback.
Merely measuring recovery duration or exhibiting a large state-value gap does
not settle that question. This narrows the next proof task without authorizing
candidate harvesting, account work or experiments. The overall Paper G goal
remains unmet.

Two reusable paper-only diagnostics are retained: conditional recovery time,
and the bias decomposition with its exact counterexample. No new external
source, data, PDF, code or outcome was needed. Registry checks verify provenance
and scope labels; they do not independently certify the mathematical argument.
