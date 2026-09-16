# Paper G — unknown-nuisance gain identification

PRIVATE / INTERNAL. Paper-only derivation; no empirical or original-novelty claim.
Session 22 started 2026-09-10T19:02:34Z (07:02 NZST September 11).
Previous goal turn: progress. Decision: **not_trigger**.

## Question and scope

The September 5 reciprocity note expressly left nuisance-projected information
undeveloped. This follow-up resolves a two-channel local case and gives an exact
two-environment ambiguity. Varying inverse-gain differences can defeat the
fixed-nuisance sign cancellation while leaving direction unidentified when a
common innovation covariance and symmetric feedback are unknown. This changes
which experimental-design certificate is valid; it does not reopen a topic.

The repository connection is its existing coupled-feedback identification
program. This Gaussian equilibrium experiment is distinct from the richer
temporally separated/pre-window observations of the motivating output-only
paper. No contradiction of that paper's complete identification theorem or
empirical finding is asserted. Conservative EcoMD is not newly claimed to
supply physical circulatory truth.

For each observed gain environment `e`, independent samples have law

\[
X_e\sim N(0,\Omega_e^{-1}),\quad
\Omega_e=B_e^T K B_e,\quad B_e=I-\Phi D_e,
\quad D_e=\operatorname{diag}(g_{1e},g_{2e}).
\]

`K` is unknown positive definite but **the same across environments**. Gains
are known. Write

\[
\Phi=\begin{pmatrix}p_1&b+a\\b-a&p_2\end{pmatrix}.
\]

The physical-coordinate orientation target is `a=(Phi12-Phi21)/2`; nuisance
parameters are `p1,p2,b,K11,K22,K12`. Evaluate local information at `a=b=0,K=I`
with `alpha_ie=1-p_i g_ie !=0`. Observations are Gaussian and independent;
no temporal-dependence, non-Gaussian or arbitrary correlated-base theorem follows.

## 1. Exact local efficient information

Set `h_ie=g_ie/alpha_ie`, `s_e=h_1e+h_2e`, `d_e=h_1e-h_2e`. With
`k=delta K12`, the off-diagonal precision differential is

\[
\delta\Omega_{12,e}
=\alpha_{1e}\alpha_{2e}\{k-s_e\,\delta b+d_e\,\delta a\}.
\]

At this diagonal Gaussian base, the normalized score for a unit off-diagonal
change is a standardized product of the two independent coordinates. It has
variance one and is orthogonal to both centered-square scores for diagonal
precision changes. Consequently diagonal-parameter nuisances do not alter this
off-diagonal score projection. With `n_e>0` samples per arm, the exact local
efficient Fisher information for `a` is

\[
\boxed{I_{a,\mathrm{eff}}=
\min_{u,v\in\mathbb R}\sum_e n_e(d_e-u-vs_e)^2.}
\]

This is a weighted least-squares residual, including rank-deficient nuisance
designs through orthogonal projection; it is not an estimator or confidence
procedure. A positive unprojected sum `sum n_e d_e^2` is insufficient.

For two environments with distinct `s_e`, the two nuisance columns span all
two-arm score vectors, so efficient orientation information is zero. This
statement is generic, not universal: with equal `s_e` and unequal `d_e`, the
orientation score survives that projection. Other nuisance parameters may then
be unidentified; positive scalar efficient information alone does not establish
uniform inference through such a singular nuisance model.

For three environments, the off-diagonal three-parameter block has full rank
exactly when `(h_1e,h_2e)` are not collinear. This is a local rank criterion,
not a global minimum-intervention theorem or a certification from gains alone
when reciprocal parameters are unknown.

## 2. An exact two-arm ambiguity, beyond zero Fisher information

Choose `D1=I` and `D2=diag(2,3)`. Let

\[
J=\begin{pmatrix}0&1\\-1&0\end{pmatrix},\quad R_\theta=e^{\theta J},\qquad
\Phi_\theta=(I-R_\theta)(D_2-R_\theta)^{-1},
\]
\[
B_{1,\theta}=I-\Phi_\theta,\qquad
K_\theta=B_{1,\theta}^{-T}B_{1,\theta}^{-1}.
\]

For sufficiently small real `theta`, all inverses exist, `K_theta` is positive
definite, and both loop matrices are arbitrarily close to zero feedback.
In particular spectral-radius stability, if required, holds in a neighborhood.
The construction implies

