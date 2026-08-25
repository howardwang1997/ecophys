# EcoMD market-physics problem reselection: G-1 result

**Frozen:** 2026-08-25
**Scope:** simulated markets, many-body and non-equilibrium market physics, and a real L3 observation bridge
**Outcome access:** none
**Decision:** no new active route; the sole paper-only D-1 watchlist subsequently failed

## 1. Decision

The source-conditioned agent-prediction reserve is superseded by the user's narrower scientific scope. Agent
program text is neither a physical market state nor a defensible molecular-dynamics analogue. This decision does
not claim that program-conditioned prediction is mathematically impossible; it removes it from the EcoMD market-
physics program.

No newly screened market-physics route crossed the frozen 15% hostile T0 activation floor. The least-bad residual
was `trajectory_space_liquidity_dpt`: ask whether a genuine price-time-priority limit order book has an active--
inactive transition in trajectory space that is either present in the unbiased dynamics or induced by one
implementable market rule. It was parked at D-1 for theorem work only. The same-day theorem audit failed both
branches before simulation; see
`papers/proposal/trajectory_space_liquidity_dpt_dminus1_result_2026-08-25.md`.

| Route | Hostile T0 | Complete Nature Computational Science | Decision |
|---|---:|---:|---|
| trajectory-space liquidity transition | 6--10% initially; 0--2% after D-1 | 1--3% initially; below 0.5% after D-1 | failed-closed |
| finite-Knudsen particle--continuum LOB | 3--7% | 1--3% | failed-closed |
| finite-noise liquidity nucleus | 3--6% | 0.5--1.5% | failed-closed |
| glass/aging, ordinary FSS, FDT/entropy | 1--6% | below 2% | already closed or exact KG isomorphism |
| invariant-measure calibration | not reopened | not reopened | failed G0 on 2026-08-10 |

These probabilities are planning judgements before outcomes, not posterior claims about a completed experiment.

## 2. Selected D-1 question and subsequent closure

For a sequence of market generators (L_N(u)), define best-quote activity and signed price current

\[
K_T=\sum_{0<t\le T}\mathbf 1\{\text{event changes a best queue or spread}\},
\qquad J_T=P_T-P_0,
\]

and the scaled cumulant generating function

\[
\psi_N(s,r;u)=\lim_{T\to\infty}T^{-1}
\log \mathbb E_u\exp[-sK_T+rJ_T].
\]

A publishable physical result requires a non-analytic limiting (psi), an activity/current discontinuity, a
closing tilted-generator spectral gap, and a defined order of the (N\to\infty) and (T\to\infty) limits. A
bimodal histogram, large finite-sample susceptibility, or a transition at an arbitrarily chosen bias (s\ne0)
does not qualify.

The D-1 theorem had to establish one of two statements:

1. a transition occurs at the unbiased physical dynamics (s=0) in an open parameter region of a genuine
   price-time-priority LOB; or
2. the Doob-driven process is exactly equivalent to one scalar, implementable and cross-engine market rule.

The second option was deliberately difficult. For a jump observable (g(x,y)), the driven rate is

\[
W_s^{\mathrm{Doob}}(x,y)=W(x,y)e^{-s g(x,y)}\frac{h_s(y)}{h_s(x)}.
\]

The eigenfunction ratio is generally full-state dependent. Calling it a cancellation fee, throttle, latency or
other scalar rule without proving equality is forbidden. The completed audit found that an unbiased cusp requires
multiple zero-cost activity phases, while natural scalar rules fail a graph-cycle or constant-escape condition.
The sole exact exception is state-independent uniform clock rescaling, which changes neither the embedded jump
chain nor its stationary law and therefore does not qualify.

## 3. D-1 kill tests

The route closes before any simulator run if any of the following holds:

1. No price-time-priority model has an (s=0) transition, and no one-parameter market rule implements the Doob
   rates exactly.
2. The apparent transition is induced by the selected observable. Non-interacting systems can exhibit a
   trajectory-space transition for a chosen activity, so non-analyticity alone does not establish many-body
   market coordination.
3. The result exists only at fixed finite (N). An irreducible finite-state continuous-time Markov chain normally
   has an analytic principal eigenvalue; finite-size crossover is not a thermodynamic singularity.
4. A slow mixture of ordinary market regimes reproduces bimodality and susceptibility without a single
   time-homogeneous generator or spectral singularity.
5. Two independently maintained engines cannot expose complete forkable state, pending events, agent state and
   RNG lineage without sharing the same imported agent dynamics.
6. Real L3 data are used to claim the response of an (s\ne0) driven process. Passive L3 observes only the natural
   (s=0) process and cannot identify that intervention.

