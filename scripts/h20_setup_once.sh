#!/usr/bin/env bash
# One-time H20 setup.
# Run from the ecophys repo root after `git clone` on the H20 machine.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

# 1) Ensure conda env exists
if ! conda env list | awk '{print $1}' | grep -qx "ecophys"; then
    echo "[setup] creating conda env ecophys (python 3.11)"
    conda create -n ecophys python=3.11 -y
fi

# 2) Install package + deps
echo "[setup] installing ecomd + deps"
conda run -n ecophys pip install -e ".[dev]"

# 3) Seed the R2 env file if missing (project-local at <repo>/.env.r2)
R2_ENV="${REPO_DIR}/.env.r2"
R2_ENV_TEMPLATE="${REPO_DIR}/.env.r2.example"
if [[ ! -f "$R2_ENV" ]]; then
    if [[ -f "$R2_ENV_TEMPLATE" ]]; then
        cp "$R2_ENV_TEMPLATE" "$R2_ENV"
        chmod 600 "$R2_ENV"
        echo "[setup] template copied: $R2_ENV_TEMPLATE → $R2_ENV"
        echo "[setup] fill in the blank values before using r2_sync"
    else
        echo "[setup] WARNING: $R2_ENV_TEMPLATE missing; create $R2_ENV manually"
    fi
fi

# 4) Check NFS mount
NFS_PATH="/AI4S/Users/howardwang/ecophys"
if [[ ! -d "$NFS_PATH" ]]; then
    echo "[setup] WARNING: $NFS_PATH is not a directory — check NFS mount"
else
    mkdir -p "$NFS_PATH"/{raw,processed,splits,experiments,reference_values,papers}
    echo "[setup] NFS layout initialized at $NFS_PATH"
fi

# 5) Check hot cache dir (H20: /root/data/ecophys — target budget 500 GB)
HOT_PATH="/root/data/ecophys"
if [[ ! -d "$HOT_PATH" ]]; then
    echo "[setup] creating $HOT_PATH"
    mkdir -p "$HOT_PATH"/{raw,processed,splits,experiments}
fi

# 6) Show free space on both drives
echo "[setup] disk usage snapshot:"
df -h /root 2>/dev/null | tail -1 | awk '{print "  /root (code):", $4 " free of " $2}' || true
df -h /root/data 2>/dev/null | tail -1 | awk '{print "  /root/data (hot cache):", $4 " free of " $2}' || true
df -h /AI4S 2>/dev/null | tail -1 | awk '{print "  /AI4S (NFS):", $4 " free of " $2}' || true

echo "[setup] done. Next:"
echo "  1) edit $R2_ENV with your R2 credentials"
echo "  2) run scripts/h20_pull_from_r2.sh <prefix> to fetch data"
echo "  3) add to your shell rc:"
echo "       export ECOPHYS_DATA_DIR=$HOT_PATH"
echo "       export ECOPHYS_NFS_DIR=/AI4S/Users/howardwang/ecophys"
