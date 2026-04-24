#!/usr/bin/env bash
# H20 launch — EcoMD v1 DIAGNOSTIC rerun (chunk_steps hypothesis test)
#
# Runs config_h20_diag.yaml (N=4000, chunk_steps=64, warmup_steps=16) into a
# SEPARATE results directory so the original results/ from the first H20 run
# is preserved for comparison.
#
# Output:
#   experiments/006_ecomd_v1/results_diag/
#     training_log.json   — per-iter loss + metrics (compare vs results/training_log.json)
#     checkpoint.pt
#     run_TIMESTAMP.log
#     run_info.json
#
# Usage:
#   bash scripts/h20_launch_v1_diag.sh
#   NPROC=8 bash scripts/h20_launch_v1_diag.sh
#   DRY_RUN=1 bash scripts/h20_launch_v1_diag.sh
#
# Compare after it finishes:
#   jq '.history[-1]' experiments/006_ecomd_v1/results/training_log.json
#   jq '.history[-1]' experiments/006_ecomd_v1/results_diag/training_log.json

set -euo pipefail

NPROC="${NPROC:-4}"
CONFIG="experiments/006_ecomd_v1/config_h20_diag.yaml"
EXP_DIR="experiments/006_ecomd_v1"
RESULTS_DIR="$EXP_DIR/results_diag"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

mkdir -p "$RESULTS_DIR"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
RUN_LOG="$RESULTS_DIR/run_${TIMESTAMP}.log"
RUN_INFO="$RESULTS_DIR/run_info.json"

echo "─────────────────────────────────────────────────────────────"
echo " EcoMD v1 DIAG launch — chunk_steps hypothesis test"
echo " NPROC=$NPROC   CONFIG=$CONFIG"
echo " OUT=$RESULTS_DIR"
echo " LOG=$RUN_LOG"
echo "─────────────────────────────────────────────────────────────"

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
fi

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
  "variant": "v1_diag_chunk64_N4K",
  "hypothesis": "chunk_steps=24/warmup=16 left only 8 BPTT steps; restoring 48-step window with halved N",
  "python": "$PYTHON_VERSION",
  "torch": "$TORCH_VERSION",
  "run_log": "run_${TIMESTAMP}.log"
}
EOF
echo " Wrote $RUN_INFO"

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
echo " Launch command:"
echo "   ${CMD[*]}"
echo ""

if [[ "${DRY_RUN:-0}" == "1" ]]; then
    echo " DRY_RUN=1 — exiting without execution."
    exit 0
fi

START=$(date +%s)
"${CMD[@]}" 2>&1 | tee "$RUN_LOG"
EXIT_CODE=${PIPESTATUS[0]}
END=$(date +%s)
ELAPSED=$((END - START))

echo ""
echo "─────────────────────────────────────────────────────────────"
echo " DIAG run finished: exit_code=$EXIT_CODE elapsed=${ELAPSED}s (~$((ELAPSED/60))min)"
echo " Log: $RUN_LOG"
echo " Results: $RESULTS_DIR/"
echo ""
echo " Compare with original v1:"
echo "   jq '.history[-1]' experiments/006_ecomd_v1/results/training_log.json"
echo "   jq '.history[-1]' $RESULTS_DIR/training_log.json"
echo ""
echo " If acf_sim becomes positive (→ +0.25 target), chunk_steps hypothesis confirmed."
echo "─────────────────────────────────────────────────────────────"

exit "$EXIT_CODE"
