# V14 Uniswap v3 U1a preperiod support freeze

**Frozen:** 2026-08-15

**Decision:** run a small outcome-blind treated-pool support/identity audit; do not open responses or controls

## Why this gate is necessary

U0 solved exact M2 timing but revealed that every pool in its 1,000-pool prefix was newly activated. The proposed
same-fee contemporaneous control is absent. It would be invalid to proceed directly to a post-event regression or
to choose controls based on realized liquidity/volume trajectories.

Before control design, the project also needs to know what “participant” is observable. Pool events expose a
position-manager owner; NPM events expose a token ID; ERC-721 transfers expose an NFT owner; the transaction
exposes a sender. These are distinct layers and none is automatically the economic beneficiary.

## U1a design

U1a takes eight pools from each fee class using only a salted hash of U0 pool addresses. It reads four event types
in the 50,400 blocks immediately before the first treatment block. Event amounts/prices are deliberately not
decoded. The identity sub-study hash-samples at most 64 NPM-managed action transactions, pairs pool and NPM events
by log order and reconstructs token transfer history only through each action block.

This measures:

- how many sampled pools have preperiod swaps and position actions;
- manager-layer concentration by action count;
- whether pool actions can be mapped to NPM token IDs without current-state survivor bias;
- whether token ownership can be resolved at the action transaction;
- the remaining gap between transaction sender, NFT owner, manager and beneficiary.

## Data-source discipline

PublicNode served U0 transactions/receipts but rejected historical state. U1a therefore uses Blockscout's official
free logs APIs for logs and PublicNode only for block headers and selected transaction envelopes. The documented
1,000-log cap is handled by deterministic interval bisection. A 128 MiB/2,000-attempt/250,000-event ceiling stops
unbounded acquisition.

Transport preflights used only U0 mechanism data already consumed; no sample-pool preperiod event was opened.
The frozen address-log preflight returned 500 events, the governance transaction-log preflight returned 28, and
an impossible adapter topic confirmed the empty-result response schema.

## Interpretation

A pass says only that free preperiod support and an NPM identity layer are feasible on this small stratified
treated sample. It does not solve control selection, alternative-manager beneficiaries, private intent,
representativeness or causal response. U1b must expand coverage; a separate protocol must identify controls from
treatment status, immutable metadata and preperiod data alone. Post-treatment access remains prohibited.

Required compute is local CPU/network. GPUs and paid data remain unnecessary and unauthorized.

## Result

U1a failed the support/identity gate despite complete transport and exact scope. Only 3/16 pools had swaps and
1/16 had position actions; six position actions supplied three NPM transactions. Pairing was 4/6 and conditional
owner resolution 4/4. This blocks the planned U1b and confirms that contract activation must be separated from
economic exposure in the model. Full result:
`experiments/v14_uniswap_v3_preperiod_support/RESULTS.md`.
