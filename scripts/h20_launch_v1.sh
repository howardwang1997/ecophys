#!/usr/bin/env bash
# H20 launch script for EcoMD v1 distributed training.
#
# Defaults to 4 cards (NPROC=4); override with `NPROC=8 bash scripts/h20_launch_v1.sh`.
# v1+ runs fine on 4 cards too — NPROC only affects wall-clock, not memory.
#
# Results captured into experiments/<exp>/results/:
#   training_log.json        — per-iter loss trace (primary deliverable)
#   checkpoint.pt            — model weights (every 30 min)
#   run_TIMESTAMP.log        — full stdout/stderr (this script tees here)
#   run_info.json            — env snapshot (git SHA, nvidia-smi, timestamp)
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

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Derive experiment's results directory from config path
EXP_DIR="$(dirname "$CONFIG")"
RESULTS_DIR="$EXP_DIR/results"
mkdir -p "$RESULTS_DIR"

TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
RUN_LOG="$RESULTS_DIR/run_${TIMESTAMP}.log"
RUN_INFO="$RESULTS_DIR/run_info.json"

echo "─────────────────────────────────────────────────────────────"
echo " EcoMD v1 distributed training launch"
echo " NPROC=$NPROC   CONFIG=$CONFIG   RESUME=${RESUME:-0}"
echo " REPO=$REPO_ROOT"
echo " LOG=$RUN_LOG"
echo "─────────────────────────────────────────────────────────────"

# Sanity checks
if ! command -v torchrun >/dev/null 2>&1; then
    echo "ERROR: torchrun not found — activate conda env (conda activate ecophys)?"
    exit 1
fi

if command -v nvidia-smi >/dev/null 2>&1; then
    n_gpus_visible=$(nvidia-smi -L 2>/dev/null | wc -l)
    echo " nvidia-smi reports $n_gpus_visible GPU(s) visible"
    if [[ "$n_gpus_visible" -lt "$NPROC" ]]; then
        echo "WARNING: NPROC=$NPROC but only $n_gpus_visible GPU(s) visible — aborting."
        exit 1
    fi
    if nvidia-smi topo -m 2>/dev/null | grep -q "NV"; then
        echo " NVLink detected in topology."
    else
        echo " Warning: no NVLink in topology; expected performance reduced."
    fi
fi

# Write structured run info BEFORE training starts (captures intent + env).
GIT_SHA="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
GIT_STATUS="$(git status --porcelain 2>/dev/null | head -20)"
HOSTNAME="$(hostname)"
PYTHON_VERSION="$(python --version 2>&1)"
TORCH_VERSION="$(python -c 'import torch; print(torch.__version__)' 2>/dev/null || echo unknown)"

cat > "$RUN_INFO" <<EOF
{
  "timestamp": "$TIMESTAMP",
  "hostname": "$HOSTNAME",
  "git_sha": "$GIT_SHA",
  "git_dirty": $(if [[ -n "$GIT_STATUS" ]]; then echo true; else echo false; fi),
  "nproc": $NPROC,
  "config": "$CONFIG",
  "resume": ${RESUME:-0},
  "python": "$PYTHON_VERSION",
  "torch": "$TORCH_VERSION",
  "run_log": "run_${TIMESTAMP}.log",
  "script": "h20_launch_v1.sh"
}
EOF
echo " Wrote $RUN_INFO"

CMD=(torchrun
    --nproc_per_node="$NPROC"
    --standalone
    -m ecomd.training.train_distributed
    --config "$CONFIG"
    $RESUME_FLAG
)

echo ""
# Default to gloo — NCCL 2.19.3 on this H20 node fails with 4+ ranks
# (Cuda failure 101 'invalid device ordinal'). Override with NCCL if fixed.
export DIST_BACKEND="${DIST_BACKEND:-gloo}"

echo " DIST_BACKEND=$DIST_BACKEND"
echo " Launch command:"
echo "   ${CMD[*]}"
echo ""

if [[ "${DRY_RUN:-0}" == "1" ]]; then
    echo " DRY_RUN=1 — exiting without execution."
    exit 0
fi

# tee stdout + stderr into the run log so user can retrieve it afterwards.
START=$(date +%s)
"${CMD[@]}" 2>&1 | tee "$RUN_LOG"
EXIT_CODE=${PIPESTATUS[0]}
END=$(date +%s)
ELAPSED=$((END - START))

echo ""
echo "─────────────────────────────────────────────────────────────"
echo " Training finished: exit_code=$EXIT_CODE elapsed=${ELAPSED}s (~$((ELAPSED/60))min)"
echo " Log: $RUN_LOG"
echo " Results: $RESULTS_DIR/"
echo "─────────────────────────────────────────────────────────────"

exit "$EXIT_CODE"
