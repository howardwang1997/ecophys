# EcoMD next-direction exploration — 2026-08-22

**Status:** superseded by the same-day T0 result; both Q and C cards are FAIL/closed, and no new NCS/NMI
route, data purchase, GPU run, or real-outcome access is authorized

**T0 update (2026-08-22):** the 29-work Q matrix, 32-work C matrix and exact passive-equivalence reduction found
no surviving theorem, certificate or algorithm. Q0, Q1, Q2 and C0 are all RED. See
`papers/proposal/ecomd_observation_quotient_t0_result_2026-08-22.md`. The candidate rankings below record the
pre-audit exploration state and are not current authorizations.

**Venue prior:** *Nature Computational Science* is the primary fit. *Nature Machine Intelligence* is conditional
on a genuinely central ML contribution plus real decision or autonomous-agent evidence.

## 1. Decision

The next search should not begin by making EcoMD more elaborate or more visually similar to molecular dynamics.
The strongest candidate scientific question is:

> In a stochastic interacting-agent system observed only through aggregate or event-level outputs, which
> intervention responses are identifiable, transferable and falsifiable, and what is the least additional
> observation or intervention needed to identify them?

Two connected claim cards deserve a zero-compute T0 audit:

1. **Observation quotient and intervention identifiability** — the primary candidate.
2. **Intervention-preserving non-equilibrium coarse-graining** — a secondary candidate that may either supply
   the first candidate's computational construction or fail independently at prior art.

They are hypotheses about a possible new method, not current novelty claims. A third, rare-event path direction
should remain parked unless one of the first two survives. EcoMD should be a difficult application and possible
failure case, not the source of ground truth.

## 2. Binding evidence and constraints

The old invariant-measure calibration route remains closed at G0. Persistent chains, hybrid pathwise/LR
gradients, randomized truncation, SMC reweighting and mixing diagnostics do not constitute a new method. The
generic simulator-audit route and the current thermodynamic/TUR route are also closed.

The repository has valuable infrastructure:

- state-complete stochastic continuation, absolute clock and RNG semantics;
- exact-resume and distributed-resume tests;
- synthetic aggregate-L2 reconstruction, sign-gauge and observation-only controls;
- continuous-time queue/Hawkes likelihood infrastructure;
- reproducible manifests, chronological splits and fail-closed preregistration.

It does not yet have positive model evidence:

- there is no endorsed checkpoint;
- the frozen state-complete M1 result is 2/11 in every fixed window;
- the current EcoMD-to-L2 adapter is a synthetic aggregate fixture, not an individual-order or price-time
  priority model;
- the real observation-bridge chain remains failed or unconfirmed, and its exposed test data cannot become a
  new confirmation set.

Consequently, no candidate may use an EcoMD-generated mechanism as evidence that the same mechanism exists in
markets.

## 3. Venue logic

