# Paper G: true-memory source and observability preflight

**PRIVATE / INTERNAL — discovery infrastructure; not public research evidence.**

Session began 2026-09-09T06:36:22Z. This follows the
[history-response resolution](ecomd_paper_g_history_response_resolution_2026-09-09.md).
It is not a new topic cycle or a reopening of that formulation.
Structured contract: `research/paper_g/true_memory_preflight_20260909.yaml`.

**Decision: partial source capability; no qualified re-entry, candidate or card.**
The literature supplies concrete physical-memory settings and a documented
generator lineage. It also directly occupies the broad claims that partial
observation benefits from memory and that observability can determine sufficient
history. The useful advance here is an exact separation of input information,
internal recurrent state, convolution-memory duration and the scored target.
No new learning method or empirically established model disagreement remains.

## Repository connection and named blockers

Paper D provides the conservative neural-PDE and autoregressive-model connection.
The closed `theory_exploration_equation_audit_v3` route already records predictive
state/Mori–Zwanzig reductions and the inability of long-horizon calibration to
recover omitted state. Cycle29's physical impulse formulation additionally failed
to supply a contribution beyond existing response diagnostics and ordinary
augmentation. This preflight checks whether true-memory sources remove those
blockers; it does not infer novelty from changing the application to PDEs.

No Paper D trajectory, checkpoint or result array was read. Existing registered
and post-hoc evidence roles are unchanged.

## The primary sources do not describe one common experiment

