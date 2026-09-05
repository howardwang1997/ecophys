# Re-exploration D-2 scenario and evidence map: GAMMA and ALPHA (2026-09-06)

Stage: `D_minus_2 scenario_and_evidence_map` under decision `pi_topic_reexploration_directive_20260906`.
Outcome access: **none**. No simulation, no GPU, no data access, no route-level decision, no topic
card. This document records the hostile-neighborhood audit for both families, the required outputs
(primary-work manifest, route-graph failure reuse, unresolved-collision list), the merge/split gate
outcome, and the updated pre-calibration hostile-T0 heuristic. Protocol reference:
`research/discovery/protocol.yaml` (D_minus_2 required_output; activation gate thresholds).

---

## 0. Method

Two-stage multi-agent audit, all lanes citation-verified (every primary work read at abstract+ level
with verbatim evidence; the two flagged collisions read at full-text level):

1. **Sweep (24 lanes).** GAMMA 12 lanes (transport-polytope fiber theory, OT-in-ML,
   randomized discretization layers, NN gauge/permutation, SBI summary sufficiency, matching
   econometrics, assignment mechanisms, auction-ML, market-sim-through-matching, PINN
   identifiability, recent gauge/constrained, implicit-bias invariance); ALPHA 12 lanes
   (Duruisseaux parent genre, differentiable ABMs, hard-matching gradients, decision-focused
   learning, mechanism decomposition, ABM validation/calibration, exposure bias, MARL
   differentiable environments — the highest-risk lane per D-3, market simulators,
   constrained physics nets, reflexive evaluation, recent attribution hunt).
2. **Adjudicate (24 batch adjudicators, blind across lanes).** Per work: OBJECT / ESTIMAND overlap
   tagging, verdict {direct_collision, adjacent, distinct, background}, severity, one-phrase
   distinguishing axis. Standard (frozen at D-3): a work that states *training/likelihood
   non-identification of pre-mechanism outputs modulo the mechanism fiber* (GAMMA) or *crosses
   training × inference enforcement of a mechanism layer in a market/matching simulator* (ALPHA)
   is a direct collision; mechanism-randomness, differentiation, calibration or single-face results
   alone are adjacent.
3. **Verify.** Every flagged direct collision goes to a 3-stance adversarial panel
   (confirm/refute/neutral, full-text evidence, ≥2 votes to confirm). Two high-severity adjacents
   additionally received hostile extension reverse-checks (can the parent be extended to occupy our
   claim?).
4. **Synthesize per family** → manifest counts, collision lists, veto-family scan V1–V7, scenario
   and evidence map, hostile scenario, verdict + conditions, hostile-T0 heuristic.

Agent totals: 55 (24 sweep + 24 adjudicate + 5 verify/panel + 2 synthesize), plus a separate
dedicated 3-stance panel for the ALPHA V1 flag (below).

---

## 1. Family GAMMA — matching-fiber gauge non-identifiability

Claim under audit: T1–T3 as framed at D-3 (`ecomd_reexploration_d3_framing_2026-09-06.md`), T4
labeled conjecture. Mechanism layer `M_k : Z×S×Ω → Y_g×S` under priority kernel
`k ∈ {fifo, pro_rata, random_unit}` × tape granularity `g`; training loss sees `θ` only through
`M_k`; the scientific object is the mechanism fiber (deterministic preimage or stochastic
likelihood-equivalence class).

### 1.1 Primary-work manifest summary

**68 verified external works** (54 adjacent / 8 distinct / 5 background / 1 flagged direct
collision → cleared 3-0 by panel). Meets the ≥15 requirement (68 ≥ 15). Six internal entries
adjudicated separately (below). Coverage: contingency-table/transportation-polytope fiber geometry,
OT computation/regularization, randomized discretization layers, neural gauge/permutation/implicit
bias, ABC summary-statistic identification, matching/market design and auctions,
loss-through-mechanism and market-simulator systems, physics-informed/gauge-selection
identification.

### 1.2 Adjudication table (external works)

