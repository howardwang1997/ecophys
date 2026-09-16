# Paper G: gradient-reliability primary comparison and scope audit

PRIVATE / INTERNAL. Paper-only development audit, not public research evidence.
Started 2026-09-09T10:08:17Z. Previous goal turn: progress, verified against the
current HydroGym receipt, manifest and canonical registries.

## Decision

**Not a qualified trigger.** The new primary comparison does not overturn an
existing gradient-method reduction or supply a matched physical disagreement.
It makes the next required contribution more precise: a gradient reliability
claim needs an explicit target, sampling law, support/tail restrictions and
finite-cost guarantee. A sample diagnostic or variance-weighted mixture alone
does not establish that contribution. No candidate harvesting or new cycle.

Repository connection: the history-response route concerns derivatives and
controlled response of learned PDE dynamics. The previous HydroGym preflight
adds a possible controlled-flow development interface. The closed invariant
calibration route additionally records `no_new_variance_cost_result`. This
audit checks a new upstream method against those blockers; it does not replace
the Paper G objective with a robotics benchmark or reopen either closed route.

## What the primary works actually disagree about

[Suh et al., ICML 2022](https://proceedings.mlr.press/v162/suh22b/suh22b.pdf)
already separate discontinuity bias, rare-gradient finite-sample behavior and
high gradient variance. Their empirical-bias definition describes samples
appearing misleadingly concentrated, including unbiased smooth cases; it does
not assert that every continuous simulator gradient is biased in expectation.
Selected Sections 2–3, Lemmas 3.1–3.5 and Appendix C assumptions were rechecked.

[Onoda et al., arXiv v1, 20 April 2026](https://arxiv.org/html/2604.18161v1)
reassess that method and present DDCG and stepwise inverse-variance mixing.
They retain the rare-gradient phenomenon. Their practical variance-control
finding concerns the studied robotics tasks, whereas the controlled examples
also examine switching estimators. Sections 1–4 and Appendices B–C were read;
other returned passages were not promoted to independently verified results.
[Official ICLR 2026 proceedings](https://proceedings.iclr.cc/paper_files/paper/2026/hash/4f0a2a0b2ca6ffd5c8d5de26d3e8d54d-Abstract-Conference.html)
confirm the venue; the arXiv text is the inspected technical version.

This is a methodological reassessment with direct overlap in some benchmark
settings, not evidence of opposite true gradients under one frozen fluid state,
policy/noise law, action, reward and horizon. Neither work predicts universal
dominance of one estimator. HydroGym's control benefits are compatible with
regimes where pathwise gradients are useful and others where they are noisy.
No performance numbers, source implementation behavior or correction narrative
is used to establish our scientific conclusion.

## Control A: exact population inequality

Specify a scalar return function \(f\), Gaussian smoothing input
\(X\sim N(\mu,\sigma^2 I_d)\), \(\sigma>0\), and
\(f\in H^1(\gamma_{\mu,\sigma})\). Thus the function and its weak gradient
have finite Gaussian second moments. Define

\[
m=E\nabla f(X),\quad V_f=\operatorname{Var}f(X),\quad
V_g=E\|\nabla f(X)-m\|^2.
\]

The exact inequality is

\[
Q(f):=V_g+2\|m\|^2-\frac{2V_f}{\sigma^2}\ge0. \tag{1}
\]

**Proof and direct parent.** Gaussian integration by parts makes
\(h=f-Ef-m\cdot(X-\mu)\) orthogonal to constant and linear Gaussian modes.
Its variance is \(V_f-\sigma^2\|m\|^2\), and
\(E\|\nabla h\|^2=V_g\). The refined Gaussian Poincaré inequality gives
\(\operatorname{Var}h\le\sigma^2 V_g/2\), proving (1). The needed result and
Hermite proof appear explicitly in
[Lehec (2008), Lemma 2.3, pp. 360–361](https://www.numdam.org/article/AFST_2008_6_17_2_357_0.pdf).
The extension from smooth functions to Gaussian \(H^1\) uses density in that
norm. This is a classical reduction, not a new inequality.

More precisely, expand \(f(\mu+\sigma z)=\sum_\alpha f_\alpha H_\alpha(z)\)
in orthonormal multivariate Hermite polynomials. Then

\[
Q(f)=\frac1{\sigma^2}\sum_{|\alpha|\ge3}(|\alpha|-2)f_\alpha^2. \tag{2}
\]

Equality holds exactly for polynomials of total degree at most two in Gaussian
\(L^2\). For one coordinate, the normalized cubic
\(f=(z^3-3z)/\sqrt6\) has \(V_f=1\), \(m=0\), \(V_g=3/\sigma^2\), so
\(Q=1/\sigma^2>0\). The normalized quadratic has \(Q=0\). Both satisfy (1).
Consequently its population validity does not require an isotropic quadratic
approximation, small curvature or short dynamical horizon.

Onoda's population form in Eq. 32 is (1) with the right-hand variance weakened
by a factor \(1-c\). For \(c\in[0,1]\), it follows from (1). This statement
concerns that population inequality only: it does not prove the empirical
gate, a confidence level, a mixture's mean-squared error, or any source
experiment. A passing necessary relation cannot establish its own regularity
and reliable-variance premises.

As an outside-class check, an indicator \(f=1_{x>r}\) has zero ordinary
derivative almost everywhere but positive variance. Substituting that ordinary
derivative into (1) gives a negative quantity. The indicator is outside the
Gaussian \(H^1\) class; its distributional derivative contains a boundary
term. This is the classical hard-event example already represented in the
ICML parent, not a counterexample to (1) or a new discontinuity detector.

For nonsingular covariance \(\Sigma\), whitening yields the invariant form

\[
E[(\nabla f-m)^T\Sigma(\nabla f-m)]+2m^T\Sigma m-2V_f\ge0. \tag{3}
\]

Changing input units requires transforming both gradients and the noise
covariance. Equation (3) is an affine change of coordinates, not an additional
method contribution. Do not transfer the isotropic formula to a different
sampling law, a stationary chaotic measure, or clipped physical actions without
specifying which Gaussian latent variable is being differentiated.

## Control B: a smooth support region missed by a finite batch

Consider a fixed batch of \(N\) independent samples from \(N(0,\sigma^2)\),
with access to each input, function value and exact derivative. Choose
\(r>h>0\) and a nonzero, nonnegative smooth compactly supported bump
\(\psi\) on \((-1,1)\). Compare functions fixed before sampling:

\[
f_0(x)=0,\qquad f_1(x)=A\psi((x-r)/h),\qquad A>0.
\]

Both are smooth and belong to Gaussian \(H^1\). Let
\(p=\Pr(X\in(r-h,r+h))\). On the event that no input enters this interval,
all recorded values and derivatives coincide exactly, with probability

\[
\Pr(E_N)=(1-p)^N. \tag{4}
\]

The gradients of their smoothed expectations at mean zero differ:

\[
d=\left.\frac{d}{d\mu}E_{N(\mu,\sigma^2)}f_1(X)\right|_{\mu=0}
=Ef_1'(X)=\frac{E[Xf_1(X)]}{\sigma^2}>0. \tag{5}
\]

The positivity follows from the positive support and nonnegative bump.
For \(f_0\), the same derivative is zero. On \(E_N\), the all-empirical
variance/mean quantities in the scalar gate are zero, so its stated inequality
passes for either function with any nonnegative variance floor. This says
nothing about subsequent zero-denominator handling or the implemented mixture.
Only the mathematical gate and the information in the observations are tested.

More generally, coupling the identical input samples shows that any
binary discriminator restricted to this batch has error probabilities satisfying

\[
e_0+e_1\ge(1-p)^N,\qquad
\max(e_0,e_1)\ge\tfrac12(1-p)^N. \tag{6}
\]

For both errors to be at most \(\delta<1/2\), a necessary sample condition is
\(N\ge\log(2\delta)/\log(1-p)\), of order
\(p^{-1}\log(1/(2\delta))\) for small \(p\). This is elementary
two-function indistinguishability, consistent with the existing rare-gradient
parent. It is not a new minimax theorem or a claim about the paper's task suite.

Scope matters: at fixed amplitude the mean-gradient gap can shrink with the
support mass. Keeping a fixed gap while shrinking support requires growing
amplitude and/or derivative bounds. A known uniform reward, gradient, curvature
or tail bound can therefore change the attainable accuracy and sample cost.
Analytic access to the complete function, deliberate targeted queries, and
additional state/support information fall outside this fixed-iid-batch result.
A nonnegative floor alone does not identify unseen support or bound its size.

## What a subsequent contribution must establish

The controls separate three questions: validity of a population identity,
reliability of its estimated moments, and accuracy/cost of the resulting
gradient or controller. None implies the next without assumptions. Frozen
finite-horizon smoothed return, an unperturbed policy objective, and long-run
invariant response also remain different targets.

Before re-entry, name the exact learned-dynamics or control contribution and
the prior blocker it removes. Freeze the objective and legal noise/action map;
the accessible oracle and all value/gradient/trajectory queries; a justified
tail or support class; the allowed error and failure probability; and the
cost of discovering rare regions. Include the existing composite-gradient
methods as baselines, accounting for estimator covariance and any reuse of
the batch to select weights. Those issues are already acknowledged in the
primary neighborhood and are not presumed novel here.

Both analytic controls are development assets. They do not supply an untouched
nonlinear-fluid confirmation partition, independent simulator replication,
field evidence, or a trained-model prevalence result. Previous source-cache
hashes were rechecked; no scientific code was imported or executed. No solver,
simulation, outcome file, checkpoint, GPU, participant, outreach, purchase,
publication, new question program, full hostile audit, forecast or machine card
was produced or accessed. Search-cycle, protocol and forecast bytes remain
unchanged. Operational verification belongs only in the private receipt.

Contract: `research/paper_g/gradient_gate_scope_audit_20260909.yaml`.
Re-entry record: `paper_g_gradient_gate_primary_scope_20260909`.
