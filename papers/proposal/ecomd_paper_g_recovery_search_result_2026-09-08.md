# Paper G: exact learning cost of unknown restoration channels

**Disposition: close this reduced two-channel formulation as an independent Paper G
novelty claim; retain the exact minimax benchmark.** Unknown action-dependent
restoration can cause unavoidable learner-versus-informed-policy regret. The
effect in this model is exactly a first-success search / truncated stochastic
shortest-path problem, with no demonstrated market-specific residual. This closes
the present reduced formulation, not all inventory-dependent credit mechanisms.

Evidence consists of the proof below and deterministic synthetic development
checks under the [frozen contract](ecomd_paper_g_recovery_search_contract_2026-09-08.md).
There is no field calibration, independent confirmation, candidate card, full F3
review, novelty forecast or Paper E/F dependency. The earlier M0 closure remains
historical; the v3 imitation and known-exogenous-access results remain valid under
their own contracts.

## 1. The unresolved distinction and the declared model

The preceding access-gate result distinguished a large economic loss from lack of
access from a learning loss against an informed policy facing the same access
process. This audit resolves the latter question in the following reduced model.

At the start of each of T rounds, the observed state is suspended S or eligible E.
Initially it is S. A suspended decision selects one channel a in {A,B}. In unknown
world theta in {A,B}, success probability is

\[
p_\theta(a)=\begin{cases}\lambda(1+\alpha),&a=\theta,\\
\lambda(1-\alpha),&a\ne\theta.\end{cases}
\]

Lambda and alpha are known, with lambda>=0, 0<=alpha<1 and lambda(1+alpha)<1;
only the identity of the better channel is unknown. Each draw is conditionally
independent. Successful restoration occurs at the **end** of the round, after which
E is absorbing. Reward is zero in S and a known Delta>=0 per round in E. One
attempt per round, switching without cost, no resets, no informative auxiliary
signal and no unchosen-channel feedback are part of the model contract.

The informed comparator knows theta, starts suspended, and has exactly the same
feasible actions and timing. It always chooses the higher-success channel. If tau
is the round of first success, both policies receive Delta*(T-min(tau,T)). Regret
therefore measures additional waiting caused by uncertainty, excluding suspension
loss already suffered by the informed comparator.

This model does **not** implement the previous inventory dealer or an actual
collateral-remediation protocol. Appending a separable customer process with an
independent feasible optimum adds a common reward term and cannot create a new
market mechanism. Inventory, shared collateral and endogenous feedback require
their own complete coupled model; no lower-bound embedding in that model is
claimed here.

## 2. Exact finite-horizon minimax theorem

Let u=1-lambda(1+alpha), v=1-lambda(1-alpha), and define

\[
 S_{2m}=(uv)^m,\qquad S_{2m+1}=\frac{u+v}{2}(uv)^m.
\]

For every integer T>=0, the minimax expected regret over the two worlds is

\[
\boxed{R_T^*=\inf_\pi\max_\theta\{V_T^{*,\theta}-V_T^{\pi,\theta}\}
=\Delta\sum_{n=0}^{T-1}(S_n-u^n).}
\]

It is attained by choosing the initial channel uniformly and then alternating
channels after each failure. This is an exact all-policy statement, not a comparison
between selected learning algorithms. It also shows that a complex learner is
unnecessary for this particular two-world uncertainty set.

**Proof.** Until success, the only observation is another failure. Fix a
deterministic policy: its nonterminal branch is a sequence of channels. If its
first n choices contain a uses of A and b=n-a uses of B, the equal-prior survival
probability is

\[
\frac{u^a v^b+v^a u^b}{2}
=(uv)^{n/2}\cosh\!\left(\frac{a-b}{2}\log\frac uv\right).
\]

This is minimized by |a-b|<=1. Alternating choices achieve that minimum
simultaneously for every prefix, giving S_n above. Expected suspended rounds
equal the survival sum from n=0 to T-1, so the alternating sequence is Bayes
optimal under the equal prior. Arbitrary private randomization gives mixtures of
deterministic failure-branch sequences; it cannot improve this Bayes minimum.
An auxiliary process whose conditional law contains no information about theta
provides at most such randomization under the declared separable contract.

