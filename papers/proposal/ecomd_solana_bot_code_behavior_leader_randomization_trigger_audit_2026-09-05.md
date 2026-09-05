# EcoMD Solana bot code--behavior and leader-randomization trigger audit

**Date:** 2026-09-05  
**Archetype:** `empirical_intervention`  
**Decision:** `not_trigger`  
**Candidate harvesting:** not authorized  
**Outcome-row access, implementation, EcoMD execution, SSH, and GPU work:** not authorized

## 1. Executive decision

The July 2026 ASE paper *Demystifying Solana Bots* and its open Zenodo package are a genuine new
measurement asset. They contain 586 public bot repositories and a separately collected panel of 200
bot-associated addresses with 44,118,825 transactions. Solana also supplies an unusually explicit
assignment mechanism: eligible vote accounts are selected by a stake-weighted pseudorandom leader
schedule, normally in four-slot windows. Jito's Validator History records client type, software
version, stake, commission and performance metadata. At first sight, those ingredients suggest a
strong experiment: map bot implementation types to on-chain response under randomly assigned
validator clients, then use the response as an EcoMD population or mechanism target.

The proposal fails two independent identification tests.

First, the authors explicitly state that the repository and address datasets were collected
independently and cannot be linked at address level. The release therefore supplies two marginals,
not paired code and behavior. Every coupling between repository categories and address traces has
the same observed likelihood; couplings can reverse any claimed category-to-execution association.
Clustering the traces does not repair this because the cluster is a deterministic function of the
same trace.

Second, the leader schedule assigns a validator identity, not a client implementation independently
of that validator's network, peering, geography, private order flow, relays, hardware and operator
policy. Randomization can identify a reduced-form effect of exposure to the assigned validator
bundle, subject to a schedule-wide interference contract. It cannot isolate the client or scheduler
mechanism when each validator runs only its observed stack. The official August 2026 Solana analysis
already reports client-separated inclusion timing and models persistent slow-scheduler leader
windows, while explicitly noting that routing, topology, client behavior and leader infrastructure
are not separated.

Finalized-chain data also omit the intake denominator: unlanded submissions, replacements, private
forwarding and original Jito bundle membership. IMC 2025 documents both that bundle membership is
absent from the final ledger and that 97% of the top 500 validators already ran a Jito-compatible
client in September 2025. Thus neither lifecycle closure nor useful Jito-versus-non-Jito overlap is
established.

The exact decision is `not_trigger`. The only scientifically defensible survivor is a narrowly
defined assigned-validator-bundle response, which could support a blockchain measurement study
after a prospective exposure audit. It neither identifies code-to-behavior mechanisms nor supplies
an irreducible ICLR method or an EcoMD truth target. No GPU experiment is justified.

## 2. Question, rivals, and cheapest discriminator

**Market-native object.** For leader window `w`, let `I_w` be the assigned vote account, `L_i` its
declared client type, `U_i` all other operator and infrastructure state, and `Y_w` a frozen DEX
response for a predeclared address or pool panel. Let `R` denote repository functionality and `X`
denote on-chain address traces.

- **H1 -- mechanism-level natural experiment:** paired code and address labels reveal bot strategy,
  while protocol leader randomization makes `L_{I_w}` an assigned treatment whose effect on `Y_w`
  identifies scheduler-dependent market dynamics.
- **H0 -- unpaired marginals plus compound assignment:** `R` and `X` are not linked; the schedule
  randomizes `I_w`, hence the compound bundle `(L_i,U_i)`, while bots can anticipate the published
  schedule. Code mapping and client mechanism remain unidentified even if a reduced-form validator
  exposure is estimable.

**Cheapest discriminator.** Before opening a transaction row, require both (i) a signed
commit-to-deployment-address-to-epoch map and (ii) client or scheduler variation within the same
validator under randomized or otherwise identified assignment. The first source says (i) is absent;
the protocol and metadata sources do not supply (ii). H1 therefore fails at the schema and assignment
level.

A positive answer would provide unusually strong mechanism labels and protocol-randomized response
truth. The null answer is still useful: it preserves the compound assigned-validator estimand and
prevents protocol pseudorandomness from being misreported as client-level causality.

## 3. Source and release contract

The ASE paper contributes two complementary datasets:

1. 586 GitHub repositories, categorized into 15 functions within five domains using source parsing,
   LLM-assisted tags and human validation; and
2. 200 leaderboard-derived addresses from Trojan and SolanaMevBot over 1 October--1 November 2025,
   with a later SolanaMevBot/Axiom validation window over 1 February--1 March 2026.

The paper reports transaction intensity, execution status, fees, invoked programs, assets and
trace-derived clusters. It also states that a bot rarely corresponds to one on-chain entity and
that the two datasets cannot be linked at address level. Behavioral correspondence is assigned by
manually relating representative trace motifs to broad code categories. The on-chain panel is
therefore service-selected rather than a population of stable bot implementations.