*Nature Computational Science* explicitly seeks computational techniques and mathematical models with
cross-disciplinary scientific use. That matches a general identification or coarse-graining method validated
outside finance and then applied to markets
([journal scope](https://www.nature.com/natcomputsci/journal-information)).

*Nature Machine Intelligence* requires machine learning, AI, robotics or multi-agent intelligence to be central,
not merely present inside a financial application
([journal scope](https://www.nature.com/natmachintell/submission-guidelines/about/aims)). A market simulator becomes
an NMI-shaped project only if, for example, an active-design learner chooses informative interventions, a learned
representation is the main methodological advance, or a randomized human/AI-agent experiment yields real
decision value. Without that evidence, NCS is the more coherent target.

## 4. Pre-T0 candidate ranking (historical)

| Rank | Candidate | Current status | NCS fit | NMI fit | Estimated T0 survival |
|---:|---|---|---:|---:|---:|
| 1 | observation quotient + intervention-identifiable response | AMBER+ | 5/5 | 4/5 conditional | 15–25% |
| 2 | intervention-preserving, cross-resolution coarse-graining | AMBER | 4/5 | 2/5 | 10–20% |
| 3 | partially observed hybrid rare-event paths | AMBER− | 3/5 | 3/5 | 5–10% |
| 4 | robust market-rule design across observationally equivalent simulators | RED without deployment partner | 3/5 | 5/5 conditional | below 5% without partner |
| 5 | mixed human–AI trading-agent ecology | RED without randomized platform | 2/5 | 4/5 conditional | below 5% without platform |
| 6 | hydrodynamic/renormalization limit of latent market particles | RED | 2/5 | 1/5 | below 5% |

These are project-planning probabilities, not acceptance-rate estimates. From the current starting point, the
joint probability of a complete Nature-level paper should not be put above roughly 3–8% for candidate 1 or 2–5%
for candidate 2. Conditional on a genuinely irreducible result, two external-system validations and a frozen
multi-market intervention result, an NCS submission could become credible; before those gates, it is not.

## 5. Candidate 1 — observation quotient and intervention identifiability

### 5.1 Scientific object

Let the latent simulator evolve under a control or intervention (u):

\[
X_{t+\Delta}\sim K_{\theta,u}(X_t,\cdot),
\qquad Y_{0:T}=H_\Delta(X_{0:T}),
\]

where (H_\Delta) is an observation operator such as queue aggregation, temporal binning or loss of agent
identity. Define observational equivalence over the passive protocol set \(\mathcal U_0\):

\[
\theta\sim_{H,\mathcal U_0}\theta'
\quad\Longleftrightarrow\quad
\mathcal L_\theta(Y_{0:T}\mid u)
=\mathcal L_{\theta'}(Y_{0:T}\mid u)
\quad\text{for all }u\in\mathcal U_0.
\]

The target is not a supposedly true latent force. It is an intervention-response functional
\(\psi_u([\theta])\), such as the change in the distribution of spread recovery or queue depletion. The first
question is whether \(\psi_u\) is constant on the passive observational equivalence class. If it is not, the
counterfactual is not identified no matter how small the passive fitting loss becomes.

A possible active-design object is

\[
u^* = \arg\max_{u\in\mathcal U}
\inf_{\theta,\theta'\,:\,\theta\not\sim\theta'}
D\!\left(
\mathcal L_\theta(Y\mid u),
\mathcal L_{\theta'}(Y\mid u)
\right),
\]

or a computationally tractable local version using the least singular direction of a response Jacobian after
quotienting known gauges.

### 5.2 What would be genuinely new

At least one of the following must survive a primary-paper audit:

- necessary and sufficient conditions for an intervention-response functional to be identifiable on an
  observation quotient of a stochastic interacting system;
- a computable distinguishability certificate with finite-sample coverage under aggregate, irregular event
  observations;
- an active intervention/observation design algorithm whose guarantee is defined on the quotient rather than on
  an arbitrarily parameterized latent state;
- a no-go theorem showing when no passive calibration objective can support the desired policy claim, paired
  with a minimal intervention construction that removes the ambiguity.

Simply combining standard SBI, Fisher information, Bayesian optimal design or a differentiable simulator is a
G0 failure.

### 5.3 Nearest collisions

- Aggregate snapshots without individual identity have already been used to learn stochastic dynamics
  ([Ma et al., ICML 2021](https://proceedings.mlr.press/v139/ma21c.html)).
- Identifiability under partial observation and hidden variables is not new; recent examples include partially
  observed linear causal models
  ([Dong et al., NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/36ecc1d1b883afc0e882876cbdd123ab-Abstract-Conference.html))
  and recovery of hidden nonlinear dynamics from incomplete observations
  ([Stepaniants et al., Physical Review Research 2024](https://journals.aps.org/prresearch/abstract/10.1103/PhysRevResearch.6.043062)).
- Heterogeneous interaction inference from trajectories is already addressed by
  [Collective relational inference](https://www.nature.com/articles/s41467-024-47098-7).
- Parameter estimation for kinetic interacting particles under partial discrete observation already has
  consistency and asymptotic theory
  ([Amorino and Pilipauskaitė](https://arxiv.org/abs/2410.10226)).
- Stationary diffusion models already represent interventions and generalize to unseen interventions
  ([Lorch et al., AISTATS 2024](https://proceedings.mlr.press/v238/lorch24a.html)); multiple interventional
  stationary distributions have also been used to study unique SDE recovery and intervention-count bounds
  ([Zweig et al.](https://arxiv.org/abs/2505.15987)).
- Active sequential SBI already chooses informative simulator parameters
  ([ASNPE, NeurIPS 2024](https://papers.nips.cc/paper_files/paper/2024/hash/e6da278cdd692077b7e4a99d55573d9c-Abstract-Conference.html)).
- Financial-simulator non-identifiability and multivariate calibration objectives are already explicit
  ([Wang, Ren and Yang](https://arxiv.org/abs/2407.16566)).
- Interventionally consistent ABM surrogates already show that passive agreement need not preserve policy
  effects ([Dyer et al.](https://arxiv.org/abs/2312.11158)).

The remaining possible gap is therefore narrow: **identification and design for an intervention-response
functional on an aggregate-observation quotient of a stochastic interacting system**, not generic parameter
recovery, passive calibration or surrogate consistency.

### 5.4 Required evidence

1. Linear interacting OU or McKean–Vlasov system with an analytic observational-equivalence class and known
   intervention response.
2. A nonlinear non-financial interacting system, such as active matter, an epidemic/opinion ABM or a stochastic
   queueing network, with a known or controllable intervention.
3. EcoMD synthetic full-state versus aggregate-observation experiments; failure is allowed and informative.
4. At least two independent market-rule regimes or venues. Candidate intervention families include tick-size,
   fee, auction and volatility-control changes, but none is selected until an outcome-blind support audit passes.
5. A final intervention whose outcomes are held out from model choice and whose effect distribution, not only
   sign, is predicted in advance.

### 5.5 Kill rules

- The proposed theorem reduces to standard observability, partial identification or optimal design after a
  change of notation.
- The certificate cannot detect a constructed pair of passive-equivalent models with opposite response signs.
- A Hawkes/state-space/observation-only baseline matches the intervention prediction at equal budget.
- Fewer than two independent real intervention regimes survive outcome-blind data qualification.
- The held-out intervention falls outside the reported predictive interval or the direction reverses across
  independent venues.

## 6. Candidate 2 — intervention-preserving non-equilibrium coarse-graining

### 6.1 Scientific object

For fine dynamics \(K^f_u\), restriction operator \(R_\Delta\), and learned coarse dynamics \(K^c_{\Delta,\bar u}\),
measure the interventional commutator

\[
\mathcal E_{u,\Delta,m}(\mu)=
D\!\left(
R_{\Delta\#}(K^f_u)^m\mu,
K^c_{\Delta,\bar u}R_{\Delta\#}\mu
\right).
\]

The method should distinguish memory caused by hidden degrees of freedom from memory introduced by temporal
binning, queue aggregation and identity loss. The headline test is whether the diagram remains approximately
commutative for unseen resolutions and unseen interventions, not whether one fitted memory kernel looks
plausible.

### 6.2 What would be genuinely new

The candidate needs an error decomposition or bound that connects:

- memory truncation;
- observation/filter-induced memory;
- stochastic event discretization;
- intervention-response error across resolutions.

An ordinary learned GLE, colored-noise model or multi-scale latent SDE is insufficient. Recent work already
covers learned GLE coarse dynamics and fluctuation–dissipation constraints
([AIGLE](https://pmc.ncbi.nlm.nih.gov/articles/PMC10998567/)), differentiable GLE fitting
([DiffGLE](https://arxiv.org/abs/2410.08424)), learned stochastic macro/micro SDEs
([NeurIPS 2025](https://proceedings.neurips.cc/paper_files/paper/2025/hash/4ec360efb3f52643ac43fda570ec0118-Abstract-Conference.html))
and memory-minimizing collective variables
([MEMnets, NCS 2025](https://www.nature.com/articles/s43588-025-00815-8)).

The broader intersection is also occupied more heavily than its name suggests:

- approximate causal abstraction already formalizes cross-scale fidelity under interventions
  ([Beckers, Eberhardt and Halpern](https://arxiv.org/abs/1906.11583));
- Mori–Zwanzig GLEs have been derived for externally driven non-equilibrium systems
  ([Izvekov, Physical Review E 2021](https://journals.aps.org/pre/abstract/10.1103/PhysRevE.104.024121));
- data-driven state-dependent memory is already available
  ([Ge, Zhang and Lei, Physical Review Letters 2024](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.133.077301));
- multidimensional, dynamically consistent, long-time GLE learning with fluctuation–dissipation constraints is
  already explicit ([Xie and E, JCTC 2024](https://pubmed.ncbi.nlm.nih.gov/39258946/));
- the order book has already been treated as a financial Brownian particle with memory/FDT tests
  ([Yura et al., Physical Review Letters 2014](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.112.098703)).

Therefore even the phrase “intervention-preserving coarse-graining” is not enough. The possible contribution
must be a specific response-identification theorem or error guarantee for path-dependent aggregate event
observations that these works do not already imply.

### 6.3 Required evidence and kill rules

- Fine-ground-truth MD or active-matter system, an independent jump/queue system, EcoMD synthetic paths and
  multi-resolution market L2 are all required.
- One observation scale and one market must remain completely unseen during model selection.
- The method fails if the learned memory or response changes arbitrarily under harmless unit/bin choices, the
  coarse-graining diagram does not close, or a finite-history state-space/Hawkes model reaches the same unseen-
  scale and unseen-intervention performance.

## 7. Parked directions

### Hybrid rare-event paths

Committors, transition-path sampling, Doob transforms and ML rare-event sampling are mature. The only possible
opening is a rate-correct, partially observed hybrid jump/continuous estimator with calibrated coverage. The
market event must be repeated queue depletion or local liquidity dislocation, not a post-hoc list of famous
crashes. This remains parked because both method novelty and external validity are lower than for candidates 1
and 2.

### Robust rule design

Optimizing a policy over an ensemble of observationally compatible simulators is scientifically attractive, but
without an exchange, regulator or controlled experimental platform there is no credible welfare ground truth.
Do not begin simulator control before such a collaboration exists.

### Human–AI trading ecology

This is the clearest NMI-shaped application, but AI homogeneity, herding and algorithmic market stability are
already crowded. Only a randomized experiment spanning AI share, model diversity, information overlap and at
least two market mechanisms could reopen it. Pure EcoMD simulation is insufficient.

### Hydrodynamic or universal-scaling route

Latent EcoMD particles have no established correspondence to observable traders, so an \(N\to\infty\) limit has
no current empirical meaning. Do not pursue a kinetic/SPDE or scaling-collapse claim until the observation
quotient has been solved and a real resolution sequence has been defined.

## 8. Enabling work that is not a headline contribution

A trustworthy conditional aggregate market simulator remains necessary infrastructure:

- replace one-step/one-event synthetic semantics with a declared aggregate-bin contract;
- compare against LOB-Bench-compatible autoregressive, diffusion, Hawkes and parametric baselines
  ([LOB-Bench, ICML 2025](https://proceedings.mlr.press/v267/nagy25a.html));
- evaluate matched-length conditional distributions and response functions, not stylized-fact pass counts;
- require chronological and cross-market holdouts;
- keep latent agent variables explicitly non-identifiable unless a candidate-1 certificate says otherwise.

Completing this work may support a strong model/software paper, but it is not by itself an NCS or NMI claim.

## 9. Recommended T0 program

No production training is justified yet. Run two claim-card audits in parallel for at most 14 calendar days.

### Days 1–4: nearest-work matrices

For each of candidates 1 and 2, inspect at least 20 primary sources across interacting-particle inference,
observability/identifiability, active design/SBI, causal abstraction, Mori–Zwanzig/GLE, temporal filtering and
financial simulator calibration. Every proposed equation must be mapped to its nearest existing result.

### Days 5–9: theorem and counterexample scratch

- Construct two microscopic stochastic systems that are passive-observation equivalent but give different
  responses to a specified intervention.
- State the proposed quotient-response theorem or no-go result with assumptions.
- For candidate 2, derive the interventional commutator and an explicit memory/observation/discretization error
  decomposition on a solvable linear system.
- Try to reduce each result to established observability, Fisher-information, Mori–Zwanzig or surrogate-
  consistency theory. Successful reduction means FAIL.

### Days 10–12: outcome-blind data support

Using only rule documents, schema, event identities, timestamps and availability metadata, determine whether at
least two independent market intervention families and a later held-out intervention can be acquired. Do not
open outcomes or purchase data.

### Days 13–14: G0 decision

A candidate passes only if all four conditions hold:

1. one irreducible mathematical or algorithmic statement survives the primary-paper matrix;
2. one analytic system and two independent external-system benchmarks are specified;
3. a real intervention panel can support chronological, venue-level confirmation;
4. the main claim is method-dependent and has a written negative control and kill rule.

If neither card passes, do not merge them into a larger proposal. Return to problem selection.

## 10. Six-figure paper spine if candidate 1 eventually survives

1. Observational-equivalence counterexample and why passive realism is insufficient.
2. Quotient-response definition, theorem/certificate and active design algorithm.
3. Analytic and nonlinear external-system recovery with strong baselines.
4. EcoMD observation map, identifiable versus non-identifiable quantities and failure cases.
5. Frozen prediction of an unseen market-rule response across two venues/regimes.
6. Coverage, ablation, scaling, compute cost and a map of conditions where the method abstains or fails.

Until this spine is achievable, the honest project state is **direction exploration, not an active Nature
submission plan**.
