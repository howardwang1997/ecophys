# Aave V3 B0 target-row-free transport repair canary v2

**Status:** frozen before every post-v1 RPC request. A PASS authorizes only a separately committed B0 v2 protocol
design. It does not authorize target-log collection, a B0 scientific execution, B1, accounts, outcomes, G1 or GPU
work.

## Immutable evidence and repair scope

Transport canary v1 at protocol commit `4f18e818...`, archived at `fc9f9bff...`, failed with zero validation errors.
RTX 2060 and Mac independently covered the same six of nine deployments; each V100 covered five and also lacked
Optimism. The only probes in this repair are the three missing routes that could raise a six-deployment host to
nine: Polygon, Base and BNB. Repeating a V100 cannot reach nine from these three probes and is excluded by this
target-free v1 coverage fact, not by a target result.

The manifest pins the v1 protocol, source, manifest, result, summary, RTX artifact and Mac artifact by SHA-256. Its
validator replays both eligible host ledgers with the immutable v1 verifier and confirms every inherited route.
The official-source audit is also hash-pinned. No v1 endpoint or host may be reinterpreted after v2 observation.

## Six inherited routes

| Deployment | Role | Endpoint | Conservative initial span |
|---|---|---|---:|
| Arbitrum | replica | `https://arb1.arbitrum.io/rpc` | 250,000 |
| Avalanche | primary | `https://avalanche-c-chain-rpc.publicnode.com` | 31,250 |
| Optimism | replica | `https://mainnet.optimism.io` | 7,813 |
| Gnosis | primary | `https://gnosis-rpc.publicnode.com` | 7,813 |
| Linea | primary | `https://linea-rpc.publicnode.com` | 31,250 |
| Scroll | primary | `https://scroll-rpc.publicnode.com` | 31,250 |

These routes are inherited separately for the selected v2 host. No new RPC request is made to them.

## Three repair probes

The fixed order and only candidates are:

1. Polygon replica `https://polygon.drpc.org`, whose v1 single-block request passed before HTTP 400 on the root
   range.
2. Base replica `https://mainnet.base.org`, whose v1 single-block request passed before HTTP 413 on the root range.
3. BNB `https://bsc.drpc.org`, selected before requests because BNB Chain lists dRPC as a provider and dRPC
   documents BSC `eth_getLogs`. This documentary evidence does not imply genesis retention; the canary tests it.

No candidate may be substituted after any response is observed.

## Target-free query and error-classification contract

The only methods are `eth_chainId` and `eth_getLogs`. Every log filter uses the zero address and retains no raw
response body or event row. Each candidate must return the expected chain ID, an empty list for `[0,0]`, and an
empty genesis-prefix range beginning at `[0,249999]`.

After the single-block empty result passes, a JSON-RPC error or persistent HTTP 400/413 across both attempts may
trigger deterministic left-prefix bisection. Every other outcome is terminal, including HTTP 401/403, 429, 5xx,
transport failure, invalid JSON/envelope, unexpected result type or a nonempty list. HTTP 400/413 at the
single-block stage is terminal. Unexpected rows are discarded immediately; only their count and response hash can
remain.

## Host selection and resource bounds

Both `rtx2060` and `local_mac` must report with CUDA hidden. A host passes only if all three repairs pass on that
same host. After both valid artifacts exist, the first passing host in the fixed order RTX 2060 then Mac is
selected. A cross-host mosaic, early selection, extra retry, replacement endpoint and post-observation rule change
are forbidden.

Per host: at most 100 HTTP attempts, 8 MiB of response bytes, two requests per second, two attempts per logical
call and a 30-second timeout. Expected wall time is under five minutes in parallel, durable output under 1 MiB,
paid data zero and GPU-hours zero. The 100-attempt cap is fail-closed if an endpoint behaves pathologically.

## Decision

`PASS_TARGET_ROW_FREE_TRANSPORT_REPAIR_AUTHORIZE_B0_V2_PROTOCOL_DESIGN_ONLY` requires two valid host artifacts and
one host covering all three repairs; the aggregate then combines its repairs with that host's six validated v1
routes. Otherwise the decision is `FAIL_TARGET_ROW_FREE_TRANSPORT_REPAIR_KEEP_B0_V2_B1_G1_GPU_LOCKED`.

Neither outcome estimates Aave program support. A failure closes the current free-RPC route until a genuinely new
archive-resource decision is made; removing BNB or weakening the B0 scientific support gates is not a repair.
