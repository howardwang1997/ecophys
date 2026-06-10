#!/usr/bin/env bash
# H20-1 autofill v4 — simple, robust.
# Every 2 min: check GPU mem per card. If mem < 1GB, find next undone config
# and launch train+eval on that card. Uses a simple done-tracker file.
#
# Usage: nohup bash scripts/_h20_1_autofill.sh > /tmp/h20_1_autofill.log 2>&1 &
set -u

REPO_ROOT="/AI4S/Users/howardwang/h204/ecophys"
cd "$REPO_ROOT"
source /root/miniconda3/bin/activate ecophys

N_CARDS=8
CHECK_INTERVAL=120
DONE_FILE="/tmp/ecomd_done_list.txt"

EXPERIMENT_QUEUE=(
    "experiments/118_delta_grid/ndx"
    "experiments/118_delta_grid/gold"
    "experiments/118_delta_grid/eurusd"
    "experiments/118_delta_grid/btcusdt"
    "experiments/114_concave_confirm"
    "experiments/121_heldout_regime/r1"
    "experiments/121_heldout_regime/r2"
    "experiments/117_leverage"
)

# Build done list once from existing results
build_done_list() {
    > "$DONE_FILE"
    for exp_dir in "${EXPERIMENT_QUEUE[@]}"; do
        for f in "$exp_dir"/results_*/training_log.json; do
            [[ -f "$f" ]] || continue
            local label=$(echo "$f" | sed 's|.*/results_||; s|/training_log.json||')
            echo "$label" >> "$DONE_FILE"
        done
    done
}

# Add a label to done list
mark_done() { echo "$1" >> "$DONE_FILE"; }

is_done() { grep -qFx "$1" "$DONE_FILE" 2>/dev/null; }

# Get cards with < 1GB mem usage (idle)
get_idle_cards() {
    local idle=""
    local card=0
    while IFS= read -r line; do
        local mem
        mem=$(echo "$line" | awk -F',' '{print $2}' | tr -d ' MiB')
        mem=${mem:-0}
        if [[ "$mem" -lt 1000 ]]; then
            idle="${idle}${card} "
        fi
        card=$((card + 1))
    done < <(nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader 2>/dev/null || true)
    echo "$idle"
}

next_undone() {
    for exp_dir in "${EXPERIMENT_QUEUE[@]}"; do
        for cfg in "$exp_dir"/config_*.yaml; do
            [[ -f "$cfg" ]] || continue
            local label=$(basename "$cfg" .yaml | sed 's/^config_//')
            is_done "$label" && continue
            echo "$cfg"
            return 0
        done
    done
    return 1
}

run_one() {
    local cfg="$1" card="$2"
    local label=$(basename "$cfg" .yaml | sed 's/^config_//')
    local dir=$(dirname "$cfg")
    local outdir="$dir/results_${label}"
    mkdir -p "$outdir"

    echo "  [train] $label → card $card — $(date +%H:%M:%S)"
    CUDA_VISIBLE_DEVICES=$card timeout 14400 torchrun --nproc_per_node=1 --standalone \
        -m ecomd.training.train_distributed --config "$cfg" --out-dir "$outdir" \
        > "$outdir/train_daemon.log" 2>&1

    if [[ -f "$outdir/training_log.json" ]]; then
        mark_done "$label"
        echo "  [eval]  $label card $card — $(date +%H:%M:%S)"
        CUDA_VISIBLE_DEVICES=$card timeout 14400 torchrun --nproc_per_node=1 --standalone \
            -m ecomd.inference.run_large \
            --ckpt "$outdir/checkpoint.pt" --config "$cfg" \
            --n-steps 4000 --n-realizations-per-rank 4 \
            > "$outdir/eval_daemon.log" 2>&1
        echo "  [done]  $label card $card — $(date +%H:%M:%S)"
    else
        echo "  [FAIL]  $label card $card — $(date +%H:%M:%S)"
    fi
}

echo "╔══════════════════════════════════════════════╗"
echo "║  AUTOFILL v4  $(date '+%Y-%m-%d %H:%M')                ║"
echo "╚══════════════════════════════════════════════╝"
build_done_list
n_done=$(wc -l < "$DONE_FILE")
echo "Done list: $n_done configs. Monitoring $N_CARDS cards every ${CHECK_INTERVAL}s"
echo "Entering main loop..."

while true; do
    echo "  loop $(date '+%H:%M:%S')"
    idle=$(get_idle_cards)
    n_idle=$(echo "$idle" | wc -w)

    if cfg=$(next_undone); then
        if [[ $n_idle -gt 0 ]]; then
            for card in $idle; do
                cfg=$(next_undone) || break
                run_one "$cfg" "$card" &
                sleep 3
            done
        fi
    else
        echo "$(date '+%H:%M') — nothing left, waiting for running jobs..."
        wait
        echo "$(date '+%H:%M') — ALL DONE"
        break
    fi

    sleep $CHECK_INTERVAL
done
