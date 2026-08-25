# Trajectory-space liquidity transition: D-1 theorem result

**Frozen question:** 2026-08-25
**Closed:** 2026-08-25
**Outcome access:** none
**Numerical work:** none
**Decision:** FAIL at the paper theorem gate; do not simulate

## 1. Executive verdict

Neither branch of the frozen qualification disjunction survives.

1. A finite irreducible price--time-priority jump process has an analytic tilted Perron root. In the natural
   positive-rate FIFO double-queue family, the large-system limit has one zero-cost activity rate. A cusp at the
   unbiased point therefore requires an added source of dynamical coexistence. The available constructions are
   ordinary multistability, a hard kinetic constraint or an exponentially slow exogenous regime; these reduce,
   respectively, to established reaction-network dynamical phase transitions, kinetically constrained models or
   the frozen slow-mixture negative control.
2. An exact Doob process can equal a predeclared scalar market-rule family only when an edge-log-rate one-form is
   a graph coboundary and the rule changes the total escape rate by the same constant in every state. Cancellation
   fees, one-channel throttles and latency fail already on a two-depth price--time-priority subgraph. Uniform
   thinning succeeds only when the baseline escape rate is state independent; it then merely rescales time and
   leaves the embedded jump chain and stationary law unchanged.

The generic mathematical ingredients are also already established: continuous-time trajectory thermodynamics
([Lecomte, Appert-Rolland and van Wijland](https://doi.org/10.1007/s10955-006-9254-0)), active--inactive
transitions in constrained systems ([Garrahan et al.](https://doi.org/10.1103/PhysRevLett.98.195702)), driven
processes via the generalized Doob transform
([Chetrite and Touchette](https://doi.org/10.1007/s00023-014-0375-8)), current transitions in open queueing
networks ([Chernyak et al.](https://doi.org/10.1007/s10955-010-0018-5)), and near-zero-bias transitions generated
by deterministic multistability
([Lazarescu et al.](https://arxiv.org/abs/1902.08416)). LOB path large deviations are themselves not new
([Rojas, Logachov and Yambartsev](https://doi.org/10.3390/math11204235)).

This is a route-level closure, not a theorem that every conceivable market jump process lacks a trajectory-space
transition. One can insert a glass constraint or a bistable hidden state into a market simulator, but doing so
does not satisfy the frozen irreducibility and novelty tests.

## 2. Minimal price--time-priority model

Let the internal state be two nonempty FIFO queues

\[
x=(B,A),\qquad
B,A\in\bigcup_{q=1}^{N}[N]_{\ne}^{q}.
\]

On side \(\sigma\in\{b,a\}\), a currently absent label appends to the queue tail at aggregate rate
\(\lambda_\sigma(N-q_\sigma)\), each resting order cancels at rate \(\gamma_\sigma\), and a market order removes
the head at rate \(N\mu_\sigma\). On depletion, a full-support refill kernel exposes the next FIFO queue. The
unwrapped price is an additive coordinate: ask and bid depletion carry current marks \(+1\) and \(-1\).
All rates and refill probabilities are positive. The internal chain is finite and irreducible, while append-tail
and pop-head are genuine price--time priority. When rates depend only on depth, the labelled process strongly
lumps to \((q_b,q_a)\).

For event channel \(e:x\to y\), let \(g_e=1\) when the event changes a best queue or spread and let
\(j_e\in\{-1,0,1\}\) be its unwrapped price mark. The tilted operator is

\[
(\mathcal L_{N,s,r}f)(x)
=\sum_{e:o(e)=x}W_e e^{-s g_e+rj_e}f(t(e))-R_N(x)f(x),
\qquad R_N(x)=\sum_{e:o(e)=x}W_e.
\]

A one-side, two-depth quotient already exposes the issue. With positive tail-add, reset and removal rates
\(a,m,d\), respectively,

\[
\mathcal L_{s,r}=
\begin{pmatrix}
-(a+m)&e^{-s}(a+me^r)\\
de^{-s}&-d
\end{pmatrix},
\]

whose principal eigenvalue is

\[
\psi(s,r)=\frac{-(a+m+d)+
\sqrt{(a+m-d)^2+4de^{-2s}(a+me^r)}}{2}.
\]

It is analytic around every positive \((a,m,d)\), including the unbiased point.

## 3. Finite-system and zero-bias results

### Proposition 1: finite-system analyticity

For every finite \(N\), if the event-channel graph is strongly connected and all legal rates are positive, the
spectral bound \(\psi_N(s,r)\) is locally real analytic for all finite real \((s,r)\).

**Proof.** The tilted operator is an irreducible Metzler matrix on the same strongly connected graph. After adding
a sufficiently large scalar multiple of the identity, Perron--Frobenius gives a simple positive dominant
eigenvalue. Its entries are analytic in \((s,r)\), so analytic perturbation of a simple eigenvalue applies. Subtracting
the scalar shift preserves analyticity. In particular,

\[
\partial_s\psi_N(0,0)
=-\sum_x\pi_N(x)\sum_{e:o(e)=x}W_e g_e,
\qquad
\partial_r\psi_N(0,0)
=\sum_x\pi_N(x)\sum_{e:o(e)=x}W_e j_e.
\]

Thus a finite-simulator kink, bimodal histogram or susceptibility peak is an avoided crossing or crossover, not a
genuine singularity. A dynamical phase transition needs a declared large-system or unbounded-state limit.

### Proposition 2: zero-cost activity criterion

Use the extensive normalization

\[
\Psi_\theta(s)=\lim_{N\to\infty}\frac1N
\lim_{T\to\infty}\frac1T\log\mathbb E_\theta e^{-sK_T}.
\]

Suppose \(K_T/(NT)\) obeys a good large-deviation principle with rate function \(I_\theta(k)\), and its effective
domain is compact. Then

\[
\Psi_\theta(s)=\sup_k\{-sk-I_\theta(k)\},
\]

and

\[
\Psi_\theta'(0^+)=-\min I_\theta^{-1}(0),
\qquad
\Psi_\theta'(0^-)=-\max I_\theta^{-1}(0).
\]

**Proof.** The variational formula is Varadhan's lemma. At zero bias, only minimizers with \(I_\theta(k)=0\)
support the subdifferential. Its endpoints are the negatives of the largest and smallest zero-cost activities.

Consequently, an activity jump at \(s=0\) is equivalent to at least two distinct zero-cost activity rates in the
unbiased limiting process. If the physical process has a unique exponentially concentrating law-of-large-numbers
activity, the frozen \(s=0\) qualification cannot hold.

### Application to the positive-rate FIFO family

For one queue, the fluid depth \(z=q/N\) has drift

\[
\dot z=\lambda(1-z)-\gamma z-\mu.
\]

When \(\lambda>\mu\), it has the unique hyperbolic attractor

\[
z_* = \frac{\lambda-\mu}{\lambda+\gamma}>0,
\]

with typical counted activity

\[
k_*=\lambda(1-z_*)+\gamma z_*+\mu
=\frac{2\lambda(\gamma+\mu)}{\lambda+\gamma}.
\]

The density-dependent-chain law of large numbers, the event-count martingale decomposition and the positive
full-support refill imply a single zero-cost time-averaged activity for this linear family. When
\(\lambda<\mu\), the process instead has one regenerative depletion/refill cycle and again one time-average.
The surface \(\lambda=\mu\) is the ordinary codimension-one queue-stability boundary, not an open-set trajectory
phase.

Moreover, its counted escape rate satisfies

\[
R_N(q)\ge N\{\mu+\min(\lambda,\gamma)\}.
\]

There is therefore no low-activity configuration whose waiting cost is subextensive in \(N\), the mechanism that
supports an inactive phase in a hard kinetically constrained model.

## 4. Why the apparent escapes do not qualify

### Exponentially slow regime mixture

Let an exogenous state switch between activity rates \(Nk_A\) and \(Nk_I\) at
\(\epsilon_N=e^{-cN}\). Its tilted block has diagonal activities
\(Nk_{A,I}(e^{-s}-1)\) and switching rate \(\epsilon_N\). Hence

\[
\lim_{N\to\infty}\frac1N\lambda_{\max}(M_N(s))
=\max\{k_A(e^{-s}-1),k_I(e^{-s}-1)\},
\]

which has a cusp at zero. This is exactly the frozen slow-regime-mixture negative control, not an endogenous LOB
trajectory phase.

### Ordinary multistability

Nonlinear agent feedback can give a fluid market model two attracting fixed points and exponentially slow
finite-\(N\) switching. The resulting near-zero spectral crossing is genuine, but its mechanism is ordinary
macroscopic bistability. Lazarescu et al. prove that deterministically multistable stochastic reaction networks
generically produce first-order dynamical transitions near zero bias. Adding FIFO matching does not make that
generic construction irreducibly market-specific.

### Hard kinetic constraint or absorbing activity

Making the counted escape rate \(o(N)\) in selected configurations can produce an active--inactive transition.
That is the established kinetically constrained mechanism of Garrahan et al. and the activity-transition theory
of [Bodineau and Toninelli](https://arxiv.org/abs/1101.1760). Price--time priority determines allocation order; it
does not itself make every legal arrival, cancellation or execution hazard vanish. Encoding facilitation zeros in
agent rules would be a direct method transplant.

### Observable-induced transition

[Vasiloiu et al.](https://doi.org/10.1103/PhysRevE.101.042115) demonstrate that a selected dynamical observable can
induce a transition even in a non-interacting system. This is why a non-analytic biased observable alone cannot
establish many-body market coordination.

## 5. Exact Doob-to-rule realizability

Let \(W_e^\theta>0\) be a predeclared market-rule family with the same event support as the baseline, and define

\[
R_\theta(e)=\log\frac{W_e^\theta}{W_e}.
\]

### Proposition 3: exact restricted-control criterion

For a finite strongly connected event-channel multigraph, \(W^\theta\) equals the \(s\)-driven Doob rates if and
only if both conditions hold:

1. there is a state potential \(V\) such that, for every channel \(e:x\to y\),
   \[
   R_\theta(e)+sg_e=V(y)-V(x),
   \]
   equivalently the left side sums to zero on every directed cycle; and
2. the escape-rate shift is state independent,
   \[
   R^\theta_{\mathrm{esc}}(x)-R_{\mathrm{esc}}(x)=\psi_s
   \quad\text{for every }x.
   \]

**Proof.** Exact Doob equality gives
\(W_e^\theta=W_e e^{-sg_e}h_s(y)/h_s(x)\); taking logarithms proves the coboundary condition with
\(V=\log h_s\). Summing outgoing driven rates and using
\(\mathcal L_s h_s=\psi_s h_s\) gives the constant escape-rate shift. Conversely, the cycle condition constructs
a consistent positive \(h=e^V\); the constant shift gives \(\mathcal L_s h=\psi h\). Irreducibility identifies this
positive eigenpair as the Perron pair and yields the Doob rates.

This criterion is a direct specialization of the generalized Doob formula plus graph-coboundary/gauge structure,
not a new central theorem; the cycle-space side is covered by
[Wachtel, Vollmer and Altaner](https://doi.org/10.1103/PhysRevE.92.042132).

For a one-parameter exponential rule \(W_e^\theta=W_e e^{\eta(\theta)q_e}\), every cycle \(C\) must obey

\[
\eta(\theta)Q_C+sG_C=0,
\qquad Q_C=\sum_{e\in C}q_e,
\qquad G_C=\sum_{e\in C}g_e.
\]

Two cycles with \(Q_CG_D-Q_DG_C\ne0\) force \(s=\eta=0\). Even when all cycle ratios agree, the rule must still
satisfy a separate constant-escape constraint in every state.

### Minimal market-rule counterexample

Hold the ask side fixed and consider buy-best depths one and two. Legal channels are tail addition
\(L:1\to2\), head execution \(M:2\to1\), and owner cancellation \(C:2\to1\). All count as best-queue activity.
If a cancellation rule multiplies only \(C\)'s rate by \(c\), cycle \(L+M\) requires \(2s=0\), while cycle
\(L+C\) requires \(\log c+2s=0\). Therefore only \(s=0,c=1\) is possible. A cancellation fee cannot exactly
implement nonzero activity bias even on this price--time-priority subgraph.

If every event is uniformly thinned, \(W^c=cW\), the cycle condition gives \(c=e^{-s}\). The escape condition is

\[
(c-1)R_{\mathrm{esc}}(x)=\psi_s
\]

for all states. At nonzero \(s\), this requires a state-independent total event rate. In that exceptional case
\(h_s\equiv1\),

\[
\psi(s)=R_0(e^{-s}-1),\qquad W^{D,s}=e^{-s}W.
\]

The embedded jump chain and invariant law are unchanged: this is only a change of clock. It is analytic and has no
active--inactive many-body physics. The original freeze's literal exact-rule disjunction therefore admitted a
scientifically empty loophole; the loophole is now closed rather than counted as qualification.

A fixed latency changes the Markov state by introducing pending messages; after state augmentation it must satisfy
the same criterion on a different graph. A fee plus strategic response does not define one cross-engine generator
without a frozen response model. A controller that directly queries \(h_s\) trivially implements the known Doob
transform and is not a low-information market rule.

## 6. Two specification defects found by the audit

1. The original potential omitted the large-system normalization. In the natural high-liquidity scaling,
   \(K_T=O(NT)\), so \(T^{-1}\log\mathbb E e^{-sK_T}\) generally diverges with \(N\). A thermodynamic activity
   potential must specify division by \(N\) and the order of limits.
2. In a finite bounded price state, \(J_T=P_T-P_0\) is a coboundary. Its tilt is a diagonal similarity transform
   and cannot change the spectrum. A nontrivial current requires an unwrapped price or winding/event current. In
   an interior stable high-liquidity book, activity and depletion current can also live at different asymptotic
   speeds, so a joint potential needs an explicit scaling for each.

These are not cosmetic corrections: either defect can manufacture a misleading numerical phase diagram.

## 7. Prior-art reduction and decision

| Proposed mechanism | Exact reduction or direct boundary | Consequence |
|---|---|---|
| generic activity tilt and trajectory thermodynamics | Lecomte et al. 2007 | method is established |
| conditioned/driven process | Chetrite--Touchette 2015 | Doob construction and control interpretation are established |
| low-activity phase from forbidden moves | Garrahan et al. 2007; Bodineau--Toninelli 2011 | KCM transplant, not a market-specific mechanism |
| near-zero transition from two attractors | Lazarescu et al. 2019 | generic large-volume multistability result |
| queue-current condensation transition | Chernyak et al. 2010 | queue-network dynamical transition is established |
| observable-created transition | Vasiloiu et al. 2020 | mandatory negative control, not coordination evidence |
| LOB rare paths and rate functions | Rojas et al. 2023 | no first-LOB-large-deviation claim remains |
| exact scalar rule | cycle coboundary plus constant escape shift | natural market primitives fail; constant-rate clock scaling is trivial |

The frozen gate is therefore failed and `trajectory_space_liquidity_dpt` is closed. Hostile residual T0 is reduced
to 0--2%; the probability of a complete Nature Computational Science result on this formulation is below 0.5%.
No cloning, simulator execution, outcome inspection, data purchase, EcoMD change or GPU work is authorized.

Reopening requires a different central theorem, not another observable or sampler: a market-specific interaction
must create an unbiased limiting activity phase without reducing to multistability, an absorbing/KCM constraint,
slow regime mixing or known queue condensation. Any Doob-rule branch must use a predeclared low-information native
rule, hold on an open interval of \(s\), alter the embedded jump chain rather than only its clock, and satisfy both
the cycle and constant-escape conditions in two independent mechanisms without querying \(h_s\).
