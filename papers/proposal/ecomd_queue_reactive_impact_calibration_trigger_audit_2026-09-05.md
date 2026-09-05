# EcoMD queue-reactive impact-calibration trigger audit

**Date:** 2026-09-05  
**Stage:** bounded D-3 re-entry-trigger audit; no new discovery cycle  
**Archetypes screened:** `simulator_method`, `measurement_method`  
**Decision:** one superseding `not_trigger`; zero qualified triggers  
**Outcome, implementation, simulation, SSH and GPU access:** none

## Decision first

Noble, Rosenbaum and Souilmi's *Bridging the Reality Gap in Limit Order Book
Simulation* supplies a useful MIT-licensed reference implementation, but it does not reopen an EcoMD
paper route.

1. The code is not a post-audit capability change. The repository was created on 2026-03-23 and its
   two commits were complete by 2026-03-26, five months before the existing Cycle 16 and
   re-entry-capability audits. The previous record understated the software asset; the asset itself
   is not new.
2. The Queue-Reactive (QR) intervention and the historical EcoMD intervention are not the same
   action. QR injects a signed schedule of executable child trades into a price-time order book.
   EcoMD's primary `state_kick` displaces a random fraction of latent agent coordinates; its other
   historical channels change price, a detached fundamental, temperature or friction. Cross-engine
   agreement or disagreement would therefore mix action semantics with dynamics.
3. The reported concavity and reversion are not independent mechanism validation. The main QR
   experiment chooses a power-law feedback kernel from a theoretical impact target and calibrates
   its multiplier against that target before plotting the resulting response. The paper explicitly
   says the kernel can be tuned to any practitioner-selected concave profile. Its alternative
   maximum-likelihood fit uses anonymous historical trades and still does not observe the
   same-state response to an assigned parent metaorder.
4. A proposed "calibration-leakage" or "orthogonal intervention basis" method does not survive exact
   reduction. In a finite linear response class it is ordinary rank and persistent excitation; in
   an unrestricted nonlinear class a finite calibration family admits an off-support twin with
   arbitrary held-out response. Independent calibration/validation and inverse-crime warnings are
   established, while current work already supplies distribution-explicit interventional-fidelity
   confidence sequences.
5. The approximately 29 microsecond public-feed mode does not identify a latency race. The paper
   itself states that the feed omits participant identities, losing orders and private send times,
   and uses a proxy fill rule. Complete winner/loser race measurement and the relevant empirical
   method are already direct prior work.

The source is retained as an engineering baseline and calibration-provenance example. It creates no
topic card, experiment plan or machine authorization. The A800 and both V100 workers remain closed
to this formulation.

## 1. Scope and relation to the existing route graph

This audit was opened only to test whether a seemingly new executable QR implementation or its
impact-calibration structure removes a named blocker. It does not harvest a new topic family. The
paper was already registered as evidence for:

- `ballistic_inflight_liquidity_phase_space`;
- `interventional_lob_fidelity_benchmark`;
- `metaorder_memory_origin_discriminator`; and
- `prospective_counterfactual_market_simulator_validity`.

The append-only trigger entry `latency_impact_qr_model_fork` had already concluded that the paper
provides neither external counterfactual truth nor several independent policy environments. The
present audit supersedes that entry only because it adds the fixed software contract, exact action
comparison and calibration-provenance reduction. No route node or status changes.

No Databento observation, repository data product, simulator output, notebook or stored EcoMD
outcome was opened. Public paper text, repository metadata and the two relevant source entry points
at a fixed commit were inspected read-only.

## 2. Fixed source and software contract

### 2.1 Primary model

The paper projects a large-tick limit order book to spread and best-level imbalance, samples event
types and volumes from empirically estimated conditional distributions, and replaces exponential
waiting times with an empirical or mixture timing law. For impact it adds

\[
  \phi_t=\sum_{t_k<t}G(t-t_k)\,\varepsilon_k\sqrt{V_k},
  \qquad
  G(t)=\left(1+\frac{t}{\tau}\right)^{-3/2},
\]

then exponentially upweights only trades opposing the accumulated signed flow. The main text sets
`tau=50 s`, calibrates `m` against a specified ten-minute TWAP target path and reports
`m=0.036` after 100,000 Monte Carlo paths. It then evaluates 500,000 simulated metaorders.

The paper is unusually explicit that this is a flexible response-insertion mechanism: the kernel
and multiplier may be calibrated to a theoretical profile, proprietary metaorder curve or
historical-trade likelihood, and the structure can match profiles other than the illustrated one.
That is a practical modeling recipe, not evidence that the mechanism generated the target without
having seen it.

### 2.2 Fixed implementation

