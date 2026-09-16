# Paper G: noise cancellation and dynamical identification

PRIVATE / INTERNAL. Selected primary theorem-scope audit and elementary
development mathematics. Started 2026-09-09 11:20:33 UTC. Decision: `not_trigger`.
No new question program, cycle, forecast, machine card or experiment.

The relevant distinction is between recovering a conditional mean on states
visited during training and identifying a noise-free rollout that visits other
states. The new paper does not remove the recorded contribution blockers for
Paper G. The control below is reusable, but reduces to standard support and
rank identification; it is not a novel impossibility theorem.

## Primary scope

[Akashi et al., arXiv2606.26727v1](https://arxiv.org/html/2606.26727v1),
25 June 2026, studies reservoir reconstruction under changed noise intensity.
Theorem 1, printed pages 7-8, infers global approximation from a universal
memoryless reservoir and noisy regression, with an independent zero-mean noise
specialization. Appendix C, especially C10-C12 on page 14, supplies its proof.
Theorem and proof pages were also visually inspected in the original PDF.

Our scope finding is mathematical: universal representability does not ensure
identification by a particular training trajectory. The regression comparison
in C11 requires a condition eliminating an unobserved parameter component.
The independent decomposition below states that condition explicitly. We
interpret the noise assumption as genuine independent zero-mean innovations;
the conclusion does not depend on notation for sample correlations.

This audit does not refute the reported benchmark performance. Section 3.3
recognizes that noise can broaden state coverage, and Appendix B uses multiple
transient initial conditions in some training regimes. Noise-intensity
extrapolation in the conclusion requires knowledge of the noise law and entry
mechanism. The spin-torque oscillator in section 3.4 is an LLG simulation,
not independent measured-device confirmation. These protocols need separate
coverage and identification assessments.

[Lehtinen et al., Noise2Noise, ICML 2018](https://proceedings.mlr.press/v80/lehtinen18a.html),
section 2, equations 3-6, is a direct primary parent for conditional-mean
preservation under noisy regression targets. It is not a claim that dynamical
noise removal identifies unvisited states. For the present setting, the familiar
population calculation, with finite second moments and E[nu | Y]=0, is

\[
\mathbb E[(h(Y)-f(Y)-\epsilon\nu)^2]
=\mathbb E[(h(Y)-f(Y))^2]+\epsilon^2\mathbb E[\nu^2].
\]

This identifies an unrestricted optimal predictor only almost everywhere under
the training state law. An off-support rollout needs additional assumptions.

## Exact bounded control

Let the observed state space be Y=[-2,2], a=1/4, and

\[
f_\theta(y)=\theta(1-y^2),\qquad
\theta\in\{-a,0,+a\},\qquad
Y_{t+1}=f_\theta(Y_t)+\epsilon\nu_{t+1},
\]

where the innovations are independent equiprobable -1 and +1. Train at
epsilon=1 from Y_0=1. These are smooth bounded maps. For every y in Y,
|f_theta(y)| <= 3/4, so every permitted noisy update stays in [-7/4,7/4],
inside Y. The innovations have conditional mean zero given the entire past.

Because f_theta(-1)=f_theta(1)=0, every training state after the initial state
is an independent sign. All three systems have exactly the same full training
path law for every sample length, including an infinite record. Their noiseless
conditional mean on the visited support is the same.

Set epsilon=0 and start again from the same initial state 1. Then

\[
Y_1=0,\qquad Y_2=\theta.
\]

The first noise-free step leaves the training support, and the second step
distinguishes the three systems. For any common data-based prediction h(0),

\[
\max\{|h(0)-a|,|h(0)+a|\}\ge a.
\]

Coupling the identical training transcripts proves this pathwise inequality;
the maximum expected absolute risk across the two alternatives is also at
least a. More training at the original initial state cannot remove it.
The positive and negative alternatives each enter a contracting invariant
interval after the first noise-free step: [0,a] or [-a,0], with derivative
magnitude at most 2a^2=1/8. The obstruction does not require unstable rollouts.
This control is not a noise-induced bifurcation result or a reproduction of
any cited benchmark.

## The missing component in regression

Let phi(y) be a fixed d-dimensional feature column, let X contain the training
feature rows, and write the clean targets as f_X=Xw_*+r. Define
z=f_X+epsilon*v, w_hat=X^+z, and P=X^+X. For a uniform approximation error
at most delta, |f(y)-phi(y)^T w_*| <= delta and ||r||_infinity <= delta.
Direct algebra gives

\[
\begin{aligned}
f(y)-\phi(y)^T\widehat w
={}&[f(y)-\phi(y)^Tw_*]
+\phi(y)^T(I-P)w_*\\
&-\phi(y)^TX^+r-\epsilon\phi(y)^TX^+v.
\end{aligned}
\]

Consequently,

\[
|f(y)-\phi(y)^T\widehat w|
\le\delta(1+\|\phi(y)^TX^+\|_1)
+|\phi(y)^T(I-P)w_*|
+\epsilon|\phi(y)^TX^+v|.
\]

The middle term vanishes when the query feature lies in the row space of X,
or the true coefficient lies in that identified space; full column rank is
sufficient. Stable noise averaging further requires suitable excitation,
conditioning and stochastic convergence assumptions. Mean-zero innovations
alone do not supply those assumptions. A growing feature dimension also needs
control of approximation and conditioning together.

In the bounded example, choose phi(y)=(1,y,y^2)^T and
w_theta=(theta,0,-theta)^T. The representation is exact, but every training row
is (1,+1,1) or (1,-1,1). Thus Xw_theta=0 for every sample length, whereas
phi(0)^T w_theta=theta. The unidentified component survives arbitrarily much
training. The impossibility itself applies to any common data-based learner,
including universal feature families, rather than relying on polynomial
features being the exact reservoir architecture in the source paper.

## Resolving observation and stopping decision

Allow a new initial-state query at Y_0=0, still with epsilon=1. Its next state
is Z=theta+nu. Independent repeated resets therefore give a sample mean with
expectation theta and variance 1/N. With the two original state types, this
additional query type makes the polynomial design full rank. This is an
ordinary identification control, not a new experimental-design method. In the
stipulated discrete family with exactly known Rademacher noise, even individual
observations have disjoint supports across alternatives; the sample-mean
calculation is not a sample-complexity lower bound or claim that replication
is necessary for identification.

This resolves the declared fixture by adding target-relevant state access.
It does not prove that arbitrary unknown dynamics can be reconstructed from
one new reset. Nor does the absence of clean targets itself cause failure:
noisy targets at appropriate states can suffice under stated assumptions.

For future evidence, freeze the state and observation map, training initial
law, noise-entry mechanism, innovation conditioning, feature/excitation
conditions, target noise setting, reachable query states and horizon. Count
reset and intervention access explicitly. Require a reference protocol with
those capabilities and a substantive contribution beyond noisy regression,
off-support diagnosis and correctly labelled augmentation.

No current source qualifies such a new contribution, finite-sample cost result,
or independent confirmation asset. The saturated history/response parent stays
closed. The next useful trigger would remove that recorded blocker, rather
than rename it as denoising or tipping prediction. Selected paper reading and
these development controls are not independent confirmation evidence.

Structured record: `research/paper_g/noise_cancellation_support_audit_20260909.yaml`.
