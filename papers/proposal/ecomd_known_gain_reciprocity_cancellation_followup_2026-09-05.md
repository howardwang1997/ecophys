# EcoMD known-gain reciprocity-cancellation follow-up

**Date:** 2026-09-05  
**Archetype:** `measurement_method`  
**Decision:** `partial_capability`  
**Standalone ICLR gain-design pitch:** killed  
**Candidate harvesting:** not authorized  
**Experiment, outcome access, implementation, SSH, and GPU status:** not authorized

## 1. Question and correction to the preceding result

The preceding weak-design audit used a purely circulatory two-channel submodel and found that
relative gain, rather than absolute gain, supplies first-order orientation information. That theorem
is exact at zero reciprocal feedback, but it must not be promoted into the broader claim that unequal
gains always identify orientation.

The unresolved fork is now sharper:

- **H1 — gain-only excitation:** any nonzero relative gain reveals the sign of a circulatory
  component;
- **H2 — joint gain--reciprocity geometry:** reciprocal feedback changes the orientation score and
  can exactly cancel the gain contrast, so a design judged strong from gains alone can be singular.

The cheapest discriminating result is an exact two-channel likelihood calculation with a nonzero
reciprocal background. It supports H2. This is a useful correction and produces a new design
diagnostic, but the direct-parent audit below shows that it is not yet a standalone ICLR topic.

## 2. Exact gain--reciprocity cancellation theorem

Take known innovation precision \(K=I_2\), diagonal gains

\[
 D_g=\operatorname{diag}(g_1,g_2),
\]

and feedback

\[
 \Phi_a=P+aA,
 \qquad
 P=\operatorname{diag}(p_1,p_2),
 \qquad
 A=\begin{pmatrix}0&1\\-1&0\end{pmatrix}.
\]

Let \(B_a=I-\Phi_aD_g\), assume \(B_a\) is nonsingular, and observe a Gaussian equilibrium
sample with precision \(\Omega_a=B_a^\top B_a\). Direct multiplication gives

\[
 \Omega_a(g)=
 \begin{pmatrix}
  (1-p_1g_1)^2+a^2g_1^2 & a c(g,P)\\
  a c(g,P) & (1-p_2g_2)^2+a^2g_2^2
 \end{pmatrix},
\]

where the effective orientation contrast is

\[
 c(g,P)=(g_1-g_2)+g_1g_2(p_1-p_2).
\]

The determinant factorizes as

\[
 \det\Omega_a(g)
 =\left\{(1-p_1g_1)(1-p_2g_2)+a^2g_1g_2\right\}^2.
\]

For \(P_{a,g}=\mathcal N(0,\Omega_a(g)^{-1})\), equal determinants make the sign
divergence exact:

\[
 D_{\mathrm{KL}}(P_{a,g}\|P_{-a,g})
 =\frac{2a^2c(g,P)^2}
 {\left\{(1-p_1g_1)(1-p_2g_2)+a^2g_1g_2\right\}^2}.
\]

Therefore \(a\) and \(-a\) are exactly observationally equivalent whenever

\[
 c(g,P)=0,
 \qquad\text{or equivalently}\qquad
 p_1-p_2=\frac1{g_1}-\frac1{g_2}.
\]

This equality can hold with \(g_1\ne g_2\). Unequal gains are thus not, by themselves, an
orientation certificate. The ambiguity also holds for the full law under any spherical innovation
distribution: equality of the two Gram matrices implies that the corresponding structural maps
differ by an orthogonal transformation of the spherical innovation. Gaussianity is sufficient for
the lower bound, but heavy tails alone do not remove it.

Two limiting cases expose the correction.

1. At \(p_1=p_2\), the result reduces to the preceding contrast \(c=g_1-g_2\). Equal gains are
   exactly blind to circulation.
2. At a common gain \(g_1=g_2=s\), the contrast is \(c=s^2(p_1-p_2)\). Common gain is not
   generically blind: reciprocal anisotropy can reveal circulatory sign. It is blind when the
   reciprocal background is isotropic on the pair.

The earlier pure-circulation theorem remains valid; the gain-only interpretation outside that
submodel does not.

## 3. Multiple environments and the correct two-channel design coordinate

For nonzero gains define

\[
 \delta=p_1-p_2,
 \qquad
 d_t=\frac1{g_{1t}}-\frac1{g_{2t}},
 \qquad
 w_t=g_{1t}g_{2t}.
\]

Then

\[
 c_t=w_t(\delta-d_t).
\]

Across independent gain environments, exact sign equivalence persists if and only if every used
environment lies on the same cancellation value \(d_t=\delta\), apart from the trivial case
\(a=0\). Hence merely repeating one unequal gain ratio can remain singular. Varying the inverse-gain
difference is the relevant protection against an unknown diagonal reciprocal contrast.

