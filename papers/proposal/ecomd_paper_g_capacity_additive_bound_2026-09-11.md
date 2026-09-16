# Paper G: shared-parameter optimism moves capacity to an additive term

PRIVATE / INTERNAL. `public_evidence_eligible: false`. Paper-only derived
upper bound for the existing model. No implementation or independent novelty
claim. Decision: `not_trigger` pending substantive parent/contribution assessment.

## 1. Result and unchanged market contract

Retain exactly the fixed-mark, prefunded, unit-action customer model and its
single exogenous restoration in the [modewise bound](ecomd_paper_g_access_modewise_bound_2026-09-11.md).
Capacity is Q>=2, the initial inventory remains q=1, and reward is in [-1,2].
The unknown iid customer law has parameters theta=(nu,p_b,p_s): buyer probability,
buyer high willingness and seller low willingness. Nu is in (0,1); no known
positive lower bound on either side is required. Willingness probabilities may
be endpoints. The learner observes every request side after acting, and its own
fill/nonfill. Restoration is one-way, independent of actions/customers and may
have unknown probability lambda in [0,1].

Let T>=1, eta=(T+1)^(-2), L=log(6T/eta), and K_T=5+3 floor(log2 T).
There exists an actual-feedback learner with an exact optimistic planning oracle
whose expected regret against the original known-law, finite-horizon optimal
dynamic controller obeys

\[
\boxed{R_T\le\min\left\{3T,\;
4Q+2QK_T+(24+16\sqrt2)\sqrt{LT}+13T\eta\right\}.}       \tag{1}
\]

Thus the bound is O(sqrt(T log T)+Q log T), uniformly in the exogenous
restoration law and all admissible customer probabilities. This improves the
Q-dependence of the previously derived generic SCAL upper bound. It does not
prove optimal Q-dependence, a Q-uniform matching lower bound, efficient planning,
or a result for transaction-triggered/repeated protection. Q remains in an
additive term; the bound is not fully independent of capacity.

This is a specific statistical refinement of the retained original model, not
a new protection variant or a new candidate cycle. The preceding allocation
review permits reconsidering a concrete structural improvement, but this proof
alone does not qualify a route for execution or establish its publication novelty.

## 2. Biases for every candidate customer law

