# Paper G cycle 30: numerical teacher fidelity and continuum ranking

**PRIVATE / INTERNAL — exploratory topic selection; not public research evidence.**
Session started 2026-09-09T07:30:25Z. Literature cutoff 2026-09-09.
This record was composed after interleaved reading and algebra; it is not a
prospective freeze, forecast, experiment, or trained-model result.

The supplied generic measurement-and-repair formulation closes at F2. Its
ranking reversal is a biased-target example, its robustness condition follows
from the squared-loss identity, and exact or stochastic physical supervision
already has direct parents. Actual prevalence among competent trained models
is unresolved. This decision does not close continuum-fidelity research.

## Repository connection and bounded question

Paper D studies neural PDE prediction and resolution transfer. Its
`scripts/run_constraint_iclr_pdebench_fno.py` loader and restriction functions
read and coarsen one source dataset. This establishes the repository connection;
it does not establish numerical bias in that dataset or explain Paper D's
reported effects. No raw data, checkpoints, or new outcome assets were opened.

G30-01 is a **measurement_method** question: when does agreement with a
numerical teacher change the ordering of PDE surrogates against continuous
physical truth, independently of the model's observation grid? The native
object is the solution operator at a fixed physical time under a fixed initial
field law. The legal intervention changes the valid label-generating numerical
scheme or its mesh and time step while holding that physical law fixed.

- H1: source fidelity materially changes a frozen pair's continuum ranking, and
  a distinct measurement or correction survives competent existing baselines.
- H0: rankings are stable at relevant error margins, or ordinary reference-error
  accounting and existing supervision methods resolve the discrepancy.
- Discriminator: paired teacher and continuum risk differences, with a certified
  reference error budget and the same input distribution, scoring measure,
  physical horizon, observation operator and model-selection policy.
- Positive value: identify when surrogate selection changes a physical decision.
- Null value: establish a sufficient fidelity margin or baseline sufficiency.

This is the second compact screen in the new repository-linked neural-PDE
measurement parent after cycle 29, not re-entry into a closed market or
stochastic-gradient formulation. No same-state disagreement between published
models has been established. The source lane is analytic truth/control, not a
claim that elementary advection truth is newly invented. One raw question, one
F1 screen and one F2 screen were considered. There was no twelve-program harvest.

## A. Separate the two meshes

Let S be the continuum solution operator, S_g a valid numerical approximation
with generation settings g=(scheme,h_g,dt_g,tolerance), and Q_o the observation
operator with grid h_o. Labels are Q_o S_g x; physical targets are Q_o S x.
Changing h_o with g fixed changes the observation, not the generating solve.
Discretization of a fixed neural operator is a third error source.

The comparison must freeze the complete initial field law before applying either
solver. For a clean linear control, use a band-limited family resolved on every
grid and a fixed common scoring grid or exact Fourier norm. A finer observation
grid alone cannot certify a more accurate label-generating solver. This is a
measurement distinction, not a new theorem.

## B. Valid conservative numerical teacher with an exact ranking reversal

For periodic advection u_t+c u_x=0, c>0, the stable first-order upwind scheme is

    U_j^(n+1) = (1-lambda) U_j^n + lambda U_(j-1)^n,
    lambda = c dt/h,  0 < lambda <= 1.

At Fourier angle theta=k h, its one-step multiplier is

    g = 1-lambda + lambda exp(-i theta),
    |g|^2 = 1-4 lambda(1-lambda) sin^2(theta/2).

The exact multiplier is exp(-i lambda theta). For 0<lambda<1 and a nonconstant
resolved mode, the numerical teacher damps amplitude although both operators
preserve the spatial mean. Its leading modified-equation diffusion is
c h(1-lambda)/2. The scheme is a valid approximation with a truncation error;
no implementation failure is involved or asserted for PDEBench.

On the common scoring representation let u=Sx and delta=S_g x-u. Compare the
two frozen predictors a=u+delta and b=u. Against numerical labels their losses
are respectively 0 and ||delta||^2; against physical truth they are respectively
||delta||^2 and 0. More generally, prediction u+alpha delta has teacher loss
(alpha-1)^2||delta||^2 and physical loss alpha^2||delta||^2. This establishes
possibility only. These are stipulated predictors, not trained networks.

Required nulls: k=0; lambda=1, which is an exact grid shift at step times; and
consistent refinement h->0 at fixed physical time. A mass projection cannot
remove this zero-mean amplitude error. None of these facts implies a failure
of the actual Paper D training or evaluation protocol.

## C. What a ranking certificate would actually require

For frozen predictions a,b and numerical reference v=u+delta, define
D_v=||a-v||^2-||b-v||^2 and D_u analogously. Expanding gives

    D_v-D_u = -2 <a-b,delta>.

If ||delta||<=epsilon is independently certified, then

    |D_v-D_u| <= 2 ||a-b|| epsilon.

Hence |D_v| above this bound certifies the same sign. Otherwise the interval
is inconclusive, not evidence of a reversal. The identity and Cauchy--Schwarz
also hold in L2 over a frozen physical input law. They address reference bias;
finite-sample and adaptive-selection uncertainty need separate accounting.