The raw worst-case first-order excitation has a closed form:

\[
 \xi_n^2(\delta)=\frac1n\sum_{t=1}^n w_t^2(\delta-d_t)^2,
\]

and

\[
 \inf_{\delta\in\mathbb R}\xi_n^2(\delta)
 =\frac1n\sum_{t=1}^n w_t^2(d_t-\bar d_w)^2,
 \qquad
 \bar d_w=\frac{\sum_t w_t^2d_t}{\sum_t w_t^2}.
\]

Thus two distinct inverse-gain differences with nonzero weights are necessary and sufficient to
avoid exact cancellation uniformly over \(\delta\) in this restricted two-channel submodel. This is
not a general optimal-design theorem: the likelihood also weights environments by their baseline
precision, and unknown \(K\), off-diagonal reciprocal feedback, stability margins, intervention
costs, and nuisance estimation change the efficient information. It is, however, a decisive
counterexample to every gain-only rank score.

## 4. The weak-design phase boundary survives with a corrected contrast

Let

\[
 q_t(a)=(1-p_1g_{1t})(1-p_2g_{2t})+a^2w_t.
\]

For independent samples the exact total sign divergence is

\[
 \sum_{t=1}^n\frac{2a^2c_t^2}{q_t(a)^2}.
\]

On a compact stable parameter set where the denominators and gains are bounded away from zero and
infinity, the divergence from \(a=0\) is of order

\[
 n\{a^2\xi_n^2+a^4\}.
\]

The \(a^2\xi_n^2\) term carries signed orientation; the \(a^4\) term carries magnitude when the
linear score disappears. The two-point separation scale is consequently

\[
 r_n\asymp
 \begin{cases}
  (\sqrt n\,\xi_n)^{-1}, & \xi_n\gg n^{-1/4},\\
  n^{-1/4}, & \xi_n\lesssim n^{-1/4}.
 \end{cases}
\]

This is still a lower-bound/testing scale, not an achieved estimator rate. The correction is that
\(\xi_n\) must be computed from the joint gain--reciprocity contrast \(c_t\), not from
\(g_{1t}-g_{2t}\) alone. A design can look well separated in raw gains and nevertheless sit exactly
at the singular boundary.

## 5. General local geometry

For \(K=I\), decompose the feedback into reciprocal and circulatory parts,

\[
 \Phi=P+Q,
 \qquad P^\top=P,
 \qquad Q^\top=-Q.
\]

The precision is

\[
 \Omega_D
 =I-DP-PD+DQ-QD
  +D(P^2+PQ-QP-Q^2)D.
\]

At a reciprocal base point \(Q=0\), the derivative in a skew direction \(U\) is the symmetric
operator

\[
 \mathcal L_{D,P}(U)
 =[D,U]+D[P,U]D.
\]

The first term is the relative-gain commutator found previously; the second is the missing
gain--reciprocity interaction. With common gains \(D=sI\),

\[
 \mathcal L_{sI,P}(U)=s^2[P,U].
\]

In an eigenbasis of \(P\), its pairwise signal is

\[
 s^2(p_i-p_j)U_{ij}.
\]

Simple reciprocal spectrum makes common gain locally informative about skew directions, whereas
repeated reciprocal eigenspaces contain first-order orientation nulls.

For general innovation precision, write \(H=K\Phi=P+Q\) with symmetric \(P\) and skew \(Q\).
The corresponding derivative is

\[
 \mathcal L_{K,D,P}(U)
 =DU-UD+D(PK^{-1}U-UK^{-1}P)D.
\]

Under common gain, congruence by \(K^{-1/2}\) turns the second term into the commutator between the
whitened reciprocal and circulatory components. The correct local diagnostic is therefore a
nuisance-projected smallest singular value of the stacked operators over environments. A condition
number of the gain matrix alone is not an identification diagnostic. The present note does not
derive the nuisance projection or prove full joint identification.

## 6. Direct-parent collision audit