| Work | Verdict | Sev | Distinguishing axis |
|---|---|---|---|
| Algebraic algorithms for sampling from conditional distributions (Diaconis–Sturmfels, 1998, Ann. Stat.) | adjacent | med | data-space sufficiency fibers for exact tests; no training claim |
| All Rational Polytopes Are Transportation Polytopes (2004, IPCO) | adjacent | low | inference-level disclosure bounds; excluded level |
| Fibers of multi-way contingency tables given conditionals (2014) | adjacent | med | deterministic constraint-granularity analog; no kernel/training |
| Counting Integer Points in Multi-Index Transportation Polytopes (2014) | distinct | none | enumeration, not identification |
| The Diameters of Network-flow Polytopes satisfy the Hirsch Conjecture (2016) | distinct | none | polytope graph distance only |
| Extreme points of general transportation polytopes (2024) | distinct | none | interval-marginal vertex geometry |
| Sinkhorn Distances (Cuturi, 2013) | distinct | none | degeneracy resolved by strict convexity |
| Smooth and Sparse Optimal Transport (2017) | distinct | none | uniqueness via regularization |
| OptNet (2017) | distinct | none | gradient through QP; excluded category |
| Scaling Algorithms for Unbalanced Transport (2016) | distinct | none | computational generalization |
| The Monge Gap (2023, ICML) | adjacent | med | pushforward-loss invariance; explicit regularizer; T4-genre |
| Sinkhorn Linearization and the Spectral Proxy (2026) | adjacent | med | IOT mechanism-fiber theorem; inference level, no granularity |
| Perturb-Softmax / Perturb-Argmax statistical representation properties (2024, arXiv:2406.02180) | cleared collision | high | state-free argmax family; noise law alone; no granularity/training |
| Understanding Straight-Through Estimator (2019) | adjacent | low | coarse-gradient validity on flat loss |
| Straightening Out the Straight-Through Estimator (2023) | adjacent | low | codebook dynamics, not fibers |
| Gumbel-Softmax (2016) | background | none | pure gradient estimator |
| Permutation Invariance in Linear Mode Connectivity (2021) | adjacent | low | internal function-preserving orbit |
| Git Re-Basin (2022) | adjacent | low | output-identical weights; T2 impossible there |
| Loss Barrier of Linear Mode Connectivity modulo Permutation Symmetries (2025, AISTATS) | adjacent | low | parameter-space barrier rates |
| Implicit Bias of GD on Separable Data (Soudry et al., 2017) | adjacent | low | T4 template, mechanism-free |
| Loss Landscape Degeneracy and Stagewise Development in Transformers (2024) | distinct | none | RLCT vocabulary only |
| Symmetry-Aware Graph Metanetwork Autoencoders (2025) | adjacent | low | gauge enlargement, function-preserving |
| Lack of confidence in ABC model choice (2011) | adjacent | low | insufficient summaries; inference level |
| On Consistency of ABC (2015) | adjacent | low | fixed-parameter identification |
| Comparison of Likelihood-Free Methods With and Without Summary Statistics (2021) | adjacent | low | benchmarking, no theorem |
| Evaluating Summary Statistics with Mutual Information for Cosmological Inference (2023) | adjacent | low | borrowable MI audit tool |
| OASIS (2026) | adjacent | med | posterior on identified set; fixed parameters, no training |
| Quotient-Space Diffusion Models (2026, ICLR Oral) | adjacent | med | internal SE(3) orbits, harmless-by-design; pre-empt |
| Who Marries Whom and Why (Choo–Siow, 2006, JPE) | adjacent | low | identification success; opposite direction |
| Cupid's Invisible Hand (2022, REStud) | adjacent | low | closed-form identification success |
| Identification in Many-to-One Two-Sided Matching Without Transfers (2024, Econometrica) | adjacent | low | exclusion restrictions restore identification |
| Partial Identification in Two-Sided Matching Models (2013) | adjacent | med | moment-inequality identified set; no dimension/kernel |
| Research Design Meets Market Design (2017, Econometrica) | adjacent | low | randomness as instrument; named carve-out |
| Discrete Probabilistic Inverse Optimal Transport (2022, ICML) | adjacent | high | owns bare positive-dimensional likelihood fiber modulo OT |
| School Choice: A Mechanism Design Approach (2003, AER) | background | none | lane anchor; no observation model |
| A New Solution to the Random Assignment Problem (Bogomolnaia–Moulin, 2001) | background | none | welfare dominance over lotteries |
| Smart Lotteries in School Choice (2026) | adjacent | low | design-side lottery optimization |
| Leveraging Uncertainties to Infer Preferences (2023) | adjacent | low | inference-level preference recovery |
| Stable and Fair Random Allocations in a Two-Sided Discrete-Concave Market (2026) | adjacent | low | BvN implementation bridge; design direction |
| Correlation of Rankings in Matching Markets (2025, Mgmt. Sci.) | adjacent | low | tie-breaking welfare effects |
| Optimal Auctions through Deep Learning (2019, ICML) | adjacent | low | mechanism learned; inverse quotient |
| Off-Policy Learning-to-Bid with AuctionGym (2023, KDD) | adjacent | low | unplayed-action missingness |
| Differentiable Electricity-Market Clearing for Gradient-Based Planning (2026) | adjacent | low | flat direction only a numerical caveat |
| Comparing Uniform Price and Discriminatory Multi-Unit Auctions (2025, NeurIPS) | adjacent | med | environment-side feedback granularity for regret |
| Bayesian Inference for Estimating Generation Costs in Electricity Markets (2026) | adjacent | med | inference-level clearing non-identification |
| Gradient Dynamics in First-Price Auctions (2026, EC) | adjacent | low | no-regret certificates, not fibers |
| MarS (2024, ICLR) | adjacent | low | pre-mechanism likelihood; engine downstream |
| TABL-ABM (2025, ECAI WS) | adjacent | low | fidelity gap attributed to agents |
| M3 (2026) | adjacent | low | order-level likelihood; no mechanism in loss |
| Do LLMs Understand Limit Order Book Dynamics? (2026) | adjacent | med | representational failure shape-echoes T2; distinguish |
| Persona-Trained Monte Carlo (2026) | adjacent | low | unimplemented forward estimator |
| A simple learning agent interacting with an agent-based market model (2024, Physica A) | adjacent | low | learning dynamics, not mechanism hiding |
| Identifiability Limits of Physics-Informed Inference for Spatial Stochastic Dynamics (2026) | adjacent | low | observation-marginal inference; excluded level |
| Counterfactual Operator Relevance for PDE Discovery (2025) | adjacent | med | fit-silent operator classes; must-distinguish T2/T3 |
| PINNs for Chemotherapy Pharmacokinetics (2026) | adjacent | low | empirical basin under non-identifiability |
| The Loss Does Not See the Basis, but Adam Does (2026) | adjacent | med | T4's natural template; internal gauge |
| Properties from Mechanisms (2022, ICLR) | adjacent | med | identification up to shared equivariance; forces T1 care |
| Measuring Dead Directions (2026) | background | none | checkpoint gauge diagnostics tooling |
| Decision Geometry of Covariance Estimation for GMVP under Heavy Tails (2026) | adjacent | low | exact invariance exploited as feature |
| On gauge freedom, conservativity and intrinsic dimensionality estimation in diffusion models (2024) | adjacent | low | internal Helmholtz gauge |
| Leveraging Gauge Freedom for Learning Non-Gradient Population Dynamics (2026) | adjacent | low | classical OT marginal non-uniqueness |
| Show Me What You Don't Know (2026) | adjacent | low | input-side fiber probing; theorem-free |
| Walking on the Fiber (2025) | adjacent | low | parameter-space posterior sampling |
| A Dirac-Frenkel-Onsager principle (2026) | adjacent | low | injected gauge momentum |
| Neural Mechanics (2020, ICLR) | adjacent | low | weight-space conservation laws; T4 cite |
| Implicit Bias of Linear Equivariant Networks (2021, ICML) | adjacent | low | Schatten-norm selection among interpolants |
| Symmetries in Overparametrized Neural Networks: A Mean-Field View (2024, NeurIPS) | adjacent | low | mean-field invariance preservation |
| Anti-Correlated Noise in Epoch-Based SGD (2025, MLST) | background | none | small-curvature noise statistics |

