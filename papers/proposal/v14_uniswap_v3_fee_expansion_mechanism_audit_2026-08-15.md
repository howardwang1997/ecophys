# V14 Uniswap v3 protocol-fee expansion mechanism audit

**Audited:** 2026-08-15  
**Decision:** `CONDITIONAL_EXACT_M2_DEVELOPMENT_SOURCE`; freeze treatment conformance before LP outcomes  
**Scientific role:** historical development only; Proposal 94 predates the V14 prospective cutoff

## 1. Bottom line

Uniswap v3 is the first free V14 candidate that has a genuinely executable M2 rule and a public, pool-level
treatment clock. It is materially better for exact mechanics than the public AEMO route and materially more
indexable than the failed CoW frame.

It is not yet an M3/M4 dataset. Wallet/position identity, manager coverage, pre-event activity support and a clean
post-response protocol remain untested. The current action is therefore a mechanism-only conformance experiment,
not an LP event study or model run.

The audit also finds a nontrivial systems lesson for the main paper:

> An executable economic mechanism is not identified by proposal prose or bytecode hash alone. It is the tuple of
> runtime code, immutable arguments, relevant storage, authority state and the event-time transactions that
> activate the rule for each unit.

Here that distinction is observable and consequential.

## 2. Primary-source ledger

