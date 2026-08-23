# EcoMD observation-quotient T0 result — 2026-08-22

**Formal decision:** FAIL / closed at 2026-08-22T22:17:33+12:00

**Scope of closure:** the Q observation-quotient response card and the C intervention-preserving
coarse-graining card frozen in
`papers/proposal/ecomd_observation_quotient_t0_freeze_2026-08-22.md`.

**Not authorized:** market-outcome access, event-window statistics, paid or bulk market data, EcoMD training,
synthetic benchmark implementation, GPU use, or holdout access.

## Executive decision

Neither card has a T0-surviving theorem, certificate or algorithm. The literature audit contains 29 primary
works for Q and 32 for C. The analytic no-go construction is correct, but it reduces to established causal
non-identifiability, latent-state symmetry and absence of persistent excitation. The apparent gaps left by the
literature are conjunctions of desired properties, not exact mathematical results.

The route is therefore closed before metadata qualification, data acquisition or implementation. Combining Q
and C does not turn two failed exits into a contribution.

## Frozen-exit verdicts

| Exit | Verdict | Decisive reduction |
|---|---|---|
| Q0 — global functional identification | **FAIL / RED** | Global fibre constancy is the definition of point identification. The differentiable local form is a null-space/rank condition. Causal-effect, generator, mean-field-kernel and stationary-SDE sign-identification results occupy the nontrivial neighbouring cases. |
| Q1 — finite-sample response certificate | **FAIL / RED** | No precise interacting-system class, computable response set, uniform coverage statement or joint rate was produced. Existing work separately covers resolution-dependent distinguishability, partial/discrete IPS inference, mixing dependence and path-level partial observation. |
| Q2 — quotient-aware active design | **FAIL / RED** | Query-specific causal experiment design, intervention-count bounds and continuous-time active design already exist. The frozen finite-candidate problem is weighted set cover; its local continuous version is information/rank design. No new IPS-specific approximation or sample-complexity guarantee was derived. |
| C0 — cross-scale response-error theorem | **FAIL / RED** | Exact forced and filtered GLEs, coarse path-response theory, causal abstraction and interventionally consistent ABM surrogates cover the proposed primitives. A sum of memory, filtering, discretization and fit errors follows generically from triangle inequalities and is not a new dynamics-specific rate. |

## Analytic audit result

For

\[
A_\eta=
\begin{pmatrix}-a&\eta c\\\eta d&-b\end{pmatrix},
\qquad B=(0,1)^\top,
\qquad C=(1,0),
\qquad \eta\in\{-1,+1\},
\]

with $ab-cd>0$, isotropic noise and passive input $u=0$, let
$D=\operatorname{diag}(1,-1)$. Then $A_-=DA_+D$, $CD=C$, and the two observed continuous paths
$Y=CZ$ admit an exact pathwise coupling. Nevertheless,

\[
G_\eta(s)=C(sI-A_\eta)^{-1}B
=\frac{\eta c}{(s+a)(s+b)-cd},
\qquad
R_\eta=\frac{\eta c}{ab-cd},
\]

so an anchored intervention through $B$ has opposite response signs.

This establishes a useful permanent guardrail: passive aggregate path realism cannot by itself license a policy
response. It is not a publication-level theorem. Moreover, $DB=-B$. If the actuator sign is defined only by
the hidden coordinate, the apparent response reversal is a label/gauge artefact. A valid market intervention
must have actor, channel and sign semantics fixed outside the latent representation.

The exact two-point construction also gives, for responses $\pm r$ and any passive-data estimator
$\widehat\psi$,

\[
\max_\eta \mathbb E_\eta |\widehat\psi-\psi_\eta|\ge r,
\qquad
\max_\eta \mathbb E_\eta (\widehat\psi-\psi_\eta)^2\ge r^2.
\]

These are elementary two-point lower bounds for identical data laws, not a new minimax result.

## Why the narrow residual did not pass

A possible future problem can be described as response-only identification for an exchangeable diffusion or
jump system under a genuinely non-injective event observation and externally anchored, restricted actuators.
One could seek an operator coercivity condition, a dimension-stable finite-sample response set and matching
minimum-intervention lower and upper bounds without recovering the microscopic kernel.

That description did not pass this T0 because it lacks all of the following:

1. a declared stochastic model and observation class;
2. an explicit observation/response operator beyond abstract fibre notation;
3. a necessary-and-sufficient condition not reducible to rank, coercivity or observability;
4. a computable estimator or confidence set;
5. a uniform finite-sample statement and a matching lower bound;
6. a proof that the rate or condition is specific to non-injective interacting systems.

Similarly, the possible coarse-graining residual — protocol-uniform, finite-sample path-response upper and lower
bounds for a non-equilibrium learned reduction — is not an achieved result. It currently combines pieces of
Netz, Müller, causal abstraction, filtered GLE and interventional-surrogate theory.

## Binding consequences

1. Close Q0, Q1, Q2 and C0 in their present forms. Do not implement them, conduct a market-support audit for
   them, or relabel the intersection as novelty.
2. EcoMD remains infrastructure and a possible later stress test. It is not evidence for latent market forces,
   causal mechanisms or policy responses.
3. Any future market response claim must use an externally anchored intervention, declared support and a
   prospective response holdout. Passive fit is insufficient even if the whole observed path law matches.
4. Any coarse simulator used for decision support should be evaluated interventionally, but this is an
   evaluation requirement rather than the current paper contribution.
5. Return to problem selection. A new card may reuse the counterexample as a sanity test, but reopening requires
   a concrete theorem statement that survives the same nearest-work reduction before any data or compute.

## Evidence trail

- Freeze: `papers/proposal/ecomd_observation_quotient_t0_freeze_2026-08-22.md`
- Primary-work matrix: `papers/proposal/ecomd_observation_quotient_t0_prior_art_matrix_2026-08-22.md`
- Analytic derivations: `papers/proposal/ecomd_observation_quotient_t0_math_scratch_2026-08-22.md`
- Machine-readable gate: `configs/empirical_physics/ecomd_observation_quotient_t0_v1.yaml`

No empirical result was opened or generated in reaching this decision.