### 1.3 Collisions

**Confirmed: none. Unresolved: none.**

**Cleared-but-instructive: Perturb-Argmax/Softmax (Cohen Indelman & Hazan, 2024,
arXiv:2406.02180).** Flagged direct_collision at adjudication (Thm 5.3 minimal translation gauge;
Prop 5.4 positive-dimensional fiber for bounded noise). 3-stance panel ruled **collision_refuted
3-0**: the paper's own scoping — "Unlike these methods, we focus on studying the statistical
properties of randomized discrete probability models rather than on optimization frameworks" — plus
state-free argmax layer, no matching kernel, no state, no tape-granularity axis, no training. It
owns "noise law determines the stochastic fiber" **for the argmax family**: T1's stochastic clause
must be scoped to matching-clearing kernels plus granularity and must cite it (condition 1).

### 1.4 Veto-family scan V1–V7

- **V1** (modulo-mechanism training/likelihood non-identification parent): only candidate
  Perturb-Argmax (2024); cleared 3-0 — **not triggered**.
- **V2** (market-law truth from field data): no row claims field-data law discovery — not triggered.
- **V3** (generic performativity): not triggered.
- **V4** (invariance/gauge-twin frame): five rows flagged (Quotient-Space Diffusion 2026; GMVP
  Decision Geometry 2026; diffusion gauge freedom 2024; population-dynamics gauge 2026;
  Dirac-Frenkel-Onsager 2026) — all internal function-preserving gauges without an external
  mechanism layer, inside the stated carve-out; triggers the mandatory not-function-preserving
  remark (condition 4), **not a veto**.
- **V5** (market-physics overclaim): not triggered.
- **V6** (field-data/cross-engine law equivalence): not triggered; internal closure respected.
- **V7** (LLM-agent evaluation): Do LLMs Understand LOB Dynamics? (2026) is object-adjacent but its
  estimand is world-model probing — not triggered.

### 1.5 Scenario and evidence map (condensed; full version in session transcript)

- **T1 (fiber taxonomy).** Threaten: DPIOT (2022), Sinkhorn Linearization (2026) (mechanism-fiber
  theorems at inference level); Perturb-Argmax (2024, cleared analog); Fibers of multi-way
  contingency tables (2014) (deterministic granularity contrast); Properties from Mechanisms (2022);
  Algebraic algorithms (1998). Support/delimit: Partial Identification in Two-Sided Matching (2013);
  Bogomolnaia–Moulin (2001) + Stable and Fair Random Allocations (2026) (BvN lottery-vs-fractional
  mathematics our tape dichotomy inverts); Smart Lotteries (2026); Correlation of Rankings (2025);
  MI summary-statistic audit (2023). Required evidence: kernel-level granularity-dichotomy theorem
  (per-unit allocation tape strictly shrinks the random_unit likelihood fiber; aggregate tape
  collapses to deterministic) with computed fiber dimensions per kernel; measured fiber dimension
  under both granularities on lab-asset fixtures separated from zero beyond seed noise.
