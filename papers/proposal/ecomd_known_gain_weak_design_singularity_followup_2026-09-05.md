# EcoMD known-gain weak-design singularity follow-up

**Date:** 2026-09-05  
**Archetype:** `measurement_method`  
**Decision:** `partial_capability`  
**Candidate harvesting:** not authorized  
**Experiment, outcome access, SSH, and GPU status:** not authorized

## 1. Why this child was reopened

The preceding known-gain audit proved the population factorization

\[
 \Omega(\gamma)
 =K-D_\gamma H^\top-HD_\gamma+D_\gamma JD_\gamma,
 \qquad H=K\Phi,\qquad J=H^\top K^{-1}H,
\]

and exhibited an exact orientation ambiguity under co-trending gains. It left finite-sample and
weak-design theory as a possible escape. The cheapest hostile question is whether this escape is
merely ordinary polynomial regression, or whether the structural factorization creates a genuinely
singular statistical regime.

The answer is mixed. Strong-design estimation reduces to established covariate-dependent Gaussian
graphical regression followed by a smooth transformation. At the co-trending boundary, however,
the first-order information for circulatory feedback vanishes while a quadratic magnitude signal
remains. This yields an exact sign nonidentification and an (n^{-1/4}) local separation scale in a
two-channel submodel. That is a real theorem-shaped residue, but not yet a complete or irreducible
ICLR method.

## 2. Strong-design finite-sample reduction

For every off-diagonal entry, the unrestricted reduced-form precision regression uses the feature
vector

\[
 x_{ij}(\gamma)=(1,\gamma_i,\gamma_j,\gamma_i\gamma_j),
\]

whereas a diagonal entry uses

\[
 x_{ii}(\gamma)=(1,\gamma_i,\gamma_i^2).
\]

If each gain environment has enough replicates to estimate its precision, recovering the
coefficients (K,H,J) is a weighted finite-dimensional regression problem, up to precision-matrix
estimation error. If instead every observation has its own continuous gain vector, then

\[
 R_t\mid\gamma_t\sim
 \mathcal N\!\left(0,\Omega(\gamma_t)^{-1}\right)
\]

is directly a covariate-dependent Gaussian graphical model. It is not legitimate to pretend that an
individual outer product is an observed precision matrix, but conditional likelihood or
pseudolikelihood supplies the standard route.

Under a design bounded away from rank loss and well-conditioned (K), coefficient error transfers
to the structural matrix through

\[
 \widehat\Phi-\Phi
 =K^{-1}(\widehat H-H)
  -K^{-1}(\widehat K-K)\Phi+o_p(\|\widehat H-H\|+\|\widehat K-K\|).
\]

Thus a generic strong-design rate, sparse penalty, debiasing step, or Wald test is not the novel
part. Zhang and Li already regress subject-specific precision structure on covariates and prove
selection and convergence results; Meng, Zhang and Li add debiased estimators, asymptotic normality
and valid inference. Bicycle separately learns cyclic steady-state systems from intervention-labelled
i.i.d. samples and proves population identification under intervention designs. The possible residue
must therefore live at the singular design boundary or in a materially stronger structural theorem.

## 3. Exact two-channel singular submodel

Take a lower-bound submodel with known innovation precision (K=I_2) and purely circulatory
feedback

\[
 \Phi_a=aA,\qquad
 A=\begin{pmatrix}0&1\\-1&0\end{pmatrix},\qquad
 D_g=\operatorname{diag}(g_1,g_2).
\]

For sufficiently small (a), (I-Phi_aD_g) is invertible. Direct multiplication gives

\[
 \Omega_a(g)
 =\begin{pmatrix}
  1+a^2g_1^2 & a(g_1-g_2)\\
  a(g_1-g_2) & 1+a^2g_2^2
 \end{pmatrix},
 \qquad
 \det\Omega_a(g)=(1+a^2g_1g_2)^2.
\]

Three conclusions follow without an estimator or asymptotic approximation.

1. If (g_1=g_2=s), then
   \(Omega_a=(1+a^2s^2)I_2=\Omega_{-a}\). The sign of circulation is exactly
   nonidentified even with infinitely many observations.
2. At (a=0), the derivative of the precision is
   \[
    \left.\partial_a\Omega_a(g)\right|_{a=0}
    =\begin{pmatrix}0&g_1-g_2\\g_1-g_2&0\end{pmatrix}.
   \]
   The one-observation Gaussian Fisher information for (a) is therefore
   ((g_1-g_2)^2): absolute gain level supplies no first-order orientation information.
3. Let (P_{a,g}=\mathcal N(0,\Omega_a(g)^{-1})). The sign-discrimination divergence is exactly
   \[
    D_{\mathrm{KL}}(P_{a,g}\|P_{-a,g})
    =\frac{2a^2(g_1-g_2)^2}{(1+a^2g_1g_2)^2}.
   \]

The divergence from the no-feedback model is also explicit:

\[
 D_{\mathrm{KL}}(P_{a,g}\|P_{0,g})
 =\frac12\left[
 \frac{2+a^2(g_1^2+g_2^2)}{(1+a^2g_1g_2)^2}
 +2\log|1+a^2g_1g_2|-2
 \right].
\]

For gains near a nonzero common level and small (a), this is of order

\[
 a^2(g_1-g_2)^2+a^4.
\]

For (n) independent observations define the root-mean-square relative-gain scale

\[
 \eta_n^2=\frac1n\sum_{t=1}^n(g_{1t}-g_{2t})^2,
\]

with common gain levels bounded away from zero and infinity. A two-point Le Cam argument then gives
the local separation boundary from (a=0) by solving

