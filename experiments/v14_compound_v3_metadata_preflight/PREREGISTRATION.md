# Compound III zero-row source-metadata preflight

**Frozen date:** 2026-08-16

**Decision authority:** the first pushed commit containing this protocol and
`data/manifests/compound_v3_metadata_preflight_v1.yaml`.

## Question

Does one exact official Comet source commit expose a complete and internally consistent minimum surface for six
Ethereum-mainnet markets, account actions/state, parameter changes and licence provenance, before any chain or
participant row is opened?

This is a source-conformance test. It does not establish deployed state, participant support, causal controls,
sample size, event eligibility or licence interpretation.

## Frozen source

- repository: `https://github.com/compound-finance/comet.git`;
- commit: `f766f51583c23acc33b2a7824654ef2029a96804`;
- markets: mainnet USDC, USDS, USDT, WBTC, WETH and wstETH; and
- permitted blobs: each named `configuration.json`, `roots.json` and migration-directory filename list, plus
  `CometMainInterface.sol`, `Configurator.sol`, `CometStorage.sol` and `LICENSE`.

Pre-freeze reconnaissance inspected the repository tree, LICENSE/README, the mainnet USDC configuration/root pair
and the required marker lines. No chain RPC, governance payload row, account state, participant action or realized
response was opened. Thresholds are therefore development conformance, not blind empirical confirmation.

## Frozen gates

All nine gates are conjunctive:

1. exact clean official Git remote and commit;
2. all six configuration, roots and migration-directory paths exist;
3. every configuration contains the frozen identity, authority, rate and nonempty collateral-asset structure;
4. every roots file contains valid Comet and Configurator addresses;
5. all six Comet roots are unique;
6. the frozen supply/withdraw/collateral/liquidation action markers exist;
7. the frozen deployment, interest-curve and collateral-parameter Configurator markers exist;
8. the frozen account principal, collateral and manager-allowance storage markers exist; and
9. the exact frozen licence markers exist.

A pass decision is `PASS_SOURCE_METADATA_AUTHORIZE_CHAIN_METADATA_ONLY`. It authorizes only a separately frozen
deployment/code/configuration and archive-provider metadata audit. A failure is
`FAIL_SOURCE_METADATA_KEEP_COMPOUND_UNADMITTED`; no path, market or marker may be removed after execution.

## Forbidden interpretation

- Repository configuration is not authoritative current on-chain state.
- Migration filenames are not proof that a proposal executed.
- Account addresses are not beneficial people.
- Absence of a successful action is not absence of intent or a reverted attempt.
- A source pass is not G1 and cannot authorize account/action/price/outcome data or model training.

## Resource contract

The run reads a previously cloned clean checkout and makes no network request. Expected runtime is seconds on one
local CPU core with a small JSON result. Paid data, remote workers, V100, RTX 2060 and H20 use are all zero.

## Validation before execution

```bash
conda run -n ecophys pytest -q \
  tests/test_m3m4_source_selection.py tests/test_compound_v3_metadata.py
conda run -n ecophys ruff check \
  ecomd/research/m3m4_source_selection.py \
  ecomd/research/compound_v3_metadata.py \
  tests/test_m3m4_source_selection.py tests/test_compound_v3_metadata.py
conda run -n ecophys mypy --strict \
  ecomd/research/m3m4_source_selection.py \
  ecomd/research/compound_v3_metadata.py
```
