#!/usr/bin/env bash
# H20 inference launcher. Argument: 'v1' or 'v1plus' (or full config path).
#
# Results captured to experiments/<exp>/results/:
#   inference_rank_{0..N-1}.json  — per-rank realizations
#   inference_merged.json         — rank-0 aggregate over all rollouts
#   inference_TIMESTAMP.log       — full stdout/stderr (this script tees here)
#
# Usage:
#   bash scripts/h20_inference.sh v1                       # 4 cards × 2 = 8 rollouts
#   bash scripts/h20_inference.sh v1plus
#   NPROC=8 bash scripts/h20_inference.sh v1               # 8 cards × 2 = 16 rollouts
#   bash scripts/h20_inference.sh v1 --n-steps 8000 --n-realizations-per-rank 4

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <v1|v1plus> [extra torchrun args...]"
    exit 1
fi

VARIANT="$1"; shift

case "$VARIANT" in
    v1)
        CONFIG=experiments/006_ecomd_v1/config_h20.yaml
        CKPT=experiments/006_ecomd_v1/results/checkpoint.pt
        ;;
    v1plus|v1+)
        CONFIG=experiments/007_ecomd_v1plus/config_h20.yaml
        CKPT=experiments/007_ecomd_v1plus/results/checkpoint.pt
        ;;
    *)
        CONFIG="$VARIANT"
        CKPT="$(dirname "$CONFIG")/results/checkpoint.pt"
        ;;
esac

NPROC="${NPROC:-4}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [[ ! -f "$CKPT" ]]; then
    echo "ERROR: checkpoint not found at $CKPT"
    echo "Run training first: bash scripts/h20_launch_${VARIANT}.sh"
    exit 1
fi

RESULTS_DIR="$(dirname "$CKPT")"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
RUN_LOG="$RESULTS_DIR/inference_${TIMESTAMP}.log"

echo "─────────────────────────────────────────────────────────────"
echo " EcoMD inference launch"
echo " VARIANT=$VARIANT   NPROC=$NPROC"
echo " CONFIG=$CONFIG"
echo " CKPT=$CKPT"
echo " LOG=$RUN_LOG"
echo "─────────────────────────────────────────────────────────────"

CMD=(torchrun
    --nproc_per_node="$NPROC"
    --standalone
    -m ecomd.inference.run_large
    --ckpt "$CKPT"
    --config "$CONFIG"
    "$@"
)

echo " Launch command:"
echo "   ${CMD[*]}"
echo ""

if [[ "${DRY_RUN:-0}" == "1" ]]; then
    echo " DRY_RUN=1 — exiting."
    exit 0
fi

START=$(date +%s)
"${CMD[@]}" 2>&1 | tee "$RUN_LOG"
EXIT_CODE=${PIPESTATUS[0]}
END=$(date +%s)
ELAPSED=$((END - START))

echo ""
echo "─────────────────────────────────────────────────────────────"
echo " Inference finished: exit_code=$EXIT_CODE elapsed=${ELAPSED}s"
echo " Merged: $RESULTS_DIR/inference_merged.json"
echo " Log: $RUN_LOG"
echo "─────────────────────────────────────────────────────────────"

exit "$EXIT_CODE"
