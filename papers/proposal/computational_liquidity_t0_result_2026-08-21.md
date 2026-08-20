# Computational liquidity T0 result — 2026-08-21

## Formal decision

**RED: stop the route. Do not enlarge the window, switch chains, relax the coupling definition or train a
model to rescue it.**

The formal run used preregistration commit `b2153f39621be2de2c30cd0e4851e75de011ce1b` and clean implementation
commit `3b1ce6f3f286bc2ddc9aa1dca9f75438cc0b8253`. It accessed only Ethereum blocks
`25780000--25780499`. The first binding failure is simple: the fixed interval contained 132 unique settlement
transactions, below the frozen minimum of 200. The result also failed the distinct-competition, low-criticality
and both coupling-support thresholds. This is not a paper result and does not authorize T1.

Canonical result payload SHA-256: `c1e270347528677b73adca1f0acadc09af1d345ea7d0a8d80f7e4eedd6268dcb`.

## Frozen-gate accounting

| Gate | Observed | Frozen requirement | Result |
|---|---:|---:|---|
| unique settlement transactions | 132 | at least 200 | **FAIL** |
| valid transaction-to-competition mappings | 131/132 = 99.24% | at least 98% | PASS |
| distinct competitions | 119 | at least 180 | **FAIL** |
| complete winner reference scores | 119/119 = 100% | at least 90% | PASS |
| queried transaction missing from returned competition | 0 | 0 | PASS |
| raw duplicate-auction payload conflicts | 5 | 0 | **FAIL in frozen implementation** |
| valid winner-removal counterfactuals | 132 | at least 100 | PASS |
| low-criticality removals, `c <= 0.001` | 12 | at least 20 | **FAIL** |
| high-criticality removals, `c >= 0.01` | 97 | at least 20 | PASS |
| submitted-coupled competitions | 12 | at least 30 | **FAIL** |
| eligible-coupled competitions | 2 | at least 10 for GREEN | **FAIL** |

One settlement transaction returned an official 404. All 131 accepted responses contained the queried hash and
all 132 computed winner-removal observations satisfied the exact nonnegative score-loss bounds. The API moved
127,045,560 bytes; the immutable compressed CoW shard is 54,013,690 bytes.

These are support counts only. No regression, correlation, significance test, task-complexity comparison,
phase-transition search or policy optimization was run.

## What the support pattern says—and does not say

The official counterfactual is technically usable: reference-score coverage and arithmetic validity are strong.
The candidate mechanism is not sufficiently supported under the frozen design. Only 12 of 119 distinct
competitions contain the preregistered submitted coupling, and only two retain it after the platform's filtering
step. The sample also contains many materially critical winners, but reporting 97 high-criticality removals does
not establish that coupling predicts criticality. That association was expressly forbidden before T0 passed.

The fixed-window sample-size miss is partly an experimental-design lesson. A recent exploratory block range had
suggested a higher settlement rate, but activity was not stable enough to justify a 500-block formal window. The
honest response is not to widen this test after observing 132. Future projects must use outcome-blind development
data to estimate event rates and freeze sample size before opening mechanism variables.

## Post-run software audit of the duplicate gate

The frozen result reports five conflicting auction IDs. A post-result diagnostic found that the payloads differ
only in the order of the top-level `transactionHashes` array. For every duplicate auction, sorting that array
reduces the number of distinct payloads to one; scores, solutions, references and transaction membership agree.
Thus the frozen implementation used an order-sensitive byte hash where the gate intended semantic equality.

This is a real validator defect, so future code now computes a semantic competition hash and has a regression
test for reversed transaction/solution arrays. It does **not** retroactively alter the formal artifact: the
post-result correction was not preregistered, and RED remains binding even if the five false conflicts are
removed because four independent support gates still fail.

## Data provenance and integrity

- Result: `results/agent_markets/cow_computational_liquidity_t0_v1.json`.
- Tracked provenance manifest: `data/manifests/cow_computational_liquidity_t0_v1.json`, canonical payload
  SHA-256 `d70294c78ed9b36dafb05ff60ab9d611596568ef40419c0cc3cb3750be16bf84`.
- Local immutable Blockscout shard: SHA-256
  `475fbe93cf0ba7b7a8821b8a2c963669ea40a815079342828504e060856aae14`.
- Local immutable CoW competition shard: SHA-256
  `4c6ac93b51efbef109e9bbec46d4a4534fa780e2b92ef8add3d9e247d0a267dd`.
- Scientific config SHA-256:
  `c323ee38d47e1fcfae564356cf6afd996ca888fab1271227f5e2f8290e5564d2`.
- Runtime config SHA-256:
  `5acdd658ae984adbd0119e452ed8369cbc7bfad54bdf856ef17d771f70015a12`.
- Canonical bulk copies:
  `r2://ecophys/raw/cow_computational_liquidity_t0_v1/{blockscout_settlement_events.json.gz,cow_competitions.jsonl.gz}`;
  verified object sizes are 9,657 and 54,013,690 bytes. The tracked upload receipt is
  `data/manifests/cow_computational_liquidity_t0_v1_r2_receipt.json`.

Blockscout is a public indexer and the CoW response is a public API, but neither public data surface states a
dataset licence clearly enough for redistribution. Raw shards remain outside git; the manifest retains source,
download time, hashes, preprocessing commit and licence status.

## Compute and claim boundary

The run used Mac CPU and public network transport. It used no V100, RTX 2060, H20, EcoMD, paid data or model
training. The current GPU pool remains idle by design.

This branch contributes reusable typed ingestion, official-counterfactual validation and a precise negative
result. It does not support a CoW paper, an NMI submission or an NCS method claim. ERCOT RTC+B is not promoted
automatically: its two bundled production switches remain too few for the desired causal story. The next problem
selection must require dense repeated units or real randomization, an outcome-blind support-calibration tier and
a second-system transfer path before another formal holdout is consumed.
