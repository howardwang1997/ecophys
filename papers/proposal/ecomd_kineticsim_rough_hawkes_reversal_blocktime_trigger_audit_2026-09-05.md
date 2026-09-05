# EcoMD KineticSim, rough Hawkes--Heston, reversal, and block-time trigger audit

**Date:** 2026-09-05 NZST  
**Mode:** bounded post-closure trigger audit; not a new discovery cycle  
**F1 quick screens:** six  
**F2 collision/contract screens:** two  
**F3 audits / machine cards:** zero / zero  
**Decisions:** four new `not_trigger`; two route-graph duplicates  
**Candidate harvesting, outcome access, implementation, simulation, SSH, and GPU work:** not authorized

## 1. Executive decision

| Screen | Attractive claim | Decisive result | Decision |
|---|---|---|---|
| Public Trader Identity | Hyperliquid L4 wallet labels may identify heterogeneous actors and adverse selection | Already audited: wallets are pseudonymous, splittable and aggregable rather than beneficial-owner or complete-policy labels; the source owns broad identity prediction | duplicate of `hyperliquid_l4_identity_truth_asset_screen_20260904` |
| KineticSim | A persistent CUDA kernel may supply a fast independent truth engine or an EcoMD systems contribution | The four backends are one author-maintained model family; only the two CUDA versions share exact random marks, the CPU check is aggregate and permissive, and the source owns the persistent-clearing contribution | `not_trigger` |
| Exact conditional point-process simulation | Shared latent Poisson/noise variables may give pathwise market-impact counterfactuals | Already audited: the result is conditional on the fitted point-process model and is not an assigned field counterfactual | duplicate of `hyperliquid_twap_field_truth_asset_preflight_20260904` |
| Matched short-horizon reversal | A sign-memory target with nearly zero return autocorrelation may expose a missing EcoMD mechanism | The source owns the measurement and explicitly does not select compensated liquidity provision; a sign--magnitude twin matches reversal and zero autocovariance under many mechanisms | `not_trigger` |
| Rough Hawkes--Heston microfoundation | The explicit micro-to-macro map may enable identifiable physics-informed calibration | The map has exact positive-dimensional gauges, Proposition 5.2 constructs many inverse images, and Remark 5.3 already states microscopic non-identifiability; generic SBI already represents multiple data-consistent configurations | `not_trigger` |
| Jump-diffusion AMM block time | The jump floor may create a new collision-clock law for EcoMD | The paper owns the jump decomposition, floor and LP-side optimum, while the repository already closed generalized block-time LVR under direct theory and empirical parents | `not_trigger` |

None removes a recorded hard blocker or leaves a contribution that is both scientifically
identified and irreducible to direct systems, SBI, measurement, or AMM theory. The correct action
is another zero-compute kill round, not an experiment plan.

## 2. KineticSim is a useful implementation, not a new EcoMD truth system

### 2.1 Question contract

The native object is the terminal aggregate call-auction book produced from one initial book, agent
population, action rule, clock and random tape. The relevant alternatives are:

- **H1 -- semantics-preserving acceleration:** a persistent shared-memory CUDA schedule implements
  exactly the same transition kernel as a declared reference engine;
- **H0 -- changed stochastic or market semantics:** backend-dependent random streams, arithmetic,
  tie rules, aggregation or observation phases produce superficially similar summary statistics
  while implementing different paths.

A discriminating result would require a pathwise commuting test under identical semantic random
marks, plus an independently maintained oracle. Passing would certify an implementation; failing
would locate a software or specification defect. Neither answer by itself establishes a new market
mechanism.

### 2.2 What the source actually supplies