The informed comparator has survival u^n in either world. Thus the displayed
formula is an equal-prior Bayes lower bound on minimax regret. An equal mixture
of the two alternating sequences swaps the two world risks and makes them equal;
each equals that lower bound. It therefore attains the minimax value. QED.

For numerical evaluation let M=floor(T/2) and z=uv. Then

\[
\sum_{n=0}^{T-1}S_n=(2-\lambda)\frac{1-z^M}{1-z}
 +\mathbf1_{T\text{ odd}}z^M,
\qquad \sum_{n=0}^{T-1}u^n=\frac{1-u^T}{1-u}.
\]

At lambda=0 use the continuous finite-horizon value T for each wait; regret is
zero. Alpha=0 also gives zero regret. T=1 has no rewarded restoration opportunity;
T=2 gives R_2*=Delta*lambda*alpha, confirming the event timing analytically.

## 3. Slow restoration has two different limiting regimes

For a **fixed** lambda>0, total regret converges to a finite constant:

\[
R_\infty^*=\Delta\left[
\frac{2-\lambda}{2\lambda-\lambda^2(1-\alpha^2)}
-\frac1{\lambda(1+\alpha)}\right].
\]

By contrast, along the environment family lambda=c/T, with fixed c>0 and alpha>0,

\[
\frac{R_T^*}{T}\longrightarrow
\Delta\left[\frac{1-e^{-c}}c
-\frac{1-e^{-c(1+\alpha)}}{c(1+\alpha)}\right]>0.
\]

To prove this limit, write the survival sum as a Riemann sum: for n/T tending to
x, S_n tends to exp(-cx) and u^n to exp(-c(1+alpha)x). Both are bounded by one,
so integration on [0,1] gives the expression. Positivity follows because
exp(-cx)>exp(-c(1+alpha)x) for x>0. **The law changes with T in this statement.**
It does not establish linear regret in a fixed market.

An additional analytic consequence, derived after the v4 computation contract
was frozen and not separately benchmarked, makes both boundaries explicit:

\[
\Delta\alpha\lambda\sum_{n=1}^{T-1}n u^{n-1}
\ \le R_T^*\ \le
\Delta\min\left\{\frac{\alpha\lambda T(T-1)}2,
\frac{\alpha}{\lambda(1+\alpha)}\right\},\quad\lambda>0.
\]

For the lower bound, replace every bad-choice factor v in a survival product by
u one at a time. Each replacement changes the product by at least
(v-u)*u^(n-1). The symmetric policy averages n/2 bad choices in an n-prefix.
For the upper bound, S_n<=(1-lambda)^n since uv<=(1-lambda)^2. Subtract u^n and
use the telescoping product bound n*lambda*alpha for the first upper bound; sum
the two infinite geometric series for the second. Each finite summand is
nonnegative, so extending the sum to infinity is legitimate.

Consequently, at fixed T the regret vanishes as lambda tends to zero: both policies
then almost never obtain access. At fixed positive lambda the regret per round
vanishes as T grows. Order-one regret per round is possible when the restoration
time is of the same order as the horizon. This is a property of the reduced
search problem, not a universal empirical law of market access.

## 4. Frozen deterministic checks

The v4 source/config/contract archive was frozen at 2026-09-08T05:34:14Z, before
numerical output access. All checks use Delta=1.

| Check | Completed scope | Result |
|---|---|---|
| Exact rational first-success reward enumeration | 36 law/horizon cells, T=1..12, 12,285 deterministic sequences | Every optimal equal-prior value and both symmetrized world risks equal the formula exactly |
| Minimax LP over mixtures of all sequences | 30 of the above cells, T<=10 | Maximum absolute regret discrepancy 1.34e-15 |
| Independent Bayesian reward DP with failure posterior | 18 cells, T=16/64/256 | Maximum absolute value discrepancy 1.43e-13 |
| Closed-form scaling evaluation | 72 frozen cells, T=16..16384 | All cells retained; no parameter selection |

The first-success enumeration accumulates reward after the actual success event;
the DP recursively updates the posterior and future reward; the formula sums
survival costs. Their agreement checks three distinct calculations. Finite checks
support the implementation; the proof supplies the general minimax theorem. These
are deterministic development results with no uncertainty intervals or claim of
independent scientific replication.

