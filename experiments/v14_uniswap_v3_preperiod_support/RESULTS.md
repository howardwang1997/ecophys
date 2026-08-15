# Uniswap v3 U1a preperiod support result

**Protocol commit:** `961266c72bae34fc4a9470dd5f6ed16f95ded6fb`

**Contract SHA-256:** `32bce1fcab85b462aed62f4e7e57536ece2a6120b09f11ac83533107b64b3adb`

**Decision:** `FAIL_PREPERIOD_SUPPORT_OR_IDENTITY_FEASIBILITY_NO_RESPONSE_ACCESS`

## Result

The run completed the exact 16-pool sample and pre-treatment window without transport errors, saturation,
duplicates or conflicting logs. The scientific support gates failed:

| Metric | Frozen gate | Observed | Result |
|---|---:|---:|---|
| Swap-active pools | at least 8 | 3 | fail |
| Position-action-active pools | at least 8 | 1 | fail |
| Position-action logs | at least 64 | 6 | fail |
| NPM manager action-count share | at least 0.50 | 1.00 of 6 | pass, tiny denominator |
| Eligible NPM action transactions | at least 32 | 3 | fail |
| Exact pool-action to token pairing | at least 0.80 | 4/6 = 0.667 | fail |
| Owner resolution conditional on exact pair | at least 0.95 | 4/4 = 1.00 | pass, conditional |

The `0x44` stratum had one swap-active pool, zero position-active pools, three swaps and zero position actions. The
`0x66` stratum had two swap-active pools, one position-active pool, 371 swaps and six position actions. Across the
full sample there were 374 swaps, zero mints, three burns and three collects.

All six position actions used NPM as the pool-level manager owner, but they came from only three transactions and
two transaction senders. Three collect events and one burn paired exactly to NPM token events; two burns had no
matching NPM token event under the frozen closest-preceding pairing rule. The two exact token histories resolved
owners for all four paired actions. No cause is assigned to the two unmatched events because raw responses were
not retained and a diagnostic re-query was not preregistered.

## Window and source integrity

The exact window was blocks 24,548,777--24,599,176. Boundary timestamps were
`2026-02-27T14:10:59Z` and `2026-03-06T15:00:59Z`, a 607,800-second span ending 12 seconds before first treatment.

- successful HTTP responses / attempts: 75 / 75;
- response bytes: 405,836;
- initial pool/event queries: 64;
- saturated queries: zero;
- transaction-log pages: three;
- transfer-history queries: two;
- raw response payloads retained: no;
- duplicate/conflicting normalized logs: zero/zero.

Independent checks reproduced sample size, activity counts, request caps, strictly pre-treatment block bounds and
artifact hashes. Eighteen combined Uniswap tests, Ruff and strict mypy passed after the run.

Artifact SHA-256 values:

- `pool_support.jsonl`: `71450acee06184eaab7e6cc04e26238cba1a6ad1d4820dafb0d099ef1abccb8a`;
- `identity_sample.jsonl`: `e9e7461f74da02bb9d241234f74c19a2dd12288c63d1cf9228d7ad1abd479179`;
- `http_response_hashes.json`: `97ed1a59a72ba2bfa77d0edbb26cccf0780c879b86b7daaae4d93d490ccd2d41`;
- `summary.json`: `3bd36ec8db1b67b9f84077b017559bda7909c705142903d6fa1d9ff66ed366ae`.

## Interpretation

For this small, hash-stratified development sample, contract-level activation is usually not an economically
active participant exposure. U0's exact 1,000-pool mechanism frame therefore cannot be treated as a ready-made
behavioral panel. The result motivates a multi-clock distinction:

1. governance authorization;
2. adapter configuration;
3. pool contract activation;
4. economic exposure through actual trading/position activity;
5. participant response.

Only the first three are validated broadly by U0. U1a shows that clock 3 does not imply clock 4 in a random
stratified sample. The sample is only 16 pools, so it does not estimate inactive prevalence for all 1,000 pools.

## Disposition

Do not add pools, extend the window, lower gates or launch U1b on this frame. No post-treatment response, control
behavior, amount/price field, paid data, remote worker or GPU was used; U2 remains locked.

The scientifically defensible choices are now:

- keep Uniswap as an exact M2 mechanism case and seek a different system for participant-level M3/M4; or
- freeze a new full-population **pre-treatment eligibility census**, explicitly as a route reset rather than a
  sample top-up, before deciding whether enough economically exposed pools exist. That census cannot open any
  post-treatment outcome and must solve the control-source problem separately.