The official repository is MIT licensed at commit
`3080096cc0c79f43f1b82112cbde713710c014f6`. GitHub metadata records creation on 2026-03-23, an
initial commit `332d6899a254...`, and a README-only follow-up on 2026-03-26. There was no code commit
after the August 2026 route audits.

At that commit:

- `cpp/bin/run_metaorder.cpp` constructs equally spaced child timestamps from total volume,
  execution duration and maximum child size;
- a child is injected as an executable `Trade` on a declared side, rather than as a latent state
  displacement;
- each rollout is seeded independently with `std::mt19937_64`, and the default driver requests
  100,000 paths;
- `cpp/bin/calibrate_impact.cpp` profiles `m` over a 50 by 50 grid of `tau` and `beta` using the
  likelihood of observed signed trades conditional on the projected QR state; and
- the raw calibration pipeline depends on Databento MBP-10 data rather than an assigned public
  parent-metaorder experiment.

There is a small paper-level provenance discrepancy: the main text reports 100,000 paths and
`m=0.036`, while Appendix D reports 50,000 paths and `m=0.035`; the fixed executable defaults to
100,000 paths. This should be documented if the engine is ever used as a baseline, but it is not a
scientific contribution and does not alter the terminal decision.

## 3. Same-action contract fails

### 3.1 Required market-native question

The scientifically meaningful fork would be:

- **State `X`:** complete pre-metaorder book state, recent signed-flow history, participant or
  parent-order state needed by the proposed mechanism, and a fixed physical clock;
- **Action `A`:** the same signed child-order schedule, including intended attempts, timing, size,
  nonfills and stopping rule;
- **Response `Y`:** execution-time price impact, post-execution reversion, and signed endogenous
  add/cancel/trade response;
- **H1:** a learned stateful market mechanism transports the response to unseen schedules without
  target-specific response fitting;
- **H0:** a target-shaped feedback channel reproduces the calibrated schedule but has no identified
  response outside that target family.

A positive result would be valuable only if an external assigned response chose between these
accounts. A null would be equally valuable because it would bound the claims that can be made from
interactive simulator plots.

### 3.2 EcoMD does not currently implement `A`

The repository's historical shock interface provides:

- `state_kick`: add a multiple of cross-sectional latent-state standard deviation to a sampled
  subset of agents;
- `price_jump`: inject an exogenous return;
- `news`: move a detached fundamental;
- `temperature_spike`: temporarily rescale effective temperature; and
- `liquidity_drop`: temporarily rescale friction.

None is an intended, signed, executable child-order tape with price, timing, fill and residual-volume
semantics. Mapping QR's TWAP to `state_kick` would choose the cross-model correspondence after seeing
two unrelated response channels. Adding a new EcoMD market-order adapter would be implementation of
a new action, not evidence that the old latent relaxation and QR impact mechanism answer one
question.

Consequently, the MIT engine does not remove `cross_system_estimand_mismatch` or
`common_action_language_missing`. It is an independently maintained baseline only in the weak
software sense.

## 4. Target-calibrated response is not an independent discriminator

### 4.1 The main response is inserted before it is evaluated

Let `T` denote the theoretical target path and `R_m(A_0)` the QR response to the chosen TWAP
`A_0`. The paper selects

\[
  \hat m\in\arg\min_m\|R_m(A_0)-T\|^2
\]

and then demonstrates that `R_m(A_0)` is concave and reverts. This is appropriate component
calibration. It cannot also serve as independent evidence that the feedback mechanism explains or
predicts that same response.

The MLE alternative is less directly target-shaped but does not repair the causal contract.
Anonymous signed trades can arise from hidden parent-order splitting, trend-reactive order flow or
other history-dependent event mechanisms. The existing metaorder-origin audit constructs equal
public laws with different parent interventions. A likelihood optimum on the public law therefore
does not identify the response to `do(parent metaorder)`.

### 4.2 The self-impact ablation is internally valid but externally tautological

The strategy experiment compares including versus excluding the strategy's fills from `phi_t`.
This isolates the effect of the programmed feedback term inside the simulator. It does not establish
the magnitude or even the state dependence of real self-impact. The difference is useful software
behavior, not field validation.

## 5. Why an intervention-basis audit is not an ICLR method here

### 5.1 Finite linear response

For a finite-horizon linear response class, stack calibration inputs in a design matrix `U_c` and
write the response operator as `H`. If `U_c` is rank deficient, any nonzero perturbation `Delta`
satisfying

\[
  \Delta U_c=0
\]

leaves all calibrated responses unchanged and can alter a held-out input. This is the elementary
nullspace witness behind the proposed "orthogonal schedule" test.

