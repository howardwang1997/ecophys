# Paper G cycle 31: bounded physical-response question screen

PRIVATE / INTERNAL. Paper-only F0/F1 exploration, not public evidence, a full literature audit, a machine card or an execution decision. Opened prospectively at 2026-09-12T02:25:14Z under the [single-round PI decision](../../research/discovery/decisions/pi_paper_g_bounded_generation_exception_20260912.yaml). The original proposal is preserved. The [question record](../../research/paper_g/cycle31_question_screen_20260912.yaml) retains the six frozen state/action/response/rival contracts.

## Decision

Retain **one F1-screened measurement question**: whether stabilization of learned fluid dynamics preserves physically available finite-time perturbation-energy gain. Its specific trained-model effect and contribution remain unresolved. Stop four other supplied formulations and deduplicate one. There are **six F0 questions, six F1 screens, zero F2 screens, zero full audits, zero forecasts and zero cards**. A retained F1 question grants no subsequent F2 or scientific execution authority.

This round connects to the repository's neural-PDE and constraint-attribution work. It does not reuse Paper D outcomes as evidence for Paper G, or reopen a financial-market thesis. The legacy source-lane names are interpreted using the existing physical-PDE scope addendum.

| Frozen question | Archetype | F1 disposition | Decisive boundary |
| --- | --- | --- | --- |
| g31_transient_energy_gain | measurement_method | deferred at F1 | Exact shear-gain reference is available in a restricted physical family; actual stabilization effect and distinct measurement contribution unproved |
| g31_actuator_metric_ranking | measurement_method | quick_closed | Coordinate/cost transport alone is a standard equivalence; learning-algorithm changes need a different identified mechanism |
| g31_thermal_budget_intervention | empirical_intervention | quick_closed | Fixed-power throughput target needs correction; selected primary anchors provide DNS, not the specified physical assignment |
| g31_actuator_reflection_intervention | empirical_intervention | quick_closed | Command sign is not automatically spatial reflection; selected physical sources do not establish the required calibrated reversal assignment |
| g31_resolved_energy_backscatter | theory_mechanism | deduplicated | Resolved/subgrid exchange and stable backscatter closure already recorded in the energy/entropy preflight |
| g31_symmetry_breaking_control | theory_mechanism | quick_closed | Elementary policy-selection distinction; no physically derived fluid-control objective establishing a new residual |

No closure asserts that the broader physical domain is impossible or exhausted. These decisions concern the supplied formulations and inspected assets. No publication probability is assigned.

## 1. Finite-time shear gain: retain a precise measurement question

**Repository difference.** The closest closed route is `paper_g_physical_history_impulse_response`. That route's supplied formulation concerned forecast/history response identification. Here the proposed observable is energy amplification of complete physical perturbations about a specified shear base, with a physical energy norm and input family. Neither missing history nor an arbitrary off-support extension creates the effect. Generic “good forecasts do not imply good response” remains insufficient as a contribution.

**One paper-only killer check, with a physical embedding.** Consider homogeneous shear (U=Sy\,e_x), viscosity (\nu>0), and a spanwise period (2\pi/k). Use shear-periodic boundary conditions in the shear direction, periodic perturbations, and the exact velocity family

\[
u(x,y,z,t)=(Sy+A(t)\cos kz,\;-B(t)\cos kz,\;0).
\]

This is an idealized homogeneous-shear system, not no-slip plane Couette flow or an ordinary periodic total velocity. The perturbation is divergence-free. Its self-advection vanishes; advection of the base contributes (-SB\cos kz) in the streamwise equation. Constant pressure therefore gives, by direct substitution into incompressible Navier–Stokes,

\[
\dot A=-aA+SB,\qquad \dot B=-aB,\qquad a=\nu k^2,
\quad M(t)=e^{-at}\begin{pmatrix}1&St\\0&1\end{pmatrix}.
\]

Volume-averaged perturbation kinetic energy is ((A^2+B^2)/4). The maximal gain **within this specified two-mode input family** is

\[
G(t)=\|M(t)\|_2^2=
e^{-2at}\frac{2+(St)^2+|St|\sqrt{(St)^2+4}}{2}.
\]

