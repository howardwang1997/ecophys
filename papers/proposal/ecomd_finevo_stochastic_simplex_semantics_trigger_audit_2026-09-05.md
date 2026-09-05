# EcoMD FinEvo stochastic-simplex semantics trigger audit

**Date:** 2026-09-05  
**Archetype:** `simulator_method`  
**Decision:** `not_trigger`  
**Candidate harvesting:** not authorized  
**Outcome access, implementation, EcoMD execution, SSH, and GPU work:** not authorized

## 1. Executive decision

FinEvo is a directly relevant 2026 preprint: it combines heterogeneous trading agents, endogenous
double-auction prices, a stochastic replicator--mutator population layer, and differentiable or
learning-based strategies. It therefore strengthens the collision boundary around any broad
"EcoMD plus evolutionary market ecology" proposal. It does not provide a qualified re-entry
trigger.

The strongest finding is exact and adverse to FinEvo's own continuous-time interpretation. The
heterogeneous-noise SDE written in the main text and Appendix E does **not** conserve total
population mass. The normalized exponential update used in the experiments does preserve the
simplex, but its weak continuous-time limit has a different diffusion ordering and a nonzero Itô
drift correction. Both facts were already derived in the classical stochastic-replicator
literature. In addition, independently redrawing a Dirichlet innovation target at every discrete
step creates an order-`h` random drift whose accumulated variance vanishes as the step `h` tends to
zero; it is not the finite diffusion contribution asserted by the step-one variance decomposition.

These are scientifically material specification errors, but correcting them is an erratum-sized
result rather than an ICLR method. Turning the checks into an automatic generator audit reduces to
local conditional-moment/generator convergence and stochastic modified equations, while the
repository's generic simulator-audit and stochastic-semantic-conformance routes are already closed.
The projection-order defect also does not reopen the measure-correct hard-projection route: here the
failure is elementary non-tangency, not a missing co-area or curvature correction. Turning FinEvo's
strategy shares into an EcoMD topic also fails: the broad evolutionary-market composition is directly occupied,
and its entropy, HHI, top-one, and phase-change conclusions are not invariant to splitting one
behaviorally identical strategy label into several labels. The latter repair reduces to the
already closed market-native actor-refinement and Markov-lumpability routes.

No new route node is warranted. The source and counterexamples are retained as an early semantic
gate for future constrained stochastic simulators.

## 2. Frozen question contract

**Market-native object.** The joint law of strategy capital shares and market-price response at a
fixed economic reallocation interval, under a declared strategy taxonomy and population-update
kernel.

**Rival explanations.** Under H1, the stated FinEvo SDE is the continuous process approximated by
the implemented exponential update, so its simplex guarantees and selection--innovation--noise
attribution apply to the simulator. Under H0, the implemented update defines a different discrete
Markov chain; the continuous equation, variance decomposition, and ecological metrics do not
identify that chain or a market mechanism.

**Cheapest discriminator.** Compute the tangent condition of the stated diffusion and the first two
conditional moments of one normalized exponential step as `h -> 0`. No simulation is needed. A
positive result would support a lawful continuous-time market ecology. A null result matters because
it prevents visually stable population paths or stylized facts from being attributed to the stated
SDE.

## 3. The stated heterogeneous diffusion is not tangent to the simplex

Let `x` be a column vector on the simplex, `D_x=diag(x)`,
`S=diag(sigma_1,...,sigma_K)`, and

\[
P(x)=I-\mathbf 1x^\top.
\]

FinEvo writes the diffusion matrix as

\[
B_{\mathrm{paper}}(x)=\gamma D_x S P(x).
\]

Simplex tangency requires `1^T B=0`. Instead,

\[
\mathbf 1^\top B_{\mathrm{paper}}(x)
=\gamma\left[x^\top S-(x^\top S\mathbf 1)x^\top\right],
\]

which is nonzero for generic heterogeneous `sigma_i`. The ordering matters. The correct diffusion
induced by noisy logits is

\[
B_{\mathrm{logit}}(x)=\gamma D_xP(x)S,
\qquad
\mathbf 1^\top B_{\mathrm{logit}}(x)=0.
\]