| Proposed contribution | Primary parent | Consequence |
|---|---|---|
| Identify a drift matrix from stationary covariance under graph restrictions | [Dettling et al. (2023)](https://doi.org/10.1137/22M1520311) | Global covariance identification in continuous Lyapunov models is characterized by graph simplicity; directed two-cycles are already a canonical obstruction. |
| Recover cyclic dynamics from several stationary intervention laws | [Zweig et al. (UAI 2026)](https://proceedings.mlr.press/v337/zweig26a.html) and [Salehkaleybar (ICML 2026)](https://openreview.net/forum?id=vjI9tsebtP) | Tight intervention-count bounds, generic recovery, a regularized estimator, and unseen-intervention prediction occupy the broad theorem-and-algorithm claim. |
| Determine the sign rather than the full coefficient | [van Seeventer and Salehkaleybar (UAI 2026)](https://proceedings.mlr.press/v337/seeventer26a.html) | Sign/non-sign/partial-identifiability is already a named stationary-dynamics target with graph criteria and explicit formulas. |
| Design interventions adaptively in cyclic linear systems | [Sharifian et al. (NeurIPS 2025)](https://proceedings.neurips.cc/paper_files/paper/2025/hash/5c1188ceaf1c61646a549062b1279729-Abstract-Conference.html) and [Mokhtarian et al. (JMLR 2023)](https://www.jmlr.org/papers/v24/22-1425.html) | Worst-case experiment counts and near-optimal adaptive design are occupied. Our inverse-gain variance is a narrow model-specific score, not a new general design framework. |
| Escape covariance singularity with non-Gaussian observations | [Recke et al. (2026)](https://arxiv.org/abs/2601.21818) and [Recke and Hansen (2026)](https://arxiv.org/abs/2603.17142) | Higher-order cumulants already give generic/local identification and semiparametric estimation in discrete and continuous Lyapunov models. Non-Gaussianity is an additional identifying assumption, not a free repair. |
| Define scaling interventions in a cyclic SCM | [Saha et al. (NeurIPS 2025)](https://proceedings.neurips.cc/paper_files/paper/2025/hash/bc766279695d2333e91963b2997172e6-Abstract-Conference.html) | Shift--scale interventions already have contractivity, composition, and counterfactual theory. Their scaling acts on a target mechanism and its disturbance, unlike the present known outgoing-column gain, so the exact algebra is not identical but the broad intervention label is occupied. |
| Learn across stationary interventional densities | [Lorch et al. (AISTATS 2024)](https://proceedings.mlr.press/v238/lorch24a.html) | Cross-environment stationary-diffusion fitting and unseen-intervention generalization are established; unrestricted stationary generators remain nonidentified. |

The exact cancellation manifold and corrected \(n^{-1/4}\) boundary were not found verbatim in
this primary-work screen. The surrounding scientific territory is nevertheless saturated. A paper
whose main algorithm maximizes inverse-gain variance would be a model-specific optimal-design
specialization with no external truth asset, not an ICLR-level advance.

## 7. Hostile assessment

The result is scientifically valid and reusable, but the standalone topic is killed for five
independent reasons.

1. **Scope:** the sharp theorem is a two-channel, known-\(K\), diagonal-reciprocal submodel. The
   general operator is only a local calculation, not necessary-and-sufficient joint identification.
2. **Parent saturation:** stationary-dynamics identification, sign identification, intervention
   counts, adaptive cyclic experiment design, and higher-cumulant recovery all have recent direct
   papers, including ICML/NeurIPS results.
3. **Assumption substitution:** invoking independent non-Gaussian innovations can break the
   covariance ambiguity, but this changes the model and lands directly in higher-cumulant/ICA
   territory. Financial heavy tails do not imply the required independent anisotropic sources;
   spherical heavy-tailed innovations preserve the ambiguity.
4. **Market bridge:** disclosed or estimated market gains are not randomized mechanism controls,
   reciprocal background is unknown, and gain-conditioned innovation drift makes every stable
   feedback matrix observationally equivalent as proved in the parent audit.
5. **Truth and architecture:** no external system supplies the same per-column gain action and
   signed nonreciprocal truth. EcoMD's current conservative force Jacobian is reciprocal and cannot
   validate a circulatory recovery claim that would have to be planted into a new architecture.

No recorded blocker is removed. The theorem improves the failure map and prevents a false-positive
design diagnostic; it does not authorize a candidate, experiment, implementation, or compute.

## 8. Exact re-entry boundary

Revisit this child only if one frozen package supplies all of the following:

1. necessary and sufficient joint identification with unknown \(K\), reciprocal nuisance, arbitrary
   gain support, sparsity and temporal dependence;
2. nuisance-efficient information and matching lower/upper bounds through simultaneous weak gain,
   weak reciprocity-spectrum and weak non-Gaussianity regimes;
3. uniformly valid confidence sets and abstention, including exact cancellation and
   gain-conditioned innovation-drift sensitivity;
4. a theorem or algorithm irreducible to Lyapunov identification, ICA/higher cumulants, cyclic
   intervention design, conditional graphical regression, or generic weak-identification methods;
5. two independent same-estimand controlled systems with known per-channel gains, quantitative
   signed nonreciprocal truth, complete lifecycle state, reuse rights, and untouched confirmation.

Until then, all three authorized GPU workers remain idle for this direction.