Zenodo record `10.5281/zenodo.21359451` is open, version `v2`, published 14 July 2026, and contains
one 40.9 MB archive with MD5 `b4c4acb3f1f8b7fec0954593c425d52e`. Only record metadata and the
archive preview were inspected. No CSV or transaction row was opened. The preview is sufficient to
confirm that the package does not advertise a repository-to-address deployment map; the primary
paper supplies the decisive negative statement.

## 4. Lemma 1: unpaired code--behavior coupling is not identified

Suppose the release gives independent samples from repository marginal `P_R` and trace marginal
`P_X`, but no paired observation. The admissible joint laws are

\[
\Pi(P_R,P_X)=\{\pi:\pi_R=P_R,\;\pi_X=P_X\}.
\]

Every `pi` in this set induces exactly the same distribution for the released data. When both a
code category and a behavioral response are non-degenerate, one admissible coupling can align the
category with high response and another can align it with low response while preserving both
marginals. Hence the sign and magnitude of

\[
E_\pi[h(X)\mid R=r]-E_\pi[h(X)\mid R=r']
\]

are not identified. Unequal sample sizes, service selection and multi-address bots enlarge rather
than shrink the equivalence class.

If `C=g(X)` is an HDBSCAN cluster or a hand-labelled trace motif, then `C` adds no information once
`X` is observed: `I(R;C|X)=0`. A generative matcher can choose a coupling, but without anchors it
cannot validate that coupling as deployment truth. This is the same observation-quotient and
selective-identity boundary already recorded in the repository, now with an unusually explicit
primary-source admission.

## 5. Lemma 2: leader randomization does not randomize client mechanism

Agave's leader-schedule implementation draws identities using a seeded `ChaChaRng` and a
stake-weighted categorical distribution. SIMD-0180 requires continued generation at epoch
boundaries with the stake-weighted randomized algorithm. Conditional on the eligible vote accounts,
stake weights and a valid assignment mechanism, repeated windows can therefore identify responses
to assigned validator identities.

But let a validator-level mean satisfy the unconstrained decomposition

\[
m_i=\alpha_{L_i}+\beta_i,
\]

where `alpha` is a client component and `beta_i` is the remaining operator bundle. Each validator is
observed with one fixed client stack. For arbitrary constants `c_l`, replacing

\[
\alpha_l\leftarrow\alpha_l+c_l,\qquad
\beta_i\leftarrow\beta_i-c_{L_i}
\]

leaves every `m_i` and every randomized-schedule observation unchanged. Thus protocol assignment
does not identify `alpha`. A comparison between windows assigned to client classes estimates the
effect of drawing a validator from those client-specific operator populations, not the effect of
changing the client while holding the operator fixed.

This distinction is substantive. Jito Validator History can make `L_i`, stake, versions,
commission and performance observable, but it does not observe or randomize routing, peering,
data-center topology, private relays, searcher relationships, hardware and scheduler configuration.
The official Solana analysis names these as unresolved causes of timing differences.

## 6. Anticipation, interference, and lifecycle

Even the compound validator effect needs a stronger design than a slot-level regression.

- The leader schedule is produced before the relevant windows, and Solana forwards transactions
  toward upcoming leaders. Searchers can condition routing, tips and bundles on the full future
  schedule. The potential outcome is therefore `Y_w(S_{w-k:w+k})`, not merely `Y_w(I_w)`.
- Four consecutive slots share one leader. Handoffs, previous state, skipped slots and subsequent
  arbitrage transmit treatment across neighboring windows. A valid analysis needs a frozen exposure
  mapping or a sharp schedule-level null, not independent-window standard errors.
- The official source establishes pseudorandom generation, but causal use still requires a frozen
  seed/eligibility reconstruction and an audit that stake, eligibility or seed-relevant state could
  not be selected using impending market conditions.
- Finalized records contain landed successful and landed failed transactions, but not all submitted,
  dropped, expired, replaced, privately forwarded or never-landed attempts. Jito bundle IDs and
  original bundle membership are not preserved on the final ledger.

Consequently, a landed-flow response can be defined, but it cannot be interpreted as a submission,
selection or scheduler mechanism without an authorized intake ledger.

## 7. Collision and contribution audit

The broad proposal is already occupied from both sides:

- Zheng et al. own the current large-scale Solana bot taxonomy and on-chain fingerprint study.
- Gerzon et al. own large-scale Jito bundle and sandwich measurement and document the missing public
  bundle history and dominant Jito adoption.
- Solana's August 2026 analysis already separates non-vote inclusion timing by validator client,
  models runs of slow-scheduler leader windows, and studies four-slot leader handoffs.
- The repository's `global_account_lock_contention_liquidity` route already closes mechanisms based
  on finalized successes without losing/private submission exposure.
- `adaptive_scheduler_information_filtration_response` closes cross-scheduler comparisons when
  policies observe different histories, and `solana_simd0525_slot_clock_leader_window_relaxation`
  closes the bundled slot-clock/leader-window intervention.

Randomization inference with interference, fixed-attribute subgroup contrasts, unpaired
multi-view matching and deterministic clustering are established statistical objects. This audit
found no market-specific theorem, estimator or lower bound that is false for those parents. Adding
EcoMD would introduce a simulator without repairing either missing pairing or client attribution.

## 8. Gate matrix

| Gate | Evidence | Decision |
|---|---|---|
| Versioned open code taxonomy | ASE paper and Zenodo package | Pass |
| Versioned on-chain address panel | Paper/package, service-selected | Partial |
| Code commit to deployed address and epoch | Explicitly absent | Fail |
| Stable one-bot/one-address unit | Paper says bots manifest through account sets | Fail |
| Known leader assignment probabilities | Stake-weighted protocol algorithm | Partial; reconstruction audit needed |
| Randomized client/scheduler within operator | Identity, not client, is assigned | Fail |
| Treatment overlap | 97% Jito-compatible among top 500 in Sep. 2025 | Fail for Jito contrast |
| Complete submission and bundle lifecycle | Final ledger omits unlanded/private intake and bundle IDs | Fail |
| Interference/anticipation contract | Full schedule is known and behavior can adapt | Fail |
| Unoccupied ICLR method residual | Direct measurement and standard-method parents | Fail |
| EcoMD observation/action map | No paired strategy or intake truth | Fail |

## 9. What remains scientifically usable

A future study could predeclare the following reduced-form estimand without claiming client
mechanism:

\[
\tau_{A,B}=E[Y_w\mid I_w\sim q_A]-E[Y_w\mid I_w\sim q_B],
\]

where `q_A` and `q_B` are explicitly defined stake-weighted populations of validators, the complete
schedule exposure is frozen, and `Y` is restricted to finalized public-state outcomes. Its label
must be “assigned validator-population bundle effect.” It may be valuable for a measurement venue,
including under a null result, but it is neither a code-to-behavior map nor a causal client effect.
At present it also lacks the new learning contribution required for ICLR.

## 10. Exact re-entry conditions

Re-audit only after all of the following exist before outcome access:

1. a licensed, signed map from exact repository commit and configuration to deployment address set
   and active epoch, with split/merge and key-rotation semantics;
2. randomized or defensibly exogenous within-validator client/scheduler crossover, or another legal
   intervention that changes the implementation while holding operator infrastructure and intake
   fixed;
3. complete, timestamped public or authorized intake state covering landed, failed, dropped,
   replaced, expired, private and bundled attempts, with bundle membership and routing exposure;
4. a frozen leader-schedule assignment reconstruction, overlap and manipulation audit, and a
   schedule-wide anticipation/interference exposure model;
5. an independently governed same-estimand confirmation system; and
6. a theorem or learning method with a stated result beyond generic unpaired coupling, randomization
   inference, interference analysis and deterministic feature clustering.

A larger address panel, more repository tags, another behavior cluster, current leader-history API,
more finalized blocks, an EcoMD fit or a regression with client fixed effects is not a trigger.

## 11. Primary sources

1. Zheng et al., *Demystifying Solana Bots: From GitHub Blueprints to On-Chain Fingerprints*, ASE
   2026, https://arxiv.org/html/2607.28424v2
2. Zheng et al., replication package v2, https://doi.org/10.5281/zenodo.21359451
3. Anza, Agave leader-schedule source at commit
   `cdbe7e760aef06d13c23c12f046e402de4b638f5`,
   https://github.com/anza-xyz/agave/blob/cdbe7e760aef06d13c23c12f046e402de4b638f5/ledger/src/leader_schedule.rs
4. Solana Foundation, SIMD-0180 at commit
   `4828b2dd994c98032af401acfa20d37688878003`,
   https://github.com/solana-foundation/solana-improvement-documents/blob/4828b2dd994c98032af401acfa20d37688878003/proposals/0180-vote-account-leader-schedule.md
5. Jito Foundation, Validator History Program at commit
   `0bd6a39d1edfd906ddcc33ac2cbdc09d7eaa9595`,
   https://github.com/jito-foundation/jito-omnidocs/blob/0bd6a39d1edfd906ddcc33ac2cbdc09d7eaa9595/stakenet/validator-history/program-overview/index.md
6. Natale, *Lowering Slot Time and Validator Economics*, 19 August 2026,
   https://solana.com/news/lowering-slot-time-and-validators-economic
7. Gerzon et al., *Quantifying the Threat of Sandwiching MEV on Jito*, IMC 2025,
   https://doi.org/10.1145/3730567.3764493

## 12. Compute decision

This audit is `not_trigger`; `candidate_harvest_authorized=false`. Do not download or open the
transaction CSVs, query validator histories or address outcomes, scrape future leader-window
responses, implement a parser or estimator, modify EcoMD, SSH to a worker, or schedule an A800/V100
job under this route. The separately authorized constraint-attribution machine decision is not
authority for this candidate.