\[
I-\Phi_\theta D_2=(I-\Phi_\theta)R_\theta,
\quad
\Omega_1(\theta)=I,\quad \Omega_2(\theta)=R_\theta^TR_\theta=I.
\]

Thus **every member of this curve has the identical two-arm observation law**,
with no gain-conditioned innovation drift. Within each member, its `K_theta`
is common to both arms. It varies between competing unknown-parameter models.

Expanding only to verify that the target changes,

\[
\Phi_\theta=
\begin{pmatrix}0&-\theta/2\\\theta&0\end{pmatrix}+O(\theta^2),
\qquad a_\theta=-3\theta/4+O(\theta^2).
\]

Small positive and negative `theta` therefore give opposite orientation signs
and zero KL divergence for every sample size. This is exact nonidentification,
not merely an `n^{-1/4}` separation regime. The inverse-gain differences of the
two arms are `0` and `1/6`, so the earlier restricted raw design score is positive.
For a direct algebraic check, writing `c=cos(theta),s=sin(theta)` gives
`Phi_theta=[[4(1-c),-s],[2s,3(1-c)]]/(7-5c)` and
`a_theta=-3s/[2(7-5c)]`; the sign change is explicit.
There is no contradiction: that result fixed `K=I` and restricted the symmetric
feedback to a diagonal matrix; this curve allows precisely the previously
unresolved common-noise and off-diagonal symmetric nuisances.

## 3. A local positive control

At `p1=p2=a=b=0,K=I`, append a third arm `D3=diag(3,2)` and use `n` observations
per arm. Now `s=(2,5,5)` and `d=(0,-1,1)`. The direction vector is orthogonal to
both nuisance columns, giving `I_a,eff=2n`.

The diagonal parameter blocks each have rank two, since each channel's gains
vary, and the off-diagonal block has rank three. The full seven-parameter
covariance map therefore has rank seven at this point. A nonsingular minor
and the inverse-function theorem give local joint identification. This does
not prove global uniqueness, optimal cost, a rate uniform near every singular
design, or performance of an estimation algorithm.

## 4. Keep physical and precision-weighted orientation distinct

The preceding general note also used `H=K Phi` and its skew component
`q=(H12-H21)/2`. Away from a known identity noise metric this is a different
target. At the base considered here,

\[
\delta q=\delta a+\tfrac12(p_2-p_1)\,\delta K_{12}.
\]

Using the symmetric part of `H12,H21` as nuisance instead yields

\[
I_{q,\mathrm{eff}}=
\min_{u,v}\sum_e n_e[d_e-u\,t_e-vs_e]^2,
\quad t_e=1+p_1h_{1e}+p_2h_{2e}.
\]

The three-arm full-rank criterion is again noncollinearity, since the map from
`(1,h1,h2)` to `(t,s,d)` is invertible. At zero reciprocal feedback the two
score formulas coincide; the exact ambiguity curve changes `q` to first order
as well. They must not otherwise be silently treated as the same estimand.

## Contribution and allocation

This fills a specified nuisance calculation and supplies an exact observational
twin under common unknown noise. Earlier fixed-nuisance KL lower witnesses stay
valid as submodel bounds; they are not achieved rates for this larger model.
The current result is elementary Gaussian score projection, Gram-factor
nonuniqueness and local rank theory. It is not certified as an independently
new scientific contribution, a high-dimensional/mixing minimax theorem, or a
uniform weak-identification method.

Existing direct-parent records remain applicable at their documented scopes:
[Kaji's weak-identification theory](https://doi.org/10.3982/ECTA16413),
covariate-dependent graphical regression, and
[cyclic experiment design](https://proceedings.neurips.cc/paper_files/paper/2025/hash/5c1188ceaf1c61646a549062b1279729-Abstract-Conference.html).
The latter uses non-Gaussian atomic interventions, so it is not asserted to
contain this exact Gaussian continuous-gain calculation. The motivating
[output-only paper](https://arxiv.org/abs/2608.25844v2) has additional temporal
moments; its theorem is not evaluated with these moments removed.

No route-level blocker is removed and no candidate cycle opens. Stop this
two-channel score/rotation follow-up. Re-entry requires a nonstandard result
beyond the recorded rank/information-design parents or a qualified truth asset;
another gain triple, normal-noise specialization or scalar rate calculation
alone is insufficient. No implementation or outcomes are authorized. The
full ICML/NMI/NCS Paper G objective remains unmet.