- **T2 (consumer instability).** Threaten: Do LLMs Understand LOB? (2026); Counterfactual Operator
  Relevance (2025); Differentiable Electricity-Market Clearing (2026); Paper D (parent — cite).
  Support: MarS (2024), M3 (2026), TABL-ABM (2025) never form the mechanism quotient in training,
  so the consequence is unoccupied. Required evidence: within-fiber pairs with exactly zero
  training-loss change and quantified, mechanism-attributable divergence (distillation, truncation,
  kernel swap, risk aggregation) that vanishes when `M_k` is removed.
- **T3 (partial-mechanism exposure).** Threaten: Show Me What You Don't Know (2026); Bayesian
  Generation-Cost Inference (2026). Required evidence: per-`D ∈ {identity, kernel swap, truncation}`
  characterization of exposed fiber directions; deployment experiments separating training-tied
  models with cross-seed effect sizes.
- **T4 (conjecture).** Genre parents to cite: Loss-Does-Not-See-the-Basis (2026); Soudry (2017);
  Neural Mechanics (2020); Linear Equivariant Networks (2021); mean-field symmetries (2024); Monge
  Gap (2023); Walking on the Fiber (2025); Leveraging Gauge Freedom (2026); Git Re-Basin (2022);
  Loss Barrier modulo Permutation (2025); Anti-Correlated Noise (2025). No theorem claim.

### 1.6 Hostile scenario (strongest attack, verbatim record)

> "T1 is Perturb-Argmax (2024) transplanted from argmax to queues, plus Chiu's Discrete
> Probabilistic Inverse Optimal Transport (2022) positive-dimensional likelihood fiber; the
> granularity contrast is Fibers of multi-way contingency tables (2014) at inference level;
> identification-up-to-mechanism is Properties from Mechanisms (2022); the fiber is just a gauge
> redundancy (Quotient-Space Diffusion Models 2026; The Loss Does Not See the Basis 2026); T2 is
> empirically anticipated by Do LLMs Understand Limit Order Book Dynamics? (2026) and theorem-shaped
> by Counterfactual Operator Relevance (2025); T4 is Soudry (2017) plus equivariant optimizers.
> What is left: a kernel label and a tape format."

Best defense: the **conjunction** is what no row states — a state-dependent matching-clearing
kernel with internal draws-without-replacement randomness whose likelihood fiber's dimension
provably changes with tape granularity, inside a training loss, with zero-loss pairs diverging for
named downstream consumers and a deployment-detectability characterization. Each analog lacks at
least two of: state dependence, kernel family, granularity axis, training context, consumer
consequence. Honest concession: if D-1 shows the shrink/collapse dichotomy is an immediate
sufficiency/data-processing corollary (the Fibers-2014 shape), or T2's unbounded divergence is
trivial given unbounded fiber diameter, the topic reduces to packaging and dies.

### 1.7 Verdict: **survive_with_conditions**

1. Scope T1's stochastic clause to matching-clearing kernels plus the kernel-randomness ×
   tape-granularity interaction; cite Perturb-Argmax (2024) as the argmax-family analog; no novelty
   claim for bare fiber existence (DPIOT 2022) or generic randomness-determines-fiber.
2. T1 lead theorem = the granularity dichotomy, with computed fiber dimensions per kernel, citing
   Fibers (2014), Algebraic algorithms (1998), Sinkhorn Linearization (2026), Properties from
   Mechanisms (2022) as delimited analogs.
3. T2/T3 cite Paper D as parent; distinguish mechanism-induced fibers from representational failure
   (Do LLMs Understand LOB 2026) and design-induced operator set-identification (Counterfactual
   Operator Relevance 2025); divergence quantitative and mechanism-attributable.
4. Dedicated remark pre-empting the gauge conflation (V4): fibers are **not** function-preserving;
   members are distinguishable by deployment maps (against Quotient-Space Diffusion 2026; Neural
   Mechanics 2020; Loss-Does-Not-See-the-Basis 2026).
5. T4 stays conjecture-labeled (equivariant-optimizer template + Soudry 2017).
6. Internal lab assets only (lab-asset-v3 fixtures); no field-market-law claims, external data,
   outreach, or GPU (V2/V6 and route-graph closures respected).

### 1.8 Hostile-T0 update (pre-calibration heuristic; NOT a calibrated forecast, NOT an activation decision)

**Point 0.55, range [0.38, 0.70].** Zero confirmed collisions after the 3-0 clearance and 68
verified works place this well above the 0.15 activation floor; residual mass sits on three die
modes: (i) T1's dichotomy reduces to a sufficiency/data-processing corollary; (ii) T2 reads as
immediate from unbounded fiber diameter; (iii) hostile gauge-twin framing (V4). Conditions 1–4
partially address each; the floor (0.38) reflects the case where none do.

---

## 2. Family ALPHA — plug-and-play attribution audit of mechanism layers

Claim under audit: the eight-cell factorial (output coordinate × training enforcement × inference
enforcement) on autoregressive market simulators with exact combinatorial clearing layer `M`,
estimand = path-dependence attribution (Paper D statistical contract inherited verbatim).

### 2.1 Primary-work manifest summary

**61 verified external works** (59 adjacent / 1 distinct / 1 background; severity 1 high / 9
medium / 39 low / 12 none). Meets the ≥15 requirement (61 ≥ 15). The MARL co-training lane
(highest risk per D-3) was searched hardest: Solver-in-the-Loop (2020), differentiable
physics/MBRL, Diff2SP, Gen-DFL, DASH, event-binning gradients — all estimand- or
object-distinct; **no work crosses training × inference enforcement of any mechanism layer in a
market/matching simulator**.

