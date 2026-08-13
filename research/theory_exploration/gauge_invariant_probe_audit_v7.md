# V7 gauge-invariant controller-probe audit

**Date:** 2026-08-13

**Frozen parent:** `gauge-invariant-controller-probes-v7@f4e074b44`

**Outcome access:** none

**Remote/GPU access:** none

**Final decision:** `V7_NO_SURVIVOR`

## 1. Scope and decision

V7 tested three proposed exits from the V6 response/latent-state alias before opening data or creating an
experiment. The audit gives the following decisions:

| Candidate | N0/I0 result | Final state | Binding reason |
|---|---|---|---|
| C1 observable quotient response | fails N0 | `RETIRED_PRIOR_ART` | every admissible functional factors through the controlled input--output behavior; standard realizations are transfer/Markov/Hankel or predictive-state objects |
| C2 drift-budget identified set | fails N0 | `RETIRED_PRIOR_ART` | the sharp linearized set is an ordinary set-membership ellipsoid/polytope and its probe criterion is standard optimal excitation |
| C3 paired loop/curvature probe | fails I0 | `RETIRED_IDENTIFIABILITY` | a fixed finite-state transducer can reproduce the complete randomized finite probe tree, so path randomization identifies assignment effects but not adaptation as a mechanism label |

Consequently no candidate reaches E0 or P0. No experiment directory, generated trajectory, market outcome, remote
job or GPU job is authorized. NMI has no non-equivalent method; NCS has neither an identified new phenomenon nor a
prospective independent data contract.

## 2. Primary-source attack matrix

