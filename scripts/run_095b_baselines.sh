#!/usr/bin/env bash
# Run 095b baselines (WGAN-LP + TrajCast-lite) via run_baseline_fit_eval.py.
# These use a different training path than ECoMD train_distributed.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

CONFIG_DIR="experiments/095b_baselines_n30"
PARALLEL="${PARALLEL:-8}"
SKIP_DONE="${SKIP_DONE:-1}"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
LOG="$CONFIG_DIR/_baseline_run_${TIMESTAMP}.log"

N_GPU="${N_GPU:-8}"

run_one() {
    local cfg="$1"; local card="$2"
    local label=$(basename "$cfg" .yaml | sed 's/^config_//')
    local outdir="$CONFIG_DIR/results_${label}"
    if [[ "$SKIP_DONE" == "1" && -f "$outdir/inference_merged.json" ]]; then
        echo "  [skip] $label" | tee -a "$LOG"
        return 0
    fi
    mkdir -p "$outdir"
    echo "═ BASELINE $label (card $card) ═ $(date +%H:%M:%S)" | tee -a "$LOG"
    local start=$(date +%s)
    CUDA_VISIBLE_DEVICES="$card" /root/miniconda3/envs/ecophys/bin/python \
        scripts/run_baseline_fit_eval.py \
        --config "$cfg" --out-dir "$outdir" >> "$outdir/fit_eval.log" 2>&1
    local rc=$?
    local elapsed=$(( $(date +%s) - start ))
    if [[ $rc -eq 0 ]]; then
        echo "  ✓ $label ${elapsed}s (card $card)" | tee -a "$LOG"
    else
        echo "  ✗ $label exit=$rc ${elapsed}s (card $card)" | tee -a "$LOG"
    fi
}

cfgs=( "$CONFIG_DIR"/config_*.yaml )
echo "═══ 095b baselines — $(date) ═══" | tee -a "$LOG"
echo "  ${#cfgs[@]} configs, PARALLEL=$PARALLEL, N_GPU=$N_GPU" | tee -a "$LOG"

card=0
for cfg in "${cfgs[@]}"; do
    while (( $(jobs -rp | wc -l) >= PARALLEL )); do
        wait -n
    done
    run_one "$cfg" "$((card % N_GPU))" &
    card=$((card + 1))
done
wait

echo "═══ 095b done — $(date) ═══" | tee -a "$LOG"

conda run -n ecophys python scripts/score_phase.py "$CONFIG_DIR" 2>&1 | tee -a "$LOG"
conda run -n ecophys python scripts/score_summary.py "$CONFIG_DIR" \
    --title "095b surrogate baselines n=30" 2>&1 | tee -a "$LOG"