### 2.2 Adjudication table (external works)

| Work | Verdict | Sev | Distinguishing axis |
|---|---|---|---|
| Towards Enforcing Hard Physics Constraints in Operator Learning (Duruisseaux et al., 2024, ICML AI4Sci WS, Zvxm14Rd1F) | adjacent | high | exact four-arm train×infer template; continuous PDE projection, not combinatorial M |
| Projected Neural Differential Equations (2024) | adjacent | low | projection intrinsic to vector field; no infer-off arm |
| Flow-based Automatic Neural Operator with Hard Constraints (2026) | adjacent | med | through-constraint always on; superiority estimand |
| Equation Recast for Canonical Operator Learning (2026) | distinct | none | parameter-regime transfer; layer presence never varied |
| Differentiable Electricity-Market Clearing for Planning (2026) | adjacent | low | plan optimized; clearing never ablated |
| GradABM (Chopra et al., 2023, AAMAS) | adjacent | low | epi feasibility; no cube |
| Automatic Differentiation of Agent-Based Models (2025) | adjacent | low | VI parameter-calibration estimand |
| Some challenges of calibrating differentiable ABMs (2023, ICML WS) | adjacent | low | GVI calibration challenges |
| INTAGS (2023) | adjacent | med | one implicit raw/raw cell; no comparison arm |
| Dual-Positive Monotone Parameterization for Bids (2026) | adjacent | med | RL bidder policies; no clearing-layer factorial |
| Does "Do Differentiable Simulators Give Better Policy Gradients?" (2026, ICLR) | adjacent | low | estimator bias; confound we must control |
| Unbiased Gradient Estimation for Event Binning (2026, ICLR) | adjacent | low | gradient-side mirror; layer never ablated |
| Policy Optimization via Mixed Gradients (2026) | adjacent | low | discrete action space, always present |
| Automatic Differentiation of Programs with Discrete Randomness (2022, NeurIPS) | adjacent | low | ABM differentiated, not trained-and-ablated |
| A unified view of LR and reparameterization gradients (2021, AISTATS) | adjacent | none | pure estimator theory |
| ADEV (2023, POPL) | adjacent | none | PL soundness theorem |
| Task-based End-to-end Model Learning (2017, NeurIPS) | adjacent | low | through-M training parent; no inference axis |
| Gen-DFL (2025) | adjacent | low | decision-robustness estimand |
| Diff2SP (2026) | adjacent | low | solver embedded in training only |
| Beyond Action Imitation / DASH (2026) | adjacent | low | pipeline-stage ablations; no clearing layer exists |
| Decision-focused Sparse Tangent Portfolio (2026, ICML) | adjacent | low | Sharpe superiority; layer always present |
| Minimizing Surrogate Losses for DFL (2025) | adjacent | low | LP zero-gradients a.e.; implementation constraint for us |
| Decomposing Financial Market Dynamics via Mechanism Analysis (2026) | adjacent | med | runtime sweeps on untrained evolutionary ABM |
| Factorizing Financial Power Law using OT (2025) | adjacent | low | design-time toggles; no training phase |
| Emergence from Emergence (2025) | adjacent | med | trained MARL market; composition conditions, never inference-ablated |
| Structural stochastic volatility (Franke–Westerhoff, 2012, JEDC) | adjacent | low | untrained MSM model contest |
| Which Sensitivity Analysis Method for ABMs? (2016, JASSS) | adjacent | low | numeric parameter grids, not mechanism presence |
| A comparison of economic ABM calibration methods (2020, JEDC) | adjacent | none | parameter-recovery estimand |
| Simulation and estimation of an agent-based market-model with a matching engine (2021) | adjacent | low | fixed M infrastructure; M prior art |
| Alleviating Non-identifiability for Financial Market Simulation (2025, IEEE TCSS) | adjacent | low | parameter fibers of untrained model |
| Calibrating ABM Financial Simulators with Pretrainable APT Surrogates (2026) | adjacent | none | optimizer-side learning; simulator untouched |
| Scheduled Sampling (2015) | adjacent | low | conditioning-input curriculum |
| Sequence Level Training with RNNs (2016) | adjacent | low | loss/supervision mismatch |
| How (not) to Train your Generative Model (2015) | adjacent | none | objective-function theory |
| Professor Forcing (2016) | adjacent | low | regime matching inside one unconstrained RNN |
| Diffusion Forcing (2024) | adjacent | low | per-token noise schedule |
| Self Forcing (2025) | adjacent | low | conditioning-context intervention, video |
| Solver-in-the-Loop (2020, NeurIPS) | adjacent | med | training-face only; inference always through solver |
| Differentiable Physics Models for Offline MBRL (2020) | adjacent | low | policy-viability estimand |
| Differentiable Physics Simulations with Contacts (2022, ICML WS) | adjacent | low | gradient-fidelity estimand |
| Differentiable Agent-Based Simulation for SBO (2021, PADS) | adjacent | low | discreteness smoothed away; no exact M |
| MarS (2024, ICLR 2025) | adjacent | low | production raw-train/through-M-infer cell; never crossed |
| M3 State-Event Foundation Model (2026) | adjacent | med | anchor mismatch documented; engine never removed |
| MarketGPT (2024) | adjacent | low | fixed interpretation layer |
| Generative AI for End-to-end LOB Modelling / Nagy et al. (2023, ICAIF) | adjacent | low | feasibility anchor; M never an experimental factor |
| TABL-ABM (2025, ECAI WS) | adjacent | low | fixed evaluation harness |
| KineticSim (2026) | background | none | M as infrastructure itself; nothing trained |
| Hamiltonian Neural Networks (2019) | adjacent | none | conservation intrinsic; no toggle exists |
| Symplectic Recurrent Neural Networks (2020) | adjacent | none | intrinsic integrator, never varied |
| Guaranteed Conservation of Momentum / DMCF (2022) | adjacent | low | constraint in weights; bundled comparison |
| Exact conservation laws for NN integrators (2022, JCP) | adjacent | none | by-construction Noether |
| Pseudo-Hamiltonian Neural Networks (2023) | adjacent | low | additive force-component reuse |
| GENERIC-FNO (2026) | adjacent | low | by-construction; projection explicitly rejected |
| Safe and Compliant Cross-Market Execution (2025) | adjacent | med | one-sided runtime shield, never crossed with training |
| RL for Execution under Dynamic Fees in DEX (2026) | adjacent | low | fixed analytic simulator; policy-value estimand |
| TRADES (2025, ECAI) | adjacent | med | realism/responsiveness; no clearing layer anywhere |
| Towards Generalizable RL for Trade Execution (2023, IJCAI) | adjacent | low | policy-overfitting bound |
| The Bidding Games (2025) | adjacent | none | fixed hand-built auction env |
| Get Real: Realism Metrics for LOB Simulations (2019) | adjacent | none | fidelity scoring, no lever on placement |
| TradeFM (2026) | adjacent | low | raw-train/through-M default; disentanglement deferred to future work |
| Discrete Flow Matching for Compound Error (2025, ICAIF) | adjacent | low | exposure-bias repair; no mechanism layer |

