# EcoMD boundary-memory, diffusive-flow, Epps, and smoothing trigger audit

**Date:** 2026-09-05  
**Scope:** four bounded route-graph, theorem, identification, source-contract, and direct-parent screens  
**Archetypes:** `theory_mechanism`, `measurement_method`, `measurement_method`, `simulator_method`  
**Decisions:** four `not_trigger`  
**Candidate harvesting:** not authorized  
**Outcome access, implementation, simulation, SSH, and GPU work:** not authorized

## 1. Executive decision

| Screen | Attractive claim | Decisive result | Decision |
|---|---|---|---|
| Retained hidden excess at price limits | Recover a censored pressure state and learn its retention from several exchange bands | Three pooled bands and the 20% lower side exceed the paper's own symmetric-iid persistence ceiling; passive clipped paths have an exact no-retention/persistent-driver twin; band assignment is endogenous | `not_trigger` |
| LMF nonlinear impact and diffusion | Distinguish permanent square-root metaorder impact from a zero-permanent transient propagator | The new source owns the positive theorem; the fork needs real parent-metaorder truth, while `tse_tick` is only a parser for commercial anonymous TSE rows | `not_trigger` |
| Coupled-book Epps decomposition | Separate asynchronous observation clocks from finite cross-book response | The exact paper and question were already screened in cycles 2 and 10; its factorization is leading-order and the same price-law kernel has non-pair-trader latent-information twins | `not_trigger` |
| Rough-target execution smoothing | Turn hard EcoMD actions into smooth controls with a sharp, roughness-adaptive bias certificate | The source already owns the sharp value-rate theorem and its execution application; value convergence does not certify gradients or event semantics, whose obvious smoothing repairs have direct ICML parents | `not_trigger` |

No screen removes a recorded blocker or leaves an irreducible ICLR contribution. This is a
successful kill round, not evidence that a larger simulation or a GPU sweep is needed.

## 2. Screen A: retained hidden excess at price limits

### 2.1 Exact question

The native object is the latent pressure beyond a daily price band and its contribution to the
next trading day. The rival explanations concern the same observed limit-close histories:

- **H1 -- retained overshoot:** clipping creates an unobserved excess and a fixed fraction survives
  to the next day, while fresh shocks are iid;
- **H0 -- persistent forcing or adaptation:** there is no stored overshoot; serially dependent news,
  order flow, liquidation, strategic adaptation, or selection into surveillance bands generates the
  same observed continuation.

A discriminating result must identify retained excess against H0 under the same stock, band rule,
pre-state, observation clock, and next-day response. A positive result would support a real latent
state for a constrained market simulator. A null result would reject the state and still delimit
when censored-state learning is scientifically invalid.

### 2.2 What the source establishes

