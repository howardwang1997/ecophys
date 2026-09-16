# Paper G: exact exogenous-parent mapping and the remaining theorem scope

PRIVATE / INTERNAL. `public_evidence_eligible: false`. Bounded primary-source
collision follow-up to the capacity-additive derivation. Decision:`not_trigger`.
No new candidate cycle, algorithm implementation or independent novelty claim.

## 1. Decision

The frozen inventory model is exactly a four-type Exo-MDP and a dimension-four
linear mixture MDP. Learning from censored customer feedback while avoiding a
state-count factor is already an established parent problem. Those properties
cannot independently motivate a new Paper G. The preceding
[capacity-additive proof](ecomd_paper_g_capacity_additive_bound_2026-09-11.md)
remains a valid retained derivation; this review does not establish that its
exact continuing-control bound is an immediate published corollary.

The unresolved contribution is narrower: whether the local inventory bias
certificate gives a useful, efficiently achievable improvement under the same
continuing-control contract. A different horizon convention or an unimplemented
planning oracle is not sufficient evidence of publication-level novelty.

## 2. Exact four-type representation

Freeze either original S/E access mode. Let e range over buyer-high,
buyer-low, seller-high, seller-low, with probability vector

\[
\mu=(\nu p_b,\nu(1-p_b),(1-\nu)(1-p_s),(1-\nu)p_s).
\]

Every legal action consists of the original hedge and quotes. Given inventory
q, action a and type e, both next inventory f_m(q,a,e) and marked reward
b_m(q,a,e) are known deterministic functions. No willingness is revealed to
the learner by writing this representation. The actual observation is the
known function of the same type: request side, own fill/nonfill, reward and
inventory. It can be coarser than e. Ignoring the extra side signal gives a
learner in the parent's unobserved-exogenous regime.

With reward normalization (b+1)/3, the model has exactly the Exo-MDP form.
In particular,

\[
P(q'\mid q,a)=\sum_e\mu_e\mathbf1\{q'=f_m(q,a,e)\},\qquad
\mathbb E[(b+1)/3\mid q,a]=\sum_e\mu_e(b_m(q,a,e)+1)/3.
\]

Reward and transition remain correlated through e. We do not replace their
joint law with independent draws. State-dependent legal actions can be encoded
in a fixed finite label set by assigning invalid labels to an existing legal
off action; this adds no attainable behavior or observation.

The transition information matrix has rank exactly4 for Q>=2. At q=1, take
no hedge. A wide ask alone gives the next-q=0 row (1,0,0,0); a narrow ask alone
gives (1,1,0,0). A wide bid alone gives next-q=2 row (0,0,0,1); a narrow bid
alone gives (0,0,1,1). These four rows are independent. The matrix has only
four columns, so its rank is4, and the maximum of transition/reward ranks is4.
This is an algebraic certificate, not a data-derived rank or an optimal
information-complexity lower bound. The probability simplex has affine
dimension3; it is not inconsistent for the feature matrix to have linear rank4.

## 3. Selected primary comparisons

