# Observation-quotient T0 mathematical scratch — 2026-08-22

**Status:** closed T0 reduction evidence; exact sanity checks, not a theorem claim or execution authorization

## 1. Passive-equivalence counterexample

For (a,c,\sigma_y,\sigma_z,\beta>0), define two stable linear diffusions indexed by
(s\in\{-1,+1\}):

\[
\begin{aligned}
dZ_t^{(s)}&=-cZ_t^{(s)}dt+\sigma_zdW_t^z+u_tdt,\\
dY_t^{(s)}&=-aY_t^{(s)}dt+s\beta Z_t^{(s)}dt+\sigma_ydW_t^y.
\end{aligned}
\]

Only (Y) is observed. More generally, the observer may receive any fixed measurable temporal transformation
(H_\Delta(Y_{0:T})).

### Proposition 1 — exact passive path equivalence

With stationary initialization and (u\equiv0), the two models induce the same law for (Y_{0:T}) and therefore
for (H_\Delta(Y_{0:T})), for every (T) and every fixed (H_\Delta).

**Proof.** Couple the (s=-1) process to the (s=+1) process by setting
(Z^{(-)}=-Z^{(+)}), (W^{z,(-)}=-W^{z,(+)}), and using the same (Y_0,W^y). The stationary law of the centered OU
coordinate is invariant under reflection and
((-\beta)Z^{(-)}=\beta Z^{(+)}). Hence the coupled (Y) paths are equal almost surely. Pushforward by any fixed
(H_\Delta) preserves equality in law. \(\square\)

### Proposition 2 — opposite response under an anchored intervention

Let (u_t=h\mathbf 1\{t\ge0\}) with (h>0), independently defined by the experimental protocol rather than by
the latent coordinate convention. Starting from the passive stationary distribution,

\[
m_Z(t)=\frac{h}{c}(1-e^{-ct})
\]

and, for (a\ne c),

\[
m_Y^{(s)}(t)=
\frac{s\beta h}{c}
\left[
\frac{1-e^{-at}}{a}-
\frac{e^{-ct}-e^{-at}}{a-c}
\right].
\]

The bracket equals
(\int_0^t e^{-a(t-r)}(1-e^{-cr})dr>0). Thus the two transient response signs are opposite for every
(t>0), and the steady responses are (s\beta h/(ac)).

This proves that passive path realism alone cannot identify even the sign of this response. It does not establish a
new result: it is a linear hidden-state instance of established causal/sign non-identifiability. If (h)'s positive
direction is defined only by the sign convention for (Z), the construction collapses to a gauge transformation and
must be rejected.

### A genuinely interacting two-mode realization

The same issue is not an artefact of the triangular drift. Let (Z=(S,H)^\top), observe (Y=S), and define

\[
dZ_t=A_\eta Z_tdt+\sigma dW_t+Bu_tdt,
\quad
A_\eta=
\begin{pmatrix}-a&\eta c\\\eta d&-b\end{pmatrix},
\quad B=\begin{pmatrix}0\\1\end{pmatrix},
\quad \eta\in\{-1,+1\},
\]

with (ab-cd>0). For (D=\operatorname{diag}(1,-1)), (A_-=DA_+D), (CD=C), and isotropic noise is
invariant under (D). The passive observed paths therefore admit an exact pathwise coupling. Their stationary
output spectrum is

\[
\mathcal S_Y^{(\eta)}(\omega)=
\sigma^2\frac{\omega^2+b^2+c^2}
{|(i\omega+a)(i\omega+b)-cd|^2},
\]

which is independent of (\eta). Yet the input--output transfer function and steady response are

\[
G_\eta(s)=\frac{\eta c}{(s+a)(s+b)-cd},
\qquad
R_\eta=\frac{\eta c}{ab-cd}.
\]

Writing (S=(X_1+X_2)/\sqrt2) and (H=(X_1-X_2)/\sqrt2) gives a two-particle aggregate/contrast
interpretation with generally nonzero and nonreciprocal couplings. It also makes the semantic hazard explicit:
(D) exchanges the hidden particle labels and sends (B\mapsto-B).

The physically correct symmetry object is consequently the joint pair ((m,u)). If a passive symmetry (g)
acts on protocols by (u\mapsto\rho_g(u)), then

\[
(m,u)\sim(gm,\rho_g(u)).
\]

A fixed-coordinate response descends to the model quotient only when the relevant symmetries leave the protocol
semantics invariant or the response itself is invariant. Here (\rho_D(u)=-u); an external class/actuator label is
therefore necessary before (+u) means the same intervention in both models.

## 2. Global quotient statement reduces to a definition

Let (\mathcal O_0:\Theta\to\mathcal P(\mathcal Y)) map parameters to passive observed path laws, and let
(\psi:\Theta\to\mathbb R) be a response functional.

### Lemma 3 — fibre factorization

