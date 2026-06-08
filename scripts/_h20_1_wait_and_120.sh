#!/usr/bin/env bash
# Wait for exp116 to finish, then launch exp120 spx train-at-N on H20-1
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
export PATH="/root/miniconda3/envs/ecophys/bin:$PATH"

echo "=== WAITING for exp116 (h20_116_criticality.sh) to finish === $(date)"
while pgrep -f "h20_116_criticality.sh" > /dev/null 2>&1; do
    done_n=$(ls experiments/116_criticality/results_*/inference_merged.json 2>/dev/null | wc -l)
    echo "  exp116 progress: ${done_n}/480 — $(date)"
    sleep 300
done
echo "=== exp116 DONE, launching exp120 spx === $(date)"

echo "=== Scoring exp116 ==="
python scripts/score_criticality.py experiments/116_criticality
echo "=== exp116 scored === $(date)"

echo "=== exp120 spx: train-at-N (30 cfg, 8 cards) ==="
DAEMON=0 PARALLEL=8 SKIP_DONE=1 bash scripts/h20_run_phase.sh experiments/120_fss_train/spx
echo "=== exp120 spx DONE === $(date)"

echo "=== Scoring exp120 ==="
python scripts/score_fss_train.py
echo "=== ALL DONE === $(date)"