### 2.3 Collisions

**Confirmed: none. Unresolved at synthesis: one — resolved 3-0 by dedicated panel the same day.**

**Duruisseaux et al. 2024 (ICML AI for Science Workshop, OpenReview Zvxm14Rd1F).** Carried from
adjudication as a V1 exact-parent-occupation flag at severity high (the batch adjudicator, bound by
the "adjacent on OBJECT and ESTIMAND" standard, did not route it to the panel). Because protocol
treats an unresolved collision as family-fatal, a dedicated 3-stance adversarial panel was
convened on the full text. Panel evidence, verbatim: Section 4 — "To investigate the effect of
appending the projection layer during training or at inference time, we compare the performance of
a baseline model with 3 different models" and "B+Projection: The original surrogate model G is
trained for N epochs in a purely data-driven way, and its output is projected using pr_C at
inference time" — the four-arm template including a locked-checkpoint inference-only surgery cell
is genuinely theirs. But all three collision clauses are domain-gated: the object is PDE operator
learning (FNO, Kolmogorov flow Re=500/5000), the layer is continuous Fourier/Leray projection, the
estimand is constraint-satisfaction/L2 fidelity with 5 seeds — no market/matching/ABM simulator, no
combinatorial/integer clearing, no SESOI-graded attribution, no paired-seed 50k bootstrap, no
lineage transfer, no reflexive axis. **Panel verdict: collision_refuted 3-0.** Ruling recorded as:
external PDE structural-template parent (genre parent) — must be cited; "first train×infer
constraint crossing" phrasing permanently falsified; novelty scoped to (i) market-native
combinatorial/integer clearing layer M and (ii) the SESOI-graded path-dependence attribution
estimand.

**Cleared-but-instructive:** Solver-in-the-Loop (2020) (one face, training enforcement, PDE);
INTAGS (2023) (raw/raw cell only, no comparison arm); Nagy 2023 / MarS 2024 / MarketGPT 2024 /
TABL-ABM 2025 / TradeFM 2026 (the (raw-train, through-M-infer) cell is the production default;
TradeFM names our confound and defers it); M3 (2026) (nearest market-side fragment; engine never
off, no FIFO to swap); Dual-Positive Monotone Parameterization (2026) (strongest market neighbor;
fails all three collision clauses); Emergence from Emergence (2025); Decomposing Financial Market
Dynamics (2026) (closest attribution genre; untrained ABM, runtime sweeps); Safe Compliant
Cross-Market Execution (2025) (inference-only shield, never crossed with training); TRADES (2025)
(reflexive-evaluation prior); matching-engine ABM (2021) + KineticSim (2026) (M-infrastructure
prior art); Alleviating Non-identifiability (2025) (parameter-level fiber vocabulary, untrained).

### 2.4 Veto-family scan V1–V7

- **V1:** the Duruisseaux flag — resolved 3-0 as external genre parent; unconditional novelty
  phrasing falsified; parent-citation condition attached. **Not triggered** after panel.
