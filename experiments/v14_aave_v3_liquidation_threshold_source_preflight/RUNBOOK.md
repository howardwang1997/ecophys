# Runbook — Aave V3 LT source/effect preflight v1

Use the `ecophys` Conda environment. Do not audit before protocol files and tests are committed and pushed. Do not
substitute a source commit, repository, file, marker or output path under v1.

## 1. Freeze and test

```bash
conda run -n ecophys ruff format --check \
  ecomd/research/aave_liquidation_threshold_source.py \
  tests/test_aave_liquidation_threshold_source.py
conda run -n ecophys ruff check \
  ecomd/research/aave_liquidation_threshold_source.py \
  tests/test_aave_liquidation_threshold_source.py
conda run -n ecophys mypy --strict ecomd/research/aave_liquidation_threshold_source.py
conda run -n ecophys pytest -q tests/test_aave_liquidation_threshold_source.py
```

Commit and push. Record the full SHA as `PROTOCOL_COMMIT` and verify the remote branch points to it.

## 2. Create detached inputs

Create a detached EcoPhys worktree at `PROTOCOL_COMMIT`. Clone source only after the freeze:

```bash
git worktree add --detach /private/tmp/ecophys-aave-lt-a0-v1-wt PROTOCOL_COMMIT
git clone --filter=blob:none --no-checkout \
  https://github.com/aave-dao/aave-v3-origin.git \
  /private/tmp/aave-v3-origin-cff15-v1
git -C /private/tmp/aave-v3-origin-cff15-v1 sparse-checkout init --no-cone
git -C /private/tmp/aave-v3-origin-cff15-v1 sparse-checkout set --no-cone \
  LICENSE \
  src/contracts/extensions/v3-config-engine/EngineFlags.sol \
  src/contracts/extensions/v3-config-engine/AaveV3ConfigEngine.sol \
  src/contracts/extensions/v3-config-engine/IAaveV3ConfigEngine.sol \
  src/contracts/extensions/v3-config-engine/libraries/CollateralEngine.sol \
  src/contracts/interfaces/IPool.sol \
  src/contracts/interfaces/IPoolConfigurator.sol \
  src/contracts/protocol/libraries/configuration/ReserveConfiguration.sol \
  src/contracts/protocol/libraries/configuration/UserConfiguration.sol \
  src/contracts/protocol/libraries/logic/GenericLogic.sol \
  src/contracts/protocol/libraries/logic/ValidationLogic.sol \
  src/contracts/protocol/libraries/math/WadRayMath.sol \
  src/contracts/protocol/pool/Pool.sol \
  src/contracts/protocol/pool/PoolConfigurator.sol
git -C /private/tmp/aave-v3-origin-cff15-v1 checkout --detach \
  cff15de6d1271b0c800fc001f4aea4c263e8a597
```

Both worktrees must have empty `git status --porcelain`. Source remote and `HEAD` must exactly match the manifest.

## 3. Execute once

Both outcome paths must be absent. From the detached EcoPhys worktree run:

```bash
test ! -e experiments/v14_aave_v3_liquidation_threshold_source_preflight/artifacts/summary.json
test ! -e experiments/v14_aave_v3_liquidation_threshold_source_preflight/artifacts/failure.json
conda run -n ecophys python -m ecomd.research.aave_liquidation_threshold_source \
  data/manifests/aave_v3_liquidation_threshold_source_preflight_v1.yaml \
  --source-repo /private/tmp/aave-v3-origin-cff15-v1 \
  --output experiments/v14_aave_v3_liquidation_threshold_source_preflight/artifacts/summary.json \
  --failure experiments/v14_aave_v3_liquidation_threshold_source_preflight/artifacts/failure.json \
  --collection-commit PROTOCOL_COMMIT
```

Do not rerun after either path appears. A scientific source fail is in `summary.json`; an exception creates only
`failure.json` and reaches no scientific decision.

## 4. Verify and archive

Without importing the audit module, independently check commits/remotes/cleanliness; manifest/artifact hashes;
fourteen distinct safe paths and file hashes; all twelve gates; markers against whitespace-normalized source; the
weighted identity, half-up division, eMode zero route and HF-boundary toy case; access locks; no raw bodies; and
success/failure mutual exclusion.

Write `RESULTS.md`, update the NCS plan, resource audit, source scorecard, daily log and long-term memory, then
commit and push the result. Even a pass leaves account, action, response and GPU queues locked.
