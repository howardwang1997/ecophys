# Uniswap v3 treatment conformance v2 result

**Protocol commit:** `2ad540a99131595cb131d425dc8885f5eff3ba5f`

**Contract SHA-256:** `d98b5201a8e377118428da401bcea3fad20248c2bc902dce9652b23fb99f2e87`

**Decision:** `PASS_EXACT_TREATMENT_FRAME_FREEZE_PREPERIOD_DESIGN`

## Result

All frozen integrity and feasibility gates passed:

- two ordered batches of exactly 500 calldata pools each;
- 1,000 unique pools across the frame;
- exactly one ordered pool `SetFeeProtocol` event and one adapter `FeeUpdateTriggered` event per calldata pool;
- exact transaction/receipt/block-hash consistency and successful receipts;
- 1,000 transitions from old fee `(0,0)` to a permitted symmetric nonzero fee;
- 107 activations to `(4,4)` / packed `0x44` and 893 to `(6,6)` / packed `0x66`;
- exact factory owner transition from `0x5e74...` to executed adapter `0xf237...`;
- frozen 7,266-byte runtime-code SHA-256 matched at the v2 provenance block tag `latest`.

The first batch contained 54 `0x44` and 446 `0x66` activations. The second contained 53 and 447. Every row had
the same frozen direct caller. Both activation-class minimums passed by wide margins without threshold repair.

## Clock

Governance executed at block 24,596,885 (`2026-03-06T07:19:59Z`). The two pool batches executed at blocks
24,599,177 and 24,599,179 (`15:01:11Z` and `15:01:35Z`). The first pool activation was therefore 2,292 blocks
and 27,672 seconds after governance. Pool `SetFeeProtocol`, not proposal execution, is the treatment clock.

## Important limitation

There is no within-frame always-treated comparison: all 1,000 rows are newly activated from `(0,0)`. The
reapplied-fee comparison anticipated in the mechanism audit is absent. U1 must not manufacture a control group
from these batches or select one using post-treatment outcomes. Any candidate control pool construction must be
specified from treatment status, immutable metadata and a frozen pre-treatment window only, with overlap and
positivity reported before response access.

## Independent verification

The detached run and copied artifacts were checked independently:

- successful RPC records: 11 in the exact frozen method order;
- attempts: one per call, with no prior transport/RPC error;
- raw RPC envelopes retained: no;
- treatment-ledger rows: 1,000;
- unique pools: 1,000;
- focused tests: 9 passed;
- Ruff and strict mypy: passed.

Artifact SHA-256 values:

- `treatment_ledger.jsonl`: `8d3c4c1137f2ad6abfe1c0fc8326bd3845d269275c8fc6b00eac857ac1a6ae08`;
- `rpc_response_hashes.json`: `a208256031ddc3ecfffca8397b785423f13ce3282466786436be3da69fe6d825`;
- `treatment_summary.json`: `75cecc8c9d403f2eeed2aef3879868fb2336c88e04f6719e96d22d066bb2f497`;
- canonical treatment-row content: `affd87b36b8331c5b2530f2f26ab5fc0c882db9a2e84045bd27eb5f5eef7d3cc`.

## Access and disposition

No LP action, swap, liquidity outcome, price, volume or post-treatment response was accessed. Paid data, remote
workers and GPU-hours were zero. The result validates a public exact-M2 treatment ledger for this deterministic,
non-representative 1,000-pool development prefix. It does not establish LP adaptation, causal effects,
representativeness or a publication-level result.

U0 unlocks only a separately frozen U1 pre-treatment support/identity/control-design audit. U2 response access and
all model/GPU work remain locked.