Both eigenvalues of the generator equal (-a). Nevertheless, when (|S|>2a), (G(t)>1) for sufficiently small positive (t): the largest eigenvalue of the symmetric part of the generator is (-a+|S|/2>0). The production balance is (\dot E=(SAB-a(A^2+B^2))/2). Thus transient amplification draws energy from the base shear while the perturbation eventually decays. The physical controls are (S,\nu,k,t), not an analyst-chosen distance metric.

For any differentiable surrogate whose finite-time derivative (widehat M(t)) is nonexpansive in this same physical energy norm,

\[
\|M(t)-\widehat M(t)\|_2\geq(\sqrt{G(t)}-1)_+.
\]

This is the reverse triangle inequality, not a new theorem. Asymptotic stability alone imposes no such obstruction: (M(t)) itself is a stable, exact counterexample to that stronger claim. A bound on spectral radius also does not imply a bound on finite-time singular-value gain. This family supplies exact analytic truth only for its admitted perturbations; it does not certify the global optimal disturbance of a wall-bounded flow. No numerical realization has been constructed or evaluated.

**Two primary anchors.** [JAWS, arXiv:2603.05538v1](https://arxiv.org/html/2603.05538v1), especially §3.3, uses a learned spatially weighted **soft Frobenius-Jacobian penalty**. This is not a certified global nonexpansive architecture. Its selected validation is viscous Burgers; no actual shear-gain suppression by JAWS is established here. Spatially adaptive stabilization and preserving sharp physical structure are already part of its intended method. We do not infer a scientific failure from prose or implementation details.

[Kai, Frame and Towne, Data-Driven Transient Growth Analysis, v1](https://arxiv.org/html/2507.02525v1) already estimates optimal input, response and gain from paired flow data, with noise/nonlinearity regularization. Classical energy-weighted singular-value analysis and a data-driven diagnostic are mandatory baselines. Its [2026 journal record](https://journals.aps.org/prfluids/abstract/10.1103/mxyg-j917) is the same work, not an independent lineage; selected v1 text and the journal abstract are not presumed identical.

**Residual question and early truth contract.** On a frozen physical input family with known (G(t)), does a named, actually applied stabilization procedure systematically reduce gain beyond its response uncertainty at comparable rollout accuracy and cost, or preserve it? A soft penalty supplies a falsifiable empirical rival, not a mathematical prediction of inevitable suppression. Relevant distinctions are the true shear-production term versus learned incremental contraction, and physical response calibration versus trajectory stability. A positive answer must identify the mechanism and its meaningful regime; a null answer must bound the distortion under a predeclared precision target. A single hand-selected bad model would not settle either claim.

The exact family makes an early synthetic truth comparison conceivable. The whole-flow optimum, a nontrivial trained-model contribution beyond existing gain diagnostics, comparison parameterizations, finite-amplitude/refinement limits, independent replication, untouched confirmation, and full cost remain unqualified. This is an F1 deferral, **not** a qualified re-entry trigger or an observed effect. Before F2, an ordinary re-entry audit must establish an actual removed blocker for the precise residual. The elementary bound alone does not remove the novelty blocker.

## 2. Actuator coordinates: stop the generic ranking formulation

The closest route is `paper_g_numerical_teacher_continuum_ranking`; this question changes the action metric, not the numerical teacher. Let the physical boundary field be (v=\Gamma a), with effort (v^\top Wv). Under an invertible command reparameterization (a=Bb), the same admissible physical action set and cost are obtained from (\Gamma'=\Gamma B) and

\[
R_b=B^\top\Gamma^\top W\Gamma B.
\]

Transporting each physical policy, its information and its constraints preserves every realized trajectory, cost and ranking. Keeping an unchanged Euclidean command ball generally changes the physical problem. This is the single killer check. It does **not** imply that retraining a fixed neural architecture or optimizer is coordinate invariant: those policy classes and optimization procedures need not transport bijectively.

The existing [FluidGym scope record](ecomd_paper_g_fluidgym_control_scope_2026-09-12.md) supplies the already-read actuation comparison context; zero new primary works were needed. The supplied generic normalization diagnostic has no identified irreducible contribution. A distinct physical actuation or learning mechanism would need a new contract; no existing published controller ranking is declared invalid.

## 3. Thermal-budget intervention: correct the endpoint, stop the supplied asset route

The proposed novelty differs from the history-response route by its physical boundary assignment. Freeze **equal supplied thermal power** for the killer check. For a cell with adiabatic sides and no other heat sources, integrated thermal balance gives

\[
\frac{dH}{dt}=P_{\mathrm{bottom}}-P_{\mathrm{top}}.
\]

In a statistically stationary regime with bounded stored heat, fixed mean bottom power fixes mean top heat throughput. The informative control response is instead the temperature drop or thermal resistance (\overline{\Delta T}/\overline P), with parasitic losses and actuator energy retained in a real experiment. A Nusselt increase at fixed power can arise through a reduced temperature difference. Simultaneously fixing power and temperature drop fixes that normalized throughput. This check does not claim that a useful heat-transfer benefit is impossible.

[Beintema et al., 2020](https://arxiv.org/abs/2003.14358) studies numerical two-dimensional convection and heat-transport suppression under a thermal-gradient contract. [Zhou and Zhu, PNAS 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12452834/) uses three-dimensional DNS, maintains the mean lower-wall temperature, and optimizes heat-transfer enhancement. Its method explicitly sets the boundary constraint; it is not an equal-power hardware experiment. Suppression and enhancement under different objectives and regimes are not opposite predictions for the same intervention.

The selected sources do not establish the physical equal-power assignment, heater calibration, losses, joint measurements or reusable trial structure required by the frozen empirical archetype. Stop this supplied formulation at F1. This is a source-scarcity result for two inspected anchors, not a claim that no such experiment exists. Do not silently turn it into a simulator program to satisfy the portfolio target.

## 4. Physical reflection intervention: the command map must implement reflection

The proposed physical randomized assignment differs from history identification. Let (R) reflect the flow and (R_A) act on the **realized actuator field**. If the dynamics are equivariant and the pre-state distribution satisfies (R_\#\mu=\mu), changing variables in the response integral yields

\[
\mathbb E_\mu[D(a)]=\mathbb E_\mu[D(R_Aa)],\qquad
\mathbb E_\mu[L(a)]=-\mathbb E_\mu[L(R_Aa)],
\]

for even drag (D) and odd lift (L). This is one symmetry-null check. For paired actuators, reflection normally exchanges physical ports and transforms vector components. It equals command negation only for a calibrated antisymmetric actuation coordinate. Negating a synchronous symmetric jet command, or merely shifting its blowing/suction phase, is not automatically spatial reflection. Holding an unbalanced shedding phase fixed also fails the ensemble premise.

[Yu et al., Experiments in Fluids 2026, institutional abstract](https://re.public.polimi.it/handle/11311/1304936) documents physical paired synthetic jets, frequency variation and PIV. [Feng, Wang and Pan, 2010, publisher abstract](https://www.sciencedirect.com/science/article/pii/S0889974610000721) varies suction duty cycle and momentum input for a rear jet. These support physical actuation feasibility; neither inspected abstract establishes the proposed randomized, reflection-balanced command-reversal dataset with independently calibrated force response. Related-article text on the publisher page was excluded.

The supplied sign-reversal interpretation and available assignment evidence fail the early empirical contract. Stop at F1. A later complete physical port-exchange experiment could be meaningful, but requires actual assignment/calibration capability and a distinct contribution beyond the standard symmetry null. No full source audit or hardware work occurred.

## 5. Resolved-energy backscatter: deduplicate and retain the exact control

The closer existing record is the [energy/entropy preflight](ecomd_paper_g_energy_entropy_preflight_2026-09-09.md), rather than only the initially nominated numerical-teacher route. It already records `energy_entropy_ecnn_2024`: stable resolved/subgrid exchange and its direct neural parent. The current broad physical-constraint formulation is therefore a duplicate.

For completeness, the one paper-only triad check fixes the physical issue exactly. On the (2\pi)-periodic two-dimensional torus, take real vorticity Fourier coefficients (A,B,C) at (k=(1,0),p=(0,2),q=(1,2)), with equal conjugate coefficients at their negatives. With (u=\nabla^\perp\psi), (\omega=\Delta\psi), the nonlinear initial derivatives are

\[
\dot\omega_k=-BC/10,\quad
\dot\omega_p=8AC/5,\quad
\dot\omega_q=-3AB/2.
\]

Choose cutoff (1<K<2), so only the (\pm k) pair is resolved. Initially (E_< = A^2) and (E=A^2+B^2/4+C^2/5). Including viscosity,

\[
\dot E_< =-ABC/5-2\nu A^2,\qquad
\dot E=-2\nu(A^2+B^2+C^2).
\]

The three nonlinear total-energy contributions cancel. For (A=B=1), changing (C=c) to (-c), with (c>10\nu), preserves the entire modal-energy spectrum but reverses the sign of resolved-energy production. This is an instantaneous Navier–Stokes statement: newly generated modes begin at zero, so their energy derivatives initially vanish. It does not assume that the three-mode family remains invariant at later times.

[van Gastelen, Edeling and Sanderse, 2024 version](https://arxiv.org/abs/2301.13770v5) already permits stable exchange with a modeled subgrid-energy state. Their [2025 2D LES version](https://arxiv.org/html/2504.05868v2), especially the introduction and §3.3, explicitly discusses backscatter and analyzes coarse-energy contributions. These are two related works from one research lineage. The phase check is reusable textbook-scale algebra, not a new physical effect, constraint principle, or closure method. No further escalation.

## 6. Symmetric optimal values versus deterministic policy selection

At a reflection-fixed state (Rs=s), let the action transform as (a\mapsto-a), (a\in[-1,1]), and consider the one-step symmetric cost (c(a)=(a^2-1)^2). A deterministic equivariant policy must choose (a=0), with cost one; the invariant distribution assigning equal probability to (a=\pm1) has zero cost. Both obey the same action budget. This single elementary control separates symmetry of optimal values/sets from equivariance of a selected deterministic action. It is an abstract decision example, **not a derived fluid-control objective**.

[Maidens et al., Symmetry reduction for dynamic programming, v2, Theorem 4](https://arxiv.org/pdf/1801.03237v2) proves that symmetry transforms an optimal policy into another optimal policy. It does not state that every optimum is one pointwise equivariant deterministic selection. [Chang et al., ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/951f87360544eeda24b5e72cf725da1d-Abstract-Conference.html) addresses broken symmetry of the environment and partially equivariant learning. That is a different contract from selecting symmetry-breaking actions in an exactly symmetric environment; we do not manufacture a contradiction between them.

The supplied generic theorem claim is elementary, and its required physical objective is absent. Stop at F1. A physical state, admissible actuation and independently derived cost creating an irreducible selection problem would be needed before reconsideration.

## Resource and evidence receipt

Ten distinct primary works were retained across the six programs: two, zero, two, two, two and two respectively. Nine are new registry works; the 2024 energy-closure work is reused. Selected full-text portions were read for JAWS, Kai v1, Zhou–Zhu, 2025 LES and Maidens v2; the other five readings were abstract/metadata scope. Two versions of one work are not counted as independent works. Search-only incidental hits are not qualified evidence. There was one paper-only killer check per program, no model/data payload access, no implementation of scientific methods, no numerical scientific tests, no runs, no GPU, no paid work, no delegation and no outreach.

The administrative ledger must record this as a **F1** deferral, not invent an F2 screen. The backward-compatible stage-count field `deferred_at_f1` does not modify scientific gates or grant authority; historical entries retain their existing F2-default interpretation. Administrative record validation is separate from scientific evidence.

The exception ends with this round. The surviving question's weakest links are distinct measurement contribution, response calibration beyond the exact restricted family, and transfer. A later ordinary re-entry audit must resolve those blockers before any F2 work. The current result supports neither ICML-main readiness nor NMI/NCS readiness. Paper G now has **55 recorded formulations over 15 cycles, with zero cards**; the detailed ledger has **22 cycles and 139 questions**, while the historical-inclusive program count is **31 cycles and 195 formulations**. These denominators have different scopes and are not publication-success statistics.

## Administrative verification

Discovery and route-graph validators passed. Protected history passed against `9d90711966256bc93eadadd406a3a9651a6ec493`; the prior search, forecast and re-entry prefixes remain intact. Twelve targeted discovery tests and two graph tests passed, including stage-aware F1 deferral accounting. The original proposal, general protocol and forecast ledger hashes are unchanged. These checks validate the records, not the scientific hypotheses. The [completion receipt](../../research/paper_g/cycle31_completion_20260912.yaml) records the budget and verification scope.