If the input is persistently exciting of sufficient order, however, its shifted windows span the
finite behavior and the response can be identified under the model assumptions. A single temporal
profile can therefore contain more than one scalar direction; it would be incorrect to claim that
one TWAP necessarily identifies only one dimension. Rank, persistent excitation and independent
validation already give the right answer.

### 5.2 Unrestricted nonlinear response

For a flexible nonlinear simulator, a finite set of calibration actions has no distribution-free
transport guarantee. One can add a continuous bump term that is zero on every calibrated action
and arbitrary near an unseen action. This is the Cycle 16 off-support twin in action space.
Restricting smoothness, memory length, Lipschitz constants or a Volterra order may yield bounds, but
then the contribution must exceed the mature system-identification result for that restricted
class. No such market-specific theorem is supplied by EcoMD or QR.

### 5.3 Direct method collisions

- The inverse-crime literature already names the error of using the same theoretical ingredients to
  synthesize and invert or validate data.
- Independent calibration/validation and simulator discrepancy are established validation
  requirements, as documented in the prior generic simulator-audit closure.
- Willems et al.'s persistent-excitation result supplies the finite linear behavior-span condition.
- Certified Interventional Fidelity already declares an estimand over an intervention distribution
  and supplies confidence intervals and anytime-valid confidence sequences, including adaptive
  sampling.
- LOB-Bench and the closed prospective-validity route already separate historical conditional
  realism, source-simulator consistency and real unseen-intervention validity.

A calibration-provenance matrix remains good reporting practice. Without a new identification
bound, score, algorithm or qualified external target, it is not an ICLR-level contribution.

## 6. Latency-mode branch also fails

The paper observes an inter-event-time mode near 29 microseconds across four stocks and interprets
it as consistent with an exchange round trip and simultaneous reaction to common signals. This is a
real measurement, but the causal conclusion is underidentified:

- exchange receipt timestamps do not reveal private decision or client send time;
- the public feed reveals winners, not the complete competitor or losing-attempt set;
- events faster than one assumed round trip can include unrelated asynchronous arrivals;
- matching-engine processing, publication and timestamp conventions are not independently varied;
  and
- the paper therefore implements a user-calibrated proxy fill probability rather than an estimated
  structural race model.

Aquilina, Budish and O'Neill already use complete failed-message information to measure latency
races. The existing `winner_loser_race_susceptibility` and
`ballistic_inflight_liquidity_phase_space` routes record the missing denominator, private send-time
and exogenous timing-assignment gates. A public-feed peak does not remove them.

## 7. Trigger decision and exact re-entry condition

The superseding trigger audit is `not_trigger` with zero removed blockers and
`candidate_harvest_authorized: false`.

Re-audit only if all of the following become concrete at once:

1. a versioned, licensed external source observes an assigned parent-metaorder schedule, complete
   pre-state, intended children including nonfills, endogenous limit-flow response and recovery;
2. an independently governed second source repeats the same action grammar, with an entire source
   reserved untouched and independent-family count fixed by an outcome-blind precision analysis;
3. EcoMD and at least one external engine implement deterministic adapters for that exact action and
   clock before outcome access;
4. calibration excludes the confirmation action family and records which response functionals
   informed every simulator component; and
5. the proposed method proves calibrated transport or abstention beyond persistent excitation,
   inverse-crime avoidance, generic model discrepancy, LOB-Bench and current interventional-fidelity
   inference.

Even then, the trigger would authorize only a bounded question screen. A new machine card and
current machine decision would still be required before data access, implementation, simulation,
SSH or GPU use.

## 8. Primary sources and fixed artifacts

1. Noble, Rosenbaum and Souilmi, [*Bridging the Reality Gap in Limit Order Book
   Simulation*](https://arxiv.org/abs/2603.24137).
2. Souilmi, [Queue-Reactive fixed MIT repository
   commit](https://github.com/SaadSouilmi/Queue-Reactive/tree/3080096cc0c79f43f1b82112cbde713710c014f6).
3. Willems, Rapisarda, Markovsky and De Moor, [*A note on persistency of
   excitation*](https://doi.org/10.1016/j.sysconle.2004.09.003).
4. Wirgin, [*The inverse crime*](https://arxiv.org/abs/math-ph/0401050).
5. Asiaee, [*Certified Interventional Fidelity*](https://proceedings.mlr.press/v337/asiaee26d.html).
6. Aquilina, Budish and O'Neill, [*Quantifying the High-Frequency Trading Arms
   Race*](https://doi.org/10.1093/qje/qjab032).
7. Nagy et al., [LOB-Bench](https://proceedings.mlr.press/v267/nagy25a.html).

