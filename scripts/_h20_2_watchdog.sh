#!/usr/bin/env bash
# H20-2 watchdog: wait for 121 held-out to finish, then launch 117 leverage
set -uo pipefail
export PATH="/root/miniconda3/envs/ecophys/bin:$PATH"
cd /AI4S/Users/howardwang/h202_amar/ecophys

echo "=== H20-2 WATCHDOG START $(date) ==="

while pgrep -f "h20_run_phase.sh" > /dev/null 2>&1; do
    n_running=$(pgrep -f "train_distributed" | wc -l)
    echo "  $(date) — h20_run_phase still running ($n_running training procs)"
    sleep 300
done

echo "=== 121 held-out done, launching 117 leverage on H20-2 === $(date)"
echo "  180 configs, 2 cards"
PARALLEL=2 bash scripts/h20_run_phase.sh experiments/117_leverage
echo "=== 117 leverage DONE $(date) ==="