An explicit two-strategy witness makes the failure unavoidable. With
`x=(1/2,1/2)` and `S=diag(1,2)`,

\[
D_xSP(x)=
\begin{pmatrix}
1/4&-1/4\\
-1/2&1/2
\end{pmatrix},
\]

so the column sums are `(-1/4,1/4)` and

\[
d(X_1+X_2)=\frac{\gamma}{4}(dW_2-dW_1),
\]

not zero. Appendix E repeats the same ordering componentwise as
`sigma_i X_i(dW_i-sum_j X_j dW_j)` and its claim that summing cancels the diffusion is false unless
the noise intensities satisfy a special restriction such as equality.

The paper is also internally inconsistent: Appendix C's variance calculation uses

\[
\gamma x_i\left(\sigma_i\eta_i-\sum_jx_j\sigma_j\eta_j\right),
\]

which corresponds to `D_x P S` and **is** tangent. Thus the theoretical SDE, the claimed proof, and
the variance calculation do not describe one diffusion.

## 4. The normalized exponential update converges to a different SDE

Ignoring innovation for one substep, the implemented update is

\[
x_i^+=
\frac{x_i\exp\{\beta V_i h+\gamma\sigma_i\sqrt h\,\xi_i\}}
{\sum_jx_j\exp\{\beta V_j h+\gamma\sigma_j\sqrt h\,\xi_j\}}.
\]

Equivalently, let logits obey

\[
dY_i=\beta V_i\,dt+\gamma\sigma_i\,dW_i,
\qquad X=\operatorname{softmax}(Y).
\]

Itô's formula gives

\[
\begin{aligned}
dX_i={}&\beta X_i(V_i-\bar V)\,dt
+c_i(X)\,dt\\
&+\gamma X_i\left(\sigma_i\,dW_i-
\sum_jX_j\sigma_j\,dW_j\right),
\end{aligned}
\]

where, with `q_j=gamma^2 sigma_j^2`,

\[
c_i(x)=\frac{x_i}{2}\left[
q_i(1-2x_i)-\sum_jx_jq_j+2\sum_jx_j^2q_j
\right]
=\frac{x_i}{2}\left[
q_i(1-2x_i)-\sum_jx_jq_j(1-2x_j)
\right].
\]

This is not a negligible higher-order term: it is order `dt`, the same order as selection. Even
homogeneous noise yields `c_i=gamma^2 sigma^2 x_i(||x||_2^2-x_i)`, which is generally nonzero.

The formula is not new. Mertikopoulos and Moustakas derived precisely this stochastic-replicator
equation from noisy cumulative scores passed through a logistic map in 2010. Mertikopoulos and
Viossat later emphasized that direct share shocks, aggregate population shocks, and noisy-logit
learning have different Itô corrections and can have different stability and extinction behavior.
FinEvo's derivation takes logarithms, drops the second-order term, and then labels the resulting
normalized exponential step first-order consistent with an SDE that has neither the correct
diffusion order nor this drift. That consistency claim is false.

Positivity and unit sum of the discrete map remain true by construction. They establish properties
of the discrete map, not consistency with the written SDE.

## 5. The Dirichlet innovation has no stated continuous-time noise limit

Restore the paper's step-size notation:

\[
X_{n+1}=(1-\mu h)\widehat X_{n+1}+\mu h M_n,
\qquad M_n\stackrel{iid}{\sim}\operatorname{Dirichlet}(\alpha).
\]

Writing `M_n=m+tilde M_n`, the centered innovation increment is
`mu h tilde M_n`. Over a fixed horizon `T` with `T/h` steps, its variance is

\[
\frac{T}{h}\mu^2h^2\operatorname{Var}(M_n)
=T\mu^2h\operatorname{Var}(M_n)\longrightarrow0.
\]

Thus the iid Dirichlet randomness disappears in the continuous-time limit; only the deterministic
drift `mu(m-X)` survives. A nondegenerate innovation diffusion would need square-root step scaling
and a tangent covariance, or a separately defined continuous-time jump/diffusion process. At the
paper's experimental choice `h=1`, the Dirichlet redraw is a valid discrete design choice, but its
finite step variance cannot simultaneously be cited as the volatility term of the stated
continuous SDE.