There exists a function (g:\mathcal O_0(\Theta)\to\mathbb R) such that
(\psi=g\circ\mathcal O_0) if and only if (\psi) is constant on every fibre of (\mathcal O_0).

The proof is immediate by defining (g(P)=\psi(\theta)) for any (\theta\) with (\mathcal O_0(\theta)=P).
Consequently, “an intervention response is identified exactly when it is constant on the observation quotient” is
terminology, not Q0.

For the exact two-point ambiguity with responses (\psi(\theta_\pm)=\pm r), any estimator based on any number
of passive paths also obeys the non-asymptotic bounds

\[
\max_{s\in\{-,+\}}\mathbb E_s|\widehat\psi-\psi(\theta_s)|\ge r,
\qquad
\max_{s\in\{-,+\}}\mathbb E_s(\widehat\psi-\psi(\theta_s))^2\ge r^2.
\]

These are the elementary two-point lower bounds for identical data laws, not a new minimax result.

## 3. Local quotient statement reduces to a rank condition

Suppose (\Theta\subset\mathbb R^p), a differentiable finite-dimensional observation summary
(O:\Theta\to\mathbb R^q) is used, and (\psi) is differentiable. First-order local identification of (\psi)
requires

\[
\ker DO(\theta)\subseteq\ker D\psi(\theta).
\]

In Euclidean coordinates this is equivalent to

\[
\nabla\psi(\theta)\in\operatorname{range}DO(\theta)^\top.
\]

Replacing (DO^\top DO) by an observed Fisher-information operator gives the same null-space condition. Unless
the stochastic interacting/path-observation setting yields a new computable operator, rate or robustness theorem,
this route is standard local estimability and fails Q0/Q2.

## 4. Finite candidate active design reduces to weighted set cover

For a finite candidate family, define the response-relevant unresolved pairs

\[
\mathcal B_{\varepsilon}=
\{\{\theta,\theta'\}:\mathcal O_0(\theta)=\mathcal O_0(\theta'),
|\psi(\theta)-\psi(\theta')|>\varepsilon\}.
\]

For each permissible experiment (e), let (S_e\subseteq\mathcal B_\varepsilon) contain pairs whose observed
laws are separated by the frozen distinguishability threshold. A collection (E) identifies the response to
tolerance (\varepsilon) exactly when

\[
\bigcup_{e\in E}S_e=\mathcal B_\varepsilon.
\]

Minimizing (\sum_{e\in E}c_e) is weighted set cover. The usual hardness and greedy logarithmic approximation
therefore apply. This construction is useful for a benchmark but cannot be Q2 novelty.

## 5. The coarse-graining commutator reduces to existing abstraction error

Let a fine intervention (u) map to a coarse intervention (\omega(u)). The discrepancy

\[
D\!\left(R_{\#}P_u^f,P_{\omega(u)}^c\right)
\]

is the distributional error of an approximate causal abstraction; averaging or maximizing it over interventions
matches established interventional-consistency constructions. Adding time indices or an (m)-step transition
operator does not create a new object.

If (D=D_{\mathrm{KL}}) and (f\in[0,1]), Pinsker's inequality already gives

\[
|\mathbb E_{R_{\#}P_u^f}f-\mathbb E_{P_{\omega(u)}^c}f|
\le \sqrt{\tfrac12D_{\mathrm{KL}}(R_{\#}P_u^f\Vert P_{\omega(u)}^c)}.
\]

Thus converting a path-space fit into a bounded-observable response bound is not C0. Likewise, decomposing a
metric error into memory, filtering, discretization and fitting terms only by the triangle inequality is not a new
theorem. C0 needs dynamics-specific rates or cancellations that existing causal-abstraction, path-space
information and Mori--Zwanzig results do not imply.

## 6. Provisional reduction ledger

| Exit | First attack | Provisional status |
|---|---|---|
| Q0 global theorem | fibre factorization; linear-SDE generator, causal-effect and sign-identifiability results | RED unless a path-dependent interacting-system criterion is strictly stronger |
| Q1 finite-sample certificate | stochastic-process distinguishability and resolution-limit literature | AMBER− pending complete rate/coverage audit |
| Q2 active design | causal-effect intervention design, dynamic model discrimination, set-cover reduction | RED |
| C0 response error | causal abstraction, coarse-grained response, path KL and exact filtered/forced GLE | RED unless a nontrivial joint rate survives |

The completed primary-work matrix closes the provisional Q1 opening. No declared model class, computable
response set, uniform coverage statement or new joint rate was derived; resolution-dependent stochastic-process
distinguishability, partial/discrete IPS inference and mixing-dependent finite-sample theory occupy the proposed
ingredients. The final statuses are Q0 RED, Q1 RED, Q2 RED and C0 RED. See
`papers/proposal/ecomd_observation_quotient_t0_result_2026-08-22.md`.
