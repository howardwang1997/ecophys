#!/usr/bin/env bash
# Phase 8 — Custom autograd.Function HBM test, mirrors h20_hbm_profile.sh
# pattern. Runs each config sequentially on a single card to get clean
# peak-HBM measurements.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

export DIST_BACKEND="${DIST_BACKEND:-nccl}"
export PYTHONPATH="${PYTHONPATH:-$REPO_ROOT}"
NPROC="${NPROC:-1}"
CARD="${CARD:-0}"

CONFIG_DIR="experiments/030_custom_autograd"
QUEUE_LOG="$CONFIG_DIR/_run_$(date +%Y%m%d-%H%M%S).log"
: > "$QUEUE_LOG"

echo "═══ CUSTOM AUTOGRAD TEST — $(date) ═══" | tee -a "$QUEUE_LOG"
echo "  Card: $CARD, NPROC: $NPROC" | tee -a "$QUEUE_LOG"

cfgs=( "$CONFIG_DIR"/config_p8_*.yaml )
echo "  Configs: ${#cfgs[@]}" | tee -a "$QUEUE_LOG"

for cfg in "${cfgs[@]}"; do
    label=$(basename "$cfg" .yaml | sed 's/^config_//')
    outdir="$CONFIG_DIR/results_${label}"
    mkdir -p "$outdir"
    if [[ -f "$outdir/training_log.json" ]]; then
        echo "  [skip $label]" | tee -a "$QUEUE_LOG"
        continue
    fi
    echo "" | tee -a "$QUEUE_LOG"
    echo "═ TEST $label ═ $(date +%H:%M:%S)" | tee -a "$QUEUE_LOG"
    start=$(date +%s)
    job_log="$outdir/train.log"
    CUDA_VISIBLE_DEVICES="$CARD" \
    timeout 600 torchrun --nproc_per_node="$NPROC" --standalone \
        -m ecomd.training.train_distributed \
        --config "$cfg" --out-dir "$outdir" 2>&1 \
      | tee "$job_log" >> "$QUEUE_LOG"
    exit_code=${PIPESTATUS[0]}
    elapsed=$(( $(date +%s) - start ))
    if [[ $exit_code -eq 0 ]]; then
        echo "  ✓ $label ${elapsed}s" | tee -a "$QUEUE_LOG"
    elif [[ $exit_code -eq 124 ]]; then
        echo "  ⏱ $label TIMEOUT after ${elapsed}s" | tee -a "$QUEUE_LOG"
    else
        echo "  ✗ $label exit=$exit_code (${elapsed}s) — likely OOM" | tee -a "$QUEUE_LOG"
    fi
done

echo "" | tee -a "$QUEUE_LOG"
echo "═══ DONE — $(date) ═══" | tee -a "$QUEUE_LOG"
echo "" | tee -a "$QUEUE_LOG"
echo "Aggregate peak HBM:" | tee -a "$QUEUE_LOG"
for d in "$CONFIG_DIR"/results_p8_*; do
    label=$(basename "$d" | sed 's/^results_//')
    if [[ -f "$d/training_log.json" ]]; then
        peak=$(conda run -n ecophys python -c "import json; d=json.load(open('$d/training_log.json')); ph=d.get('peak_hbm', {}); print(f\"alloc={ph.get('alloc_gb', 0):.2f}GB reserved={ph.get('reserved_gb', 0):.2f}GB\")" 2>/dev/null)
        echo "  $label: $peak" | tee -a "$QUEUE_LOG"
    else
        echo "  $label: OOM/missing" | tee -a "$QUEUE_LOG"
    fi
done