## 6. Why the variance decomposition is not market-volatility attribution

The displayed additive formula concerns conditional variance of one **strategy-share increment**,
not variance of market returns. Independence of centered inputs at a single update can remove local
cross-covariances, but it does not decompose closed-loop price volatility: selection, innovation,
and perturbations change orders, prices, portfolios, future payoffs, and subsequent population
shares through the same feedback system.

The paper separately reports stylized facts of simulated return series. No theorem or intervention
connects the local `Var(Delta x_i)` components to those return statistics. Removing selection,
innovation, or perturbation also changes a mechanism that directly defines the reported share
metrics, so the corresponding ablations show implementation sensitivity rather than causal
identification of a real-market volatility source.

This distinction survives every mathematical repair above. A correct stochastic-replicator SDE
would still be an analyst-chosen capital-reallocation policy unless its transition hazards and
payoff-to-adoption map were identified from a market-native population process.

## 7. Strategy-label refinement changes the ecological metrics

Suppose one strategy label of share `x_i` is replaced by `r` behaviorally identical labels, each
with share `x_i/r`, while aggregate capital, orders, and prices are coupled to remain unchanged.
Then the paper's population metrics change mechanically:

\[
H'=H+x_i\log r,
\qquad
\mathrm{HHI}'=\mathrm{HHI}-x_i^2(1-1/r).
\]

Top-one share can fall from `x_i` to `x_i/r`; the identity of the dominant label and hence the
phase-change count can also change. Independent noise per new label changes the population law as
well, whereas shared noise makes invariance a coupling convention. Therefore high diversity,
lower concentration, and frequent phase transitions are not properties of the market process until
the strategy taxonomy and clone semantics are fixed independently of the desired conclusion.

A learned quotient over behaviorally equivalent strategies is not an open shortcut. Exact
closed-loop equivalence is Markov lumpability; capital-preserving independent splitting is a
branching or infinite-divisibility condition; and approximate behavioral state abstraction is a
mature learning problem. The repository already closed the market-native refinement version after
explicit FIFO, pro-rata, rounding, and false-name counterexamples.

## 8. Collision and residual-novelty audit

| Candidate formulation | Collision or fatal weakness | Decision |
|---|---|---|
| Correct FinEvo's projection order and Itô term | Exact noisy-logit stochastic-replicator formula is in Mertikopoulos--Moustakas; correction is too small | Kill |
| Build an automatic discrete-update-to-SDE checker | First two local moments and weak generators are standard; stochastic modified equations already formalize algorithm-to-SDE approximation; generic audit and semantic-conformance routes are closed | Kill |
| Use Aitchison geometry for simplex Brownian motion | Direct geometric stochastic-replicator parent already supplies the construction and approximation theory | Kill |
| Make ecological metrics invariant to strategy splitting | Reduces to diversity-granularity axioms, behavioral quotienting, branching, and Markov lumpability; no market-native identity anchor | Kill |
| Combine FinEvo population evolution with EcoMD mechanics | FinEvo directly occupies evolutionary market ecology; combining two analyst-designed simulators supplies no external truth or irreducible learning method | Kill |
| Claim population-size robustness from `N=60,80,100,120` | Latent agent count and strategy-label granularity are not market-native; stable selected moments do not identify a projective path law | Kill |

The most generous method residual would infer or certify the weak generator of a black-box
constrained stochastic update. For an increment `Delta_h`, however, the obvious certificate is

\[
b_h(x)=h^{-1}\mathbb E[\Delta_h\mid x],
\qquad
a_h(x)=h^{-1}\mathbb E[\Delta_h\Delta_h^\top\mid x],
\]

together with a Lindeberg condition and convergence on a core of test functions. Estimating these
moments by autodifferentiation or Monte Carlo is not itself a new algorithm, theorem, or scientific
object. A finite set of step sizes also cannot uniquely determine all higher-order modified
equations without additional assumptions. No separating lower bound, new estimator, or independent
two-system validation contract emerged from this source.

