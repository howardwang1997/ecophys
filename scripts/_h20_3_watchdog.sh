#!/usr/bin/env bash
# H20-3 watchdog: wait for 114 btcusdt to finish, then launch 117 leverage
set -uo pipefail
export PATH="/root/miniconda3/envs/ecophys/bin:$PATH"
cd /root/ecophys

echo "=== H20-3 WATCHDOG START $(date) ==="

# Wait for h20_run_phase to finish
while pgrep -f "h20_run_phase.sh" > /dev/null 2>&1; do
    n_running=$(pgrep -f "train_distributed" | wc -l)
    echo "  $(date) — h20_run_phase still running ($n_running training procs)"
    sleep 300
done

echo "=== 114 done, launching 117 leverage on H20-3 === $(date)"
echo "  120 configs, 2 cards"
PARALLEL=2 bash scripts/h20_run_phase.sh experiments/117_leverage
echo "=== 117 leverage DONE $(date) ==="