A second exact twin shows why small solver disagreement is insufficient.
Take scalar predictions a=1,b=-1 and two numerical references v1=v2=0. Both
possible truths u=epsilon and u=-epsilon are compatible with reference error
at most epsilon, yet D_u=-4u has opposite signs. Even identical references
can share bias. Conversely, if <a-b,delta>=0, reference error does not affect
this pair's ranking. The proposed generic certificate is elementary error
propagation, not a new calibration algorithm.

## D. Noisy physical truth: useful condition, occupied generic remedy

For fresh oracle Y with E[Y|x]=u, fixed predictions a,b give

    D_hat = ||a||^2-||b||^2-2<a-b,Y>,
    E[D_hat|x] = D_u,
    Var(D_hat|x) = 4 (a-b)^T Cov(Y|x) (a-b).

The squared reference term cancels. Finite covariance suffices for this variance
identity; concentration, optional stopping and model selection need additional
contracts. If E[Y|x]=u+beta, its remaining bias is -2<a-b,beta>. More walks
reduce variance but need not remove fixed stopping or approximation bias.
This is the standard paired squared-loss calculation, not a new debiasing method.

WoS-NO supplies a relevant Poisson weak-supervision parent; its selected section
3.2 explicitly acknowledges practical bias from early termination and caching.
It does not qualify a zero-bias finite-cost continuum oracle for this project.
No allegation about its implementation or empirical claims is used here.

## Primary-work collision map

Seven works were retained: six selected full texts and one abstract. The F1
anchors were FNO discretization error, CROP and synthetic data generation;
the remaining works were used for the bounded F2 screen. This is not a full
fifteen-work audit, and no publication probability was assigned.

| Primary source and reading scope | Binding comparison or boundary |
|---|---|
| [Lanthaler, Stuart & Trautner, FNO discretization error, v2](https://arxiv.org/pdf/2405.02221v2), selected formulation and training sections | Discretization of a fixed FNO; the scope alone does not settle numerical label bias. |
| [Gao et al., CROP, ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/hash/313829757739365201b5adb3a1cbd9bd-Abstract-Conference.html), abstract only | Addresses model discretization mismatch. No full-method equivalence or source-fidelity result inferred. |
| [Hasani & Ward, SMAI-JCM 11 (2025), 497–516](https://smai-jcm.centre-mersenne.org/item/10.5802/smai-jcm.132.pdf), selected formulation and section 4.3 | Exact manufactured training data is direct prior. Forward/backward sampling laws differ, so that comparison is not a pure fixed-input fidelity intervention. |
| [Berner et al., principled neural architectures, v1](https://arxiv.org/pdf/2506.10973v1), selected principles and appendices A.4/B | Function-space convergence and error decomposition; this reading does not certify a data-generation solver. The later journal version was not substituted for this text. |
| [McGreivy & Hakim, v1](https://arxiv.org/pdf/2407.07218v1), selected sections 1–2 | Equal-accuracy or equal-time classical baselines and amortized costs are required comparators. No current-model ranking prevalence is inferred. |
| [Rowbottom et al., MLMC neural-operator training, v2](https://arxiv.org/pdf/2505.12940v2), selected section 2.1 and data hierarchy | Multilevel gradient estimation has direct prior. Projection/subsampling levels do not automatically certify independently regenerated PDE labels. |
| [Viswanath et al., WoS-NO, v2](https://arxiv.org/html/2603.01193v2), selected sections 3.1–3.2 and appendix E.1 | Stochastic physical weak supervision is direct prior; finite stopping bias remains a separate truth-contract issue. |

Other search results were unpromoted intake. No unsupported absence-of-prior
claim is made. In particular, differences between observation-grid papers and
source-label papers are not treated as opposing predictions.

## F2 disposition and reusable contract

The **current generic claim** is closed: analytic ranking reversal plus the
norm bound plus exact/noisy supervision does not establish a distinct method.
The hard contribution failure is the exact parent reduction and direct remedy
collision, not lack of an experiment, low venue probability, or a proven null
effect in real networks. No full empirical benchmark was supplied or rejected.

Retain four assets: the two-mesh contract; the upwind/exact/null control; the
reference-bias ranking identity and shared-bias twin; the noisy-oracle condition.
Any future empirical formulation must separate evaluation-reference changes
for frozen models from label-generation changes followed by retraining.

For the latter, freeze the physical input law, complete initial/boundary state,
forcing, solver family and tolerance, generation grid/time step, observation
and scoring operators, training/selection seeds and budget, physical horizon,
and confirmation partition. Account for label generation, training, tuning,
inference and truth measurement costs. Manufactured solutions must not silently
change the physical input prior. A nonlinear extension needs actual error bounds,
lawful immutable source assets and independent confirmation; none is qualified.

Cycles 29 and 30 now exhaust two bounded no-card screens in this neural-PDE
measurement parent. Do not open cycle 31 by renaming history, conservation,
resolution or fidelity. Re-entry needs a recorded qualified trigger: a same-state
primary model disagreement, a new truth/control asset removing a named blocker,
or a theorem defeating the recorded reduction. Until then, only a named-blocker
source preflight is appropriate; a new paper title or benchmark wish list is not
enough. This is a stopping rule for this parent, not for all Paper G discovery.

No machine card, forecast, scientific implementation, solver run, outcome access,
GPU work, purchase, outreach, publication, commit or push is authorized by this
record. Existing Paper D evidence roles and artifacts remain unchanged.