| Neighborhood | Primary result checked | Exact collision with V7 |
|---|---|---|
| input--output realization | [Minimal LPV input--output realizations](https://arxiv.org/abs/2305.08508) shows that minimal realizations of the same behavior are isomorphic; [stable input--output realizations](https://arxiv.org/abs/2607.03849) characterizes finite-dimensional stable realization through Hankel rank and response decay | C1's latent-gauge quotient is the behavior already represented by Markov/sub-Markov parameters, Hankel operators and minimal realizations |
| predictive state | [Predictive State Representations](https://proceedings.neurips.cc/paper_files/paper/2001/hash/1e4d36177d71bbb3558e43af9577d70e-Abstract.html) uses action-conditional future tests as state | the nonlinear/stochastic form of C1 is a functional of controlled future laws, not a new latent object |
| closed-loop identification | [Dual system-level closed-loop identification](https://arxiv.org/abs/2304.02379) parameterizes known-feedback closed-loop responses directly | exact controller knowledge does not make a response functional a new identification primitive |
| intervention diversity | [Interventional Gaussian LTI identification](https://proceedings.mlr.press/v236/rajendran24a.html) and [switching-system identifiability](https://proceedings.mlr.press/v235/balsells-rodas24a.html) already state the assumptions under which multiple environments identify latent dynamics | V7 cannot replace cross-regime assumptions with the word "probe" |
| bounded-error identification | [Set-membership identification with guaranteed simulation accuracy](https://arxiv.org/abs/2001.07628) constructs the feasible parameter set of all models compatible with bounded noise and derives finite/infinite-horizon guarantees | C2's drift ball intersected with observational constraints is the same feasible-set construction |
| active safe shrinkage | [Active exploration in adaptive MPC](https://arxiv.org/abs/2003.14120) and its [exact set-membership reformulation](https://arxiv.org/abs/2211.16300) make future inputs shrink parameter uncertainty while enforcing robust constraints | choosing safe probes to reduce C2's diameter is already an active/dual-control design problem |
| mismatch bounds | [Online coreset set-membership identification](https://arxiv.org/abs/2506.22804) gives feasible-set contraction under persistent excitation and an explicit Hausdorff bound when the disturbance radius is wrong | a drift-budget sensitivity bound alone is not a new guarantee |
| randomized paths | [Design and Analysis of Switchback Experiments](https://arxiv.org/abs/2009.00148) optimizes randomization times/probabilities and gives inference under known or misspecified carryover; [Markov switchback experiments](https://arxiv.org/abs/2403.17285) treats carryover and reward autocorrelation jointly | C3's paired forward/reverse path is a switchback design when its target is a path-assignment effect |
| fixed cyclic dynamics | [Geometric stochastic pumps](https://arxiv.org/abs/0705.2057) produces path-dependent current under a fixed stochastic kinetic mechanism | loop area, order and curvature do not by themselves imply adaptation |

The PDF versions of the bounded-error, active-set-membership and switchback papers were rendered and inspected at
their formal definitions, not used only through abstracts.

## 3. Card C1 — quotient factorization

Let

\[
\mathcal B(m)
=\left\{P_m(o_{0:H}\mid a_{0:H-1}):H\ge 0,\ a_{0:H-1}\in\mathcal A_{safe}^H\right\}
\]

be the controlled input--output behavior. V7 defined `m ~ m'` exactly when
`mathcal B(m)=mathcal B(m')`.

### Lemma V7.1 (set-theoretic factorization)

For a functional `f` on the model class, the following are equivalent:

1. `f(m)=f(m')` whenever `m ~ m'`;
2. there is a unique functional `f_bar` on `im(mathcal B)` such that

\[
f=\bar f\circ\mathcal B.
\]

**Proof.** If `f` is constant on equivalence classes, define `f_bar(B(m))=f(m)`. Equality of behaviors makes
this well defined, and surjectivity onto `im(B)` gives uniqueness. The converse follows by substitution. `square`

This lemma is elementary and supplies no scientific discriminator. In linear classes, `mathcal B` is encoded by
the transfer function, Markov/sub-Markov parameters or Hankel operator; minimal state realizations are unique only
up to the corresponding isomorphism. In general controlled stochastic classes, action-conditional tests give a
predictive-state representation. A scientifically useful scalar of this behavior can still be designed, but
calling it gauge invariant does not make it a new representation or identification theorem.

**C1 decision:** `RETIRED_PRIOR_ART`. Re-entry would require a specified functional with a guarantee unavailable
from the full input--output law or its standard finite representation, not merely a market interpretation.

## 4. Card C2 — exact drift modulus

The local V6 intervention equation can be written

\[
b=S\delta+e,\qquad \lVert e\rVert_2\le\rho,
\]

where `delta` is the proposed response change, `S` is the frozen probe-sensitivity stack and `e` absorbs the
declared cross-regime drift. With no additional parameter restriction, the sharp feasible set is

\[
\Theta_\rho(b)=\{\delta:\lVert S\delta-b\rVert_2\le\rho\}.
\]

### Lemma V7.2 (sharp linear drift width)

Let `S` have full column rank, let `delta_ls=S^dagger b`, and let
`r=(I-SS^dagger)b`. If `rho >= ||r||_2`, then

\[
\Theta_\rho(b)
=\left\{\delta_{ls}+h:
h^\top S^\top S h\le \rho^2-\lVert r\rVert_2^2\right\}.
\]

Its Euclidean diameter and the width of a linear target `ell^T delta` are exactly

\[
\operatorname{diam}_2(\Theta_\rho)
=\frac{2\sqrt{\rho^2-\lVert r\rVert_2^2}}{\sigma_{min}(S)},
\qquad
\operatorname{width}_{\ell}(\Theta_\rho)
=2\sqrt{\rho^2-\lVert r\rVert_2^2}
\left\lVert S^{\dagger\top}\ell\right\rVert_2.
\]

If `S` is rank deficient, the set is unbounded in every feasible null direction unless an external parameter set
removes that direction.

**Proof.** Orthogonality of `r` to `col(S)` gives
`||S(delta-delta_ls)-r||_2^2=||S(delta-delta_ls)||_2^2+||r||_2^2`. The extremizers are the smallest right singular
vector for diameter and the support points of the resulting ellipsoid for directional width. A null vector can be
added without changing the residual in the rank-deficient case. `square`

This is a useful interpretation of Experiment 151: the BPO stack leaves an infinite null direction, while a
full-rank generated stack gives a radius inversely proportional to its smallest singular value. But the lemma is
elementary set-membership geometry. Selecting probes to maximize `sigma_min(S)` is E-optimal excitation; general
set-membership and adaptive MPC results already handle polytopic uncertainty, nonlinear constraints, future-input
dependent set shrinkage, safety and disturbance-radius mismatch. A nonlinear latent metric changes the feasible
set geometry but not this methodological category unless the exact mechanism yields a distinct sharp theorem.

**C2 decision:** `RETIRED_PRIOR_ART`. Re-entry requires a controller-specific non-Euclidean identified-set theorem
with a matching lower bound that is strictly unavailable from robust/set-membership identification under the same
assumptions.

## 5. Card C3 — finite probe-tree alias

Let `T` be any finite safe probe tree of depth `H`. A randomized protocol chooses each next action according to a
known policy supported on `T`. Suppose an alleged adaptive system specifies, for every reachable history `h_t` and
action `a_t`, an output kernel

\[
Q_t(\mathrm d o_{t+1}\mid h_t,a_t).
\]

### Proposition V7.3 (fixed-transducer equivalence)

There exists a fixed, time-homogeneous controlled Markov transducer on the finite-depth history state that has
exactly the same joint law of actions and observations under every randomized policy supported on `T`. Its hidden
state is finite when the reachable action and observation supports are finite.

**Construction.** Give the transducer one state for each reachable history node, including time in the node label.
At state `h_t` under action `a_t`, draw the next observation from `Q_t`, then transition to the child state
`h_{t+1}=(h_t,a_t,o_{t+1})`. For finite observation support this is a finite-state transducer; for general output
spaces it is the corresponding fixed Markov kernel on the finite-depth history space. Induction on `t` proves
equality of every path law. `square`

Therefore no statistic of the finite randomized probe record can distinguish parameter adaptation from a fixed
hidden-memory realization when both are allowed to implement the same path kernels. This includes loop area,
forward--reverse contrast, response curvature and noncommutativity. Randomization remains valuable: under the
usual consistency, support and carryover assumptions it identifies causal effects of assigning one controller
path rather than another. It does not identify the ontological decomposition of that response into "adaptation"
versus fixed latent state. Restricting the null to memoryless or low-order systems makes the statistic a declared
model-class test, not a universal adaptation detector.

**C3 decision:** `RETIRED_IDENTIFIABILITY`. Its causal path-effect version is standard switchback inference; its
mechanism-label version is defeated by the fixed-transducer alias. Re-entry requires an externally measured state,
a physical reset/erasure intervention with a manipulation check, or a restriction whose scientific validity is
independently testable.

## 6. Venue and resource consequence

- **NMI:** `NO_SURVIVOR`. C1 and C2 are standard systems objects; C3 supplies no new identified learning target.
- **NCS:** `NO_SURVIVOR_IDENTIFIABILITY`. A randomized controller path can support a causal treatment-effect paper
  only after a real prospective system and replication exist, but it cannot support the proposed adaptation claim.
- **Experiments:** none. The frozen stop rule fired before E0/P0, so simulation would illustrate known geometry or
  the constructed alias without changing the decision.
- **Data:** no outcome, paid dataset or prospective assignment was opened. Primary papers and public metadata only.
- **Compute:** negligible local document/graph work; zero remote CPU, zero V100/RTX2060 contact and zero GPU-hours.

V7 is an informative closure: quotienting removes unidentifiable coordinates only by moving the target to ordinary
input--output behavior; bounding drift turns point identification into standard set membership; and randomizing a
finite path identifies assignments rather than a latent mechanism label. The next iteration must change the
scientific target or add an external measurement/reset, not rename one of these three operations.