Representative frozen cells at alpha=0.5:

| Regime | T | lambda | Exact minimax regret | Regret / T |
|---|---:|---:|---:|---:|
| Fixed environment | 256 | 0.01 | 27.002607 | 0.105479 |
| Fixed environment | 4096 | 0.01 | 33.207863 | 0.008107 |
| Fixed environment | 16384 | 0.01 | 33.207863 | 0.002027 |
| lambda=1/T family | 256 | 1/256 | 29.220683 | 0.114143 |
| lambda=1/T family | 4096 | 1/4096 | 467.776798 | 0.114203 |
| lambda=1/T family | 16384 | 1/16384 | 1871.156494 | 0.114206 |

The first regime tends to total regret 33.207863; the second tends to normalized
regret 0.114207332. Rewards are abstract units of this synthetic model, not measured
market profits or calibrated ticks. The audit used one CPU process on the existing
V100 server for 3.132216 seconds, zero GPU computation and no external data.

[Two-regime figure](../../experiments/paper_g/recovery_search_20260908_v4/recovery_search_boundary.png)
and [all 72 cells](../../experiments/paper_g/recovery_search_20260908_v4/scaling_cells.csv)
are included with the reproducibility artifacts.

## 5. Primary-parent collision and terminal decision

[Rosenberg, Cohen, Mansour and Kaplan (ICML 2020)](https://proceedings.mlr.press/v119/rosenberg20a.html)
study learning stochastic shortest paths. Their [Appendix C](https://proceedings.mlr.press/v119/rosenberg20a/rosenberg20a-supp.pdf)
uses an initial state and absorbing goal with one unknown action having larger
success probability. The kernel mapping is B*=1/p+ and epsilon=1-p-/p+.
Our observation and action spaces are the same; minimizing truncated waiting cost
preserves every policy's reward and regret up to the common affine transformation
given above. Their stated small-epsilon range includes alpha<1/15 with B*>=2;
the frozen alpha=0.05 law lies inside it. Their published repeated-episode bound
is not this finite-horizon exact formula. We do not claim that the formula is
printed there, only the direct parent construction and exact reduction.

[Gittins (1979), Section 10](https://academic.oup.com/jrsssb/article/41/2/148/7027626)
already treats search ending at the first success. Its independent-arm index
theorem is not invoked for this correlated two-world prior. The present elementary
balancing proof is self-contained.

The existence of unavoidable regret is therefore scientifically resolved in
this reduced model, but it provides no established irreducible market contribution.
**Record `paper_g_m2r_unknown_recovery_channel_search` as `failed_closed` for
independent-paper novelty.** Retain the theorem, timing contract, rational
enumerator, posterior DP, minimax LP and scaling benchmark as reusable assets.

Re-entry into a broader endogenous-access problem requires a specified lawful
coupling between trading, inventory/funding and restoration that cannot be removed
by relabelling the two success arms. Both worlds must preserve the same feasible
comparator and actual feedback; any proposed bound must contain a structured
residual beyond existing search, SSP and constrained-control results. A new name,
more seeds or a neural policy is insufficient. No such coupled mechanism has been
established by this audit, and no wider family is claimed impossible.

## 6. Artifacts and evidence boundaries

- Implementation: `ecomd/paper_g/recovery_search.py`.
- Frozen config: `configs/paper_g/recovery_search_v4.yaml`.
- Data and source: `experiments/paper_g/recovery_search_20260908_v4/`.
- Source archive SHA256: `5c69a78239ee3971d08016a787a6ba2eac10dc608d00679622306a86af2ea136`.
- Git base: `297c36551fdfb25af564bc575f11ea27f95280bf`; the exact uncommitted source
  archive, not the base commit alone, identifies the executed implementation.
- Decision: `research/discovery/decisions/pi_paper_g_recovery_search_audit_20260908.yaml`.
- Receipt: `research/paper_g/recovery_search_v4_receipt.yaml`.

This PI-directed continuation accessed only declared synthetic development outputs.
It is recorded separately from the outcome-free re-entry trigger ledger. Historical
cycle counts and forecasts are not backfilled; no fresh candidate-harvesting cycle
or full activation claim is made. Operational conformance records remain private.
