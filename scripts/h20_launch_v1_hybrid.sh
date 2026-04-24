#!/usr/bin/env bash
# H20 launch — EcoMD v1 HYBRID (winning architecture from Mac ablation #008).
#
# Config: experiments/009_v1_hybrid_h20/config_h20.yaml
#   - readout_mode=hybrid (per_edge + per_node)
#   - body_order=4, k=200 (dense k-NN, 2% coverage on N=10K)
#   - grad_clip=100, chunk=48 (lessons from prior H20 diag runs)
#
# Runtime estimate: ~4-6 min training (200 iter × ~1s/iter on 4 cards).
#
# Usage:
#   bash scripts/h20_launch_v1_hybrid.sh
#   NPROC=8 bash scripts/h20_launch_v1_hybrid.sh
#   DRY_RUN=1 bash scripts/h20_launch_v1_hybrid.sh
#
# After training finishes, run the stylized-facts eval via:
#   bash scripts/h20_inference.sh experiments/009_v1_hybrid_h20/config_h20.yaml
# and inspect results/inference_merged.json for the aggregated #6 ACF(r²).

set -euo pipefail

NPROC="${NPROC:-4}"
CONFIG="experiments/009_v1_hybrid_h20/config_h20.yaml"
EXP_DIR="experiments/009_v1_hybrid_h20"
RESULTS_DIR="$EXP_DIR/results"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

mkdir -p "$RESULTS_DIR"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
RUN_LOG="$RESULTS_DIR/run_${TIMESTAMP}.log"
RUN_INFO="$RESULTS_DIR/run_info.json"

echo "─────────────────────────────────────────────────────────────"
echo " EcoMD v1 HYBRID launch (Mac ablation-winning architecture)"
echo " NPROC=$NPROC   CONFIG=$CONFIG"
echo " OUT=$RESULTS_DIR   LOG=$RUN_LOG"
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
  "variant": "v1_hybrid_h20",
  "notes": "readout_mode=hybrid, body=4, k=200, clip=100, chunk=48; winning Mac config H scaled to N=10K",
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
echo " HYBRID run finished: exit_code=$EXIT_CODE elapsed=${ELAPSED}s (~$((ELAPSED/60))min)"
echo " Log: $RUN_LOG"
echo " Results: $RESULTS_DIR/"
echo ""
echo " Next step: evaluate 11 stylized facts on checkpoint"
echo "   bash scripts/h20_inference.sh $CONFIG"
echo "─────────────────────────────────────────────────────────────"

exit "$EXIT_CODE"
