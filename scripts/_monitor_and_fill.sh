#!/usr/bin/env bash
# Monitor all 4 H20 machines and report GPU utilization.
# Run from H20-1: bash scripts/_monitor_and_fill.sh
set -uo pipefail

H20_1_HOST="localhost"
H20_2_HOST="10.239.75.28"
H20_3_HOST="10.239.68.24"
H20_4_HOST="10.239.71.11"
SSH="ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no"

check_machine() {
    local name="$1" host="$2"
    local gpu_info
    if [[ "$host" == "localhost" ]]; then
        gpu_info=$(nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader 2>&1)
    else
        gpu_info=$($SSH root@${host} "nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader" 2>&1)
    fi
    local n_gpus=$(echo "$gpu_info" | wc -l)
    local idle=0
    for line in "$gpu_info"; do
        util=$(echo "$line" | awk -F',' '{print $1}' | tr -d ' %')
        if [[ "${util:-0}" -lt 10 ]]; then
            idle=$((idle + 1))
        fi
    done
    echo "$name: $n_gpus GPUs, $idle idle"
    echo "$gpu_info"
}

echo "═══════════════════════════════════════"
echo "  Fleet monitor — $(date)"
echo "═══════════════════════════════════════"

echo ""
echo "=== H20-1 (8×H20, main) ==="
check_machine "H20-1" "$H20_1_HOST"

echo ""
echo "=== H20-2 (2×H20, side) ==="
check_machine "H20-2" "$H20_2_HOST"

echo ""
echo "=== H20-3 (2×H20, side) ==="
check_machine "H20-3" "$H20_3_HOST"

echo ""
echo "=== H20-4 (CPU, abides) ==="
$SSH root@${H20_4_HOST} "tail -3 /tmp/h20_4_run.log 2>/dev/null || echo 'no log'" 2>&1

echo ""
echo "=== H20-1 progress ==="
echo "-- ndx δ-grid --"
ls experiments/118_delta_grid/ndx/results_*/training_log.json 2>/dev/null | wc -l
echo "-- gold δ-grid --"
ls experiments/118_delta_grid/gold/results_*/training_log.json 2>/dev/null | wc -l
echo "-- eurusd δ-grid --"
ls experiments/118_delta_grid/eurusd/results_*/training_log.json 2>/dev/null | wc -l
echo "-- btcusdt δ-grid --"
ls experiments/118_delta_grid/btcusdt/results_*/training_log.json 2>/dev/null | wc -l
echo "-- 114 top-up --"
ls experiments/114_concave_confirm/results_*/training_log.json 2>/dev/null | wc -l

echo ""
echo "═══════════════════════════════════════"