- **V2:** no trigger — ALPHA claims no field-data law; lab replay engine plus synthetic DGP only.
- **V3:** no standard-parent reduction found; gradient/DFL/sensitivity parents all change estimand
  or object.
- **V4:** no external trigger; internal cycle-7 audit already consistent (charges ≠ transition
  laws); gauge exposure is an audited output, not an assumption.
- **V5:** no trigger; DMCF (2022) exemplifies the bundling failure our one-factor-per-cell design
  must avoid.
- **V6:** no trigger — OOD axes are within-engine stress tests, no cross-engine law claim.
- **V7:** no external trigger; internal negative-knowledge ledger consumed as citation; design must
  still preregister arms and report all cells.

### 2.5 Scenario and evidence map (condensed)

- **Cube primary claim.** Threaten: Duruisseaux 2024 (template), Solver-in-the-Loop 2020 (training
  face), Flow-based Automatic Neural Operator 2026 ("ablations are routine" optics), Paper D
  (internal parent — no double-counting). Support: no external work trains a market simulator
  through exact combinatorial M; zero-training checkpoint surgery on market simulators appears
  nowhere in 61 works; TradeFM (2026) explicitly defers exactly our question. Required evidence:
  all 8 cells on locked checkpoints, paired seeds, SESOI-graded ordered classification with 50k
  paired bootstrap on cell contrasts (train×infer interaction = attribution signature), Holm
  secondaries, honest unresolved cells.
- **OOD / kernel-swap axes.** Threaten: matching-engine ABM 2021 (swap as re-plumbing), M3 2026.
  Support: KineticSim 2026 (bitwise-identical books across configurations make the swap
  well-defined); no adjudicated work varies priority kernel or tick size on a *learned* simulator.
  Required: per-axis paired contrasts with class stability/flip reporting + demonstration that the
  swap changes M behavior on identical inputs.
- **Reflexive cell.** Threaten: TRADES 2025, DEX closed-loop 2026, Safe Compliant Execution 2025.
  Required: exploratory-only status, excluded from confirmatory inference, paired-seed discipline.
- **Architecture-transfer gate.** Threaten: implicit "transfer is folklore" attack. Required:
  preregistered gate, both lineages through the same 8-cell grid, both outcomes reported
  regardless.

### 2.6 Hostile scenario (strongest attack, verbatim record)

> "This is a domain transplant of an existing ablation design, not a discovery: the training ×
> inference constraint-enforcement factorial already exists in the PDE parent genre (Duruisseaux et
> al. 2024, with one face already in Solver-in-the-Loop 2020 and the whole cube already run
> internally as Paper D); in the market domain every production generator (Nagy 2023; MarS 2024;
> MarketGPT 2024; TABL-ABM 2025; TradeFM 2026) already trains raw and infers through an exact
> matching engine, so the headline cell is the field's default pipeline; the 'attribution' estimand
> is a fidelity/superiority comparison relabeled; and the remaining cells are a routine ablation
> any engineer would run."

Best defense: across 61 verified external works, none crosses training with inference enforcement
of any mechanism layer in a market/matching simulator, none trains a market simulator through an
exact combinatorial clearing layer, none performs locked-checkpoint surgery; the attribution
estimand (constitutive vs removable, SESOI-graded, with an honest unresolved class) appears nowhere
in the lane. Conditional on parent citation and scoped novelty, the attack reduces to taste.

### 2.7 Verdict: **survive_with_conditions**

1. Cite Duruisseaux et al. 2024 as external genre parent and Paper D as internal design parent;
   never claim "first train×inference constraint crossing"; novelty restricted to market-native
   combinatorial M plus the path-dependence attribution estimand.
2. Resolve the V1 flag by panel **[DONE 2026-09-06: collision_refuted 3-0; ruling recorded
   above]**.
3. Cite the single-cell market works (Nagy 2023; MarS 2024; MarketGPT 2024; TABL-ABM 2025;
   TradeFM 2026; M3 2026) as default-pipeline evidence only; no novelty claim for any single cell.
4. Cite matching-engine ABM (2021) and KineticSim (2026) as M-infrastructure prior art.
5. Preregister estimator/surrogate handling of discontinuity-induced gradient bias in through-M
   training arms (Does "Do Differentiable Simulators Give Better Policy Gradients?" ICLR 2026;
   Minimizing Surrogate Losses for DFL 2025 — LP/integer programs have zero gradient a.e.);
   estimator choice frozen before training.
6. Reflexive cell exploratory-only, excluded from confirmatory inference (TRADES 2025; DEX
   closed-loop 2026 for paired-seed discipline).
7. Preregister OOD axes and the architecture-transfer gate on both lineages; report all cells,
   axes, both lineage outcomes including class flips and nulls.

### 2.8 Hostile-T0 update (pre-calibration heuristic; NOT a calibrated forecast, NOT an activation decision)

**Point 0.22, range [0.12, 0.33].** Upward: 61 works, zero confirmed collisions (post-panel),
unoccupied market-side cube, production works deferring exactly this question. Downward: dense
adjacent genre inviting "routine ablation" optics; the estimand-boundary attack (attribution as
relabeled superiority). Relative to prior failed candidates (Solana SIMD-0525: 12–17%, lower
bound 12%; TSE 2027: 10–17%, lower bound 10%), zero confirmed collisions and a clear
transplant-plus-estimand residual justify a higher point, but the **lower bound 0.12 sits below
the 0.15 activation floor** — ALPHA alone could fail activation in the pessimistic branch; this is
a primary input to the merge-gate decision below.