The direct method family is mature: thermodynamic formalism, cloning, tilted generators, Doob transforms,
optimal control and Lee--Yang diagnostics are not contributions. Relevant primary precedents include
[Lecomte et al.](https://arxiv.org/abs/cond-mat/0606211),
[Chetrite and Touchette](https://arxiv.org/abs/1405.5157), and
[Vasiloiu et al.](https://doi.org/10.1103/PhysRevE.101.042115). Market-side phase and large-deviation precedents
include [Lux and Marchesi](https://doi.org/10.1038/17290),
[Rojas et al.](https://arxiv.org/abs/2004.10632), and
[Tóth et al.](https://doi.org/10.1103/PhysRevX.1.021006).

## 4. Why finite-Knudsen was closed

The attractive MD analogy was to represent individual orders as particles, approximate high-occupancy regions by
a continuum field, and return to exact jumps near queue depletion. The narrow estimand would have been the signed
depletion probability

\[
p_N^\sigma(x,T)=\Pr_x\{\tau_N\le T,
\text{ first depleted side}=\sigma\},
\qquad \tau_N=\inf\{t:Q_b^N(t)Q_a^N(t)=0\}.
\]

It failed G-1 for four independent reasons.

- [Yura et al.](https://doi.org/10.1103/PhysRevE.92.042811) already introduced the financial Knudsen number and
  connected high Kn, discrete order effects, asymmetric depletion and violent price motion.
- LOB diffusion/SPDE limits already connect microscopic, mesoscopic and macroscopic states; examples include
  [Horst and Kreher](https://doi.org/10.1016/j.spa.2018.11.023) and
  [Hambly, Kalsi and Newbury](https://arxiv.org/abs/1808.07107).
- Adaptive kinetic--fluid and jump--diffusion methods already switch back to discrete dynamics at low occupancy
  and boundaries, with error analysis. Examples include
  [Duncan, Erban and Zygalakis](https://doi.org/10.1016/j.jcp.2016.08.034) and
  [Filbet and Xiong](https://doi.org/10.1016/j.jcp.2018.06.064).
- A scalar Knudsen number cannot certify a first-passage law. Two books may share best depth, local flow rates and
  Kn while a hidden cancellation state makes their finite-horizon depletion probabilities differ by order one.
  Passing the full kinetic state avoids this non-identification but reduces the proposal to a generic hybrid
  solver transplant.

Uniform path convergence also does not by itself imply hitting-law convergence: (x_n(t)=1/n\to0) uniformly,
yet (x_n) never reaches the absorbing set ((-infty,0]) while the limiting path does at time zero. A genuinely
new market-boundary correction remained imaginable but had only 3--7% T0 survival and no verified common scaling
family in two independent engines. It is therefore failed-closed, not retained as a candidate.

## 5. Why the liquidity-nucleus route was closed

The proposed intervention held visible depth, spread, instantaneous OFI and total removed volume fixed while
rearranging order age, splitting or owner inventory, then compared crash committors. An order-one effect would
only prove that the visible projection is not committor-sufficient, reproducing the closed observation-quotient
problem.

Two minimal counterexamples are decisive.

1. In an exchangeable memoryless queue-reactive model, age and owner relabelling exactly preserve the committor.
   Adding TTL, age-dependent cancellation or inventory-triggered withdrawal writes the effect into the agent rule;
   it does not establish an emergent critical nucleus.
2. The same quantity at one level may be one large order or many unit orders. A per-order cancellation clock gives
   different depletion risk, while a per-share clock removes it. The alleged nucleus therefore changes under an
   arbitrary order-unit convention.

Transition-path theory already supplies committors and reactive currents for Markov jump processes
([Metzner, Schütte and Vanden-Eijnden](https://doi.org/10.1137/070699500)); queue-state first-passage probabilities
are established for LOBs ([Cont, Stoikov and Talreja](https://doi.org/10.1287/opre.1090.0780)). ABIDES, PAMS and
Bourse also lack a documented bit-complete common branch-state contract, while real L3 omits private inventory and
pending agent actions. The route is failed-closed unless a future theorem is invariant to order unitization,
defines a nontrivial nucleus scaling law, and avoids hidden owner state.

## 6. Simulator and observation contracts

The usable simulator pool is:

- [ABIDES](https://github.com/jpmorganchase/abides-jpmc-public), pinned to `f9cbe513`, BSD-3; rich event and agent
  semantics, but archived and without a documented complete branch checkpoint;
- [PAMS 0.2.2](https://github.com/masanorihirano/pams), pinned to `28cbb861`, EPL-1.0; use only the sequential
  runner because parallel logging order is not deterministic;
- [Bourse 0.4.0](https://github.com/zombie-einstein/bourse), pinned to `17285fde`, MIT; independent lightweight
  matching countercheck, but book serialization omits the whole agent/RNG/event state.

BSE is a zero-latency, unit-order negative control. SHIFT lacks an open server and clear repository licence;
JAX-LOB lacks a licence and release tags. Neither enters a publication contract.

The common observable floor is ordered add/cancel/execute events, reliable event indices and timestamps, and ten
levels of bid/ask depth. Real agent count is not observable, so simulated agent count cannot be presented as an
empirical system-size axis. L3 can validate only frozen (s=0) activity/current and hazard signatures.

## 7. Closure

The companion paper audit could not obtain a market-specific (s=0) theorem or a nontrivial exact one-rule Doob
equivalence, so the watchlist is failed-closed. Do not implement cloning, buy data, alter EcoMD, run
ABIDES/PAMS/Bourse, inspect outcomes or use GPU under this formulation. Combining finite-Knudsen, a committor and
an s-ensemble does not raise the probability and remains expressly disallowed.