**Wan et al., arXiv:2409.14557v4, July23 2026.** Read selected formal setup,
representation/rank definitions, Theorem3 and the reset/feedback portion of
Algorithm2. This version's theorem gives an episodic upper bound
Otilde(H r sqrt(K)+H r^2); its no-observation regime sees reward and next
endogenous state. Thus the frozen model's r=4 representation is a direct
parent collision. The theorem is over K episodes of H steps. Setting K=1,H=T
does not yield the retained sqrt(T) continuing bound, and assigning short
episodes does not authorize physical inventory resets. The older v3 headline
rate is superseded for this comparison. No complete proof or scientific code
audit was performed. [Primary v4](https://arxiv.org/pdf/2409.14557v4).

**Chae et al., AISTATS2025.** Read Assumptions1–2, Algorithm1, computational
discussion and Theorem1, with PDF pages4–6 visually checked. This is an
average-reward linear-mixture parent with known deterministic reward and a
global bias-span bound. The displayed theorem retains
Otilde(d sqrt(H T)+H sqrt(d T)+d^(7/4) H T^(1/4)); use this expression when
varying capacity, rather than silently dropping terms based on the abstract.
The published planner uses clipped discounted value iteration. Section4 below
gives an exact known-reward representation for our model, but does not prove
that the preceding local-bias optimistic planner has the same computational
properties. [Primary paper](https://proceedings.mlr.press/v258/chae25a.html).

**Osband and Van Roy, NeurIPS2014, eluder dimension.** Selected Section2,
Theorem1/Corollary1 and the optimism discussion already relate parameterized
model learning to a value-sensitivity constant. Its displayed Bayesian,
repeated finite-episode statement is not directly the retained frequentist
continuing guarantee. Scalar next-inventory means alone are insufficient for
an automatic reduction: different distributions can share a mean and have
different continuation values. No applicable constant was certified here.
[Primary paper](https://papers.neurips.cc/paper_files/paper/2014/file/b0a77afa642922102120b01b1ae6f200-Paper.pdf).

**Maran, Salaorni and Restelli, arXiv:2603.02862v1.** Selected Section2 and
Section3.1 concern observed exogenous state and a known endogenous transition
component, with finite-episode guarantees. Simply calling customer willingness
an exogenous state would supply unavailable observations. This selected result
does not license an exploration-free learner under the original feedback.
[Primary v1](https://arxiv.org/html/2603.02862v1). These four selected comparisons
are not a full hostile audit or a completed literature neighborhood.

## 4. Known deterministic reward without giving away willingness

For a frozen mode, augment the observed state to x=(q,z), where z is the
previous realized raw reward, in {-1,0,1,2}, and set z_initial=0. The new known
reward is rbar(x,a)=(z+1)/3. The next state is

\[
x'=(f_m(q,a,e),b_m(q,a,e)).
\]

The learner already knows z. This changes neither legal actions nor knowledge
of the current customer type. Over n rounds,

\[
3\sum_{t=1}^n\bar r_t-n=\sum_{t=1}^n b_t-b_n+z_1.
\]

Consequently the transformed and original cumulative rewards differ only by
an endpoint term; their infinite-horizon gains obey gbar=(g+1)/3.
If g+h(q)=max_a E[b+h(q')], then

\[
\bar h(q,z)=(h(q)+z)/3
\]

satisfies the augmented Bellman equation. Its span is at most (2Q+3)/3 using
the retained inventory certificate. This is a direct substitution, valid even
for unreachable artificial initial reward labels.

To meet the linear-mixture feature normalization, use
phi_e(x,a,x')=one-half times the deterministic-type transition indicator and
theta=2mu. Then P=phi dot theta, ||theta||_2<=2, and for every F in[0,H],
||phi_F||_2<=H. Thus d=4 is sufficient independently of Q. This removes
unknown stochastic reward as a representation-level barrier to this parent;
it does not remove the existing independent-contribution blocker.

The imported theorem's global span certificate is O(Q). Its displayed bound
therefore does not directly certify O(sqrt(T log T)+Q log T) with constants
independent of Q. This compares proved certificates, not empirical algorithms
or optimal achievable rates. A tighter instance analysis could still erase
the apparent distinction. No superiority over the parent's actual performance
is claimed. Extending a fixed-time parent statement to the random mode boundary
also requires an explicit stopping-time/anytime argument before importing an
end-to-end learning theorem; none is asserted here.

## 5. Allocation and next decisive test

Close the broad contribution pitches based on latent exogenous customers,
shared parameters, or removal of an inventory-state-count factor. Retain the
two exact reductions above as reusable standard theory assets. No complete
collision of the precise capacity-additive theorem has been established, and
no new scientific contribution has been established either.

The next bounded paper-only target is the computational bottleneck of that
specific theorem: construct a planner that preserves the local-bias and actual
feedback guarantees with an explicit error/cost bound, and determine whether
that construction is a routine parent specialization. If it is routine, stop
this proposal as an independent Paper G rather than adding access variants.
There is no authority for implementation or experiments at this stage.
