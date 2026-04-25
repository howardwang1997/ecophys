#!/usr/bin/env bash
# H20 master launcher — v3 architecture batch (6 configs).
#
# Trains A0..A5 from experiments/022_h20_batch/ sequentially. Each is
# 4-card DDP, ~200s training. Total wall ~20 minutes including eval.
#
# Usage:
#   git pull
#   bash scripts/h20_batch_v3.sh                 # all 6
#   bash scripts/h20_batch_v3.sh A3              # single
#   NPROC=8 bash scripts/h20_batch_v3.sh         # 8 cards
#   DAEMON=1 nohup bash scripts/h20_batch_v3.sh > /tmp/batch.log 2>&1 &

set -uo pipefail

NPROC="${NPROC:-4}"
DAEMON="${DAEMON:-0}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

export DIST_BACKEND="${DIST_BACKEND:-gloo}"
export ECOPHYS_DATA_DIR="${ECOPHYS_DATA_DIR:-$REPO_ROOT/data/sample}"
export PYTHONPATH="${PYTHONPATH:-$REPO_ROOT}"

# (variant, config, ckpt-dir)
declare -a JOBS=(
    "A0|experiments/022_h20_batch/config_a0_baseline.yaml|experiments/022_h20_batch/results_a0"
    "A1|experiments/022_h20_batch/config_a1_multi_asset.yaml|experiments/022_h20_batch/results_a1"
    "A2|experiments/022_h20_batch/config_a2_multi_asset_mshawkes.yaml|experiments/022_h20_batch/results_a2"
    "A3|experiments/022_h20_batch/config_a3_multi_asset_regime.yaml|experiments/022_h20_batch/results_a3"
    "A4|experiments/022_h20_batch/config_a4_multi_asset_twopop.yaml|experiments/022_h20_batch/results_a4"
    "A5|experiments/022_h20_batch/config_a5_all_features.yaml|experiments/022_h20_batch/results_a5"
)

REQUESTED="${1:-all}"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
QUEUE_LOG="experiments/022_h20_batch/_queue_${TIMESTAMP}.log"
mkdir -p experiments/022_h20_batch
: > "$QUEUE_LOG"

run_one() {
    local label="$1"
    local config="$2"
    local outdir="$3"
    mkdir -p "$outdir"
    echo "" | tee -a "$QUEUE_LOG"
    echo "═══ JOB $label ═══ $(date +%H:%M:%S)" | tee -a "$QUEUE_LOG"
    echo "  config=$config" | tee -a "$QUEUE_LOG"
    echo "  out=$outdir"    | tee -a "$QUEUE_LOG"
    local start=$(date +%s)
    local job_log="$outdir/run_${TIMESTAMP}.log"
    torchrun --nproc_per_node="$NPROC" --standalone \
        -m ecomd.training.train_distributed \
        --config "$config" --out-dir "$outdir" 2>&1 \
      | tee "$job_log" >> "$QUEUE_LOG"
    local exit_code=${PIPESTATUS[0]}
    local elapsed=$(( $(date +%s) - start ))
    if [[ $exit_code -eq 0 ]]; then
        echo "  ✓ $label done in ${elapsed}s" | tee -a "$QUEUE_LOG"
    else
        echo "  ✗ $label FAILED exit=$exit_code (${elapsed}s)" | tee -a "$QUEUE_LOG"
    fi
}

main() {
    echo "═══ H20 batch v3 — $(date) ═══" | tee -a "$QUEUE_LOG"
    echo " NPROC=$NPROC  DIST_BACKEND=$DIST_BACKEND" | tee -a "$QUEUE_LOG"
    for entry in "${JOBS[@]}"; do
        IFS='|' read -r label config outdir <<< "$entry"
        if [[ "$REQUESTED" != "all" && "$REQUESTED" != "$label" ]]; then continue; fi
        run_one "$label" "$config" "$outdir"
    done
    echo "" | tee -a "$QUEUE_LOG"
    echo "═══ Queue done $(date) ═══" | tee -a "$QUEUE_LOG"
    echo "Next: bash scripts/h20_batch_v3_eval.sh" | tee -a "$QUEUE_LOG"
}

if [[ "$DAEMON" == "1" ]]; then
    nohup bash -c 'main' >> "$QUEUE_LOG" 2>&1 &
    echo "started PID $!  log: $QUEUE_LOG"
    echo "$!" > "${QUEUE_LOG}.pid"
else
    main
fi