[Das (2026)](https://arxiv.org/abs/2608.08625) defines

\[
R_t=\operatorname{clip}(X_t,-C,C),\qquad
L_t=X_t-R_t,\qquad
X_{t+1}=\epsilon_{t+1}+\lambda L_t,
\]

where the shocks are iid, symmetric and regularly varying with index \(\nu>1\). The stationary
latent tail retains index \(\nu\) and multiplies its amplitude by
\((1-\lambda^\nu)^{-1}\). In the wide-band, single-dominant-shock limit, the next-day same-sign
mean is proportional to \(C\), same-limit persistence has a nonzero limit, and opposite-limit
reversal is of order \(C^{-\nu}\).

For persistence, let

\[
B_j=\sum_{m=0}^{j}\lambda^{-m},\qquad
\mathcal Z(\lambda,\nu)=\sum_{j\geq 0}B_j^{-\nu}.
\]

Then the paper derives

\[
Q(\lambda,\nu)=\lim_{C\to\infty}P_{++}(C)
=1-\frac{1}{\mathcal Z(\lambda,\nu)}.
\]

As \(\lambda\uparrow1\), \(\mathcal Z\to\zeta(\nu)\), so with the empirical benchmark
\(\nu=3\), every admissible \(\lambda<1\) satisfies

\[
Q(\lambda,3)<Q_{\max}(3)=1-\frac{1}{\zeta(3)}\simeq0.1681.
\]

The paper's NSE table reports:

| Band | Upper persistence | Lower persistence | Pooled persistence | Relation to 0.1681 ceiling |
|---:|---:|---:|---:|---|
| 2% | 0.7470 | 0.8125 | 0.7885 | impossible under the asymptotic symmetric-iid model |
| 5% | 0.4630 | 0.4282 | 0.4478 | impossible |
| 10% | 0.2510 | 0.3082 | 0.2674 | impossible |
| 20% | 0.1325 | 0.2045 | 0.1452 | pooled value feasible, lower direction impossible |

The narrow bands need not be in the wide-band regime, so their ceiling violations do not refute the
finite-\(C\) recursion by themselves. They do refute using the paper's asymptotic persistence map
to estimate one structural \(\lambda\) across those bands. The 20% lower-direction violation is
more serious, and the paper itself says that one effective \(\lambda\) does not reproduce the full
band and directional dependence. Its estimate \(217/1494\) at 20% is consequently an effective
pooled calibration, not identification of retained demand.

### 2.3 Exact passive-law nonidentification

Let \(\{R_t\}\) have any observed law supported on \([-C,C]\), including all limit-close and
next-day statistics above. Construct a no-retention model by taking

\[
\lambda'=0,\qquad X'_t=R_t,\qquad \epsilon'_t=R_t.
\]

Then \(R'_t=\operatorname{clip}(X'_t,-C,C)=R_t\) pathwise and \(L'_t=0\). The driver
\(\epsilon'_t\) is generally serially dependent, which is exactly H0. Therefore the iid innovation
restriction, not the clipped observations, separates retained overshoot from persistent forcing.
No statistic of the passive daily return path can test which semantic latent generated it.

This witness does not say the retained-excess model is useless. It says its mechanism claim needs
an independent innovation restriction, a pressure proxy, or a legal exogenous threshold
intervention. Merely fitting a recurrent latent model, a neural filter, or EcoMD chooses one member
of the observational equivalence class.

### 2.4 The band is not an exogenous instrument

The official [NSE price-band page](https://www.nseindia.com/static/regulations/daily-price-bands-reports)
states that downward revision occurs daily, upward revision bi-monthly, and both are conditional on
objective criteria. The official [ASM page](https://www.nseindia.com/static/regulations/additional-surveillance-measure)
links surveillance and band reductions to high-low and close-close variation, volume, volatility,
client concentration, market capitalization, delivery share, unique PANs, and valuation. Dynamic
bands can also flex intraday. These variables also predict persistence, liquidity, order flow, and
news response. Pooling 2%, 5%, 10%, and 20% events therefore does not create randomized variation
in \(C\).

Even with a valid external band change, generic identification is occupied. Dynamic Tobit models
already treat serial censored processes with non-Gaussian and time-varying scale, while
[Zhang and Guo (2023)](https://arxiv.org/abs/2207.02422) give adaptive identification,
asymptotic normality, and finite-sample error bounds for stochastic systems under possibly varying
saturation and correlated, nonstationary feedback signals. A new EcoMD result would need a
market-native partial-identification or intervention theorem beyond these parents, not a new
neural censored-state estimator.

### 2.5 Decision and re-entry condition

`not_trigger`. The source adds a valuable falsifiable ceiling and makes the old
`constraint_release_intent_overshoot` failure more precise, but it supplies neither exogenous band
assignment nor an observed excess state. Re-enter only with a prospectively assigned, unbundled
threshold change on the same securities; complete submitted and rejected attempts; a predeclared
innovation/adaptation control; untouched confirmation; and a theorem that identifies or sharply
bounds a retained-state functional beyond dynamic Tobit and saturated-system identification.

## 3. Screen B: nonlinear LMF impact and the diffusion paradox

### 3.1 Exact question

The native object is the long-horizon variance growth generated by labeled parent-metaorder
executions. The source names a real model fork:

- **H1 -- nonzero permanent nonlinear impact:** LMF order splitting with cumulative metaorder
  impact \(I(Q)\propto Q^\delta\) produces diffusion for all long-memory exponents when
  \(\delta\leq1/2\);
- **H0 -- zero-permanent transient propagator:** metaorder correlations and power-law impact decay
  obey a compensating relationship that also produces diffusion.

Both a positive and a null result matter, but only if impact, decay, parent boundaries, child
schedules, flow-memory exponents, and variance growth are estimated on the same economic unit.

### 3.2 What is already owned

[Sato, Fujiwara, and Kanazawa (2026)](https://arxiv.org/abs/2608.00988) embed nonlinear
metaorder impact in the Lillo--Mike--Farmer process and map it to a nonlinear Levy walk. Within
their model class they prove that \(\delta\leq1/2\) is necessary and sufficient for normal diffusion
for every long-range-correlation exponent \(\gamma\in(0,1)\). They extend the calculation to
multiple splitters, resting periods, and post-metaorder decay with a nonzero permanent component.
They explicitly contrast this with a zero-permanent, power-law-decay theory and call for a
microscopic-data test.

That theorem and debate are scientifically strong. They are also the source's contribution, so an
EcoMD implementation or synthetic phase diagram is a programmed-mechanism reproduction.
The unresolved empirical fork inherits the repository's exact
`metaorder_memory_origin_discriminator` gate: anonymous public trades do not reveal true parent
boundaries or whether their long memory came from splitting, reactive flow, or a latent event
process.

### 3.3 `tse_tick` is not the missing truth asset

[Li et al. (2026)](https://arxiv.org/abs/2608.23053) release a useful parser and query layer for
Nikkei NEEDS TSE archives. The pinned [MIT repository](https://github.com/tse-tick/tse_tick/tree/01d74d8e283a3e4d2774f277b1ff22c6234c5359)
handles era-dependent layouts, 95-column individual-stock ticks, quotes, and a Parquet store. Its
README is explicit that it supplies no data: users need an institutional Nikkei NEEDS subscription
and raw archives. Neither the paper nor schema advertises beneficial-owner, participant, or true
parent-metaorder links.

Thus the library lowers parsing cost but changes none of the relevant information set. It is not an
open truth asset under the public/open-data authorization, and a commercial anonymous TSE tape
would still fail the parent-label gate.

### 3.4 Decision and re-entry condition

`not_trigger`. Re-enter only with lawful, prospectively frozen parent-metaorder or participant
labels that expose peak and permanent impact, post-completion decay, child schedules, order-flow
memory, and long-horizon variance on the same units, plus an independent replication and an
irreducible residual beyond the 2026 theorem. A larger LMF simulation, anonymous reconstruction,
or installing `tse_tick` is not a trigger.

## 4. Screen C: coupled-book Epps decomposition

### 4.1 Exact question and duplicate gate

The native response is equal-window cross-asset return correlation as aggregation time changes.
The rivals are asynchronous observation, finite economic transmission, and their combination.
[Angstmann and Gebbie (2026)](https://arxiv.org/abs/2606.14182) derives a reaction--diffusion
order-book coupling and separates an observation-clock overlap factor from an exponential
coupling-response factor.

This exact primary source was already cited in repository cycle 2, and cycle 10 explicitly screened
`epps_effect_mechanism_discriminator` before pruning it as mature. It is therefore not a
post-closure trigger, irrespective of the paper's recency relative to the current date.

### 4.2 Why the decomposition is not mechanism identification

In the coupling-only reduction the paper obtains

\[
\rho_{\Delta}^{\rm coup}\simeq \rho_\infty
\left[1-\frac{1-e^{-\kappa\Delta}}{\kappa\Delta}\right].
\]

With clock overlap \(\mathcal A_{12}(\Delta)\), the combined expression is

\[
\rho_{\Delta}^{\rm comb}\simeq \rho_\infty\mathcal A_{12}(\Delta)
\left[1-\frac{1-e^{-\kappa\Delta}}{\kappa\Delta}\right].
\]

The source correctly labels this a leading-order separability approximation, assumes clocks are
exogenous to innovations and local coupling response, and states that similar Epps envelopes can
have different sources. An observed correlation curve alone does not uniquely factor into
\(\mathcal A_{12}\) and a response kernel. Moreover, any bivariate reduced price process with the
same exponential cross-covariance kernel reproduces the complete Gaussian price law without a
pair-trader or reaction front. Calling that kernel common-information diffusion, lead--lag response,
or book coupling changes the latent mechanism but not the observed second-order law.

Timestamp randomization and refresh thinning can measure estimator/clock attenuation under a
frozen latent path. They do not identify the economic source of the residual response. This is
consistent with the established [alternative-sampling study](https://arxiv.org/abs/2011.11281),
which already compares calendar, trade, and volume time using a Hawkes benchmark.

### 4.3 Decision and re-entry condition

`not_trigger`. Re-enter only for a legal state-preserving intervention that changes cross-book
coupling while holding common news, routing, inventory, clocks, and observation fixed; complete
synchronized event state; two independently governed systems; and a response restriction that
cannot be represented by a latent multivariate diffusion, Hawkes/lead--lag kernel, or clock overlap.
Fitting the factorized Epps curve or programming pair traders in EcoMD is not external evidence.

## 5. Screen D: stochastic tracking as hard-event smoothing

### 5.1 Exact question

The native object is the cost and policy error introduced by replacing a jump/block execution
target or hard simulator action with an absolutely continuous control. The attractive proposal is
to choose the smoothing coefficient from target roughness and obtain a certified differentiable
EcoMD policy. The rival explanations are:

- the same roughness modulus controls decision value, policy distance, pathwise gradient bias, and
  hard-event constraint error; or
- value approximation can converge sharply while policies, event identities, stopping times, and
  pathwise gradients remain unstable or semantically different.

### 5.2 Direct theorem and value/gradient gap

[Nutz and Voss (2026)](https://arxiv.org/abs/2608.29468) analyze quadratic tracking of a
general stochastic target under an absolutely continuous control penalty \(\kappa\). Their bounds
are controlled by an \(L^2\) time-translation/Besov modulus. They obtain the sharp
\(O(\sqrt{\kappa})\) value rate for square-integrable cadlag semimartingales, more general
roughness-dependent rates, matching lower bounds in benchmark classes, and an optimal-execution
application that smooths jump or block strategies.

This already owns the broad theorem and the market application. It controls an objective-value
gap under its Hilbert-space problem; it does not imply convergence of policy derivatives,
allocation identities, queue priority, event time, constraint violations, or gradients through a
different simulator. Near a hard boundary, arbitrarily small value gaps can coexist with different
active sets or discrete actions.

The obvious ICLR repair is also crowded. [Adaptive Barrier Smoothing](https://proceedings.mlr.press/v202/zhang23s.html)
already derives gradient bias/variance bounds and convergence for softened complementarity
dynamics, while [Suh et al. (2022)](https://proceedings.mlr.press/v162/suh22b.html) analyze
stiffness/discontinuity-induced pathwise-gradient failure and introduce mixed-order estimators.
Porting roughness-tuned smoothing to EcoMD without a new event-semantic theorem is an application,
not an irreducible method.

### 5.3 Decision and re-entry condition

`not_trigger`. Re-enter only with a prospectively written theorem for stochastic, event-driven
market controls that simultaneously gives a sharp decision-value rate, policy or active-set error,
constraint/event-time error, and expected-gradient error; has a matching lower bound; survives a
forward-equivalent representation change; and is not reducible to tracking regularization,
barrier smoothing, mixed-order policy gradients, or standard nonsmooth optimization. It would
still need two exact truth systems and a market-native action bridge before EcoMD/GPU work.

## 6. Joint machine decision

All four formulations map to already failed-closed route families; no duplicate graph node is
created. None removes a recorded blocker, so no topic card, sandbox authorization, experiment
plan, or worker manifest may be opened. The A800 at `100.113.230.38` and V100 workers at
`100.80.236.112` and `100.123.220.57` remain idle for these routes.

The next exploration should not rename these four families. It should begin from a new truth or
control asset that exposes one previously missing semantic object: a valid assigned intervention,
authoritative parent/action labels, complete branchable hard-event state, or an independent
same-estimand confirmation system. Only after such an object passes the append-only re-entry gate
should a new question program or GPU plan be written.
