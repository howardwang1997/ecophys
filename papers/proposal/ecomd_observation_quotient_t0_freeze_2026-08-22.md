# EcoMD observation-quotient T0 freeze — 2026-08-22

## Purpose

This gate asks whether aggregate observations of stochastic interacting systems leave a genuinely new,
theorem-level problem in identifying intervention responses or preserving them under coarse-graining. It runs
before market-outcome inspection, data purchase, simulator training or numerical benchmark construction.

The two candidate cards are:

- **Q — response identification on an observation quotient**;
- **C — intervention-response-preserving non-equilibrium coarse-graining**.

They are audited independently. They may be connected only after at least one passes its own novelty gate.
Combining two failed cards is not a PASS.

## Frozen objects

Let a latent stochastic system under protocol (u\in\mathcal U) have path law

\[
X_{0:T}\sim P_{\theta,u}, \qquad Y_{0:T}=H_\Delta(X_{0:T}),
\]

where (H_\Delta) may discard identities, aggregate agents or queues, bin event time, or filter the path. The
passive observational fibre is

\[
[\theta]_0=\{\theta':H_{\Delta\#}P_{\theta',0}=H_{\Delta\#}P_{\theta,0}\}.
\]

For a prespecified observable response (\psi_u(\theta)), point identification means that (\psi_u) is constant
on ([\theta]_0). This statement is a definition, not a theorem contribution. Likewise, choosing a protocol that
maximizes KL, total variation, Fisher information or another distance between candidate output laws is standard
model-discrimination/experimental-design machinery unless a new guarantee is proved for the frozen setting.

For coarse-graining, let (K_u^f) and (K_{\Delta,\bar u}^c) denote fine and coarse transition operators and
(R_\Delta) the restriction map. The diagnostic commutator is

\[
\mathcal E_{u,\Delta,m}(\mu)=D\!\left(
R_{\Delta\#}(K_u^f)^m\mu,
K_{\Delta,\bar u}^{c,m}R_{\Delta\#}\mu
\right).
\]

Writing this discrepancy, minimizing it, or calling it interventional consistency is not by itself new.

## First mandatory counterexample

T0 must begin with the hidden linear system

\[
\begin{aligned}
dZ_t&=-cZ_t\,dt+\sigma_z\,dW_t^z+u_t\,dt,\\
dY_t&=-aY_t\,dt+bZ_t\,dt+\sigma_y\,dW_t^y,
\end{aligned}
\qquad a,c,\sigma_z,\sigma_y>0,
\]

where only (Y), or any fixed linear temporal aggregation of (Y), is observed. Compare (b=+\beta) and
(b=-\beta), with stationary initialization under (u=0).

Under the passive protocol, the two observed path laws are identical: reflect (Z\mapsto-Z) and
(W^z\mapsto-W^z), so (bZ) and therefore the entire (Y) path are unchanged. Under the externally anchored
constant intervention (u_t=h>0), however,

\[
\mathbb E[Y_t]-\mathbb E[Y_0]
=\frac{bh}{c}\left[
\frac{1-e^{-at}}{a}-\frac{e^{-ct}-e^{-at}}{a-c}
\right],
\]

with the (a=c) value defined by continuity. The bracket is positive for (t>0), so the response signs are
opposite and the stationary responses are (\pm\beta h/(ac)).

This counterexample is a required sanity check, not a novelty result. If the intervention direction is defined
only through the latent coordinate, the sign difference is a relabelling gauge and the example is invalid. Every
later intervention must therefore have operational semantics fixed independently of the latent parameterization.

## Required primary-literature matrix

Reviews may route the search but cannot establish novelty. The matrix must contain at least 20 primary works for
each card and record exact object, assumptions, result, collision and residual gap.

### Q clusters

1. parameter, functional and sign identifiability under latent or partial observation;
2. stochastic interacting-particle and mean-field inverse problems;
3. stationary SDE causal models and interventional SDE identification;
4. aggregate snapshots, identity-free trajectories and event-process observation;
5. interventional Markov equivalence, partial identification and causal effect bounds;
6. active causal discovery, minimum-cost interventions and dynamical model discrimination;
7. simulator/ABM non-identifiability and interventionally consistent surrogates;
8. finite-sample inference under mixing and misspecified observation operators.

### C clusters

1. exact and approximate causal abstraction, including soft interventions;
2. Mori--Zwanzig and generalized Langevin projection;
3. nonequilibrium/external-force GLE and response theory;
4. coarse-grained linear and nonlinear response;
5. temporal filtering, sampling-induced memory and hidden-state memory;
6. path-space relative entropy/force matching and non-equilibrium transferability;
7. finite-time and long-time coarse-graining error bounds;
8. learned memory kernels, collective variables and multiscale stochastic models;
9. financial/order-book coarse-graining, memory and fluctuation--dissipation work.

Backward and forward citation neighbours through 2026-08-22 are required.

## Allowed exits

At least one exit must survive a nearest-five-result non-equivalence table. Application novelty or a verbal
combination of existing tools is ineligible.

### Q0 — global functional-identification theorem

Necessary and sufficient conditions identify a prespecified response functional from path-dependent aggregate
observations in a stochastic interacting system. The result must be more than “the functional is constant on the
observational fibre” and must not reduce to existing observability, interventional Markov equivalence, stationary-
SDE or partial-identification criteria.

### Q1 — finite-sample response certificate

A computable confidence set or abstention certificate has uniform coverage over a declared interacting-system
class and explicitly exposes dependence on trajectory length, mixing, number of agents, bin width and observation
loss. Point-estimation consistency under a correctly specified finite-dimensional state-space model is
insufficient.

### Q2 — quotient-aware active design

An algorithm selects physically available observations or interventions to identify only the target response,
not all latent parameters, with a guarantee for a continuous stochastic model class. A Fisher-information,
mutual-information, KL-separation, Bayesian-design or finite-set-cover objective without a new approximation,
sample-complexity or robustness result is a FAIL.

### C0 — response-error theorem across observation scales

A theorem decomposes unseen-intervention response error into memory truncation, observation/filter-induced
memory, stochastic-event discretization and learned-dynamics error, and yields a useful bound across unseen
resolutions. It must not be implied by approximate causal abstraction, path-space information inequalities,
existing coarse-grained response theory or generic Mori--Zwanzig truncation bounds.

## Immediate reductions that force FAIL

- the fibre-constancy criterion is presented as the main theorem;
- the hidden-OU counterexample is presented as the main result;
- minimal intervention choice reduces to test cover, set cover or standard optimal model discrimination;
- local identification reduces to a Jacobian/Fisher-information rank or tangent-space condition;
- the method requires a privileged latent sign, label or agent identity absent from the observation contract;
- a learned GLE, colored-noise model, path-relative-entropy fit or interventional loss is the contribution;
- EcoMD synthetic recovery is the only positive evidence;
- “first in finance”, “first differentiable implementation” or molecular-dynamics terminology carries novelty.

## PASS and stop rules

A card passes T0 only if all conditions hold:

1. one allowed exit survives the complete matrix and nearest-five non-equivalence test;
2. the exact mathematical statement, assumptions and failure case are written;
3. an analytic benchmark and two independent non-EcoMD system families are specified;
4. equal-budget baselines and a negative control can falsify the method-dependent claim;
5. outcome-blind metadata can support at least two independent real market interventions and a later frozen
   intervention;
6. the anticipated result would change which intervention response a simulator may legitimately report.

If neither card passes, close both before implementation and return to problem selection. Do not merge them into
a broader proposal, relax the venue burden or reopen a previously failed EcoMD route.

## Data and compute lock

Allowed: papers, official rule documents, schemas, event identities, dates and availability/licence metadata.
Forbidden: market outcomes, event-window statistics, paid data, bulk downloads, EcoMD training, synthetic
benchmark implementation and GPU use. The current GitHub D0 outcome embargo and all prior holdouts remain
unchanged.

The T0 review window is at most 14 calendar days. A first literature/reduction verdict is due before any
metadata-only market-support audit.
