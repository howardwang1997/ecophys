# Paper G: blocking-bandit parent and comparator scope

PRIVATE / INTERNAL. `public_evidence_eligible: false`. Bounded parent audit;
no new question program, simulation or activation. Decision: `not_trigger`.

**Result:** reward-correlated cooldown and policy-dependent availability already
have direct bandit parents. Their selected guarantees do not resolve exact
dynamic-oracle regret for the repository's inventory/protection contract.
Neither a direct transfer nor independent Paper G novelty is established.

## Repository connection and selected sources

The preceding [native MMP audit](ecomd_paper_g_mmp_recovery_scope_2026-09-11.md)
isolated a policy-dependent occupation term that the external-clock proof cannot
remove. The present check asks whether this obstacle is already recognized in
the nearest parent, rather than opening another venue or candidate.

[Basu et al., Blocking Bandits, NeurIPS 2019](https://proceedings.neurips.cc/paper_files/paper/2019/file/88fee0421317424e4469f33a48f50cb0-Paper.pdf)
models deterministic unavailability after an arm is selected. Section 1.2
explicitly distinguishes policy-dependent availability from sleeping-bandit
availability and describes the product countdown-state MDP. The main UCB
comparison is to an informed greedy policy; greedy need not equal the full
optimal schedule. Sections 1–2 and selected comparator statements were read,
not the supplementary proofs. PDF page 3 was visually checked.

[Atsidakou et al., Combinatorial Blocking Bandits with Stochastic Delays, ICML 2021](https://proceedings.mlr.press/v139/atsidakou21a/atsidakou21a.pdf)
allows joint, correlated reward/delay draws, bounded armwise delays and a fixed
family of feasible subsets. The learner observes chosen rewards and availability.
Its optimal comparator knows distributions but not future realizations. Theorem 7
controls approximate regret with coefficient alpha*beta/(1+alpha*beta); the
positive result assumes hereditary feasibility. Selected Sections 2–5 and the
theorem statement were inspected; the full proof was not audited. PDF pages
3, 4 and 8 were visually checked. Published experiment context was visible in
the text response, but supplies no new Paper G evidence or outcome access.

## Exact inclusion of a stripped parent mechanism

For each arm i and round t, independently draw a Bernoulli variable F with
parameter p_i. Fix b_i in (0,1] and a nonnegative integer L_i, and define

\[
X_{i,t}=b_i F_{i,t},\qquad D_{i,t}=1+L_i F_{i,t}.
\]

Selecting arm i reveals X and blocks that same arm for D-1 later rounds. A
zero outcome gives no cooldown; a positive outcome gives L_i blocked rounds.
The pair is bounded, iid across the stipulated draws and correlated within a
draw, so it satisfies the selected stochastic-blocking model exactly. Choose
the fixed hereditary family consisting of the empty set and all singletons.
Reward observation may itself identify F; no hidden future draw is supplied.

This is an elementary specialization of an existing parent. It rules out
claiming that *outcome-dependent cooldown alone* escapes that parent. It is
**not** a legal reduction of the complete EcoMD inventory model: there is no
inventory boundary, shared counter, group purge, reset decision or pending
execution in this specialization. Those omissions cannot be silently applied
to a native market lower bound.

## Why the regret comparator must remain explicit

Let V* denote full known-law dynamic value for a fixed contract and let J(pi)
be a learner's expected return. For a fixed coefficient rho in (0,1),

\[
R_\rho=\rho V^*-J(\pi),\qquad
R_1=(1-\rho)V^*+R_\rho.
\]

Thus a sublinear upper bound on R_rho leaves a potentially order-T term when
V* grows proportionally to T. It does not establish sublinear R_1. Conversely,
the identity is not a lower bound proving that a particular algorithm actually
incurs that loss. Even an exact per-round selection oracle (alpha=beta=1)
leaves rho=1/2 in the cited generic blocking guarantee; a static selection oracle
is not an exact horizon-wide scheduling oracle. Special instances can admit
stronger results, so no universal impossibility claim follows.

For the older greedy comparator, the analogous decomposition is
V*-J(pi)=[V*-J(greedy)]+[J(greedy)-J(pi)]. Learning error and known-law
scheduling suboptimality must be reported separately.

Reward transformations also require care. Adding c to each *selected* arm's
payoff changes return by c times the expected number of selected arms, which
can differ across policies. The repository's valid constant-per-round reward
shift is not the same transformation. No signed inventory-profit objective is
transferred merely by normalizing observed selected-arm payoffs.

## Remaining native mismatch and stopping decision

The direct identification “each quote is an arm” has not been established.
For example, a successful execution in one protected group can affect another
quote that was not itself selected. The selected parent blocks only selected
arms through their own draws. Encoding a whole group as a larger action must
still preserve quote choice, inventory, threshold/window memory, lawful resets,
feedback and objective; no such equivalent encoding is proved here.

A completed finite-state MDP may be a useful representation, but finiteness
alone does not exclude a worthwhile efficient-learning theorem. The relevant
test is whether a native structural bound improves on the existing generic
parent while retaining the same oracle, feedback and legal lifecycle. No such
bound, accessible participant truth asset or independent implementation has
been established by this audit. Historic MMP blockers remain unchanged.

Stop expanding the blocking bibliography for the bare cooldown claim. A next
decisive update must either certify a lawful group/inventory representation
and a quantitative learning residual, or identify a truth/control asset removing
the recorded participant-state blocker. Source mismatch alone is not that
update. No candidate harvesting, account work or execution is authorized.

## Recorded scope

Two primary papers; two standard paper-only diagnostics (parent specialization
and comparator decomposition); two PDF caches and four page renders; no
scientific code, data/model payload or numerical outcome. Formal, contract,
manifest, existing graph node, re-entry ledger, daily log and memory are updated.
The publication-level objective of the active Paper G goal remains unmet.
