#!/usr/bin/env bash
# Run the 093 traditional baseline batch — GARCH, GBM, AR1+SV, Lux-Marchesi
# fit + sample + score. One config = one (asset, model, seed) cell.
#
# Identical structure to h20_run_baseline_phase.sh but calls
# scripts/run_traditional_baseline.py (which dispatches on the
# `traditional.model` field).

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

CONFIG_DIR="${1:-}"
if [[ -z "$CONFIG_DIR" || ! -d "$CONFIG_DIR" ]]; then
    echo "Usage: $0 <experiments/093_.../>" >&2
    exit 1
fi

PARALLEL="${PARALLEL:-8}"
SKIP_DONE="${SKIP_DONE:-1}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
QUEUE_LOG="$CONFIG_DIR/queue_${TIMESTAMP}.log"
: > "$QUEUE_LOG"

fit_one_card() {
    local card="$1"; local label="$2"; local cfg="$3"; local outdir="$4"
    mkdir -p "$outdir"
    if [[ "$SKIP_DONE" == "1" && -f "$outdir/inference_merged.json" ]]; then
        echo "  [skip $label]" | tee -a "$QUEUE_LOG"
        return 0
    fi
    {
        echo "" | tee -a "$QUEUE_LOG"
        echo "═ TRADITIONAL $label (card $card) ═ $(date +%H:%M:%S)" | tee -a "$QUEUE_LOG"
        local start=$(date +%s)
        local job_log="$outdir/traditional_${TIMESTAMP}.log"
        CUDA_VISIBLE_DEVICES="$card" \
        timeout 600 conda run -n ecophys python scripts/run_traditional_baseline.py \
            --config "$cfg" --out-dir "$outdir" 2>&1 \
          | tee "$job_log" >> "$QUEUE_LOG"
        local exit_code=${PIPESTATUS[0]}
        local elapsed=$(( $(date +%s) - start ))
        if [[ $exit_code -eq 0 ]]; then
            echo "  ✓ $label ${elapsed}s (card $card)" | tee -a "$QUEUE_LOG"
        else
            echo "  ✗ $label exit=$exit_code ${elapsed}s (card $card)" | tee -a "$QUEUE_LOG"
        fi
    } &
}

main() {
    echo "═══ TRADITIONAL PHASE — $(date) ═══" | tee -a "$QUEUE_LOG"
    echo "  CONFIG_DIR=$CONFIG_DIR PARALLEL=$PARALLEL SKIP_DONE=$SKIP_DONE" | tee -a "$QUEUE_LOG"

    cfgs=( "$CONFIG_DIR"/config_*.yaml )
    if [[ ${#cfgs[@]} -eq 0 ]]; then
        echo "[error] no config_*.yaml in $CONFIG_DIR" | tee -a "$QUEUE_LOG"
        return 1
    fi
    echo "  Configs: ${#cfgs[@]}" | tee -a "$QUEUE_LOG"

    local card=0
    for cfg in "${cfgs[@]}"; do
        local label=$(basename "$cfg" .yaml | sed 's/^config_//')
        local outdir="$CONFIG_DIR/results_${label}"
        while (( $(jobs -rp | wc -l) >= PARALLEL )); do
            wait -n
        done
        fit_one_card "$card" "$label" "$cfg" "$outdir"
        card=$(( (card + 1) % PARALLEL ))
    done
    wait

    echo "" | tee -a "$QUEUE_LOG"
    echo "═══ DONE — $(date) ═══" | tee -a "$QUEUE_LOG"
}

main
