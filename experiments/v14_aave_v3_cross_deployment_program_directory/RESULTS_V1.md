# Aave V3 cross-deployment program directory v1 result

**Decision:** `INFRASTRUCTURE_FAILURE_NO_B0_SCIENTIFIC_DECISION`

## Sealed execution

- Protocol and collection commit: `7079562919b039f69927a916ccc08281e1d2462b`.
- Manifest SHA-256: `1136d03e39fdc4e518f6f77b71a8929e579b31ca2979c50caadf874e7f9dedb1`.
- Execution began from a clean detached worktree after 34/34 Aave tests, format, Ruff, strict mypy,
  manifest/parent validation and all ten frozen Aave source-object checks passed.
- `failure.json` SHA-256:
  `714c3ed29acd92df19fab1b1eedadc52c46f61db321f13756284b0b35ceeffdf`.
- `rpc_response_hashes.json` SHA-256:
  `0784cb7bf2383f4b4df20d6754265cea3e3dd5eb022ab7ae654360b9d2c987d8`.
- `summary.json` and `program_directory.json` do not exist, as required for this exception path.

## What happened

Arbitrum completed 66 successful requests: two `eth_chainId`, two `eth_blockNumber` and 62
`eth_getBlockByNumber` calls. These resolved the cutoff independently on the two frozen endpoints. The first
Provider `eth_getLogs` request to `https://arbitrum-one-rpc.publicnode.com` returned HTTP 403 on all three allowed
attempts. The frozen multiblock-error rule recursively bisected the interval; every attempted child, including
block 0 alone, returned the same 403.

The collector therefore terminated fail-closed with 14 failed logical `eth_getLogs` calls, three HTTP attempts per
logical failure. The complete run used 108 HTTP attempts and received 129,956 response bytes. Cross-field checks
reproduce `66 + 14 * 3 = 108`; all successful and failed methods are within the four-method allowlist, and no
successful event-log response exists.

## Interpretation and locks

This is a transport/capability failure, not evidence that cross-deployment Aave programs are absent or
insufficient. No B0 scientific gate was evaluated, no program count or topic support was observed, and v1 must not
be retried or repaired in place. B1 compiler design/execution, transaction/receipt/calldata/trace/state, accounts,
realized responses, G1 and every GPU job remain locked.

Only chain IDs and block headers were successfully normalized. No Provider or Configurator log row, transaction
object, receipt, calldata, trace, historical state, bytecode, participant action, liquidation, price/oracle value or
response row was retained. Paid data, external workers and GPU use were zero.

## Versioned repair boundary

A successor may perform a separately frozen, target-row-free transport canary and then change only the execution
transport or error classification. It must preserve the ten-deployment universe, deployment-held-out split,
2026-08-15 cutoff, program inclusion rule, support thresholds, hard caps and downstream access locks. Endpoint or
worker selection must be determined from empty-address transport canaries rather than target program counts.
