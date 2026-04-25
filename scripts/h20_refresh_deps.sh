#!/usr/bin/env bash
# Refresh H20 ecophys env to pick up new deps added to pyproject.toml.
# Idempotent — safe to run on existing setup. Use this when you see
# ImportError / ModuleNotFoundError in training/inference logs.
#
# Specifically catches: arch (GARCH for conditional_kurtosis fact #7).
#
# Usage:
#   bash scripts/h20_refresh_deps.sh

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

echo "[refresh] re-installing ecomd + all extras into env 'ecophys'"
conda run -n ecophys pip install -e ".[dev]"

echo "[refresh] verifying critical optional deps"
conda run -n ecophys python -c "
import importlib
for mod in ['arch', 'statsmodels', 'POT', 'torchsde']:
    try:
        importlib.import_module(mod)
        print(f'  [ok]  {mod}')
    except Exception as e:
        print(f'  [FAIL] {mod}: {e}')
"
echo "[refresh] done"