For a fixed suspended/eligible mode, the existing discounted imitation argument
gives |V_gamma(q)-V_gamma(q')|<=2|q-q'|. It holds also at the endpoints nu=0,1,
which can occur inside confidence sets even though the true law is two-sided.

Normalize discounted values at q=0. Their adjacent differences are bounded by2,
and (1-gamma)V_gamma(0) lies in[-1,2]. Finite-dimensional compactness along a
subsequence gamma->1 yields a scalar g and h(0)=0 satisfying

\[
g+h(q)=\max_{a\in A_m(q)}\{r_\theta(q,a)+P_\theta h(q,a)\},
\qquad |h(q+1)-h(q)|\le2.                         \tag{2}
\]

Consequently span(h)<=2Q. Bellman telescoping bounds any policy's average
return above by g and a maximizing stationary policy attains g from every q.
Hence g is the optimal scalar gain, including candidate endpoint laws. No
communication claim for those endpoints is needed.

The optimistic planner maximizes g over the confidence set for theta and
over g,h satisfying (2), with g in[-1,2] and h(0)=0. This set is nonempty and
compact: there are finitely many legal actions/states, the Bellman constraints
are closed and the local bound bounds h. A maximizer exists. The planner uses
one common theta for all inventories, not separate adversarial laws per state.
It selects a stationary Bellman-maximizing action for that model.

This is an existence oracle. No polynomial-time algorithm for this constrained
planning problem is asserted or implemented.

## 3. Three observed streams and count-doubling epochs

Maintain three counts/empirical means, shared across modes:

- N_nu counts all observed request sides.
- N_b counts buyer requests facing a legally posted wide ask102. Its fill
  indicator is a Bernoulli(p_b) observation.
- N_s counts seller requests facing a legally posted wide bid98. Its fill
  indicator is a Bernoulli(p_s) observation.

No willingness observation is imputed for a narrow/off quote. Quote decisions
precede the current request and willingness, so the sampled willingness streams
remain iid Bernoulli streams under adaptive selection. A stopped observation
sequence can be extended by fresh iid variables for the concentration argument;
this extension gives the learner no extra observations.

For n>=1 use the clipped Hoeffding interval with radius sqrt(L/(2n)); for n=0
use[0,1]. A union bound over three streams and sample counts1,...,T shows that
all intervals contain their parameters with probability at least1-eta. Their
widths are at most

\[
d(n)=\min\{1,\sqrt{2L/\max(1,n)}\}.                \tag{3}
\]

At each epoch start freeze these intervals, solve the optimistic problem in
the current mode, and follow its stationary policy. End the epoch as soon as
any stream accumulates max(1,N_j at epoch start) new observations, or when the
mode changes. Retain all counts after the mode change and start from the actual
current inventory. Each counter triggers at most1+floor(log2 T) endings, and
there is at most one mode-change ending. The number of nonempty epochs is
therefore at most K_T. No market reset or explicit exploratory probe is added.

## 4. Local prediction error has no capacity factor

Fix an epoch's h and a legal action; let qbar be the deterministic post-hedge
inventory. Subtract the common hedge cost and h(qbar) from r+h(q_next).
For each request side its conditional expectation is:

- off:0;
- narrow:1+h(qbar plus/minus1)-h(qbar), lying in[-1,3];
- wide:p_side[2+h(qbar plus/minus1)-h(qbar)], lying in[0,4].

Only feasible neighboring inventories are used. The two side expectations
therefore lie in a common interval[-1,4], and a willingness-probability change
has coefficient at most4. If W_b,W_s indicate the posted legal wide quotes,
then for two laws theta and theta-tilde,

\[
|(\widetilde r+\widetilde P h)-(r+Ph)|
\le6|\widetilde\nu-\nu|
+4\nu W_b|\widetilde p_b-p_b|
+4(1-\nu)W_s|\widetilde p_s-p_s|.                 \tag{4}
\]

The constant6 is conservative. To verify the weights, first change the side
mixture while holding the tilde side expectations fixed, then change those
expectations at the true weights nu and1-nu. Equation(4) is bounded by10 even
on a confidence failure. Its proof uses adjacent value differences, not the
global span2Q. Reward and inventory-transition correlation is retained.

## 5. Expected regret accounting without conditioning martingales on success

Let g_m be the true gain of the current mode and let tilde-g,h be the current
optimistic epoch solution. On the event that all confidence intervals cover,
tilde-g>=g_m. On its complement g_m-tilde-g<=3. Let d_j be the frozen widths.
For each round define the mean-zero, history-adapted residual

\[
Z_t=\mathbb E[r_t+h(q_{t+1})\mid\mathcal F_t,a_t]
       -[r_t+h(q_{t+1})],
\]

where the current h and action are chosen before the customer draw. The epoch
Bellman equation and (4) imply, on every sample path,

\[
g_{m_t}-r_t\le
6d_\nu+4\nu W_b d_b+4(1-\nu)W_s d_s
+13\mathbf1_{\mathrm{confidence\ failure}}
+h(q_{t+1})-h(q_t)+Z_t.                           \tag{5}
\]

The factor13 accounts for at most3 of lost optimism and10 of model error on
the failure event. The added widths are nonnegative there. Sum (5) over epochs:
the potential increments telescope within each epoch and contribute at most
2QK_T. The unconditional expectation of sum Z_t is zero. In particular, we
do not incorrectly condition a martingale on a future global success event.

For each observed stream, the number n already seen when its next observation
arrives is less than twice max(1,N_j at epoch start). Thus its frozen width is
at most2sqrt(L)/sqrt(max(1,n)). Summing over observations gives

\[
\sum_{\text{observations of }j}d_j\le4\sqrt{L N_j(T)}.   \tag{6}
\]

The selection W_b d_b is predictable. Therefore
E sum nu W_b d_b=E sum 1_{buyer} W_b d_b, and similarly for sellers. These
equalities hold unconditionally, including failed confidence paths. Since
N_nu(T)=T and N_b(T)+N_s(T)<=T, equations(5)–(6) yield

\[
\mathbb E\left[\sum_t g_{m_t}-\sum_t r_t\right]
\le2QK_T+(24+16\sqrt2)\sqrt{LT}+13T\eta.          \tag{7}
\]

Finally, the earlier modewise oracle comparison gives
V_T^*<=E sum_t g_m_t+4Q, because the one-way external mode law is independent
of the policy. Combining with(7) proves(1). This comparison remains the full
finite-horizon dynamic oracle, not a greedy or discounted approximation.

## 6. Novelty, limits and next decisive work

The proof uses standard confidence-set optimism and count doubling plus the
repository's already derived local imitation certificate. Shared-parameter
learning is not a new general principle. For example, the official abstract
of [Chae et al., AISTATS2025](https://proceedings.mlr.press/v258/chae25a.html)
reports an efficient average-reward linear-mixture algorithm with a bound
depending on feature dimension and bias span. Only that abstract/metadata was
inspected here; no exact reduction, full theorem comparison or superiority
over its instantiated bound is certified. Search leads on other structured
MDPs are not a completed novelty neighborhood.

Equation(1) is a stronger model-specific statistical upper bound. Independent
novelty, efficient optimistic planning, optimal capacity dependence and a
complete prior collision audit remain open. The existing Q2 lower witness
retains its scope; it does not become a lower bound uniform in Q or positive
lambda. No transaction-triggered protection result follows.

The next decisive review should check whether the exact local-bias/shared-stream
specialization is already available and whether the optimistic planner can be
realized efficiently under the same contract. Until then this is a reusable
theory asset, not an activated Paper G. No experiment or code execution was
performed to establish the bound.
