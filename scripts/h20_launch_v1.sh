#!/usr/bin/env bash
# H20 launch script for EcoMD v1 distributed training.
#
# Defaults to 4 cards (NPROC=4); override with `NPROC=8 bash scripts/h20_launch_v1.sh`
# to scale to 8 cards once 4-card run is verified stable.
#
# Prerequisites (run ONCE per H20 after a fresh git pull):
#   1. `bash scripts/h20_setup_once.sh`
#   2. Activate conda env: `conda activate ecophys`
#   3. Login to wandb: `wandb login` (or set WANDB_API_KEY env var)
#   4. Ensure data is pulled: `bash scripts/h20_pull_from_r2.sh ...`
#
# Usage:
#   bash scripts/h20_launch_v1.sh              # 4 cards, fresh run
#   NPROC=8 bash scripts/h20_launch_v1.sh      # 8 cards
#   RESUME=1 bash scripts/h20_launch_v1.sh     # resume from last checkpoint
#   DRY_RUN=1 bash scripts/h20_launch_v1.sh    # print command without executing

set -euo pipefail

NPROC="${NPROC:-4}"
CONFIG="${CONFIG:-experiments/006_ecomd_v1/config_h20.yaml}"
RESUME_FLAG=""
if [[ "${RESUME:-0}" == "1" ]]; then
    RESUME_FLAG="--resume"
fi

# Repo root = dir containing this script's parent
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "─────────────────────────────────────────────────────────────"
echo " EcoMD v1 distributed training launch"
echo " NPROC=$NPROC   CONFIG=$CONFIG   RESUME=${RESUME:-0}"
echo " REPO=$REPO_ROOT"
echo "─────────────────────────────────────────────────────────────"

# Sanity checks
if ! command -v torchrun >/dev/null 2>&1; then
    echo "ERROR: torchrun not found — activate conda env (conda activate ecophys)?"
    exit 1
fi

if [[ -n "${CUDA_VISIBLE_DEVICES+x}" ]]; then
    echo " CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"
fi

if command -v nvidia-smi >/dev/null 2>&1; then
    n_gpus_visible=$(nvidia-smi -L 2>/dev/null | wc -l)
    echo " nvidia-smi reports $n_gpus_visible GPU(s) visible"
    if [[ "$n_gpus_visible" -lt "$NPROC" ]]; then
        echo "WARNING: NPROC=$NPROC but only $n_gpus_visible GPU(s) visible — aborting."
        exit 1
    fi
fi

# Check if NVLink is active (heuristic — look for NVL in topo)
if command -v nvidia-smi >/dev/null 2>&1; then
    if nvidia-smi topo -m 2>/dev/null | grep -q "NV"; then
        echo " NVLink detected in topology."
    else
        echo " Warning: no NVLink in topology; expected performance reduced."
    fi
fi

CMD=(torchrun
    --nproc_per_node="$NPROC"
    --standalone
    -m ecomd.training.train_distributed
    --config "$CONFIG"
    $RESUME_FLAG
)

echo ""
echo " Launch command:"
echo "   ${CMD[*]}"
echo ""

if [[ "${DRY_RUN:-0}" == "1" ]]; then
    echo " DRY_RUN=1 — exiting without execution."
    exit 0
fi

exec "${CMD[@]}"