---

## 3. Route-graph failure reuse (required output)

Internal entries adjudicated for both families (not collisions):

- **Paper D (internal, terminal 2026-09-03)** — parent for both families (GAMMA T2 minimal special
  case; ALPHA design + statistical contract). Cite, never collide; novelty must not double-count.
- **Hard-matching gradient lane** (Lee–Yu–Yang; Parmas–Sugiyama; Potto; StochasticAD/ADEV; ICLR
  2026 event-binned weak derivatives) — pre-adjudicated distinct (gradient-estimation estimand) at
  the 2026-09-05 boundary-flux audit; reused as citation, not re-audited.
- **Internal metaorder-reconstruction audits (2026-09-05)** — distinct (tape-to-parent inference
  level); consumed as citation.
- **Cycle-7 conservation-symmetry audit (2026-08-26)** — consistent (conserved charges fix
  equivalence classes, not transition laws); informs T1 framing, no conflict.
- **Route-graph closures (222 failed routes, 99 audits)** — V2/V6 and sibling closure semantics
  respected throughout; no failed_closed family reopened; both families are new formula/new
  estimand objects under child-card provenance rules.

---

## 4. Merge/split gate decision (recorded 2026-09-06, with D-2 evidence)

**Decision: ONE paper, GAMMA-led.** GAMMA T1–T3 theorem core carries the scientific claims; the
ALPHA eight-cell cube is the experimental section (the Paper D propositions+audit template).

Rationale (from D-2 evidence):

1. **Activation-gate asymmetry.** GAMMA hostile-T0 = 0.55 [0.38, 0.70]; ALPHA = 0.22 [0.12, 0.33].
   ALPHA's lower bound (0.12) is below the 0.15 activation floor — ALPHA as a standalone topic
   could fail activation in the pessimistic branch; merged into a GAMMA-led paper it contributes
   experimental machinery without carrying standalone activation risk. GAMMA standalone carries the
   reverse risk ("known mathematics, new packaging" — its strongest attack), which the cube's
   empirical bite answers.
2. **Mutually neutralizing strongest attacks.** ALPHA's "domain transplant of a workshop ablation"
   is answered by GAMMA's theorem core (the cube measures T1/T3-predicted structure — the
   kernel-swap OOD axis IS T3's partial-mechanism exposure; the through-M training arms are where
   T1's fiber binds). GAMMA's "kernel label and tape format" packaging attack is answered by
   ALPHA's empirical attribution results on a real instrument.
3. **Shared instrument and compute.** Both halves use lab-asset-v3 as the exact-truth engine; the
   merged compute plan stays at Paper-D scale (≈ Paper D × 2 ceiling) rather than two papers'
   worth; the statistical contract is inherited once, verbatim.
4. **Both families meet the D-2 quantitative bar** (68 and 61 verified primary works ≥ 15; zero
   confirmed, zero unresolved collisions after panels), so the merge is between two survivors, not
   a rescue.

Fallback (unchanged from D-3): if the merged paper dies at D-1, the die mode determines whether any
component survives; no automatic split into two papers.

---

## 5. Status relative to the activation gate (informational only)

| Gate item | GAMMA | ALPHA | Merged paper |
|---|---|---|---|
| hostile_t0_lower_bound ≥ 0.15 | 0.38 ✓ | 0.12 ✗ (point 0.22 ✓) | carried by GAMMA-lead |
| ≥15 primary works | 68 ✓ | 61 ✓ | ✓ |
| ≥2 killer tests | pending D-1 | pending D-1 | D-1 next |
| ≥2 independent simulator lineages | pending D-1 contracts | same | EcoMD v2 + fact-surrogate |
| no unresolved direct collision | ✓ (post-panel) | ✓ (post-panel) | ✓ |
| real-data bridge qualified | pending | pending | stylized-fact bridge at D-1 |
| outcome-blind decision, explicit authorization, contamination control, confirmation split | — | — | D0+ |

The hostile-T0 numbers above are **pre-calibration heuristics**; protocol requires calibrated
forecasts to `research/discovery/forecast_ledger.yaml` at D-1 before any activation decision.

---

## 6. Sequencing (next: D-1)

1. **D-1 (next)**: killer tests (≥2 per family, specified against the D-2 die modes), theorem-work
   proof attempts (T1 granularity dichotomy; T2 bounded quantitative lead — legal in screening),
   simulator contracts for both lineages, stylized-fact bridge qualification, calibrated hostile-T0
   forecasts to the forecast ledger.
2. **D0**: outcome-blind freeze of the merged-paper preregistration (grid, contract v1, analyzer
   list) — requires explicit PI authorization before any GPU/execution.
3. Ops prerequisite before any D1 execution: V100 disk cleanup (98%/96% full).

*Session ledger: logs/2026-09-06.md Session 4. Workflow artifacts: d2-hostile-neighborhood-audit
(55 agents) and alpha-v1-panel (3 agents) under the session task records.*
