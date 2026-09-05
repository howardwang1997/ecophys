# EcoMD hard-matching boundary-flux trigger audit

**Date:** 2026-09-05  
**Stage:** post-closure re-entry trigger screen  
**Archetype:** `simulator_method`  
**Decision:** `not_trigger`  
**Candidate harvesting:** not authorized  
**Outcome access, implementation, simulation, SSH, and GPU status:** none

## 1. Decision first

The proposed escape was to preserve an exact hard market-matching forward pass while estimating
the derivative of its **expected** loss by sampling the probability flux through price ties, queue
depletions and event-order boundaries. This is mathematically sound, and it corrects the usual
mistake of treating an almost-everywhere zero pathwise derivative as the derivative of an
expectation.

It is not a new method. The exact interior-plus-boundary identity, unbiased manifold sampling for
linear branch surfaces, conditional Monte Carlo reduction, probability-flow interpretation,
compositional differentiation of parametric discontinuities, and unbiased differentiation of
discrete probabilistic programs all have direct primary parents. In particular,
[Lee, Yu, and Yang (NeurIPS 2018)](https://papers.nips.cc/paper_files/paper/2018/hash/b096577e264d1ebd6b41041f392eec23-Abstract.html)
already turn exponentially many cells cut by `L` affine branches into `L` surface integrals, and
[Michel et al. (OOPSLA 2024)](https://doi.org/10.1145/3649843) provide a compositional language
and Monte Carlo evaluator for parametric discontinuities, including finite loops by unrolling.

Market structure therefore supplies an application and perhaps a compiler engineering challenge,
not an irreducible ICLR contribution. No theorem with a strict variance--cost advantage over the
named parents was derived. The current source also does not remove EcoMD's more basic semantic
problem: its core simulator produces aggregate price dynamics and does not implement an exact
individual-order price-time-priority market. The route remains closed and all three GPU workers
remain idle.

## 2. Frozen question contract

### Market-native object

Let a continuously distributed action/noise tape `U` and parameters `theta` determine a hard
matching trajectory: price ranking, time priority, queue depletion, fills, inventories and a scalar
downstream loss. The object is

\[
  J(\theta)=\mathbb E[L(M_\theta(U))],
\]

where `M` keeps the exact categorical matching rule rather than a softened allocation.

### Rival explanations

- **H1 -- exploitable market boundary structure.** Matching boundaries admit a local pivotal
  estimator that is unbiased and has a provable variance--cost advantage over score-function,
  conditional-Monte-Carlo, boundary-sampling and stochastic-AD estimators.
- **H0 -- established boundary calculus.** The proposed estimator is a market spelling of an
  interior pathwise term plus a classical moving-boundary/weak-derivative term; any speedup comes
  from ordinary conditioning, importance sampling, control variates or compiler specialization.

### Discriminating result

H1 would require an estimator theorem that is false for generic branch programs: exact
unbiasedness, reverse-mode scaling, and a non-asymptotic variance--work bound strictly better on a
declared matching class, together with a matching lower bound outside that class. A null result is
useful because it prevents a known boundary correction or domain-specific implementation from
being presented as an ICLR algorithm.

## 3. Exact boundary identity

Suppose the fixed-noise space is partitioned into regions `R_k(theta)` on which the loss has a smooth
representative `ell_k(theta,u)`, and let `S_kl(theta)` be an interface with normal `n_kl` and normal
velocity `v_kl`. Under the usual integrability and transversality conditions, Reynolds transport gives

\[
  \nabla_\theta J
  =\sum_k\int_{R_k(\theta)}\nabla_\theta(\ell_k q)\,du
   +\sum_{k<l}\int_{S_{kl}(\theta)}q(u)
      [\ell]_{kl}(u)\,v_{kl}(u)\!\cdot\! n_{kl}(u)\,dS(u).
\]

The first term is the ordinary within-regime pathwise derivative. The second is exactly the missing
probability flux: jump size times density times boundary speed. A measure-zero boundary can have a
nonzero first-order contribution because its `O(delta)` crossing probability multiplies an
`O(1)` loss jump.

For one monotone comparison, write `Z` for the other randomness and `E` for a scalar innovation
with conditional density `f(e|Z)`. If the two continuations are `a_theta(Z,E)` and
`b_theta(Z,E)` and the hard branch is `E <= tau_theta(Z)`, conditioning yields

\[
\begin{aligned}
\nabla_\theta J
=\mathbb E_Z\bigg[&\int_{-\infty}^{\tau_\theta}
       \nabla_\theta(a_\theta f)\,de
 +\int_{\tau_\theta}^{\infty}
       \nabla_\theta(b_\theta f)\,de\\
&+f(\tau_\theta\mid Z)
  \{a_\theta(Z,\tau_\theta)-b_\theta(Z,\tau_\theta)\}
  \nabla_\theta\tau_\theta(Z)\bigg].
\end{aligned}
\]

Thus a proposed "pivotal tie" estimator that forces the innovation to its critical value and runs
both continuations is not a new identity. It is conditional Monte Carlo/manifold sampling of the
surface term. Rewriting the comparison as a conditional Bernoulli primitive gives the same
reachable-state difference used by weak derivatives or stochastic AD.

## 4. Market toy exposes the missing term but not novelty

For a first-price bid `B_theta = theta + sigma E`, opponent maximum bid `C` with CDF `F` and
density `f`, and value `v`, the exact utility is

\[
  J(\theta)=\mathbb E[(v-B_\theta)\mathbf 1\{B_\theta>C\}].
\]

Its derivative contains

\[
  J'(\theta)=\mathbb E[-\mathbf 1\{B_\theta>C\}]
  +\mathbb E[(v-B_\theta)f(B_\theta)].
\]

Naive pathwise AD returns only the first term. The second is the tie-boundary flux. This is the same
failure highlighted for discrete auction allocation by
[Kohring, Pieroth, and Bichler (ICML 2023)](https://proceedings.mlr.press/v202/kohring23a.html),
although that work chooses a biased smooth-market objective and bounds its utility error rather
than estimating the exact boundary term.

The formula is a clean unit test for any future implementation. It is not itself a new theorem.

## 5. Direct collision map

| Primary work | Occupied object | Consequence |
|---|---|---|
| [Lee, Yu, and Yang 2018](https://papers.nips.cc/paper_files/paper/2018/hash/b096577e264d1ebd6b41041f392eec23-Abstract.html) | Unbiased reparameterization gradient for piecewise-smooth programs: interior term plus manifold-sampled boundary term; affine branch partitions cost linear rather than exponential in branch count | Owns the proposed boundary-flux identity and the obvious affine matching implementation. |
| [Feng and Liu 2016](https://arxiv.org/abs/1603.06378) | Change-of-variables conditional Monte Carlo for sensitivities of discontinuous integrands, including maxima, finance and chance constraints | Owns threshold conditioning and critical-value sampling as a variance-reduction principle. |
| [Parmas and Sugiyama 2021](https://proceedings.mlr.press/v130/parmas21a.html) | Probability-mass-flow unification of LR and RP; supplementary theory explicitly adds jump-surface corrections and importance sampling on the surface | A new "probability flux" interpretation or learned surface proposal is not empty territory. |
| [Michel et al. 2024](https://doi.org/10.1145/3649843) | Potto: compositional semantics, separate compilation and Monte Carlo evaluation for parametric discontinuities; finite loops are unrolled | Owns the general differentiable-language/compiler claim and supports nonlinear boundaries through declared diffeomorphisms. |
| [Arya et al. 2022](https://proceedings.neurips.cc/paper_files/paper/2022/hash/43d8e5fc816c692f342493331d5e98fc-Abstract-Conference.html) and [ADEV](https://doi.org/10.1145/3571198) | Unbiased derivatives of expectations for discrete/mixed probabilistic programs, auxiliary continuations and compositional estimator choices | Recasting a threshold as a probabilistic branch or evaluating an alternative path returns to established stochastic AD. |
| [Chen et al. 2026](https://arxiv.org/abs/2602.12590) | ICLR application of synthesized weak derivatives to exact-forward discontinuous event binning | Applying weak-derivative backpropagation to market event bins is a direct domain transfer, not a fresh primitive. |
| [Kohring et al. 2023](https://proceedings.mlr.press/v202/kohring23a.html) | Smooth-market gradients, bias bounds and equilibrium transfer for auctions with indivisible allocation | Owns the immediate market-learning baseline and requires any exact method to beat a strong domain comparator. |

## 6. Why the remaining automation gap is not enough

There is a real software gap between the parents. Lee et al. restrict their efficient construction to
loop-free affine conditions. Potto requires a finite unrolled loop and an invertible boundary map
supplied outside its core language. StochasticAD explicitly leaves automatic handling of
continuous-to-discrete comparisons and comparison-driven while loops to future work. A market
engine has dynamic order counts, data-dependent loops, mutable queues and discontinuous
continuations.

But "instrument a matching engine and implement these known terms" is not yet a scientific
contribution. The obvious implementation choices are all inherited:

1. enumerate or importance-sample comparison surfaces as in Lee/Potto;
2. analytically condition a pivot innovation as in conditional Monte Carlo;
3. encode the comparison as a Bernoulli and use score, enumeration or stochastic derivatives; or
4. smooth the branch and accept a declared bias as in smooth markets and DiscoGrad-style methods.

Dynamic tracing, custom CUDA kernels or an EcoMD benchmark could make those methods usable but
would not prove a new estimator. Automatic inversion of arbitrary nonlinear dynamic conditions is
also a much broader program-analysis problem, not a market-native scientific residual.

## 7. EcoMD transfer and feasibility

The current EcoMD package does not expose the object required by this candidate. Its core dynamics
are fixed-step latent-agent/Langevin updates with aggregate price formation. The L2 adapters emit
synthetic aggregate queues and IDs; they are not an individual-order matching engine with
persistent ownership, exact price-time priority and legal counterfactual actions. The separate lab
reference engine is a protocol fixture, not an established EcoMD simulator lineage.

Consequently, experiments would first require changing the scientific object and building a new
hard-event simulator. Even perfect analytic gradients on that new engine would validate an
algorithmic implementation against synthetic truth, not identify a real market intervention. This
fails both transfer and cost-of-next-update gates before GPU value is considered.

## 8. Gate decision

| Gate | Result |
|---|---|
| Exact expected gradient exists despite hard forward rule | Pass under density, integrability and transversality assumptions |
| Boundary-flux identity is new | Fail: Lee 2018, conditional Monte Carlo and mass-flow theory are direct parents |
| Compositional parametric-discontinuity AD is new | Fail: Potto/Teg directly occupy it |
| Discrete alternative-path correction is new | Fail: stochastic AD, ADEV and weak derivatives occupy it |
| Market specialization has a strict variance--cost theorem | Fail: none derived |
| Current EcoMD supplies exact hard matching semantics | Fail |
| Two independent same-estimand truth systems exist | Fail |
| A recorded blocker is removed | Fail |

**Decision:** `not_trigger`, `removed_blockers: []`, and
`candidate_harvest_authorized: false`. This strengthens the existing
`conservative_differentiable_transaction_integrator` closure rather than creating a new route node.

Re-entry requires all of the following before implementation:

1. a precisely declared dynamic matching-program class not already handled by finite unrolling or
   an explicit probabilistic-branch rewrite;
2. an exact reverse-mode estimator with a proved non-asymptotic variance--work advantage over
   boundary sampling, conditional Monte Carlo, LR/control-variate, StochasticAD/ADEV and common-
   random finite differences;
3. a matching lower bound or hard regime showing why that advantage is structural rather than an
   implementation constant;
4. analytic or gold-standard gradient truth on two independent non-EcoMD systems; and
5. a market-native action/response contract preserved by a real hard-matching EcoMD extension.

Without such a theorem sketch, no code, benchmark, SSH session or GPU job is justified.