| Source; inspected sections | State/input and contribution | Boundary relevant here |
|---|---|---|
| [MemNO, ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/file/89379d5fc6eb34ff98488202fb52b9d0-Paper-Conference.pdf), sections 1–5, dataset description | Establishes memory benefits with lossy/noisy PDE observations; combines neural operators with sequence models. Its stated task forecasts a trajectory from the observed initial field. | Generated rollout history is not a sequence of new true observations. Its 1D interpolation/2D downsampling is not identical to sharp Fourier filtering. |
| [HS-FNO](https://arxiv.org/pdf/2605.09523), sections 3–4, discussion | Treats a delay-PDE history segment as state and enforces shift-append transport. | A supplied physical history, an internal recurrent state and missing subgrid variables are different interfaces. The source explicitly says shift-append does not repair an inaccurate new slice or an undersampled memory grid. |
| [Flux-form spatiotemporal operators](https://arxiv.org/pdf/2608.18148), sections 2–4.1 | Uses filtered history slabs, divergence-form updates and a memory-length guideline based on closure energy injection. | Its guideline includes an oscillatory-correlation caveat and a local grid search; it is not a universal observability theorem. |
| [Pan and Duraisamy, SIADS 2018](https://arxiv.org/pdf/1803.09318), sections 3 and 5 | Derives closure models and finite-history rank criteria. Section 5 distinguishes reconstructing the whole hidden state from reconstructing only the needed closure quantity. | A target-specific observability rank test is direct prior, not a new method obtained by adding a PDE name. |
| [Brolly 2026](https://arxiv.org/html/2603.28671v1), scoring rules, equations 8–11 and Proposition 1 | Studies stochastic coarse-state prediction and MSE variance penalties. Equation 10 averages energy scores evaluated separately at successive lead times. | This objective addresses conditional lead-time marginals; it is not automatically a strictly proper score for the complete temporal joint law. |

MemNO's results do not contradict PDE-Refiner's history ablation under a frozen
observation operator, information supply and training protocol. Likewise, a
delay equation with an explicitly supplied history is not the same prediction
problem as a partially observed deterministic PDE started from one coarse field.
The supposed opposite-sign fork therefore fails the same-estimand check.

## Check A: generated history does not increase supplied information

Fix the trained parameters independently of the test realization. Let O be all
true information supplied at initialization, Y a future target and
G_1(O),...,G_m(O) deterministic model-generated states. Then

\[
\sigma(O,G_1(O),\ldots,G_m(O))=\sigma(O),
\quad
\inf_f\mathbb E\|Y-f(O,G_1,\ldots,G_m)\|^2
=\mathbb E\operatorname{tr}\operatorname{Cov}(Y\mid O).
\]

The infimum is over all measurable predictors with finite risk. An independent
model random seed also cannot reveal the realized hidden state; conditional
sampling can still represent its uncertainty. A recurrent model may improve
approximation, optimization, or retention of information that a compressed
current prediction would discard. Thus this identity does not refute MemNO's
benefits. It excludes interpreting those benefits as acquisition of additional
physical observations. Supplying a true earlier field changes O and must be
counted in the information budget. This is standard conditional-expectation
algebra, not a new information theorem.

## Check B: memory-kernel duration and sufficient observed history can differ

Consider periodic advection-diffusion, u_t+c u_s=nu u_ss. One real Fourier pair
u=x cos(ks)-z sin(ks) obeys

\[
\dot x=-\gamma x+\omega z,\qquad
\dot z=-\omega x-\gamma z,
\quad\gamma=\nu k^2>0,\quad\omega=ck>0.
\]

The full two-coordinate state is Markov. If the observation retains only x,
eliminating z gives

\[
\dot x(t)=-\gamma x(t)+\omega e^{-\gamma t}z(0)
-\omega^2\int_0^t e^{-\gamma(t-s)}x(s)\,ds.
\]

The normalized convolution kernel decays on time 1/gamma. Nevertheless, write
r=exp(-gamma Delta), theta=omega Delta. Two exact observed samples satisfy

\[
x_{n+1}=2r\cos\theta\,x_n-r^2x_{n-1}.
\]

When sin(theta) is nonzero they also recover
z_n=(cos(theta)x_n-r x_{n-1})/sin(theta). At theta=pi/2 this reconstruction is
well conditioned, and the history spans only one interval Delta while 1/gamma
can be arbitrarily large as gamma decreases. A long eliminated-state kernel
therefore need not require a long window of exact observations. This is an
elementary state-space realization, directly within the established closure and
observability lineage.

There is a complementary null. For a sharp Fourier projector retaining complete
real mode pairs, the constant-coefficient advection-diffusion generator commutes
with the projector. The retained field then evolves autonomously even when
discarded modes carry large energy. High-frequency energy alone does not imply
memory. Observing one quadrature and retaining full Fourier pairs are different
physical measurement operators; this comparison is not a representation-invariant
new physical effect and is not a substitute for nonlinear spectral-transfer
tests in the flux-form paper.

The source's actual diagnostic is q(t)=<r_closure(t),u_bar(t)>, whose temporal
correlation is used to guide history length. It discusses how oscillatory
correlations require a different truncation and subsequently searches a range of
lengths. We have not computed that diagnostic for its benchmark or established
that its qualified empirical guideline fails. Kernel decay, injection
decorrelation and predictive observability must simply retain separate names.
[Exact source definition and caveats](https://arxiv.org/pdf/2608.18148).

## Check C: observability depends on the requested future and noise

At Delta=pi/omega, the sampled propagator of Check B is -r I. Any number of
noiseless x observations fails to identify z. Yet every future x on this same
sampling grid is exactly predictable from current x. The off-grid target at
tau=pi/(2omega) equals exp(-gamma tau)z and is not identified. A demand to recover
the complete hidden state would therefore be unnecessarily strong for the first
target and necessary for the second. This is ordinary sampling/observability,
not new physics or a failure of a source paper.

For a finite Gaussian truth fixture with full state Z~N(0,Sigma), observations
O=H Z+epsilon, independent epsilon~N(0,R), Sigma and R positive definite, the
posterior covariance is

\[
\Sigma_{\mid O}=\Sigma-\Sigma H^T(H\Sigma H^T+R)^{-1}H\Sigma.
\]

The irreducible MSE of target BZ is tr(B Sigma_|O B^T). Even a full-rank finite
observation matrix does not make this zero under positive observation noise for
a nonzero B. This supplies a precise noisy control, not a new filtering formula.
It also prevents a noisy state-estimation problem from being scored against a
noiseless inversion oracle without counting the information difference.

## Check D: per-lead scores do not alone identify temporal dependence

Condition on one fixed initial observation. Let R be a fair sign. The two
forecast laws for future pairs (R,R) and (R,-R) have identical marginals at both
times. Every sum of per-lead energy scores has the same expectation for the two
laws, while their temporal covariance is +1 versus -1 and the variance of the
two-time sum is 4 versus 0. A joint score on the two-dimensional path can
distinguish them. This is a standard marginal-versus-joint counterexample.

Equation 10 in the Brolly source is an average over lead-wise scores. Its MSE
decomposition and conditional-marginal scoring claims are compatible with this
check; no refutation of those results is asserted. If an additional correctly
specified Markov model, full support and identification of all conditional
one-step kernels are imposed, joint laws may follow from those extra assumptions.
They cannot be inferred from the additive score alone for a coarse non-Markov
process. Replacing it with an existing joint kernel/energy score is already an
occupied method family and is not proposed as a new Paper G topic.

## Reusable truth-source contract

MemNO's Appendix E names the [r-buitrago LPSDA fork](https://github.com/r-buitrago/LPSDA)
for KS generation. Its README documents controlled time spacing and exposed
viscosity/initial-mode parameters. The [repository license](https://github.com/r-buitrago/LPSDA/blob/master/LICENSE)
is MIT. This is a useful alternative source lineage to the previously inspected
PDEBench generator, but only README/license metadata was qualified here. Neither
an immutable solver version, its complete dependencies nor its output accuracy
was checked. No code or generated data was acquired or executed. Dataset and
third-party dependency rights are separate. A fork is not an independent solver
lineage merely because its URL differs.

The supported future estimand family is conditional prediction risk for a frozen
target BZ or resolved field, and a separately declared joint-path distribution
score. Physical action response requires an additional explicit actuation/lift
contract; this preflight supplies none. Required replay state includes full fine
state, parameters, integration clock, boundary conditions, observation/filter map,
sensor-noise seed, exactly supplied true history, generated feedback, recurrent
initialization and target times. Observation noise, omitted state and fresh
process forcing must be distinct fields.

Before any authorized implementation, freeze disjoint trajectory/seed partitions
and observation operators without consulting outcomes. Existing Paper D material
is development only for a newly selected question. A future confirmation seed
range is not yet a qualified untouched partition; no independent nonlinear
replication or real-system bridge has been established. Count fine-solver work,
true history acquisition, observation bandwidth, model training, recurrent-state
storage and inference separately. Current work used no scientific compute; a
future execution budget remains unqualified.

Stop at a mismatched information budget, missing immutable replay contract,
unqualified rights, absent appropriate confirmation, or reduction to the direct
memory/filtering/score parents. This plan cannot authorize participant work,
outreach, candidate harvesting, outcomes or implementation.

## Consequence for the search

Record one partial-capability audit with zero removed blockers. Keep existing
route statuses and the search-cycle counts unchanged. The four elementary checks
are reusable controls, not four new questions or publication claims. The source
map now prevents three invalid shortcuts: calling generated states new evidence,
reading kernel duration as a universal required history length, and reading
lead-wise calibration as joint-path calibration.

Next intake must provide an immutable source/control contract or a substantive
result that leaves a residual after MemNO, target-specific observability/filtering
and correctly specified probabilistic scoring. Audit that trigger before a new
candidate in these closed families. Repeating the same papers at greater length
or proposing a combined memory-plus-noise architecture does not qualify.
The repository-linked ICML-main/NMI/NCS goal remains active and unfulfilled.
