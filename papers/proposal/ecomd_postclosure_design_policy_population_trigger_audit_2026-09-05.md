# EcoMD post-closure design, policy, and population trigger audit

**Date:** 2026-09-05  
**Scope:** three post-closure primary-work screens  
**Archetypes:** `measurement_method`, `simulator_method`, `simulator_method`  
**Decisions:** three `not_trigger`  
**Candidate harvesting:** not authorized  
**Outcome access, implementation, simulation, SSH, and GPU work:** not authorized

## 1. Why these three sources were screened

The closed EcoMD program has three recurring blockers that a genuinely new source might remove:

1. observationally equivalent market states need an experiment that returns honest ambiguity rather
   than a forced point answer;
2. predictive simulator accuracy needs a policy-relevant validity target that does not collapse to
   ordinary transition fitting or off-policy evaluation;
3. agent-count transfer needs a population object that survives economically equivalent splitting
   and has a finite-population error theorem.

Three recent works appear, at headline level, to address exactly these blockers:

- [Fotias (2026)](https://arxiv.org/abs/2609.03686) introduces resolution-aware
  experimental design (RAED) under persistent nuisance uncertainty;
- [Dann, Mansour, and Mohri (2026)](https://arxiv.org/abs/2605.29032) formulate
  policy-aware simulator learning as a model--policy minimax game;
- [Makkar et al. (2026)](https://arxiv.org/abs/2609.02928) learn low-dimensional
  mean-field representations from offline trajectories and finite population snapshots.

The audit asks whether any source removes a recorded blocker rather than merely supplying a useful
component. The answer is no for all three formulations.

## 2. Screen A: response-resolution experimental design

### 2.1 Exact question

The market-native object is the set of intervention responses still compatible with a public
pre-state and a legal market action. Rival explanations are:

- **H1 -- response-resolution is a new target:** design the intervention that minimizes the size of
  a valid set of possible response functionals, even when latent market state persists;
- **H2 -- target relabelling:** a finite response target is simply the structural label in RAED,
  while continuous targets reduce to goal-oriented design or confidence-region design.

A positive answer would reopen outcome-blind design for the observation-quotient route. A null answer
is useful because it prevents rebranding structural set identification as an EcoMD-specific method.

### 2.2 Exact finite-target reduction

Let the original structural state be $s\in\mathcal S$, its nuisance state be
$\theta\in\Theta_s$, and experiment $e$ induce observation law
\(P^e_{s,\theta}\). Suppose the target is a finite response functional

\[
q:\mathcal S\longrightarrow\mathcal Q.
\]

Construct an ordinary RAED problem whose structural families are $u\in\mathcal Q$, whose nuisance
space is the disjoint union

\[
\Theta'_u=\bigsqcup_{s:q(s)=u}\{s\}\times\Theta_s,
\]

and whose observation law is

\[
P^e_{u,(s,\theta)}=P^e_{s,\theta}.
\]

Choose the validity and efficiency measures on $\Theta'_u$ to equal the intended weights over the
original states in the target fibre. A nonempty candidate set
\(\Gamma_e(Y)\subseteq\mathcal Q\), its false-exclusion loss, its nuisance-tail risk, and its
expected cardinality are then exactly the RAED objects. No approximation and no market assumption
is needed. The proposed finite response-resolution method is RAED after reindexing.

For a continuous $q(s)$, binning gives the same finite reduction but makes the answer depend on the
analyst's resolution. Without binning, the direct parents are goal-oriented optimal experimental
design and confidence-region design. [Attia, Alexanderian, and Saibaba
(2018)](https://arxiv.org/abs/1802.06517) already optimize an experiment for uncertainty in a
quantity of interest rather than the latent parameter. If the target is a finite optimal action,
the same reindexing applies; if the target is regret, the problem is ordinary Bayesian or minimax
decision-theoretic design. Response-only active causal design is also established in
[Wang et al. (2020)](https://proceedings.mlr.press/v119/wang20w.html).

### 2.3 Sequential and market exits

RAED explicitly states that its theory is one-step and names adaptive sequential alias-breaking as a
future extension. That makes a sequential version potentially useful, but not automatically novel:
sequential composite testing and safe stopping already have non-asymptotic parents such as
[PEAK](https://proceedings.mlr.press/v235/cho24a.html). A qualifying child would need a sequential
resolution theorem that is false for generic composite testing, not merely an acquisition function
wrapped around the RAED score.

The market bridge remains absent. [Acharya et al.
(2026)](https://arxiv.org/abs/2609.04087) give a market-native reminder of the same obstruction:
adjacent SPX--VIX smile laws admit a block-preserving Markovization while multi-period claims can
differ. That is strong evidence for honest ambiguity, but the paper already supplies the relevant
feasibility theorem and numerical solver; it does not supply a legal assigned market intervention,
complete pre-state, or untouched response truth for EcoMD.

### 2.4 Decision

`not_trigger`. RAED is a valuable evaluation language for a future qualified experiment, but a
response-functional variant is either an exact relabelling, a discretization choice, or an instance
of established goal-oriented/decision-theoretic design. No observation-quotient or causal-field
blocker is removed.

## 3. Screen B: policy-class-complete simulator validity

### 3.1 Exact question

The native object is the value gap between a market simulator and its target under the same
state-feedback trading strategy. Rival explanations are:

- **H1 -- deterministic tests suffice:** agreement for every deterministic stationary policy
  extends to all stationary randomized policies;
- **H2 -- occupancy feedback breaks convex extension:** state-wise randomization changes the
  resolvent nonlinearly and can reveal a difference hidden from every deterministic policy.

Both answers matter: H1 would drastically reduce a simulator validation suite; H2 requires the
policy class to be stated explicitly and invalidates a tempting shortcut.

### 3.2 The 2026 proposition is false

Proposition 2 of Dann, Mansour, and Mohri claims H1 because a randomized policy is a state-wise
mixture and occupancy is said to depend linearly on that mixture. The second statement is false:

\[
d_\pi\ \text{contains}\ (I-\gamma P_\pi)^{-1},
\]

so it is generally nonlinear in the action probabilities.

An explicit three-state counterexample uses states $(s_0,g,z)$, discount
$\gamma=1/2$, absorbing $(g,z)$, reward $r(g,\cdot)=1$, and zero reward elsewhere. Actions at
$(g,z)$ are identical. At $s_0$, define models $M$ and $\widetilde M$ by

| model/action | self | to $g$ | to $z$ |
|---|---:|---:|---:|
| $(M,a)$ | 0 | 0.20 | 0.80 |
| $(\widetilde M,a)$ | 0.50 | 0.15 | 0.35 |
| $(M,b)$ and $(\widetilde M,b)$ | 0 | 0.60 | 0.40 |

Because $V(g)=2$, deterministic action $a$ has value $0.2$ in both models and action $b$
has value $0.6$ in both. Since the other-state actions are identical, every deterministic
stationary policy agrees. Under the policy that mixes $(a,b)$ equally at $s_0$, however,

\[
V_M(s_0)=0.4,
\qquad
V_{\widetilde M}(s_0)
=\tfrac12\{0.25V_{\widetilde M}(s_0)+0.375\cdot2\}
=\frac37.
\]

Thus $0.4\ne3/7$. This is a valid correction to the new paper, but it is not a new research
contribution.

### 3.3 Direct collision with Proper Value Equivalence

[Grimm et al. (2021)](https://papers.nips.cc/paper_files/paper/2021/hash/400e5e6a7ce0c754f281525fae75a873-Abstract.html)
already prove exactly this separation in Proposition 5 and display a three-state witness in Figure 2:
the model and environment agree for all deterministic policies but disagree for a stochastic policy.
They also make the crucial distinction that deterministic-policy proper value equivalence is enough
to recover an optimal policy; it is not equality of every randomized policy's value. The earlier
[Value Equivalence Principle](https://arxiv.org/abs/2011.03506) and its proper-value extension
already define the relevant model classes.

Consequently, neither the counterexample nor the statement “randomized strategies must be included
when pointwise value fidelity is required” survives the direct-prior gate.

### 3.4 Small randomized test suites: a useful but non-actionable lemma

There is a narrow algebraic observation that is not the old counterexample. For two known finite
discounted $n$-state MDPs, parameterize a stationary policy by its free action probabilities $x$.
By Cramer's rule, every value component is a rational function of $x$. Each determinant is affine
in each state's probability block and has total degree at most $n$. After cross multiplication, a
value difference is represented by a polynomial of total degree at most $2n$. Since
$I-\gamma P_\pi$ is nonsingular for every stochastic $P_\pi$, equality for every randomized
policy is equivalent to these cross-products being zero polynomials.

With exact value oracles, sampling policy coordinates from a sufficiently large finite grid gives a
Schwartz--Zippel identity screen. This does **not** provide an ICLR route:

1. if transition and reward tensors are known, direct model comparison is cheaper and exact;
2. if only rollout samples are available, an arbitrarily small model perturbation gives a nonzero
   polynomial with arbitrarily small value gap, so no fixed-sample zero-versus-nonzero test exists;
3. tolerant worst-policy testing needs a margin, occupancy coverage, and an anti-concentration or
   complexity condition, and can concentrate its witness in a high-dimensional policy region;
4. estimating many policies from shared samples and fixed-confidence policy tests already have
   direct parents in [multiple-policy high-confidence evaluation](https://proceedings.mlr.press/v206/dann23a.html)
   and [policy testing in MDPs](https://proceedings.mlr.press/v300/ariu26a.html).

This is another instance of the simulator-oracle trilemma: exact model access makes the proposed
test redundant; sampled access makes uniform certification impossible without assumptions that
become the real contribution.

### 3.5 EcoMD and decision

The 2026 method actively samples the true environment and evaluates on control simulators. Its
practical critic relaxation explicitly removes the strategic policy adversary and relies on uniform
occupancy coverage. Its own fixed-offline-data discussion reduces to critic fitting plus a standard
trust-region/pessimistic policy. None of this supplies EcoMD's missing common market action language,
same-state field counterfactual, independent intervention families, or untouched outcome source.

`not_trigger`. The false proposition should be remembered as a mandatory policy-class check, but
the correction is directly occupied and the exact-oracle testing residue has no realistic statistical
advantage. No simulator-validity blocker is removed.

## 4. Screen C: learned mean-field representation and population transfer

### 4.1 Exact question

The native object is a population representation used to transfer a learned simulator or policy
across economically equivalent market populations. Rival explanations are:

- **H1 -- a learned empirical mean field is the native object:** encode each agent's state--action
  pair and average, so the learned dynamics become independent of raw agent count;
- **H2 -- the apparent invariance depends on an analyst-chosen population unit:** identity splitting,
  heterogeneous economic mass, major players, common noise, and interaction dependence alter the
  empirical law or invalidate the theorem.

The discriminating result is invariance under a declared weight-preserving agent refinement plus a
finite-population error bound for the actual dependent system, not an iid resampling bound.

### 4.2 What the new theorem and experiment actually cover

Makkar et al. assume a symmetric mean-field game in which one agent is negligible and reward and
transition depend on the population law only through

\[
m_h^\star=\mathbb E_{(x,a)\sim\nu_h}[f_h^\star(x,a)].
\]

Their offline theorem assumes a finite realizable candidate class, independent trajectory episodes,
and $K$ population samples at every episode-stage. The finite-snapshot term is proportional to

\[
\mathbb E\|\widehat m-m\|_2^2\le B_f^2/K.
\]

This is an iid empirical-mean error conditional on the population law. It is not a propagation-of-
chaos result for one finite population of interacting traders, not a common-noise result, and not a
bound for persistent identities observed along one market path. The empirical section explicitly
isolates representation learning in a one-step routing game with deterministic rewards; it does not
implement the confidence-set algorithm, learn transitions, or validate the stated finite-horizon
bound.

### 4.3 Agent splitting is not solved by unweighted mean pooling

For a realized $N$-agent snapshot, the proposed empirical representation is

\[
\widehat m_N=\frac1N\sum_{i=1}^N f(x_i,a_i).
\]

Splitting agent $j$ into two records with the same state--action label gives

\[
\widehat m_{N+1}
=\frac{\sum_{i\ne j}f(x_i,a_i)+2f(x_j,a_j)}{N+1},
\]

which generally differs from $\widehat m_N$. If the two records carry half the original order,
inventory, or capital, invariance still requires the feature map to respect that size decomposition.
A weighted empirical measure

\[
\widehat m_w=\frac{\sum_i w_i f(x_i,a_i)}{\sum_i w_i}
\]

is invariant only after a native conserved weight, its split rule, and feature homogeneity are
declared. Wallet, account, order, beneficial owner, and unit of capital are not interchangeable
market population units. Learning $f$ cannot identify that ontology from aggregate price paths.

The obvious relaxations are already separate mature parents. Major players and finite-agent
approximation are treated by [Major-Minor Mean Field MARL](https://proceedings.mlr.press/v235/cui24a.html);
population-dependent policies under aggregate shocks are treated by
[common-noise mean-field imitation learning](https://arxiv.org/abs/2605.03357);
mean embeddings of population distributions with non-asymptotic analysis appear in
[Wang, Yang, and Wang (2020)](https://proceedings.mlr.press/v119/wang20z.html); and robust
finite-population approximation under model mismatch appears in
[Wang (2026)](https://proceedings.mlr.press/v337/wang26i.html). Combining these components with
EcoMD is not an irreducible algorithmic contribution.

### 4.4 Decision

`not_trigger`. The new source is a useful direct parent for population-aware learning, but its
finite-$K$ result is not finite interacting-market transfer, its unweighted mean is not
agent-splitting invariant, and the market-native population measure is absent. No population-size,
unitization, external-truth, or two-system blocker is removed.

## 5. Joint verdict and exact re-entry conditions

All three sources improve the vocabulary for future work but do not create a qualified re-entry:

| screen | genuine new capability | fatal reduction or missing contract | decision |
|---|---|---|---|
| response-resolution design | calibrated candidate-set design under persistent nuisance | finite target is exact RAED relabelling; continuous target is GO-OED/confidence design; no legal market truth | `not_trigger` |
| policy-aware simulator validity | active strategic error search and critic bounds | key deterministic-to-randomized claim is false and its counterexample is already PVE Proposition 5; offline/field truth absent | `not_trigger` |
| learned mean-field representation | offline low-dimensional population encoding with an iid snapshot term | no split-invariant economic mass, dependent finite-population theorem, major/common-noise closure, or market truth | `not_trigger` |

A future trigger must satisfy one of the following, before a topic neighborhood is harvested:

1. a sequential response-resolution theorem with a lower bound that cannot be represented as RAED,
   goal-oriented design, sequential composite testing, or decision-theoretic design, plus a legal
   market action and untouched response source;
2. a noisy black-box policy-class equivalence test with a declared tolerant alternative, realistic
   access advantage, dimension-controlled sample complexity, and a matching lower bound beyond
   multiple-policy evaluation and MDP policy testing;
3. a weighted refinement-invariant population object with a market-observable economic unit and a
   finite dependent-particle/common-noise/major-player transfer theorem that is false for existing
   mean-field parents.

Until then, there is no machine card, no experiment plan, and no authority to connect to or schedule
the A800 or either V100 for these routes.