[Jayakody and Jayakody (2026)](https://arxiv.org/abs/2606.21784) formalize persistent,
state-carrying clearing: one block owns one price-grid market, keeps the aggregate book in shared
memory across steps, aggregates orders by atomics and clears with cooperative scans. On an RTX 5090
they report 54.7 billion agent-events per second and large speedups over NumPy, PyTorch, JAX and a
naive CUDA kernel. This is a genuine systems result, and it is already the source's central claim.

The pinned [Apache-2.0 repository](https://github.com/KineticSim/Project-KineticSim/tree/70527b0d0a763e017ab0785fb50986a8ac50ecb3)
contains an optimized CUDA backend, a deliberately naive CUDA ablation, PyTorch/JAX implementations
and a NumPy reference. The scientific object is deliberately narrow: a discrete-time,
price-grid, uniform-price call auction over aggregate bid and ask quantities, with hand-written
noise, momentum, maker and fundamental rules. It does not retain individual order priority, fill
identity, inventory, latency messages or an adaptive policy state.

The strongest correctness claim also needs careful scope:

- optimized and naive CUDA share device-side decisions and a stateless counter-based random
  function, so their final price, volume and trade count can be compared exactly;
- the NumPy engine uses a different RNG and is checked only through mean final price, final-price
  standard deviation and mean volume;
- the public `validate_correctness.py` declares that aggregate CPU comparison passed whenever all
  three relative errors are below `0.10`. The paper's displayed configuration happens to be within
  `0.1%`, but that empirical row is not a pathwise semantic certificate;
- every backend and its reference specification are maintained in the same repository. This is an
  engineering cross-check, not an independent scientific lineage.

[JAX-LOB](https://arxiv.org/abs/2308.13289) already establishes massively parallel GPU LOB
simulation and end-to-end RL as a method neighborhood. KineticSim distinguishes itself with the
persistent batch-clearing pattern; porting that already-published pattern into EcoMD, or benchmarking
it on an A800 and two V100s, would be reproduction and hardware engineering.

### 2.3 Route collision and decision

The proposal collides with `cross_simulator_disagreement_intervention_certificate`,
`adaptive_scheduler_information_filtration_response`, and
`stochastic_simulator_gradient_semantic_conformance`. If two implementations have the same complete
kernel, a discrepancy is a conformance failure. If EcoMD's Langevin/time-bucket dynamics replace
the call auction, the compared systems no longer implement one estimand. If only throughput is
claimed, KineticSim owns the contribution.

**Decision:** `not_trigger`. Re-enter only for two independently maintained engines that implement
one full state/action/clock/randomness contract and for a new certificate or complexity result not
reducible to deterministic conformance, analytic truth, common-random comparison or ordinary
systems benchmarking. A GPU port is not such a trigger.

## 3. Rough Hawkes--Heston gives a non-identifiability certificate, not an inference topic

### 3.1 Question contract

The native object is the law of rescaled price, variance and common jumps generated by a marked
Hawkes order-flow model. The alternatives are:

- **H1 -- identified microfoundation:** the macroscopic rough Hawkes--Heston coefficients determine
  the microscopic endogeneity, sign asymmetry and marked-excitation parameters;
- **H0 -- observational quotient:** distinct microscopic parameter vectors induce the same complete
  macroscopic law, so calibration can identify only combinations or an equivalence class.

A useful positive result would recover a uniquely defined microscopic functional from declared
observations. A useful null result would state the identified quotient and prohibit semantic claims
about its individual coordinates.

### 3.2 Exact gauges in the published map

[Wang, Wu, and Zhu (2026)](https://arxiv.org/abs/2608.07709) prove full-sequence convergence of a
Poisson-embedded marked Hawkes system to the complete canonical rough Hawkes--Heston weak solution.
Their coefficient map includes

\[
 \nu_J(dz)=2\frac{\bar p m_\star\mu_0}{\theta}F_J(dz),\qquad
 \xi=\frac{\theta c_Jr_\star}{m_\star},
\]

\[
 c_B=\frac{\theta\mu_0}{m_\star}
 \frac{\omega_++\beta^2\omega_-}{(\omega_++\beta\omega_-)^2},\qquad
 \rho=-\frac{(\beta-1)\sqrt q}{\sqrt{(1+q)(1+\beta^2q)}} ,
\]

with the remaining drift determined by these quantities and `mu_0`. Two exact transformations are
therefore invisible to every reduced-form coefficient:

\[
 (\theta,m_\star)\mapsto(a\theta,am_\star),\qquad a>0,
\]

and

\[
 (c_J,r_\star)\mapsto(sc_J,r_\star/s),\qquad s>0.
\]

These are not merely weak-identification directions. In the published finite-`T` construction,
`theta` and `m_star` enter the observed normalization through their ratio, while `c_J` and `r_T`
enter marked excitation through their product. The same gauges survive the displayed finite-scale
model.

There is further nonuniqueness in sign asymmetry. For a prescribed negative `rho`, Proposition 5.2
allows a continuum of sufficiently large `beta` values, solves for a compatible `q`, and then
adjusts the other microscopic constants. The paper's numerical example explicitly calls
`beta=8` one admissible realization, not the realization. Most decisively, its own Remark 5.3 says
that the individual parameters remain non-identifiable because only `theta/m_star` and `c_J r_star`
are determined.

### 3.3 The obvious ML repair is occupied

Learning a posterior over all compatible parameters, reporting stiff combinations, or returning a
set instead of a point is valuable practice but not a new ICLR contribution. [Schroeder and Macke
(ICML 2024)](https://proceedings.mlr.press/v235/schroder24b.html) already train simulation-based
model inference over model components and parameters and explicitly recover multiple
data-consistent configurations and non-identifiable parameters. Classical profile likelihood,
Bayesian partial identification and model-sloppiness analysis cover the same product/ratio fibres.
The repository's broader `observation_quotient_response` route already requires a new action-level
functional that is constant on the passive equivalence class.

Finite-scale correction does not rescue the frozen question: the two displayed gauges are exact in
the source construction, not artifacts of taking `T` to infinity. Adding raw marked-event labels
would change the observation contract and reduce to ordinary Hawkes likelihood/SBI; using only
price and variance cannot recover the semantic microcoordinates. EcoMD is also not an independent
implementation of this marked point process.

**Decision:** `not_trigger`. Re-enter only if a legal observation or intervention is proved to
identify a nontrivial market-native functional outside the published coefficient quotient, with a
matching lower bound and a method false for existing SBI/partial-identification parents. More
finite-`T` paths cannot break an exact gauge.

## 4. Short-horizon reversal is a strong measurement target but not mechanism truth

### 4.1 What is established

[Kitron and Wengrowicz (2026)](https://arxiv.org/abs/2608.21888) report a carefully matched
out-of-sample measurement: at 15 minutes, directional reversal appears in 90% of 183 Binance pairs
versus 2.7% of 187 US stocks and ETFs. The result survives a frozen six-month holdout, permutation
tests, artifact checks and independent venues. It is concentrated after aggressive taker flow, but
the authors correctly state that this is consistent with compensated liquidity provision rather
than a test that selects that mechanism. They also show that a fitted Glauber chain matches the
predictive AUC while materially overproducing linear autocorrelation and variance-ratio effects.

The pinned [MIT replication repository](https://github.com/nadav2/short-horizon-reversion/tree/5eb5117d353abe0569f2d98aeadddf634e044e1f)
contains frozen universes, result files, hashes and deterministic analysis code. The raw candles and
order-flow inputs are intentionally gitignored and rebuilt from public Binance, other exchange,
Dukascopy and credentialed Alpaca interfaces. This is a good reproduction asset, but its reported
sample and holdout outcomes are already used; a later public period could replicate the measurement,
not create a new mechanism intervention.

### 4.2 Exact sign--magnitude twin

Write a zero-mean return as `R_t=S_t M_t`, where `S_t` is an unbiased sign and `M_t>0`. Let

\[
 p=P(S_{t+1}=S_t)<\tfrac12,
\]

so the optimal one-lag direction is reversal. Define

\[
 a=E[M_tM_{t+1}\mid S_{t+1}=S_t],\qquad
 b=E[M_tM_{t+1}\mid S_{t+1}\ne S_t].
\]

Then

\[
 E[R_tR_{t+1}]=pa-(1-p)b.
\]

For any reversal strength `p` and any `b>0`, choosing

\[
 a=\frac{1-p}{p}b
\]

makes lag-one return autocovariance exactly zero while leaving the sign transition and hence the
one-lag directional predictor unchanged. This conditional construction is attainable as a
stationary process: generate the sign by iid transition increments `U_t=S_{t-1}S_t`, with
`P(U_t=1)=p`, and set `M_t=x` after a same-sign increment and `M_t=y` after a reversal, where
`x/y=(1-p)/p`. Then `E[R_t]=0` by global-sign symmetry and
`E[R_tR_{t+1}]=E[M_t](px-(1-p)y)=0`. Conversely, other positive ratios produce either sign of
linear autocorrelation without changing the sign rule. The same AUC and near-zero Pearson
correlation can therefore arise from many joint sign--magnitude laws.

This witness explains why adding the statistic as an EcoMD loss is not mechanism identification.
A liquidity-provider inventory response, bid--ask bounce, bar aggregation, liquidation flow, common
information or a designed latent kernel can all be tuned to the same passive summary pair. The
source's own rejected Glauber generative check is evidence for this gap, not a ready-made repair.
Task-aware generator training and simulator adequacy metrics already occupy the generic ML move.

**Decision:** `not_trigger`. Re-enter only with an assigned action or an authoritative maker-state
label that separates compensated liquidity response from the named alternatives on the same
prestate, plus untouched independent confirmation. Matching reversal AUC, autocorrelation and
variance ratio is useful evaluator QA, not an ICLR mechanism paper.

## 5. Jump-diffusion block time is a direct occupied descendant

[Bundi (2026)](https://arxiv.org/abs/2608.30321) decomposes constant-product AMM LVR into a
block-time-dependent diffusion term, a block-time-independent jump term and a bounded remainder.
For symmetric jump laws the jump component is an exact positive floor; the paper also derives an
LP-side optimum that is invariant to pool size and jump parameters at the order of the
decomposition. These are the attractive theorem, the null boundary and the application. They are
all already the source's contribution.

The existing `generalized_block_time_amm_response` route was closed because [Nezlobin and Tassy
(2025)](https://arxiv.org/abs/2505.05113) analyze deterministic and arbitrary inter-block laws and
prove constant spacing asymptotically optimal, while [Fritsch and Canidio
(2024)](https://arxiv.org/abs/2404.05803) measure how AMM arbitrage losses change with block time.
The new jump floor is a legitimate extension of that literature, not a new unoccupied EcoMD
question. Simulating jumps or endogenous agents would reproduce the theorem unless a separately
identified welfare action and response were supplied; the source itself warns that LP-side LVR is
not full protocol welfare.

**Decision:** `not_trigger`. Re-enter only for a protocol-native interaction and falsifiable
response theorem outside LVR, arbitrage latency and price-tracking stability, with unbundled
assignment and complete state. Do not rename block time as a molecular free-flight or collision
clock.

## 6. Two exact duplicates

### 6.1 Public Trader Identity

The Hyperliquid paper and repository were already used by the 2026-09-04 L4 truth-asset audit. The
archive materially improves message lifecycle visibility, but one wallet need not be one economic
actor and does not expose complete strategy, belief, owner, off-venue inventory or an assigned
counterfactual. Broad wallet-level adverse-selection and return-prediction claims are the source's
result. No later release or new field was found in this screen, so a second ledger entry would be a
duplicate rather than epistemic progress.

### 6.2 Exact conditional point-process simulation

The exact latent-Poisson conditional simulator was already included in the Hyperliquid TWAP field
preflight. It can compute paired strategy paths under a fitted point-process law, but the shared
latent noise is a model coupling, not observation of both field potential outcomes. It supplies no
native TWAP assignment tape, nonfill linkage, block prestate or independent confirmation. No new
capability claim remains to audit.

## 7. Portfolio and compute decision

KineticSim and rough Hawkes--Heston received the two collision/contract screens because they were
the only quick-screen candidates that could plausibly have supplied, respectively, a new truth
system or a theorem-level identifiable quotient. Both fail on exact grounds. Reversal and block
time close at F1; the other two are exact duplicates. No subject reaches F3, so there is no forecast,
machine card, experiment matrix or implementation plan.

In particular:

- no SSH connection was opened to `100.113.230.38`, `100.80.236.112`, or `100.123.220.57`;
- the A800 and two V100 workers received zero jobs;
- no external repository was cloned or executed, and no market outcome dataset was downloaded;
- the current Paper D decision cannot authorize unrelated EcoMD experiments.

The next admissible exploration must start from a newly released capability that actually removes
one named blocker: an independent full-state engine with the same native estimand; an authoritative
economic-actor or assigned-action label; a representation-invariant theorem outside the published
rough-model quotient; or an unbundled prospective market intervention with untouched replication.
Another GPU implementation, passive-statistic fit, parameter posterior, or block-time sweep is not
such a capability.
