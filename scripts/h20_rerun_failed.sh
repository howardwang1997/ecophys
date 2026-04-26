#!/usr/bin/env bash
# Rerun the 12 weekend configs that failed.
#
#   F4-F8 ("parameter incompatibility")  — clear stale state, retry as-is
#   F11, F14, H series ("OOM")           — use *_safe.yaml shrunk versions
#
# Usage on H20:
#   git pull
#   git checkout feature/h20-batch-v3
#   bash scripts/h20_rerun_failed.sh                # all 12
#   bash scripts/h20_rerun_failed.sh F              # only F4-F8 + F11/F14
#   bash scripts/h20_rerun_failed.sh H              # only H0-H4

set -uo pipefail

if [[ "${NPROC:-}" == "1" && -z "${FORCE_NPROC:-}" ]]; then
    echo "[guard] env had NPROC=1 — unsetting"
    unset NPROC
fi
NPROC="${NPROC:-4}"
GROUP="${1:-all}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

export DIST_BACKEND="${DIST_BACKEND:-gloo}"
export ECOPHYS_DATA_DIR="${ECOPHYS_DATA_DIR:-$REPO_ROOT/data/sample}"
export PYTHONPATH="${PYTHONPATH:-$REPO_ROOT}"

CONFIG_DIR="experiments/023_weekend"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
QUEUE_LOG="$CONFIG_DIR/_rerun_${TIMESTAMP}.log"
: > "$QUEUE_LOG"

# (label, config, outdir)  — F4-F8 use original config (no shrink needed),
# but we wipe stale state. F11/F14/H use _safe versions.
declare -a JOBS_F=(
    "f4_hidden64|$CONFIG_DIR/config_f4_hidden64.yaml|$CONFIG_DIR/results_f4_hidden64"
    "f5_hidden96|$CONFIG_DIR/config_f5_hidden96.yaml|$CONFIG_DIR/results_f5_hidden96"
    "f6_dstate64|$CONFIG_DIR/config_f6_dstate64.yaml|$CONFIG_DIR/results_f6_dstate64"
    "f7_sps100|$CONFIG_DIR/config_f7_sps100.yaml|$CONFIG_DIR/results_f7_sps100"
    "f8_sps200|$CONFIG_DIR/config_f8_sps200.yaml|$CONFIG_DIR/results_f8_sps200"
    "f11_safe|$CONFIG_DIR/config_f11_chunk32_safe.yaml|$CONFIG_DIR/results_f11_safe"
    "f14_safe|$CONFIG_DIR/config_f14_f3_plus_hidden64_safe.yaml|$CONFIG_DIR/results_f14_safe"
)
declare -a JOBS_H=(
    "h0_safe|$CONFIG_DIR/config_h0_n20k_safe.yaml|$CONFIG_DIR/results_h0_safe"
    "h1_safe|$CONFIG_DIR/config_h1_n50k_safe.yaml|$CONFIG_DIR/results_h1_safe"
    "h2_safe|$CONFIG_DIR/config_h2_n20k_f3loss_safe.yaml|$CONFIG_DIR/results_h2_safe"
    "h3_safe|$CONFIG_DIR/config_h3_n50k_f3loss_safe.yaml|$CONFIG_DIR/results_h3_safe"
    "h4_safe|$CONFIG_DIR/config_h4_n100k_yolo_safe.yaml|$CONFIG_DIR/results_h4_safe"
)

case "$GROUP" in
    F|f) JOBS=("${JOBS_F[@]}") ;;
    H|h) JOBS=("${JOBS_H[@]}") ;;
    *)   JOBS=("${JOBS_F[@]}" "${JOBS_H[@]}") ;;
esac

run_one() {
    local label="$1" config="$2" outdir="$3"
    mkdir -p "$outdir"
    # Wipe stale checkpoint (root cause of "param incompatibility" if cfg differs)
    rm -f "$outdir/checkpoint.pt"
    echo "" | tee -a "$QUEUE_LOG"
    echo "═ TRAIN $label ═ $(date +%H:%M:%S)" | tee -a "$QUEUE_LOG"
    local start=$(date +%s)
    timeout 3000 torchrun --nproc_per_node="$NPROC" --standalone \
        -m ecomd.training.train_distributed \
        --config "$config" --out-dir "$outdir" 2>&1 \
      | tee "$outdir/train_${TIMESTAMP}.log" >> "$QUEUE_LOG"
    local exit_code=${PIPESTATUS[0]}
    local elapsed=$(( $(date +%s) - start ))
    if [[ $exit_code -eq 0 ]]; then
        echo "  ✓ $label ${elapsed}s" | tee -a "$QUEUE_LOG"
    else
        echo "  ✗ $label exit=$exit_code (${elapsed}s) — keep going" | tee -a "$QUEUE_LOG"
    fi
}

eval_one() {
    local label="$1" config="$2" outdir="$3"
    if [[ ! -f "$outdir/checkpoint.pt" ]]; then
        echo "  [skip-eval $label] no ckpt" | tee -a "$QUEUE_LOG"
        return 0
    fi
    if [[ -f "$outdir/inference_merged.json" ]]; then
        echo "  [skip-eval $label] already done" | tee -a "$QUEUE_LOG"
        return 0
    fi
    echo "" | tee -a "$QUEUE_LOG"
    echo "═ EVAL  $label ═ $(date +%H:%M:%S)" | tee -a "$QUEUE_LOG"
    local start=$(date +%s)
    timeout 1800 torchrun --nproc_per_node="$NPROC" --standalone \
        -m ecomd.inference.run_large \
        --ckpt "$outdir/checkpoint.pt" --config "$config" \
        --n-steps 4000 --n-realizations-per-rank 2 2>&1 \
      | tee "$outdir/eval_${TIMESTAMP}.log" >> "$QUEUE_LOG"
    local exit_code=${PIPESTATUS[0]}
    local elapsed=$(( $(date +%s) - start ))
    if [[ $exit_code -eq 0 ]]; then
        echo "  ✓ eval $label ${elapsed}s" | tee -a "$QUEUE_LOG"
    else
        echo "  ✗ eval $label exit=$exit_code" | tee -a "$QUEUE_LOG"
    fi
}

echo "═══ RERUN FAILED — group=$GROUP, ${#JOBS[@]} configs ═══" | tee -a "$QUEUE_LOG"
echo " NPROC=$NPROC log=$QUEUE_LOG" | tee -a "$QUEUE_LOG"
for entry in "${JOBS[@]}"; do
    IFS='|' read -r label config outdir <<< "$entry"
    run_one "$label" "$config" "$outdir"
done
for entry in "${JOBS[@]}"; do
    IFS='|' read -r label config outdir <<< "$entry"
    eval_one "$label" "$config" "$outdir"
done
echo "" | tee -a "$QUEUE_LOG"
echo "═══ DONE $(date) ═══" | tee -a "$QUEUE_LOG"