The repository's `stochastic_simulator_gradient_semantic_conformance` route already demanded a
semantic certificate beyond analytic, unbiased-gradient, probabilistic-program, and cross-solver
checks and closed when no such theorem or common two-system fixture survived. The
`measure_correct_hard_projection_stochastic_simulators` route separately closed the nonlinear-
constraint correction idea under constrained-Langevin parents. FinEvo supplies a clean new defect
fixture, but no theorem that removes either route's blocker.

## 9. Gate matrix

| Gate | Result |
|---|---|
| Written heterogeneous diffusion preserves total share | Fail |
| Appendix C, Appendix E, and main SDE use one noise operator | Fail |
| Normalized exponential map is first-order weak consistent with written SDE | Fail |
| Itô drift is included | Fail |
| Iid Dirichlet innovation retains finite continuous-time variance | Fail |
| Share-increment variance identifies price volatility | Fail |
| Ecological metrics survive behavior-preserving label splitting | Fail |
| Broad evolutionary market simulator is unoccupied | Fail; FinEvo itself is direct collision |
| Correction yields a new ICLR theorem or estimator | Fail |
| Two independent same-estimand truth systems exist | Fail |

## 10. Preserved reusable asset

For every future simplex- or conservation-constrained stochastic simulator, run this semantic gate
before any experiment:

1. verify left-null conservation of every diffusion and jump operator;
2. preserve matrix ordering when state-dependent projections and heterogeneous scales do not
   commute;
3. derive the weak generator of the actual discrete map through order `h`, including Itô terms;
4. classify every random input by its `h`, `sqrt(h)`, or jump-intensity scaling;
5. distinguish latent-state variance from the market observable named in the claim; and
6. split and merge behaviorally identical labels while holding aggregate actions fixed.

This six-part test is useful repository QA and reviewer evidence. It is not an activated paper.

## 11. Exact re-entry conditions

Re-audit only if a future source or theorem supplies all of the following:

1. a constrained-update generator estimator or compiler with a nontrivial finite-sample upper bound
   and a separating lower bound beyond local Kramers--Moyal moments, standard weak convergence, and
   stochastic modified equations;
2. a representation-invariant market estimand under a declared strategy split/merge operation,
   with an observable economic identity or capital measure rather than simulator labels;
3. a result showing when local generator certification controls a new downstream intervention
   response, rather than only internal simulator consistency;
4. analytical or gold-standard truth on at least two independently maintained non-EcoMD stochastic
   systems and an untouched market confirmation partition; and
5. a new current machine decision authorizing implementation and compute.

Another corrected projector, softmax layer, simplex-preserving integrator, mechanism ablation,
stylized-fact table, latent-`N` sweep, or EcoMD--FinEvo component composition is not a trigger.

## 12. Primary sources

1. Zou et al., *FinEvo: From Isolated Backtests to Ecological Market Games for Multi-Agent
   Financial Strategy Evolution*, arXiv:2602.00948v1 (2026),
   https://arxiv.org/abs/2602.00948
2. Mertikopoulos and Moustakas, *The emergence of rational behavior in the presence of stochastic
   perturbations*, Annals of Applied Probability 20 (2010),
   https://doi.org/10.1214/09-AAP651
3. Mertikopoulos and Viossat, *Imitation Dynamics with Payoff Shocks*, arXiv:1412.7842 (2014),
   https://arxiv.org/abs/1412.7842
4. Lehmann, *Darwinian evolution as Brownian motion on the simplex: A geometric perspective on
   stochastic replicator dynamics*, arXiv:2008.05410 (2020),
   https://arxiv.org/abs/2008.05410
5. Li, Tai and E, *Stochastic Modified Equations and Adaptive Stochastic Gradient Algorithms*, ICML
   2017, https://proceedings.mlr.press/v70/li17f.html

## 13. Compute decision

This audit is `not_trigger`; `candidate_harvest_authorized=false`. Do not reproduce FinEvo, download
its outcomes, implement a corrected layer, modify EcoMD, SSH to a worker, or schedule the A800/V100
pool under this route. The current constraint-attribution machine decision is unrelated and grants
no authority here.
