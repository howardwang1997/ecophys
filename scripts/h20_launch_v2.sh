#!/usr/bin/env bash
# H20 launch — EcoMD v2.1 (Mac ablation winner) single DDP production run.
#
# Uses experiments/016_ecomd_v2/config_h20_spx_N10k.yaml (v2.1 recipe:
# gauge off, T=ones, Kyle off, phi=1.0). 4-card DDP by default.
#
# For batched hyperparameter sweep instead, use:
#   bash scripts/h20_launch_v2_ablation.sh h20_full
#
# Usage:
#   git pull
#   bash scripts/h20_launch_v2.sh                   # 4 cards
#   NPROC=8 bash scripts/h20_launch_v2.sh           # 8 cards
#   DRY_RUN=1 bash scripts/h20_launch_v2.sh
#   CONFIG=<path> bash scripts/h20_launch_v2.sh     # custom config

set -euo pipefail

NPROC="${NPROC:-4}"
CONFIG="${CONFIG:-experiments/016_ecomd_v2/config_h20_spx_N10k.yaml}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

EXP_DIR="$(dirname "$CONFIG")"
RESULTS_DIR="$EXP_DIR/results"
mkdir -p "$RESULTS_DIR"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
RUN_LOG="$RESULTS_DIR/run_${TIMESTAMP}.log"
RUN_INFO="$RESULTS_DIR/run_info.json"

echo "─────────────────────────────────────────────────────────────"
echo " EcoMD v2.1 launch"
echo " NPROC=$NPROC"
echo " CONFIG=$CONFIG"
echo " LOG=$RUN_LOG"
echo "─────────────────────────────────────────────────────────────"

if ! command -v torchrun >/dev/null 2>&1; then
    echo "ERROR: torchrun not found — conda activate ecophys?"
    exit 1
fi

if command -v nvidia-smi >/dev/null 2>&1; then
    n_gpu=$(nvidia-smi -L 2>/dev/null | wc -l)
    echo " nvidia-smi: $n_gpu GPU(s)"
    if [[ "$n_gpu" -lt "$NPROC" ]]; then
        echo "WARNING: NPROC=$NPROC but only $n_gpu GPUs; aborting."
        exit 1
    fi
fi

GIT_SHA="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
HOSTNAME="$(hostname)"
cat > "$RUN_INFO" <<EOF
{
  "timestamp": "$TIMESTAMP",
  "hostname": "$HOSTNAME",
  "git_sha": "$GIT_SHA",
  "nproc": $NPROC,
  "config": "$CONFIG",
  "variant": "ecomd_v2.1",
  "notes": "Mac ablation winner: gauge_enforce=false, T_init_mode=ones, kyle_enabled=false, phi_init_gain=1.0"
}
EOF

CMD=(torchrun
    --nproc_per_node="$NPROC"
    --standalone
    -m ecomd.training.train_distributed
    --config "$CONFIG"
    --out-dir "$RESULTS_DIR"
)

export DIST_BACKEND="${DIST_BACKEND:-gloo}"
echo ""
echo " DIST_BACKEND=$DIST_BACKEND"
echo " Launch: ${CMD[*]}"

if [[ "${DRY_RUN:-0}" == "1" ]]; then
    echo " DRY_RUN=1 — exit"
    exit 0
fi

START=$(date +%s)
"${CMD[@]}" 2>&1 | tee "$RUN_LOG"
EXIT=${PIPESTATUS[0]}
END=$(date +%s)
ELAPSED=$((END - START))

echo ""
echo "─────────────────────────────────────────────────────────────"
echo " Finished: exit=$EXIT  elapsed=${ELAPSED}s (~$((ELAPSED/60))min)"
echo " Log: $RUN_LOG"
echo " Next: eval via scripts/h20_inference.sh <config>"
echo "─────────────────────────────────────────────────────────────"

exit "$EXIT"
