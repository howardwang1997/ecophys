# EcoMD Solana bot code--behavior and leader-randomization trigger audit (2026-09-05)

## Durable decision

`not_trigger`; no candidate harvesting, outcome access, implementation, SSH or GPU work is
authorized for this route.

The 2026 ASE paper *Demystifying Solana Bots* and Zenodo package are useful new assets: 586 bot
repositories and a separately collected panel of 200 bot-associated addresses with 44,118,825
transactions. They do not provide paired implementation truth. The paper explicitly says the two
datasets were collected independently and cannot be linked at address level; it also says a bot
rarely corresponds to one on-chain entity. The on-chain sample is drawn from top addresses of named
bot services, not a stable population of deployed repository commits.

## Two exact obstructions

1. **Unpaired coupling.** Observing only `P_R` for repository categories and `P_X` for address
   traces leaves every coupling `pi in Pi(P_R,P_X)` observationally equivalent. Couplings can align
   a code category with either high- or low-response addresses while preserving both released
   marginals. Therefore code-category-to-execution response is unidentified. A cluster `C=g(X)`
   adds no information about `R` after `X` and cannot serve as a deployment label.
2. **Compound leader assignment.** The Solana/Agave schedule uses a seeded stake-weighted draw of
   validator identities, normally for four consecutive slots. It does not randomize client type
   within validator. With `m_i=alpha_{L_i}+beta_i`, arbitrary client-specific shifts in `alpha` can
   be cancelled in validator effects `beta_i` without changing observations. Schedule randomization
   may identify an assigned-validator-population bundle effect, but not the effect of swapping the
   client or scheduler while holding infrastructure, peering, private flow and policy fixed.

The leader schedule is known in advance, so bots can route, tip and bundle in anticipation; outcomes
depend on neighboring schedule exposure, not an independent current-window treatment. Finalized
ledger data also omit unlanded, dropped, replaced and privately forwarded attempts and do not retain
original Jito bundle membership. IMC 2025 reports 97% Jito-compatible adoption among the top 500
validators as of September 2025, eliminating useful Jito-versus-non-Jito support. Jito Validator
History supplies valuable client/stake/version covariates but does not randomize or observe the
remaining operator bundle.

## Novelty collision

Zheng et al. occupy the broad code-taxonomy plus on-chain-fingerprint contribution; Gerzon et al.
occupy large-scale Jito bundle/sandwich measurement; Solana's August 2026 analysis already reports
client-separated non-vote inclusion timing and slow-scheduler leader-window models. Internally the
proposal collides with `global_account_lock_contention_liquidity`,
`adaptive_scheduler_information_filtration_response`, and
`solana_simd0525_slot_clock_leader_window_relaxation`. Generic unpaired matching, randomization
inference and interference analysis do not become a new ICLR method by adding EcoMD.

## Preserved residual and re-entry

The only preserved estimand is explicitly labelled “assigned validator-population bundle effect” on
finalized outcomes under a frozen schedule exposure. It might support a prospective blockchain
measurement study, including a valuable null, but is not an EcoMD truth map or ICLR method now.

Re-enter only with a signed repository-commit/configuration-to-address-set-to-epoch map; randomized
or exogenous within-validator client/scheduler crossover; complete intake including landed, failed,
dropped, replaced, expired, private and bundled attempts; frozen schedule reconstruction,
manipulation, overlap and interference audits; independent same-estimand confirmation; and a method
or theorem beyond standard unpaired coupling and randomization/interference parents. More addresses,
tags, clusters, finalized blocks, client fixed effects or an EcoMD fit are not triggers.

Formal result:
`papers/proposal/ecomd_solana_bot_code_behavior_leader_randomization_trigger_audit_2026-09-05.md`.
