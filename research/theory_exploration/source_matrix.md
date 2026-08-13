# Primary-source coverage matrix

**Search date:** 2026-08-13
**Rule:** theorem/equation coverage blocks claims; venue fit does not establish novelty

| Primary source | Audited result | Candidate statement blocked or constrained | Residual gap, if any |
|---|---|---|---|
| [Controlled world-model identifiability](https://arxiv.org/abs/2607.22430) | Theorem 1 identifies Gaussian latent state and controlled mean up to an orthogonal map under spectral separation `gamma_rep>0` and conditional action excitation `rho_tr>0`; Theorem 3 constructs counterfactual error amplification `delta/rho_tr`. Preprint. | A generic “mechanism diversity identifies response” or “coverage controls counterfactual error” theorem. | Exact mechanisms might yield a different, weaker excitation condition, but no such non-equivalence is currently shown. |
| [Causal Modeling of Policy Interventions](https://proceedings.mlr.press/v202/hizli23a.html) | Eq. (5) factorizes a sequential policy counterfactual under consistency, positivity, continuous-time no-unmeasured-confounding and full mediation. | Action-lift transport presented as a new identity. | A result surviving singular observed-state paths under weaker assumptions would need to differ from this factorization explicitly. |
| [Causal representation from multiple distributions](https://arxiv.org/abs/2307.06250) | Theorems 1–2 identify latent causal structure up to CD-equivalence under soft interventions; Theorem 3 composes unseen target combinations. Preprint. | Generic multi-intervention identifiability and unseen intervention composition. | Adaptive temporal mechanism sequences are not automatically covered, but static composition alone is occupied. |
| [Score-based causal representation learning](https://www.jmlr.org/papers/v26/24-0194.html) | Theorem 22 gives node-level recovery from two discrepant interventions; Theorems 25–26 extend to latent variables and graph recovery. | Intervention pairs as a novel source of latent identifiability. | Our lead must exploit known mechanism operators in a way not reducible to score diversity. |
| [Predictive State Representations](https://proceedings.neurips.cc/paper_files/paper/2001/hash/1e4d36177d71bbb3558e43af9577d70e-Abstract.html) | Action-conditional future predictions constitute a state; linear PSR dimension is no larger than a minimal POMDP representation. | “Identify only a behaviorally sufficient observable state” as a new construction. | A mechanism-sequence-specific equivalence must differ from a standard PSR. |
| [Generalized cross-MDP bisimulation](https://proceedings.neurips.cc/paper_files/paper/2025/hash/458567910b6d21f438f22aa20c036723-Abstract-Conference.html) | Generalized bisimulation metrics support state aggregation and policy-transfer control across MDPs. | Mechanism-conditioned predictive quotient plus generic transfer bound. | A sharper exact-mechanism bound remains logically possible but unproved. |
| [Effect-Invariant Mechanisms](https://www.jmlr.org/papers/v25/23-0802.html) | Proposition 8 and Theorem 9 identify effect-invariant sets and establish zero-shot generalization under stated environments. | Invariance alone as the basis of unseen-mechanism transfer. | Need a sequential-adaptation result not expressible as effect invariance. |
| [Causal abstraction](https://www.jmlr.org/papers/v26/23-0058.html) | Arbitrary mechanism transformations are handled through intervention-faithful causal abstraction. | Renaming an exact exchange map as a new abstraction theorem. | A market mechanism may be a useful instance, not general mathematical novelty. |
| [Invariant causal prediction for block MDPs](https://arxiv.org/abs/2003.06016) | Theorem 1 and Proposition 1 characterize invariant causal state abstractions and identifiability across environment interventions. Preprint. | Environment-invariant observable state as a new idea. | Async event clocks and known mechanics could change rates, but not the underlying quotient claim by themselves. |
| [HOWM](https://proceedings.mlr.press/v162/zhao22b.html) | Proposition 4.4 links homomorphism/projection structure to equivariant compositional generalization. | Generic lifting to unseen combinations of mechanisms or objects. | Adaptive, history-dependent composition is not settled by this result alone. |
| [DSGE as a Structured World Model](https://arxiv.org/abs/2607.03144) | Proposition 2 states structural re-composition under policy change and identifies the reduced-form off-regime failure. Preprint. | Exact-mechanism replay or structural policy substitution as new. | It reinforces the value of a separated mechanism but also the Lucas-critique risk when behavior changes. |
| [Markovian perturbation and response](https://arxiv.org/abs/0710.4394) | Theorem 2.10 characterizes Markov response functions; response depends on the perturbation family outside equilibrium. | Generic mechanical-versus-behavioral linear-response decomposition. | A non-perturbative, observable and identifiable response law could remain, but is not yet supplied. |
| [Two-time-scale Markov reduction](https://epubs.siam.org/doi/10.1137/S003613990139756X) | Singular perturbation gives averaged generators and asymptotic expansions for fast and slow states. | Fast/slow architecture or leading-order separation as theorem novelty. | Only a stronger finite-timescale error under market-specific discontinuities could be mathematically distinct. |
| [Geometric stochastic pumps](https://arxiv.org/abs/0705.2057) | Cyclic changes in a memoryless stochastic kinetic system generate geometric, path-dependent currents. | The naive identity “nonzero intervention-loop/order effect implies adaptation.” | An excess-over-frozen estimand may still be useful if its frozen baseline and confounds are externally identified. |
| [Interventional Gaussian LTI identification](https://proceedings.mlr.press/v236/rajendran24a.html) | Diverse intervention signals across environments identify system parameters under ICA-style diversity assumptions. | A stacked mechanism-rank witness as sufficient novelty. | A candidate must not reduce to ordinary persistent excitation or stacked observability. |
| [Identifiability of Switching Dynamical Systems](https://proceedings.mlr.press/v235/balsells-rodas24a.html) | Markov switching models and continuous latent switching dynamics are identified up to stated transformations under temporal and distributional conditions. | Mechanism switching as a new route to latent dynamical-state identification. | A new result would need weaker or structurally different assumptions, not merely known regime labels. |
| [Active learning for optimal intervention design](https://www.nature.com/articles/s42256-023-00719-0) | A causal Bayesian acquisition rule has information-theoretic bounds and consistency for sequential intervention selection. | Choosing informative known mechanism sequences as a generic NMI method. | A safe adaptive-market design could be an application; novelty requires a distinct objective or theorem. |
| [Physical-parameter identifiability in world models](https://arxiv.org/abs/2607.27017) | Controlled interventions show that input availability and prediction targets govern what a latent predictive representation retains. Preprint. | Assuming next-state prediction automatically recovers all physical or adaptive parameters. | Prediction-target-conditioned identifiability is a possible search direction, not an admitted candidate. |
| [SEC Tick Size Pilot study](https://www.sec.gov/about/divisions-offices/division-economic-risk-analysis/staff-papers-analyses/dera_wp_tick_size-market_quality) | Controlled comparisons establish heterogeneous spread, depth, volatility and efficiency effects. | A generic claim that tick-size changes affect market quality. | Event-time adaptation dynamics could be different, but require stronger data and identification. |
| [Tick Size Pilot imposition and conclusion](https://doi.org/10.1016/j.finmar.2025.101024) | Both forward and reverse windows and depth-of-book heterogeneity are already analyzed. | Treating the start/end pair itself as a new reversal study. | A predeclared adaptation spectrum or excess closed-loop residual must add a distinct prediction and independent replication. |
| [Economic World Models blueprint](https://arxiv.org/abs/2608.06020) | Provides an executable multiscale systems agenda and taxonomy. Preprint. | Using “multi-scale hybrid architecture” as a theorem or validated mechanism. | It motivates system design and benchmark breadth only. |

## V2 equation-level audit

| Primary source | Audited result | V2 statement blocked or constrained | Residual gap, if any |
|---|---|---|---|
| [Masked Prediction: A Parameter Identifiability View](https://proceedings.neurips.cc/paper_files/paper/2022/hash/85dd09d356ca561169b2c03e43cf305e-Abstract-Conference.html) | Definition 1 makes identifiability injectivity from model parameters to one or a collection of optimal predictors, up to hidden-state permutation. Theorem 2 shows one pairwise HMM target is nonidentifying; Claim 1 gives distinct stochastic transitions with the same declared matrix power; Theorem 4 shows all pairwise tasks on three adjacent tokens can still fail; Theorem 5 identifies the HMM from a two-token tensor target under its assumptions. | T1 target completeness, T2 horizon thresholds and T3 complementary targets as generic new primitives. | A different model class may have a useful task-design theorem, but it needs a result not specialized from these injectivity/tensor arguments. |
| [Computational Mechanics: Pattern and Prediction, Structure and Simplicity](https://csc.ucdavis.edu/~cmg/compmech/pubs/cmppss.htm) | Histories with the same conditional future distribution form causal states; the epsilon-machine is the unique minimal representation consistent with accurate prediction. | A target-conditioned minimal predictive partition as new representation theory. | Intervention-specific restrictions may change the chosen future sigma-algebra, but not the underlying sufficiency construction. |
| [Equivalent Comparisons of Experiments](https://projecteuclid.org/journals/annals-of-mathematical-statistics/volume-24/issue-2/Equivalent-Comparisons-of-Experiments/10.1214/aoms/1177729032.full) | Blackwell comparison orders experiments by attainable decision performance and its equivalent randomization/garbling relation. | T4 target-induced universal informativeness order. | A task order for one restricted intervention/loss family can be useful, but cannot be claimed as a new universal order. |
| [Sensitivity and convergence of uniformly ergodic Markov chains](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/26A9854BCB8D103B3A63A9B272616EC0/S0021900200001066a.pdf/sensitivity_and_convergence_of_uniformly_ergodic_markov_chains.pdf) | Iterated ergodicity coefficients bound finite-time kernel perturbation and invariant-law sensitivity; the bound accumulates transition error against convergence. | A relaxation envelope plus model perturbation allowance as new theory. | A market application must estimate and validate its class prospectively; the inequality itself is occupied. |
| [Mixing Time Estimation with Contraction Methods](https://proceedings.mlr.press/v117/wolfer20a.html) | A generalized Dobrushin contraction coefficient controls nonreversible mixing time, with fully data-dependent high-confidence intervals from one trajectory. | Estimating an uncertain contraction envelope as the main methodological novelty. | Partial observation and nonstationarity remain difficult applications, not an automatic new theorem. |
| [Revisiting Event-Study Designs](https://academic.oup.com/restud/article/91/6/3253/7601390) | Dynamic treatment responses by horizon are standard estimands; valid attribution requires explicit targets, no anticipation and parallel trends, and conventional regressions can fail under heterogeneous effects. | “Measure how a rule response decays over time” as a distinct empirical estimand. | A new response-vector restriction may survive, but slower decay alone does not. |
| [Using Synthetic Controls](https://www.aeaweb.org/articles?id=10.1257/jel.20191450) | Establishes feasibility, data requirements and failure modes for synthetic-control comparative designs. | Treating a fitted donor path as sufficient causal validation of a digital twin. | A credible donor pool and design-specific falsification remain case-specific obligations. |
| [Bayesian calibration of computer models](https://rss.onlinelibrary.wiley.com/doi/abs/10.1111/1467-9868.00294) | Calibrated prediction must account for simulator inadequacy and uncertainty rather than absorb all discrepancy into fitted parameters. | Naming the real-minus-simulator residual as a new scientific mechanism. | Query-specific discrepancy structure can be scientifically useful, but residual existence is not mechanism identification. |
| [Learning about physical parameters: the importance of model discrepancy](https://www.tonyohagan.co.uk/academic/pdf/simmach.pdf) | Discrepancy is confounded with calibration parameters without meaningful prior structure; ignoring it can yield biased, overconfident inference even as data increase. | Interpreting an EcoMD residual as a physical or behavioral parameter. | Independent measurements or defensible discrepancy restrictions are needed. |
| [Equilibrium Causal Digital Twins](https://arxiv.org/abs/2607.21667) | A finite intervention design can be matched by systems that disagree on the target counterfactual; validation and transport require query-specific structural assumptions, with partial identification when point identification fails. Preprint. | Finite pre-period/digital-twin validation as proof that the post-rule residual is adaptive. | A sharply restricted structural market class could still yield an identified query, but v2 supplies no such restriction. |
| [Digital Twin Counterfactual Framework](https://arxiv.org/abs/2604.01325) | Separates levels of twin fidelity and marginally testable claims from copula-dependent claims that remain assumption-indexed. Preprint. | A generic hierarchy of digital-twin validation tests as our new contribution. | EcoMD can implement such a hierarchy, but implementation is infrastructure rather than the headline. |

### V2 synthesis

- NMI T1--T4 have direct nearest results; the task-family intersection identity is ordinary partition/sufficiency
  algebra. V2 therefore ends `NMI_NO_SURVIVOR`.
- NCS relaxation exceedance is a valid rejection of the prospectively declared model class, but published mixing,
  dynamic causal-response and simulator-discrepancy results occupy its components. Experiment 145 proves that a
  non-adaptive hidden state can generate the same qualitative certificate. V2 therefore ends
  `NCS_C0_FAIL_IDENTIFICATION`, not a mechanism conjecture.

## Venue-scope evidence

- [NMI aims and scope](https://www.nature.com/natmachintell/submission-guidelines/about/aims) supports a route only
  when the method is broadly useful across AI/ML environments, not merely a market simulator.
- [NCS aims and scope](https://www.nature.com/natcomputsci/natcomputsci/natcomputsci/about/aims) supports a route only
  when computation produces a substantive, replicated scientific result.

These pages route a surviving contribution; they do not reduce its novelty burden.

## Derived identity retained from the audit

For an exact or conditionally independent-noise fast mechanism,

\[
Q_{n+1}=G_M(Q_n,A_n,\varepsilon_n^G),\qquad
\varepsilon_n^G\perp Z\mid(Q_n,A_n,M),
\]

the factorization gives `I(Z;Q_{n+1} | Q_n,A_n,M)=0`. This is a standard conditional-independence/data-processing
identity, not a novelty claim. It closes the idea that an exact event-layer update directly identifies hidden
behavior; only later feedback into observed actions can add information, returning the problem to controlled or
switching system identification and active experiment design.

## V3 equation-level audit

| Primary source | Audited result | V3 statement blocked or constrained | Residual gap, if any |
|---|---|---|---|
| [Operational Markov condition](https://arxiv.org/abs/1801.09811) | Defines an intervention-relative necessary-and-sufficient Markov condition using causal breaks and future process independence; the classical limit is ordinary conditional independence. | C1 as a new controlled closure definition or reset/replay certificate. | A finance implementation may be useful, but a finite probe family certifies only its declared instrument span. |
| [Completing State Representations using Spectral Learning](https://papers.nips.cc/paper/7686-completing-state-representations-using-spectral-learning) | PSR-f augments an imperfect state with predictive tests; Theorem 2 gives the minimal test/history dimensions through system-dynamics ranks and Theorem 3 gives consistent spectral completion. | C1 as a new minimal repair of an aliased state. | Nonlinear or continuous implementations remain engineering/statistical questions unless they produce a distinct theorem. |
| [Non-Markovian Memory Strength Bounds Quantum Process Recoverability](https://doi.org/10.1038/s41534-021-00481-4) | Classical finite Markov order is conditional factorization/CMI; Theorem 1 bounds supported multi-time observable error of a recovered finite-memory process by operational memory strength. | C1/C2 as a new chain from memory witness to finite repair and task-error guarantee. | The instrument-specific restriction matters operationally, but it is already part of the framework. |
| [Process-Tensor Tomography of SGD](https://arxiv.org/abs/2601.16563) | Defines observable operational Markov consistency, causal-break interventions, divergence backflow and uncertainty for learning dynamics. Preprint. | Reset/replay and data-processing backflow as a new ML memory diagnostic. | Markets are a different application domain, not a new diagnostic principle. |
| [Data-driven Mori--Zwanzig](https://epubs.siam.org/doi/10.1137/21M1401759) | The exact generalized Langevin decomposition separates resolved Markov dynamics, memory and orthogonal dynamics; the work learns reduced Markov and memory operators from data. | C2 as a new interpretation of semigroup defects as missing memory or a new learned memory-kernel program. | A sharper task-specific estimator could matter, but no v3 non-equivalent estimator or bound survived. |
| [Partial Observation of Linear Systems with Mori--Zwanzig](https://arxiv.org/abs/2606.23341) | Develops explicit Mori--Zwanzig representations for partially observed linear systems. Preprint. | Partial observation alone as the novelty that distinguishes C2 from established memory reduction. | Nonlinear market observation is harder, but hardness is not mathematical novelty. |
| [Glynn--Meyn Poisson perturbation](https://doi.org/10.1214/aop/1039639370) | Poisson-equation solutions control Markov-chain stability, invariant measures and perturbations. | C3's invariant-observable weighting identity as a new calibration theorem. | Computable neural approximation may be useful only with a distinct guarantee beyond direct substitution. |
| [Stein's method for steady-state diffusion approximations](https://arxiv.org/abs/2102.12027) | The prelimit-generator method rewrites distributional error as an expected generator difference evaluated on a Poisson/Stein solution. | C3 as a new learned critic/operator discrepancy. | A controlled partial-observation application still inherits the state-closure problem. |
| [Learning dynamical systems via Koopman operator regression in reproducing kernel Hilbert spaces](https://proceedings.mlr.press/v235/kostic24a.html) | Gives high-probability operator-power prediction bounds uniform over arbitrarily long horizons for ergodic Markov systems, with mass-preserving constructions. | Long-horizon operator control itself as the missing C3 theorem. | These guarantees assume a valid state/operator class; they do not repair an omitted state. |
| [DySLIM](https://proceedings.mlr.press/v235/schiff24b.html) | Regularizes learned dynamics by matching invariant measures while retaining pointwise trajectory fitting. | Joint pointwise plus invariant-measure calibration as a new practical objective. | Closure and multi-time validation remain necessary, but v3 found no new repair. |
| [Learning invariant-preserving neural operators](https://arxiv.org/abs/2306.01187) | Learns solution operators while explicitly preserving invariant measures for long-time statistical fidelity. | Invariant-measure preservation as the standalone C3 contribution. | A market-specific implementation would be application evidence only. |

### V3 synthesis

- C1 is a controlled PSR/operational-Markov closure test, and PSR-f already supplies a rank-based state repair.
- C2 is a process-memory or Mori--Zwanzig diagnostic; process-recovery theory already links operational memory to
  supported task error.
- C3 is standard Poisson/Stein operator comparison combined with occupied long-horizon Koopman and
  invariant-measure objectives.
- The exact noisy-XOR construction in `formal_cards_v3.md` shows that perfect one-step and one-time invariant fit
  can coexist with wrong multi-time dynamics. It is an elementary scope warning, not a novelty claim.

V3 therefore closes `V3_NO_SURVIVOR`. Experiment 146 was not run because the mandatory literature stop condition
fired before preregistration.

## V4 phenomenon-first audit

| Primary source | Audited result | V4 statement blocked or constrained | Residual gap, if any |
|---|---|---|---|
| [Dynamic LLM laboratory markets](https://arxiv.org/abs/2505.07457) | LLM agents interact through endogenous price feedback and are compared with human positive- and negative-feedback market experiments; broad trends can match while heterogeneity differs. | P1 as the first human/LLM dynamic-market comparison or first population-response mismatch. | A prospectively signed law across three population classes and independent experiments was not supplied by v4. |
| [LLM credence-goods markets](https://arxiv.org/abs/2603.08853) | Varies liability, verifiability, reputation, repetition and preferences, then compares institution-dependent outcomes with human experiments. | A generic cross-institution response spectrum for agentic markets. | Exact reproducibility and broader populations remain useful benchmark questions, not an admitted Nature claim. |
| [Collective cooperation without individual fidelity](https://arxiv.org/abs/2606.30454) | Uses the same human protocol, payoffs and networks for nine open-weight LLMs and finds macro agreement with micro heterogeneity and conditional-rule mismatch. | P2's intended aggregate-to-micro dissociation. | Replication across mechanisms could strengthen the finding but does not make the phenomenon new. |
| [LLM A/B surrogacy](https://arxiv.org/abs/2606.17165) | Gives surrogacy/comparability identification, falsification and overlap-bias tools for human effects; assumes no interference. | Generic treatment-effect transport/calibration as a new method. | Multi-agent interference is explicitly open, but direct composition with existing interference methods is not enough for NMI. |
| [LLMs predict social-science experiments](https://www.nature.com/articles/s41586-026-10742-x) | Tests hundreds of effects in preregistered experiment archives and finds useful correlation but systematic effect-size overestimation. | Treatment-effect fidelity across experiments as an unexplored scientific question. | Strategic interaction is different, but needs an independently identified and replicated law. |
| [Experimental design in two-sided platforms](https://arxiv.org/abs/2002.05670) | Mean-field marketplace models characterize interference bias under demand-, supply- and two-sided randomization. | Treating marketplace interference as a new complication introduced by LLM agents. | A distinct surrogate-under-interference estimand or theorem remains logically possible but was not found. |
| [Treatment-dependent network interference](https://proceedings.mlr.press/v286/shankar25a.html) | Provides estimators and assumptions when treatment changes the interference network. | Endogenous interaction structure alone as a new causal-estimation primitive. | LLM-specific measurement error may alter rates, but v4 derived no new non-equivalent result. |
| [Illusion of intervention](https://arxiv.org/abs/2605.20767) | Shows that an LLM-simulated treatment can alter the simulated user rather than only the intervention. | Treating prompt/persona invariance as an optional robustness check. | Executable-mechanism/text orthogonalization is useful design hygiene, but nearby framing and demand-effect work occupies the broad claim. |

### V4 synthesis

- P1's broad three-population comparison is a benchmark composition without a preregistered signed law or sealed
  data pair; it is `RETIRED_PRIOR_ART`.
- P2's macro--micro dissociation has a direct matched-protocol precedent and is `RETIRED_PRIOR_ART`.
- P3 lacks a randomized memory-break witness and independent replication, so it is `RETIRED_NO_WITNESS`.
- The OpenICPSR credence-goods package is development-only metadata. Its licence and outcome files were not opened
  after D0 failed.

V4 therefore closes `V4_NO_SURVIVOR` without an experiment, raw outcome inspection, API call, worker contact or GPU
use.

## V5 endogenous market-rule feedback audit

| Primary source | What is already established | What it blocks | Remaining admissible role |
|---|---|---|---|
| [RTS 11 consolidated text](https://eur-lex.europa.eu/eli/reg_del/2017/588/2023-06-05/eng) and [2023 amendment](https://eur-lex.europa.eu/eli/reg_del/2023/960/oj/eng) | Previous-calendar-year ADNT selects one of six liquidity columns; the column applies from 1 April historically and the first Monday of April after the amendment; the table and major exceptions are statutory. | Treating the assignment clock, thresholds or grid as an inferred model. | Ground truth for the assignment ITT and versioned exclusions. |
| [AMF 2018 tick-size report](https://www.amf-france.org/sites/institutionnel/files/contenu_simple/lettre_ou_cahier/risques_tendances/MiFID%20II%20Impact%20of%20the%20New%20Tick%20Size%20Regime.pdf) | Explicitly says tick changes can change the daily number of trades and calls the relation circular, while predicting wide annual bands prevent material feedback. | “First endogenous/circular tick rule” and purely conceptual feedback claims. | Falsifiable regulator baseline for a repeated-cycle magnitude test. |
| [FCA annual reclassification study](https://www.fca.org.uk/publications/research-articles/uk-tick-size) | DiD around the 2024 reclassification links larger ticks to spreads, cancellation/order behavior and depth; the regulator acknowledges selection risk. | First one-step reclassification effect on market quality. | Mandatory baseline; it does not estimate next annual ADNT or next assignment. |
| [ESMA FITRS schema/register](https://www.esma.europa.eu/data-reporting/mifir-reporting) and [legal notice](https://registers.esma.europa.eu/publication/legalNoticePage) | Official annual instrument records contain identifiers, calculation periods, ADNT and most-relevant-market ADNT; transformed register information is reusable with attribution. | Claims that the annual panel must be purchased or reconstructed from unofficial snapshots. | EU development and temporal validation after a real-data preregistration. |
| [FCA FITRS instructions](https://www.fca.org.uk/publication/systems-information/fca-fitrs-tech-spec.pdf) and [legal terms](https://www.fca.org.uk/legal) | Full files retain the latest record per ISIN/reporting period and a documented download API; Data numerical datasets may fall under UK OGL while generic scraping is prohibited. | Unrestricted UI scraping or redistribution of raw UK files. | Sealed replication through the documented API only, after terms are archived. |
| [RTS 28](https://eur-lex.europa.eu/eli/reg_del/2017/576/oj/eng) | Annual execution reporting groups shares at ADNT 80 and 2,000. | Treating all RTS 11 cutoffs as single-rule discontinuities. | Mark 80/2,000 as joint-rule sensitivities, not clean primary cutoffs. |
| [Robust RD inference](https://doi.org/10.3982/ECTA11757), [discrete-score RD](https://www.aeaweb.org/articles?id=10.1257/aer.20160945), [multi-cutoff RD](https://arxiv.org/abs/1912.07346) | Robust bias correction, multi-cutoff pooling and honest inference for discrete running variables are existing methods. | V5 NMI method novelty. | Mandatory estimation and failure-diagnostic oracles for an NCS application. |

### V5 synthesis

- G0 passes; D0 is conditional on the price/corporate-action and UK licence paths.
- Blind zero-row facets show repeated local support around all cutoffs, but are upper bounds before exclusions.
- NMI has no survivor. Experiment 148 also closes the NCS candidate at generated feasibility: only 9/16 gated cells
  passed; one rounded null over-rejected and every 5% effect cell missed the power gate.
- All 6,600 primary fits and 1,800 oracle constructions succeeded and all diagnostics passed, so the result is a
  statistical-design failure rather than an implementation failure. Real values, remote workers and GPUs remain
  locked; the final v5 state is `V5_NO_SURVIVOR`.

## V6 exact-controller and adaptive-demand audit

| Primary source | What is established | V6 statement blocked or constrained | Remaining admissible role |
|---|---|---|---|
| [EIP-1559](https://eips.ethereum.org/EIPS/eip-1559) | Exact integer execution-base-fee recurrence with a target, denominator and minimum upward increment. | Treating the execution controller as learned or novel. | Bit-exact mechanical oracle. |
| [EIP-4844](https://eips.ethereum.org/EIPS/eip-4844) | Excess blob gas and integer `fake_exponential` define the blob base fee. | Floating-point approximations as protocol truth. | Exact blob-fee oracle and generated controller. |
| [EIP-7918](https://eips.ethereum.org/EIPS/eip-7918) | Parent execution fee selects a strict reserve branch that prevents blob-excess decreases and uses the current schedule at forks. | Interpreting every cross-resource lag or hysteresis as adaptive demand. | Protocol-only negative control and cross-resource mechanical baseline. |
| [EIP-8134](https://eips.ethereum.org/EIPS/eip-8134) and [EIP-8135](https://eips.ethereum.org/EIPS/eip-8135) | BPO1/2 changed only target, maximum and update fraction at canonical timestamps. | Unversioned schedules or claims that the changes were inferred. | Development interventions; not untouched replication. |
| [EIP-8138](https://eips.ethereum.org/EIPS/eip-8138) | BPO3 is a draft prospective parameter-only change, but activation and all parameter cells remain blank. | Treating motivational scaling text as a finalized intervention. | Monitor and freeze only after official finalization. |
| [EIP-7999](https://eips.ethereum.org/EIPS/eip-7999) | A unified multidimensional fee proposal normalizes resource limits and generalizes fee coupling. | Unified multidimensional controller framing as a new theorem. | Nearest protocol-design comparator. |
| [Dynamical Analysis of EIP-1559](https://arxiv.org/abs/2102.10567) | Adaptive base-fee stability, convergence and possible chaos already have dynamical analysis. | Generic controller stability as V6 novelty. | Required theory baseline. |
| [Optimal Dynamic Fees for Blockchain Resources](https://arxiv.org/abs/2309.12735) | Multi-resource demand cross-effects, controller optimization and Ethereum calibration are explicit. | Broad cross-resource Jacobian/control novelty. | Mandatory structural/control baseline. |
| [Dual system-level closed-loop identification](https://arxiv.org/abs/2304.02379) | Known-feedback closed-loop response identification is an established systems problem. | Exact controller plus response learner as an NMI method. | Direct method oracle. |
| [Price Elasticity of Gas Demand on L1 and L2](https://arxiv.org/abs/2606.13555) | Wallet-lagged-fee IV targets causal gas-demand elasticity under congestion endogeneity. | Naive demand-on-fee regression and first causal elasticity claims. | Empirical identification baseline. |
| [Xatu data](https://github.com/ethpandaops/xatu-data) | CC BY 4.0 public Parquet exposes finalized/deduplicated canonical execution and consensus plus blob events. | Claims that basic field reconstruction requires paid data. | Conditional free-data route; attribution/replication still required. |
| [EIP-7892](https://eips.ethereum.org/EIPS/eip-7892) | Prague and BPO schedule constants deliberately co-vary target, maximum and update fraction. | Treating BPO capacity transfer as automatically nontrivial. | Exact scale-equivalence oracle. |
| [OP Holocene SystemConfig](https://specs.optimism.io/protocol/holocene/system-config.html) | OP Stack chains can configure EIP-1559 denominator and elasticity dynamically. | Treating one Ethereum parameter family as the only controller topology. | Non-proportional generated attacks and compatible-system catalog. |
| [Base deployment registry](https://github.com/base/contract-deployments/tree/12116aa7e58d3c6fc86de45075759e05a1c113be) | A frozen official MIT repository records eight Base gas-controller operations: seven receipt-backed and one README-only at that commit. | Calling Base episodes prospective or independent replications. | Same-chain blind historical topology; response outcomes remain sealed. |
| [Base configuration changelog](https://docs.base.org/base-chain/network-information/configuration-changelog) | Controller and minimum-base-fee parameters can change near one another. | Treating the February denominator operation as an isolated behavioral instrument. | Confounder registry and exclusion/robustness input. |

### V6 synthesis

- G0 passed Experiment 149: 97 official cases/107 blocks, 86 observable blob-fee values and zero mismatch.
- NMI has no survivor because every current method statement is a direct composition of occupied results.
- Exp150 is permanently void after premature formal-cell execution. Its clean, disjoint-seed repair Exp151 passed
  the frozen generated alias/rank gates: BPO rank 2, generated non-proportional rank 4, raw SHA256
  `6b81a0eddac2fc16697382128dff5621b75cb52d1bf8712e4a0f3193f431c649`.
- NCS is `RETIRED_IDENTIFIABILITY`. Full-rank generated separation assumes cross-regime latent-dynamics
  invariance; regime-specific latent dynamics restore observational equivalence, and no current event topology
  makes that assumption testable with prospective independent replication.
- The official EIP-8138 page was rechecked on 2026-08-13 and remained Draft with TODO activation, target, maximum
  and update-fraction cells. A future change and independent replication therefore remain unregistered.
- No chain outcome, remote worker or GPU has been used.

## V7 gauge-invariant controller-probe audit

| Primary source | What is established | V7 statement blocked or constrained | Remaining admissible role |
|---|---|---|---|
| [Minimal LPV input--output realizations](https://arxiv.org/abs/2305.08508) | Minimal state realizations of the same LPV input--output behavior are isomorphic under the stated conditions. | A latent-relabeling-invariant response as a new realization object. | Direct C1 oracle. |
| [Stable input--output realizations](https://arxiv.org/abs/2607.03849) | Finite Hankel rank plus uniform response decay characterizes stable finite-dimensional realization, with extensions to LPV and switched systems. | Hankel/Markov response stability as V7 novelty. | Stability and finite-representation baseline. |
| [Predictive State Representations](https://proceedings.neurips.cc/paper_files/paper/2001/hash/1e4d36177d71bbb3558e43af9577d70e-Abstract.html) | Action-conditional future tests form a state without identifying an ontological hidden state. | General stochastic controlled-behavior quotient as a new idea. | Nonlinear/stochastic C1 oracle. |
| [Set-membership identification with guaranteed simulation accuracy](https://arxiv.org/abs/2001.07628) | The feasible parameter set contains all bounded-noise-compatible models and yields finite/infinite-horizon worst-case guarantees. | Drift-ball intersection as a new identified-set construction. | Direct C2 oracle. |
| [Active exploration in adaptive MPC](https://arxiv.org/abs/2003.14120) and [exact dual set-membership MPC](https://arxiv.org/abs/2211.16300) | Future safe controls can shrink performance-relevant parameter uncertainty, including an exact predicted set-membership reformulation with robust feasibility. | Safe probe selection for identified-set contraction as a new method. | Active-design and safety oracle. |
| [Online coreset set-membership identification](https://arxiv.org/abs/2506.22804) | Persistent excitation contracts feasible-set volume; disturbance-bound mismatch receives an explicit Hausdorff error bound. | Drift-radius sensitivity as a standalone new theorem. | Mismatch/convergence oracle. |
| [Design and Analysis of Switchback Experiments](https://arxiv.org/abs/2009.00148) | Optimizes randomization points/probabilities and supports exact/asymptotic inference under known or misspecified carryover. | Paired controller paths as a new causal design. | Direct C3 path-effect oracle. |
| [Markov switchback experiments](https://arxiv.org/abs/2403.17285) | Treats delayed effects and autocorrelated rewards with Markov/model-based estimators. | Markovian carryover as the missing distinction. | Carryover/autocorrelation oracle. |
| [Geometric stochastic pumps](https://arxiv.org/abs/0705.2057) | Fixed stochastic kinetics can yield cyclic, path-dependent current. | Loop curvature/order as an adaptation certificate. | Mandatory fixed-mechanism negative control. |

### V7 synthesis

- C1 is `RETIRED_PRIOR_ART`: constancy on V7's equivalence classes is exactly factorization through controlled
  input--output behavior.
- C2 is `RETIRED_PRIOR_ART`: the sharp linear drift set is the standard set-membership ellipsoid, with diameter
  proportional to `1/sigma_min(S)` and unbounded null directions.
- C3 is `RETIRED_IDENTIFIABILITY`: switchbacks identify path assignments, while a fixed history-state transducer
  can reproduce the complete finite randomized probe-tree law.
- No experiment, outcome, remote worker or GPU was used; the final decision is `V7_NO_SURVIVOR`.

## V8 causal-memory-transplant audit

| Primary source | What is established | V8 statement blocked or constrained | Remaining admissible role |
|---|---|---|---|
| [Memory Transplants for LLM Agents](https://openreview.net/pdf?id=AIJsjIqfsp) | Independently varies memory architecture and content across code-to-math shift with a `2 x 2` factorial design, seven transplant conditions, frozen prompts, canonical export/import and preregistered controls. | Memory transplantation and architecture/content separation as a new protocol or method. | Direct transplant-method oracle. |
| [Shachi](https://arxiv.org/abs/2509.21862) | Makes Config, Memory, Tools and LLM controllable; transfers OASIS/EconAgent memory into CognitiveBiases and carries agent state between StockAgent and OASIS. | Broad novelty of cross-environment history-dependent behavior via memory, including economic-agent settings. | Economic-domain comparator; its exploratory evidence does not establish a universal law. |
| [Causal Intervention-Based Memory Selection](https://arxiv.org/abs/2605.17641) | Treats external memory as an editable intervention surface and compares no-memory, with-memory and perturbed-memory outputs. | `do(memory)` notation and perturbed capsules as a new causal primitive. | Memory-perturbation and robustness baseline. |
| [ExpeTrans](https://aclanthology.org/2025.acl-long.520/) and [Echo](https://arxiv.org/abs/2604.05533) | Transfer accumulated textual or structured experience from source tasks to new target tasks. | General source-to-target experience reuse through explicit memory. | Cross-task transfer baselines. |
| [Memory Contagion](https://arxiv.org/abs/2606.23195) | Constructs clean and source-biased memory stores, exposes future agents to them, and measures cross-temporal behavioral propagation with controlled memory/retrieval manipulations. | Narrowed “source-induced behavior moves through memory into a fresh agent” phenomenon. | Bias-specific direct comparator and model-specificity warning. |
| [Contagion Networks](https://arxiv.org/abs/2606.20493) | Defines cross-agent preference propagation coefficients and studies topology-dependent suppression/cascade regimes. | Behavioral-contagion terminology or a propagation matrix as novelty. | Multi-agent network-propagation baseline; requires independent replication. |
| [G-Memory](https://proceedings.neurips.cc/paper_files/paper/2025/hash/136a45cd9b841bf785625709a19c6508-Abstract-Conference.html) and [Rememberer](https://proceedings.neurips.cc/paper_files/paper/2023/hash/f6b22ac37beb5da61efd4882082c9ecd-Abstract-Conference.html) | Cross-trial multi-agent memory and reuse of episode experience across goals are established agent architectures. | Persistent experience changing later behavior as a new capability. | Architecture/performance oracles. |
| [Pricing for competitive online learners](https://arxiv.org/abs/1910.09314), [online load balancing](https://proceedings.mlr.press/v139/bistritz21a.html) and [safe nonstationary pricing](https://proceedings.mlr.press/v242/turan24a.html) | Couple online-learning/evolving users to adaptive resource prices and prove constraint, convergence, safety or regret properties. | The rejected dynamic-price-controller gain by agent-learning-rate phase-boundary idea. | Control baselines only. |

### V8 synthesis

- The proposed memory method is `RETIRED_PRIOR_ART`: transplantation, factorial architecture/content separation and
  causal external-memory perturbation are direct prior art.
- The proposed phenomenon is `RETIRED_PRIOR_ART`: economic-agent memory carry-over, cross-temporal memory contagion
  and cross-agent preference propagation already cover the broad and narrowed descriptions.
- Algebraically, the frozen `tau_mem` is four times the source-regime by capsule-semantics interaction coefficient
  in a saturated effects-coded factorial model. Its cluster-randomized implementation is rigorous but standard.
- A stronger exact-economy replication remains a possible specialist project, not an NMI/NCS survivor without a
  new signed cross-mechanism law or external scientific measurement.
- The stop rule fired at N0. No experiment, generated outcome, model/API call, remote worker or GPU was used; final
  decision `V8_NO_SURVIVOR_PRIOR_ART`.

## V9 age-structured-liquidity audit

| Primary source | What is established | V9 statement blocked or constrained | Remaining admissible role |
|---|---|---|---|
| [Bridging the Reality Gap in Limit Order Book Simulation](https://arxiv.org/abs/2603.24137) | Equal-sized queues can have different survival times because their formation paths differ; gradually depleted queues may encode more conviction than recently placed volume. | Path/age-enriched queue state as a new state-completeness motivation. | Direct path-dependent survival oracle. |
| [Order Behavior in High Frequency Markets](https://egrove.olemiss.edu/etd/562/) | Reconstructs total, fleeting and static books and decomposes their different contributions to displayed liquidity. | Claiming heterogeneous displayed-depth durability or an ex-post lifetime partition as new. | Descriptive oracle; ex-post labels cannot be used prospectively. |
| [Queuing Uncertainty of Limit Orders](https://ink.library.smu.edu.sg/lkcsb_research/7748/) | Latency-driven queue uncertainty produces clustered new submissions, immediate cancellations and rapidly reverting depth overshoot. | Young replenishment that looks liquid and then disappears as a new mechanism. | Signed equilibrium countermodel and baseline. |
| [Order-Flow Filtration and Directional Association with Short-Horizon Returns](https://arxiv.org/abs/2507.22712) | Filters messages by lifetime, modification count and timing; standing-book lifetime filtration changes directional association only modestly and heterogeneously. | Simple lifecycle filtering as method novelty or guaranteed predictive gain. | Hard negative lifecycle baseline. |
| [The determinants of limit order cancellations](https://onlinelibrary.wiley.com/doi/10.1111/fire.12363) | Estimates competing termination hazards with time-varying depth and queue-position covariates. | Age-conditioned cancellation/execution risk as a new statistical method. | Competing-risk and calibration oracle. |
| [Limit-order book resiliency after effective market orders](https://arxiv.org/abs/1602.00731) | Measures spread, depth and order-intensity recovery after market-order shocks. | Post-depletion raw-depth recovery as a new observable. | Raw resilience baseline. |
| [Order Flows and Limit Order Book Resiliency on the Meso-Scale](https://arxiv.org/abs/1708.02715) | Limit flows and relative addition/cancellation rates can predict resilience better than shallow depth. | Raw depth as an adequate comparator for a lifecycle statistic. | Flow, cancellation and deeper-shape oracle. |
| [The order book as a queueing system](https://arxiv.org/abs/1311.5661) | Relates average depth, execution probability and conservation of order flows in a birth--death model. | Cohort mass balance or survival accounting as an irreducible mechanism by itself. | Queue-flow accounting baseline. |

### V9 synthesis

- `D_h(t)=sum_j q_j S_j(h|F_t)` is expected future standing volume by linearity; it is not a new identity or an
  automatic measure of willingness to trade.
- No fixed sign survives competing cancellation/execution risk, age-dependent replenishment quality and endogenous
  shock selection. Ex-post lifetime classes are descriptive oracles and leak a prospective target.
- The exact recovery-gap phrasing appears residual, but it composes occupied objects and the current free sample has
  no independent multi-day train/validation/test or venue replication.
- The candidate is `RETIRED_NO_WITNESS`; final decision `V9_NO_SURVIVOR_SCOPE_AND_PRIOR_ART`. No outcome,
  experiment, remote worker or GPU was opened.
