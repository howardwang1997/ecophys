# Compound III source-metadata preflight v2 result

**Protocol commit:** `0245e6ebcd11e263e13bdeb98ff2d66cb1498b6c`

**Official source commit:** `f766f51583c23acc33b2a7824654ef2029a96804`

**Decision:** `PASS_SOURCE_METADATA_AUTHORIZE_CHAIN_METADATA_ONLY`

**Artifact SHA-256:** `643edb6750ab5567528a9754bdf92b84143deaa82a9225a9c8ea9730e0d81e11`

## 1. Execution

V2 ran once from a clean detached EcoPhys worktree after its invocation-only repair was committed and pushed. The
external official Comet checkout matched the frozen remote and commit and had empty Git status. The collector made
no network or chain request.

The run passed all nine conjunctive gates and wrote one 11,318-byte JSON artifact. Sixteen retained file records
were independently checked with `shasum -a 256 -c`; every hash matched the pinned source checkout. Nine focused
tests also pass. V1 remains the separately recorded pre-source import-path failure.

## 2. Gate ledger

| Gate | Result | Evidence |
|---|---|---|
| source commit/remote | pass | exact official remote and frozen 40-character commit |
| clean source | pass | no source worktree modification |
| market files | pass | all six configuration/root pairs and migration directories exist |
| market schema | pass | 6/6 carry required identity, authority, rate, collateral and valid-address structure |
| unique Comet roots | pass | six markets have six distinct Comet proxy addresses |
| action surface | pass | all nine frozen base/collateral/liquidation action markers found |
| configuration surface | pass | all five frozen deployment/rate/collateral setter markers found |
| state surface | pass | account principal, collateral and manager-allowance markers found |
| licence provenance | pass | all three exact frozen licence markers found |

## 3. Source inventory

| Market | Base | Collateral configurations | Migration filenames | Comet root unique |
|---|---:|---:|---:|---:|
| mainnet USDC | USDC | 5 | 17 | yes |
| mainnet USDS | USDS | 5 | 4 | yes |
| mainnet USDT | USDT | 6 | 9 | yes |
| mainnet WBTC | WBTC | 2 | 2 | yes |
| mainnet WETH | WETH | 2 | 18 | yes |
| mainnet wstETH | wstETH | 2 | 6 | yes |
| **Total** | — | **22** | **56** | **6/6** |

All six roots name the same Configurator address. That is useful for a common executable parameter surface but is
also a control-design warning: a governance payload may update multiple markets through shared authority. A
parallel Comet market is not automatically untreated.

The 56 migration filenames show that the pinned source tree contains multiple historical configuration-change
families. They are not proof that any transaction executed, and their counts are not intervention sample sizes.

## 4. Scientific disposition

The result establishes that Compound is worth the next bounded metadata gate. It does **not** pass G1. In
particular, it does not establish:

- which source configuration corresponds to current deployed bytecode and storage;
- an archive-complete account population at any pre-event block;
- the minimum nonzero state that counts as economic exposure;
- participant support, concentration, overlap or control validity;
- reverted/private intent or beneficial-person identity;
- an eligible prospective governance intervention or response vector; or
- chain-data retention/redistribution rights.

The only newly authorized step is a separately frozen chain-*metadata* audit of deployment roots, implementation
code, authority/configuration state, local execution clocks, archive capability and licence/retention provenance.
It may not query account mappings, user action events, liquidations, prices or realized responses.

## 5. Resource use

The scientific collector completed in about one second on local CPU. It read 16 small source files and wrote one
11.3 KiB artifact. Network/RPC, paid data, remote workers and GPU-hours were all zero. The two V100s and RTX 2060
remain idle; more compute cannot replace the next identification and provenance gates.
