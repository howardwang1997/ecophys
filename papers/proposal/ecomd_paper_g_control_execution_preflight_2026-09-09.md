# Paper G: physical control and executed-law preflight

**PRIVATE / INTERNAL — discovery infrastructure; not public research evidence.**

Session began 2026-09-09T06:53:28Z. Structured record:
`research/paper_g/control_execution_preflight_20260909.yaml`.

**Decision: partial source capability, zero removed blockers; no new candidate.**
Controlled PDE benchmarks supply a more concrete action interface than an
unspecified forecast perturbation. However, joint trajectory guidance, actual
execution, stochastic optimism and policy-shift calibration have direct parents.
The exact checks below retain their value as controls, without establishing a
new method or a failure of a published implementation. This is source intake
following the closed physical-history formulation, not another topic cycle.

## Repository connection and scope

Paper D's conservative PDE surrogates provide the repository connection. Its
scope was read; no trajectories, checkpoints or result arrays were accessed.
The named blocker is the absence of a contribution beyond existing sensitivity
and generic remedies (`generic_sensitivity_and_history_nuisance_remedies_have_direct_prior`).
This preflight asks whether a controlled physical source supplies a capability
that removes that blocker. It does not revise the closed history formulation,
apply a market-specific closure to all PDE control, or change Paper D evidence
roles. No same-state, same-action primary model disagreement is established.

## Primary-work contracts

