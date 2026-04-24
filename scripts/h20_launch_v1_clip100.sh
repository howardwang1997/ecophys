#!/usr/bin/env bash
# H20 launch — EcoMD v1 grad_clip=100 diagnostic
#
# Single-variable change from config_h20.yaml: grad_clip_max_norm 1.0 → 100.
# Output goes to experiments/006_ecomd_v1/results_clip100/ so prior runs
# (results/ and results_diag/) stay intact for side-by-side compare.
#
# Runtime: ~55s on 4 cards (100 iters × 531ms).
#
# Usage:
#   bash scripts/h20_launch_v1_clip100.sh
#   NPROC=8 bash scripts/h20_launch_v1_clip100.sh
#   DRY_RUN=1 bash scripts/h20_launch_v1_clip100.sh
#
# After it finishes, compare three-way:
#   jq '.history | {first:.[0], mid:.[50], last:.[-1]}' experiments/006_ecomd_v1/results/training_log.json
#   jq '.history | {first:.[0], mid:.[50], last:.[-1]}' experiments/006_ecomd_v1/results_diag/training_log.json
#   jq '.history | {first:.[0], mid:.[50], last:.[-1]}' experiments/006_ecomd_v1/results_clip100/training_log.json

set -euo pipefail

NPROC="${NPROC:-4}"
CONFIG="experiments/006_ecomd_v1/config_h20_clip100.yaml"
EXP_DIR="experiments/006_ecomd_v1"
RESULTS_DIR="$EXP_DIR/results_clip100"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

mkdir -p "$RESULTS_DIR"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
RUN_LOG="$RESULTS_DIR/run_${TIMESTAMP}.log"
RUN_INFO="$RESULTS_DIR/run_info.json"

echo "─────────────────────────────────────────────────────────────"
echo " EcoMD v1 CLIP=100 launch — gradient clipping hypothesis test"
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
  "variant": "v1_clip100",
  "hypothesis": "grad_clip=1.0 caps effective lr at 6.6e-6; raise to 100 → effective lr ~6.7e-4",
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
echo " CLIP=100 run finished: exit_code=$EXIT_CODE elapsed=${ELAPSED}s"
echo " Log: $RUN_LOG"
echo " Results: $RESULTS_DIR/"
echo ""
echo " Decision rule:"
echo "   - acf_sim late mean > 0.1 AND loss < 0.7: clip hypothesis confirmed."
echo "   - loss plateaus near 0.82 like before: problem is architecture."
echo "─────────────────────────────────────────────────────────────"

exit "$EXIT_CODE"
