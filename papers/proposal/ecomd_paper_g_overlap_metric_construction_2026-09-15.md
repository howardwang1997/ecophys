# Paper G: a constructive test for truncated overlap reconstruction

PRIVATE / INTERNAL — 2026-09-15. Exploratory derivation; excluded from public evidence.

The existing g41 route now has a specific analytic stress case for its approximation target. Exact nearest-neighbor overlaps can coexist with a finite coherent-dynamics error when long-range overlaps are reconstructed by linked products and combined with a dense kinetic operator. This is a hand-derived model result, not a claim about an observed molecular experiment or an independently established new theorem. It does not yet demonstrate a learning advantage. The route remains parked.

## New direct comparator

[Xie and Gu, arXiv:2501.05003v1 (9 January 2025)](https://arxiv.org/html/2501.05003v1), selected sections II–III, construct distant overlaps from nearest-neighbor products. Their projector expansion explicitly identifies discarded complementary-subspace terms; completeness makes the product exact. Their two-dimensional Shin–Metiu calculation reports close dynamical agreement despite some long-range overlap differences. This is a direct inexpensive comparator, not an all-pairs calculation. The published example is preserved as development evidence; its finite-time results are not contradicted by the different model below. Main-text formulas and reported settings were read, not code, raw matrices, or numerical figure values. No later-version parity is asserted.

The original [Gu LDR work](https://arxiv.org/html/2304.04369v1) remains the existing operator parent. Reopening that page is not counted as a new work or deeper audit. Earlier Procrustes/KRR, diabatic fitting, factorized propagation and exact-rank landmark comparisons remain required.

## C1: a finite geometric term behind small overlap errors

Let c = hbar²/(2M), and retain the normalized real electronic vector

\[
u(x)=(\cos\theta(x),\sin\theta(x)).
\]

For a smooth nuclear amplitude psi with compatible boundaries, direct differentiation gives

\[
\langle u,-c\partial_x^2(u\psi)\rangle
=-c\psi''+c(\theta')^2\psi.
\]

Here u·u'=0 and u·u''=−|u'|². The geometric scalar is an established projected-kinetic/Born–Huang term. It is not a newly discovered physical effect. A spatially varying theta' gives a spatially varying effective potential, rather than merely a global phase.

On a nearest-neighbor central-difference grid, the exact overlap is cos(theta(x+h)−theta(x)) = 1−h²(theta')²/2+O(h³). Replacing a positive scalar overlap by its unitary polar factor 1 discards the finite geometric potential after multiplication by the kinetic scale h^−2. This illustrates why small raw overlap errors are not by themselves an accuracy contract. It does not allege that the linked-product paper unitarizes its links: the construction below uses the actual unmodified links.

## C2: exact links, linked products and dense kinetics

Use the infinite uniform grid x_n = nh and a rotating retained vector u_n=(cos(anh),sin(anh)), a>0. Define the nuclear kinetic operator by

\[
T_0=\frac{c\pi^2}{3h^2},\qquad
T_k=\frac{2c(-1)^k}{h^2 k^2}\quad(k\ne0).
\]

Its Fourier symbol is cp² for |p|<pi/h. This explicitly defined sinc-grid operator fixes the discretization and avoids any claim about all DVR choices. The exact overlap is A_k=cos(akh). Products of exact nearest-neighbor links instead give

\[
\widetilde A_k=q^{|k|},\qquad q=\cos(ah),\quad 0<ah<\pi/2.
\]

Both are positive-semidefinite Gram kernels with unit diagonal. Thus Gram positivity and perfect nearest-link fitting do not remove this example. Compare the Hermitian projected generators K_k=T_k A_k and Ktilde_k=T_k Atilde_k, with the same retained subspace and zero retained potential. This is a generator comparison; it is not an identification of a finite Strang-compressed propagator with the exponential of a compressed generator.

For a fixed momentum p with |p±a|<pi/h, the exact symbol is

\[
\lambda_h(p)=\tfrac12[c(p+a)^2+c(p-a)^2]=c(p^2+a^2).
\]

The linked symbol is

\[
\widetilde\lambda_h(p)=\frac{c}{h^2}
\left[\frac{\pi^2}{3}+4\operatorname{Re}\operatorname{Li}_2(-q e^{iph})\right].
\]

This follows directly from the absolutely convergent series defining Li_2 for q<1. At q=1, the bracket is p²h². Also

\[
\partial_q\operatorname{Li}_2(-q e^{iph})
=-\frac{\log(1+q e^{iph})}{q},\qquad
q-1=-a^2h^2/2+O(h^4).
\]

The derivative and its next derivative are bounded near q=1 for p in any fixed compact momentum interval as h→0. Taylor expansion therefore yields, uniformly on that interval,

\[
\widetilde\lambda_h(p)
=cp^2+2ca^2\log2+O(h^2),
\qquad
\widetilde\lambda_h-\lambda_h
\longrightarrow ca^2(2\log2-1).
\]

This is a finite error in the geometric energy even as the grid spacing vanishes. Its relevance is limited to the explicitly stated generator, overlap approximation, subspace and order of limits. It is not an empirical failure of the published Shin–Metiu case, nor a statement about an untruncated electronic basis.

To expose an observable consequence rather than an unobservable scalar shift, add a second retained state e_3 in an orthogonal ambient direction, with constant retained energy Delta. These states arise from the smooth three-level electronic Hamiltonian H_e(x)=Delta e_3 e_3^dagger + G w(x)w(x)^dagger, where w(x)=(-sin(ax),cos(ax),0) and G>Delta>0. Retain u(x) and e_3, and omit w(x). Cross-state overlaps vanish; the exact global Gram rank is three. Prepare the same normalized, compact-momentum-support nuclear packet in both retained channels with amplitudes 1/sqrt(2). Measure the bounded, channel-swap observable in this declared local frame. Its exact expectation is cos[(ca²−Delta)t/hbar]; the linked limit is cos[(2ca² log2−Delta)t/hbar]. This defines a legitimate observable of the projected model. It is not a claim about an arbitrary laboratory measurement or the dynamics of omitted states. Compact momentum support supplies normalizable wavepackets; isolated nonnormalizable plane waves are used only to obtain operator symbols.

An essential counter-control: with a three-point finite-difference kinetic operator, only exact nearest links enter. Both constructions then give exactly the same discrete generator and converge to cp²+ca². The defect is therefore the interaction between long-range reconstruction and the declared kinetic stencil, not a universal failure of link-based methods.

## A concrete learning target, and why it is not yet a contribution

For the existing overlap-factor learner, replace an unweighted edge loss by the explicitly defined operator-action objective

\[
L=\mathbb E_{\psi\sim\mu}
\|[(T\odot\widehat A)-(T\odot A)]\psi\|^2,
\]

where the product multiplies each electronic overlap block by the corresponding nuclear kinetic entry. Fix the packet distribution mu, electronic reference, geometry labels and kinetic discretization. Under a simultaneous unitary gauge transformation of factors, reference overlaps and packets, the objective is invariant. It is implementable only when the required reference actions can be obtained; sparse edge labels do not supply them for free. Full-space operator error controls propagation through the standard Duhamel bound ||Uhat(t)−U(t)||≤|t| ||Hhat−H||/hbar for the bounded finite-grid Hermitian operators. A packet-averaged loss alone does not imply that uniform bound or control all evolved packets.

This specifies an operation and a failure regime, but weighted regression/operator fitting is not by itself new. The rank-three example is exactly recoverable from three independent Gram columns using the already recorded landmark baseline. Even a formula-based correction can solve this special family. Consequently, success on this toy cannot establish a neural advantage.

The next decisive contribution check is whether a specified learned factor/residual model, trained across a declared family, needs fewer expensive electronic-reference queries than kinetic-aware landmarks, overlap-informed KRR and linked products at matched coherent error, after including training and reuse cost. Those comparators must receive the same labels and can use the same kinetic-aware loss. A molecular reference and a plausible transferable structure remain unresolved. No numerical benchmark, outcome acquisition or implementation is authorized by this record.

One new primary work; two analytic controls with a stencil counter-control and an explicit prospective objective; zero new formulations, cycles, forecasts or cards. No F2/F3. g41 remains parked, now with a concrete discretization-dependent stress family and a stronger direct comparator. The ICLR/ICML goal remains incomplete.
