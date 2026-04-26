#!/usr/bin/env bash
# Phase 6 HBM profile — runs each profile config sequentially on a single
# card (NOT config-parallel — we want isolated memory peak measurements,
# not contention). Each config trains 3 iters, no eval.
#
# After all 6 configs complete, run scripts/score_hbm_profile.py to
# aggregate peak HBM from each training_log.json into a markdown table.
#
# Usage:
#   bash scripts/h20_hbm_profile.sh
#   conda run -n ecophys python scripts/score_hbm_profile.py

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

export DIST_BACKEND="${DIST_BACKEND:-nccl}"
export PYTHONPATH="${PYTHONPATH:-$REPO_ROOT}"
NPROC="${NPROC:-1}"
CARD="${CARD:-0}"  # which single card to profile on

CONFIG_DIR="experiments/028_hbm_profile"
QUEUE_LOG="$CONFIG_DIR/_run_$(date +%Y%m%d-%H%M%S).log"
: > "$QUEUE_LOG"

echo "═══ HBM PROFILE — $(date) ═══" | tee -a "$QUEUE_LOG"
echo "  Card: $CARD, NPROC: $NPROC, BACKEND: $DIST_BACKEND" | tee -a "$QUEUE_LOG"

cfgs=( "$CONFIG_DIR"/config_p6_*.yaml )
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
    echo "═ PROFILE $label ═ $(date +%H:%M:%S)" | tee -a "$QUEUE_LOG"
    start=$(date +%s)
    job_log="$outdir/train.log"
    # 5 min timeout — should finish in ~30s for n_iters=3, leeway for slow
    # large-N forward / OOM cleanup.
    CUDA_VISIBLE_DEVICES="$CARD" \
    timeout 300 torchrun --nproc_per_node="$NPROC" --standalone \
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
        # OOM is also informative — record and continue.
        echo "  ✗ $label exit=$exit_code (${elapsed}s) — likely OOM" | tee -a "$QUEUE_LOG"
    fi
done

echo "" | tee -a "$QUEUE_LOG"
echo "──── SCORE ────" | tee -a "$QUEUE_LOG"
conda run -n ecophys python scripts/score_hbm_profile.py 2>&1 | tee -a "$QUEUE_LOG" || \
    echo "  (score script failed — re-run manually)" | tee -a "$QUEUE_LOG"

echo "" | tee -a "$QUEUE_LOG"
echo "═══ DONE — $(date) ═══" | tee -a "$QUEUE_LOG"
