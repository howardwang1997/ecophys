#!/usr/bin/env bash
# Robust autofill daemon for H20-1 (8×H20).
# Monitors idle cards, launches train+eval, chains into H20-2 overflow.
# Kills stale h20_run_phase processes on startup.
#
# Usage: nohup bash scripts/_h20_1_autofill.sh > /tmp/h20_1_autofill.log 2>&1 &
set -uo pipefail

REPO_ROOT="/AI4S/Users/howardwang/h204/ecophys"
cd "$REPO_ROOT"
source /root/miniconda3/bin/activate ecophys

IDLE_THRESHOLD=10
CHECK_INTERVAL=300
N_CARDS=8
MAX_CONCURRENT=8

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

LOCKDIR="/tmp/ecomd_card_lock"

get_idle_cards() {
    local idle=""
    local card=0
    while IFS= read -r line; do
        util=$(echo "$line" | awk -F',' '{print $1}' | tr -d ' %')
        if [[ "${util:-0}" -lt $IDLE_THRESHOLD ]] && [[ ! -f "$LOCKDIR/card_${card}" ]]; then
            idle="${idle}${card} "
        fi
        card=$((card + 1))
    done < <(nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader 2>/dev/null)
    echo "$idle"
}

next_undone_config() {
    local running_configs
    running_configs=$(ps aux | grep 'train_distributed.*--config' | grep -v grep | \
        sed 's/.*--config //' | sed 's/ .*//' | sort -u)
    for exp_dir in "${EXPERIMENT_QUEUE[@]}"; do
        for cfg in "$exp_dir"/config_*.yaml; do
            [[ -f "$cfg" ]] || continue
            local label=$(basename "$cfg" .yaml | sed 's/^config_//')
            local outdir="$exp_dir/results_${label}"
            if [[ -f "$outdir/training_log.json" ]]; then continue; fi
            if [[ -f "$outdir/.training_lock" ]]; then continue; fi
            if echo "$running_configs" | grep -qF "$cfg"; then continue; fi
            echo "$cfg"
            return 0
        done
    done
    return 1
}

count_all_remaining() {
    local rem=0
    for exp_dir in "${EXPERIMENT_QUEUE[@]}"; do
        for cfg in "$exp_dir"/config_*.yaml; do
            [[ -f "$cfg" ]] || continue
            local label=$(basename "$cfg" .yaml | sed 's/^config_//')
            local outdir="$exp_dir/results_${label}"
            [[ ! -f "$outdir/training_log.json" ]] && rem=$((rem + 1))
        done
    done
    echo $rem
}

count_all_eval_remaining() {
    local rem=0
    for exp_dir in "${EXPERIMENT_QUEUE[@]}"; do
        for cfg in "$exp_dir"/config_*.yaml; do
            [[ -f "$cfg" ]] || continue
            local label=$(basename "$cfg" .yaml | sed 's/^config_//')
            local outdir="$exp_dir/results_${label}"
            if [[ -f "$outdir/training_log.json" ]] && [[ ! -f "$outdir/inference_merged.json" ]]; then
                rem=$((rem + 1))
            fi
        done
    done
    echo $rem
}

launch_train() {
    local card="$1" cfg="$2"
    local label=$(basename "$cfg" .yaml | sed 's/^config_//')
    local dir=$(dirname "$cfg")
    local outdir="$dir/results_${label}"
    mkdir -p "$outdir"
    touch "$outdir/.training_lock"
    touch "$LOCKDIR/card_${card}"
    echo "  [train] $label → card $card — $(date +%H:%M:%S)"
    (
        CUDA_VISIBLE_DEVICES=$card timeout 14400 torchrun --nproc_per_node=1 --standalone \
            -m ecomd.training.train_distributed \
            --config "$cfg" --out-dir "$outdir" \
            > "$outdir/train_daemon.log" 2>&1
        rm -f "$LOCKDIR/card_${card}"
        rm -f "$outdir/.training_lock"
        if [[ -f "$outdir/training_log.json" ]]; then
            echo "  [train✓] $label — $(date +%H:%M:%S)"
            CUDA_VISIBLE_DEVICES=$card timeout 14400 torchrun --nproc_per_node=1 --standalone \
                -m ecomd.inference.run_large \
                --ckpt "$outdir/checkpoint.pt" --config "$cfg" \
                --n-steps 4000 --n-realizations-per-rank 4 \
                > "$outdir/eval_daemon.log" 2>&1
            echo "  [eval✓] $label — $(date +%H:%M:%S)"
        else
            echo "  [train✗] $label — $(date +%H:%M:%S)"
        fi
    ) &
}

echo "╔══════════════════════════════════════════════╗"
echo "║  H20-1 AUTOFILL DAEMON v2  $(date '+%Y-%m-%d %H:%M')  ║"
echo "╚══════════════════════════════════════════════╝"
mkdir -p "$LOCKDIR"
rm -f "$LOCKDIR"/card_*

rem=$(count_all_remaining)
echo "Queue: ${#EXPERIMENT_QUEUE[@]} experiment dirs, $rem configs to train"
echo "Monitoring every ${CHECK_INTERVAL}s, $N_CARDS cards"

while true; do
    rem=$(count_all_remaining)
    evrem=$(count_all_eval_remaining)
    if [[ $rem -eq 0 && $evrem -eq 0 ]]; then
        echo "$(date '+%H:%M') — ALL EXPERIMENTS DONE"
        break
    fi

    idle_cards=$(get_idle_cards)
    n_idle=$(echo "$idle_cards" | wc -w)
    n_running=$(jobs -rp | wc -l)

    echo "$(date '+%H:%M') — rem=$rem eval=$evrem idle=$n_idle running=$n_running"

    if [[ $n_idle -gt 0 ]]; then
        for card in $idle_cards; do
            cfg=$(next_undone_config) || break
            launch_train "$card" "$cfg"
            sleep 2
        done
    fi

    sleep $CHECK_INTERVAL
done

echo "╔══════════════════════════════════════════════╗"
echo "║  DAEMON FINISHED  $(date '+%Y-%m-%d %H:%M')           ║"
echo "╚══════════════════════════════════════════════╝"
