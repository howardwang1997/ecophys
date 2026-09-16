# Paper G: stationary tail sensitivity and finite simulation horizons

PRIVATE / INTERNAL — paper-only truth-asset preflight, 2026-09-12.
Decision: `not_trigger`. No new topic, experiment, original theorem or removed
route-level blocker is claimed.

The named blocker is calibration of a population tail derivative from dependent
simulator paths, with a new bias/variance/cost result. This note checks whether a
dynamically generated tail supplies an analytic reference beyond the preceding
externally specified quantile examples. It does supply a restricted reference;
it does not supply a calibrated estimator or its novelty.

## 1. A native stochastic-recursion reference

Fix sigma > 0 and theta < 0. Consider iid standard normal Z_t and

\[
X_{t+1}=A_{t+1}X_t+1,\qquad A_t=\exp(\theta+\sigma Z_t),\quad X_0=0.
\]

Theta controls mean log amplification; sigma controls its dispersion. These are
coefficients of the transition law, not an analyst's tail metric or initial
quantile family. Random affine recursions are a financial-model parent class;
this particular lognormal recursion is a diagnostic, not a derived EcoMD model
or an assertion that market returns obey it.

For S_j=sum_{i=1}^j Z_i and S_0=0, put

\[
Y_m=\sum_{j=0}^{m-1}\exp(j\theta+\sigma S_j),\qquad
Y_\infty=\sum_{j=0}^{\infty}\exp(j\theta+\sigma S_j).
\]

At each fixed m, X_m and Y_m have the same distribution by reversal of the iid
coefficients. Their multi-time paths are not thereby identified. The strong law
makes the infinite sum finite almost surely. It satisfies the stationary affine
fixed-point equation, with the shifted remainder independent of the first A.

The log moment generating function is

\[
\Lambda_\theta(p)=\log E A^p=p\theta+\tfrac12\sigma^2p^2.
\]

Its positive zero and inverse are

\[
\alpha(\theta)=-2\theta/\sigma^2,\quad
\gamma(\theta)=-\sigma^2/(2\theta),\quad
\alpha'(\theta)=-2/\sigma^2,\quad
\gamma'(\theta)=\sigma^2/(2\theta^2).
\]

All required positive moments of A exist, log A is nonarithmetic, E log A < 0,
B=1, and no deterministic point is invariant under every A. The classical
stationary-tail result therefore gives P(Y_infinity > u) ~ C_theta u^{-alpha},
with C_theta > 0. The displayed derivatives are elementary derivatives of its
explicit exponent. They are not derivatives of a finite Hill expectation.

## 2. Fixed duration has a different asymptotic tail

For each fixed m and every p > 0, E Y_m^p is finite: it is a finite sum of
lognormal terms, using subadditivity for p <= 1 and the standard finite-sum
convexity bound for p > 1. Thus for every q > 0,

\[
u^q P(X_m>u)\le E[X_m^{q+1}]/u\longrightarrow0.
\]

Consequently X_m has no finite positive power-law exponent. More specifically,
for m >= 2, -log P(X_m>u)/log u tends to infinity. Taking m to infinity first
instead gives alpha. This is a noncommutation of duration and extreme-threshold
limits. It does not rule out accurate finite-threshold approximation or ordinary
consistency when duration and sample size increase together. All moments alone
are not used to assert any particular extreme-value domain of attraction.

## 3. An elementary joint horizon/threshold calculation

Let L=log u and m=floor(c L), with fixed c > 0. Write W_j=j theta+sigma S_j.
Since

\[
\exp(\max_{j<m}W_j)\le Y_m\le m\exp(\max_{j<m}W_j),
\]

a single Gaussian term gives a lower probability bound and a union bound gives
an upper bound with thresholds L and L-log m, respectively. Each W_j is normal
with mean j theta and variance j sigma^2. Gaussian tail logarithms, log m=o(L),
and a grid j/L in (0,c] yield

\[
-\frac{\log P(X_{\lfloor c\log u\rfloor}>u)}{\log u}
\longrightarrow J_\theta(c)
=\inf_{0<s\le c}\frac{(1-\theta s)^2}{2\sigma^2s}
=\begin{cases}
\dfrac{(1-\theta c)^2}{2\sigma^2c},&c<1/|\theta|,\\
-2\theta/\sigma^2,&c\ge1/|\theta|.
\end{cases}
\]

For completeness, the upper bound is at most m times the largest individual
Gaussian tail; minimizing its standardized squared threshold gives the displayed
infimum. The objective diverges as s decreases to zero, so the minimizing grid
points stay away from zero. For the lower bound choose j/L approaching
min(c,1/|theta|), with j <= m-1. Both bounds have the same logarithmic rate.
No independence between the W_j is required for this sandwich.

The stationary exponent can therefore already be wrong at logarithmic order
when c < 1/|theta|. At or above that boundary, exponent agreement alone does not
establish relative-error accuracy, Hill consistency, a parameter-uniform
derivative limit, or an efficient sampling algorithm. Near theta=0 the duration
coefficient diverges; a compact parameter domain bounded away from zero is a
substantive condition, not a cosmetic numerical choice.

Differentiating the explicit rate at fixed c gives
partial_theta J=(theta c-1)/sigma^2 below the boundary and -2/sigma^2 above it;
the derivatives match at the boundary. This algebra does **not** justify
interchanging a parameter derivative with the probability asymptotics.

## 4. Direct primary collision and decision

[Buraczewski, Collamore, Damek and Zienkiewicz (2016), *Large deviation estimates
for exceedance times of perpetuity sequences and their dual processes*, Annals
of Probability 44, 3688–3739](https://web.math.ku.dk/~jcolla/AOP1059.pdf)
already studies this parent problem. Section 2.1 states the affine stationary-tail
conditions; Lemma 2.1 identifies the conditional exceedance-time scale
rho=1/Lambda'(alpha); Theorem 2.1 gives sharper short-horizon asymptotics than
the logarithmic sandwich above. Here rho=1/|theta|. Positive B makes the backward
sum increasing, and fixed-time reversal connects its exceedances to X_m.
Selected statements and conditions were read in extracted primary text; the full
proof was not independently verified. The formulas above are a standard
specialization and elementary derivation, not an originality claim.

Retain the explicit stationary sensitivity and horizon diagnostic as a restricted
analytic control. A known lognormal law already permits direct calculation of
the target, so learning its exponent is not a competitive contribution by itself.
Neither the dependent-path gradient-calibration blocker nor the new
bias/variance/cost blocker is removed. Stop affine-recursion, lognormal and
horizon-threshold variants as standalone topic generators. Re-entry needs an
independently motivated nonstandard model or calibrated estimator result beyond
these primary parents, with an explicit equal-cost comparison. No candidate
harvesting or scientific execution follows from this record.