| Fact | First-party/public evidence | Consequence |
|---|---|---|
| Proposal 94 is on-chain proposal ID 94 | [Uniswap Foundation proposal 94](https://vote.uniswapfoundation.org/proposals/94); execution calldata is `execute(94)` | Historical development event only. |
| Governance execution | Ethereum transaction `0xd6c4...9833`, block 24,596,885, successful receipt | Chain receipt, not front-end status, defines execution. |
| Factory owner actually changed | The factory emitted `OwnerChanged(0x5E74..., 0xf237...)` | The executed adapter is `0xf237...`. |
| Proposal prose names another adapter | Proposal text and the description embedded in Seatbelt commit `c212a947...` list `0x3e40...` | Prose is stale and cannot be used as the mechanism identifier. |
| Seatbelt calldata uses the executed adapter | `sims/94.sim.ts` at `c212a947...` defines `MAINNET_V3_OPEN_FEE_ADAPTER = 0xf237...`; file SHA-256 `5c6a148a...d2d3da` | The same source artifact contains correct calldata and stale explanatory text; decode actions separately from prose. |
| Verified deployed source | Blockscout verifies `V3OpenFeeAdapter`, Solidity 0.8.29, Cancun, source SHA-256 `5d27bfa6...4ff7cf` | The verified source is byte-for-byte equal to the official Git source used in this audit. |
| Exact source version | [Uniswap protocol-fees](https://github.com/Uniswap/protocol-fees), deployment commit `cf7d8a1...`, activation-script commit `62c74e2...` | Pin both deployment configuration and governance action. |
| Per-pool update is permissionless and explicit | `triggerFeeUpdate` resolves pool override -> tier default -> global default, calls pool `setFeeProtocol`, then emits `FeeUpdateTriggered` | Proposal execution alone does not activate a pool. |
| Default fees | Deployer stores packed `0x44` for 0.01%/0.05% and `0x66` for 0.30%/1.00% tiers | Protocol receives one fourth or one sixth of the LP fee, respectively. |
| Initial propagation is batched | Direct calls use selector `0x08f4779e`, `batchTriggerFeeUpdateByPool(address[])`, with 500 addresses per transaction | Each pool has its own treatment event even inside a batch. |

The executed block header timestamp is 2026-03-06 07:19:59 UTC. The Agora page payload reports
2026-03-06 21:54:35 UTC for the same block/transaction. The block header is authoritative. The first observed
batch begins at block 24,599,177, 2,292 blocks and 27,672 seconds after governance execution. Thus the proposal
clock and pool-treatment clock differ by about 7 hours 41 minutes.

## 3. Why the stale address matters scientifically

Both `0x3e40...` and `0xf237...` currently have 7,266-byte runtime code with the same SHA-256
`37bd11b8...f66bef` and Keccak-256 `c70860da...f579c0`. The redeployment did not create a distinguishable runtime
code hash because the source and immutable constructor arguments are the same. The deployment commit instead
adds a global `defaultFee` storage initialization before ownership transfer.

Therefore this identification is invalid:

\[
  M_t = H(\text{runtime bytecode}).
\]

A minimally sufficient on-chain mechanism descriptor is instead

\[
  M_t = (H(B), I, S_t^{\mathrm{relevant}}, A_t, E_{\le t}),
\]

where `B` is runtime bytecode, `I` immutable arguments, `S` relevant storage, `A` the authority graph and `E` the
executed transition/event history. This is not proposed as a new theorem; it is an empirical design constraint
and a useful cross-domain lesson for Economic World Models.

## 4. Exact clocks and replay object

There are at least three clocks:

1. **governance clock:** factory authority changes from the old adapter to `0xf237...`;
2. **configuration clock:** adapter storage determines the fee returned by its waterfall;
3. **pool activation clock:** the pool executes `setFeeProtocol` and emits old/new token-side denominators.

For pool `p`, the frozen treatment time must be its successful `SetFeeProtocol` log, not 6 March as a date and not
the proposal execution block. `FeeUpdateTriggered` supplies caller, pool and packed fee; the adjacent pool event
supplies the exact old and new values. This supports an answer-free mechanical ledger:

\[
 (p,t_p,f^{old}_{0p},f^{old}_{1p},f^{new}_{0p},f^{new}_{1p}).
\]

Given a fixed sequence of swaps and liquidity states, v3 core deterministically diverts the configured share of
swap fees from LP fee growth to protocol fees. That is a valid M2 replay target. It does not identify what swaps
or LP actions would have occurred under the counterfactual rule; those belong to M3/M4.

## 5. Identification opportunities and limits

The first two propagation transactions form a deterministic 1,000-pool conformance prefix. Within that frame:

- pools moving from `(0,0)` to nonzero are newly treated;
- pools whose old and new values are equal are contemporaneous always-treated comparisons;
- the governance-to-first-trigger interval is an exact **mechanical** no-change interval, but not necessarily a
  behavioral no-anticipation interval;
- `0x44` versus `0x66` is a known dose difference but is confounded with fee tier and cannot be treated as random;
- propagation order may reflect the updater's discovery order and is not a population sample.

The event is therefore useful for historical development of a matched or synthetic-control design, not by itself
for a universal causal claim.

## 6. M3/M4 observation boundary

Free on-chain logs can expose submitted and successful state-changing actions. They cannot expose private intent,
dropped private transactions or an LP's economic owner.

For v3 positions, the official NonfungiblePositionManager supplies token IDs, liquidity changes and ERC-721
ownership transfers. This can define an operational position/wallet identity only if a pre-treatment audit closes:

1. position-to-pool mapping is reconstructible without current-state survivor bias;
2. owner-at-action-time is reconstructed from complete transfer history;
3. burned positions and positions minted through alternative managers are counted;
4. manager/vault contracts are reported separately rather than called individual LPs;
5. failed **submitted on-chain** actions are taken from receipts, while private/dropped intentions remain out of
   scope;
6. the fraction of treatment-pool liquidity/actions covered by the chosen identity layer is measured before any
   post-treatment response is opened.

If these clauses fail, Uniswap remains an M2 mechanism source and pool-level event study only. It cannot support
the V14 claim about persistent participants or ecological selection.

## 7. Sequential free experiments

### U0 — treatment conformance (now frozen)

Read only the governance transaction/receipt/block, deployed code and the first two propagation
transaction/receipt/block triples. Require 1,000 exact calldata/event pairs and enough newly activated pools in
both fee groups. Reconnaissance had already accessed their calldata lengths and receipt event-type counts, so U0
is not presented as pristine; old/new fee arguments, activation classes and LP responses were still unopened
when the thresholds were frozen. No LP or market response is read.

### U1 — pre-treatment support and identity coverage

Only after U0 passes, freeze a separate protocol that opens a fixed pre-treatment window. Pool inclusion may use
only immutable metadata and that pre-window. It must report activity, NPM/alternative-manager coverage, position
mapping completeness, owner continuity, contract-wallet share and missingness. It may select a development subset
but cannot open any post-trigger action.

### U2 — post-response development

Only after the U1 pool list and estimator are committed, open one fixed post window. Candidate response variables
are liquidity add/remove, range repositioning, position exit, fee collection and contribution-share change.
Always-treated pools, fake cutoffs, anticipation windows, gas/congestion controls, token shocks and competing-DEX
placebos are mandatory. This remains historical development and cannot replace future prospective confirmation.

### U3 — exact M2 and model ladder

Implement fixed-action fee accounting first. M3/M4 is allowed only if U1 directly measures the participant and
population layers. Learned models must beat persistence, event-study, exact-mechanics-only and frozen-policy
baselines out of time. A GPU campaign is not authorized by U0.

## 8. Data and compute decision

- **Data purchase:** none. Ethereum transactions, receipts, block headers, verified source and event logs are
  public; provider coverage/rate limits still require manifests and retries.
- **U0 compute:** local CPU/network, under one core-hour, zero GPU.
- **U1/U2 likely compute:** CPU-first log indexing and joins; the V100 hosts may run CPU jobs with CUDA hidden if
  local throughput is insufficient.
- **GPU:** 2060 smoke and V100 model jobs remain locked until exact treatment plus identity coverage pass.
- **Expansion:** only after a preperiod volume/row-count benchmark; no H20 assumption.

## 9. Decision

Proceed with U0. If it passes, Uniswap replaces CoW/AEMO as the free exact-M2 **development** source, while the
future on-chain event registry remains the prospective confirmation route. If U1 cannot recover a defensible
identity-covered action panel, narrow the scientific object instead of imputing behavior: retain Uniswap for exact
mechanics and seek another real system for M3/M4.