\[
 n(\eta_n^2a^2+a^4)\asymp1.
\]

Consequently,

\[
 r_n\asymp
 \begin{cases}
  (\sqrt n\,\eta_n)^{-1}, & \eta_n\gg n^{-1/4},\\
  n^{-1/4}, & \eta_n\lesssim n^{-1/4}.
 \end{cases}
\]

This is a testing/separation lower-bound scale, not a claimed achieved estimation rate. In the
second regime, the (a^2) magnitude can become detectable while the sign remains indistinguishable:
the total (a) versus (-a) divergence is only of order (na^2\eta_n^2). At exactly
(eta_n=0), no amount of data recovers orientation.

## 4. General commutator geometry

The same phenomenon is not peculiar to two dimensions. Linearizing at (Phi=0) in a direction
(U) gives

\[
 D\Omega_0[U]
 =-D_\gamma U^\top K-KUD_\gamma.
\]

Write (G=KU). Under a common gain (D_\gamma=sI), every (K)-circulatory direction satisfying
(G^\top=-G) disappears to first order. With (D_\gamma=sI+E), its first-order signal is the
commutator

\[
 [E,G]=EG-GE,
 \qquad [E,G]_{ij}=(E_{ii}-E_{jj})G_{ij}.
\]

Thus the pairwise spectrum of relative gain, not the number of dates or the absolute gain level,
controls orientation information. The quadratic term
(D_\gamma U^\top KUD_\gamma) retains magnitude information and creates the singular transition.
This geometry suggests a useful design diagnostic: report the information separately on reciprocal
and (K)-circulatory tangent subspaces rather than one condition number that hides the
orientation-null directions.

## 5. Collision and novelty audit

| Proposed contribution | Direct parent or reduction | Consequence |
|---|---|---|
| One sample per gain-dependent precision matrix | Zhang--Li Gaussian graphical regression; Meng--Zhang--Li debiased graphical regression | Conditional likelihood, sparse rates, debiasing and ordinary strong-design tests are occupied. The exact quadratic structural constraint is narrower. |
| Cyclic graph learning from intervention-labelled equilibrium samples | Bicycle, plus the cyclic-intervention parents in the preceding audit | A broad “interventions identify cycles” headline is occupied, including population identification and unseen-intervention prediction. |
| Weak-design or nonstandard inference | Kaji's general weak-identification theory and the mature weak-GMM literature | Singular transformations, impossibility of regular inference and reduced-form-first analysis are not new by themselves. |
| (n^{-1/4}) boundary for co-trending gains | Exact submodel above | This particular commutator/quadratic boundary was not found as a stated result in the minimal primary-work screen, but it is currently only a lower-bound witness in a narrow submodel. |
| Overidentification test (J=H^\top K^{-1}H) | Nonlinear Wald/GMM specification testing | Standard calibration fails near the singularity; merely substituting a bootstrap or weak-GMM test is not an ICLR contribution. |

The key correction to the naive reduction is that an unrestricted graphical regression estimates
regular reduced-form objects such as a linear orientation signal and a quadratic magnitude signal.
Recovering signed circulatory feedback from them is a singular, sometimes set-valued transformation.
This is exactly the kind of setting where general weak-identification theory warns that conventional
Wald inference is invalid. The market-specific algebra can instantiate that theory, but it does not
yet exceed it.

## 6. Why this is not an experiment-ready ICLR topic

The result passes only a narrow theorem-shape test.

- It is a two-channel submodel lower bound. There is no matching estimator or uniformly honest
  confidence set across strong, weak and unidentified designs.
- Necessary and sufficient global identification for an arbitrary gain support, unknown (K),
  sparsity and temporal dependence remains open here.
- There is no demonstrated advantage over fitting the regular reduced-form precision coefficients
  and applying an identification-robust transformation.
- The gain-conditioned innovation exclusion remains untestable against unrestricted drift; an
  analyst-chosen drift radius would yield an analyst-chosen identified set.
- Current EcoMD is built from a scalar potential. Its instantaneous force Jacobian is a Hessian, so
  the purely circulatory linear direction used by this lower bound is not a truth-bearing component
  of the current conservative M0 architecture. Adding one would be a new modeling assumption, not a
  validation.
- No lawful external system presently supplies independently varied quantitative gains, complete
  output, signed coupling truth and untouched independent replication under this estimand.

The result therefore does not remove a recorded market-truth, same-estimand replication or
direct-parent blocker. EcoMD-generated gains and couplings would be useful only after activation as
an adversarial synthetic case; they cannot be the evidence that activates the claim.

## 7. Machine decision and exact re-entry boundary

**Decision:** retain the known-gain family as `partial_capability`, but do not authorize candidate
harvesting, implementation, outcome access, SSH or GPU work. The finite-sample branch is narrower
than first thought, yet still below an ICLR machine-card threshold.

Re-audit only after a frozen child delivers all of the following before a full neighborhood search:

1. necessary and sufficient identification in terms of the gain-support evaluation operator;
2. matching minimax lower and upper bounds over dimension, sparsity, temporal dependence, unknown
   innovation precision and a vanishing relative-gain spectrum, including the (n^{-1/4}) transition;
3. confidence sets and model checks with uniform coverage through sign nonidentification and bounded,
   externally justified innovation drift;
4. a strict separation from covariate-dependent graphical regression, Bicycle and generic
   weak-identification/GMM machinery; and
5. two independently governed controlled systems with quantitative gain and signed coupling truth,
   plus a lawful market bridge if a financial claim is retained.

Until that package or a qualifying truth asset appears, all three authorized workers remain idle for
this direction.
