#!/usr/bin/env bash
# H20-1 one-shot batch: finds 8 undone configs, runs them, exits.
# Caller should loop: while true; do bash scripts/_h20_1_batch.sh; sleep 60; done
set -u
cd /AI4S/Users/howardwang/h204/ecophys
source /root/miniconda3/bin/activate ecophys

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

# Rebuild done list
> "$DONE_FILE"
for d in "${EXPERIMENT_QUEUE[@]}"; do
    for f in "$d"/results_*/training_log.json; do
        [[ -f "$f" ]] || continue
        echo "$f" | sed 's|.*/results_||; s|/training_log.json||' >> "$DONE_FILE"
    done
done

# Find up to 8 undone configs
todo=()
for d in "${EXPERIMENT_QUEUE[@]}"; do
    for cfg in "$d"/config_*.yaml; do
        [[ -f "$cfg" ]] || continue
        label=$(basename "$cfg" .yaml | sed 's/^config_//')
        grep -qFx "$label" "$DONE_FILE" && continue
        todo+=("$cfg")
        [[ ${#todo[@]} -ge 8 ]] && break 2
    done
done

if [[ ${#todo[@]} -eq 0 ]]; then
    echo "$(date '+%H:%M') ALL DONE"
    exit 0
fi

echo "$(date '+%H:%M') launching ${#todo[@]} configs"
card=0
for cfg in "${todo[@]}"; do
    label=$(basename "$cfg" .yaml | sed 's/^config_//')
    dir=$(dirname "$cfg")
    outdir="$dir/results_${label}"
    mkdir -p "$outdir"
    echo "  $label → card $card"
    (
        CUDA_VISIBLE_DEVICES=$card timeout 14400 torchrun --nproc_per_node=1 --standalone \
            -m ecomd.training.train_distributed --config "$cfg" --out-dir "$outdir" \
            > "$outdir/train_daemon.log" 2>&1
        if [[ -f "$outdir/training_log.json" ]]; then
            CUDA_VISIBLE_DEVICES=$card timeout 14400 torchrun --nproc_per_node=1 --standalone \
                -m ecomd.inference.run_large \
                --ckpt "$outdir/checkpoint.pt" --config "$cfg" \
                --n-steps 4000 --n-realizations-per-rank 4 \
                > "$outdir/eval_daemon.log" 2>&1
            echo "  [done] $label card $card" >> /tmp/h20_1_batch.log
        fi
    ) &
    card=$((card + 1))
done
wait
echo "$(date '+%H:%M') batch done"