| Primary source and inspected scope | Established capability | Relevant boundary |
|---|---|---|
| [DiffPhyCon, NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/file/07a363fd2263091c2063998e0034999c-Paper-Conference.pdf), sections 2–3, selected evaluation descriptions and appendix L | Joint trajectory/control generation, objective guidance and explicit control-prior reweighting; evaluation executes controls in a numerical simulator. | Generated-state error versus the trajectory obtained from generated controls is already measured. Merely adding an execution comparison or removing the action prior is not new. |
| [SafeDiffCon](https://arxiv.org/pdf/2502.02205v4), sections 4.1–4.3 and selected appendix A | Uses calibration residuals for safety, post-training and inference-time adaptation of a diffusion controller. | This reading is arXiv v4, June 24, 2026; its ICML 2025 venue was separately verified. Versions are not assumed identical. We do not independently certify its implementation or coverage. |
| [Levine 2018](https://arxiv.org/pdf/1805.00909), sections 2.3–3.2 | Exact control-as-inference can condition stochastic transitions on favorable outcomes; fixing the true dynamics gives a structured variational control problem. | The stochastic optimism mechanism and fixed-dynamics remedy directly occupy the broad claim considered here. |
| [Tibshirani et al., NeurIPS 2019](https://papers.neurips.cc/paper_files/paper/2019/file/8fb21ee7a2207526da55a679f0332de2-Paper.pdf), section 2, equation 6 and Corollary 1 | Weighted conformal coverage under covariate shift, with unchanged response kernel and target/source covariate density ratio. | Target support, dependence, score construction and probability masses are part of the theorem. Marginal coverage is not uniform conditional safety. |
| [Zhang, Shi and Luo, AISTATS 2023](https://proceedings.mlr.press/v206/zhang23c.html), primary abstract only | Conformal prediction for a target policy's return using a pseudo-policy resampling construction. | Broad off-policy prediction is occupied. No detailed theorem or finite-horizon PDE guarantee inferred from the abstract. |
| [Rahaman et al., L4DC 2026](https://proceedings.mlr.press/v331/rahaman26a.html), primary abstract only | Conditional generative environment priors, nuisance-parameter adaptation, robust conformal regions and MPC. | Broad generative planning plus robust calibration under environment shift is occupied; a complete equivalence to the present setup is not asserted. |

These are four selected mathematical/method readings and two abstract-level
boundary records, not a full fifteen-work hostile audit. SafeDiffCon explicitly
motivates calibration by predicted-versus-actual safety differences; it must not
be described as oblivious to execution. The following stochastic fixture is a
declared mathematical system, not evidence about its benchmark outcomes.

## Check A: which probability law can the controller change?

Fix the full initial state. Let the behavior action law be mu(da), and let the
physical conditional trajectory kernel be K(du|a). Assume a perfect model of

\[
p(da,du)=\mu(da)K(du\mid a).
\]

For finite cost W and finite positive normalization, joint guidance defines

\[
q_{\rm gen}(da,du)=Z^{-1}\mu(da)K(du\mid a)e^{-W(u,a)}.
\]

Sampling an action from its marginal q_A and executing it in the original
system produces a different, fully specified law:

\[
q_{\rm exec}(da,du)=q_A(da)K(du\mid a),\qquad
q_A(da)=Z^{-1}\mu(da)\mathbb E_K[e^{-W(U,a)}\mid a].
\]

Equality holds exactly when, for q_A-almost every action, the tilt is constant
K-almost surely over the physical outcome. In particular, a deterministic
system K=delta_{S(a)} with known initial state and an exact model satisfies
q_gen=q_exec. Outcome-independent action costs also preserve K. Randomness in
diffusion sampling is not by itself a stochastic physical disturbance.

With partially observed initial conditions, K must include the conditional
unobserved state. With feedback, a whole future action sequence can depend on
future observations and this open-loop factorization cannot be reused without
an explicit causal policy factorization. These are standard probability/control
identities, not a newly discovered physical effect.

## Check B: four atoms, a feasible safe action, and the established remedy

Take actions A in {0,-2} with uniform behavior law. The true system is
U=A+xi, where fresh physical xi is independently -1 or +1 with probability 1/2.
An unsafe outcome is U>0. Action -2 is always safe; action 0 has risk 1/2.
Define W=beta*1{U>0}+lambda*A^2, with beta,lambda>=0. Set
b=exp(-beta), h=exp(-4*lambda), D=1+b+2*h. Exact atom normalization gives

\[
q_{\rm gen}(U>0)=\frac bD,\qquad
q_A(A=0)=\frac{1+b}D,\qquad
q_{\rm exec}(U>0)=\frac{1+b}{2D}.
\]

For fixed finite lambda and beta tending to infinity, generated risk vanishes,
but executed risk tends to 1/[2(1+2h)]. That limit approaches 1/2 as lambda
subsequently grows. No approximation, model-fitting error, inaccessible safe
action or numerical experiment is needed for this distinction.

The competent baseline constrains the physical kernel and optimizes only the
action law nu:

\[
\min_\nu\left\{\mathbb E_{\nu K}W+
D_{\rm KL}(\nu\Vert\mu)\right\},\qquad
\nu^*(da)\propto\mu(da)e^{-\mathbb E_K[W(U,a)\mid a]}.
\]

Substitution rewrites the objective as KL(nu||nu*) minus its log normalizer,
which proves optimality. For this fixture,

\[
\Pr_{\nu^*K}(U>0)=
\frac{e^{-\beta/2}}{2(e^{-\beta/2}+h)}\longrightarrow0
\quad(\beta\to\infty,\ \lambda\text{ fixed}).
\]

Thus fixing dynamics removes the entire supplied limiting risk discrepancy.
This is an elementary instance of the established control-as-inference parent,
not a new optimizer. It proves neither a finite-data learning result nor the
prevalence of this issue in deterministic PDE benchmarks.

## Check C: calibration must target the executed distribution

For fixed open-loop policies, put X=(initial state, action sequence) and let Y
be the safety score of the executed trajectory. Suppose calibration draws have
law p_X(dx)K(dy|x), while independently drawn target executions have law
q_X(dx)K(dy|x). If q_X is absolutely continuous with respect to p_X, then

\[
\frac{d(q_XK)}{d(p_XK)}(x,y)=\frac{dq_X}{dp_X}(x).
\]

With known weights w and a fixed predictor trained independently of calibration,
the standard weighted split-conformal construction uses a distribution of
residuals R_i with masses w(X_i)/(sum_j w(X_j)+w(x)), plus a test atom at infinity
of mass w(x)/(sum_j w(X_j)+w(x)). The residual locations themselves are unchanged.
This is a valid parent contract, not a proposed calibration method.

A generator's joint density ratio is not automatically the ratio for real
execution. If the physical kernel shifts, action weights alone are insufficient.
For feedback policies with a common environment kernel and initial law, the
trajectory likelihood ratio is the product of target/behavior action
probabilities conditional on the observed history, subject to support. That is
an ordinary path-likelihood identity; a coverage theorem additionally needs the
appropriate sampling and dependence conditions. Adaptive calibration reuse,
selection of a controller using its own interval, and accepted-only deployment
cannot be covered merely by quoting fixed-policy marginal coverage.

## Reusable truth/control source preflight

The [official SafeDiffCon repository](https://github.com/AI4Science-WestlakeU/safediffcon)
documents Burgers, smoke and tokamak directories and training/evaluation entry
points. Its page displays an MIT label. Only README/directory metadata was
inspected; full license text, immutable implementation and dependency rights
are not qualified. Dataset and checkpoint links were not followed. The two
DiffPhyCon papers share a source lineage and are not independent replication.

- Supported estimands to freeze: true executed safety probability and control
  cost under one declared initial-state and policy law, with generated scores
  reported separately; feedback and open-loop versions require separate contracts.
- Assignment/interference: randomize the legal controller before a reset; state
  which randomness belongs to physical dynamics, observations, behavior policy
  and model sampling. Shared disturbance tapes are a coupling design, not extra
  independent replicates. Future noise cannot be supplied to the controller.
- Complete lifecycle/replay: PDE and parameters, full reset state, observation
  operator, actuator support and saturation, action times/interpolation, boundary
  conditions, disturbance process, solver tolerance, controller updates and all
  RNG states. None is jointly qualified by the inspected metadata.
- Rights/ethics/release: no participants or field experiment proposed; exact code,
  dependency, source data and derived-release permissions remain unqualified.
- Confirmation: reserve entire physical regimes and independently drawn noise
  sequences before outcomes; training, calibration, selection and final evaluation
  need declared roles. Existing Paper D evidence is development for a new question.
- Replication/cost: no independent second solver or real-system bridge qualified;
  charge source evolution, training, calibration, online adaptation and inference
  separately. Current scientific compute is zero; future costs are unqualified.
- Stop: no harvest without an explicit residual beyond fixed-dynamics control and
  correctly specified calibration, and a qualified trigger. Stop source escalation
  on incomplete replay/support/rights or absent untouched confirmation. A plan
  grants no implementation, outcomes, compute, outreach or publication authority.

## Disposition and next decisive evidence

Retain three analytic controls and the versioned primary-source map. The source
capability is partial: a controlled PDE benchmark is documented, but it removes
no contribution blocker or replay/confirmation requirement. No new cycle, raw
question, forecast, F3 audit, machine card or execution is recorded.

Re-entry would require a substantive result or newly qualified control asset
that leaves a finite-cost, physically defined residual after the fixed-kernel
and proper target-law baselines. Repeating the stochastic-optimism example,
adding conformal prediction to a diffusion controller, or reporting generated
versus executed error alone does not qualify. The general PDE-control domain
remains open; no trained-model negative result or venue probability is inferred.
