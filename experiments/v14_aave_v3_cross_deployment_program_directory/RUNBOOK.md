# Aave V3 cross-deployment program directory v1 runbook

Do not run this protocol until the manifest, collector, tests, preregistration and runbook are committed, pushed and
the remote branch is verified at the exact protocol SHA.

## 1. Materialize immutable source

Create a fresh partial clone outside the EcoPhys worktree, detach at the frozen commit and materialize exactly the
ten pinned address files:

```bash
git clone --filter=blob:none --sparse \
  https://github.com/aave-dao/aave-address-book.git \
  /private/tmp/aave-address-book-b0-v1
git -C /private/tmp/aave-address-book-b0-v1 checkout --detach \
  70e2f303fe93616784148d6827df6644e5dda4db
git -C /private/tmp/aave-address-book-b0-v1 sparse-checkout set --no-cone \
  src/AaveV3Arbitrum.sol src/AaveV3Avalanche.sol src/AaveV3BNB.sol \
  src/AaveV3Base.sol src/AaveV3Ethereum.sol src/AaveV3Gnosis.sol \
  src/AaveV3Linea.sol src/AaveV3Optimism.sol src/AaveV3Polygon.sol \
  src/AaveV3Scroll.sol
```

The collector reads `commit:path` git objects, not mutable worktree copies.

## 2. Clean protocol worktree and preflight

Create a clean detached EcoPhys worktree at `<PROTOCOL_COMMIT>`, materialize all tracked parent/code/test paths and
confirm every output is absent. Run only Conda Python:

```bash
conda run -n ecophys python -m pytest \
  tests/test_aave_cross_deployment_program_directory.py \
  tests/test_aave_bundle_structure.py \
  tests/test_aave_lt_event_directory.py \
  tests/test_aave_liquidation_threshold_source.py -q
conda run -n ecophys python -m ruff format --check \
  ecomd/research/aave_cross_deployment_program_directory.py \
  tests/test_aave_cross_deployment_program_directory.py
conda run -n ecophys python -m ruff check \
  ecomd/research/aave_cross_deployment_program_directory.py \
  tests/test_aave_cross_deployment_program_directory.py
conda run -n ecophys python -m mypy --strict --explicit-package-bases \
  ecomd/research/aave_cross_deployment_program_directory.py
```

Then verify the duplicate-safe manifest, parent hashes/decisions and all ten address-book objects locally. No chain
request is made by these checks.

## 3. One sealed collection

Replace `<PROTOCOL_COMMIT>` with the verified pushed SHA and run once:

```bash
conda run -n ecophys python \
  -m ecomd.research.aave_cross_deployment_program_directory \
  data/manifests/aave_v3_cross_deployment_program_directory_v1.yaml \
  --address-book-source /private/tmp/aave-address-book-b0-v1 \
  --summary experiments/v14_aave_v3_cross_deployment_program_directory/artifacts/summary.json \
  --directory experiments/v14_aave_v3_cross_deployment_program_directory/artifacts/program_directory.json \
  --response-hashes experiments/v14_aave_v3_cross_deployment_program_directory/artifacts/rpc_response_hashes.json \
  --failure experiments/v14_aave_v3_cross_deployment_program_directory/artifacts/failure.json \
  --collection-commit <PROTOCOL_COMMIT>
```

The collector refuses a dirty EcoPhys worktree or any existing output. Internal transport retries and deterministic
range bisection are already part of the protocol. Do not manually retry, replace an endpoint, omit a deployment,
change a cutoff or raise a cap under v1.

## 4. Archive and gate

If `failure.json` exists, preserve it and the response-hash ledger; B1 remains closed. On normal completion, write
a standalone verifier that does not import the collector, rederive every cutoff, surface, history, program and gate
from the immutable normalized artifacts, then write `RESULTS.md`.

Regardless of PASS or FAIL, commit and push the exact artifacts and result documentation. A PASS licenses only a
new B1 protocol design. Do not open transaction/receipt/calldata/trace, state, account, response or model rows and
do not start a GPU job.
